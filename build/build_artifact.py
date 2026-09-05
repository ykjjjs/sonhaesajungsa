# -*- coding: utf-8 -*-
"""미리보기본을 claude.ai 아티팩트로 발행할 형태로 변환.

아티팩트는 <!doctype>…<head>…<body> 를 발행 시점에 감싸므로 껍데기를 벗기고,
CSP 상 스타일시트는 fonts.googleapis.com 만 허용되므로 Pretendard CDN 링크를 뺀다
(폴백 스택에 -apple-system / Apple SD Gothic Neo / system-ui 가 이미 들어 있다).

    python3 build/build_artifact.py            → dist/artifact/{exam,book}.html
    python3 build/build_artifact.py <교재URL>   → 기출본의 교재 링크를 그 주소로 연결
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

def main(book_url=None):
    book = strip(PREVIEW / '전자교재.html')
    # 쿼리가 안 넘어올 수 있으므로 #q= 도 읽는다
    book = book.replace("const p = new URLSearchParams(location.search).get('q');",
        "const p = new URLSearchParams(location.search).get('q')\n"
        "      || new URLSearchParams(location.hash.slice(1)).get('q');")
    book = book.replace('<a class="gbtn" href="./index.html">${body[2]}</a>',
                        '<span class="gbtn">${body[2]}</span>')
    (ARTIFACT / 'book.html').write_text(book, encoding='utf-8')

    exam = strip(PREVIEW / '기출.html')
    if book_url:
        exam = exam.replace('<a class="bookLink" href="./book.html">전자교재 →</a>',
            f'<a class="bookLink" href="{book_url}" target="_blank" rel="noopener">전자교재 →</a>')
        exam = exam.replace('href=\\"./book.html?q=${encodeURIComponent(t)}\\"',
                            f'href=\\"{book_url}#q=${{encodeURIComponent(t)}}\\"')
        exam = exam.replace('href="./book.html?q=${encodeURIComponent(t)}"',
                            f'href="{book_url}#q=${{encodeURIComponent(t)}}"')
    (ARTIFACT / 'exam.html').write_text(exam, encoding='utf-8')

    print(f'아티팩트  exam {kb(ARTIFACT / "exam.html")}KB · book {kb(ARTIFACT / "book.html")}KB'
          + (f' · 교재 링크 연결됨' if book_url else ' · 교재 링크 미연결(URL 인자를 주세요)'))

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else None)
