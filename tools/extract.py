import pdfplumber, re, sys, json, unicodedata

CIRCLED = "①②③④⑤"

def cluster_lines(words, tol=4.5):
    ws = sorted(words, key=lambda w: (w['top'], w['x0']))
    lines, cur, cur_top = [], [], None
    for w in ws:
        if cur_top is None or abs(w['top'] - cur_top) <= tol:
            cur.append(w)
            cur_top = w['top'] if cur_top is None else (cur_top + w['top'])/2
        else:
            lines.append(cur); cur = [w]; cur_top = w['top']
    if cur: lines.append(cur)
    out = []
    for ln in lines:
        ln = sorted(ln, key=lambda w: w['x0'])
        out.append((round(min(w['top'] for w in ln),1), ' '.join(w['text'] for w in ln)))
    return out

def column_boundary(words, width):
    """Find the vertical whitespace gutter nearest the page centre."""
    occupied = [False] * (int(width) // 5 + 2)
    for w in words:
        for b in range(int(w['x0']) // 5, int(w['x1']) // 5 + 1):
            if 0 <= b < len(occupied): occupied[b] = True
        # widest empty run inside the middle third
    lo, hi = int(width * 0.33) // 5, int(width * 0.67) // 5
    best, run_start = None, None
    for b in range(lo, hi + 1):
        if not occupied[b]:
            if run_start is None: run_start = b
        else:
            if run_start is not None:
                if best is None or b - run_start > best[1] - best[0]: best = (run_start, b)
                run_start = None
    if run_start is not None and (best is None or hi + 1 - run_start > best[1] - best[0]):
        best = (run_start, hi + 1)
    if best is None or (best[1] - best[0]) < 2: return width / 2
    return (best[0] + best[1]) / 2 * 5

def page_lines(page):
    words = page.extract_words(use_text_flow=False, keep_blank_chars=False,
                               x_tolerance=1.5, y_tolerance=2)
    mid = page.width * RATIO
    left  = [w for w in words if w['x0'] <  mid]
    right = [w for w in words if w['x0'] >= mid]
    return cluster_lines(left) + cluster_lines(right)

RATIO = 0.485
JUNK = re.compile(r'^(━+|─+|-+)$')
SPLIT = re.compile(r'(?=[①②③④])')
HDR  = re.compile(r'(손해사정사\s*시험|보험전문인|\d+\s*쪽$|^\d+$)')

def doc_lines(path):
    res = []
    with pdfplumber.open(path) as pdf:
        for pg in pdf.pages:
            for top, t in page_lines(pg):
                t = t.strip()
                if not t or JUNK.match(t): continue
                if HDR.search(t) and len(t) < 40: continue
                for part in SPLIT.split(t):
                    part = part.strip()
                    if part: res.append(part)
    return res

NUMSP = re.compile(r'^(\d)\s+(\d)\s*[.．]')
QSTART = re.compile(r'^(\d{1,2})\s*[.．]\s*(.*)')

def parse(path):
    lines = doc_lines(path)
    qs, cur, bucket = [], None, None
    expect = 1
    for t in lines:
        t = NUMSP.sub(lambda m: m.group(1)+m.group(2)+'.', t)
        m = QSTART.match(t)
        if m and expect <= int(m.group(1)) <= expect + 3 and len(m.group(2)) > 4:
            if cur: qs.append(cur)
            cur = {"no": int(m.group(1)), "stem": m.group(2).strip(), "options": {}}
            bucket = "stem"; expect = int(m.group(1)) + 1
            continue
        if cur is None: continue
        # option markers
        hit = None
        for i, c in enumerate(CIRCLED[:4], 1):
            if t.startswith(c):
                hit = (i, t[1:].strip()); break
        if hit:
            cur["options"][hit[0]] = hit[1]; bucket = hit[0]
        else:
            if bucket == "stem":
                cur["stem"] += " " + t
            elif isinstance(bucket, int) and bucket in cur["options"]:
                cur["options"][bucket] += " " + t
    if cur: qs.append(cur)
    return qs

if __name__ == "__main__":
    qs = parse(sys.argv[1])
    print(f"parsed {len(qs)} questions")
    bad = [q for q in qs if len(q["options"]) != 4]
    print(f"options!=4: {[ (q['no'], len(q['options'])) for q in bad ]}")
    if len(sys.argv) > 2:
        json.dump(qs, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
