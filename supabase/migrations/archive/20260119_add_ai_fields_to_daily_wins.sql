-- Add AI-specific fields to daily_wins table
-- Migration: 20260119_add_ai_fields_to_daily_wins.sql

ALTER TABLE public.daily_wins
ADD COLUMN IF NOT EXISTS topic TEXT,
ADD COLUMN IF NOT EXISTS angle TEXT,
ADD COLUMN IF NOT EXISTS hook TEXT,
ADD COLUMN IF NOT EXISTS outline JSONB,
ADD COLUMN IF NOT EXISTS platform TEXT,
ADD COLUMN IF NOT EXISTS estimated_time INTEGER DEFAULT 10,
ADD COLUMN IF NOT EXISTS relevance_score DECIMAL(3,2) DEFAULT 0.8,
ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'generated',
ADD COLUMN IF NOT EXISTS is_ai_generated BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS surprise_score DECIMAL(3,2),
ADD COLUMN IF NOT EXISTS intelligence_brief TEXT,
ADD COLUMN IF NOT EXISTS visual_prompt TEXT,
ADD COLUMN IF NOT EXISTS engagement_prediction DECIMAL(3,2),
ADD COLUMN IF NOT EXISTS viral_potential DECIMAL(3,2),
ADD COLUMN IF NOT EXISTS follow_up_ideas JSONB DEFAULT '[]';

-- Update win_type and category to be optional or have defaults for AI wins
ALTER TABLE public.daily_wins ALTER COLUMN win_type DROP NOT NULL;
ALTER TABLE public.daily_wins ALTER COLUMN category DROP NOT NULL;
ALTER TABLE public.daily_wins ALTER COLUMN achievement_date SET DEFAULT CURRENT_DATE;
ALTER TABLE public.daily_wins ALTER COLUMN achievement_date DROP NOT NULL;
ALTER TABLE public.daily_wins ALTER COLUMN created_by DROP NOT NULL;
