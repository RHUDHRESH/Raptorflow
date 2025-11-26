-- Strategic Marketing System Database Schema
-- Migration: 20240125_strategic_system

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- POSITIONING (Strategic Foundation)
-- ============================================================================

CREATE TABLE IF NOT EXISTS positioning (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  for_cohort_id UUID REFERENCES cohorts(id),
  problem_statement TEXT,
  category_frame TEXT NOT NULL,
  differentiator TEXT NOT NULL,
  reason_to_believe TEXT NOT NULL,
  competitive_alternative TEXT,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS message_architecture (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  positioning_id UUID REFERENCES positioning(id) ON DELETE CASCADE,
  primary_claim TEXT NOT NULL,
  tagline TEXT,
  elevator_pitch TEXT,
  proof_points JSONB, -- [{id, claim, evidence, priority, for_journey_stage}]
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- CAMPAIGNS (Strategic Orchestration)
-- ============================================================================

CREATE TABLE IF NOT EXISTS campaigns (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  positioning_id UUID REFERENCES positioning(id),
  message_architecture_id UUID REFERENCES message_architecture(id),
  objective TEXT NOT NULL,
  objective_type TEXT CHECK (objective_type IN ('awareness', 'consideration', 'conversion', 'retention', 'advocacy')),
  objective_statement TEXT,
  success_definition TEXT,
  primary_metric TEXT,
  target_value TEXT,
  secondary_metrics JSONB,
  budget NUMERIC,
  start_date DATE,
  end_date DATE,
  status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'paused', 'completed', 'archived')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS campaign_cohorts (
  campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
  cohort_id UUID REFERENCES cohorts(id) ON DELETE CASCADE,
  priority TEXT DEFAULT 'secondary' CHECK (priority IN ('primary', 'secondary')),
  journey_stage_current TEXT,
  journey_stage_target TEXT,
  PRIMARY KEY (campaign_id, cohort_id)
);

CREATE TABLE IF NOT EXISTS campaign_channels (
  campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
  channel TEXT NOT NULL,
  role TEXT CHECK (role IN ('reach', 'engage', 'convert', 'retain')),
  budget_percentage NUMERIC,
  frequency TEXT,
  key_messages JSONB,
  PRIMARY KEY (campaign_id, channel)
);

-- ============================================================================
-- ENHANCED COHORTS (Strategic Attributes)
-- ============================================================================

-- Add strategic attributes to cohorts table
ALTER TABLE cohorts ADD COLUMN IF NOT EXISTS buying_triggers JSONB;
ALTER TABLE cohorts ADD COLUMN IF NOT EXISTS decision_criteria JSONB;
ALTER TABLE cohorts ADD COLUMN IF NOT EXISTS objection_map JSONB;
ALTER TABLE cohorts ADD COLUMN IF NOT EXISTS attention_windows JSONB;
ALTER TABLE cohorts ADD COLUMN IF NOT EXISTS competitive_frame JSONB;
ALTER TABLE cohorts ADD COLUMN IF NOT EXISTS journey_distribution JSONB;
ALTER TABLE cohorts ADD COLUMN IF NOT EXISTS decision_making_unit JSONB;

-- ============================================================================
-- ENHANCED MOVES (Campaign Integration)
-- ============================================================================

-- Link moves to campaigns and add journey transitions
ALTER TABLE moves ADD COLUMN IF NOT EXISTS campaign_id UUID REFERENCES campaigns(id);
ALTER TABLE moves ADD COLUMN IF NOT EXISTS journey_stage_from TEXT;
ALTER TABLE moves ADD COLUMN IF NOT EXISTS journey_stage_to TEXT;
ALTER TABLE moves ADD COLUMN IF NOT EXISTS message_variant_id UUID;
ALTER TABLE moves ADD COLUMN IF NOT EXISTS creative_brief JSONB;

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_campaigns_workspace ON campaigns(workspace_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);
CREATE INDEX IF NOT EXISTS idx_campaigns_dates ON campaigns(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_moves_campaign ON moves(campaign_id);
CREATE INDEX IF NOT EXISTS idx_positioning_workspace ON positioning(workspace_id);
CREATE INDEX IF NOT EXISTS idx_positioning_active ON positioning(is_active);
CREATE INDEX IF NOT EXISTS idx_message_arch_positioning ON message_architecture(positioning_id);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS on new tables
ALTER TABLE positioning ENABLE ROW LEVEL SECURITY;
ALTER TABLE message_architecture ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaign_cohorts ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaign_channels ENABLE ROW LEVEL SECURITY;

-- Positioning policies
CREATE POLICY "Users can view positioning in their workspace"
  ON positioning FOR SELECT
  USING (workspace_id IN (
    SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
  ));

CREATE POLICY "Users can create positioning in their workspace"
  ON positioning FOR INSERT
  WITH CHECK (workspace_id IN (
    SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
  ));

CREATE POLICY "Users can update positioning in their workspace"
  ON positioning FOR UPDATE
  USING (workspace_id IN (
    SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
  ));

-- Campaign policies
CREATE POLICY "Users can view campaigns in their workspace"
  ON campaigns FOR SELECT
  USING (workspace_id IN (
    SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
  ));

CREATE POLICY "Users can create campaigns in their workspace"
  ON campaigns FOR INSERT
  WITH CHECK (workspace_id IN (
    SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
  ));

CREATE POLICY "Users can update campaigns in their workspace"
  ON campaigns FOR UPDATE
  USING (workspace_id IN (
    SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
  ));

-- Message architecture policies (inherit from positioning)
CREATE POLICY "Users can view message architecture"
  ON message_architecture FOR SELECT
  USING (positioning_id IN (
    SELECT id FROM positioning WHERE workspace_id IN (
      SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
    )
  ));

CREATE POLICY "Users can create message architecture"
  ON message_architecture FOR INSERT
  WITH CHECK (positioning_id IN (
    SELECT id FROM positioning WHERE workspace_id IN (
      SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
    )
  ));

-- Campaign cohorts policies (inherit from campaign)
CREATE POLICY "Users can view campaign cohorts"
  ON campaign_cohorts FOR SELECT
  USING (campaign_id IN (
    SELECT id FROM campaigns WHERE workspace_id IN (
      SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
    )
  ));

CREATE POLICY "Users can manage campaign cohorts"
  ON campaign_cohorts FOR ALL
  USING (campaign_id IN (
    SELECT id FROM campaigns WHERE workspace_id IN (
      SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
    )
  ));

-- Campaign channels policies (inherit from campaign)
CREATE POLICY "Users can view campaign channels"
  ON campaign_channels FOR SELECT
  USING (campaign_id IN (
    SELECT id FROM campaigns WHERE workspace_id IN (
      SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
    )
  ));

CREATE POLICY "Users can manage campaign channels"
  ON campaign_channels FOR ALL
  USING (campaign_id IN (
    SELECT id FROM campaigns WHERE workspace_id IN (
      SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
    )
  ));

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_positioning_updated_at BEFORE UPDATE ON positioning
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_message_architecture_updated_at BEFORE UPDATE ON message_architecture
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_campaigns_updated_at BEFORE UPDATE ON campaigns
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
