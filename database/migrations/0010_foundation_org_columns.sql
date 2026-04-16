-- Add foundation completion columns to organizations
-- These are needed for POST /foundation/complete to track completion state

ALTER TABLE organizations
ADD COLUMN foundation_complete boolean NOT NULL DEFAULT false,
ADD COLUMN foundation_json jsonb,
ADD COLUMN foundation_completed_at timestamptz;

CREATE INDEX idx_organizations_foundation_complete ON organizations (foundation_complete);
