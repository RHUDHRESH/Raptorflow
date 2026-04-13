CREATE TABLE campaigns (
    campaign_id text PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    name text NOT NULL,
    goal text NOT NULL,
    status text NOT NULL DEFAULT 'draft',
    active_move_id text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE campaign_moves (
    move_id text PRIMARY KEY,
    campaign_id text NOT NULL REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    move_type text NOT NULL,
    sequence_number integer NOT NULL,
    status text NOT NULL DEFAULT 'planned',
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE campaign_tasks (
    task_id text PRIMARY KEY,
    move_id text NOT NULL REFERENCES campaign_moves(move_id) ON DELETE CASCADE,
    campaign_id text NOT NULL REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    title text NOT NULL,
    status text NOT NULL DEFAULT 'pending',
    scheduled_date date,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE generated_content (
    content_id text PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    campaign_id text REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    task_id text REFERENCES campaign_tasks(task_id) ON DELETE SET NULL,
    content_type text NOT NULL,
    status text NOT NULL DEFAULT 'generated',
    body jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE campaign_briefs (
    brief_id text PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    campaign_id text REFERENCES campaigns(campaign_id) ON DELETE SET NULL,
    status text NOT NULL DEFAULT 'submitted',
    original_text text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE replan_sessions (
    replan_session_id text PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    campaign_id text NOT NULL REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    trigger_type text NOT NULL,
    status text NOT NULL DEFAULT 'queued',
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE campaign_performance_log (
    performance_log_id text PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    campaign_id text NOT NULL REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    move_id text REFERENCES campaign_moves(move_id) ON DELETE SET NULL,
    metric_name text NOT NULL,
    metric_value numeric(18,6) NOT NULL,
    recorded_at timestamptz NOT NULL
);

ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaign_moves ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaign_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE generated_content ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaign_briefs ENABLE ROW LEVEL SECURITY;
ALTER TABLE replan_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaign_performance_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY campaigns_tenant_isolation ON campaigns
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());
CREATE POLICY campaign_moves_tenant_isolation ON campaign_moves
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());
CREATE POLICY campaign_tasks_tenant_isolation ON campaign_tasks
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());
CREATE POLICY generated_content_tenant_isolation ON generated_content
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());
CREATE POLICY campaign_briefs_tenant_isolation ON campaign_briefs
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());
CREATE POLICY replan_sessions_tenant_isolation ON replan_sessions
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());
CREATE POLICY campaign_performance_log_tenant_isolation ON campaign_performance_log
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());
