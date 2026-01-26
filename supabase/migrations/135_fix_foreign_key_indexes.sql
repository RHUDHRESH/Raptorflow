-- =================================================================
-- PERFORMANCE FIXES: Missing Foreign Key Indexes
-- Migration: 135_fix_foreign_key_indexes.sql
-- Priority: LOW - Adds missing indexes for foreign key constraints
-- =================================================================

-- Add missing indexes for foreign key constraints
-- These improve join performance and prevent locking issues

-- Index for payment_transactions.plan_id foreign key
CREATE INDEX CONCURRENTLY IF NOT EXISTS
idx_payment_transactions_plan_id_fkey
ON public.payment_transactions(plan_id);

-- Index for payment_transactions.subscription_id foreign key
CREATE INDEX CONCURRENTLY IF NOT EXISTS
idx_payment_transactions_subscription_id_fkey
ON public.payment_transactions(subscription_id);

-- Index for users.banned_by foreign key
CREATE INDEX CONCURRENTLY IF NOT EXISTS
idx_users_banned_by_fkey
ON public.users(banned_by);

-- Create composite indexes for common query patterns
-- These will help with the RLS policy performance

-- Composite index for user_sessions (user_id, is_active, expires_at)
CREATE INDEX CONCURRENTLY IF NOT EXISTS
idx_user_sessions_user_active_expires
ON public.user_sessions(user_id, is_active, expires_at)
WHERE is_active = true;

-- Composite index for payment_transactions (user_id, status, created_at)
CREATE INDEX CONCURRENTLY IF NOT EXISTS
idx_payment_transactions_user_status_created
ON public.payment_transactions(user_id, status, created_at);

-- Composite index for subscriptions (user_id, status, current_period_end)
CREATE INDEX CONCURRENTLY IF NOT EXISTS
idx_subscriptions_user_status_period
ON public.subscriptions(user_id, status, current_period_end)
WHERE status IN ('active', 'trialing');

-- Composite index for audit_logs (user_id, action, created_at)
CREATE INDEX CONCURRENTLY IF NOT EXISTS
idx_audit_logs_user_action_created
ON public.audit_logs(user_id, action, created_at);

-- Composite index for security_events (user_id, event_type, created_at)
CREATE INDEX CONCURRENTLY IF NOT EXISTS
idx_security_events_user_type_created
ON public.security_events(user_id, event_type, created_at);

-- Composite index for admin_actions (admin_id, target_user_id, created_at)
CREATE INDEX CONCURRENTLY IF NOT EXISTS
idx_admin_actions_admin_target_created
ON public.admin_actions(admin_id, target_user_id, created_at);

-- Composite index for workspaces (owner_id, status, created_at)
CREATE INDEX CONCURRENTLY IF NOT EXISTS
idx_workspaces_owner_status_created
ON public.workspaces(owner_id, status, created_at)
WHERE status = 'active';

-- Composite index for icp_profiles (workspace_id, created_at)
CREATE INDEX CONCURRENTLY IF NOT EXISTS
idx_icp_profiles_workspace_created
ON public.icp_profiles(workspace_id, created_at);

-- Composite index for foundations (workspace_id, status, created_at)
CREATE INDEX CONCURRENTLY IF NOT EXISTS
idx_foundations_workspace_status_created
ON public.foundations(workspace_id, status, created_at)
WHERE status = 'active';

-- Composite index for business_context_manifests (workspace_id, version, created_at)
CREATE INDEX CONCURRENTLY IF NOT EXISTS
idx_bcm_workspace_version_created
ON public.business_context_manifests(workspace_id, version, created_at);
