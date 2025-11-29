-- Create moves table
CREATE TABLE IF NOT EXISTS moves (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'planning', -- 'planning', 'active', 'completed', 'paused'
  type TEXT, -- 'campaign', 'one-off', etc.
  primary_goal TEXT,
  secondary_goals TEXT[],
  primary_cohort TEXT,
  secondary_cohorts TEXT[],
  timeframe INTEGER, -- days
  intensity TEXT, -- 'Light', 'Standard', 'Aggressive'
  progress INTEGER DEFAULT 0,
  days_elapsed INTEGER DEFAULT 0,
  campaign_id TEXT, -- Optional link to a campaign (can be FK later if campaigns table exists)
  journey_stage_from TEXT,
  journey_stage_to TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Enable RLS
ALTER TABLE moves ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view moves in their workspace" ON moves
  FOR SELECT
  USING (
    workspace_id IN (
      SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Users can insert moves in their workspace" ON moves
  FOR INSERT
  WITH CHECK (
    workspace_id IN (
      SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Users can update moves in their workspace" ON moves
  FOR UPDATE
  USING (
    workspace_id IN (
      SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Users can delete moves in their workspace" ON moves
  FOR DELETE
  USING (
    workspace_id IN (
      SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
    )
  );

-- Realtime
alter publication supabase_realtime add table moves;
