-- Database functions for health checks, rate limiting, and monitoring
-- Migration: 20240123_database_functions.sql

-- Function to check if RLS is enabled on a table
CREATE OR REPLACE FUNCTION check_rls_enabled(table_name TEXT)
RETURNS TABLE(relrowsecurity BOOLEAN)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT relrowsecurity
    FROM pg_class
    JOIN pg_namespace ON pg_namespace.oid = pg_class.relnamespace
    WHERE pg_class.relname = table_name AND pg_namespace.nspname = 'public';
END;
$$;

-- Function to check if an index exists
CREATE OR REPLACE FUNCTION check_index_exists(table_name TEXT, column_names TEXT[])
RETURNS TABLE(exists BOOLEAN)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    index_exists BOOLEAN := FALSE;
BEGIN
    -- Check if there's an index on the specified columns
    SELECT EXISTS (
        SELECT 1
        FROM pg_index i
        JOIN pg_class t ON t.oid = i.indrelid
        JOIN pg_class ix ON ix.oid = i.indexrelid
        JOIN pg_namespace n ON n.oid = t.relnamespace
        WHERE t.relname = table_name
        AND n.nspname = 'public'
        AND i.indisvalid = true
        AND array_position(i.indkey, attnum) IS NOT NULL
    ) INTO index_exists;

    RETURN QUERY SELECT index_exists;
END;
$$;

-- Function to get database size
CREATE OR REPLACE FUNCTION get_database_size()
RETURNS TABLE(size_mb NUMERIC)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT pg_database_size(current_database()) / 1024.0 / 1024.0 as size_mb;
END;
$$;

-- Function to get table count
CREATE OR REPLACE FUNCTION get_table_count()
RETURNS TABLE(count INTEGER)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT COUNT(*)
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_type = 'BASE TABLE';
END;
$$;

-- Function to get index count
CREATE OR REPLACE FUNCTION get_index_count()
RETURNS TABLE(count INTEGER)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT COUNT(*)
    FROM pg_indexes
    WHERE schemaname = 'public';
END;
$$;

-- Function to get active connections
CREATE OR REPLACE FUNCTION get_active_connections()
RETURNS TABLE(count INTEGER)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT COUNT(*)
    FROM pg_stat_activity
    WHERE datname = current_database()
    AND state = 'active';
END;
$$;

-- Function to get current usage for a workspace
CREATE OR REPLACE FUNCTION get_current_usage(workspace_id UUID)
RETURNS TABLE(
    tokens_used INTEGER,
    cost_usd DECIMAL(10,6),
    period_start TIMESTAMPTZ,
    period_end TIMESTAMPTZ,
    agent_breakdown JSONB
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    current_period_start TIMESTAMPTZ;
    current_period_end TIMESTAMPTZ;
BEGIN
    -- Get current month period
    current_period_start := date_trunc('month', CURRENT_TIMESTAMP);
    current_period_end := current_period_start + INTERVAL '1 month';

    RETURN QUERY
    SELECT
        COALESCE(SUM(tokens_used), 0) as tokens_used,
        COALESCE(SUM(cost_usd), 0) as cost_usd,
        current_period_start as period_start,
        current_period_end as period_end,
        jsonb_object_agg(agent, total_tokens) as agent_breakdown
    FROM (
        SELECT
            agent_name as agent,
            SUM(tokens_used) as total_tokens,
            SUM(cost_usd) as total_cost
        FROM usage_records
        WHERE workspace_id = get_current_usage.workspace_id
        AND period_start >= current_period_start
        AND period_start < current_period_end
        GROUP BY agent_name
    ) agent_usage;
END;
$$;

-- Function to check subscription limits
CREATE OR REPLACE FUNCTION check_subscription_limits(
    workspace_id UUID,
    required_tokens INTEGER DEFAULT 0,
    required_cost DECIMAL(10,6) DEFAULT 0
)
RETURNS TABLE(
    allowed BOOLEAN,
    limit_tokens INTEGER,
    limit_cost DECIMAL(10,6),
    subscription_tier TEXT
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    user_subscription TEXT;
    token_limit INTEGER;
    cost_limit DECIMAL(10,6);
    current_usage_tokens INTEGER;
    current_usage_cost DECIMAL(10,6);
BEGIN
    -- Get user's subscription tier
    SELECT u.subscription_tier INTO user_subscription
    FROM users u
    JOIN workspaces w ON w.user_id = u.id
    WHERE w.id = check_subscription_limits.workspace_id;

    -- Set limits based on subscription tier
    CASE user_subscription
        WHEN 'free' THEN
            token_limit := 10000;
            cost_limit := 10.0;
        WHEN 'starter' THEN
            token_limit := 50000;
            cost_limit := 50.0;
        WHEN 'growth' THEN
            token_limit := 200000;
            cost_limit := 200.0;
        WHEN 'enterprise' THEN
            token_limit := 1000000;
            cost_limit := 1000.0;
        ELSE
            token_limit := 10000;
            cost_limit := 10.0;
    END CASE;

    -- Get current usage
    SELECT COALESCE(SUM(tokens_used), 0), COALESCE(SUM(cost_usd), 0)
    INTO current_usage_tokens, current_usage_cost
    FROM usage_records
    WHERE workspace_id = check_subscription_limits.workspace_id
    AND period_start >= date_trunc('month', CURRENT_TIMESTAMP);

    -- Check if within limits
    RETURN QUERY
    SELECT
        (current_usage_tokens + required_tokens <= token_limit
         AND current_usage_cost + required_cost <= cost_limit) as allowed,
        token_limit,
        cost_limit,
        COALESCE(user_subscription, 'free') as subscription_tier;
END;
$$;

-- Function to increment usage
CREATE OR REPLACE FUNCTION increment_usage(workspace_id UUID, tokens INTEGER, cost DECIMAL(10,6))
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    INSERT INTO usage_records (
        workspace_id,
        period_start,
        tokens_used,
        cost_usd,
        agent_breakdown,
        created_at
    ) VALUES (
        increment_usage.workspace_id,
        date_trunc('month', CURRENT_TIMESTAMP),
        tokens,
        cost,
        '{}'::jsonb,
        NOW()
    )
    ON CONFLICT (workspace_id, period_start)
    DO UPDATE SET
        tokens_used = usage_records.tokens_used + tokens,
        cost_usd = usage_records.cost_usd + cost,
        updated_at = NOW();
END;
$$;

-- Function to get workspace ID for user (helper function)
CREATE OR REPLACE FUNCTION get_workspace_id()
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    workspace_uuid UUID;
BEGIN
    SELECT id INTO workspace_uuid
    FROM workspaces
    WHERE user_id = auth.uid()
    LIMIT 1;

    RETURN workspace_uuid;
END;
$$;

-- Function to check if user owns workspace
CREATE OR REPLACE FUNCTION is_workspace_owner(workspace_id UUID)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1
        FROM workspaces
        WHERE id = is_workspace_owner.workspace_id
        AND user_id = auth.uid()
    );
END;
$$;

-- Function to record audit log
CREATE OR REPLACE FUNCTION record_audit_log(
    user_id UUID,
    workspace_id UUID,
    action TEXT,
    resource_type TEXT,
    resource_id UUID,
    details JSONB,
    ip_address TEXT,
    user_agent TEXT,
    success BOOLEAN,
    error_message TEXT
)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    INSERT INTO audit_logs (
        user_id,
        workspace_id,
        action,
        resource_type,
        resource_id,
        details,
        ip_address,
        user_agent,
        success,
        error_message,
        created_at
    ) VALUES (
        record_audit_log.user_id,
        record_audit_log.workspace_id,
        record_audit_log.action,
        record_audit_log.resource_type,
        record_audit_log.resource_id,
        record_audit_log.details,
        record_audit_log.ip_address,
        record_audit_log.user_agent,
        record_audit_log.success,
        record_audit_log.error_message,
        NOW()
    );
END;
$$;

-- Function to cleanup old audit logs (older than 1 year)
CREATE OR REPLACE FUNCTION cleanup_old_audit_logs()
RETURNS INTEGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM audit_logs
    WHERE created_at < NOW() - INTERVAL '1 year';

    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    RETURN deleted_count;
END;
$$;

-- Function to get workspace statistics
CREATE OR REPLACE FUNCTION get_workspace_stats(workspace_id UUID)
RETURNS TABLE(
    total_icps INTEGER,
    total_moves INTEGER,
    total_campaigns INTEGER,
    total_assets INTEGER,
    last_activity TIMESTAMPTZ
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    WITH stats AS (
        SELECT
            (SELECT COUNT(*) FROM icp_profiles WHERE workspace_id = get_workspace_stats.workspace_id) as icps,
            (SELECT COUNT(*) FROM moves WHERE workspace_id = get_workspace_stats.workspace_id) as moves,
            (SELECT COUNT(*) FROM campaigns WHERE workspace_id = get_workspace_stats.workspace_id) as campaigns,
            (SELECT COUNT(*) FROM muse_assets WHERE workspace_id = get_workspace_stats.workspace_id) as assets,
            (SELECT MAX(updated_at) FROM (
                SELECT updated_at FROM icp_profiles WHERE workspace_id = get_workspace_stats.workspace_id
                UNION ALL
                SELECT updated_at FROM moves WHERE workspace_id = get_workspace_stats.workspace_id
                UNION ALL
                SELECT updated_at FROM campaigns WHERE workspace_id = get_workspace_stats.workspace_id
                UNION ALL
                SELECT updated_at FROM muse_assets WHERE workspace_id = get_workspace_stats.workspace_id
            ) recent) as last_activity
    )
    SELECT
        icps as total_icps,
        moves as total_moves,
        campaigns as total_campaigns,
        assets as total_assets,
        last_activity
    FROM stats;
END;
$$;

-- Grant execute permissions to authenticated users
GRANT EXECUTE ON FUNCTION check_rls_enabled(TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION check_index_exists(TEXT, TEXT[]) TO authenticated;
GRANT EXECUTE ON FUNCTION get_database_size() TO authenticated;
GRANT EXECUTE ON FUNCTION get_table_count() TO authenticated;
GRANT EXECUTE ON FUNCTION get_index_count() TO authenticated;
GRANT EXECUTE ON FUNCTION get_active_connections() TO authenticated;
GRANT EXECUTE ON FUNCTION get_current_usage(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION check_subscription_limits(UUID, INTEGER, DECIMAL) TO authenticated;
GRANT EXECUTE ON FUNCTION increment_usage(UUID, INTEGER, DECIMAL) TO authenticated;
GRANT EXECUTE ON FUNCTION get_workspace_id() TO authenticated;
GRANT EXECUTE ON FUNCTION is_workspace_owner(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION record_audit_log(UUID, UUID, TEXT, TEXT, UUID, JSONB, TEXT, TEXT, BOOLEAN, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION get_workspace_stats(UUID) TO authenticated;

-- Grant service role permissions for system functions
GRANT EXECUTE ON FUNCTION cleanup_old_audit_logs() TO service_role;
