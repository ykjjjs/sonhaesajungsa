const path = require('path');
const ROOT = path.resolve(__dirname, '..');
const fileUrl = p => 'file://' + path.join(ROOT, p);
const { chromium } = require('playwright');
const { start } = require('./serve');

// 워커를 흉내 내는 가짜 API — 결제 전/후 상태를 오가며 화면을 확인한다
function mockRoutes(pg, st) {
  return pg.route('**/api/**', async route => {
    const url = route.request().url();
    const body = JSON.parse(route.request().postData() || '{}');
    const j = (o, s = 200) => route.fulfill({ status: s, contentType: 'application/json',
      body: JSON.stringify(o) });
    if (url.endsWith('/me')) return j({ email:'a@b.com', phone:'', paid: st.paid,
      paidUntil: st.paid ? st.until : null, amount: 9900 });
    if (url.endsWith('/login') || url.endsWith('/signup'))
      return j({ token:'T', email:'a@b.com', phone: body.phone||'', paid: st.paid,
        paidUntil: st.paid ? st.until : null, amount: 9900 });
    if (url.endsWith('/pay/request')) { st.notified = st.notified || !!body.notify;
      return j({ status: st.paid?'paid':'pending', code:'4821', amount:9900, bank:'토스뱅크',
        account:'1001-4387-0102', holder:'연지우', receipt_phone: body.receiptPhone || '',
        paid: st.paid, paidUntil: st.paid ? st.until : null }); }
    if (url.endsWith('/content')) {
      if (!st.paid) return j({ error:'이용권 결제 후 이용할 수 있습니다.' }, 402);
      return j({ ok:true, data: st.full });
    }
    if (url.endsWith('/load')) return j({ state: null });
    if (url.endsWith('/save')) return j({ ok:true });
    return j({ error:'?' }, 404);
  });
}

(async () => {
  const { srv, url: BASE } = await start();
  const full = JSON.parse(require('fs').readFileSync(path.join(ROOT,'data/exam.json'),'utf8'));
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const out = {}; const errs = [];

  // ── 1. 미결제 계정 ──
  const st = { paid: 0, until: Math.floor(Date.now()/1000)+31536000, full };
  const pg = await b.newPage();
  pg.on('pageerror', e => errs.push('PAGEERROR ' + e.message));
  pg.on('console', m => { if (m.type()==='error' && !/ERR_CONNECTION|Failed to load resource/.test(m.text())) errs.push(m.text()); });
  await mockRoutes(pg, st);
  await pg.addInitScript(() => localStorage.setItem('sonsa:auth', JSON.stringify({token:'T',email:'a@b.com'})));
  await pg.goto(BASE + '/index.html');
  await pg.waitForTimeout(900);

  out.free = await pg.evaluate(() => ({
    years: YEARS, n: BANK.length, full: S.full, paid: S.paid,
    yearOpts: [...document.getElementById('selYear').options].map(o=>o.value),
    lic: (document.getElementById('licBox').textContent||'').trim(),
  }));

  // 잠금 항목 선택 → 결제창
  await pg.selectOption('#selYear', '__pay'); await pg.waitForTimeout(500);
  out.payOpen = await pg.$eval('#payOv', n => n.classList.contains('on'));
  out.paySheet = await pg.evaluate(() => ({
    bank: document.getElementById('payBank').textContent,
    acct: document.getElementById('payAcct').textContent,
    amt:  document.getElementById('payAmt2').textContent,
    name: document.getElementById('payName').textContent,
    title: document.getElementById('payAmt').textContent,
  }));
  out.yearAfterCancel = await pg.$eval('#selYear', n => n.value);

  // 입금 완료 → 아직 미승인
  await pg.click('#payDone'); await pg.waitForTimeout(600);
  out.afterNotify = { notified: st.notified,
    stillOpen: await pg.$eval('#payOv', n=>n.classList.contains('on')),
    err: (await pg.textContent('#payErr')||'').trim(),
    toast: (await pg.textContent('#toast')||'').trim() };

  // ── 2. 서버에서 승인이 났다고 가정하고 새로고침 ──
  st.paid = 1;
  await pg.click('#payRefresh'); await pg.waitForTimeout(1200);
  out.afterApprove = await pg.evaluate(() => ({
    n: BANK.length, years: YEARS, full: S.full, paid: S.paid,
    payClosed: !document.getElementById('payOv').classList.contains('on'),
    lic: (document.getElementById('licBox').textContent||'').trim(),
    yearOpts: [...document.getElementById('selYear').options].map(o=>o.value),
  }));
  await pg.close();

  // ── 3. 교재 게이트 ──
  for (const [name, paid] of [['book-unpaid',0],['book-paid',1]]) {
    const p2 = await b.newPage();
    p2.on('pageerror', e => errs.push('BOOK ' + e.message));
    const s2 = { paid, until: st.until, full: JSON.parse(require('fs').readFileSync(path.join(ROOT,'data/book.json'),'utf8')) };
    await mockRoutes(p2, s2);
    await p2.addInitScript(() => localStorage.setItem('sonsa:auth', JSON.stringify({token:'T'})));
    await p2.goto(BASE + '/book.html');
    await p2.waitForTimeout(1000);
    out[name] = await p2.evaluate(() => ({
      h1: (document.querySelector('h1')||{}).textContent,
      chapters: document.querySelectorAll('.chcard').length,
      terms: typeof TERMS === 'object' ? Object.keys(TERMS).length : 0,
      search: typeof SEARCH !== 'undefined' ? SEARCH.length : 0,
    }));
    await p2.close();
  }

  // ── 4. 로그인 안 한 상태로 교재 ──
  const p3 = await b.newPage(); await mockRoutes(p3, { paid:0, full:{} });
  await p3.goto(BASE + '/book.html'); await p3.waitForTimeout(700);
  out.bookAnon = (await p3.textContent('h1')||'').trim();
  await p3.close();

  out.errs = errs;
  console.log(JSON.stringify(out, null, 1));
  await b.close(); srv.close();
})();
