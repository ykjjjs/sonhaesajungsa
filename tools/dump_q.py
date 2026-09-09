# -*- coding: utf-8 -*-
"""해설을 쓰기 위해 문항을 그대로 펼쳐 본다.
   사용: python tools/dump_q.py 49 보험업법 11 20
"""
import json, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
E = json.load(open(ROOT / 'data' / 'exam.json', encoding='utf-8'))
Y = {45: '2022', 46: '2023', 47: '2024', 48: '2025', 49: '2026'}
r, subj = int(sys.argv[1]), sys.argv[2]
a, b = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (1, 40)
for q in E[Y[r]]['1차 1교시'][subj]:
    if not (a <= q['no'] <= b):
        continue
    alt = ('  복수정답 %s' % q['altAnswers']) if q.get('altAnswers') else ''
    done = '  [해설있음]' if (q.get('explanation') or '').strip() else ''
    print('\n【%d번】 정답 %d%s%s' % (q['no'], q['answer'] + 1, alt, done))
    print(q['q'])
    for i, c in enumerate(q['choices']):
        print('  %s%d. %s' % ('★' if i == q['answer'] else ' ', i + 1, c))
