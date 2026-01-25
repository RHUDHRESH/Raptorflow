-- Migration: 20260120_calendar_fields.sql
-- Add start/end dates for high-fidelity calendar support

ALTER TABLE public.moves 
ADD COLUMN IF NOT EXISTS start_date TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS end_date TIMESTAMPTZ;

ALTER TABLE public.campaigns
ADD COLUMN IF NOT EXISTS start_date TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS end_date TIMESTAMPTZ;

-- Comments
COMMENT ON COLUMN public.moves.start_date IS 'Scheduled start for the move.';
COMMENT ON COLUMN public.moves.end_date IS 'Scheduled or actual completion date.';
