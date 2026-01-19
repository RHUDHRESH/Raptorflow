-- Add execution column to moves table
ALTER TABLE public.moves ADD COLUMN IF NOT EXISTS execution JSONB DEFAULT '[]';
