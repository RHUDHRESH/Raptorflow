-- RaptorFlow Assets Table
-- Stores metadata for uploaded files in Supabase Storage

CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    original_name TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    size_bytes INTEGER NOT NULL CHECK (size_bytes > 0),
    storage_path TEXT NOT NULL UNIQUE,
    public_url TEXT,
    asset_type VARCHAR(20) NOT NULL CHECK (asset_type IN ('image', 'document', 'video', 'audio')),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes for common queries
CREATE INDEX idx_assets_workspace ON assets(workspace_id);
CREATE INDEX idx_assets_type ON assets(workspace_id, asset_type);
CREATE INDEX idx_assets_created ON assets(workspace_id, created_at DESC);

-- RLS Policies (permissive for reconstruction mode)
ALTER TABLE assets ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all for service role" ON assets FOR ALL USING (true);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_assets_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_assets_updated_at
    BEFORE UPDATE ON assets
    FOR EACH ROW
    EXECUTE FUNCTION update_assets_updated_at();
