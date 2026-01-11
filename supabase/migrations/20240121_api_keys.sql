-- API Keys table for programmatic access
-- Migration: 20240121_api_keys.sql

CREATE TABLE IF NOT EXISTS public.api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    key_hash TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    permissions JSONB DEFAULT '{"read": true, "write": false, "delete": false}',
    last_used_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_api_keys_workspace_id ON public.api_keys(workspace_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_key_hash ON public.api_keys(key_hash);
CREATE INDEX IF NOT EXISTS idx_api_keys_expires_at ON public.api_keys(expires_at);
CREATE INDEX IF NOT EXISTS idx_api_keys_last_used_at ON public.api_keys(last_used_at);

-- GIN index for JSONB permissions
CREATE INDEX IF NOT EXISTS idx_api_keys_permissions_gin ON public.api_keys USING GIN (permissions);

-- Enable RLS
ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own API keys" ON public.api_keys
    FOR SELECT USING (
        workspace_id IN (
            SELECT id FROM public.workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create own API keys" ON public.api_keys
    FOR INSERT WITH CHECK (
        workspace_id IN (
            SELECT id FROM public.workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update own API keys" ON public.api_keys
    FOR UPDATE USING (
        workspace_id IN (
            SELECT id FROM public.workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete own API keys" ON public.api_keys
    FOR DELETE USING (
        workspace_id IN (
            SELECT id FROM public.workspaces
            WHERE user_id = auth.uid()
        )
    );

-- Function to hash API keys
CREATE OR REPLACE FUNCTION hash_api_key(api_key TEXT)
RETURNS TEXT AS $$
BEGIN
    -- Use SHA-256 for hashing (never store raw keys)
    RETURN encode(sha256(api_key::bytea), 'hex');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to validate API key
CREATE OR REPLACE FUNCTION validate_api_key(key_hash TEXT)
RETURNS TABLE(workspace_id UUID, permissions JSONB) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ak.workspace_id,
        ak.permissions
    FROM public.api_keys ak
    WHERE ak.key_hash = key_hash
    AND (ak.expires_at IS NULL OR ak.expires_at > NOW())
    FOR UPDATE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to update last used timestamp
CREATE OR REPLACE FUNCTION update_api_key_last_used()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_used_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_api_keys_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
CREATE TRIGGER api_keys_updated_at
    BEFORE UPDATE ON public.api_keys
    FOR EACH ROW
    EXECUTE FUNCTION update_api_keys_updated_at();

-- Function to generate API key
CREATE OR REPLACE FUNCTION generate_api_key()
RETURNS TEXT AS $$
DECLARE
    key_prefix TEXT := 'rk_';
    random_bytes TEXT;
    api_key TEXT;
BEGIN
    -- Generate 32 random bytes and encode as hex
    random_bytes := encode(gen_random_bytes(32), 'hex');
    api_key := key_prefix || random_bytes;
    RETURN api_key;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to create API key with hash
CREATE OR REPLACE FUNCTION create_api_key(
    p_workspace_id UUID,
    p_name TEXT,
    p_permissions JSONB DEFAULT '{"read": true, "write": false, "delete": false}',
    p_expires_at TIMESTAMPTZ DEFAULT NULL
)
RETURNS TABLE(api_key TEXT, key_id UUID) AS $$
DECLARE
    new_api_key TEXT;
    new_key_hash TEXT;
    new_key_id UUID;
BEGIN
    -- Generate API key and hash
    new_api_key := generate_api_key();
    new_key_hash := hash_api_key(new_api_key);

    -- Insert into database
    INSERT INTO public.api_keys (
        workspace_id,
        key_hash,
        name,
        permissions,
        expires_at
    ) VALUES (
        p_workspace_id,
        new_key_hash,
        p_name,
        p_permissions,
        p_expires_at
    ) RETURNING id INTO new_key_id;

    RETURN QUERY SELECT new_api_key, new_key_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to revoke API key
CREATE OR REPLACE FUNCTION revoke_api_key(key_id UUID, workspace_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM public.api_keys
    WHERE id = key_id
    AND workspace_id = workspace_id;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count > 0;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- View for active API keys
CREATE OR REPLACE VIEW active_api_keys AS
SELECT
    ak.id,
    ak.workspace_id,
    ak.name,
    ak.permissions,
    ak.last_used_at,
    ak.expires_at,
    ak.created_at,
    w.name as workspace_name,
    w.user_id
FROM public.api_keys ak
JOIN public.workspaces w ON ak.workspace_id = w.id
WHERE (ak.expires_at IS NULL OR ak.expires_at > NOW());

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.api_keys TO authenticated;
GRANT SELECT ON active_api_keys TO authenticated;
GRANT EXECUTE ON FUNCTION hash_api_key(TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION validate_api_key(TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION generate_api_key() TO authenticated;
GRANT EXECUTE ON FUNCTION create_api_key(UUID, TEXT, JSONB, TIMESTAMPTZ) TO authenticated;
GRANT EXECUTE ON FUNCTION revoke_api_key(UUID, UUID) TO authenticated;
