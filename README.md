# 손해사정사 1차 — 기출 600문항 + 전자교재

5개년(제45~49회) 1차 기출 **600문항**과 3과목 **전자교재 55절**.
화면은 s2s 디자인 토큰(메탈블랙 · 은빛크리스탈 · 블루사파이어)을 그대로 따랐고,
외부 라이브러리는 쓰지 않습니다.

```
wrangler.toml            루트에 둔다 (Cloudflare 빌드가 루트에서 실행됨)
worker/worker.js         /api/* 만 처리. 정적 파일은 ASSETS 가 서빙
worker/schema.sql        D1 스키마 (users, sessions)
public/index.html        기출 풀이 앱 + 오답 노트 (무료 회차만 내장)
public/book.html         전자교재 (본문 없음 — 이용권 계정만 서버에서 받음)
public/admin.html        관리자 — 결제 승인·가입자·자동 입금 감지·CSV
data/exam.json           문항 600개 — KV `content:exam`
data/sample_exam.json    무료 회차 120문항 — KV `content:sample_exam`
data/book.json           교재 본문·용어사전 — KV `content:book`
입금자동승인_안드로이드.md   공기계 + MacroDroid 설정
```

## 이용권 · 결제

**무통장입금**으로 받습니다. PG 수수료가 없습니다.

| | |
|---|---|
| 가격 | **9,900원 · 1년** |
| 무료 | **2026년 제49회 120문항** (회원가입만 하면 전부 풀 수 있음) |
| 유료 | 5개년 **600문항** + 전자교재 **55절** |
| 승인 | 입금자명 뒤 **4자리 코드** + **금액 일치** → 자동. 안 잡히면 `/admin.html` 수동 |
| 연장 | 이용권이 살아 있을 때 재입금하면 **남은 기간에 1년 추가** |

> ⚠️ 금액을 공인중개사(5,500원)와 **반드시 다르게** 두었습니다.
> 한 대의 공기계로 두 서비스의 입금 알림을 받을 때 금액이 구분자 역할을 합니다.
> 자세한 설정은 `입금자동승인_안드로이드.md` 참조.

### 콘텐츠가 새어 나가지 않게 하는 구조

배포본 `index.html` 에는 **무료 회차 120문항만** 들어 있고, `book.html` 에는 **본문이 없습니다**.
나머지는 `/api/content` 가 `activePaid` 를 확인한 뒤에만 내려줍니다(아니면 **402**).
소스를 열어도 유료분은 나오지 않습니다.

```
              미결제                     이용권 ON
index.html    내장 120문항               /api/content → 600문항
book.html     "이용권이 필요합니다"        /api/content → 55절
```

### API

| 경로 | 인증 | 하는 일 |
|---|---|---|
| `/api/signup` `/api/login` `/api/me` | — | 가입·로그인·이용권 상태 |
| `/api/sample` | 없음 | 무료 회차 |
| `/api/content` | **이용권** | 전체 기출·교재 (미결제 402) |
| `/api/pay/request` | 로그인 | 코드 발급·계좌 안내·입금 완료 알림·현금영수증 |
| `/api/hook/deposit` | `HOOK_SECRET` | 입금 알림 수신 → 코드·금액 매칭 시 자동 승인 |
| `/api/admin/*` | `ADMIN_PASSWORD` | 목록·승인·해제·입금 로그 |

### 관리 페이지 `/admin.html`

앱과 **같은 디자인 토큰·같은 Pretendard·같은 밤낮 모드**를 씁니다(`sonsa:theme` 공유).

- **KPI 6칸** — 승인 대기 · 이용권 활성 · 가입자 · 결제 전환율 · 누적 매출 · 자동 승인
- **결제** — 코드·금액·상태·이용 만료·현금영수증 번호·요청/승인 시각, 행마다 승인·해제
- **가입자** — 결제까지 안 온 계정도 모두. 이용권 활성 여부와 가입 시각
- **자동 입금 감지** — 자동승인 / 미매칭 / 금액불일치 / 중복 + **알림 원문**
- 이메일·코드 검색, **CSV 내려받기**(현금영수증 일괄 발급용), `/` 검색 포커스 · `r` 새로고침
- 세션 12시간, `noindex,nofollow`
| `/api/save` `/api/load` | 로그인 | 풀이 기록 |

> ⚠️ **처음 배포한다면 아래 「배포 순서」 1단계를 먼저 하세요.**
> `wrangler.toml` 의 `database_id` 와 KV `id` 가 비어 있으면 배포가 실패합니다.

## 화면 기능

| | |
|---|---|
| 드롭박스 | 연도(2022~2026) · 과목(보험업법·보험계약법·손해사정이론) · 모드(전체/오답 다시풀기/안 푼 문항) |
| 이전·다음 | 하단 고정 바. 진도 막대가 위에 붙는다 |
| 저장 | 수동 저장 + 30초 자동 저장 + 창 닫을 때 저장 |
| 채점 흐름 | **확인**을 누르기 전까지 보기를 몇 번이든 바꿀 수 있다. 확인 → 정오답·해설 표시, 다음 → 이동 |
| 이력 표시 | 문항마다 `이력 정답 n · 오답 n` 태그 |
| **오답 노트** | 전용 화면(탭 또는 `n`). 아래 표 참조 |
| 전자교재 | 헤더의 `전자교재 →`. 문항 지문의 용어를 누르면 그 낱말을 검색한 채로 열린다 |
| 로그인 | 이메일·비밀번호. 기록이 계정에 저장돼 다른 기기에서 이어진다 |
| 로컬 모드 | 로그인 없이 이 기기에만 저장 (localStorage, 실패해도 죽지 않게 try/catch) |
| 키보드 | `1~4` 보기 선택 · `Enter` 확인/다음 · `←` `→` 이동 · `n` 오답 노트 |

## 오답 노트

한 화면에 세 구역이 들어 있습니다.

| 구역 | 내용 |
|---|---|
| **오늘 복습** | 복습 대상 / 오답 전체 / 별표 / 메모 카드. 경과일 구간 칩(오늘 · 하루 · 3일 · 1주 · 2주 넘게 방치). 「오늘 복습 시작」이 그 문항들만 모아 준다 |
| **취약점** | 과목별·연도별 오답률 막대(50% 넘으면 붉게) · 반복해서 틀리는 문항 상위 5개 |
| **오답 목록** | `과목 · 연도`로 묶고 칩으로 필터(전체 / 복습 대상 / 2회 이상 / 별표 / 메모). 행마다 `✕ 내 답 · 정답 · N회 틀림 · N일 전 · ★ · 메모`. 누르면 그 문항으로 점프 |

- **복습 스케줄** — 틀린 다음 날부터 대상. 정렬은 *틀린 횟수 우선, 그다음 오래 묵힌 순*
- **졸업 조건** — 한 번 맞히면 그 자리에서 제거
- **저장 형식** — `snapshot v2`

```js
S.seen[id] = { ok, no, last:'ok'|'no', at, noAt, pick }  // pick = 내가 고른 오답 보기
S.note[id] = '내 메모'
S.star[id] = true
```

워커는 state 를 통째로 KV 에 넣으므로 워커 수정 없이 기기간 동기화됩니다.

## 배포 순서

```bash
# 1) D1 · KV 생성 후 wrangler.toml 의 database_id / id 를 채운다
npx wrangler d1 create sonhaesajeongsa-db
npx wrangler kv namespace create CONTENT

# 2) 스키마 적용
npx wrangler d1 execute sonhaesajeongsa-db --remote --file=worker/schema.sql

# 3) 문항과 교재를 KV 에 올린다
npx wrangler kv key put --binding=KV "content:exam" --path=data/exam.json --remote
npx wrangler kv key put --binding=KV "content:sample_exam" --path=data/sample_exam.json --remote
npx wrangler kv key put --binding=KV "content:book" --path=data/book.json --remote

# 4) 비밀값 두 개 (결제 자동승인 · 관리자)
npx wrangler secret put HOOK_SECRET
npx wrangler secret put ADMIN_PASSWORD

# 5) 배포
npx wrangler deploy
```

GitHub Actions 로 자동 배포하려면 저장소 Secrets 에
`CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID` 를 넣어 두면 됩니다
(대시보드 Workers Builds 연결은 쓰지 않습니다).

## 문항 데이터 형식

```jsonc
{
  "2022": {                       // 연도
    "1차 1교시": {                 // 교시
      "보험업법": [                // 과목
        {
          "subject": "보험업법",
          "no": 1,
          "importance": "mid",
          "q": "문제 지문",
          "choices": ["보기1","보기2","보기3","보기4"],
          "answer": 0,             // 0-based
          "altAnswers": [3],       // 복수정답일 때만
          "explanation": "",       // 해설 (아직 비어 있음)
          "wrongWhy": {},          // 오답 사유 { "2": "...", "3": "..." }
          "terms": [],
          "source": "ocr-verified" // 제47회 두 과목만. OCR 복원 후 육안 검수한 문항
        }
      ]
    }
  }
}
```

- 정답표는 회차별 **확정답안** PDF에서 추출해 문항과 1:1 대조했습니다.
- 복수정답 3문항: 2022 보험업법 19번, 2022 손해사정이론 29번, 2026 손해사정이론 32번.
- `explanation` / `wrongWhy` 는 비어 있고, 앱은 비었을 때 "해설은 준비 중입니다"로 표시합니다.
  채워 넣으면 자동으로 그 자리에 나옵니다.

## 원자료 출처

미래보험교육원 기출문제 자료실 (보험개발원 공식본은 제47회 첨부가 없음).
제47회 보험업법·손해사정이론 PDF는 숫자·보기번호가 이미지로 박혀 있어
구조는 좌표로, 내용은 crop OCR + 텍스트층 대조로 복원한 뒤
숫자·괄호가 들어간 52문항을 원본 이미지로 육안 검수했습니다.
