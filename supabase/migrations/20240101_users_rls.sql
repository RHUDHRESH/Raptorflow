-- RLS policies for users table
-- Migration: 20240101_users_rls.sql

-- Users can view own profile
CREATE POLICY "Users can view own profile" ON public.users
    FOR SELECT USING (auth.uid() = id);

-- Users can update own profile
CREATE POLICY "Users can update own profile" ON public.users
    FOR UPDATE USING (auth.uid() = id);

-- No INSERT policy (handled by trigger)
-- No DELETE policy (users should contact support)
