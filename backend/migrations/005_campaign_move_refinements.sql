-- Campaign and Move model enhancements

ALTER TABLE campaigns
ADD COLUMN IF NOT EXISTS workspace_id UUID,
ADD COLUMN IF NOT EXISTS phase_order JSONB DEFAULT '[]'::JSONB,
ADD COLUMN IF NOT EXISTS milestones JSONB DEFAULT '[]'::JSONB,
ADD COLUMN IF NOT EXISTS campaign_tag TEXT;

ALTER TABLE campaigns
ADD COLUMN IF NOT EXISTS arc_data JSONB DEFAULT '{}'::JSONB;

CREATE INDEX IF NOT EXISTS idx_campaigns_workspace ON campaigns(workspace_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_tag ON campaigns(campaign_tag);

ALTER TABLE moves
ADD COLUMN IF NOT EXISTS workspace_id UUID,
ADD COLUMN IF NOT EXISTS campaign_name TEXT,
ADD COLUMN IF NOT EXISTS campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS consensus_metrics JSONB DEFAULT '{}'::JSONB,
ADD COLUMN IF NOT EXISTS decree TEXT,
ADD COLUMN IF NOT EXISTS reasoning_chain_id UUID REFERENCES reasoning_chains(id);

CREATE INDEX IF NOT EXISTS idx_moves_campaign ON moves(campaign_id);
CREATE INDEX IF NOT EXISTS idx_moves_workspace ON moves(workspace_id);
