# -*- coding: utf-8 -*-
"""2차 기출(논술) 문항을 전자교재 절에 대응시킨다.

1차 대응(build_map.py)처럼 TF·IDF 로 돌리면 회계원리·의학이론 문항이 엉뚱한 절에 붙는다.
2차는 과목이 교재와 겹치는 곳이 좁으므로, 절마다 **볼 과목**과 **본문에 반드시 있어야 할 낱말**을
사람이 정해 두고 그 조건을 만족하는 문항만 붙인다. 틀린 연결은 없느니만 못하다.

  · 모범답안이 있는 문항만 붙인다(초보자가 답을 확인할 수 있어야 한다).
  · 한 절에 최대 PER 문항. 낱말이 많이 걸린 문항 → 최근 회차 순.

결과: content/exam2_map.py  (MAP2 = {(과목, 장, 절): [(회차, 2차 과목, 번호), ...]})
실행: python tools/build_map2.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'content'))
from ans2_data import ANS            # noqa: E402
from book_data import BOOK           # noqa: E402

PER = 3

FIRE = '책임·화재·기술보험 등의 이론과 실무'
LIA = '책임·근로자재해보상보험의 이론과 실무'
TH3 = '제3보험의 이론과 실무'
MAR = '해상보험의 이론과 실무'
CARP = '자동차보험의 이론과 실무(대인배상 및 자기신체손해)'
CARO = '자동차보험의 이론과 실무(대물배상 및 차량손해)'
LAW = [FIRE, LIA, TH3, MAR, CARP, CARO]

# (과목, 장, 절): (볼 2차 과목, 본문에 있어야 할 낱말)
RULES = {
    # ── 보험계약법 ──
    ('보험계약법', 0, 0): (LAW, ['불이익변경금지', '불이익변경의 금지', '사행계약', '부합계약']),
    ('보험계약법', 0, 1): (LAW, ['승낙 전', '승낙전', '낙부통지', '청약의 철회', '청약철회', '약관의 교부', '설명의무']),
    ('보험계약법', 0, 2): (LAW, ['고지의무', '계약 전 알릴 의무', '계약전 알릴 의무', '계약전알릴의무', 'Duty of Disclosure']),
    ('보험계약법', 0, 3): (LAW, ['위험의 변경', '위험변경', '위험의 증가', '위험증가', '계약 후 알릴 의무',
                            '계약후 알릴 의무', '직업 또는 직무', '직무의 변경']),
    ('보험계약법', 0, 4): (LAW, ['계속보험료', '보험료의 납입', '보험료 납입', '실효', '부활', '보험료의 반환']),
    ('보험계약법', 0, 5): (LAW, ['면책사유', '보상하지 않는 손해', '보상하지 아니하는 손해', '중대한 과실', '소멸시효']),
    ('보험계약법', 1, 0): ([FIRE, MAR, CARO, LIA], ['피보험이익', '보험가액', '협정보험가액', '재조달가액', '신가보험']),
    ('보험계약법', 1, 1): ([FIRE, LIA, CARO, CARP, TH3], ['중복보험', '일부보험', '초과보험', '비례보상', '독립책임액']),
    ('보험계약법', 1, 2): ([FIRE, LIA, MAR, CARO, CARP], ['손해방지', '손해경감', '대위', 'Sue and Labour', 'Sue & Labour']),
    ('보험계약법', 1, 3): ([MAR, FIRE], ['공동해손', '적하보험', '선박보험', 'York-Antwerp', 'MIA', '운송보험']),
    ('보험계약법', 1, 4): ([LIA, CARP, CARO, FIRE], ['직접청구', '자동차손해배상보장법', '자배법', '운행자', '책임보험']),
    ('보험계약법', 2, 0): ([TH3, LIA], ['생명보험', '보험수익자', '인보험', '사망보험금']),
    ('보험계약법', 2, 1): ([TH3], ['타인의 생명', '타인의 사망', '서면동의', '서면에 의한 동의', '단체보험']),
    ('보험계약법', 2, 2): ([TH3, CARP], ['상해보험', '질병·상해보험', '실손의료', '후유장해', '장해지급률']),
    # ── 보험업법 ──
    ('보험업법', 0, 2): (LAW, ['전문보험계약자', '일반보험계약자']),
    ('보험업법', 3, 2): (LAW, ['보험대리점', '보험중개사']),
    ('보험업법', 3, 3): (LAW, ['승환계약', '부당한 계약전환', '특별이익']),
    ('보험업법', 5, 0): (LAW, ['책임준비금', '지급여력']),
    ('보험업법', 6, 0): (LAW, ['손해사정사의 의무', '손해사정사 보수교육', '손해사정사의 금지', '손해사정업자']),
    ('보험업법', 6, 1): (LAW, ['손해사정서']),
    ('보험업법', 6, 2): (LAW, ['보험요율 산출기관', '보험요율산출기관']),
    # ── 손해사정이론 ──
    ('손해사정이론', 1, 1): (LAW, ['역선택', '도덕적 해이', '보험사기']),
    ('손해사정이론', 1, 2): ([LIA, TH3, CARP], ['산업재해보상보험', '산재보험', '국민건강보험', '근로복지공단']),
    ('손해사정이론', 2, 0): (LAW, ['언더라이팅', '계약심사', '인수심사']),
    ('손해사정이론', 2, 1): (LAW, ['순보험료', '부가보험료', '경험요율']),
    ('손해사정이론', 2, 2): (LAW, ['최대선의', 'Utmost Good Faith', 'utmost good faith']),
    ('손해사정이론', 3, 0): ([FIRE, LIA, CARO, CARP, TH3, MAR], ['손해사정 절차', '현장조사', '손해사정사가 착안', '조사방법']),
    ('손해사정이론', 3, 1): (LAW, ['자기부담금', '공제금액', 'Deductible', 'deductible', '소손해면책']),
    ('손해사정이론', 3, 2): (LAW, ['실손보상', '감가상각', '재조달가액', '잔존물']),
    ('손해사정이론', 3, 3): ([LIA, FIRE], ['배상청구기준', '손해사고기준', 'Claims-made', 'Claims made', 'claims-made',
                              '소급담보', 'Occurrence', 'CGL']),
    ('손해사정이론', 4, 0): (LAW, ['재보험']),
    ('손해사정이론', 4, 1): (LAW, ['비례재보험', 'Excess of Loss', 'Quota Share', 'Surplus']),
}


def main():
    rows = json.loads((ROOT / 'data' / 'exam2.json').read_text(encoding='utf-8'))
    titles = {(subj, ci, si): s['title'] for subj, b in BOOK.items()
              for ci, c in enumerate(b['chapters']) for si, s in enumerate(c['sections'])}
    out = {}
    for addr, (subjects, words) in RULES.items():
        assert addr in titles, addr
        cands = []
        for r in rows:
            if r['subject'] not in subjects:
                continue
            for q in r['q']:
                if not ANS.get((r['round'], r['subject']), {}).get(q['no']):
                    continue
                body = q.get('body', '')
                # '화재보험'·'산재보험' 안의 '재보험'이 재보험 절에 걸리지 않게 가려 둔다
                look = body.replace('화재보험', '화_보험').replace('산재보험', '산_보험')
                score = sum(look.count(w) for w in words)
                if score:
                    cands.append((score, r['round'], r['subject'], q['no'], body))
        cands.sort(key=lambda x: (-x[0], -x[1]))
        if cands:
            out[addr] = cands[:PER]

    lines = ['# -*- coding: utf-8 -*-',
             '"""tools/build_map2.py 가 만든 산출물 — 직접 고치지 말 것.',
             '키는 (과목, 장, 절), 값은 그 절과 관련된 2차 기출 (회차, 2차 과목, 번호)."""',
             '', 'MAP2 = {']
    for addr in sorted(out):
        lines.append('    %r: [%s],' % (addr, ', '.join('(%d, %r, %d)' % (c[1], c[2], c[3]) for c in out[addr])))
    lines.append('}')
    (ROOT / 'content' / 'exam2_map.py').write_text('\n'.join(lines) + '\n', encoding='utf-8')

    tot = sum(len(v) for v in out.values())
    print('2차 대응 %d문항 · 절 %d / %d' % (tot, len(out), len(titles)))
    for addr in sorted(out):
        print('  %s %s' % (addr, titles[addr]))
        for c in out[addr]:
            print('      [%d] 제%d회 %s %d번 · %s' % (c[0], c[1], c[2][:12], c[3], c[4][:60].replace('\n', ' ')))


if __name__ == '__main__':
    main()
