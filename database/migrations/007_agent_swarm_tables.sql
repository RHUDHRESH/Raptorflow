-- ============================================================================
-- Agent Swarm System Tables
-- ============================================================================
-- This migration creates tables for the multi-agent swarm system including:
-- - Agent registry and messaging
-- - Experiments and A/B testing
-- - Trends and competitor intelligence
-- - Policy decisions and debates
-- - Visual design specifications

-- ============================================================================
-- AGENT REGISTRY & MESSAGING
-- ============================================================================

CREATE TABLE IF NOT EXISTS agent_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  type TEXT NOT NULL,
  origin TEXT NOT NULL,
  targets TEXT[] DEFAULT '{}',
  payload JSONB,
  priority TEXT DEFAULT 'MEDIUM' CHECK (priority IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
  correlation_id TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  ttl INT DEFAULT 3600
);

CREATE INDEX IF NOT EXISTS idx_agent_messages_correlation ON agent_messages(correlation_id);
CREATE INDEX IF NOT EXISTS idx_agent_messages_type ON agent_messages(type);
CREATE INDEX IF NOT EXISTS idx_agent_messages_origin ON agent_messages(origin);
CREATE INDEX IF NOT EXISTS idx_agent_messages_created ON agent_messages(created_at DESC);


-- ============================================================================
-- EXPERIMENTS & A/B TESTING (SplitMind Agent)
-- ============================================================================

CREATE TABLE IF NOT EXISTS experiments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  move_id UUID REFERENCES moves(id),
  hypothesis TEXT NOT NULL,
  variants JSONB,  -- [{"variant": "A", "asset_id": "...", "name": "..."}]
  sample_size_per_variant INT,
  duration_days INT,
  success_metric TEXT,
  stop_conditions JSONB,
  status TEXT DEFAULT 'running' CHECK (status IN ('running', 'completed', 'stopped', 'failed')),
  winner_variant TEXT,
  confidence FLOAT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  created_by_agent TEXT
);

CREATE INDEX IF NOT EXISTS idx_experiments_move ON experiments(move_id);
CREATE INDEX IF NOT EXISTS idx_experiments_status ON experiments(status);
CREATE INDEX IF NOT EXISTS idx_experiments_created ON experiments(created_at DESC);


CREATE TABLE IF NOT EXISTS experiment_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  experiment_id UUID REFERENCES experiments(id) ON DELETE CASCADE,
  variant TEXT NOT NULL,
  metric_name TEXT NOT NULL,
  metric_value FLOAT,
  sample_size INT,
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_experiment_results_experiment ON experiment_results(experiment_id);
CREATE INDEX IF NOT EXISTS idx_experiment_results_variant ON experiment_results(variant);
CREATE INDEX IF NOT EXISTS idx_experiment_results_timestamp ON experiment_results(timestamp DESC);


CREATE TABLE IF NOT EXISTS experiment_metadata (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  experiment_id UUID REFERENCES experiments(id) ON DELETE CASCADE,
  key TEXT,
  value JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_experiment_metadata_experiment ON experiment_metadata(experiment_id);


-- ============================================================================
-- TRENDS & SIGNALS (PulseSeer Agent)
-- ============================================================================

CREATE TABLE IF NOT EXISTS trends (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  topic TEXT NOT NULL,
  platforms TEXT[],
  velocity FLOAT,  -- Growth rate
  lifecycle_stage TEXT CHECK (lifecycle_stage IN ('emerging', 'peak', 'declining')),
  relevant_cohorts UUID[],
  opportunity_score FLOAT,
  first_seen TIMESTAMPTZ,
  expiry_date TIMESTAMPTZ,
  source TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_trends_topic ON trends(topic);
CREATE INDEX IF NOT EXISTS idx_trends_platforms ON trends USING GIN(platforms);
CREATE INDEX IF NOT EXISTS idx_trends_cohorts ON trends USING GIN(relevant_cohorts);
CREATE INDEX IF NOT EXISTS idx_trends_opportunity ON trends(opportunity_score DESC);
CREATE INDEX IF NOT EXISTS idx_trends_lifecycle ON trends(lifecycle_stage);


CREATE TABLE IF NOT EXISTS trend_mentions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  trend_id UUID REFERENCES trends(id) ON DELETE CASCADE,
  source_platform TEXT,
  source_url TEXT,
  mention_count INT,
  engagement INT,
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_trend_mentions_trend ON trend_mentions(trend_id);


-- ============================================================================
-- COMPETITOR INTELLIGENCE (MirrorScout Agent)
-- ============================================================================

CREATE TABLE IF NOT EXISTS competitors (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID REFERENCES workspaces(id),
  name TEXT NOT NULL,
  website_url TEXT,
  industry TEXT,
  platforms JSONB,  -- {"linkedin": "@handle", "twitter": "@handle"}
  last_analyzed TIMESTAMPTZ,
  notes JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_competitors_workspace ON competitors(workspace_id);
CREATE INDEX IF NOT EXISTS idx_competitors_name ON competitors(name);
CREATE INDEX IF NOT EXISTS idx_competitors_last_analyzed ON competitors(last_analyzed DESC);


CREATE TABLE IF NOT EXISTS competitor_content (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  competitor_id UUID REFERENCES competitors(id) ON DELETE CASCADE,
  platform TEXT,
  content_type TEXT,
  title TEXT,
  body TEXT,
  url TEXT,
  metadata JSONB,
  performance_metrics JSONB,  -- {"likes": 100, "shares": 20, "comments": 5}
  patterns JSONB,  -- ["proof_heavy", "pain_focused"]
  scraped_at TIMESTAMPTZ DEFAULT NOW(),
  scraped_by_agent TEXT
);

CREATE INDEX IF NOT EXISTS idx_competitor_content_competitor ON competitor_content(competitor_id);
CREATE INDEX IF NOT EXISTS idx_competitor_content_platform ON competitor_content(platform);
CREATE INDEX IF NOT EXISTS idx_competitor_content_type ON competitor_content(content_type);


CREATE TABLE IF NOT EXISTS competitor_patterns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  competitor_id UUID REFERENCES competitors(id) ON DELETE CASCADE,
  pattern_type TEXT,
  pattern_name TEXT,
  pattern_data JSONB,
  frequency INT,
  success_rate FLOAT,
  identified_at TIMESTAMPTZ DEFAULT NOW(),
  identified_by_agent TEXT
);

CREATE INDEX IF NOT EXISTS idx_competitor_patterns_competitor ON competitor_patterns(competitor_id);


-- ============================================================================
-- POLICY & GOVERNANCE (Policy Arbiter)
-- ============================================================================

CREATE TABLE IF NOT EXISTS policy_decisions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conflict_id TEXT,
  agents_involved TEXT[],
  issue_description TEXT,
  decision TEXT,
  reasoning TEXT,
  overrides JSONB,  -- {"winning_agent": "STRAT-01", "override_reason": "..."}
  binding BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_policy_decisions_conflict ON policy_decisions(conflict_id);
CREATE INDEX IF NOT EXISTS idx_policy_decisions_created ON policy_decisions(created_at DESC);


CREATE TABLE IF NOT EXISTS agent_debates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  debate_id TEXT,
  topic TEXT,
  question TEXT,
  correlation_id TEXT,
  participants TEXT[],
  context JSONB,
  rounds INT,
  voting_threshold FLOAT,
  final_decision TEXT,
  confidence FLOAT,
  consensus_reached BOOLEAN,
  votes JSONB,  -- {"agent_id": "decision_value"}
  reasoning JSONB,  -- {"agent_id": "their_reasoning"}
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_debates_debate_id ON agent_debates(debate_id);
CREATE INDEX IF NOT EXISTS idx_agent_debates_correlation ON agent_debates(correlation_id);


CREATE TABLE IF NOT EXISTS debate_rounds (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  debate_id TEXT REFERENCES agent_debates(debate_id),
  round_number INT,
  positions JSONB,  -- {"agent_id": {"decision": "...", "reasoning": "..."}}
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_debate_rounds_debate ON debate_rounds(debate_id);


-- ============================================================================
-- VISUAL DESIGN SPECIFICATIONS (NoirFrame Agent)
-- ============================================================================

CREATE TABLE IF NOT EXISTS visual_designs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brief_id UUID,
  channel TEXT,
  format TEXT,
  mood TEXT,
  color_palette TEXT[],
  composition TEXT,
  elements TEXT[],
  canva_template_id TEXT,
  canva_template_name TEXT,
  image_gen_prompt TEXT,
  image_gen_model TEXT,  -- "dall-e", "midjourney", "stable-diffusion"
  aspect_ratio TEXT,
  design_notes JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by_agent TEXT
);

CREATE INDEX IF NOT EXISTS idx_visual_designs_brief ON visual_designs(brief_id);
CREATE INDEX IF NOT EXISTS idx_visual_designs_channel ON visual_designs(channel);
CREATE INDEX IF NOT EXISTS idx_visual_designs_mood ON visual_designs(mood);


CREATE TABLE IF NOT EXISTS visual_design_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  channel TEXT,
  format TEXT,
  mood TEXT,
  template_config JSONB,
  success_rate FLOAT,
  usage_count INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_visual_templates_mood ON visual_design_templates(mood);
CREATE INDEX IF NOT EXISTS idx_visual_templates_channel ON visual_design_templates(channel);


-- ============================================================================
-- CONTENT ADAPTATION SPECS (PortaMorph Agent)
-- ============================================================================

CREATE TABLE IF NOT EXISTS content_adaptations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_asset_id UUID,
  target_channel TEXT,
  target_format TEXT,
  source_format TEXT,
  adapted_body TEXT,
  adaptation_rules JSONB,
  quality_score FLOAT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by_agent TEXT
);

CREATE INDEX IF NOT EXISTS idx_content_adaptations_source ON content_adaptations(source_asset_id);
CREATE INDEX IF NOT EXISTS idx_content_adaptations_target_channel ON content_adaptations(target_channel);


CREATE TABLE IF NOT EXISTS adaptation_patterns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_format TEXT,
  target_format TEXT,
  pattern_data JSONB,  -- Rules for this adaptation
  success_rate FLOAT,
  usage_count INT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_adaptation_patterns_source_target ON adaptation_patterns(source_format, target_format);


-- ============================================================================
-- AGENT LEARNING & RECOMMENDATIONS
-- ============================================================================

CREATE TABLE IF NOT EXISTS agent_recommendations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id TEXT,
  move_id UUID,
  recommendation_type TEXT,
  recommendation_text TEXT,
  expected_impact FLOAT,
  accepted BOOLEAN,
  executed BOOLEAN,
  actual_impact FLOAT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  evaluated_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_agent_recommendations_agent ON agent_recommendations(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_recommendations_move ON agent_recommendations(move_id);
CREATE INDEX IF NOT EXISTS idx_agent_recommendations_accepted ON agent_recommendations(accepted);


CREATE TABLE IF NOT EXISTS agent_trust_scores (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id TEXT PRIMARY KEY,
  trust_score FLOAT DEFAULT 0.7,
  accuracy_score FLOAT DEFAULT 0.7,
  reliability_score FLOAT DEFAULT 0.7,
  recommendations_count INT DEFAULT 0,
  successful_recommendations INT DEFAULT 0,
  last_updated TIMESTAMPTZ DEFAULT NOW()
);


-- ============================================================================
-- PATTERN LIBRARY (for system learning)
-- ============================================================================

CREATE TABLE IF NOT EXISTS content_patterns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  pattern_type TEXT,  -- "hook", "emotional_tone", "structure"
  pattern_name TEXT,
  pattern_description TEXT,
  performing_assets UUID[],
  success_rate FLOAT,
  recommended_for_cohorts UUID[],
  recommended_for_channels TEXT[],
  usage_count INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_content_patterns_type ON content_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_content_patterns_success_rate ON content_patterns(success_rate DESC);


-- ============================================================================
-- EXTEND EXISTING TABLES
-- ============================================================================

-- Add columns to assets table
ALTER TABLE assets ADD COLUMN IF NOT EXISTS created_by_agent TEXT;
ALTER TABLE assets ADD COLUMN IF NOT EXISTS reviewed_by_agents TEXT[];
ALTER TABLE assets ADD COLUMN IF NOT EXISTS agent_debate_id UUID;
ALTER TABLE assets ADD COLUMN IF NOT EXISTS experiment_id UUID REFERENCES experiments(id);
ALTER TABLE assets ADD COLUMN IF NOT EXISTS experiment_variant TEXT;
ALTER TABLE assets ADD COLUMN IF NOT EXISTS pattern_id UUID REFERENCES content_patterns(id);

-- Add columns to moves table
ALTER TABLE moves ADD COLUMN IF NOT EXISTS triggered_by_trend_id UUID REFERENCES trends(id);
ALTER TABLE moves ADD COLUMN IF NOT EXISTS competitor_analysis JSONB;
ALTER TABLE moves ADD COLUMN IF NOT EXISTS created_by_agent TEXT;
ALTER TABLE moves ADD COLUMN IF NOT EXISTS agent_recommendations JSONB;

-- Add columns to cohorts table
ALTER TABLE cohorts ADD COLUMN IF NOT EXISTS drift_detected BOOLEAN DEFAULT FALSE;
ALTER TABLE cohorts ADD COLUMN IF NOT EXISTS last_drift_check TIMESTAMPTZ;

-- ============================================================================
-- RLS (Row Level Security) Policies
-- ============================================================================

ALTER TABLE experiments ENABLE ROW LEVEL SECURITY;
ALTER TABLE experiments ADD POLICY experiments_workspace_isolation
  ON experiments USING (move_id IN (SELECT id FROM moves WHERE workspace_id = current_setting('workspace_id')::uuid));

ALTER TABLE trends ENABLE ROW LEVEL SECURITY;
ALTER TABLE trends ADD POLICY trends_workspace_isolation
  ON trends USING (workspace_id = current_setting('workspace_id')::uuid);

ALTER TABLE competitors ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitors ADD POLICY competitors_workspace_isolation
  ON competitors USING (workspace_id = current_setting('workspace_id')::uuid);

ALTER TABLE agent_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_recommendations ADD POLICY agent_recommendations_workspace_isolation
  ON agent_recommendations USING (move_id IN (SELECT id FROM moves WHERE workspace_id = current_setting('workspace_id')::uuid));

-- ============================================================================
-- VIEWS for Analytics
-- ============================================================================

CREATE OR REPLACE VIEW agent_performance AS
SELECT
  agent_id,
  COUNT(*) as total_recommendations,
  SUM(CASE WHEN accepted THEN 1 ELSE 0 END) as accepted_recommendations,
  SUM(CASE WHEN executed THEN 1 ELSE 0 END) as executed_recommendations,
  AVG(CASE WHEN executed THEN actual_impact ELSE NULL END) as avg_actual_impact,
  ROUND(AVG(CASE WHEN executed THEN actual_impact ELSE NULL END) / NULLIF(AVG(expected_impact), 0), 2) as impact_accuracy
FROM agent_recommendations
GROUP BY agent_id;


CREATE OR REPLACE VIEW experiment_summary AS
SELECT
  move_id,
  COUNT(*) as total_experiments,
  SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_experiments,
  AVG(CASE WHEN status = 'completed' THEN confidence ELSE NULL END) as avg_confidence,
  MAX(CASE WHEN status = 'completed' THEN confidence ELSE NULL END) as max_confidence
FROM experiments
GROUP BY move_id;


CREATE OR REPLACE VIEW trend_opportunities AS
SELECT
  id,
  topic,
  opportunity_score,
  lifecycle_stage,
  platforms,
  relevant_cohorts,
  expiry_date,
  (EXTRACT(EPOCH FROM (expiry_date - NOW())) / 3600) as hours_until_expiry
FROM trends
WHERE expiry_date > NOW()
ORDER BY opportunity_score DESC;


-- ============================================================================
-- MIGRATION METADATA
-- ============================================================================

INSERT INTO migrations (name, description, status, executed_at)
VALUES (
  '007_agent_swarm_tables',
  'Create agent swarm system tables: experiments, trends, competitors, debates, visual designs, adaptations',
  'completed',
  NOW()
) ON CONFLICT DO NOTHING;
