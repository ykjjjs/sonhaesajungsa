const path = require('path');
const ROOT = path.resolve(__dirname, '..');
const fileUrl = p => 'file://' + path.join(ROOT, p);
const { chromium } = require('playwright');
const { start } = require('./serve');

const now = Math.floor(Date.now()/1000), D = 86400;
const PAY = [
  { email:'kim@example.com', code:'4821', amount:9900, status:'pending', receipt_phone:'01012345678',
    requested: now-600, approved:null, paid:0, paid_until:null, phone:'01012345678' },
  { email:'lee@example.com', code:'1007', amount:9900, status:'paid', receipt_phone:'01099998888',
    requested: now-3*D, approved: now-3*D+120, paid:1, paid_until: now+362*D, phone:'01099998888' },
  { email:'park@example.com', code:'3315', amount:9900, status:'paid', receipt_phone:null,
    requested: now-9*D, approved: now-9*D+90, paid:1, paid_until: now+356*D, phone:null },
  { email:'choi@example.com', code:'7742', amount:9900, status:'rejected', receipt_phone:null,
    requested: now-14*D, approved:null, paid:0, paid_until:null, phone:'01055556666' },
];
const CUST = [
  ...PAY.map(p => ({ email:p.email, phone:p.phone, paid:p.paid, paid_until:p.paid_until,
    created: p.requested-3600, code:p.code, pay_status:p.status, receipt_phone:p.receipt_phone,
    requested:p.requested, approved:p.approved })),
  { email:'trial@example.com', phone:null, paid:0, paid_until:null, created: now-2*D,
    code:null, pay_status:null },
  { email:'guest@example.com', phone:null, paid:0, paid_until:null, created: now-40, code:null, pay_status:null },
];
const DEP = [
  { id:5, raw:'토스뱅크 입금 9,900원 김손해4821 잔액 1,240,300원', amount:9900, code:'4821',
    matched_email:'kim@example.com', status:'matched', created: now-540 },
  { id:4, raw:'토스뱅크 입금 5,500원 박공인2211 잔액 1,230,400원', amount:5500, code:'2211',
    matched_email:null, status:'unmatched', created: now-2*3600 },
  { id:3, raw:'토스뱅크 입금 9,000원 이용자1007 잔액 1,224,900원', amount:9000, code:'1007',
    matched_email:null, status:'amount_mismatch', created: now-5*3600 },
  { id:2, raw:'토스뱅크 입금 9,900원 이용자1007 잔액 1,215,000원', amount:9900, code:'1007',
    matched_email:null, status:'duplicate', created: now-2*D },
];

function mock(pg, opts = {}) {
  return pg.route('**/api/**', route => {
    const u = route.request().url();
    const b = JSON.parse(route.request().postData() || '{}');
    const j = (o, s=200) => route.fulfill({ status:s, contentType:'application/json', body:JSON.stringify(o) });
    if (u.endsWith('/admin/login'))
      return b.password === 'right' ? j({ adminToken:'AT' }) : j({ error:'비밀번호가 틀립니다.' }, 401);
    if (b.adminToken !== 'AT') return j({ error:'관리자 인증이 필요합니다.' }, 401);
    if (u.endsWith('/admin/list')) return j({ rows: opts.empty ? [] : PAY, amount:9900 });
    if (u.endsWith('/admin/customers')) return j({ rows: opts.empty ? [] : CUST });
    if (u.endsWith('/admin/deposits')) return j({ rows: opts.empty ? [] : DEP });
    if (u.endsWith('/admin/approve') || u.endsWith('/admin/reject')) { opts.acted = u; return j({ ok:true }); }
    return j({ error:'?' }, 404);
  });
}

(async () => {
  const { srv, url: BASE } = await start();
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const errs = [], out = {};
  const pg = await b.newPage({ viewport:{width:1280,height:900} });
  pg.on('pageerror', e => errs.push('PAGEERROR ' + e.message));
  pg.on('console', m => { if (m.type()==='error' && !/ERR_CONNECTION|Failed to load resource/.test(m.text())) errs.push(m.text()); });
  const opts = {};
  await mock(pg, opts);
  await pg.goto(BASE + '/admin.html');
  await pg.waitForTimeout(500);

  // 1. 로그인 화면 · 틀린 비밀번호
  out.loginShown = await pg.$eval('.login h2', n => n.textContent);
  await pg.fill('#pw', 'wrong'); await pg.click('#go'); await pg.waitForTimeout(400);
  out.badPw = (await pg.textContent('.err')).trim();

  // 2. 올바른 비밀번호
  await pg.fill('#pw', 'right'); await pg.click('#go'); await pg.waitForTimeout(700);
  out.kpis = await pg.$$eval('.kpi', ns => ns.map(n => n.querySelector('b').textContent + ' / ' + n.querySelector('span').textContent));
  out.tabs = await pg.$$eval('.tab', ns => ns.map(n => n.textContent.replace(/\s+/g,' ').trim()));
  out.payRows = await pg.$$eval('#tbl tbody tr', n => n.length);
  out.pills = await pg.$$eval('#tbl .pill', ns => ns.map(n => n.textContent.trim()));

  // 3. 검색
  await pg.fill('#q', 'lee'); await pg.waitForTimeout(250);
  out.search = await pg.$$eval('#tbl tbody tr', n => n.length);
  await pg.fill('#q', 'zzz'); await pg.waitForTimeout(250);
  out.searchEmpty = (await pg.textContent('#tbl .empty h2')).trim();
  await pg.fill('#q', ''); await pg.waitForTimeout(250);

  // 4. 탭 이동
  await pg.click('[data-t="cust"]'); await pg.waitForTimeout(300);
  out.custRows = await pg.$$eval('#tbl tbody tr', n => n.length);
  out.custHead = await pg.$$eval('#tbl th', ns => ns.map(n => n.textContent.trim()));
  await pg.click('[data-t="dep"]'); await pg.waitForTimeout(300);
  out.depRows = await pg.$$eval('#tbl tbody tr', n => n.length);
  out.depPills = await pg.$$eval('#tbl .pill', ns => ns.map(n => n.textContent.trim()));
  out.depRaw = await pg.$eval('#tbl td.wrap', n => n.textContent.trim().slice(0,30));

  // 5. 승인
  await pg.click('[data-t="pay"]'); await pg.waitForTimeout(300);
  pg.on('dialog', d => d.accept());
  await pg.click('[data-ap="kim@example.com"]'); await pg.waitForTimeout(700);
  out.approved = (opts.acted || '').split('/').pop();
  out.toast = (await pg.textContent('#toast')).trim();

  // 6. CSV
  const dl = pg.waitForEvent('download', { timeout: 5000 }).catch(() => null);
  await pg.click('#csv');
  const d = await dl;
  out.csv = d ? d.suggestedFilename() : null;

  // 7. 밤낮
  out.theme0 = await pg.getAttribute('html','data-theme');
  await pg.click('#themeBtn'); await pg.waitForTimeout(250);
  out.theme1 = await pg.getAttribute('html','data-theme');

  // 8. 단축키
  await pg.keyboard.press('/'); await pg.waitForTimeout(200);
  out.slashFocus = await pg.evaluate(() => document.activeElement.id);

  // 9. 폰트·토큰이 앱과 같은지
  out.tokens = await pg.evaluate(() => {
    const cs = getComputedStyle(document.documentElement);
    return { bg: cs.getPropertyValue('--bg').trim(), sap2: cs.getPropertyValue('--sap2').trim(),
      ease: cs.getPropertyValue('--ease').trim(), font: getComputedStyle(document.body).fontFamily.split(',')[0] };
  });
  await pg.close();

  // 10. 빈 상태
  const p2 = await b.newPage(); await mock(p2, { empty:true });
  await p2.addInitScript(() => localStorage.setItem('sonsa:admin','AT'));
  await p2.goto(BASE + '/admin.html'); await p2.waitForTimeout(700);
  out.emptyState = (await p2.textContent('#tbl .empty h2')).trim();
  await p2.click('[data-t="dep"]'); await p2.waitForTimeout(300);
  out.emptyDep = (await p2.textContent('#tbl .empty p')).trim().slice(0,40);
  await p2.close();

  out.errs = errs;
  console.log(JSON.stringify(out, null, 1));
  await b.close(); srv.close();
})();
