-- RaptorFlow Complete Database Schema (v2.0) - Part 8: Functions & Triggers
-- Database functions for business logic and automation

-- =====================================
-- 23. UTILITY FUNCTIONS
-- =====================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to generate workspace slug
CREATE OR REPLACE FUNCTION generate_workspace_slug(name TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN lower(regexp_replace(name, '[^a-zA-Z0-9\s]', '', 'g'));
END;
$$ language 'plpgsql';

-- Function to check if user is workspace member
CREATE OR REPLACE FUNCTION is_workspace_member(workspace_uuid UUID, user_uuid UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM workspace_members
        WHERE workspace_id = workspace_uuid
        AND user_id = user_uuid
    );
END;
$$ language 'plpgsql';

-- Function to get user role in workspace
CREATE OR REPLACE FUNCTION get_user_workspace_role(workspace_uuid UUID, user_uuid UUID)
RETURNS TEXT AS $$
BEGIN
    RETURN (
        SELECT role FROM workspace_members
        WHERE workspace_id = workspace_uuid
        AND user_id = user_uuid
        LIMIT 1
    );
END;
$$ language 'plpgsql';

-- Function to calculate campaign progress
CREATE OR REPLACE FUNCTION calculate_campaign_progress(campaign_uuid UUID)
RETURNS NUMERIC AS $$
DECLARE
    total_moves INTEGER;
    completed_moves INTEGER;
    progress NUMERIC;
BEGIN
    SELECT COUNT(*) INTO total_moves
    FROM moves
    WHERE campaign_id = campaign_uuid;

    SELECT COUNT(*) INTO completed_moves
    FROM moves
    WHERE campaign_id = campaign_uuid
    AND status = 'completed';

    IF total_moves = 0 THEN
        RETURN 0;
    END IF;

    progress := (completed_moves::NUMERIC / total_moves::NUMERIC) * 100;
    RETURN progress;
END;
$$ language 'plpgsql';

-- Function to generate experiment checkin dates
CREATE OR REPLACE FUNCTION generate_experiment_checkin_dates(duration_days INTEGER DEFAULT 7)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
    checkin_due TIMESTAMPTZ;
    checkin_remind TIMESTAMPTZ;
    checkin_expire TIMESTAMPTZ;
BEGIN
    checkin_due := now() + (duration_days || ' days')::INTERVAL;
    checkin_remind := checkin_due - INTERVAL '24 hours';
    checkin_expire := checkin_due + INTERVAL '7 days';

    result := jsonb_build_object(
        'checkin_due_at', checkin_due,
        'checkin_remind_at', checkin_remind,
        'checkin_expire_at', checkin_expire
    );

    RETURN result;
END;
$$ language 'plpgsql';

-- =====================================
-- 24. VECTOR SIMILARITY FUNCTIONS
-- =====================================

-- Function to find similar learnings
CREATE OR REPLACE FUNCTION find_similar_learnings(query_embedding VECTOR(768), workspace_uuid UUID, limit_count INTEGER DEFAULT 5)
RETURNS TABLE (
    learning_id UUID,
    content TEXT,
    similarity_score REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        bl.id,
        bl.content,
        1 - (bl.embedding <=> query_embedding) as similarity
    FROM blackbox_learnings bl
    WHERE bl.workspace_id = workspace_uuid
    AND bl.embedding IS NOT NULL
    ORDER BY bl.embedding <=> query_embedding
    LIMIT limit_count;
END;
$$ language 'plpgsql';

-- Function to find similar assets
CREATE OR REPLACE FUNCTION find_similar_assets(query_embedding VECTOR(768), workspace_uuid UUID, asset_type_param TEXT DEFAULT NULL, limit_count INTEGER DEFAULT 5)
RETURNS TABLE (
    asset_id UUID,
    content TEXT,
    asset_type TEXT,
    similarity_score REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ma.id,
        ma.content,
        ma.asset_type,
        1 - (ma.embedding <=> query_embedding) as similarity
    FROM muse_assets ma
    WHERE ma.workspace_id = workspace_uuid
    AND ma.embedding IS NOT NULL
    AND (asset_type_param IS NULL OR ma.asset_type = asset_type_param)
    ORDER BY ma.embedding <=> query_embedding
    LIMIT limit_count;
END;
$$ language 'plpgsql';

-- Function to find similar concepts
CREATE OR REPLACE FUNCTION find_similar_concepts(query_embedding VECTOR(768), workspace_uuid UUID, concept_type_param TEXT DEFAULT NULL, limit_count INTEGER DEFAULT 5)
RETURNS TABLE (
    concept_id UUID,
    name TEXT,
    description TEXT,
    similarity_score REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        kc.id,
        kc.name,
        kc.description,
        1 - (kc.embedding <=> query_embedding) as similarity
    FROM knowledge_concepts kc
    WHERE kc.workspace_id = workspace_uuid
    AND kc.embedding IS NOT NULL
    AND (concept_type_param IS NULL OR kc.concept_type = concept_type_param)
    ORDER BY kc.embedding <=> query_embedding
    LIMIT limit_count;
END;
$$ language 'plpgsql';

-- =====================================
-- 25. BUSINESS LOGIC FUNCTIONS
-- =====================================

-- Function to create new campaign with KPIs
CREATE OR REPLACE FUNCTION create_campaign_with_kpis(
    workspace_uuid UUID,
    campaign_title TEXT,
    campaign_objective TEXT,
    campaign_description TEXT DEFAULT NULL,
    primary_kpi_name TEXT DEFAULT NULL,
    kpi_target_value NUMERIC DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    campaign_id UUID;
BEGIN
    -- Create campaign
    INSERT INTO campaigns (workspace_id, title, description, objective, primary_kpi)
    VALUES (workspace_uuid, campaign_title, campaign_description, campaign_objective, primary_kpi_name)
    RETURNING id INTO campaign_id;

    -- Create KPI if provided
    IF primary_kpi_name IS NOT NULL AND kpi_target_value IS NOT NULL THEN
        INSERT INTO campaign_kpis (campaign_id, metric_name, target_value)
        VALUES (campaign_id, primary_kpi_name, kpi_target_value);
    END IF;

    RETURN campaign_id;
END;
$$ language 'plpgsql';

-- Function to launch experiment with checkin dates
CREATE OR REPLACE FUNCTION launch_experiment(
    experiment_uuid UUID
)
RETURNS BOOLEAN AS $$
DECLARE
    checkin_dates JSONB;
BEGIN
    -- Update experiment status and set checkin dates
    UPDATE blackbox_experiments
    SET
        status = 'launched',
        launched_at = now(),
        checkin_due_at = (now() + (duration_days || ' days')::INTERVAL),
        checkin_remind_at = (now() + (duration_days || ' days')::INTERVAL - INTERVAL '24 hours'),
        checkin_expire_at = (now() + (duration_days || ' days')::INTERVAL + INTERVAL '7 days')
    WHERE id = experiment_uuid;

    RETURN FOUND;
END;
$$ language 'plpgsql';

-- Function to archive completed campaigns
CREATE OR REPLACE FUNCTION archive_completed_campaigns(workspace_uuid UUID)
RETURNS INTEGER AS $$
DECLARE
    archived_count INTEGER;
BEGIN
    UPDATE campaigns
    SET status = 'archived'
    WHERE workspace_id = workspace_uuid
    AND status = 'wrapup'
    AND updated_at < now() - INTERVAL '30 days';

    GET DIAGNOSTICS archived_count = ROW_COUNT;
    RETURN archived_count;
END;
$$ language 'plpgsql';

-- Function to calculate workspace usage metrics
CREATE OR REPLACE FUNCTION calculate_workspace_metrics(workspace_uuid UUID)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
    total_campaigns INTEGER;
    active_campaigns INTEGER;
    total_moves INTEGER;
    completed_moves INTEGER;
    total_experiments INTEGER;
    active_experiments INTEGER;
    total_assets INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_campaigns FROM campaigns WHERE workspace_id = workspace_uuid;
    SELECT COUNT(*) INTO active_campaigns FROM campaigns WHERE workspace_id = workspace_uuid AND status = 'active';
    SELECT COUNT(*) INTO total_moves FROM moves WHERE workspace_id = workspace_uuid;
    SELECT COUNT(*) INTO completed_moves FROM moves WHERE workspace_id = workspace_uuid AND status = 'completed';
    SELECT COUNT(*) INTO total_experiments FROM blackbox_experiments WHERE workspace_id = workspace_uuid;
    SELECT COUNT(*) INTO active_experiments FROM blackbox_experiments WHERE workspace_id = workspace_uuid AND status = 'launched';
    SELECT COUNT(*) INTO total_assets FROM muse_assets WHERE workspace_id = workspace_uuid;

    result := jsonb_build_object(
        'total_campaigns', total_campaigns,
        'active_campaigns', active_campaigns,
        'total_moves', total_moves,
        'completed_moves', completed_moves,
        'total_experiments', total_experiments,
        'active_experiments', active_experiments,
        'total_assets', total_assets,
        'calculated_at', now()
    );

    RETURN result;
END;
$$ language 'plpgsql';

-- =====================================
-- 26. TRIGGERS
-- =====================================

-- Updated timestamp triggers
CREATE TRIGGER update_workspaces_updated_at BEFORE UPDATE ON workspaces
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_foundation_brand_kits_updated_at BEFORE UPDATE ON foundation_brand_kits
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_foundation_positioning_updated_at BEFORE UPDATE ON foundation_positioning
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_campaigns_updated_at BEFORE UPDATE ON campaigns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_moves_updated_at BEFORE UPDATE ON moves
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_muse_assets_updated_at BEFORE UPDATE ON muse_assets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_muse_collections_updated_at BEFORE UPDATE ON muse_collections
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_skills_updated_at BEFORE UPDATE ON skills
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agent_memory_semantic_updated_at BEFORE UPDATE ON agent_memory_semantic
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agent_memory_procedural_updated_at BEFORE UPDATE ON agent_memory_procedural
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_concepts_updated_at BEFORE UPDATE ON knowledge_concepts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_entity_embeddings_updated_at BEFORE UPDATE ON entity_embeddings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_icp_profiles_updated_at BEFORE UPDATE ON icp_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_icp_firmographics_updated_at BEFORE UPDATE ON icp_firmographics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_icp_pain_map_updated_at BEFORE UPDATE ON icp_pain_map
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_icp_psycholinguistics_updated_at BEFORE UPDATE ON icp_psycholinguistics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_radar_dossiers_updated_at BEFORE UPDATE ON radar_dossiers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cohorts_updated_at BEFORE UPDATE ON cohorts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_strategy_versions_updated_at BEFORE UPDATE ON strategy_versions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_matrix_overview_updated_at BEFORE UPDATE ON matrix_overview
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_invoices_updated_at BEFORE UPDATE ON invoices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payment_methods_updated_at BEFORE UPDATE ON payment_methods
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workspace_settings_updated_at BEFORE UPDATE ON workspace_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to validate workspace membership
CREATE OR REPLACE FUNCTION validate_workspace_membership()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if user is workspace member for inserts
    IF TG_OP = 'INSERT' THEN
        IF NOT is_workspace_member(NEW.workspace_id, NEW.user_id) THEN
            RAISE EXCEPTION 'User is not a member of this workspace';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply membership validation trigger
CREATE TRIGGER validate_workspace_membership_trigger BEFORE INSERT ON workspace_members
    FOR EACH ROW EXECUTE FUNCTION validate_workspace_membership();
