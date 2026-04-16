-- Add users table and auth indexes
-- Migration for RaptorFlow auth system

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