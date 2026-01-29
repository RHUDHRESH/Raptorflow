-- BCM Manifests Table
-- Stores BCM JSON with versioning and timestamps

CREATE TABLE IF NOT EXISTS bcm_manifests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id UUID REFERENCES onboarding_sessions(id) ON DELETE SET NULL,
    version INTEGER NOT NULL,
    checksum VARCHAR(64) NOT NULL,
    manifest_json JSONB NOT NULL,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(workspace_id, version)
);

CREATE INDEX IF NOT EXISTS idx_bcm_manifests_workspace_id ON bcm_manifests(workspace_id);
CREATE INDEX IF NOT EXISTS idx_bcm_manifests_session_id ON bcm_manifests(session_id);
CREATE INDEX IF NOT EXISTS idx_bcm_manifests_version ON bcm_manifests(workspace_id, version);

CREATE OR REPLACE FUNCTION update_bcm_manifests_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_bcm_manifests_updated_at
BEFORE UPDATE ON bcm_manifests
FOR EACH ROW EXECUTE FUNCTION update_bcm_manifests_updated_at();

COMMENT ON TABLE bcm_manifests IS 'BCM manifests with versioning and timestamps';
COMMENT ON COLUMN bcm_manifests.version IS 'Incrementing version number per workspace';
