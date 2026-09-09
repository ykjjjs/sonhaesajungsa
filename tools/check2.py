# -*- coding: utf-8 -*-
"""2차 문항이 제대로 잘렸는지 점검한다.

    python tools/check2.py

· 배점 합계가 100이 아닌 과목지
· 문장 도중에 시작하는 것으로 보이는 문항
· 표의 항목줄에서 시작하는 것으로 보이는 문항
"""
import io, json, os, re, sys

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = json.load(io.open(os.path.join(ROOT, 'data', 'exam2.json'), encoding='utf-8'))

CUT = re.compile(r'^[는은이가을를의에로와과도만]\s|^\d{1,2}\s*[.)]\s|^[,·)\]}]')
LABEL = re.compile(r'^[^\n:]{0,22}:')

bad_paper, bad_q = [], []
for r in rows:
    tot = sum(q['points'] for q in r['q'])
    if tot != 100 or not (3 <= len(r['q']) <= 20):
        bad_paper.append((r, tot))
    for q in r['q']:
        head = q['body'][:46]
        why = None
        if CUT.match(head):
            why = '문장 도중에서 시작'
        elif LABEL.match(head):
            why = '표의 항목줄에서 시작'
        elif len(q['body']) < 40:
            why = '너무 짧음'
        if why:
            bad_q.append((r, q, why))

print('과목지 %d · 문항 %d' % (len(rows), sum(len(r['q']) for r in rows)))
print('\n배점 합계나 문항 수가 이상한 과목지 %d개' % len(bad_paper))
for r, tot in bad_paper:
    print('  제%d회 %-42s 문항 %2d · 배점합 %3d%s'
          % (r['round'], r['subject'][:42], len(r['q']), tot,
             ' (수기 보정본)' if r.get('manual') else ''))

print('\n살펴볼 문항 %d개' % len(bad_q))
for r, q, why in bad_q:
    print('  제%d회 %-26s %2d번 [%s] %s'
          % (r['round'], r['subject'][:26], q['no'], why,
             q['body'][:52].replace('\n', ' ')))
