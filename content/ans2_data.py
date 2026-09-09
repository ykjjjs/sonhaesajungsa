# -*- coding: utf-8 -*-
"""2차 모범답안 모음.

과목별 모듈 ans2_<회차>_<과목키>.py 안의 ANS2 딕셔너리를 모아
{(회차, 과목명): {문항번호: {...}}} 형태로 돌려준다.
아직 쓰지 않은 회차·과목은 그냥 건너뛴다.

문항 하나의 모양
    3: {
      "plan": "① 쟁점  ② 근거  ③ 결론 순서로 쓴다.",   # 답안 뼈대(선택)
      "ans": "<p>…</p>",                                # 모범답안 본문(HTML)
      "keys": ["실화책임법", "경과실", "구상"],          # 채점 키워드
      "law": ["상법 제683조", "실화책임에 관한 법률 제3조"],
    }
"""
import importlib

# 과목명 ↔ 모듈 이름 조각
SUBJ_KEY = {
    '의학이론': 'med',
    '책임·근로자재해보상보험의 이론과 실무': 'lia',
    '제3보험의 이론과 실무': 'th3',
    '자동차보험의 이론과 실무(대인배상 및 자기신체손해)': 'carp',
    '회계원리': 'acc',
    '해상보험의 이론과 실무': 'mar',
    '책임·화재·기술보험 등의 이론과 실무': 'fire',
    '자동차보험의 이론과 실무(대물배상 및 차량손해)': 'caro',
    '자동차구조 및 정비이론과 실무': 'cars',
}

ROUNDS = [49, 48, 47, 46, 45, 44, 43, 40]


def load():
    out = {}
    for rnd in ROUNDS:
        for subj, key in SUBJ_KEY.items():
            name = 'ans2_%d_%s' % (rnd, key)
            try:
                mod = importlib.import_module(name)
            except ImportError:
                continue
            table = getattr(mod, 'ANS2', None)
            if table:
                out[(rnd, subj)] = table
    return out


ANS = load()
