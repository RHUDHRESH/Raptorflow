-- Migration: 20260119_blackbox_resurrection.sql
-- Description: Align blackbox_strategies with current implementation and create strategy_reviews table

-- 1. Update blackbox_strategies with missing columns
DO $$
BEGIN
    -- Add risk_reasons if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='blackbox_strategies' AND column_name='risk_reasons') THEN
        ALTER TABLE public.blackbox_strategies ADD COLUMN risk_reasons JSONB DEFAULT '[]';
    END IF;

    -- Add phases if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='blackbox_strategies' AND column_name='phases') THEN
        ALTER TABLE public.blackbox_strategies ADD COLUMN phases JSONB DEFAULT '[]';
    END IF;

    -- Add expected_upside if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='blackbox_strategies' AND column_name='expected_upside') THEN
        ALTER TABLE public.blackbox_strategies ADD COLUMN expected_upside TEXT;
    END IF;

    -- Add potential_downside if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='blackbox_strategies' AND column_name='potential_downside') THEN
        ALTER TABLE public.blackbox_strategies ADD COLUMN potential_downside TEXT;
    END IF;

    -- Add risk_tolerance if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='blackbox_strategies' AND column_name='risk_tolerance') THEN
        ALTER TABLE public.blackbox_strategies ADD COLUMN risk_tolerance INTEGER DEFAULT 5;
    END IF;

    -- Add timeline if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='blackbox_strategies' AND column_name='timeline') THEN
        ALTER TABLE public.blackbox_strategies ADD COLUMN timeline TEXT;
    END IF;

    -- Add budget_range if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='blackbox_strategies' AND column_name='budget_range') THEN
        ALTER TABLE public.blackbox_strategies ADD COLUMN budget_range TEXT;
    END IF;

    -- Add tokens_used if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='blackbox_strategies' AND column_name='tokens_used') THEN
        ALTER TABLE public.blackbox_strategies ADD COLUMN tokens_used INTEGER DEFAULT 0;
    END IF;

    -- Add cost_usd if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='blackbox_strategies' AND column_name='cost_usd') THEN
        ALTER TABLE public.blackbox_strategies ADD COLUMN cost_usd DECIMAL(10,4) DEFAULT 0.0000;
    END IF;

    -- Add focus_area if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='blackbox_strategies' AND column_name='focus_area') THEN
        ALTER TABLE public.blackbox_strategies ADD COLUMN focus_area TEXT;
    END IF;

    -- Add risk_score if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='blackbox_strategies' AND column_name='risk_score') THEN
        ALTER TABLE public.blackbox_strategies ADD COLUMN risk_score DECIMAL(3,2) DEFAULT 0.00;
    END IF;

    -- Add bold_idea if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='blackbox_strategies' AND column_name='bold_idea') THEN
        ALTER TABLE public.blackbox_strategies ADD COLUMN bold_idea TEXT;
    END IF;

    -- Add converted_at if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='blackbox_strategies' AND column_name='converted_at') THEN
        ALTER TABLE public.blackbox_strategies ADD COLUMN converted_at TIMESTAMPTZ;
    END IF;

    -- Add moves_created if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='blackbox_strategies' AND column_name='moves_created') THEN
        ALTER TABLE public.blackbox_strategies ADD COLUMN moves_created INTEGER DEFAULT 0;
    END IF;

    -- Add conversion_summary if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='blackbox_strategies' AND column_name='conversion_summary') THEN
        ALTER TABLE public.blackbox_strategies ADD COLUMN conversion_summary JSONB DEFAULT '{}';
    END IF;

    -- Add review_status if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='blackbox_strategies' AND column_name='review_status') THEN
        ALTER TABLE public.blackbox_strategies ADD COLUMN review_status TEXT DEFAULT 'pending';
    END IF;

    -- Add analysis if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='blackbox_strategies' AND column_name='analysis') THEN
        ALTER TABLE public.blackbox_strategies ADD COLUMN analysis JSONB DEFAULT '{}';
    END IF;

    -- Add feasibility if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='blackbox_strategies' AND column_name='feasibility') THEN
        ALTER TABLE public.blackbox_strategies ADD COLUMN feasibility JSONB DEFAULT '{}';
    END IF;

    -- Add feedback if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='blackbox_strategies' AND column_name='feedback') THEN
        ALTER TABLE public.blackbox_strategies ADD COLUMN feedback JSONB DEFAULT '{}';
    END IF;

    -- Add reviewed_at if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='blackbox_strategies' AND column_name='reviewed_at') THEN
        ALTER TABLE public.blackbox_strategies ADD COLUMN reviewed_at TIMESTAMPTZ;
    END IF;

    -- Add converted_to_move_id if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='blackbox_strategies' AND column_name='converted_to_move_id') THEN
        ALTER TABLE public.blackbox_strategies ADD COLUMN converted_to_move_id UUID REFERENCES moves(id);
    END IF;
END $$;

-- 2. Create strategy_reviews table
CREATE TABLE IF NOT EXISTS public.strategy_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_id UUID NOT NULL REFERENCES blackbox_strategies(id) ON DELETE CASCADE,
    risk_score DECIMAL(3,2) NOT NULL,
    risk_level TEXT NOT NULL,
    status TEXT DEFAULT 'pending', -- pending, completed, rejected
    feedback TEXT,
    reviewed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Enable RLS on strategy_reviews
ALTER TABLE public.strategy_reviews ENABLE ROW LEVEL SECURITY;

-- 4. Create RLS policies for strategy_reviews
-- Users can view reviews for strategies in their workspace
CREATE POLICY "Users can view strategy reviews" ON public.strategy_reviews
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.blackbox_strategies
            WHERE public.blackbox_strategies.id = public.strategy_reviews.strategy_id
            AND user_owns_workspace(public.blackbox_strategies.workspace_id)
        )
    );

-- Users can create reviews (normally handled by AI, but for consistency)
CREATE POLICY "Users can create strategy reviews" ON public.strategy_reviews
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.blackbox_strategies
            WHERE public.blackbox_strategies.id = public.strategy_reviews.strategy_id
            AND user_owns_workspace(public.blackbox_strategies.workspace_id)
        )
    );

-- Users can update reviews
CREATE POLICY "Users can update strategy reviews" ON public.strategy_reviews
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.blackbox_strategies
            WHERE public.blackbox_strategies.id = public.strategy_reviews.strategy_id
            AND user_owns_workspace(public.blackbox_strategies.workspace_id)
        )
    );

-- Users can delete reviews
CREATE POLICY "Users can delete strategy reviews" ON public.strategy_reviews
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM public.blackbox_strategies
            WHERE public.blackbox_strategies.id = public.strategy_reviews.strategy_id
            AND user_owns_workspace(public.blackbox_strategies.workspace_id)
        )
    );

-- Add indexes for strategy_reviews
CREATE INDEX IF NOT EXISTS idx_strategy_reviews_strategy_id ON public.strategy_reviews(strategy_id);
CREATE INDEX IF NOT EXISTS idx_strategy_reviews_status ON public.strategy_reviews(status);
