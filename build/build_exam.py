# -*- coding: utf-8 -*-
"""문항 해설을 data/exam.json 에 병합한다.

문항 본문·보기·정답은 확정답안 PDF 에서 뽑아 온 것이라 손대지 않는다.
해설(`explanation`)과 오답 이유(`wrongWhy`)만 `content/expl_*.py` 에서 덮어쓴다.
같은 파일을 다시 돌려도 결과가 같다(멱등).

    python3 build/build_exam.py
"""
import json
from paths import DATA, kb
from expl_data import EXPL

YEAR = {45: '2022', 46: '2023', 47: '2024', 48: '2025', 49: '2026'}


def main():
    path = DATA / 'exam.json'
    exam = json.loads(path.read_text(encoding='utf-8'))

    index = {}
    for y, sessions in exam.items():
        for sess, subjects in sessions.items():
            for subj, lst in subjects.items():
                for q in lst:
                    index[(y, subj, q['no'])] = q

    written, missing = 0, []
    for (r, subj, no), v in EXPL.items():
        q = index.get((YEAR[r], subj, no))
        if q is None:
            missing.append((r, subj, no))
            continue
        q['explanation'] = v.get('e', '').strip()
        q['wrongWhy'] = {str(k): str(t).strip() for k, t in (v.get('w') or {}).items()}
        if v.get('terms'):
            q['terms'] = v['terms']
        written += 1

    path.write_text(json.dumps(exam, ensure_ascii=False, separators=(',', ':')),
                    encoding='utf-8')

    total = len(index)
    done = sum(1 for q in index.values() if (q.get('explanation') or '').strip())
    print(f'해설  {written}개 병합 · 전체 {done}/{total}문항 · exam.json {kb(path)}KB'
          + (f' · 대응 없는 항목 {missing}' if missing else ''))


if __name__ == '__main__':
    main()
