-- 손해사정사 1차 학습 서비스 D1 스키마

CREATE TABLE IF NOT EXISTS users (
  email      TEXT PRIMARY KEY,
  pass_salt  TEXT NOT NULL,
  pass_hash  TEXT NOT NULL,
  phone      TEXT,                        -- 휴대폰(현금영수증 발급용, 선택)
  paid       INTEGER NOT NULL DEFAULT 0,  -- 0=미결제, 1=승인
  paid_until INTEGER,                     -- 이용 만료(unix초). now < paid_until 이면 이용 가능
  created    INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
  token   TEXT PRIMARY KEY,
  email   TEXT NOT NULL,
  created INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sessions_email ON sessions(email);

-- 무통장입금 결제 요청
CREATE TABLE IF NOT EXISTS payments (
  email         TEXT PRIMARY KEY,
  code          TEXT NOT NULL,            -- 입금자명 뒤에 붙일 4자리 식별코드
  amount        INTEGER NOT NULL,
  status        TEXT NOT NULL DEFAULT 'pending',  -- pending | paid | rejected
  receipt_phone TEXT,                     -- 현금영수증 요청 번호(선택)
  requested     INTEGER,
  approved      INTEGER
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_payments_code ON payments(code);

CREATE TABLE IF NOT EXISTS admin_sessions (
  token   TEXT PRIMARY KEY,
  created INTEGER NOT NULL
);

-- 입금 알림 수신 로그 (안드로이드 공기계 → 웹훅)
CREATE TABLE IF NOT EXISTS deposits (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  raw           TEXT,       -- 원본 알림 텍스트(300자까지)
  amount        INTEGER,    -- 파싱된 금액
  code          TEXT,       -- 추출된 입금자명 코드(4자리)
  matched_email TEXT,       -- 자동 매칭된 유저(없으면 NULL)
  status        TEXT,       -- matched | unmatched | amount_mismatch | duplicate
  created       INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_deposits_created ON deposits(created);
