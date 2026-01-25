-- Migration: 20260118_update_icp_profiles_trinity.sql
-- Add Trinity fields (Persona, Avatar, Confidence) to ICP profiles

ALTER TABLE public.icp_profiles 
ADD COLUMN IF NOT EXISTS persona_name TEXT,
ADD COLUMN IF NOT EXISTS avatar TEXT DEFAULT '👤',
ADD COLUMN IF NOT EXISTS confidence INTEGER DEFAULT 0;

-- Comment for clarity
COMMENT ON COLUMN public.icp_profiles.persona_name IS 'Human persona name for this cohort (e.g., Sarah)';
COMMENT ON COLUMN public.icp_profiles.avatar IS 'Emoji or URL representing the persona';
COMMENT ON COLUMN public.icp_profiles.confidence IS 'AI confidence score for this derivation (0-100)';
