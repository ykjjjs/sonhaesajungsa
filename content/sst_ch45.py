# -*- coding: utf-8 -*-
"""손해사정이론 제4장 손해사정 실무(4절) · 제5장 재보험(3절)"""

L1 = {
 "title": "손해사정의 의의와 절차",
 "desc": "여섯 단계", "minutes": 7, "src": "손해사정 실무",
 "lead": "손해사정은 사고가 보상 대상인지를 판단하고 손해액과 지급보험금을 확정하는 업무이다. 절차의 각 단계가 곧 손해사정사의 업무 범위가 되므로, 단계별 내용과 인과관계 학설을 함께 정리한다.",
 "html": """
<h2><span class="hno">01</span>손해사정의 의의</h2>
<p>손해사정이란 보험사고로 인한 손해의 발생 사실을 확인하고, 보험약관 및 관계 법규의 적용 가능 여부를 판단하며, 손해액과 보험금을 <b>사정(査定)</b>하는 일련의 업무를 말한다.</p>

<h2><span class="hno">02</span>절차</h2>
<div class="bx c"><h5><span class="bdg">개념</span>손해사정의 여섯 단계</h5>
  <div class="bx-s"><ol>
    <li><b>사고 접수</b>와 계약 사항 확인</li>
    <li><b>보험사고의 확인</b> — 사고 사실과 원인 조사</li>
    <li><b>보상책임 유무의 판단</b> — 약관·법규 적용, 면책 여부</li>
    <li><b>손해액의 산정</b></li>
    <li><b>보험금의 계산</b> — 공제·비례보상·한도 적용</li>
    <li><b>보험금 지급</b>과 대위·구상</li>
  </ol></div>
  <div class="bx-d"><p>3단계와 4단계를 섞지 않는 것이 중요하다. <b>보상책임의 유무</b>는 법률 판단이고, <b>손해액 산정</b>은 사실 확정이다. 보상책임이 없으면 손해액을 아무리 정확히 계산해도 의미가 없다.</p>
  <p>보험업법 제7장이 규율하는 손해사정서 작성·교부는 5~6단계에 해당한다. 이론과 법이 여기서 만난다.</p></div></div>

<h2><span class="hno">03</span>손해액 산정의 기준</h2>
<ul>
  <li><b>시가(actual cash value)</b> — 재조달가액에서 감가상각을 뺀 값. 원칙</li>
  <li><b>재조달가액(replacement cost)</b> — 같은 것을 새로 마련하는 데 드는 값. 신가보험에서 적용</li>
  <li><b>협정보험가액</b> — 당사자가 미리 정한 값(기평가보험)</li>
</ul>

<div class="bx t"><h5><span class="bdg">함정</span>손해액 산정 비용의 부담자</h5>
  <div class="bx-s">손해액의 산정에 관한 비용은 <b>보험자</b>의 부담으로 한다(상법 제676조 제2항). 보험증권 재교부 비용이 <b>보험계약자</b> 부담인 것과 짝을 이룬다.</div></div>
""",
 "cards": [
   ["손해사정의 3단계와 4단계는?", "<b>보상책임 유무의 판단</b> → <b>손해액의 산정</b>"],
   ["손해액 산정의 원칙적 기준은?", "<b>시가</b>(재조달가액 − 감가상각)"],
   ["손해액 산정 비용의 부담자는?", "<b>보험자</b>"],
 ]}

L2 = {
 "title": "공제(deductible)",
 "desc": "네 가지 방식과 계산", "minutes": 9, "src": "손해사정 실무",
 "lead": "공제는 소액 손해를 보상에서 제외하고 도덕적 위태를 억제하는 장치이다. 유형마다 계산식이 다르므로 계산 문제로 직접 출제된다. 유형별 산정식을 정확히 구별하여야 한다.",
 "html": """
<h2><span class="hno">01</span>왜 두는가</h2>
<ul>
  <li>소액 청구를 걸러 <b>사업비 절감</b></li>
  <li>자기부담을 남겨 <b>도덕적 위태 억제</b></li>
  <li>보험료 인하로 <b>가입 부담 완화</b></li>
</ul>

<h2><span class="hno">02</span>네 가지 방식</h2>
<div class="bx c"><h5><span class="bdg">개념</span>공제의 유형</h5>
  <div class="bx-s"><ul>
    <li><b>직접공제(straight deductible)</b> — 손해액에서 공제액을 뺀 나머지를 보상</li>
    <li><b>참여공제(franchise deductible)</b> — 손해액이 기준을 넘으면 <b>전액</b> 보상, 넘지 않으면 무보상</li>
    <li><b>소멸성공제(disappearing deductible)</b> — 손해액이 커질수록 공제액이 줄어 결국 사라진다</li>
    <li><b>종합공제(aggregate deductible)</b> — 일정 기간 누적 손해가 기준을 넘은 뒤부터 보상</li>
  </ul></div>
  <div class="bx-d"><p><b>대기기간(waiting period)</b>은 시간을 기준으로 한 공제로 볼 수 있다. 소득보상보험 등에서 쓰인다.</p></div></div>

<h2><span class="hno">03</span>소멸성공제의 계산</h2>
<p>보험금 = (손해액 − 공제 한도) × <b>조정계수</b></p>
<div class="bx e"><h5><span class="bdg">사례</span>제47회 손해사정이론 27번</h5>
  <div class="bx-s">공제 한도 <b>50만 원</b>, 손실 금액 <b>600만 원</b>, 조정계수 <b>110%</b><br>
  보험금 = (600 − 50) × 1.1 = 550 × 1.1 = <b>605만 원</b></div>
  <div class="bx-d"><p>조정계수가 100%를 넘는 이유는, 공제로 줄어든 부분을 손해가 커질수록 되돌려 주기 위해서다. 손해액이 일정 수준에 이르면 (손해액 − 공제액) × 계수가 손해액과 같아지고, 그 지점에서 공제가 <b>소멸</b>한다.</p>
  <p>소멸 지점은 <b>손해액 = 공제액 × 계수 ÷ (계수 − 1)</b>로 구한다. 위 예에서는 50 × 1.1 ÷ 0.1 = 550만 원에서 공제가 사라지고, 그 이상은 손해액 전액이 보상된다. 다만 문제는 대개 계산식만 적용하면 되도록 출제된다.</p></div></div>

<h2><span class="hno">04</span>공동보험조항(coinsurance)</h2>
<p>보험가액의 일정 비율 이상을 부보하도록 요구하고, 미달 시 비례 삭감하는 조항이다.</p>
<div class="bx c"><h5><span class="bdg">개념</span>80% 코인슈어런스</h5>
  <div class="bx-s">보험금 = 손해액 × <b>보험금액 ÷ (보험가액 × 80%)</b> (단, 손해액 한도)</div>
  <div class="bx-d"><p>왜 이런 조항을 두는가. 대부분의 화재 손해는 전손이 아니라 부분손해다. 코인슈어런스가 없으면 계약자는 소액만 부보하고도 부분손해를 전액 받으므로, 충분히 부보한 계약자와 형평이 깨진다.</p></div></div>
""",
 "cards": [
   ["참여공제와 직접공제의 차이는?", "참여공제는 기준 초과 시 <b>전액</b> 보상, 직접공제는 <b>공제 후</b> 보상"],
   ["소멸성공제의 계산식은?", "(손해액 − 공제 한도) × <b>조정계수</b>"],
   ["공제를 두는 세 이유는?", "사업비 절감 · <b>도덕적 위태 억제</b> · 보험료 인하"],
   ["80% 코인슈어런스의 분모는?", "<b>보험가액 × 80%</b>"],
 ]}

L3 = {
 "title": "보험금 산정 — 실손보상과 그 예외",
 "desc": "원칙과 네 가지 예외", "minutes": 8, "src": "손해사정 실무",
 "lead": "손해보험의 보험금은 실제 손해를 초과하지 아니한다. 다만 기평가보험, 대체비용보험, 정액보험과 같이 이 원칙이 그대로 적용되지 않는 경우가 있다. 원칙을 지키는 장치와 예외를 구별하여 정리한다.",
 "html": """
<h2><span class="hno">01</span>실손보상의 원칙</h2>
<p>피보험자는 보험으로 <b>사고 이전의 상태로 회복</b>될 뿐, 그 이상의 이득을 얻지 못한다. 이 원칙을 지키는 장치가 보험가액 한도, 비례보상, 보험자대위, 타보험조항이다.</p>

<h2><span class="hno">02</span>네 가지 예외</h2>
<div class="bx c"><h5><span class="bdg">개념</span>실손보상이 관철되지 않는 자리</h5>
  <div class="bx-s"><ul>
    <li><b>기평가보험</b> — 협정보험가액으로 보상</li>
    <li><b>신가보험</b> — 감가 없이 재조달가액으로 보상</li>
    <li><b>생명보험 등 정액보험</b> — 약정 금액 지급</li>
    <li><b>대체비용보험·평가액보험</b> 등 특약</li>
  </ul></div>
  <div class="bx-d"><p>신가보험이 허용되는 이유는 <b>복구 기능</b>이다. 20년 된 공장 설비에 감가된 금액만 주면 공장은 다시 돌아가지 못한다. 다만 도덕적 위태를 키우므로 실제 복구를 조건으로 하는 등의 제어가 붙는다.</p></div></div>

<h2><span class="hno">03</span>보험금 계산의 순서</h2>
<ol>
  <li><b>손해액</b> 확정 (시가 또는 재조달가액)</li>
  <li><b>비례보상</b> 적용 (일부보험·코인슈어런스)</li>
  <li><b>공제</b> 차감</li>
  <li><b>보험금액 한도</b> 적용</li>
  <li><b>중복보험 분담</b> 조정</li>
</ol>
<div class="bx t"><h5><span class="bdg">함정</span>순서를 바꾸면 답이 달라진다</h5>
  <div class="bx-s">비례보상을 먼저 하고 공제를 빼는지, 공제를 먼저 빼고 비례하는지에 따라 결과가 다르다. 약관이 정한 순서를 따르되, 시험에서는 대개 <b>비례 → 공제</b> 순서로 낸다.</div></div>

<h2><span class="hno">04</span>일부보험 계산 예</h2>
<div class="bx e"><h5><span class="bdg">사례</span>단계별 적용</h5>
  <div class="bx-s">보험가액 2억, 보험금액 1억, 손해액 4천만, 공제 200만이면<br>
  ① 비례: 4,000만 × (1억 ÷ 2억) = 2,000만<br>
  ② 공제: 2,000만 − 200만 = <b>1,800만 원</b></div></div>
""",
 "cards": [
   ["실손보상의 예외 넷은?", "<b>기평가보험 · 신가보험 · 정액보험</b> · 대체비용보험"],
   ["신가보험을 허용하는 이유는?", "감가액만으로는 <b>복구</b>가 불가능하기 때문"],
   ["보험금 계산의 일반 순서는?", "손해액 → <b>비례보상</b> → <b>공제</b> → 보험금액 한도 → 중복보험 분담"],
 ]}

L4 = {
 "title": "배상책임보험의 담보기준과 특약",
 "desc": "사고발생기준 vs 청구기준", "minutes": 8, "src": "배상책임보험 실무",
 "lead": "배상책임보험의 담보기준은 사고발생기준과 청구기준으로 나뉜다. 어느 시점을 기준으로 담보하는지에 따라 보험기간의 의미와 부수 특약이 달라진다. 청구기준에서는 소급담보일자와 보고기간연장특약이 함께 출제된다.",
 "html": """
<h2><span class="hno">01</span>두 담보기준</h2>
<table>
  <tr><th></th><th>사고발생기준</th><th>청구기준</th></tr>
  <tr><td>담보 요건</td><td>보험기간 중 <b>사고 발생</b></td><td>보험기간 중 <b>배상청구 제기</b></td></tr>
  <tr><td>보험자 관점</td><td>장기 꼬리위험(long tail) 부담</td><td><b>불확실성 감소</b></td></tr>
  <tr><td>피보험자 관점</td><td>담보 공백 적음</td><td>보험 중단 시 <b>공백 위험</b></td></tr>
  <tr><td>주요 적용</td><td>일반배상책임</td><td>전문직·생산물·환경오염 배상책임</td></tr>
</table>

<div class="bx c"><h5><span class="bdg">개념</span>청구기준의 두 장치</h5>
  <div class="bx-s"><ul>
    <li><b>소급담보일자(retroactive date)</b> — 이 날짜 이후에 발생한 사고만 담보</li>
    <li><b>보고연장기간(ERP, tail cover)</b> — 계약 종료 후 일정 기간 내 청구를 담보</li>
  </ul></div>
  <div class="bx-d"><p>이 둘이 있어야 청구기준이 제대로 작동한다. 소급담보일자는 <b>과거 쪽 경계</b>를, 보고연장기간은 <b>미래 쪽 경계</b>를 긋는다.</p>
  <p>“보험계약 체결 이후 발생한 사고가 대상이다”라는 설명이 틀린 이유가 여기에 있다. 소급담보일자를 계약 체결 전으로 설정하면 그 이후에 발생한 사고도 담보되기 때문이다.</p></div></div>

<h2><span class="hno">02</span>재보험특약의 sunset clause</h2>
<p>청구기준과 발상이 닮은 재보험 조항이 있다. <b>sunset clause</b>는 보험기간 종료 후 <b>일정 기간 이내</b>에 발생한 사고 건에 대해 재보험자에게 통지할 것을 요구하고, 그 기간이 지나면 재보험자의 책임이 존재하지 않음을 명시한다. 통상 배상책임보험 관련 <b>초과손해액재보험</b> 특약에 적용된다.</p>
<div class="bx e"><h5><span class="bdg">사례</span>제47회 손해사정이론 33번</h5>
  <div class="bx-s">위 설명을 주고 조항 이름을 물었다. 정답은 <b>sunset clause</b>. 선택지에는 commutation clause, counsel and concur clause, reports and remittance clause가 함께 나왔다.</div></div>

<h2><span class="hno">03</span>주요 특약조항</h2>
<ul>
  <li><b>commutation clause</b> — 미결 손해를 일시금으로 정산하고 관계를 종료</li>
  <li><b>counsel and concur clause</b> — 중요한 소송 대응에 재보험자의 동의를 요구</li>
  <li><b>reports and remittance clause</b> — 출재 명세 보고와 정산금 송금의 주기·방법</li>
  <li><b>sunset clause</b> — 통지 기간을 제한하여 꼬리위험을 차단</li>
</ul>
""",
 "cards": [
   ["청구기준의 담보 요건은?", "보험기간 중 <b>배상청구</b>가 제기될 것"],
   ["청구기준의 두 경계 장치는?", "<b>소급담보일자</b>(과거) · <b>보고연장기간</b>(미래)"],
   ["sunset clause의 기능은?", "보험기간 종료 후 <b>통지 기간</b>을 제한해 꼬리위험 차단"],
   ["청구기준이 주로 쓰이는 보험은?", "전문직·생산물·환경오염 등 <b>잠복형</b> 배상책임"],
 ]}

RE1 = {
 "title": "재보험의 의의와 기능",
 "desc": "보험자의 보험", "minutes": 7, "src": "재보험론",
 "lead": "재보험은 보험자가 인수한 위험의 일부 또는 전부를 다른 보험자에게 다시 인수시키는 계약이다. 원보험계약과의 법적 관계, 그리고 재보험의 네 가지 기능이 이 절의 내용이다.",
 "html": """
<h2><span class="hno">01</span>의의</h2>
<p>재보험은 보험자(원보험자·출재사)가 인수한 위험의 전부 또는 일부를 다른 보험자(재보험자·수재사)에게 전가하는 계약이다. 법적으로는 <b>독립한 손해보험계약</b>이다.</p>
<div class="bx c"><h5><span class="bdg">개념</span>원보험과의 관계</h5>
  <div class="bx-s"><ul>
    <li>재보험계약은 원보험계약과 <b>별개의 계약</b>이다</li>
    <li>원보험계약자는 재보험자에게 <b>직접 청구할 수 없다</b>(cut-through 조항이 있으면 예외)</li>
    <li>재보험은 <b>불이익변경금지의 예외</b>다(상법 제663조)</li>
    <li>보험업법상 재보험은 <b>손해보험업의 한 종목</b>이다</li>
  </ul></div>
  <div class="bx-d"><p>재보험이 불이익변경금지의 예외인 이유는 당사자가 모두 전문가인 <b>기업보험</b>이기 때문이다. 해상보험과 나란히 예외로 열거된 것도 같은 맥락이다.</p></div></div>

<h2><span class="hno">02</span>기능</h2>
<ul>
  <li><b>인수능력(capacity) 확대</b> — 자기 자본으로 감당 못 할 큰 위험도 인수</li>
  <li><b>실적 안정</b> — 대형 손해의 충격을 완화</li>
  <li><b>대재해 보호</b> — 누적 위험 방어</li>
  <li><b>경영 지원</b> — 재보험자의 언더라이팅·요율 노하우 제공, 미경과보험료 부담 완화</li>
</ul>

<h2><span class="hno">03</span>운영방식</h2>
<div class="bx c"><h5><span class="bdg">개념</span>clean-cut과 run-off</h5>
  <div class="bx-s"><ul>
    <li><b>clean-cut 방식</b> — 특약 기간이 끝나면 미경과분·미결손해를 정산하여 관계를 <b>끊는다</b></li>
    <li><b>run-off 방식</b> — 특약출재기간이 끝나도 출재된 개별 원보험계약의 만기 도래 또는 청산이 <b>완전히 종결될 때까지</b> 재보험자의 책임이 계속된다</li>
    <li><b>cut-off 방식</b> — 특약 종료와 동시에 책임이 끊긴다</li>
    <li><b>cut-through 방식</b> — 원보험계약자가 재보험자에게 직접 청구할 수 있게 하는 조항</li>
  </ul></div>
  <div class="bx-d"><p>제47회 손해사정이론 35번이 run-off 방식을 물었다. 네 용어의 형태가 유사하므로 다음과 같이 구별한다. <b>run-off</b>는 잔여 책임을 만기까지 유지하는 방식, <b>cut-off</b>는 해지 시점에 책임을 즉시 종료하는 방식, <b>clean-cut</b>은 미경과보험료를 정산하고 종료하는 방식, <b>cut-through</b>는 원보험계약자가 재보험자에게 직접 청구할 수 있도록 하는 조항이다.</p></div></div>
""",
 "cards": [
   ["재보험계약의 법적 성질은?", "원보험과 <b>별개</b>의 독립한 손해보험계약"],
   ["재보험의 네 기능은?", "<b>인수능력 확대</b> · 실적 안정 · 대재해 보호 · 경영 지원"],
   ["run-off 방식이란?", "특약 종료 후에도 개별 원보험계약이 <b>완전히 종결될 때까지</b> 책임 계속"],
   ["cut-through 조항이란?", "원보험계약자가 재보험자에게 <b>직접 청구</b>할 수 있게 하는 조항"],
 ]}

RE2 = {
 "title": "비례재보험과 비비례재보험",
 "desc": "무엇을 나누는가", "minutes": 9, "src": "재보험론",
 "lead": "재보험은 나누는 대상에 따라 두 갈래로 구분된다. 비례재보험은 보험금액을 비율로 나누고, 비비례재보험은 손해액을 기준으로 나눈다. 이 구분이 특약의 구조와 계산식을 모두 결정한다.",
 "html": """
<h2><span class="hno">01</span>비례재보험(proportional)</h2>
<p>보험금액을 일정 비율로 나누고, 보험료와 보험금도 <b>같은 비율</b>로 나눈다.</p>
<table>
  <tr><th>종류</th><th>내용</th></tr>
  <tr><td><b>비례재보험특약</b><br>(quota share)</td><td>모든 계약을 <b>동일한 비율</b>로 출재. 단순하지만 좋은 위험도 함께 나간다</td></tr>
  <tr><td><b>초과액재보험특약</b><br>(surplus share)</td><td>보유한도(line)를 넘는 부분만 출재. 계약마다 출재 비율이 <b>달라진다</b></td></tr>
</table>

<h2><span class="hno">02</span>비비례재보험(non-proportional)</h2>
<p>손해액이 일정 금액(<b>자기부담액, retention·priority</b>)을 넘을 때 그 초과분을 재보험자가 부담한다.</p>
<table>
  <tr><th>종류</th><th>기준</th></tr>
  <tr><td><b>초과손해액재보험</b><br>(excess of loss)</td><td>1건의 위험 또는 1사고당 손해액</td></tr>
  <tr><td>├ per risk XOL</td><td><b>위험 단위</b>당 초과분</td></tr>
  <tr><td>└ per event(occurrence) XOL</td><td><b>사고 단위</b>당 초과분 — 대재해 방어</td></tr>
  <tr><td><b>초과손해율재보험</b><br>(stop loss)</td><td>일정 기간의 <b>손해율</b>이 기준을 넘을 때</td></tr>
</table>

<div class="bx c"><h5><span class="bdg">개념</span>two-risk warranty</h5>
  <div class="bx-s">둘 이상의 위험이 관련된 손해여야 담보한다는 조건이다. 일반적으로 <b>per event excess of loss reinsurance treaty</b>에 적용된다.</div>
  <div class="bx-d"><p>사고 단위 초과손해액재보험은 대재해를 겨냥한다. 그런데 단일 위험의 대형 손해까지 여기서 회수되면 per risk 특약과 중복된다. two-risk warranty는 <b>둘 이상의 위험이 관련된</b> 사고일 것을 요구하여 그 경계를 정한다.</p>
  <p>제47회 손해사정이론 36번이 이 조건이 적용되는 특약을 물었다.</p></div></div>

<h2><span class="hno">03</span>패키지보험</h2>
<p>여러 부문의 위험을 한 증권으로 묶은 보험이다. 부문별 담보위험은 다음과 같다.</p>
<ul>
  <li><b>재산종합위험담보</b>(property all risks cover)</li>
  <li><b>기계위험담보</b>(machinery breakdown cover)</li>
  <li><b>기업휴지위험담보</b>(business interruption cover)</li>
  <li><b>배상책임위험담보</b>(general liability cover)</li>
</ul>
<div class="bx t"><h5><span class="bdg">함정</span>‘사업복합형위험담보’</h5>
  <div class="bx-s">business multi-line cover는 패키지보험의 부문별 담보위험에 <b>해당하지 않는다</b>. 제47회 손해사정이론 39번의 정답이었다. 정식 부문은 <b>기업휴지</b>(business interruption)다.</div></div>
""",
 "cards": [
   ["비례·비비례가 나누는 대상은?", "비례=<b>보험금액</b>, 비비례=<b>손해액</b>"],
   ["quota share와 surplus share의 차이는?", "quota는 <b>동일 비율</b>, surplus는 보유한도 <b>초과분</b>만"],
   ["two-risk warranty가 적용되는 특약은?", "<b>per event excess of loss</b> reinsurance treaty"],
   ["패키지보험의 부문이 아닌 것은?", "<b>사업복합형위험담보</b>(business multi-line cover)"],
 ]}

RE3 = {
 "title": "재보험 특약조항",
 "desc": "계약을 굴리는 문구들", "minutes": 7, "src": "재보험 실무",
 "lead": "재보험 특약의 조항은 영문 명칭으로 출제된다. 각 조항의 명칭과 기능을 정확히 대응시키는 것이 이 절의 학습 목표이다.",
 "html": """
<h2><span class="hno">01</span>주요 조항</h2>
<table>
  <tr><th>조항</th><th>기능</th></tr>
  <tr><td><b>sunset clause</b></td><td>보험기간 종료 후 <b>통지 기간</b>을 제한. 초과손해액재보험 특약에 적용</td></tr>
  <tr><td><b>commutation clause</b></td><td>미결 손해를 <b>일시금으로 정산</b>하고 관계 종료</td></tr>
  <tr><td><b>counsel and concur clause</b></td><td>중요 소송의 대응·합의에 재보험자의 <b>동의</b> 요구</td></tr>
  <tr><td><b>reports and remittance clause</b></td><td>출재 <b>명세 보고</b>와 정산금 <b>송금</b>의 주기·방법</td></tr>
  <tr><td><b>errors and omissions clause</b></td><td>사무상 착오·누락이 있어도 담보를 유지</td></tr>
  <tr><td><b>follow the fortunes</b></td><td>원보험자의 <b>운명을 따른다</b> — 성실한 처리라면 결과를 수용</td></tr>
  <tr><td><b>cut-through clause</b></td><td>원보험계약자의 <b>직접 청구</b>를 허용</td></tr>
  <tr><td><b>insolvency clause</b></td><td>원보험자 파산 시에도 재보험자의 책임 유지</td></tr>
</table>

<div class="bx c"><h5><span class="bdg">개념</span>세 조항의 대비</h5>
  <div class="bx-s"><b>sunset</b>은 시간을 끊고, <b>commutation</b>은 금액으로 끊고, <b>counsel and concur</b>는 판단에 개입한다.</div>
  <div class="bx-d"><p>이름의 뜻으로 기억하면 편하다. sunset은 해가 지듯 담보가 끝나고, commutation은 ‘환산·교환’이므로 미결 손해를 현금으로 바꾸며, counsel and concur는 ‘변호와 동의’이므로 소송 관여다.</p></div></div>

<h2><span class="hno">02</span>손해사정과 재보험</h2>
<p>재보험이 붙은 계약에서는 손해사정 결과가 곧 재보험 회수액을 결정한다. <b>follow the fortunes</b> 원칙에 따라 재보험자는 원보험자의 성실한 사정 결과를 존중하지만, <b>counsel and concur</b> 조항이 있으면 중요 건에 대해 관여한다.</p>

<div class="bx i"><h5><span class="bdg">참고</span>이 과목이 끝나는 자리</h5>
  <div class="bx-s">손해사정이론은 리스크의 정의에서 출발해 재보험으로 끝난다. 개인의 위험이 보험단체로, 보험단체가 재보험 시장으로, 다시 자본시장으로 퍼져 나가는 <b>위험 분산의 사슬</b>이 이 과목의 줄거리다.</div></div>
""",
 "cards": [
   ["미결 손해를 일시금으로 정산하는 조항은?", "<b>commutation clause</b>"],
   ["재보험자가 소송 대응에 동의권을 갖는 조항은?", "<b>counsel and concur clause</b>"],
   ["원보험자의 처리 결과를 따르는 원칙은?", "<b>follow the fortunes</b>"],
   ["원보험자 파산 시에도 책임을 유지하는 조항은?", "<b>insolvency clause</b>"],
 ]}

SS_CH4 = {"title": "손해사정 실무", "blurb": "절차, 공제, 보험금 산정, 배상책임 담보기준",
          "sections": [L1, L2, L3, L4]}
SS_CH5 = {"title": "재보험", "blurb": "의의와 기능, 비례·비비례, 특약조항",
          "sections": [RE1, RE2, RE3]}
