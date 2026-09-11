# -*- coding: utf-8 -*-
"""저장소 안에서만 경로를 잡는다. 컨테이너 절대경로를 쓰지 않는다."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'app'
CONTENT = ROOT / 'content'
DATA = ROOT / 'data'
PUBLIC = ROOT / 'public'
DIST = ROOT / 'dist'          # 빌드 산출물(커밋하지 않음)
PREVIEW = DIST / 'preview'    # 전체 콘텐츠가 박힌 오프라인본
ARTIFACT = DIST / 'artifact'  # 아티팩트 발행용

for d in (DIST, PREVIEW, ARTIFACT):
    d.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(CONTENT))

FREE_YEAR = '2026'   # 결제 전에 열어 두는 회차 (제49회)
# 결제 전(가입만 한 계정·체험 모드)에 여는 예시 문항
FREE_Q1 = {'보험업법': [1, 2, 3, 4], '보험계약법': [1, 2, 3], '손해사정이론': [1, 2, 3]}   # 2026년 1차 10문항
FREE_Q2 = [('의학이론', 1),                                                          # 제49회 2차 3문항
           ('회계원리', 1),
           ('자동차보험의 이론과 실무(대물배상 및 차량손해)', 1)]
FREE_BOOK = [('보험업법', '총칙')]                                                    # 전자교재 무료 장

PRICE = 9900         # 원 — 공인중개사(5,500)와 반드시 다르게 둘 것

def kb(p):
    return Path(p).stat().st_size // 1024
