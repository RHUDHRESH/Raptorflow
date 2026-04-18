-- Competitor snapshots for tracking competitor site changes
-- Used by competitor deep scans to detect changes and create diffs

CREATE TABLE IF NOT EXISTS competitor_snapshots (
    snapshot_id text PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    competitor_url text NOT NULL,
    hash text,
    status text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'scanning', 'completed', 'changed', 'unchanged', 'failed')),
    scrape_data jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE competitor_snapshots ENABLE ROW LEVEL SECURITY;

CREATE POLICY competitor_snapshots_tenant ON competitor_snapshots
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

CREATE INDEX idx_competitor_snapshots_org_url ON competitor_snapshots (org_id, competitor_url);
CREATE INDEX idx_competitor_snapshots_created_at ON competitor_snapshots (org_id, created_at DESC);
CREATE INDEX idx_competitor_snapshots_status ON competitor_snapshots (org_id, status);