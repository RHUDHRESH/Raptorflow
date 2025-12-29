-- Supabase triggers for real-time notifications
-- These triggers will automatically send push/in-app notifications when notifications are created

-- Function to send real-time notification via Supabase Realtime
CREATE OR REPLACE FUNCTION send_realtime_notification()
RETURNS TRIGGER AS $$
BEGIN
    -- Send notification to Supabase Realtime for in-app notifications
    -- This will trigger real-time updates to connected clients
    PERFORM pg_notify(
        'new_notification',
        json_build_object(
            'id', NEW.id,
            'workspace_id', NEW.workspace_id,
            'type', NEW.type,
            'channel', NEW.channel,
            'title', NEW.title,
            'message', NEW.message,
            'recipients', NEW.recipients,
            'priority', NEW.priority,
            'status', NEW.status,
            'created_at', NEW.created_at,
            'metadata', NEW.metadata
        )::text
    );

    -- Also send to specific recipient channels
    IF jsonb_typeof(NEW.recipients) = 'array' THEN
        FOR recipient IN SELECT value FROM jsonb_array_elements_text(NEW.recipients)
        LOOP
            PERFORM pg_notify(
                'notification_' || recipient,
                json_build_object(
                    'id', NEW.id,
                    'workspace_id', NEW.workspace_id,
                    'type', NEW.type,
                    'channel', NEW.channel,
                    'title', NEW.title,
                    'message', NEW.message,
                    'priority', NEW.priority,
                    'status', NEW.status,
                    'created_at', NEW.created_at
                )::text
            );
        END LOOP;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for new notifications
DROP TRIGGER IF EXISTS notification_realtime_trigger ON notifications;
CREATE TRIGGER notification_realtime_trigger
    AFTER INSERT ON notifications
    FOR EACH ROW
    EXECUTE FUNCTION send_realtime_notification();

-- Function to handle notification status updates
CREATE OR REPLACE FUNCTION update_notification_status()
RETURNS TRIGGER AS $$
BEGIN
    -- Send status update to relevant recipients
    IF jsonb_typeof(OLD.recipients) = 'array' THEN
        FOR recipient IN SELECT value FROM jsonb_array_elements_text(OLD.recipients)
        LOOP
            PERFORM pg_notify(
                'notification_status_' || recipient,
                json_build_object(
                    'id', OLD.id,
                    'workspace_id', OLD.workspace_id,
                    'old_status', OLD.status,
                    'new_status', NEW.status,
                    'updated_at', NEW.updated_at
                )::text
            );
        END LOOP;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for notification status updates
DROP TRIGGER IF EXISTS notification_status_trigger ON notifications;
CREATE TRIGGER notification_status_trigger
    AFTER UPDATE ON notifications
    FOR EACH ROW
    WHEN (OLD.status IS DISTINCT FROM NEW.status)
    EXECUTE FUNCTION update_notification_status();

-- Function to handle read status updates
CREATE OR REPLACE FUNCTION handle_notification_read()
RETURNS TRIGGER AS $$
BEGIN
    -- Send read status update to specific user
    IF jsonb_typeof(NEW.recipients) = 'array' THEN
        FOR recipient IN SELECT value FROM jsonb_array_elements_text(NEW.recipients)
        LOOP
            PERFORM pg_notify(
                'notification_read_' || recipient,
                json_build_object(
                    'id', NEW.id,
                    'workspace_id', NEW.workspace_id,
                    'read', NEW.read,
                    'read_at', NEW.read_at
                )::text
            );
        END LOOP;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for read status updates
DROP TRIGGER IF EXISTS notification_read_trigger ON notifications;
CREATE TRIGGER notification_read_trigger
    AFTER UPDATE ON notifications
    FOR EACH ROW
    WHEN (OLD.read IS DISTINCT FROM NEW.read)
    EXECUTE FUNCTION handle_notification_read();

-- Function to create notification delivery logs
CREATE OR REPLACE FUNCTION log_notification_delivery()
RETURNS TRIGGER AS $$
BEGIN
    -- Create delivery log entries for each recipient and channel
    IF jsonb_typeof(NEW.recipients) = 'array' AND jsonb_typeof(NEW.delivery_results) = 'object' THEN
        -- Get channels from delivery results
        FOR channel_rec IN SELECT key FROM jsonb_each_text(NEW.delivery_results)
        LOOP
            -- Get delivery result for this channel
            delivery_result := NEW.delivery_results -> channel_rec.key;

            -- Create log entry for each recipient
            FOR recipient IN SELECT value FROM jsonb_array_elements_text(NEW.recipients)
            LOOP
                INSERT INTO notification_delivery_logs (
                    notification_id,
                    recipient,
                    channel,
                    status,
                    sent_at,
                    metadata
                ) VALUES (
                    NEW.id,
                    recipient,
                    channel_rec.key,
                    CASE
                        WHEN (delivery_result ->> 'sent_count')::int > 0 THEN 'sent'
                        ELSE 'failed'
                    END,
                    NEW.sent_at,
                    json_build_object(
                        'delivery_result', delivery_result,
                        'workspace_id', NEW.workspace_id
                    )
                );
            END LOOP;
        END LOOP;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for delivery logging
DROP TRIGGER IF EXISTS notification_delivery_log_trigger ON notifications;
CREATE TRIGGER notification_delivery_log_trigger
    AFTER INSERT ON notifications
    FOR EACH ROW
    WHEN (NEW.status = 'sent')
    EXECUTE FUNCTION log_notification_delivery();

-- Function to update template usage count
CREATE OR REPLACE FUNCTION update_template_usage()
RETURNS TRIGGER AS $$
BEGIN
    -- Update template usage count if template_id is provided
    IF NEW.template_id IS NOT NULL THEN
        UPDATE notification_templates
        SET usage_count = usage_count + 1,
            updated_at = NOW()
        WHERE id = NEW.template_id::uuid;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for template usage tracking
DROP TRIGGER IF EXISTS template_usage_trigger ON notifications;
CREATE TRIGGER template_usage_trigger
    AFTER INSERT ON notifications
    FOR EACH ROW
    WHEN (NEW.template_id IS NOT NULL)
    EXECUTE FUNCTION update_template_usage();

-- Function to handle notification preferences changes
CREATE OR REPLACE FUNCTION broadcast_preference_changes()
RETURNS TRIGGER AS $$
BEGIN
    -- Broadcast preference changes to user's active connections
    PERFORM pg_notify(
        'preferences_updated_' || NEW.user_id,
        json_build_object(
            'user_id', NEW.user_id,
            'workspace_id', NEW.workspace_id,
            'updated_at', NEW.updated_at,
            'preferences', json_build_object(
                'email_notifications', NEW.email_notifications,
                'sms_notifications', NEW.sms_notifications,
                'push_notifications', NEW.push_notifications,
                'in_app_notifications', NEW.in_app_notifications,
                'business_hours_only', NEW.business_hours_only,
                'quiet_hours_enabled', NEW.quiet_hours_enabled,
                'quiet_hours_start', NEW.quiet_hours_start,
                'quiet_hours_end', NEW.quiet_hours_end,
                'timezone', NEW.timezone,
                'notification_types', NEW.notification_types
            )
        )::text
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for preference changes
DROP TRIGGER IF EXISTS preference_change_trigger ON notification_preferences;
CREATE TRIGGER preference_change_trigger
    AFTER UPDATE ON notification_preferences
    FOR EACH ROW
    EXECUTE FUNCTION broadcast_preference_changes();

-- Views for notification analytics and monitoring
CREATE OR REPLACE VIEW notification_dashboard AS
SELECT
    n.workspace_id,
    COUNT(*) as total_notifications,
    COUNT(CASE WHEN n.status = 'delivered' THEN 1 END) as delivered_count,
    COUNT(CASE WHEN n.status = 'failed' THEN 1 END) as failed_count,
    COUNT(CASE WHEN n.read = TRUE THEN 1 END) as read_count,
    COUNT(CASE WHEN n.priority = 'urgent' THEN 1 END) as urgent_count,
    COUNT(CASE WHEN n.priority = 'high' THEN 1 END) as high_priority_count,
    AVG(CASE WHEN n.sent_at IS NOT NULL AND n.created_at IS NOT NULL
        THEN EXTRACT(EPOCH FROM (n.sent_at - n.created_at)) END) as avg_send_time_seconds,
    DATE_TRUNC('hour', n.created_at) as hour_bucket
FROM notifications n
WHERE n.created_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY n.workspace_id, DATE_TRUNC('hour', n.created_at)
ORDER BY hour_bucket DESC;

CREATE OR REPLACE VIEW user_notification_summary AS
SELECT
    p.workspace_id,
    p.user_id,
    p.email_notifications,
    p.sms_notifications,
    p.push_notifications,
    p.in_app_notifications,
    p.business_hours_only,
    p.quiet_hours_enabled,
    COUNT(CASE WHEN n.created_at >= CURRENT_DATE AND n.read = FALSE THEN 1 END) as unread_today,
    COUNT(CASE WHEN n.created_at >= CURRENT_DATE - INTERVAL '7 days' AND n.read = FALSE THEN 1 END) as unread_week,
    COUNT(CASE WHEN n.created_at >= CURRENT_DATE - INTERVAL '30 days' THEN 1 END) as total_month,
    COUNT(CASE WHEN n.created_at >= CURRENT_DATE - INTERVAL '30 days' AND n.status = 'delivered' THEN 1 END) as delivered_month
FROM notification_preferences p
LEFT JOIN notifications n ON p.workspace_id = n.workspace_id
    AND jsonb_array_length(n.recipients) > 0
    AND n.recipients @> jsonb_build_array(p.user_id::text)
GROUP BY p.workspace_id, p.user_id,
    p.email_notifications, p.sms_notifications, p.push_notifications,
    p.in_app_notifications, p.business_hours_only, p.quiet_hours_enabled;

-- Function to clean up old notifications (for maintenance)
CREATE OR REPLACE FUNCTION cleanup_old_notifications(days_to_keep INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Delete notifications older than specified days
    DELETE FROM notifications
    WHERE created_at < CURRENT_DATE - INTERVAL '1 day' * days_to_keep
        AND status IN ('delivered', 'failed')
        AND read = TRUE;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    -- Also clean up old delivery logs
    DELETE FROM notification_delivery_logs
    WHERE created_at < CURRENT_DATE - INTERVAL '1 day' * days_to_keep;

    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get notification statistics for a workspace
CREATE OR REPLACE FUNCTION get_workspace_notification_stats(workspace_uuid UUID, days_back INTEGER DEFAULT 30)
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'period', days_back || ' days',
        'total_notifications', COUNT(*),
        'delivered', COUNT(CASE WHEN status = 'delivered' THEN 1 END),
        'failed', COUNT(CASE WHEN status = 'failed' THEN 1 END),
        'pending', COUNT(CASE WHEN status = 'pending' THEN 1 END),
        'read', COUNT(CASE WHEN read = TRUE THEN 1 END),
        'unread', COUNT(CASE WHEN read = FALSE THEN 1 END),
        'urgent', COUNT(CASE WHEN priority = 'urgent' THEN 1 END),
        'high_priority', COUNT(CASE WHEN priority = 'high' THEN 1 END),
        'by_channel', (
            SELECT json_object_agg(channel, count)
            FROM (
                SELECT channel, COUNT(*) as count
                FROM notifications
                WHERE workspace_id = workspace_uuid
                    AND created_at >= CURRENT_DATE - INTERVAL '1 day' * days_back
                GROUP BY channel
            ) channel_stats
        ),
        'by_type', (
            SELECT json_object_agg(type, count)
            FROM (
                SELECT type, COUNT(*) as count
                FROM notifications
                WHERE workspace_id = workspace_uuid
                    AND created_at >= CURRENT_DATE - INTERVAL '1 day' * days_back
                GROUP BY type
            ) type_stats
        ),
        'avg_delivery_time', AVG(
            CASE WHEN sent_at IS NOT NULL AND created_at IS NOT NULL
                THEN EXTRACT(EPOCH FROM (sent_at - created_at))
            END
        )
    ) INTO result
    FROM notifications
    WHERE workspace_id = workspace_uuid
        AND created_at >= CURRENT_DATE - INTERVAL '1 day' * days_back;

    RETURN COALESCE(result, '{}'::json);
END;
$$ LANGUAGE plpgsql;
