-- Complete System Setup Migration
-- This migration sets up all tables, RLS policies, functions, and triggers

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create custom types
CREATE TYPE user_role AS ENUM ('user', 'admin', 'super_admin', 'support', 'billing_admin');
CREATE TYPE onboarding_status AS ENUM ('pending_workspace', 'pending_storage', 'pending_plan_selection', 'pending_payment', 'active', 'suspended', 'cancelled');
CREATE TYPE subscription_status AS ENUM ('trialing', 'active', 'past_due', 'canceled', 'unpaid', 'incomplete');
CREATE TYPE billing_cycle AS ENUM ('monthly', 'yearly');
CREATE TYPE action_category AS ENUM ('auth', 'profile', 'workspace', 'subscription', 'payment', 'admin', 'security');
CREATE TYPE security_event_type AS ENUM ('login_success', 'login_failure', 'password_change', 'mfa_enabled', 'mfa_disabled', 'suspicious_activity', 'data_export', 'account_deleted');

-- Enhanced users table with additional fields
ALTER TABLE users ADD COLUMN IF NOT EXISTS role user_role DEFAULT 'user';
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_number TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS timezone TEXT DEFAULT 'UTC';
ALTER TABLE users ADD COLUMN IF NOT EXISTS language TEXT DEFAULT 'en';
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS login_count INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS mfa_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS mfa_secret TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS backup_codes TEXT[];
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS data_retention_days INTEGER DEFAULT 365;
ALTER TABLE users ADD COLUMN IF NOT EXISTS gdpr_consent_given BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS gdpr_consent_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS marketing_consent BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS created_ip_address INET;
ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_ip_address INET;

-- Admin actions table for tracking admin operations
CREATE TABLE IF NOT EXISTS admin_actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    admin_id UUID REFERENCES users(id) ON DELETE CASCADE,
    target_user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    action TEXT NOT NULL,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User sessions table for active session management
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_token TEXT UNIQUE NOT NULL,
    refresh_token TEXT UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT,
    device_fingerprint TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

-- Enhanced security events table
ALTER TABLE security_events ADD COLUMN IF NOT EXISTS session_id UUID REFERENCES user_sessions(id) ON DELETE SET NULL;
ALTER TABLE security_events ADD COLUMN IF NOT EXISTS device_fingerprint TEXT;
ALTER TABLE security_events ADD COLUMN IF NOT EXISTS risk_score INTEGER DEFAULT 0;
ALTER TABLE security_events ADD COLUMN IF NOT EXISTS resolved BOOLEAN DEFAULT FALSE;
ALTER TABLE security_events ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE security_events ADD COLUMN IF NOT EXISTS resolved_by UUID REFERENCES users(id);

-- Subscription usage tracking
CREATE TABLE IF NOT EXISTS subscription_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subscription_id UUID REFERENCES subscriptions(id) ON DELETE CASCADE,
    metric_name TEXT NOT NULL,
    metric_value BIGINT DEFAULT 0,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(subscription_id, metric_name, period_start)
);

-- Webhook logs for tracking external service communications
CREATE TABLE IF NOT EXISTS webhook_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload JSONB,
    response_status INTEGER,
    response_body TEXT,
    attempt_count INTEGER DEFAULT 1,
    success BOOLEAN DEFAULT FALSE,
    next_retry_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Data export requests for GDPR compliance
CREATE TABLE IF NOT EXISTS data_export_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    status TEXT DEFAULT 'pending',
    format TEXT DEFAULT 'json',
    expires_at TIMESTAMP WITH TIME ZONE,
    download_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Email logs for tracking all communications
CREATE TABLE IF NOT EXISTS email_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    template_name TEXT NOT NULL,
    to_email TEXT NOT NULL,
    subject TEXT,
    status TEXT DEFAULT 'pending',
    provider TEXT DEFAULT 'resend',
    provider_id TEXT,
    error_message TEXT,
    sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- API rate limiting
CREATE TABLE IF NOT EXISTS api_rate_limits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    identifier TEXT NOT NULL, -- IP address or user ID
    endpoint TEXT NOT NULL,
    request_count INTEGER DEFAULT 1,
    window_start TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    window_end TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(identifier, endpoint, window_start)
);

-- System settings for configuration
CREATE TABLE IF NOT EXISTS system_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key TEXT UNIQUE NOT NULL,
    value JSONB NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default system settings
INSERT INTO system_settings (key, value, description, is_public) VALUES
('maintenance_mode', 'false', 'System maintenance mode toggle', true),
('max_login_attempts', '5', 'Maximum failed login attempts before lockout', false),
('session_timeout_hours', '24', 'Session timeout in hours', false),
('password_min_length', '8', 'Minimum password length', false),
('enable_mfa_for_admins', 'true', 'Require MFA for admin users', false),
('data_retention_days', '365', 'Default data retention period in days', false),
('gdpr_enabled', 'true', 'GDPR compliance enabled', true),
('support_email', 'support@raptorflow.com', 'Customer support email', true)
ON CONFLICT (key) DO NOTHING;

-- Enhanced RLS Policies

-- Users table policies
DROP POLICY IF EXISTS "Users can view own profile" ON users;
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = auth_user_id);

DROP POLICY IF EXISTS "Admins can view all users" ON users;
CREATE POLICY "Admins can view all users" ON users
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE auth.uid() = auth_user_id 
            AND role IN ('admin', 'super_admin', 'support', 'billing_admin')
        )
    );

DROP POLICY IF EXISTS "Users can update own profile" ON users;
CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = auth_user_id);

DROP POLICY IF EXISTS "Admins can update users" ON users;
CREATE POLICY "Admins can update users" ON users
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE auth.uid() = auth_user_id 
            AND role IN ('admin', 'super_admin')
        )
    );

DROP POLICY IF EXISTS "Super admins can manage roles" ON users;
CREATE POLICY "Super admins can manage roles" ON users
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE auth.uid() = auth_user_id 
            AND role = 'super_admin'
        )
    );

-- Workspaces policies
DROP POLICY IF EXISTS "Users can view own workspaces" ON workspaces;
CREATE POLICY "Users can view own workspaces" ON workspaces
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM user_workspaces 
            WHERE user_workspaces.workspace_id = workspaces.id 
            AND user_workspaces.user_id = (
                SELECT id FROM users WHERE auth.uid() = auth_user_id
            )
        )
    );

DROP POLICY IF EXISTS "Admins can view all workspaces" ON workspaces;
CREATE POLICY "Admins can view all workspaces" ON workspaces
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE auth.uid() = auth_user_id 
            AND role IN ('admin', 'super_admin', 'support')
        )
    );

-- Subscriptions policies
DROP POLICY IF EXISTS "Users can view own subscription" ON subscriptions;
CREATE POLICY "Users can view own subscription" ON subscriptions
    FOR SELECT USING (
        user_id = (SELECT id FROM users WHERE auth.uid() = auth_user_id)
    );

DROP POLICY IF EXISTS "Admins can view all subscriptions" ON subscriptions;
CREATE POLICY "Admins can view all subscriptions" ON subscriptions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE auth.uid() = auth_user_id 
            AND role IN ('admin', 'super_admin', 'billing_admin')
        )
    );

-- Payment transactions policies
DROP POLICY IF EXISTS "Users can view own transactions" ON payment_transactions;
CREATE POLICY "Users can view own transactions" ON payment_transactions
    FOR SELECT USING (
        user_id = (SELECT id FROM users WHERE auth.uid() = auth_user_id)
    );

DROP POLICY IF EXISTS "Admins can view all transactions" ON payment_transactions;
CREATE POLICY "Admins can view all transactions" ON payment_transactions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE auth.uid() = auth_user_id 
            AND role IN ('admin', 'super_admin', 'billing_admin')
        )
    );

-- Audit logs policies
DROP POLICY IF EXISTS "Users can view own audit logs" ON audit_logs;
CREATE POLICY "Users can view own audit logs" ON audit_logs
    FOR SELECT USING (
        actor_id = (SELECT id FROM users WHERE auth.uid() = auth_user_id)
    );

DROP POLICY IF EXISTS "Admins can view all audit logs" ON audit_logs;
CREATE POLICY "Admins can view all audit logs" ON audit_logs
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE auth.uid() = auth_user_id 
            AND role IN ('admin', 'super_admin', 'support')
        )
    );

-- Security events policies
DROP POLICY IF EXISTS "Users can view own security events" ON security_events;
CREATE POLICY "Users can view own security events" ON security_events
    FOR SELECT USING (
        user_id = (SELECT id FROM users WHERE auth.uid() = auth_user_id)
    );

DROP POLICY IF EXISTS "Admins can view all security events" ON security_events;
CREATE POLICY "Admins can view all security events" ON security_events
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE auth.uid() = auth_user_id 
            AND role IN ('admin', 'super_admin', 'support')
        )
    );

-- Admin actions policies
DROP POLICY IF EXISTS "Admins can view admin actions" ON admin_actions;
CREATE POLICY "Admins can view admin actions" ON admin_actions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE auth.uid() = auth_user_id 
            AND role IN ('admin', 'super_admin')
        )
    );

DROP POLICY IF EXISTS "Admins can log actions" ON admin_actions;
CREATE POLICY "Admins can log actions" ON admin_actions
    FOR INSERT WITH CHECK (
        admin_id = (SELECT id FROM users WHERE auth.uid() = auth_user_id)
    );

-- User sessions policies
DROP POLICY IF EXISTS "Users can view own sessions" ON user_sessions;
CREATE POLICY "Users can view own sessions" ON user_sessions
    FOR SELECT USING (
        user_id = (SELECT id FROM users WHERE auth.uid() = auth_user_id)
    );

DROP POLICY IF EXISTS "Users can delete own sessions" ON user_sessions;
CREATE POLICY "Users can delete own sessions" ON user_sessions
    FOR DELETE USING (
        user_id = (SELECT id FROM users WHERE auth.uid() = auth_user_id)
    );

-- Data export requests policies
DROP POLICY IF EXISTS "Users can view own export requests" ON data_export_requests;
CREATE POLICY "Users can view own export requests" ON data_export_requests
    FOR SELECT USING (
        user_id = (SELECT id FROM users WHERE auth.uid() = auth_user_id)
    );

DROP POLICY IF EXISTS "Users can create export requests" ON data_export_requests;
CREATE POLICY "Users can create export requests" ON data_export_requests
    FOR INSERT WITH CHECK (
        user_id = (SELECT id FROM users WHERE auth.uid() = auth_user_id)
    );

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_onboarding_status ON users(onboarding_status);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
CREATE INDEX IF NOT EXISTS idx_users_last_login_at ON users(last_login_at);

CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_session_token ON user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);

CREATE INDEX IF NOT EXISTS idx_audit_logs_actor_id ON audit_logs(actor_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action_category ON audit_logs(action_category);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);

CREATE INDEX IF NOT EXISTS idx_security_events_user_id ON security_events(user_id);
CREATE INDEX IF NOT EXISTS idx_security_events_event_type ON security_events(event_type);
CREATE INDEX IF NOT EXISTS idx_security_events_created_at ON security_events(created_at);

CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_current_period_end ON subscriptions(current_period_end);

CREATE INDEX IF NOT EXISTS idx_payment_transactions_user_id ON payment_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_payment_transactions_status ON payment_transactions(status);
CREATE INDEX IF NOT EXISTS idx_payment_transactions_created_at ON payment_transactions(created_at);

-- Create functions for automated processes

-- Function to update login count and last login
CREATE OR REPLACE FUNCTION update_login_info()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE users 
    SET 
        last_login_at = NOW(),
        login_count = COALESCE(login_count, 0) + 1,
        updated_ip_address = inet_client_addr()
    WHERE id = NEW.user_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger for login tracking
DROP TRIGGER IF EXISTS on_session_created ON user_sessions;
CREATE TRIGGER on_session_created
    AFTER INSERT ON user_sessions
    FOR EACH ROW EXECUTE FUNCTION update_login_info();

-- Function to clean up expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS void AS $$
BEGIN
    UPDATE user_sessions 
    SET is_active = false 
    WHERE expires_at < NOW() AND is_active = true;
    
    DELETE FROM user_sessions 
    WHERE expires_at < NOW() - INTERVAL '7 days';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check and update subscription status
CREATE OR REPLACE FUNCTION update_subscription_status()
RETURNS TRIGGER AS $$
BEGIN
    -- Update subscription to past_due if period has ended
    IF NEW.current_period_end < NOW() AND NEW.status = 'active' THEN
        UPDATE subscriptions 
        SET status = 'past_due' 
        WHERE id = NEW.id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger for subscription status
DROP TRIGGER IF EXISTS check_subscription_status ON subscriptions;
CREATE TRIGGER check_subscription_status
    AFTER UPDATE ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_subscription_status();

-- Function to log security events
CREATE OR REPLACE FUNCTION log_security_event(
    p_user_id UUID,
    p_event_type security_event_type,
    p_ip_address INET DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL,
    p_details JSONB DEFAULT NULL
)
RETURNS void AS $$
BEGIN
    INSERT INTO security_events (
        user_id,
        event_type,
        ip_address,
        user_agent,
        details,
        risk_score
    ) VALUES (
        p_user_id,
        p_event_type,
        COALESCE(p_ip_address, inet_client_addr()),
        p_user_agent,
        p_details,
        CASE 
            WHEN p_event_type = 'login_failure' THEN 30
            WHEN p_event_type = 'suspicious_activity' THEN 80
            ELSE 0
        END
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get user permissions
CREATE OR REPLACE FUNCTION get_user_permissions(p_user_id UUID)
RETURNS JSONB AS $$
DECLARE
    user_record users%ROWTYPE;
    permissions JSONB;
BEGIN
    SELECT * INTO user_record FROM users WHERE id = p_user_id;
    
    IF NOT FOUND THEN
        RETURN '[]'::JSONB;
    END IF;
    
    permissions := '[]'::JSONB;
    
    -- Base permissions for all users
    permissions := permissions || '["view_own_profile", "update_own_profile"]'::JSONB;
    
    -- Active user permissions
    IF user_record.onboarding_status = 'active' THEN
        permissions := permissions || '["access_dashboard", "manage_workspace"]'::JSONB;
    END IF;
    
    -- Role-based permissions
    CASE user_record.role
        WHEN 'support' THEN
            permissions := permissions || '["view_all_users", "view_all_subscriptions"]'::JSONB;
        WHEN 'billing_admin' THEN
            permissions := permissions || '["view_all_subscriptions", "manage_subscriptions"]'::JSONB;
        WHEN 'admin' THEN
            permissions := permissions || '["view_all_users", "manage_users", "view_all_subscriptions", "manage_subscriptions", "view_audit_logs"]'::JSONB;
        WHEN 'super_admin' THEN
            permissions := permissions || '["view_all_users", "manage_users", "manage_roles", "view_all_subscriptions", "manage_subscriptions", "view_audit_logs", "manage_system_settings", "impersonate_users"]'::JSONB;
    END CASE;
    
    RETURN permissions;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create view for admin dashboard
CREATE OR REPLACE VIEW admin_dashboard AS
SELECT 
    (SELECT COUNT(*) FROM users) as total_users,
    (SELECT COUNT(*) FROM users WHERE onboarding_status = 'active') as active_users,
    (SELECT COUNT(*) FROM users WHERE onboarding_status = 'pending_payment') as pending_payments,
    (SELECT COUNT(*) FROM subscriptions WHERE status = 'active') as active_subscriptions,
    (SELECT COUNT(*) FROM subscriptions WHERE status = 'past_due') as past_due_subscriptions,
    (SELECT SUM(amount_paise)/100 FROM payment_transactions WHERE status = 'completed' AND created_at >= CURRENT_DATE) as daily_revenue,
    (SELECT SUM(amount_paise)/100 FROM payment_transactions WHERE status = 'completed' AND created_at >= CURRENT_DATE - INTERVAL '7 days') as weekly_revenue,
    (SELECT SUM(amount_paise)/100 FROM payment_transactions WHERE status = 'completed' AND created_at >= CURRENT_DATE - INTERVAL '30 days') as monthly_revenue;

-- Create scheduled task for cleanup (requires pg_cron extension)
-- SELECT cron.schedule('cleanup-expired-sessions', '0 */6 * * *', 'SELECT cleanup_expired_sessions();');

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO authenticated, anon;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO authenticated;

-- Revoke sensitive permissions from anon
REVOKE ALL ON users FROM anon;
REVOKE ALL ON user_sessions FROM anon;
REVOKE ALL ON admin_actions FROM anon;
REVOKE ALL ON security_events FROM anon;

COMMIT;
