# -*- coding: utf-8 -*-
"""기출 문항과 교재 절을 잇는 대응표를 만든다.

판정 근거는 셋이다.
  1. 조문 번호 일치 — 가장 강한 신호(제4조, 제651조 …)
  2. 절을 특징짓는 낱말 일치 — 55개 절에 대한 TF·IDF 로 뽑는다
  3. 같은 과목 여부 — 다른 과목의 절은 감점한다

결과는 content/exam_map.py 로 저장한다. 자동 판정이므로 점수를 함께 남겨
낮은 점수의 대응은 사람이 다시 볼 수 있게 한다.
"""
import json, re, sys, math, html as H, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'content'))
from book_data import BOOK                                    # noqa: E402

EXAM = json.load(open(ROOT / 'data' / 'exam.json', encoding='utf-8'))
YEAR2R = {'2022': 45, '2023': 46, '2024': 47, '2025': 48, '2026': 49}

TAG = re.compile(r'<[^>]+>')
JO = re.compile(r'제\s?(\d+)조(?:의\s?(\d+))?')
WORD = re.compile(r'[가-힣]{2,10}|[A-Za-z][A-Za-z\-]{2,}')

# 문항 어디에나 나오는 껍데기 낱말 — 변별력이 없다
STOP = set("""관한 설명으로 옳지 않은 것은 모두 고른 다음 경우 내용으로 옳은 해당하는
아닌 것을 것이 가장 거리가 개인가 아래 보기 순서대로 바르게 나열한 들어갈 내용
대하여 대한 따른 따라 관하여 있는 없는 하는 하지 한다 된다 이다 그리고 또는 다만
경우에 때에는 위하여 통하여 등의 등을 등이 라고 이라 하여야 하여도 수는 수가 문제
보험 보험자 보험계약 계약 회사 규정 조항 법률 다음의 이러한 그러한 어느 무엇 얼마
설명 기술 진술 지문 답안 정답 문항""".split())


def plain(s):
    return H.unescape(TAG.sub(' ', s))


def sections():
    for subj, b in BOOK.items():
        for ci, c in enumerate(b['chapters']):
            for si, s in enumerate(c['sections']):
                yield (subj, ci, si), c, s


def tokens(text):
    return [w for w in WORD.findall(text) if w not in STOP]


def build_vectors():
    """절마다 특징 낱말 가중치와 조문 집합을 만든다."""
    raw, jos, titles = {}, {}, {}
    for addr, c, s in sections():
        body = ' '.join([s['title'], s.get('desc', ''), s.get('lead', ''),
                         plain(s['html']),
                         ' '.join(q + ' ' + plain(a) for q, a in s.get('cards', []))])
        raw[addr] = collections.Counter(tokens(body))
        jos[addr] = {(m.group(1), m.group(2) or '') for m in JO.finditer(body + ' ' + s.get('src', ''))}
        titles[addr] = (c['title'], s['title'])

    n = len(raw)
    df = collections.Counter()
    for cnt in raw.values():
        df.update(cnt.keys())

    vec = {}
    for addr, cnt in raw.items():
        w = {}
        for t, f in cnt.items():
            if df[t] > n * 0.5:            # 절 절반 이상에 나오면 변별력이 없다
                continue
            w[t] = (1 + math.log(f)) * math.log(n / df[t])
        top = dict(sorted(w.items(), key=lambda kv: -kv[1])[:120])
        norm = math.sqrt(sum(v * v for v in top.values())) or 1.0
        vec[addr] = {t: v / norm for t, v in top.items()}
    return vec, jos, titles


def questions():
    for y in EXAM:
        for sess in EXAM[y]:
            for subj, lst in EXAM[y][sess].items():
                for q in lst:
                    yield y, subj, q


# 자동 판정이 빗나간 문항을 손으로 바로잡는다. (회차, 과목, 번호) → (과목, 장, 절)
OVERRIDE = {
    (49, '보험업법', 1): ('보험업법', 0, 0),          # 용어의 정의 종합
    (47, '보험업법', 2): ('보험업법', 0, 0),          # 용어의 정의 종합
    (45, '보험계약법', 1): ('보험계약법', 0, 0),      # 상법 제4편의 적용·준용 범위
    (47, '손해사정이론', 35): ('손해사정이론', 4, 2),  # run-off 등 특약조항
}

# 이 점수에 못 미치면 아예 붙이지 않는다. 틀린 연결은 없느니만 못하다.
FLOOR = 0.15


def main():
    vec, jos, titles = build_vectors()
    out = collections.defaultdict(list)
    low = []

    for y, subj, q in questions():
        blob = q['q'] + ' ' + ' '.join(q['choices'])
        qt = set(tokens(blob))
        qjo = {(m.group(1), m.group(2) or '') for m in JO.finditer(blob)}
        best = []
        for addr, w in vec.items():
            sc = sum(w[t] for t in qt if t in w)
            hit = qjo & jos[addr]
            if hit:
                sc += 0.35 * len(hit)
            if addr[0] != subj:
                sc *= 0.55                 # 다른 과목의 절은 감점
            best.append((sc, addr))
        best.sort(key=lambda x: -x[0])
        sc, addr = best[0]
        fixed = OVERRIDE.get((YEAR2R[y], subj, q['no']))
        if fixed:
            addr, sc = fixed, max(sc, 1.0)
        elif sc < FLOOR:
            low.append((y, subj, q['no'], round(sc, 3), addr))
            continue
        rec = {'y': y, 'r': YEAR2R[y], 's': subj, 'n': q['no'],
               'score': round(sc, 3), 'q': q['q'][:70].replace('\n', ' ')}
        out[addr].append(rec)

    for addr in out:
        out[addr].sort(key=lambda r: (r['r'], r['n']))

    lines = ['# -*- coding: utf-8 -*-',
             '"""기출 문항 ↔ 교재 절 대응표 — tools/build_map.py 가 만든다.',
             '',
             '키는 (과목, 장 번호, 절 번호), 값은 그 절이 다루는 기출 문항이다.',
             '직접 고치지 말고 tools/build_map.py 를 고친 뒤 다시 만든다."""',
             '',
             'MAP = {']
    for addr in sorted(out, key=lambda a: (a[0], a[1], a[2])):
        lines.append(' %r: [' % (addr,))
        for r in out[addr]:
            lines.append('   {"r": %d, "s": %r, "n": %d, "score": %s, "q": %r},'
                         % (r['r'], r['s'], r['n'], r['score'], r['q']))
        lines.append(' ],')
    lines.append('}')
    (ROOT / 'content' / 'exam_map.py').write_text('\n'.join(lines) + '\n', encoding='utf-8')

    tot = sum(len(v) for v in out.values())
    print('대응 %d / 600 · 절 %d / %d · 점수가 낮아 붙이지 않은 문항 %d건'
          % (tot, len(out), len(vec), len(low)))
    empty = [a for a in vec if a not in out]
    if empty:
        print('기출이 붙지 않은 절 %d개' % len(empty))
        for a in empty:
            print('   ', a, titles[a][1])
    print('절당 문항 수 상위')
    for n, a in sorted(((len(v), a) for a, v in out.items()), reverse=True)[:10]:
        print('   %3d  %-34s %s' % (n, titles[a][1], a))
    print('붙이지 않은 문항 (앞 12건 — OVERRIDE 에 손으로 넣으면 살아난다)')
    for y, subj, no, sc, addr in low[:12]:
        print('   제%d회 %s %s번  %.3f  (최선 후보 %s)' % (YEAR2R[y], subj, no, sc, titles[addr][1]))


main()
