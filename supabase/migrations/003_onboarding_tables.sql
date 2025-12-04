-- =====================================================
-- ONBOARDING TABLES MIGRATION
-- Creates tables for onboarding intake, agent executions, and shared links
-- =====================================================

-- Onboarding intake table - stores all onboarding step data
CREATE TABLE IF NOT EXISTS public.onboarding_intake (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Step 1: Positioning
    positioning JSONB DEFAULT '{}',
    positioning_derived JSONB DEFAULT '{}',
    
    -- Step 2: Company
    company JSONB DEFAULT '{}',
    company_enriched JSONB DEFAULT '{}',
    
    -- Step 3: Product
    product JSONB DEFAULT '{}',
    product_derived JSONB DEFAULT '{}',
    
    -- Step 4: Market
    market JSONB DEFAULT '{}',
    market_system_view JSONB DEFAULT '{}',
    
    -- Step 5: Strategy
    strategy JSONB DEFAULT '{}',
    strategy_derived JSONB DEFAULT '{}',
    
    -- Generated outputs
    icps JSONB DEFAULT '[]',
    war_plan JSONB DEFAULT '{}',
    metrics_framework JSONB DEFAULT '{}',
    
    -- Progress tracking
    current_step INTEGER DEFAULT 1,
    completed_steps INTEGER[] DEFAULT '{}',
    
    -- Mode and ownership
    mode VARCHAR(20) DEFAULT 'self-service', -- 'self-service' or 'sales-assisted'
    sales_rep_id UUID REFERENCES auth.users(id),
    share_token VARCHAR(100) UNIQUE,
    
    -- Payment tracking
    selected_plan VARCHAR(50),
    payment_status VARCHAR(20) DEFAULT 'pending',
    payment_completed_at TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agent execution logs - tracks all agent runs
CREATE TABLE IF NOT EXISTS public.agent_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    intake_id UUID REFERENCES public.onboarding_intake(id) ON DELETE CASCADE,
    agent_name VARCHAR(100) NOT NULL,
    input JSONB NOT NULL,
    output JSONB,
    status VARCHAR(20) DEFAULT 'pending', -- pending, running, completed, failed
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration_ms INTEGER,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Shared links for sales-assisted onboarding
CREATE TABLE IF NOT EXISTS public.shared_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    intake_id UUID REFERENCES public.onboarding_intake(id) ON DELETE CASCADE,
    token VARCHAR(100) UNIQUE NOT NULL,
    sales_rep_id UUID REFERENCES auth.users(id),
    expires_at TIMESTAMPTZ,
    accessed_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMPTZ,
    payment_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_onboarding_intake_user_id ON public.onboarding_intake(user_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_intake_share_token ON public.onboarding_intake(share_token);
CREATE INDEX IF NOT EXISTS idx_agent_executions_intake_id ON public.agent_executions(intake_id);
CREATE INDEX IF NOT EXISTS idx_agent_executions_status ON public.agent_executions(status);
CREATE INDEX IF NOT EXISTS idx_shared_links_token ON public.shared_links(token);
CREATE INDEX IF NOT EXISTS idx_shared_links_intake_id ON public.shared_links(intake_id);

-- Enable RLS
ALTER TABLE public.onboarding_intake ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agent_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.shared_links ENABLE ROW LEVEL SECURITY;

-- RLS Policies for onboarding_intake
CREATE POLICY "Users can view own intake" ON public.onboarding_intake
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own intake" ON public.onboarding_intake
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own intake" ON public.onboarding_intake
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Sales reps can view assigned intake" ON public.onboarding_intake
    FOR SELECT USING (auth.uid() = sales_rep_id);

CREATE POLICY "Sales reps can update assigned intake" ON public.onboarding_intake
    FOR UPDATE USING (auth.uid() = sales_rep_id);

-- RLS Policies for agent_executions (users can see their own intake's executions)
CREATE POLICY "Users can view own agent executions" ON public.agent_executions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.onboarding_intake 
            WHERE id = intake_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own agent executions" ON public.agent_executions
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.onboarding_intake 
            WHERE id = intake_id AND user_id = auth.uid()
        )
    );

-- RLS Policies for shared_links
CREATE POLICY "Users can view own shared links" ON public.shared_links
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.onboarding_intake 
            WHERE id = intake_id AND (user_id = auth.uid() OR sales_rep_id = auth.uid())
        )
    );

CREATE POLICY "Users can insert shared links for own intake" ON public.shared_links
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.onboarding_intake 
            WHERE id = intake_id AND (user_id = auth.uid() OR sales_rep_id = auth.uid())
        )
    );

-- Public read access for shared links by token (for sales-assisted flow)
CREATE POLICY "Anyone can read shared links by token" ON public.shared_links
    FOR SELECT USING (true);

-- Add onboarding fields to profiles if they don't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' AND column_name = 'onboarding_completed') THEN
        ALTER TABLE public.profiles ADD COLUMN onboarding_completed BOOLEAN DEFAULT FALSE;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' AND column_name = 'onboarding_completed_at') THEN
        ALTER TABLE public.profiles ADD COLUMN onboarding_completed_at TIMESTAMPTZ;
    END IF;
END $$;

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at trigger to onboarding_intake
DROP TRIGGER IF EXISTS update_onboarding_intake_updated_at ON public.onboarding_intake;
CREATE TRIGGER update_onboarding_intake_updated_at
    BEFORE UPDATE ON public.onboarding_intake
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- Grant permissions for service role
GRANT ALL ON public.onboarding_intake TO service_role;
GRANT ALL ON public.agent_executions TO service_role;
GRANT ALL ON public.shared_links TO service_role;

-- Grant permissions for authenticated users
GRANT SELECT, INSERT, UPDATE ON public.onboarding_intake TO authenticated;
GRANT SELECT, INSERT ON public.agent_executions TO authenticated;
GRANT SELECT, INSERT, UPDATE ON public.shared_links TO authenticated;

-- =====================================================
-- SUCCESS MESSAGE
-- =====================================================
DO $$ 
BEGIN
    RAISE NOTICE 'Onboarding tables migration completed successfully!';
END $$;

