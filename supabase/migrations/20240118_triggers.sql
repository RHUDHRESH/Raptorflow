-- Database triggers for automated operations
-- Migration: 20240118_triggers.sql

-- Trigger function to update updated_at column (general purpose)
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at triggers to all tables that have updated_at column
CREATE TRIGGER users_updated_at
    BEFORE UPDATE ON public.users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER workspaces_updated_at
    BEFORE UPDATE ON public.workspaces
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER foundations_updated_at
    BEFORE UPDATE ON public.foundations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER icp_profiles_updated_at
    BEFORE UPDATE ON public.icp_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER moves_updated_at
    BEFORE UPDATE ON public.moves
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER campaigns_updated_at
    BEFORE UPDATE ON public.campaigns
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER muse_assets_updated_at
    BEFORE UPDATE ON public.muse_assets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER blackbox_strategies_updated_at
    BEFORE UPDATE ON public.blackbox_strategies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER daily_wins_updated_at
    BEFORE UPDATE ON public.daily_wins
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER competitor_profiles_updated_at
    BEFORE UPDATE ON public.competitor_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER subscriptions_updated_at
    BEFORE UPDATE ON public.subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER invoices_updated_at
    BEFORE UPDATE ON public.invoices
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER api_keys_updated_at
    BEFORE UPDATE ON public.api_keys
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Trigger to handle new user creation from Supabase auth
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    -- Insert user profile
    INSERT INTO public.users (id, email, full_name)
    VALUES (
        NEW.id,
        NEW.email,
        NEW.raw_user_meta_data->>'full_name'
    )
    ON CONFLICT (id) DO UPDATE SET
        email = EXCLUDED.email,
        full_name = EXCLUDED.full_name,
        updated_at = NOW();

    -- Create default workspace
    INSERT INTO public.workspaces (user_id, name, slug)
    VALUES (
        NEW.id,
        COALESCE(
            NEW.raw_user_meta_data->>'workspace_name',
            CONCAT(SPLIT_PART(NEW.email, '@', 1), '''s Workspace')
        ),
        CONCAT('ws-', LEFT(NEW.id::TEXT, 8))
    )
    ON CONFLICT (user_id) DO NOTHING;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Drop and recreate trigger to avoid conflicts
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION handle_new_user();

-- Trigger to update foundation summary when related data changes
CREATE OR REPLACE FUNCTION update_foundation_summary()
RETURNS TRIGGER AS $$
DECLARE
    foundation_record RECORD;
    new_summary TEXT;
BEGIN
    -- Get foundation data
    SELECT * INTO foundation_record
    FROM public.foundations
    WHERE id = NEW.foundation_id;

    IF foundation_record IS NOT NULL THEN
        -- Generate new summary based on foundation data
        new_summary := CONCAT(
            COALESCE(foundation_record.company_name, 'Unknown Company'),
            ' is a ',
            COALESCE(foundation_record.industry, 'business'),
            ' focused on ',
            COALESCE(foundation_record.target_market, 'their market'),
            '. Mission: ',
            COALESCE(foundation_record.mission, 'To provide value'),
            '. Vision: ',
            COALESCE(foundation_record.vision, 'To be the best')
        );

        -- Update foundation summary
        UPDATE public.foundations
        SET summary = new_summary
        WHERE id = foundation_record.id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for foundation summary updates
CREATE TRIGGER foundation_icp_trigger
    AFTER INSERT OR UPDATE ON public.icp_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_foundation_summary();

-- Trigger to validate ICP count limit (max 3 per workspace)
CREATE OR REPLACE FUNCTION validate_icp_limit()
RETURNS TRIGGER AS $$
DECLARE
    icp_count INTEGER;
BEGIN
    -- Count existing ICPs in workspace (excluding current record for updates)
    SELECT COUNT(*) INTO icp_count
    FROM public.icp_profiles
    WHERE workspace_id = NEW.workspace_id
    AND (TG_OP = 'INSERT' OR id != NEW.id);

    -- Check limit
    IF icp_count >= 3 THEN
        RAISE EXCEPTION 'Maximum of 3 ICP profiles allowed per workspace. Current count: %', icp_count;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply ICP limit validation
CREATE TRIGGER validate_icp_count_insert
    BEFORE INSERT ON public.icp_profiles
    FOR EACH ROW
    EXECUTE FUNCTION validate_icp_limit();

CREATE TRIGGER validate_icp_count_update
    BEFORE UPDATE ON public.icp_profiles
    FOR EACH ROW
    EXECUTE FUNCTION validate_icp_limit();

-- Trigger to log data changes for audit
CREATE OR REPLACE FUNCTION audit_data_changes()
RETURNS TRIGGER AS $$
DECLARE
    workspace_id UUID;
    user_id UUID;
    audit_log_id UUID;
BEGIN
    -- Extract workspace_id and user_id based on table
    CASE TG_TABLE_NAME
        WHEN 'users' THEN
            workspace_id := NULL;
            user_id := NEW.id;
        WHEN 'workspaces' THEN
            workspace_id := NEW.id;
            user_id := NEW.user_id;
        WHEN 'foundations' THEN
            workspace_id := NEW.workspace_id;
            user_id := (SELECT user_id FROM public.workspaces WHERE id = NEW.workspace_id);
        WHEN 'icp_profiles' THEN
            workspace_id := NEW.workspace_id;
            user_id := (SELECT user_id FROM public.workspaces WHERE id = NEW.workspace_id);
        WHEN 'moves' THEN
            workspace_id := NEW.workspace_id;
            user_id := (SELECT user_id FROM public.workspaces WHERE id = NEW.workspace_id);
        WHEN 'campaigns' THEN
            workspace_id := NEW.workspace_id;
            user_id := (SELECT user_id FROM public.workspaces WHERE id = NEW.workspace_id);
        WHEN 'muse_assets' THEN
            workspace_id := NEW.workspace_id;
            user_id := (SELECT user_id FROM public.workspaces WHERE id = NEW.workspace_id);
        WHEN 'blackbox_strategies' THEN
            workspace_id := NEW.workspace_id;
            user_id := (SELECT user_id FROM public.workspaces WHERE id = NEW.workspace_id);
        WHEN 'daily_wins' THEN
            workspace_id := NEW.workspace_id;
            user_id := (SELECT user_id FROM public.workspaces WHERE id = NEW.workspace_id);
        WHEN 'competitor_profiles' THEN
            workspace_id := NEW.workspace_id;
            user_id := (SELECT user_id FROM public.workspaces WHERE id = NEW.workspace_id);
        ELSE
            workspace_id := NULL;
            user_id := NULL;
    END CASE;

    -- Log the change if we have workspace_id
    IF workspace_id IS NOT NULL THEN
        audit_log_id := log_data_change(
            p_workspace_id := workspace_id,
            p_table_name := TG_TABLE_NAME,
            p_operation := TG_OP,
            p_record_id := COALESCE(NEW.id, OLD.id),
            p_old_values := CASE WHEN TG_OP = 'DELETE' THEN to_jsonb(OLD) ELSE NULL END,
            p_new_values := CASE WHEN TG_OP != 'DELETE' THEN to_jsonb(NEW) ELSE NULL END,
            p_user_id := user_id
        );
    END IF;

    -- Return the appropriate record
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Apply audit triggers to key tables
CREATE TRIGGER audit_users_changes
    AFTER INSERT OR UPDATE OR DELETE ON public.users
    FOR EACH ROW
    EXECUTE FUNCTION audit_data_changes();

CREATE TRIGGER audit_workspaces_changes
    AFTER INSERT OR UPDATE OR DELETE ON public.workspaces
    FOR EACH ROW
    EXECUTE FUNCTION audit_data_changes();

CREATE TRIGGER audit_foundations_changes
    AFTER INSERT OR UPDATE OR DELETE ON public.foundations
    FOR EACH ROW
    EXECUTE FUNCTION audit_data_changes();

CREATE TRIGGER audit_icp_profiles_changes
    AFTER INSERT OR UPDATE OR DELETE ON public.icp_profiles
    FOR EACH ROW
    EXECUTE FUNCTION audit_data_changes();

CREATE TRIGGER audit_moves_changes
    AFTER INSERT OR UPDATE OR DELETE ON public.moves
    FOR EACH ROW
    EXECUTE FUNCTION audit_data_changes();

CREATE TRIGGER audit_campaigns_changes
    AFTER INSERT OR UPDATE OR DELETE ON public.campaigns
    FOR EACH ROW
    EXECUTE FUNCTION audit_data_changes();

CREATE TRIGGER audit_muse_assets_changes
    AFTER INSERT OR UPDATE OR DELETE ON public.muse_assets
    FOR EACH ROW
    EXECUTE FUNCTION audit_data_changes();

CREATE TRIGGER audit_blackbox_strategies_changes
    AFTER INSERT OR UPDATE OR DELETE ON public.blackbox_strategies
    FOR EACH ROW
    EXECUTE FUNCTION audit_data_changes();

CREATE TRIGGER audit_daily_wins_changes
    AFTER INSERT OR UPDATE OR DELETE ON public.daily_wins
    FOR EACH ROW
    EXECUTE FUNCTION audit_data_changes();

CREATE TRIGGER audit_competitor_profiles_changes
    AFTER INSERT OR UPDATE OR DELETE ON public.competitor_profiles
    FOR EACH ROW
    EXECUTE FUNCTION audit_data_changes();

-- Trigger to update usage when agent execution completes
CREATE OR REPLACE FUNCTION update_usage_on_execution()
RETURNS TRIGGER AS $$
DECLARE
    workspace_id UUID;
    user_id UUID;
BEGIN
    -- Only update usage when execution is completed
    IF NEW.status = 'completed' AND OLD.status != 'completed' THEN
        workspace_id := NEW.workspace_id;
        user_id := NEW.user_id;

        -- Increment usage
        PERFORM increment_usage(
            workspace_id := workspace_id,
            tokens := COALESCE(NEW.tokens_used, 0),
            cost_usd := COALESCE(NEW.cost_usd, 0),
            agent_name := NEW.agent_name
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply usage update trigger
CREATE TRIGGER update_usage_on_agent_execution
    AFTER UPDATE ON public.agent_executions
    FOR EACH ROW
    EXECUTE FUNCTION update_usage_on_execution();

-- Trigger to validate subscription limits before expensive operations
CREATE OR REPLACE FUNCTION check_subscription_limits_trigger()
RETURNS TRIGGER AS $$
DECLARE
    limits RECORD;
    estimated_tokens INTEGER := 1000; -- Default estimate
    estimated_cost DECIMAL(10,6) := 0.01; -- Default estimate
BEGIN
    -- Get estimated tokens/cost based on operation type
    CASE TG_TABLE_NAME
        WHEN 'agent_executions' THEN
            estimated_tokens := 5000;
            estimated_cost := 0.05;
        WHEN 'muse_assets' THEN
            estimated_tokens := 2000;
            estimated_cost := 0.02;
        WHEN 'moves' THEN
            estimated_tokens := 3000;
            estimated_cost := 0.03;
        ELSE
            estimated_tokens := 1000;
            estimated_cost := 0.01;
    END CASE;

    -- Check limits
    SELECT * INTO limits
    FROM check_subscription_limits(NEW.workspace_id, estimated_tokens, estimated_cost)
    LIMIT 1;

    -- Raise exception if limits would be exceeded
    IF NOT limits.allowed THEN
        RAISE EXCEPTION 'Subscription limits would be exceeded. Current: % tokens, $% cost. Limit: % tokens, $% cost. Upgrade your plan at https://raptorflow.app/billing',
            limits.current_tokens,
            limits.current_cost,
            limits.limit_tokens,
            limits.limit_cost;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply subscription limit checks
CREATE TRIGGER check_limits_before_agent_execution
    BEFORE INSERT ON public.agent_executions
    FOR EACH ROW
    EXECUTE FUNCTION check_subscription_limits_trigger();

CREATE TRIGGER check_limits_before_muse_asset_creation
    BEFORE INSERT ON public.muse_assets
    FOR EACH ROW
    EXECUTE FUNCTION check_subscription_limits_trigger();

CREATE TRIGGER check_limits_before_move_creation
    BEFORE INSERT ON public.moves
    FOR EACH ROW
    EXECUTE FUNCTION check_subscription_limits_trigger();

-- Trigger to automatically set primary ICP when only one exists
CREATE OR REPLACE FUNCTION auto_set_primary_icp()
RETURNS TRIGGER AS $$
DECLARE
    icp_count INTEGER;
BEGIN
    -- Count ICPs in workspace after the operation
    SELECT COUNT(*) INTO icp_count
    FROM public.icp_profiles
    WHERE workspace_id = NEW.workspace_id;

    -- If this is the first ICP, set it as primary
    IF icp_count = 1 THEN
        UPDATE public.icp_profiles
        SET is_primary = true
        WHERE id = NEW.id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply auto-primary ICP trigger
CREATE TRIGGER auto_set_primary_icp_trigger
    AFTER INSERT ON public.icp_profiles
    FOR EACH ROW
    EXECUTE FUNCTION auto_set_primary_icp();

-- Trigger to update campaign status based on moves
CREATE OR REPLACE FUNCTION update_campaign_status_from_moves()
RETURNS TRIGGER AS $$
DECLARE
    campaign_moves RECORD;
    active_count INTEGER;
    completed_count INTEGER;
    total_count INTEGER;
BEGIN
    -- Only update if move belongs to a campaign
    IF NEW.campaign_id IS NOT NULL THEN
        -- Get move statistics for this campaign
        SELECT
            COUNT(*) as total_count,
            COUNT(*) FILTER (WHERE status = 'active') as active_count,
            COUNT(*) FILTER (WHERE status = 'completed') as completed_count
        INTO total_count, active_count, completed_count
        FROM public.moves
        WHERE campaign_id = NEW.campaign_id;

        -- Update campaign status based on move statuses
        IF active_count > 0 THEN
            UPDATE public.campaigns
            SET status = 'active'
            WHERE id = NEW.campaign_id;
        ELSIF completed_count = total_count AND total_count > 0 THEN
            UPDATE public.campaigns
            SET status = 'completed',
                ended_at = NOW()
            WHERE id = NEW.campaign_id;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply campaign status update trigger
CREATE TRIGGER update_campaign_status_from_moves_trigger
    AFTER UPDATE ON public.moves
    FOR EACH ROW
    EXECUTE FUNCTION update_campaign_status_from_moves();

-- Trigger to validate workspace ownership
CREATE OR REPLACE FUNCTION validate_workspace_ownership()
RETURNS TRIGGER AS $$
DECLARE
    owner_id UUID;
BEGIN
    -- Get workspace owner
    SELECT user_id INTO owner_id
    FROM public.workspaces
    WHERE id = NEW.workspace_id;

    -- Validate ownership
    IF owner_id IS NULL THEN
        RAISE EXCEPTION 'Workspace % not found', NEW.workspace_id;
    END IF;

    IF owner_id != auth.uid() THEN
        RAISE EXCEPTION 'Access denied: User does not own workspace %', NEW.workspace_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Apply workspace ownership validation to key tables
CREATE TRIGGER validate_foundation_workspace_ownership
    BEFORE INSERT OR UPDATE ON public.foundations
    FOR EACH ROW
    EXECUTE FUNCTION validate_workspace_ownership();

CREATE TRIGGER validate_icp_workspace_ownership
    BEFORE INSERT OR UPDATE ON public.icp_profiles
    FOR EACH ROW
    EXECUTE FUNCTION validate_workspace_ownership();

CREATE TRIGGER validate_moves_workspace_ownership
    BEFORE INSERT OR UPDATE ON public.moves
    FOR EACH ROW
    EXECUTE FUNCTION validate_workspace_ownership();

CREATE TRIGGER validate_campaigns_workspace_ownership
    BEFORE INSERT OR UPDATE ON public.campaigns
    FOR EACH ROW
    EXECUTE FUNCTION validate_workspace_ownership();

-- Trigger to handle soft deletes (mark as deleted instead of actual delete)
CREATE OR REPLACE FUNCTION soft_delete()
RETURNS TRIGGER AS $$
BEGIN
    -- Add deleted_at timestamp instead of deleting
    NEW.deleted_at = NOW();
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Note: Soft delete triggers would be added to specific tables as needed
-- This is a template that can be applied when implementing soft deletes

-- Function to enable/disable triggers for maintenance
CREATE OR REPLACE FUNCTION toggle_table_triggers(
    table_name TEXT,
    enable BOOLEAN DEFAULT true
)
RETURNS TEXT AS $$
DECLARE
    result TEXT;
BEGIN
    IF enable THEN
        EXECUTE format('ALTER TABLE %I ENABLE TRIGGER ALL', table_name);
        result := format('Enabled all triggers on table %s', table_name);
    ELSE
        EXECUTE format('ALTER TABLE %I DISABLE TRIGGER ALL', table_name);
        result := format('Disabled all triggers on table %s', table_name);
    END IF;

    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions for trigger management
GRANT EXECUTE ON FUNCTION toggle_table_triggers(TEXT, BOOLEAN) TO authenticated;
