-- Transactional Workspace Creation
-- Migration: 20260119_transactional_onboarding.sql

CREATE OR REPLACE FUNCTION public.create_workspace_secure(
    p_name TEXT,
    p_slug TEXT,
    p_user_id UUID,
    p_audit_data JSONB
) RETURNS JSONB AS $$
DECLARE
    v_workspace_id UUID;
    v_onboarding_status TEXT;
    v_workspace RECORD;
BEGIN
    -- 1. Check current user onboarding status
    SELECT onboarding_status INTO v_onboarding_status FROM public.users WHERE id = p_user_id;

    IF v_onboarding_status != 'pending_workspace' THEN
        RAISE EXCEPTION 'Invalid onboarding status: %', v_onboarding_status;
    END IF;

    -- 2. Create Workspace
    INSERT INTO public.workspaces (
        user_id, name, slug, status
    ) VALUES (
        p_user_id, p_name, p_slug, 'provisioning'
    ) RETURNING * INTO v_workspace;

    v_workspace_id := v_workspace.id;

    -- 3. Create Workspace Member (Owner)
    INSERT INTO public.workspace_members (
        user_id, workspace_id, role
    ) VALUES (
        p_user_id, v_workspace_id, 'owner'
    );

    -- 4. Update User Status
    UPDATE public.users
    SET onboarding_status = 'pending_storage'
    WHERE id = p_user_id;

    -- 5. Audit Log
    INSERT INTO public.audit_logs (
        actor_id, action, action_category, description, target_type, target_id, ip_address, user_agent
    ) VALUES (
        p_user_id,
        'workspace_created',
        'onboarding',
        'Created workspace: ' || p_name,
        'workspace',
        v_workspace_id,
        p_audit_data->>'ip_address',
        p_audit_data->>'user_agent'
    );

    RETURN row_to_json(v_workspace)::JSONB;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION public.create_workspace_secure TO authenticated;
