/**
 * 손해사정사 1차 기출 백엔드 — Cloudflare Worker + D1 + KV
 *
 *   · 이메일/비밀번호 가입·로그인
 *   · 풀이 기록(선택·정오답 이력)을 계정에 저장 → 어느 기기에서든 이어서
 *   · 문항 데이터(600문항)는 KV 에 넣고 로그인한 사용자에게만 내려준다
 *
 * 인증 방식은 스마트YOU(gonginjunggaesa)와 s2s-lecture 에서 검증된 것을 그대로 따랐다.
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

const DOCS = ['exam', 'book'];            // exam=기출 600문항, book=이론 전자교재
const MAX_STATE = 2 * 1024 * 1024;        // 풀이 기록 2MB 상한
const now = () => Math.floor(Date.now() / 1000);

const json = (o, s = 200) => new Response(JSON.stringify(o), {
  status: s, headers: { 'Content-Type': 'application/json; charset=utf-8', ...CORS },
});
const err = (m, s = 400) => json({ error: m }, s);

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
  return env.DB.prepare('SELECT email, created FROM users WHERE email=?').bind(s.email).first();
}

async function handleApi(request, env, path) {
  let body = {};
  try { body = await request.json(); } catch (e) {}

  /* ── 회원가입 ── */
  if (path === '/signup') {
    const email = String(body.email || '').trim().toLowerCase();
    const password = String(body.password || '');
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return err('올바른 이메일 형식이 아닙니다.');
    if (password.length < 6) return err('비밀번호는 6자 이상이어야 합니다.');
    const exists = await env.DB.prepare('SELECT email FROM users WHERE email=?').bind(email).first();
    if (exists) return err('이미 가입된 이메일입니다. 로그인해 주세요.');
    const salt = randHex(16);
    const ph = await pbkdf2(password, salt);
    await env.DB.prepare('INSERT INTO users(email,pass_salt,pass_hash,created) VALUES(?,?,?,?)')
      .bind(email, salt, ph, now()).run();
    const token = randHex(24);
    await env.DB.prepare('INSERT INTO sessions(token,email,created) VALUES(?,?,?)')
      .bind(token, email, now()).run();
    return json({ email, token });
  }

  /* ── 로그인 ── */
  if (path === '/login') {
    const email = String(body.email || '').trim().toLowerCase();
    const password = String(body.password || '');
    const u = await env.DB.prepare('SELECT email,pass_salt,pass_hash FROM users WHERE email=?')
      .bind(email).first();
    if (!u) return err('가입되지 않은 이메일이거나 비밀번호가 틀립니다.', 401);
    const ph = await pbkdf2(password, u.pass_salt);
    if (!timingEqual(ph, u.pass_hash)) return err('가입되지 않은 이메일이거나 비밀번호가 틀립니다.', 401);
    const token = randHex(24);
    await env.DB.prepare('INSERT INTO sessions(token,email,created) VALUES(?,?,?)')
      .bind(token, email, now()).run();
    return json({ email: u.email, token });
  }

  /* ── 내 정보 ── */
  if (path === '/me') {
    const u = await userByToken(env, body.token);
    if (!u) return err('세션이 만료되었습니다. 다시 로그인해 주세요.', 401);
    return json({ email: u.email });
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
    return new Response('{"state":' + (raw || 'null') + '}', {
      headers: { 'Content-Type': 'application/json; charset=utf-8', ...CORS },
    });
  }

  /* ── 문항·교재 전송 (로그인 사용자 전용) ── */
  if (path === '/content') {
    const u = await userByToken(env, body.token);
    if (!u) return err('로그인이 필요합니다.', 401);
    const doc = String(body.doc || 'exam');
    if (!DOCS.includes(doc)) return err('알 수 없는 콘텐츠입니다.');
    const raw = await env.KV.get('content:' + doc);
    if (!raw) return err('콘텐츠가 아직 준비되지 않았습니다.', 503);
    // raw 는 이미 JSON 문자열 → 재파싱 없이 그대로 감싸 보낸다
    return new Response('{"ok":true,"data":' + raw + '}', {
      headers: { 'Content-Type': 'application/json; charset=utf-8', ...CORS },
    });
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
