-- Foundation versioning for audit trail and rollback
-- Tracks all Foundation changes with previous values

CREATE TABLE IF NOT EXISTS foundation_versions (
    version_id text PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    foundation_version integer NOT NULL,
    change_description text,
    changed_fields jsonb NOT NULL DEFAULT '[]'::jsonb,
    previous_values jsonb NOT NULL DEFAULT '{}'::jsonb,
    impact_assessment jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE foundation_versions ENABLE ROW LEVEL SECURITY;

CREATE POLICY foundation_versions_tenant ON foundation_versions
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

CREATE INDEX idx_foundation_versions_org_version 
    ON foundation_versions (org_id, foundation_version DESC);

CREATE INDEX idx_foundation_versions_created_at 
    ON foundation_versions (org_id, created_at DESC);