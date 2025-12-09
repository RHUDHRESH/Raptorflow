-- =====================================================
-- MIGRATION 024: Drop Duplicate Indexes
-- =====================================================
-- Migration 023 created duplicate indexes with idx_* prefix
-- The schema already had indexes with *_idx suffix naming
-- Dropping the duplicates to fix WARN: duplicate_index linter errors

-- Activity Events partitions - drop duplicates
DROP INDEX IF EXISTS idx_activity_events_2025_q1_organization_id;
DROP INDEX IF EXISTS idx_activity_events_2025_q2_organization_id;
DROP INDEX IF EXISTS idx_activity_events_default_organization_id;

-- Audit Logs partitions - drop duplicates
DROP INDEX IF EXISTS idx_audit_logs_2025_q1_user_id;
DROP INDEX IF EXISTS idx_audit_logs_2025_q2_user_id;
DROP INDEX IF EXISTS idx_audit_logs_2025_q3_user_id;
DROP INDEX IF EXISTS idx_audit_logs_2025_q4_user_id;
DROP INDEX IF EXISTS idx_audit_logs_default_user_id;

-- Job Executions partitions - drop duplicates
DROP INDEX IF EXISTS idx_job_executions_2025_q1_job_id;
DROP INDEX IF EXISTS idx_job_executions_default_job_id;

-- Metrics partitions - drop duplicates
DROP INDEX IF EXISTS idx_metrics_2025_q1_metric_id;
DROP INDEX IF EXISTS idx_metrics_2025_q2_metric_id;
DROP INDEX IF EXISTS idx_metrics_default_metric_id;
