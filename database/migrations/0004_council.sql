CREATE TABLE council_sessions (
    session_id text PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    campaign_id text REFERENCES campaigns(campaign_id) ON DELETE SET NULL,
    session_type text NOT NULL,
    status text NOT NULL DEFAULT 'queued',
    question text NOT NULL,
    total_cost_usd double precision NOT NULL DEFAULT 0,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE council_agent_positions (
    position_id text PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    session_id text NOT NULL REFERENCES council_sessions(session_id) ON DELETE CASCADE,
    avatar_key text NOT NULL,
    round_number integer NOT NULL,
    content text NOT NULL,
    extracted_ripple_data jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE council_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE council_agent_positions ENABLE ROW LEVEL SECURITY;

CREATE POLICY council_sessions_tenant_isolation ON council_sessions
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

CREATE POLICY council_agent_positions_tenant_isolation ON council_agent_positions
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());
