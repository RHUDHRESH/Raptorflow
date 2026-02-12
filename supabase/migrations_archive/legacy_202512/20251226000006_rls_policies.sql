-- RaptorFlow Complete Database Schema (v2.0) - Part 7: RLS Policies
-- Row Level Security for workspace isolation and data protection

-- =====================================
-- 19. ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================

-- Enable RLS on all tables
ALTER TABLE workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspace_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation_brand_kits ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation_positioning ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation_voice_tones ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation_state ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE moves ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaign_kpis ENABLE ROW LEVEL SECURITY;
ALTER TABLE move_approvals ENABLE ROW LEVEL SECURITY;
ALTER TABLE blackbox_experiments ENABLE ROW LEVEL SECURITY;
ALTER TABLE blackbox_telemetry ENABLE ROW LEVEL SECURITY;
ALTER TABLE blackbox_outcomes ENABLE ROW LEVEL SECURITY;
ALTER TABLE blackbox_learnings ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_decision_audit ENABLE ROW LEVEL SECURITY;
ALTER TABLE muse_assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE muse_asset_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE muse_collections ENABLE ROW LEVEL SECURITY;
ALTER TABLE skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_registry ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_presets ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_memory_episodic ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_memory_semantic ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_memory_procedural ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_concepts ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_links ENABLE ROW LEVEL SECURITY;
ALTER TABLE entity_embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE fact_store ENABLE ROW LEVEL SECURITY;
ALTER TABLE ml_feature_store ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_lineage ENABLE ROW LEVEL SECURITY;
ALTER TABLE graph_threads ENABLE ROW LEVEL SECURITY;
ALTER TABLE checkpoints ENABLE ROW LEVEL SECURITY;
ALTER TABLE checkpoint_blobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE checkpoint_writes ENABLE ROW LEVEL SECURITY;
ALTER TABLE checkpoint_metadata ENABLE ROW LEVEL SECURITY;
ALTER TABLE icp_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE icp_firmographics ENABLE ROW LEVEL SECURITY;
ALTER TABLE icp_pain_map ENABLE ROW LEVEL SECURITY;
ALTER TABLE icp_psycholinguistics ENABLE ROW LEVEL SECURITY;
ALTER TABLE icp_disqualifiers ENABLE ROW LEVEL SECURITY;
ALTER TABLE radar_signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE radar_signal_angles ENABLE ROW LEVEL SECURITY;
ALTER TABLE radar_dossiers ENABLE ROW LEVEL SECURITY;
ALTER TABLE cohorts ENABLE ROW LEVEL SECURITY;
ALTER TABLE cohort_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE strategy_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE matrix_overview ENABLE ROW LEVEL SECURITY;
ALTER TABLE matrix_kpis ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE payment_methods ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspace_settings ENABLE ROW LEVEL SECURITY;

-- =====================================
-- 20. WORKSPACE RLS POLICIES
-- =====================================

-- Workspaces: Owners and admins can view/edit, members can view
CREATE POLICY "Workspaces: Owners and admins can view all" ON workspaces
    FOR SELECT USING (
        auth.uid() IN (
            SELECT user_id FROM workspace_members
            WHERE workspace_members.workspace_id = workspaces.id
            AND workspace_members.role IN ('owner', 'admin')
        )
    );

CREATE POLICY "Workspaces: Members can view their workspaces" ON workspaces
    FOR SELECT USING (
        auth.uid() IN (
            SELECT user_id FROM workspace_members
            WHERE workspace_members.workspace_id = workspaces.id
        )
    );

CREATE POLICY "Workspaces: Owners and admins can update" ON workspaces
    FOR UPDATE USING (
        auth.uid() IN (
            SELECT user_id FROM workspace_members
            WHERE workspace_members.workspace_id = workspaces.id
            AND workspace_members.role IN ('owner', 'admin')
        )
    );

CREATE POLICY "Workspaces: Owners can insert" ON workspaces
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Workspaces: Owners can delete" ON workspaces
    FOR DELETE USING (
        auth.uid() IN (
            SELECT user_id FROM workspace_members
            WHERE workspace_members.workspace_id = workspaces.id
            AND workspace_members.role = 'owner'
        )
    );

-- Workspace Members: All members can view, owners/admins can manage
CREATE POLICY "Workspace Members: Members can view their workspace members" ON workspace_members
    FOR SELECT USING (
        auth.uid() IN (
            SELECT user_id FROM workspace_members
            WHERE workspace_members.workspace_id = workspace_members.workspace_id
        )
    );

CREATE POLICY "Workspace Members: Owners and admins can insert" ON workspace_members
    FOR INSERT WITH CHECK (
        auth.uid() IN (
            SELECT user_id FROM workspace_members
            WHERE workspace_members.workspace_id = workspace_members.workspace_id
            AND workspace_members.role IN ('owner', 'admin')
        )
    );

CREATE POLICY "Workspace Members: Owners and admins can update" ON workspace_members
    FOR UPDATE USING (
        auth.uid() IN (
            SELECT user_id FROM workspace_members
            WHERE workspace_members.workspace_id = workspace_members.workspace_id
            AND workspace_members.role IN ('owner', 'admin')
        )
    );

CREATE POLICY "Workspace Members: Users can update their own membership" ON workspace_members
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Workspace Members: Owners and admins can delete" ON workspace_members
    FOR DELETE USING (
        auth.uid() IN (
            SELECT user_id FROM workspace_members
            WHERE workspace_members.workspace_id = workspace_members.workspace_id
            AND workspace_members.role IN ('owner', 'admin')
        )
    );

CREATE POLICY "Workspace Members: Users can delete their own membership" ON workspace_members
    FOR DELETE USING (auth.uid() = user_id);

-- =====================================
-- 21. FOUNDATION MODULE RLS POLICIES
-- =====================================

-- Foundation Brand Kits: Workspace members can view, owners/admins can manage
CREATE POLICY "Foundation Brand Kits: Workspace members can view" ON foundation_brand_kits
    FOR SELECT USING (
        workspace_id IN (
            SELECT workspace_id FROM workspace_members
            WHERE workspace_members.user_id = auth.uid()
        )
    );

CREATE POLICY "Foundation Brand Kits: Owners and admins can manage" ON foundation_brand_kits
    FOR ALL USING (
        auth.uid() IN (
            SELECT user_id FROM workspace_members
            WHERE workspace_members.workspace_id = foundation_brand_kits.workspace_id
            AND workspace_members.role IN ('owner', 'admin')
        )
    );

-- Foundation Positioning: Inherit from brand kit policies
CREATE POLICY "Foundation Positioning: Workspace members can view" ON foundation_positioning
    FOR SELECT USING (
        brand_kit_id IN (
            SELECT id FROM foundation_brand_kits
            WHERE workspace_id IN (
                SELECT workspace_id FROM workspace_members
                WHERE workspace_members.user_id = auth.uid()
            )
        )
    );

CREATE POLICY "Foundation Positioning: Owners and admins can manage" ON foundation_positioning
    FOR ALL USING (
        auth.uid() IN (
            SELECT user_id FROM workspace_members
            WHERE workspace_members.workspace_id = (
                SELECT workspace_id FROM foundation_brand_kits
                WHERE foundation_brand_kits.id = foundation_positioning.brand_kit_id
            )
            AND workspace_members.role IN ('owner', 'admin')
        )
    );

-- Foundation Voice Tones: Inherit from brand kit policies
CREATE POLICY "Foundation Voice Tones: Workspace members can view" ON foundation_voice_tones
    FOR SELECT USING (
        brand_kit_id IN (
            SELECT id FROM foundation_brand_kits
            WHERE workspace_id IN (
                SELECT workspace_id FROM workspace_members
                WHERE workspace_members.user_id = auth.uid()
            )
        )
    );

CREATE POLICY "Foundation Voice Tones: Owners and admins can manage" ON foundation_voice_tones
    FOR ALL USING (
        auth.uid() IN (
            SELECT user_id FROM workspace_members
            WHERE workspace_members.workspace_id = (
                SELECT workspace_id FROM foundation_brand_kits
                WHERE foundation_brand_kits.id = foundation_voice_tones.brand_kit_id
            )
            AND workspace_members.role IN ('owner', 'admin')
        )
    );

-- Foundation State: Workspace members can view, owners/admins can manage
CREATE POLICY "Foundation State: Workspace members can view" ON foundation_state
    FOR SELECT USING (
        workspace_id IN (
            SELECT workspace_id FROM workspace_members
            WHERE workspace_members.user_id = auth.uid()
        )
    );

CREATE POLICY "Foundation State: Owners and admins can manage" ON foundation_state
    FOR ALL USING (
        auth.uid() IN (
            SELECT user_id FROM workspace_members
            WHERE workspace_members.workspace_id = foundation_state.workspace_id
            AND workspace_members.role IN ('owner', 'admin')
        )
    );

-- =====================================
-- 22. CAMPAIGNS & MOVES RLS POLICIES
-- =====================================

-- Campaigns: Workspace members can view, owners/admins can manage
CREATE POLICY "Campaigns: Workspace members can view" ON campaigns
    FOR SELECT USING (
        workspace_id IN (
            SELECT workspace_id FROM workspace_members
            WHERE workspace_members.user_id = auth.uid()
        )
    );

CREATE POLICY "Campaigns: Owners and admins can manage" ON campaigns
    FOR ALL USING (
        auth.uid() IN (
            SELECT user_id FROM workspace_members
            WHERE workspace_members.workspace_id = campaigns.workspace_id
            AND workspace_members.role IN ('owner', 'admin')
        )
    );

-- Moves: Workspace members can view, owners/admins can manage
CREATE POLICY "Moves: Workspace members can view" ON moves
    FOR SELECT USING (
        workspace_id IN (
            SELECT workspace_id FROM workspace_members
            WHERE workspace_members.user_id = auth.uid()
        )
    );

CREATE POLICY "Moves: Owners and admins can manage" ON moves
    FOR ALL USING (
        auth.uid() IN (
            SELECT user_id FROM workspace_members
            WHERE workspace_members.workspace_id = moves.workspace_id
            AND workspace_members.role IN ('owner', 'admin')
        )
    );

-- Campaign KPIs: Inherit from campaign policies
CREATE POLICY "Campaign KPIs: Workspace members can view" ON campaign_kpis
    FOR SELECT USING (
        campaign_id IN (
            SELECT id FROM campaigns
            WHERE workspace_id IN (
                SELECT workspace_id FROM workspace_members
                WHERE workspace_members.user_id = auth.uid()
            )
        )
    );

CREATE POLICY "Campaign KPIs: Owners and admins can manage" ON campaign_kpis
    FOR ALL USING (
        auth.uid() IN (
            SELECT user_id FROM workspace_members
            WHERE workspace_members.workspace_id = (
                SELECT workspace_id FROM campaigns
                WHERE campaigns.id = campaign_kpis.campaign_id
            )
            AND workspace_members.role IN ('owner', 'admin')
        )
    );

-- Move Approvals: Workspace members can view, owners/admins can manage
CREATE POLICY "Move Approvals: Workspace members can view" ON move_approvals
    FOR SELECT USING (
        move_id IN (
            SELECT id FROM moves
            WHERE workspace_id IN (
                SELECT workspace_id FROM workspace_members
                WHERE workspace_members.user_id = auth.uid()
            )
        )
    );

CREATE POLICY "Move Approvals: Users can manage their own approvals" ON move_approvals
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Move Approvals: Owners and admins can manage all" ON move_approvals
    FOR ALL USING (
        auth.uid() IN (
            SELECT user_id FROM workspace_members
            WHERE workspace_members.workspace_id = (
                SELECT workspace_id FROM moves
                WHERE moves.id = move_approvals.move_id
            )
            AND workspace_members.role IN ('owner', 'admin')
        )
    );
