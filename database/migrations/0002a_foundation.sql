CREATE TABLE foundation_snapshots (
    foundation_snapshot_id text PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    foundation_version integer NOT NULL,
    sections jsonb NOT NULL DEFAULT '{}'::jsonb,
    source text NOT NULL DEFAULT 'manual',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (org_id, foundation_version)
);

CREATE TABLE uploaded_assets (
    asset_id text PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    asset_kind text NOT NULL,
    storage_key text NOT NULL,
    mime_type text NOT NULL,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE foundation_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE uploaded_assets ENABLE ROW LEVEL SECURITY;

CREATE POLICY foundation_snapshots_tenant_isolation ON foundation_snapshots
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

CREATE POLICY uploaded_assets_tenant_isolation ON uploaded_assets
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());
