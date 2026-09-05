-- 손해사정사 1차 기출 D1 스키마
CREATE TABLE IF NOT EXISTS users (
  email     TEXT PRIMARY KEY,
  pass_salt TEXT NOT NULL,
  pass_hash TEXT NOT NULL,
  created   INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
  token   TEXT PRIMARY KEY,
  email   TEXT NOT NULL,
  created INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sessions_email ON sessions(email);
