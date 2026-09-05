# -*- coding: utf-8 -*-
"""손해사정사 1차 전자교재 콘텐츠.
근거: 보험업법 [법률 제20436호, 시행 2025. 1. 31.] — 국가법령정보센터 조문 대조."""

TERMS = {
 "보험상품": {"d": "위험보장을 목적으로 우연한 사건 발생에 관하여 금전 및 그 밖의 급여를 지급할 것을 약정하고 대가를 수수하는 계약.",
   "more": "생명보험상품·손해보험상품·제3보험상품으로 나뉘며, 국민건강보험·고용보험 등 대통령령으로 정하는 것은 보험상품에서 제외된다.",
   "src": "보험업법 제2조 제1호"},
 "보험업": {"d": "보험상품의 취급과 관련하여 발생하는 보험의 인수, 보험료 수수 및 보험금 지급 등을 영업으로 하는 것.",
   "more": "생명보험업·손해보험업·제3보험업으로 구분된다. ‘영업으로’라는 말이 붙어 있어 일회적인 위험 인수는 보험업이 아니다.",
   "src": "보험업법 제2조 제2호"},
 "제3보험": {"d": "사람의 질병·상해 또는 이에 따른 간병에 관하여 금전 및 그 밖의 급여를 지급할 것을 약정하는 보험.",
   "more": "사람에 관한 보험이라는 점에서 생명보험을 닮았고, 실제 손해를 메운다는 점에서 손해보험을 닮았다. 그래서 생·손보 어느 쪽이든 취급할 수 있다.",
   "src": "보험업법 제2조 제1호 다목"},
 "전문보험계약자": {"d": "보험계약에 관한 전문성, 자산규모 등에 비추어 보험계약의 내용을 이해하고 이행할 능력이 있는 자.",
   "more": "국가, 한국은행, 대통령령으로 정하는 금융기관, 주권상장법인 등이 이에 해당한다. 다만 일부는 보험회사에 서면으로 통지하고 보험회사가 동의하면 일반보험계약자로 대우받을 수 있다.",
   "src": "보험업법 제2조 제19호"},
 "일반보험계약자": {"d": "전문보험계약자가 아닌 보험계약자.",
   "more": "설명의무·적합성 원칙 등 모집 규제의 보호를 받는 쪽이다. 규제의 두께가 전문보험계약자와 다르다는 점이 실익이다.",
   "src": "보험업법 제2조 제20호"},
 "모집": {"d": "보험계약의 체결을 중개하거나 대리하는 것.",
   "more": "보험회사가 스스로 보험을 인수하는 행위는 모집이 아니다. 모집을 할 수 있는 자는 법이 한정하고 있다.",
   "src": "보험업법 제2조 제12호"},
 "상호회사": {"d": "보험업을 경영할 목적으로 보험업법에 따라 설립된 회사로서 보험계약자를 사원으로 하는 회사.",
   "more": "주식회사의 주주에 해당하는 자리에 보험계약자가 앉는다. 그래서 명칭에 ‘상호회사’를 반드시 넣어야 한다(제35조).",
   "src": "보험업법 제2조 제7호"},
 "자회사": {"d": "보험회사가 다른 회사(민법 또는 특별법에 따른 조합을 포함)의 의결권 있는 발행주식(출자지분을 포함) 총수의 100분의 15를 초과하여 소유하는 경우의 그 다른 회사.",
   "more": "상법상 모자회사 기준(50% 초과)이나 공정거래법상 계열 기준과 다르다. 보험업법은 15% 초과라는 낮은 문턱을 쓴다.",
   "src": "보험업법 제2조 제18호"},
 "외국보험회사": {"d": "대한민국 이외의 국가의 법령에 따라 설립되어 대한민국 이외의 국가에서 보험업을 경영하는 자.",
   "more": "설립준거법과 영업지가 모두 국외여야 한다. 국내에 지점을 두면 ‘외국보험회사국내지점’으로 별도의 규율을 받는다.",
   "src": "보험업법 제2조 제8호"},
 "허가": {"d": "법령상의 일반적 금지를 특정인에게 풀어 주는 행정행위. 보험업은 보험종목별로 금융위원회의 허가를 받아야 한다.",
   "more": "보험업법은 ‘허가’와 ‘인가’를 조문마다 구분해 쓴다. 지문에서 둘을 바꿔 놓는 것이 흔한 함정이다.",
   "src": "보험업법 제4조 제1항"},
 "겸영": {"d": "하나의 보험회사가 둘 이상의 보험업을 함께 경영하는 것.",
   "more": "생명보험업과 손해보험업의 겸영은 원칙적으로 금지된다. 다만 생명보험·제3보험의 재보험, 다른 법령에 따라 겸영할 수 있는 종목, 제3보험에 부가되는 보험은 예외다.",
   "src": "보험업법 제10조"},
 "기금": {"d": "상호회사의 설립 재원. 주식회사의 자본금에 대응한다.",
   "more": "정관에는 ‘기금의 총액’, ‘기금 갹출자가 가질 권리’, ‘기금과 설립비용의 상각 방법’을 적어야 한다. ‘기금의 납입 방법’은 정관기재사항이 아니다.",
   "src": "보험업법 제34조"},
}


from terms_more import MORE
TERMS.update(MORE)

from terms_more2 import MORE2
TERMS.update(MORE2)

from bul_ch1 import CH1
from bul_ch2 import CH2
from bul_ch3 import CH3
from bul_ch4 import CH4
from bul_ch567 import CH5, CH6, CH7
from bkl_ch1 import BK_CH1
from bkl_ch23 import BK_CH2, BK_CH3
from sst_ch123 import SS_CH1, SS_CH2, SS_CH3
from sst_ch45 import SS_CH4, SS_CH5

BOOK = {
 "보험업법": {"desc": "조문 하나하나를 근거로 짚어 갑니다.",
   "chapters": [CH1, CH2, CH3, CH4, CH5, CH6, CH7]},
 "보험계약법": {"desc": "상법 제4편(보험)의 통칙과 각칙을 판례와 함께.",
   "chapters": [BK_CH1, BK_CH2, BK_CH3]},
 "손해사정이론": {"desc": "리스크에서 손해사정 실무·재보험까지 이론의 뼈대.",
   "chapters": [SS_CH1, SS_CH2, SS_CH3, SS_CH4, SS_CH5]},
}

# ── 보충 콘텐츠 병합 ──────────────────────────────────────────
def _merge(book, subj, ex):
    chs = book[subj]['chapters']
    for (ci, si), add in ex.items():
        sec = chs[ci]['sections'][si]
        sec['html'] = sec['html'] + add.get('html', '')
        sec['cards'] = list(sec.get('cards', [])) + list(add.get('cards', []))

from ex_bul_a import EX_BUL_A
from ex_bul_b import EX_BUL_B
from ex_bul_c import EX_BUL_C
from ex_bul_d import EX_BUL_D
from ex_bkl_a import EX_BKL_A
from ex_bkl_b import EX_BKL_B
from ex_sst_a import EX_SST_A
from ex_sst_b import EX_SST_B

for _ex in (EX_BUL_A, EX_BUL_B, EX_BUL_C, EX_BUL_D):
    _merge(BOOK, "보험업법", _ex)
for _ex in (EX_BKL_A, EX_BKL_B):
    _merge(BOOK, "보험계약법", _ex)
for _ex in (EX_SST_A, EX_SST_B):
    _merge(BOOK, "손해사정이론", _ex)

# 절 끝에 붙는 '기출' 상자 (보험업법은 각 장 파일 본문에 직접 넣었다)
from gichul_box import GICHUL_BKL, GICHUL_SST
_merge(BOOK, "보험계약법", GICHUL_BKL)
_merge(BOOK, "손해사정이론", GICHUL_SST)


# ── 기출 대응표 붙이기 ────────────────────────────────────────
# tools/build_map.py 가 만든 exam_map.MAP 을 절마다 exq 로 심는다.
# 대응표를 다시 만드는 중에는 파일이 없을 수 있으므로 없으면 건너뛴다.
try:
    from exam_map import MAP as _EXAM_MAP
except ImportError:
    _EXAM_MAP = {}

for (_subj, _ci, _si), _rows in _EXAM_MAP.items():
    try:
        _sec = BOOK[_subj]['chapters'][_ci]['sections'][_si]
    except (KeyError, IndexError):
        continue
    _sec['exq'] = [[r['r'], r['s'], r['n'], r.get('q', '')] for r in _rows]
