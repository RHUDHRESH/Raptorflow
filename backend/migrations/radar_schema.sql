-- Radar Database Schema
-- Core tables for competitive intelligence system

-- Radar Sources (websites, social profiles, etc.)
CREATE TABLE radar_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    url TEXT NOT NULL,
    scan_frequency VARCHAR(20) DEFAULT 'daily',
    health_score INTEGER DEFAULT 100,
    last_checked TIMESTAMP,
    last_success TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    config JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Signals (core competitive intelligence)
CREATE TABLE radar_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    category VARCHAR(20) NOT NULL,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    strength VARCHAR(10) NOT NULL,
    freshness VARCHAR(10) NOT NULL,
    action_suggestion TEXT,
    source_competitor VARCHAR(255),
    source_url TEXT,
    cluster_id UUID,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Signal Evidence
CREATE TABLE radar_signal_evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    signal_id UUID NOT NULL REFERENCES radar_signals(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL,
    source VARCHAR(255) NOT NULL,
    url TEXT,
    content TEXT NOT NULL,
    confidence DECIMAL(3,2) NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Signal Clusters
CREATE TABLE radar_signal_clusters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    category VARCHAR(20) NOT NULL,
    theme VARCHAR(255) NOT NULL,
    signal_count INTEGER DEFAULT 0,
    strength VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Signal-to-Move Mappings
CREATE TABLE radar_signal_move_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    signal_id UUID NOT NULL REFERENCES radar_signals(id) ON DELETE CASCADE,
    move_id UUID NOT NULL REFERENCES moves(id) ON DELETE CASCADE,
    objective VARCHAR(20) NOT NULL,
    stage VARCHAR(20) NOT NULL,
    channel VARCHAR(50) NOT NULL,
    relevance_score DECIMAL(3,2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Dossiers (Intelligence packs)
CREATE TABLE radar_dossiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    campaign_id UUID REFERENCES campaigns(id),
    title VARCHAR(500) NOT NULL,
    summary JSONB DEFAULT '[]',
    pinned_signals JSONB DEFAULT '[]',
    hypotheses JSONB DEFAULT '[]',
    recommended_experiments JSONB DEFAULT '[]',
    copy_snippets JSONB DEFAULT '[]',
    market_narrative JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_published BOOLEAN DEFAULT false
);

-- Scan Jobs (Background processing)
CREATE TABLE radar_scan_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    source_ids JSONB NOT NULL,
    scan_type VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    signals_found INTEGER DEFAULT 0,
    errors JSONB DEFAULT '[]',
    config JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_radar_signals_tenant_category ON radar_signals(tenant_id, category);
CREATE INDEX idx_radar_signals_strength_freshness ON radar_signals(strength, freshness);
CREATE INDEX idx_radar_signals_created_at ON radar_signals(created_at DESC);
CREATE INDEX idx_radar_signal_evidence_signal_id ON radar_signal_evidence(signal_id);
CREATE INDEX idx_radar_scan_jobs_status ON radar_scan_jobs(status);
CREATE INDEX idx_radar_dossiers_campaign_id ON radar_dossiers(campaign_id);

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_radar_sources_updated_at BEFORE UPDATE ON radar_sources FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_radar_signals_updated_at BEFORE UPDATE ON radar_signals FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_radar_signal_clusters_updated_at BEFORE UPDATE ON radar_signal_clusters FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_radar_dossiers_updated_at BEFORE UPDATE ON radar_dossiers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
