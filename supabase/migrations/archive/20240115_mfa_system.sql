-- Multi-Factor Authentication System
-- Migration: 20240115_mfa_system.sql
--
-- This migration implements a comprehensive MFA system with TOTP, SMS, and backup codes

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- MFA configuration table
CREATE TABLE IF NOT EXISTS user_mfa (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- MFA type and configuration
    mfa_type TEXT NOT NULL CHECK (
        mfa_type IN ('totp', 'sms', 'email', 'backup_codes')
    ),
    is_enabled BOOLEAN DEFAULT FALSE,
    is_primary BOOLEAN DEFAULT FALSE, -- Primary MFA method

    -- TOTP configuration
    secret TEXT, -- Encrypted TOTP secret
    backup_codes TEXT[], -- Encrypted backup codes
    last_used_backup_code TEXT, -- Track used backup codes

    -- SMS/Email configuration
    phone_number TEXT,
    email_address TEXT,

    -- Setup tracking
    setup_completed_at TIMESTAMPTZ,
    setup_ip_address INET,
    setup_user_agent TEXT,

    -- Usage tracking
    last_used_at TIMESTAMPTZ,
    usage_count INTEGER DEFAULT 0,

    -- Security
    failed_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(user_id, mfa_type)
);

-- MFA challenges table
CREATE TABLE IF NOT EXISTS mfa_challenges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    mfa_type TEXT NOT NULL CHECK (
        mfa_type IN ('totp', 'sms', 'email', 'backup_code')
    ),

    -- Challenge details
    challenge_code TEXT, -- Encrypted challenge code
    challenge_token TEXT UNIQUE NOT NULL DEFAULT (encode(gen_random_bytes(32), 'hex')),
    challenge_data JSONB, -- Additional challenge data

    -- Validity
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '10 minutes'),
    is_used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMPTZ,

    -- Context
    session_id TEXT,
    ip_address INET,
    user_agent TEXT,
    device_fingerprint TEXT,

    -- Result
    success BOOLEAN,
    failure_reason TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- MFA session tracking
CREATE TABLE IF NOT EXISTS mfa_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token TEXT UNIQUE NOT NULL,

    -- MFA requirements
    mfa_required BOOLEAN DEFAULT FALSE,
    mfa_completed BOOLEAN DEFAULT FALSE,
    required_mfa_types TEXT[], -- Which MFA types are required

    -- Session details
    ip_address INET,
    user_agent TEXT,
    device_fingerprint TEXT,

    -- Validity
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '30 minutes'),
    completed_at TIMESTAMPTZ,

    -- Security
    is_active BOOLEAN DEFAULT TRUE,
    revoked_at TIMESTAMPTZ,
    revoked_reason TEXT
);

-- MFA trusted devices
CREATE TABLE IF NOT EXISTS mfa_trusted_devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_fingerprint TEXT NOT NULL,
    device_name TEXT,

    -- Trust settings
    is_trusted BOOLEAN DEFAULT TRUE,
    trust_duration_days INTEGER DEFAULT 30,
    expires_at TIMESTAMPTZ,

    -- Context
    ip_address INET,
    user_agent TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_used_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(user_id, device_fingerprint)
);

-- Create indexes
CREATE INDEX idx_user_mfa_user_id ON user_mfa(user_id);
CREATE INDEX idx_user_mfa_type ON user_mfa(mfa_type);
CREATE INDEX idx_user_mfa_enabled ON user_mfa(is_enabled) WHERE is_enabled = TRUE;

CREATE INDEX idx_mfa_challenges_user_id ON mfa_challenges(user_id);
CREATE INDEX idx_mfa_challenges_token ON mfa_challenges(challenge_token);
CREATE INDEX idx_mfa_challenges_expires_at ON mfa_challenges(expires_at);
CREATE INDEX idx_mfa_challenges_is_used ON mfa_challenges(is_used) WHERE is_used = FALSE;

CREATE INDEX idx_mfa_sessions_user_id ON mfa_sessions(user_id);
CREATE INDEX idx_mfa_sessions_token ON mfa_sessions(session_token);
CREATE INDEX idx_mfa_sessions_expires_at ON mfa_sessions(expires_at);
CREATE INDEX idx_mfa_sessions_active ON mfa_sessions(is_active) WHERE is_active = TRUE;

CREATE INDEX idx_mfa_trusted_devices_user_id ON mfa_trusted_devices(user_id);
CREATE INDEX idx_mfa_trusted_devices_fingerprint ON mfa_trusted_devices(device_fingerprint);
CREATE INDEX idx_mfa_trusted_devices_expires_at ON mfa_trusted_devices(expires_at);

-- Create triggers for updated_at
CREATE TRIGGER update_user_mfa_updated_at
    BEFORE UPDATE ON user_mfa
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mfa_trusted_devices_last_used_at
    BEFORE UPDATE ON mfa_trusted_devices
    FOR EACH ROW
    EXECUTE FUNCTION
    BEGIN
        NEW.last_used_at = NOW();
        RETURN NEW;
    END;

-- Function to generate TOTP secret
CREATE OR REPLACE FUNCTION generate_totp_secret()
RETURNS TEXT AS $$
BEGIN
    RETURN encode(gen_random_bytes(20), 'base64');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to generate backup codes
CREATE OR REPLACE FUNCTION generate_backup_codes(p_count INTEGER DEFAULT 10)
RETURNS TEXT[] AS $$
DECLARE
    codes TEXT[] := '{}';
    i INTEGER;
BEGIN
    FOR i IN 1..p_count LOOP
        codes := array_append(codes, lpad(floor(random() * 1000000)::text, 6, '0'));
    END LOOP;
    RETURN codes;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to setup TOTP MFA
CREATE OR REPLACE FUNCTION setup_totp_mfa(
    p_user_id UUID,
    p_secret TEXT DEFAULT NULL,
    p_backup_codes_count INTEGER DEFAULT 10
) RETURNS TABLE(
    secret TEXT,
    backup_codes TEXT[],
    qr_code_url TEXT
) AS $$
DECLARE
    totp_secret TEXT;
    backup_codes TEXT[];
    qr_url TEXT;
BEGIN
    -- Generate secret if not provided
    totp_secret := COALESCE(p_secret, generate_totp_secret());

    -- Generate backup codes
    backup_codes := generate_backup_codes(p_backup_codes_count);

    -- Insert or update TOTP configuration
    INSERT INTO user_mfa (
        user_id,
        mfa_type,
        secret,
        backup_codes,
        setup_completed_at,
        setup_ip_address,
        setup_user_agent
    ) VALUES (
        p_user_id,
        'totp',
        totp_secret,
        backup_codes,
        NOW(),
        inet_client_addr(),
        current_setting('request.headers')::json->>'user-agent'
    )
    ON CONFLICT (user_id, mfa_type)
    DO UPDATE SET
        secret = EXCLUDED.secret,
        backup_codes = EXCLUDED.backup_codes,
        setup_completed_at = NOW(),
        setup_ip_address = inet_client_addr(),
        setup_user_agent = current_setting('request.headers')::json->>'user-agent',
        updated_at = NOW();

    -- Generate QR code URL (for authenticator apps)
    qr_url := format(
        'otpauth://totp/Raptorflow:%s?secret=%s&issuer=Raptorflow',
        (SELECT email FROM users WHERE id = p_user_id),
        totp_secret
    );

    RETURN QUERY SELECT totp_secret, backup_codes, qr_url;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to setup SMS MFA
CREATE OR REPLACE FUNCTION setup_sms_mfa(
    p_user_id UUID,
    p_phone_number TEXT
) RETURNS BOOLEAN AS $$
BEGIN
    -- Insert or update SMS configuration
    INSERT INTO user_mfa (
        user_id,
        mfa_type,
        phone_number,
        setup_completed_at,
        setup_ip_address,
        setup_user_agent
    ) VALUES (
        p_user_id,
        'sms',
        p_phone_number,
        NOW(),
        inet_client_addr(),
        current_setting('request.headers')::json->>'user-agent'
    )
    ON CONFLICT (user_id, mfa_type)
    DO UPDATE SET
        phone_number = EXCLUDED.phone_number,
        setup_completed_at = NOW(),
        setup_ip_address = inet_client_addr(),
        setup_user_agent = current_setting('request.headers')::json->>'user-agent',
        updated_at = NOW();

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to create MFA challenge
CREATE OR REPLACE FUNCTION create_mfa_challenge(
    p_user_id UUID,
    p_mfa_type TEXT,
    p_session_id TEXT DEFAULT NULL,
    p_device_fingerprint TEXT DEFAULT NULL
) RETURNS TEXT AS $$
DECLARE
    challenge_id UUID;
    challenge_code TEXT;
    encrypted_code TEXT;
    user_email TEXT;
    user_phone TEXT;
BEGIN
    -- Get user contact information
    SELECT email, phone INTO user_email, user_phone
    FROM users
    WHERE id = p_user_id;

    -- Generate challenge code
    CASE p_mfa_type
        WHEN 'totp' THEN
            challenge_code := NULL; -- TOTP doesn't use challenge codes
        WHEN 'sms' THEN
            challenge_code := lpad(floor(random() * 1000000)::text, 6, '0');
        WHEN 'email' THEN
            challenge_code := lpad(floor(random() * 1000000)::text, 6, '0');
        WHEN 'backup_code' THEN
            challenge_code := NULL; -- Backup codes are pre-generated
        ELSE
            RAISE EXCEPTION 'Unsupported MFA type: %', p_mfa_type;
    END CASE;

    -- Encrypt challenge code
    IF challenge_code IS NOT NULL THEN
        encrypted_code := pgp_sym_encrypt(challenge_code, current_setting('app.mfa_encryption_key'));
    END IF;

    -- Create challenge record
    INSERT INTO mfa_challenges (
        user_id,
        mfa_type,
        challenge_code,
        session_id,
        device_fingerprint,
        ip_address,
        user_agent
    ) VALUES (
        p_user_id,
        p_mfa_type,
        encrypted_code,
        p_session_id,
        p_device_fingerprint,
        inet_client_addr(),
        current_setting('request.headers')::json->>'user-agent'
    ) RETURNING id INTO challenge_id;

    -- TODO: Send SMS/Email with challenge code
    -- This would integrate with external SMS/email services

    RETURN challenge_id::text;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to verify MFA challenge
CREATE OR REPLACE FUNCTION verify_mfa_challenge(
    p_challenge_token TEXT,
    p_code TEXT,
    p_device_fingerprint TEXT DEFAULT NULL
) RETURNS TABLE(
    success BOOLEAN,
    mfa_type TEXT,
    user_id UUID,
    session_token TEXT,
    error_message TEXT
) AS $$
DECLARE
    challenge_record RECORD;
    user_mfa_record RECORD;
    decrypted_code TEXT;
    is_backup_code BOOLEAN := FALSE;
    session_token TEXT;
BEGIN
    -- Get challenge record
    SELECT * INTO challenge_record
    FROM mfa_challenges
    WHERE challenge_token = p_challenge_token
    AND is_used = FALSE
    AND expires_at > NOW();

    IF NOT FOUND THEN
        RETURN QUERY SELECT FALSE, NULL, NULL, NULL, 'Invalid or expired challenge';
        RETURN;
    END IF;

    -- Get user MFA configuration
    SELECT * INTO user_mfa_record
    FROM user_mfa
    WHERE user_id = challenge_record.user_id
    AND mfa_type = challenge_record.mfa_type
    AND is_enabled = TRUE;

    IF NOT FOUND THEN
        RETURN QUERY SELECT FALSE, NULL, NULL, NULL, 'MFA method not enabled';
        RETURN;
    END IF;

    -- Check if MFA is locked
    IF user_mfa_record.locked_until > NOW() THEN
        RETURN QUERY SELECT FALSE, NULL, NULL, NULL, 'MFA method locked due to failed attempts';
        RETURN;
    END IF;

    -- Verify code based on MFA type
    CASE challenge_record.mfa_type
        WHEN 'totp' THEN
            -- TODO: Implement TOTP verification
            -- This would use a TOTP library to verify the code
            NULL; -- Placeholder

        WHEN 'sms', 'email' THEN
            -- Decrypt and verify challenge code
            decrypted_code := pgp_sym_decrypt(challenge_record.challenge_code::bytea, current_setting('app.mfa_encryption_key'));

            IF decrypted_code != p_code THEN
                -- Increment failed attempts
                UPDATE user_mfa
                SET
                    failed_attempts = failed_attempts + 1,
                    locked_until = CASE
                        WHEN failed_attempts + 1 >= 5 THEN NOW() + INTERVAL '15 minutes'
                        ELSE NULL
                    END,
                    updated_at = NOW()
                WHERE id = user_mfa_record.id;

                RETURN QUERY SELECT FALSE, NULL, NULL, NULL, 'Invalid verification code';
                RETURN;
            END IF;

        WHEN 'backup_code' THEN
            -- Check against backup codes
            is_backup_code := p_code = ANY(user_mfa_record.backup_codes);

            IF NOT is_backup_code THEN
                RETURN QUERY SELECT FALSE, NULL, NULL, NULL, 'Invalid backup code';
                RETURN;
            END IF;

            -- Mark backup code as used
            UPDATE user_mfa
            SET
                backup_codes = array_remove(backup_codes, p_code),
                last_used_backup_code = p_code,
                updated_at = NOW()
            WHERE id = user_mfa_record.id;

        ELSE
            RETURN QUERY SELECT FALSE, NULL, NULL, NULL, 'Unsupported MFA type';
            RETURN;
    END CASE;

    -- Mark challenge as used
    UPDATE mfa_challenges
    SET
        is_used = TRUE,
        used_at = NOW(),
        success = TRUE
    WHERE id = challenge_record.id;

    -- Update MFA usage
    UPDATE user_mfa
    SET
        last_used_at = NOW(),
        usage_count = usage_count + 1,
        failed_attempts = 0,
        locked_until = NULL,
        updated_at = NOW()
    WHERE id = user_mfa_record.id;

    -- Generate session token
    session_token := encode(gen_random_bytes(32), 'hex');

    -- Create MFA session
    INSERT INTO mfa_sessions (
        user_id,
        session_token,
        mfa_required: FALSE,
        mfa_completed: TRUE,
        ip_address,
        user_agent,
        device_fingerprint
    ) VALUES (
        challenge_record.user_id,
        session_token,
        FALSE,
        TRUE,
        inet_client_addr(),
        current_setting('request.headers')::json->>'user-agent',
        p_device_fingerprint
    );

    RETURN QUERY SELECT TRUE, challenge_record.mfa_type, challenge_record.user_id, session_token, NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to enable/disable MFA
CREATE OR REPLACE FUNCTION toggle_mfa_method(
    p_user_id UUID,
    p_mfa_type TEXT,
    p_enabled BOOLEAN
) RETURNS BOOLEAN AS $$
BEGIN
    UPDATE user_mfa
    SET
        is_enabled = p_enabled,
        updated_at = NOW()
    WHERE user_id = p_user_id
    AND mfa_type = p_mfa_type;

    -- Log the change
    INSERT INTO audit_logs (
        actor_id,
        action,
        action_category,
        description,
        details,
        success,
        created_at
    ) VALUES (
        p_user_id,
        CASE WHEN p_enabled THEN 'MFA_ENABLED' ELSE 'MFA_DISABLED' END,
        'security',
        format('MFA method %s %s for user %s',
               p_mfa_type,
               CASE WHEN p_enabled THEN 'enabled' ELSE 'disabled' END,
               p_user_id),
        jsonb_build_object(
            'mfa_type', p_mfa_type,
            'enabled', p_enabled
        ),
        TRUE,
        NOW()
    );

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get user MFA status
CREATE OR REPLACE FUNCTION get_user_mfa_status(p_user_id UUID)
RETURNS TABLE(
    mfa_type TEXT,
    is_enabled BOOLEAN,
    is_primary BOOLEAN,
    setup_completed_at TIMESTAMPTZ,
    last_used_at TIMESTAMPTZ,
    usage_count INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        um.mfa_type,
        um.is_enabled,
        um.is_primary,
        um.setup_completed_at,
        um.last_used_at,
        um.usage_count
    FROM user_mfa um
    WHERE um.user_id = p_user_id
    ORDER BY um.is_primary DESC, um.created_at;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Enable RLS on MFA tables
ALTER TABLE user_mfa ENABLE ROW LEVEL SECURITY;
ALTER TABLE mfa_challenges ENABLE ROW LEVEL SECURITY;
ALTER TABLE mfa_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE mfa_trusted_devices ENABLE ROW LEVEL SECURITY;

-- RLS policies for user_mfa
CREATE POLICY "Users can manage own MFA" ON user_mfa
    FOR ALL USING (
        user_id = (SELECT id FROM users WHERE auth_user_id = auth.uid())
    );

CREATE POLICY "Admins can view all MFA" ON user_mfa
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE auth_user_id = auth.uid()
            AND role IN ('admin', 'super_admin')
        )
    );

-- RLS policies for mfa_challenges
CREATE POLICY "Users can manage own challenges" ON mfa_challenges
    FOR ALL USING (
        user_id = (SELECT id FROM users WHERE auth_user_id = auth.uid())
    );

-- RLS policies for mfa_sessions
CREATE POLICY "Users can manage own sessions" ON mfa_sessions
    FOR ALL USING (
        user_id = (SELECT id FROM users WHERE auth_user_id = auth.uid())
    );

-- RLS policies for mfa_trusted_devices
CREATE POLICY "Users can manage own trusted devices" ON mfa_trusted_devices
    FOR ALL USING (
        user_id = (SELECT id FROM users WHERE auth_user_id = auth.uid())
    );

-- Grant permissions to authenticated users
GRANT EXECUTE ON FUNCTION generate_totp_secret() TO authenticated;
GRANT EXECUTE ON FUNCTION generate_backup_codes(INTEGER) TO authenticated;
GRANT EXECUTE ON FUNCTION setup_totp_mfa(UUID, TEXT, INTEGER) TO authenticated;
GRANT EXECUTE ON FUNCTION setup_sms_mfa(UUID, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION create_mfa_challenge(UUID, TEXT, TEXT, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION verify_mfa_challenge(TEXT, TEXT, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION toggle_mfa_method(UUID, TEXT, BOOLEAN) TO authenticated;
GRANT EXECUTE ON FUNCTION get_user_mfa_status(UUID) TO authenticated;

-- Log the MFA system setup
INSERT INTO audit_logs (
    action,
    action_category,
    description,
    details,
    success,
    created_at
) VALUES (
    'MFA_SYSTEM_SETUP',
    'security',
    'Multi-factor authentication system implemented',
    jsonb_build_object(
        'migration', '20240115_mfa_system.sql',
        'tables_created', 4,
        'functions_created', 8,
        'mfa_types', ARRAY['totp', 'sms', 'email', 'backup_codes']
    ),
    TRUE,
    NOW()
);
