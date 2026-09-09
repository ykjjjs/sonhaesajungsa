# -*- coding: utf-8 -*-
"""2차 문항을 그대로 찍어 본다.

    python tools/dump2.py <회차> <과목 일부> [시작] [끝]
    python tools/dump2.py 49 제3보험
"""
import io, json, os, sys

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = json.load(io.open(os.path.join(ROOT, 'data', 'exam2.json'), encoding='utf-8'))

rnd = int(sys.argv[1])
part = sys.argv[2]
a = int(sys.argv[3]) if len(sys.argv) > 3 else 1
b = int(sys.argv[4]) if len(sys.argv) > 4 else 99

hit = [r for r in rows if r['round'] == rnd and part in r['subject']]
if not hit:
    print('그런 과목지가 없습니다.')
    sys.exit(1)
for r in hit:
    print('=' * 70)
    print('제%d회 · %s (%s) · %d문항' % (r['round'], r['subject'], r['track'], len(r['q'])))
    for q in r['q']:
        if not (a <= q['no'] <= b):
            continue
        print('-' * 70)
        print('[%d] %d점   %s' % (q['no'], q['points'], '배점 ' + str(q.get('sub'))))
        print(q['body'])
