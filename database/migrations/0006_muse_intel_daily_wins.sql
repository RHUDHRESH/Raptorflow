CREATE TABLE muse_conversations (
    conversation_id text PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    route text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE muse_messages (
    message_id text PRIMARY KEY,
    conversation_id text NOT NULL REFERENCES muse_conversations(conversation_id) ON DELETE CASCADE,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    role text NOT NULL,
    body text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE competitor_snapshots (
    snapshot_id text PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    competitor_name text NOT NULL,
    snapshot_type text NOT NULL,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    captured_at timestamptz NOT NULL
);

CREATE TABLE competitor_diffs (
    diff_id text PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    snapshot_id text NOT NULL REFERENCES competitor_snapshots(snapshot_id) ON DELETE CASCADE,
    significance text NOT NULL,
    summary text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE competitor_social_posts (
    post_id text PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    competitor_name text NOT NULL,
    platform text NOT NULL,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    captured_at timestamptz NOT NULL
);

CREATE TABLE ad_library_entries (
    ad_entry_id text PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    competitor_name text NOT NULL,
    platform text NOT NULL,
    screenshot_s3_key text,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    captured_at timestamptz NOT NULL
);

CREATE TABLE seo_rankings (
    ranking_id text PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    keyword text NOT NULL,
    rank integer NOT NULL,
    captured_at timestamptz NOT NULL
);

CREATE TABLE intel_alerts (
    alert_id text PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    campaign_id text REFERENCES campaigns(campaign_id) ON DELETE SET NULL,
    source_type text NOT NULL,
    source_id text NOT NULL,
    alert_type text NOT NULL,
    significance text NOT NULL,
    title text NOT NULL,
    summary text NOT NULL,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    captured_at timestamptz NOT NULL,
    delivered_at timestamptz,
    resolved_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE daily_wins (
    briefing_id text PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    briefing_date date NOT NULL,
    generated_at timestamptz NOT NULL,
    lead_summary text NOT NULL,
    full_briefing text NOT NULL,
    recommended_action text NOT NULL,
    recommended_action_type text NOT NULL,
    recommended_action_data jsonb NOT NULL DEFAULT '{}'::jsonb,
    viewed_at timestamptz,
    acted_on_at timestamptz,
    action_outcome text,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (org_id, briefing_date)
);

CREATE TABLE nudges (
    nudge_id text PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    user_id uuid NOT NULL REFERENCES org_users(org_user_id) ON DELETE CASCADE,
    nudge_type text NOT NULL,
    priority text NOT NULL,
    title text NOT NULL,
    body text NOT NULL,
    action_type text,
    action_data jsonb NOT NULL DEFAULT '{}'::jsonb,
    source_type text NOT NULL,
    source_id text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    delivered_at timestamptz,
    viewed_at timestamptz,
    acted_on_at timestamptz,
    dismissed_at timestamptz,
    suppressed boolean NOT NULL DEFAULT FALSE
);

CREATE TABLE snark_batches (
    batch_id text PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    generated_at timestamptz NOT NULL,
    valid_from timestamptz NOT NULL,
    valid_until timestamptz NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE snark_office_chat (
    message_id text PRIMARY KEY,
    batch_id text NOT NULL REFERENCES snark_batches(batch_id) ON DELETE CASCADE,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    speaker_key text NOT NULL,
    body text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE snark_speech_bubbles (
    bubble_id text PRIMARY KEY,
    batch_id text NOT NULL REFERENCES snark_batches(batch_id) ON DELETE CASCADE,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    speaker_key text NOT NULL,
    body text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE muse_conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE muse_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitor_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitor_diffs ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitor_social_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE ad_library_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE seo_rankings ENABLE ROW LEVEL SECURITY;
ALTER TABLE intel_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_wins ENABLE ROW LEVEL SECURITY;
ALTER TABLE nudges ENABLE ROW LEVEL SECURITY;
ALTER TABLE snark_batches ENABLE ROW LEVEL SECURITY;
ALTER TABLE snark_office_chat ENABLE ROW LEVEL SECURITY;
ALTER TABLE snark_speech_bubbles ENABLE ROW LEVEL SECURITY;

CREATE POLICY muse_conversations_tenant_isolation ON muse_conversations
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());
CREATE POLICY muse_messages_tenant_isolation ON muse_messages
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());
CREATE POLICY competitor_snapshots_tenant_isolation ON competitor_snapshots
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());
CREATE POLICY competitor_diffs_tenant_isolation ON competitor_diffs
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());
CREATE POLICY competitor_social_posts_tenant_isolation ON competitor_social_posts
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());
CREATE POLICY ad_library_entries_tenant_isolation ON ad_library_entries
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());
CREATE POLICY seo_rankings_tenant_isolation ON seo_rankings
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());
CREATE POLICY intel_alerts_tenant_isolation ON intel_alerts
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());
CREATE POLICY daily_wins_tenant_isolation ON daily_wins
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());
CREATE POLICY nudges_tenant_isolation ON nudges
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());
CREATE POLICY snark_batches_tenant_isolation ON snark_batches
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());
CREATE POLICY snark_office_chat_tenant_isolation ON snark_office_chat
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());
CREATE POLICY snark_speech_bubbles_tenant_isolation ON snark_speech_bubbles
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

CREATE INDEX intel_alerts_org_id_captured_at_idx ON intel_alerts (org_id, captured_at DESC);
CREATE INDEX intel_alerts_source_idx ON intel_alerts (org_id, source_type, source_id);
CREATE INDEX daily_wins_org_id_generated_at_idx ON daily_wins (org_id, generated_at DESC);
CREATE INDEX nudges_org_id_user_id_created_at_idx ON nudges (org_id, user_id, created_at DESC);
