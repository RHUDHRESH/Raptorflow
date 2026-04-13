-- Migration: 0008_agent_essences_full
-- Purpose: Add missing columns to agent_essences table to match the AgentEssence Rust struct
-- Date: 2026-04-12
-- 
-- Columns present in 0005_prl.sql (unchanged):
--   agent_id, org_id, avatar_key, essence_core, ego_baseline, ego_state,
--   skill_atoms, created_at, updated_at
--
-- Columns missing (added below):
--   display_name, ego_multipliers, ego_decay_rate, persona_vector,
--   reflection_vfe, reflection_mean, reflection_std, reflection_cooldown,
--   active_session_id, last_active_at

-- Add display_name column (optional text field for human-readable avatar name)
ALTER TABLE agent_essences ADD COLUMN IF NOT EXISTS display_name text;

-- Add ego_multipliers: per-avatar sensitivity vector for Plutchik emotions
-- Default to all-ones so existing rows behave neutrally until seeded with real values
ALTER TABLE agent_essences ADD COLUMN IF NOT EXISTS ego_multipliers double precision[8] NOT NULL DEFAULT '{1,1,1,1,1,1,1,1}';

-- Add ego_decay_rate: exponential decay constant (per hour)
-- Controls how fast ego_state returns to ego_baseline between sessions
-- Default 0.1 means decay to baseline in ~10 hours (safe midpoint)
ALTER TABLE agent_essences ADD COLUMN IF NOT EXISTS ego_decay_rate double precision NOT NULL DEFAULT 0.1;

-- Add persona_vector: embedding of the essence core for semantic drift detection
-- Used by skill_alignment_gate to reject skills that diverge too far from persona
-- Using pgvector with 1536 dimensions (text-embedding-3-small)
ALTER TABLE agent_essences ADD COLUMN IF NOT EXISTS persona_vector vector(1536);

-- Add reflection_vfe: Variational Free Energy score from last reflection cycle
-- Part of Tier 1/2 reflection gating logic in EelTopology
ALTER TABLE agent_essences ADD COLUMN IF NOT EXISTS reflection_vfe double precision NOT NULL DEFAULT 0.0;

-- Add reflection_mean: rolling mean of reflection quality scores
-- Used to decide whether new skill gets origin='reflection_tier1' or gets rejected
ALTER TABLE agent_essences ADD COLUMN IF NOT EXISTS reflection_mean double precision NOT NULL DEFAULT 0.0;

-- Add reflection_std: rolling standard deviation of reflection quality
-- Together with reflection_mean, forms the Bayesian update boundary
ALTER TABLE agent_essences ADD COLUMN IF NOT EXISTS reflection_std double precision NOT NULL DEFAULT 0.0;

-- Add reflection_cooldown: minutes remaining before avatar can reflect again
-- Prevents reflection storms after War Room sessions
ALTER TABLE agent_essences ADD COLUMN IF NOT EXISTS reflection_cooldown integer NOT NULL DEFAULT 0;

-- Add active_session_id: tracks which session currently has this avatar locked
-- Prevents double-loading same avatar in two simultaneous sessions for same org
-- Using plain nullable uuid - NO FK constraint yet since sessions table doesn't exist
-- Will add FK constraint in a later migration when sessions table is defined
ALTER TABLE agent_essences ADD COLUMN IF NOT EXISTS active_session_id uuid DEFAULT NULL;

-- Add last_active_at: timestamp of last session this avatar participated in
-- Used by EgoDecay::compute_decay to compute hours_idle for inter-session decay
-- NULL means "never active" - decay code must treat NULL as decay fully to baseline
ALTER TABLE agent_essences ADD COLUMN IF NOT EXISTS last_active_at timestamptz DEFAULT NULL;

-- Index on active_session_id for quick lookup when checking avatar lock status
CREATE INDEX IF NOT EXISTS agent_essences_active_session_idx ON agent_essences (active_session_id) WHERE active_session_id IS NOT NULL;

-- Index on last_active_at for efficient decay calculation queries
CREATE INDEX IF NOT EXISTS agent_essences_last_active_idx ON agent_essences (org_id, last_active_at DESC) WHERE last_active_at IS NOT NULL;

-- Index on avatar_key for fast avatar lookup within an org
CREATE INDEX IF NOT EXISTS agent_essences_org_avatar_idx ON agent_essences (org_id, avatar_key);
