-- 20260118_secure_user_data.sql
-- Enforce RLS on Key Business Tables

-- 1. Secure TABLE: moves
ALTER TABLE IF EXISTS public.moves ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own moves" ON public.moves;
DROP POLICY IF EXISTS "Users can insert own moves" ON public.moves;
DROP POLICY IF EXISTS "Users can update own moves" ON public.moves;
DROP POLICY IF EXISTS "Users can delete own moves" ON public.moves;

CREATE POLICY "Users can view own moves" ON public.moves
  FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can insert own moves" ON public.moves
  FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update own moves" ON public.moves
  FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "Users can delete own moves" ON public.moves
  FOR DELETE USING (user_id = auth.uid());

-- 2. Secure TABLE: business_context_manifests
ALTER TABLE IF EXISTS public.business_context_manifests ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own context" ON public.business_context_manifests;
DROP POLICY IF EXISTS "Users can manage own context" ON public.business_context_manifests;

CREATE POLICY "Users can view own context" ON public.business_context_manifests
  FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can manage own context" ON public.business_context_manifests
  FOR ALL USING (user_id = auth.uid());

-- 3. Secure TABLE: user_uploads (if exists) or create it
CREATE TABLE IF NOT EXISTS public.user_uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) NOT NULL,
    file_path TEXT NOT NULL,
    file_type TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.user_uploads ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own uploads" ON public.user_uploads
  FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can insert own uploads" ON public.user_uploads
  FOR INSERT WITH CHECK (user_id = auth.uid());
