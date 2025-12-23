-- Expansion for Moves & Campaigns Production Engine

-- Add production fields to campaigns
ALTER TABLE campaigns 
ADD COLUMN IF NOT EXISTS arc_data JSONB DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS kpi_targets JSONB DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS rag_status TEXT DEFAULT 'green',
ADD COLUMN IF NOT EXISTS strategy_context_id UUID; -- Link to specific Gold Context version

-- Add production fields to moves
ALTER TABLE moves
ADD COLUMN IF NOT EXISTS scheduled_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS priority INTEGER DEFAULT 3, -- 1: High, 5: Low
ADD COLUMN IF NOT EXISTS move_type TEXT, -- social, email, ad, research
ADD COLUMN IF NOT EXISTS tool_requirements JSONB DEFAULT '[]'::jsonb;

-- Detailed KPI Tracking Table
CREATE TABLE IF NOT EXISTS campaign_kpis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    metric_name TEXT NOT NULL,
    current_value NUMERIC DEFAULT 0,
    target_value NUMERIC,
    unit TEXT,
    last_updated TIMESTAMPTZ DEFAULT now(),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Audit Log for Agent Decisions
CREATE TABLE IF NOT EXISTS agent_decision_audit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    agent_id TEXT NOT NULL,
    decision_type TEXT NOT NULL, -- move_gen, campaign_pivot, tool_call
    input_state JSONB,
    output_decision JSONB,
    rationale TEXT,
    cost_estimate NUMERIC,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Enable RLS
ALTER TABLE campaign_kpis ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_decision_audit ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY tenant_isolation_kpis ON campaign_kpis 
    USING (EXISTS (SELECT 1 FROM campaigns WHERE campaigns.id = campaign_kpis.campaign_id AND campaigns.tenant_id = auth.uid()));

CREATE POLICY tenant_isolation_audit ON agent_decision_audit 
    USING (tenant_id = auth.uid());

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_moves_campaign_id ON moves(campaign_id);
CREATE INDEX IF NOT EXISTS idx_campaign_kpis_campaign_id ON campaign_kpis(campaign_id);
CREATE INDEX IF NOT EXISTS idx_agent_audit_tenant_id ON agent_decision_audit(tenant_id);
