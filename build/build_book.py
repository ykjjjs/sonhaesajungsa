# -*- coding: utf-8 -*-
"""전자교재 빌드.

검색 인덱스와 용어사전 마크업을 빌드 시점에 만들어 HTML 에 박는다.
  · dist/preview/textbook.html  전체 본문 내장 (오프라인·아티팩트용)
  · public/book.html            본문 없음 — 이용권 계정만 /api/content 로 받는다
  · data/book.json              KV `content:book` 로 올릴 원본
"""
import json, re, html as H
from paths import APP, DATA, PUBLIC, PREVIEW, FREE_BOOK, FREE_Q1, FREE_Q2, kb

try:
    from easy_data import EASY          # 절마다 '쉽게 이해하기' 원고
except ImportError:
    EASY = {}
try:
    from exam2_map import MAP2          # 절 → 2차 기출 (tools/build_map2.py 산출물)
except ImportError:
    MAP2 = {}
try:
    from ans2_data import ANS           # 2차 모범답안
except ImportError:
    ANS = {}
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

def attach():
    """절마다 xq1(1차 기출 본문·정답·해설) · xq2(2차 기출·모범답안) · easy 를 심는다."""
    exam = json.loads((DATA / 'exam.json').read_text(encoding='utf-8'))
    rows2 = json.loads((DATA / 'exam2.json').read_text(encoding='utf-8'))
    idx1 = {}
    for y, sess in exam.items():
        for subjs in sess.values():
            for subj, qs in subjs.items():
                for q in qs:
                    idx1[(int(y) - 1977, subj, q['no'])] = q
    idx2 = {(r['round'], r['subject'], q['no']): (r, q) for r in rows2 for q in r['q']}
    n1 = n2 = ne = 0
    for subj, b in BOOK.items():
        for ci, c in enumerate(b['chapters']):
            for si, sec in enumerate(c['sections']):
                xs = []
                for r_, sj, no, _ in sec.get('exq', []):
                    q = idx1.get((r_, sj, no))
                    if q:
                        xs.append({'r': r_, 's': sj, 'n': no, 'q': q['q'], 'c': q['choices'],
                                   'a': q['answer'], 'e': q.get('explanation', ''),
                                   'w': q.get('wrongWhy', {})})
                sec['xq1'] = xs
                x2 = []
                for rnd, sj2, no in MAP2.get((subj, ci, si), []):
                    hit, a = idx2.get((rnd, sj2, no)), ANS.get((rnd, sj2), {}).get(no)
                    if hit and a:
                        r2, q2 = hit
                        x2.append({'r': rnd, 's': sj2, 't': r2['track'], 'n': no,
                                   'p': q2.get('points', 0), 'b': q2.get('body', ''), 'a': a})
                sec['xq2'] = x2
                e = EASY.get((subj, ci, si))
                if e:
                    sec['easy'] = e
                n1 += len(xs); n2 += len(x2); ne += bool(e)
    missing = [(subj, ci, si) for subj, b in BOOK.items() for ci, c in enumerate(b['chapters'])
               for si, _ in enumerate(c['sections']) if (subj, ci, si) not in EASY]
    if missing:
        print('  ! 쉽게 이해하기 원고가 없는 절', missing)
    return n1, n2, ne


def free_part(search):
    """결제 전 배포본 — 무료 장만 본문을 두고, 나머지 절은 제목만 남겨 자물쇠를 건다."""
    keep = set(FREE_BOOK)
    book = {}
    for subj, b in BOOK.items():
        chs = []
        for c in b['chapters']:
            if (subj, c['title']) in keep:
                free1 = {(49, sj, no) for sj, nos in FREE_Q1.items() for no in nos}
                free2 = {(49, sj, no) for sj, no in FREE_Q2}
                secs = []
                for x in c['sections']:
                    y = dict(x)
                    y['xq1'] = [q if (q['r'], q['s'], q['n']) in free1
                                else {'r': q['r'], 's': q['s'], 'n': q['n'], 'locked': True}
                                for q in x.get('xq1', [])]
                    y['xq2'] = [q if (q['r'], q['s'], q['n']) in free2
                                else {'r': q['r'], 's': q['s'], 't': q['t'], 'n': q['n'], 'p': q['p'], 'locked': True}
                                for q in x.get('xq2', [])]
                    secs.append(y)
                chs.append({k: v for k, v in c.items() if k != 'sections'} | {'sections': secs})
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
    n1, n2, ne = attach()
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
    print(f'      절에 심은 것: 1차 기출 {n1} · 2차 기출 {n2} · 쉽게 이해하기 {ne}/{n}')
    print(f'교재  절 {n} · 본문 {ch:,}자 · 카드 {cards} · 용어 {len(TERMS)} · '
          f'미리보기 {kb(PREVIEW / "textbook.html")}KB · 배포본 {kb(PUBLIC / "book.html")}KB · '
          f'book.json {kb(DATA / "book.json")}KB')

if __name__ == '__main__':
    main()
