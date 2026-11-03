CREATE TABLE IF NOT EXISTS requests (
  id TEXT PRIMARY KEY,
  contact TEXT NOT NULL UNIQUE,
  kind TEXT NOT NULL CHECK (kind IN ('email', 'npub')),
  ip_hash TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS requests_ip_created ON requests (ip_hash, created_at);
CREATE INDEX IF NOT EXISTS requests_created ON requests (created_at);
