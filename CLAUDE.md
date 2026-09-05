# CLAUDE.md — 손해사정사 1차 학습 서비스

손해사정사 1차 5개년 기출 **600문항**과 3과목 **전자교재 55절**을 파는 서비스.
Cloudflare Workers + D1 + KV. 외부 라이브러리 0.

## 시작하기

```bash
npm i                # playwright (검증용). 파이썬은 표준 라이브러리만 씀
npm run build        # content/ → public/ + data/ + dist/preview/
npm run verify       # Playwright 4종 (약 2~3분)
npm run serve        # public/ 을 :8788 로
```

빌드는 항상 통과해야 하고, 화면을 건드렸으면 `npm run verify` 까지 통과시킨 뒤 커밋한다.

## 구조

```
app/           HTML 템플릿 — 여기를 고친다 (public/ 은 산출물)
content/       교재 본문·용어사전 파이썬 모듈
build/         빌드 스크립트 (paths.py 가 모든 경로의 기준)
test/          Playwright 검증
tools/         PDF 문항 추출 (이력용, 평소엔 안 씀)
data/          exam.json · sample_exam.json · book.json → KV 로 올림
public/        빌드 산출물 — 직접 고치지 말 것
worker/        worker.js · schema.sql
dist/          미리보기·아티팩트 (gitignore)
```

### 절대 잊지 말 것

- **`public/*.html` 을 직접 고치지 않는다.** `app/` 템플릿을 고치고 `npm run build`.
  직접 고치면 다음 빌드에 통째로 덮인다.
- **`wrangler.toml` 은 저장소 루트에 둔다.** Cloudflare 빌드가 루트에서 돈다.
- **템플릿을 인덱스로 잘라 붙이는 패치 금지.** 구분자 문자열이 CSS 에도 나타나
  빈 슬라이스가 만들어지면 `str.replace("", …)` 가 글자마다 삽입되어 파일이 폭발한다
  (실제로 48MB 사고가 났다). 패치는 반드시 이렇게 한다.
  ```python
  assert s.count(old) == 1      # 유일성 먼저 확인
  s = s.replace(old, new)
  ```
- **PBKDF2 반복은 100,000 을 넘기지 않는다.** Workers 실환경 상한이라 넘기면
  가입·로그인이 통째로 실패한다.
- **가격을 공인중개사(5,500원)와 같게 만들지 않는다.** 같은 안드로이드 공기계로
  두 서비스의 입금 알림을 받는데, **금액이 서비스 구분자**다. 지금은 9,900원.
- **한글은 UTF-8 그대로** 쓴다. `\uXXXX` 이스케이프 금지.
- **인라인 `onclick` 금지.** 이벤트 위임으로 처리한다.
- localStorage 에 민감 정보를 넣지 않는다. 토큰과 풀이 기록만.

## 콘텐츠가 새어 나가지 않게 하는 구조

이 서비스의 핵심 제약이다. 건드릴 때 반드시 이해하고 손댈 것.

```
              미결제                        이용권 ON
public/index.html   내장 120문항(2026)      /api/content → 600문항
public/book.html    본문 없음(BOOK=null)     /api/content → 55절
```

- `build/build_app.py` 가 배포본에는 **무료 회차만** 박고, 전체는 `dist/preview/` 에만 박는다
- `build/build_book.py` 가 배포본 `book.html` 은 `__BOOK__` 을 `null` 로 채운다
- `/api/content` 는 `activePaid(u)` 를 확인하고 미결제면 **402**
- 무료 회차와 가격은 `build/paths.py` 의 `FREE_YEAR` · `PRICE` 한 곳에서 바꾼다

## 결제 — 무통장입금

PG 없음. 수수료 0원.

```
가입 → /api/pay/request 가 4자리 코드 발급
   → 고객이 "이름+코드" 로 9,900원 입금
   → 공기계 토스 알림을 MacroDroid 가 /api/hook/deposit 으로 전송
   → 코드 + 금액이 모두 맞으면 자동 승인 (1년, 기존 기간에 연장)
   → 안 잡히면 /admin.html 에서 수동 승인
```

- 금액 문자열의 콤마를 **지우지 않고** 4자리를 찾는다 → `9,900` 이 코드로 오인되지 않음
- `deposits` 테이블에 `matched / unmatched / amount_mismatch / duplicate` 로 전부 기록
- 설정 절차는 `입금자동승인_안드로이드.md`

## API

| 경로 | 인증 | 하는 일 |
|---|---|---|
| `/api/signup` `/api/login` `/api/me` | — | 가입·로그인·이용권 상태 |
| `/api/sample` | 없음 | 무료 회차 |
| `/api/content` | **이용권** | 전체 기출·교재 (미결제 402) |
| `/api/pay/request` | 로그인 | 코드 발급·계좌 안내·입금완료 알림·현금영수증 |
| `/api/hook/deposit` | `HOOK_SECRET` | 입금 알림 → 자동 승인 |
| `/api/admin/*` | `ADMIN_PASSWORD` | 목록·승인·해제·입금 로그 |
| `/api/save` `/api/load` | 로그인 | 풀이 기록 |

풀이 기록은 KV 에 통째로 넣는다. 그래서 **스키마를 바꿔도 워커를 고칠 필요가 없다.**

```js
S.seen[id] = { ok, no, last:'ok'|'no', at, noAt, pick }  // pick = 내가 고른 오답 보기
S.note[id] = '내 메모'
S.star[id] = true
```

## 디자인

s2s-lecture 토큰을 그대로 쓴다. 세 화면(`index` · `book` · `admin`)이 **같은 토큰 블록**을
복사해 쓰고 밤낮 모드 키도 `sonsa:theme` 로 공유한다. 한 곳을 바꾸면 세 곳을 같이 바꾼다.

- 배경 `#0A0A0C` · 카드 `#141417` · 경계 `#232328` · 은빛 5단계
- 사파이어(`--grad`)는 **주 버튼 한 곳에만**. 여기저기 쓰면 무너진다
- 제목은 `--crystal` 그라디언트 텍스트, 카드에 `--glass` `::before`
- 애플식 효과: 스크롤 헤어라인, IntersectionObserver 리빌, 스프링 이징(`--ease`),
  모바일 바텀시트 — **전부 `prefers-reduced-motion` 에서 정지**

## 알려진 함정

- **오답 모드에서 정답을 맞히면 화면이 튀던 버그**가 있었다. 채점 즉시 목록에서 빠지는데
  `S.pos` 는 그대로여서 다른 문항이 그려졌다. `S.pin` 으로 붙잡아 두는 방식으로 고쳤으니
  `list()` 나 `nextBtn` 을 손댈 때 이 동작을 깨뜨리지 말 것.
- `book.html` 은 `__BOOK__` 이 `null` 일 때 `/api/content` 로 받아 온다.
  `BOOK`/`TERMS`/`SEARCH`/`TLC` 를 재할당하지 말고 `Object.assign` / `push` 로 채워야 한다.
- 아티팩트로 발행할 때는 `build/build_artifact.py` 를 쓴다. Pretendard CDN 은 CSP 에 막힌다.

## 남은 일

- **문항별 해설** — `explanation` / `wrongWhy` 가 비어 있다(2026 보험업법 10문항만 시범).
  앱은 비면 "해설은 준비 중입니다"로 표시한다. 교재 55절을 근거로 인용하며 채우면 된다.
- **시행령 조문 대조** — law.go.kr 에서 시행령 본문을 못 가져왔다. 법제처 Open API 키 필요.
- **계좌 정보** — `worker/worker.js` 의 `BANK` 는 공인중개사 설정을 가져온 것. 확인 필요.
- **환불 규정** — 결제 화면 문구가 임시다.

## 배포

`main` 에 푸시하면 Cloudflare 대시보드의 **Workers Builds** 가 클론해서 `npx wrangler deploy`.
GitHub Actions 워크플로는 이중 배포를 막으려고 지웠다(되살리는 법은 README).
첫 배포 절차와 실패 원인표는 `README.md`.

---

## 작업 태도

- 가정을 말하고 시작한다. 해석이 갈리면 고르지 말고 묻는다.
- 요청한 것만 만든다. 안 시킨 기능·추상화·설정 가능성을 넣지 않는다.
- 고칠 것만 고친다. 옆의 멀쩡한 코드를 "개선"하지 않는다. 기존 스타일을 따른다.
- 내가 만든 고아 코드(안 쓰게 된 import·변수)는 치우고, 원래 있던 죽은 코드는 알리기만 한다.
- 200줄을 썼는데 50줄로 되겠으면 다시 쓴다.
- 끝냈다고 하기 전에 `npm run build` 와 (화면을 건드렸으면) `npm run verify` 를 통과시킨다.
