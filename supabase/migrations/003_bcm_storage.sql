-- BCM Storage Migration
-- Creates tables for Business Context Manifest persistence with versioning

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create business_context_manifests table
CREATE TABLE IF NOT EXISTS business_context_manifests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL,
    user_id UUID,

    -- Version information
    version_major INTEGER NOT NULL DEFAULT 1,
    version_minor INTEGER NOT NULL DEFAULT 0,
    version_patch INTEGER NOT NULL DEFAULT 0,
    version_string TEXT NOT NULL DEFAULT '1.0.0',

    -- BCM data (JSON)
    company_info JSONB,
    icps JSONB,
    competitors JSONB,
    brand_data JSONB,
    market_data JSONB,
    messaging_data JSONB,
    channels_data JSONB,
    goals_data JSONB,
    issues_data JSONB,

    -- Metadata
    generated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completion_percentage DECIMAL(5,2) DEFAULT 0.00,
    token_count INTEGER DEFAULT 0,
    checksum VARCHAR(64) NOT NULL,

    -- Validation metadata
    validation_warnings JSONB DEFAULT '[]',
    missing_fields JSONB DEFAULT '[]',
    evidence_count INTEGER DEFAULT 0,

    -- Compression info
    compression_applied BOOLEAN DEFAULT FALSE,
    compression_ratio DECIMAL(5,2) DEFAULT 0.00,
    original_token_count INTEGER DEFAULT 0,

    -- Links and references
    raw_step_ids TEXT[] DEFAULT '{}',
    links JSONB DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT business_context_manifests_workspace_id_fkey
        FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
    CONSTRAINT business_context_manifests_user_id_fkey
        FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE SET NULL,
    CONSTRAINT business_context_manifests_version_unique
        UNIQUE (workspace_id, version_major, version_minor, version_patch),
    CONSTRAINT business_context_manifests_checksum_check
        CHECK (checksum IS NOT NULL AND length(checksum) = 64)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_bcm_workspace_id ON business_context_manifests(workspace_id);
CREATE INDEX IF NOT EXISTS idx_bcm_user_id ON business_context_manifests(user_id);
CREATE INDEX IF NOT EXISTS idx_bcm_created_at ON business_context_manifests(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_bcm_updated_at ON business_context_manifests(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_bcm_version ON business_context_manifests(version_major, version_minor, version_patch);
CREATE INDEX IF NOT EXISTS idx_bcm_checksum ON business_context_manifests(checksum);
CREATE INDEX IF NOT EXISTS idx_bcm_completion ON business_context_manifests(completion_percentage DESC);
CREATE INDEX IF NOT EXISTS idx_bcm_tokens ON business_context_manifests(token_count);

-- Create BCM version history table for tracking changes
CREATE TABLE IF NOT EXISTS bcm_version_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL,
    user_id UUID,

    -- Version information
    from_version_major INTEGER NOT NULL,
    from_version_minor INTEGER NOT NULL,
    from_version_patch INTEGER NOT NULL,
    from_version_string TEXT NOT NULL,

    to_version_major INTEGER NOT NULL,
    to_version_minor INTEGER NOT NULL,
    to_version_patch INTEGER NOT NULL,
    to_version_string TEXT NOT NULL,

    -- Change information
    change_type TEXT NOT NULL, -- 'major', 'minor', 'patch', 'hotfix'
    change_description TEXT,
    change_reason TEXT,

    -- Data comparison
    fields_changed TEXT[] DEFAULT '{}',
    checksum_before VARCHAR(64),
    checksum_after VARCHAR(64),

    -- Metadata
    changed_by UUID REFERENCES auth.users(id),
    changed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT bcm_version_history_workspace_id_fkey
        FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
    CONSTRAINT bcm_version_history_user_id_fkey
        FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE SET NULL
);

-- Indexes for version history
CREATE INDEX IF NOT EXISTS idx_bcm_history_workspace_id ON bcm_version_history(workspace_id);
CREATE INDEX IF NOT EXISTS idx_bcm_history_changed_at ON bcm_version_history(changed_at DESC);
CREATE INDEX IF NOT EXISTS idx_bcm_history_from_version ON bcm_version_history(from_version_major, from_version_minor, from_version_patch);
CREATE INDEX IF NOT EXISTS idx_bcm_history_to_version ON bcm_version_history(to_version_major, to_version_minor, to_version_patch);

-- Create BCM access logs table for audit trail
CREATE TABLE IF NOT EXISTS bcm_access_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL,
    user_id UUID,

    -- Access information
    access_type TEXT NOT NULL, -- 'create', 'read', 'update', 'delete', 'rebuild'
    access_source TEXT NOT NULL, -- 'api', 'service', 'migration', 'system'

    -- Request details
    request_id TEXT,
    ip_address INET,
    user_agent TEXT,

    -- Performance metrics
    response_time_ms INTEGER,
    cache_hit BOOLEAN DEFAULT FALSE,
    storage_tier TEXT, -- 'tier0', 'tier1', 'tier2', 'database'

    -- Result
    success BOOLEAN NOT NULL,
    error_message TEXT,
    error_code TEXT,

    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT bcm_access_logs_workspace_id_fkey
        FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
    CONSTRAINT bcm_access_logs_user_id_fkey
        FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE SET NULL
);

-- Indexes for access logs
CREATE INDEX IF NOT EXISTS idx_bcm_logs_workspace_id ON bcm_access_logs(workspace_id);
CREATE INDEX IF NOT EXISTS idx_bcm_logs_user_id ON bcm_access_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_bcm_logs_created_at ON bcm_access_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_bcm_logs_access_type ON bcm_access_logs(access_type);
CREATE INDEX IF NOT EXISTS idx_bcm_logs_success ON bcm_access_logs(success);

-- Create BCM metrics table for performance tracking
CREATE TABLE IF NOT EXISTS bcm_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL,

    -- Metrics data
    metric_date DATE NOT NULL,

    -- Generation metrics
    total_generations INTEGER DEFAULT 0,
    successful_generations INTEGER DEFAULT 0,
    failed_generations INTEGER DEFAULT 0,
    avg_generation_time_ms INTEGER DEFAULT 0,

    -- Storage metrics
    cache_hits INTEGER DEFAULT 0,
    cache_misses INTEGER DEFAULT 0,
    database_reads INTEGER DEFAULT 0,
    database_writes INTEGER DEFAULT 0,

    -- Performance metrics
    avg_token_count DECIMAL(8,2) DEFAULT 0.00,
    avg_compression_ratio DECIMAL(5,2) DEFAULT 0.00,
    avg_response_time_ms INTEGER DEFAULT 0,

    -- Size metrics
    total_storage_size_bytes BIGINT DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT bcm_metrics_workspace_id_fkey
        FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
    CONSTRAINT bcm_metrics_date_workspace_unique
        UNIQUE (metric_date, workspace_id)
);

-- Indexes for metrics
CREATE INDEX IF NOT EXISTS idx_bcm_metrics_workspace_id ON bcm_metrics(workspace_id);
CREATE INDEX IF NOT EXISTS idx_bcm_metrics_date ON bcm_metrics(metric_date DESC);
CREATE INDEX IF NOT EXISTS idx_bcm_metrics_created_at ON bcm_metrics(created_at DESC);

-- Create BCM cleanup queue for background jobs
CREATE TABLE IF NOT EXISTS bcm_cleanup_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL,

    -- Cleanup task
    task_type TEXT NOT NULL, -- 'expire_old_versions', 'cleanup_logs', 'compress_data'
    task_data JSONB DEFAULT '{}',

    -- Scheduling
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    priority INTEGER DEFAULT 5, -- 1=high, 5=low

    -- Status
    status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,

    -- Results
    result JSONB DEFAULT '{}',
    error_message TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Constraints
    CONSTRAINT bcm_cleanup_queue_workspace_id_fkey
        FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
);

-- Indexes for cleanup queue
CREATE INDEX IF NOT EXISTS idx_bcm_cleanup_workspace_id ON bcm_cleanup_queue(workspace_id);
CREATE INDEX IF NOT EXISTS idx_bcm_cleanup_status ON bcm_cleanup_queue(status);
CREATE INDEX IF NOT EXISTS idx_bcm_cleanup_scheduled_at ON bcm_cleanup_queue(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_bcm_cleanup_priority ON bcm_cleanup_queue(priority);

-- Create RLS (Row Level Security) policies
ALTER TABLE business_context_manifests ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access BCMs for their own workspaces
CREATE POLICY "Users can view own workspace BCMs" ON business_context_manifests
    FOR SELECT USING (
        workspace_id IN (
            SELECT id FROM workspaces WHERE owner_id = auth.uid()
            OR id IN (
                SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
            )
        )
    );

CREATE POLICY "Users can create BCMs in own workspaces" ON business_context_manifests
    FOR INSERT WITH CHECK (
        workspace_id IN (
            SELECT id FROM workspaces WHERE owner_id = auth.uid()
            OR id IN (
                SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
            )
        )
    );

CREATE POLICY "Users can update own workspace BCMs" ON business_context_manifests
    FOR UPDATE USING (
        workspace_id IN (
            SELECT id FROM workspaces WHERE owner_id = auth.uid()
            OR id IN (
                SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
            )
        )
    );

CREATE POLICY "Users can delete own workspace BCMs" ON business_context_manifests
    FOR DELETE USING (
        workspace_id IN (
            SELECT id FROM workspaces WHERE owner_id = auth.uid()
            OR id IN (
                SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
            )
        )
    );

-- Enable RLS for other tables
ALTER TABLE bcm_version_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE bcm_access_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE bcm_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE bcm_cleanup_queue ENABLE ROW LEVEL SECURITY;

-- Create trigger for updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to tables
CREATE TRIGGER update_business_context_manifests_updated_at
    BEFORE UPDATE ON business_context_manifests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bcm_version_history_updated_at
    BEFORE UPDATE ON bcm_version_history
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bcm_metrics_updated_at
    BEFORE UPDATE ON bcm_metrics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bcm_cleanup_queue_updated_at
    BEFORE UPDATE ON bcm_cleanup_queue
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create trigger for version history on BCM updates
CREATE OR REPLACE FUNCTION log_bcm_version_change()
RETURNS TRIGGER AS $$
DECLARE
    old_version TEXT;
    new_version TEXT;
    change_type TEXT;
BEGIN
    -- Only log if version actually changed
    IF TG_OP = 'UPDATE' THEN
        old_version := OLD.version_major || '.' || OLD.version_minor || '.' || OLD.version_patch;
        new_version := NEW.version_major || '.' || NEW.version_minor || '.' || NEW.version_patch;

        IF old_version != new_version THEN
            -- Determine change type
            IF NEW.version_major > OLD.version_major THEN
                change_type := 'major';
            ELSIF NEW.version_minor > OLD.version_minor THEN
                change_type := 'minor';
            ELSE
                change_type := 'patch';
            END IF;

            -- Insert version history record
            INSERT INTO bcm_version_history (
                workspace_id,
                user_id,
                from_version_major,
                from_version_minor,
                from_version_patch,
                from_version_string,
                to_version_major,
                to_version_minor,
                to_version_patch,
                to_version_string,
                change_type,
                checksum_before,
                checksum_after,
                changed_by
            ) VALUES (
                NEW.workspace_id,
                NEW.user_id,
                OLD.version_major,
                OLD.version_minor,
                OLD.version_patch,
                old_version,
                NEW.version_major,
                NEW.version_minor,
                NEW.version_patch,
                new_version,
                change_type,
                OLD.checksum,
                NEW.checksum,
                auth.uid()
            );
        END IF;
    END IF;

    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER log_bcm_version_change_trigger
    AFTER UPDATE ON business_context_manifests
    FOR EACH ROW EXECUTE FUNCTION log_bcm_version_change();

-- Create trigger for logging access
CREATE OR REPLACE FUNCTION log_bcm_access()
RETURNS TRIGGER AS $$
BEGIN
    -- Log access attempt (this would be called from application layer)
    -- For now, we'll just return the record
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Comments for documentation
COMMENT ON TABLE business_context_manifests IS 'Business Context Manifests with versioning and checksums';
COMMENT ON TABLE bcm_version_history IS 'Tracks version changes for BCMs';
COMMENT ON TABLE bcm_access_logs IS 'Audit trail for BCM access';
COMMENT ON TABLE bcm_metrics IS 'Performance metrics for BCM operations';
COMMENT ON TABLE bcm_cleanup_queue IS 'Background job queue for BCM maintenance';

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
-- GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
-- GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO authenticated;
