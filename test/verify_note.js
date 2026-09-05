const path = require('path');
const ROOT = path.resolve(__dirname, '..');
const fileUrl = p => 'file://' + path.join(ROOT, p);
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const pg = await b.newPage();
  const errs = [];
  pg.on('pageerror', e => errs.push('PAGEERROR ' + e.message));
  pg.on('console', m => { if (m.type()==='error' && !/ERR_CONNECTION/.test(m.text())) errs.push(m.text()); });
  await pg.goto(fileUrl('public/index.html'));
  await pg.waitForTimeout(600);
  const out = {};

  // 시드: 오답 이력을 다양한 시점으로 심는다
  out.seeded = await pg.evaluate(() => {
    const D = 864e5, now = Date.now();
    const pick = (n, off) => BANK.filter((q,i)=>i%off===0).slice(0,n);
    let k = 0;
    const plant = (q, no, daysAgo, pickIdx) => {
      S.seen[q.id] = { ok:0, no, last:'no', at: now - daysAgo*D, noAt: now - daysAgo*D, pick: pickIdx };
    };
    pick(6,7).forEach((q,i)=>plant(q, 1, 0, (q.answer+1)%4));      // 오늘 틀림
    pick(5,11).forEach((q,i)=>plant(q, 1, 2, (q.answer+2)%4));     // 하루 지남
    pick(4,17).forEach((q,i)=>plant(q, 2, 5, (q.answer+1)%4));     // 3일 지남
    pick(3,23).forEach((q,i)=>plant(q, 3, 9, (q.answer+3)%4));     // 1주 지남
    pick(2,31).forEach((q,i)=>plant(q, 4, 20, (q.answer+1)%4));    // 2주 넘김
    // 맞힌 이력도 섞어 정답률이 계산되게
    BANK.slice(300,340).forEach(q => { S.seen[q.id] = { ok:1, no:0, last:'ok', at: now }; });
    S.star[BANK[0].id] = true; S.star[BANK[7].id] = true;
    S.note[BANK[7].id] = '대주주·자회사만 자기자본 기준.';
    return { wrong: wrongCount(), due: dueCount(), star: starCount() };
  });

  // 노트 탭 열기
  await pg.click('#tabNote'); await pg.waitForTimeout(400);
  out.tabBadge = await pg.textContent('#tabNoteN');
  out.cards = await pg.$$eval('.ncard b', n => n.map(x=>x.textContent));
  out.dueChips = await pg.$$eval('.duechip', n => n.map(x=>x.textContent.trim()));
  out.weakBars = await pg.$$eval('.wk', n => n.map(x=>x.textContent.replace(/\s+/g,' ').trim()));
  out.groups = await pg.$$eval('.grp > h3', n => n.map(x=>x.textContent.trim()));
  out.rows = await pg.$$eval('.nrow', n => n.length);
  out.miniRows = await pg.$$eval('.mini', n => n.length);
  out.memoShown = await pg.$$eval('.nrow .memo', n => n.map(x=>x.textContent.trim()));
  out.quizBarHidden = await pg.$eval('#quizBar', n => getComputedStyle(n).display);

  // 필터 칩
  await pg.click('[data-nf="rep"]'); await pg.waitForTimeout(250);
  out.repRows = await pg.$$eval('.nrow', n => n.length);
  await pg.click('[data-nf="star"]'); await pg.waitForTimeout(250);
  out.starRows = await pg.$$eval('.nrow', n => n.length);
  await pg.click('[data-nf="all"]'); await pg.waitForTimeout(250);

  // 별표 토글
  const before = await pg.evaluate(()=>starCount());
  await pg.click('.nrow .starBtn'); await pg.waitForTimeout(250);
  out.starToggle = [before, await pg.evaluate(()=>starCount())];

  // 행 클릭 → 문항으로 점프
  await pg.click('.nrow'); await pg.waitForTimeout(400);
  out.jumped = { view: await pg.evaluate(()=>S.view), mode: await pg.evaluate(()=>S.mode),
                 stem: (await pg.textContent('.stem')||'').slice(0,28) };

  // 오늘 복습 시작
  await pg.click('#tabNote'); await pg.waitForTimeout(300);
  await pg.click('#startDue'); await pg.waitForTimeout(400);
  out.dueMode = await pg.evaluate(()=>({mode:S.mode, n:list().length}));

  // 정답을 골라 확인 → 노트에서 졸업하는지 (실제 UI 경로로)
  const g0 = await pg.evaluate(() => {
    const q = list()[S.pos]; return { id:q.id, ans:q.answer, before: wrongCount() }; });
  await pg.click(`.opt[data-i="${g0.ans}"]`); await pg.waitForTimeout(120);
  await pg.click('#nextBtn'); await pg.waitForTimeout(350);
  out.graduate = await pg.evaluate(id => ({
    before: null, after: wrongCount(), last: S.seen[id].last, pick: S.seen[id].pick }), g0.id);
  out.graduate.before = g0.before;
  out.verdictSeen = await pg.textContent('.verdict').catch(()=>null);
  out.verdictIsSameQ = await pg.evaluate(id => list()[S.pos].id === id, g0.id);

  // 다음 문항으로 넘어간 뒤(2단계) 오답을 골라 해설·메모·교재 링크 확인
  await pg.click('#nextBtn'); await pg.waitForTimeout(300);
  const bad = await pg.evaluate(() => (list()[S.pos].answer + 1) % 4);
  await pg.click(`.opt[data-i="${bad}"]`); await pg.waitForTimeout(120);
  await pg.click('#nextBtn'); await pg.waitForTimeout(350);
  out.memoBox = await pg.$eval('#memo', n => n.dataset.memo).catch(()=>null);
  await pg.fill('#memo', '자기자본 기준은 대주주·자회사뿐.');
  await pg.waitForTimeout(150);
  out.memoSaved = await pg.evaluate(()=>{const k=document.getElementById('memo').dataset.memo; return S.note[k];});
  out.bookLinks = await pg.$$eval('.blink', n => n.map(x=>x.getAttribute('href')));

  // 저장 왕복
  out.roundtrip = await pg.evaluate(() => {
    const snap = snapshot();
    const n0 = Object.keys(S.note).length, s0 = starCount(), w0 = wrongCount();
    S.sel={}; S.seen={}; S.note={}; S.star={};
    applyState(JSON.parse(JSON.stringify(snap)));
    return { v: snap.v, notes:[n0, Object.keys(S.note).length],
             stars:[s0, starCount()], wrong:[w0, wrongCount()] };
  });

  // 'n' 단축키
  await pg.keyboard.press('n'); await pg.waitForTimeout(250);
  out.hotkey = await pg.evaluate(()=>S.view);

  out.errs = errs;
  console.log(JSON.stringify(out, null, 1));
  await b.close();
})();
