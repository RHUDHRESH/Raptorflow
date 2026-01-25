-- =================================================================
-- CHUNK 2: FUNCTION & EXTENSION SECURITY FIXES (FIXED)
-- Run this after CHUNK 1 succeeded
-- =================================================================

-- STEP 1: Fix function security issues (WARN level)
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
    WHERE u.auth_user_id = user_auth_uid
    AND u.is_active = true;
END;
$$;

DROP FUNCTION IF EXISTS public.handle_new_user CASCADE;

CREATE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    RETURN NEW;
END;
$$;

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

-- STEP 2: Handle extension security properly (WARN level)
-- Create extensions schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS extensions;

-- NOTE: Vector extension is in use by foundations table (ai_context_embedding column)
-- We'll create a new vector extension in extensions schema for future use
-- The existing vector extension in public schema will remain for compatibility

-- STEP 3: Grant function permissions
GRANT EXECUTE ON FUNCTION public.update_updated_at_column TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_user_by_auth_uid TO authenticated;
GRANT EXECUTE ON FUNCTION public.handle_new_user TO service_role;
GRANT EXECUTE ON FUNCTION public.update_updated_at TO authenticated;

-- STEP 4: Grant extension schema permissions
GRANT USAGE ON SCHEMA extensions TO authenticated;
GRANT USAGE ON SCHEMA extensions TO service_role;
GRANT USAGE ON SCHEMA extensions TO anon;

-- STEP 5: Update database search path
ALTER DATABASE postgres SET search_path = "$user", public, extensions;

-- =================================================================
-- CHUNK 2 COMPLETE (FIXED)
-- Fixed: 4 function search_path mutable issues
-- Handled: extension in public schema (kept for compatibility)
-- Next: Run CHUNK 3 for ICP policies and performance fixes
-- =================================================================
