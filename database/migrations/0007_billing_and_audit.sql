CREATE TABLE subscriptions (
    subscription_id text PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    provider text NOT NULL DEFAULT 'razorpay',
    status text NOT NULL,
    plan_amount_inr integer NOT NULL DEFAULT 5000,
    grace_period_ends_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE payment_events (
    payment_event_id text PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    provider_event_id text NOT NULL,
    event_type text NOT NULL,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (provider_event_id)
);

CREATE TABLE org_monthly_costs (
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    month date NOT NULL,
    inference_cost_usd double precision NOT NULL DEFAULT 0,
    scraping_cost_usd double precision NOT NULL DEFAULT 0,
    storage_cost_usd double precision NOT NULL DEFAULT 0,
    session_count integer NOT NULL DEFAULT 0,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (org_id, month)
);

CREATE TABLE system_alerts (
    alert_id text PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    alert_type text NOT NULL,
    severity text NOT NULL,
    title text NOT NULL,
    body text NOT NULL,
    source_table text NOT NULL,
    source_id text,
    dedupe_key text NOT NULL,
    acknowledged_at timestamptz,
    resolved_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (org_id, dedupe_key)
);

CREATE TABLE foundation_cache_events (
    event_id text PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    foundation_version integer NOT NULL,
    event_type text NOT NULL,
    invalidation_scope text NOT NULL,
    affected_sections jsonb NOT NULL DEFAULT '[]'::jsonb,
    cache_key text,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE content_feedback_loops (
    loop_id text PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    campaign_id text REFERENCES campaigns(campaign_id) ON DELETE SET NULL,
    source_asset_id text,
    performance_signal text NOT NULL,
    signal_payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    routed_to text NOT NULL,
    processed_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE payment_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE org_monthly_costs ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation_cache_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_feedback_loops ENABLE ROW LEVEL SECURITY;

CREATE POLICY subscriptions_tenant_isolation ON subscriptions
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

CREATE POLICY payment_events_tenant_isolation ON payment_events
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

CREATE POLICY org_monthly_costs_tenant_isolation ON org_monthly_costs
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

CREATE POLICY system_alerts_tenant_isolation ON system_alerts
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

CREATE POLICY foundation_cache_events_tenant_isolation ON foundation_cache_events
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

CREATE POLICY content_feedback_loops_tenant_isolation ON content_feedback_loops
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

CREATE INDEX payment_events_org_id_created_at_idx ON payment_events (org_id, created_at DESC);
CREATE INDEX org_monthly_costs_org_id_month_idx ON org_monthly_costs (org_id, month DESC);
CREATE INDEX system_alerts_org_id_created_at_idx ON system_alerts (org_id, created_at DESC);
CREATE INDEX system_alerts_org_id_type_idx ON system_alerts (org_id, alert_type, created_at DESC);
CREATE INDEX foundation_cache_events_org_id_created_at_idx ON foundation_cache_events (org_id, created_at DESC);
CREATE INDEX content_feedback_loops_org_id_created_at_idx ON content_feedback_loops (org_id, created_at DESC);
