/**
 * 손해사정사 1차 학습 서비스 백엔드 — Cloudflare Worker + D1 + KV
 *
 *   · 이메일/비밀번호 가입·로그인
 *   · 무통장입금 결제 (PG 없음) — 입금자명 4자리 코드 + 금액 매칭으로 자동 승인
 *   · 이용권이 있는 사용자에게만 전체 콘텐츠 전송. 없으면 최근 회차 샘플만
 *   · 풀이 기록(선택·오답 이력·메모·별표)을 계정에 저장 → 어느 기기에서든 이어서
 *
 * 인증·결제 흐름은 스마트YOU(gonginjunggaesa)에서 검증된 것을 그대로 따랐다.
 * ⚠ PBKDF2 반복은 Cloudflare Workers 실환경에서 최대 100,000. 넘기면 가입·로그인이 통째로 실패한다.
 *
 * 정적 파일(public/*)은 ASSETS 바인딩이 서빙하고, 여기서는 /api/* 만 처리한다.
 */

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Access-Control-Max-Age': '86400',
};

/* ── 판매 설정 ────────────────────────────────────────────────
   금액은 공인중개사(5,500원)와 반드시 다르게 둔다.
   같은 안드로이드 공기계로 두 서비스의 입금 알림을 받을 때
   금액이 서비스 구분자 역할을 하기 때문이다. */
const BANK = { bank: '토스뱅크', account: '1001-4387-0102', holder: '연지우', amount: 9900 };
const YEAR = 365 * 24 * 3600;             // 이용 기간 1년
const DOCS = ['exam', 'book'];            // exam=기출 600문항, book=전자교재
const MAX_STATE = 2 * 1024 * 1024;        // 풀이 기록 2MB 상한

const now = () => Math.floor(Date.now() / 1000);
const activePaid = u => !!(u && u.paid_until && u.paid_until > now());

const json = (o, s = 200) => new Response(JSON.stringify(o), {
  status: s, headers: { 'Content-Type': 'application/json; charset=utf-8', ...CORS },
});
const err = (m, s = 400) => json({ error: m }, s);
const rawJson = str => new Response(str, {
  headers: { 'Content-Type': 'application/json; charset=utf-8', ...CORS },
});

const hex = buf => [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, '0')).join('');
function randHex(n = 24) { const a = new Uint8Array(n); crypto.getRandomValues(a); return hex(a.buffer); }

async function pbkdf2(password, saltHex) {
  const enc = new TextEncoder();
  const salt = Uint8Array.from(saltHex.match(/../g).map(h => parseInt(h, 16)));
  const key = await crypto.subtle.importKey('raw', enc.encode(password), 'PBKDF2', false, ['deriveBits']);
  const bits = await crypto.subtle.deriveBits(
    { name: 'PBKDF2', salt, iterations: 100000, hash: 'SHA-256' }, key, 256);
  return hex(bits);
}
function timingEqual(a, b) {
  if (typeof a !== 'string' || typeof b !== 'string' || a.length !== b.length) return false;
  let r = 0;
  for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return r === 0;
}

async function userByToken(env, token) {
  if (!token) return null;
  const s = await env.DB.prepare('SELECT email FROM sessions WHERE token=?').bind(token).first();
  if (!s) return null;
  return env.DB.prepare('SELECT email, phone, paid, paid_until, created FROM users WHERE email=?')
    .bind(s.email).first();
}
async function adminOk(env, token) {
  if (!token) return false;
  const row = await env.DB.prepare('SELECT created FROM admin_sessions WHERE token=?').bind(token).first();
  if (!row) return false;
  if (now() - row.created > 43200) {      // 12시간
    await env.DB.prepare('DELETE FROM admin_sessions WHERE token=?').bind(token).run();
    return false;
  }
  return true;
}

/* 승인 — 관리자 수동승인과 입금 웹훅 자동승인이 함께 쓴다.
   이미 이용권이 살아 있으면 남은 기간에 1년을 얹는다(연장). */
async function approveUser(env, email) {
  const u = await env.DB.prepare('SELECT paid_until FROM users WHERE email=?').bind(email).first();
  const base = (u && u.paid_until && u.paid_until > now()) ? u.paid_until : now();
  const until = base + YEAR;
  await env.DB.prepare('UPDATE users SET paid=1, paid_until=? WHERE email=?').bind(until, email).run();
  await env.DB.prepare('UPDATE payments SET status=?, approved=? WHERE email=?')
    .bind('paid', now(), email).run();
  return until;
}

/* 이미 쓰고 있는 코드는 피해서 4자리를 뽑는다 */
async function freshCode(env) {
  for (let i = 0; i < 30; i++) {
    const c = String(Math.floor(1000 + Math.random() * 9000));
    const hit = await env.DB.prepare('SELECT code FROM payments WHERE code=?').bind(c).first();
    if (!hit) return c;
  }
  return null;
}

const meShape = u => ({
  email: u.email, phone: u.phone || '',
  paid: activePaid(u) ? 1 : 0,
  paidUntil: u.paid_until || null,
  amount: BANK.amount,
});

/* 관리자 로그인 보호 — 비밀번호가 짧아도 버티게 하는 층.
   ① 같은 IP 5회 실패 → 15분 잠금
   ② 전체 합계 30회 실패 → 새 IP 는 15분 잠금(분산 시도 대비)
   ③ 한 번 성공한 IP 는 30일간 ② 의 전체 잠금에서 제외 — 주인이 갇히지 않게 한다
   ④ 실패할 때마다 2초 지연 */
const ADMIN_MAX_FAIL = 5;        // 같은 IP 실패 허용 횟수
const ADMIN_GLOBAL_MAX = 30;     // 전체 실패 허용 횟수
const ADMIN_LOCK_SEC = 900;      // 잠금 유지 시간(초)
const ADMIN_TRUST_SEC = 2592000; // 성공한 IP 를 기억하는 기간(30일)
const ADMIN_FAIL_DELAY = 2000;   // 실패 응답 지연(밀리초)

async function handleApi(request, env, path) {
  let body = {};
  try { body = await request.json(); } catch (e) {}

  /* ── 무료 샘플 (인증 불필요) ───────────────────────────────
     결제 전에도 최근 한 회차는 통째로 풀어 볼 수 있게 한다. */
  if (path === '/sample') {
    const doc = String(body.doc || 'exam');
    if (!DOCS.includes(doc)) return err('알 수 없는 콘텐츠입니다.');
    const raw = await env.KV.get('content:sample_' + doc);
    if (!raw) return err('샘플이 아직 준비되지 않았습니다.', 503);
    return rawJson('{"ok":true,"sample":true,"data":' + raw + '}');
  }

  /* ── 입금 웹훅 (안드로이드 공기계 알림 포워딩 → 자동 승인) ──
     조건: 입금자명의 4자리 코드가 '대기 중' 결제건과 일치 + 금액이 정확히 일치. */
  if (path === '/hook/deposit') {
    if (!env.HOOK_SECRET) return err('서버에 HOOK_SECRET 이 설정되지 않았습니다.', 500);
    if (!timingEqual(String(body.secret || ''), env.HOOK_SECRET)) return err('인증 실패.', 401);

    const text = String(body.text || body.raw || '');
    let amount = parseInt(body.amount, 10) || 0;
    if (!amount) {
      const m = text.replace(/,/g, '').match(/(\d{3,7})\s*원/);
      if (m) amount = parseInt(m[1], 10);
    }
    // 콤마를 지우지 않은 원문에서 4자리를 찾는다 → '9,900' 은 걸리지 않는다
    const cands = body.code ? [String(body.code)] : (text.match(/\d{4}/g) || []);

    let matched = null, dup = null;
    for (const c of cands) {
      const p = await env.DB.prepare('SELECT email, code, status FROM payments WHERE code=?').bind(c).first();
      if (!p) continue;
      if (p.status === 'pending') { matched = p; break; }
      if (p.status === 'paid' && !dup) dup = p;
    }

    let status, matchedEmail = null;
    if (matched && amount === BANK.amount) {
      await approveUser(env, matched.email);
      status = 'matched'; matchedEmail = matched.email;
    } else if (matched) status = 'amount_mismatch';
    else if (dup) status = 'duplicate';
    else status = 'unmatched';

    await env.DB.prepare(
      'INSERT INTO deposits(raw,amount,code,matched_email,status,created) VALUES(?,?,?,?,?,?)')
      .bind(text.slice(0, 300), amount || null,
            (matched || dup || {}).code || cands[0] || null, matchedEmail, status, now()).run();
    return json({ ok: true, status, email: matchedEmail });
  }

  /* ── 회원가입 ── */
  if (path === '/signup') {
    const email = String(body.email || '').trim().toLowerCase();
    const password = String(body.password || '');
    const phone = String(body.phone || '').replace(/[^0-9]/g, '');
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return err('올바른 이메일 형식이 아닙니다.');
    if (password.length < 6) return err('비밀번호는 6자 이상이어야 합니다.');
    const exists = await env.DB.prepare('SELECT email FROM users WHERE email=?').bind(email).first();
    if (exists) return err('이미 가입된 이메일입니다. 로그인해 주세요.');
    const salt = randHex(16);
    const ph = await pbkdf2(password, salt);
    await env.DB.prepare('INSERT INTO users(email,pass_salt,pass_hash,phone,created) VALUES(?,?,?,?,?)')
      .bind(email, salt, ph, phone || null, now()).run();
    const token = randHex(24);
    await env.DB.prepare('INSERT INTO sessions(token,email,created) VALUES(?,?,?)')
      .bind(token, email, now()).run();
    return json({ email, token, paid: 0, paidUntil: null, amount: BANK.amount });
  }

  /* ── 로그인 ── */
  if (path === '/login') {
    const email = String(body.email || '').trim().toLowerCase();
    const password = String(body.password || '');
    const u = await env.DB.prepare(
      'SELECT email,pass_salt,pass_hash,phone,paid,paid_until FROM users WHERE email=?').bind(email).first();
    if (!u) return err('가입되지 않은 이메일이거나 비밀번호가 틀립니다.', 401);
    const ph = await pbkdf2(password, u.pass_salt);
    if (!timingEqual(ph, u.pass_hash)) return err('가입되지 않은 이메일이거나 비밀번호가 틀립니다.', 401);
    const token = randHex(24);
    await env.DB.prepare('INSERT INTO sessions(token,email,created) VALUES(?,?,?)')
      .bind(token, email, now()).run();
    return json({ token, ...meShape(u) });
  }

  /* ── 내 정보 (이용권 상태 포함) ── */
  if (path === '/me') {
    const u = await userByToken(env, body.token);
    if (!u) return err('세션이 만료되었습니다. 다시 로그인해 주세요.', 401);
    return json(meShape(u));
  }

  /* ── 결제(무통장) 요청·조회 ── */
  if (path === '/pay/request') {
    const u = await userByToken(env, body.token);
    if (!u) return err('세션이 만료되었습니다.', 401);

    let p = await env.DB.prepare('SELECT * FROM payments WHERE email=?').bind(u.email).first();
    if (!p) {
      const code = await freshCode(env);
      if (!code) return err('코드 발급에 실패했습니다. 잠시 후 다시 시도해 주세요.', 503);
      await env.DB.prepare(
        'INSERT INTO payments(email,code,amount,status,receipt_phone,requested) VALUES(?,?,?,?,?,?)')
        .bind(u.email, code, BANK.amount, 'pending', u.phone || null, now()).run();
      p = { email: u.email, code, amount: BANK.amount, status: 'pending', receipt_phone: u.phone || '' };
    }
    // 이미 승인된 뒤 재결제(연장) 요청이면 새 코드로 다시 대기 상태를 만든다
    if (p.status === 'paid' && body.renew) {
      const code = await freshCode(env);
      if (code) {
        await env.DB.prepare('UPDATE payments SET code=?, status=?, requested=?, approved=NULL WHERE email=?')
          .bind(code, 'pending', now(), u.email).run();
        p.code = code; p.status = 'pending';
      }
    }
    // 입금 완료 알림 + 현금영수증 신청
    if (body.notify) {
      const wantRcpt = body.receipt !== false;
      const phone = !wantRcpt ? null
        : (body.receiptPhone ? String(body.receiptPhone).replace(/[^0-9]/g, '') : (u.phone || null));
      await env.DB.prepare('UPDATE payments SET receipt_phone=?, requested=? WHERE email=?')
        .bind(phone, now(), u.email).run();
      p.receipt_phone = phone || '';
    }
    return json({
      status: p.status, code: p.code, amount: BANK.amount,
      bank: BANK.bank, account: BANK.account, holder: BANK.holder,
      receipt_phone: p.receipt_phone || u.phone || '',
      paid: activePaid(u) ? 1 : 0, paidUntil: u.paid_until || null,
    });
  }

  /* ── 풀이 기록 저장·불러오기 (KV) ── */
  if (path === '/save') {
    const u = await userByToken(env, body.token);
    if (!u) return err('세션이 만료되었습니다.', 401);
    const s = JSON.stringify(body.state || {});
    if (s.length > MAX_STATE) return err('저장 용량을 초과했습니다.', 413);
    await env.KV.put('state:' + u.email, s);
    return json({ ok: true });
  }
  if (path === '/load') {
    const u = await userByToken(env, body.token);
    if (!u) return err('세션이 만료되었습니다.', 401);
    const raw = await env.KV.get('state:' + u.email);
    return rawJson('{"state":' + (raw || 'null') + '}');
  }

  /* ── 전체 콘텐츠 (이용권 필요) ── */
  if (path === '/content') {
    const u = await userByToken(env, body.token);
    if (!u) return err('로그인이 필요합니다.', 401);
    if (!activePaid(u)) return err('이용권 결제 후 이용할 수 있습니다.', 402);
    const doc = String(body.doc || 'exam');
    if (!DOCS.includes(doc)) return err('알 수 없는 콘텐츠입니다.');
    const raw = await env.KV.get('content:' + doc);
    if (!raw) return err('콘텐츠가 아직 준비되지 않았습니다.', 503);
    // raw 는 이미 JSON 문자열 → 재파싱 없이 그대로 감싸 보낸다
    return rawJson('{"ok":true,"data":' + raw + '}');
  }

  /* ── 관리자 ── */
  if (path === '/admin/login') {
    if (!env.ADMIN_PASSWORD) return err('서버에 ADMIN_PASSWORD 가 설정되지 않았습니다.', 500);
    const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
    const fkey = 'adminfail:' + ip;
    const tkey = 'admintrust:' + ip;
    const [failRaw, globalRaw, trusted] = await Promise.all([
      env.KV.get(fkey), env.KV.get('adminfail:_all'), env.KV.get(tkey),
    ]);
    const fails = parseInt(failRaw, 10) || 0;
    const globalFails = parseInt(globalRaw, 10) || 0;

    if (fails >= ADMIN_MAX_FAIL) {
      return err('이 기기에서 로그인 시도가 너무 많습니다. 15분 뒤에 다시 시도해 주세요.', 429);
    }
    if (!trusted && globalFails >= ADMIN_GLOBAL_MAX) {
      return err('관리자 로그인이 일시적으로 잠겼습니다. 15분 뒤에 다시 시도해 주세요.', 429);
    }
    if (!timingEqual(String(body.password || ''), env.ADMIN_PASSWORD)) {
      await Promise.all([
        env.KV.put(fkey, String(fails + 1), { expirationTtl: ADMIN_LOCK_SEC }),
        env.KV.put('adminfail:_all', String(globalFails + 1), { expirationTtl: ADMIN_LOCK_SEC }),
        new Promise(r => setTimeout(r, ADMIN_FAIL_DELAY)),
      ]);
      return err('비밀번호가 틀립니다.', 401);
    }
    await Promise.all([
      env.KV.delete(fkey),
      env.KV.put(tkey, '1', { expirationTtl: ADMIN_TRUST_SEC }),
    ]);
    const token = randHex(24);
    await env.DB.prepare('INSERT INTO admin_sessions(token,created) VALUES(?,?)').bind(token, now()).run();
    return json({ adminToken: token });
  }
  if (path === '/admin/list') {
    if (!(await adminOk(env, body.adminToken))) return err('관리자 인증이 필요합니다.', 401);
    const { results } = await env.DB.prepare(
      `SELECT p.email, p.code, p.amount, p.status, p.receipt_phone, p.requested, p.approved,
              u.paid, u.paid_until, u.phone
       FROM payments p LEFT JOIN users u ON u.email = p.email
       ORDER BY (p.status='pending') DESC, p.requested DESC LIMIT 200`).all();
    return json({ rows: results || [], amount: BANK.amount });
  }
  if (path === '/admin/customers') {
    if (!(await adminOk(env, body.adminToken))) return err('관리자 인증이 필요합니다.', 401);
    const { results } = await env.DB.prepare(
      `SELECT u.email, u.phone, u.paid, u.paid_until, u.created,
              p.code, p.status AS pay_status, p.receipt_phone, p.requested, p.approved
       FROM users u LEFT JOIN payments p ON p.email = u.email
       ORDER BY u.created DESC LIMIT 5000`).all();
    return json({ rows: results || [] });
  }
  if (path === '/admin/deposits') {
    if (!(await adminOk(env, body.adminToken))) return err('관리자 인증이 필요합니다.', 401);
    const { results } = await env.DB.prepare(
      'SELECT id, raw, amount, code, matched_email, status, created FROM deposits ORDER BY created DESC LIMIT 100').all();
    return json({ rows: results || [] });
  }
  if (path === '/admin/approve' || path === '/admin/reject') {
    if (!(await adminOk(env, body.adminToken))) return err('관리자 인증이 필요합니다.', 401);
    const email = String(body.email || '').trim().toLowerCase();
    const u = await env.DB.prepare('SELECT email FROM users WHERE email=?').bind(email).first();
    if (!u) return err('해당 사용자를 찾을 수 없습니다.', 404);
    if (path === '/admin/approve') {
      const until = await approveUser(env, email);
      return json({ ok: true, paidUntil: until });
    }
    await env.DB.prepare('UPDATE users SET paid=0, paid_until=NULL WHERE email=?').bind(email).run();
    await env.DB.prepare('UPDATE payments SET status=? WHERE email=?').bind('rejected', email).run();
    return json({ ok: true });
  }

  return err('알 수 없는 요청입니다.', 404);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname.startsWith('/api/')) {
      if (request.method === 'OPTIONS') return new Response(null, { headers: CORS });
      if (request.method !== 'POST') return err('POST 요청만 허용됩니다.', 405);
      try {
        return await handleApi(request, env, url.pathname.replace(/^\/api/, ''));
      } catch (e) {
        return err('서버 오류: ' + (e && e.message ? e.message : String(e)), 500);
      }
    }
    if (env.ASSETS) return env.ASSETS.fetch(request);
    return new Response('Not found', { status: 404 });
  },
};
