-- =====================================================
-- MIGRATION 002: Enums (Status Models)
-- =====================================================

CREATE TYPE org_role AS ENUM ('owner', 'admin', 'editor', 'viewer', 'billing');
CREATE TYPE plan_type AS ENUM ('free', 'starter', 'growth', 'enterprise');
CREATE TYPE subscription_status AS ENUM ('trialing', 'active', 'past_due', 'paused', 'cancelled', 'expired');
CREATE TYPE payment_status AS ENUM ('initiated', 'pending', 'processing', 'success', 'failed', 'refunded');
CREATE TYPE payment_method_type AS ENUM ('upi', 'card', 'netbanking', 'wallet', 'upi_autopay', 'card_recurring');
CREATE TYPE mandate_status AS ENUM ('pending_authorization', 'active', 'paused', 'revoked', 'expired', 'failed');
CREATE TYPE invoice_status AS ENUM ('draft', 'pending', 'paid', 'overdue', 'cancelled', 'refunded');
CREATE TYPE campaign_status AS ENUM ('draft', 'planned', 'active', 'paused', 'completed', 'cancelled');
CREATE TYPE job_status AS ENUM ('pending', 'running', 'completed', 'failed', 'cancelled', 'timeout');
CREATE TYPE audit_action AS ENUM ('create', 'read', 'update', 'delete', 'login', 'logout', 'export');
