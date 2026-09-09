# -*- coding: utf-8 -*-
"""2차 기출 PDF 를 회차·과목·문항으로 나누어 data/exam2.json 으로 만든다."""
import io, json, os, re, sys, warnings

warnings.filterwarnings('ignore')
sys.stdout.reconfigure(encoding='utf-8')
import pdfplumber

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
ROOT = os.environ.get(
    'SONSA2_PDF',
    'C:/Users/user/Downloads/손해사정사_2차_기출_40-49회')
OUT = os.path.join(PROJ, 'data', 'exam2.json')
MANUAL = os.path.join(PROJ, 'data', 'exam2_manual.json')

SUBJ = [
    ('의학이론', '의학이론', '신체'),
    ('책임근재', '책임·근로자재해보상보험의 이론과 실무', '신체'),
    ('책임보험 · 근로자재해', '책임·근로자재해보상보험의 이론과 실무', '신체'),
    ('책임·근로자재해', '책임·근로자재해보상보험의 이론과 실무', '신체'),
    ('제3보험', '제3보험의 이론과 실무', '신체'),
    ('대인배상', '자동차보험의 이론과 실무(대인배상 및 자기신체손해)', '신체'),
    ('자동차대인', '자동차보험의 이론과 실무(대인배상 및 자기신체손해)', '신체'),
    ('자동차보험(대인)', '자동차보험의 이론과 실무(대인배상 및 자기신체손해)', '신체'),
    ('회계원리', '회계원리', '재물'),
    ('해상보험', '해상보험의 이론과 실무', '재물'),
    ('책임화재기술', '책임·화재·기술보험 등의 이론과 실무', '재물'),
    ('책임 · 화재 · 기술', '책임·화재·기술보험 등의 이론과 실무', '재물'),
    ('책임·화재·기술', '책임·화재·기술보험 등의 이론과 실무', '재물'),
    ('구조정비', '자동차구조 및 정비이론과 실무', '차량'),
    ('자보대인', '자동차보험의 이론과 실무(대인배상 및 자기신체손해)', '신체'),
    ('화재등', '책임·화재·기술보험 등의 이론과 실무', '재물'),
    ('대물배상', '자동차보험의 이론과 실무(대물배상 및 차량손해)', '차량'),
    ('자동차대물', '자동차보험의 이론과 실무(대물배상 및 차량손해)', '차량'),
    ('자동차보험 대물', '자동차보험의 이론과 실무(대물배상 및 차량손해)', '차량'),
    ('자동차보험(대물)', '자동차보험의 이론과 실무(대물배상 및 차량손해)', '차량'),
    ('자동차구조', '자동차구조 및 정비이론과 실무', '차량'),
    ('자동차 구조', '자동차구조 및 정비이론과 실무', '차량'),
    ('해상', '해상보험의 이론과 실무', '재물'),
    ('의학', '의학이론', '신체'),
]

ORDER = ['의학이론', '책임·근로자재해보상보험의 이론과 실무',
         '제3보험의 이론과 실무',
         '자동차보험의 이론과 실무(대인배상 및 자기신체손해)',
         '회계원리', '해상보험의 이론과 실무',
         '책임·화재·기술보험 등의 이론과 실무',
         '자동차보험의 이론과 실무(대물배상 및 차량손해)',
         '자동차구조 및 정비이론과 실무']


def subject_of(fn):
    b = fn.replace('_', ' ')
    for key, name, kind in SUBJ:
        if key.replace('_', ' ') in b:
            return name, kind
    return None, None


HDR = re.compile(r'\(제\s*\d\d\s*회\)[^\n]{0,60}?\(\s*\d+\s*-\s*\d+\s*\)')
TITLE = re.compile(r'제\s*\d{0,2}\s*회\s*보험계리사[^\n\u3010]{0,80}?시험문제'
                   r'(?:\s*\([^)]{0,30}\))?')
BRACE = re.compile(r'\u3010[^\u3011]{0,90}\u3011')
FOOT = re.compile(r'\((?:뒷면|다음면|다음장|뒷장)[^)]{0,10}\)')
PAGEN = re.compile(r'(?m)^\s*-?\s*\d{1,3}\s*-?\s*$')
RUN = re.compile(r'(?m)^\s*\(?제\s*\d{0,2}\s*회\)?[^\n]{0,50}$')


def clean(t):
    for rx in (HDR, TITLE, BRACE, FOOT):
        t = rx.sub('\n', t)
    out = []
    for ln in t.split('\n'):
        s = ln.strip()
        if not s:
            out.append('')
            continue
        if re.fullmatch(r'-?\s*\d{1,3}\s*-?', s):
            continue
        if re.fullmatch(r'\(?제\s*\d{0,2}\s*회\)?\s*[^\n]{0,45}', s) and \
           re.match(r'\(?제\s*\d{0,2}\s*회\)?', s) and len(s) < 50 and \
           ('회' in s) and not re.search(r'[.?!점]$', s):
            continue
        if re.fullmatch(r'\d{4}\s*년도\s*시행', s):
            continue
        out.append(re.sub(r'[ \t]+', ' ', s))
    t = '\n'.join(out)
    return re.sub(r'\n{3,}', '\n\n', t).strip()


CAND = re.compile(r'(\d{1,2})\s*\.(?=\s|[^\d\s])')
BAD_PREV = set('0123456789.,%-\u2013\u2014')
TABLE_NO = re.compile(r'(?:<|\[|\(|별)?\s*표\s*$')
NEXT_NUM = re.compile(r'\s*\d{1,2}\s*\.\s')
DATE_TAIL = re.compile(r'(?:19|20)\d\d\s*[.년]\s*\d{1,2}\s*[.월]\s*$')
# 2023. 5. 2. / 2023년 5월 2일 처럼 날짜 전체를 이루는 구간
DATE_SPAN = re.compile(r'(?:19|20)\d\d\s*[.년]\s*\d{1,2}\s*[.월]\s*\d{1,2}\s*[.일]?')
SUBQ = re.compile(r'\(\s*1\s*\)|(?<![0-9(])1\s*\)')
TOTPT = re.compile(r'총\s*(\d{1,3})\s*점')
PT = re.compile(r'(\d{1,3}(?:\.\d)?)\s*점')


LABEL = re.compile(r'\d{1,2}\s*\.\s*[^\n:]{0,22}:')


def chain_of(t):
    """1,2,3... 으로 이어지고 구간마다 배점 표시가 있는 사슬을 고른다.
    표 안의 '2. 피보험자 :' 같은 항목줄은 점수를 낮게 주어 밀어낸다."""
    spans = [(m.start(), m.end()) for m in DATE_SPAN.finditer(t)]

    def in_date(i):
        return any(a < i < b for a, b in spans)

    cs = []
    for m in CAND.finditer(t):
        i = m.start()
        if i and t[i - 1] in BAD_PREV:
            continue
        if DATE_TAIL.search(t[max(0, i - 16):i]) or in_date(i):
            continue          # '2023. 5. 2.' 처럼 날짜 안의 숫자인 경우
        if NEXT_NUM.match(t, m.end()):
            continue          # '~ 7. 20.' 처럼 뒤에 또 숫자가 이어지는 경우
        if TABLE_NO.search(t[max(0, i - 6):i]):
            continue          # '<표2. 보험가액>' 처럼 표 번호인 경우
        line = t[i:t.find('\n', i) if t.find('\n', i) > 0 else len(t)]
        pt = 1 if PT.search(t[i:i + 300]) else 0
        lab = 1 if LABEL.match(line) else 0
        cs.append((int(m.group(1)), i, (0 if lab else 1) + pt))
    n = len(cs)
    if not n:
        return []
    marks = [m.start() for m in PT.finditer(t)]

    def has_pt(lo, hi):
        return any(lo <= x < hi for x in marks)

    NEG = -10 ** 6
    score = [cs[i][2] if has_pt(cs[i][1], len(t)) else NEG for i in range(n)]
    cnt = [1 if score[i] > NEG else 0 for i in range(n)]
    nxt = [-1] * n
    for i in range(n - 1, -1, -1):
        for j in range(i + 1, n):
            if cs[j][0] != cs[i][0] + 1 or score[j] <= 0 and cnt[j] == 0:
                continue
            if score[j] <= NEG or not has_pt(cs[i][1], cs[j][1]):
                continue
            cand = (score[j] + cs[i][2], cnt[j] + 1)
            if cand > (score[i], cnt[i]):
                score[i], cnt[i], nxt[i] = cand[0], cand[1], j
    head, hb = -1, (0, 0)
    for i in range(n):
        if cs[i][0] == 1 and (score[i], cnt[i]) > hb:
            head, hb = i, (score[i], cnt[i])
    pos, i = [], head
    while i >= 0:
        pos.append(cs[i][1])
        i = nxt[i]
    return pos


def fit100(cands):
    reach = {0: []}
    for opts in cands:
        cur = {}
        for tot, pick in reach.items():
            for v in opts:
                nt = tot + v
                if nt <= 100 and nt not in cur:
                    cur[nt] = pick + [v]
        reach = cur
        if not reach:
            return None
    return reach.get(100)


def split_q(t):
    pos = chain_of(t)
    segs = []
    for k, s0 in enumerate(pos):
        e = pos[k + 1] if k + 1 < len(pos) else len(t)
        segs.append(re.sub(r'^\d{1,2}\s*\.\s*', '', t[s0:e].strip()))
    cands = []
    for body in segs:
        pts = [float(x) for x in PT.findall(body)]
        pts = [int(p) if p == int(p) else p for p in pts]
        if not pts:
            cands.append([0])
            continue
        opts = []
        m = SUBQ.search(body)
        head = body[:m.start()] if m else body   # 첫 물음((1) 또는 1)) 앞이 문두이다
        h = [float(x) for x in PT.findall(head)]
        tot = TOTPT.findall(head)
        if tot:
            # '각 2점, 총 10점' — 마지막에 밝힌 총점이 그 문항의 배점이다
            opts.append(int(tot[-1]))
        if len(h) >= 2:
            if abs(h[-1] - sum(h[:-1])) < 1e-9:
                # '…(4점) …(3점) …(3점) 기술하시오.(10점)' — 끝의 숫자가 합계이다
                order = [h[-1], sum(h)]
            else:
                # '…쓰시오.(4점) … 쓰시오.(6점)' — 부분점수를 더한 것이 배점이다
                order = [sum(h), h[-1]]
        elif h:
            order = [h[0]]
        else:
            order = []
        order += [max(pts), pts[-1], pts[0], sum(pts)]
        for v in order:
            if float(v).is_integer() and int(v) not in opts:
                opts.append(int(v))
        if not opts:
            # '각 2.5점' 처럼 정수 후보가 하나도 없을 때만 5의 배수를 열어 둔다.
            # 모든 문항에 열어 두면 조합이 너무 많아져 엉뚱한 답이 먼저 잡힌다.
            opts = list(range(10, 41, 5)) + [5]
        cands.append(opts)
    fixed = fit100(cands) if len(cands) <= 20 else None
    out = []
    for k, body in enumerate(segs):
        pts = [float(x) for x in PT.findall(body)]
        out.append({'no': k + 1, 'body': body,
                    'sub': [int(p) if p == int(p) else p for p in pts],
                    'points': fixed[k] if fixed else
                              (int(max(pts)) if pts else 0)})
    return out, bool(fixed)


rows, skipped = [], []
for rd in sorted(os.listdir(ROOT)):
    m = re.match(r'제(\d\d)회$', rd)
    if not m:
        continue
    rnd = int(m.group(1))
    qd = os.path.join(ROOT, rd, '문제')
    if not os.path.isdir(qd):
        continue
    for fn in sorted(os.listdir(qd)):
        if not fn.lower().endswith('.pdf'):
            continue
        name, kind = subject_of(fn)
        if not name:
            skipped.append((rnd, fn))
            continue
        with pdfplumber.open(os.path.join(qd, fn)) as pdf:
            raw = '\n'.join(p.extract_text() or '' for p in pdf.pages)
        t = clean(raw)
        qs, ok = split_q(t)
        digits = len(re.findall(r'\d', t))
        rows.append({'round': rnd, 'subject': name, 'track': kind,
                     'src': fn, 'chars': len(t), 'digits': digits,
                     'pts_ok': ok, 'q': qs})

# 배점이 잘못 잡힌 과목지를 손으로 바로잡는다.
# 합이 100이 되어 검사를 통과하더라도 문항별로는 틀릴 수 있다.
POINTS_FIX = {
    # 제43회 의학이론은 열 문항이 모두 10점인데, 소문항 배점이 섞여 들어갔다
    (43, '의학이론'): [10] * 10,
    # 제40회 의학이론도 열 문항이 모두 10점이다(소문항 5+5, 8+2 등이 섞여 들어갔다)
    (40, '의학이론'): [10] * 10,
}
for r in rows:
    fix = POINTS_FIX.get((r['round'], r['subject']))
    if fix and len(fix) == len(r['q']):
        for q, pt in zip(r['q'], fix):
            q['points'] = pt

# 글자층에서 숫자가 빠진 과목지는 손으로 옮겨 적은 파일로 갈음한다
if os.path.exists(MANUAL):
    man = json.load(io.open(MANUAL, encoding='utf-8'))
    idx = {(r['round'], r['subject']): i for i, r in enumerate(rows)}
    for m in man:
        key = (m['round'], m['subject'])
        if key in idx:
            rows[idx[key]].update(m)
            rows[idx[key]]['manual'] = True
        else:
            m['manual'] = True
            rows.append(m)

rows.sort(key=lambda r: (-r['round'], ORDER.index(r['subject'])))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
io.open(OUT, 'w', encoding='utf-8', newline='\n').write(
    json.dumps(rows, ensure_ascii=False, indent=1))

nq = sum(len(r['q']) for r in rows)
print('과목지 %d개 · 문항 %d개 → %s\n' % (len(rows), nq, OUT))
bad = [r for r in rows if len(r['q']) < 3 or not r['pts_ok']]
print('손봐야 할 과목지 %d / %d' % (len(bad), len(rows)))
for r in bad:
    print('  제%d회 %-42s 문항 %2d · 배점합 %3d · 숫자 %4d'
          % (r['round'], r['subject'][:42], len(r['q']),
             sum(q['points'] for q in r['q']), r['digits']))
for rnd, fn in skipped:
    print('  과목 미상: 제%d회 %s' % (rnd, fn))
