-- Foundation sections table for per-section storage
-- Used by PATCH /foundation/section/:section_id and GET /foundation/snapshot
-- This allows efficient per-section updates without versioning overhead

CREATE TABLE IF NOT EXISTS foundation_sections (
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    section_key text NOT NULL,
    value jsonb NOT NULL DEFAULT '{}'::jsonb,
    updated_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (org_id, section_key)
);

ALTER TABLE foundation_sections ENABLE ROW LEVEL SECURITY;

CREATE POLICY foundation_sections_tenant ON foundation_sections
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

CREATE INDEX idx_foundation_sections_updated_at ON foundation_sections (org_id, updated_at DESC);
