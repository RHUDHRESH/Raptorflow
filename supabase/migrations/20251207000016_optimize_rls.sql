-- =====================================================
-- MIGRATION 016: Optimize RLS Performance
-- =====================================================

-- Wrap auth.uid() in subquery to prevent re-evaluation per row
-- https://supabase.com/docs/guides/database/postgres/row-level-security#call-functions-with-select

-- Drop existing policies
DROP POLICY IF EXISTS profiles_select_own ON public.profiles;
DROP POLICY IF EXISTS profiles_update_own ON public.profiles;
DROP POLICY IF EXISTS profiles_insert_own ON public.profiles;

-- Recreate with optimized auth checks
CREATE POLICY profiles_select_own ON public.profiles
  FOR SELECT
  USING (id = (SELECT auth.uid()));

CREATE POLICY profiles_update_own ON public.profiles
  FOR UPDATE
  USING (id = (SELECT auth.uid()));

CREATE POLICY profiles_insert_own ON public.profiles
  FOR INSERT
  WITH CHECK (id = (SELECT auth.uid()));
