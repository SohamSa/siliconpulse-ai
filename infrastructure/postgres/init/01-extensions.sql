-- SiliconPulse AI — PostgreSQL bootstrap (runs once on empty volume)
-- Application schema is managed by Alembic in Phase 5+.

CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Lightweight readiness marker for ops checks
CREATE TABLE IF NOT EXISTS schema_bootstrap (
    id SMALLINT PRIMARY KEY DEFAULT 1 CHECK (id = 1),
    product TEXT NOT NULL DEFAULT 'SiliconPulse AI',
    phase TEXT NOT NULL DEFAULT 'phase-2-infra',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO schema_bootstrap (id) VALUES (1)
ON CONFLICT (id) DO NOTHING;
