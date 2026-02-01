from sqlalchemy import text
from app.db.session import engine

SCHEMA_SQL = """
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS tenants (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL REFERENCES tenants(id),
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('admin','analyst','viewer')),
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS machines (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL REFERENCES tenants(id),
  machine_code TEXT NOT NULL,
  machine_name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (tenant_id, machine_code)
);

CREATE TABLE IF NOT EXISTS production_events (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL REFERENCES tenants(id),
  machine_id UUID NOT NULL REFERENCES machines(id),
  event_ts TIMESTAMPTZ NOT NULL,
  good_qty INT NOT NULL DEFAULT 0,
  scrap_qty INT NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS downtime_events (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL REFERENCES tenants(id),
  machine_id UUID NOT NULL REFERENCES machines(id),
  start_ts TIMESTAMPTZ NOT NULL,
  end_ts TIMESTAMPTZ NOT NULL,
  reason TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS data_quality_issues (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL REFERENCES tenants(id),
  system_name TEXT NOT NULL CHECK (system_name IN ('ERP','MES','WMS','Other')),
  severity TEXT NOT NULL CHECK (severity IN ('low','medium','high','critical')),
  issue_type TEXT NOT NULL,
  field_name TEXT,
  record_id TEXT,
  detected_ts TIMESTAMPTZ NOT NULL DEFAULT now(),
  status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open','resolved'))
);

CREATE INDEX IF NOT EXISTS idx_prod_tenant_ts ON production_events(tenant_id, event_ts);
CREATE INDEX IF NOT EXISTS idx_down_tenant_ts ON downtime_events(tenant_id, start_ts);
CREATE INDEX IF NOT EXISTS idx_dq_tenant_ts ON data_quality_issues(tenant_id, detected_ts);
"""

def init_db():
    with engine.begin() as conn:
        conn.execute(text(SCHEMA_SQL))
