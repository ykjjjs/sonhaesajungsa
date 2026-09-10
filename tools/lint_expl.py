# -*- coding: utf-8 -*-
"""1차 해설 점검 — 확정답안과 대조하고 태그 균형을 본다.

  1) 해설 첫머리의 '정답은 ○이다'가 data/exam.json 의 정답과 같은가
  2) w 의 키가 오답 보기 세 개와 정확히 일치하는가
  3) <b> 등 태그가 짝을 이루는가
  4) 빈 해설이나 빈 오답풀이가 없는가

사용
  python tools/lint_expl.py            전체
  python tools/lint_expl.py 48         한 회차만
"""
import json
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'content'))

SUBJ = {'bul': '보험업법', 'bkl': '보험계약법', 'sst': '손해사정이론'}
ROUNDS = (45, 46, 47, 48, 49)
YEAR = {45: '2022', 46: '2023', 47: '2024', 48: '2025', 49: '2026'}
CIRCLE = {'①': 1, '②': 2, '③': 3, '④': 4, '⑤': 5}
TAGS = ('b', 'i', 'u', 'p', 'ul', 'ol', 'li', 'span')


def load_exam():
    with open(ROOT / 'data' / 'exam.json', encoding='utf-8') as f:
        return json.load(f)


def tag_balance(html):
    bad = []
    for t in TAGS:
        o = len(re.findall(r'<%s[ >]' % t, html))
        c = len(re.findall(r'</%s>' % t, html))
        if o != c:
            bad.append('%s %d/%d' % (t, o, c))
    return bad


def main():
    only = {int(a) for a in sys.argv[1:] if a.isdigit()}
    exam = load_exam()
    import importlib
    total = flaws = 0
    for r in ROUNDS:
        if only and r not in only:
            continue
        for abbr, subj in SUBJ.items():
            try:
                mod = importlib.import_module('expl_%d_%s' % (r, abbr))
            except ImportError:
                continue
            table = getattr(mod, 'EXPL_%d_%s' % (r, abbr.upper()), None)
            if not table:
                continue
            qs = exam.get(YEAR[r], {}).get('1차 1교시', {}).get(subj, [])
            key = {q['no']: q['answer'] + 1 for q in qs}
            hits = []
            for no in sorted(table):
                v = table[no]
                total += 1
                e = (v.get('e') or '').strip()
                w = v.get('w') or {}
                if not e:
                    hits.append('%2d 해설이 비었다' % no)
                    continue
                m = re.match(r'\s*정답은\s*([①-⑤])', e)
                said = CIRCLE[m.group(1)] if m else None
                multi = '복수정답' in e[:80]
                right = key.get(no)
                if right is None:
                    hits.append('%2d 원문 문항을 찾지 못하였다' % no)
                elif multi:
                    pass
                elif said is None:
                    hits.append('%2d 첫머리에 정답 표시가 없다' % no)
                elif said != right:
                    hits.append('%2d 정답 불일치, 확정 %d, 해설 %d' % (no, right, said))
                if right:
                    want = sorted(set(range(1, len(qs[no - 1]['choices']) + 1)) - {right})
                    got = sorted(int(k) for k in w)
                    if got != want:
                        hits.append('%2d 오답키 %s, 있어야 할 것 %s' % (no, got, want))
                for k, t in w.items():
                    if not (t or '').strip():
                        hits.append('%2d 보기 %s 풀이가 비었다' % (no, k))
                for name, html in [('e', e)] + [('w%s' % k, t) for k, t in w.items()]:
                    bad = tag_balance(html or '')
                    if bad:
                        hits.append('%2d %s 태그 불균형 %s' % (no, name, ', '.join(bad)))
            miss = [n for n in range(1, len(qs) + 1) if n not in table] if qs else []
            mark = '흠 없음' if not hits else '%d건' % len(hits)
            print('제%d회 %s  %d/%d  %s%s' % (
                r, subj, len(table), len(qs), mark,
                '  미작성 %s' % miss if miss else ''))
            for h in hits:
                print('   ', h)
            flaws += len(hits)
    print('\n해설 %d개, 흠 %d건' % (total, flaws))
    return 1 if flaws else 0


if __name__ == '__main__':
    sys.exit(main())
