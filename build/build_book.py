# -*- coding: utf-8 -*-
"""전자교재 빌드.

검색 인덱스와 용어사전 마크업을 빌드 시점에 만들어 HTML 에 박는다.
  · dist/preview/textbook.html  전체 본문 내장 (오프라인·아티팩트용)
  · public/book.html            본문 없음 — 이용권 계정만 /api/content 로 받는다
  · data/book.json              KV `content:book` 로 올릴 원본
"""
import json, re, html as H
from paths import APP, DATA, PUBLIC, PREVIEW, FREE_BOOK, kb
from book_data import BOOK, TERMS

TAG = re.compile(r'<[^>]+>')
WS = re.compile(r'\s+')

def plain(s):
    return WS.sub(' ', H.unescape(TAG.sub(' ', s))).strip()

def build_search():
    out = []
    for subj, b in BOOK.items():
        for ci, c in enumerate(b['chapters']):
            for si, s in enumerate(c['sections']):
                t = ' '.join([s['title'], s.get('lead', ''), plain(s['html']),
                              ' '.join(q + ' ' + plain(a) for q, a in s.get('cards', []))])
                out.append({'s': subj, 'c': ci, 'i': si, 'title': s['title'],
                            'chap': c['title'], 't': WS.sub(' ', t)})
    return out

def build_gloss():
    groups = {}
    for k in sorted(TERMS, key=lambda x: (x[0], x)):
        groups.setdefault(k[0], []).append(k)
    parts = []
    for g in groups:
        rows = ''.join(
            f'<div class="glrow"><b>{H.escape(k)}</b><span>{H.escape(TERMS[k]["d"])}</span>'
            + (f'<div class="src">{H.escape(TERMS[k]["src"])}</div>' if TERMS[k].get('src') else '')
            + '</div>' for k in groups[g])
        parts.append(f'<div class="glgroup"><h4>{H.escape(g)}</h4>{rows}</div>')
    return ''.join(parts)

def retime():
    """본문 분량에 맞춰 예상 학습시간을 다시 매긴다 — 분당 420자 + 카드 1장당 12초."""
    for b in BOOK.values():
        for c in b['chapters']:
            for s in c['sections']:
                n = len(plain(s['html'])) + len(s.get('lead', ''))
                s['minutes'] = max(6, int(round(n / 420 + len(s.get('cards', [])) * 0.2)))

def free_part(search):
    """결제 전 배포본 — 무료 장만 본문을 두고, 나머지 절은 제목만 남겨 자물쇠를 건다."""
    keep = set(FREE_BOOK)
    book = {}
    for subj, b in BOOK.items():
        chs = []
        for c in b['chapters']:
            if (subj, c['title']) in keep:
                chs.append(c)
            else:
                chs.append({k: v for k, v in c.items() if k != 'sections'} | {'sections': [
                    {'title': x['title'], 'desc': x.get('desc', ''), 'minutes': x.get('minutes', 8),
                     'locked': True} for x in c['sections']]})
        book[subj] = {k: v for k, v in b.items() if k != 'chapters'} | {'chapters': chs}
    text = ' '.join(s['html'] for subj, b in book.items() for c in b['chapters']
                    for s in c['sections'] if not s.get('locked'))
    terms = {k: v for k, v in TERMS.items() if k in text}
    srch = [e for e in search if (e['s'], e['chap']) in keep]
    return {'BOOK': book, 'TERMS': terms, 'SEARCH': srch}


def main():
    retime()
    tpl = (APP / 'book.html').read_text(encoding='utf-8')
    search = build_search()
    gloss = build_gloss()

    full = (tpl.replace('__FREE__', 'null')
               .replace('__BOOK__', json.dumps(BOOK, ensure_ascii=False))
               .replace('__TERMS__', json.dumps(TERMS, ensure_ascii=False))
               .replace('__SEARCH__', json.dumps(search, ensure_ascii=False))
               .replace('__GLOSS_HTML__', gloss))
    (PREVIEW / 'textbook.html').write_text(full, encoding='utf-8')

    free = free_part(search)
    gated = (tpl.replace('__FREE__', json.dumps(free, ensure_ascii=False))
                .replace('__BOOK__', 'null').replace('__TERMS__', 'null')
                .replace('__SEARCH__', 'null').replace('__GLOSS_HTML__', ''))
    (PUBLIC / 'book.html').write_text(gated, encoding='utf-8')

    (DATA / 'book.json').write_text(json.dumps(
        {'BOOK': BOOK, 'TERMS': TERMS, 'SEARCH': search, 'GLOSS': gloss},
        ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

    n = sum(len(c['sections']) for b in BOOK.values() for c in b['chapters'])
    ch = sum(len(s['html']) for b in BOOK.values() for c in b['chapters'] for s in c['sections'])
    cards = sum(len(s.get('cards', [])) for b in BOOK.values() for c in b['chapters'] for s in c['sections'])
    print(f'교재  절 {n} · 본문 {ch:,}자 · 카드 {cards} · 용어 {len(TERMS)} · '
          f'미리보기 {kb(PREVIEW / "textbook.html")}KB · 배포본 {kb(PUBLIC / "book.html")}KB · '
          f'book.json {kb(DATA / "book.json")}KB')

if __name__ == '__main__':
    main()
