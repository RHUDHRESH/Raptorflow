-- Migration: 0021_avatars_harness
-- Avatar domain model + Harness execution ledger

BEGIN;

-- ─────────────────────────────────────────────────────────────────────────────
-- AVATARS
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS avatars (
    avatar_id TEXT PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    avatar_key TEXT NOT NULL,
    display_name TEXT NOT NULL,
    role TEXT NOT NULL,
    archetype TEXT NOT NULL,
    personality JSONB NOT NULL DEFAULT '{}'::jsonb,
    system_prompt TEXT NOT NULL DEFAULT '',
    tool_permissions JSONB NOT NULL DEFAULT '{}'::jsonb,
    memory_scope TEXT NOT NULL DEFAULT 'org',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(org_id, avatar_key)
);

CREATE INDEX IF NOT EXISTS idx_avatars_org_id ON avatars(org_id);
CREATE INDEX IF NOT EXISTS idx_avatars_org_id_active ON avatars(org_id, is_active) WHERE is_active = TRUE;

COMMENT ON TABLE avatars IS 'Configurable agent personas used by Council, Muse, Office, and later capabilities.';
COMMENT ON COLUMN avatars.avatar_key IS 'Unique key within org: strategist, growth_operator, copywriter, researcher, analyst, creative_director, proof_collector';
COMMENT ON COLUMN avatars.personality IS 'JSON: { tone, risk_tolerance, creativity, skepticism, detail_level }';
COMMENT ON COLUMN avatars.tool_permissions IS 'JSON: { can_use_bedrock, can_read_foundation, can_read_intel, can_write_artifacts, can_trigger_jobs, requires_approval_for_external_actions }';

-- ─────────────────────────────────────────────────────────────────────────────
-- HARNESS RUNS
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS harness_runs (
    run_id TEXT PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    run_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    input JSONB NOT NULL DEFAULT '{}'::jsonb,
    output JSONB,
    error_message TEXT,
    created_by TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT harness_runs_status_check CHECK (status IN ('queued', 'running', 'completed', 'failed', 'cancelled'))
);

CREATE INDEX IF NOT EXISTS idx_harness_runs_org_id ON harness_runs(org_id);
CREATE INDEX IF NOT EXISTS idx_harness_runs_org_id_status ON harness_runs(org_id, status);
CREATE INDEX IF NOT EXISTS idx_harness_runs_created_at ON harness_runs(created_at DESC);

COMMENT ON TABLE harness_runs IS 'Execution ledger for harness orchestration runs.';
COMMENT ON COLUMN harness_runs.status IS 'queued | running | completed | failed | cancelled';

-- ─────────────────────────────────────────────────────────────────────────────
-- HARNESS STEPS
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS harness_steps (
    step_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES harness_runs(run_id) ON DELETE CASCADE,
    org_id UUID NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    avatar_id TEXT REFERENCES avatars(avatar_id) ON DELETE SET NULL,
    step_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    input JSONB NOT NULL DEFAULT '{}'::jsonb,
    output JSONB,
    error_message TEXT,
    sequence_number INT NOT NULL DEFAULT 1,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT harness_steps_status_check CHECK (status IN ('queued', 'running', 'completed', 'failed', 'cancelled'))
);

CREATE INDEX IF NOT EXISTS idx_harness_steps_run_id ON harness_steps(run_id);
CREATE INDEX IF NOT EXISTS idx_harness_steps_org_id ON harness_steps(org_id);
CREATE INDEX IF NOT EXISTS idx_harness_steps_avatar_id ON harness_steps(avatar_id) WHERE avatar_id IS NOT NULL;

COMMENT ON TABLE harness_steps IS 'Per-step ledger within a harness run, tied to specific avatars.';

COMMIT;
