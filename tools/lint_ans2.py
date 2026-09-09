# -*- coding: utf-8 -*-
"""2차 모범답안 파일을 훑어 자잘한 흠을 잡는다.

    python tools/lint_ans2.py

· 열고 닫히지 않은 HTML 태그
· 눈에 보이지 않는 채움문자(한글 채움, 폭 없는 공백 등)
· 답안 번호가 그 과목지에 없는 경우
· 답안에 꼭 있어야 할 열쇠(plan·ans·keys)가 빠진 경우
"""
import io, json, os, re, sys, glob, importlib

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'content'))

TAGS = ('b', 'p', 'ul', 'ol', 'li', 'h3', 'h4', 'span', 'i')
GHOST = re.compile('[ᅟᅠㅤ​‌‍﻿­]')

bad = []

# ── 1. 파일 단위로 태그와 채움문자를 본다 ──────────────────
for path in sorted(glob.glob(os.path.join(ROOT, 'content', 'ans2_*.py'))):
    name = os.path.basename(path)
    if name == 'ans2_data.py':
        continue
    s = io.open(path, encoding='utf-8').read()
    for t in TAGS:
        o = len(re.findall(r'<%s[ >]' % t, s))
        c = len(re.findall(r'</%s>' % t, s))
        if o != c:
            bad.append('%-22s <%s> 열림 %d · 닫힘 %d' % (name, t, o, c))
    for m in GHOST.finditer(s):
        bad.append('%-22s 채움문자 U+%04X … %s'
                   % (name, ord(m.group()),
                      s[max(0, m.start() - 20):m.start() + 20].replace('\n', ' ')))

# ── 2. 문항 번호와 필수 열쇠를 본다 ─────────────────────────
rows = json.load(io.open(os.path.join(ROOT, 'data', 'exam2.json'), encoding='utf-8'))
nos = {(r['round'], r['subject']): {q['no'] for q in r['q']} for r in rows}

from ans2_data import ANS                                   # noqa: E402
for (rnd, subj), table in sorted(ANS.items()):
    have = nos.get((rnd, subj))
    if have is None:
        bad.append('제%d회 %s — 그런 과목지가 없습니다' % (rnd, subj))
        continue
    for n in sorted(set(table) - have):
        bad.append('제%d회 %s %d번 — 그런 문항이 없습니다(문항 %s)'
                   % (rnd, subj, n, sorted(have)))
    for n, a in sorted(table.items()):
        for k in ('plan', 'ans', 'keys'):
            if not a.get(k):
                bad.append('제%d회 %s %d번 — %s 가 비었습니다' % (rnd, subj, n, k))

print('모범답안 %d개' % sum(len(t) for t in ANS.values()))
if bad:
    print('\n살펴볼 곳 %d군데' % len(bad))
    for b in bad:
        print('  ' + b)
else:
    print('흠 없음')
