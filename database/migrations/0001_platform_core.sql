CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

CREATE SCHEMA IF NOT EXISTS app;

CREATE OR REPLACE FUNCTION app.current_org_id() RETURNS uuid AS $$
  SELECT NULLIF(current_setting('app.current_org_id', true), '')::uuid;
$$ LANGUAGE sql STABLE;

CREATE TABLE organizations (
    org_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL,
subscription_status text NOT NULL DEFAULT 'none',
    foundation_version integer NOT NULL DEFAULT 0,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE org_users (
    org_user_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    clerk_user_id text NOT NULL,
    email text NOT NULL,
    role text NOT NULL DEFAULT 'owner',
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (org_id, clerk_user_id)
);

CREATE TABLE audit_logs (
    audit_log_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id uuid REFERENCES organizations(org_id) ON DELETE CASCADE,
    actor_id text,
    operation_type text NOT NULL,
    target_type text NOT NULL,
    target_id text,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE org_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY organizations_tenant_isolation ON organizations
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

CREATE POLICY org_users_tenant_isolation ON org_users
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

CREATE POLICY audit_logs_tenant_isolation ON audit_logs
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());
