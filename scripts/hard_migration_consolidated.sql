-- ============================================================================
-- RAPTORFLOW HARD MIGRATION: AUTH CONSOLIDATION & CLEANUP
-- Script: scripts/hard_migration_consolidated.sql
-- ============================================================================

BEGIN;

-- 1. PRE-MIGRATION DATA BACKUP (Optional but recommended in production)
-- SELECT * INTO profiles_backup_20260119 FROM profiles;

-- 2. ENSURE NEW SCHEMA STRUCTURE
-- (This part repeats parts of the migration for safety)
CREATE SEQUENCE IF NOT EXISTS ucid_seq START 1;

CREATE OR REPLACE FUNCTION public.generate_ucid()
RETURNS TEXT AS $$
DECLARE
    year_prefix TEXT;
    seq_val TEXT;
BEGIN
    year_prefix := to_char(CURRENT_DATE, 'YYYY');
    seq_val := lpad(nextval('ucid_seq')::TEXT, 4, '0');
    RETURN 'RF-' || year_prefix || '-' || seq_val;
END;
$$ LANGUAGE plpgsql;

-- 3. UNIFY USER DATA
-- Strategy: Use auth.users as the source of truth, merge data from users/user_profiles
INSERT INTO public.profiles (id, email, full_name, avatar_url, role, onboarding_status)
SELECT 
    au.id,
    au.email,
    COALESCE(
        up.full_name, 
        u.full_name, 
        au.raw_user_meta_data->>'full_name', 
        au.raw_user_meta_data->>'name', 
        split_part(au.email, '@', 1)
    ),
    COALESCE(
        up.avatar_url, 
        au.raw_user_meta_data->>'avatar_url', 
        au.raw_user_meta_data->>'picture', 
        ''
    ),
    'user',
    CASE 
        WHEN u.onboarding_status = 'active' THEN 'active'
        WHEN u.has_completed_onboarding = true THEN 'active'
        ELSE 'pending'
    END
FROM auth.users au
LEFT JOIN public.user_profiles up ON au.id = up.id
LEFT JOIN public.users u ON au.id = u.id
ON CONFLICT (id) DO UPDATE SET
    full_name = EXCLUDED.full_name,
    avatar_url = EXCLUDED.avatar_url,
    onboarding_status = EXCLUDED.onboarding_status,
    updated_at = NOW();

-- 4. ASSIGN UCIDs TO ALL PROFILES
UPDATE public.profiles SET ucid = public.generate_ucid() WHERE ucid IS NULL;

-- 5. CONSOLIDATE WORKSPACES
-- Ensure every profile has exactly one personal workspace
INSERT INTO public.workspaces (owner_id, name, slug)
SELECT 
    p.id, 
    'My Personal Workspace',
    'personal-' || p.id::text
FROM public.profiles p
WHERE p.id NOT IN (SELECT owner_id FROM public.workspaces)
ON CONFLICT DO NOTHING;

-- 6. HARD CLEANUP: DROP REDUNDANT TABLES
-- WARNING: This is the "Hard Migration" step. Ensure data integrity before this!
DROP TABLE IF EXISTS public.user_profiles CASCADE;
DROP TABLE IF EXISTS public.user_sessions CASCADE;
DROP TABLE IF EXISTS public.jwt_sessions CASCADE;
DROP TABLE IF EXISTS public.mfa_sessions CASCADE;
DROP TABLE IF EXISTS public.impersonation_sessions CASCADE;
DROP TABLE IF EXISTS public.impersonation_logs CASCADE;
DROP TABLE IF EXISTS public.impersonation_permissions CASCADE;
DROP TABLE IF EXISTS public.audit_logs_v2 CASCADE;
DROP TABLE IF EXISTS public.security_events_v2 CASCADE;
DROP TABLE IF EXISTS public.user_behavior_baselines CASCADE;
DROP TABLE IF EXISTS public.ip_access_logs CASCADE;
DROP TABLE IF EXISTS public.ip_reputation CASCADE;
DROP TABLE IF EXISTS public.ip_access_challenges CASCADE;
DROP TABLE IF EXISTS public.onboarding_sessions CASCADE;

-- Rename public.users if it's not the profiles table to avoid confusion
-- We keep public.profiles as the single source of truth.
-- If public.users exists and is redundant, drop it.
DROP TABLE IF EXISTS public.users CASCADE;

-- 7. VERIFY MIGRATION
DO $$
DECLARE
    profile_count INTEGER;
    workspace_count INTEGER;
BEGIN
    SELECT count(*) INTO profile_count FROM public.profiles;
    SELECT count(*) INTO workspace_count FROM public.workspaces;
    
    RAISE NOTICE 'Migration Complete: % profiles, % workspaces created.', profile_count, workspace_count;
    
    IF profile_count != workspace_count THEN
        RAISE WARNING 'Mismatch between profiles and workspaces! Verify manually.';
    END IF;
END $$;

COMMIT;
