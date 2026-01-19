-- 20260118_foundation_schema.sql
-- Create table for Foundation data (RICPs, Messaging, Channels)

CREATE TABLE IF NOT EXISTS public.business_context_manifests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  ricps JSONB DEFAULT '[]'::jsonb,
  messaging JSONB DEFAULT '{}'::jsonb,
  channels JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Ensure one manifest per user
  CONSTRAINT unique_user_manifest UNIQUE (user_id)
);

-- Enable RLS
ALTER TABLE public.business_context_manifests ENABLE ROW LEVEL SECURITY;

-- RLS Policies
DROP POLICY IF EXISTS "Users can view own foundation" ON public.business_context_manifests;
DROP POLICY IF EXISTS "Users can manage own foundation" ON public.business_context_manifests;

CREATE POLICY "Users can view own foundation" ON public.business_context_manifests
  FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can manage own foundation" ON public.business_context_manifests
  FOR ALL USING (user_id = auth.uid());

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_business_context_modtime ON public.business_context_manifests;

CREATE TRIGGER update_business_context_modtime
    BEFORE UPDATE ON public.business_context_manifests
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();
