-- Migration for RaptorFlow auth and foundation tables
-- Combines: users/auth (0002_auth_indexes) + foundation_snapshots/uploaded_assets (0002_foundation)

-- ============================================
-- PART 1: Users and Auth (from 0002_auth_indexes)
-- ============================================

CREATE TABLE users (
    clerk_user_id text PRIMARY KEY,
    email text NOT NULL,
    first_name text,
    last_name text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

-- Add indexes for auth performance
CREATE INDEX idx_users_clerk_user_id ON users(clerk_user_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_org_users_org_id_clerk_user_id ON org_users(org_id, clerk_user_id);
CREATE INDEX idx_org_users_clerk_user_id ON org_users(clerk_user_id);
CREATE INDEX idx_organizations_subscription_status ON organizations(subscription_status);

-- Enable RLS on users table
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own data (based on JWT claims)
-- This requires the current_user_id() function to extract user_id from JWT
CREATE POLICY users_self_access ON users
    USING (clerk_user_id = current_setting('app.current_user_id', true))
    WITH CHECK (clerk_user_id = current_setting('app.current_user_id', true));

-- Function to set current user ID from JWT
CREATE OR REPLACE FUNCTION app.current_user_id() RETURNS text AS $$
  SELECT NULLIF(current_setting('app.current_user_id', true), '');
$$ LANGUAGE sql STABLE;

-- Add updated_at trigger for users table
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- PART 2: Foundation Tables (from 0002_foundation)
-- ============================================

CREATE TABLE foundation_snapshots (
    foundation_snapshot_id text PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    foundation_version integer NOT NULL,
    sections jsonb NOT NULL DEFAULT '{}'::jsonb,
    source text NOT NULL DEFAULT 'manual',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (org_id, foundation_version)
);

CREATE TABLE uploaded_assets (
    asset_id text PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    asset_kind text NOT NULL,
    storage_key text NOT NULL,
    mime_type text NOT NULL,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE foundation_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE uploaded_assets ENABLE ROW LEVEL SECURITY;

CREATE POLICY foundation_snapshots_tenant_isolation ON foundation_snapshots
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());

CREATE POLICY uploaded_assets_tenant_isolation ON uploaded_assets
    USING (org_id = app.current_org_id())
    WITH CHECK (org_id = app.current_org_id());
