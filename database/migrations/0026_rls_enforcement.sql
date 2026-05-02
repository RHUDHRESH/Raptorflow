-- Migration: 0026_rls_enforcement
-- Add missing RLS coverage for org-scoped tables added after the base tenant model.

BEGIN;

ALTER TABLE org_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE org_members FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS org_members_tenant_isolation ON org_members;
CREATE POLICY org_members_tenant_isolation ON org_members
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS sessions_tenant_isolation ON sessions;
CREATE POLICY sessions_tenant_isolation ON sessions
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

ALTER TABLE avatars ENABLE ROW LEVEL SECURITY;
ALTER TABLE avatars FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS avatars_tenant_isolation ON avatars;
CREATE POLICY avatars_tenant_isolation ON avatars
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

ALTER TABLE harness_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE harness_runs FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS harness_runs_tenant_isolation ON harness_runs;
CREATE POLICY harness_runs_tenant_isolation ON harness_runs
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

ALTER TABLE harness_steps ENABLE ROW LEVEL SECURITY;
ALTER TABLE harness_steps FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS harness_steps_tenant_isolation ON harness_steps;
CREATE POLICY harness_steps_tenant_isolation ON harness_steps
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

ALTER TABLE avatar_capability_grants ENABLE ROW LEVEL SECURITY;
ALTER TABLE avatar_capability_grants FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS avatar_capability_grants_tenant_isolation ON avatar_capability_grants;
CREATE POLICY avatar_capability_grants_tenant_isolation ON avatar_capability_grants
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

ALTER TABLE harness_context_packs ENABLE ROW LEVEL SECURITY;
ALTER TABLE harness_context_packs FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS harness_context_packs_tenant_isolation ON harness_context_packs;
CREATE POLICY harness_context_packs_tenant_isolation ON harness_context_packs
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

ALTER TABLE capability_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE capability_runs FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS capability_runs_tenant_isolation ON capability_runs;
CREATE POLICY capability_runs_tenant_isolation ON capability_runs
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

ALTER TABLE capability_artifacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE capability_artifacts FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS capability_artifacts_tenant_isolation ON capability_artifacts;
CREATE POLICY capability_artifacts_tenant_isolation ON capability_artifacts
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

ALTER TABLE artifact_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE artifact_versions FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS artifact_versions_tenant_isolation ON artifact_versions;
CREATE POLICY artifact_versions_tenant_isolation ON artifact_versions
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

ALTER TABLE artifact_ripple_links ENABLE ROW LEVEL SECURITY;
ALTER TABLE artifact_ripple_links FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS artifact_ripple_links_tenant_isolation ON artifact_ripple_links;
CREATE POLICY artifact_ripple_links_tenant_isolation ON artifact_ripple_links
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

ALTER TABLE avatar_souls ENABLE ROW LEVEL SECURITY;
ALTER TABLE avatar_souls FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS avatar_souls_tenant_isolation ON avatar_souls;
CREATE POLICY avatar_souls_tenant_isolation ON avatar_souls
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

ALTER TABLE avatar_memory_edges ENABLE ROW LEVEL SECURITY;
ALTER TABLE avatar_memory_edges FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS avatar_memory_edges_tenant_isolation ON avatar_memory_edges;
CREATE POLICY avatar_memory_edges_tenant_isolation ON avatar_memory_edges
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

ALTER TABLE avatar_instinct_frames ENABLE ROW LEVEL SECURITY;
ALTER TABLE avatar_instinct_frames FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS avatar_instinct_frames_tenant_isolation ON avatar_instinct_frames;
CREATE POLICY avatar_instinct_frames_tenant_isolation ON avatar_instinct_frames
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

ALTER TABLE avatar_presence_states ENABLE ROW LEVEL SECURITY;
ALTER TABLE avatar_presence_states FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS avatar_presence_states_tenant_isolation ON avatar_presence_states;
CREATE POLICY avatar_presence_states_tenant_isolation ON avatar_presence_states
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

ALTER TABLE avatar_debate_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE avatar_debate_events FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS avatar_debate_events_tenant_isolation ON avatar_debate_events;
CREATE POLICY avatar_debate_events_tenant_isolation ON avatar_debate_events
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

ALTER TABLE avatar_artifact_trails ENABLE ROW LEVEL SECURITY;
ALTER TABLE avatar_artifact_trails FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS avatar_artifact_trails_tenant_isolation ON avatar_artifact_trails;
CREATE POLICY avatar_artifact_trails_tenant_isolation ON avatar_artifact_trails
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

ALTER TABLE council_orchestration_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE council_orchestration_runs FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS council_orchestration_runs_tenant_isolation ON council_orchestration_runs;
CREATE POLICY council_orchestration_runs_tenant_isolation ON council_orchestration_runs
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

ALTER TABLE council_avatar_turns ENABLE ROW LEVEL SECURITY;
ALTER TABLE council_avatar_turns FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS council_avatar_turns_tenant_isolation ON council_avatar_turns;
CREATE POLICY council_avatar_turns_tenant_isolation ON council_avatar_turns
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

ALTER TABLE avatar_identity_states ENABLE ROW LEVEL SECURITY;
ALTER TABLE avatar_identity_states FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS avatar_identity_states_tenant_isolation ON avatar_identity_states;
CREATE POLICY avatar_identity_states_tenant_isolation ON avatar_identity_states
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

ALTER TABLE avatar_experience_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE avatar_experience_log FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS avatar_experience_log_tenant_isolation ON avatar_experience_log;
CREATE POLICY avatar_experience_log_tenant_isolation ON avatar_experience_log
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

COMMIT;
