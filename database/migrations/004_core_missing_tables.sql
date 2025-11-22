-- ============================================
-- RAPTORFLOW CORE MISSING TABLES MIGRATION
-- Run this after 003_quests_table.sql
-- ============================================

-- ============================================
-- COHORTS/ICPs TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS cohorts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL,
  name VARCHAR(200) NOT NULL,
  executive_summary TEXT,
  
  -- Demographics
  demographics JSONB DEFAULT '{}', -- {company_size, industry, revenue, location}
  buyer_role VARCHAR(100),
  
  -- Psychographics (B=MAP framework)
  psychographics JSONB DEFAULT '{}', -- {motivation, ability, prompt_receptiveness, risk_tolerance, status_drive, community_orientation}
  
  -- Core fields
  pain_points TEXT[],
  goals TEXT[],
  behavioral_triggers TEXT[],
  
  -- Communication
  communication JSONB DEFAULT '{}', -- {channels, tone, format}
  budget VARCHAR(100),
  timeline VARCHAR(100),
  decision_structure VARCHAR(100),
  
  -- Tag fabric (50+ psychographic tags)
  tags TEXT[] DEFAULT '{}',
  
  -- Metadata
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- COHORT RELATIONS (ICP to ICP)
-- ============================================
CREATE TABLE IF NOT EXISTS cohort_relations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL,
  from_cohort_id UUID REFERENCES cohorts(id) ON DELETE CASCADE,
  to_cohort_id UUID REFERENCES cohorts(id) ON DELETE CASCADE,
  relation_type VARCHAR(50), -- 'recommends_to', 'upgrades_to', 'competes_with', 'influences'
  strength INTEGER CHECK (strength BETWEEN 1 AND 10),
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- GLOBAL STRATEGY TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS global_strategies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL UNIQUE,
  
  -- Business Context
  business_context JSONB DEFAULT '{}', -- {company_name, industry, stage, team_size}
  offers JSONB DEFAULT '[]', -- Array of {name, description, pricing, target_segment}
  
  -- Market Position
  markets JSONB DEFAULT '[]', -- Array of {geography, channels, positioning}
  center_of_gravity VARCHAR(200), -- Primary strategic focus
  
  -- Success Criteria
  success_metrics JSONB DEFAULT '{}', -- {primary_metric, target_value, timeframe}
  ninety_day_goal TEXT,
  
  -- Constitution (operational rules)
  constitution JSONB DEFAULT '{}', -- {tone_guidelines, forbidden_tactics, brand_values, constraints}
  
  -- Metadata
  strategy_state VARCHAR(20) DEFAULT 'Draft' CHECK (strategy_state IN ('Draft', 'Active', 'Archived')),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- QUICK WINS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS quick_wins (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL,
  title VARCHAR(250) NOT NULL,
  summary TEXT,
  
  -- Source intelligence
  source_type VARCHAR(50), -- 'news', 'internal_asset', 'trend', 'support_insight'
  source_url TEXT,
  source_data JSONB DEFAULT '{}',
  
  -- ICP targeting
  target_cohort_ids UUID[],
  matched_tags TEXT[], -- Which ICP tags this opportunity matches
  
  -- Suggested action
  suggested_move_type VARCHAR(100), -- Maneuver type suggestion
  suggested_assets UUID[], -- Asset IDs to use
  micro_asset_suggestions JSONB DEFAULT '[]', -- Array of {type, description, example}
  
  -- Metadata
  status VARCHAR(20) DEFAULT 'New' CHECK (status IN ('New', 'Reviewed', 'Actioned', 'Dismissed')),
  priority_score INTEGER CHECK (priority_score BETWEEN 1 AND 10),
  expires_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  actioned_at TIMESTAMP
);

-- ============================================
-- WORKSPACES TABLE (for multi-user support)
-- ============================================
CREATE TABLE IF NOT EXISTS workspaces (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(200) NOT NULL,
  slug VARCHAR(100) UNIQUE,
  plan VARCHAR(20) DEFAULT 'Ascent' CHECK (plan IN ('Ascent', 'Glide', 'Soar')),
  
  -- Limits by plan
  cohorts_limit INTEGER DEFAULT 3,
  moves_per_sprint_limit INTEGER DEFAULT 5,
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- USER WORKSPACES (many-to-many)
-- ============================================
CREATE TABLE IF NOT EXISTS user_workspaces (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
  role VARCHAR(20) DEFAULT 'Owner' CHECK (role IN ('Owner', 'Strategist', 'Creator', 'Analyst', 'Viewer')),
  joined_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id, workspace_id)
);

-- ============================================
-- SUPPORT FEEDBACK TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS support_feedback (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL,
  
  -- Source
  type VARCHAR(50), -- 'ticket', 'review', 'nps', 'conversation', 'complaint'
  source VARCHAR(100), -- Platform/channel
  
  -- Content
  title VARCHAR(250),
  content TEXT,
  sentiment VARCHAR(20), -- 'positive', 'neutral', 'negative', 'critical'
  
  -- Intelligence extraction
  extracted_tags TEXT[], -- Auto-extracted pain/desire tags
  related_cohort_ids UUID[],
  triggers_defensive_move BOOLEAN DEFAULT false,
  
  -- Metadata
  customer_id VARCHAR(100),
  created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- MOVE DECISIONS (for Weekly Review)
-- ============================================
CREATE TABLE IF NOT EXISTS move_decisions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  move_id UUID REFERENCES moves(id) ON DELETE CASCADE,
  sprint_id UUID REFERENCES sprints(id),
  decision VARCHAR(20) NOT NULL CHECK (decision IN ('Scale', 'Tweak', 'Kill', 'Archive')),
  rationale TEXT,
  ai_recommendation VARCHAR(20),
  ai_reasoning TEXT,
  decided_by UUID,
  decided_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- NOTIFICATIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL,
  user_id UUID,
  type VARCHAR(50), -- 'sprint_review_ready', 'anomaly_critical', 'move_approval_needed'
  title VARCHAR(250),
  message TEXT,
  link TEXT,
  read BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- INDEXES
-- ============================================
CREATE INDEX IF NOT EXISTS idx_cohorts_workspace ON cohorts(workspace_id);
CREATE INDEX IF NOT EXISTS idx_cohorts_tags ON cohorts USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_cohort_relations_workspace ON cohort_relations(workspace_id);
CREATE INDEX IF NOT EXISTS idx_cohort_relations_from ON cohort_relations(from_cohort_id);
CREATE INDEX IF NOT EXISTS idx_cohort_relations_to ON cohort_relations(to_cohort_id);
CREATE INDEX IF NOT EXISTS idx_global_strategies_workspace ON global_strategies(workspace_id);
CREATE INDEX IF NOT EXISTS idx_quick_wins_workspace ON quick_wins(workspace_id);
CREATE INDEX IF NOT EXISTS idx_quick_wins_status ON quick_wins(status);
CREATE INDEX IF NOT EXISTS idx_quick_wins_cohorts ON quick_wins USING GIN(target_cohort_ids);
CREATE INDEX IF NOT EXISTS idx_workspaces_slug ON workspaces(slug);
CREATE INDEX IF NOT EXISTS idx_user_workspaces_user ON user_workspaces(user_id);
CREATE INDEX IF NOT EXISTS idx_user_workspaces_workspace ON user_workspaces(workspace_id);
CREATE INDEX IF NOT EXISTS idx_support_feedback_workspace ON support_feedback(workspace_id);
CREATE INDEX IF NOT EXISTS idx_support_feedback_tags ON support_feedback USING GIN(extracted_tags);
CREATE INDEX IF NOT EXISTS idx_move_decisions_move ON move_decisions(move_id);
CREATE INDEX IF NOT EXISTS idx_move_decisions_sprint ON move_decisions(sprint_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_workspace ON notifications(workspace_id);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(read);

-- ============================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================
CREATE TRIGGER update_cohorts_updated_at
  BEFORE UPDATE ON cohorts
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_global_strategies_updated_at
  BEFORE UPDATE ON global_strategies
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workspaces_updated_at
  BEFORE UPDATE ON workspaces
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- RLS POLICIES
-- ============================================

-- Enable RLS
ALTER TABLE cohorts ENABLE ROW LEVEL SECURITY;
ALTER TABLE cohort_relations ENABLE ROW LEVEL SECURITY;
ALTER TABLE global_strategies ENABLE ROW LEVEL SECURITY;
ALTER TABLE quick_wins ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE support_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE move_decisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- Cohorts policies
CREATE POLICY "Users can view cohorts in their workspace"
  ON cohorts FOR SELECT
  USING (workspace_id = get_user_workspace_id());

CREATE POLICY "Users can insert cohorts in their workspace"
  ON cohorts FOR INSERT
  WITH CHECK (workspace_id = get_user_workspace_id());

CREATE POLICY "Users can update cohorts in their workspace"
  ON cohorts FOR UPDATE
  USING (workspace_id = get_user_workspace_id())
  WITH CHECK (workspace_id = get_user_workspace_id());

CREATE POLICY "Users can delete cohorts in their workspace"
  ON cohorts FOR DELETE
  USING (workspace_id = get_user_workspace_id());

-- Cohort relations policies
CREATE POLICY "Users can view cohort relations in their workspace"
  ON cohort_relations FOR SELECT
  USING (workspace_id = get_user_workspace_id());

CREATE POLICY "Users can manage cohort relations in their workspace"
  ON cohort_relations FOR ALL
  USING (workspace_id = get_user_workspace_id())
  WITH CHECK (workspace_id = get_user_workspace_id());

-- Global strategies policies
CREATE POLICY "Users can view their workspace strategy"
  ON global_strategies FOR SELECT
  USING (workspace_id = get_user_workspace_id());

CREATE POLICY "Users can insert their workspace strategy"
  ON global_strategies FOR INSERT
  WITH CHECK (workspace_id = get_user_workspace_id());

CREATE POLICY "Users can update their workspace strategy"
  ON global_strategies FOR UPDATE
  USING (workspace_id = get_user_workspace_id())
  WITH CHECK (workspace_id = get_user_workspace_id());

-- Quick wins policies
CREATE POLICY "Users can view quick wins in their workspace"
  ON quick_wins FOR SELECT
  USING (workspace_id = get_user_workspace_id());

CREATE POLICY "Users can manage quick wins in their workspace"
  ON quick_wins FOR ALL
  USING (workspace_id = get_user_workspace_id())
  WITH CHECK (workspace_id = get_user_workspace_id());

-- Workspaces policies (users can view workspaces they belong to)
CREATE POLICY "Users can view their workspaces"
  ON workspaces FOR SELECT
  USING (
    id IN (
      SELECT workspace_id FROM user_workspaces WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Owners can update their workspace"
  ON workspaces FOR UPDATE
  USING (
    id IN (
      SELECT workspace_id FROM user_workspaces 
      WHERE user_id = auth.uid() AND role = 'Owner'
    )
  );

-- User workspaces policies
CREATE POLICY "Users can view their workspace memberships"
  ON user_workspaces FOR SELECT
  USING (user_id = auth.uid() OR workspace_id = get_user_workspace_id());

CREATE POLICY "Owners can manage workspace memberships"
  ON user_workspaces FOR ALL
  USING (
    workspace_id IN (
      SELECT workspace_id FROM user_workspaces 
      WHERE user_id = auth.uid() AND role = 'Owner'
    )
  );

-- Support feedback policies
CREATE POLICY "Users can view support feedback in their workspace"
  ON support_feedback FOR SELECT
  USING (workspace_id = get_user_workspace_id());

CREATE POLICY "Users can manage support feedback in their workspace"
  ON support_feedback FOR ALL
  USING (workspace_id = get_user_workspace_id())
  WITH CHECK (workspace_id = get_user_workspace_id());

-- Move decisions policies
CREATE POLICY "Users can view move decisions in their workspace"
  ON move_decisions FOR SELECT
  USING (
    move_id IN (
      SELECT id FROM moves WHERE workspace_id = get_user_workspace_id()
    )
  );

CREATE POLICY "Users can manage move decisions in their workspace"
  ON move_decisions FOR ALL
  USING (
    move_id IN (
      SELECT id FROM moves WHERE workspace_id = get_user_workspace_id()
    )
  );

-- Notifications policies
CREATE POLICY "Users can view their own notifications"
  ON notifications FOR SELECT
  USING (user_id = auth.uid());

CREATE POLICY "Users can update their own notifications"
  ON notifications FOR UPDATE
  USING (user_id = auth.uid());

CREATE POLICY "System can insert notifications"
  ON notifications FOR INSERT
  WITH CHECK (workspace_id = get_user_workspace_id());

-- ============================================
-- HELPER FUNCTION (if not already exists)
-- ============================================
-- Note: This is a placeholder. In production, implement proper workspace resolution
-- For development, you can use a fixed workspace ID or implement based on your auth setup

CREATE OR REPLACE FUNCTION get_user_workspace_id()
RETURNS UUID AS $$
BEGIN
  -- Option 1: Get from user_workspaces table
  RETURN (
    SELECT workspace_id 
    FROM user_workspaces 
    WHERE user_id = auth.uid() 
    LIMIT 1
  );
  
  -- Option 2: For development, return a fixed UUID
  -- RETURN 'YOUR_DEV_WORKSPACE_ID'::uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

