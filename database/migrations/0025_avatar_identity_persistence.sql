-- Migration: 0025_avatar_identity_persistence
-- Identity persistence layer: mood state, personality drift, experience log

BEGIN;

-- ─────────────────────────────────────────────────────────────
-- AVATAR IDENTITY STATES
-- Tracks mutable avatar state that evolves over time
-- ─────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS avatar_identity_states (
    identity_state_id TEXT PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    avatar_id TEXT NOT NULL REFERENCES avatars(avatar_id) ON DELETE CASCADE,
    mood_confidence NUMERIC NOT NULL DEFAULT 0.5 CHECK (mood_confidence >= 0.0 AND mood_confidence <= 1.0),
    mood_skepticism NUMERIC NOT NULL DEFAULT 0.5 CHECK (mood_skepticism >= 0.0 AND mood_skepticism <= 1.0),
    mood_creativity NUMERIC NOT NULL DEFAULT 0.5 CHECK (mood_creativity >= 0.0 AND mood_creativity <= 1.0),
    mood_urgency NUMERIC NOT NULL DEFAULT 0.5 CHECK (mood_urgency >= 0.0 AND mood_urgency <= 1.0),
    ego_drift_accumulator JSONB NOT NULL DEFAULT '[]'::jsonb,
    total_debates_participated INT NOT NULL DEFAULT 0,
    total_challenges_issued INT NOT NULL DEFAULT 0,
    total_challenges_received INT NOT NULL DEFAULT 0,
    total_challenges_won INT NOT NULL DEFAULT 0,
    total_syntheses_influenced INT NOT NULL DEFAULT 0,
    personality_summary TEXT NOT NULL DEFAULT '',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(org_id, avatar_id)
);

CREATE INDEX IF NOT EXISTS idx_avatar_identity_states_org_id ON avatar_identity_states(org_id);
CREATE INDEX IF NOT EXISTS idx_avatar_identity_states_avatar_id ON avatar_identity_states(avatar_id);
CREATE INDEX IF NOT EXISTS idx_avatar_identity_states_mood ON avatar_identity_states(org_id, avatar_id);

COMMENT ON TABLE avatar_identity_states IS 'Mutable identity state: mood, experience log, ego drift. Updated after each debate round.';
COMMENT ON COLUMN avatar_identity_states.mood_confidence IS '0.0=insecure 1.0=overconfident';
COMMENT ON COLUMN avatar_identity_states.mood_skepticism IS '0.0=trusting 1.0=paranoid';
COMMENT ON COLUMN avatar_identity_states.mood_creativity IS '0.0=literal 1.0=visionary';
COMMENT ON COLUMN avatar_identity_states.mood_urgency IS '0.0=patient 1.0=panicked';
COMMENT ON COLUMN avatar_identity_states.ego_drift_accumulator IS 'Array of recent ego drift deltas for trend analysis';

-- ─────────────────────────────────────────────────────────────
-- AVATAR EXPERIENCE LOG
-- Tracks individual debate events for personality formation
-- ─────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS avatar_experience_log (
    experience_id TEXT PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    avatar_id TEXT NOT NULL REFERENCES avatars(avatar_id) ON DELETE CASCADE,
    experience_type TEXT NOT NULL,
    summary TEXT NOT NULL DEFAULT '',
    outcome TEXT NOT NULL DEFAULT '',
    salience NUMERIC NOT NULL DEFAULT 0.5 CHECK (salience >= 0.0 AND salience <= 1.0),
    related_avatar_key TEXT,
    related_hook_type TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_avatar_experience_log_org_id ON avatar_experience_log(org_id);
CREATE INDEX IF NOT EXISTS idx_avatar_experience_log_avatar_id ON avatar_experience_log(avatar_id);
CREATE INDEX IF NOT EXISTS idx_avatar_experience_log_recent ON avatar_experience_log(org_id, avatar_id, created_at DESC);

COMMENT ON TABLE avatar_experience_log IS 'Per-avatar experience history for personality formation and dynamic prompt construction';

COMMIT;
