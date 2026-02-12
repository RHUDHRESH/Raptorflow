-- RLS Performance Optimization
-- Add indexes to support RLS policy performance
-- Created: 2026-02-10

-- =====================================
-- INDEXES FOR RLS POLICY PERFORMANCE
-- =====================================

-- Legacy environments can lag schema rollout. These helpers keep the
-- migration idempotent by skipping indexes/comments when dependencies do not exist.
CREATE OR REPLACE FUNCTION public._rf_try_create_index(
    p_table_regclass text,
    p_sql text
) RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    IF to_regclass(p_table_regclass) IS NULL THEN
        RAISE NOTICE 'Skipping index creation; table % not found.', p_table_regclass;
        RETURN;
    END IF;

    BEGIN
        EXECUTE p_sql;
    EXCEPTION
        WHEN undefined_column THEN
            RAISE NOTICE 'Skipping index creation due to missing column(s): %', p_sql;
        WHEN undefined_object THEN
            RAISE NOTICE 'Skipping index creation due to missing object(s): %', p_sql;
    END;
END;
$$;

CREATE OR REPLACE FUNCTION public._rf_try_comment_index(
    p_index_name text,
    p_comment text
) RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    IF to_regclass(p_index_name) IS NULL THEN
        RAISE NOTICE 'Skipping index comment; index % not found.', p_index_name;
        RETURN;
    END IF;

    EXECUTE format('COMMENT ON INDEX %I IS %L', p_index_name, p_comment);
END;
$$;

-- Workspace isolation indexes
SELECT public._rf_try_create_index('public.workspaces', 'CREATE INDEX IF NOT EXISTS idx_workspaces_id ON workspaces(id)');
SELECT public._rf_try_create_index('public.workspace_members', 'CREATE INDEX IF NOT EXISTS idx_workspace_members_workspace_id ON workspace_members(workspace_id)');
SELECT public._rf_try_create_index('public.workspace_members', 'CREATE INDEX IF NOT EXISTS idx_workspace_members_user_id ON workspace_members(user_id)');

-- Foundation tables
SELECT public._rf_try_create_index('public.foundation_brand_kits', 'CREATE INDEX IF NOT EXISTS idx_foundation_brand_kits_workspace ON foundation_brand_kits(workspace_id)');
SELECT public._rf_try_create_index('public.foundation_positioning', 'CREATE INDEX IF NOT EXISTS idx_foundation_positioning_workspace ON foundation_positioning(workspace_id)');
SELECT public._rf_try_create_index('public.foundation_voice_tones', 'CREATE INDEX IF NOT EXISTS idx_foundation_voice_tones_workspace ON foundation_voice_tones(workspace_id)');
SELECT public._rf_try_create_index('public.foundation_state', 'CREATE INDEX IF NOT EXISTS idx_foundation_state_workspace ON foundation_state(workspace_id)');

-- Campaign and moves
SELECT public._rf_try_create_index('public.campaigns', 'CREATE INDEX IF NOT EXISTS idx_campaigns_workspace ON campaigns(workspace_id)');
SELECT public._rf_try_create_index('public.campaigns', 'CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status)');
SELECT public._rf_try_create_index('public.campaigns', 'CREATE INDEX IF NOT EXISTS idx_campaigns_created_at ON campaigns(created_at DESC)');
SELECT public._rf_try_create_index('public.moves', 'CREATE INDEX IF NOT EXISTS idx_moves_workspace ON moves(workspace_id)');
SELECT public._rf_try_create_index('public.moves', 'CREATE INDEX IF NOT EXISTS idx_moves_campaign ON moves(campaign_id)');
SELECT public._rf_try_create_index('public.moves', 'CREATE INDEX IF NOT EXISTS idx_moves_status ON moves(status)');

-- ICP profiles
SELECT public._rf_try_create_index('public.icp_profiles', 'CREATE INDEX IF NOT EXISTS idx_icp_profiles_workspace ON icp_profiles(workspace_id)');
SELECT public._rf_try_create_index('public.icp_firmographics', 'CREATE INDEX IF NOT EXISTS idx_icp_firmographics_profile ON icp_firmographics(profile_id)');
SELECT public._rf_try_create_index('public.icp_pain_map', 'CREATE INDEX IF NOT EXISTS idx_icp_pain_map_profile ON icp_pain_map(profile_id)');
SELECT public._rf_try_create_index('public.icp_psycholinguistics', 'CREATE INDEX IF NOT EXISTS idx_icp_psycholinguistics_profile ON icp_psycholinguistics(profile_id)');

-- Blackbox experiments
SELECT public._rf_try_create_index('public.blackbox_experiments', 'CREATE INDEX IF NOT EXISTS idx_blackbox_experiments_workspace ON blackbox_experiments(workspace_id)');
SELECT public._rf_try_create_index('public.blackbox_telemetry', 'CREATE INDEX IF NOT EXISTS idx_blackbox_telemetry_experiment ON blackbox_telemetry(experiment_id)');
SELECT public._rf_try_create_index('public.blackbox_outcomes', 'CREATE INDEX IF NOT EXISTS idx_blackbox_outcomes_experiment ON blackbox_outcomes(experiment_id)');

-- Muse assets
SELECT public._rf_try_create_index('public.muse_assets', 'CREATE INDEX IF NOT EXISTS idx_muse_assets_workspace ON muse_assets(workspace_id)');
SELECT public._rf_try_create_index('public.muse_asset_versions', 'CREATE INDEX IF NOT EXISTS idx_muse_asset_versions_asset ON muse_asset_versions(asset_id)');
SELECT public._rf_try_create_index('public.muse_collections', 'CREATE INDEX IF NOT EXISTS idx_muse_collections_workspace ON muse_collections(workspace_id)');

-- Agent memory
SELECT public._rf_try_create_index('public.agent_memory_episodic', 'CREATE INDEX IF NOT EXISTS idx_agent_memory_episodic_workspace ON agent_memory_episodic(workspace_id)');
SELECT public._rf_try_create_index('public.agent_memory_semantic', 'CREATE INDEX IF NOT EXISTS idx_agent_memory_semantic_workspace ON agent_memory_semantic(workspace_id)');
SELECT public._rf_try_create_index('public.agent_memory_procedural', 'CREATE INDEX IF NOT EXISTS idx_agent_memory_procedural_workspace ON agent_memory_procedural(workspace_id)');

-- Composite indexes for common queries
SELECT public._rf_try_create_index('public.campaigns', 'CREATE INDEX IF NOT EXISTS idx_campaigns_workspace_status ON campaigns(workspace_id, status)');
SELECT public._rf_try_create_index('public.moves', 'CREATE INDEX IF NOT EXISTS idx_moves_workspace_status ON moves(workspace_id, status)');
SELECT public._rf_try_create_index('public.campaigns', 'CREATE INDEX IF NOT EXISTS idx_campaigns_workspace_created ON campaigns(workspace_id, created_at DESC)');

-- Partial indexes for active records
SELECT public._rf_try_create_index('public.campaigns', 'CREATE INDEX IF NOT EXISTS idx_campaigns_active ON campaigns(workspace_id, id) WHERE status NOT IN (''archived'', ''deleted'')');
SELECT public._rf_try_create_index('public.moves', 'CREATE INDEX IF NOT EXISTS idx_moves_active ON moves(workspace_id, id) WHERE status NOT IN (''archived'', ''deleted'')');

-- BRIN indexes for timestamp columns (efficient for large tables)
SELECT public._rf_try_create_index('public.agent_decision_audit', 'CREATE INDEX IF NOT EXISTS idx_agent_decision_audit_created_brin ON agent_decision_audit USING BRIN(created_at)');
SELECT public._rf_try_create_index('public.blackbox_telemetry', 'CREATE INDEX IF NOT EXISTS idx_blackbox_telemetry_created_brin ON blackbox_telemetry USING BRIN(created_at)');

-- GIN indexes for JSONB columns
SELECT public._rf_try_create_index('public.campaigns', 'CREATE INDEX IF NOT EXISTS idx_campaigns_metadata_gin ON campaigns USING GIN(metadata)');
SELECT public._rf_try_create_index('public.moves', 'CREATE INDEX IF NOT EXISTS idx_moves_metadata_gin ON moves USING GIN(metadata)');
SELECT public._rf_try_create_index('public.blackbox_experiments', 'CREATE INDEX IF NOT EXISTS idx_blackbox_experiments_config_gin ON blackbox_experiments USING GIN(config)');

-- Covering indexes for frequently accessed columns
SELECT public._rf_try_create_index('public.campaigns', 'CREATE INDEX IF NOT EXISTS idx_campaigns_list ON campaigns(workspace_id, id, name, status, created_at)');
SELECT public._rf_try_create_index('public.moves', 'CREATE INDEX IF NOT EXISTS idx_moves_list ON moves(workspace_id, id, name, status, due_date)');

SELECT public._rf_try_comment_index('idx_campaigns_workspace_status', 'Optimizes workspace + status filtering');
SELECT public._rf_try_comment_index('idx_campaigns_active', 'Partial index for active campaigns only');
SELECT public._rf_try_comment_index('idx_agent_decision_audit_created_brin', 'BRIN index for time-series data');

DROP FUNCTION public._rf_try_comment_index(text, text);
DROP FUNCTION public._rf_try_create_index(text, text);
