-- Migration: Experiment Modernization
-- Adds hypothesis-driven fields to the experiments table

ALTER TABLE experiments
ADD COLUMN IF NOT EXISTS hypothesis TEXT,
ADD COLUMN IF NOT EXISTS control TEXT,
ADD COLUMN IF NOT EXISTS variant TEXT,
ADD COLUMN IF NOT EXISTS success_metric TEXT,
ADD COLUMN IF NOT EXISTS sample_size TEXT,
ADD COLUMN IF NOT EXISTS duration_days INTEGER DEFAULT 7,
ADD COLUMN IF NOT EXISTS action_steps TEXT[] DEFAULT '{}'::text[];

-- Update comment for clarity
COMMENT ON TABLE experiments IS 'Hypothesis-driven experiments for the Blackbox Industrial engine.';
