-- Onboarding Status Migration
-- Migrates from simple onboarding status to Redis-based session system with BCM integration

-- ==========================================
-- ONBOARDING SESSIONS TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS onboarding_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Session identification
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Session metadata
    client_name VARCHAR(255),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Progress tracking
    current_step INTEGER DEFAULT 1,
    total_steps INTEGER DEFAULT 24,
    completion_percentage DECIMAL(5,2) DEFAULT 0.00,

    -- Status tracking
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'abandoned', 'paused')),

    -- BCM integration
    bcm_generated BOOLEAN DEFAULT FALSE,
    bcm_version VARCHAR(20),
    bcm_checksum VARCHAR(64),
    bcm_generated_at TIMESTAMP WITH TIME ZONE,
    bcm_finalized BOOLEAN DEFAULT FALSE,
    bcm_finalized_at TIMESTAMP WITH TIME ZONE,

    -- Session data (backup for Redis)
    session_data JSONB DEFAULT '{}',

    -- Migration tracking
    migrated_from_legacy BOOLEAN DEFAULT FALSE,
    legacy_onboarding_status VARCHAR(50),
    legacy_onboarding_step VARCHAR(50),

    -- Metadata
    metadata JSONB DEFAULT '{}',

    -- Constraints
    CONSTRAINT check_completion_range CHECK (completion_percentage >= 0 AND completion_percentage <= 100),
    CONSTRAINT check_current_step_range CHECK (current_step >= 1 AND current_step <= total_steps)
);

-- ==========================================
-- ONBOARDING STEPS TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS onboarding_steps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Relations
    session_id UUID NOT NULL REFERENCES onboarding_sessions(id) ON DELETE CASCADE,

    -- Step identification
    step_number INTEGER NOT NULL,
    step_name VARCHAR(255) NOT NULL,
    phase_number INTEGER NOT NULL,

    -- Status tracking
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'in-progress', 'complete', 'blocked', 'error')),

    -- Step data
    step_data JSONB DEFAULT '{}',

    -- Timestamps
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Validation
    is_required BOOLEAN DEFAULT TRUE,

    -- Constraints
    UNIQUE(session_id, step_number),
    CONSTRAINT check_step_number_positive CHECK (step_number > 0)
);

-- ==========================================
-- BUSINESS CONTEXT MANIFESTS TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS business_context_manifests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Relations
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id UUID REFERENCES onboarding_sessions(id) ON DELETE SET NULL,

    -- Manifest metadata
    version VARCHAR(20) NOT NULL DEFAULT '1.0',
    checksum VARCHAR(64) NOT NULL,

    -- Manifest content
    manifest_json JSONB NOT NULL,

    -- Generation metadata
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    generated_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Size tracking
    token_count INTEGER DEFAULT 0,
    size_bytes INTEGER DEFAULT 0,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Constraints
    UNIQUE(workspace_id, version),
    CONSTRAINT check_token_count_positive CHECK (token_count >= 0),
    CONSTRAINT check_size_bytes_positive CHECK (size_bytes >= 0)
);

-- ==========================================
-- ONBOARDING MIGRATION LOG
-- ==========================================
CREATE TABLE IF NOT EXISTS onboarding_migration_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Migration details
    migration_type VARCHAR(100) NOT NULL,
    migration_version VARCHAR(50) NOT NULL,

    -- Source and target
    source_user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    target_session_id UUID REFERENCES onboarding_sessions(id) ON DELETE CASCADE,

    -- Legacy data
    legacy_onboarding_status VARCHAR(50),
    legacy_onboarding_step VARCHAR(50),
    legacy_has_completed_onboarding BOOLEAN,
    legacy_preferences JSONB,

    -- Migration status
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'failed')),
    error_message TEXT,

    -- Timestamps
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Metadata
    metadata JSONB DEFAULT '{}'
);

-- ==========================================
-- INDEXES
-- ==========================================
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_session_id ON onboarding_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_user_id ON onboarding_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_workspace_id ON onboarding_sessions(workspace_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_status ON onboarding_sessions(status);
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_completion ON onboarding_sessions(completion_percentage);
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_started_at ON onboarding_sessions(started_at);
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_migrated_from_legacy ON onboarding_sessions(migrated_from_legacy);

CREATE INDEX IF NOT EXISTS idx_onboarding_steps_session_id ON onboarding_steps(session_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_steps_session_step ON onboarding_steps(session_id, step_number);
CREATE INDEX IF NOT EXISTS idx_onboarding_steps_status ON onboarding_steps(status);
CREATE INDEX IF NOT EXISTS idx_onboarding_steps_phase ON onboarding_steps(phase_number);
CREATE INDEX IF NOT EXISTS idx_onboarding_steps_completed_at ON onboarding_steps(completed_at);

CREATE INDEX IF NOT EXISTS idx_business_context_manifests_workspace_id ON business_context_manifests(workspace_id);
CREATE INDEX IF NOT EXISTS idx_business_context_manifests_session_id ON business_context_manifests(session_id);
CREATE INDEX IF NOT EXISTS idx_business_context_manifests_version ON business_context_manifests(workspace_id, version);
CREATE INDEX IF NOT EXISTS idx_business_context_manifests_checksum ON business_context_manifests(checksum);
CREATE INDEX IF NOT EXISTS idx_business_context_manifests_is_active ON business_context_manifests(is_active);

CREATE INDEX IF NOT EXISTS idx_onboarding_migration_log_user_id ON onboarding_migration_log(source_user_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_migration_log_session_id ON onboarding_migration_log(target_session_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_migration_log_status ON onboarding_migration_log(status);
CREATE INDEX IF NOT EXISTS idx_onboarding_migration_log_type ON onboarding_migration_log(migration_type);

-- ==========================================
-- TRIGGERS FOR UPDATED_AT
-- ==========================================
CREATE OR REPLACE FUNCTION update_onboarding_session_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE OR REPLACE FUNCTION update_onboarding_step_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE OR REPLACE FUNCTION update_bcm_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.generated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_onboarding_session_updated_at BEFORE UPDATE ON onboarding_sessions
    FOR EACH ROW EXECUTE FUNCTION update_onboarding_session_updated_at();

CREATE TRIGGER update_onboarding_step_updated_at BEFORE UPDATE ON onboarding_steps
    FOR EACH ROW EXECUTE FUNCTION update_onboarding_step_updated_at();

CREATE TRIGGER update_bcm_updated_at BEFORE UPDATE ON business_context_manifests
    FOR EACH ROW EXECUTE FUNCTION update_bcm_updated_at();

-- ==========================================
-- MIGRATION FUNCTION: LEGACY TO NEW SYSTEM
-- ==========================================
CREATE OR REPLACE FUNCTION migrate_legacy_onboarding_status()
RETURNS TRIGGER AS $$
DECLARE
    legacy_user_id UUID;
    new_session_id UUID;
    workspace_id UUID;
    legacy_status TEXT;
    legacy_step TEXT;
    has_completed BOOLEAN;
    migration_log_id UUID;

    -- Constants for step mapping
    step_mapping JSONB DEFAULT '{
        "welcome": 1,
        "evidence": 2,
        "brand": 3,
        "truth": 4,
        "offer": 5,
        "market": 6,
        "competitors": 7,
        "angle": 8,
        "category": 9,
        "capabilities": 10,
        "perceptual": 11,
        "positioning": 12,
        "gap": 13,
        "positioning_statements": 14,
        "focus": 15,
        "icp": 16,
        "process": 17,
        "messaging": 18,
        "soundbites": 19,
        "hierarchy": 20,
        "augmentation": 21,
        "channels": 22,
        "market_size": 23,
        "todos": 24,
        "synthesis": 25,
        "export": 26
    }'::jsonb;
BEGIN
    -- Get the user ID from the auth.users record
    legacy_user_id := NEW.id;

    -- Get workspace ID for the user
    SELECT w.id INTO workspace_id
    FROM workspaces w
    WHERE w.owner_id = legacy_user_id
    LIMIT 1;

    -- Get legacy onboarding status
    legacy_status := COALESCE(NEW.onboarding_status, 'none');
    legacy_step := COALESCE(NEW.onboarding_step, 'welcome');
    has_completed := COALESCE(NEW.has_completed_onboarding, FALSE);

    -- Skip if already migrated
    IF EXISTS (
        SELECT 1 FROM onboarding_sessions
        WHERE user_id = legacy_user_id
        AND migrated_from_legacy = TRUE
    ) THEN
        RETURN NEW;
    END IF;

    -- Create migration log entry
    INSERT INTO onboarding_migration_log (
        migration_type,
        migration_version,
        source_user_id,
        legacy_onboarding_status,
        legacy_onboarding_step,
        legacy_has_completed_onboarding,
        legacy_preferences,
        status
    ) VALUES (
        'legacy_to_redis',
        '1.0',
        legacy_user_id,
        legacy_status,
        legacy_step,
        has_completed,
        NEW.preferences,
        'in_progress'
    ) RETURNING id INTO migration_log_id;

    -- Generate session ID
    new_session_id := 'session-' || EXTRACT(EPOCH FROM NOW())::TEXT || '-' || SUBSTR(MD5(legacy_user_id::TEXT), 1, 8);

    -- Create new onboarding session
    INSERT INTO onboarding_sessions (
        session_id,
        user_id,
        workspace_id,
        client_name,
        started_at,
        current_step,
        total_steps,
        completion_percentage,
        status,
        migrated_from_legacy,
        legacy_onboarding_status,
        legacy_onboarding_step,
        session_data,
        metadata
    ) VALUES (
        new_session_id,
        legacy_user_id,
        workspace_id,
        COALESCE(NEW.full_name, SPLIT_PART(NEW.email, '@', 1)),
        COALESCE(NEW.created_at, NOW()),
        COALESCE((step_mapping->>legacy_step)::INTEGER, 1),
        24,
        CASE
            WHEN has_completed THEN 100.0
            WHEN legacy_step IS NOT NULL THEN
                GREATEST((step_mapping->>legacy_step)::INTEGER, 1) * 4.17  -- Approximate percentage
            ELSE 0.0
        END,
        CASE
            WHEN has_completed THEN 'completed'
            WHEN legacy_status IN ('active', 'in_progress') THEN 'active'
            ELSE 'abandoned'
        END,
        TRUE,
        legacy_status,
        legacy_step,
        jsonb_build_object(
            'legacy_status', legacy_status,
            'legacy_step', legacy_step,
            'legacy_has_completed_onboarding', has_completed,
            'migrated_at', NOW()
        ),
        jsonb_build_object(
            'migration_log_id', migration_log_id,
            'migration_version', '1.0'
        )
    ) RETURNING id;

    -- Create step records for completed steps
    IF has_completed THEN
        INSERT INTO onboarding_steps (
            session_id,
            step_number,
            step_name,
            phase_number,
            status,
            step_data,
            started_at,
            completed_at,
            updated_at,
            is_required
        )
        SELECT
            new_session_id,
            step_number,
            step_name,
            phase_number,
            'complete',
            jsonb_build_object('migrated_from_legacy', TRUE),
            COALESCE(NEW.created_at, NOW()),
            COALESCE(NEW.updated_at, NOW()),
            NOW(),
            step_number <= 12  -- First 12 steps are typically required
        FROM (
            SELECT
                unnest(ARRAY[
                    1, 'Evidence Vault', 1,
                    2, 'Brand Synthesis', 1,
                    3, 'Strategic Integrity', 1,
                    4, 'Truth Confirmation', 1,
                    5, 'The Offer', 2,
                    6, 'Market Intelligence', 3,
                    7, 'Competitive Landscape', 3,
                    8, 'Comparative Angle', 3,
                    9, 'Market Category', 4,
                    10, 'Product Capabilities', 4,
                    11, 'Perceptual Map', 4,
                    12, 'Position Grid', 4
                ]) AS step_data(step_number, step_name, phase_number)
        ) AS steps(step_number, step_name, phase_number);
    END IF;

    -- Update migration log
    UPDATE onboarding_migration_log
    SET status = 'completed',
        completed_at = NOW(),
        target_session_id = (SELECT id FROM onboarding_sessions WHERE session_id = new_session_id)
    WHERE id = migration_log_id;

    -- Update user to mark migration complete
    UPDATE users
    SET onboarding_status = 'migrated',
        updated_at = NOW()
    WHERE id = legacy_user_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger for automatic migration
CREATE TRIGGER migrate_legacy_onboarding_on_update
    AFTER UPDATE ON users
    FOR EACH ROW
    WHEN (
        NEW.onboarding_status IS DISTINCT FROM OLD.onboarding_status
        OR NEW.onboarding_step IS DISTINCT FROM OLD.onboarding_step
        OR NEW.has_completed_onboarding IS DISTINCT FROM OLD.has_completed_onboarding
    )
    EXECUTE FUNCTION migrate_legacy_onboarding_status();

-- ==========================================
-- RLS POLICIES FOR NEW TABLES
-- ==========================================
ALTER TABLE onboarding_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE onboarding_steps ENABLE ROW LEVEL SECURITY;
ALTER TABLE business_context_manifests ENABLE ROW LEVEL SECURITY;
ALTER TABLE onboarding_migration_log ENABLE ROW LEVEL SECURITY;

-- Users can only see their own onboarding sessions
CREATE POLICY "Users can view own onboarding sessions" ON onboarding_sessions FOR SELECT USING (
    user_id = (SELECT id FROM users WHERE auth_user_id = auth.uid())
);

CREATE POLICY "Users can update own onboarding sessions" ON onboarding_sessions FOR UPDATE USING (
    user_id = (SELECT id FROM users WHERE auth_user_id = auth.uid())
);

-- Users can view steps for their own sessions
CREATE POLICY "Users can view own onboarding steps" ON onboarding_steps FOR SELECT USING (
    session_id IN (
        SELECT id FROM onboarding_sessions
        WHERE user_id = (SELECT id FROM users WHERE auth_user_id = auth.uid())
    )
);

-- Users can view BCMs for their workspaces
CREATE POLICY "Users can view workspace BCMs" ON business_context_manifests FOR SELECT USING (
    workspace_id IN (
        SELECT id FROM workspaces
        WHERE owner_id = (SELECT id FROM users WHERE auth_user_id = auth.uid())
        OR id IN (
            SELECT workspace_id FROM workspace_members
            WHERE user_id = (SELECT id FROM users WHERE auth_user_id = auth.uid())
        )
    )
);

-- Users can view their own migration logs
CREATE POLICY "Users can view own migration logs" ON onboarding_migration_log FOR SELECT USING (
    source_user_id = (SELECT id FROM users WHERE auth_user_id = auth.uid())
);

-- ==========================================
-- VIEWS FOR CONVENIENT ACCESS
-- ==========================================
CREATE OR REPLACE VIEW user_onboarding_status AS
SELECT
    u.id as user_id,
    u.email,
    u.full_name,
    u.onboarding_status as legacy_status,
    u.has_completed_onboarding as legacy_completed,
    os.session_id,
    os.status as session_status,
    os.current_step,
    os.total_steps,
    os.completion_percentage,
    os.started_at as session_started_at,
    os.completed_at as session_completed_at,
    os.bcm_generated,
    os.bcm_version,
    os.bcm_finalized,
    os.migrated_from_legacy,
    CASE
        WHEN os.bcm_finalized THEN 'finalized'
        WHEN os.bcm_generated THEN 'bcm_generated'
        WHEN os.status = 'completed' THEN 'completed'
        WHEN os.status = 'active' THEN 'in_progress'
        ELSE os.status
    END as calculated_status
FROM users u
LEFT JOIN onboarding_sessions os ON u.id = os.user_id
WHERE u.is_active = TRUE;

CREATE OR REPLACE VIEW workspace_onboarding_summary AS
SELECT
    w.id as workspace_id,
    w.name as workspace_name,
    w.owner_id,
    COUNT(os.id) as total_sessions,
    COUNT(CASE WHEN os.status = 'completed' THEN 1 END) as completed_sessions,
    COUNT(CASE WHEN os.status = 'active' THEN 1 END) as active_sessions,
    AVG(os.completion_percentage) as avg_completion_percentage,
    COUNT(CASE WHEN os.bcm_generated THEN 1 END) as bcm_generated_sessions,
    COUNT(CASE WHEN os.bcm_finalized THEN 1 END) as bcm_finalized_sessions,
    MAX(os.completed_at) as last_completion_at
FROM workspaces w
LEFT JOIN onboarding_sessions os ON w.id = os.workspace_id
GROUP BY w.id, w.name, w.owner_id;

-- ==========================================
-- INSERT DEFAULT STEP CONFIGURATION
-- ==========================================
INSERT INTO onboarding_steps (
    session_id,
    step_number,
    step_name,
    phase_number,
    status,
    is_required,
    step_data
)
SELECT
    s.id,
    step_number,
    step_name,
    phase_number,
    'pending',
    step_number <= 12,  -- First 12 steps are required
    jsonb_build_object(
        'description', step_description,
        'estimated_time_minutes', estimated_time,
        'dependencies', dependencies
    )
FROM (
    SELECT
        uuid_generate_v4() as id,
        unnest(ARRAY[
            1, 'Evidence Vault', 1, 'Collect and organize evidence documents', 30, ARRAY[]::text[],
            2, 'Brand Synthesis', 1, 'Synthesize brand identity and values', 45, ARRAY[1],
            3, 'Strategic Integrity', 1, 'Ensure strategic alignment across all elements', 60, ARRAY[1, 2],
            4, 'Truth Confirmation', 1, 'Validate truth claims with evidence', 30, ARRAY[1, 2, 3],
            5, 'The Offer', 2, 'Define core value proposition', 45, ARRAY[1, 2, 3, 4],
            6, 'Market Intelligence', 3, 'Gather market research and insights', 60, ARRAY[1, 2, 3, 4, 5],
            7, 'Competitive Landscape', 3, 'Analyze competitive positioning', 45, ARRAY[1, 2, 3, 4, 5, 6],
            8, 'Comparative Angle', 3, 'Define competitive advantages', 30, ARRAY[1, 2, 3, 4, 5, 6, 7],
            9, 'Market Category', 4, 'Position in market category', 30, ARRAY[1, 2, 3, 4, 5, 6, 7, 8],
            10, 'Product Capabilities', 4, 'Document product capabilities', 45, ARRAY[1, 2, 3, 4, 5, 6, 7, 8, 9],
            11, 'Perceptual Map', 4, 'Create perceptual positioning map', 60, ARRAY[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            12, 'Position Grid', 4, 'Define positioning matrix', 45, ARRAY[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            13, 'Gap Analysis', 4, 'Identify gaps and opportunities', 30, ARRAY[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            14, 'Positioning Statements', 5, 'Craft positioning statements', 60, ARRAY[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
            15, 'Focus & Sacrifice', 5, 'Define strategic focus', 45, ARRAY[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
            16, 'ICP Personas', 5, 'Develop ideal customer profiles', 75, ARRAY[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
            17, 'Market Education', 5, 'Create market education content', 60, ARRAY[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
            18, 'Messaging Rules', 5, 'Define messaging guidelines', 45, ARRAY[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17],
            19, 'Soundbites Library', 5, 'Create soundbite library', 30, ARRAY[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
            20, 'Channel Strategy', 6, 'Define channel strategy', 60, ARRAY[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
            21, 'Market Size', 6, 'Calculate market sizing', 45, ARRAY[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
            22, 'Validation Tasks', 6, 'Complete validation tasks', 30, ARRAY[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21],
            23, 'Final Synthesis', 6, 'Synthesize final deliverables', 90, ARRAY[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22],
            24, 'Export & Launch', 6, 'Export and launch deliverables', 30, ARRAY[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
        ]) AS step_data(step_number, step_name, phase_number, step_description, estimated_time, dependencies)
) s
WHERE NOT EXISTS (
    SELECT 1 FROM onboarding_steps
    WHERE step_number = s.step_number
    AND session_id = s.id
);

-- ==========================================
-- COMMENTS
-- ==========================================
COMMENT ON TABLE onboarding_sessions IS 'Tracks onboarding sessions with Redis integration and BCM support';
COMMENT ON TABLE onboarding_steps IS 'Individual steps within onboarding sessions';
COMMENT ON TABLE business_context_manifests IS 'Business Context Manifests with versioning and integrity tracking';
COMMENT ON TABLE onboarding_migration_log IS 'Logs migration from legacy onboarding status to new system';

COMMENT ON COLUMN onboarding_sessions.session_id IS 'Unique identifier for the onboarding session';
COMMENT ON COLUMN onboarding_sessions.completion_percentage IS 'Percentage of onboarding completion (0-100)';
COMMENT ON COLUMN onboarding_sessions.bcm_generated IS 'Whether BCM has been generated for this session';
COMMENT ON COLUMN onboarding_sessions.bcm_finalized IS 'Whether BCM has been finalized for this session';
COMMENT ON COLUMN onboarding_sessions.migrated_from_legacy IS 'Whether this session was migrated from legacy status';

COMMENT ON COLUMN business_context_manifests.version IS 'BCM schema version';
COMMENT ON COLUMN business_context_manifests.checksum IS 'SHA-256 checksum for integrity verification';
COMMENT ON COLUMN business_context_manifests.token_count IS 'Estimated token count for the manifest';
COMMENT ON COLUMN business_context_manifests.size_bytes IS 'Size of manifest in bytes';
