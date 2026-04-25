-- Migration: 0022_capability_harness_cortex
-- Avatar Capability Harness Cortex layer

BEGIN;

-- ─────────────────────────────────────────────────────────────────────────────
-- CAPABILITY DEFINITIONS
-- Schema-bound skills executable by the harness
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS capability_definitions (
    capability_id TEXT PRIMARY KEY,
    capability_key TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    domain TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    input_schema JSONB NOT NULL DEFAULT '{}'::jsonb,
    output_schema JSONB NOT NULL DEFAULT '{}'::jsonb,
    required_context JSONB NOT NULL DEFAULT '{}'::jsonb,
    allowed_tools JSONB NOT NULL DEFAULT '[]'::jsonb,
    artifact_type TEXT NOT NULL,
    evaluator_key TEXT NOT NULL DEFAULT 'default',
    ripple_policy JSONB NOT NULL DEFAULT '{}'::jsonb,
    risk_level TEXT NOT NULL DEFAULT 'low',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT capability_definitions_domain_check CHECK (domain IN (
        'foundation', 'positioning', 'offer', 'copy', 'content',
        'proof', 'distribution', 'analysis', 'research', 'operations'
    )),
    CONSTRAINT capability_definitions_risk_level_check CHECK (risk_level IN ('low', 'medium', 'high'))
);

CREATE INDEX IF NOT EXISTS idx_capability_definitions_org_id ON capability_definitions(org_id);
CREATE INDEX IF NOT EXISTS idx_capability_definitions_capability_key ON capability_definitions(capability_key);
CREATE INDEX IF NOT EXISTS idx_capability_definitions_domain ON capability_definitions(domain);
CREATE INDEX IF NOT EXISTS idx_capability_definitions_is_active ON capability_definitions(is_active) WHERE is_active = TRUE;

COMMENT ON TABLE capability_definitions IS 'Schema-bound skills executable by avatars within the harness.';
COMMENT ON COLUMN capability_definitions.capability_key IS 'Dot-notation key: e.g. copy.hooks.generate, foundation.icp.refine';
COMMENT ON COLUMN capability_definitions.domain IS 'Capability domain: foundation, positioning, offer, copy, content, proof, distribution, analysis, research, operations';
COMMENT ON COLUMN capability_definitions.risk_level IS 'Execution risk: low (draft only), medium (strategist model), high (not yet allowed)';
COMMENT ON COLUMN capability_definitions.evaluator_key IS 'Evaluator to use: default, strict, lenient';
COMMENT ON COLUMN capability_definitions.ripple_policy IS 'JSON: { extract: bool, max_ripples: int, types: [string] }';

-- ─────────────────────────────────────────────────────────────────────────────
-- AVATAR CAPABILITY GRANTS
-- Which avatars can invoke which capabilities
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS avatar_capability_grants (
    grant_id TEXT PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    avatar_id TEXT NOT NULL REFERENCES avatars(avatar_id) ON DELETE CASCADE,
    capability_id TEXT NOT NULL REFERENCES capability_definitions(capability_id) ON DELETE CASCADE,
    grant_scope TEXT NOT NULL DEFAULT 'org',
    constraints JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(org_id, avatar_id, capability_id),
    CONSTRAINT avatar_capability_grants_scope_check CHECK (grant_scope IN ('org', 'campaign'))
);

CREATE INDEX IF NOT EXISTS idx_avatar_capability_grants_org_id ON avatar_capability_grants(org_id);
CREATE INDEX IF NOT EXISTS idx_avatar_capability_grants_avatar_id ON avatar_capability_grants(avatar_id);
CREATE INDEX IF NOT EXISTS idx_avatar_capability_grants_capability_id ON avatar_capability_grants(capability_id);
CREATE INDEX IF NOT EXISTS idx_avatar_capability_grants_lookup ON avatar_capability_grants(org_id, avatar_id, capability_id) WHERE is_enabled = TRUE;

COMMENT ON TABLE avatar_capability_grants IS 'Capability grants per avatar within an org.';

-- ─────────────────────────────────────────────────────────────────────────────
-- HARNESS CONTEXT PACKS
-- Assembled context for capability execution
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS harness_context_packs (
    context_pack_id TEXT PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    run_id TEXT REFERENCES harness_runs(run_id) ON DELETE CASCADE,
    capability_id TEXT REFERENCES capability_definitions(capability_id) ON DELETE SET NULL,
    avatar_id TEXT REFERENCES avatars(avatar_id) ON DELETE SET NULL,
    scope TEXT NOT NULL DEFAULT 'run',
    token_budget INT NOT NULL DEFAULT 6000,
    foundation_context JSONB NOT NULL DEFAULT '{}'::jsonb,
    intel_context JSONB NOT NULL DEFAULT '{}'::jsonb,
    campaign_context JSONB NOT NULL DEFAULT '{}'::jsonb,
    office_context JSONB NOT NULL DEFAULT '{}'::jsonb,
    ripple_context JSONB NOT NULL DEFAULT '[]'::jsonb,
    compressed_context TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_harness_context_packs_org_id ON harness_context_packs(org_id);
CREATE INDEX IF NOT EXISTS idx_harness_context_packs_run_id ON harness_context_packs(run_id) WHERE run_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_harness_context_packs_capability_id ON harness_context_packs(capability_id) WHERE capability_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_harness_context_packs_avatar_id ON harness_context_packs(avatar_id) WHERE avatar_id IS NOT NULL;

COMMENT ON TABLE harness_context_packs IS 'Assembled context packs for capability execution.';
COMMENT ON COLUMN harness_context_packs.scope IS 'Context scope: run, capability, artifact';
COMMENT ON COLUMN harness_context_packs.token_budget IS 'Max tokens for this context pack';

-- ─────────────────────────────────────────────────────────────────────────────
-- CAPABILITY RUNS
-- Individual capability executions within a harness run
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS capability_runs (
    capability_run_id TEXT PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    harness_run_id TEXT REFERENCES harness_runs(run_id) ON DELETE SET NULL,
    harness_step_id TEXT REFERENCES harness_steps(step_id) ON DELETE SET NULL,
    avatar_id TEXT REFERENCES avatars(avatar_id) ON DELETE SET NULL,
    capability_id TEXT NOT NULL REFERENCES capability_definitions(capability_id),
    context_pack_id TEXT REFERENCES harness_context_packs(context_pack_id) ON DELETE SET NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    input JSONB NOT NULL DEFAULT '{}'::jsonb,
    output JSONB,
    error_message TEXT,
    model_id TEXT,
    token_usage JSONB NOT NULL DEFAULT '{}'::jsonb,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT capability_runs_status_check CHECK (status IN (
        'queued', 'building_context', 'running', 'completed', 'failed', 'cancelled'
    ))
);

CREATE INDEX IF NOT EXISTS idx_capability_runs_org_id ON capability_runs(org_id);
CREATE INDEX IF NOT EXISTS idx_capability_runs_harness_run_id ON capability_runs(harness_run_id) WHERE harness_run_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_capability_runs_avatar_id ON capability_runs(avatar_id) WHERE avatar_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_capability_runs_capability_id ON capability_runs(capability_id);
CREATE INDEX IF NOT EXISTS idx_capability_runs_status ON capability_runs(org_id, status, created_at DESC);

COMMENT ON TABLE capability_runs IS 'Individual capability executions within a harness run.';
COMMENT ON COLUMN capability_runs.status IS 'queued | building_context | running | completed | failed | cancelled';

-- ─────────────────────────────────────────────────────────────────────────────
-- CAPABILITY ARTIFACTS
-- Outputs produced by capability executions
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS capability_artifacts (
    artifact_id TEXT PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    capability_run_id TEXT REFERENCES capability_runs(capability_run_id) ON DELETE SET NULL,
    harness_run_id TEXT REFERENCES harness_runs(run_id) ON DELETE SET NULL,
    avatar_id TEXT REFERENCES avatars(avatar_id) ON DELETE SET NULL,
    capability_id TEXT REFERENCES capability_definitions(capability_id) ON DELETE SET NULL,
    artifact_type TEXT NOT NULL,
    title TEXT NOT NULL,
    body JSONB NOT NULL DEFAULT '{}'::jsonb,
    status TEXT NOT NULL DEFAULT 'draft',
    version INT NOT NULL DEFAULT 1,
    evaluation JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT capability_artifacts_status_check CHECK (status IN ('draft', 'reviewed', 'approved', 'rejected', 'archived'))
);

CREATE INDEX IF NOT EXISTS idx_capability_artifacts_org_id ON capability_artifacts(org_id);
CREATE INDEX IF NOT EXISTS idx_capability_artifacts_capability_run_id ON capability_artifacts(capability_run_id) WHERE capability_run_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_capability_artifacts_harness_run_id ON capability_artifacts(harness_run_id) WHERE harness_run_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_capability_artifacts_avatar_id ON capability_artifacts(avatar_id) WHERE avatar_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_capability_artifacts_capability_id ON capability_artifacts(capability_id) WHERE capability_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_capability_artifacts_type_status ON capability_artifacts(org_id, artifact_type, status);

COMMENT ON TABLE capability_artifacts IS 'Outputs produced by capability executions.';
COMMENT ON COLUMN capability_artifacts.artifact_type IS 'Type: hook_set, icp_refined, positioning, offer_design, calendar_plan';
COMMENT ON COLUMN capability_artifacts.status IS 'Lifecycle: draft | reviewed | approved | rejected | archived';

-- ─────────────────────────────────────────────────────────────────────────────
-- ARTIFACT VERSIONS
-- Version history for capability artifacts
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS artifact_versions (
    artifact_version_id TEXT PRIMARY KEY,
    artifact_id TEXT NOT NULL REFERENCES capability_artifacts(artifact_id) ON DELETE CASCADE,
    org_id UUID NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    version INT NOT NULL,
    body JSONB NOT NULL,
    change_reason TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(artifact_id, version)
);

CREATE INDEX IF NOT EXISTS idx_artifact_versions_artifact_id ON artifact_versions(artifact_id);
CREATE INDEX IF NOT EXISTS idx_artifact_versions_org_id ON artifact_versions(org_id);

COMMENT ON TABLE artifact_versions IS 'Version history for capability artifacts.';

-- ─────────────────────────────────────────────────────────────────────────────
-- ARTIFACT RIPPLE LINKS
-- Links between artifacts and learning ripples
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS artifact_ripple_links (
    link_id TEXT PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    artifact_id TEXT NOT NULL REFERENCES capability_artifacts(artifact_id) ON DELETE CASCADE,
    ripple_id TEXT NOT NULL REFERENCES ripples(ripple_id) ON DELETE CASCADE,
    link_type TEXT NOT NULL DEFAULT 'derived_from',
    salience NUMERIC NOT NULL DEFAULT 0.5,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(artifact_id, ripple_id, link_type),
    CONSTRAINT artifact_ripple_links_type_check CHECK (link_type IN ('derived_from', 'refines', 'contradicts', 'extends'))
);

CREATE INDEX IF NOT EXISTS idx_artifact_ripple_links_org_id ON artifact_ripple_links(org_id);
CREATE INDEX IF NOT EXISTS idx_artifact_ripple_links_artifact_id ON artifact_ripple_links(artifact_id);
CREATE INDEX IF NOT EXISTS idx_artifact_ripple_links_ripple_id ON artifact_ripple_links(ripple_id);

COMMENT ON TABLE artifact_ripple_links IS 'Links between capability artifacts and learning ripples.';
COMMENT ON COLUMN artifact_ripple_links.link_type IS 'derived_from | refines | contradicts | extends';

COMMIT;
