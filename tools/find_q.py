# -*- coding: utf-8 -*-
"""기출 검색 — 낱말로 문항을 찾아 회차·번호·정답을 보여 준다.
   사용: python tools/find_q.py 전문보험계약자 [과목]
"""
import json, sys, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parents[1]
E = json.load(open(ROOT / 'data' / 'exam.json', encoding='utf-8'))
YEAR2R = {'2022': 45, '2023': 46, '2024': 47, '2025': 48, '2026': 49}

def rows():
    for y in E:
        for sess in E[y]:
            for subj, lst in E[y][sess].items():
                for q in lst:
                    yield y, subj, q

def main():
    kws = [a for a in sys.argv[1:] if not a.startswith('-')]
    full = '-f' in sys.argv
    n = 0
    for y, subj, q in rows():
        blob = q['q'] + ' ' + ' '.join(q['choices'])
        if all(k in blob for k in kws):
            n += 1
            print(f"[{y}·제{YEAR2R[y]}회] {subj} {q['no']}번  정답 {q['answer']+1}"
                  + (f"  (복수정답 {q['altAnswers']})" if q.get('altAnswers') else ''))
            print('   ', q['q'][:150])
            if full:
                for i, c in enumerate(q['choices']):
                    mark = '★' if i == q['answer'] else ' '
                    print(f"    {mark}{i+1}. {c[:160]}")
    print(f'— {n}건')

main()
