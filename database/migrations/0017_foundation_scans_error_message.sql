-- Add error_message column to foundation_scans for proper error persistence
-- Fixes false positive: scan jobs were stuck in 'running' forever with no error trace

ALTER TABLE foundation_scans
ADD COLUMN IF NOT EXISTS error_message text;

CREATE INDEX IF NOT EXISTS idx_foundation_scans_error ON foundation_scans (org_id, error_message)
WHERE error_message IS NOT NULL;
