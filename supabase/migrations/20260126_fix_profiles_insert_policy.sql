-- Fix: Add INSERT policy for profiles table
-- The profiles table is missing an INSERT policy which prevents new user profile creation

-- Allow users to insert their own profile (using auth.uid() = id)
DROP POLICY IF EXISTS "profiles_self_insert" ON public.profiles;
CREATE POLICY "profiles_self_insert" ON public.profiles
    FOR INSERT
    WITH CHECK (auth.uid() = id);

-- Also allow service role to insert profiles (for system operations)
DROP POLICY IF EXISTS "profiles_service_insert" ON public.profiles;
CREATE POLICY "profiles_service_insert" ON public.profiles
    FOR INSERT
    WITH CHECK (true);  -- Service role bypasses RLS anyway, but this makes intent clear

-- Grant insert to authenticated users on profiles
GRANT INSERT ON public.profiles TO authenticated;
GRANT INSERT ON public.profiles TO service_role;

-- Ensure the handle_new_user trigger function has proper permissions
GRANT EXECUTE ON FUNCTION public.handle_new_user() TO service_role;
GRANT EXECUTE ON FUNCTION public.handle_new_user() TO authenticated;

-- Add INSERT policy for subscriptions (needed for plan selection)
DROP POLICY IF EXISTS "subscriptions_self_insert" ON public.subscriptions;
CREATE POLICY "subscriptions_self_insert" ON public.subscriptions
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "subscriptions_self_update" ON public.subscriptions;
CREATE POLICY "subscriptions_self_update" ON public.subscriptions
    FOR UPDATE
    USING (auth.uid() = user_id);

-- Grant permissions
GRANT INSERT, UPDATE ON public.subscriptions TO authenticated;
GRANT INSERT, UPDATE ON public.subscriptions TO service_role;

-- Make sure plans table is readable by everyone (needed for plan selection page)
DROP POLICY IF EXISTS "plans_public_read" ON public.plans;
CREATE POLICY "plans_public_read" ON public.plans
    FOR SELECT
    USING (true);

GRANT SELECT ON public.plans TO anon;
GRANT SELECT ON public.plans TO authenticated;
GRANT SELECT ON public.plans TO service_role;

-- Add audit_logs insert policy
DROP POLICY IF EXISTS "audit_logs_self_insert" ON public.audit_logs;
CREATE POLICY "audit_logs_self_insert" ON public.audit_logs
    FOR INSERT
    WITH CHECK (true);  -- Any authenticated user can create audit logs

GRANT INSERT ON public.audit_logs TO authenticated;
GRANT INSERT ON public.audit_logs TO service_role;
