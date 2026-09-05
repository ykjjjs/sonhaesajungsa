# -*- coding: utf-8 -*-
"""기출 앱 빌드.

배포본(public/index.html)에는 **무료 회차만** 박는다. 나머지는 이용권이 있어야
/api/content 로 내려온다. 소스를 열어도 전체 600문항이 나오지 않게 하는 것이 요점이다.
미리보기본(dist/preview)에는 전체를 박아 오프라인으로 확인할 수 있게 한다.
"""
import json
from paths import APP, DATA, PUBLIC, PREVIEW, FREE_YEAR, PRICE, kb
from book_data import TERMS, BOOK

try:
    from exam_map import MAP as EXAM_MAP
except ImportError:
    EXAM_MAP = {}

def count(c):
    return sum(len(v) for y in c.values() for s in y.values() for v in s.values())

def book_links():
    """문항 → 교재 절. 절 목록을 따로 두고 문항은 그 번호만 가리킨다(용량 절약)."""
    seclist, index = [], {}
    for subj, b in BOOK.items():
        for ci, c in enumerate(b['chapters']):
            for si, s in enumerate(c['sections']):
                index[(subj, ci, si)] = len(seclist)
                seclist.append([subj, ci, si, c['title'], s['title']])
    qbook = {}
    for addr, rows in EXAM_MAP.items():
        i = index.get(tuple(addr))
        if i is None:
            continue
        for r in rows:
            qbook['%d|%s|%d' % (r['r'], r['s'], r['n'])] = i
    return seclist, qbook

def main():
    tpl = (APP / 'index.html').read_text(encoding='utf-8')
    seclist, qbook = book_links()
    content = json.loads((DATA / 'exam.json').read_text(encoding='utf-8'))
    sample = {FREE_YEAR: content[FREE_YEAR]} if FREE_YEAR in content else {}
    assert sample, f'{FREE_YEAR} 회차를 찾지 못했습니다'

    # 긴 용어부터 — '보험자대위'가 '보험자'보다 먼저 걸려야 한다
    terms = sorted((t for t in TERMS if len(t) >= 3), key=len, reverse=True)

    def render(data):
        return (tpl.replace('__CONTENT__', json.dumps(data, ensure_ascii=False))
                   .replace('__TERMLINK__', json.dumps(terms, ensure_ascii=False))
                   .replace('__SECLIST__', json.dumps(seclist, ensure_ascii=False))
                   .replace('__QBOOK__', json.dumps(qbook, ensure_ascii=False,
                                                    separators=(',', ':')))
                   .replace('__FREE_YEAR__', json.dumps(FREE_YEAR))
                   .replace('__PRICE__', str(PRICE)))

    (PUBLIC / 'index.html').write_text(render(sample), encoding='utf-8')
    (PREVIEW / 'exam.html').write_text(render(content), encoding='utf-8')
    (DATA / 'sample_exam.json').write_text(
        json.dumps(sample, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

    print(f'기출  배포본 {count(sample)}문항({FREE_YEAR}년) {kb(PUBLIC / "index.html")}KB · '
          f'미리보기 {count(content)}문항 {kb(PREVIEW / "exam.html")}KB · '
          f'용어링크 {len(terms)} · 교재연결 {len(qbook)}문항 · {PRICE:,}원')

if __name__ == '__main__':
    main()
