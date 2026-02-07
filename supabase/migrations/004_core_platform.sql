-- =====================================================
-- RAPTORFLOW CORE PLATFORM SCHEMA
-- Migration 004: ICPs, Campaigns, Moves, Protocols, Metrics, Spikes
-- =====================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- ENUMS
-- =====================================================

-- Barrier types
CREATE TYPE barrier_type AS ENUM (
  'OBSCURITY',   -- Not known, low visibility
  'RISK',        -- Known but not trusted
  'INERTIA',     -- Trusted but not urgent
  'FRICTION',    -- Signed up but not activated
  'CAPACITY',    -- Active but not expanding
  'ATROPHY'      -- Churning or at risk
);

-- Protocol types
CREATE TYPE protocol_type AS ENUM (
  'A_AUTHORITY_BLITZ',
  'B_TRUST_ANCHOR',
  'C_COST_OF_INACTION',
  'D_HABIT_HARDCODE',
  'E_ENTERPRISE_WEDGE',
  'F_CHURN_INTERCEPT'
);

-- Goal types
CREATE TYPE goal_type AS ENUM (
  'velocity',
  'efficiency',
  'penetration'
);

-- Demand source types
CREATE TYPE demand_source_type AS ENUM (
  'capture',
  'creation',
  'expansion'
);

-- Persuasion axis types
CREATE TYPE persuasion_axis_type AS ENUM (
  'money',
  'time',
  'risk_image'
);

-- Campaign status
CREATE TYPE campaign_status AS ENUM (
  'draft',
  'planned',
  'active',
  'paused',
  'completed',
  'cancelled'
);

-- Move status
CREATE TYPE move_status AS ENUM (
  'planned',
  'generating_assets',
  'ready',
  'running',
  'paused',
  'completed',
  'failed'
);

-- Asset status
CREATE TYPE asset_status AS ENUM (
  'draft',
  'generating',
  'needs_review',
  'approved',
  'deployed',
  'archived'
);

-- RAG status
CREATE TYPE rag_status AS ENUM (
  'green',
  'amber',
  'red',
  'unknown'
);

-- Spike type
CREATE TYPE spike_type AS ENUM (
  'pipeline',
  'efficiency',
  'expansion'
);

-- Spike status
CREATE TYPE spike_status AS ENUM (
  'configuring',
  'active',
  'paused',
  'completed',
  'cancelled'
);

-- Guardrail action type
CREATE TYPE guardrail_action AS ENUM (
  'alert_only',
  'pause_and_alert',
  'auto_pause'
);

-- =====================================================
-- ICPS TABLE - 6D Intelligence Profiles
-- =====================================================
CREATE TABLE IF NOT EXISTS public.icps (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  intake_id UUID REFERENCES public.onboarding_intake(id) ON DELETE SET NULL,
  
  -- Core identity
  label VARCHAR(100) NOT NULL,
  slug VARCHAR(100),
  summary TEXT,
  
  -- 6D Dimensions (stored as JSONB for flexibility)
  firmographics JSONB DEFAULT '{}',
  -- { employee_range, industries[], stages[], regions[], exclude[], revenue_range, business_model }
  
  technographics JSONB DEFAULT '{}',
  -- { must_have[], nice_to_have[], red_flags[], current_stack[] }
  
  psychographics JSONB DEFAULT '{}',
  -- { pain_points[], motivations[], internal_triggers[], buying_constraints[], risk_tolerance }
  
  behavioral_triggers JSONB DEFAULT '[]',
  -- [{ signal, source, urgency_boost, description }]
  
  buying_committee JSONB DEFAULT '[]',
  -- [{ role, typical_title, concerns[], success_criteria[], influence_level }]
  
  category_context JSONB DEFAULT '{}',
  -- { market_position, current_solution, switching_triggers[], awareness_level }
  
  -- Scoring and prioritization
  fit_score INTEGER DEFAULT 0 CHECK (fit_score >= 0 AND fit_score <= 100),
  fit_reasoning TEXT,
  priority_rank INTEGER DEFAULT 0,
  
  -- Messaging
  messaging_angle TEXT,
  qualification_questions JSONB DEFAULT '[]',
  
  -- Barrier association
  primary_barriers barrier_type[] DEFAULT '{}',
  
  -- Status
  is_selected BOOLEAN DEFAULT true,
  is_archived BOOLEAN DEFAULT false,
  version INTEGER DEFAULT 1,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- COHORTS TABLE - Live segments linked to ICPs
-- =====================================================
CREATE TABLE IF NOT EXISTS public.cohorts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  icp_id UUID REFERENCES public.icps(id) ON DELETE SET NULL,
  
  -- Identity
  name VARCHAR(200) NOT NULL,
  description TEXT,
  
  -- Definition
  definition JSONB NOT NULL DEFAULT '{}',
  -- { rules[], data_sources[], refresh_frequency }
  
  -- Stats (updated periodically)
  member_count INTEGER DEFAULT 0,
  last_synced_at TIMESTAMPTZ,
  
  -- Status
  is_active BOOLEAN DEFAULT true,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- BARRIERS TABLE - Barrier classifications
-- =====================================================
CREATE TABLE IF NOT EXISTS public.barriers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- Association
  icp_id UUID REFERENCES public.icps(id) ON DELETE CASCADE,
  cohort_id UUID REFERENCES public.cohorts(id) ON DELETE CASCADE,
  
  -- Classification
  barrier_type barrier_type NOT NULL,
  confidence DECIMAL(3,2) DEFAULT 0.5 CHECK (confidence >= 0 AND confidence <= 1),
  
  -- Supporting data
  supporting_signals JSONB DEFAULT '[]',
  -- [{ signal_name, value, threshold, source, timestamp }]
  
  metrics_snapshot JSONB DEFAULT '{}',
  analysis_notes TEXT,
  
  -- Recommended protocols
  recommended_protocols protocol_type[] DEFAULT '{}',
  
  -- Timestamps
  diagnosed_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Only one active barrier per ICP/cohort
  CONSTRAINT unique_active_barrier UNIQUE (icp_id, cohort_id, barrier_type)
);

-- =====================================================
-- PROTOCOLS TABLE - Protocol definitions
-- =====================================================
CREATE TABLE IF NOT EXISTS public.protocols (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Core identity
  code protocol_type NOT NULL UNIQUE,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  
  -- Targeting
  targets_barrier barrier_type NOT NULL,
  
  -- Configuration
  trigger_conditions JSONB DEFAULT '[]',
  -- [{ metric, operator, threshold, description }]
  
  required_asset_types JSONB DEFAULT '[]',
  -- ['pillar_content', 'case_study', 'calculator', etc.]
  
  channel_rules JSONB DEFAULT '{}',
  -- { primary[], secondary[], exclude[] }
  
  metric_targets JSONB DEFAULT '{}',
  -- { metric_name: { target, unit, rag_thresholds } }
  
  standard_checklist JSONB DEFAULT '[]',
  -- [{ task, category, is_required }]
  
  -- Meta
  is_active BOOLEAN DEFAULT true,
  display_order INTEGER DEFAULT 0,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- MOVE TEMPLATES TABLE - Reusable move library
-- =====================================================
CREATE TABLE IF NOT EXISTS public.move_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Identity
  slug VARCHAR(100) NOT NULL UNIQUE,
  name VARCHAR(200) NOT NULL,
  description TEXT,
  
  -- Targeting
  protocol_type protocol_type NOT NULL,
  barrier_type barrier_type NOT NULL,
  funnel_stage VARCHAR(50), -- 'tofu', 'mofu', 'bofu', 'lifecycle'
  
  -- Configuration
  required_inputs JSONB DEFAULT '[]',
  -- [{ key, label, type, required }]
  
  channels JSONB DEFAULT '[]',
  -- ['linkedin_organic', 'youtube', 'email', etc.]
  
  task_template JSONB DEFAULT '[]',
  -- [{ task, category, estimated_hours, dependencies[] }]
  
  asset_requirements JSONB DEFAULT '[]',
  -- [{ type, quantity, description }]
  
  automation_hooks JSONB DEFAULT '{}',
  -- { triggers[], actions[], integrations[] }
  
  success_metrics JSONB DEFAULT '[]',
  -- [{ metric, target, unit }]
  
  -- Scoring
  base_impact_score INTEGER DEFAULT 50,
  base_effort_score INTEGER DEFAULT 50,
  
  -- Meta
  is_active BOOLEAN DEFAULT true,
  display_order INTEGER DEFAULT 0,
  tags JSONB DEFAULT '[]',
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- CAMPAIGNS TABLE - Strategic campaign containers
-- =====================================================
CREATE TABLE IF NOT EXISTS public.campaigns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- Identity
  name VARCHAR(200) NOT NULL,
  description TEXT,
  
  -- Strategy configuration
  goal goal_type NOT NULL,
  demand_source demand_source_type NOT NULL,
  persuasion_axis persuasion_axis_type NOT NULL,
  
  -- ICP targeting
  icp_ids UUID[] DEFAULT '{}',
  cohort_ids UUID[] DEFAULT '{}',
  
  -- Barrier and protocol binding
  primary_barriers barrier_type[] DEFAULT '{}',
  protocols protocol_type[] DEFAULT '{}',
  
  -- Time window
  start_date DATE,
  end_date DATE,
  
  -- Budget
  budget_plan JSONB DEFAULT '{}',
  -- { total, currency, allocation: { channel: percentage } }
  
  -- Targets
  targets JSONB DEFAULT '{}',
  -- { pipeline_value, opps, conversion_rate, etc. }
  
  -- Status and RAG
  status campaign_status DEFAULT 'draft',
  rag_status rag_status DEFAULT 'unknown',
  rag_details JSONB DEFAULT '{}',
  
  -- Meta
  created_from_spike UUID,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- MOVES TABLE - Active move instances
-- =====================================================
CREATE TABLE IF NOT EXISTS public.moves (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- Associations
  campaign_id UUID REFERENCES public.campaigns(id) ON DELETE CASCADE,
  spike_id UUID,
  template_id UUID REFERENCES public.move_templates(id) ON DELETE SET NULL,
  
  -- Identity
  name VARCHAR(200) NOT NULL,
  description TEXT,
  
  -- Configuration
  protocol protocol_type,
  icp_id UUID REFERENCES public.icps(id) ON DELETE SET NULL,
  
  -- Customized data from template
  channels JSONB DEFAULT '[]',
  tasks JSONB DEFAULT '[]',
  -- [{ id, task, status, assignee, due_date, completed_at }]
  
  -- Scoring
  impact_score INTEGER DEFAULT 50,
  effort_score INTEGER DEFAULT 50,
  ev_score DECIMAL(5,2), -- Expected value = (impact * probability) / effort
  
  -- Status and progress
  status move_status DEFAULT 'planned',
  progress_percentage INTEGER DEFAULT 0,
  
  -- RAG
  rag_status rag_status DEFAULT 'unknown',
  rag_details JSONB DEFAULT '{}',
  
  -- Metrics
  kpis JSONB DEFAULT '{}',
  -- { metric_name: { target, actual, unit } }
  
  -- Dates
  planned_start DATE,
  planned_end DATE,
  actual_start TIMESTAMPTZ,
  actual_end TIMESTAMPTZ,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- ASSETS TABLE - Muse-generated assets
-- =====================================================
CREATE TABLE IF NOT EXISTS public.assets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- Associations
  move_id UUID REFERENCES public.moves(id) ON DELETE SET NULL,
  campaign_id UUID REFERENCES public.campaigns(id) ON DELETE SET NULL,
  icp_id UUID REFERENCES public.icps(id) ON DELETE SET NULL,
  protocol protocol_type,
  
  -- Identity
  name VARCHAR(300) NOT NULL,
  asset_type VARCHAR(100) NOT NULL,
  -- 'pillar_webinar_script', 'linkedin_post', 'email_sequence', 'battlecard', etc.
  
  -- Content
  content TEXT,
  content_format VARCHAR(50) DEFAULT 'markdown', -- 'markdown', 'html', 'json'
  
  -- Variants for A/B
  variants JSONB DEFAULT '[]',
  -- [{ id, name, content, performance_data }]
  
  -- Status
  status asset_status DEFAULT 'draft',
  
  -- Distribution
  distribution_links JSONB DEFAULT '{}',
  -- { platform: url }
  
  -- Performance
  performance_data JSONB DEFAULT '{}',
  
  -- Meta
  tags JSONB DEFAULT '[]',
  version INTEGER DEFAULT 1,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  approved_at TIMESTAMPTZ,
  deployed_at TIMESTAMPTZ
);

-- =====================================================
-- METRICS TABLE - Tracked metrics with RAG
-- =====================================================
CREATE TABLE IF NOT EXISTS public.metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- Scope
  scope_type VARCHAR(50) NOT NULL, -- 'channel', 'move', 'protocol', 'campaign', 'icp', 'business'
  scope_id UUID, -- Reference to the scoped entity
  
  -- Metric definition
  metric_name VARCHAR(100) NOT NULL,
  metric_category VARCHAR(100),
  
  -- Value
  value DECIMAL(15,4),
  unit VARCHAR(50),
  
  -- Period
  period_start TIMESTAMPTZ,
  period_end TIMESTAMPTZ,
  
  -- Targets and RAG
  target_value DECIMAL(15,4),
  rag_status rag_status DEFAULT 'unknown',
  rag_thresholds JSONB DEFAULT '{}',
  -- { green_above, red_below }
  
  -- Source
  source VARCHAR(100), -- 'manual', 'integration_xyz', etc.
  raw_data JSONB DEFAULT '{}',
  
  -- Timestamps
  recorded_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- SPIKES TABLE - 30-day sprint definitions
-- =====================================================
CREATE TABLE IF NOT EXISTS public.spikes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- Identity
  name VARCHAR(200) NOT NULL,
  
  -- Type and targeting
  spike_type spike_type NOT NULL,
  goal goal_type NOT NULL,
  demand_source demand_source_type,
  
  -- ICP targeting
  primary_icp_id UUID REFERENCES public.icps(id) ON DELETE SET NULL,
  secondary_icp_ids UUID[] DEFAULT '{}',
  
  -- Barriers and protocols
  barriers barrier_type[] DEFAULT '{}',
  protocols protocol_type[] DEFAULT '{}',
  
  -- Targets
  targets JSONB NOT NULL DEFAULT '{}',
  -- { pipeline_value, opps, cac_ceiling, max_payback_months }
  
  -- Time window
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  
  -- Linked entities
  campaign_id UUID REFERENCES public.campaigns(id) ON DELETE SET NULL,
  move_ids UUID[] DEFAULT '{}',
  
  -- Status
  status spike_status DEFAULT 'configuring',
  
  -- Progress tracking
  current_day INTEGER DEFAULT 0,
  progress_percentage INTEGER DEFAULT 0,
  
  -- RAG
  rag_status rag_status DEFAULT 'unknown',
  rag_details JSONB DEFAULT '{}',
  
  -- Results (post-mortem)
  results JSONB DEFAULT '{}',
  learnings JSONB DEFAULT '[]',
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

-- =====================================================
-- GUARDRAILS TABLE - CAC/payback rules and kill-switch
-- =====================================================
CREATE TABLE IF NOT EXISTS public.guardrails (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- Scope
  spike_id UUID REFERENCES public.spikes(id) ON DELETE CASCADE,
  campaign_id UUID REFERENCES public.campaigns(id) ON DELETE CASCADE,
  icp_id UUID REFERENCES public.icps(id) ON DELETE SET NULL,
  
  -- Rule definition
  name VARCHAR(200) NOT NULL,
  description TEXT,
  
  metric VARCHAR(100) NOT NULL,
  -- 'cac_blended_7d', 'payback_months', 'conversion_rate', etc.
  
  operator VARCHAR(20) NOT NULL,
  -- 'greater_than', 'less_than', 'equals', 'between'
  
  threshold DECIMAL(15,4) NOT NULL,
  threshold_upper DECIMAL(15,4), -- For 'between' operator
  
  -- Action
  action guardrail_action DEFAULT 'alert_only',
  
  -- Status
  is_active BOOLEAN DEFAULT true,
  is_triggered BOOLEAN DEFAULT false,
  last_triggered_at TIMESTAMPTZ,
  trigger_count INTEGER DEFAULT 0,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- GUARDRAIL EVENTS TABLE - Kill-switch event log
-- =====================================================
CREATE TABLE IF NOT EXISTS public.guardrail_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  guardrail_id UUID NOT NULL REFERENCES public.guardrails(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- Event details
  event_type VARCHAR(50) NOT NULL, -- 'triggered', 'resolved', 'overridden', 'paused'
  
  metric_value DECIMAL(15,4),
  threshold_value DECIMAL(15,4),
  
  -- Action taken
  action_taken VARCHAR(100),
  affected_entities JSONB DEFAULT '{}',
  -- { campaigns[], moves[], assets[] }
  
  -- Override info
  override_reason TEXT,
  overridden_by UUID REFERENCES auth.users(id),
  
  -- Timestamps
  occurred_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- EXPERIMENT LEDGER TABLE - Track bets and experiments
-- =====================================================
CREATE TABLE IF NOT EXISTS public.experiments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- Association
  spike_id UUID REFERENCES public.spikes(id) ON DELETE SET NULL,
  campaign_id UUID REFERENCES public.campaigns(id) ON DELETE SET NULL,
  move_id UUID REFERENCES public.moves(id) ON DELETE SET NULL,
  
  -- Identity
  name VARCHAR(200) NOT NULL,
  hypothesis TEXT,
  
  -- Bet type
  bet_type VARCHAR(50) DEFAULT 'growth', -- 'core', 'growth', 'frontier'
  
  -- Scoring
  expected_impact INTEGER DEFAULT 50,
  probability INTEGER DEFAULT 50,
  effort INTEGER DEFAULT 50,
  ev_score DECIMAL(5,2),
  
  -- Status
  status VARCHAR(50) DEFAULT 'planned', -- 'planned', 'running', 'completed', 'killed'
  
  -- Results
  actual_outcome TEXT,
  learnings TEXT,
  promoted_to_baseline BOOLEAN DEFAULT false,
  
  -- Timestamps
  started_at TIMESTAMPTZ,
  ended_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- INDEXES
-- =====================================================

-- ICPs
CREATE INDEX IF NOT EXISTS idx_icps_user_id ON public.icps(user_id);
CREATE INDEX IF NOT EXISTS idx_icps_intake_id ON public.icps(intake_id);
CREATE INDEX IF NOT EXISTS idx_icps_is_selected ON public.icps(is_selected);
CREATE INDEX IF NOT EXISTS idx_icps_fit_score ON public.icps(fit_score DESC);

-- Cohorts
CREATE INDEX IF NOT EXISTS idx_cohorts_user_id ON public.cohorts(user_id);
CREATE INDEX IF NOT EXISTS idx_cohorts_icp_id ON public.cohorts(icp_id);

-- Barriers
CREATE INDEX IF NOT EXISTS idx_barriers_user_id ON public.barriers(user_id);
CREATE INDEX IF NOT EXISTS idx_barriers_icp_id ON public.barriers(icp_id);
CREATE INDEX IF NOT EXISTS idx_barriers_type ON public.barriers(barrier_type);

-- Campaigns
CREATE INDEX IF NOT EXISTS idx_campaigns_user_id ON public.campaigns(user_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON public.campaigns(status);
CREATE INDEX IF NOT EXISTS idx_campaigns_dates ON public.campaigns(start_date, end_date);

-- Moves
CREATE INDEX IF NOT EXISTS idx_moves_user_id ON public.moves(user_id);
CREATE INDEX IF NOT EXISTS idx_moves_campaign_id ON public.moves(campaign_id);
CREATE INDEX IF NOT EXISTS idx_moves_status ON public.moves(status);
CREATE INDEX IF NOT EXISTS idx_moves_spike_id ON public.moves(spike_id);

-- Assets
CREATE INDEX IF NOT EXISTS idx_assets_user_id ON public.assets(user_id);
CREATE INDEX IF NOT EXISTS idx_assets_move_id ON public.assets(move_id);
CREATE INDEX IF NOT EXISTS idx_assets_type ON public.assets(asset_type);
CREATE INDEX IF NOT EXISTS idx_assets_status ON public.assets(status);

-- Metrics
CREATE INDEX IF NOT EXISTS idx_metrics_user_id ON public.metrics(user_id);
CREATE INDEX IF NOT EXISTS idx_metrics_scope ON public.metrics(scope_type, scope_id);
CREATE INDEX IF NOT EXISTS idx_metrics_name ON public.metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_metrics_period ON public.metrics(period_start, period_end);

-- Spikes
CREATE INDEX IF NOT EXISTS idx_spikes_user_id ON public.spikes(user_id);
CREATE INDEX IF NOT EXISTS idx_spikes_status ON public.spikes(status);
CREATE INDEX IF NOT EXISTS idx_spikes_dates ON public.spikes(start_date, end_date);

-- Guardrails
CREATE INDEX IF NOT EXISTS idx_guardrails_user_id ON public.guardrails(user_id);
CREATE INDEX IF NOT EXISTS idx_guardrails_spike_id ON public.guardrails(spike_id);
CREATE INDEX IF NOT EXISTS idx_guardrails_is_active ON public.guardrails(is_active);

-- Experiments
CREATE INDEX IF NOT EXISTS idx_experiments_user_id ON public.experiments(user_id);
CREATE INDEX IF NOT EXISTS idx_experiments_spike_id ON public.experiments(spike_id);

-- =====================================================
-- ROW LEVEL SECURITY (RLS)
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE public.icps ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cohorts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.barriers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.protocols ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.move_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.moves ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.spikes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.guardrails ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.guardrail_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.experiments ENABLE ROW LEVEL SECURITY;

-- ICPs policies
CREATE POLICY "Users can view own ICPs" ON public.icps FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own ICPs" ON public.icps FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own ICPs" ON public.icps FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own ICPs" ON public.icps FOR DELETE USING (auth.uid() = user_id);

-- Cohorts policies
CREATE POLICY "Users can view own cohorts" ON public.cohorts FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own cohorts" ON public.cohorts FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own cohorts" ON public.cohorts FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own cohorts" ON public.cohorts FOR DELETE USING (auth.uid() = user_id);

-- Barriers policies
CREATE POLICY "Users can view own barriers" ON public.barriers FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own barriers" ON public.barriers FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own barriers" ON public.barriers FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own barriers" ON public.barriers FOR DELETE USING (auth.uid() = user_id);

-- Protocols are public read (system data)
CREATE POLICY "Anyone can view protocols" ON public.protocols FOR SELECT TO PUBLIC USING (true);

-- Move templates are public read (system data)
CREATE POLICY "Anyone can view move templates" ON public.move_templates FOR SELECT TO PUBLIC USING (true);

-- Campaigns policies
CREATE POLICY "Users can view own campaigns" ON public.campaigns FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own campaigns" ON public.campaigns FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own campaigns" ON public.campaigns FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own campaigns" ON public.campaigns FOR DELETE USING (auth.uid() = user_id);

-- Moves policies
CREATE POLICY "Users can view own moves" ON public.moves FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own moves" ON public.moves FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own moves" ON public.moves FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own moves" ON public.moves FOR DELETE USING (auth.uid() = user_id);

-- Assets policies
CREATE POLICY "Users can view own assets" ON public.assets FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own assets" ON public.assets FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own assets" ON public.assets FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own assets" ON public.assets FOR DELETE USING (auth.uid() = user_id);

-- Metrics policies
CREATE POLICY "Users can view own metrics" ON public.metrics FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own metrics" ON public.metrics FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own metrics" ON public.metrics FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own metrics" ON public.metrics FOR DELETE USING (auth.uid() = user_id);

-- Spikes policies
CREATE POLICY "Users can view own spikes" ON public.spikes FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own spikes" ON public.spikes FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own spikes" ON public.spikes FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own spikes" ON public.spikes FOR DELETE USING (auth.uid() = user_id);

-- Guardrails policies
CREATE POLICY "Users can view own guardrails" ON public.guardrails FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own guardrails" ON public.guardrails FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own guardrails" ON public.guardrails FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own guardrails" ON public.guardrails FOR DELETE USING (auth.uid() = user_id);

-- Guardrail events policies
CREATE POLICY "Users can view own guardrail events" ON public.guardrail_events FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own guardrail events" ON public.guardrail_events FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Experiments policies
CREATE POLICY "Users can view own experiments" ON public.experiments FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own experiments" ON public.experiments FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own experiments" ON public.experiments FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own experiments" ON public.experiments FOR DELETE USING (auth.uid() = user_id);

-- =====================================================
-- TRIGGERS - Updated at
-- =====================================================

-- Apply updated_at trigger to all relevant tables
CREATE TRIGGER update_icps_updated_at BEFORE UPDATE ON public.icps
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_cohorts_updated_at BEFORE UPDATE ON public.cohorts
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_barriers_updated_at BEFORE UPDATE ON public.barriers
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_protocols_updated_at BEFORE UPDATE ON public.protocols
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_move_templates_updated_at BEFORE UPDATE ON public.move_templates
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_campaigns_updated_at BEFORE UPDATE ON public.campaigns
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_moves_updated_at BEFORE UPDATE ON public.moves
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_assets_updated_at BEFORE UPDATE ON public.assets
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_spikes_updated_at BEFORE UPDATE ON public.spikes
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_guardrails_updated_at BEFORE UPDATE ON public.guardrails
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- =====================================================
-- SEED DATA: Protocols
-- =====================================================
INSERT INTO public.protocols (code, name, description, targets_barrier, trigger_conditions, required_asset_types, channel_rules, metric_targets, standard_checklist, display_order) VALUES
(
  'A_AUTHORITY_BLITZ',
  'Authority Blitz',
  'Build thought leadership and brand awareness through content-first demand creation. Targets prospects who don''t know you exist.',
  'OBSCURITY',
  '[{"metric": "brand_search_volume", "operator": "less_than", "threshold": 100, "description": "Low brand awareness"}]',
  '["pillar_content", "social_posts", "podcast_appearance", "keynote"]',
  '{"primary": ["linkedin_organic", "youtube", "podcast"], "secondary": ["twitter", "newsletter"], "exclude": ["cold_outbound"]}',
  '{"impressions": {"target": 100000, "unit": "monthly"}, "brand_search_lift": {"target": 30, "unit": "percentage"}}',
  '[{"task": "Create pillar content piece", "category": "content", "is_required": true}, {"task": "Slice into 30 micro-content pieces", "category": "content", "is_required": true}, {"task": "Schedule 3x daily posting", "category": "distribution", "is_required": true}]',
  1
),
(
  'B_TRUST_ANCHOR',
  'Trust Anchor',
  'Build credibility through social proof, case studies, and validation. Targets prospects who know you but don''t trust you enough to buy.',
  'RISK',
  '[{"metric": "demo_to_close_rate", "operator": "less_than", "threshold": 15, "description": "Low conversion from demo"}]',
  '["case_study", "comparison_page", "roi_calculator", "testimonial_wall", "security_page"]',
  '{"primary": ["website", "retargeting", "email"], "secondary": ["linkedin_ads"], "exclude": []}',
  '{"demo_conversion": {"target": 20, "unit": "percentage"}, "trust_score": {"target": 80, "unit": "nps"}}',
  '[{"task": "Create comparison vs competitors page", "category": "content", "is_required": true}, {"task": "Build ROI calculator", "category": "tools", "is_required": true}, {"task": "Collect 5 testimonials", "category": "social_proof", "is_required": true}]',
  2
),
(
  'C_COST_OF_INACTION',
  'Cost of Inaction',
  'Create urgency through fear of missing out and consequences of delay. Targets prospects stuck in evaluation paralysis.',
  'INERTIA',
  '[{"metric": "avg_sales_cycle", "operator": "greater_than", "threshold": 90, "description": "Long sales cycles"}]',
  '["wake_up_report", "competitor_move_alert", "deadline_campaign", "executive_briefing"]',
  '{"primary": ["abm_direct", "email", "linkedin_dm"], "secondary": ["retargeting"], "exclude": []}',
  '{"pipeline_velocity": {"target": 30, "unit": "percentage_improvement"}, "stalled_deal_reactivation": {"target": 20, "unit": "percentage"}}',
  '[{"task": "Create industry wake-up report", "category": "content", "is_required": true}, {"task": "Build cost of delay calculator", "category": "tools", "is_required": true}, {"task": "Launch time-bound offer", "category": "campaign", "is_required": false}]',
  3
),
(
  'D_HABIT_HARDCODE',
  'Habit Hard-Code',
  'Drive activation and habit formation for new users. Targets users who signed up but haven''t reached value.',
  'FRICTION',
  '[{"metric": "activation_rate", "operator": "less_than", "threshold": 40, "description": "Low activation rate"}]',
  '["onboarding_sequence", "quick_start_guide", "progress_tracker", "milestone_celebrations"]',
  '{"primary": ["in_app", "email", "push"], "secondary": ["sms"], "exclude": ["paid_ads"]}',
  '{"time_to_value": {"target": 3, "unit": "days"}, "activation_rate": {"target": 60, "unit": "percentage"}}',
  '[{"task": "Define activation event", "category": "analytics", "is_required": true}, {"task": "Create onboarding email sequence", "category": "lifecycle", "is_required": true}, {"task": "Add progress indicators", "category": "product", "is_required": true}]',
  4
),
(
  'E_ENTERPRISE_WEDGE',
  'Enterprise Wedge',
  'Expand within accounts and drive enterprise deals. Targets power users ready for expansion.',
  'CAPACITY',
  '[{"metric": "usage_at_limit", "operator": "greater_than", "threshold": 80, "description": "Users hitting limits"}]',
  '["business_case_pdf", "qbr_deck", "expansion_proposal", "champion_toolkit"]',
  '{"primary": ["customer_success", "in_app", "email"], "secondary": ["executive_outreach"], "exclude": []}',
  '{"expansion_rate": {"target": 25, "unit": "percentage"}, "nrr": {"target": 115, "unit": "percentage"}}',
  '[{"task": "Identify expansion signals", "category": "analytics", "is_required": true}, {"task": "Create boss-forwardable business case", "category": "sales_enablement", "is_required": true}, {"task": "Build QBR deck template", "category": "customer_success", "is_required": true}]',
  5
),
(
  'F_CHURN_INTERCEPT',
  'Churn Intercept',
  'Prevent and recover churning customers through intervention. Targets at-risk accounts showing churn signals.',
  'ATROPHY',
  '[{"metric": "health_score", "operator": "less_than", "threshold": 40, "description": "Low health score"}]',
  '["loss_aversion_email", "pause_plan_page", "win_back_sequence", "exit_survey"]',
  '{"primary": ["email", "in_app", "phone"], "secondary": ["direct_mail"], "exclude": []}',
  '{"save_rate": {"target": 30, "unit": "percentage"}, "churn_rate": {"target": 5, "unit": "percentage_max"}}',
  '[{"task": "Set up churn prediction model", "category": "analytics", "is_required": true}, {"task": "Create loss aversion messaging", "category": "lifecycle", "is_required": true}, {"task": "Implement pause plan option", "category": "product", "is_required": true}]',
  6
)
ON CONFLICT (code) DO UPDATE SET
  name = EXCLUDED.name,
  description = EXCLUDED.description,
  targets_barrier = EXCLUDED.targets_barrier,
  trigger_conditions = EXCLUDED.trigger_conditions,
  required_asset_types = EXCLUDED.required_asset_types,
  channel_rules = EXCLUDED.channel_rules,
  metric_targets = EXCLUDED.metric_targets,
  standard_checklist = EXCLUDED.standard_checklist,
  display_order = EXCLUDED.display_order;

-- =====================================================
-- SEED DATA: Move Templates
-- =====================================================
INSERT INTO public.move_templates (slug, name, description, protocol_type, barrier_type, funnel_stage, required_inputs, channels, task_template, asset_requirements, success_metrics, base_impact_score, base_effort_score, display_order) VALUES
(
  'content-waterfall',
  'Content Waterfall',
  'Create one pillar piece and atomize it into 30+ pieces of micro-content for sustained presence.',
  'A_AUTHORITY_BLITZ',
  'OBSCURITY',
  'tofu',
  '[{"key": "pillar_topic", "label": "Pillar Topic", "type": "text", "required": true}, {"key": "target_icp", "label": "Target ICP", "type": "select", "required": true}]',
  '["linkedin_organic", "youtube_shorts", "twitter", "newsletter"]',
  '[{"task": "Research and outline pillar topic", "category": "planning", "estimated_hours": 4}, {"task": "Create pillar content (webinar/guide)", "category": "creation", "estimated_hours": 12}, {"task": "Extract 30 micro-content pieces", "category": "creation", "estimated_hours": 6}, {"task": "Schedule 3x daily for 2 weeks", "category": "distribution", "estimated_hours": 2}]',
  '[{"type": "pillar_content", "quantity": 1, "description": "Main webinar/guide"}, {"type": "social_posts", "quantity": 30, "description": "Micro-content pieces"}]',
  '[{"metric": "impressions", "target": 50000, "unit": "total"}, {"metric": "engagement_rate", "target": 3, "unit": "percentage"}]',
  75,
  60,
  1
),
(
  'validation-loop',
  'Validation Loop',
  'Build trust through comparison pages, ROI calculators, and social proof deployment.',
  'B_TRUST_ANCHOR',
  'RISK',
  'mofu',
  '[{"key": "competitors", "label": "Key Competitors", "type": "multiselect", "required": true}, {"key": "proof_points", "label": "Proof Points", "type": "textarea", "required": true}]',
  '["website", "retargeting", "email"]',
  '[{"task": "Create us vs them comparison", "category": "content", "estimated_hours": 8}, {"task": "Build interactive ROI calculator", "category": "tools", "estimated_hours": 16}, {"task": "Deploy proof wall on site", "category": "website", "estimated_hours": 4}, {"task": "Set up retargeting to pricing visitors", "category": "paid", "estimated_hours": 3}]',
  '[{"type": "comparison_page", "quantity": 1, "description": "Us vs competitors"}, {"type": "roi_calculator", "quantity": 1, "description": "Interactive calculator"}, {"type": "retargeting_ads", "quantity": 3, "description": "Trust-focused creatives"}]',
  '[{"metric": "demo_conversion_rate", "target": 20, "unit": "percentage"}, {"metric": "pricing_page_conversion", "target": 5, "unit": "percentage"}]',
  80,
  70,
  2
),
(
  'spear-attack',
  'Spear Attack',
  'ABM-style targeted outreach with personalized wake-up reports and direct engagement.',
  'C_COST_OF_INACTION',
  'INERTIA',
  'bofu',
  '[{"key": "target_accounts", "label": "Target Accounts", "type": "multiselect", "required": true}, {"key": "trigger_event", "label": "Trigger Event", "type": "text", "required": true}]',
  '["linkedin_dm", "email", "direct_mail"]',
  '[{"task": "Research target accounts", "category": "research", "estimated_hours": 8}, {"task": "Create personalized audit reports", "category": "content", "estimated_hours": 12}, {"task": "Record personalized Loom videos", "category": "outreach", "estimated_hours": 6}, {"task": "Execute multi-touch sequence", "category": "outreach", "estimated_hours": 4}]',
  '[{"type": "account_audit", "quantity": 10, "description": "Per-account analysis"}, {"type": "loom_videos", "quantity": 10, "description": "Personalized videos"}, {"type": "email_sequence", "quantity": 1, "description": "5-touch sequence"}]',
  '[{"metric": "reply_rate", "target": 15, "unit": "percentage"}, {"metric": "meetings_booked", "target": 5, "unit": "count"}]',
  85,
  80,
  3
),
(
  'facilitator-nudge',
  'Facilitator Nudge',
  'Guide new users to activation through progressive onboarding and milestone celebrations.',
  'D_HABIT_HARDCODE',
  'FRICTION',
  'lifecycle',
  '[{"key": "activation_event", "label": "Activation Event", "type": "text", "required": true}, {"key": "time_to_value_target", "label": "Time to Value Target (days)", "type": "number", "required": true}]',
  '["in_app", "email", "push"]',
  '[{"task": "Map user journey to activation", "category": "analytics", "estimated_hours": 4}, {"task": "Create onboarding email sequence", "category": "lifecycle", "estimated_hours": 8}, {"task": "Build in-app progress tracker", "category": "product", "estimated_hours": 12}, {"task": "Set up milestone celebrations", "category": "product", "estimated_hours": 4}]',
  '[{"type": "email_sequence", "quantity": 1, "description": "7-day onboarding"}, {"type": "in_app_guides", "quantity": 5, "description": "Interactive walkthroughs"}, {"type": "push_notifications", "quantity": 3, "description": "Nudge sequences"}]',
  '[{"metric": "activation_rate", "target": 60, "unit": "percentage"}, {"metric": "time_to_value", "target": 3, "unit": "days"}]',
  70,
  65,
  4
),
(
  'champions-armory',
  'Champion''s Armory',
  'Equip internal champions with tools to sell internally and drive expansion.',
  'E_ENTERPRISE_WEDGE',
  'CAPACITY',
  'lifecycle',
  '[{"key": "expansion_signals", "label": "Expansion Signals", "type": "multiselect", "required": true}, {"key": "avg_deal_size", "label": "Average Deal Size", "type": "number", "required": true}]',
  '["customer_success", "email", "in_app"]',
  '[{"task": "Identify expansion-ready accounts", "category": "analytics", "estimated_hours": 4}, {"task": "Create business case PDF generator", "category": "tools", "estimated_hours": 16}, {"task": "Build QBR deck template", "category": "sales_enablement", "estimated_hours": 8}, {"task": "Launch expansion outreach", "category": "customer_success", "estimated_hours": 6}]',
  '[{"type": "business_case_pdf", "quantity": 1, "description": "Boss-forwardable doc"}, {"type": "qbr_deck", "quantity": 1, "description": "Review template"}, {"type": "upgrade_prompt", "quantity": 1, "description": "In-app upgrade flow"}]',
  '[{"metric": "expansion_rate", "target": 25, "unit": "percentage"}, {"metric": "nrr", "target": 115, "unit": "percentage"}]',
  90,
  75,
  5
),
(
  'churn-intercept-sequence',
  'Churn Intercept Sequence',
  'Intervene with at-risk customers before they cancel with loss aversion and save offers.',
  'F_CHURN_INTERCEPT',
  'ATROPHY',
  'lifecycle',
  '[{"key": "churn_signals", "label": "Churn Signals", "type": "multiselect", "required": true}, {"key": "pause_offer", "label": "Pause Offer Available", "type": "boolean", "required": true}]',
  '["email", "in_app", "phone"]',
  '[{"task": "Set up churn prediction alerts", "category": "analytics", "estimated_hours": 8}, {"task": "Create loss aversion email sequence", "category": "lifecycle", "estimated_hours": 6}, {"task": "Build pause plan page", "category": "product", "estimated_hours": 8}, {"task": "Train CS team on save playbook", "category": "enablement", "estimated_hours": 4}]',
  '[{"type": "email_sequence", "quantity": 1, "description": "5-touch save sequence"}, {"type": "pause_page", "quantity": 1, "description": "Alternative to cancel"}, {"type": "exit_survey", "quantity": 1, "description": "Feedback collection"}]',
  '[{"metric": "save_rate", "target": 30, "unit": "percentage"}, {"metric": "churn_rate", "target": 5, "unit": "percentage_max"}]',
  85,
  60,
  6
)
ON CONFLICT (slug) DO UPDATE SET
  name = EXCLUDED.name,
  description = EXCLUDED.description,
  protocol_type = EXCLUDED.protocol_type,
  barrier_type = EXCLUDED.barrier_type,
  funnel_stage = EXCLUDED.funnel_stage,
  required_inputs = EXCLUDED.required_inputs,
  channels = EXCLUDED.channels,
  task_template = EXCLUDED.task_template,
  asset_requirements = EXCLUDED.asset_requirements,
  success_metrics = EXCLUDED.success_metrics,
  base_impact_score = EXCLUDED.base_impact_score,
  base_effort_score = EXCLUDED.base_effort_score,
  display_order = EXCLUDED.display_order;

-- =====================================================
-- GRANT PERMISSIONS
-- =====================================================

-- Service role has full access
GRANT ALL ON public.icps TO service_role;
GRANT ALL ON public.cohorts TO service_role;
GRANT ALL ON public.barriers TO service_role;
GRANT ALL ON public.protocols TO service_role;
GRANT ALL ON public.move_templates TO service_role;
GRANT ALL ON public.campaigns TO service_role;
GRANT ALL ON public.moves TO service_role;
GRANT ALL ON public.assets TO service_role;
GRANT ALL ON public.metrics TO service_role;
GRANT ALL ON public.spikes TO service_role;
GRANT ALL ON public.guardrails TO service_role;
GRANT ALL ON public.guardrail_events TO service_role;
GRANT ALL ON public.experiments TO service_role;

-- Authenticated users have restricted access (RLS handles specifics)
GRANT SELECT, INSERT, UPDATE, DELETE ON public.icps TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.cohorts TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.barriers TO authenticated;
GRANT SELECT ON public.protocols TO authenticated;
GRANT SELECT ON public.move_templates TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.campaigns TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.moves TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.assets TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.metrics TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.spikes TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.guardrails TO authenticated;
GRANT SELECT, INSERT ON public.guardrail_events TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.experiments TO authenticated;

-- =====================================================
-- SUCCESS MESSAGE
-- =====================================================
DO $$ 
BEGIN
    RAISE NOTICE 'Core platform migration completed successfully!';
    RAISE NOTICE 'Created tables: icps, cohorts, barriers, protocols, move_templates, campaigns, moves, assets, metrics, spikes, guardrails, guardrail_events, experiments';
    RAISE NOTICE 'Seeded: 6 protocols, 6 move templates';
END $$;

