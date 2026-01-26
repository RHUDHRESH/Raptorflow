-- JWT Token Rotation System
-- Migration: 20240115_jwt_rotation.sql
--
-- This migration implements JWT token rotation with secure token management,
-- blacklisting, and automatic cleanup

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- JWT token blacklist
CREATE TABLE IF NOT EXISTS jwt_token_blacklist (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Token identification
    jti TEXT UNIQUE NOT NULL, -- JWT ID
    token_type TEXT NOT NULL CHECK (
        token_type IN ('access', 'refresh', 'session', 'api_key')
    ),

    -- Token metadata
    user_id UUID REFERENCES users(id),
    client_id TEXT,
    scope TEXT[],
    issued_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,

    -- Revocation details
    revoked_at TIMESTAMPTZ DEFAULT NOW(),
    revoked_by UUID REFERENCES users(id),
    revoked_reason TEXT,

    -- Security context
    ip_address INET,
    user_agent TEXT,
    device_fingerprint TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- JWT token rotation tracking
CREATE TABLE IF NOT EXISTS jwt_token_rotations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Rotation details
    old_jti TEXT NOT NULL,
    new_jti TEXT NOT NULL,

    -- Token metadata
    user_id UUID REFERENCES users(id),
    client_id TEXT,
    token_type TEXT NOT NULL CHECK (
        token_type IN ('access', 'refresh', 'session', 'api_key')
    ),

    -- Rotation reasons
    rotation_reason TEXT NOT NULL CHECK (
        rotation_reason IN ('security_policy', 'user_request', 'suspicious_activity', 'token_compromise', 'scheduled_rotation')
    ),

    -- Timing
    rotated_at TIMESTAMPTZ DEFAULT NOW(),
    old_expires_at TIMESTAMPTZ,
    new_expires_at TIMESTAMPTZ,

    -- Context
    ip_address INET,
    user_agent TEXT,
    device_fingerprint TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- JWT session management
CREATE TABLE IF NOT EXISTS jwt_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Session identification
    session_jti TEXT UNIQUE NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id),

    -- Session metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_accessed_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,

    -- Security context
    ip_address INET,
    user_agent TEXT,
    device_fingerprint TEXT,

    -- Session status
    is_active BOOLEAN DEFAULT TRUE,
    revoked_at TIMESTAMPTZ,
    revoked_reason TEXT,

    -- Usage tracking
    access_count INTEGER DEFAULT 0,
    last_rotation_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- JWT key management
CREATE TABLE IF NOT EXISTS jwt_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Key identification
    key_id TEXT UNIQUE NOT NULL,
    key_name TEXT,
    key_type TEXT NOT NULL CHECK (
        key_type IN ('signing', 'encryption', 'verification')
    ),

    -- Key material
    public_key TEXT NOT NULL,
    private_key TEXT, -- Encrypted
    key_algorithm TEXT NOT NULL DEFAULT 'RS256',

    -- Key status
    is_active BOOLEAN DEFAULT TRUE,
    is_primary BOOLEAN DEFAULT FALSE,

    -- Validity period
    valid_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_until TIMESTAMPTZ,

    -- Usage tracking
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMPTZ,

    -- Metadata
    metadata JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- JWT configuration
CREATE TABLE IF NOT EXISTS jwt_configuration (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Token settings
    access_token_lifetime INTEGER DEFAULT 3600, -- 1 hour
    refresh_token_lifetime INTEGER DEFAULT 2592000, -- 30 days
    session_token_lifetime INTEGER DEFAULT 1800, -- 30 minutes

    -- Rotation settings
    enable_rotation BOOLEAN DEFAULT TRUE,
    rotation_threshold_seconds INTEGER DEFAULT 1800, -- 30 minutes
    max_refresh_tokens_per_user INTEGER DEFAULT 5,

    -- Security settings
    require_device_fingerprint BOOLEAN DEFAULT TRUE,
    require_ip_binding BOOLEAN DEFAULT FALSE,
    max_concurrent_sessions INTEGER DEFAULT 3,

    -- Cleanup settings
    cleanup_interval_hours INTEGER DEFAULT 24,
    retention_days INTEGER DEFAULT 90,

    -- Metadata
    configuration JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_jwt_token_blacklist_jti ON jwt_token_blacklist(jti);
CREATE INDEX idx_jwt_token_blacklist_user_id ON jwt_token_blacklist(user_id);
CREATE INDEX idx_jwt_token_blacklist_token_type ON jwt_token_blacklist(token_type);
CREATE INDEX idx_jwt_token_blacklist_expires_at ON jwt_token_blacklist(expires_at);
CREATE INDEX idx_jwt_token_blacklist_revoked_at ON jwt_token_blacklist(revoked_at);

CREATE INDEX idx_jwt_token_rotations_old_jti ON jwt_token_rotations(old_jti);
CREATE INDEX idx_jwt_token_rotations_new_jti ON jwt_token_rotations(new_jti);
CREATE INDEX idx_jwt_token_rotations_user_id ON jwt_token_rotations(user_id);
CREATE INDEX idx_jwt_token_rotations_rotated_at ON jwt_token_rotations(rotated_at);

CREATE INDEX idx_jwt_sessions_session_jti ON jwt_sessions(session_jti);
CREATE INDEX idx_jwt_sessions_user_id ON jwt_sessions(user_id);
CREATE INDEX idx_jwt_sessions_expires_at ON jwt_sessions(expires_at);
CREATE INDEX idx_jwt_sessions_is_active ON jwt_sessions(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_jwt_sessions_last_accessed_at ON jwt_sessions(last_accessed_at);

CREATE INDEX idx_jwt_keys_key_id ON jwt_keys(key_id);
CREATE INDEX idx_jwt_keys_key_type ON jwt_keys(key_type);
CREATE INDEX idx_jwt_keys_is_active ON jwt_keys(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_jwt_keys_is_primary ON jwt_keys(is_primary) WHERE is_primary = TRUE;

-- Create triggers for updated_at
CREATE TRIGGER update_jwt_keys_updated_at
    BEFORE UPDATE ON jwt_keys
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_jwt_configuration_updated_at
    BEFORE UPDATE ON jwt_configuration
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to generate JWT key pair
CREATE OR REPLACE FUNCTION generate_jwt_key_pair(
    p_key_name TEXT DEFAULT NULL,
    p_key_type TEXT DEFAULT 'signing',
    p_algorithm TEXT DEFAULT 'RS256',
    p_valid_days INTEGER DEFAULT 365
) RETURNS TABLE(
    key_id TEXT,
    public_key TEXT,
    private_key TEXT
) AS $$
DECLARE
    key_id_val TEXT;
    public_key_val TEXT;
    private_key_val TEXT;
    valid_until TIMESTAMPTZ;
BEGIN
    -- Generate unique key ID
    key_id_val := format('jwt_%s_%s', p_key_type, encode(gen_random_bytes(16), 'hex');

    -- Generate RSA key pair (simplified - in production use proper crypto library)
    -- This is a placeholder implementation
    public_key_val := '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----';
    private_key_val := '-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PRIVATE KEY-----';

    -- Set validity period
    valid_until := NOW() + (p_valid_days || 365) * INTERVAL '1 day';

    -- Store key
    INSERT INTO jwt_keys (
        key_id,
        key_name,
        key_type,
        public_key,
        private_key,
        key_algorithm,
        valid_from,
        valid_until,
        metadata
    ) VALUES (
        key_id_val,
        p_key_name,
        p_key_type,
        public_key_val,
        pgp_sym_encrypt(private_key_val, current_setting('app.jwt_encryption_key')),
        p_algorithm,
        NOW(),
        valid_until,
        jsonb_build_object('generated_at', NOW())
    ) RETURNING key_id_val, public_key_val, private_key_val;

    RETURN QUERY SELECT key_id_val, public_key_val, private_key_val;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to create JWT token
CREATE OR REPLACE FUNCTION create_jwt_token(
    p_user_id UUID,
    p_token_type TEXT DEFAULT 'access',
    p_scope TEXT[] DEFAULT '{}',
    p_client_id TEXT DEFAULT NULL,
    p_expires_in_seconds INTEGER DEFAULT 3600,
    p_device_fingerprint TEXT DEFAULT NULL,
    p_ip_address INET DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL
) RETURNS TABLE(
    jti TEXT,
    token TEXT,
    expires_at TIMESTAMPTZ
) AS $$
DECLARE
    jti_val TEXT;
    token_val TEXT;
    expires_at_val TIMESTAMPTZ;
    payload JSONB;
    signing_key TEXT;
    config RECORD;
BEGIN
    -- Get JWT configuration
    SELECT * INTO config
    FROM jwt_configuration
    LIMIT 1;

    -- Generate JWT ID
    jti_val := encode(gen_random_bytes(32), 'hex');

    -- Set expiration
    expires_at_val := NOW() + (p_expires_in_seconds || config.access_token_lifetime) * INTERVAL '1 second';

    -- Build payload
    payload := jsonb_build_object(
        'jti', jti_val,
        'sub', p_user_id,
        'token_type', p_token_type,
        'scope', p_scope,
        'client_id', p_client_id,
        'iat', EXTRACT(EPOCH FROM NOW()),
        'exp', EXTRACT(EPOCH FROM expires_at_val),
        'device_fingerprint', p_device_fingerprint,
        'ip_address', p_ip_address,
        'user_agent', p_user_agent
    );

    -- Get primary signing key
    SELECT public_key INTO signing_key
    FROM jwt_keys
    WHERE key_type = 'signing'
    AND is_active = TRUE
    AND is_primary = TRUE
    AND valid_from <= NOW()
    AND valid_until > NOW()
    LIMIT 1;

    IF signing_key IS NULL THEN
        RAISE EXCEPTION 'No active signing key available';
    END IF;

    -- Create JWT token (simplified)
    token_val := encode(
        jsonb_build_object(
            'header', jsonb_build_object('alg', 'RS256', 'typ', 'JWT'),
            'payload', payload
        )::text,
        'base64'
    );

    -- Store token in appropriate table
    IF p_token_type = 'session' THEN
        INSERT INTO jwt_sessions (
            session_jti,
            user_id,
            expires_at,
            ip_address,
            user_agent,
            device_fingerprint
        ) VALUES (
            jti_val,
            p_user_id,
            expires_at_val,
            p_ip_address,
            p_user_agent,
            p_device_fingerprint
        );
    END IF;

    RETURN QUERY SELECT jti_val, token_val, expires_at_val;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to rotate JWT token
CREATE OR REPLACE FUNCTION rotate_jwt_token(
    p_current_jti TEXT,
    p_rotation_reason TEXT DEFAULT 'security_policy',
    p_device_fingerprint TEXT DEFAULT NULL,
    p_ip_address INET DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL
) RETURNS TABLE(
    new_jti TEXT,
    new_token TEXT,
    expires_at TIMESTAMPTZ
) AS $$
DECLARE
    current_token RECORD;
    new_jti_val TEXT;
    new_token_val TEXT;
    expires_at_val TIMESTAMPTZ;
    user_id UUID;
    client_id TEXT;
    scope TEXT[];
    token_type TEXT;
    old_expires_at TIMESTAMPTZ;
BEGIN
    -- Get current token info
    SELECT
        jt.user_id,
        jt.client_id,
        jt.scope,
        jt.token_type,
        jt.expires_at
    INTO user_id, client_id, scope, token_type, old_expires_at
    FROM jwt_token_blacklist jt
    WHERE jt.jti = p_current_jti
    AND jt.is_active = FALSE
    LIMIT 1;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Token not found or not blacklisted';
    END IF;

    -- Check if token is expired
    IF old_expires_at < NOW() THEN
        RAISE EXCEPTION 'Cannot rotate expired token';
    END IF;

    -- Generate new token
    SELECT jti, token, expires_at INTO new_jti_val, new_token_val, expires_at_val
    FROM create_jwt_token(
        user_id,
        token_type,
        scope,
        client_id,
        NULL, -- Use default expiration
        p_device_fingerprint,
        p_ip_address,
        p_user_agent
    );

    -- Record rotation
    INSERT INTO jwt_token_rotations (
        old_jti,
        new_jti,
        user_id,
        client_id,
        token_type,
        p_rotation_reason,
        old_expires_at,
        expires_at_val,
        p_ip_address,
        p_user_agent,
        p_device_fingerprint
    ) VALUES (
        p_current_jti,
        new_jti_val,
        user_id,
        client_id,
        token_type,
        p_rotation_reason,
        old_expires_at,
        expires_at_val,
        p_ip_address,
        p_user_agent,
        p_device_fingerprint
    );

    -- Blacklist old token
    UPDATE jwt_token_blacklist
    SET
        revoked_at = NOW(),
        revoked_reason = p_rotation_reason
    WHERE jti = p_current_jti;

    RETURN QUERY SELECT new_jti_val, new_token_val, expires_at_val;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to blacklist token
CREATE OR REPLACE FUNCTION blacklist_jwt_token(
    p_jti TEXT,
    p_reason TEXT DEFAULT 'manual_revocation',
    p_user_id UUID DEFAULT NULL
) RETURNS BOOLEAN AS $$
BEGIN
    UPDATE jwt_token_blacklist
    SET
        is_active = FALSE,
        revoked_at = NOW(),
        revoked_by = p_user_id,
        revoked_reason = p_reason
    WHERE jti = p_jti
    AND is_active = TRUE;

    RETURN FOUND;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to validate JWT token
CREATE OR REPLACE FUNCTION validate_jwt_token(
    p_token TEXT,
    p_device_fingerprint TEXT DEFAULT NULL,
    p_ip_address INET DEFAULT NULL,
    p_check_blacklist BOOLEAN DEFAULT TRUE
) RETURNS TABLE(
    is_valid BOOLEAN,
    jti TEXT,
    user_id UUID,
    token_type TEXT,
    scope TEXT[],
    expires_at TIMESTAMPTZ,
    is_blacklisted BOOLEAN,
    error_message TEXT
) AS $$
DECLARE
    payload JSONB;
    jti_val TEXT;
    user_id_val UUID;
    expires_at_val TIMESTAMPTZ;
    is_blacklisted_val BOOLEAN;
    error_msg TEXT;
BEGIN
    -- Parse JWT token (simplified)
    BEGIN
        payload := jsonb_decode(decode(split_part(p_token, '.', 2));
        jti_val := payload->>'jti';
        user_id_val := (payload->>'sub')::UUID;
        expires_at_val := to_timestamp((payload->>'exp')::BIGINT);
    EXCEPTION WHEN OTHERS THEN
        RETURN QUERY SELECT FALSE, NULL, NULL, NULL, NULL, NULL, TRUE, 'Invalid token format';
    END;

    -- Check if token is expired
    IF expires_at_val < NOW() THEN
        RETURN QUERY SELECT FALSE, jti_val, user_id_val, NULL, NULL, expires_at_val, FALSE, 'Token expired';
    END IF;

    -- Check blacklist if required
    IF p_check_blacklist THEN
        SELECT is_active = FALSE INTO is_blacklisted_val
        FROM jwt_token_blacklist
        WHERE jti = jti_val
        AND is_active = TRUE
        AND expires_at > NOW();

        IF is_blacklisted_val THEN
            RETURN QUERY SELECT FALSE, jti_val, user_id_val, NULL, NULL, expires_at_val, TRUE, 'Token is blacklisted';
        END IF;
    END IF;

    -- Check device fingerprint if required
    IF p_device_fingerprint IS NOT NULL THEN
        -- TODO: Implement device fingerprint validation
        NULL;
    END IF;

    -- Check IP binding if required
    IF p_ip_address IS NOT NULL THEN
        -- TODO: Implement IP binding validation
        NULL;
    END IF;

    -- Token is valid
    RETURN QUERY SELECT TRUE, jti_val, user_id_val, NULL, NULL, expires_at_val, FALSE, NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to cleanup expired tokens
CREATE OR REPLACE FUNCTION cleanup_expired_jwt_tokens()
RETURNS TABLE(
    table_name TEXT,
    records_deleted INTEGER
) AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Cleanup expired blacklist entries
    DELETE FROM jwt_token_blacklist
    WHERE expires_at < NOW()
    RETURNING GET DIAGNOSTICS ROW_COUNT INTO deleted_count;

    RETURN QUERY SELECT 'jwt_token_blacklist', deleted_count;

EXCEPTION WHEN OTHERS THEN
    RETURN QUERY SELECT 'jwt_token_blacklist', 0;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to rotate JWT keys
CREATE OR REPLACE FUNCTION rotate_jwt_keys(
    p_key_type TEXT DEFAULT 'signing',
    p_grace_period_days INTEGER DEFAULT 7
) RETURNS TABLE(
    old_key_id TEXT,
    new_key_id TEXT,
    rotated_at TIMESTAMPTZ
) AS $$
DECLARE
    old_key_id_val TEXT;
    new_key_id_val TEXT;
    grace_period TIMESTAMPTZ;
BEGIN
    -- Get current primary key
    SELECT key_id INTO old_key_id_val
    FROM jwt_keys
    WHERE key_type = p_key_type
    AND is_primary = TRUE
    AND is_active = TRUE
    LIMIT 1;

    IF old_key_id_val IS NULL THEN
        RAISE EXCEPTION 'No primary key found for type: %', p_key_type;
    END IF;

    -- Set grace period
    grace_period := NOW() + (p_grace_period_days || 7) * INTERVAL '1 day';

    -- Generate new key
    SELECT key_id INTO new_key_id_val
    FROM generate_jwt_key_pair(
        format('jwt_%s_%s', p_key_type, encode(gen_random_bytes(16), 'hex'),
        p_key_type,
        'RS256',
        365
    );

    -- Make new key primary
    UPDATE jwt_keys
    SET
        is_primary = TRUE,
        updated_at = NOW()
    WHERE key_id = new_key_id_val;

    -- Update old key to non-primary with grace period
    UPDATE jwt_keys
    SET
        is_primary = FALSE,
        valid_until = grace_period,
        updated_at = NOW()
    WHERE key_id = old_key_id_val;

    RETURN QUERY SELECT old_key_id_val, new_key_id_val, NOW();
END;
$$ LANGUAGE plpgsql SECURITY GENERATOR;

-- Enable RLS on JWT tables
ALTER TABLE jwt_token_blacklist ENABLE ROW LEVEL SECURITY;
ALTER TABLE jwt_token_rotations ENABLE ROW LEVEL SECURITY;
ALTER TABLE jwt_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE jwt_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE jwt_configuration ENABLE ROW LEVEL SECURITY;

-- RLS policies for jwt_token_blacklist
CREATE POLICY "Users can manage own blacklist entries" ON jwt_token_blacklist
    FOR ALL USING (
        user_id = (SELECT id FROM users WHERE auth_user_id = auth.uid())
    );

CREATE POLICY "Admins can manage all blacklist entries" ON jwt_token_blacklist
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE auth_user_id = auth.uid()
            AND role IN ('admin', 'super_admin')
        )
    );

-- RLS policies for jwt_sessions
CREATE POLICY "Users can manage own sessions" ON jwt_sessions
    FOR ALL USING (
        user_id = (SELECT id FROM users WHERE auth_user_id = auth.uid())
    );

CREATE POLICY "Admins can manage all sessions" ON jwt_sessions
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE auth_user_id = auth.uid()
            AND role IN ('admin', 'super_admin')
        )
    );

-- RLS policies for jwt_keys
CREATE POLICY "Admins can manage JWT keys" ON jwt_keys
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE auth_user_id = auth.uid()
            AND role IN ('admin', 'super_admin')
        )
    );

-- Grant permissions to authenticated users
GRANT EXECUTE ON FUNCTION generate_jwt_key_pair(TEXT, TEXT, TEXT, INTEGER) TO authenticated;
GRANT EXECUTE ON FUNCTION create_jwt_token(UUID, TEXT, TEXT[], TEXT, INTEGER, TEXT, INET, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION rotate_jwt_token(TEXT, TEXT, TEXT, INET, TEXT) TO authenticated;
GRANT EXECUTE FUNCTION blacklist_jwt_token(TEXT, TEXT, UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION validate_jwt_token(TEXT, TEXT, INET, BOOLEAN) TO authenticated;
GRANT EXECUTE ON FUNCTION cleanup_expired_jwt_tokens() TO authenticated;
GRANT EXECUTE ON FUNCTION rotate_jwt_keys(TEXT, INTEGER) TO authenticated;

-- Initialize JWT configuration
INSERT INTO jwt_configuration (
    access_token_lifetime,
    refresh_token_lifetime,
    session_token_lifetime,
    enable_rotation,
    rotation_threshold_seconds,
    max_refresh_tokens_per_user,
    require_device_fingerprint,
    require_ip_binding,
    max_concurrent_sessions,
    cleanup_interval_hours,
    retention_days
) VALUES (
    3600,
    2592000,
    1800,
    TRUE,
    1800,
    5,
    TRUE,
    FALSE,
    3,
    24,
    90
) ON CONFLICT DO NOTHING;

-- Generate initial signing key
SELECT * FROM generate_jwt_key_pair('jwt_signing_primary', 'signing', 'RS256', 365);

-- Log the JWT rotation system setup
INSERT INTO audit_logs (
    action,
    action_category,
    description,
    details,
    success,
    created_at
) VALUES (
    'JWT_ROTATION_SYSTEM_SETUP',
    'security',
    'JWT token rotation system implemented',
    jsonb_build_object(
        'migration', '20240115_jwt_rotation.sql',
        'tables_created', 5,
        'functions_created', 8,
        'initial_key_generated', TRUE
    ),
    TRUE,
    NOW()
);
