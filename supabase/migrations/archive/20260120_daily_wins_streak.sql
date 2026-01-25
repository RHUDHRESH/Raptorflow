-- Migration: 20260120_daily_wins_streak.sql
-- Add streak tracking to Workspaces

ALTER TABLE public.workspaces
ADD COLUMN IF NOT EXISTS daily_wins_streak INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS last_win_at TIMESTAMPTZ;

-- Comments
COMMENT ON COLUMN public.workspaces.daily_wins_streak IS 'Current consecutive days of posting content wins.';
COMMENT ON COLUMN public.workspaces.last_win_at IS 'Timestamp of the last posted daily win.';
