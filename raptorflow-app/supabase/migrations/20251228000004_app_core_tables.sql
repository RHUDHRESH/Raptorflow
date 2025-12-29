-- Core app tables to align backend expectations with current database

-- Campaigns: extend existing table with backend fields
ALTER TABLE campaigns
    ADD COLUMN IF NOT EXISTS tenant_id UUID,
    ADD COLUMN IF NOT EXISTS workspace_id UUID,
    ADD COLUMN IF NOT EXISTS title TEXT,
    ADD COLUMN IF NOT EXISTS objective TEXT,
    ADD COLUMN IF NOT EXISTS arc_data JSONB DEFAULT '{}'::JSONB,
    ADD COLUMN IF NOT EXISTS phase_order JSONB DEFAULT '[]'::JSONB,
    ADD COLUMN IF NOT EXISTS milestones JSONB DEFAULT '[]'::JSONB,
    ADD COLUMN IF NOT EXISTS campaign_tag TEXT,
    ADD COLUMN IF NOT EXISTS kpi_targets JSONB DEFAULT '{}'::JSONB,
    ADD COLUMN IF NOT EXISTS audit_data JSONB DEFAULT '{}'::JSONB;

CREATE OR REPLACE FUNCTION campaigns_sync_defaults()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.workspace_id IS NULL THEN
        NEW.workspace_id := NEW.organization_id;
    END IF;
    IF NEW.organization_id IS NULL THEN
        NEW.organization_id := NEW.workspace_id;
    END IF;
    IF NEW.title IS NULL AND NEW.name IS NOT NULL THEN
        NEW.title := NEW.name;
    END IF;
    IF NEW.name IS NULL AND NEW.title IS NOT NULL THEN
        NEW.name := NEW.title;
    END IF;
    IF NEW.objective IS NULL AND NEW.description IS NOT NULL THEN
        NEW.objective := NEW.description;
    END IF;
    IF NEW.description IS NULL AND NEW.objective IS NOT NULL THEN
        NEW.description := NEW.objective;
    END IF;
    IF NEW.tenant_id IS NULL AND NEW.workspace_id IS NOT NULL THEN
        NEW.tenant_id := NEW.workspace_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS campaigns_sync_defaults_trigger ON campaigns;
CREATE TRIGGER campaigns_sync_defaults_trigger
    BEFORE INSERT OR UPDATE ON campaigns
    FOR EACH ROW
    EXECUTE FUNCTION campaigns_sync_defaults();

-- Moves table for execution workflows
CREATE TABLE IF NOT EXISTS moves (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID,
    workspace_id UUID,
    title TEXT,
    description TEXT,
    status TEXT,
    priority INTEGER,
    move_type TEXT,
    tool_requirements JSONB DEFAULT '[]'::JSONB,
    refinement_data JSONB DEFAULT '{}'::JSONB,
    consensus_metrics JSONB DEFAULT '{}'::JSONB,
    decree TEXT,
    reasoning_chain_id UUID,
    campaign_name TEXT,
    checklist JSONB DEFAULT '[]'::JSONB,
    assets JSONB DEFAULT '[]'::JSONB,
    daily_metrics JSONB DEFAULT '[]'::JSONB,
    confidence NUMERIC,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    paused_at TIMESTAMPTZ,
    rag_status TEXT,
    rag_reason TEXT,
    execution_result JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_moves_workspace_id ON moves(workspace_id);
CREATE INDEX IF NOT EXISTS idx_moves_campaign_id ON moves(campaign_id);

-- Radar tables
CREATE TABLE IF NOT EXISTS radar_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    url TEXT NOT NULL,
    scan_frequency VARCHAR(20) DEFAULT 'daily',
    health_score INTEGER DEFAULT 100,
    last_checked TIMESTAMPTZ,
    last_success TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    config JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS radar_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    category VARCHAR(20) NOT NULL,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    strength VARCHAR(10) NOT NULL,
    freshness VARCHAR(10) NOT NULL,
    action_suggestion TEXT,
    source_competitor VARCHAR(255),
    source_url TEXT,
    cluster_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::JSONB
);

CREATE TABLE IF NOT EXISTS radar_signal_evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    signal_id UUID NOT NULL REFERENCES radar_signals(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL,
    source VARCHAR(255) NOT NULL,
    url TEXT,
    content TEXT NOT NULL,
    confidence DECIMAL(3,2) NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::JSONB
);

CREATE TABLE IF NOT EXISTS radar_signal_clusters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    category VARCHAR(20) NOT NULL,
    theme VARCHAR(255) NOT NULL,
    signal_count INTEGER DEFAULT 0,
    strength VARCHAR(10) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS radar_signal_move_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    signal_id UUID NOT NULL REFERENCES radar_signals(id) ON DELETE CASCADE,
    move_id UUID REFERENCES moves(id) ON DELETE CASCADE,
    objective VARCHAR(20) NOT NULL,
    stage VARCHAR(20) NOT NULL,
    channel VARCHAR(50) NOT NULL,
    relevance_score DECIMAL(3,2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS radar_dossiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    campaign_id UUID,
    title VARCHAR(500) NOT NULL,
    summary JSONB DEFAULT '[]'::JSONB,
    pinned_signals JSONB DEFAULT '[]'::JSONB,
    hypotheses JSONB DEFAULT '[]'::JSONB,
    recommended_experiments JSONB DEFAULT '[]'::JSONB,
    copy_snippets JSONB DEFAULT '[]'::JSONB,
    market_narrative JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_published BOOLEAN DEFAULT false
);

CREATE TABLE IF NOT EXISTS radar_scan_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    source_ids JSONB NOT NULL,
    scan_type VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    signals_found INTEGER DEFAULT 0,
    errors JSONB DEFAULT '[]'::JSONB,
    config JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_radar_signals_tenant_category ON radar_signals(tenant_id, category);
CREATE INDEX IF NOT EXISTS idx_radar_signals_strength_freshness ON radar_signals(strength, freshness);
CREATE INDEX IF NOT EXISTS idx_radar_signals_created_at ON radar_signals(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_radar_signal_evidence_signal_id ON radar_signal_evidence(signal_id);
CREATE INDEX IF NOT EXISTS idx_radar_scan_jobs_status ON radar_scan_jobs(status);
CREATE INDEX IF NOT EXISTS idx_radar_dossiers_campaign_id ON radar_dossiers(campaign_id);

-- Notifications tables (minimal compatibility)
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'informational',
    channel VARCHAR(20) NOT NULL DEFAULT 'email',
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    subject VARCHAR(255),
    recipients JSONB NOT NULL DEFAULT '[]'::JSONB,
    sender_id UUID,
    priority VARCHAR(20) DEFAULT 'normal',
    status VARCHAR(20) DEFAULT 'pending',
    delivery_results JSONB DEFAULT '{}'::JSONB,
    read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMPTZ,
    scheduled_at TIMESTAMPTZ,
    sent_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::JSONB
);

CREATE TABLE IF NOT EXISTS notification_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    user_id UUID NOT NULL,
    email_notifications BOOLEAN DEFAULT TRUE,
    sms_notifications BOOLEAN DEFAULT FALSE,
    push_notifications BOOLEAN DEFAULT TRUE,
    in_app_notifications BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(workspace_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_notifications_workspace_id ON notifications(workspace_id);
CREATE INDEX IF NOT EXISTS idx_notifications_tenant_id ON notifications(tenant_id);
