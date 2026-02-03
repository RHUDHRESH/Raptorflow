-- ============================================
-- CANONICAL AUTH SYSTEM MIGRATION
-- Creates auth triggers and helper functions
-- Date: 2026-01-30
-- ============================================

BEGIN;

-- ============================================
-- HELPER FUNCTION: Generate Workspace Slug
-- ============================================
CREATE OR REPLACE FUNCTION public.generate_workspace_slug(base text)
RETURNS text AS $$
DECLARE
    sanitized text := lower(regexp_replace(base, '[^a-z0-9]+', '-', 'g'));
    candidate text;
BEGIN
    LOOP
        candidate := sanitized || '-' || substr(md5(gen_random_uuid()::text), 1, 8);
        EXIT WHEN NOT EXISTS (SELECT 1 FROM public.workspaces WHERE slug = candidate);
    END LOOP;
    RETURN candidate;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================
-- AUTH TRIGGER: Handle New User
-- ============================================
CREATE OR REPLACE FUNCTION public.handle_new_auth_user()
RETURNS TRIGGER AS $$
DECLARE
    new_user_id uuid;
    existing_workspace_id uuid;
    name_hint text := split_part(new.email, '@', 1);
    display_name text;
    workspace_slug text;
BEGIN
    -- Check if user already exists
    SELECT id INTO new_user_id FROM public.users WHERE auth_user_id = new.id;

    -- Create user if doesn't exist
    IF new_user_id IS NULL THEN
        INSERT INTO public.users (auth_user_id, email, full_name, avatar_url, email_verified)
        VALUES (
            new.id,
            new.email,
            COALESCE(new.raw_user_meta_data->>'full_name', name_hint),
            new.raw_user_meta_data->>'avatar_url',
            new.email_confirmed_at IS NOT NULL
        ) RETURNING id INTO new_user_id;
    END IF;

    -- Check if workspace already exists
    SELECT id INTO existing_workspace_id
    FROM public.workspaces
    WHERE owner_id = new_user_id
    LIMIT 1;

    -- Create workspace if doesn't exist
    IF existing_workspace_id IS NULL THEN
        display_name := COALESCE(new.raw_user_meta_data->>'full_name', name_hint);
        workspace_slug := public.generate_workspace_slug(name_hint);

        INSERT INTO public.workspaces (name, slug, owner_id, is_trial)
        VALUES (
            display_name || '''s Workspace',
            workspace_slug,
            new_user_id,
            true
        ) RETURNING id INTO existing_workspace_id;
    END IF;

    -- Add user to workspace as owner
    INSERT INTO public.workspace_members (workspace_id, user_id, role, is_active)
    VALUES (existing_workspace_id, new_user_id, 'owner', true)
    ON CONFLICT (workspace_id, user_id) DO UPDATE
        SET role = EXCLUDED.role,
            is_active = true,
            joined_at = COALESCE(workspace_members.joined_at, NOW());

    RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, auth;

-- Drop existing trigger if exists
DROP TRIGGER IF EXISTS trg_handle_new_auth_user ON auth.users;

-- Create trigger
CREATE TRIGGER trg_handle_new_auth_user
AFTER INSERT ON auth.users
FOR EACH ROW EXECUTE FUNCTION public.handle_new_auth_user();

-- ============================================
-- COMMENTS
-- ============================================
COMMENT ON FUNCTION public.generate_workspace_slug(text) IS 'Generates unique workspace slugs';
COMMENT ON FUNCTION public.handle_new_auth_user() IS 'Automatically creates user profile and workspace on auth signup';

COMMIT;
