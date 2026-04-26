-- Migration: 0023_avatar_soul_engine
-- AvatarSoul Engine substrate
-- Identity, memory, instincts, debate, presence, artifact trails

BEGIN;

-- ============================================
-- AVATAR SOULS
-- Core identity kernel for each avatar
-- ============================================

CREATE TABLE IF NOT EXISTS avatar_souls (
    soul_id TEXT PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    avatar_id TEXT NOT NULL REFERENCES avatars(avatar_id) ON DELETE CASCADE,
    identity_kernel JSONB NOT NULL DEFAULT '{}'::jsonb,
    worldview JSONB NOT NULL DEFAULT '[]'::jsonb,
    obsessions JSONB NOT NULL DEFAULT '[]'::jsonb,
    reflexes JSONB NOT NULL DEFAULT '[]'::jsonb,
    taboos JSONB NOT NULL DEFAULT '[]'::jsonb,
    debate_style JSONB NOT NULL DEFAULT '{}'::jsonb,
    embodiment_level TEXT NOT NULL DEFAULT 'deep',
    operating_principles JSONB NOT NULL DEFAULT '[]'::jsonb,
    evaluation_bias JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(org_id, avatar_id)
);

CREATE INDEX idx_avatar_souls_org_id ON avatar_souls(org_id);
CREATE INDEX idx_avatar_souls_avatar_id ON avatar_souls(avatar_id);

-- ============================================
-- AVATAR MEMORY EDGES
-- Salient relationships between avatars and ripples
-- ============================================

CREATE TABLE IF NOT EXISTS avatar_memory_edges (
    memory_edge_id TEXT PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    avatar_id TEXT NOT NULL REFERENCES avatars(avatar_id) ON DELETE CASCADE,
    ripple_id TEXT NOT NULL REFERENCES ripples(ripple_id) ON DELETE CASCADE,
    relationship_type TEXT NOT NULL,
    salience NUMERIC NOT NULL DEFAULT 0.5 CHECK (salience >= 0.0 AND salience <= 1.0),
    decay_policy TEXT NOT NULL DEFAULT 'normal',
    use_when TEXT NOT NULL DEFAULT '',
    last_used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(org_id, avatar_id, ripple_id, relationship_type)
);

CREATE INDEX idx_avatar_memory_edges_org_id ON avatar_memory_edges(org_id);
CREATE INDEX idx_avatar_memory_edges_avatar_id ON avatar_memory_edges(avatar_id);
CREATE INDEX idx_avatar_memory_edges_avatar_salience ON avatar_memory_edges(avatar_id, salience DESC);
CREATE INDEX idx_avatar_memory_edges_ripple_id ON avatar_memory_edges(ripple_id);

-- ============================================
-- AVATAR INSTINCT FRAMES
-- Deterministic trigger-response snapshots
-- ============================================

CREATE TABLE IF NOT EXISTS avatar_instinct_frames (
    instinct_frame_id TEXT PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    avatar_id TEXT NOT NULL REFERENCES avatars(avatar_id) ON DELETE CASCADE,
    harness_run_id TEXT REFERENCES harness_runs(run_id) ON DELETE CASCADE,
    capability_run_id TEXT REFERENCES capability_runs(capability_run_id) ON DELETE SET NULL,
    trigger_kind TEXT NOT NULL,
    dominant_concern TEXT NOT NULL DEFAULT '',
    risk_flags JSONB NOT NULL DEFAULT '[]'::jsonb,
    recommended_posture TEXT NOT NULL DEFAULT '',
    visible_summary TEXT NOT NULL DEFAULT '',
    private_notes JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_avatar_instinct_frames_org_id ON avatar_instinct_frames(org_id);
CREATE INDEX idx_avatar_instinct_frames_avatar_id ON avatar_instinct_frames(avatar_id);
CREATE INDEX idx_avatar_instinct_frames_harness_run_id ON avatar_instinct_frames(harness_run_id);

-- ============================================
-- AVATAR PRESENCE STATES
-- Visible avatar state during harness runs
-- ============================================

CREATE TABLE IF NOT EXISTS avatar_presence_states (
    presence_id TEXT PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    avatar_id TEXT NOT NULL REFERENCES avatars(avatar_id) ON DELETE CASCADE,
    harness_run_id TEXT REFERENCES harness_runs(run_id) ON DELETE CASCADE,
    state TEXT NOT NULL,
    current_focus TEXT NOT NULL DEFAULT '',
    current_concern TEXT NOT NULL DEFAULT '',
    confidence NUMERIC NOT NULL DEFAULT 0.5 CHECK (confidence >= 0.0 AND confidence <= 1.0),
    visible_summary TEXT NOT NULL DEFAULT '',
    last_event_id TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(org_id, avatar_id, harness_run_id)
);

CREATE INDEX idx_avatar_presence_states_org_id ON avatar_presence_states(org_id);
CREATE INDEX idx_avatar_presence_states_avatar_id ON avatar_presence_states(avatar_id);
CREATE INDEX idx_avatar_presence_states_harness_run_id ON avatar_presence_states(harness_run_id);

-- ============================================
-- AVATAR DEBATE EVENTS
-- Structured debate contributions
-- ============================================

CREATE TABLE IF NOT EXISTS avatar_debate_events (
    debate_event_id TEXT PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    harness_run_id TEXT NOT NULL REFERENCES harness_runs(run_id) ON DELETE CASCADE,
    speaker_avatar_id TEXT REFERENCES avatars(avatar_id) ON DELETE SET NULL,
    target_avatar_id TEXT REFERENCES avatars(avatar_id) ON DELETE SET NULL,
    event_type TEXT NOT NULL,
    stance TEXT,
    content JSONB NOT NULL DEFAULT '{}'::jsonb,
    confidence NUMERIC NOT NULL DEFAULT 0.5 CHECK (confidence >= 0.0 AND confidence <= 1.0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_avatar_debate_events_org_id ON avatar_debate_events(org_id);
CREATE INDEX idx_avatar_debate_events_harness_run_id ON avatar_debate_events(harness_run_id);
CREATE INDEX idx_avatar_debate_events_speaker ON avatar_debate_events(speaker_avatar_id);
CREATE INDEX idx_avatar_debate_events_created_at ON avatar_debate_events(harness_run_id, created_at);

-- ============================================
-- AVATAR ARTIFACT TRAILS
-- Artifact contribution history
-- ============================================

CREATE TABLE IF NOT EXISTS avatar_artifact_trails (
    trail_id TEXT PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    avatar_id TEXT NOT NULL REFERENCES avatars(avatar_id) ON DELETE CASCADE,
    artifact_id TEXT NOT NULL REFERENCES capability_artifacts(artifact_id) ON DELETE CASCADE,
    harness_run_id TEXT REFERENCES harness_runs(run_id) ON DELETE SET NULL,
    contribution_type TEXT NOT NULL,
    summary TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(org_id, avatar_id, artifact_id, contribution_type)
);

CREATE INDEX idx_avatar_artifact_trails_org_id ON avatar_artifact_trails(org_id);
CREATE INDEX idx_avatar_artifact_trails_avatar_id ON avatar_artifact_trails(avatar_id);
CREATE INDEX idx_avatar_artifact_trails_artifact_id ON avatar_artifact_trails(artifact_id);

COMMIT;
