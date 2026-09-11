# -*- coding: utf-8 -*-
"""교재 본문 설명 문장을 현행 법령 원문과 대조한다(인용 상자는 check_law.py 가 본다).

대상: 55절의 리드·본문·암기 카드, 용어사전, '쉽게 이해하기' 원고.
문장마다 조문 인용(제N조, 제N조 제K항, 「상법」·시행령·같은 조 …)을 찾아
  1) 인용한 조문이 현행 법령에 있는가(삭제된 조문인가)
  2) 문장 속 숫자·기간·비율(2주, 1개월, 100분의 15, 300억원 …)이 그 조문(항)에 실제로 있는가
  3) 문장의 핵심 낱말이 그 조문에 얼마나 들어 있는가(번호를 잘못 붙이면 낮게 나온다)
를 보고, 하나라도 걸리면 보고한다. 자동 판정이므로 보고된 문장은 사람이 원문과 읽어 보고 고친다.

    python tools/check_text.py              # 보고서를 dist/check_text.txt 에 쓰고 요약 출력
"""
import html as H
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'content'))
import check_law as CL                                   # noqa: E402

CL.LAWS.update({'약관규제법': '약관규제법.json', '개인정보 보호법': '개인정보보호법.json',
                '자동차손해배상 보장법': '자배법.json', '금융소비자보호법': '금소법.json'})
ALIAS = {'보험업법 시행령': '보험업법 시행령', '시행령': '보험업법 시행령', '보험업법': '보험업법', '상법': '상법',
         '약관규제법': '약관규제법', '약관의 규제에 관한 법률': '약관규제법', '개인정보 보호법': '개인정보 보호법',
         '자동차손해배상 보장법': '자동차손해배상 보장법', '자배법': '자동차손해배상 보장법',
         '금융소비자 보호에 관한 법률': '금융소비자보호법', '금융소비자보호법': '금융소비자보호법', '금소법': '금융소비자보호법'}
OTHER_LAW = re.compile(r'(국민건강보험법|고용보험법|산업재해보상보험법|산재보험법|민법|형법|보험사기방지|예금자보호법|전자서명법|'
                       r'근로기준법|국민연금법|신용정보|금융산업의 구조개선|자본시장|은행법|외국환거래법|소득세법|근로자퇴직급여|'
                       r'지배구조|같은 법 시행령|노인복지법|영국|MIA|ICC|ITC|York|IFRS)')
TAG = re.compile(r'<[^>]+>')
NAMES = '|'.join(sorted(map(re.escape, list(ALIAS) + ['법']), key=len, reverse=True))
CIT = re.compile(r'(?:「?(' + NAMES + r')」?\s*)?제\s*(\d+)\s*조(?:\s*의\s*(\d+))?(?:\s*제\s*(\d+)\s*항)?(?:\s*제\s*(\d+)\s*호)?')
SAME = re.compile(r'같은\s*(?:조|항)(?:\s*제\s*(\d+)\s*항)?')
NUM = re.compile(r'(\d+)\s*분의\s*(\d+)|(?<![\d.])(\d[\d,]*)\s*(개월|월|일|년|주일|주|퍼센트|%|억원|천만원|만원|원|세|명)')
CIRCLED = '①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳'
WORD = re.compile(r'[가-힣]{2,8}')
STOP = set('''경우 다음 해당 규정 조문 사항 이하 이상 이내 초과 미만 한다 한다고 된다 있다 없다 아니다 아니한다 있는 없는 하는 하여 하고 하며
관한 관하여 대한 대하여 따라 따른 위하여 그리고 또는 다만 이러한 그러한 이는 이를 이것 그것 여기 지문 문항 출제 기출 함정 개념 사례 참고 심화
정리 구별 이유 취지 핵심 결과 효과 요건 원칙 예외 뜻이다 것이다 때문이다 보험 보험회사 보험계약 계약 조항 법률 법령 대통령령 금융위원회 제항 제호
틀린 옳은 지문은 틀린다 틀렸다 옳다 반드시 모두 각각 각호 호의 항의 조의 앞의 뒤의 같은 다른 이하 부터 까지 에게 에서 으로 로서 로써 이다 한다
'''.split())


def plain(s):
    s = re.sub(r'</(p|li|tr|h\d|div)>|<br\s*/?>|</td>', '\n', s)
    return H.unescape(TAG.sub(' ', s))


def sentences(text):
    for line in text.split('\n'):
        line = re.sub(r'\s+', ' ', line).strip()
        if not line:
            continue
        for s in re.split(r'(?<=[다음함임])\.\s+', line):
            if len(s) >= 6:
                yield s


def norm_num(m):
    if m.group(1):
        return f'{int(m.group(1))}분의{int(m.group(2))}'
    n, u = m.group(3).replace(',', ''), m.group(4)
    if u == '%':
        return f'100분의{n}'
    u = {'월': '개월', '주일': '주'}.get(u, u)
    return n + u


def numbers(text, law=False):
    if law:
        text = re.sub(r'(^|[\s/])\d+(의\d+)?\.\s', ' ', text)      # 호 번호 '4. ' 가 뒤 숫자에 붙지 않게
    out = set()
    for m in NUM.finditer(text):
        pre = text[max(0, m.start() - 6):m.start()]
        if not law and (re.search(r'(19|20)\d\d년\s*$', pre) or re.fullmatch(r'(19|20)\d\d', m.group(3) or '')):
            continue                                              # 개정 연월
        k = norm_num(m)
        out.add((k, m.group(0).strip()))
        if k.endswith('퍼센트'):
            out.add(('100분의' + k[:-3], m.group(0)))
    return out


def unit_slice(units, para):
    """조문 단위 목록에서 제K항(과 그 호)만 떼어 낸다. 항이 없으면 전체."""
    if not para:
        return units
    mark = CIRCLED[para - 1] if para <= len(CIRCLED) else None
    start = next((i for i, u in enumerate(units) if mark and u.lstrip().startswith(mark)), None)
    if start is None:
        return units
    end = next((i for i in range(start + 1, len(units)) if units[i].lstrip()[:1] in CIRCLED), len(units))
    return units[start:end]


def collect():
    from book_data import BOOK, TERMS
    from easy_data import EASY
    items = []
    for subj, b in BOOK.items():
        for ci, c in enumerate(b['chapters']):
            for si, s in enumerate(c['sections']):
                where = f'{subj} {ci + 1}장 {si + 1}절 「{s["title"]}」'
                items.append((subj, where, plain(s.get('lead', '') + '\n' + s['html'])))
                for q, a in s.get('cards', []):
                    items.append((subj, where + ' 카드', plain(q + ' → ' + a)))
    for k, v in TERMS.items():
        src = v.get('src', '')
        subj = '보험계약법' if src.startswith('상법') else '보험업법' if '보험업법' in src else '용어'
        items.append((subj, f'용어 「{k}」', plain(v.get('d', '') + '\n' + v.get('more', ''))))
    for (subj, ci, si), v in EASY.items():
        items.append((subj, f'쉽게 이해하기 {subj} {ci + 1}장 {si + 1}절',
                      '\n'.join([v['one'], *v['plain'], v['ex'], v['exam']] + [w[0] + ': ' + w[1] for w in v['words']])))
    return items


def main():
    laws = CL.load_laws()
    default = {'보험업법': '보험업법', '보험계약법': '상법'}
    report, n_sent, n_cite = [], 0, 0
    for subj, where, text in collect():
        last_art = None
        for s in sentences(text):
            s_clean = re.sub(r'제\s*\d+\s*회[^.]*?\d+\s*번', ' ', s)   # '제47회 보험업법 12번' 같은 출처 표기
            cites = []
            last_law = default.get(subj)       # 법령명 없는 인용은 같은 문장 앞에 적힌 법령, 없으면 과목의 법령
            for m in CIT.finditer(s_clean):
                name = m.group(1)
                if name == '법':
                    law = '보험업법'
                elif name:
                    law = ALIAS[name]
                else:
                    if OTHER_LAW.search(s_clean[max(0, m.start() - 25):m.start()]):
                        continue
                    law = last_law
                if name and s_clean[max(0, m.start() - 12):m.start()].rstrip().endswith('같은 법'):
                    continue
                art = (int(m.group(2)), int(m.group(3) or 0))
                cites.append((law, art, int(m.group(4) or 0)))
                last_law, last_art = law, art
            for m in SAME.finditer(s_clean):
                if last_art and last_law:
                    cites.append((last_law, last_art, int(m.group(1) or 0)))
            if not cites:
                continue
            n_sent += 1
            n_cite += len(cites)
            probs, texts = [], []
            for law, art, para in cites:
                L = laws.get(law)
                if not L:
                    continue
                a = L['arts'].get(art)
                label = f'{law} 제{art[0]}조' + (f'의{art[1]}' if art[1] else '') + (f' 제{para}항' if para else '')
                if not a:
                    probs.append(f'없는 조문 {label}')
                    continue
                units = unit_slice(a['units'], para)
                head = re.sub(r'^제\d+조(의\d+)?(\([^)]*\))?\s*', '', units[0]).strip() if units else ''
                if len(units) <= 1 and head.startswith('삭제'):
                    probs.append(f'삭제된 조문 {label}')
                texts.append((label, a['title'], ' '.join(units)))
            if not texts:
                if probs:
                    report.append((where, s, probs, []))
                continue
            joined = ' '.join(t for _, _, t in texts)
            have = {k for k, _ in numbers(joined, law=True)}
            for k, raw in sorted(numbers(s_clean)):
                if k not in have:
                    probs.append(f'원문에 없는 숫자 {raw}')
            words = [w for w in dict.fromkeys(WORD.findall(s_clean)) if w not in STOP]
            if len(words) >= 5:
                jn = re.sub(r'\s+', '', joined)
                hit = sum(1 for w in words if w in jn or (len(w) >= 3 and w[:-1] in jn))
                if hit / len(words) < 0.3:
                    probs.append(f'낱말 일치 {hit / len(words):.2f}')
            if probs:
                report.append((where, s, probs, texts))
    out = ROOT / 'dist' / 'check_text.txt'
    with open(out, 'w', encoding='utf-8') as f:
        f.write('현행 법령 기준 — ' + ', '.join(f'{k} {v["eff"]}' for k, v in laws.items()) + '\n')
        for where, s, probs, texts in report:
            f.write(f'\n■ {where}\n  문장: {s}\n  판정: {" · ".join(probs)}\n')
            for label, title, t in texts:
                f.write(f'  원문: {label}({title}) {t[:300]}\n')
    kinds = {}
    for _, _, probs, _ in report:
        for p in probs:
            key = p.rsplit(' ', 1)[0] if p.startswith('원문에') else p.split(' ')[0]
            kinds[key] = kinds.get(key, 0) + 1
    print(f'인용 문장 {n_sent} · 인용 {n_cite} · 보고 {len(report)}문장 · 유형 {kinds} → {out}')


if __name__ == '__main__':
    main()
