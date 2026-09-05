# -*- coding: utf-8 -*-
"""기출 앱 빌드.

배포본(public/index.html)에는 **무료 회차만** 박는다. 나머지는 이용권이 있어야
/api/content 로 내려온다. 소스를 열어도 전체 600문항이 나오지 않게 하는 것이 요점이다.
미리보기본(dist/preview)에는 전체를 박아 오프라인으로 확인할 수 있게 한다.
"""
import json
from paths import APP, DATA, PUBLIC, PREVIEW, FREE_YEAR, PRICE, kb
from book_data import TERMS

def count(c):
    return sum(len(v) for y in c.values() for s in y.values() for v in s.values())

def main():
    tpl = (APP / 'index.html').read_text(encoding='utf-8')
    content = json.loads((DATA / 'exam.json').read_text(encoding='utf-8'))
    sample = {FREE_YEAR: content[FREE_YEAR]} if FREE_YEAR in content else {}
    assert sample, f'{FREE_YEAR} 회차를 찾지 못했습니다'

    # 긴 용어부터 — '보험자대위'가 '보험자'보다 먼저 걸려야 한다
    terms = sorted((t for t in TERMS if len(t) >= 3), key=len, reverse=True)

    def render(data):
        return (tpl.replace('__CONTENT__', json.dumps(data, ensure_ascii=False))
                   .replace('__TERMLINK__', json.dumps(terms, ensure_ascii=False))
                   .replace('__FREE_YEAR__', json.dumps(FREE_YEAR))
                   .replace('__PRICE__', str(PRICE)))

    (PUBLIC / 'index.html').write_text(render(sample), encoding='utf-8')
    (PREVIEW / '기출.html').write_text(render(content), encoding='utf-8')
    (DATA / 'sample_exam.json').write_text(
        json.dumps(sample, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

    print(f'기출  배포본 {count(sample)}문항({FREE_YEAR}년) {kb(PUBLIC / "index.html")}KB · '
          f'미리보기 {count(content)}문항 {kb(PREVIEW / "기출.html")}KB · '
          f'용어링크 {len(terms)} · {PRICE:,}원')

if __name__ == '__main__':
    main()
