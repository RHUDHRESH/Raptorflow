-- Add Assets Table for Asset Factory
-- Run this after 001_move_system_schema.sql

CREATE TABLE IF NOT EXISTS assets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL,
  move_id UUID REFERENCES moves(id) ON DELETE SET NULL,
  icp_id UUID,
  name VARCHAR(250) NOT NULL,
  type VARCHAR(50) NOT NULL CHECK (type IN ('case_study', 'whitepaper', 'video', 'blog_post', 'social_post', 'email', 'landing_page', 'creative', 'template', 'other')),
  status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'review', 'approved', 'published', 'archived')),
  url TEXT,
  file_path TEXT,
  thumbnail_url TEXT,
  description TEXT,
  tags VARCHAR(50)[] DEFAULT '{}',
  metadata JSONB DEFAULT '{}',
  created_by UUID,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  published_at TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_assets_workspace ON assets(workspace_id);
CREATE INDEX IF NOT EXISTS idx_assets_move ON assets(move_id);
CREATE INDEX IF NOT EXISTS idx_assets_icp ON assets(icp_id);
CREATE INDEX IF NOT EXISTS idx_assets_type ON assets(type);
CREATE INDEX IF NOT EXISTS idx_assets_status ON assets(status);
CREATE INDEX IF NOT EXISTS idx_assets_tags ON assets USING GIN(tags);

-- Trigger for updated_at
CREATE TRIGGER update_assets_updated_at
  BEFORE UPDATE ON assets
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- RLS Policy
ALTER TABLE assets ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view assets in their workspace"
  ON assets FOR SELECT
  USING (workspace_id = get_user_workspace_id());

CREATE POLICY "Users can insert assets in their workspace"
  ON assets FOR INSERT
  WITH CHECK (workspace_id = get_user_workspace_id());

CREATE POLICY "Users can update assets in their workspace"
  ON assets FOR UPDATE
  USING (workspace_id = get_user_workspace_id())
  WITH CHECK (workspace_id = get_user_workspace_id());

CREATE POLICY "Users can delete assets in their workspace"
  ON assets FOR DELETE
  USING (workspace_id = get_user_workspace_id());


