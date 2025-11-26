-- ============================================
-- RAPTORFLOW STRATEGIC SYSTEM FOUNDATION
-- Migration 009: New Tables for Strategic Marketing System
-- Run after 008_self_improving_loops.sql
-- ============================================

-- ============================================
-- 1. POSITIONING TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.positioning (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
  
  -- Basic Info
  name VARCHAR(255) NOT NULL,
  for_cohort_id UUID REFERENCES public.cohorts(id) ON DELETE SET NULL,
  
  -- Positioning Statement Components
  who_statement TEXT, -- "who are drowning in..."
  category_frame TEXT, -- "[Product] is the [category]"
  differentiator TEXT, -- "that [unique value]"
  reason_to_believe TEXT, -- "because [evidence]"
  competitive_alternative TEXT, -- What they'd do without you
  
  -- Status
  is_active BOOLEAN DEFAULT false,
  is_validated BOOLEAN DEFAULT false,
  
  -- Metadata
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  
  -- Only one active positioning per workspace
  CONSTRAINT one_active_per_workspace UNIQUE (workspace_id, is_active) 
    WHERE (is_active = true)
);

-- ============================================
-- 2. MESSAGE ARCHITECTURE TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.message_architecture (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  positioning_id UUID NOT NULL REFERENCES public.positioning(id) ON DELETE CASCADE,
  
  -- Message Hierarchy
  primary_claim TEXT NOT NULL, -- The ONE thing you want them to believe
  proof_points JSONB DEFAULT '[]'::jsonb, -- Array of {claim, evidence[], for_journey_stages[]}
  
  -- Messaging Variants
  tagline VARCHAR(100), -- 5-7 word memorable tagline
  elevator_pitch TEXT, -- 30-second pitch version
  long_form_narrative TEXT, -- Full story version
  
  -- Metadata
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 3. CAMPAIGNS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.campaigns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
  positioning_id UUID REFERENCES public.positioning(id) ON DELETE SET NULL,
  
  -- Basic Info
  name VARCHAR(255) NOT NULL,
  description TEXT,
  
  -- Objective (Single objective per campaign)
  objective VARCHAR(50) NOT NULL CHECK (objective IN ('awareness', 'consideration', 'conversion', 'retention', 'advocacy')),
  objective_statement TEXT, -- "Increase demo requests by 40% in Q1"
  primary_metric VARCHAR(100), -- "Demo requests"
  target_value NUMERIC, -- 50
  
  -- Timeline
  start_date DATE,
  end_date DATE,
  
  -- Budget (optional)
  budget_total NUMERIC,
  budget_currency VARCHAR(3) DEFAULT 'USD',
  
  -- Channel Strategy
  channel_strategy JSONB DEFAULT '[]'::jsonb, -- Array of {channel, role, budget_percentage, frequency}
  
  -- Status
  status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'planning', 'active', 'paused', 'completed', 'cancelled')),
  
  -- Performance Tracking
  health_score INTEGER CHECK (health_score BETWEEN 0 AND 100),
  current_performance JSONB DEFAULT '{}'::jsonb, -- {metric_name: current_value}
  
  -- Metadata
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  launched_at TIMESTAMP WITH TIME ZONE,
  completed_at TIMESTAMP WITH TIME ZONE
);

-- ============================================
-- 4. CAMPAIGN COHORTS (Junction Table)
-- ============================================
CREATE TABLE IF NOT EXISTS public.campaign_cohorts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  campaign_id UUID NOT NULL REFERENCES public.campaigns(id) ON DELETE CASCADE,
  cohort_id UUID NOT NULL REFERENCES public.cohorts(id) ON DELETE CASCADE,
  
  -- Priority
  priority VARCHAR(20) DEFAULT 'secondary' CHECK (priority IN ('primary', 'secondary')),
  
  -- Journey Stage Targeting
  journey_stage_current VARCHAR(50), -- Where they are now
  journey_stage_target VARCHAR(50), -- Where we want them to be
  
  -- Metadata
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  
  -- One cohort can only be in a campaign once
  UNIQUE(campaign_id, cohort_id)
);

-- ============================================
-- 5. STRATEGY INSIGHTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.strategy_insights (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
  
  -- Source (what generated this insight)
  source_type VARCHAR(50) NOT NULL, -- 'campaign', 'move', 'cohort', 'asset', 'positioning'
  source_id UUID, -- ID of the source entity
  
  -- Insight Details
  insight_type VARCHAR(50) NOT NULL, -- 'cohort_preference', 'campaign_pacing', 'move_effectiveness', 'asset_optimization', 'positioning_validation'
  title VARCHAR(255) NOT NULL,
  description TEXT NOT NULL,
  
  -- Evidence
  evidence JSONB DEFAULT '{}'::jsonb, -- Supporting data for the insight
  
  -- Recommendation
  recommended_action TEXT,
  
  -- Confidence & Impact
  confidence_score NUMERIC CHECK (confidence_score BETWEEN 0 AND 1), -- 0.0 to 1.0
  impact_score INTEGER CHECK (impact_score BETWEEN 1 AND 10), -- 1 to 10
  
  -- Status
  status VARCHAR(20) DEFAULT 'new' CHECK (status IN ('new', 'reviewed', 'actioned', 'dismissed')),
  
  -- Metadata
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  reviewed_at TIMESTAMP WITH TIME ZONE,
  actioned_at TIMESTAMP WITH TIME ZONE
);

-- ============================================
-- 6. COMPETITORS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.competitors (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
  
  -- Basic Info
  name VARCHAR(255) NOT NULL,
  website TEXT,
  
  -- Competitive Intelligence
  positioning_statement TEXT,
  key_messages TEXT[],
  
  -- Analysis
  strengths TEXT[],
  weaknesses TEXT[],
  
  -- Market Position
  price_position VARCHAR(50), -- 'premium', 'mid-market', 'budget'
  market_share_estimate NUMERIC, -- Percentage (0-100)
  
  -- Metadata
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 7. INDEXES
-- ============================================

-- Positioning indexes
CREATE INDEX IF NOT EXISTS idx_positioning_workspace ON public.positioning(workspace_id);
CREATE INDEX IF NOT EXISTS idx_positioning_active ON public.positioning(workspace_id, is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_positioning_cohort ON public.positioning(for_cohort_id);

-- Message architecture indexes
CREATE INDEX IF NOT EXISTS idx_message_architecture_positioning ON public.message_architecture(positioning_id);

-- Campaigns indexes
CREATE INDEX IF NOT EXISTS idx_campaigns_workspace ON public.campaigns(workspace_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_positioning ON public.campaigns(positioning_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON public.campaigns(status);
CREATE INDEX IF NOT EXISTS idx_campaigns_dates ON public.campaigns(start_date, end_date);

-- Campaign cohorts indexes
CREATE INDEX IF NOT EXISTS idx_campaign_cohorts_campaign ON public.campaign_cohorts(campaign_id);
CREATE INDEX IF NOT EXISTS idx_campaign_cohorts_cohort ON public.campaign_cohorts(cohort_id);

-- Strategy insights indexes
CREATE INDEX IF NOT EXISTS idx_strategy_insights_workspace ON public.strategy_insights(workspace_id);
CREATE INDEX IF NOT EXISTS idx_strategy_insights_source ON public.strategy_insights(source_type, source_id);
CREATE INDEX IF NOT EXISTS idx_strategy_insights_type ON public.strategy_insights(insight_type);
CREATE INDEX IF NOT EXISTS idx_strategy_insights_status ON public.strategy_insights(status);

-- Competitors indexes
CREATE INDEX IF NOT EXISTS idx_competitors_workspace ON public.competitors(workspace_id);

-- ============================================
-- 8. TRIGGERS FOR UPDATED_AT
-- ============================================

-- Positioning trigger
DROP TRIGGER IF EXISTS update_positioning_updated_at ON public.positioning;
CREATE TRIGGER update_positioning_updated_at
  BEFORE UPDATE ON public.positioning
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- Message architecture trigger
DROP TRIGGER IF EXISTS update_message_architecture_updated_at ON public.message_architecture;
CREATE TRIGGER update_message_architecture_updated_at
  BEFORE UPDATE ON public.message_architecture
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- Campaigns trigger
DROP TRIGGER IF EXISTS update_campaigns_updated_at ON public.campaigns;
CREATE TRIGGER update_campaigns_updated_at
  BEFORE UPDATE ON public.campaigns
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- Competitors trigger
DROP TRIGGER IF EXISTS update_competitors_updated_at ON public.competitors;
CREATE TRIGGER update_competitors_updated_at
  BEFORE UPDATE ON public.competitors
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- ============================================
-- 9. ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================

-- Enable RLS
ALTER TABLE public.positioning ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.message_architecture ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.campaign_cohorts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.strategy_insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.competitors ENABLE ROW LEVEL SECURITY;

-- Positioning policies
DROP POLICY IF EXISTS "Users can view positioning in their workspace" ON public.positioning;
CREATE POLICY "Users can view positioning in their workspace"
  ON public.positioning FOR SELECT
  USING (workspace_id = get_user_workspace_id());

DROP POLICY IF EXISTS "Users can insert positioning in their workspace" ON public.positioning;
CREATE POLICY "Users can insert positioning in their workspace"
  ON public.positioning FOR INSERT
  WITH CHECK (workspace_id = get_user_workspace_id());

DROP POLICY IF EXISTS "Users can update positioning in their workspace" ON public.positioning;
CREATE POLICY "Users can update positioning in their workspace"
  ON public.positioning FOR UPDATE
  USING (workspace_id = get_user_workspace_id())
  WITH CHECK (workspace_id = get_user_workspace_id());

DROP POLICY IF EXISTS "Users can delete positioning in their workspace" ON public.positioning;
CREATE POLICY "Users can delete positioning in their workspace"
  ON public.positioning FOR DELETE
  USING (workspace_id = get_user_workspace_id());

-- Message architecture policies
DROP POLICY IF EXISTS "Users can view message architecture in their workspace" ON public.message_architecture;
CREATE POLICY "Users can view message architecture in their workspace"
  ON public.message_architecture FOR SELECT
  USING (
    positioning_id IN (
      SELECT id FROM public.positioning WHERE workspace_id = get_user_workspace_id()
    )
  );

DROP POLICY IF EXISTS "Users can manage message architecture in their workspace" ON public.message_architecture;
CREATE POLICY "Users can manage message architecture in their workspace"
  ON public.message_architecture FOR ALL
  USING (
    positioning_id IN (
      SELECT id FROM public.positioning WHERE workspace_id = get_user_workspace_id()
    )
  )
  WITH CHECK (
    positioning_id IN (
      SELECT id FROM public.positioning WHERE workspace_id = get_user_workspace_id()
    )
  );

-- Campaigns policies
DROP POLICY IF EXISTS "Users can view campaigns in their workspace" ON public.campaigns;
CREATE POLICY "Users can view campaigns in their workspace"
  ON public.campaigns FOR SELECT
  USING (workspace_id = get_user_workspace_id());

DROP POLICY IF EXISTS "Users can insert campaigns in their workspace" ON public.campaigns;
CREATE POLICY "Users can insert campaigns in their workspace"
  ON public.campaigns FOR INSERT
  WITH CHECK (workspace_id = get_user_workspace_id());

DROP POLICY IF EXISTS "Users can update campaigns in their workspace" ON public.campaigns;
CREATE POLICY "Users can update campaigns in their workspace"
  ON public.campaigns FOR UPDATE
  USING (workspace_id = get_user_workspace_id())
  WITH CHECK (workspace_id = get_user_workspace_id());

DROP POLICY IF EXISTS "Users can delete campaigns in their workspace" ON public.campaigns;
CREATE POLICY "Users can delete campaigns in their workspace"
  ON public.campaigns FOR DELETE
  USING (workspace_id = get_user_workspace_id());

-- Campaign cohorts policies
DROP POLICY IF EXISTS "Users can view campaign cohorts in their workspace" ON public.campaign_cohorts;
CREATE POLICY "Users can view campaign cohorts in their workspace"
  ON public.campaign_cohorts FOR SELECT
  USING (
    campaign_id IN (
      SELECT id FROM public.campaigns WHERE workspace_id = get_user_workspace_id()
    )
  );

DROP POLICY IF EXISTS "Users can manage campaign cohorts in their workspace" ON public.campaign_cohorts;
CREATE POLICY "Users can manage campaign cohorts in their workspace"
  ON public.campaign_cohorts FOR ALL
  USING (
    campaign_id IN (
      SELECT id FROM public.campaigns WHERE workspace_id = get_user_workspace_id()
    )
  )
  WITH CHECK (
    campaign_id IN (
      SELECT id FROM public.campaigns WHERE workspace_id = get_user_workspace_id()
    )
  );

-- Strategy insights policies
DROP POLICY IF EXISTS "Users can view strategy insights in their workspace" ON public.strategy_insights;
CREATE POLICY "Users can view strategy insights in their workspace"
  ON public.strategy_insights FOR SELECT
  USING (workspace_id = get_user_workspace_id());

DROP POLICY IF EXISTS "Users can manage strategy insights in their workspace" ON public.strategy_insights;
CREATE POLICY "Users can manage strategy insights in their workspace"
  ON public.strategy_insights FOR ALL
  USING (workspace_id = get_user_workspace_id())
  WITH CHECK (workspace_id = get_user_workspace_id());

-- Competitors policies
DROP POLICY IF EXISTS "Users can view competitors in their workspace" ON public.competitors;
CREATE POLICY "Users can view competitors in their workspace"
  ON public.competitors FOR SELECT
  USING (workspace_id = get_user_workspace_id());

DROP POLICY IF EXISTS "Users can manage competitors in their workspace" ON public.competitors;
CREATE POLICY "Users can manage competitors in their workspace"
  ON public.competitors FOR ALL
  USING (workspace_id = get_user_workspace_id())
  WITH CHECK (workspace_id = get_user_workspace_id());

-- ============================================
-- 10. GRANT PERMISSIONS
-- ============================================

-- Grant usage on schema (if not already granted)
GRANT USAGE ON SCHEMA public TO anon, authenticated;

-- Grant permissions on new tables
GRANT SELECT, INSERT, UPDATE, DELETE ON public.positioning TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.message_architecture TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.campaigns TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.campaign_cohorts TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.strategy_insights TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.competitors TO authenticated;

-- ============================================
-- MIGRATION COMPLETE
-- ============================================
