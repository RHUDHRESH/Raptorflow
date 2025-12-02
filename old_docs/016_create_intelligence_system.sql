-- Migration 016: Create Intelligence & Signal System
-- Phase: Week 2 - Codex Schema Creation
-- Purpose: Add market intelligence, signals, and insights tracking
-- New Tables: 2 (intelligence_signals, market_insights)
-- Scope: Expand from 55 → 57 tables

-- ============================================================================
-- TABLE 1: intelligence_signals
-- Purpose: Track market signals and intelligence gathered by agents
-- Workspace isolation: workspace_id + RLS policy
-- ============================================================================
CREATE TABLE IF NOT EXISTS intelligence_signals (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

  -- Signal source
  source_agent_id uuid REFERENCES agent_registry(id) ON DELETE SET NULL,
  source_type text NOT NULL, -- "competitor", "market", "trend", "industry", "customer"
  data_source text, -- "semrush", "ahrefs", "newsapi", "brave_search", "twitter", "linkedin", "google_trends", "internal"

  -- Signal details
  signal_title text NOT NULL,
  signal_description text,
  signal_category text NOT NULL, -- "competitor_activity", "market_trend", "industry_news", "customer_sentiment", "technology_shift"

  -- Intelligence content
  key_findings text[],
  data_points jsonb, -- structured data from the signal
  confidence_score numeric, -- 0-100
  relevance_score numeric, -- 0-100 (how relevant to current campaigns)

  -- Context
  related_competitor_ids uuid[],
  related_cohort_ids uuid[],
  related_campaign_ids uuid[],

  -- Timeline
  signal_date timestamp with time zone,
  detection_date timestamp with time zone DEFAULT now(),
  expiry_date timestamp with time zone, -- when signal becomes outdated

  -- Action status
  action_status text DEFAULT 'new', -- new, acknowledged, actioned, archived
  assigned_to_user_id uuid REFERENCES auth.users(id) ON DELETE SET NULL,
  action_notes text,

  -- Metadata
  created_by uuid NOT NULL REFERENCES auth.users(id) ON DELETE SET NULL,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),

  CONSTRAINT intelligence_signals_workspace_check CHECK (workspace_id IS NOT NULL),
  CONSTRAINT intelligence_signals_source_check CHECK (source_type IN ('competitor', 'market', 'trend', 'industry', 'customer')),
  CONSTRAINT intelligence_signals_category_check CHECK (signal_category IN ('competitor_activity', 'market_trend', 'industry_news', 'customer_sentiment', 'technology_shift')),
  CONSTRAINT intelligence_signals_status_check CHECK (action_status IN ('new', 'acknowledged', 'actioned', 'archived'))
);

CREATE INDEX idx_intelligence_signals_workspace ON intelligence_signals(workspace_id);
CREATE INDEX idx_intelligence_signals_status ON intelligence_signals(workspace_id, action_status);
CREATE INDEX idx_intelligence_signals_category ON intelligence_signals(workspace_id, signal_category);
CREATE INDEX idx_intelligence_signals_date ON intelligence_signals(workspace_id, detection_date DESC);
CREATE INDEX idx_intelligence_signals_agent ON intelligence_signals(source_agent_id);

ALTER TABLE intelligence_signals ENABLE ROW LEVEL SECURITY;

CREATE POLICY intelligence_signals_workspace_isolation ON intelligence_signals
  USING (workspace_id = current_setting('app.current_workspace_id')::uuid)
  WITH CHECK (workspace_id = current_setting('app.current_workspace_id')::uuid);

-- ============================================================================
-- TABLE 2: market_insights
-- Purpose: Aggregated, analyzed insights derived from intelligence signals
-- Workspace isolation: workspace_id + RLS policy
-- ============================================================================
CREATE TABLE IF NOT EXISTS market_insights (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

  -- Insight identification
  insight_title text NOT NULL,
  insight_description text,
  insight_type text NOT NULL, -- "opportunity", "threat", "trend", "gap", "pattern"
  category text, -- "competitive", "market", "customer", "technology"

  -- Source signals
  source_signal_ids uuid[],
  source_agent_id uuid REFERENCES agent_registry(id) ON DELETE SET NULL,
  number_of_signals_analyzed integer,

  -- Analysis content
  key_conclusions text[],
  supporting_evidence text[],
  confidence_level text DEFAULT 'medium', -- low, medium, high
  confidence_score numeric,

  -- Implications and recommendations
  business_implications text[],
  recommended_actions text[],
  potential_impact text,
  potential_roi_percentage numeric,

  -- Target context
  relevant_for_competitors uuid[],
  relevant_for_cohorts uuid[],
  relevant_for_campaigns uuid[],
  relevant_segments text[],

  -- Timeline
  time_relevance_start date,
  time_relevance_end date,
  discovery_date timestamp with time zone DEFAULT now(),

  -- Status
  insight_status text DEFAULT 'active', -- active, archived, superseded
  actioned_date timestamp with time zone,

  -- Metadata
  created_by uuid NOT NULL REFERENCES auth.users(id) ON DELETE SET NULL,
  reviewed_by uuid REFERENCES auth.users(id) ON DELETE SET NULL,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),

  CONSTRAINT market_insights_workspace_check CHECK (workspace_id IS NOT NULL),
  CONSTRAINT market_insights_type_check CHECK (insight_type IN ('opportunity', 'threat', 'trend', 'gap', 'pattern')),
  CONSTRAINT market_insights_confidence_check CHECK (confidence_level IN ('low', 'medium', 'high')),
  CONSTRAINT market_insights_status_check CHECK (insight_status IN ('active', 'archived', 'superseded'))
);

CREATE INDEX idx_market_insights_workspace ON market_insights(workspace_id);
CREATE INDEX idx_market_insights_type ON market_insights(workspace_id, insight_type);
CREATE INDEX idx_market_insights_status ON market_insights(workspace_id, insight_status);
CREATE INDEX idx_market_insights_date ON market_insights(workspace_id, discovery_date DESC);
CREATE INDEX idx_market_insights_relevance ON market_insights(workspace_id, time_relevance_start, time_relevance_end);

ALTER TABLE market_insights ENABLE ROW LEVEL SECURITY;

CREATE POLICY market_insights_workspace_isolation ON market_insights
  USING (workspace_id = current_setting('app.current_workspace_id')::uuid)
  WITH CHECK (workspace_id = current_setting('app.current_workspace_id')::uuid);

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to create insight from signals
CREATE OR REPLACE FUNCTION create_insight_from_signals(
  p_workspace_id uuid,
  p_signal_ids uuid[],
  p_insight_title text,
  p_insight_type text,
  p_conclusions text[],
  p_created_by uuid
)
RETURNS uuid AS $$
DECLARE
  v_insight_id uuid;
  v_confidence_score numeric;
  v_signal_count integer;
BEGIN
  -- Calculate confidence from number of signals
  v_signal_count := array_length(p_signal_ids, 1);
  v_confidence_score := LEAST(50 + (v_signal_count * 10), 100);

  -- Create new insight
  INSERT INTO market_insights (
    workspace_id, source_signal_ids, insight_title, insight_type,
    key_conclusions, number_of_signals_analyzed, confidence_score, created_by
  ) VALUES (
    p_workspace_id, p_signal_ids, p_insight_title, p_insight_type,
    p_conclusions, v_signal_count, v_confidence_score, p_created_by
  )
  RETURNING id INTO v_insight_id;

  RETURN v_insight_id;
END;
$$ LANGUAGE plpgsql;

-- Function to get active insights for workspace
CREATE OR REPLACE FUNCTION get_active_insights(p_workspace_id uuid)
RETURNS TABLE (
  id uuid,
  title text,
  type text,
  confidence numeric,
  signal_count integer,
  created_at timestamp with time zone
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    mi.id,
    mi.insight_title,
    mi.insight_type,
    mi.confidence_score,
    mi.number_of_signals_analyzed,
    mi.created_at
  FROM market_insights mi
  WHERE mi.workspace_id = p_workspace_id
  AND mi.insight_status = 'active'
  AND (mi.time_relevance_end IS NULL OR mi.time_relevance_end >= CURRENT_DATE)
  ORDER BY mi.confidence_score DESC, mi.created_at DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to get high-priority signals
CREATE OR REPLACE FUNCTION get_priority_signals(p_workspace_id uuid, p_confidence_threshold numeric DEFAULT 75)
RETURNS TABLE (
  id uuid,
  title text,
  category text,
  confidence numeric,
  relevance numeric,
  created_at timestamp with time zone
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    s.id,
    s.signal_title,
    s.signal_category,
    s.confidence_score,
    s.relevance_score,
    s.created_at
  FROM intelligence_signals s
  WHERE s.workspace_id = p_workspace_id
  AND s.action_status = 'new'
  AND s.confidence_score >= p_confidence_threshold
  ORDER BY (s.confidence_score * s.relevance_score / 100) DESC, s.created_at DESC;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- MIGRATION VERIFICATION BLOCK
-- ============================================================================

/*
POST-MIGRATION VERIFICATION:

1. Table creation:
   SELECT COUNT(*) FROM information_schema.tables
   WHERE table_schema = 'public' AND table_name IN
   ('intelligence_signals', 'market_insights');
   -- Expected: 2

2. RLS policies:
   SELECT COUNT(*) FROM pg_policies
   WHERE tablename IN ('intelligence_signals', 'market_insights');
   -- Expected: 2

3. Indexes created:
   SELECT COUNT(*) FROM pg_indexes
   WHERE tablename IN ('intelligence_signals', 'market_insights')
   AND schemaname = 'public';
   -- Expected: 10+ indexes

4. Functions created:
   SELECT COUNT(*) FROM pg_proc
   WHERE proname IN ('create_insight_from_signals', 'get_active_insights', 'get_priority_signals')
   AND pronamespace = 'public'::regnamespace;
   -- Expected: 3

5. Foreign key constraints:
   SELECT COUNT(*) FROM information_schema.table_constraints
   WHERE constraint_type = 'FOREIGN KEY'
   AND table_name IN ('intelligence_signals', 'market_insights');
   -- Expected: 4+ FKs
*/
