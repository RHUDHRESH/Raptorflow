-- =================================================================
-- PERFORMANCE FIXES: Remove Unused Indexes
-- Migration: 136_remove_unused_indexes.sql
-- Priority: LOW - Removes unused indexes to improve write performance
-- =================================================================

-- Remove unused indexes that have never been used
-- This improves write performance and reduces storage

-- Drop unused indexes from payments table
DROP INDEX CONCURRENTLY IF EXISTS idx_payments_user_id;

-- Drop unused indexes from email_logs table
DROP INDEX CONCURRENTLY IF EXISTS idx_email_logs_user_id;

-- Drop unused indexes from users table
DROP INDEX CONCURRENTLY IF EXISTS idx_users_email;
DROP INDEX CONCURRENTLY IF EXISTS idx_users_onboarding_status;
DROP INDEX CONCURRENTLY IF EXISTS idx_users_role;
DROP INDEX CONCURRENTLY IF EXISTS idx_users_is_active;
DROP INDEX CONCURRENTLY IF EXISTS idx_users_created_at;

-- Drop unused indexes from workspaces table
DROP INDEX CONCURRENTLY IF EXISTS idx_workspaces_user_id;
DROP INDEX CONCURRENTLY IF EXISTS idx_workspaces_slug;
DROP INDEX CONCURRENTLY IF EXISTS idx_workspaces_status;

-- Drop unused indexes from subscriptions table
DROP INDEX CONCURRENTLY IF EXISTS idx_subscriptions_user_id;
DROP INDEX CONCURRENTLY IF EXISTS idx_subscriptions_status;
DROP INDEX CONCURRENTLY IF EXISTS idx_subscriptions_plan_id;
DROP INDEX CONCURRENTLY IF EXISTS idx_subscriptions_current_period_end;

-- Drop unused indexes from payment_transactions table
DROP INDEX CONCURRENTLY IF EXISTS idx_payment_transactions_user_id;
DROP INDEX CONCURRENTLY IF EXISTS idx_payment_transactions_transaction_id;
DROP INDEX CONCURRENTLY IF EXISTS idx_payment_transactions_status;
DROP INDEX CONCURRENTLY IF EXISTS idx_payment_transactions_created_at;

-- Drop unused indexes from user_sessions table
DROP INDEX CONCURRENTLY IF EXISTS idx_user_sessions_user_id;
DROP INDEX CONCURRENTLY IF EXISTS idx_user_sessions_session_token;
DROP INDEX CONCURRENTLY IF EXISTS idx_user_sessions_is_active;
DROP INDEX CONCURRENTLY IF EXISTS idx_user_sessions_expires_at;

-- Drop unused indexes from audit_logs table
DROP INDEX CONCURRENTLY IF EXISTS idx_audit_logs_actor_id;
DROP INDEX CONCURRENTLY IF EXISTS idx_audit_logs_action;
DROP INDEX CONCURRENTLY IF EXISTS idx_audit_logs_created_at;
DROP INDEX CONCURRENTLY IF EXISTS idx_audit_logs_target_id;

-- Drop unused indexes from admin_actions table
DROP INDEX CONCURRENTLY IF EXISTS idx_admin_actions_admin_id;
DROP INDEX CONCURRENTLY IF EXISTS idx_admin_actions_target_user_id;
DROP INDEX CONCURRENTLY IF EXISTS idx_admin_actions_created_at;

-- Drop unused indexes from security_events table
DROP INDEX CONCURRENTLY IF EXISTS idx_security_events_user_id;
DROP INDEX CONCURRENTLY IF EXISTS idx_security_events_event_type;
DROP INDEX CONCURRENTLY IF EXISTS idx_security_events_created_at;

-- Drop unused indexes from profiles table
DROP INDEX CONCURRENTLY IF EXISTS idx_profiles_email;
DROP INDEX CONCURRENTLY IF EXISTS idx_profiles_workspace;
DROP INDEX CONCURRENTLY IF EXISTS idx_profiles_role;
DROP INDEX CONCURRENTLY IF EXISTS idx_profiles_subscription;

-- Drop unused indexes from business_context_manifests table
DROP INDEX CONCURRENTLY IF EXISTS idx_bcm_workspace;
DROP INDEX CONCURRENTLY IF EXISTS idx_bcm_version;
DROP INDEX CONCURRENTLY IF EXISTS idx_bcm_checksum;

-- Drop unused indexes from foundations table
DROP INDEX CONCURRENTLY IF EXISTS idx_foundations_workspace;
DROP INDEX CONCURRENTLY IF EXISTS idx_foundations_status;
DROP INDEX CONCURRENTLY IF EXISTS idx_foundations_embedding;

-- Drop unused indexes from icp_profiles table
DROP INDEX CONCURRENTLY IF EXISTS idx_icp_workspace;
DROP INDEX CONCURRENTLY IF EXISTS idx_icp_name;

-- Drop unused indexes from ICP related tables
DROP INDEX CONCURRENTLY IF EXISTS idx_icp_firmographics_profile;
DROP INDEX CONCURRENTLY IF EXISTS idx_icp_pain_profile;
DROP INDEX CONCURRENTLY IF EXISTS idx_icp_psycholinguistics_profile;
DROP INDEX CONCURRENTLY IF EXISTS idx_icp_disqualifiers_profile;
