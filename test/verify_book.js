const path = require('path');
const ROOT = path.resolve(__dirname, '..');
const fileUrl = p => 'file://' + path.join(ROOT, p);
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const pg = await b.newPage();
  const errs = [];
  pg.on('console', m => { if (m.type()==='error') errs.push(m.text()); });
  pg.on('pageerror', e => errs.push('PAGEERROR ' + e.message));
  await pg.goto(fileUrl('dist/preview/textbook.html'));
  await pg.waitForTimeout(600);

  // 1. glossary
  await pg.click('text=용어사전');
  await pg.waitForTimeout(400);
  const gl = await pg.$$eval('.glrow', n => n.length);

  // 2. search speed + marks
  const t0 = Date.now();
  await pg.fill('#q', '고지의무');
  await pg.waitForTimeout(300);
  const t1 = Date.now() - t0;
  const hits = await pg.$$eval('.glrow.hit', n => n.length);
  const marks = await pg.$$eval('mark', n => n.length);

  // 3. click a hit -> navigates to section
  await pg.click('.glrow.hit');
  await pg.waitForTimeout(500);
  const h1 = await pg.$eval('.readhead h1', n => n.textContent.trim()).catch(()=>null);

  // 4. theme toggle
  await pg.click('.themeBtn'); await pg.waitForTimeout(250);
  const th = await pg.getAttribute('html', 'data-theme');

  // 5. box sheet
  await pg.click('.bx'); await pg.waitForTimeout(400);
  const sheetOn = await pg.$eval('#ov', n => n.classList.contains('on'));
  const sheetTitle = await pg.$eval('#sheet h2, #sheet h3, #sheet h1', n=>n.textContent.trim()).catch(()=>null);

  console.log(JSON.stringify({gl, searchMs:t1, hits, marks, h1, th, sheetOn, sheetTitle, errs}, null, 1));
  await b.close();
})();
