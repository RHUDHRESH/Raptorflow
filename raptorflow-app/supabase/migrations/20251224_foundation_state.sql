-- Universal Foundation State Table (2025-12-24)

CREATE TABLE IF NOT EXISTS foundation_state (
    tenant_id UUID PRIMARY KEY,
    data JSONB NOT NULL DEFAULT '{}',
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Enable RLS
ALTER TABLE foundation_state ENABLE ROW LEVEL SECURITY;

-- Tenant Isolation
CREATE POLICY tenant_isolation_foundation_state ON foundation_state
    FOR ALL USING (tenant_id = auth.uid()) WITH CHECK (tenant_id = auth.uid());

-- Index for lookup
CREATE INDEX IF NOT EXISTS idx_foundation_state_tenant ON foundation_state(tenant_id);
