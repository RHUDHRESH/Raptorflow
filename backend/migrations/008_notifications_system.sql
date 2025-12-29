-- Notifications table for comprehensive notification management
-- This table stores all notifications with delivery tracking and metadata

CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'informational',
    channel VARCHAR(20) NOT NULL DEFAULT 'email',
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    subject VARCHAR(255),
    recipients JSONB NOT NULL DEFAULT '[]'::JSONB,
    sender_id UUID,
    priority VARCHAR(20) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'delivered', 'failed', 'cancelled')),
    delivery_results JSONB DEFAULT '{}'::JSONB,
    read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP WITH TIME ZONE,
    scheduled_at TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::JSONB,
    template_id VARCHAR(100),
    batch_id VARCHAR(100),
    parent_notification_id UUID REFERENCES notifications(id) ON DELETE SET NULL
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_notifications_workspace_id ON notifications(workspace_id);
CREATE INDEX IF NOT EXISTS idx_notifications_tenant_id ON notifications(tenant_id);
CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications(status);
CREATE INDEX IF NOT EXISTS idx_notifications_channel ON notifications(channel);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type);
CREATE INDEX IF NOT EXISTS idx_notifications_priority ON notifications(priority);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notifications_scheduled_at ON notifications(scheduled_at) WHERE scheduled_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(read) WHERE read = FALSE;
CREATE INDEX IF NOT EXISTS idx_notifications_batch_id ON notifications(batch_id) WHERE batch_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_notifications_parent ON notifications(parent_notification_id) WHERE parent_notification_id IS NOT NULL;

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_notifications_workspace_status ON notifications(workspace_id, status);
CREATE INDEX IF NOT EXISTS idx_notifications_tenant_channel ON notifications(tenant_id, channel);
CREATE INDEX IF NOT EXISTS idx_notifications_recipient_lookup ON notifications USING GIN (recipients);

-- Notification templates table
CREATE TABLE IF NOT EXISTS notification_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    subject VARCHAR(255),
    content TEXT NOT NULL,
    variables JSONB DEFAULT '[]'::JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    updated_by UUID
);

-- Template indexes
CREATE INDEX IF NOT EXISTS idx_notification_templates_workspace ON notification_templates(workspace_id);
CREATE INDEX IF NOT EXISTS idx_notification_templates_channel ON notification_templates(channel);
CREATE INDEX IF NOT EXISTS idx_notification_templates_active ON notification_templates(is_active) WHERE is_active = TRUE;

-- Notification preferences table
CREATE TABLE IF NOT EXISTS notification_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    user_id UUID NOT NULL,
    email_notifications BOOLEAN DEFAULT TRUE,
    sms_notifications BOOLEAN DEFAULT FALSE,
    push_notifications BOOLEAN DEFAULT TRUE,
    in_app_notifications BOOLEAN DEFAULT TRUE,
    business_hours_only BOOLEAN DEFAULT TRUE,
    quiet_hours_enabled BOOLEAN DEFAULT FALSE,
    quiet_hours_start TIME DEFAULT '22:00:00',
    quiet_hours_end TIME DEFAULT '08:00:00',
    timezone VARCHAR(50) DEFAULT 'UTC',
    notification_types JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(workspace_id, user_id)
);

-- Preference indexes
CREATE INDEX IF NOT EXISTS idx_notification_preferences_user ON notification_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_notification_preferences_workspace ON notification_preferences(workspace_id);

-- Notification delivery logs table for detailed tracking
CREATE TABLE IF NOT EXISTS notification_delivery_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notification_id UUID NOT NULL REFERENCES notifications(id) ON DELETE CASCADE,
    recipient VARCHAR(255) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    metadata JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Delivery log indexes
CREATE INDEX IF NOT EXISTS idx_notification_delivery_logs_notification ON notification_delivery_logs(notification_id);
CREATE INDEX IF NOT EXISTS idx_notification_delivery_logs_status ON notification_delivery_logs(status);
CREATE INDEX IF NOT EXISTS idx_notification_delivery_logs_recipient ON notification_delivery_logs(recipient);

-- Notification schedules table
CREATE TABLE IF NOT EXISTS notification_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    notification_data JSONB NOT NULL,
    recipients JSONB NOT NULL DEFAULT '[]'::JSONB,
    channels JSONB NOT NULL DEFAULT '[]'::JSONB,
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    frequency VARCHAR(20) DEFAULT 'once',
    end_date TIMESTAMP WITH TIME ZONE,
    max_occurrences INTEGER DEFAULT 0,
    occurrence_count INTEGER DEFAULT 0,
    next_run TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'active', 'paused', 'completed', 'cancelled')),
    timezone VARCHAR(50) DEFAULT 'UTC',
    business_hours_only BOOLEAN DEFAULT FALSE,
    retry_failed BOOLEAN DEFAULT TRUE,
    max_retries INTEGER DEFAULT 3,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID
);

-- Schedule indexes
CREATE INDEX IF NOT EXISTS idx_notification_schedules_workspace ON notification_schedules(workspace_id);
CREATE INDEX IF NOT EXISTS idx_notification_schedules_next_run ON notification_schedules(next_run) WHERE status = 'scheduled';
CREATE INDEX IF NOT EXISTS idx_notification_schedules_status ON notification_schedules(status);

-- Triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to all tables
DROP TRIGGER IF EXISTS notifications_updated_at_trigger ON notifications;
CREATE TRIGGER notifications_updated_at_trigger
    BEFORE UPDATE ON notifications
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS notification_templates_updated_at_trigger ON notification_templates;
CREATE TRIGGER notification_templates_updated_at_trigger
    BEFORE UPDATE ON notification_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS notification_preferences_updated_at_trigger ON notification_preferences;
CREATE TRIGGER notification_preferences_updated_at_trigger
    BEFORE UPDATE ON notification_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS notification_schedules_updated_at_trigger ON notification_schedules;
CREATE TRIGGER notification_schedules_updated_at_trigger
    BEFORE UPDATE ON notification_schedules
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Views for common queries
CREATE OR REPLACE VIEW notification_summary AS
SELECT
    n.id,
    n.workspace_id,
    n.type,
    n.channel,
    n.title,
    n.status,
    n.priority,
    n.read,
    n.created_at,
    n.sent_at,
    n.delivered_at,
    jsonb_array_length(n.recipients) as recipient_count,
    CASE
        WHEN n.status = 'delivered' THEN 1
        WHEN n.status = 'sent' THEN 0.8
        WHEN n.status = 'failed' THEN 0
        ELSE 0.5
    END as delivery_score
FROM notifications n;

CREATE OR REPLACE VIEW user_notification_counts AS
SELECT
    p.user_id,
    p.workspace_id,
    COUNT(CASE WHEN n.read = FALSE THEN 1 END) as unread_count,
    COUNT(CASE WHEN n.read = TRUE THEN 1 END) as read_count,
    COUNT(*) as total_count
FROM notification_preferences p
LEFT JOIN notifications n ON p.workspace_id = n.workspace_id
    AND jsonb_array_length(n.recipients) > 0
    AND n.created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY p.user_id, p.workspace_id;
