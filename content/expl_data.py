# -*- coding: utf-8 -*-
"""문항 해설 모듈을 한자리에 모은다.

파일 하나가 (회차, 과목) 하나를 맡는다. 이름은 `expl_<회차>_<과목약칭>.py`,
안에 담긴 변수는 `EXPL_<회차>_<약칭 대문자>` 이고 키는 문항 번호(1부터)다.

    EXPL_49_BUL = {
      1: {"e": "정답은 ②이다. …",
          "w": {"1": "…", "3": "…", "4": "…"},
          "terms": [{"t": "자회사", "d": "…"}]},
    }

아직 쓰지 않은 (회차, 과목)의 모듈은 없어도 된다. 있는 것만 모은다.
"""
import importlib

SUBJ = {'bul': '보험업법', 'bkl': '보험계약법', 'sst': '손해사정이론'}
ROUNDS = (45, 46, 47, 48, 49)

EXPL = {}
LOADED = []

for _r in ROUNDS:
    for _abbr, _subj in SUBJ.items():
        _name = 'expl_%d_%s' % (_r, _abbr)
        try:
            _mod = importlib.import_module(_name)
        except ImportError:
            continue
        _table = getattr(_mod, 'EXPL_%d_%s' % (_r, _abbr.upper()), None)
        if not _table:
            continue
        LOADED.append((_r, _subj, len(_table)))
        for _no, _v in _table.items():
            EXPL[(_r, _subj, int(_no))] = _v
