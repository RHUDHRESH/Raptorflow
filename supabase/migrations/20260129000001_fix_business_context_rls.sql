-- Fix Business Context Storage with RLS and Multi-Tenancy
-- Ensure proper data isolation and business context management

BEGIN;

-- Create business_context table if not exists
CREATE TABLE IF NOT EXISTS business_context (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    version VARCHAR(20) DEFAULT '1.0.0',
    business_data JSONB NOT NULL DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Create BCM (Business Context Manifest) table
CREATE TABLE IF NOT EXISTS bcm_manifests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    business_context_id UUID REFERENCES business_context(id) ON DELETE CASCADE,
    bcm_data JSONB NOT NULL DEFAULT '{}',
    version VARCHAR(20) DEFAULT '1.0.0',
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'archived')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_business_context_user_id ON business_context(user_id);
CREATE INDEX IF NOT EXISTS idx_business_context_workspace_id ON business_context(workspace_id);
CREATE INDEX IF NOT EXISTS idx_business_context_is_active ON business_context(is_active);

CREATE INDEX IF NOT EXISTS idx_bcm_manifests_user_id ON bcm_manifests(user_id);
CREATE INDEX IF NOT EXISTS idx_bcm_manifests_workspace_id ON bcm_manifests(workspace_id);
CREATE INDEX IF NOT EXISTS idx_bcm_manifests_business_context_id ON bcm_manifests(business_context_id);
CREATE INDEX IF NOT EXISTS idx_bcm_manifests_status ON bcm_manifests(status);
CREATE INDEX IF NOT EXISTS idx_bcm_manifests_is_active ON bcm_manifests(is_active);

-- Enable RLS
ALTER TABLE business_context ENABLE ROW LEVEL SECURITY;
ALTER TABLE bcm_manifests ENABLE ROW LEVEL SECURITY;

-- RLS Policies for Business Context
CREATE POLICY "Users can view own business context" ON business_context
FOR SELECT USING (user_id IN (SELECT id FROM users WHERE auth_user_id = auth.uid()));

CREATE POLICY "Users can insert own business context" ON business_context
FOR INSERT WITH CHECK (user_id IN (SELECT id FROM users WHERE auth_user_id = auth.uid()));

CREATE POLICY "Users can update own business context" ON business_context
FOR UPDATE USING (user_id IN (SELECT id FROM users WHERE auth_user_id = auth.uid()));

CREATE POLICY "Users can delete own business context" ON business_context
FOR DELETE USING (user_id IN (SELECT id FROM users WHERE auth_user_id = auth.uid()));

-- RLS Policies for BCM Manifests
CREATE POLICY "Users can view own BCM manifests" ON bcm_manifests
FOR SELECT USING (user_id IN (SELECT id FROM users WHERE auth_user_id = auth.uid()));

CREATE POLICY "Users can insert own BCM manifests" ON bcm_manifests
FOR INSERT WITH CHECK (user_id IN (SELECT id FROM users WHERE auth_user_id = auth.uid()));

CREATE POLICY "Users can update own BCM manifests" ON bcm_manifests
FOR UPDATE USING (user_id IN (SELECT id FROM users WHERE auth_user_id = auth.uid()));

CREATE POLICY "Users can delete own BCM manifests" ON bcm_manifests
FOR DELETE USING (user_id IN (SELECT id FROM users WHERE auth_user_id = auth.uid()));

-- Updated_at trigger for business_context
CREATE TRIGGER update_business_context_updated_at
BEFORE UPDATE ON business_context
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Updated_at trigger for bcm_manifests
CREATE TRIGGER update_bcm_manifests_updated_at
BEFORE UPDATE ON bcm_manifests
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to get active business context for user
CREATE OR REPLACE FUNCTION get_active_business_context(p_user_id UUID)
RETURNS TABLE (
    id UUID,
    workspace_id UUID,
    version VARCHAR(20),
    business_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        bc.id,
        bc.workspace_id,
        bc.version,
        bc.business_data,
        bc.created_at,
        bc.updated_at
    FROM business_context bc
    WHERE bc.user_id = p_user_id
    AND bc.is_active = TRUE
    ORDER BY bc.updated_at DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get active BCM for user
CREATE OR REPLACE FUNCTION get_active_bcm_manifest(p_user_id UUID)
RETURNS TABLE (
    id UUID,
    business_context_id UUID,
    bcm_data JSONB,
    version VARCHAR(20),
    status VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        bcm.id,
        bcm.business_context_id,
        bcm.bcm_data,
        bcm.version,
        bcm.status,
        bcm.created_at,
        bcm.updated_at
    FROM bcm_manifests bcm
    WHERE bcm.user_id = p_user_id
    AND bcm.is_active = TRUE
    AND bcm.status = 'active'
    ORDER BY bcm.updated_at DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant permissions to authenticated users
GRANT SELECT, INSERT, UPDATE, DELETE ON business_context TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON bcm_manifests TO authenticated;
GRANT EXECUTE ON FUNCTION get_active_business_context TO authenticated;
GRANT EXECUTE ON FUNCTION get_active_bcm_manifest TO authenticated;

COMMIT;
