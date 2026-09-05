# -*- coding: utf-8 -*-
"""수험서 문체 점검 — 교재 원고에서 비유·구어·화자개입 표현을 찾는다.

붙잡히는 것들
  1) 비유·의인   : 덮쳐 온다 / 제자리를 찾는다 / 붙잡는다 / 뭉치 / 도려낸 ...
  2) 청유·권유   : ~해 보자 / ~해 두자 / ~하자 / ~기 바란다
  3) 화자 개입   : 우리 / 여러분 / 필자 / 기억해 두자
  4) 정서·과장   : 결정적이다 / 무너진다 / 흔들린다 / 전부다
  5) 줄표 남용   : 한 문단에 ― 또는 — 가 두 번 이상
"""
import re, sys, pathlib

PATTERNS = [
 ('비유', r'덮쳐|제자리를 찾|붙잡[는아어]|뭉치|도려낸|무너진다|흔들린다|튀[던는]|새어 나가|살아 있다|앉[는아]\s|끌어당|당긴다|걸려 있다|열어 두었다|박[아혀]\s|따라온다|수렴한다|의 지도|지도를 그리|큰 지도'),
 ('청유', r'해\s?보자|해\s?두자|하자[.,]|보자[.,]|두자[.,]|기억하자|외우자|잡아\s?두자|바란다'),
 ('화자', r'우리[가는의]|여러분|필자|당신'),
 ('과장', r'결정적이다|전부다|점수를 지킨다|반드시 틀린다|틀리기 십상|여기서 갈린다'),
 ('구어', r'~?하면 된다\.|셈이다|편이 안전하다|편이 낫다|보면 된다'),
]

def scan(path):
    src = path.read_text(encoding='utf-8')
    hits = []
    for ln, line in enumerate(src.splitlines(), 1):
        for name, pat in PATTERNS:
            for m in re.finditer(pat, line):
                hits.append((ln, name, m.group(0), line.strip()[:110]))
        if line.count('—') >= 2:
            hits.append((ln, '줄표', '—×%d' % line.count('—'), line.strip()[:110]))
    return hits

def main():
    root = pathlib.Path(__file__).resolve().parents[1] / 'content'
    files = sorted(root.glob('*.py'))
    if len(sys.argv) > 1:
        files = [root / a for a in sys.argv[1:]]
    total = 0
    for f in files:
        hits = scan(f)
        if not hits:
            continue
        total += len(hits)
        print(f'\n── {f.name}  ({len(hits)}건)')
        for ln, name, word, ctx in hits:
            print(f'  {ln:>4} [{name}] {word}   … {ctx}')
    print(f'\n합계 {total}건')
    return 1 if total else 0

if __name__ == '__main__':
    sys.exit(main())
