# -*- coding: utf-8 -*-
"""미리보기본을 claude.ai 아티팩트로 발행할 형태로 변환.

아티팩트는 <!doctype>…<head>…<body> 를 발행 시점에 감싸므로 껍데기를 벗기고,
CSP 상 스타일시트는 fonts.googleapis.com 만 허용되므로 Pretendard CDN 링크를 뺀다
(폴백 스택에 -apple-system / Apple SD Gothic Neo / system-ui 가 이미 들어 있다).

    python3 build/build_artifact.py                      → dist/artifact/{exam,book}.html
    python3 build/build_artifact.py <교재URL> <기출URL>   → 두 판을 서로 잇는다

아티팩트는 별개의 주소로 발행되므로 상대경로 링크가 통하지 않는다. 두 URL 을 주면
기출 → 교재('교재에서 읽기'), 교재 → 기출('이 절에서 출제된 기출')을 절대주소로 바꾸고,
쿼리스트링이 넘어오지 않는 환경을 대비해 해시(#)로도 읽게 만든다.
"""
import re, sys
from paths import PREVIEW, ARTIFACT, kb

FONT = re.compile(r'<link rel="stylesheet" href="https://cdn\.jsdelivr\.net[^>]*>\s*')
HEADCUT = re.compile(r'^.*?<title>(.*?)</title>\s*', re.S)
METAS = re.compile(r'<meta[^>]*>\s*')

def strip(src):
    s = src.read_text(encoding='utf-8')
    m = HEADCUT.match(s)
    title, s = m.group(1), s[m.end():]
    s = METAS.sub('', s, count=3)
    s = FONT.sub('', s)
    s = s.replace('</head>\n<body>', '', 1).replace('</head>', '', 1)
    s = re.sub(r'<body[^>]*>\s*', '', s, count=1)
    s = re.sub(r'\s*</body>\s*</html>\s*$', '\n', s)
    assert '<!DOCTYPE' not in s and '<head>' not in s, '껍데기가 남았습니다'
    assert 'jsdelivr' not in s, '차단되는 CDN 링크가 남았습니다'
    # 호스트가 root 에 찍어 둔 data-theme 을 첫 로드에 존중한다
    s = s.replace("(mq.matches ? 'light' : 'dark')",
                  "(document.documentElement.getAttribute('data-theme') || (mq.matches ? 'light' : 'dark'))")
    return f'<title>{title}</title>\n' + s

HASH_READ = ("new URLSearchParams(location.search.slice(1) + '&' + location.hash.slice(1))")


def one(s, old, new, need=True):
    n = s.count(old)
    assert n == 1 or not need, '치환 대상 %d건: %s' % (n, old[:50])
    return s.replace(old, new)


def main(book_url=None, exam_url=None):
    book = strip(PREVIEW / 'textbook.html')
    # 쿼리가 안 넘어올 수 있으므로 해시도 함께 읽는다
    book = one(book, "  const u = new URLSearchParams(location.search);",
               "  const u = " + HASH_READ + ";")
    book = one(book, '<a class="gbtn" href="./index.html">${body[2]}</a>',
               '<span class="gbtn">${body[2]}</span>')
    if exam_url:
        book = one(book, 'href="./index.html?r=${x[0]}&s=${encodeURIComponent(x[1])}&n=${x[2]}"',
                   f'href="{exam_url}#r=${{x[0]}}&s=${{encodeURIComponent(x[1])}}&n=${{x[2]}}"'
                   ' target="_blank" rel="noopener"')
    (ARTIFACT / 'book.html').write_text(book, encoding='utf-8')

    exam = strip(PREVIEW / 'exam.html')
    exam = one(exam, "  const u = new URLSearchParams(location.search);",
               "  const u = " + HASH_READ + ";")
    if book_url:
        exam = one(exam, '<a class="bookLink" href="./book.html">전자교재 →</a>',
                   f'<a class="bookLink" href="{book_url}" target="_blank" rel="noopener">전자교재 →</a>')
        exam = one(exam, 'href="./book.html?q=${encodeURIComponent(t)}"',
                   f'href="{book_url}#q=${{encodeURIComponent(t)}}"')
        exam = one(exam, "href=\"./book.html?sec=${encodeURIComponent(bk[0] + '|' + bk[1] + '|' + bk[2])}\"",
                   f"href=\"{book_url}#sec=${{encodeURIComponent(bk[0] + '|' + bk[1] + '|' + bk[2])}}\"")
    (ARTIFACT / 'exam.html').write_text(exam, encoding='utf-8')

    link = '교재↔기출 연결됨' if (book_url and exam_url) else '연결 URL 미지정'
    print(f'아티팩트  exam {kb(ARTIFACT / "exam.html")}KB · book {kb(ARTIFACT / "book.html")}KB · {link}')


if __name__ == '__main__':
    main(*sys.argv[1:3])
