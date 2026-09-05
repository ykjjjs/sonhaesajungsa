"""제47회 손해사정사 1차 PDF 복원.
숫자·문항번호·보기번호가 텍스트가 아닌 작은 이미지로 박혀 있는 PDF 전용.
구조(문항번호/보기번호)는 이미지 x좌표 군집으로 판정하고, 내용은 crop OCR."""
import pdfplumber, subprocess, os, re, difflib, tempfile, json, hashlib
from PIL import Image
from collections import Counter

DPI = 400
S = DPI / 72.0
SYM = "0123456789().,?~%·ㆍ-:;"

def _run_tess(pil, lang, psm, whitelist=None):
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        pil.save(f.name); p = f.name
    cmd = ['tesseract', p, 'stdout', '-l', lang, '--psm', str(psm)]
    if whitelist: cmd += ['-c', 'tessedit_char_whitelist=' + whitelist]
    r = subprocess.run(cmd, capture_output=True, text=True)
    os.unlink(p)
    return re.sub(r'\s+', ' ', r.stdout).strip()

def _crop(img, o, pad=6, scale=3, lpad=None):
    box = (max(0, int(o['x0']*S)-(pad if lpad is None else lpad)), max(0, int(o['top']*S)-pad),
           int(o['x1']*S)+pad, int((o['top']+o['height'])*S)+pad)
    c = img.crop(box).convert('L')
    c = c.resize((c.width*scale, c.height*scale), Image.LANCZOS)
    return c.point(lambda v: 0 if v < 165 else 255)

def ink_profile(img, o):
    """이미지의 세로 잉크 유무를 pt 절대좌표 기준으로 반환."""
    c = _crop(img, o, pad=2, scale=1).convert('L')
    w, h = c.size
    px = c.load()
    x00 = o['x0'] - 2 / S
    ink = [any(px[x, y] < 128 for y in range(h)) for x in range(w)]
    return ink, x00, w

def runs_and_gaps(img, o, min_gap_pt=11.0):
    ink, x00, w = ink_profile(img, o)
    gaps, runs, r0, g0 = [], [], None, None
    for x in range(w + 1):
        on = ink[x] if x < w else False
        if on:
            if g0 is not None:
                if (x - g0) / S >= min_gap_pt: gaps.append((x00 + g0 / S, x00 + x / S))
                g0 = None
            if r0 is None: r0 = x
        else:
            if r0 is not None: runs.append((x00 + r0 / S, x00 + x / S)); r0 = None
            if g0 is None: g0 = x
    return runs, gaps

def ocr_image(img, o, has_base, lpad=None):
    c = _crop(img, o, lpad=lpad)
    if has_base:
        return _run_tess(c, 'kor+eng', 7)
    t = _run_tess(c, 'eng', 7, SYM)
    if not re.search(r'[0-9?()]', t):
        t2 = _run_tess(c, 'eng', 8, SYM)
        if re.search(r'[0-9?()]', t2): t = t2
    return t

def splice(base, ocr):
    """base = 텍스트층의 정확한 한글(숫자 없음), ocr = 같은 구간의 숫자 포함 인식 결과."""
    if not re.search(r'\d', ocr): return base
    keep = [i for i, ch in enumerate(base) if not ch.isspace()]
    b_s = ''.join(base[i] for i in keep)
    o = re.sub(r'\s+', '', ocr)
    o_nod = re.sub(r'\d', '', o)
    sm = difflib.SequenceMatcher(None, o_nod, b_s, autojunk=False)
    if sm.ratio() < 0.5:
        return base + ' ' + ' '.join(re.findall(r'\d+', ocr))
    m = {}
    for a, b, n in sm.get_matching_blocks():
        for k in range(n): m[a+k] = b+k
    ins, j, run = [], 0, ''
    for ch in o:
        if ch.isdigit(): run += ch
        else:
            if run:
                t = m.get(j-1)
                pos = keep[t+1] if (t is not None and t+1 < len(keep)) else (keep[t]+1 if t is not None else 0)
                ins.append((pos, run)); run = ''
            j += 1
    if run:
        t = m.get(j-1); ins.append((keep[t]+1 if t is not None else len(base), run))
    out = list(base)
    for pos, run in sorted(ins, key=lambda t: -t[0]): out.insert(pos, run)
    return ''.join(out)

def render(path):
    d = tempfile.mkdtemp()
    subprocess.run(['pdftoppm', '-r', str(DPI), '-png', path, d + '/p'], check=True)
    return d

def structure_cols(pdf, mid):
    """보기번호 열 = 이미지 x0 최빈값. 문항번호 열 = 그 왼쪽 6~15pt 구간."""
    xs = {'L': [], 'R': []}
    for pg in pdf.pages:
        for o in pg.images:
            if o['height'] < 8 or o['top'] <= 95 or o['width'] > 600: continue
            xs['L' if o['x0'] < mid else 'R'].append(round(o['x0']))
    cols = {}
    for side, v in xs.items():
        if not v: cols[side] = (None, None); continue
        ox = Counter(v).most_common(1)[0][0]
        cols[side] = (ox - 15, ox - 6, ox)      # qlo, qhi, ox
    return cols

def parse(path, cache=None):
    cache = cache or {}
    d = render(path)
    pages = sorted(f for f in os.listdir(d) if f.endswith('.png'))
    qs, cur, bucket, qn, on = [], None, None, 0, 0
    with pdfplumber.open(path) as pdf:
        mid = pdf.pages[0].width * 0.485
        cols = structure_cols(pdf, mid)
        for i, pg in enumerate(pdf.pages):
            img = Image.open(os.path.join(d, pages[i]))
            words = [w for w in pg.extract_words(x_tolerance=1.5, y_tolerance=2) if w['top'] > 95]
            imgs = [o for o in pg.images if o['height'] >= 8 and o['top'] > 95 and o['width'] <= 600]
            toks = []
            # 같은 줄(top ±5)에 놓인 이미지끼리 묶어, 보기번호 열 이미지가 있는 줄에서는
            # 오른쪽에 이어지는 넓은 이미지도 다음 보기의 시작으로 본다 (2단 보기 배치 대응)
            imgs_sorted = sorted(imgs, key=lambda o: (o['top'], o['x0']))
            rows, cur_row, rtop = [], [], None
            for o in imgs_sorted:
                if rtop is None or abs(o['top']-rtop) <= 5:
                    cur_row.append(o); rtop = o['top'] if rtop is None else (rtop+o['top'])/2
                else:
                    rows.append(cur_row); cur_row = [o]; rtop = o['top']
            if cur_row: rows.append(cur_row)
            optstart = set()
            for row in rows:
                for side in ('L', 'R'):
                    qlo, qhi, ox = cols[side]
                    if ox is None: continue
                    anchor = [o for o in row if abs(o['x0']-ox) <= 2.5]
                    if not anchor: continue
                    wide_anchor = any(a['width'] > 30 for a in anchor)
                    for o in row:
                        if (o['x0'] < mid) != (side == 'L'): continue
                        if abs(o['x0']-ox) <= 2.5 or (wide_anchor and o['x0'] > ox + 20 and o['width'] > 30):
                            optstart.add(id(o))
            for o in imgs:
                side = 'L' if o['x0'] < mid else 'R'
                qlo, qhi, ox = cols[side]
                if qlo is not None and qlo <= o['x0'] <= qhi and o['width'] < 27:
                    toks.append({'x0': o['x0'], 'top': o['top'], 't': '', 'k': 'q'}); continue
                if id(o) in optstart:
                    if o['width'] <= 30:
                        toks.append({'x0': o['x0'], 'top': o['top'], 't': '', 'k': 'o'}); continue
                    # 한 이미지 안에 보기 2개가 들어 있는 경우(2단 배치) 넓은 공백에서 분할
                    runs, gaps = runs_and_gaps(img, o)
                    cuts = [g for g in gaps if o['x0'] + 25 < g[0] and g[1] < o['x1'] - 3]
                    segs, prev = [], o['x0']
                    for a, b in cuts:
                        segs.append((prev, a)); prev = b
                    segs.append((prev, o['x1']))
                    for a, b in segs:
                        toks.append({'x0': a, 'top': o['top'], 'k': 'o', 't': ''})
                        inner = [r for r in runs if r[0] >= a - 0.5 and r[1] <= b + 0.5]
                        start = (max(inner[0][1], inner[0][0] + 10.5) + 1.2) if inner else (a + 15)   # 첫 잉크 런 = 보기번호 → 건너뜀
                        sub = dict(o); sub['x0'] = start; sub['x1'] = b
                        if sub['x1'] - sub['x0'] < 2:
                            continue
                        cov = [w for w in words if w['x0'] >= sub['x0']-2 and w['x1'] <= sub['x1']+2 and abs(w['top']-sub['top']) < 9]
                        base = ' '.join(w['text'] for w in sorted(cov, key=lambda w: w['x0']))
                        key = f"{os.path.basename(path)}|{i}|{sub['x0']:.1f}|{sub['top']:.1f}|s2"
                        t = cache[key] if key in cache else ocr_image(img, sub, bool(base), lpad=1)
                        cache[key] = t
                        for w in cov: w['_d'] = True
                        txt = splice(base, t) if base else t
                        if txt: toks.append({'x0': start, 'top': o['top'], 't': txt, 'k': 't'})
                    continue
                cov = [w for w in words if w['x0'] >= o['x0']-2 and w['x1'] <= o['x1']+2 and abs(w['top']-o['top']) < 9]
                base = ' '.join(w['text'] for w in sorted(cov, key=lambda w: w['x0']))
                key = f"{os.path.basename(path)}|{i}|{o['x0']:.1f}|{o['top']:.1f}"
                if key in cache: t = cache[key]
                else:
                    t = ocr_image(img, o, bool(base)); cache[key] = t
                if not t and not base: continue
                for w in cov: w['_d'] = True
                toks.append({'x0': o['x0'], 'top': o['top'],
                             't': splice(base, t) if base else t, 'k': 't'})
            for w in words:
                if w.get('_d'): continue
                toks.append({'x0': w['x0'], 'top': w['top'], 't': w['text'], 'k': 't'})
            groups = []
            for sel in ([t for t in toks if t['x0'] < mid], [t for t in toks if t['x0'] >= mid]):
                sel = sorted(sel, key=lambda t: (t['top'], t['x0']))
                curg, top = [], None
                for t in sel:
                    if top is None or abs(t['top']-top) <= 5:
                        curg.append(t); top = t['top'] if top is None else (top+t['top'])/2
                    else:
                        groups.append(sorted(curg, key=lambda x: x['x0'])); curg = [t]; top = t['top']
                if curg: groups.append(sorted(curg, key=lambda x: x['x0']))
            for g in groups:
                for t in g:
                    if t['k'] == 'q':
                        if cur: qs.append(cur)
                        qn += 1; on = 0
                        cur = {'no': qn, 'stem': '', 'options': {},
                               'pos': {'page': i, 'x0': t['x0'], 'top': t['top']}}; bucket = 'stem'; continue
                    if cur is None: continue
                    if t['k'] == 'o':
                        on += 1
                        if on <= 4: cur['options'][on] = ''; bucket = on
                        else: bucket = None
                        continue
                    txt = t['t'].strip()
                    if not txt: continue
                    if bucket == 'stem': cur['stem'] += (' ' if cur['stem'] else '') + txt
                    elif isinstance(bucket, int) and bucket in cur['options']:
                        cur['options'][bucket] += (' ' if cur['options'][bucket] else '') + txt
    if cur: qs.append(cur)
    subprocess.run(['rm', '-rf', d])
    return qs, cache
