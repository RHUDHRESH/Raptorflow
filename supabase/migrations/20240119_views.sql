-- Database views for common queries and reporting
-- Migration: 20240119_views.sql

-- Workspace Summary View
CREATE OR REPLACE VIEW workspace_summary AS
SELECT
    w.id as workspace_id,
    w.name as workspace_name,
    w.slug,
    w.user_id,
    u.email as user_email,
    u.full_name as user_name,
    u.subscription_tier,
    w.created_at as workspace_created_at,
    w.updated_at as workspace_updated_at,

    -- Foundation info
    f.company_name,
    f.industry,
    f.mission,
    f.vision,
    f.summary as foundation_summary,

    -- ICP counts
    (SELECT COUNT(*) FROM public.icp_profiles WHERE workspace_id = w.id) as icp_count,
    (SELECT COUNT(*) FILTER (WHERE is_primary = true) FROM public.icp_profiles WHERE workspace_id = w.id) as primary_icp_count,

    -- Move counts by status
    (SELECT COUNT(*) FROM public.moves WHERE workspace_id = w.id) as total_moves,
    (SELECT COUNT(*) FROM public.moves WHERE workspace_id = w.id AND status = 'active') as active_moves,
    (SELECT COUNT(*) FROM public.moves WHERE workspace_id = w.id AND status = 'completed') as completed_moves,

    -- Campaign counts by status
    (SELECT COUNT(*) FROM public.campaigns WHERE workspace_id = w.id) as total_campaigns,
    (SELECT COUNT(*) FROM public.campaigns WHERE workspace_id = w.id AND status = 'active') as active_campaigns,
    (SELECT COUNT(*) FROM public.campaigns WHERE workspace_id = w.id AND status = 'completed') as completed_campaigns,

    -- Content counts
    (SELECT COUNT(*) FROM public.muse_assets WHERE workspace_id = w.id) as total_assets,
    (SELECT COUNT(*) FROM public.daily_wins WHERE workspace_id = w.id) as total_daily_wins,
    (SELECT COUNT(*) FROM public.blackbox_strategies WHERE workspace_id = w.id) as total_strategies,

    -- Usage stats
    COALESCE(ur.tokens_used, 0) as current_tokens_used,
    COALESCE(ur.cost_usd, 0) as current_cost,

    -- Recent activity
    (SELECT MAX(created_at) FROM public.moves WHERE workspace_id = w.id) as last_move_activity,
    (SELECT MAX(created_at) FROM public.campaigns WHERE workspace_id = w.id) as last_campaign_activity,
    (SELECT MAX(created_at) FROM public.muse_assets WHERE workspace_id = w.id) as last_asset_activity

FROM public.workspaces w
LEFT JOIN public.users u ON w.user_id = u.id
LEFT JOIN public.foundations f ON w.id = f.workspace_id
LEFT JOIN public.usage_records ur ON w.id = ur.workspace_id
    AND ur.period_start = DATE_TRUNC('month', NOW())
    AND ur.period_end = DATE_TRUNC('month', NOW()) + INTERVAL '1 month' - INTERVAL '1 microsecond';

-- Usage Summary View
CREATE OR REPLACE VIEW usage_summary AS
SELECT
    ur.workspace_id,
    w.name as workspace_name,
    w.user_id,
    u.email as user_email,
    u.subscription_tier,
    ur.period_start,
    ur.period_end,
    ur.tokens_used,
    ur.cost_usd,
    ur.agent_breakdown,

    -- Calculate daily averages
    CASE
        WHEN EXTRACT(DAY FROM ur.period_end - ur.period_start) > 0
        THEN ROUND(ur.tokens_used::NUMERIC / EXTRACT(DAY FROM ur.period_end - ur.period_start), 2)
        ELSE 0
    END as avg_daily_tokens,

    CASE
        WHEN EXTRACT(DAY FROM ur.period_end - ur.period_start) > 0
        THEN ROUND(ur.cost_usd::NUMERIC / EXTRACT(DAY FROM ur.period_end - ur.period_start), 4)
        ELSE 0
    END as avg_daily_cost,

    -- Usage breakdown by agent
    jsonb_object_keys(ur.agent_breakdown) as agents_used,

    -- Month over month comparison
    LAG(ur.tokens_used) OVER (PARTITION BY ur.workspace_id ORDER BY ur.period_start) as prev_month_tokens,
    LAG(ur.cost_usd) OVER (PARTITION BY ur.workspace_id ORDER BY ur.period_start) as prev_month_cost,

    -- Growth percentages
    CASE
        WHEN LAG(ur.tokens_used) OVER (PARTITION BY ur.workspace_id ORDER BY ur.period_start) > 0
        THEN ROUND(((ur.tokens_used - LAG(ur.tokens_used) OVER (PARTITION BY ur.workspace_id ORDER BY ur.period_start))::NUMERIC /
                   LAG(ur.tokens_used) OVER (PARTITION BY ur.workspace_id ORDER BY ur.period_start)) * 100, 2)
        ELSE NULL
    END as token_growth_pct,

    CASE
        WHEN LAG(ur.cost_usd) OVER (PARTITION BY ur.workspace_id ORDER BY ur.period_start) > 0
        THEN ROUND(((ur.cost_usd - LAG(ur.cost_usd) OVER (PARTITION BY ur.workspace_id ORDER BY ur.period_start))::NUMERIC /
                   LAG(ur.cost_usd) OVER (PARTITION BY ur.workspace_id ORDER BY ur.period_start)) * 100, 2)
        ELSE NULL
    END as cost_growth_pct

FROM public.usage_records ur
JOIN public.workspaces w ON ur.workspace_id = w.id
JOIN public.users u ON w.user_id = u.id
ORDER BY ur.period_start DESC;

-- Agent Performance View
CREATE OR REPLACE VIEW agent_performance AS
SELECT
    ae.agent_name,
    ae.workspace_id,
    w.name as workspace_name,
    DATE_TRUNC('day', ae.created_at) as execution_date,

    -- Execution counts
    COUNT(*) as total_executions,
    COUNT(*) FILTER (WHERE status = 'completed') as completed_executions,
    COUNT(*) FILTER (WHERE status = 'running') as running_executions,
    COUNT(*) FILTER (WHERE status = 'failed') as failed_executions,

    -- Success rate
    CASE
        WHEN COUNT(*) > 0
        THEN ROUND((COUNT(*) FILTER (WHERE status = 'completed')::NUMERIC / COUNT(*)) * 100, 2)
        ELSE 0
    END as success_rate_pct,

    -- Token and cost metrics
    COALESCE(SUM(ae.tokens_used), 0) as total_tokens_used,
    COALESCE(AVG(ae.tokens_used), 0) as avg_tokens_per_execution,
    COALESCE(SUM(ae.cost_usd), 0) as total_cost,
    COALESCE(AVG(ae.cost_usd), 0) as avg_cost_per_execution,

    -- Performance metrics
    COALESCE(AVG(EXTRACT(EPOCH FROM (ae.completed_at - ae.started_at))), 0) as avg_execution_time_seconds,
    MIN(EXTRACT(EPOCH FROM (ae.completed_at - ae.started_at))) as min_execution_time_seconds,
    MAX(EXTRACT(EPOCH FROM (ae.completed_at - ae.started_at))) as max_execution_time_seconds,

    -- Error analysis
    COUNT(*) FILTER (WHERE ae.error IS NOT NULL) as error_count,
    STRING_AGG(DISTINCT LEFT(ae.error, 100), '; ') as sample_errors

FROM public.agent_executions ae
JOIN public.workspaces w ON ae.workspace_id = w.id
GROUP BY ae.agent_name, ae.workspace_id, w.name, DATE_TRUNC('day', ae.created_at)
ORDER BY execution_date DESC, total_executions DESC;

-- ICP Performance View
CREATE OR REPLACE VIEW icp_performance AS
SELECT
    icp.id as icp_id,
    icp.name as icp_name,
    icp.workspace_id,
    w.name as workspace_name,
    icp.is_primary,
    icp.fit_score,
    icp.created_at,

    -- Related moves count
    (SELECT COUNT(*) FROM public.moves WHERE target_icp_id = icp.id) as targeted_moves_count,
    (SELECT COUNT(*) FROM public.moves WHERE target_icp_id = icp.id AND status = 'completed') as completed_moves_count,

    -- Related assets count
    (SELECT COUNT(*) FROM public.muse_assets WHERE target_icp_id = icp.id) as targeted_assets_count,

    -- Campaign involvement
    (SELECT COUNT(DISTINCT campaign_id)
     FROM public.moves
     WHERE target_icp_id = icp.id
     AND campaign_id IS NOT NULL) as involved_campaigns_count,

    -- Success metrics
    CASE
        WHEN (SELECT COUNT(*) FROM public.moves WHERE target_icp_id = icp.id) > 0
        THEN ROUND(((SELECT COUNT(*) FROM public.moves WHERE target_icp_id = icp.id AND status = 'completed')::NUMERIC /
                   (SELECT COUNT(*) FROM public.moves WHERE target_icp_id = icp.id)) * 100, 2)
        ELSE 0
    END as move_success_rate_pct,

    -- Content quality
    COALESCE(AVG(ma.quality_score), 0) as avg_asset_quality_score,
    COUNT(ma.id) as total_assets_with_quality_score

FROM public.icp_profiles icp
JOIN public.workspaces w ON icp.workspace_id = w.id
LEFT JOIN public.muse_assets ma ON icp.id = ma.target_icp_id
GROUP BY icp.id, icp.name, icp.workspace_id, w.name, icp.is_primary, icp.fit_score, icp.created_at
ORDER BY icp.is_primary DESC, icp.fit_score DESC;

-- Campaign Performance View
CREATE OR REPLACE VIEW campaign_performance AS
SELECT
    c.id as campaign_id,
    c.name as campaign_name,
    c.workspace_id,
    w.name as workspace_name,
    c.status,
    c.started_at,
    c.ended_at,
    c.budget_usd,

    -- Move statistics
    (SELECT COUNT(*) FROM public.moves WHERE campaign_id = c.id) as total_moves,
    (SELECT COUNT(*) FROM public.moves WHERE campaign_id = c.id AND status = 'completed') as completed_moves,
    (SELECT COUNT(*) FROM public.moves WHERE campaign_id = c.id AND status = 'active') as active_moves,

    -- Asset statistics
    (SELECT COUNT(*) FROM public.muse_assets ma
     JOIN public.moves m ON ma.move_id = m.id
     WHERE m.campaign_id = c.id) as total_assets,

    -- Duration metrics
    CASE
        WHEN c.started_at IS NOT NULL AND c.ended_at IS NOT NULL
        THEN EXTRACT(DAYS FROM c.ended_at - c.started_at)
        WHEN c.started_at IS NOT NULL
        THEN EXTRACT(DAYS FROM NOW() - c.started_at)
        ELSE NULL
    END as duration_days,

    -- Budget utilization
    CASE
        WHEN c.budget_usd > 0
        THEN ROUND((COALESCE(SUM(ae.cost_usd), 0) / c.budget_usd) * 100, 2)
        ELSE 0
    END as budget_utilization_pct,

    -- Total cost
    COALESCE(SUM(ae.cost_used), 0) as total_cost,

    -- Success metrics
    CASE
        WHEN (SELECT COUNT(*) FROM public.moves WHERE campaign_id = c.id) > 0
        THEN ROUND(((SELECT COUNT(*) FROM public.moves WHERE campaign_id = c.id AND status = 'completed')::NUMERIC /
                   (SELECT COUNT(*) FROM public.moves WHERE campaign_id = c.id)) * 100, 2)
        ELSE 0
    END as move_completion_rate_pct

FROM public.campaigns c
JOIN public.workspaces w ON c.workspace_id = w.id
LEFT JOIN public.moves m ON c.id = m.campaign_id
LEFT JOIN public.agent_executions ae ON m.id = ae.move_id  -- This would need proper join logic
GROUP BY c.id, c.name, c.workspace_id, w.name, c.status, c.started_at, c.ended_at, c.budget_usd
ORDER BY c.created_at DESC;

-- Content Quality View
CREATE OR REPLACE VIEW content_quality_summary AS
SELECT
    ma.workspace_id,
    w.name as workspace_name,
    ma.asset_type,
    COUNT(*) as total_assets,
    COUNT(*) FILTER (WHERE ma.quality_score IS NOT NULL) as assets_with_score,
    COALESCE(AVG(ma.quality_score), 0) as avg_quality_score,
    MIN(ma.quality_score) as min_quality_score,
    MAX(ma.quality_score) as max_quality_score,

    -- Quality distribution
    COUNT(*) FILTER (WHERE ma.quality_score >= 80) as high_quality_count,
    COUNT(*) FILTER (WHERE ma.quality_score >= 60 AND ma.quality_score < 80) as medium_quality_count,
    COUNT(*) FILTER (WHERE ma.quality_score < 60 OR ma.quality_score IS NULL) as low_quality_count,

    -- Recent activity
    MAX(ma.created_at) as last_asset_created,
    COUNT(*) FILTER (WHERE ma.created_at >= NOW() - INTERVAL '7 days') as assets_created_last_7_days,
    COUNT(*) FILTER (WHERE ma.created_at >= NOW() - INTERVAL '30 days') as assets_created_last_30_days

FROM public.muse_assets ma
JOIN public.workspaces w ON ma.workspace_id = w.id
GROUP BY ma.workspace_id, w.name, ma.asset_type
ORDER BY avg_quality_score DESC;

-- Daily Wins Performance View
CREATE OR REPLACE VIEW daily_wins_performance AS
SELECT
    dw.workspace_id,
    w.name as workspace_name,
    DATE_TRUNC('week', dw.win_date) as week_start,
    dw.platform,

    -- Content metrics
    COUNT(*) as total_wins,
    COUNT(*) FILTER (WHERE dw.status = 'posted') as posted_wins,
    COUNT(*) FILTER (WHERE dw.status = 'idea') as idea_wins,

    -- Engagement metrics
    COALESCE(AVG(dw.estimated_minutes), 0) as avg_estimated_minutes,
    COALESCE(SUM(dw.estimated_minutes), 0) as total_estimated_minutes,

    -- Quality metrics
    COALESCE(AVG(dw.relevance_score), 0) as avg_relevance_score,
    MAX(dw.relevance_score) as max_relevance_score,

    -- Trend analysis
    COUNT(*) FILTER (WHERE dw.win_date >= NOW() - INTERVAL '7 days') as wins_last_7_days,
    COUNT(*) FILTER (WHERE dw.win_date >= NOW() - INTERVAL '30 days') as wins_last_30_days,

    -- Conversion rate (ideas to posted)
    CASE
        WHEN COUNT(*) FILTER (WHERE dw.status = 'idea') > 0
        THEN ROUND((COUNT(*) FILTER (WHERE dw.status = 'posted')::NUMERIC /
                   COUNT(*) FILTER (WHERE dw.status = 'idea')) * 100, 2)
        ELSE 0
    END as idea_to_posted_conversion_pct

FROM public.daily_wins dw
JOIN public.workspaces w ON dw.workspace_id = w.id
GROUP BY dw.workspace_id, w.name, DATE_TRUNC('week', dw.win_date), dw.platform
ORDER BY week_start DESC, total_wins DESC;

-- Blackbox Strategy Performance View
CREATE OR REPLACE VIEW blackbox_strategy_performance AS
SELECT
    bs.workspace_id,
    w.name as workspace_name,
    bs.focus_area,
    bs.risk_level,

    -- Strategy counts
    COUNT(*) as total_strategies,
    COUNT(*) FILTER (WHERE bs.status = 'proposed') as proposed_strategies,
    COUNT(*) FILTER (WHERE bs.status = 'accepted') as accepted_strategies,
    COUNT(*) FILTER (WHERE bs.converted_move_id IS NOT NULL) as converted_strategies,

    -- Risk analysis
    COALESCE(AVG(bs.risk_level), 0) as avg_risk_level,
    MIN(bs.risk_level) as min_risk_level,
    MAX(bs.risk_level) as max_risk_level,

    -- Conversion metrics
    CASE
        WHEN COUNT(*) > 0
        THEN ROUND((COUNT(*) FILTER (WHERE bs.converted_move_id IS NOT NULL)::NUMERIC / COUNT(*)) * 100, 2)
        ELSE 0
    END as conversion_rate_pct,

    -- Success of converted strategies
    COUNT(*) FILTER (WHERE bs.converted_move_id IS NOT NULL) as converted_count,
    COUNT(*) FILTER (
        WHERE bs.converted_move_id IS NOT NULL
        AND EXISTS(SELECT 1 FROM public.moves m WHERE m.id = bs.converted_move_id AND m.status = 'completed')
    ) as successful_conversions,

    -- Recent activity
    MAX(bs.created_at) as last_strategy_proposed,
    COUNT(*) FILTER (WHERE bs.created_at >= NOW() - INTERVAL '30 days') as strategies_last_30_days

FROM public.blackbox_strategies bs
JOIN public.workspaces w ON bs.workspace_id = w.id
GROUP BY bs.workspace_id, w.name, bs.focus_area, bs.risk_level
ORDER BY conversion_rate_pct DESC, total_strategies DESC;

-- System Health View
CREATE OR REPLACE VIEW system_health AS
SELECT
    -- User statistics
    (SELECT COUNT(*) FROM public.users) as total_users,
    (SELECT COUNT(*) FROM public.users WHERE created_at >= NOW() - INTERVAL '7 days') as new_users_last_7_days,
    (SELECT COUNT(*) FROM public.users WHERE created_at >= NOW() - INTERVAL '30 days') as new_users_last_30_days,

    -- Workspace statistics
    (SELECT COUNT(*) FROM public.workspaces) as total_workspaces,
    (SELECT COUNT(*) FROM public.workspaces WHERE created_at >= NOW() - INTERVAL '7 days') as new_workspaces_last_7_days,

    -- Subscription distribution
    (SELECT COUNT(*) FROM public.users WHERE subscription_tier = 'free') as free_users,
    (SELECT COUNT(*) FROM public.users WHERE subscription_tier = 'starter') as starter_users,
    (SELECT COUNT(*) FROM public.users WHERE subscription_tier = 'pro' OR subscription_tier = 'growth') as pro_users,
    (SELECT COUNT(*) FROM public.users WHERE subscription_tier = 'enterprise') as enterprise_users,

    -- Content statistics
    (SELECT COUNT(*) FROM public.icp_profiles) as total_icps,
    (SELECT COUNT(*) FROM public.moves) as total_moves,
    (SELECT COUNT(*) FROM public.campaigns) as total_campaigns,
    (SELECT COUNT(*) FROM public.muse_assets) as total_assets,

    -- Usage statistics
    (SELECT COALESCE(SUM(tokens_used), 0) FROM public.usage_records
     WHERE period_start = DATE_TRUNC('month', NOW())) as current_month_tokens,
    (SELECT COALESCE(SUM(cost_usd), 0) FROM public.usage_records
     WHERE period_start = DATE_TRUNC('month', NOW())) as current_month_cost,

    -- Agent execution statistics
    (SELECT COUNT(*) FROM public.agent_executions WHERE created_at >= NOW() - INTERVAL '24 hours') as executions_last_24h,
    (SELECT COUNT(*) FROM public.agent_executions WHERE created_at >= NOW() - INTERVAL '7 days') as executions_last_7_days,
    (SELECT COALESCE(AVG(tokens_used), 0) FROM public.agent_executions WHERE created_at >= NOW() - INTERVAL '24 hours') as avg_tokens_per_execution_24h,

    -- Error rates
    (SELECT COUNT(*) FROM public.agent_executions WHERE created_at >= NOW() - INTERVAL '24 hours' AND status = 'failed') as failed_executions_24h,
    CASE
        WHEN (SELECT COUNT(*) FROM public.agent_executions WHERE created_at >= NOW() - INTERVAL '24 hours') > 0
        THEN ROUND(((SELECT COUNT(*) FROM public.agent_executions WHERE created_at >= NOW() - INTERVAL '24 hours' AND status = 'failed')::NUMERIC /
                   (SELECT COUNT(*) FROM public.agent_executions WHERE created_at >= NOW() - INTERVAL '24 hours')) * 100, 2)
        ELSE 0
    END as error_rate_24h_pct;

-- Grant permissions for views
GRANT SELECT ON workspace_summary TO authenticated;
GRANT SELECT ON usage_summary TO authenticated;
GRANT SELECT ON agent_performance TO authenticated;
GRANT SELECT ON icp_performance TO authenticated;
GRANT SELECT ON campaign_performance TO authenticated;
GRANT SELECT ON content_quality_summary TO authenticated;
GRANT SELECT ON daily_wins_performance TO authenticated;
GRANT SELECT ON blackbox_strategy_performance TO authenticated;
GRANT SELECT ON system_health TO authenticated;
