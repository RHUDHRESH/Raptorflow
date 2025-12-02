-- Migration 017: Create Alerts & Notifications System
-- Phase: Week 2 - Codex Schema Creation
-- Purpose: Add real-time alerts, notifications, and event tracking
-- New Tables: 2 (system_alerts, user_notifications)
-- Scope: Expand from 57 → 59 tables
-- This completes Week 2 schema expansion (43 → 59 tables)

-- ============================================================================
-- TABLE 1: system_alerts
-- Purpose: System-level alerts triggered by agents or conditions
-- Workspace isolation: workspace_id + RLS policy
-- ============================================================================
CREATE TABLE IF NOT EXISTS system_alerts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

  -- Alert identification
  alert_type text NOT NULL, -- "performance", "error", "milestone", "anomaly", "action_required", "opportunity"
  severity_level text NOT NULL DEFAULT 'info', -- critical, high, medium, low, info
  status text NOT NULL DEFAULT 'active', -- active, acknowledged, resolved, dismissed

  -- Content
  title text NOT NULL,
  description text,
  message text,
  action_url text, -- Link to take action

  -- Source
  triggered_by_agent_id uuid REFERENCES agent_registry(id) ON DELETE SET NULL,
  triggered_by_signal_id uuid REFERENCES intelligence_signals(id) ON DELETE SET NULL,
  triggered_by_event text, -- "campaign_milestone", "competitor_activity", "performance_drop", etc.

  -- Context
  related_campaign_id uuid REFERENCES campaigns(id) ON DELETE CASCADE,
  related_cohort_id uuid REFERENCES cohorts(id) ON DELETE CASCADE,
  related_move_id uuid REFERENCES moves(id) ON DELETE CASCADE,

  -- Data
  data_points jsonb, -- relevant metrics/data triggering the alert
  recommended_actions text[],

  -- Timeline
  created_at timestamp with time zone DEFAULT now(),
  triggered_at timestamp with time zone,
  acknowledged_at timestamp with time zone,
  resolved_at timestamp with time zone,
  expiry_date timestamp with time zone,

  -- Acknowledgement
  acknowledged_by uuid REFERENCES auth.users(id) ON DELETE SET NULL,
  action_taken text,

  -- Metadata
  created_by uuid NOT NULL REFERENCES auth.users(id) ON DELETE SET NULL,
  updated_at timestamp with time zone DEFAULT now(),

  CONSTRAINT system_alerts_workspace_check CHECK (workspace_id IS NOT NULL),
  CONSTRAINT system_alerts_type_check CHECK (alert_type IN ('performance', 'error', 'milestone', 'anomaly', 'action_required', 'opportunity')),
  CONSTRAINT system_alerts_severity_check CHECK (severity_level IN ('critical', 'high', 'medium', 'low', 'info')),
  CONSTRAINT system_alerts_status_check CHECK (status IN ('active', 'acknowledged', 'resolved', 'dismissed'))
);

CREATE INDEX idx_system_alerts_workspace ON system_alerts(workspace_id);
CREATE INDEX idx_system_alerts_status ON system_alerts(workspace_id, status);
CREATE INDEX idx_system_alerts_severity ON system_alerts(workspace_id, severity_level);
CREATE INDEX idx_system_alerts_type ON system_alerts(workspace_id, alert_type);
CREATE INDEX idx_system_alerts_created ON system_alerts(workspace_id, created_at DESC);
CREATE INDEX idx_system_alerts_campaign ON system_alerts(related_campaign_id);

ALTER TABLE system_alerts ENABLE ROW LEVEL SECURITY;

CREATE POLICY system_alerts_workspace_isolation ON system_alerts
  USING (workspace_id = current_setting('app.current_workspace_id')::uuid)
  WITH CHECK (workspace_id = current_setting('app.current_workspace_id')::uuid);

-- ============================================================================
-- TABLE 2: user_notifications
-- Purpose: Individual notifications sent to users
-- Workspace isolation: workspace_id + RLS policy
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_notifications (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  -- Notification content
  notification_type text NOT NULL, -- "alert", "achievement", "message", "reminder", "summary"
  title text NOT NULL,
  message text NOT NULL,
  description text,

  -- Related context
  related_alert_id uuid REFERENCES system_alerts(id) ON DELETE CASCADE,
  related_achievement_id uuid REFERENCES achievements(id) ON DELETE SET NULL,
  related_campaign_id uuid REFERENCES campaigns(id) ON DELETE CASCADE,

  -- Delivery
  channel text NOT NULL DEFAULT 'in_app', -- in_app, email, slack, sms, push
  is_read boolean DEFAULT false,
  read_at timestamp with time zone,
  delivery_status text DEFAULT 'pending', -- pending, delivered, failed, bounced
  delivery_method text, -- for email/sms, the actual recipient

  -- Action
  action_url text,
  action_label text,
  call_to_action text,

  -- Priority
  priority_level text DEFAULT 'normal', -- low, normal, high, urgent
  expires_at timestamp with time zone,

  -- Metadata
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),

  CONSTRAINT user_notifications_workspace_check CHECK (workspace_id IS NOT NULL),
  CONSTRAINT user_notifications_type_check CHECK (notification_type IN ('alert', 'achievement', 'message', 'reminder', 'summary')),
  CONSTRAINT user_notifications_channel_check CHECK (channel IN ('in_app', 'email', 'slack', 'sms', 'push')),
  CONSTRAINT user_notifications_priority_check CHECK (priority_level IN ('low', 'normal', 'high', 'urgent'))
);

CREATE INDEX idx_user_notifications_workspace ON user_notifications(workspace_id);
CREATE INDEX idx_user_notifications_user ON user_notifications(user_id);
CREATE INDEX idx_user_notifications_read ON user_notifications(user_id, is_read);
CREATE INDEX idx_user_notifications_type ON user_notifications(workspace_id, notification_type);
CREATE INDEX idx_user_notifications_created ON user_notifications(user_id, created_at DESC);
CREATE INDEX idx_user_notifications_channel ON user_notifications(workspace_id, channel);

ALTER TABLE user_notifications ENABLE ROW LEVEL SECURITY;

CREATE POLICY user_notifications_workspace_isolation ON user_notifications
  USING (workspace_id = current_setting('app.current_workspace_id')::uuid)
  WITH CHECK (workspace_id = current_setting('app.current_workspace_id')::uuid);

CREATE POLICY user_notifications_own_access ON user_notifications
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to create and send alert
CREATE OR REPLACE FUNCTION create_system_alert(
  p_workspace_id uuid,
  p_alert_type text,
  p_severity text,
  p_title text,
  p_description text,
  p_agent_id uuid DEFAULT NULL,
  p_campaign_id uuid DEFAULT NULL,
  p_data_points jsonb DEFAULT NULL
)
RETURNS uuid AS $$
DECLARE
  v_alert_id uuid;
BEGIN
  -- Create the alert
  INSERT INTO system_alerts (
    workspace_id, alert_type, severity_level, title, description,
    triggered_by_agent_id, related_campaign_id, data_points, created_by
  ) VALUES (
    p_workspace_id, p_alert_type, p_severity, p_title, p_description,
    p_agent_id, p_campaign_id, p_data_points, auth.uid()
  )
  RETURNING id INTO v_alert_id;

  RETURN v_alert_id;
END;
$$ LANGUAGE plpgsql;

-- Function to send notification to user
CREATE OR REPLACE FUNCTION send_user_notification(
  p_workspace_id uuid,
  p_user_id uuid,
  p_notification_type text,
  p_title text,
  p_message text,
  p_channel text DEFAULT 'in_app',
  p_priority text DEFAULT 'normal',
  p_action_url text DEFAULT NULL,
  p_alert_id uuid DEFAULT NULL
)
RETURNS uuid AS $$
DECLARE
  v_notification_id uuid;
BEGIN
  -- Create notification
  INSERT INTO user_notifications (
    workspace_id, user_id, notification_type, title, message,
    channel, priority_level, action_url, related_alert_id
  ) VALUES (
    p_workspace_id, p_user_id, p_notification_type, p_title, p_message,
    p_channel, p_priority, p_action_url, p_alert_id
  )
  RETURNING id INTO v_notification_id;

  RETURN v_notification_id;
END;
$$ LANGUAGE plpgsql;

-- Function to acknowledge alert
CREATE OR REPLACE FUNCTION acknowledge_alert(
  p_alert_id uuid,
  p_user_id uuid
)
RETURNS void AS $$
BEGIN
  UPDATE system_alerts
  SET
    status = 'acknowledged',
    acknowledged_by = p_user_id,
    acknowledged_at = now(),
    updated_at = now()
  WHERE id = p_alert_id;
END;
$$ LANGUAGE plpgsql;

-- Function to mark notification as read
CREATE OR REPLACE FUNCTION mark_notification_as_read(
  p_notification_id uuid
)
RETURNS void AS $$
BEGIN
  UPDATE user_notifications
  SET
    is_read = true,
    read_at = now(),
    updated_at = now()
  WHERE id = p_notification_id;
END;
$$ LANGUAGE plpgsql;

-- Function to get active unread notifications for user
CREATE OR REPLACE FUNCTION get_user_unread_notifications(p_user_id uuid)
RETURNS TABLE (
  id uuid,
  type text,
  title text,
  message text,
  priority text,
  created_at timestamp with time zone
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    un.id,
    un.notification_type,
    un.title,
    un.message,
    un.priority_level,
    un.created_at
  FROM user_notifications un
  WHERE un.user_id = p_user_id
  AND un.is_read = false
  AND (un.expires_at IS NULL OR un.expires_at > now())
  ORDER BY un.priority_level DESC, un.created_at DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to get critical alerts for workspace
CREATE OR REPLACE FUNCTION get_critical_alerts(p_workspace_id uuid)
RETURNS TABLE (
  id uuid,
  title text,
  description text,
  alert_type text,
  created_at timestamp with time zone
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    sa.id,
    sa.title,
    sa.description,
    sa.alert_type,
    sa.created_at
  FROM system_alerts sa
  WHERE sa.workspace_id = p_workspace_id
  AND sa.severity_level IN ('critical', 'high')
  AND sa.status = 'active'
  AND (sa.expiry_date IS NULL OR sa.expiry_date > now())
  ORDER BY sa.created_at DESC;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- MIGRATION VERIFICATION BLOCK
-- ============================================================================

/*
POST-MIGRATION VERIFICATION:

1. Table creation:
   SELECT COUNT(*) FROM information_schema.tables
   WHERE table_schema = 'public' AND table_name IN
   ('system_alerts', 'user_notifications');
   -- Expected: 2

2. RLS policies:
   SELECT COUNT(*) FROM pg_policies
   WHERE tablename IN ('system_alerts', 'user_notifications');
   -- Expected: 4 (system_alerts: 1, user_notifications: 2)

3. Indexes created:
   SELECT COUNT(*) FROM pg_indexes
   WHERE tablename IN ('system_alerts', 'user_notifications')
   AND schemaname = 'public';
   -- Expected: 12+ indexes

4. Functions created:
   SELECT COUNT(*) FROM pg_proc
   WHERE proname IN (
     'create_system_alert',
     'send_user_notification',
     'acknowledge_alert',
     'mark_notification_as_read',
     'get_user_unread_notifications',
     'get_critical_alerts'
   )
   AND pronamespace = 'public'::regnamespace;
   -- Expected: 6

5. Foreign key constraints:
   SELECT COUNT(*) FROM information_schema.table_constraints
   WHERE constraint_type = 'FOREIGN KEY'
   AND table_name IN ('system_alerts', 'user_notifications');
   -- Expected: 10+ FKs

6. FINAL TABLE COUNT CHECK:
   SELECT COUNT(*) FROM information_schema.tables
   WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
   -- Expected: 59 (43 from Week 1 + 16 new from Week 2)

   NOTE: table_name filtering to verify:
   - 5 tables from migration 013 (positioning, message_architecture, campaigns, campaign_quests, campaign_cohorts)
   - 3 tables from migration 014 (achievements, user_achievements, user_stats)
   - 4 tables from migration 015 (agent_registry, agent_capabilities, agent_assignments, agent_performance)
   - 2 tables from migration 016 (intelligence_signals, market_insights)
   - 2 tables from migration 017 (system_alerts, user_notifications)
   = Total 16 new tables (but only 59 shown because agent_registry duplicates - CHECK THIS)
*/

-- ============================================================================
-- FINAL SCHEMA SUMMARY FOR WEEK 2
-- ============================================================================

/*
WEEK 2 SCHEMA EXPANSION SUMMARY:

Start State (after Week 1): 43 tables
Schema added in Week 2:
  - Migration 013: 5 tables (positioning, message_architecture, campaigns, campaign_quests, campaign_cohorts)
  - Migration 014: 3 tables (achievements, user_achievements, user_stats)
  - Migration 015: 4 tables (agent_registry, agent_capabilities, agent_assignments, agent_performance)
  - Migration 016: 2 tables (intelligence_signals, market_insights)
  - Migration 017: 2 tables (system_alerts, user_notifications)

Expected End State: 59 tables

New Codex Systems Online:
  ✓ Positioning & Campaign Management System
  ✓ Gamification & Achievements System
  ✓ Agent Registry & Performance Tracking
  ✓ Market Intelligence & Signal System
  ✓ Alerts & Notifications System

Foreign Keys: 40+ new constraints
RLS Policies: 15+ new policies
Indexes: 60+ new indexes
Functions: 20+ helper functions
Triggers: Multiple update triggers

This completes the Codex Schema Foundation for Week 2.
*/
