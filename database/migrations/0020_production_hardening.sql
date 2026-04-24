CREATE TABLE IF NOT EXISTS clerk_processed_events (
    event_id text PRIMARY KEY,
    event_type text NOT NULL,
    processed boolean NOT NULL DEFAULT false,
    processed_at timestamptz,
    error text,
    created_at timestamptz NOT NULL DEFAULT now(),
    payload jsonb NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS razorpay_events (
    event_id text PRIMARY KEY,
    event_type text NOT NULL,
    org_id uuid REFERENCES organizations(org_id) ON DELETE SET NULL,
    subscription_id text,
    payment_id text,
    order_id text,
    signature text,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    processed boolean NOT NULL DEFAULT false,
    processed_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE payment_events
    ADD COLUMN IF NOT EXISTS event_id uuid DEFAULT gen_random_uuid(),
    ADD COLUMN IF NOT EXISTS razorpay_event_id text,
    ADD COLUMN IF NOT EXISTS payment_id text,
    ADD COLUMN IF NOT EXISTS order_id text,
    ADD COLUMN IF NOT EXISTS amount bigint,
    ADD COLUMN IF NOT EXISTS currency text,
    ADD COLUMN IF NOT EXISTS status text,
    ADD COLUMN IF NOT EXISTS metadata jsonb,
    ADD COLUMN IF NOT EXISTS processed boolean NOT NULL DEFAULT false,
    ADD COLUMN IF NOT EXISTS processed_at timestamptz;

UPDATE payment_events
SET razorpay_event_id = provider_event_id
WHERE razorpay_event_id IS NULL AND provider_event_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS payment_events_razorpay_event_id_uidx
    ON payment_events (razorpay_event_id)
    WHERE razorpay_event_id IS NOT NULL;

CREATE TABLE IF NOT EXISTS ai_generations (
    generation_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    user_id text REFERENCES users(clerk_user_id) ON DELETE SET NULL,
    provider text NOT NULL DEFAULT 'aws-bedrock',
    model_id text NOT NULL,
    purpose text NOT NULL,
    prompt_hash text NOT NULL,
    output_schema text,
    output_valid boolean NOT NULL DEFAULT false,
    input_tokens integer,
    output_tokens integer,
    latency_ms integer,
    error text,
    created_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE clerk_processed_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE razorpay_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_generations ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS clerk_processed_events_service_only ON clerk_processed_events;
CREATE POLICY clerk_processed_events_service_only ON clerk_processed_events
    USING (false)
    WITH CHECK (true);

DROP POLICY IF EXISTS razorpay_events_tenant_isolation ON razorpay_events;
CREATE POLICY razorpay_events_tenant_isolation ON razorpay_events
    USING (org_id IS NULL OR org_id = app.current_org_id())
    WITH CHECK (org_id IS NULL OR org_id = app.current_org_id());

DROP POLICY IF EXISTS ai_generations_tenant_isolation ON ai_generations;
CREATE POLICY ai_generations_tenant_isolation ON ai_generations
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

CREATE INDEX IF NOT EXISTS razorpay_events_org_id_created_at_idx ON razorpay_events (org_id, created_at DESC);
CREATE INDEX IF NOT EXISTS razorpay_events_processed_idx ON razorpay_events (processed, created_at DESC);
CREATE INDEX IF NOT EXISTS ai_generations_org_id_created_at_idx ON ai_generations (org_id, created_at DESC);
CREATE INDEX IF NOT EXISTS ai_generations_model_purpose_idx ON ai_generations (model_id, purpose, created_at DESC);
