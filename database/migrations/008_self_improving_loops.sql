-- ============================================================================
-- Self-Improving Loops and Meta-Learning Tables
-- ============================================================================
-- Tracks agent recommendations and their outcomes, enabling the system
-- to learn from patterns and improve agent trust scoring.

-- Agent Recommendations Tracking
-- Stores every recommendation made by an agent
CREATE TABLE IF NOT EXISTS agent_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Agent and Context
    agent_id VARCHAR(50) NOT NULL,
    agent_name VARCHAR(255) NOT NULL,
    correlation_id VARCHAR(255) NOT NULL,
    workflow_id VARCHAR(255) NOT NULL,

    -- Recommendation Details
    recommendation_type VARCHAR(100) NOT NULL,  -- e.g., "strategy", "content", "creative", "safety"
    recommendation_content JSONB NOT NULL,
    confidence_score FLOAT DEFAULT 0.5,

    -- Supporting Reasoning
    reasoning TEXT,
    evidence JSONB,  -- Sources used for recommendation

    -- Outcome Tracking (populated later)
    outcome_status VARCHAR(50),  -- pending, approved, rejected, partial, implemented
    outcome_quality_score FLOAT,  -- 0-100: How good was this recommendation?
    outcome_notes TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    evaluated_at TIMESTAMP WITH TIME ZONE,

    -- Indexing
    INDEX idx_recommendations_agent (agent_id),
    INDEX idx_recommendations_workflow (workflow_id),
    INDEX idx_recommendations_status (outcome_status),
    INDEX idx_recommendations_created (created_at DESC)
);

-- Learning Patterns Extracted from Recommendations
-- Meta-learning agent identifies patterns in successful recommendations
CREATE TABLE IF NOT EXISTS recommendation_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Pattern Identification
    pattern_name VARCHAR(255) NOT NULL,
    pattern_category VARCHAR(100) NOT NULL,  -- e.g., "high_confidence", "consensus", "expert_opinion"
    agent_ids VARCHAR[] NOT NULL,  -- Agents that follow this pattern

    -- Pattern Specification
    pattern_definition JSONB NOT NULL,  -- The actual pattern (IF conditions, THEN action)
    success_rate FLOAT DEFAULT 0.0,  -- % of time this pattern leads to approved recommendations
    frequency_count INT DEFAULT 0,  -- How many times this pattern has been observed

    -- Pattern Evolution
    confidence_level FLOAT DEFAULT 0.0,  -- Meta-learner confidence in this pattern
    recommendation_strength VARCHAR(50),  -- weak, moderate, strong, very_strong

    -- Timestamps
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_confirmed_at TIMESTAMP WITH TIME ZONE,
    next_review_at TIMESTAMP WITH TIME ZONE,

    -- Indexing
    INDEX idx_patterns_category (pattern_category),
    INDEX idx_patterns_success (success_rate DESC),
    INDEX idx_patterns_agents (agent_ids)
);

-- Agent Trust Scores
-- Dynamically updated scores based on recommendation outcomes
CREATE TABLE IF NOT EXISTS agent_trust_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Agent Reference
    agent_id VARCHAR(50) NOT NULL,
    agent_name VARCHAR(255) NOT NULL,

    -- Trust Metrics
    overall_trust_score FLOAT DEFAULT 0.5,  -- 0-1, starts at 0.5 (neutral)
    accuracy_score FLOAT DEFAULT 0.5,  -- Recommendations that get approved
    consistency_score FLOAT DEFAULT 0.5,  -- Recommendations that align with patterns
    timeliness_score FLOAT DEFAULT 0.5,  -- Recommendations provided within SLA
    reliability_score FLOAT DEFAULT 0.5,  -- Agent availability and execution

    -- Performance Metrics
    total_recommendations INT DEFAULT 0,
    approved_recommendations INT DEFAULT 0,
    rejected_recommendations INT DEFAULT 0,
    partial_recommendations INT DEFAULT 0,

    approval_rate FLOAT DEFAULT 0.0,  -- approved / total
    avg_quality_score FLOAT DEFAULT 0.0,  -- Average outcome quality

    -- Trend Analysis
    trust_trend VARCHAR(50),  -- improving, stable, declining
    improvement_rate FLOAT DEFAULT 0.0,  -- Trust change per week

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_evaluated_at TIMESTAMP WITH TIME ZONE,

    UNIQUE(workspace_id, agent_id),

    -- Indexing
    INDEX idx_trust_overall (overall_trust_score DESC),
    INDEX idx_trust_agent (agent_id),
    INDEX idx_trust_updated (updated_at DESC)
);

-- Outcome Evaluations
-- Records actual outcomes of implemented recommendations
CREATE TABLE IF NOT EXISTS recommendation_outcomes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Reference
    recommendation_id UUID NOT NULL REFERENCES agent_recommendations(id) ON DELETE CASCADE,
    agent_id VARCHAR(50) NOT NULL,

    -- Outcome Assessment
    quality_dimensions JSONB NOT NULL,  -- {relevance, accuracy, timing, creativity, compliance}
    quality_scores JSONB NOT NULL,  -- Scores for each dimension (0-100)
    overall_quality_score FLOAT NOT NULL,  -- Weighted average

    -- Comparative Assessment
    compared_against INT,  -- If evaluated against alternatives, count of alternatives
    ranked_position INT,  -- Where this recommendation ranked (1 = best)
    outperformed_count INT DEFAULT 0,  -- How many recommendations did it outperform?

    -- Human Feedback
    evaluator_feedback TEXT,
    evaluator_id UUID REFERENCES auth.users(id),

    -- Temporal Context
    evaluation_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    impact_observed_date TIMESTAMP WITH TIME ZONE,
    impact_duration_days INT,

    -- Indexing
    INDEX idx_outcomes_recommendation (recommendation_id),
    INDEX idx_outcomes_agent (agent_id),
    INDEX idx_outcomes_quality (overall_quality_score DESC),
    INDEX idx_outcomes_date (evaluation_date DESC)
);

-- Meta-Learner State
-- Stores the state and memory of the meta-learning agent
CREATE TABLE IF NOT EXISTS meta_learner_state (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Learner Configuration
    learner_version VARCHAR(50) NOT NULL,
    learning_rate FLOAT DEFAULT 0.1,
    pattern_confidence_threshold FLOAT DEFAULT 0.7,

    -- Learned Knowledge
    learned_patterns JSONB NOT NULL,  -- Complete pattern library
    agent_profiles JSONB NOT NULL,  -- Profiles of each agent's strengths/weaknesses
    decision_rules JSONB NOT NULL,  -- Rules for agent selection

    -- Learning Progress
    samples_processed INT DEFAULT 0,
    last_learning_iteration_at TIMESTAMP WITH TIME ZONE,
    next_learning_iteration_at TIMESTAMP WITH TIME ZONE,
    learning_cycles_completed INT DEFAULT 0,

    -- Model Performance
    model_accuracy FLOAT DEFAULT 0.0,  -- How well patterns predict outcomes
    model_coverage FLOAT DEFAULT 0.0,  -- % of recommendations explained by patterns

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(workspace_id)
);

-- Agent Recommendation Analysis View
-- Aggregated view for recommendation analysis
CREATE VIEW IF NOT EXISTS v_agent_recommendation_analysis AS
SELECT
    ar.agent_id,
    ar.agent_name,
    COUNT(*) as total_recommendations,
    SUM(CASE WHEN ar.outcome_status = 'approved' THEN 1 ELSE 0 END) as approved_count,
    SUM(CASE WHEN ar.outcome_status = 'rejected' THEN 1 ELSE 0 END) as rejected_count,
    AVG(ar.confidence_score) as avg_confidence,
    AVG(COALESCE(ar.outcome_quality_score, 0)) as avg_quality,
    MAX(ar.created_at) as last_recommendation_at
FROM agent_recommendations ar
GROUP BY ar.agent_id, ar.agent_name;

-- Pattern Effectiveness View
-- Shows how effective discovered patterns are
CREATE VIEW IF NOT EXISTS v_pattern_effectiveness AS
SELECT
    rp.pattern_name,
    rp.pattern_category,
    rp.success_rate,
    rp.frequency_count,
    rp.confidence_level,
    COUNT(DISTINCT ar.agent_id) as participating_agents,
    AVG(COALESCE(ro.overall_quality_score, 0)) as avg_pattern_quality
FROM recommendation_patterns rp
LEFT JOIN agent_recommendations ar ON ar.workspace_id = rp.workspace_id
LEFT JOIN recommendation_outcomes ro ON ro.recommendation_id = ar.id
GROUP BY rp.id, rp.pattern_name, rp.pattern_category, rp.success_rate, rp.frequency_count, rp.confidence_level;

-- RLS Policies
ALTER TABLE agent_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE recommendation_patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_trust_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE recommendation_outcomes ENABLE ROW LEVEL SECURITY;
ALTER TABLE meta_learner_state ENABLE ROW LEVEL SECURITY;

CREATE POLICY agent_recommendations_workspace_isolation ON agent_recommendations
    FOR ALL USING (workspace_id = current_workspace_id());

CREATE POLICY recommendation_patterns_workspace_isolation ON recommendation_patterns
    FOR ALL USING (workspace_id = current_workspace_id());

CREATE POLICY agent_trust_scores_workspace_isolation ON agent_trust_scores
    FOR ALL USING (workspace_id = current_workspace_id());

CREATE POLICY recommendation_outcomes_workspace_isolation ON recommendation_outcomes
    FOR ALL USING (workspace_id = current_workspace_id());

CREATE POLICY meta_learner_state_workspace_isolation ON meta_learner_state
    FOR ALL USING (workspace_id = current_workspace_id());

-- Comments
COMMENT ON TABLE agent_recommendations IS 'Tracks every recommendation made by agents, with outcomes for learning';
COMMENT ON TABLE recommendation_patterns IS 'Patterns discovered by meta-learner from successful recommendations';
COMMENT ON TABLE agent_trust_scores IS 'Dynamic trust scores for each agent based on recommendation outcomes';
COMMENT ON TABLE recommendation_outcomes IS 'Detailed evaluation of recommendation outcomes';
COMMENT ON TABLE meta_learner_state IS 'State and memory of the meta-learning agent';
