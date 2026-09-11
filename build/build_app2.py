# -*- coding: utf-8 -*-
"""2차 기출 앱 빌드.

data/exam2.json 에 모범답안(content/ans2_*.py)을 얹어 화면에 박는다.
1차와 같은 방식으로 배포본에는 무료 회차만 넣고, 미리보기본에는 전부 넣는다.
"""
import json
from paths import APP, DATA, PUBLIC, PREVIEW, FREE_Q2, kb

try:
    from ans2_data import ANS
except ImportError:
    ANS = {}

FREE_ROUND2 = 49          # 결제 전에 열어 두는 회차


def merge(rows):
    """문항마다 모범답안을 얹는다. 없으면 그대로 둔다.

    답안 번호가 그 과목지에 없는 번호이면 경고한다.
    소문항을 따로 번호 매겨 쓰다가 생기는 흔한 실수를 여기서 잡는다.
    """
    n = 0
    for r in rows:
        table = ANS.get((r['round'], r['subject']), {})
        nos = {q['no'] for q in r['q']}
        for bad in sorted(set(table) - nos):
            print('  ! 제%d회 %s %d번 답안 — 그런 문항이 없습니다(문항 %s)'
                  % (r['round'], r['subject'], bad, sorted(nos)))
        for q in r['q']:
            a = table.get(q['no'])
            if not a:
                continue
            q['a'] = a
            n += 1
    return n


def strip(rows, keep):
    """결제 전 배포본 — 예시 문항(FREE_Q2)만 본문·모범답안을 남기고 나머지는 번호·배점만."""
    free = set(FREE_Q2)
    out = []
    for r in rows:
        qs = []
        for q in r['q']:
            if r['round'] in keep and (r['subject'], q['no']) in free:
                qs.append(q)
            else:
                qs.append({'no': q['no'], 'points': q['points'], 'locked': True})
        opened = any(not q.get('locked') for q in qs)
        out.append({k: r[k] for k in ('round', 'subject', 'track')} |
                   {'q': qs} | ({} if opened else {'locked': True}))
    return out


def main():
    rows = json.loads((DATA / 'exam2.json').read_text(encoding='utf-8'))
    na = merge(rows)
    tpl = (APP / 'exam2.html').read_text(encoding='utf-8')

    def render(data):
        return (tpl.replace('__EXAM2__', json.dumps(data, ensure_ascii=False))
                   .replace('__FREE_ROUND2__', str(FREE_ROUND2))
                   .replace('__FREE_N2__', str(len(FREE_Q2))))

    (PUBLIC / 'exam2.html').write_text(
        render(strip(rows, {FREE_ROUND2})), encoding='utf-8')
    (PREVIEW / 'exam2.html').write_text(render(rows), encoding='utf-8')
    (DATA / 'exam2_full.json').write_text(
        json.dumps(rows, ensure_ascii=False, separators=(',', ':')),
        encoding='utf-8')

    nq = sum(len(r['q']) for r in rows)
    rounds = sorted({r['round'] for r in rows}, reverse=True)
    print('2차  과목지 %d · 문항 %d · 모범답안 %d · 회차 %s\n'
          '     배포본 %dKB(제%d회) · 미리보기 %dKB'
          % (len(rows), nq, na, ', '.join('제%d회' % r for r in rounds),
             kb(PUBLIC / 'exam2.html'), FREE_ROUND2,
             kb(PREVIEW / 'exam2.html')))


if __name__ == '__main__':
    main()
