-- Migration: 0024_multi_avatar_council_orchestration
-- Deterministic multi-avatar council orchestration pipeline
-- Code-decided orchestration: create run -> select roster -> build context -> form positions -> challenge rounds -> synthesize -> artifact

BEGIN;

-- ============================================
-- COUNCIL ORCHESTRATION RUNS
-- Top-level orchestration run that tracks the entire council pipeline
-- ============================================
CREATE TABLE IF NOT EXISTS council_orchestration_runs (
    council_run_id TEXT PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    harness_run_id TEXT REFERENCES harness_runs(run_id) ON DELETE SET NULL,
    request_summary TEXT NOT NULL,
    mode TEXT NOT NULL DEFAULT 'dry_run',
    status TEXT NOT NULL DEFAULT 'queued',
    avatar_roster JSONB NOT NULL DEFAULT '[]'::jsonb,
    context_summary TEXT NOT NULL DEFAULT '',
    synthesis JSONB NOT NULL DEFAULT '{}'::jsonb,
    final_artifact_id TEXT,
    error_message TEXT,
    created_by TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================
-- COUNCIL AVATAR TURNS
-- Individual turn for each avatar within an orchestration run
-- ============================================
CREATE TABLE IF NOT EXISTS council_avatar_turns (
    turn_id TEXT PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    council_run_id TEXT NOT NULL REFERENCES council_orchestration_runs(council_run_id) ON DELETE CASCADE,
    harness_run_id TEXT REFERENCES harness_runs(run_id) ON DELETE SET NULL,
    avatar_id TEXT NOT NULL REFERENCES avatars(avatar_id) ON DELETE CASCADE,
    avatar_key TEXT NOT NULL,
    turn_type TEXT NOT NULL,
    sequence_number INT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    input JSONB NOT NULL DEFAULT '{}'::jsonb,
    output JSONB NOT NULL DEFAULT '{}'::jsonb,
    debate_event_id TEXT,
    instinct_frame_id TEXT,
    presence_id TEXT,
    error_message TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes for efficient lookups
CREATE INDEX IF NOT EXISTS idx_council_orch_runs_org ON council_orchestration_runs(org_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_council_orch_runs_status ON council_orchestration_runs(status);
CREATE INDEX IF NOT EXISTS idx_council_avatar_turns_run ON council_avatar_turns(council_run_id, sequence_number);
CREATE INDEX IF NOT EXISTS idx_council_avatar_turns_org ON council_avatar_turns(org_id);

COMMIT;
