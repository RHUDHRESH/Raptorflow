-- Foundation scans table for tracking URL scan jobs
-- Used by POST /foundation/scan/start and GET /foundation/scan/status

CREATE TABLE IF NOT EXISTS foundation_scans (
    scan_id text PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    url text NOT NULL,
    status text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'complete', 'failed')),
    quick_scan_data jsonb,
    deep_scan_data jsonb,
    started_at timestamptz NOT NULL DEFAULT now(),
    completed_at timestamptz
);

ALTER TABLE foundation_scans ENABLE ROW LEVEL SECURITY;

CREATE POLICY foundation_scans_tenant ON foundation_scans
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

CREATE INDEX idx_foundation_scans_org_status ON foundation_scans (org_id, status);
CREATE INDEX idx_foundation_scans_started_at ON foundation_scans (org_id, started_at DESC);
