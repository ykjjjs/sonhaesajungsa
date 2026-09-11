# -*- coding: utf-8 -*-
"""교재의 조문 인용 상자를 현행 법령 원문과 대조한다.

교재 원고(content/*.py)의 <div class="law"><span class="no">보험업법 제N조 …</span> … </div> 를 모두 찾아
  1) 인용한 문장이 현행 조문 어디와 가장 가까운지(유사도)
  2) 문장 속 숫자·기간(2주, 1개월, 100분의 15, 300억원 …)이 그 조문에 실제로 있는지
  3) 조문 제목이 현행과 같은지
를 본다. 개정으로 바뀐 문구, 삭제된 호, 번호가 밀린 조문을 찾는 것이 목적이다.

법령 원문은 data/law/ 에 법제처 OPEN API(JSON) 그대로 둔다. 새로 받으려면:
    python tools/check_law.py --fetch
점검:
    python tools/check_law.py            # 전체
    python tools/check_law.py ex_bul_d.py
"""
import difflib
import html as H
import io
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAWDIR = ROOT / 'data' / 'law'
LAWS = {'보험업법': '보험업법.json', '상법': '상법.json', '보험업법 시행령': '보험업법_시행령.json'}
SIM_FLOOR = 0.80          # 이보다 낮으면 '현행과 다름'

TAG = re.compile(r'<[^>]+>')
NUM = re.compile(r'\d+분의\s*\d+|\d[\d,]*(?:\.\d+)?\s*(?:개월|일|년|주|퍼센트|%|억원|만원|천만원|원|세|명|회|배)')
REF = re.compile(r'제\s*(\d+)\s*조(?:\s*의\s*(\d+))?')
# 조문 제목으로 쓰인 '제N조' — 뒤에 괄호 제목·항 번호가 오거나 줄이 끝난다
HEAD = re.compile(r'제\s*(\d+)\s*조(?:\s*의\s*(\d+))?(?=\s*[(①-⑳]|\s*$)')


# ── 법령 원문 ────────────────────────────────────────────────────────────
def fetch():
    LAWDIR.mkdir(parents=True, exist_ok=True)
    for name, fn in LAWS.items():
        q = urllib.parse.urlencode({'OC': 'test', 'target': 'law', 'type': 'JSON', 'query': name, 'display': 100})
        d = json.loads(urllib.request.urlopen('https://www.law.go.kr/DRF/lawSearch.do?' + q, timeout=60).read())
        laws = d['LawSearch'].get('law', [])
        laws = laws if isinstance(laws, list) else [laws]
        hit = next(l for l in laws if l.get('법령명한글') == name and l.get('현행연혁코드') == '현행')
        raw = urllib.request.urlopen('https://www.law.go.kr/DRF/lawService.do?OC=test&target=law&type=JSON&MST='
                                     + hit['법령일련번호'], timeout=120).read().decode('utf-8')
        (LAWDIR / fn).write_text(raw, encoding='utf-8')
        print('받음', name, '시행', hit.get('시행일자'))


def _flat(x):
    out = []
    if isinstance(x, dict):
        for k in ('조문내용', '항내용', '호내용', '목내용'):
            if isinstance(x.get(k), str) and x[k].strip():
                out.append(x[k].strip())
        for k in ('항', '호', '목'):
            if k in x:
                v = x[k]
                for y in (v if isinstance(v, list) else [v]):
                    out += _flat(y)
    elif isinstance(x, list):
        for y in x:
            out += _flat(y)
    return out


def load_laws():
    laws = {}
    for name, fn in LAWS.items():
        p = LAWDIR / fn
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding='utf-8'))['법령']
        info = d.get('기본정보', {})
        arts = {}
        for u in d['조문']['조문단위']:
            if u.get('조문여부') != '조문':
                continue
            key = (int(u['조문번호']), int(u.get('조문가지번호') or 0))
            arts[key] = {'title': u.get('조문제목', ''), 'units': _flat(u)}
        laws[name] = {'arts': arts, 'eff': info.get('시행일자', '')}
    return laws


def norm(s):
    s = H.unescape(TAG.sub(' ', s))
    s = re.sub(r'<[^>]*$', '', s)
    s = s.replace('ㆍ', '·').replace('ᆞ', '·')
    s = re.sub(r'[“”"\'‘’「」『』()\[\]〈〉<>]', '', s)
    s = re.sub(r'\s+', '', s)
    return s


# ── 교재 원고의 인용 상자 ──────────────────────────────────────────────
BOX = re.compile(r'<div class="law"><span class="no">(.*?)</span>(.*?)</div>', re.S)


def parse_label(label, default):
    name = default
    for n in sorted(LAWS, key=len, reverse=True):
        if label.strip().startswith(n):
            name = n
            break
    refs = [(int(a), int(b or 0)) for a, b in REF.findall(label)]
    m = re.search(r'제\s*(\d+)\s*조\s*~\s*제\s*(\d+)\s*조', label)
    if m:
        refs = [(i, 0) for i in range(int(m.group(1)), int(m.group(2)) + 1)]
    return name, refs


def lines_of(body):
    parts = re.split(r'<br\s*/?>|</p>|<p>|</li>|<li>', body)
    out = []
    for p in parts:
        t = H.unescape(TAG.sub('', p)).strip()
        if len(norm(t)) >= 8:
            out.append(t)
    return out


def best(line, units):
    a = norm(line)
    top, where = 0.0, ''
    for u in units:
        b = norm(u)
        if not b:
            continue
        if a in b:
            return 1.0, u
        sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
        # 짧은 인용이 긴 항의 일부일 수 있으므로 인용 쪽 길이 기준으로도 본다
        blocks = sum(bl.size for bl in sm.get_matching_blocks())
        r = max(sm.ratio(), blocks / max(len(a), 1) * (0.9 if len(a) < len(b) else 1.0))
        if r > top:
            top, where = r, u
    # 한 줄에 여러 항·호를 몰아 적은 인용은 조문 전체와 겹치는 비율로 본다
    whole = norm(' '.join(units))
    if top < SIM_FLOOR and whole:
        sm = difflib.SequenceMatcher(None, a, whole, autojunk=False)
        cov = sum(bl.size for bl in sm.get_matching_blocks() if bl.size >= 4) / max(len(a), 1)
        if cov > top:
            top, where = cov, ' '.join(units)
    return top, where


def check_file(path, laws):
    src = path.read_text(encoding='utf-8')
    findings = []
    default = '상법' if path.name.startswith(('bkl', 'ex_bkl')) else '보험업법'
    for m in BOX.finditer(src):
        label, body = m.group(1), m.group(2)
        name, refs = parse_label(label, default)
        law = laws.get(name)
        if not law or not refs:
            continue
        lineno = src.count('\n', 0, m.start()) + 1
        # 제목 확인 (제목이 적혀 있으면)
        tm = re.search(r'제\s*\d+\s*조(?:\s*의\s*\d+)?\s*\(([^)]+)\)', label)
        if tm and len(refs) == 1 and refs[0] in law['arts']:
            real = law['arts'][refs[0]]['title']
            if norm(tm.group(1)) not in norm(real) and norm(real) not in norm(tm.group(1)):
                findings.append((lineno, label, '제목', f'교재 「{tm.group(1)}」 ↔ 현행 「{real}」', ''))
        for r in refs:
            if r not in law['arts']:
                findings.append((lineno, label, '없는 조문', f'제{r[0]}조' + (f'의{r[1]}' if r[1] else ''), ''))
        cur = refs
        for ln in lines_of(body):
            # 줄 첫머리의 '제N조'가 조문 제목일 때만 대상 조문을 바꾼다('제4조 제1항에 따라 …' 같은 참조는 제외)
            lead = HEAD.match(ln)
            if not lead:
                m2 = REF.match(ln)          # 괄호 없는 제목이라도 상자에 적힌 조문이면 제목으로 본다
                if m2 and (int(m2.group(1)), int(m2.group(2) or 0)) in refs:
                    lead = m2
            if lead:
                cur = [(int(lead.group(1)), int(lead.group(2) or 0))]
            units = [u for r in cur for u in law['arts'].get(r, {}).get('units', [])]
            if not units:
                continue
            sim, where = best(ln, units)
            text = ' '.join(units)
            miss = [n for n in NUM.findall(ln) if norm(n) not in norm(text)]
            if sim < SIM_FLOOR or miss:
                why = []
                if sim < SIM_FLOOR:
                    why.append(f'유사도 {sim:.2f}')
                if miss:
                    why.append('원문에 없는 숫자 ' + ', '.join(miss))
                findings.append((lineno, label, ' · '.join(why), ln, where))
    return findings


def main():
    if '--fetch' in sys.argv:
        fetch()
        return 0
    laws = load_laws()
    print('현행 법령 기준 —', ', '.join(f'{n} 시행 {v["eff"]}' for n, v in laws.items()))
    files = [a for a in sys.argv[1:] if not a.startswith('--')]
    paths = [ROOT / 'content' / f for f in files] if files else sorted((ROOT / 'content').glob('*.py'))
    total = 0
    for p in paths:
        fs = check_file(p, laws)
        if not fs:
            continue
        total += len(fs)
        print(f'\n── {p.name}  ({len(fs)}건)')
        for lineno, label, why, ln, where in fs:
            print(f'  {lineno:>5}  [{label.strip()[:40]}]  {why}')
            if ln:
                print(f'         교재: {ln[:150]}')
            if where:
                print(f'         현행: {where[:150]}')
    print(f'\n합계 {total}건')
    return 1 if total else 0


if __name__ == '__main__':
    sys.exit(main())
