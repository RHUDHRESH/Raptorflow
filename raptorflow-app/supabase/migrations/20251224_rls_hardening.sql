-- Hardening Migration for RaptorFlow RLS and Schema Integrity (2025-12-24)

-- 1. Standardize tenant_id types
-- agent_decision_audit
ALTER TABLE IF EXISTS agent_decision_audit
ALTER COLUMN tenant_id TYPE UUID USING tenant_id::uuid;

-- 2. Add tenant_id to tables missing explicit isolation
ALTER TABLE IF EXISTS agent_memory_episodic ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE IF EXISTS checkpoints ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE IF EXISTS checkpoint_blobs ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE IF EXISTS checkpoint_writes ADD COLUMN IF NOT EXISTS tenant_id UUID;

-- 3. Enable RLS on all tables
ALTER TABLE IF EXISTS foundation_brand_kit ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS foundation_positioning ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS foundation_voice_tone ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS moves ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS move_approvals ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS blackbox_telemetry ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS blackbox_outcomes ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS ml_feature_store ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS agent_memory_episodic ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS agent_memory_semantic ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS skill_registry ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS muse_assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS checkpoints ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS checkpoint_blobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS checkpoint_writes ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS model_lineage ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS knowledge_concepts ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS knowledge_links ENABLE ROW LEVEL SECURITY;

-- 4. Clean up existing basic policies to replace with comprehensive ones
DROP POLICY IF EXISTS tenant_isolation_brand_kit ON foundation_brand_kit;
DROP POLICY IF EXISTS tenant_isolation_campaigns ON campaigns;
DROP POLICY IF EXISTS tenant_isolation_telemetry ON blackbox_telemetry;
DROP POLICY IF EXISTS tenant_isolation_semantic_memory ON agent_memory_semantic;
DROP POLICY IF EXISTS tenant_isolation_kpis ON campaign_kpis;
DROP POLICY IF EXISTS tenant_isolation_audit ON agent_decision_audit;
DROP POLICY IF EXISTS tenant_isolation_positioning ON brand_positioning_intelligence;
DROP POLICY IF EXISTS tenant_isolation_voice ON brand_voice_persona;

-- 5. Comprehensive Tenant Isolation Policies

-- Foundation
CREATE POLICY tenant_isolation_brand_kit ON foundation_brand_kit
    FOR ALL USING (tenant_id = auth.uid()) WITH CHECK (tenant_id = auth.uid());

CREATE POLICY tenant_isolation_positioning ON foundation_positioning
    FOR ALL USING (EXISTS (SELECT 1 FROM foundation_brand_kit WHERE id = brand_kit_id AND tenant_id = auth.uid()));

CREATE POLICY tenant_isolation_voice ON foundation_voice_tone
    FOR ALL USING (EXISTS (SELECT 1 FROM foundation_brand_kit WHERE id = brand_kit_id AND tenant_id = auth.uid()));

-- Campaigns & Moves
CREATE POLICY tenant_isolation_campaigns ON campaigns
    FOR ALL USING (tenant_id = auth.uid()) WITH CHECK (tenant_id = auth.uid());

CREATE POLICY tenant_isolation_moves ON moves
    FOR ALL USING (EXISTS (SELECT 1 FROM campaigns WHERE campaigns.id = moves.campaign_id AND campaigns.tenant_id = auth.uid()));

CREATE POLICY tenant_isolation_move_approvals ON move_approvals
    FOR ALL USING (EXISTS (SELECT 1 FROM moves JOIN campaigns ON moves.campaign_id = campaigns.id WHERE moves.id = move_approvals.move_id AND campaigns.tenant_id = auth.uid()));

CREATE POLICY tenant_isolation_kpis ON campaign_kpis
    FOR ALL USING (EXISTS (SELECT 1 FROM campaigns WHERE campaigns.id = campaign_kpis.campaign_id AND campaigns.tenant_id = auth.uid()));

-- Blackbox & Telemetry
CREATE POLICY tenant_isolation_telemetry ON blackbox_telemetry
    FOR ALL USING (tenant_id = auth.uid()) WITH CHECK (tenant_id = auth.uid());

CREATE POLICY tenant_isolation_outcomes ON blackbox_outcomes
    FOR ALL USING (EXISTS (SELECT 1 FROM campaigns WHERE campaigns.id = blackbox_outcomes.campaign_id AND campaigns.tenant_id = auth.uid()));

CREATE POLICY tenant_isolation_audit ON agent_decision_audit
    FOR ALL USING (tenant_id = auth.uid()) WITH CHECK (tenant_id = auth.uid());

-- Memory & ML
CREATE POLICY tenant_isolation_semantic_memory ON agent_memory_semantic
    FOR ALL USING (tenant_id = auth.uid()) WITH CHECK (tenant_id = auth.uid());

CREATE POLICY tenant_isolation_episodic_memory ON agent_memory_episodic
    FOR ALL USING (tenant_id = auth.uid()) WITH CHECK (tenant_id = auth.uid());

CREATE POLICY tenant_isolation_ml_feature ON ml_feature_store
    FOR ALL USING (EXISTS (SELECT 1 FROM campaigns WHERE id = entity_id AND tenant_id = auth.uid()));

-- Muse Assets
CREATE POLICY tenant_isolation_muse_assets ON muse_assets
    FOR ALL USING ((metadata->>'workspace_id')::uuid = auth.uid()) WITH CHECK ((metadata->>'workspace_id')::uuid = auth.uid());

-- LangGraph Checkpoints
CREATE POLICY tenant_isolation_checkpoints ON checkpoints
    FOR ALL USING (tenant_id = auth.uid()) WITH CHECK (tenant_id = auth.uid());

CREATE POLICY tenant_isolation_checkpoint_blobs ON checkpoint_blobs
    FOR ALL USING (tenant_id = auth.uid()) WITH CHECK (tenant_id = auth.uid());

CREATE POLICY tenant_isolation_checkpoint_writes ON checkpoint_writes
    FOR ALL USING (tenant_id = auth.uid()) WITH CHECK (tenant_id = auth.uid());

-- Knowledge Graph
CREATE POLICY tenant_isolation_knowledge_concepts ON knowledge_concepts
    FOR ALL USING (workspace_id::uuid = auth.uid()) WITH CHECK (workspace_id::uuid = auth.uid());

CREATE POLICY tenant_isolation_knowledge_links ON knowledge_links
    FOR ALL USING (workspace_id::uuid = auth.uid()) WITH CHECK (workspace_id::uuid = auth.uid());

-- Skill Registry (Public Read, Service Write)
CREATE POLICY skill_registry_read ON skill_registry FOR SELECT USING (true);
CREATE POLICY skill_registry_service ON skill_registry FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY skills_read ON skills FOR SELECT USING (true);
CREATE POLICY skills_service ON skills FOR ALL TO service_role USING (true) WITH CHECK (true);
