# -*- coding: utf-8 -*-
"""'쉽게 이해하기' 원고를 (과목, 장, 절) 키로 모은다. build/build_book.py 가 절마다 easy 로 심는다."""
from easy_bul import EASY_BUL
from easy_bkl import EASY_BKL
from easy_sst import EASY_SST

EASY = {}
for _subj, _table in (('보험업법', EASY_BUL), ('보험계약법', EASY_BKL), ('손해사정이론', EASY_SST)):
    for (_ci, _si), _v in _table.items():
        EASY[(_subj, _ci, _si)] = _v
