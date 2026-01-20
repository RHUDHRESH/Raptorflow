-- Migration: 20260120_blackbox_updates.sql
-- Enhance Blackbox Strategy tracking

ALTER TABLE public.blackbox_strategies 
ADD COLUMN IF NOT EXISTS last_run_at TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS engine_version TEXT DEFAULT 'v4.0-infinity';

-- Add unique constraint for active proposed strategies per workspace if needed
-- CREATE UNIQUE INDEX idx_unique_proposed_strategy ON blackbox_strategies(workspace_id, name) WHERE status = 'proposed';
