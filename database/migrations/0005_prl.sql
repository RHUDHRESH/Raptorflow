CREATE TABLE ripples (
    ripple_id text PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    agent_id uuid NOT NULL,
    campaign_id text,
    scope text NOT NULL,
    hierarchy_level integer NOT NULL,
    memory_class text NOT NULL,
    source text NOT NULL,
    trigger_text text NOT NULL,
    raw_text text NOT NULL,
    summary_text text NOT NULL,
    embedding vector(64),
    simhash bigint[8],
    emotion_vector double precision[8],
    salience double precision NOT NULL DEFAULT 0,
    confidence double precision NOT NULL DEFAULT 0,
    importance_band text NOT NULL DEFAULT 'normal',
    prediction_json jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE ripple_edges (
    edge_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    source_ripple_id text NOT NULL REFERENCES ripples(ripple_id) ON DELETE CASCADE,
    target_ripple_id text NOT NULL REFERENCES ripples(ripple_id) ON DELETE CASCADE,
    edge_type text NOT NULL,
    weight double precision NOT NULL DEFAULT 0,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE agent_essences (
    agent_id uuid PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    avatar_key text NOT NULL,
    essence_core jsonb NOT NULL DEFAULT '{}'::jsonb,
    ego_baseline double precision[8] NOT NULL,
    ego_state double precision[8] NOT NULL,
    skill_atoms jsonb NOT NULL DEFAULT '[]'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (org_id, avatar_key)
);

ALTER TABLE ripples ENABLE ROW LEVEL SECURITY;
ALTER TABLE ripple_edges ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_essences ENABLE ROW LEVEL SECURITY;

CREATE POLICY ripples_tenant_isolation ON ripples
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

CREATE POLICY ripple_edges_tenant_isolation ON ripple_edges
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

CREATE POLICY agent_essences_tenant_isolation ON agent_essences
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

CREATE INDEX ripples_org_agent_created_idx ON ripples (org_id, agent_id, created_at DESC);
CREATE INDEX ripples_org_scope_created_idx ON ripples (org_id, scope, created_at DESC);
CREATE INDEX ripple_edges_org_source_idx ON ripple_edges (org_id, source_ripple_id);
