-- Migration: 20260120_bcm_evolution_index.sql
-- Add Evolution tracking to Workspaces

ALTER TABLE public.workspaces
ADD COLUMN IF NOT EXISTS current_bcm_ucid TEXT,
ADD COLUMN IF NOT EXISTS evolution_index FLOAT DEFAULT 1.0;

-- Comments
COMMENT ON COLUMN public.workspaces.current_bcm_ucid IS 'The current active RaptorFlow UCID for strategic context.';
COMMENT ON COLUMN public.workspaces.evolution_index IS 'A maturity score (1.0 - 10.0) derived from BCM Ledger interactions.';
