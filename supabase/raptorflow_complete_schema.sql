-- =====================================================
-- RAPTORFLOW COMPLETE DATABASE SCHEMA
-- Run this AFTER deleting all existing tables
-- Production-ready schema with all tables, RLS, and seed data
-- =====================================================

-- ===========================================
-- SECTION 1: EXTENSIONS
-- ===========================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ===========================================
-- SECTION 2: ENUMS
-- ===========================================

-- Barrier types (the 6 barriers in the funnel)
CREATE TYPE barrier_type AS ENUM (
  'OBSCURITY',   -- Not known, low visibility
  'RISK',        -- Known but not trusted
  'INERTIA',     -- Trusted but not urgent
  'FRICTION',    -- Signed up but not activated
  'CAPACITY',    -- Active but not expanding
  'ATROPHY'      -- Churning or at risk
);

-- Protocol types (the 6 protocols to overcome barriers)
CREATE TYPE protocol_type AS ENUM (
  'A_AUTHORITY_BLITZ',
  'B_TRUST_ANCHOR',
  'C_COST_OF_INACTION',
  'D_HABIT_HARDCODE',
  'E_ENTERPRISE_WEDGE',
  'F_CHURN_INTERCEPT'
);

-- Goal types for campaigns
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

-- RAG status (Red/Amber/Green)
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

-- ===========================================
-- SECTION 3: CORE TABLES
-- ===========================================

-- PROFILES TABLE (extends auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
  id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  email TEXT,
  full_name TEXT,
  avatar_url TEXT,
  
  -- Plan & Subscription
  plan TEXT DEFAULT 'none' CHECK (plan IN ('none', 'ascent', 'glide', 'soar')),
  plan_status TEXT DEFAULT 'inactive' CHECK (plan_status IN ('inactive', 'active', 'expired', 'cancelled')),
  plan_started_at TIMESTAMPTZ,
  plan_expires_at TIMESTAMPTZ,
  
  -- Onboarding
  onboarding_completed BOOLEAN DEFAULT FALSE,
  onboarding_completed_at TIMESTAMPTZ,
  
  -- Payment info
  payment_status TEXT DEFAULT 'pending' CHECK (payment_status IN ('pending', 'completed', 'failed', 'refunded')),
  last_payment_id TEXT,
  last_payment_amount INTEGER,
  last_payment_date TIMESTAMPTZ,
  
  -- PhonePe specific
  phonepe_merchant_user_id TEXT,
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- PAYMENTS TABLE (payment history)
CREATE TABLE IF NOT EXISTS public.payments (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
  
  -- Payment details
  amount INTEGER NOT NULL,
  currency TEXT DEFAULT 'INR',
  plan TEXT NOT NULL CHECK (plan IN ('ascent', 'glide', 'soar')),
  
  -- PhonePe transaction details
  phonepe_transaction_id TEXT,
  phonepe_merchant_transaction_id TEXT UNIQUE,
  phonepe_payment_instrument_type TEXT,
  
  -- Status
  status TEXT DEFAULT 'initiated' CHECK (status IN ('initiated', 'pending', 'success', 'failed', 'refunded')),
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  
  -- Response data
  response_code TEXT,
  response_message TEXT,
  raw_response JSONB
);

-- PLAN PRICES (reference table)
CREATE TABLE IF NOT EXISTS public.plan_prices (
  plan TEXT PRIMARY KEY CHECK (plan IN ('ascent', 'glide', 'soar')),
  price_inr INTEGER NOT NULL,
  price_paise INTEGER NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  features JSONB,
  duration_days INTEGER DEFAULT 30,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- SECTION 4: ONBOARDING TABLES
-- ===========================================

-- Onboarding intake table
CREATE TABLE IF NOT EXISTS public.onboarding_intake (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Step 1: Positioning
    positioning JSONB DEFAULT '{}',
    positioning_derived JSONB DEFAULT '{}',
    
    -- Step 2: Company
    company JSONB DEFAULT '{}',
    company_enriched JSONB DEFAULT '{}',
    
    -- Step 3: Product
    product JSONB DEFAULT '{}',
    product_derived JSONB DEFAULT '{}',
    
    -- Step 4: Market
    market JSONB DEFAULT '{}',
    market_system_view JSONB DEFAULT '{}',
    
    -- Step 5: Strategy
    strategy JSONB DEFAULT '{}',
    strategy_derived JSONB DEFAULT '{}',
    
    -- Generated outputs
    icps JSONB DEFAULT '[]',
    war_plan JSONB DEFAULT '{}',
    metrics_framework JSONB DEFAULT '{}',
    
    -- Progress tracking
    current_step INTEGER DEFAULT 1,
    completed_steps INTEGER[] DEFAULT '{}',
    
    -- Mode and ownership
    mode VARCHAR(20) DEFAULT 'self-service',
    sales_rep_id UUID REFERENCES auth.users(id),
    share_token VARCHAR(100) UNIQUE,
    
    -- Payment tracking
    selected_plan VARCHAR(50),
    payment_status VARCHAR(20) DEFAULT 'pending',
    payment_completed_at TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agent execution logs
CREATE TABLE IF NOT EXISTS public.agent_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    intake_id UUID REFERENCES public.onboarding_intake(id) ON DELETE CASCADE,
    agent_name VARCHAR(100) NOT NULL,
    input JSONB NOT NULL,
    output JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration_ms INTEGER,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Shared links for sales-assisted onboarding
CREATE TABLE IF NOT EXISTS public.shared_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    intake_id UUID REFERENCES public.onboarding_intake(id) ON DELETE CASCADE,
    token VARCHAR(100) UNIQUE NOT NULL,
    sales_rep_id UUID REFERENCES auth.users(id),
    expires_at TIMESTAMPTZ,
    accessed_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMPTZ,
    payment_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- SECTION 5: PLATFORM TABLES
-- ===========================================

-- ICPS TABLE - 6D Intelligence Profiles
CREATE TABLE IF NOT EXISTS public.icps (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  intake_id UUID REFERENCES public.onboarding_intake(id) ON DELETE SET NULL,
  
  -- Core identity
  label VARCHAR(100) NOT NULL,
  slug VARCHAR(100),
  summary TEXT,
  
  -- 6D Dimensions
  firmographics JSONB DEFAULT '{}',
  technographics JSONB DEFAULT '{}',
  psychographics JSONB DEFAULT '{}',
  behavioral_triggers JSONB DEFAULT '[]',
  buying_committee JSONB DEFAULT '[]',
  category_context JSONB DEFAULT '{}',
  
  -- Scoring
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
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- COHORTS TABLE - Live segments
CREATE TABLE IF NOT EXISTS public.cohorts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    
    -- 6D Profile Data
    firmographics JSONB DEFAULT '{}',
    psychographics JSONB DEFAULT '{}',
    behavioral_triggers JSONB DEFAULT '[]',
    buying_committee JSONB DEFAULT '[]',
    category_context JSONB DEFAULT '{}',
    
    -- Interest Tags for Radar
    interest_tags JSONB DEFAULT '[]',
    tags_count INTEGER DEFAULT 0,
    
    -- Scoring
    fit_score INTEGER DEFAULT 0,
    fit_reasoning TEXT,
    messaging_angle TEXT,
    qualification_questions JSONB DEFAULT '[]',
    
    -- Radar tracking
    last_radar_scan TIMESTAMPTZ,
    radar_opportunities_found INTEGER DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- BARRIERS TABLE
CREATE TABLE IF NOT EXISTS public.barriers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  icp_id UUID REFERENCES public.icps(id) ON DELETE CASCADE,
  cohort_id UUID REFERENCES public.cohorts(id) ON DELETE CASCADE,
  
  barrier_type barrier_type NOT NULL,
  confidence DECIMAL(3,2) DEFAULT 0.5 CHECK (confidence >= 0 AND confidence <= 1),
  
  supporting_signals JSONB DEFAULT '[]',
  metrics_snapshot JSONB DEFAULT '{}',
  analysis_notes TEXT,
  recommended_protocols protocol_type[] DEFAULT '{}',
  
  diagnosed_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT unique_active_barrier UNIQUE (icp_id, cohort_id, barrier_type)
);

-- PROTOCOLS TABLE
CREATE TABLE IF NOT EXISTS public.protocols (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code protocol_type NOT NULL UNIQUE,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  targets_barrier barrier_type NOT NULL,
  trigger_conditions JSONB DEFAULT '[]',
  required_asset_types JSONB DEFAULT '[]',
  channel_rules JSONB DEFAULT '{}',
  metric_targets JSONB DEFAULT '{}',
  standard_checklist JSONB DEFAULT '[]',
  is_active BOOLEAN DEFAULT true,
  display_order INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- MOVE TEMPLATES TABLE
CREATE TABLE IF NOT EXISTS public.move_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug VARCHAR(100) NOT NULL UNIQUE,
  name VARCHAR(200) NOT NULL,
  description TEXT,
  protocol_type protocol_type NOT NULL,
  barrier_type barrier_type NOT NULL,
  funnel_stage VARCHAR(50),
  required_inputs JSONB DEFAULT '[]',
  channels JSONB DEFAULT '[]',
  task_template JSONB DEFAULT '[]',
  asset_requirements JSONB DEFAULT '[]',
  automation_hooks JSONB DEFAULT '{}',
  success_metrics JSONB DEFAULT '[]',
  base_impact_score INTEGER DEFAULT 50,
  base_effort_score INTEGER DEFAULT 50,
  is_active BOOLEAN DEFAULT true,
  display_order INTEGER DEFAULT 0,
  tags JSONB DEFAULT '[]',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- CAMPAIGNS TABLE
CREATE TABLE IF NOT EXISTS public.campaigns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  name VARCHAR(200) NOT NULL,
  description TEXT,
  goal goal_type NOT NULL,
  demand_source demand_source_type NOT NULL,
  persuasion_axis persuasion_axis_type NOT NULL,
  icp_ids UUID[] DEFAULT '{}',
  cohort_ids UUID[] DEFAULT '{}',
  primary_barriers barrier_type[] DEFAULT '{}',
  protocols protocol_type[] DEFAULT '{}',
  start_date DATE,
  end_date DATE,
  budget_plan JSONB DEFAULT '{}',
  targets JSONB DEFAULT '{}',
  status campaign_status DEFAULT 'draft',
  rag_status rag_status DEFAULT 'unknown',
  rag_details JSONB DEFAULT '{}',
  created_from_spike UUID,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- MOVES TABLE
CREATE TABLE IF NOT EXISTS public.moves (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  campaign_id UUID REFERENCES public.campaigns(id) ON DELETE CASCADE,
  spike_id UUID,
  template_id UUID REFERENCES public.move_templates(id) ON DELETE SET NULL,
  name VARCHAR(200) NOT NULL,
  description TEXT,
  protocol protocol_type,
  icp_id UUID REFERENCES public.icps(id) ON DELETE SET NULL,
  channels JSONB DEFAULT '[]',
  tasks JSONB DEFAULT '[]',
  impact_score INTEGER DEFAULT 50,
  effort_score INTEGER DEFAULT 50,
  ev_score DECIMAL(5,2),
  status move_status DEFAULT 'planned',
  progress_percentage INTEGER DEFAULT 0,
  rag_status rag_status DEFAULT 'unknown',
  rag_details JSONB DEFAULT '{}',
  kpis JSONB DEFAULT '{}',
  planned_start DATE,
  planned_end DATE,
  actual_start TIMESTAMPTZ,
  actual_end TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ASSETS TABLE (Muse)
CREATE TABLE IF NOT EXISTS public.assets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  move_id UUID REFERENCES public.moves(id) ON DELETE SET NULL,
  campaign_id UUID REFERENCES public.campaigns(id) ON DELETE SET NULL,
  icp_id UUID REFERENCES public.icps(id) ON DELETE SET NULL,
  protocol protocol_type,
  name VARCHAR(300) NOT NULL,
  asset_type VARCHAR(100) NOT NULL,
  content TEXT,
  content_format VARCHAR(50) DEFAULT 'markdown',
  variants JSONB DEFAULT '[]',
  status asset_status DEFAULT 'draft',
  distribution_links JSONB DEFAULT '{}',
  performance_data JSONB DEFAULT '{}',
  tags JSONB DEFAULT '[]',
  version INTEGER DEFAULT 1,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  approved_at TIMESTAMPTZ,
  deployed_at TIMESTAMPTZ
);

-- METRICS TABLE
CREATE TABLE IF NOT EXISTS public.metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  scope_type VARCHAR(50) NOT NULL,
  scope_id UUID,
  metric_name VARCHAR(100) NOT NULL,
  metric_category VARCHAR(100),
  value DECIMAL(15,4),
  unit VARCHAR(50),
  period_start TIMESTAMPTZ,
  period_end TIMESTAMPTZ,
  target_value DECIMAL(15,4),
  rag_status rag_status DEFAULT 'unknown',
  rag_thresholds JSONB DEFAULT '{}',
  source VARCHAR(100),
  raw_data JSONB DEFAULT '{}',
  recorded_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- SPIKES TABLE (30-day sprints)
CREATE TABLE IF NOT EXISTS public.spikes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  name VARCHAR(200) NOT NULL,
  spike_type spike_type NOT NULL,
  goal goal_type NOT NULL,
  demand_source demand_source_type,
  primary_icp_id UUID REFERENCES public.icps(id) ON DELETE SET NULL,
  secondary_icp_ids UUID[] DEFAULT '{}',
  barriers barrier_type[] DEFAULT '{}',
  protocols protocol_type[] DEFAULT '{}',
  targets JSONB NOT NULL DEFAULT '{}',
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  campaign_id UUID REFERENCES public.campaigns(id) ON DELETE SET NULL,
  move_ids UUID[] DEFAULT '{}',
  status spike_status DEFAULT 'configuring',
  current_day INTEGER DEFAULT 0,
  progress_percentage INTEGER DEFAULT 0,
  rag_status rag_status DEFAULT 'unknown',
  rag_details JSONB DEFAULT '{}',
  results JSONB DEFAULT '{}',
  learnings JSONB DEFAULT '[]',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

-- GUARDRAILS TABLE
CREATE TABLE IF NOT EXISTS public.guardrails (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  spike_id UUID REFERENCES public.spikes(id) ON DELETE CASCADE,
  campaign_id UUID REFERENCES public.campaigns(id) ON DELETE CASCADE,
  icp_id UUID REFERENCES public.icps(id) ON DELETE SET NULL,
  name VARCHAR(200) NOT NULL,
  description TEXT,
  metric VARCHAR(100) NOT NULL,
  operator VARCHAR(20) NOT NULL,
  threshold DECIMAL(15,4) NOT NULL,
  threshold_upper DECIMAL(15,4),
  action guardrail_action DEFAULT 'alert_only',
  is_active BOOLEAN DEFAULT true,
  is_triggered BOOLEAN DEFAULT false,
  last_triggered_at TIMESTAMPTZ,
  trigger_count INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- GUARDRAIL EVENTS TABLE
CREATE TABLE IF NOT EXISTS public.guardrail_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  guardrail_id UUID NOT NULL REFERENCES public.guardrails(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  event_type VARCHAR(50) NOT NULL,
  metric_value DECIMAL(15,4),
  threshold_value DECIMAL(15,4),
  action_taken VARCHAR(100),
  affected_entities JSONB DEFAULT '{}',
  override_reason TEXT,
  overridden_by UUID REFERENCES auth.users(id),
  occurred_at TIMESTAMPTZ DEFAULT NOW()
);

-- EXPERIMENTS TABLE
CREATE TABLE IF NOT EXISTS public.experiments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  spike_id UUID REFERENCES public.spikes(id) ON DELETE SET NULL,
  campaign_id UUID REFERENCES public.campaigns(id) ON DELETE SET NULL,
  move_id UUID REFERENCES public.moves(id) ON DELETE SET NULL,
  name VARCHAR(200) NOT NULL,
  hypothesis TEXT,
  bet_type VARCHAR(50) DEFAULT 'growth',
  expected_impact INTEGER DEFAULT 50,
  probability INTEGER DEFAULT 50,
  effort INTEGER DEFAULT 50,
  ev_score DECIMAL(5,2),
  status VARCHAR(50) DEFAULT 'planned',
  actual_outcome TEXT,
  learnings TEXT,
  promoted_to_baseline BOOLEAN DEFAULT false,
  started_at TIMESTAMPTZ,
  ended_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RADAR OPPORTUNITIES TABLE
CREATE TABLE IF NOT EXISTS public.radar_opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    cohort_id UUID REFERENCES public.cohorts(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    trend_type VARCHAR(50),
    relevance_score INTEGER DEFAULT 0,
    urgency VARCHAR(50),
    matching_tags JSONB DEFAULT '[]',
    content_angles JSONB DEFAULT '[]',
    risk_level VARCHAR(50) DEFAULT 'safe',
    risk_notes TEXT,
    sources JSONB DEFAULT '[]',
    peak_window VARCHAR(255),
    decay_estimate VARCHAR(255),
    status VARCHAR(50) DEFAULT 'new',
    actioned_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

-- CONTENT IDEAS TABLE
CREATE TABLE IF NOT EXISTS public.content_ideas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    opportunity_id UUID REFERENCES public.radar_opportunities(id) ON DELETE SET NULL,
    cohort_id UUID REFERENCES public.cohorts(id) ON DELETE SET NULL,
    headline VARCHAR(500),
    subheadline VARCHAR(500),
    body_copy TEXT,
    call_to_action VARCHAR(255),
    hashtags JSONB DEFAULT '[]',
    visual_concept TEXT,
    visual_style VARCHAR(50),
    color_suggestions JSONB DEFAULT '[]',
    variations JSONB DEFAULT '[]',
    format VARCHAR(50),
    platform VARCHAR(100),
    estimated_time VARCHAR(50),
    difficulty VARCHAR(50),
    resources_needed JSONB DEFAULT '[]',
    engagement_estimate VARCHAR(50),
    best_posting_time VARCHAR(100),
    expected_reach_multiplier DECIMAL(3,1),
    status VARCHAR(50) DEFAULT 'draft',
    published_at TIMESTAMPTZ,
    actual_engagement JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- SECTION 6: INDEXES
-- ===========================================

-- Profiles
CREATE INDEX IF NOT EXISTS idx_profiles_email ON public.profiles(email);
CREATE INDEX IF NOT EXISTS idx_profiles_plan ON public.profiles(plan);
CREATE INDEX IF NOT EXISTS idx_profiles_plan_expires_at ON public.profiles(plan_expires_at);
CREATE INDEX IF NOT EXISTS idx_profiles_plan_status ON public.profiles(plan_status);

-- Payments
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON public.payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON public.payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_phonepe_txn ON public.payments(phonepe_merchant_transaction_id);

-- Onboarding
CREATE INDEX IF NOT EXISTS idx_onboarding_intake_user_id ON public.onboarding_intake(user_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_intake_share_token ON public.onboarding_intake(share_token);
CREATE INDEX IF NOT EXISTS idx_agent_executions_intake_id ON public.agent_executions(intake_id);
CREATE INDEX IF NOT EXISTS idx_agent_executions_status ON public.agent_executions(status);
CREATE INDEX IF NOT EXISTS idx_shared_links_token ON public.shared_links(token);

-- ICPs
CREATE INDEX IF NOT EXISTS idx_icps_user_id ON public.icps(user_id);
CREATE INDEX IF NOT EXISTS idx_icps_intake_id ON public.icps(intake_id);
CREATE INDEX IF NOT EXISTS idx_icps_fit_score ON public.icps(fit_score DESC);

-- Cohorts
CREATE INDEX IF NOT EXISTS idx_cohorts_user_id ON public.cohorts(user_id);
CREATE INDEX IF NOT EXISTS idx_cohorts_status ON public.cohorts(status);
CREATE INDEX IF NOT EXISTS idx_cohorts_interest_tags ON public.cohorts USING GIN(interest_tags);

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

-- Spikes
CREATE INDEX IF NOT EXISTS idx_spikes_user_id ON public.spikes(user_id);
CREATE INDEX IF NOT EXISTS idx_spikes_status ON public.spikes(status);
CREATE INDEX IF NOT EXISTS idx_spikes_dates ON public.spikes(start_date, end_date);

-- Guardrails
CREATE INDEX IF NOT EXISTS idx_guardrails_user_id ON public.guardrails(user_id);
CREATE INDEX IF NOT EXISTS idx_guardrails_spike_id ON public.guardrails(spike_id);

-- Experiments
CREATE INDEX IF NOT EXISTS idx_experiments_user_id ON public.experiments(user_id);
CREATE INDEX IF NOT EXISTS idx_experiments_spike_id ON public.experiments(spike_id);

-- Radar
CREATE INDEX IF NOT EXISTS idx_radar_opportunities_user_id ON public.radar_opportunities(user_id);
CREATE INDEX IF NOT EXISTS idx_radar_opportunities_cohort_id ON public.radar_opportunities(cohort_id);
CREATE INDEX IF NOT EXISTS idx_radar_opportunities_status ON public.radar_opportunities(status);

-- Content Ideas
CREATE INDEX IF NOT EXISTS idx_content_ideas_user_id ON public.content_ideas(user_id);
CREATE INDEX IF NOT EXISTS idx_content_ideas_cohort_id ON public.content_ideas(cohort_id);
CREATE INDEX IF NOT EXISTS idx_content_ideas_status ON public.content_ideas(status);

-- ===========================================
-- SECTION 7: ROW LEVEL SECURITY
-- ===========================================

-- Enable RLS on all tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.plan_prices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.onboarding_intake ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agent_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.shared_links ENABLE ROW LEVEL SECURITY;
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
ALTER TABLE public.radar_opportunities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.content_ideas ENABLE ROW LEVEL SECURITY;

-- Profiles policies
CREATE POLICY "Users can view own profile" ON public.profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON public.profiles FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Users can insert own profile" ON public.profiles FOR INSERT WITH CHECK (auth.uid() = id);

-- Payments policies
CREATE POLICY "Users can view own payments" ON public.payments FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own payments" ON public.payments FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Plan prices are public
CREATE POLICY "Anyone can view plan prices" ON public.plan_prices FOR SELECT TO PUBLIC USING (true);

-- Onboarding policies
CREATE POLICY "Users can view own intake" ON public.onboarding_intake FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own intake" ON public.onboarding_intake FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own intake" ON public.onboarding_intake FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Sales reps can view assigned intake" ON public.onboarding_intake FOR SELECT USING (auth.uid() = sales_rep_id);
CREATE POLICY "Sales reps can update assigned intake" ON public.onboarding_intake FOR UPDATE USING (auth.uid() = sales_rep_id);

-- Agent executions
CREATE POLICY "Users can view own agent executions" ON public.agent_executions FOR SELECT USING (EXISTS (SELECT 1 FROM public.onboarding_intake WHERE id = intake_id AND user_id = auth.uid()));
CREATE POLICY "Users can insert own agent executions" ON public.agent_executions FOR INSERT WITH CHECK (EXISTS (SELECT 1 FROM public.onboarding_intake WHERE id = intake_id AND user_id = auth.uid()));

-- Shared links
CREATE POLICY "Anyone can read shared links" ON public.shared_links FOR SELECT USING (true);
CREATE POLICY "Users can insert shared links" ON public.shared_links FOR INSERT WITH CHECK (EXISTS (SELECT 1 FROM public.onboarding_intake WHERE id = intake_id AND (user_id = auth.uid() OR sales_rep_id = auth.uid())));

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

-- Protocols are public
CREATE POLICY "Anyone can view protocols" ON public.protocols FOR SELECT TO PUBLIC USING (true);

-- Move templates are public
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

-- Radar policies
CREATE POLICY "Users can view own radar" ON public.radar_opportunities FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own radar" ON public.radar_opportunities FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own radar" ON public.radar_opportunities FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own radar" ON public.radar_opportunities FOR DELETE USING (auth.uid() = user_id);

-- Content ideas policies
CREATE POLICY "Users can view own content" ON public.content_ideas FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own content" ON public.content_ideas FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own content" ON public.content_ideas FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own content" ON public.content_ideas FOR DELETE USING (auth.uid() = user_id);

-- ===========================================
-- SECTION 8: FUNCTIONS
-- ===========================================

-- Updated at trigger function
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Handle new user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name, avatar_url)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'name'),
    NEW.raw_user_meta_data->>'avatar_url'
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Activate plan after payment
CREATE OR REPLACE FUNCTION public.activate_plan(
  p_user_id UUID,
  p_plan TEXT,
  p_payment_id TEXT,
  p_amount INTEGER
)
RETURNS BOOLEAN AS $$
DECLARE
  v_duration_days INTEGER;
BEGIN
  v_duration_days := CASE p_plan
    WHEN 'ascent' THEN 30
    WHEN 'glide' THEN 30
    WHEN 'soar' THEN 30
    ELSE 30
  END;

  UPDATE public.profiles
  SET
    plan = p_plan,
    plan_status = 'active',
    plan_started_at = NOW(),
    plan_expires_at = NOW() + (v_duration_days || ' days')::INTERVAL,
    payment_status = 'completed',
    last_payment_id = p_payment_id,
    last_payment_amount = p_amount,
    last_payment_date = NOW()
  WHERE id = p_user_id;

  RETURN FOUND;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Check expired plans
CREATE OR REPLACE FUNCTION public.check_expired_plans()
RETURNS void AS $$
BEGIN
    UPDATE public.profiles
    SET 
        plan_status = 'expired',
        updated_at = NOW()
    WHERE 
        plan_status = 'active'
        AND plan_expires_at IS NOT NULL
        AND plan_expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

-- Check cohort limit
CREATE OR REPLACE FUNCTION public.check_cohort_limit()
RETURNS TRIGGER AS $$
DECLARE
    user_plan VARCHAR(50);
    cohort_count INTEGER;
    plan_limit INTEGER;
BEGIN
    SELECT plan INTO user_plan FROM profiles WHERE id = NEW.user_id;
    
    plan_limit := CASE user_plan
        WHEN 'soar' THEN 10
        WHEN 'glide' THEN 5
        WHEN 'ascent' THEN 3
        ELSE 1
    END;
    
    SELECT COUNT(*) INTO cohort_count FROM cohorts WHERE user_id = NEW.user_id;
    
    IF cohort_count >= plan_limit THEN
        RAISE EXCEPTION 'Cohort limit reached. Your % plan allows % cohorts.', COALESCE(user_plan, 'free'), plan_limit;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ===========================================
-- SECTION 9: TRIGGERS
-- ===========================================

-- Auth user trigger
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Updated at triggers
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON public.profiles FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER update_onboarding_intake_updated_at BEFORE UPDATE ON public.onboarding_intake FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER update_icps_updated_at BEFORE UPDATE ON public.icps FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER update_cohorts_updated_at BEFORE UPDATE ON public.cohorts FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER update_barriers_updated_at BEFORE UPDATE ON public.barriers FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER update_protocols_updated_at BEFORE UPDATE ON public.protocols FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER update_move_templates_updated_at BEFORE UPDATE ON public.move_templates FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER update_campaigns_updated_at BEFORE UPDATE ON public.campaigns FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER update_moves_updated_at BEFORE UPDATE ON public.moves FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER update_assets_updated_at BEFORE UPDATE ON public.assets FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER update_spikes_updated_at BEFORE UPDATE ON public.spikes FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER update_guardrails_updated_at BEFORE UPDATE ON public.guardrails FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER update_content_ideas_updated_at BEFORE UPDATE ON public.content_ideas FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- Cohort limit trigger
CREATE TRIGGER enforce_cohort_limit BEFORE INSERT ON public.cohorts FOR EACH ROW EXECUTE FUNCTION public.check_cohort_limit();

-- ===========================================
-- SECTION 10: SEED DATA
-- ===========================================

-- Plan prices
INSERT INTO public.plan_prices (plan, price_inr, price_paise, name, description, features, duration_days) VALUES
('ascent', 5000, 500000, 'Ascent', 'Start building your strategy', '["Complete 7-pillar strategy intake", "1 strategic workspace", "AI-powered plan generation", "90-day war map creation", "PDF & Notion export", "Email support", "30-day methodology access"]', 30),
('glide', 7000, 700000, 'Glide', 'For founders who mean business', '["Everything in Ascent", "3 strategic workspaces", "Advanced AI strategy engine", "Real-time collaboration (up to 3)", "Integrations: Notion, Slack, Linear", "Priority support", "90-day methodology access", "Monthly strategy review call"]', 30),
('soar', 10000, 1000000, 'Soar', 'The complete strategic arsenal', '["Everything in Glide", "Unlimited workspaces", "Team collaboration (up to 10)", "White-label exports", "API access", "Dedicated success manager", "1-on-1 strategy onboarding call", "Lifetime methodology access", "Quarterly strategy sessions"]', 30)
ON CONFLICT (plan) DO UPDATE SET
  price_inr = EXCLUDED.price_inr,
  price_paise = EXCLUDED.price_paise,
  name = EXCLUDED.name,
  description = EXCLUDED.description,
  features = EXCLUDED.features,
  duration_days = EXCLUDED.duration_days;

-- Protocols
INSERT INTO public.protocols (code, name, description, targets_barrier, trigger_conditions, required_asset_types, channel_rules, metric_targets, standard_checklist, display_order) VALUES
('A_AUTHORITY_BLITZ', 'Authority Blitz', 'Build thought leadership through content-first demand creation.', 'OBSCURITY', '[{"metric": "brand_search_volume", "operator": "less_than", "threshold": 100}]', '["pillar_content", "social_posts", "podcast_appearance"]', '{"primary": ["linkedin_organic", "youtube", "podcast"], "secondary": ["twitter", "newsletter"]}', '{"impressions": {"target": 100000, "unit": "monthly"}}', '[{"task": "Create pillar content piece", "category": "content", "is_required": true}]', 1),
('B_TRUST_ANCHOR', 'Trust Anchor', 'Build credibility through social proof and validation.', 'RISK', '[{"metric": "demo_to_close_rate", "operator": "less_than", "threshold": 15}]', '["case_study", "comparison_page", "roi_calculator"]', '{"primary": ["website", "retargeting", "email"]}', '{"demo_conversion": {"target": 20, "unit": "percentage"}}', '[{"task": "Create comparison page", "category": "content", "is_required": true}]', 2),
('C_COST_OF_INACTION', 'Cost of Inaction', 'Create urgency through consequences of delay.', 'INERTIA', '[{"metric": "avg_sales_cycle", "operator": "greater_than", "threshold": 90}]', '["wake_up_report", "deadline_campaign"]', '{"primary": ["abm_direct", "email", "linkedin_dm"]}', '{"pipeline_velocity": {"target": 30, "unit": "percentage_improvement"}}', '[{"task": "Create wake-up report", "category": "content", "is_required": true}]', 3),
('D_HABIT_HARDCODE', 'Habit Hard-Code', 'Drive activation and habit formation for new users.', 'FRICTION', '[{"metric": "activation_rate", "operator": "less_than", "threshold": 40}]', '["onboarding_sequence", "quick_start_guide"]', '{"primary": ["in_app", "email", "push"]}', '{"activation_rate": {"target": 60, "unit": "percentage"}}', '[{"task": "Define activation event", "category": "analytics", "is_required": true}]', 4),
('E_ENTERPRISE_WEDGE', 'Enterprise Wedge', 'Expand within accounts and drive enterprise deals.', 'CAPACITY', '[{"metric": "usage_at_limit", "operator": "greater_than", "threshold": 80}]', '["business_case_pdf", "qbr_deck"]', '{"primary": ["customer_success", "in_app", "email"]}', '{"expansion_rate": {"target": 25, "unit": "percentage"}}', '[{"task": "Identify expansion signals", "category": "analytics", "is_required": true}]', 5),
('F_CHURN_INTERCEPT', 'Churn Intercept', 'Prevent and recover churning customers.', 'ATROPHY', '[{"metric": "health_score", "operator": "less_than", "threshold": 40}]', '["loss_aversion_email", "pause_plan_page"]', '{"primary": ["email", "in_app", "phone"]}', '{"save_rate": {"target": 30, "unit": "percentage"}}', '[{"task": "Set up churn prediction", "category": "analytics", "is_required": true}]', 6)
ON CONFLICT (code) DO UPDATE SET
  name = EXCLUDED.name,
  description = EXCLUDED.description,
  targets_barrier = EXCLUDED.targets_barrier,
  display_order = EXCLUDED.display_order;

-- Move templates
INSERT INTO public.move_templates (slug, name, description, protocol_type, barrier_type, funnel_stage, base_impact_score, base_effort_score, display_order) VALUES
('content-waterfall', 'Content Waterfall', 'Create one pillar piece and atomize into micro-content.', 'A_AUTHORITY_BLITZ', 'OBSCURITY', 'tofu', 75, 60, 1),
('validation-loop', 'Validation Loop', 'Build trust through comparison pages and ROI calculators.', 'B_TRUST_ANCHOR', 'RISK', 'mofu', 80, 70, 2),
('spear-attack', 'Spear Attack', 'ABM-style targeted outreach with personalized reports.', 'C_COST_OF_INACTION', 'INERTIA', 'bofu', 85, 80, 3),
('facilitator-nudge', 'Facilitator Nudge', 'Guide new users to activation through onboarding.', 'D_HABIT_HARDCODE', 'FRICTION', 'lifecycle', 70, 65, 4),
('champions-armory', 'Champions Armory', 'Equip champions with tools to sell internally.', 'E_ENTERPRISE_WEDGE', 'CAPACITY', 'lifecycle', 90, 75, 5),
('churn-intercept-sequence', 'Churn Intercept Sequence', 'Intervene with at-risk customers before they cancel.', 'F_CHURN_INTERCEPT', 'ATROPHY', 'lifecycle', 85, 60, 6)
ON CONFLICT (slug) DO UPDATE SET
  name = EXCLUDED.name,
  description = EXCLUDED.description,
  protocol_type = EXCLUDED.protocol_type,
  barrier_type = EXCLUDED.barrier_type,
  display_order = EXCLUDED.display_order;

-- ===========================================
-- SECTION 11: GRANTS
-- ===========================================

-- Service role grants
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO service_role;

-- Authenticated user grants
GRANT SELECT, INSERT, UPDATE, DELETE ON public.profiles TO authenticated;
GRANT SELECT, INSERT ON public.payments TO authenticated;
GRANT SELECT ON public.plan_prices TO authenticated;
GRANT SELECT, INSERT, UPDATE ON public.onboarding_intake TO authenticated;
GRANT SELECT, INSERT ON public.agent_executions TO authenticated;
GRANT SELECT, INSERT, UPDATE ON public.shared_links TO authenticated;
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
GRANT SELECT, INSERT, UPDATE, DELETE ON public.radar_opportunities TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.content_ideas TO authenticated;

-- Anonymous user grants (for shared links)
GRANT SELECT ON public.plan_prices TO anon;
GRANT SELECT ON public.shared_links TO anon;

-- ===========================================
-- COMPLETE
-- ===========================================
DO $$ 
BEGIN
    RAISE NOTICE '✅ Raptorflow complete schema created successfully!';
    RAISE NOTICE 'Tables: 21 | Enums: 12 | Functions: 5 | Triggers: 15';
END $$;
