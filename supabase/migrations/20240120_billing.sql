-- Billing tables
-- Migration: 20240120_billing.sql

CREATE TABLE IF NOT EXISTS public.subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE UNIQUE,
    plan TEXT NOT NULL CHECK (plan IN ('free', 'starter', 'pro', 'enterprise')),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'cancelled', 'past_due', 'unpaid')),
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    cancel_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.usage_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    cost_usd DECIMAL(10,6) DEFAULT 0,
    agent_breakdown JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'sent', 'paid', 'void', 'past_due')),
    paid_at TIMESTAMPTZ,
    invoice_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for subscriptions
CREATE INDEX IF NOT EXISTS idx_subscriptions_workspace_id ON public.subscriptions(workspace_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_plan ON public.subscriptions(plan);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON public.subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_current_period_end ON public.subscriptions(current_period_end);

-- Indexes for usage records
CREATE INDEX IF NOT EXISTS idx_usage_records_workspace_id ON public.usage_records(workspace_id);
CREATE INDEX IF NOT EXISTS idx_usage_records_period_start ON public.usage_records(period_start);
CREATE INDEX IF NOT EXISTS idx_usage_records_period_end ON public.usage_records(period_end);
CREATE INDEX IF NOT EXISTS idx_usage_records_created_at ON public.usage_records(created_at);

-- Indexes for invoices
CREATE INDEX IF NOT EXISTS idx_invoices_workspace_id ON public.invoices(workspace_id);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON public.invoices(status);
CREATE INDEX IF NOT EXISTS idx_invoices_paid_at ON public.invoices(paid_at);
CREATE INDEX IF NOT EXISTS idx_invoices_created_at ON public.invoices(created_at);

-- GIN index for JSONB columns
CREATE INDEX IF NOT EXISTS idx_usage_records_agent_breakdown_gin ON public.usage_records USING GIN (agent_breakdown);

-- Enable RLS on all tables
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.usage_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.invoices ENABLE ROW LEVEL SECURITY;

-- RLS policies for subscriptions
CREATE POLICY "Users can view own subscriptions" ON public.subscriptions
    FOR SELECT USING (
        workspace_id IN (
            SELECT id FROM public.workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create own subscriptions" ON public.subscriptions
    FOR INSERT WITH CHECK (
        workspace_id IN (
            SELECT id FROM public.workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update own subscriptions" ON public.subscriptions
    FOR UPDATE USING (
        workspace_id IN (
            SELECT id FROM public.workspaces
            WHERE user_id = auth.uid()
        )
    );

-- RLS policies for usage records
CREATE POLICY "Users can view own usage records" ON public.usage_records
    FOR SELECT USING (
        workspace_id IN (
            SELECT id FROM public.workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create own usage records" ON public.usage_records
    FOR INSERT WITH CHECK (
        workspace_id IN (
            SELECT id FROM public.workspaces
            WHERE user_id = auth.uid()
        )
    );

-- RLS policies for invoices
CREATE POLICY "Users can view own invoices" ON public.invoices
    FOR SELECT USING (
        workspace_id IN (
            SELECT id FROM public.workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create own invoices" ON public.invoices
    FOR INSERT WITH CHECK (
        workspace_id IN (
            SELECT id FROM public.workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update own invoices" ON public.invoices
    FOR UPDATE USING (
        workspace_id IN (
            SELECT id FROM public.workspaces
            WHERE user_id = auth.uid()
        )
    );

-- Triggers to update updated_at
CREATE OR REPLACE FUNCTION public.update_subscriptions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER subscriptions_updated_at
    BEFORE UPDATE ON public.subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION public.update_subscriptions_updated_at();

CREATE OR REPLACE FUNCTION public.update_invoices_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER invoices_updated_at
    BEFORE UPDATE ON public.invoices
    FOR EACH ROW
    EXECUTE FUNCTION public.update_invoices_updated_at();
