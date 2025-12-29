-- Campaign and Move model enhancements for first-class campaign entity
-- This migration ensures all required fields and indexes are present

-- Ensure campaigns table has all required fields for first-class entity
ALTER TABLE campaigns
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_campaigns_tenant_workspace ON campaigns(tenant_id, workspace_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);
CREATE INDEX IF NOT EXISTS idx_campaigns_created_at ON campaigns(created_at DESC);

-- Ensure moves table has proper nullable campaign_id foreign key
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'moves' AND column_name = 'campaign_id'
    ) THEN
        ALTER TABLE moves ADD COLUMN campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL;
    END IF;
END $$;

-- Add additional indexes for moves table
CREATE INDEX IF NOT EXISTS idx_moves_status ON moves(status);
CREATE INDEX IF NOT EXISTS idx_moves_campaign_status ON moves(campaign_id, status);
CREATE INDEX IF NOT EXISTS idx_moves_workspace_campaign ON moves(workspace_id, campaign_id);
CREATE INDEX IF NOT EXISTS idx_moves_created_at ON moves(created_at DESC);

-- Add updated_at trigger for campaigns (if not exists)
CREATE OR REPLACE FUNCTION update_campaign_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS campaign_updated_at_trigger ON campaigns;
CREATE TRIGGER campaign_updated_at_trigger
    BEFORE UPDATE ON campaigns
    FOR EACH ROW
    EXECUTE FUNCTION update_campaign_updated_at();

-- Add updated_at trigger for moves (if not exists)
CREATE OR REPLACE FUNCTION update_move_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS move_updated_at_trigger ON moves;
CREATE TRIGGER move_updated_at_trigger
    BEFORE UPDATE ON moves
    FOR EACH ROW
    EXECUTE FUNCTION update_move_updated_at();

-- Add campaign move count view for performance
CREATE OR REPLACE VIEW campaign_move_counts AS
SELECT
    c.id as campaign_id,
    c.title,
    c.workspace_id,
    c.status,
    COUNT(m.id) as move_count,
    COUNT(CASE WHEN m.status = 'completed' THEN 1 END) as completed_moves,
    COUNT(CASE WHEN m.status = 'in_progress' THEN 1 END) as active_moves
FROM campaigns c
LEFT JOIN moves m ON c.id = m.campaign_id
GROUP BY c.id, c.title, c.workspace_id, c.status;

-- Add index for campaign_tag uniqueness within workspace
CREATE UNIQUE INDEX IF NOT EXISTS idx_campaigns_workspace_tag_unique
ON campaigns(workspace_id, campaign_tag)
WHERE campaign_tag IS NOT NULL;
