-- Approval Gates Migration for Cognitive Engine HITL System
-- Implements PROMPT 43 from STREAM_3_COGNITIVE_ENGINE

-- Create approval_gates table
CREATE TABLE IF NOT EXISTS approval_gates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Request details
    request_type TEXT NOT NULL CHECK (request_type IN ('plan_approval', 'output_approval', 'high_cost_action', 'external_post', 'deletion', 'data_export')),
    output_preview TEXT NOT NULL,
    risk_level INTEGER NOT NULL CHECK (risk_level BETWEEN 1 AND 5),
    reason TEXT NOT NULL,

    -- Status tracking
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'expired', 'auto_approved')),
    response_feedback TEXT,
    responded_at TIMESTAMPTZ,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '5 hours'),

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    correlation_id TEXT UNIQUE,
    estimated_cost DECIMAL(10,4) DEFAULT 0.0000,
    actual_cost DECIMAL(10,4) DEFAULT 0.0000
);

-- Create indexes for performance
CREATE INDEX idx_approval_gates_workspace_status ON approval_gates(workspace_id, status);
CREATE INDEX idx_approval_gates_user_status ON approval_gates(user_id, status);
CREATE INDEX idx_approval_gates_created_at ON approval_gates(created_at DESC);
CREATE INDEX idx_approval_gates_expires_at ON approval_gates(expires_at) WHERE status = 'pending';
CREATE INDEX idx_approval_gates_correlation_id ON approval_gates(correlation_id) WHERE correlation_id IS NOT NULL;

-- Create approval_responses table for detailed feedback
CREATE TABLE IF NOT EXISTS approval_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    gate_id UUID NOT NULL REFERENCES approval_gates(id) ON DELETE CASCADE,

    -- Response details
    approver_id UUID NOT NULL REFERENCES auth.users(id),
    approved BOOLEAN NOT NULL,
    feedback TEXT,
    modified_output TEXT,

    -- Scoring
    confidence_score INTEGER CHECK (confidence_score BETWEEN 1 AND 10),
    risk_assessment TEXT CHECK (risk_assessment IN ('low_risk', 'medium_risk', 'high_risk', 'unacceptable')),

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    response_time_ms INTEGER,

    -- Metadata
    approval_method TEXT DEFAULT 'manual' CHECK (approval_method IN ('manual', 'auto', 'escalated')),
    delegation_from UUID REFERENCES auth.users(id)
);

-- Create indexes for approval responses
CREATE INDEX idx_approval_responses_gate_id ON approval_responses(gate_id);
CREATE INDEX idx_approval_responses_approver ON approval_responses(approver_id, created_at DESC);

-- Create approval_templates for common approval types
CREATE TABLE IF NOT EXISTS approval_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Template details
    name TEXT NOT NULL,
    description TEXT,
    request_type TEXT NOT NULL,

    -- Auto-approval rules
    auto_approval_rules JSONB DEFAULT '{}'::jsonb,
    risk_threshold INTEGER DEFAULT 3,
    cost_threshold DECIMAL(10,4) DEFAULT 0.5000,

    -- Notification settings
    notification_channels JSONB DEFAULT '["email"]'::jsonb,
    escalation_rules JSONB DEFAULT '{}'::jsonb,

    -- Status
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for templates
CREATE INDEX idx_approval_templates_workspace_active ON approval_templates(workspace_id, active);

-- Row Level Security
ALTER TABLE approval_gates ENABLE ROW LEVEL SECURITY;
ALTER TABLE approval_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE approval_templates ENABLE ROW LEVEL SECURITY;

-- RLS Policies for approval_gates
CREATE POLICY "Users can view their own approval gates" ON approval_gates
    FOR SELECT USING (
        auth.uid() = user_id OR
        auth.uid() IN (SELECT user_id FROM workspace_members WHERE workspace_id = approval_gates.workspace_id AND role IN ('admin', 'owner'))
    );

CREATE POLICY "Users can create approval gates" ON approval_gates
    FOR INSERT WITH CHECK (
        auth.uid() = user_id OR
        auth.uid() IN (SELECT user_id FROM workspace_members WHERE workspace_id = approval_gates.workspace_id AND role IN ('admin', 'owner', 'member'))
    );

CREATE POLICY "Users can update approval gates" ON approval_gates
    FOR UPDATE USING (
        auth.uid() = user_id OR
        auth.uid() IN (SELECT user_id FROM workspace_members WHERE workspace_id = approval_gates.workspace_id AND role IN ('admin', 'owner'))
    );

-- RLS Policies for approval_responses
CREATE POLICY "Users can view approval responses for their gates" ON approval_responses
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM approval_gates
            WHERE approval_gates.id = approval_responses.gate_id
            AND (
                auth.uid() = approval_gates.user_id OR
                auth.uid() IN (SELECT user_id FROM workspace_members WHERE workspace_id = approval_gates.workspace_id AND role IN ('admin', 'owner'))
            )
        )
    );

CREATE POLICY "Users can create approval responses" ON approval_responses
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM approval_gates
            WHERE approval_gates.id = approval_responses.gate_id
            AND (
                auth.uid() = approval_responses.approver_id OR
                auth.uid() IN (SELECT user_id FROM workspace_members WHERE workspace_id = approval_gates.workspace_id AND role IN ('admin', 'owner'))
            )
        )
    );

-- RLS Policies for approval_templates
CREATE POLICY "Workspace members can view approval templates" ON approval_templates
    FOR SELECT USING (
        auth.uid() IN (SELECT user_id FROM workspace_members WHERE workspace_id = approval_templates.workspace_id)
    );

CREATE POLICY "Workspace admins can manage approval templates" ON approval_templates
    FOR ALL USING (
        auth.uid() IN (SELECT user_id FROM workspace_members WHERE workspace_id = approval_templates.workspace_id AND role IN ('admin', 'owner'))
    );

-- Functions for approval management

-- Function to create approval gate
CREATE OR REPLACE FUNCTION create_approval_gate(
    p_workspace_id UUID,
    p_user_id UUID,
    p_request_type TEXT,
    p_output_preview TEXT,
    p_risk_level INTEGER,
    p_reason TEXT,
    p_metadata JSONB DEFAULT '{}'::jsonb,
    p_correlation_id TEXT DEFAULT NULL,
    p_estimated_cost DECIMAL(10,4) DEFAULT 0.0000
) RETURNS UUID AS $$
DECLARE
    gate_id UUID;
BEGIN
    INSERT INTO approval_gates (
        workspace_id,
        user_id,
        request_type,
        output_preview,
        risk_level,
        reason,
        metadata,
        correlation_id,
        estimated_cost,
        expires_at
    ) VALUES (
        p_workspace_id,
        p_user_id,
        p_request_type,
        p_output_preview,
        p_risk_level,
        p_reason,
        p_metadata,
        p_correlation_id,
        p_estimated_cost,
        NOW() + (
            CASE
                WHEN p_risk_level >= 4 THEN INTERVAL '24 hours'
                WHEN p_risk_level >= 3 THEN INTERVAL '12 hours'
                ELSE INTERVAL '5 hours'
            END
        )
    ) RETURNING id INTO gate_id;

    RETURN gate_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to respond to approval gate
CREATE OR REPLACE FUNCTION respond_to_approval_gate(
    p_gate_id UUID,
    p_approver_id UUID,
    p_approved BOOLEAN,
    p_feedback TEXT DEFAULT NULL,
    p_modified_output TEXT DEFAULT NULL,
    p_confidence_score INTEGER DEFAULT NULL,
    p_risk_assessment TEXT DEFAULT NULL
) RETURNS BOOLEAN AS $$
DECLARE
    gate_record RECORD;
BEGIN
    -- Lock the gate for update
    SELECT * INTO gate_record FROM approval_gates WHERE id = p_gate_id FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Approval gate not found';
    END IF;

    IF gate_record.status != 'pending' THEN
        RAISE EXCEPTION 'Approval gate is not pending';
    END IF;

    IF gate_record.expires_at < NOW() THEN
        UPDATE approval_gates SET status = 'expired' WHERE id = p_gate_id;
        RAISE EXCEPTION 'Approval gate has expired';
    END IF;

    -- Create response record
    INSERT INTO approval_responses (
        gate_id,
        approver_id,
        approved,
        feedback,
        modified_output,
        confidence_score,
        risk_assessment,
        response_time_ms,
        created_at
    ) VALUES (
        p_gate_id,
        p_approver_id,
        p_approved,
        p_feedback,
        p_modified_output,
        p_confidence_score,
        p_risk_assessment,
        EXTRACT(MILLISECONDS FROM (NOW() - gate_record.created_at))::INTEGER,
        NOW()
    );

    -- Update gate status
    UPDATE approval_gates SET
        status = CASE WHEN p_approved THEN 'approved' ELSE 'rejected' END,
        response_feedback = p_feedback,
        responded_at = NOW()
    WHERE id = p_gate_id;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to auto-approve low-risk gates
CREATE OR REPLACE FUNCTION auto_approve_low_risk_gates() RETURNS INTEGER AS $$
DECLARE
    approved_count INTEGER := 0;
    gate_record RECORD;
BEGIN
    -- Auto-approve gates that meet criteria
    FOR gate_record IN
        SELECT * FROM approval_gates
        WHERE status = 'pending'
        AND risk_level <= 2
        AND estimated_cost <= 0.1000
        AND created_at < NOW() - INTERVAL '1 minute'
        AND expires_at > NOW()
    LOOP
        -- Check if there's an auto-approval template
        IF EXISTS (
            SELECT 1 FROM approval_templates
            WHERE workspace_id = gate_record.workspace_id
            AND active = true
            AND request_type = gate_record.request_type
            AND risk_threshold >= gate_record.risk_level
            AND cost_threshold >= gate_record.estimated_cost
        ) THEN
            UPDATE approval_gates SET
                status = 'auto_approved',
                responded_at = NOW()
            WHERE id = gate_record.id;

            -- Log auto-approval
            INSERT INTO approval_responses (
                gate_id,
                approver_id,
                approved,
                feedback,
                approval_method,
                created_at
            ) VALUES (
                gate_record.id,
                '00000000-0000-0000-0000-000000000000', -- System user
                true,
                'Auto-approved: Low risk and cost within thresholds',
                'auto',
                NOW()
            );

            approved_count := approved_count + 1;
        END IF;
    END LOOP;

    RETURN approved_count;
END;
$$ LANGUAGE plpgsql;

-- Function to expire pending gates
CREATE OR REPLACE FUNCTION expire_pending_gates() RETURNS INTEGER AS $$
DECLARE
    expired_count INTEGER := 0;
BEGIN
    UPDATE approval_gates
    SET status = 'expired', responded_at = NOW()
    WHERE status = 'pending' AND expires_at < NOW();

    GET DIAGNOSTICS expired_count = ROW_COUNT;
    RETURN expired_count;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to update updated_at on approval_templates
CREATE OR REPLACE FUNCTION update_approval_templates_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_approval_templates_updated_at
    BEFORE UPDATE ON approval_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_approval_templates_updated_at();

-- Grant permissions to authenticated users
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON approval_gates TO authenticated;
GRANT ALL ON approval_responses TO authenticated;
GRANT ALL ON approval_templates TO authenticated;

-- Grant execute permissions on functions
GRANT EXECUTE ON FUNCTION create_approval_gate TO authenticated;
GRANT EXECUTE ON FUNCTION respond_to_approval_gate TO authenticated;
GRANT EXECUTE ON FUNCTION auto_approve_low_risk_gates TO authenticated;
GRANT EXECUTE ON FUNCTION expire_pending_gates TO authenticated;

-- Create scheduled job for auto-approval (requires pg_cron extension)
-- SELECT cron.schedule('auto-approve-gates', '*/1 * * * *', 'SELECT auto_approve_low_risk_gates();');
-- SELECT cron.schedule('expire-gates', '*/5 * * * *', 'SELECT expire_pending_gates();');
