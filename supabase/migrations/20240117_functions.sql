-- Helper functions for database operations
-- Migration: 20240117_functions.sql

-- Function to get workspace ID for authenticated user
CREATE OR REPLACE FUNCTION get_workspace_id()
RETURNS UUID AS $$
DECLARE
    workspace_id UUID;
BEGIN
    -- Get the first workspace for the authenticated user
    SELECT id INTO workspace_id
    FROM public.workspaces
    WHERE user_id = auth.uid()
    LIMIT 1;

    RETURN workspace_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if user owns workspace
CREATE OR REPLACE FUNCTION is_workspace_owner(workspace_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    is_owner BOOLEAN := FALSE;
BEGIN
    -- Check if the authenticated user owns the workspace
    SELECT EXISTS(
        SELECT 1
        FROM public.workspaces
        WHERE id = workspace_id
        AND user_id = auth.uid()
    ) INTO is_owner;

    RETURN is_owner;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to increment usage tracking
CREATE OR REPLACE FUNCTION increment_usage(
    workspace_id UUID,
    tokens INTEGER DEFAULT 0,
    cost_usd DECIMAL(10,6) DEFAULT 0,
    agent_name TEXT DEFAULT NULL
)
RETURNS VOID AS $$
DECLARE
    current_period_start TIMESTAMPTZ;
    current_period_end TIMESTAMPTZ;
    usage_record_id UUID;
    agent_breakdown JSONB;
BEGIN
    -- Validate workspace ownership
    IF NOT is_workspace_owner(workspace_id) THEN
        RAISE EXCEPTION 'Access denied: User does not own workspace %', workspace_id;
    END IF;

    -- Get current period (monthly)
    current_period_start := DATE_TRUNC('month', NOW());
    current_period_end := current_period_start + INTERVAL '1 month' - INTERVAL '1 microsecond';

    -- Build agent breakdown
    agent_breakdown := COALESCE(
        jsonb_build_object(agent_name, tokens),
        '{}'::jsonb
    );

    -- Check if usage record exists for this period
    SELECT id INTO usage_record_id
    FROM public.usage_records
    WHERE workspace_id = workspace_id
    AND period_start = current_period_start
    AND period_end = current_period_end;

    IF usage_record_id IS NOT NULL THEN
        -- Update existing record
        UPDATE public.usage_records
        SET
            tokens_used = tokens_used + tokens,
            cost_usd = cost_usd + cost_usd,
            agent_breakdown = agent_breakdown || agent_breakdown
        WHERE id = usage_record_id;
    ELSE
        -- Create new record
        INSERT INTO public.usage_records (
            workspace_id,
            period_start,
            period_end,
            tokens_used,
            cost_usd,
            agent_breakdown
        ) VALUES (
            workspace_id,
            current_period_start,
            current_period_end,
            tokens,
            cost_usd,
            agent_breakdown
        );
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get current usage for workspace
CREATE OR REPLACE FUNCTION get_current_usage(workspace_id UUID)
RETURNS TABLE(
    tokens_used BIGINT,
    cost_usd DECIMAL(10,6),
    period_start TIMESTAMPTZ,
    period_end TIMESTAMPTZ,
    agent_breakdown JSONB
) AS $$
BEGIN
    -- Validate workspace ownership
    IF NOT is_workspace_owner(workspace_id) THEN
        RAISE EXCEPTION 'Access denied: User does not own workspace %', workspace_id;
    END IF;

    RETURN QUERY
    SELECT
        ur.tokens_used,
        ur.cost_usd,
        ur.period_start,
        ur.period_end,
        ur.agent_breakdown
    FROM public.usage_records ur
    WHERE ur.workspace_id = workspace_id
    AND ur.period_start = DATE_TRUNC('month', NOW())
    AND ur.period_end = DATE_TRUNC('month', NOW()) + INTERVAL '1 month' - INTERVAL '1 microsecond';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check subscription limits
CREATE OR REPLACE FUNCTION check_subscription_limits(
    workspace_id UUID,
    required_tokens INTEGER DEFAULT 0,
    required_cost DECIMAL(10,6) DEFAULT 0
)
RETURNS TABLE(
    allowed BOOLEAN,
    current_tokens BIGINT,
    current_cost DECIMAL(10,6),
    limit_tokens BIGINT,
    limit_cost DECIMAL(10,6),
    subscription_tier TEXT
) AS $$
DECLARE
    sub_record RECORD;
    usage_record RECORD;
    token_limit BIGINT := 100000; -- Default free tier limit
    cost_limit DECIMAL(10,6) := 10.00; -- Default free tier limit
BEGIN
    -- Validate workspace ownership
    IF NOT is_workspace_owner(workspace_id) THEN
        RAISE EXCEPTION 'Access denied: User does not own workspace %', workspace_id;
    END IF;

    -- Get subscription info
    SELECT s.plan, u.subscription_tier INTO sub_record
    FROM public.subscriptions s
    JOIN public.workspaces w ON s.workspace_id = w.id
    JOIN public.users u ON w.user_id = u.id
    WHERE s.workspace_id = workspace_id
    AND s.status = 'active'
    LIMIT 1;

    -- Set limits based on subscription tier
    IF sub_record.plan = 'free' THEN
        token_limit := 100000;
        cost_limit := 10.00;
    ELSIF sub_record.plan = 'starter' THEN
        token_limit := 500000;
        cost_limit := 50.00;
    ELSIF sub_record.plan = 'pro' OR sub_record.plan = 'growth' THEN
        token_limit := 2000000;
        cost_limit := 200.00;
    ELSIF sub_record.plan = 'enterprise' THEN
        token_limit := 10000000;
        cost_limit := 1000.00;
    END IF;

    -- Get current usage
    SELECT tokens_used, cost_usd INTO usage_record
    FROM get_current_usage(workspace_id)
    LIMIT 1;

    -- Check if adding required usage would exceed limits
    RETURN QUERY
    SELECT
        (COALESCE(usage_record.tokens_used, 0) + required_tokens <= token_limit
         AND COALESCE(usage_record.cost_usd, 0) + required_cost <= cost_limit) as allowed,
        COALESCE(usage_record.tokens_used, 0) as current_tokens,
        COALESCE(usage_record.cost_usd, 0) as current_cost,
        token_limit as limit_tokens,
        cost_limit as limit_cost,
        COALESCE(sub_record.plan, 'free') as subscription_tier;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to generate unique slug
CREATE OR REPLACE FUNCTION generate_unique_slug(base_name TEXT)
RETURNS TEXT AS $$
DECLARE
    slug TEXT;
    counter INTEGER := 1;
    original_slug TEXT;
BEGIN
    -- Convert to lowercase and replace spaces with hyphens
    original_slug := lower(regexp_replace(base_name, '[^a-zA-Z0-9\s]', '', 'g'));
    original_slug := regexp_replace(original_slug, '\s+', '-', 'g');
    slug := original_slug;

    -- Check if slug exists, add counter if needed
    WHILE EXISTS(SELECT 1 FROM public.workspaces WHERE slug = slug) LOOP
        slug := original_slug || '-' || counter;
        counter := counter + 1;

        -- Prevent infinite loop
        IF counter > 1000 THEN
            RAISE EXCEPTION 'Unable to generate unique slug for %', base_name;
        END IF;
    END LOOP;

    RETURN slug;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get primary ICP for workspace
CREATE OR REPLACE FUNCTION get_primary_icp(workspace_id UUID)
RETURNS UUID AS $$
DECLARE
    primary_icp_id UUID;
BEGIN
    -- Validate workspace ownership
    IF NOT is_workspace_owner(workspace_id) THEN
        RAISE EXCEPTION 'Access denied: User does not own workspace %', workspace_id;
    END IF;

    -- Get primary ICP
    SELECT id INTO primary_icp_id
    FROM public.icp_profiles
    WHERE workspace_id = workspace_id
    AND is_primary = true
    LIMIT 1;

    -- If no primary ICP, get the first one
    IF primary_icp_id IS NULL THEN
        SELECT id INTO primary_icp_id
        FROM public.icp_profiles
        WHERE workspace_id = workspace_id
        ORDER BY created_at
        LIMIT 1;
    END IF;

    RETURN primary_icp_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to set primary ICP
CREATE OR REPLACE FUNCTION set_primary_icp(workspace_id UUID, icp_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    -- Validate workspace ownership
    IF NOT is_workspace_owner(workspace_id) THEN
        RAISE EXCEPTION 'Access denied: User does not own workspace %', workspace_id;
    END IF;

    -- Validate ICP belongs to workspace
    IF NOT EXISTS(SELECT 1 FROM public.icp_profiles WHERE id = icp_id AND workspace_id = workspace_id) THEN
        RAISE EXCEPTION 'ICP % does not belong to workspace %', icp_id, workspace_id;
    END IF;

    -- Remove primary flag from all ICPs in workspace
    UPDATE public.icp_profiles
    SET is_primary = false
    WHERE workspace_id = workspace_id;

    -- Set new primary ICP
    UPDATE public.icp_profiles
    SET is_primary = true
    WHERE id = icp_id;

    RETURN true;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to count ICPs in workspace
CREATE OR REPLACE FUNCTION count_icps(workspace_id UUID)
RETURNS INTEGER AS $$
DECLARE
    icp_count INTEGER;
BEGIN
    -- Validate workspace ownership
    IF NOT is_workspace_owner(workspace_id) THEN
        RAISE EXCEPTION 'Access denied: User does not own workspace %', workspace_id;
    END IF;

    SELECT COUNT(*) INTO icp_count
    FROM public.icp_profiles
    WHERE workspace_id = workspace_id;

    RETURN icp_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get workspace statistics
CREATE OR REPLACE FUNCTION get_workspace_stats(workspace_id UUID)
RETURNS TABLE(
    stat_name TEXT,
    stat_value BIGINT
) AS $$
BEGIN
    -- Validate workspace ownership
    IF NOT is_workspace_owner(workspace_id) THEN
        RAISE EXCEPTION 'Access denied: User does not own workspace %', workspace_id;
    END IF;

    RETURN QUERY
    SELECT 'icp_profiles'::TEXT, COUNT(*)::BIGINT
    FROM public.icp_profiles
    WHERE workspace_id = workspace_id

    UNION ALL

    SELECT 'moves'::TEXT, COUNT(*)::BIGINT
    FROM public.moves
    WHERE workspace_id = workspace_id

    UNION ALL

    SELECT 'campaigns'::TEXT, COUNT(*)::BIGINT
    FROM public.campaigns
    WHERE workspace_id = workspace_id

    UNION ALL

    SELECT 'muse_assets'::TEXT, COUNT(*)::BIGINT
    FROM public.muse_assets
    WHERE workspace_id = workspace_id

    UNION ALL

    SELECT 'daily_wins'::TEXT, COUNT(*)::BIGINT
    FROM public.daily_wins
    WHERE workspace_id = workspace_id

    UNION ALL

    SELECT 'agent_executions'::TEXT, COUNT(*)::BIGINT
    FROM public.agent_executions
    WHERE workspace_id = workspace_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to search across all content types
CREATE OR REPLACE FUNCTION search_workspace_content(
    workspace_id UUID,
    search_query TEXT,
    content_types TEXT[] DEFAULT ARRAY['icp_profiles', 'moves', 'campaigns', 'muse_assets']
)
RETURNS TABLE(
    content_type TEXT,
    content_id UUID,
    title TEXT,
    summary TEXT,
    relevance_score REAL
) AS $$
BEGIN
    -- Validate workspace ownership
    IF NOT is_workspace_owner(workspace_id) THEN
        RAISE EXCEPTION 'Access denied: User does not own workspace %', workspace_id;
    END IF;

    -- Search ICP profiles
    IF 'icp_profiles' = ANY(content_types) THEN
        RETURN QUERY
        SELECT
            'icp_profiles'::TEXT,
            id,
            name,
            COALESCE(summary, '')::TEXT,
            ts_rank(to_tsvector('english', name || ' ' || COALESCE(summary, '')), plainto_tsquery('english', search_query)) as relevance_score
        FROM public.icp_profiles
        WHERE workspace_id = workspace_id
        AND to_tsvector('english', name || ' ' || COALESCE(summary, '')) @@ plainto_tsquery('english', search_query);
    END IF;

    -- Search moves
    IF 'moves' = ANY(content_types) THEN
        RETURN QUERY
        SELECT
            'moves'::TEXT,
            id,
            name,
            COALESCE(goal, '')::TEXT,
            ts_rank(to_tsvector('english', name || ' ' || COALESCE(goal, '')), plainto_tsquery('english', search_query)) as relevance_score
        FROM public.moves
        WHERE workspace_id = workspace_id
        AND to_tsvector('english', name || ' ' || COALESCE(goal, '')) @@ plainto_tsquery('english', search_query);
    END IF;

    -- Search campaigns
    IF 'campaigns' = ANY(content_types) THEN
        RETURN QUERY
        SELECT
            'campaigns'::TEXT,
            id,
            name,
            COALESCE(description, '')::TEXT,
            ts_rank(to_tsvector('english', name || ' ' || COALESCE(description, '')), plainto_tsquery('english', search_query)) as relevance_score
        FROM public.campaigns
        WHERE workspace_id = workspace_id
        AND to_tsvector('english', name || ' ' || COALESCE(description, '')) @@ plainto_tsquery('english', search_query);
    END IF;

    -- Search muse assets
    IF 'muse_assets' = ANY(content_types) THEN
        RETURN QUERY
        SELECT
            'muse_assets'::TEXT,
            id,
            title,
            COALESCE(content, '')::TEXT,
            ts_rank(to_tsvector('english', title || ' ' || COALESCE(content, '')), plainto_tsquery('english', search_query)) as relevance_score
        FROM public.muse_assets
        WHERE workspace_id = workspace_id
        AND to_tsvector('english', title || ' ' || COALESCE(content, '')) @@ plainto_tsquery('english', search_query);
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to validate email format
CREATE OR REPLACE FUNCTION validate_email(email TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN email ~ '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$';
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to sanitize input text
CREATE OR REPLACE FUNCTION sanitize_input(text_input TEXT)
RETURNS TEXT AS $$
BEGIN
    -- Remove HTML tags and special characters
    RETURN regexp_replace(text_input, '<[^>]*>', '', 'g');
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to generate UUID from string (for consistent IDs)
CREATE OR REPLACE FUNCTION generate_uuid_from_string(input_string TEXT)
RETURNS UUID AS $$
BEGIN
    RETURN uuid_generate_md5(input_string::bytea);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Grant permissions for functions
GRANT EXECUTE ON FUNCTION get_workspace_id() TO authenticated;
GRANT EXECUTE ON FUNCTION is_workspace_owner(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION increment_usage(UUID, INTEGER, DECIMAL(10,6), TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION get_current_usage(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION check_subscription_limits(UUID, INTEGER, DECIMAL(10,6)) TO authenticated;
GRANT EXECUTE ON FUNCTION generate_unique_slug(TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION get_primary_icp(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION set_primary_icp(UUID, UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION count_icps(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION get_workspace_stats(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION search_workspace_content(UUID, TEXT, TEXT[]) TO authenticated;
GRANT EXECUTE ON FUNCTION validate_email(TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION sanitize_input(TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION generate_uuid_from_string(TEXT) TO authenticated;
