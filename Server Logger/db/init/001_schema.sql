-- Schema for commlogs
CREATE TABLE IF NOT EXISTS logs (
  id BIGSERIAL PRIMARY KEY,
  ts TIMESTAMPTZ NOT NULL,
  source_host TEXT,
  src_ip INET, dst_ip INET,
  src_port INT, dst_port INT,
  protocol TEXT,
  direction TEXT,
  status TEXT,
  latency_ms INT,
  bytes_in INT, bytes_out INT,
  service TEXT,
  raw TEXT,
  tags JSONB
);

CREATE INDEX IF NOT EXISTS idx_logs_ts ON logs (ts);
CREATE INDEX IF NOT EXISTS idx_logs_service ON logs (service);
CREATE INDEX IF NOT EXISTS idx_logs_protocol ON logs (protocol);
CREATE INDEX IF NOT EXISTS idx_logs_status ON logs (status);
CREATE INDEX IF NOT EXISTS idx_logs_src_ip ON logs (src_ip);
CREATE INDEX IF NOT EXISTS idx_logs_dst_port ON logs (dst_port);
