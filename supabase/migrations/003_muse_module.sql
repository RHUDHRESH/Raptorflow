-- Create muse_assets table
CREATE TABLE IF NOT EXISTS muse_assets (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  content TEXT, -- Markdown or plain text
  type TEXT NOT NULL, -- 'email', 'post', 'script', 'ad', 'long-form'
  status TEXT DEFAULT 'draft', -- 'draft', 'final', 'archived'
  tags TEXT[],
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Enable RLS
ALTER TABLE muse_assets ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view assets in their workspace" ON muse_assets
  FOR SELECT
  USING (
    workspace_id IN (
      SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Users can insert assets in their workspace" ON muse_assets
  FOR INSERT
  WITH CHECK (
    workspace_id IN (
      SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Users can update assets in their workspace" ON muse_assets
  FOR UPDATE
  USING (
    workspace_id IN (
      SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Users can delete assets in their workspace" ON muse_assets
  FOR DELETE
  USING (
    workspace_id IN (
      SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
    )
  );

-- Realtime
alter publication supabase_realtime add table muse_assets;
