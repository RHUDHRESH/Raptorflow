-- =================================================================
-- SECURITY FIXES: Function Search Path Mutable Issues
-- Migration: 131_fix_function_security.sql
-- Priority: MEDIUM - Fixes function security vulnerabilities
-- =================================================================

-- Fix function search path issues by adding SET search_path
-- This prevents SQL injection and privilege escalation

-- Drop and recreate functions with fixed search_path
DROP FUNCTION IF EXISTS public.update_updated_at_column CASCADE;

CREATE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

-- Drop and recreate get_user_by_auth_uid function
DROP FUNCTION IF EXISTS public.get_user_by_auth_uid CASCADE;

CREATE FUNCTION public.get_user_by_auth_uid(user_auth_uid text)
RETURNS TABLE (
    id uuid,
    email text,
    role text,
    is_active boolean,
    created_at timestamptz,
    updated_at timestamptz
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    RETURN QUERY
    SELECT
        u.id,
        u.email,
        u.role,
        u.is_active,
        u.created_at,
        u.updated_at
    FROM public.users u
    WHERE u.auth_uid = user_auth_uid
    AND u.is_active = true;
END;
$$;

-- Drop and recreate handle_new_user function
DROP FUNCTION IF EXISTS public.handle_new_user CASCADE;

CREATE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    workspace_id uuid;
BEGIN
    -- Create a default workspace for the new user
    INSERT INTO public.workspaces (name, slug, owner_id, status)
    VALUES (
        'Default Workspace',
        'default-' || substr(md5(NEW.id::text), 1, 8),
        NEW.id,
        'active'
    ) RETURNING id INTO workspace_id;

    -- Update user with workspace reference
    UPDATE public.users
    SET workspace_id = workspace_id
    WHERE id = NEW.id;

    RETURN NEW;
END;
$$;

-- Drop and recreate update_updated_at function
DROP FUNCTION IF EXISTS public.update_updated_at CASCADE;

CREATE FUNCTION public.update_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

-- Grant necessary permissions
GRANT EXECUTE ON FUNCTION public.update_updated_at_column TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_user_by_auth_uid TO authenticated;
GRANT EXECUTE ON FUNCTION public.handle_new_user TO service_role;
GRANT EXECUTE ON FUNCTION public.update_updated_at TO authenticated;
