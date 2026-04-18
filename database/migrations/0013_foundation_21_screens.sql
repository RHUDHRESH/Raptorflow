-- Add indexes for common foundation section lookups
-- This enables efficient querying of the 21-screen onboarding data

CREATE INDEX IF NOT EXISTS idx_foundation_snapshots_org_version 
ON foundation_snapshots (org_id, foundation_version DESC);

CREATE INDEX IF NOT EXISTS idx_foundation_snapshots_sections_gin 
ON foundation_snapshots USING GIN (sections jsonb_path_ops);

-- Add composite index for common section queries
CREATE INDEX IF NOT EXISTS idx_foundation_sections_org_key 
ON foundation_sections (org_id, section_key);