-- Additional indexes for performance optimization
-- Migration: 20240116_indexes.sql

-- Performance indexes for pagination and sorting
CREATE INDEX IF NOT EXISTS idx_users_created_at_desc ON public.users(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_workspaces_created_at_desc ON public.workspaces(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_foundations_created_at_desc ON public.foundations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_icp_profiles_created_at_desc ON public.icp_profiles(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_moves_created_at_desc ON public.moves(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_campaigns_created_at_desc ON public.campaigns(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_muse_assets_created_at_desc ON public.muse_assets(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_blackbox_strategies_created_at_desc ON public.blackbox_strategies(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_daily_wins_created_at_desc ON public.daily_wins(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_executions_created_at_desc ON public.agent_executions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_created_at_desc ON public.onboarding_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_evidence_vault_created_at_desc ON public.evidence_vault(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_research_findings_created_at_desc ON public.research_findings(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_competitor_profiles_created_at_desc ON public.competitor_profiles(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_feedback_created_at_desc ON public.user_feedback(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_usage_records_created_at_desc ON public.usage_records(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_subscriptions_created_at_desc ON public.subscriptions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_invoices_created_at_desc ON public.invoices(created_at DESC);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_workspaces_user_created ON public.workspaces(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_foundations_workspace_created ON public.foundations(workspace_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_icp_profiles_workspace_created ON public.icp_profiles(workspace_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_icp_profiles_workspace_primary ON public.icp_profiles(workspace_id, is_primary);
CREATE INDEX IF NOT EXISTS idx_moves_workspace_created ON public.moves(workspace_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_moves_workspace_status ON public.moves(workspace_id, status);
CREATE INDEX IF NOT EXISTS idx_moves_campaign_created ON public.moves(campaign_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_campaigns_workspace_created ON public.campaigns(workspace_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_campaigns_workspace_status ON public.campaigns(workspace_id, status);
CREATE INDEX IF NOT EXISTS idx_muse_assets_workspace_created ON public.muse_assets(workspace_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_muse_assets_workspace_type ON public.muse_assets(workspace_id, asset_type);
CREATE INDEX IF NOT EXISTS idx_muse_assets_move_created ON public.muse_assets(move_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_muse_assets_icp_created ON public.muse_assets(target_icp_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_blackbox_strategies_workspace_created ON public.blackbox_strategies(workspace_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_blackbox_strategies_workspace_status ON public.blackbox_strategies(workspace_id, status);
CREATE INDEX IF NOT EXISTS idx_daily_wins_workspace_date ON public.daily_wins(workspace_id, win_date DESC);
CREATE INDEX IF NOT EXISTS idx_daily_wins_workspace_status ON public.daily_wins(workspace_id, status);
CREATE INDEX IF NOT EXISTS idx_agent_executions_workspace_session ON public.agent_executions(workspace_id, session_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_executions_workspace_agent ON public.agent_executions(workspace_id, agent_name, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_executions_workspace_status ON public.agent_executions(workspace_id, status);
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_workspace_status ON public.onboarding_sessions(workspace_id, status);
CREATE INDEX IF NOT EXISTS idx_evidence_vault_workspace_session ON public.evidence_vault(workspace_id, session_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_evidence_vault_workspace_status ON public.evidence_vault(workspace_id, processing_status);
CREATE INDEX IF NOT EXISTS idx_research_findings_workspace_created ON public.research_findings(workspace_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_research_findings_workspace_type ON public.research_findings(workspace_id, research_type);
CREATE INDEX IF NOT EXISTS idx_competitor_profiles_workspace_created ON public.competitor_profiles(workspace_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_feedback_workspace_created ON public.user_feedback(workspace_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_usage_records_workspace_period ON public.usage_records(workspace_id, period_start DESC, period_end DESC);
CREATE INDEX IF NOT EXISTS idx_subscriptions_workspace_status ON public.subscriptions(workspace_id, status);
CREATE INDEX IF NOT EXISTS idx_invoices_workspace_status ON public.invoices(workspace_id, status);

-- Partial indexes for status filters (more efficient)
CREATE INDEX IF NOT EXISTS idx_moves_active ON public.moves(workspace_id, created_at DESC) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_moves_completed ON public.moves(workspace_id, created_at DESC) WHERE status = 'completed';
CREATE INDEX IF NOT EXISTS idx_campaigns_active ON public.campaigns(workspace_id, created_at DESC) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_campaigns_completed ON public.campaigns(workspace_id, created_at DESC) WHERE status = 'completed';
CREATE INDEX IF NOT EXISTS idx_muse_assets_draft ON public.muse_assets(workspace_id, created_at DESC) WHERE status = 'draft';
CREATE INDEX IF NOT EXISTS idx_muse_assets_published ON public.muse_assets(workspace_id, created_at DESC) WHERE status = 'published';
CREATE INDEX IF NOT EXISTS idx_blackbox_strategies_pending ON public.blackbox_strategies(workspace_id, created_at DESC) WHERE status = 'proposed';
CREATE INDEX IF NOT EXISTS idx_daily_wins_posted ON public.daily_wins(workspace_id, win_date DESC) WHERE status = 'posted';
CREATE INDEX IF NOT EXISTS idx_daily_wins_idea ON public.daily_wins(workspace_id, win_date DESC) WHERE status = 'idea';
CREATE INDEX IF NOT EXISTS idx_agent_executions_running ON public.agent_executions(workspace_id, started_at DESC) WHERE status = 'running';
CREATE INDEX IF NOT EXISTS idx_agent_executions_completed ON public.agent_executions(workspace_id, completed_at DESC) WHERE status = 'completed';
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_in_progress ON public.onboarding_sessions(workspace_id, started_at DESC) WHERE status = 'in_progress';
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_completed ON public.onboarding_sessions(workspace_id, completed_at DESC) WHERE status = 'completed';
CREATE INDEX IF NOT EXISTS idx_evidence_vault_pending ON public.evidence_vault(workspace_id, created_at DESC) WHERE processing_status = 'pending';
CREATE INDEX IF NOT EXISTS idx_evidence_vault_processed ON public.evidence_vault(workspace_id, processed_at DESC) WHERE processing_status = 'processed';
CREATE INDEX IF NOT EXISTS idx_subscriptions_active ON public.subscriptions(workspace_id, current_period_end DESC) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_invoices_unpaid ON public.invoices(workspace_id, created_at DESC) WHERE status != 'paid';

-- GIN indexes for JSONB columns (for efficient JSON queries)
CREATE INDEX IF NOT EXISTS idx_users_preferences_gin ON public.users USING GIN (preferences);
CREATE INDEX IF NOT EXISTS idx_workspaces_settings_gin ON public.workspaces USING GIN (settings);
CREATE INDEX IF NOT EXISTS idx_foundations_values_gin ON public.foundations USING GIN (values);
CREATE INDEX IF NOT EXISTS idx_foundations_messaging_guardrails_gin ON public.foundations USING GIN (messaging_guardrails);
CREATE INDEX IF NOT EXISTS idx_icp_profiles_demographics_gin ON public.icp_profiles USING GIN (demographics);
CREATE INDEX IF NOT EXISTS idx_icp_profiles_psychographics_gin ON public.icp_profiles USING GIN (psychographics);
CREATE INDEX IF NOT EXISTS idx_icp_profiles_behaviors_gin ON public.icp_profiles USING GIN (behaviors);
CREATE INDEX IF NOT EXISTS idx_icp_profiles_pain_points_gin ON public.icp_profiles USING GIN (pain_points);
CREATE INDEX IF NOT EXISTS idx_icp_profiles_goals_gin ON public.icp_profiles USING GIN (goals);
CREATE INDEX IF NOT EXISTS idx_moves_strategy_gin ON public.moves USING GIN (strategy);
CREATE INDEX IF NOT EXISTS idx_moves_execution_plan_gin ON public.moves USING GIN (execution_plan);
CREATE INDEX IF NOT EXISTS idx_moves_success_metrics_gin ON public.moves USING GIN (success_metrics);
CREATE INDEX IF NOT EXISTS idx_moves_results_gin ON public.moves USING GIN (results);
CREATE INDEX IF NOT EXISTS idx_campaigns_target_icps_gin ON public.campaigns USING GIN (target_icps);
CREATE INDEX IF NOT EXISTS idx_campaigns_phases_gin ON public.campaigns USING GIN (phases);
CREATE INDEX IF NOT EXISTS idx_campaigns_success_metrics_gin ON public.campaigns USING GIN (success_metrics);
CREATE INDEX IF NOT EXISTS idx_campaigns_results_gin ON public.campaigns USING GIN (results);
CREATE INDEX IF NOT EXISTS idx_muse_assets_metadata_gin ON public.muse_assets USING GIN (metadata);
CREATE INDEX IF NOT EXISTS idx_blackbox_strategies_risk_reasons_gin ON public.blackbox_strategies USING GIN (risk_reasons);
CREATE INDEX IF NOT EXISTS idx_blackbox_strategies_phases_gin ON public.blackbox_strategies USING GIN (phases);
CREATE INDEX IF NOT EXISTS idx_agent_executions_input_gin ON public.agent_executions USING GIN (input);
CREATE INDEX IF NOT EXISTS idx_agent_executions_output_gin ON public.agent_executions USING GIN (output);
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_step_data_gin ON public.onboarding_sessions USING GIN (step_data);
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_completed_steps_gin ON public.onboarding_sessions USING GIN (completed_steps);
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_evidence_items_gin ON public.onboarding_sessions USING GIN (evidence_items);
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_extracted_facts_gin ON public.onboarding_sessions USING GIN (extracted_facts);
CREATE INDEX IF NOT EXISTS idx_evidence_vault_key_topics_gin ON public.evidence_vault USING GIN (key_topics);
CREATE INDEX IF NOT EXISTS idx_research_findings_sources_gin ON public.research_findings USING GIN (sources);
CREATE INDEX IF NOT EXISTS idx_research_findings_findings_gin ON public.research_findings USING GIN (findings);
CREATE INDEX IF NOT EXISTS idx_competitor_profiles_strengths_gin ON public.competitor_profiles USING GIN (strengths);
CREATE INDEX IF NOT EXISTS idx_competitor_profiles_weaknesses_gin ON public.competitor_profiles USING GIN (weaknesses);
CREATE INDEX IF NOT EXISTS idx_competitor_profiles_content_strategy_gin ON public.competitor_profiles USING GIN (content_strategy);
CREATE INDEX IF NOT EXISTS idx_usage_records_agent_breakdown_gin ON public.usage_records USING GIN (agent_breakdown);

-- Text search indexes for full-text search
CREATE INDEX IF NOT EXISTS idx_users_full_name_fts ON public.users USING GIN (to_tsvector('english', full_name));
CREATE INDEX IF NOT EXISTS idx_workspaces_name_fts ON public.workspaces USING GIN (to_tsvector('english', name));
CREATE INDEX IF NOT EXISTS idx_foundations_company_name_fts ON public.foundations USING GIN (to_tsvector('english', company_name));
CREATE INDEX IF NOT EXISTS idx_foundations_summary_fts ON public.foundations USING GIN (to_tsvector('english', summary));
CREATE INDEX IF NOT EXISTS idx_icp_profiles_name_fts ON public.icp_profiles USING GIN (to_tsvector('english', name));
CREATE INDEX IF NOT EXISTS idx_icp_profiles_tagline_fts ON public.icp_profiles USING GIN (to_tsvector('english', tagline));
CREATE INDEX IF NOT EXISTS idx_icp_profiles_summary_fts ON public.icp_profiles USING GIN (to_tsvector('english', summary));
CREATE INDEX IF NOT EXISTS idx_moves_name_fts ON public.moves USING GIN (to_tsvector('english', name));
CREATE INDEX IF NOT EXISTS idx_moves_goal_fts ON public.moves USING GIN (to_tsvector('english', goal));
CREATE INDEX IF NOT EXISTS idx_campaigns_name_fts ON public.campaigns USING GIN (to_tsvector('english', name));
CREATE INDEX IF NOT EXISTS idx_campaigns_description_fts ON public.campaigns USING GIN (to_tsvector('english', description));
CREATE INDEX IF NOT EXISTS idx_muse_assets_title_fts ON public.muse_assets USING GIN (to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_muse_assets_content_fts ON public.muse_assets USING GIN (to_tsvector('english', content));
CREATE INDEX IF NOT EXISTS idx_blackbox_strategies_name_fts ON public.blackbox_strategies USING GIN (to_tsvector('english', name));
CREATE INDEX IF NOT EXISTS idx_daily_wins_topic_fts ON public.daily_wins USING GIN (to_tsvector('english', topic));
CREATE INDEX IF NOT EXISTS idx_daily_wins_angle_fts ON public.daily_wins USING GIN (to_tsvector('english', angle));
CREATE INDEX IF NOT EXISTS idx_daily_wins_hook_fts ON public.daily_wins USING GIN (to_tsvector('english', hook));
CREATE INDEX IF NOT EXISTS idx_research_findings_summary_fts ON public.research_findings USING GIN (to_tsvector('english', summary));
CREATE INDEX IF NOT EXISTS idx_competitor_profiles_name_fts ON public.competitor_profiles USING GIN (to_tsvector('english', name));
CREATE INDEX IF NOT EXISTS idx_competitor_profiles_positioning_fts ON public.competitor_profiles USING GIN (to_tsvector('english', positioning));

-- Unique indexes for data integrity (additional constraints)
CREATE UNIQUE INDEX IF NOT EXISTS idx_workspaces_user_name_unique ON public.workspaces(user_id, name) WHERE name IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_foundations_workspace_unique ON public.foundations(workspace_id) WHERE workspace_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_icp_profiles_workspace_name_unique ON public.icp_profiles(workspace_id, name) WHERE name IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_onboarding_sessions_workspace_unique ON public.onboarding_sessions(workspace_id) WHERE workspace_id IS NOT NULL;

-- Covering indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_moves_workspace_status_created_covering ON public.moves(workspace_id, status, created_at DESC) INCLUDE (name, goal);
CREATE INDEX IF NOT EXISTS idx_campaigns_workspace_status_created_covering ON public.campaigns(workspace_id, status, created_at DESC) INCLUDE (name, description);
CREATE INDEX IF NOT EXISTS idx_muse_assets_workspace_type_created_covering ON public.muse_assets(workspace_id, asset_type, created_at DESC) INCLUDE (title, status);
CREATE INDEX IF NOT EXISTS idx_agent_executions_workspace_agent_created_covering ON public.agent_executions(workspace_id, agent_name, created_at DESC) INCLUDE (status, tokens_used, cost_usd);

-- Indexes for time-based queries
CREATE INDEX IF NOT EXISTS idx_usage_records_period_workspace ON public.usage_records(period_start DESC, period_end DESC, workspace_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_period_end_workspace ON public.subscriptions(current_period_end DESC, workspace_id);
CREATE INDEX IF NOT EXISTS idx_invoices_created_workspace_status ON public.invoices(created_at DESC, workspace_id, status);

-- Indexes for foreign key performance
CREATE INDEX IF NOT EXISTS idx_moves_target_icp_id ON public.moves(target_icp_id) WHERE target_icp_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_muse_assets_target_icp_id ON public.muse_assets(target_icp_id) WHERE target_icp_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_muse_assets_move_id ON public.muse_assets(move_id) WHERE move_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_blackbox_strategies_converted_move_id ON public.blackbox_strategies(converted_move_id) WHERE converted_move_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_daily_wins_expanded_content_id ON public.daily_wins(expanded_content_id) WHERE expanded_content_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_evidence_vault_session_id ON public.evidence_vault(session_id) WHERE session_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_user_feedback_output_id ON public.user_feedback(output_id) WHERE output_id IS NOT NULL;

-- Function to analyze index usage
CREATE OR REPLACE FUNCTION analyze_index_usage()
RETURNS TABLE(
    schemaname TEXT,
    tablename TEXT,
    indexname TEXT,
    idx_scan BIGINT,
    idx_tup_read BIGINT,
    idx_tup_fetch BIGINT,
    idx_size TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        pg_stat_user_indexes.schemaname,
        pg_stat_user_indexes.relname as tablename,
        pg_stat_user_indexes.indexrelname as indexname,
        pg_stat_user_indexes.idx_scan,
        pg_stat_user_indexes.idx_tup_read,
        pg_stat_user_indexes.idx_tup_fetch,
        pg_size_pretty(pg_relation_size(pg_stat_user_indexes.indexrelid)) as idx_size
    FROM pg_stat_user_indexes
    ORDER BY pg_stat_user_indexes.idx_scan DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to suggest missing indexes based on query patterns
CREATE OR REPLACE FUNCTION suggest_missing_indexes()
RETURNS TABLE(
    tablename TEXT,
    column_names TEXT,
    suggested_index TEXT,
    reason TEXT
) AS $$
BEGIN
    -- This is a simplified version - in production you'd analyze pg_stat_statements
    RETURN QUERY
    SELECT
        'moves'::TEXT as tablename,
        'workspace_id, status, created_at'::TEXT as column_names,
        'CREATE INDEX idx_moves_workspace_status_created ON moves(workspace_id, status, created_at DESC)'::TEXT as suggested_index,
        'Common query pattern for filtering moves by workspace and status with pagination'::TEXT as reason
    UNION ALL
    SELECT
        'campaigns'::TEXT as tablename,
        'workspace_id, status, created_at'::TEXT as column_names,
        'CREATE INDEX idx_campaigns_workspace_status_created ON campaigns(workspace_id, status, created_at DESC)'::TEXT as suggested_index,
        'Common query pattern for filtering campaigns by workspace and status with pagination'::TEXT as reason
    UNION ALL
    SELECT
        'muse_assets'::TEXT as tablename,
        'workspace_id, asset_type, created_at'::TEXT as column_names,
        'CREATE INDEX idx_muse_assets_workspace_type_created ON muse_assets(workspace_id, asset_type, created_at DESC)'::TEXT as suggested_index,
        'Common query pattern for filtering assets by workspace and type with pagination'::TEXT as reason;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant permissions for index analysis functions
GRANT EXECUTE ON FUNCTION analyze_index_usage() TO authenticated;
GRANT EXECUTE ON FUNCTION suggest_missing_indexes() TO authenticated;
