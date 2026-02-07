-- RaptorFlow Complete Database Schema (v2.0) - Part 6: Indexes & Performance
-- Database indexes for optimal query performance

-- =====================================
-- 18. PERFORMANCE INDEXES
-- =====================================

-- Workspace indexes (critical for multi-tenant performance)
CREATE INDEX IF NOT EXISTS idx_workspace_members_workspace_id ON workspace_members(workspace_id);
CREATE INDEX IF NOT EXISTS idx_workspace_members_user_id ON workspace_members(user_id);
CREATE INDEX IF NOT EXISTS idx_workspace_members_role ON workspace_members(role);

-- Foundation module indexes
CREATE INDEX IF NOT EXISTS idx_foundation_brand_kits_workspace_id ON foundation_brand_kits(workspace_id);
CREATE INDEX IF NOT EXISTS idx_foundation_brand_kits_active ON foundation_brand_kits(is_active);
CREATE INDEX IF NOT EXISTS idx_foundation_positioning_brand_kit_id ON foundation_positioning(brand_kit_id);
CREATE INDEX IF NOT EXISTS idx_foundation_voice_tones_brand_kit_id ON foundation_voice_tones(brand_kit_id);

-- Campaign indexes
CREATE INDEX IF NOT EXISTS idx_campaigns_workspace_id ON campaigns(workspace_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);
CREATE INDEX IF NOT EXISTS idx_campaigns_objective ON campaigns(objective);
CREATE INDEX IF NOT EXISTS idx_campaigns_created_at ON campaigns(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_campaigns_workspace_status ON campaigns(workspace_id, status);

-- Move indexes
CREATE INDEX IF NOT EXISTS idx_moves_workspace_id ON moves(workspace_id);
CREATE INDEX IF NOT EXISTS idx_moves_campaign_id ON moves(campaign_id);
CREATE INDEX IF NOT EXISTS idx_moves_status ON moves(status);
CREATE INDEX IF NOT EXISTS idx_moves_goal ON moves(goal);
CREATE INDEX IF NOT EXISTS idx_moves_channel ON moves(channel);
CREATE INDEX IF NOT EXISTS idx_moves_priority ON moves(priority DESC);
CREATE INDEX IF NOT EXISTS idx_moves_workspace_status ON moves(workspace_id, status);
CREATE INDEX IF NOT EXISTS idx_moves_due_date ON moves(due_date);

-- Blackbox experiment indexes
CREATE INDEX IF NOT EXISTS idx_blackbox_experiments_workspace_id ON blackbox_experiments(workspace_id);
CREATE INDEX IF NOT EXISTS idx_blackbox_experiments_status ON blackbox_experiments(status);
CREATE INDEX IF NOT EXISTS idx_blackbox_experiments_goal ON blackbox_experiments(goal);
CREATE INDEX IF NOT EXISTS idx_blackbox_experiments_channel ON blackbox_experiments(channel);
CREATE INDEX IF NOT EXISTS idx_blackbox_experiments_created_at ON blackbox_experiments(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_blackbox_experiments_checkin_due ON blackbox_experiments(checkin_due_at);

-- Vector similarity indexes (for embeddings)
CREATE INDEX IF NOT EXISTS idx_blackbox_learnings_embedding ON blackbox_learnings USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_agent_memory_episodic_embedding ON agent_memory_episodic USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_agent_memory_semantic_embedding ON agent_memory_semantic USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_agent_memory_procedural_embedding ON agent_memory_procedural USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_entity_embeddings_embedding ON entity_embeddings USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_fact_store_embedding ON fact_store USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_muse_assets_embedding ON muse_assets USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_knowledge_concepts_embedding ON knowledge_concepts USING ivfflat (embedding vector_cosine_ops);

-- Muse asset indexes
CREATE INDEX IF NOT EXISTS idx_muse_assets_workspace_id ON muse_assets(workspace_id);
CREATE INDEX IF NOT EXISTS idx_muse_assets_type ON muse_assets(asset_type);
CREATE INDEX IF NOT EXISTS idx_muse_assets_status ON muse_assets(status);
CREATE INDEX IF NOT EXISTS idx_muse_assets_created_at ON muse_assets(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_muse_asset_versions_asset_id ON muse_asset_versions(asset_id);
CREATE INDEX IF NOT EXISTS idx_muse_collections_workspace_id ON muse_collections(workspace_id);

-- Skills registry indexes
CREATE INDEX IF NOT EXISTS idx_skills_active ON skills(is_active);
CREATE INDEX IF NOT EXISTS idx_skills_category ON skills(category);
CREATE INDEX IF NOT EXISTS idx_skill_registry_active ON skill_registry(is_active);
CREATE INDEX IF NOT EXISTS idx_skill_registry_category ON skill_registry(category);

-- ICP indexes
CREATE INDEX IF NOT EXISTS idx_icp_profiles_workspace_id ON icp_profiles(workspace_id);
CREATE INDEX IF NOT EXISTS idx_icp_profiles_priority ON icp_profiles(priority);
CREATE INDEX IF NOT EXISTS idx_icp_profiles_status ON icp_profiles(status);
CREATE INDEX IF NOT EXISTS idx_icp_firmographics_icp_id ON icp_firmographics(icp_id);
CREATE INDEX IF NOT EXISTS idx_icp_pain_map_icp_id ON icp_pain_map(icp_id);
CREATE INDEX IF NOT EXISTS idx_icp_psycholinguistics_icp_id ON icp_psycholinguistics(icp_id);
CREATE INDEX IF NOT EXISTS idx_icp_disqualifiers_icp_id ON icp_disqualifiers(icp_id);

-- Radar indexes
CREATE INDEX IF NOT EXISTS idx_radar_signals_workspace_id ON radar_signals(workspace_id);
CREATE INDEX IF NOT EXISTS idx_radar_signals_timestamp ON radar_signals(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_radar_signals_confidence ON radar_signals(confidence);
CREATE INDEX IF NOT EXISTS idx_radar_signals_source_type ON radar_signals(source_type);
CREATE INDEX IF NOT EXISTS idx_radar_signal_angles_signal_id ON radar_signal_angles(signal_id);
CREATE INDEX IF NOT EXISTS idx_radar_dossiers_workspace_id ON radar_dossiers(workspace_id);
CREATE INDEX IF NOT EXISTS idx_radar_dossiers_date ON radar_dossiers(date DESC);

-- Cohort indexes
CREATE INDEX IF NOT EXISTS idx_cohorts_workspace_id ON cohorts(workspace_id);
CREATE INDEX IF NOT EXISTS idx_cohorts_active ON cohorts(is_active);
CREATE INDEX IF NOT EXISTS idx_cohort_members_cohort_id ON cohort_members(cohort_id);
CREATE INDEX IF NOT EXISTS idx_cohort_members_joined_at ON cohort_members(joined_at DESC);

-- Strategy and matrix indexes
CREATE INDEX IF NOT EXISTS idx_strategy_versions_workspace_id ON strategy_versions(workspace_id);
CREATE INDEX IF NOT EXISTS idx_strategy_versions_status ON strategy_versions(status);
CREATE INDEX IF NOT EXISTS idx_matrix_overview_workspace_id ON matrix_overview(workspace_id);
CREATE INDEX IF NOT EXISTS idx_matrix_overview_period ON matrix_overview(period_start DESC);
CREATE INDEX IF NOT EXISTS idx_matrix_kpis_workspace_id ON matrix_kpis(workspace_id);
CREATE INDEX IF NOT EXISTS idx_matrix_kpis_metric_name ON matrix_kpis(metric_name);
CREATE INDEX IF NOT EXISTS idx_matrix_kpis_period ON matrix_kpis(period_start DESC);

-- Payment indexes
CREATE INDEX IF NOT EXISTS idx_subscriptions_workspace_id ON subscriptions(workspace_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_invoices_subscription_id ON invoices(subscription_id);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
CREATE INDEX IF NOT EXISTS idx_invoices_due_date ON invoices(due_date);
CREATE INDEX IF NOT EXISTS idx_payment_methods_workspace_id ON payment_methods(workspace_id);
CREATE INDEX IF NOT EXISTS idx_payment_methods_default ON payment_methods(is_default);

-- User preference indexes
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_user_preferences_workspace_id ON user_preferences(workspace_id);
CREATE INDEX IF NOT EXISTS idx_workspace_settings_workspace_id ON workspace_settings(workspace_id);

-- Telemetry and audit indexes
CREATE INDEX IF NOT EXISTS idx_blackbox_telemetry_workspace_id ON blackbox_telemetry(workspace_id);
CREATE INDEX IF NOT EXISTS idx_blackbox_telemetry_experiment_id ON blackbox_telemetry(experiment_id);
CREATE INDEX IF NOT EXISTS idx_blackbox_telemetry_timestamp ON blackbox_telemetry(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_blackbox_outcomes_workspace_id ON blackbox_outcomes(workspace_id);
CREATE INDEX IF NOT EXISTS idx_blackbox_outcomes_timestamp ON blackbox_outcomes(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_agent_decision_audit_workspace_id ON agent_decision_audit(workspace_id);
CREATE INDEX IF NOT EXISTS idx_agent_decision_audit_agent_id ON agent_decision_audit(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_decision_audit_created_at ON agent_decision_audit(created_at DESC);

-- Knowledge graph indexes
CREATE INDEX IF NOT EXISTS idx_knowledge_concepts_workspace_id ON knowledge_concepts(workspace_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_concepts_type ON knowledge_concepts(concept_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_links_source_id ON knowledge_links(source_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_links_target_id ON knowledge_links(target_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_links_workspace_id ON knowledge_links(workspace_id);

-- ML and checkpointing indexes
CREATE INDEX IF NOT EXISTS idx_ml_feature_store_workspace_id ON ml_feature_store(workspace_id);
CREATE INDEX IF NOT EXISTS idx_ml_feature_store_entity ON ml_feature_store(entity_id, entity_type);
CREATE INDEX IF NOT EXISTS idx_model_lineage_workspace_id ON model_lineage(workspace_id);
CREATE INDEX IF NOT EXISTS idx_graph_threads_workspace_id ON graph_threads(workspace_id);
CREATE INDEX IF NOT EXISTS idx_graph_threads_status ON graph_threads(status);
CREATE INDEX IF NOT EXISTS idx_checkpoints_workspace_id ON checkpoints(workspace_id);
CREATE INDEX IF NOT EXISTS idx_checkpoint_blobs_workspace_id ON checkpoint_blobs(workspace_id);
CREATE INDEX IF NOT EXISTS idx_checkpoint_writes_workspace_id ON checkpoint_writes(workspace_id);
CREATE INDEX IF NOT EXISTS idx_checkpoint_metadata_thread_id ON checkpoint_metadata(thread_id);

-- Campaign KPI and approval indexes
CREATE INDEX IF NOT EXISTS idx_campaign_kpis_campaign_id ON campaign_kpis(campaign_id);
CREATE INDEX IF NOT EXISTS idx_campaign_kpis_metric_name ON campaign_kpis(metric_name);
CREATE INDEX IF NOT EXISTS idx_move_approvals_move_id ON move_approvals(move_id);
CREATE INDEX IF NOT EXISTS idx_move_approvals_status ON move_approvals(status);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_campaigns_workspace_status_created ON campaigns(workspace_id, status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_moves_workspace_status_priority ON moves(workspace_id, status, priority DESC);
CREATE INDEX IF NOT EXISTS idx_experiments_workspace_status_created ON blackbox_experiments(workspace_id, status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_assets_workspace_type_status ON muse_assets(workspace_id, asset_type, status);
CREATE INDEX IF NOT EXISTS idx_signals_workspace_timestamp_confidence ON radar_signals(workspace_id, timestamp DESC, confidence);
