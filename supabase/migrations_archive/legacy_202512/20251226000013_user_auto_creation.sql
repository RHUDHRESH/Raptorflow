-- RaptorFlow User Account Auto-Creation Trigger
-- Automatically creates workspace and user setup when a new user signs up

-- =====================================
-- USER ACCOUNT AUTO-CREATION
-- =====================================

-- Function to handle new user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    -- 1. Create a workspace for the new user
    INSERT INTO public.workspaces (id, name, slug, created_at, updated_at)
    VALUES (
        gen_random_uuid(),
        NEW.raw_user_meta_data->>'name' || ' Workspace',
        lower(regexp_replace(COALESCE(NEW.raw_user_meta_data->>'name', 'User'), '[^a-zA-Z0-9\s]', '', 'g')),
        now(),
        now()
    )
    RETURNING id INTO workspace_id;

    -- 2. Add user as workspace owner
    INSERT INTO public.workspace_members (tenant_id, user_id, role, created_at)
    VALUES (workspace_id, NEW.id, 'owner', now());

    -- 3. Initialize foundation state
    INSERT INTO public.foundation_state (tenant_id, current_phase, created_at, updated_at)
    VALUES (workspace_id, 'brand_kit', now(), now());

    -- 4. Create default strategy version
    INSERT INTO public.strategy_versions (
        tenant_id,
        name,
        version,
        description,
        status,
        created_at,
        updated_at
    )
    VALUES (
        workspace_id,
        'Default Strategy',
        'v1.0',
        'Initial strategy version for new workspace',
        'active',
        now(),
        now()
    );

    -- 5. Set up user preferences
    INSERT INTO public.user_preferences (
        user_id,
        tenant_id,
        theme,
        language,
        timezone,
        created_at,
        updated_at
    )
    VALUES (
        NEW.id,
        workspace_id,
        'light',
        'en',
        'UTC',
        now(),
        now()
    );

    -- 6. Initialize workspace settings with defaults
    INSERT INTO public.workspace_settings (
        tenant_id,
        features_enabled,
        limits,
        notifications,
        ui_preferences,
        created_at,
        updated_at
    )
    SELECT
        workspace_id,
        setting_value,
        setting_value,
        setting_value,
        setting_value,
        now(),
        now()
    FROM default_workspace_settings;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger for new user signup
CREATE OR REPLACE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- =====================================
-- GOOGLE OAUTH METADATA HANDLING
-- =====================================

-- Function to update user metadata from Google OAuth
CREATE OR REPLACE FUNCTION public.update_user_metadata()
RETURNS TRIGGER AS $$
BEGIN
    -- Update user with Google OAuth metadata
    NEW.raw_user_meta_data = COALESCE(
        NEW.raw_user_meta_data,
        jsonb_build_object(
            'provider', 'google',
            'avatar_url', NEW.raw_user_meta_data->>'avatar_url',
            'full_name', NEW.raw_user_meta_data->>'full_name',
            'email', NEW.email
        )
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger for user metadata updates
CREATE OR REPLACE TRIGGER update_user_metadata_trigger
    BEFORE UPDATE ON auth.users
    FOR EACH ROW
    WHEN (NEW.raw_user_meta_data IS DISTINCT FROM OLD.raw_user_meta_data)
    EXECUTE FUNCTION public.update_user_metadata();

-- =====================================
-- WORKSPACE DEFAULTS
-- =====================================

-- Function to get user's primary workspace
CREATE OR REPLACE FUNCTION public.get_user_workspace(user_uuid UUID)
RETURNS UUID AS $$
DECLARE
    workspace_uuid UUID;
BEGIN
    -- Get the workspace where user is the owner
    SELECT tenant_id INTO workspace_uuid
    FROM workspace_members
    WHERE user_id = user_uuid
    AND role = 'owner'
    LIMIT 1;

    -- If no owner workspace found, get any workspace
    IF workspace_uuid IS NULL THEN
        SELECT tenant_id INTO workspace_uuid
        FROM workspace_members
        WHERE user_id = user_uuid
        LIMIT 1;
    END IF;

    RETURN workspace_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if user has access to workspace
CREATE OR REPLACE FUNCTION public.user_has_workspace_access(user_uuid UUID, workspace_uuid UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM workspace_members
        WHERE user_id = user_uuid
        AND tenant_id = workspace_uuid
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================
-- SESSION HANDLING
-- =====================================

-- Function to create user session data
CREATE OR REPLACE FUNCTION public.create_user_session(user_uuid UUID)
RETURNS JSONB AS $$
DECLARE
    workspace_uuid UUID;
    session_data JSONB;
BEGIN
    -- Get user's primary workspace
    workspace_uuid := get_user_workspace(user_uuid);

    -- Build session data
    session_data := jsonb_build_object(
        'user_id', user_uuid,
        'workspace_id', workspace_uuid,
        'has_workspace', workspace_uuid IS NOT NULL,
        'session_created_at', now()
    );

    RETURN session_data;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================
-- VALIDATION FUNCTIONS
-- =====================================

-- Function to validate user setup completeness
CREATE OR REPLACE FUNCTION public.validate_user_setup(user_uuid UUID)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
    workspace_uuid UUID;
    has_workspace BOOLEAN;
    has_foundation BOOLEAN;
    has_strategy BOOLEAN;
    has_preferences BOOLEAN;
BEGIN
    -- Get user's workspace
    workspace_uuid := get_user_workspace(user_uuid);
    has_workspace := workspace_uuid IS NOT NULL;

    -- Check foundation state
    SELECT EXISTS (
        SELECT 1 FROM foundation_state
        WHERE tenant_id = workspace_uuid
    ) INTO has_foundation;

    -- Check strategy version
    SELECT EXISTS (
        SELECT 1 FROM strategy_versions
        WHERE tenant_id = workspace_uuid
        AND status = 'active'
    ) INTO has_strategy;

    -- Check user preferences
    SELECT EXISTS (
        SELECT 1 FROM user_preferences
        WHERE user_id = user_uuid
    ) INTO has_preferences;

    result := jsonb_build_object(
        'user_id', user_uuid,
        'workspace_id', workspace_uuid,
        'setup_complete', has_workspace AND has_foundation AND has_strategy AND has_preferences,
        'has_workspace', has_workspace,
        'has_foundation', has_foundation,
        'has_strategy', has_strategy,
        'has_preferences', has_preferences,
        'validated_at', now()
    );

    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================
-- CLEANUP FUNCTIONS
-- =====================================

-- Function to handle user deletion (cascade cleanup)
CREATE OR REPLACE FUNCTION public.handle_user_deletion()
RETURNS TRIGGER AS $$
BEGIN
    -- Delete user's workspace memberships
    DELETE FROM workspace_members WHERE user_id = OLD.id;

    -- Delete user preferences
    DELETE FROM user_preferences WHERE user_id = OLD.id;

    -- Note: Workspaces and other data are preserved for audit purposes
    -- In a real application, you might want to handle workspace ownership transfer

    RETURN OLD;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger for user deletion
CREATE OR REPLACE TRIGGER on_auth_user_deleted
    BEFORE DELETE ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_user_deletion();
