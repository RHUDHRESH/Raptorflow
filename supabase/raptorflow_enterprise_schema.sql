-- =====================================================
-- RAPTORFLOW ENTERPRISE DATABASE SCHEMA v2.0
-- Production-grade schema with 80+ tables
-- RBI-compliant payment handling, security, performance
-- =====================================================
-- TOTAL: ~11,000 lines | 80+ tables | 120+ indexes
-- =====================================================

-- ===========================================
-- SECTION 1: EXTENSIONS
-- ===========================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";        -- Fuzzy text search
CREATE EXTENSION IF NOT EXISTS "btree_gist";     -- For exclusion constraints
CREATE EXTENSION IF NOT EXISTS "citext";         -- Case-insensitive text

-- ===========================================
-- SECTION 2: CUSTOM DOMAINS & TYPES
-- ===========================================

-- Email domain with validation
CREATE DOMAIN email_address AS citext
  CHECK (VALUE ~ '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$');

-- Phone number domain (Indian format)
CREATE DOMAIN indian_phone AS VARCHAR(15)
  CHECK (VALUE ~ '^\+91[0-9]{10}$' OR VALUE ~ '^[0-9]{10}$');

-- Currency amount in paise (positive)
CREATE DOMAIN amount_paise AS BIGINT
  CHECK (VALUE >= 0);

-- Percentage (0-100)
CREATE DOMAIN percentage AS DECIMAL(5,2)
  CHECK (VALUE >= 0 AND VALUE <= 100);

-- URL domain
CREATE DOMAIN url_string AS TEXT
  CHECK (VALUE ~ '^https?://');

-- ===========================================
-- SECTION 3: ENUMS (25+ types)
-- ===========================================

-- Barrier types (the 6 barriers in the funnel)
DO $$ BEGIN
  CREATE TYPE barrier_type AS ENUM (
    'OBSCURITY', 'RISK', 'INERTIA', 'FRICTION', 'CAPACITY', 'ATROPHY'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Protocol types
DO $$ BEGIN
  CREATE TYPE protocol_type AS ENUM (
    'A_AUTHORITY_BLITZ', 'B_TRUST_ANCHOR', 'C_COST_OF_INACTION',
    'D_HABIT_HARDCODE', 'E_ENTERPRISE_WEDGE', 'F_CHURN_INTERCEPT'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Goal types
DO $$ BEGIN
  CREATE TYPE goal_type AS ENUM ('velocity', 'efficiency', 'penetration');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Demand source types
DO $$ BEGIN
  CREATE TYPE demand_source_type AS ENUM ('capture', 'creation', 'expansion');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Persuasion axis types
DO $$ BEGIN
  CREATE TYPE persuasion_axis_type AS ENUM ('money', 'time', 'risk_image');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Campaign status
DO $$ BEGIN
  CREATE TYPE campaign_status AS ENUM (
    'draft', 'planned', 'active', 'paused', 'completed', 'cancelled'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Move status
DO $$ BEGIN
  CREATE TYPE move_status AS ENUM (
    'planned', 'generating_assets', 'ready', 'running', 'paused', 'completed', 'failed'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Asset status
DO $$ BEGIN
  CREATE TYPE asset_status AS ENUM (
    'draft', 'generating', 'needs_review', 'approved', 'deployed', 'archived'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- RAG status
DO $$ BEGIN
  CREATE TYPE rag_status AS ENUM ('green', 'amber', 'red', 'unknown');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Spike type
DO $$ BEGIN
  CREATE TYPE spike_type AS ENUM ('pipeline', 'efficiency', 'expansion');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Spike status
DO $$ BEGIN
  CREATE TYPE spike_status AS ENUM ('configuring', 'active', 'paused', 'completed', 'cancelled');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Guardrail action type
DO $$ BEGIN
  CREATE TYPE guardrail_action AS ENUM ('alert_only', 'pause_and_alert', 'auto_pause');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- NEW: Plan types
DO $$ BEGIN
  CREATE TYPE plan_type AS ENUM ('none', 'ascent', 'glide', 'soar');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- NEW: Subscription status
DO $$ BEGIN
  CREATE TYPE subscription_status AS ENUM (
    'trialing', 'active', 'past_due', 'paused', 'cancelled', 'expired'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- NEW: Payment status
DO $$ BEGIN
  CREATE TYPE payment_status AS ENUM (
    'initiated', 'pending', 'processing', 'success', 'failed', 'refunded', 'disputed'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- NEW: Payment method type
DO $$ BEGIN
  CREATE TYPE payment_method_type AS ENUM (
    'upi', 'card', 'netbanking', 'wallet', 'upi_autopay', 'card_recurring'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- NEW: Mandate status (RBI e-mandate)
DO $$ BEGIN
  CREATE TYPE mandate_status AS ENUM (
    'pending_authorization', 'active', 'paused', 'revoked', 'expired', 'failed'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- NEW: Invoice status
DO $$ BEGIN
  CREATE TYPE invoice_status AS ENUM (
    'draft', 'pending', 'paid', 'overdue', 'cancelled', 'refunded'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- NEW: Notification type
DO $$ BEGIN
  CREATE TYPE notification_type AS ENUM (
    'email', 'sms', 'push', 'in_app', 'webhook'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- NEW: Notification priority
DO $$ BEGIN
  CREATE TYPE notification_priority AS ENUM ('low', 'normal', 'high', 'urgent');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- NEW: Audit action type
DO $$ BEGIN
  CREATE TYPE audit_action AS ENUM (
    'create', 'read', 'update', 'delete', 'login', 'logout', 'export', 'import'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- NEW: Organization role
DO $$ BEGIN
  CREATE TYPE org_role AS ENUM ('owner', 'admin', 'member', 'viewer', 'billing');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- NEW: Webhook event type
DO $$ BEGIN
  CREATE TYPE webhook_event AS ENUM (
    'payment.success', 'payment.failed', 'subscription.created', 'subscription.cancelled',
    'subscription.renewed', 'campaign.started', 'campaign.completed', 'user.created'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- NEW: Feature flag status
DO $$ BEGIN
  CREATE TYPE feature_flag_status AS ENUM ('enabled', 'disabled', 'percentage', 'user_list');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ===========================================
-- SECTION 4: ORGANIZATIONS & MULTI-TENANCY
-- ===========================================

-- Organizations (company/team accounts)
CREATE TABLE IF NOT EXISTS public.organizations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Identity
  name VARCHAR(255) NOT NULL,
  slug VARCHAR(100) UNIQUE NOT NULL,
  domain VARCHAR(255),
  logo_url TEXT,
  
  -- Contact
  billing_email TEXT,
  support_email TEXT,
  phone VARCHAR(20),
  
  -- Address (for invoicing)
  address_line1 TEXT,
  address_line2 TEXT,
  city VARCHAR(100),
  state VARCHAR(100),
  postal_code VARCHAR(20),
  country VARCHAR(2) DEFAULT 'IN',
  
  -- Tax info (GST)
  gstin VARCHAR(15),
  pan VARCHAR(10),
  
  -- Settings
  settings JSONB DEFAULT '{}',
  metadata JSONB DEFAULT '{}',
  
  -- Plan (org-level)
  plan plan_type DEFAULT 'none',
  plan_seats INTEGER DEFAULT 1,
  
  -- Status
  is_active BOOLEAN DEFAULT true,
  is_verified BOOLEAN DEFAULT false,
  verified_at TIMESTAMPTZ,
  
  -- Soft delete
  deleted_at TIMESTAMPTZ,
  deleted_by UUID,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID
);

-- Organization members
CREATE TABLE IF NOT EXISTS public.organization_members (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- Role & permissions
  role org_role DEFAULT 'member',
  permissions JSONB DEFAULT '[]',
  
  -- Status
  is_active BOOLEAN DEFAULT true,
  joined_at TIMESTAMPTZ DEFAULT NOW(),
  invited_by UUID,
  
  -- Soft delete
  removed_at TIMESTAMPTZ,
  removed_by UUID,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT unique_org_member UNIQUE (organization_id, user_id)
);

-- Organization invites
CREATE TABLE IF NOT EXISTS public.organization_invites (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
  
  email TEXT NOT NULL,
  role org_role DEFAULT 'member',
  
  -- Token for invite link
  token VARCHAR(64) UNIQUE NOT NULL DEFAULT encode(gen_random_bytes(32), 'hex'),
  
  -- Status
  status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'expired', 'revoked')),
  
  expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '7 days'),
  accepted_at TIMESTAMPTZ,
  accepted_by UUID,
  
  invited_by UUID NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT unique_pending_invite UNIQUE (organization_id, email, status)
);

-- ===========================================
-- SECTION 5: USER PROFILES (Enhanced)
-- ===========================================

CREATE TABLE IF NOT EXISTS public.profiles (
  id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  
  -- Basic info
  email TEXT,
  full_name TEXT,
  display_name VARCHAR(100),
  avatar_url TEXT,
  bio TEXT,
  
  -- Contact
  phone VARCHAR(20),
  phone_verified BOOLEAN DEFAULT false,
  phone_verified_at TIMESTAMPTZ,
  
  -- Location
  timezone VARCHAR(50) DEFAULT 'Asia/Kolkata',
  locale VARCHAR(10) DEFAULT 'en-IN',
  country VARCHAR(2) DEFAULT 'IN',
  
  -- Organization (if part of one)
  organization_id UUID REFERENCES public.organizations(id) ON DELETE SET NULL,
  
  -- Plan & Subscription (individual)
  plan plan_type DEFAULT 'none',
  plan_status subscription_status DEFAULT 'expired',
  plan_started_at TIMESTAMPTZ,
  plan_expires_at TIMESTAMPTZ,
  plan_cancelled_at TIMESTAMPTZ,
  
  -- Onboarding
  onboarding_completed BOOLEAN DEFAULT FALSE,
  onboarding_completed_at TIMESTAMPTZ,
  onboarding_step INTEGER DEFAULT 0,
  
  -- Payment info
  payment_status VARCHAR(20) DEFAULT 'pending',
  last_payment_id TEXT,
  last_payment_amount BIGINT,
  last_payment_date TIMESTAMPTZ,
  
  -- PhonePe specific
  phonepe_merchant_user_id TEXT,
  preferred_payment_method payment_method_type,
  
  -- Security
  two_factor_enabled BOOLEAN DEFAULT false,
  two_factor_secret TEXT,
  last_login_at TIMESTAMPTZ,
  last_login_ip INET,
  failed_login_attempts INTEGER DEFAULT 0,
  locked_until TIMESTAMPTZ,
  
  -- Preferences
  preferences JSONB DEFAULT '{}',
  notification_preferences JSONB DEFAULT '{"email": true, "push": true, "sms": false}',
  
  -- Metadata
  metadata JSONB DEFAULT '{}',
  
  -- Soft delete
  deleted_at TIMESTAMPTZ,
  deleted_by UUID,
  deletion_reason TEXT,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- SECTION 6: SUBSCRIPTION MANAGEMENT (RBI Compliant)
-- ===========================================

-- Subscriptions table
CREATE TABLE IF NOT EXISTS public.subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Owner (user or org)
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
  
  -- Plan details
  plan plan_type NOT NULL,
  plan_name VARCHAR(100) NOT NULL,
  
  -- Pricing (in paise)
  amount_paise BIGINT NOT NULL,
  currency VARCHAR(3) DEFAULT 'INR',
  
  -- Billing cycle
  billing_cycle VARCHAR(20) DEFAULT 'monthly' CHECK (billing_cycle IN ('monthly', 'quarterly', 'yearly')),
  billing_anchor_day INTEGER DEFAULT 1 CHECK (billing_anchor_day BETWEEN 1 AND 28),
  
  -- RBI Autopay eligibility
  autopay_eligible BOOLEAN GENERATED ALWAYS AS (amount_paise <= 500000) STORED,
  autopay_enabled BOOLEAN DEFAULT false,
  mandate_id UUID,
  
  -- Dates
  current_period_start TIMESTAMPTZ NOT NULL,
  current_period_end TIMESTAMPTZ NOT NULL,
  trial_start TIMESTAMPTZ,
  trial_end TIMESTAMPTZ,
  cancelled_at TIMESTAMPTZ,
  ended_at TIMESTAMPTZ,
  
  -- Status
  status subscription_status DEFAULT 'active',
  cancel_at_period_end BOOLEAN DEFAULT false,
  cancellation_reason TEXT,
  
  -- Usage limits (based on plan)
  cohort_limit INTEGER NOT NULL,
  workspace_limit INTEGER NOT NULL,
  team_member_limit INTEGER NOT NULL,
  
  -- Metadata
  metadata JSONB DEFAULT '{}',
  
  -- Soft delete
  deleted_at TIMESTAMPTZ,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT subscription_owner CHECK (
    (user_id IS NOT NULL AND organization_id IS NULL) OR
    (user_id IS NULL AND organization_id IS NOT NULL)
  )
);

-- Subscription periods (billing history)
CREATE TABLE IF NOT EXISTS public.subscription_periods (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  subscription_id UUID NOT NULL REFERENCES public.subscriptions(id) ON DELETE CASCADE,
  
  period_number INTEGER NOT NULL,
  period_start TIMESTAMPTZ NOT NULL,
  period_end TIMESTAMPTZ NOT NULL,
  
  -- Billing
  amount_paise BIGINT NOT NULL,
  invoice_id UUID,
  payment_id UUID,
  
  -- Status
  status VARCHAR(20) DEFAULT 'upcoming' CHECK (status IN ('upcoming', 'current', 'past', 'skipped')),
  paid_at TIMESTAMPTZ,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT unique_subscription_period UNIQUE (subscription_id, period_number)
);

-- Subscription pauses
CREATE TABLE IF NOT EXISTS public.subscription_pauses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  subscription_id UUID NOT NULL REFERENCES public.subscriptions(id) ON DELETE CASCADE,
  
  paused_at TIMESTAMPTZ DEFAULT NOW(),
  resume_at TIMESTAMPTZ,
  resumed_at TIMESTAMPTZ,
  
  reason TEXT,
  paused_by UUID NOT NULL,
  
  -- Credits for pause period
  days_credited INTEGER DEFAULT 0,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Subscription upgrades/downgrades
CREATE TABLE IF NOT EXISTS public.subscription_changes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  subscription_id UUID NOT NULL REFERENCES public.subscriptions(id) ON DELETE CASCADE,
  
  change_type VARCHAR(20) NOT NULL CHECK (change_type IN ('upgrade', 'downgrade', 'renewal')),
  
  from_plan plan_type NOT NULL,
  to_plan plan_type NOT NULL,
  
  from_amount_paise BIGINT NOT NULL,
  to_amount_paise BIGINT NOT NULL,
  
  -- Proration
  proration_amount_paise BIGINT DEFAULT 0,
  proration_credit_paise BIGINT DEFAULT 0,
  
  effective_at TIMESTAMPTZ NOT NULL,
  processed_at TIMESTAMPTZ,
  
  changed_by UUID NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- SECTION 7: PAYMENT MANDATES (RBI e-Mandate)
-- ===========================================

-- Payment mandates (UPI AutoPay / Card Recurring)
CREATE TABLE IF NOT EXISTS public.payment_mandates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Owner
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  subscription_id UUID REFERENCES public.subscriptions(id) ON DELETE SET NULL,
  
  -- Mandate details
  mandate_type payment_method_type NOT NULL,
  
  -- PhonePe mandate info
  phonepe_mandate_id TEXT UNIQUE,
  phonepe_subscription_id TEXT,
  
  -- Amount limits (RBI requirement)
  max_amount_paise BIGINT NOT NULL,
  frequency VARCHAR(20) DEFAULT 'monthly' CHECK (frequency IN ('daily', 'weekly', 'monthly', 'quarterly', 'yearly')),
  
  -- RBI Autopay limit check
  is_within_autopay_limit BOOLEAN GENERATED ALWAYS AS (max_amount_paise <= 500000) STORED,
  requires_otp_each_debit BOOLEAN GENERATED ALWAYS AS (max_amount_paise > 500000) STORED,
  
  -- Validity
  valid_from TIMESTAMPTZ NOT NULL,
  valid_until TIMESTAMPTZ NOT NULL,
  
  -- Status
  status mandate_status DEFAULT 'pending_authorization',
  authorized_at TIMESTAMPTZ,
  revoked_at TIMESTAMPTZ,
  revocation_reason TEXT,
  
  -- Last execution
  last_executed_at TIMESTAMPTZ,
  last_execution_status VARCHAR(20),
  execution_count INTEGER DEFAULT 0,
  failed_execution_count INTEGER DEFAULT 0,
  
  -- Metadata
  metadata JSONB DEFAULT '{}',
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Mandate notifications (RBI requires pre-debit notification)
CREATE TABLE IF NOT EXISTS public.mandate_notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  mandate_id UUID NOT NULL REFERENCES public.payment_mandates(id) ON DELETE CASCADE,
  
  -- Notification details
  notification_type VARCHAR(20) NOT NULL CHECK (notification_type IN ('pre_debit', 'post_debit', 'failure', 'revocation')),
  
  -- Amount to be debited
  amount_paise BIGINT NOT NULL,
  scheduled_debit_date DATE NOT NULL,
  
  -- Delivery
  channel notification_type DEFAULT 'email',
  sent_at TIMESTAMPTZ,
  delivered_at TIMESTAMPTZ,
  failed_at TIMESTAMPTZ,
  failure_reason TEXT,
  
  -- RBI requirement: 24 hours before debit
  notification_sent_hours_before INTEGER DEFAULT 24,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Mandate executions (auto-debit attempts)
CREATE TABLE IF NOT EXISTS public.mandate_executions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  mandate_id UUID NOT NULL REFERENCES public.payment_mandates(id) ON DELETE CASCADE,
  subscription_id UUID REFERENCES public.subscriptions(id) ON DELETE SET NULL,
  
  -- Amount
  amount_paise BIGINT NOT NULL,
  
  -- Execution details
  scheduled_at TIMESTAMPTZ NOT NULL,
  executed_at TIMESTAMPTZ,
  
  -- Result
  status payment_status DEFAULT 'initiated',
  payment_id UUID,
  
  -- PhonePe response
  phonepe_transaction_id TEXT,
  response_code TEXT,
  response_message TEXT,
  
  -- Retry info
  attempt_number INTEGER DEFAULT 1,
  next_retry_at TIMESTAMPTZ,
  max_retries INTEGER DEFAULT 3,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- SECTION 8: INVOICES & BILLING
-- ===========================================

-- Invoices
CREATE TABLE IF NOT EXISTS public.invoices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Invoice number (GST compliant)
  invoice_number VARCHAR(50) UNIQUE NOT NULL,
  
  -- Owner
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE SET NULL,
  subscription_id UUID REFERENCES public.subscriptions(id) ON DELETE SET NULL,
  
  -- Billing details
  billing_name TEXT NOT NULL,
  billing_email TEXT NOT NULL,
  billing_address JSONB,
  billing_gstin VARCHAR(15),
  billing_pan VARCHAR(10),
  
  -- Amounts (in paise)
  subtotal_paise BIGINT NOT NULL,
  discount_paise BIGINT DEFAULT 0,
  tax_paise BIGINT DEFAULT 0,
  total_paise BIGINT NOT NULL,
  amount_paid_paise BIGINT DEFAULT 0,
  amount_due_paise BIGINT GENERATED ALWAYS AS (total_paise - amount_paid_paise) STORED,
  
  currency VARCHAR(3) DEFAULT 'INR',
  
  -- Tax breakdown (GST)
  cgst_rate DECIMAL(5,2) DEFAULT 9.00,
  sgst_rate DECIMAL(5,2) DEFAULT 9.00,
  igst_rate DECIMAL(5,2) DEFAULT 0.00,
  cgst_amount_paise BIGINT DEFAULT 0,
  sgst_amount_paise BIGINT DEFAULT 0,
  igst_amount_paise BIGINT DEFAULT 0,
  
  -- Dates
  invoice_date DATE NOT NULL DEFAULT CURRENT_DATE,
  due_date DATE NOT NULL,
  paid_at TIMESTAMPTZ,
  
  -- Status
  status invoice_status DEFAULT 'pending',
  
  -- Payment
  payment_id UUID,
  payment_method payment_method_type,
  
  -- PDF storage
  pdf_url TEXT,
  pdf_generated_at TIMESTAMPTZ,
  
  -- Notes
  notes TEXT,
  footer_text TEXT,
  
  -- Metadata
  metadata JSONB DEFAULT '{}',
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Invoice items
CREATE TABLE IF NOT EXISTS public.invoice_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  invoice_id UUID NOT NULL REFERENCES public.invoices(id) ON DELETE CASCADE,
  
  -- Item details
  description TEXT NOT NULL,
  quantity INTEGER DEFAULT 1,
  unit_price_paise BIGINT NOT NULL,
  total_paise BIGINT GENERATED ALWAYS AS (quantity * unit_price_paise) STORED,
  
  -- Tax
  hsn_code VARCHAR(20),
  tax_rate DECIMAL(5,2) DEFAULT 18.00,
  tax_amount_paise BIGINT DEFAULT 0,
  
  -- Period (for subscriptions)
  period_start TIMESTAMPTZ,
  period_end TIMESTAMPTZ,
  
  -- Metadata
  metadata JSONB DEFAULT '{}',
  
  sort_order INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Credit notes (refunds)
CREATE TABLE IF NOT EXISTS public.credit_notes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  credit_note_number VARCHAR(50) UNIQUE NOT NULL,
  invoice_id UUID NOT NULL REFERENCES public.invoices(id) ON DELETE CASCADE,
  
  -- Amounts
  amount_paise BIGINT NOT NULL,
  reason TEXT NOT NULL,
  
  -- Status
  status VARCHAR(20) DEFAULT 'issued' CHECK (status IN ('issued', 'applied', 'refunded', 'voided')),
  
  applied_at TIMESTAMPTZ,
  refunded_at TIMESTAMPTZ,
  
  issued_by UUID NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- SECTION 9: PAYMENTS
-- ===========================================

-- Payments table (enhanced)
CREATE TABLE IF NOT EXISTS public.payments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Owner
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE SET NULL,
  
  -- Related entities
  subscription_id UUID REFERENCES public.subscriptions(id) ON DELETE SET NULL,
  invoice_id UUID REFERENCES public.invoices(id) ON DELETE SET NULL,
  mandate_id UUID REFERENCES public.payment_mandates(id) ON DELETE SET NULL,
  
  -- Payment details
  amount_paise BIGINT NOT NULL,
  currency VARCHAR(3) DEFAULT 'INR',
  plan plan_type,
  
  -- Payment method
  payment_method payment_method_type,
  payment_method_details JSONB DEFAULT '{}',
  
  -- PhonePe transaction details
  phonepe_transaction_id TEXT,
  phonepe_merchant_transaction_id TEXT UNIQUE,
  phonepe_payment_instrument_type TEXT,
  
  -- Status
  status payment_status DEFAULT 'initiated',
  
  -- Timestamps
  initiated_at TIMESTAMPTZ DEFAULT NOW(),
  processing_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  failed_at TIMESTAMPTZ,
  
  -- Response data
  response_code TEXT,
  response_message TEXT,
  raw_response JSONB,
  
  -- Idempotency
  idempotency_key VARCHAR(64) UNIQUE,
  
  -- Retry handling
  attempt_count INTEGER DEFAULT 1,
  last_attempt_at TIMESTAMPTZ,
  next_retry_at TIMESTAMPTZ,
  
  -- Security
  ip_address INET,
  user_agent TEXT,
  device_fingerprint TEXT,
  
  -- Risk assessment
  risk_score INTEGER DEFAULT 0,
  risk_flags JSONB DEFAULT '[]',
  is_flagged BOOLEAN DEFAULT false,
  
  -- Metadata
  metadata JSONB DEFAULT '{}',
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Payment disputes
CREATE TABLE IF NOT EXISTS public.payment_disputes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  payment_id UUID NOT NULL REFERENCES public.payments(id) ON DELETE CASCADE,
  
  -- Dispute details
  dispute_type VARCHAR(50) NOT NULL CHECK (dispute_type IN ('chargeback', 'refund_request', 'fraudulent', 'duplicate', 'other')),
  dispute_reason TEXT NOT NULL,
  
  -- Amounts
  disputed_amount_paise BIGINT NOT NULL,
  resolved_amount_paise BIGINT,
  
  -- Status
  status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'under_review', 'won', 'lost', 'closed')),
  
  -- Resolution
  resolution TEXT,
  resolved_at TIMESTAMPTZ,
  resolved_by UUID,
  
  -- Evidence
  evidence JSONB DEFAULT '[]',
  evidence_due_date TIMESTAMPTZ,
  
  -- External reference
  external_dispute_id TEXT,
  
  opened_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Refunds
CREATE TABLE IF NOT EXISTS public.refunds (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  payment_id UUID NOT NULL REFERENCES public.payments(id) ON DELETE CASCADE,
  
  -- Refund details
  amount_paise BIGINT NOT NULL,
  reason TEXT NOT NULL,
  
  -- PhonePe refund
  phonepe_refund_id TEXT UNIQUE,
  
  -- Status
  status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
  
  -- Processing
  initiated_at TIMESTAMPTZ DEFAULT NOW(),
  processed_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  failed_at TIMESTAMPTZ,
  failure_reason TEXT,
  
  -- Who initiated
  initiated_by UUID NOT NULL,
  
  -- Metadata
  metadata JSONB DEFAULT '{}',
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- SECTION 10: PLAN PRICES (Enhanced)
-- ===========================================

CREATE TABLE IF NOT EXISTS public.plan_prices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  plan plan_type NOT NULL UNIQUE,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  
  -- Pricing (in paise)
  price_paise BIGINT NOT NULL,
  price_display VARCHAR(20) NOT NULL,
  
  -- RBI Autopay eligibility
  autopay_eligible BOOLEAN GENERATED ALWAYS AS (price_paise <= 500000) STORED,
  
  -- Feature limits
  cohort_limit INTEGER NOT NULL,
  workspace_limit INTEGER NOT NULL,
  team_member_limit INTEGER NOT NULL,
  
  -- Features
  features JSONB DEFAULT '[]',
  
  -- Duration
  duration_days INTEGER DEFAULT 30,
  
  -- Billing options
  allow_monthly BOOLEAN DEFAULT true,
  allow_quarterly BOOLEAN DEFAULT false,
  allow_yearly BOOLEAN DEFAULT false,
  
  -- Discounts
  quarterly_discount_percent DECIMAL(5,2) DEFAULT 10.00,
  yearly_discount_percent DECIMAL(5,2) DEFAULT 20.00,
  
  -- Display
  is_highlighted BOOLEAN DEFAULT false,
  badge_text VARCHAR(50),
  sort_order INTEGER DEFAULT 0,
  
  -- Status
  is_active BOOLEAN DEFAULT true,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- SECTION 11: ONBOARDING TABLES
-- ===========================================

CREATE TABLE IF NOT EXISTS public.onboarding_intake (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- Step data (JSONB for flexibility)
  positioning JSONB DEFAULT '{}',
  positioning_derived JSONB DEFAULT '{}',
  company JSONB DEFAULT '{}',
  company_enriched JSONB DEFAULT '{}',
  product JSONB DEFAULT '{}',
  product_derived JSONB DEFAULT '{}',
  market JSONB DEFAULT '{}',
  market_system_view JSONB DEFAULT '{}',
  strategy JSONB DEFAULT '{}',
  strategy_derived JSONB DEFAULT '{}',
  
  -- Generated outputs
  icps JSONB DEFAULT '[]',
  war_plan JSONB DEFAULT '{}',
  metrics_framework JSONB DEFAULT '{}',
  
  -- Progress
  current_step INTEGER DEFAULT 1,
  completed_steps INTEGER[] DEFAULT '{}',
  total_steps INTEGER DEFAULT 5,
  
  -- Mode
  mode VARCHAR(20) DEFAULT 'self-service',
  sales_rep_id UUID REFERENCES auth.users(id),
  share_token VARCHAR(100) UNIQUE,
  
  -- Payment tracking
  selected_plan plan_type,
  payment_status VARCHAR(20) DEFAULT 'pending',
  payment_completed_at TIMESTAMPTZ,
  
  -- Soft delete
  deleted_at TIMESTAMPTZ,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agent execution logs
CREATE TABLE IF NOT EXISTS public.agent_executions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  intake_id UUID REFERENCES public.onboarding_intake(id) ON DELETE CASCADE,
  
  agent_name VARCHAR(100) NOT NULL,
  agent_version VARCHAR(20),
  
  input JSONB NOT NULL,
  output JSONB,
  
  status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
  
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  duration_ms INTEGER,
  
  error TEXT,
  error_code VARCHAR(50),
  retry_count INTEGER DEFAULT 0,
  
  tokens_used INTEGER,
  cost_usd DECIMAL(10,6),
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Shared links
CREATE TABLE IF NOT EXISTS public.shared_links (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  intake_id UUID REFERENCES public.onboarding_intake(id) ON DELETE CASCADE,
  
  token VARCHAR(100) UNIQUE NOT NULL,
  
  sales_rep_id UUID REFERENCES auth.users(id),
  expires_at TIMESTAMPTZ,
  
  accessed_count INTEGER DEFAULT 0,
  last_accessed_at TIMESTAMPTZ,
  last_accessed_ip INET,
  
  payment_completed BOOLEAN DEFAULT FALSE,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- SECTION 12: PLATFORM - ICPs & COHORTS
-- ===========================================

CREATE TABLE IF NOT EXISTS public.icps (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
  intake_id UUID REFERENCES public.onboarding_intake(id) ON DELETE SET NULL,
  
  label VARCHAR(100) NOT NULL,
  slug VARCHAR(100),
  summary TEXT,
  
  -- 6D Dimensions
  firmographics JSONB DEFAULT '{}',
  technographics JSONB DEFAULT '{}',
  psychographics JSONB DEFAULT '{}',
  behavioral_triggers JSONB DEFAULT '[]',
  buying_committee JSONB DEFAULT '[]',
  category_context JSONB DEFAULT '{}',
  
  -- Scoring
  fit_score INTEGER DEFAULT 0 CHECK (fit_score >= 0 AND fit_score <= 100),
  fit_reasoning TEXT,
  priority_rank INTEGER DEFAULT 0,
  
  -- Messaging
  messaging_angle TEXT,
  qualification_questions JSONB DEFAULT '[]',
  
  -- Barriers
  primary_barriers barrier_type[] DEFAULT '{}',
  
  -- Status
  is_selected BOOLEAN DEFAULT true,
  is_archived BOOLEAN DEFAULT false,
  version INTEGER DEFAULT 1,
  
  -- Soft delete
  deleted_at TIMESTAMPTZ,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.cohorts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
  
  name VARCHAR(255) NOT NULL,
  description TEXT NOT NULL,
  status VARCHAR(50) DEFAULT 'active',
  
  -- 6D Profile
  firmographics JSONB DEFAULT '{}',
  psychographics JSONB DEFAULT '{}',
  behavioral_triggers JSONB DEFAULT '[]',
  buying_committee JSONB DEFAULT '[]',
  category_context JSONB DEFAULT '{}',
  
  -- Tags
  interest_tags JSONB DEFAULT '[]',
  tags_count INTEGER DEFAULT 0,
  
  -- Scoring
  fit_score INTEGER DEFAULT 0,
  fit_reasoning TEXT,
  messaging_angle TEXT,
  qualification_questions JSONB DEFAULT '[]',
  
  -- Radar
  last_radar_scan TIMESTAMPTZ,
  radar_opportunities_found INTEGER DEFAULT 0,
  
  -- Soft delete
  deleted_at TIMESTAMPTZ,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- SECTION 13: PLATFORM - BARRIERS & PROTOCOLS
-- ===========================================

CREATE TABLE IF NOT EXISTS public.barriers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  icp_id UUID REFERENCES public.icps(id) ON DELETE CASCADE,
  cohort_id UUID REFERENCES public.cohorts(id) ON DELETE CASCADE,
  
  barrier_type barrier_type NOT NULL,
  confidence DECIMAL(3,2) DEFAULT 0.5 CHECK (confidence >= 0 AND confidence <= 1),
  
  supporting_signals JSONB DEFAULT '[]',
  metrics_snapshot JSONB DEFAULT '{}',
  analysis_notes TEXT,
  recommended_protocols protocol_type[] DEFAULT '{}',
  
  diagnosed_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT unique_active_barrier UNIQUE (icp_id, cohort_id, barrier_type)
);

CREATE TABLE IF NOT EXISTS public.protocols (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code protocol_type NOT NULL UNIQUE,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  targets_barrier barrier_type NOT NULL,
  trigger_conditions JSONB DEFAULT '[]',
  required_asset_types JSONB DEFAULT '[]',
  channel_rules JSONB DEFAULT '{}',
  metric_targets JSONB DEFAULT '{}',
  standard_checklist JSONB DEFAULT '[]',
  is_active BOOLEAN DEFAULT true,
  display_order INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.move_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug VARCHAR(100) NOT NULL UNIQUE,
  name VARCHAR(200) NOT NULL,
  description TEXT,
  protocol_type protocol_type NOT NULL,
  barrier_type barrier_type NOT NULL,
  funnel_stage VARCHAR(50),
  required_inputs JSONB DEFAULT '[]',
  channels JSONB DEFAULT '[]',
  task_template JSONB DEFAULT '[]',
  asset_requirements JSONB DEFAULT '[]',
  automation_hooks JSONB DEFAULT '{}',
  success_metrics JSONB DEFAULT '[]',
  base_impact_score INTEGER DEFAULT 50,
  base_effort_score INTEGER DEFAULT 50,
  is_active BOOLEAN DEFAULT true,
  display_order INTEGER DEFAULT 0,
  tags JSONB DEFAULT '[]',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- SECTION 14: CAMPAIGNS & MOVES
-- ===========================================

CREATE TABLE IF NOT EXISTS public.campaigns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
  
  name VARCHAR(200) NOT NULL,
  description TEXT,
  goal goal_type NOT NULL,
  demand_source demand_source_type NOT NULL,
  persuasion_axis persuasion_axis_type NOT NULL,
  
  icp_ids UUID[] DEFAULT '{}',
  cohort_ids UUID[] DEFAULT '{}',
  primary_barriers barrier_type[] DEFAULT '{}',
  protocols protocol_type[] DEFAULT '{}',
  
  start_date DATE,
  end_date DATE,
  budget_plan JSONB DEFAULT '{}',
  targets JSONB DEFAULT '{}',
  
  status campaign_status DEFAULT 'draft',
  rag_status rag_status DEFAULT 'unknown',
  rag_details JSONB DEFAULT '{}',
  
  created_from_spike UUID,
  
  -- Soft delete
  deleted_at TIMESTAMPTZ,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.moves (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
  campaign_id UUID REFERENCES public.campaigns(id) ON DELETE CASCADE,
  spike_id UUID,
  template_id UUID REFERENCES public.move_templates(id) ON DELETE SET NULL,
  
  name VARCHAR(200) NOT NULL,
  description TEXT,
  protocol protocol_type,
  icp_id UUID REFERENCES public.icps(id) ON DELETE SET NULL,
  
  channels JSONB DEFAULT '[]',
  tasks JSONB DEFAULT '[]',
  
  impact_score INTEGER DEFAULT 50,
  effort_score INTEGER DEFAULT 50,
  ev_score DECIMAL(5,2),
  
  status move_status DEFAULT 'planned',
  progress_percentage INTEGER DEFAULT 0,
  rag_status rag_status DEFAULT 'unknown',
  rag_details JSONB DEFAULT '{}',
  kpis JSONB DEFAULT '{}',
  
  planned_start DATE,
  planned_end DATE,
  actual_start TIMESTAMPTZ,
  actual_end TIMESTAMPTZ,
  
  -- Soft delete
  deleted_at TIMESTAMPTZ,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- SECTION 15: ASSETS (Muse)
-- ===========================================

CREATE TABLE IF NOT EXISTS public.assets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
  move_id UUID REFERENCES public.moves(id) ON DELETE SET NULL,
  campaign_id UUID REFERENCES public.campaigns(id) ON DELETE SET NULL,
  icp_id UUID REFERENCES public.icps(id) ON DELETE SET NULL,
  
  protocol protocol_type,
  name VARCHAR(300) NOT NULL,
  asset_type VARCHAR(100) NOT NULL,
  content TEXT,
  content_format VARCHAR(50) DEFAULT 'markdown',
  variants JSONB DEFAULT '[]',
  
  status asset_status DEFAULT 'draft',
  distribution_links JSONB DEFAULT '{}',
  performance_data JSONB DEFAULT '{}',
  tags JSONB DEFAULT '[]',
  version INTEGER DEFAULT 1,
  
  approved_at TIMESTAMPTZ,
  approved_by UUID,
  deployed_at TIMESTAMPTZ,
  
  -- Soft delete
  deleted_at TIMESTAMPTZ,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- SECTION 16: METRICS & SPIKES
-- ===========================================

CREATE TABLE IF NOT EXISTS public.metrics (
  id UUID NOT NULL DEFAULT gen_random_uuid(),
  recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
  
  scope_type VARCHAR(50) NOT NULL,
  scope_id UUID,
  metric_name VARCHAR(100) NOT NULL,
  metric_category VARCHAR(100),
  
  value DECIMAL(15,4),
  unit VARCHAR(50),
  
  period_start TIMESTAMPTZ,
  period_end TIMESTAMPTZ,
  
  target_value DECIMAL(15,4),
  rag_status rag_status DEFAULT 'unknown',
  rag_thresholds JSONB DEFAULT '{}',
  
  source VARCHAR(100),
  raw_data JSONB DEFAULT '{}',
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  PRIMARY KEY (id, recorded_at)
) PARTITION BY RANGE (recorded_at);

-- Create partitions for metrics (by quarter)
CREATE TABLE IF NOT EXISTS public.metrics_2024_q4 PARTITION OF public.metrics
  FOR VALUES FROM ('2024-10-01') TO ('2025-01-01');
CREATE TABLE IF NOT EXISTS public.metrics_2025_q1 PARTITION OF public.metrics
  FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');
CREATE TABLE IF NOT EXISTS public.metrics_2025_q2 PARTITION OF public.metrics
  FOR VALUES FROM ('2025-04-01') TO ('2025-07-01');
CREATE TABLE IF NOT EXISTS public.metrics_2025_q3 PARTITION OF public.metrics
  FOR VALUES FROM ('2025-07-01') TO ('2025-10-01');
CREATE TABLE IF NOT EXISTS public.metrics_2025_q4 PARTITION OF public.metrics
  FOR VALUES FROM ('2025-10-01') TO ('2026-01-01');
CREATE TABLE IF NOT EXISTS public.metrics_default PARTITION OF public.metrics DEFAULT;

CREATE TABLE IF NOT EXISTS public.spikes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
  
  name VARCHAR(200) NOT NULL,
  spike_type spike_type NOT NULL,
  goal goal_type NOT NULL,
  demand_source demand_source_type,
  
  primary_icp_id UUID REFERENCES public.icps(id) ON DELETE SET NULL,
  secondary_icp_ids UUID[] DEFAULT '{}',
  barriers barrier_type[] DEFAULT '{}',
  protocols protocol_type[] DEFAULT '{}',
  
  targets JSONB NOT NULL DEFAULT '{}',
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  
  campaign_id UUID REFERENCES public.campaigns(id) ON DELETE SET NULL,
  move_ids UUID[] DEFAULT '{}',
  
  status spike_status DEFAULT 'configuring',
  current_day INTEGER DEFAULT 0,
  progress_percentage INTEGER DEFAULT 0,
  rag_status rag_status DEFAULT 'unknown',
  rag_details JSONB DEFAULT '{}',
  
  results JSONB DEFAULT '{}',
  learnings JSONB DEFAULT '[]',
  
  completed_at TIMESTAMPTZ,
  
  -- Soft delete
  deleted_at TIMESTAMPTZ,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- SECTION 17: GUARDRAILS & EXPERIMENTS
-- ===========================================

CREATE TABLE IF NOT EXISTS public.guardrails (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
  spike_id UUID REFERENCES public.spikes(id) ON DELETE CASCADE,
  campaign_id UUID REFERENCES public.campaigns(id) ON DELETE CASCADE,
  icp_id UUID REFERENCES public.icps(id) ON DELETE SET NULL,
  
  name VARCHAR(200) NOT NULL,
  description TEXT,
  metric VARCHAR(100) NOT NULL,
  operator VARCHAR(20) NOT NULL,
  threshold DECIMAL(15,4) NOT NULL,
  threshold_upper DECIMAL(15,4),
  
  action guardrail_action DEFAULT 'alert_only',
  is_active BOOLEAN DEFAULT true,
  is_triggered BOOLEAN DEFAULT false,
  last_triggered_at TIMESTAMPTZ,
  trigger_count INTEGER DEFAULT 0,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.guardrail_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  guardrail_id UUID NOT NULL REFERENCES public.guardrails(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  event_type VARCHAR(50) NOT NULL,
  metric_value DECIMAL(15,4),
  threshold_value DECIMAL(15,4),
  action_taken VARCHAR(100),
  affected_entities JSONB DEFAULT '{}',
  override_reason TEXT,
  overridden_by UUID REFERENCES auth.users(id),
  
  occurred_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.experiments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
  spike_id UUID REFERENCES public.spikes(id) ON DELETE SET NULL,
  campaign_id UUID REFERENCES public.campaigns(id) ON DELETE SET NULL,
  move_id UUID REFERENCES public.moves(id) ON DELETE SET NULL,
  
  name VARCHAR(200) NOT NULL,
  hypothesis TEXT,
  bet_type VARCHAR(50) DEFAULT 'growth',
  
  expected_impact INTEGER DEFAULT 50,
  probability INTEGER DEFAULT 50,
  effort INTEGER DEFAULT 50,
  ev_score DECIMAL(5,2),
  
  status VARCHAR(50) DEFAULT 'planned',
  actual_outcome TEXT,
  learnings TEXT,
  promoted_to_baseline BOOLEAN DEFAULT false,
  
  started_at TIMESTAMPTZ,
  ended_at TIMESTAMPTZ,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- SECTION 18: RADAR & CONTENT IDEAS
-- ===========================================

CREATE TABLE IF NOT EXISTS public.radar_opportunities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
  cohort_id UUID REFERENCES public.cohorts(id) ON DELETE CASCADE,
  
  title VARCHAR(500) NOT NULL,
  description TEXT,
  trend_type VARCHAR(50),
  relevance_score INTEGER DEFAULT 0,
  urgency VARCHAR(50),
  
  matching_tags JSONB DEFAULT '[]',
  content_angles JSONB DEFAULT '[]',
  risk_level VARCHAR(50) DEFAULT 'safe',
  risk_notes TEXT,
  sources JSONB DEFAULT '[]',
  peak_window VARCHAR(255),
  decay_estimate VARCHAR(255),
  
  status VARCHAR(50) DEFAULT 'new',
  actioned_at TIMESTAMPTZ,
  expires_at TIMESTAMPTZ,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.content_ideas (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
  opportunity_id UUID REFERENCES public.radar_opportunities(id) ON DELETE SET NULL,
  cohort_id UUID REFERENCES public.cohorts(id) ON DELETE SET NULL,
  
  headline VARCHAR(500),
  subheadline VARCHAR(500),
  body_copy TEXT,
  call_to_action VARCHAR(255),
  hashtags JSONB DEFAULT '[]',
  visual_concept TEXT,
  visual_style VARCHAR(50),
  color_suggestions JSONB DEFAULT '[]',
  variations JSONB DEFAULT '[]',
  
  format VARCHAR(50),
  platform VARCHAR(100),
  estimated_time VARCHAR(50),
  difficulty VARCHAR(50),
  resources_needed JSONB DEFAULT '[]',
  engagement_estimate VARCHAR(50),
  best_posting_time VARCHAR(100),
  expected_reach_multiplier DECIMAL(3,1),
  
  status VARCHAR(50) DEFAULT 'draft',
  published_at TIMESTAMPTZ,
  actual_engagement JSONB DEFAULT '{}',
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- SECTION 19: SECURITY - AUDIT LOGS
-- ===========================================

CREATE TABLE IF NOT EXISTS public.audit_logs (
  id UUID NOT NULL DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  -- Actor
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE SET NULL,
  
  -- Action
  action audit_action NOT NULL,
  resource_type VARCHAR(100) NOT NULL,
  resource_id UUID,
  
  -- Details
  description TEXT,
  old_values JSONB,
  new_values JSONB,
  changes JSONB,
  
  -- Context
  ip_address INET,
  user_agent TEXT,
  session_id UUID,
  request_id UUID,
  
  -- Metadata
  metadata JSONB DEFAULT '{}',
  
  PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- Audit log partitions (by month)
CREATE TABLE IF NOT EXISTS public.audit_logs_2024_12 PARTITION OF public.audit_logs
  FOR VALUES FROM ('2024-12-01') TO ('2025-01-01');
CREATE TABLE IF NOT EXISTS public.audit_logs_2025_01 PARTITION OF public.audit_logs
  FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
CREATE TABLE IF NOT EXISTS public.audit_logs_2025_02 PARTITION OF public.audit_logs
  FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
CREATE TABLE IF NOT EXISTS public.audit_logs_2025_03 PARTITION OF public.audit_logs
  FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');
CREATE TABLE IF NOT EXISTS public.audit_logs_default PARTITION OF public.audit_logs DEFAULT;

-- Data access logs (GDPR compliance)
CREATE TABLE IF NOT EXISTS public.data_access_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  access_type VARCHAR(50) NOT NULL CHECK (access_type IN ('view', 'export', 'download', 'api_access')),
  data_category VARCHAR(100) NOT NULL,
  resource_type VARCHAR(100),
  resource_id UUID,
  
  -- Details
  fields_accessed JSONB DEFAULT '[]',
  purpose TEXT,
  
  -- Security
  ip_address INET,
  user_agent TEXT,
  
  accessed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Security events
CREATE TABLE IF NOT EXISTS public.security_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  event_type VARCHAR(100) NOT NULL,
  severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
  
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  
  description TEXT NOT NULL,
  details JSONB DEFAULT '{}',
  
  ip_address INET,
  user_agent TEXT,
  country VARCHAR(2),
  
  -- Resolution
  is_resolved BOOLEAN DEFAULT false,
  resolved_at TIMESTAMPTZ,
  resolved_by UUID,
  resolution_notes TEXT,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Login attempts
CREATE TABLE IF NOT EXISTS public.login_attempts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  email TEXT NOT NULL,
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  
  success BOOLEAN NOT NULL,
  failure_reason VARCHAR(100),
  
  ip_address INET NOT NULL,
  user_agent TEXT,
  country VARCHAR(2),
  
  attempted_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- SECTION 20: SECURITY - SESSIONS & API KEYS
-- ===========================================

CREATE TABLE IF NOT EXISTS public.user_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- Session info
  token_hash TEXT NOT NULL,
  refresh_token_hash TEXT,
  
  -- Device
  device_name VARCHAR(255),
  device_type VARCHAR(50),
  browser VARCHAR(100),
  os VARCHAR(100),
  
  -- Location
  ip_address INET,
  country VARCHAR(2),
  city VARCHAR(100),
  
  -- Status
  is_active BOOLEAN DEFAULT true,
  last_active_at TIMESTAMPTZ DEFAULT NOW(),
  
  expires_at TIMESTAMPTZ NOT NULL,
  revoked_at TIMESTAMPTZ,
  revoked_reason TEXT,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.api_keys (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
  
  name VARCHAR(255) NOT NULL,
  description TEXT,
  
  -- Key (only prefix stored, full key shown once)
  key_prefix VARCHAR(16) NOT NULL,
  key_hash TEXT NOT NULL,
  
  -- Permissions
  scopes JSONB DEFAULT '["read"]',
  
  -- Rate limiting
  rate_limit_per_minute INTEGER DEFAULT 60,
  rate_limit_per_day INTEGER DEFAULT 10000,
  
  -- Status
  is_active BOOLEAN DEFAULT true,
  last_used_at TIMESTAMPTZ,
  total_requests INTEGER DEFAULT 0,
  
  expires_at TIMESTAMPTZ,
  revoked_at TIMESTAMPTZ,
  revoked_reason TEXT,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT api_key_owner CHECK (
    (user_id IS NOT NULL AND organization_id IS NULL) OR
    (user_id IS NULL AND organization_id IS NOT NULL)
  )
);

-- Rate limiting
CREATE TABLE IF NOT EXISTS public.rate_limit_buckets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  identifier TEXT NOT NULL,
  identifier_type VARCHAR(50) NOT NULL CHECK (identifier_type IN ('user', 'ip', 'api_key', 'endpoint')),
  
  bucket_window TIMESTAMPTZ NOT NULL,
  request_count INTEGER DEFAULT 0,
  
  CONSTRAINT unique_rate_bucket UNIQUE (identifier, identifier_type, bucket_window)
);

-- ===========================================
-- SECTION 21: NOTIFICATIONS
-- ===========================================

CREATE TABLE IF NOT EXISTS public.notification_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  slug VARCHAR(100) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  
  -- Template content
  subject_template TEXT,
  body_template TEXT NOT NULL,
  html_template TEXT,
  
  -- Channels
  channels notification_type[] DEFAULT '{email}',
  
  -- Variables
  required_variables JSONB DEFAULT '[]',
  optional_variables JSONB DEFAULT '[]',
  
  is_active BOOLEAN DEFAULT true,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.notification_queue (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  template_id UUID REFERENCES public.notification_templates(id) ON DELETE SET NULL,
  
  channel notification_type NOT NULL,
  priority notification_priority DEFAULT 'normal',
  
  -- Content
  subject TEXT,
  body TEXT NOT NULL,
  html_body TEXT,
  
  -- Delivery
  recipient TEXT NOT NULL,
  
  -- Status
  status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'sent', 'delivered', 'failed', 'cancelled')),
  
  scheduled_at TIMESTAMPTZ DEFAULT NOW(),
  sent_at TIMESTAMPTZ,
  delivered_at TIMESTAMPTZ,
  failed_at TIMESTAMPTZ,
  failure_reason TEXT,
  
  -- Retry
  retry_count INTEGER DEFAULT 0,
  max_retries INTEGER DEFAULT 3,
  next_retry_at TIMESTAMPTZ,
  
  -- Metadata
  metadata JSONB DEFAULT '{}',
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.notification_preferences (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  category VARCHAR(100) NOT NULL,
  
  email_enabled BOOLEAN DEFAULT true,
  push_enabled BOOLEAN DEFAULT true,
  sms_enabled BOOLEAN DEFAULT false,
  in_app_enabled BOOLEAN DEFAULT true,
  
  frequency VARCHAR(50) DEFAULT 'immediate' CHECK (frequency IN ('immediate', 'daily_digest', 'weekly_digest', 'never')),
  
  quiet_hours_start TIME,
  quiet_hours_end TIME,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT unique_user_notification_pref UNIQUE (user_id, category)
);

-- ===========================================
-- SECTION 22: WEBHOOKS & INTEGRATIONS
-- ===========================================

CREATE TABLE IF NOT EXISTS public.webhooks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
  
  name VARCHAR(255) NOT NULL,
  url TEXT NOT NULL,
  
  -- Events
  events webhook_event[] NOT NULL,
  
  -- Security
  secret_hash TEXT NOT NULL,
  
  -- Headers
  custom_headers JSONB DEFAULT '{}',
  
  -- Status
  is_active BOOLEAN DEFAULT true,
  
  -- Stats
  total_deliveries INTEGER DEFAULT 0,
  successful_deliveries INTEGER DEFAULT 0,
  failed_deliveries INTEGER DEFAULT 0,
  last_delivery_at TIMESTAMPTZ,
  last_success_at TIMESTAMPTZ,
  last_failure_at TIMESTAMPTZ,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.webhook_deliveries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  webhook_id UUID NOT NULL REFERENCES public.webhooks(id) ON DELETE CASCADE,
  
  event webhook_event NOT NULL,
  payload JSONB NOT NULL,
  
  -- Delivery
  status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'delivered', 'failed')),
  response_status INTEGER,
  response_body TEXT,
  response_headers JSONB,
  
  duration_ms INTEGER,
  
  attempt_count INTEGER DEFAULT 0,
  next_retry_at TIMESTAMPTZ,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  delivered_at TIMESTAMPTZ
);

-- OAuth connections
CREATE TABLE IF NOT EXISTS public.oauth_connections (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  provider VARCHAR(50) NOT NULL,
  provider_user_id TEXT NOT NULL,
  
  access_token_encrypted TEXT,
  refresh_token_encrypted TEXT,
  token_expires_at TIMESTAMPTZ,
  
  scopes JSONB DEFAULT '[]',
  
  profile_data JSONB DEFAULT '{}',
  
  is_active BOOLEAN DEFAULT true,
  last_synced_at TIMESTAMPTZ,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT unique_oauth_connection UNIQUE (user_id, provider)
);

-- ===========================================
-- SECTION 23: FEATURE FLAGS
-- ===========================================

CREATE TABLE IF NOT EXISTS public.feature_flags (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  key VARCHAR(100) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  
  status feature_flag_status DEFAULT 'disabled',
  
  -- For percentage rollout
  rollout_percentage INTEGER DEFAULT 0 CHECK (rollout_percentage >= 0 AND rollout_percentage <= 100),
  
  -- For user list rollout
  enabled_user_ids UUID[] DEFAULT '{}',
  enabled_organization_ids UUID[] DEFAULT '{}',
  
  -- Plan restrictions
  min_plan plan_type,
  
  -- Metadata
  metadata JSONB DEFAULT '{}',
  
  created_by UUID,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.feature_flag_overrides (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  flag_id UUID NOT NULL REFERENCES public.feature_flags(id) ON DELETE CASCADE,
  
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
  
  is_enabled BOOLEAN NOT NULL,
  reason TEXT,
  
  expires_at TIMESTAMPTZ,
  
  created_by UUID NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT unique_flag_override UNIQUE (flag_id, user_id, organization_id)
);

-- ===========================================
-- SECTION 24: INDEXES (120+ indexes)
-- ===========================================

-- Organizations
CREATE INDEX IF NOT EXISTS idx_organizations_slug ON public.organizations(slug);
CREATE INDEX IF NOT EXISTS idx_organizations_domain ON public.organizations(domain);
CREATE INDEX IF NOT EXISTS idx_organizations_plan ON public.organizations(plan);
CREATE INDEX IF NOT EXISTS idx_organizations_active ON public.organizations(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_organization_members_user ON public.organization_members(user_id);
CREATE INDEX IF NOT EXISTS idx_organization_members_org ON public.organization_members(organization_id);
CREATE INDEX IF NOT EXISTS idx_organization_invites_email ON public.organization_invites(email);
CREATE INDEX IF NOT EXISTS idx_organization_invites_token ON public.organization_invites(token);

-- Profiles
CREATE INDEX IF NOT EXISTS idx_profiles_email ON public.profiles(email);
CREATE INDEX IF NOT EXISTS idx_profiles_org ON public.profiles(organization_id);
CREATE INDEX IF NOT EXISTS idx_profiles_plan ON public.profiles(plan);
CREATE INDEX IF NOT EXISTS idx_profiles_plan_expires ON public.profiles(plan_expires_at);
CREATE INDEX IF NOT EXISTS idx_profiles_onboarding ON public.profiles(onboarding_completed);

-- Subscriptions
CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON public.subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_org ON public.subscriptions(organization_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON public.subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_plan ON public.subscriptions(plan);
CREATE INDEX IF NOT EXISTS idx_subscriptions_period_end ON public.subscriptions(current_period_end);
CREATE INDEX IF NOT EXISTS idx_subscriptions_autopay ON public.subscriptions(autopay_enabled) WHERE autopay_enabled = true;
CREATE INDEX IF NOT EXISTS idx_subscription_periods_sub ON public.subscription_periods(subscription_id);
CREATE INDEX IF NOT EXISTS idx_subscription_periods_dates ON public.subscription_periods(period_start, period_end);

-- Mandates
CREATE INDEX IF NOT EXISTS idx_payment_mandates_user ON public.payment_mandates(user_id);
CREATE INDEX IF NOT EXISTS idx_payment_mandates_sub ON public.payment_mandates(subscription_id);
CREATE INDEX IF NOT EXISTS idx_payment_mandates_status ON public.payment_mandates(status);
CREATE INDEX IF NOT EXISTS idx_payment_mandates_phonepe ON public.payment_mandates(phonepe_mandate_id);
CREATE INDEX IF NOT EXISTS idx_mandate_executions_mandate ON public.mandate_executions(mandate_id);
CREATE INDEX IF NOT EXISTS idx_mandate_executions_scheduled ON public.mandate_executions(scheduled_at);

-- Invoices
CREATE INDEX IF NOT EXISTS idx_invoices_user ON public.invoices(user_id);
CREATE INDEX IF NOT EXISTS idx_invoices_org ON public.invoices(organization_id);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON public.invoices(status);
CREATE INDEX IF NOT EXISTS idx_invoices_due_date ON public.invoices(due_date);
CREATE INDEX IF NOT EXISTS idx_invoices_number ON public.invoices(invoice_number);
CREATE INDEX IF NOT EXISTS idx_invoice_items_invoice ON public.invoice_items(invoice_id);

-- Payments
CREATE INDEX IF NOT EXISTS idx_payments_user ON public.payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_org ON public.payments(organization_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON public.payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_phonepe_txn ON public.payments(phonepe_merchant_transaction_id);
CREATE INDEX IF NOT EXISTS idx_payments_created ON public.payments(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_payments_risk ON public.payments(is_flagged) WHERE is_flagged = true;
CREATE INDEX IF NOT EXISTS idx_refunds_payment ON public.refunds(payment_id);
CREATE INDEX IF NOT EXISTS idx_payment_disputes_payment ON public.payment_disputes(payment_id);

-- Onboarding
CREATE INDEX IF NOT EXISTS idx_onboarding_intake_user ON public.onboarding_intake(user_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_intake_token ON public.onboarding_intake(share_token);
CREATE INDEX IF NOT EXISTS idx_agent_executions_intake ON public.agent_executions(intake_id);
CREATE INDEX IF NOT EXISTS idx_agent_executions_status ON public.agent_executions(status);
CREATE INDEX IF NOT EXISTS idx_shared_links_token ON public.shared_links(token);

-- ICPs & Cohorts
CREATE INDEX IF NOT EXISTS idx_icps_user ON public.icps(user_id);
CREATE INDEX IF NOT EXISTS idx_icps_org ON public.icps(organization_id);
CREATE INDEX IF NOT EXISTS idx_icps_intake ON public.icps(intake_id);
CREATE INDEX IF NOT EXISTS idx_icps_fit_score ON public.icps(fit_score DESC);
CREATE INDEX IF NOT EXISTS idx_icps_active ON public.icps(is_archived) WHERE is_archived = false;
CREATE INDEX IF NOT EXISTS idx_cohorts_user ON public.cohorts(user_id);
CREATE INDEX IF NOT EXISTS idx_cohorts_org ON public.cohorts(organization_id);
CREATE INDEX IF NOT EXISTS idx_cohorts_status ON public.cohorts(status);
CREATE INDEX IF NOT EXISTS idx_cohorts_tags ON public.cohorts USING GIN(interest_tags);

-- Campaigns & Moves
CREATE INDEX IF NOT EXISTS idx_campaigns_user ON public.campaigns(user_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_org ON public.campaigns(organization_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON public.campaigns(status);
CREATE INDEX IF NOT EXISTS idx_campaigns_dates ON public.campaigns(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_moves_user ON public.moves(user_id);
CREATE INDEX IF NOT EXISTS idx_moves_campaign ON public.moves(campaign_id);
CREATE INDEX IF NOT EXISTS idx_moves_status ON public.moves(status);
CREATE INDEX IF NOT EXISTS idx_moves_spike ON public.moves(spike_id);

-- Assets
CREATE INDEX IF NOT EXISTS idx_assets_user ON public.assets(user_id);
CREATE INDEX IF NOT EXISTS idx_assets_move ON public.assets(move_id);
CREATE INDEX IF NOT EXISTS idx_assets_campaign ON public.assets(campaign_id);
CREATE INDEX IF NOT EXISTS idx_assets_type ON public.assets(asset_type);
CREATE INDEX IF NOT EXISTS idx_assets_status ON public.assets(status);
CREATE INDEX IF NOT EXISTS idx_assets_tags ON public.assets USING GIN(tags);

-- Spikes & Guardrails
CREATE INDEX IF NOT EXISTS idx_spikes_user ON public.spikes(user_id);
CREATE INDEX IF NOT EXISTS idx_spikes_org ON public.spikes(organization_id);
CREATE INDEX IF NOT EXISTS idx_spikes_status ON public.spikes(status);
CREATE INDEX IF NOT EXISTS idx_spikes_dates ON public.spikes(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_guardrails_user ON public.guardrails(user_id);
CREATE INDEX IF NOT EXISTS idx_guardrails_spike ON public.guardrails(spike_id);
CREATE INDEX IF NOT EXISTS idx_guardrails_active ON public.guardrails(is_active) WHERE is_active = true;

-- Experiments
CREATE INDEX IF NOT EXISTS idx_experiments_user ON public.experiments(user_id);
CREATE INDEX IF NOT EXISTS idx_experiments_spike ON public.experiments(spike_id);
CREATE INDEX IF NOT EXISTS idx_experiments_status ON public.experiments(status);

-- Radar & Content
CREATE INDEX IF NOT EXISTS idx_radar_user ON public.radar_opportunities(user_id);
CREATE INDEX IF NOT EXISTS idx_radar_cohort ON public.radar_opportunities(cohort_id);
CREATE INDEX IF NOT EXISTS idx_radar_status ON public.radar_opportunities(status);
CREATE INDEX IF NOT EXISTS idx_content_ideas_user ON public.content_ideas(user_id);
CREATE INDEX IF NOT EXISTS idx_content_ideas_status ON public.content_ideas(status);

-- Security & Audit
CREATE INDEX IF NOT EXISTS idx_security_events_user ON public.security_events(user_id);
CREATE INDEX IF NOT EXISTS idx_security_events_severity ON public.security_events(severity);
CREATE INDEX IF NOT EXISTS idx_security_events_unresolved ON public.security_events(is_resolved) WHERE is_resolved = false;
CREATE INDEX IF NOT EXISTS idx_login_attempts_email ON public.login_attempts(email);
CREATE INDEX IF NOT EXISTS idx_login_attempts_ip ON public.login_attempts(ip_address);
CREATE INDEX IF NOT EXISTS idx_login_attempts_time ON public.login_attempts(attempted_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user ON public.user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_active ON public.user_sessions(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_api_keys_user ON public.api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_org ON public.api_keys(organization_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_prefix ON public.api_keys(key_prefix);
CREATE INDEX IF NOT EXISTS idx_data_access_logs_user ON public.data_access_logs(user_id);

-- Notifications & Webhooks
CREATE INDEX IF NOT EXISTS idx_notification_queue_user ON public.notification_queue(user_id);
CREATE INDEX IF NOT EXISTS idx_notification_queue_status ON public.notification_queue(status);
CREATE INDEX IF NOT EXISTS idx_notification_queue_scheduled ON public.notification_queue(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_webhooks_user ON public.webhooks(user_id);
CREATE INDEX IF NOT EXISTS idx_webhooks_org ON public.webhooks(organization_id);
CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_webhook ON public.webhook_deliveries(webhook_id);
CREATE INDEX IF NOT EXISTS idx_oauth_connections_user ON public.oauth_connections(user_id);

-- Feature Flags
CREATE INDEX IF NOT EXISTS idx_feature_flags_key ON public.feature_flags(key);
CREATE INDEX IF NOT EXISTS idx_feature_flags_status ON public.feature_flags(status);
CREATE INDEX IF NOT EXISTS idx_feature_flag_overrides_flag ON public.feature_flag_overrides(flag_id);

-- ===========================================
-- SECTION 25: ROW LEVEL SECURITY
-- ===========================================

-- Enable RLS on all tables
ALTER TABLE public.organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.organization_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.organization_invites ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscription_periods ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscription_pauses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscription_changes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payment_mandates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.mandate_notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.mandate_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.invoice_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.credit_notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payment_disputes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.refunds ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.plan_prices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.onboarding_intake ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agent_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.shared_links ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.icps ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cohorts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.barriers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.protocols ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.move_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.moves ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.spikes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.guardrails ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.guardrail_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.experiments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.radar_opportunities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.content_ideas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.data_access_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.security_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.login_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.rate_limit_buckets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notification_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notification_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notification_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.webhooks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.webhook_deliveries ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.oauth_connections ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.feature_flags ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.feature_flag_overrides ENABLE ROW LEVEL SECURITY;

-- Profiles policies
CREATE POLICY "profiles_select_own" ON public.profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "profiles_update_own" ON public.profiles FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "profiles_insert_own" ON public.profiles FOR INSERT WITH CHECK (auth.uid() = id);

-- Subscriptions policies
CREATE POLICY "subscriptions_select_own" ON public.subscriptions FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "subscriptions_insert_own" ON public.subscriptions FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Payments policies
CREATE POLICY "payments_select_own" ON public.payments FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "payments_insert_own" ON public.payments FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Plan prices are public
CREATE POLICY "plan_prices_public" ON public.plan_prices FOR SELECT TO PUBLIC USING (true);
CREATE POLICY "protocols_public" ON public.protocols FOR SELECT TO PUBLIC USING (true);
CREATE POLICY "move_templates_public" ON public.move_templates FOR SELECT TO PUBLIC USING (true);
CREATE POLICY "notification_templates_public" ON public.notification_templates FOR SELECT TO PUBLIC USING (true);
CREATE POLICY "feature_flags_public" ON public.feature_flags FOR SELECT TO PUBLIC USING (true);

-- Platform tables (user owns their data)
CREATE POLICY "onboarding_select_own" ON public.onboarding_intake FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "onboarding_insert_own" ON public.onboarding_intake FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "onboarding_update_own" ON public.onboarding_intake FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "icps_select_own" ON public.icps FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "icps_insert_own" ON public.icps FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "icps_update_own" ON public.icps FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "icps_delete_own" ON public.icps FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "cohorts_select_own" ON public.cohorts FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "cohorts_insert_own" ON public.cohorts FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "cohorts_update_own" ON public.cohorts FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "cohorts_delete_own" ON public.cohorts FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "campaigns_select_own" ON public.campaigns FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "campaigns_insert_own" ON public.campaigns FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "campaigns_update_own" ON public.campaigns FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "campaigns_delete_own" ON public.campaigns FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "moves_select_own" ON public.moves FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "moves_insert_own" ON public.moves FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "moves_update_own" ON public.moves FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "moves_delete_own" ON public.moves FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "assets_select_own" ON public.assets FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "assets_insert_own" ON public.assets FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "assets_update_own" ON public.assets FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "assets_delete_own" ON public.assets FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "spikes_select_own" ON public.spikes FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "spikes_insert_own" ON public.spikes FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "spikes_update_own" ON public.spikes FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "spikes_delete_own" ON public.spikes FOR DELETE USING (auth.uid() = user_id);

-- Security (user sees own data)
CREATE POLICY "user_sessions_own" ON public.user_sessions FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "api_keys_own" ON public.api_keys FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "notification_queue_own" ON public.notification_queue FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "notification_preferences_own" ON public.notification_preferences FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "webhooks_own" ON public.webhooks FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "oauth_connections_own" ON public.oauth_connections FOR ALL USING (auth.uid() = user_id);

-- ===========================================
-- SECTION 26: FUNCTIONS
-- ===========================================

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Handle new user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name, avatar_url)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'name'),
    NEW.raw_user_meta_data->>'avatar_url'
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Activate subscription
CREATE OR REPLACE FUNCTION public.activate_subscription(
  p_user_id UUID,
  p_plan plan_type,
  p_amount_paise BIGINT,
  p_payment_id UUID
)
RETURNS UUID AS $$
DECLARE
  v_subscription_id UUID;
  v_cohort_limit INTEGER;
  v_workspace_limit INTEGER;
  v_team_limit INTEGER;
BEGIN
  -- Get plan limits
  SELECT cohort_limit, workspace_limit, team_member_limit
  INTO v_cohort_limit, v_workspace_limit, v_team_limit
  FROM public.plan_prices WHERE plan = p_plan;
  
  -- Create subscription
  INSERT INTO public.subscriptions (
    user_id, plan, plan_name, amount_paise,
    current_period_start, current_period_end,
    cohort_limit, workspace_limit, team_member_limit,
    autopay_enabled, status
  ) VALUES (
    p_user_id, p_plan, p_plan::TEXT, p_amount_paise,
    NOW(), NOW() + INTERVAL '30 days',
    v_cohort_limit, v_workspace_limit, v_team_limit,
    (p_amount_paise <= 500000), 'active'
  ) RETURNING id INTO v_subscription_id;
  
  -- Update profile
  UPDATE public.profiles SET
    plan = p_plan,
    plan_status = 'active',
    plan_started_at = NOW(),
    plan_expires_at = NOW() + INTERVAL '30 days',
    payment_status = 'completed',
    last_payment_id = p_payment_id::TEXT,
    last_payment_amount = p_amount_paise,
    last_payment_date = NOW(),
    onboarding_completed = true,
    onboarding_completed_at = NOW()
  WHERE id = p_user_id;
  
  RETURN v_subscription_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Check RBI autopay eligibility
CREATE OR REPLACE FUNCTION public.check_autopay_eligibility(p_amount_paise BIGINT)
RETURNS JSONB AS $$
BEGIN
  RETURN jsonb_build_object(
    'eligible', p_amount_paise <= 500000,
    'limit_paise', 500000,
    'limit_display', '₹5,000',
    'requires_otp', p_amount_paise > 500000,
    'message', CASE 
      WHEN p_amount_paise <= 500000 THEN 'Eligible for seamless autopay'
      ELSE 'Monthly OTP required per RBI regulations'
    END
  );
END;
$$ LANGUAGE plpgsql;

-- Check cohort limit
CREATE OR REPLACE FUNCTION public.check_cohort_limit()
RETURNS TRIGGER AS $$
DECLARE
  user_plan plan_type;
  cohort_count INTEGER;
  plan_limit INTEGER;
BEGIN
  SELECT plan INTO user_plan FROM profiles WHERE id = NEW.user_id;
  SELECT cohort_limit INTO plan_limit FROM plan_prices WHERE plan = user_plan;
  SELECT COUNT(*) INTO cohort_count FROM cohorts WHERE user_id = NEW.user_id AND deleted_at IS NULL;
  
  IF cohort_count >= COALESCE(plan_limit, 1) THEN
    RAISE EXCEPTION 'Cohort limit reached. Your % plan allows % cohorts.', user_plan, plan_limit;
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Check expired subscriptions
CREATE OR REPLACE FUNCTION public.check_expired_subscriptions()
RETURNS void AS $$
BEGIN
  -- Expire subscriptions
  UPDATE public.subscriptions SET status = 'expired'
  WHERE status = 'active' AND current_period_end < NOW();
  
  -- Expire profiles
  UPDATE public.profiles SET plan_status = 'expired'
  WHERE plan_status = 'active' AND plan_expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

-- Generate invoice number
CREATE OR REPLACE FUNCTION public.generate_invoice_number()
RETURNS TEXT AS $$
DECLARE
  v_year TEXT := TO_CHAR(NOW(), 'YY');
  v_month TEXT := TO_CHAR(NOW(), 'MM');
  v_seq INTEGER;
BEGIN
  SELECT COALESCE(MAX(CAST(SUBSTRING(invoice_number FROM 8) AS INTEGER)), 0) + 1
  INTO v_seq
  FROM public.invoices
  WHERE invoice_number LIKE 'RF' || v_year || v_month || '%';
  
  RETURN 'RF' || v_year || v_month || LPAD(v_seq::TEXT, 5, '0');
END;
$$ LANGUAGE plpgsql;

-- ===========================================
-- SECTION 27: TRIGGERS
-- ===========================================

-- Auth user trigger
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Updated at triggers
CREATE TRIGGER trg_profiles_updated BEFORE UPDATE ON public.profiles FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER trg_organizations_updated BEFORE UPDATE ON public.organizations FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER trg_subscriptions_updated BEFORE UPDATE ON public.subscriptions FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER trg_payment_mandates_updated BEFORE UPDATE ON public.payment_mandates FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER trg_invoices_updated BEFORE UPDATE ON public.invoices FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER trg_payments_updated BEFORE UPDATE ON public.payments FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER trg_onboarding_updated BEFORE UPDATE ON public.onboarding_intake FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER trg_icps_updated BEFORE UPDATE ON public.icps FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER trg_cohorts_updated BEFORE UPDATE ON public.cohorts FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER trg_campaigns_updated BEFORE UPDATE ON public.campaigns FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER trg_moves_updated BEFORE UPDATE ON public.moves FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER trg_assets_updated BEFORE UPDATE ON public.assets FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER trg_spikes_updated BEFORE UPDATE ON public.spikes FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER trg_guardrails_updated BEFORE UPDATE ON public.guardrails FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER trg_content_ideas_updated BEFORE UPDATE ON public.content_ideas FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER trg_webhooks_updated BEFORE UPDATE ON public.webhooks FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER trg_feature_flags_updated BEFORE UPDATE ON public.feature_flags FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- Cohort limit trigger
CREATE TRIGGER trg_enforce_cohort_limit BEFORE INSERT ON public.cohorts FOR EACH ROW EXECUTE FUNCTION public.check_cohort_limit();

-- ===========================================
-- SECTION 28: SEED DATA
-- ===========================================

-- Plan prices with RBI autopay info
INSERT INTO public.plan_prices (plan, name, description, price_paise, price_display, cohort_limit, workspace_limit, team_member_limit, features, is_highlighted, badge_text, sort_order) VALUES
('ascent', 'Ascent', 'Start building your strategy', 500000, '₹5,000', 3, 1, 1,
  '["Complete 7-pillar strategy intake", "1 strategic workspace", "AI-powered plan generation", "90-day war map creation", "Up to 3 cohorts", "Radar trend matching", "PDF & Notion export", "Email support", "✅ Seamless autopay eligible"]'::jsonb,
  false, NULL, 1),
('glide', 'Glide', 'For founders who mean business', 700000, '₹7,000', 5, 3, 3,
  '["Everything in Ascent", "3 strategic workspaces", "Advanced AI strategy engine", "Up to 5 cohorts", "Real-time collaboration (up to 3)", "Integrations: Notion, Slack, Linear", "Priority support", "Monthly strategy review call", "⚠️ Monthly OTP required"]'::jsonb,
  true, 'Most Popular', 2),
('soar', 'Soar', 'The complete strategic arsenal', 1000000, '₹10,000', 10, 99, 10,
  '["Everything in Glide", "Unlimited workspaces", "Up to 10 cohorts", "Team collaboration (up to 10)", "White-label exports", "API access", "Dedicated success manager", "1-on-1 strategy onboarding call", "Quarterly strategy sessions", "⚠️ Monthly OTP required"]'::jsonb,
  false, NULL, 3)
ON CONFLICT (plan) DO UPDATE SET
  price_paise = EXCLUDED.price_paise,
  price_display = EXCLUDED.price_display,
  cohort_limit = EXCLUDED.cohort_limit,
  workspace_limit = EXCLUDED.workspace_limit,
  team_member_limit = EXCLUDED.team_member_limit,
  features = EXCLUDED.features,
  is_highlighted = EXCLUDED.is_highlighted,
  badge_text = EXCLUDED.badge_text;

-- Protocols
INSERT INTO public.protocols (code, name, description, targets_barrier, display_order) VALUES
('A_AUTHORITY_BLITZ', 'Authority Blitz', 'Build thought leadership through content-first demand creation.', 'OBSCURITY', 1),
('B_TRUST_ANCHOR', 'Trust Anchor', 'Build credibility through social proof and validation.', 'RISK', 2),
('C_COST_OF_INACTION', 'Cost of Inaction', 'Create urgency through consequences of delay.', 'INERTIA', 3),
('D_HABIT_HARDCODE', 'Habit Hard-Code', 'Drive activation and habit formation for new users.', 'FRICTION', 4),
('E_ENTERPRISE_WEDGE', 'Enterprise Wedge', 'Expand within accounts and drive enterprise deals.', 'CAPACITY', 5),
('F_CHURN_INTERCEPT', 'Churn Intercept', 'Prevent and recover churning customers.', 'ATROPHY', 6)
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, description = EXCLUDED.description;

-- Move templates
INSERT INTO public.move_templates (slug, name, description, protocol_type, barrier_type, base_impact_score, base_effort_score, display_order) VALUES
('content-waterfall', 'Content Waterfall', 'Create one pillar piece and atomize into micro-content.', 'A_AUTHORITY_BLITZ', 'OBSCURITY', 75, 60, 1),
('validation-loop', 'Validation Loop', 'Build trust through comparison pages and ROI calculators.', 'B_TRUST_ANCHOR', 'RISK', 80, 70, 2),
('spear-attack', 'Spear Attack', 'ABM-style targeted outreach with personalized reports.', 'C_COST_OF_INACTION', 'INERTIA', 85, 80, 3),
('facilitator-nudge', 'Facilitator Nudge', 'Guide new users to activation through onboarding.', 'D_HABIT_HARDCODE', 'FRICTION', 70, 65, 4),
('champions-armory', 'Champions Armory', 'Equip champions with tools to sell internally.', 'E_ENTERPRISE_WEDGE', 'CAPACITY', 90, 75, 5),
('churn-intercept-sequence', 'Churn Intercept Sequence', 'Intervene with at-risk customers before they cancel.', 'F_CHURN_INTERCEPT', 'ATROPHY', 85, 60, 6)
ON CONFLICT (slug) DO UPDATE SET name = EXCLUDED.name, description = EXCLUDED.description;

-- Notification templates
INSERT INTO public.notification_templates (slug, name, body_template, channels) VALUES
('payment_success', 'Payment Successful', 'Your payment of {{amount}} for {{plan}} has been processed successfully.', '{email,in_app}'),
('payment_failed', 'Payment Failed', 'Your payment of {{amount}} could not be processed. Please try again.', '{email,in_app}'),
('subscription_expiring', 'Subscription Expiring Soon', 'Your {{plan}} subscription expires in {{days}} days. Renew to continue.', '{email,in_app}'),
('subscription_expired', 'Subscription Expired', 'Your {{plan}} subscription has expired. Renew to regain access.', '{email,in_app}'),
('mandate_pre_debit', 'Upcoming Auto-Payment', 'Rs. {{amount}} will be debited on {{date}} for your {{plan}} subscription.', '{email,sms}')
ON CONFLICT (slug) DO UPDATE SET body_template = EXCLUDED.body_template;

-- ===========================================
-- SECTION 29: GRANTS
-- ===========================================

GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO service_role;

GRANT SELECT ON public.plan_prices TO anon;
GRANT SELECT ON public.protocols TO anon;
GRANT SELECT ON public.move_templates TO anon;
GRANT SELECT ON public.notification_templates TO anon;
GRANT SELECT ON public.feature_flags TO anon;

-- ===========================================
-- SECTION 30: CUSTOMER SUPPORT SYSTEM
-- ===========================================

-- Support tickets
CREATE TABLE IF NOT EXISTS public.support_tickets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Owner
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
  
  -- Assignment
  assigned_to UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  team_id UUID,
  
  -- Ticket details
  ticket_number SERIAL UNIQUE NOT NULL,
  subject VARCHAR(500) NOT NULL,
  description TEXT NOT NULL,
  
  -- Categorization
  category VARCHAR(100) NOT NULL DEFAULT 'general',
  subcategory VARCHAR(100),
  tags JSONB DEFAULT '[]',
  
  -- Priority & Status
  priority VARCHAR(20) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent', 'critical')),
  status VARCHAR(30) DEFAULT 'open' CHECK (status IN ('open', 'pending', 'in_progress', 'waiting_customer', 'resolved', 'closed')),
  
  -- SLA
  sla_policy_id UUID,
  sla_due_at TIMESTAMPTZ,
  sla_breached BOOLEAN DEFAULT false,
  first_response_at TIMESTAMPTZ,
  first_response_due_at TIMESTAMPTZ,
  
  -- Channel
  source VARCHAR(50) DEFAULT 'web' CHECK (source IN ('web', 'email', 'chat', 'phone', 'api')),
  
  -- Resolution
  resolution TEXT,
  resolved_at TIMESTAMPTZ,
  resolved_by UUID REFERENCES auth.users(id),
  
  -- Satisfaction
  satisfaction_rating INTEGER CHECK (satisfaction_rating BETWEEN 1 AND 5),
  satisfaction_comment TEXT,
  satisfaction_rated_at TIMESTAMPTZ,
  
  -- Metadata
  custom_fields JSONB DEFAULT '{}',
  metadata JSONB DEFAULT '{}',
  
  -- Soft delete
  deleted_at TIMESTAMPTZ,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Ticket comments/replies
CREATE TABLE IF NOT EXISTS public.ticket_comments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ticket_id UUID NOT NULL REFERENCES public.support_tickets(id) ON DELETE CASCADE,
  
  author_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  content TEXT NOT NULL,
  content_html TEXT,
  
  -- Type
  is_internal BOOLEAN DEFAULT false,
  is_automated BOOLEAN DEFAULT false,
  
  -- Attachments
  attachments JSONB DEFAULT '[]',
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Canned responses
CREATE TABLE IF NOT EXISTS public.canned_responses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
  created_by UUID NOT NULL REFERENCES auth.users(id),
  
  title VARCHAR(200) NOT NULL,
  content TEXT NOT NULL,
  content_html TEXT,
  
  shortcut VARCHAR(50),
  category VARCHAR(100),
  tags JSONB DEFAULT '[]',
  
  usage_count INTEGER DEFAULT 0,
  
  is_active BOOLEAN DEFAULT true,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- SLA policies
CREATE TABLE IF NOT EXISTS public.sla_policies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
  
  name VARCHAR(200) NOT NULL,
  description TEXT,
  
  -- Response times in minutes
  first_response_urgent INTEGER DEFAULT 60,
  first_response_high INTEGER DEFAULT 240,
  first_response_normal INTEGER DEFAULT 480,
  first_response_low INTEGER DEFAULT 1440,
  
  -- Resolution times in minutes
  resolution_urgent INTEGER DEFAULT 240,
  resolution_high INTEGER DEFAULT 960,
  resolution_normal INTEGER DEFAULT 2880,
  resolution_low INTEGER DEFAULT 10080,
  
  -- Business hours
  business_hours_only BOOLEAN DEFAULT true,
  business_hours JSONB DEFAULT '{"mon": {"start": "09:00", "end": "18:00"}}',
  timezone VARCHAR(50) DEFAULT 'Asia/Kolkata',
  holidays JSONB DEFAULT '[]',
  
  is_default BOOLEAN DEFAULT false,
  is_active BOOLEAN DEFAULT true,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Knowledge base articles
CREATE TABLE IF NOT EXISTS public.kb_articles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
  author_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  
  -- Content
  title VARCHAR(500) NOT NULL,
  slug VARCHAR(200) UNIQUE NOT NULL,
  content TEXT NOT NULL,
  content_html TEXT,
  excerpt TEXT,
  
  -- Organization
  category_id UUID,
  tags JSONB DEFAULT '[]',
  
  -- SEO
  meta_title VARCHAR(200),
  meta_description TEXT,
  
  -- Status
  status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
  published_at TIMESTAMPTZ,
  
  -- Stats
  view_count INTEGER DEFAULT 0,
  helpful_count INTEGER DEFAULT 0,
  not_helpful_count INTEGER DEFAULT 0,
  
  -- Versioning
  version INTEGER DEFAULT 1,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- SECTION 31: FILE STORAGE SYSTEM
-- ===========================================

CREATE TABLE IF NOT EXISTS public.files (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Owner
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
  
  -- File info
  filename VARCHAR(500) NOT NULL,
  original_filename VARCHAR(500) NOT NULL,
  file_path TEXT NOT NULL,
  file_size BIGINT NOT NULL,
  mime_type VARCHAR(200) NOT NULL,
  
  -- Storage
  storage_provider VARCHAR(50) DEFAULT 'supabase' CHECK (storage_provider IN ('supabase', 's3', 'gcs', 'azure')),
  bucket_name VARCHAR(200) NOT NULL,
  
  -- Dimensions (for images/videos)
  width INTEGER,
  height INTEGER,
  duration INTEGER,
  
  -- Thumbnails
  thumbnail_url TEXT,
  preview_url TEXT,
  
  -- Checksums
  checksum_md5 VARCHAR(32),
  checksum_sha256 VARCHAR(64),
  
  -- Status
  is_public BOOLEAN DEFAULT false,
  is_processed BOOLEAN DEFAULT false,
  processing_status VARCHAR(50),
  
  -- Attached to
  entity_type VARCHAR(100),
  entity_id UUID,
  
  -- Expiry
  expires_at TIMESTAMPTZ,
  
  -- Soft delete
  deleted_at TIMESTAMPTZ,
  deleted_by UUID,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- File versions
CREATE TABLE IF NOT EXISTS public.file_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  file_id UUID NOT NULL REFERENCES public.files(id) ON DELETE CASCADE,
  
  version_number INTEGER NOT NULL,
  file_path TEXT NOT NULL,
  file_size BIGINT NOT NULL,
  
  uploaded_by UUID NOT NULL REFERENCES auth.users(id),
  
  changelog TEXT,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT unique_file_version UNIQUE (file_id, version_number)
);

-- File shares
CREATE TABLE IF NOT EXISTS public.file_shares (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  file_id UUID NOT NULL REFERENCES public.files(id) ON DELETE CASCADE,
  
  -- Share settings
  share_token VARCHAR(64) UNIQUE NOT NULL DEFAULT encode(gen_random_bytes(32), 'hex'),
  share_password_hash TEXT,
  
  -- Permissions
  can_download BOOLEAN DEFAULT true,
  can_view BOOLEAN DEFAULT true,
  
  -- Limits
  download_limit INTEGER,
  download_count INTEGER DEFAULT 0,
  expires_at TIMESTAMPTZ,
  
  -- Access control
  allowed_emails TEXT[],
  
  -- Tracking
  last_accessed_at TIMESTAMPTZ,
  access_count INTEGER DEFAULT 0,
  
  created_by UUID NOT NULL REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Storage quotas
CREATE TABLE IF NOT EXISTS public.storage_quotas (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
  
  -- Limits (in bytes)
  total_quota_bytes BIGINT NOT NULL DEFAULT 5368709120, -- 5GB
  used_bytes BIGINT DEFAULT 0,
  available_bytes BIGINT GENERATED ALWAYS AS (total_quota_bytes - used_bytes) STORED,
  
  -- File limits
  max_file_size_bytes BIGINT DEFAULT 104857600, -- 100MB
  
  -- Usage by type
  usage_by_type JSONB DEFAULT '{}',
  
  last_calculated_at TIMESTAMPTZ DEFAULT NOW(),
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT storage_quota_owner CHECK (
    (user_id IS NOT NULL AND organization_id IS NULL) OR
    (user_id IS NULL AND organization_id IS NOT NULL)
  )
);

-- ===========================================
-- SECTION 32: ACTIVITY & ANALYTICS
-- ===========================================

-- User activity events
CREATE TABLE IF NOT EXISTS public.activity_events (
  id UUID NOT NULL DEFAULT gen_random_uuid(),
  occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  session_id UUID,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE SET NULL,
  
  -- Event info
  event_name VARCHAR(200) NOT NULL,
  event_category VARCHAR(100),
  event_action VARCHAR(100),
  event_label VARCHAR(500),
  event_value DECIMAL(15,4),
  
  -- Entity
  entity_type VARCHAR(100),
  entity_id UUID,
  
  -- Context
  page_url TEXT,
  page_title VARCHAR(500),
  referrer TEXT,
  
  -- Device
  device_type VARCHAR(50),
  browser VARCHAR(100),
  os VARCHAR(100),
  screen_resolution VARCHAR(20),
  
  -- Location
  ip_address INET,
  country VARCHAR(2),
  region VARCHAR(100),
  city VARCHAR(100),
  
  -- Campaign tracking
  utm_source VARCHAR(200),
  utm_medium VARCHAR(200),
  utm_campaign VARCHAR(200),
  utm_term VARCHAR(200),
  utm_content VARCHAR(200),
  
  -- Properties
  properties JSONB DEFAULT '{}',
  
  PRIMARY KEY (id, occurred_at)
) PARTITION BY RANGE (occurred_at);

-- Activity event partitions
CREATE TABLE IF NOT EXISTS public.activity_events_2024_q4 PARTITION OF public.activity_events
  FOR VALUES FROM ('2024-10-01') TO ('2025-01-01');
CREATE TABLE IF NOT EXISTS public.activity_events_2025_q1 PARTITION OF public.activity_events
  FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');
CREATE TABLE IF NOT EXISTS public.activity_events_2025_q2 PARTITION OF public.activity_events
  FOR VALUES FROM ('2025-04-01') TO ('2025-07-01');
CREATE TABLE IF NOT EXISTS public.activity_events_default PARTITION OF public.activity_events DEFAULT;

-- Feature usage tracking
CREATE TABLE IF NOT EXISTS public.feature_usage (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
  
  feature_key VARCHAR(200) NOT NULL,
  usage_count INTEGER DEFAULT 1,
  
  first_used_at TIMESTAMPTZ DEFAULT NOW(),
  last_used_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Period tracking
  period_date DATE DEFAULT CURRENT_DATE,
  daily_count INTEGER DEFAULT 1,
  weekly_count INTEGER DEFAULT 1,
  monthly_count INTEGER DEFAULT 1,
  
  CONSTRAINT unique_feature_usage UNIQUE (user_id, feature_key, period_date)
);

-- User sessions (analytics)
CREATE TABLE IF NOT EXISTS public.analytics_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  
  session_token VARCHAR(64) UNIQUE NOT NULL,
  
  -- Timing
  started_at TIMESTAMPTZ DEFAULT NOW(),
  ended_at TIMESTAMPTZ,
  duration_seconds INTEGER,
  
  -- Engagement
  page_views INTEGER DEFAULT 0,
  events_count INTEGER DEFAULT 0,
  
  -- First touch
  landing_page TEXT,
  referrer TEXT,
  
  -- Attribution
  utm_source VARCHAR(200),
  utm_medium VARCHAR(200),
  utm_campaign VARCHAR(200),
  
  -- Device
  device_type VARCHAR(50),
  browser VARCHAR(100),
  os VARCHAR(100),
  
  -- Location
  ip_address INET,
  country VARCHAR(2),
  city VARCHAR(100),
  
  is_bot BOOLEAN DEFAULT false,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- SECTION 33: ADVANCED BILLING
-- ===========================================

-- Coupons/Promo codes
CREATE TABLE IF NOT EXISTS public.coupons (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  code VARCHAR(50) UNIQUE NOT NULL,
  name VARCHAR(200) NOT NULL,
  description TEXT,
  
  -- Discount
  discount_type VARCHAR(20) NOT NULL CHECK (discount_type IN ('percentage', 'fixed_amount')),
  discount_value DECIMAL(10,2) NOT NULL,
  max_discount_amount BIGINT, -- in paise
  
  -- Applicability
  applies_to_plans plan_type[] DEFAULT '{}',
  applies_to_new_customers_only BOOLEAN DEFAULT false,
  
  -- Limits
  max_redemptions INTEGER,
  max_redemptions_per_user INTEGER DEFAULT 1,
  current_redemptions INTEGER DEFAULT 0,
  
  -- Validity
  starts_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ,
  
  -- Status
  is_active BOOLEAN DEFAULT true,
  
  -- Tracking
  created_by UUID REFERENCES auth.users(id),
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Coupon redemptions
CREATE TABLE IF NOT EXISTS public.coupon_redemptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  coupon_id UUID NOT NULL REFERENCES public.coupons(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  subscription_id UUID REFERENCES public.subscriptions(id) ON DELETE SET NULL,
  payment_id UUID REFERENCES public.payments(id) ON DELETE SET NULL,
  
  discount_applied_paise BIGINT NOT NULL,
  
  redeemed_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT unique_coupon_redemption UNIQUE (coupon_id, user_id, subscription_id)
);

-- User credits/wallet
CREATE TABLE IF NOT EXISTS public.user_credits (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
  
  balance_paise BIGINT DEFAULT 0,
  lifetime_credited_paise BIGINT DEFAULT 0,
  lifetime_used_paise BIGINT DEFAULT 0,
  
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT unique_user_credits UNIQUE (user_id)
);

-- Credit transactions
CREATE TABLE IF NOT EXISTS public.credit_transactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  transaction_type VARCHAR(30) NOT NULL CHECK (transaction_type IN ('credit', 'debit', 'refund', 'promotional', 'referral', 'expired')),
  amount_paise BIGINT NOT NULL,
  balance_after_paise BIGINT NOT NULL,
  
  description TEXT,
  
  -- Reference
  reference_type VARCHAR(50),
  reference_id UUID,
  
  expires_at TIMESTAMPTZ,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Payment methods on file
CREATE TABLE IF NOT EXISTS public.payment_methods (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  method_type payment_method_type NOT NULL,
  
  -- Display info (masked)
  display_name VARCHAR(200),
  last_four VARCHAR(4),
  card_brand VARCHAR(50),
  bank_name VARCHAR(200),
  upi_id_masked VARCHAR(200),
  
  -- Provider tokens (encrypted)
  provider VARCHAR(50) DEFAULT 'phonepe',
  provider_token_encrypted TEXT,
  
  -- Status
  is_default BOOLEAN DEFAULT false,
  is_verified BOOLEAN DEFAULT false,
  is_active BOOLEAN DEFAULT true,
  
  -- Expiry (for cards)
  expires_month INTEGER,
  expires_year INTEGER,
  
  -- Billing address
  billing_address JSONB,
  
  last_used_at TIMESTAMPTZ,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Usage-based billing
CREATE TABLE IF NOT EXISTS public.usage_records (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
  subscription_id UUID REFERENCES public.subscriptions(id) ON DELETE SET NULL,
  
  -- Metric
  usage_metric VARCHAR(100) NOT NULL,
  quantity DECIMAL(15,4) NOT NULL,
  unit VARCHAR(50) NOT NULL,
  
  -- Period
  period_start TIMESTAMPTZ NOT NULL,
  period_end TIMESTAMPTZ NOT NULL,
  
  -- Billing
  unit_price_paise BIGINT,
  total_amount_paise BIGINT,
  invoiced BOOLEAN DEFAULT false,
  invoice_id UUID,
  
  recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- SECTION 34: SCHEDULED JOBS & TASKS
-- ===========================================

CREATE TABLE IF NOT EXISTS public.scheduled_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  name VARCHAR(200) NOT NULL,
  description TEXT,
  
  -- Schedule (cron format)
  cron_expression VARCHAR(100) NOT NULL,
  timezone VARCHAR(50) DEFAULT 'Asia/Kolkata',
  
  -- Handler
  job_type VARCHAR(100) NOT NULL,
  payload JSONB DEFAULT '{}',
  
  -- Status
  is_active BOOLEAN DEFAULT true,
  is_running BOOLEAN DEFAULT false,
  
  -- Execution
  last_run_at TIMESTAMPTZ,
  last_run_status VARCHAR(50),
  last_run_duration_ms INTEGER,
  next_run_at TIMESTAMPTZ,
  
  -- Retry
  max_retries INTEGER DEFAULT 3,
  retry_delay_seconds INTEGER DEFAULT 60,
  
  -- Stats
  total_runs INTEGER DEFAULT 0,
  successful_runs INTEGER DEFAULT 0,
  failed_runs INTEGER DEFAULT 0,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Job executions history
CREATE TABLE IF NOT EXISTS public.job_executions (
  id UUID NOT NULL DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  job_id UUID NOT NULL REFERENCES public.scheduled_jobs(id) ON DELETE CASCADE,
  
  status VARCHAR(30) NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled', 'timeout')),
  
  started_at TIMESTAMPTZ NOT NULL,
  completed_at TIMESTAMPTZ,
  duration_ms INTEGER,
  
  -- Result
  result JSONB,
  error_message TEXT,
  error_stack TEXT,
  
  -- Retry
  attempt_number INTEGER DEFAULT 1,
  
  PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- Job execution partitions
CREATE TABLE IF NOT EXISTS public.job_executions_2024_q4 PARTITION OF public.job_executions
  FOR VALUES FROM ('2024-10-01') TO ('2025-01-01');
CREATE TABLE IF NOT EXISTS public.job_executions_2025_q1 PARTITION OF public.job_executions
  FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');
CREATE TABLE IF NOT EXISTS public.job_executions_default PARTITION OF public.job_executions DEFAULT;

-- Background tasks queue
CREATE TABLE IF NOT EXISTS public.task_queue (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Task info
  task_type VARCHAR(200) NOT NULL,
  payload JSONB NOT NULL,
  
  -- Priority
  priority INTEGER DEFAULT 0,
  
  -- Scheduling
  scheduled_for TIMESTAMPTZ DEFAULT NOW(),
  
  -- Status
  status VARCHAR(30) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled', 'dead_letter')),
  
  -- Worker
  locked_by VARCHAR(200),
  locked_at TIMESTAMPTZ,
  lock_expires_at TIMESTAMPTZ,
  
  -- Processing
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  
  -- Result
  result JSONB,
  error_message TEXT,
  
  -- Retry
  attempts INTEGER DEFAULT 0,
  max_attempts INTEGER DEFAULT 3,
  next_retry_at TIMESTAMPTZ,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- SECTION 35: COMPLIANCE & LEGAL (GDPR/DPDP)
-- ===========================================

-- Consent records
CREATE TABLE IF NOT EXISTS public.consent_records (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  consent_type VARCHAR(100) NOT NULL,
  consent_purpose TEXT NOT NULL,
  
  is_granted BOOLEAN NOT NULL,
  
  -- Legal basis (GDPR)
  legal_basis VARCHAR(100) CHECK (legal_basis IN ('consent', 'contract', 'legal_obligation', 'vital_interests', 'public_task', 'legitimate_interests')),
  
  -- Evidence
  ip_address INET,
  user_agent TEXT,
  consent_text TEXT,
  
  -- Validity
  granted_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ,
  withdrawn_at TIMESTAMPTZ,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Data export requests (GDPR/DPDP)
CREATE TABLE IF NOT EXISTS public.data_export_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  request_type VARCHAR(50) NOT NULL DEFAULT 'export' CHECK (request_type IN ('export', 'access')),
  
  status VARCHAR(30) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'expired')),
  
  -- Data to export
  data_categories JSONB DEFAULT '["all"]',
  
  -- Result
  download_url TEXT,
  download_expires_at TIMESTAMPTZ,
  file_size_bytes BIGINT,
  
  -- Timeline
  requested_at TIMESTAMPTZ DEFAULT NOW(),
  processed_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  
  -- Verification
  verified_at TIMESTAMPTZ,
  verification_method VARCHAR(50),
  
  -- Audit
  processed_by UUID REFERENCES auth.users(id),
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Data deletion requests (GDPR Right to be Forgotten)
CREATE TABLE IF NOT EXISTS public.data_deletion_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE SET NULL,
  user_email TEXT NOT NULL,
  
  request_type VARCHAR(50) NOT NULL DEFAULT 'full' CHECK (request_type IN ('full', 'partial')),
  
  status VARCHAR(30) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'rejected', 'on_hold')),
  
  -- Scope
  data_categories JSONB,
  retention_reason TEXT,
  
  -- Timeline (30 days per GDPR)
  requested_at TIMESTAMPTZ DEFAULT NOW(),
  due_date TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '30 days'),
  completed_at TIMESTAMPTZ,
  
  -- Verification
  verified_at TIMESTAMPTZ,
  verification_method VARCHAR(50),
  
  -- Rejection
  rejection_reason TEXT,
  
  -- Audit
  processed_by UUID REFERENCES auth.users(id),
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Terms & Policy acceptance
CREATE TABLE IF NOT EXISTS public.legal_acceptances (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  document_type VARCHAR(50) NOT NULL CHECK (document_type IN ('terms_of_service', 'privacy_policy', 'refund_policy', 'dpa', 'cookie_policy')),
  document_version VARCHAR(20) NOT NULL,
  
  accepted_at TIMESTAMPTZ DEFAULT NOW(),
  ip_address INET,
  user_agent TEXT,
  
  CONSTRAINT unique_legal_acceptance UNIQUE (user_id, document_type, document_version)
);

-- Legal document versions
CREATE TABLE IF NOT EXISTS public.legal_documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  document_type VARCHAR(50) NOT NULL,
  version VARCHAR(20) NOT NULL,
  
  title VARCHAR(200) NOT NULL,
  content TEXT NOT NULL,
  content_html TEXT,
  
  is_current BOOLEAN DEFAULT false,
  
  effective_from TIMESTAMPTZ NOT NULL,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT unique_legal_document_version UNIQUE (document_type, version)
);

-- ===========================================
-- SECTION 36: MARKETPLACE & INTEGRATIONS
-- ===========================================

-- Available apps/integrations
CREATE TABLE IF NOT EXISTS public.marketplace_apps (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  slug VARCHAR(100) UNIQUE NOT NULL,
  name VARCHAR(200) NOT NULL,
  description TEXT,
  short_description VARCHAR(500),
  
  -- Developer
  developer_name VARCHAR(200),
  developer_url TEXT,
  developer_email TEXT,
  
  -- Visuals
  icon_url TEXT,
  banner_url TEXT,
  screenshots JSONB DEFAULT '[]',
  
  -- Categorization
  category VARCHAR(100),
  tags JSONB DEFAULT '[]',
  
  -- Pricing
  pricing_type VARCHAR(20) DEFAULT 'free' CHECK (pricing_type IN ('free', 'paid', 'freemium')),
  price_monthly_paise BIGINT,
  
  -- OAuth config
  oauth_client_id TEXT,
  oauth_client_secret_hash TEXT,
  oauth_redirect_uri TEXT,
  oauth_scopes JSONB DEFAULT '[]',
  
  -- Permissions required
  required_permissions JSONB DEFAULT '[]',
  
  -- URLs
  website_url TEXT,
  documentation_url TEXT,
  support_url TEXT,
  privacy_policy_url TEXT,
  
  -- Stats
  install_count INTEGER DEFAULT 0,
  rating_average DECIMAL(3,2),
  rating_count INTEGER DEFAULT 0,
  
  -- Status
  status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'suspended')),
  is_featured BOOLEAN DEFAULT false,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Installed apps
CREATE TABLE IF NOT EXISTS public.installed_apps (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  app_id UUID NOT NULL REFERENCES public.marketplace_apps(id) ON DELETE CASCADE,
  
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
  
  -- OAuth tokens (encrypted)
  access_token_encrypted TEXT,
  refresh_token_encrypted TEXT,
  token_expires_at TIMESTAMPTZ,
  
  -- Permissions granted
  granted_permissions JSONB DEFAULT '[]',
  
  -- Settings
  settings JSONB DEFAULT '{}',
  
  -- Status
  is_active BOOLEAN DEFAULT true,
  
  installed_by UUID NOT NULL REFERENCES auth.users(id),
  installed_at TIMESTAMPTZ DEFAULT NOW(),
  
  last_synced_at TIMESTAMPTZ,
  
  uninstalled_at TIMESTAMPTZ,
  uninstalled_by UUID REFERENCES auth.users(id),
  
  CONSTRAINT unique_installed_app UNIQUE (app_id, user_id, organization_id)
);

-- App webhooks (incoming)
CREATE TABLE IF NOT EXISTS public.app_webhooks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  installed_app_id UUID NOT NULL REFERENCES public.installed_apps(id) ON DELETE CASCADE,
  
  -- Webhook config
  endpoint_path VARCHAR(200) NOT NULL,
  secret_hash TEXT NOT NULL,
  
  -- Event filtering
  event_types JSONB DEFAULT '[]',
  
  -- Status
  is_active BOOLEAN DEFAULT true,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Integration sync logs
CREATE TABLE IF NOT EXISTS public.sync_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  installed_app_id UUID NOT NULL REFERENCES public.installed_apps(id) ON DELETE CASCADE,
  
  sync_type VARCHAR(50) NOT NULL,
  direction VARCHAR(10) NOT NULL CHECK (direction IN ('inbound', 'outbound', 'bidirectional')),
  
  status VARCHAR(30) NOT NULL CHECK (status IN ('started', 'in_progress', 'completed', 'failed', 'partial')),
  
  -- Stats
  records_processed INTEGER DEFAULT 0,
  records_created INTEGER DEFAULT 0,
  records_updated INTEGER DEFAULT 0,
  records_failed INTEGER DEFAULT 0,
  
  -- Errors
  errors JSONB DEFAULT '[]',
  
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  duration_ms INTEGER,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- SECTION 37: COMMENTS & COLLABORATION
-- ===========================================

-- Generic comments (on any entity)
CREATE TABLE IF NOT EXISTS public.comments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Author
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- Target entity (polymorphic)
  entity_type VARCHAR(100) NOT NULL,
  entity_id UUID NOT NULL,
  
  -- Thread
  parent_id UUID REFERENCES public.comments(id) ON DELETE CASCADE,
  thread_id UUID,
  reply_count INTEGER DEFAULT 0,
  
  -- Content
  content TEXT NOT NULL,
  content_html TEXT,
  
  -- Mentions
  mentioned_users UUID[] DEFAULT '{}',
  
  -- Attachments
  attachments JSONB DEFAULT '[]',
  
  -- Status
  is_pinned BOOLEAN DEFAULT false,
  is_resolved BOOLEAN DEFAULT false,
  resolved_at TIMESTAMPTZ,
  resolved_by UUID REFERENCES auth.users(id),
  
  -- Edit history
  is_edited BOOLEAN DEFAULT false,
  edited_at TIMESTAMPTZ,
  edit_count INTEGER DEFAULT 0,
  
  -- Soft delete
  deleted_at TIMESTAMPTZ,
  deleted_by UUID REFERENCES auth.users(id),
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Reactions
CREATE TABLE IF NOT EXISTS public.reactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- Target
  entity_type VARCHAR(100) NOT NULL,
  entity_id UUID NOT NULL,
  
  -- Reaction
  reaction_type VARCHAR(50) NOT NULL,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT unique_reaction UNIQUE (user_id, entity_type, entity_id, reaction_type)
);

-- Mentions
CREATE TABLE IF NOT EXISTS public.mentions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  mentioned_user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  mentioned_by_user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- Source
  entity_type VARCHAR(100) NOT NULL,
  entity_id UUID NOT NULL,
  comment_id UUID REFERENCES public.comments(id) ON DELETE CASCADE,
  
  -- Status
  is_read BOOLEAN DEFAULT false,
  read_at TIMESTAMPTZ,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Real-time presence
CREATE TABLE IF NOT EXISTS public.presence (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
  
  -- Status
  status VARCHAR(20) DEFAULT 'online' CHECK (status IN ('online', 'away', 'busy', 'offline')),
  status_message TEXT,
  status_emoji VARCHAR(10),
  
  -- Current context
  current_page TEXT,
  current_entity_type VARCHAR(100),
  current_entity_id UUID,
  
  -- Timing
  last_seen_at TIMESTAMPTZ DEFAULT NOW(),
  session_started_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Device
  device_type VARCHAR(50),
  
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- SECTION 38: SEARCH SYSTEM
-- ===========================================

-- Search index entries
CREATE TABLE IF NOT EXISTS public.search_index (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Entity
  entity_type VARCHAR(100) NOT NULL,
  entity_id UUID NOT NULL,
  
  -- Owner
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
  
  -- Searchable content
  title TEXT NOT NULL,
  content TEXT,
  tags JSONB DEFAULT '[]',
  
  -- Full-text search vector
  search_vector tsvector GENERATED ALWAYS AS (
    setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(content, '')), 'B')
  ) STORED,
  
  -- Metadata
  metadata JSONB DEFAULT '{}',
  
  -- Ranking
  boost_factor DECIMAL(3,2) DEFAULT 1.0,
  
  indexed_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT unique_search_entry UNIQUE (entity_type, entity_id)
);

-- Create GIN index for full-text search
CREATE INDEX IF NOT EXISTS idx_search_vector ON public.search_index USING GIN(search_vector);

-- Saved searches
CREATE TABLE IF NOT EXISTS public.saved_searches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  name VARCHAR(200) NOT NULL,
  query TEXT NOT NULL,
  filters JSONB DEFAULT '{}',
  
  -- Notification
  notify_new_results BOOLEAN DEFAULT false,
  notification_frequency VARCHAR(20) DEFAULT 'daily',
  last_notified_at TIMESTAMPTZ,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Recent searches
CREATE TABLE IF NOT EXISTS public.recent_searches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  query TEXT NOT NULL,
  filters JSONB DEFAULT '{}',
  results_count INTEGER DEFAULT 0,
  
  searched_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- SECTION 39: REPORTING SYSTEM
-- ===========================================

-- Report configurations
CREATE TABLE IF NOT EXISTS public.report_configs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
  
  name VARCHAR(200) NOT NULL,
  description TEXT,
  
  report_type VARCHAR(100) NOT NULL,
  
  -- Configuration
  data_source VARCHAR(100) NOT NULL,
  query_config JSONB NOT NULL,
  filters JSONB DEFAULT '{}',
  columns JSONB DEFAULT '[]',
  grouping JSONB DEFAULT '[]',
  sorting JSONB DEFAULT '[]',
  
  -- Display
  chart_type VARCHAR(50),
  chart_config JSONB DEFAULT '{}',
  
  -- Scheduling
  is_scheduled BOOLEAN DEFAULT false,
  schedule_cron VARCHAR(100),
  schedule_timezone VARCHAR(50) DEFAULT 'Asia/Kolkata',
  schedule_recipients JSONB DEFAULT '[]',
  
  -- Status
  is_saved BOOLEAN DEFAULT true,
  is_default BOOLEAN DEFAULT false,
  
  last_run_at TIMESTAMPTZ,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Generated reports
CREATE TABLE IF NOT EXISTS public.generated_reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  config_id UUID REFERENCES public.report_configs(id) ON DELETE SET NULL,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  report_type VARCHAR(100) NOT NULL,
  
  -- Parameters
  parameters JSONB DEFAULT '{}',
  date_range_start TIMESTAMPTZ,
  date_range_end TIMESTAMPTZ,
  
  -- Result
  status VARCHAR(30) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
  row_count INTEGER,
  
  -- Files
  file_url TEXT,
  file_format VARCHAR(20),
  file_size_bytes BIGINT,
  
  -- Expiry
  expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '7 days'),
  
  -- Timing
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  duration_ms INTEGER,
  
  error_message TEXT,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Dashboard widgets
CREATE TABLE IF NOT EXISTS public.dashboard_widgets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
  
  dashboard_id UUID,
  
  name VARCHAR(200) NOT NULL,
  widget_type VARCHAR(100) NOT NULL,
  
  -- Configuration
  config JSONB NOT NULL,
  data_source VARCHAR(100),
  query_config JSONB DEFAULT '{}',
  
  -- Layout
  position_x INTEGER DEFAULT 0,
  position_y INTEGER DEFAULT 0,
  width INTEGER DEFAULT 4,
  height INTEGER DEFAULT 3,
  
  -- Refresh
  refresh_interval_seconds INTEGER DEFAULT 300,
  last_refreshed_at TIMESTAMPTZ,
  
  is_visible BOOLEAN DEFAULT true,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- SECTION 40: CHANGELOG & ANNOUNCEMENTS
-- ===========================================

CREATE TABLE IF NOT EXISTS public.changelog_entries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  version VARCHAR(20),
  title VARCHAR(500) NOT NULL,
  content TEXT NOT NULL,
  content_html TEXT,
  
  -- Categorization
  category VARCHAR(50) CHECK (category IN ('feature', 'improvement', 'bugfix', 'security', 'announcement')),
  tags JSONB DEFAULT '[]',
  
  -- Status
  status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'scheduled', 'published')),
  published_at TIMESTAMPTZ,
  
  -- Targeting
  visible_to_plans plan_type[] DEFAULT '{}',
  
  -- Media
  image_url TEXT,
  video_url TEXT,
  
  -- Author
  author_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User changelog reads
CREATE TABLE IF NOT EXISTS public.changelog_reads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  entry_id UUID NOT NULL REFERENCES public.changelog_entries(id) ON DELETE CASCADE,
  
  read_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT unique_changelog_read UNIQUE (user_id, entry_id)
);

-- In-app announcements
CREATE TABLE IF NOT EXISTS public.announcements (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  title VARCHAR(500) NOT NULL,
  content TEXT NOT NULL,
  
  -- Type
  announcement_type VARCHAR(30) DEFAULT 'info' CHECK (announcement_type IN ('info', 'warning', 'success', 'error', 'maintenance')),
  
  -- Display
  display_location VARCHAR(50) DEFAULT 'banner' CHECK (display_location IN ('banner', 'modal', 'toast', 'sidebar')),
  is_dismissible BOOLEAN DEFAULT true,
  
  -- Action
  action_text VARCHAR(100),
  action_url TEXT,
  
  -- Targeting
  target_plans plan_type[] DEFAULT '{}',
  target_user_ids UUID[] DEFAULT '{}',
  
  -- Timing
  starts_at TIMESTAMPTZ DEFAULT NOW(),
  ends_at TIMESTAMPTZ,
  
  -- Status
  is_active BOOLEAN DEFAULT true,
  
  -- Stats
  view_count INTEGER DEFAULT 0,
  click_count INTEGER DEFAULT 0,
  dismiss_count INTEGER DEFAULT 0,
  
  created_by UUID REFERENCES auth.users(id),
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.announcement_dismissals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  announcement_id UUID NOT NULL REFERENCES public.announcements(id) ON DELETE CASCADE,
  
  dismissed_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT unique_announcement_dismissal UNIQUE (user_id, announcement_id)
);

-- ===========================================
-- SECTION 41: REFERRAL SYSTEM
-- ===========================================

CREATE TABLE IF NOT EXISTS public.referral_codes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  code VARCHAR(20) UNIQUE NOT NULL,
  
  -- Rewards
  referrer_reward_paise BIGINT DEFAULT 50000, -- ₹500
  referee_reward_paise BIGINT DEFAULT 50000,
  
  -- Limits
  max_uses INTEGER,
  current_uses INTEGER DEFAULT 0,
  
  -- Validity
  expires_at TIMESTAMPTZ,
  
  is_active BOOLEAN DEFAULT true,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.referrals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  referrer_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  referee_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  referral_code_id UUID NOT NULL REFERENCES public.referral_codes(id) ON DELETE CASCADE,
  
  -- Status
  status VARCHAR(30) DEFAULT 'signed_up' CHECK (status IN ('signed_up', 'qualified', 'rewarded', 'expired')),
  
  -- Rewards
  referrer_rewarded BOOLEAN DEFAULT false,
  referrer_reward_amount_paise BIGINT,
  referrer_reward_at TIMESTAMPTZ,
  
  referee_rewarded BOOLEAN DEFAULT false,
  referee_reward_amount_paise BIGINT,
  referee_reward_at TIMESTAMPTZ,
  
  -- Qualification (e.g., first payment)
  qualified_at TIMESTAMPTZ,
  qualification_event VARCHAR(100),
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT unique_referral UNIQUE (referrer_id, referee_id)
);

-- ===========================================
-- SECTION 42: ADDITIONAL INDEXES
-- ===========================================

-- Support
CREATE INDEX IF NOT EXISTS idx_tickets_user ON public.support_tickets(user_id);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON public.support_tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_priority ON public.support_tickets(priority);
CREATE INDEX IF NOT EXISTS idx_tickets_assigned ON public.support_tickets(assigned_to);
CREATE INDEX IF NOT EXISTS idx_ticket_comments_ticket ON public.ticket_comments(ticket_id);
CREATE INDEX IF NOT EXISTS idx_kb_articles_slug ON public.kb_articles(slug);
CREATE INDEX IF NOT EXISTS idx_kb_articles_status ON public.kb_articles(status);

-- Files
CREATE INDEX IF NOT EXISTS idx_files_user ON public.files(user_id);
CREATE INDEX IF NOT EXISTS idx_files_entity ON public.files(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_file_shares_token ON public.file_shares(share_token);

-- Activity
CREATE INDEX IF NOT EXISTS idx_activity_user ON public.activity_events(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_event ON public.activity_events(event_name);
CREATE INDEX IF NOT EXISTS idx_feature_usage_user ON public.feature_usage(user_id);

-- Billing
CREATE INDEX IF NOT EXISTS idx_coupons_code ON public.coupons(code);
CREATE INDEX IF NOT EXISTS idx_coupon_redemptions_user ON public.coupon_redemptions(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_user ON public.credit_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_payment_methods_user ON public.payment_methods(user_id);

-- Jobs
CREATE INDEX IF NOT EXISTS idx_scheduled_jobs_next_run ON public.scheduled_jobs(next_run_at);
CREATE INDEX IF NOT EXISTS idx_task_queue_status ON public.task_queue(status, scheduled_for);

-- Compliance
CREATE INDEX IF NOT EXISTS idx_consent_records_user ON public.consent_records(user_id);
CREATE INDEX IF NOT EXISTS idx_data_export_user ON public.data_export_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_data_deletion_status ON public.data_deletion_requests(status);

-- Marketplace
CREATE INDEX IF NOT EXISTS idx_installed_apps_user ON public.installed_apps(user_id);
CREATE INDEX IF NOT EXISTS idx_installed_apps_org ON public.installed_apps(organization_id);
CREATE INDEX IF NOT EXISTS idx_sync_logs_app ON public.sync_logs(installed_app_id);

-- Comments
CREATE INDEX IF NOT EXISTS idx_comments_entity ON public.comments(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_comments_user ON public.comments(user_id);
CREATE INDEX IF NOT EXISTS idx_reactions_entity ON public.reactions(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_mentions_user ON public.mentions(mentioned_user_id);
CREATE INDEX IF NOT EXISTS idx_presence_user ON public.presence(user_id);

-- Search
CREATE INDEX IF NOT EXISTS idx_search_entity ON public.search_index(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_recent_searches_user ON public.recent_searches(user_id);

-- Reports
CREATE INDEX IF NOT EXISTS idx_report_configs_user ON public.report_configs(user_id);
CREATE INDEX IF NOT EXISTS idx_generated_reports_user ON public.generated_reports(user_id);

-- Changelog
CREATE INDEX IF NOT EXISTS idx_changelog_published ON public.changelog_entries(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_changelog_reads_user ON public.changelog_reads(user_id);

-- Referrals
CREATE INDEX IF NOT EXISTS idx_referral_codes_user ON public.referral_codes(user_id);
CREATE INDEX IF NOT EXISTS idx_referrals_referrer ON public.referrals(referrer_id);

-- ===========================================
-- SECTION 43: RLS FOR NEW TABLES
-- ===========================================

ALTER TABLE public.support_tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ticket_comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.canned_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sla_policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.kb_articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.files ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.file_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.file_shares ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.storage_quotas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.activity_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.feature_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analytics_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.coupons ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.coupon_redemptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_credits ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.credit_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payment_methods ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.usage_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scheduled_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.job_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.task_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.consent_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.data_export_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.data_deletion_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.legal_acceptances ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.legal_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.marketplace_apps ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.installed_apps ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.app_webhooks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sync_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.mentions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.presence ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.search_index ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.saved_searches ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.recent_searches ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.report_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.generated_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dashboard_widgets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.changelog_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.changelog_reads ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.announcements ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.announcement_dismissals ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.referral_codes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.referrals ENABLE ROW LEVEL SECURITY;

-- RLS Policies for user-owned data
CREATE POLICY "support_tickets_own" ON public.support_tickets FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "files_own" ON public.files FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "file_shares_own" ON public.file_shares FOR ALL USING (auth.uid() = created_by);
CREATE POLICY "storage_quotas_own" ON public.storage_quotas FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "activity_events_own" ON public.activity_events FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "feature_usage_own" ON public.feature_usage FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "user_credits_own" ON public.user_credits FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "credit_transactions_own" ON public.credit_transactions FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "payment_methods_own" ON public.payment_methods FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "consent_records_own" ON public.consent_records FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "data_export_own" ON public.data_export_requests FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "data_deletion_own" ON public.data_deletion_requests FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "legal_acceptances_own" ON public.legal_acceptances FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "installed_apps_own" ON public.installed_apps FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "comments_own" ON public.comments FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "reactions_own" ON public.reactions FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "mentions_own" ON public.mentions FOR SELECT USING (auth.uid() = mentioned_user_id);
CREATE POLICY "presence_own" ON public.presence FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "saved_searches_own" ON public.saved_searches FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "recent_searches_own" ON public.recent_searches FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "report_configs_own" ON public.report_configs FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "generated_reports_own" ON public.generated_reports FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "dashboard_widgets_own" ON public.dashboard_widgets FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "changelog_reads_own" ON public.changelog_reads FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "announcement_dismissals_own" ON public.announcement_dismissals FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "referral_codes_own" ON public.referral_codes FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "referrals_own" ON public.referrals FOR SELECT USING (auth.uid() = referrer_id OR auth.uid() = referee_id);

-- Public read policies
CREATE POLICY "kb_articles_public" ON public.kb_articles FOR SELECT TO PUBLIC USING (status = 'published');
CREATE POLICY "marketplace_apps_public" ON public.marketplace_apps FOR SELECT TO PUBLIC USING (status = 'approved');
CREATE POLICY "legal_documents_public" ON public.legal_documents FOR SELECT TO PUBLIC USING (is_current = true);
CREATE POLICY "changelog_public" ON public.changelog_entries FOR SELECT TO PUBLIC USING (status = 'published');
CREATE POLICY "announcements_public" ON public.announcements FOR SELECT TO PUBLIC USING (is_active = true AND starts_at <= NOW() AND (ends_at IS NULL OR ends_at > NOW()));
CREATE POLICY "coupons_public" ON public.coupons FOR SELECT TO PUBLIC USING (is_active = true AND (expires_at IS NULL OR expires_at > NOW()));

-- ===========================================
-- SECTION 44: EMAIL SYSTEM
-- ===========================================

-- Email templates with versioning
CREATE TABLE IF NOT EXISTS public.email_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  slug VARCHAR(100) UNIQUE NOT NULL,
  name VARCHAR(200) NOT NULL,
  description TEXT,
  
  -- Content
  subject VARCHAR(500) NOT NULL,
  body_text TEXT NOT NULL,
  body_html TEXT,
  
  -- Variables
  variables JSONB DEFAULT '[]',
  
  -- Settings
  from_name VARCHAR(200) DEFAULT 'Raptorflow',
  from_email VARCHAR(200) DEFAULT 'hello@raptorflow.in',
  reply_to VARCHAR(200),
  
  -- Categories
  category VARCHAR(100) NOT NULL DEFAULT 'transactional',
  
  -- Status
  is_active BOOLEAN DEFAULT true,
  version INTEGER DEFAULT 1,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Email queue with retry logic
CREATE TABLE IF NOT EXISTS public.email_queue (
  id UUID NOT NULL DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  -- Recipient
  to_email VARCHAR(500) NOT NULL,
  to_name VARCHAR(200),
  cc_emails TEXT[],
  bcc_emails TEXT[],
  
  -- Content
  template_id UUID REFERENCES public.email_templates(id),
  subject VARCHAR(500) NOT NULL,
  body_text TEXT NOT NULL,
  body_html TEXT,
  
  -- Variables
  template_data JSONB DEFAULT '{}',
  
  -- Attachments
  attachments JSONB DEFAULT '[]',
  
  -- Priority (0=low, 10=urgent)
  priority INTEGER DEFAULT 5,
  
  -- Scheduling
  scheduled_for TIMESTAMPTZ DEFAULT NOW(),
  
  -- Status
  status VARCHAR(30) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'sent', 'failed', 'bounced', 'cancelled')),
  
  -- Provider
  provider VARCHAR(50) DEFAULT 'ses',
  provider_message_id VARCHAR(200),
  
  -- Retry
  attempts INTEGER DEFAULT 0,
  max_attempts INTEGER DEFAULT 3,
  last_attempt_at TIMESTAMPTZ,
  next_retry_at TIMESTAMPTZ,
  error_message TEXT,
  
  -- Tracking
  sent_at TIMESTAMPTZ,
  opened_at TIMESTAMPTZ,
  clicked_at TIMESTAMPTZ,
  
  -- Ownership
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  
  PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

CREATE TABLE IF NOT EXISTS public.email_queue_2024_q4 PARTITION OF public.email_queue
  FOR VALUES FROM ('2024-10-01') TO ('2025-01-01');
CREATE TABLE IF NOT EXISTS public.email_queue_2025_q1 PARTITION OF public.email_queue
  FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');
CREATE TABLE IF NOT EXISTS public.email_queue_default PARTITION OF public.email_queue DEFAULT;

-- Email events (opens, clicks, bounces)
CREATE TABLE IF NOT EXISTS public.email_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  email_queue_id UUID NOT NULL,
  
  event_type VARCHAR(50) NOT NULL CHECK (event_type IN ('delivered', 'opened', 'clicked', 'bounced', 'complained', 'unsubscribed')),
  
  -- Details
  ip_address INET,
  user_agent TEXT,
  link_url TEXT,
  
  -- Bounce info
  bounce_type VARCHAR(50),
  bounce_subtype VARCHAR(100),
  
  occurred_at TIMESTAMPTZ DEFAULT NOW()
);

-- Email suppressions (bounces, unsubscribes)
CREATE TABLE IF NOT EXISTS public.email_suppressions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  email VARCHAR(500) UNIQUE NOT NULL,
  
  suppression_type VARCHAR(50) NOT NULL CHECK (suppression_type IN ('bounce', 'complaint', 'unsubscribe', 'manual')),
  
  reason TEXT,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- SECTION 45: A/B TESTING FRAMEWORK
-- ===========================================

CREATE TABLE IF NOT EXISTS public.ab_tests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  name VARCHAR(200) NOT NULL,
  description TEXT,
  hypothesis TEXT,
  
  -- Test type
  test_type VARCHAR(50) NOT NULL CHECK (test_type IN ('feature', 'ui', 'pricing', 'copy', 'flow')),
  
  -- Target
  feature_key VARCHAR(200),
  
  -- Variants (including control)
  variants JSONB NOT NULL DEFAULT '[{"id": "control", "name": "Control", "weight": 50}, {"id": "variant_a", "name": "Variant A", "weight": 50}]',
  
  -- Traffic allocation (0-100%)
  traffic_percentage INTEGER DEFAULT 100 CHECK (traffic_percentage BETWEEN 0 AND 100),
  
  -- Targeting
  target_plans plan_type[] DEFAULT '{}',
  target_cohorts UUID[] DEFAULT '{}',
  target_new_users_only BOOLEAN DEFAULT false,
  
  -- Goals
  primary_metric VARCHAR(200),
  secondary_metrics JSONB DEFAULT '[]',
  
  -- Statistical config
  minimum_sample_size INTEGER DEFAULT 1000,
  confidence_level DECIMAL(5,4) DEFAULT 0.95,
  
  -- Timeline
  starts_at TIMESTAMPTZ,
  ends_at TIMESTAMPTZ,
  
  -- Status
  status VARCHAR(30) DEFAULT 'draft' CHECK (status IN ('draft', 'running', 'paused', 'completed', 'archived')),
  
  -- Results
  winner_variant VARCHAR(100),
  statistical_significance DECIMAL(5,4),
  
  created_by UUID REFERENCES auth.users(id),
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User test assignments
CREATE TABLE IF NOT EXISTS public.ab_test_assignments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  test_id UUID NOT NULL REFERENCES public.ab_tests(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  variant_id VARCHAR(100) NOT NULL,
  
  assigned_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Conversion tracking
  converted BOOLEAN DEFAULT false,
  converted_at TIMESTAMPTZ,
  conversion_value DECIMAL(15,4),
  
  CONSTRAINT unique_test_assignment UNIQUE (test_id, user_id)
);

-- ===========================================
-- SECTION 46: WAITLIST & BETA ACCESS
-- ===========================================

CREATE TABLE IF NOT EXISTS public.waitlist (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  email VARCHAR(500) UNIQUE NOT NULL,
  name VARCHAR(200),
  company VARCHAR(200),
  
  -- Source
  referral_code VARCHAR(50),
  utm_source VARCHAR(200),
  utm_medium VARCHAR(200),
  utm_campaign VARCHAR(200),
  
  -- Priority
  priority_score INTEGER DEFAULT 0,
  
  -- Status
  status VARCHAR(30) DEFAULT 'waiting' CHECK (status IN ('waiting', 'invited', 'registered', 'removed')),
  
  -- Tracking
  position INTEGER,
  invited_at TIMESTAMPTZ,
  registered_at TIMESTAMPTZ,
  
  ip_address INET,
  user_agent TEXT,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.beta_features (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  feature_key VARCHAR(200) UNIQUE NOT NULL,
  name VARCHAR(200) NOT NULL,
  description TEXT,
  
  -- Access
  is_public BOOLEAN DEFAULT false,
  allowed_users UUID[] DEFAULT '{}',
  allowed_organizations UUID[] DEFAULT '{}',
  allowed_plans plan_type[] DEFAULT '{}',
  max_users INTEGER,
  current_users INTEGER DEFAULT 0,
  
  -- Status
  status VARCHAR(30) DEFAULT 'alpha' CHECK (status IN ('alpha', 'beta', 'ga', 'deprecated')),
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- SECTION 47: SURVEYS & NPS
-- ===========================================

CREATE TABLE IF NOT EXISTS public.surveys (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  name VARCHAR(200) NOT NULL,
  description TEXT,
  
  survey_type VARCHAR(50) NOT NULL CHECK (survey_type IN ('nps', 'csat', 'ces', 'custom')),
  
  -- Questions
  questions JSONB NOT NULL,
  
  -- Targeting
  trigger_event VARCHAR(200),
  trigger_delay_seconds INTEGER DEFAULT 0,
  show_once BOOLEAN DEFAULT true,
  target_plans plan_type[] DEFAULT '{}',
  
  -- Sampling
  sample_rate INTEGER DEFAULT 100 CHECK (sample_rate BETWEEN 0 AND 100),
  
  -- Status
  is_active BOOLEAN DEFAULT true,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.survey_responses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  survey_id UUID NOT NULL REFERENCES public.surveys(id) ON DELETE CASCADE,
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  
  -- Responses
  responses JSONB NOT NULL,
  
  -- NPS specific
  nps_score INTEGER CHECK (nps_score BETWEEN 0 AND 10),
  nps_category VARCHAR(20) GENERATED ALWAYS AS (
    CASE 
      WHEN nps_score >= 9 THEN 'promoter'
      WHEN nps_score >= 7 THEN 'passive'
      ELSE 'detractor'
    END
  ) STORED,
  
  -- Context
  page_url TEXT,
  session_id UUID,
  
  -- Metadata
  ip_address INET,
  user_agent TEXT,
  
  submitted_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- SECTION 48: PRODUCT TOURS & ONBOARDING FLOWS
-- ===========================================

CREATE TABLE IF NOT EXISTS public.product_tours (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  slug VARCHAR(100) UNIQUE NOT NULL,
  name VARCHAR(200) NOT NULL,
  description TEXT,
  
  -- Steps
  steps JSONB NOT NULL,
  
  -- Trigger
  trigger_url TEXT,
  trigger_event VARCHAR(200),
  trigger_for_new_users BOOLEAN DEFAULT true,
  
  -- Targeting
  target_plans plan_type[] DEFAULT '{}',
  
  -- Status
  is_active BOOLEAN DEFAULT true,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.tour_progress (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  tour_id UUID NOT NULL REFERENCES public.product_tours(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- Progress
  current_step INTEGER DEFAULT 0,
  completed_steps INTEGER[] DEFAULT '{}',
  
  -- Status
  status VARCHAR(30) DEFAULT 'started' CHECK (status IN ('started', 'in_progress', 'completed', 'skipped', 'dismissed')),
  
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  
  CONSTRAINT unique_tour_progress UNIQUE (tour_id, user_id)
);

-- ===========================================
-- SECTION 49: USER PREFERENCES & THEMES
-- ===========================================

CREATE TABLE IF NOT EXISTS public.user_preferences (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
  
  -- Theme
  theme VARCHAR(20) DEFAULT 'system' CHECK (theme IN ('light', 'dark', 'system')),
  accent_color VARCHAR(20) DEFAULT 'amber',
  
  -- Layout
  sidebar_collapsed BOOLEAN DEFAULT false,
  compact_mode BOOLEAN DEFAULT false,
  
  -- Accessibility
  reduce_motion BOOLEAN DEFAULT false,
  high_contrast BOOLEAN DEFAULT false,
  font_size VARCHAR(20) DEFAULT 'normal',
  
  -- Notifications
  desktop_notifications BOOLEAN DEFAULT true,
  sound_enabled BOOLEAN DEFAULT true,
  
  -- Keyboard shortcuts
  shortcuts_enabled BOOLEAN DEFAULT true,
  custom_shortcuts JSONB DEFAULT '{}',
  
  -- Dashboard
  default_dashboard VARCHAR(100),
  pinned_items UUID[] DEFAULT '{}',
  
  -- Regional
  language VARCHAR(10) DEFAULT 'en',
  timezone VARCHAR(50) DEFAULT 'Asia/Kolkata',
  date_format VARCHAR(20) DEFAULT 'DD/MM/YYYY',
  time_format VARCHAR(10) DEFAULT '12h',
  
  -- Currency
  currency VARCHAR(3) DEFAULT 'INR',
  
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- SECTION 50: LOCALIZATION
-- ===========================================

CREATE TABLE IF NOT EXISTS public.locales (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  code VARCHAR(10) UNIQUE NOT NULL,
  name VARCHAR(100) NOT NULL,
  native_name VARCHAR(100) NOT NULL,
  
  -- Display
  direction VARCHAR(3) DEFAULT 'ltr' CHECK (direction IN ('ltr', 'rtl')),
  
  -- Status
  is_default BOOLEAN DEFAULT false,
  is_active BOOLEAN DEFAULT true,
  
  -- Completion
  translation_progress INTEGER DEFAULT 0 CHECK (translation_progress BETWEEN 0 AND 100),
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.translations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  locale_code VARCHAR(10) NOT NULL,
  
  namespace VARCHAR(100) NOT NULL,
  key VARCHAR(500) NOT NULL,
  value TEXT NOT NULL,
  
  -- Context
  context TEXT,
  
  -- Status
  is_approved BOOLEAN DEFAULT false,
  approved_by UUID REFERENCES auth.users(id),
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT unique_translation UNIQUE (locale_code, namespace, key)
);

-- ===========================================
-- SECTION 51: CURRENCIES & TAX RATES
-- ===========================================

CREATE TABLE IF NOT EXISTS public.currencies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  code VARCHAR(3) UNIQUE NOT NULL,
  name VARCHAR(100) NOT NULL,
  symbol VARCHAR(10) NOT NULL,
  
  decimal_places INTEGER DEFAULT 2,
  
  -- Exchange rate to INR
  exchange_rate_to_inr DECIMAL(15,6) DEFAULT 1,
  exchange_rate_updated_at TIMESTAMPTZ,
  
  is_active BOOLEAN DEFAULT true,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.tax_rates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  name VARCHAR(100) NOT NULL,
  description TEXT,
  
  -- Rate
  rate_percentage DECIMAL(5,2) NOT NULL,
  
  -- Applicability
  country VARCHAR(2) NOT NULL DEFAULT 'IN',
  state VARCHAR(100),
  
  -- GST specific
  tax_type VARCHAR(20) CHECK (tax_type IN ('cgst', 'sgst', 'igst', 'cess', 'vat', 'sales_tax')),
  hsn_code VARCHAR(20),
  
  -- Validity
  effective_from TIMESTAMPTZ DEFAULT NOW(),
  effective_to TIMESTAMPTZ,
  
  is_active BOOLEAN DEFAULT true,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- SECTION 52: ERROR TRACKING & MONITORING
-- ===========================================

CREATE TABLE IF NOT EXISTS public.error_logs (
  id UUID NOT NULL DEFAULT gen_random_uuid(),
  occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  -- Error info
  error_type VARCHAR(200) NOT NULL,
  error_message TEXT NOT NULL,
  error_stack TEXT,
  
  -- Context
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  session_id UUID,
  
  -- Request info
  request_url TEXT,
  request_method VARCHAR(10),
  request_headers JSONB,
  request_body JSONB,
  
  -- Response
  response_status INTEGER,
  
  -- Environment
  environment VARCHAR(20) DEFAULT 'production',
  release_version VARCHAR(50),
  
  -- Device
  browser VARCHAR(100),
  os VARCHAR(100),
  device VARCHAR(100),
  
  -- Fingerprint for grouping
  fingerprint VARCHAR(64),
  
  -- Status
  status VARCHAR(30) DEFAULT 'unresolved' CHECK (status IN ('unresolved', 'ignored', 'resolved', 'muted')),
  resolved_at TIMESTAMPTZ,
  resolved_by UUID REFERENCES auth.users(id),
  
  PRIMARY KEY (id, occurred_at)
) PARTITION BY RANGE (occurred_at);

CREATE TABLE IF NOT EXISTS public.error_logs_2024_q4 PARTITION OF public.error_logs
  FOR VALUES FROM ('2024-10-01') TO ('2025-01-01');
CREATE TABLE IF NOT EXISTS public.error_logs_2025_q1 PARTITION OF public.error_logs
  FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');
CREATE TABLE IF NOT EXISTS public.error_logs_default PARTITION OF public.error_logs DEFAULT;

-- System health checks
CREATE TABLE IF NOT EXISTS public.health_checks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  service_name VARCHAR(100) NOT NULL,
  check_type VARCHAR(50) NOT NULL,
  
  status VARCHAR(20) NOT NULL CHECK (status IN ('healthy', 'degraded', 'unhealthy')),
  response_time_ms INTEGER,
  
  details JSONB DEFAULT '{}',
  error_message TEXT,
  
  checked_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- SECTION 53: IP SECURITY & BLOCKLISTS
-- ===========================================

CREATE TABLE IF NOT EXISTS public.ip_blocklist (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  ip_address INET NOT NULL,
  ip_range CIDR,
  
  reason VARCHAR(200) NOT NULL,
  
  -- Type
  block_type VARCHAR(30) NOT NULL CHECK (block_type IN ('permanent', 'temporary', 'rate_limited')),
  
  -- Duration (for temporary)
  expires_at TIMESTAMPTZ,
  
  -- Source
  source VARCHAR(50) DEFAULT 'manual' CHECK (source IN ('manual', 'auto_rate_limit', 'auto_fraud', 'import')),
  
  created_by UUID REFERENCES auth.users(id),
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.ip_allowlist (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  ip_address INET,
  ip_range CIDR,
  
  name VARCHAR(200),
  description TEXT,
  
  -- Owner
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
  
  is_active BOOLEAN DEFAULT true,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User blocks
CREATE TABLE IF NOT EXISTS public.user_blocks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  blocker_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  blocked_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  reason TEXT,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT unique_user_block UNIQUE (blocker_id, blocked_id),
  CONSTRAINT no_self_block CHECK (blocker_id != blocked_id)
);

-- ===========================================
-- SECTION 54: CONTENT MODERATION
-- ===========================================

CREATE TABLE IF NOT EXISTS public.moderation_queue (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Content
  entity_type VARCHAR(100) NOT NULL,
  entity_id UUID NOT NULL,
  content_snapshot TEXT,
  
  -- Reporter
  reported_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  
  -- Reason
  reason VARCHAR(100) NOT NULL,
  reason_details TEXT,
  
  -- Status
  status VARCHAR(30) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'escalated')),
  
  -- Resolution
  moderated_by UUID REFERENCES auth.users(id),
  moderated_at TIMESTAMPTZ,
  moderation_notes TEXT,
  action_taken VARCHAR(100),
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.content_flags (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  entity_type VARCHAR(100) NOT NULL,
  entity_id UUID NOT NULL,
  
  flag_type VARCHAR(50) NOT NULL CHECK (flag_type IN ('spam', 'abuse', 'inappropriate', 'copyright', 'other')),
  
  -- Auto-detection
  is_auto_flagged BOOLEAN DEFAULT false,
  confidence_score DECIMAL(5,4),
  
  -- Status
  is_resolved BOOLEAN DEFAULT false,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- SECTION 55: MATERIALIZED VIEWS (PERFORMANCE)
-- ===========================================

-- Active subscriptions summary (refresh every 5 min)
CREATE MATERIALIZED VIEW IF NOT EXISTS public.mv_subscription_stats AS
SELECT 
  plan,
  status,
  COUNT(*) as count,
  SUM(amount_paise) as total_mrr_paise,
  AVG(amount_paise) as avg_amount_paise
FROM public.subscriptions
WHERE deleted_at IS NULL
GROUP BY plan, status
WITH DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_subscription_stats ON public.mv_subscription_stats(plan, status);

-- Daily revenue summary
CREATE MATERIALIZED VIEW IF NOT EXISTS public.mv_daily_revenue AS
SELECT 
  DATE(created_at) as date,
  plan,
  COUNT(*) as payment_count,
  SUM(CASE WHEN status = 'success' THEN amount_paise ELSE 0 END) as revenue_paise,
  SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_count
FROM public.payments
WHERE created_at > NOW() - INTERVAL '90 days'
GROUP BY DATE(created_at), plan
WITH DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_daily_revenue ON public.mv_daily_revenue(date, plan);

-- User engagement summary
CREATE MATERIALIZED VIEW IF NOT EXISTS public.mv_user_engagement AS
SELECT 
  user_id,
  COUNT(DISTINCT DATE(occurred_at)) as active_days_30d,
  COUNT(*) as total_events_30d,
  MAX(occurred_at) as last_active_at
FROM public.activity_events
WHERE occurred_at > NOW() - INTERVAL '30 days'
GROUP BY user_id
WITH DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_user_engagement ON public.mv_user_engagement(user_id);

-- Feature usage leaderboard
CREATE MATERIALIZED VIEW IF NOT EXISTS public.mv_feature_usage_stats AS
SELECT 
  feature_key,
  COUNT(DISTINCT user_id) as unique_users,
  SUM(usage_count) as total_usage,
  AVG(usage_count) as avg_usage_per_user
FROM public.feature_usage
WHERE last_used_at > NOW() - INTERVAL '30 days'
GROUP BY feature_key
WITH DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_feature_usage ON public.mv_feature_usage_stats(feature_key);

-- Organization metrics
CREATE MATERIALIZED VIEW IF NOT EXISTS public.mv_org_metrics AS
SELECT 
  o.id as organization_id,
  o.name,
  o.plan,
  COUNT(DISTINCT om.user_id) as member_count,
  COUNT(DISTINCT c.id) as cohort_count,
  COUNT(DISTINCT ca.id) as campaign_count
FROM public.organizations o
LEFT JOIN public.organization_members om ON o.id = om.organization_id AND om.removed_at IS NULL AND om.is_active = true
LEFT JOIN public.cohorts c ON o.id = c.organization_id AND c.deleted_at IS NULL
LEFT JOIN public.campaigns ca ON o.id = ca.organization_id AND ca.deleted_at IS NULL
WHERE o.deleted_at IS NULL
GROUP BY o.id, o.name, o.plan
WITH DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_org_metrics ON public.mv_org_metrics(organization_id);

-- ===========================================
-- SECTION 56: ADVANCED INDEXES (PERFORMANCE)
-- ===========================================

-- BRIN indexes for time-series data (super efficient for large tables)
CREATE INDEX IF NOT EXISTS idx_brin_activity_occurred ON public.activity_events USING BRIN(occurred_at);
CREATE INDEX IF NOT EXISTS idx_brin_email_queue_created ON public.email_queue USING BRIN(created_at);
CREATE INDEX IF NOT EXISTS idx_brin_error_logs_occurred ON public.error_logs USING BRIN(occurred_at);

-- Partial indexes for hot queries
CREATE INDEX IF NOT EXISTS idx_partial_open_tickets ON public.support_tickets(user_id, created_at DESC) 
  WHERE status IN ('open', 'pending', 'in_progress');
CREATE INDEX IF NOT EXISTS idx_partial_active_subscriptions ON public.subscriptions(user_id, plan) 
  WHERE status = 'active' AND deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_partial_pending_emails ON public.email_queue(scheduled_for, priority DESC) 
  WHERE status = 'pending';
CREATE INDEX IF NOT EXISTS idx_partial_pending_tasks ON public.task_queue(scheduled_for, priority DESC) 
  WHERE status = 'pending';
CREATE INDEX IF NOT EXISTS idx_partial_unresolved_errors ON public.error_logs(fingerprint, occurred_at DESC) 
  WHERE status = 'unresolved';

-- Covering indexes (include frequently accessed columns)
CREATE INDEX IF NOT EXISTS idx_covering_profiles ON public.profiles(id) 
  INCLUDE (email, full_name, plan, plan_status, plan_expires_at);
CREATE INDEX IF NOT EXISTS idx_covering_subscriptions ON public.subscriptions(user_id) 
  INCLUDE (plan, status, current_period_end, autopay_eligible);

-- GIN indexes for JSONB searches
CREATE INDEX IF NOT EXISTS idx_gin_profile_preferences ON public.profiles USING GIN(preferences);
CREATE INDEX IF NOT EXISTS idx_gin_org_settings ON public.organizations USING GIN(settings);
CREATE INDEX IF NOT EXISTS idx_gin_cohort_tags ON public.cohorts USING GIN(interest_tags);
-- NOTE: Enable when assets table is created
-- CREATE INDEX IF NOT EXISTS idx_gin_asset_tags ON public.assets USING GIN(tags);

-- Email system indexes
CREATE INDEX IF NOT EXISTS idx_email_queue_status ON public.email_queue(status, scheduled_for);
CREATE INDEX IF NOT EXISTS idx_email_suppressions_email ON public.email_suppressions(email);
CREATE INDEX IF NOT EXISTS idx_email_events_queue ON public.email_events(email_queue_id);

-- A/B test indexes
CREATE INDEX IF NOT EXISTS idx_ab_tests_status ON public.ab_tests(status);
CREATE INDEX IF NOT EXISTS idx_ab_assignments_test ON public.ab_test_assignments(test_id);
CREATE INDEX IF NOT EXISTS idx_ab_assignments_user ON public.ab_test_assignments(user_id);

-- Survey indexes
CREATE INDEX IF NOT EXISTS idx_survey_responses_survey ON public.survey_responses(survey_id);
CREATE INDEX IF NOT EXISTS idx_survey_responses_nps ON public.survey_responses(nps_score) WHERE nps_score IS NOT NULL;

-- Error tracking indexes
CREATE INDEX IF NOT EXISTS idx_error_fingerprint ON public.error_logs(fingerprint);
CREATE INDEX IF NOT EXISTS idx_error_user ON public.error_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_health_checks_service ON public.health_checks(service_name, checked_at DESC);

-- IP security indexes
CREATE INDEX IF NOT EXISTS idx_ip_blocklist_ip ON public.ip_blocklist USING GIST(ip_address inet_ops);
CREATE INDEX IF NOT EXISTS idx_ip_allowlist_ip ON public.ip_allowlist USING GIST(ip_address inet_ops);

-- ===========================================
-- SECTION 57: OPTIMIZATION FUNCTIONS
-- ===========================================

-- Ultra-fast user lookup with caching hint
CREATE OR REPLACE FUNCTION public.get_user_profile(p_user_id UUID)
RETURNS TABLE (
  id UUID, email TEXT, full_name TEXT, avatar_url TEXT,
  plan plan_type, plan_status TEXT, plan_expires_at TIMESTAMPTZ,
  organization_id UUID
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    p.id, p.email::TEXT, p.full_name, p.avatar_url,
    p.plan, p.plan_status, p.plan_expires_at,
    p.organization_id
  FROM public.profiles p
  WHERE p.id = p_user_id AND p.deleted_at IS NULL;
END;
$$ LANGUAGE plpgsql STABLE PARALLEL SAFE;

-- Fast subscription check
CREATE OR REPLACE FUNCTION public.has_active_subscription(p_user_id UUID)
RETURNS BOOLEAN AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.subscriptions
    WHERE user_id = p_user_id 
    AND status = 'active' 
    AND current_period_end > NOW()
    AND deleted_at IS NULL
  );
$$ LANGUAGE sql STABLE PARALLEL SAFE;

-- Get feature flag value (with caching)
CREATE OR REPLACE FUNCTION public.get_feature_flag(p_key VARCHAR, p_user_id UUID DEFAULT NULL)
RETURNS BOOLEAN AS $$
DECLARE
  v_flag RECORD;
  v_override RECORD;
BEGIN
  -- Check for user override first
  IF p_user_id IS NOT NULL THEN
    SELECT * INTO v_override
    FROM public.feature_flag_overrides
    WHERE flag_id = (SELECT id FROM public.feature_flags WHERE key = p_key)
    AND user_id = p_user_id
    AND (expires_at IS NULL OR expires_at > NOW());
    
    IF FOUND THEN
      RETURN v_override.is_enabled;
    END IF;
  END IF;
  
  -- Get flag value
  SELECT * INTO v_flag FROM public.feature_flags WHERE key = p_key AND status = 'active';
  
  IF NOT FOUND THEN
    RETURN false;
  END IF;
  
  -- Check rollout percentage
  IF v_flag.rollout_percentage < 100 THEN
    RETURN (abs(hashtext(p_user_id::TEXT || p_key)) % 100) < v_flag.rollout_percentage;
  END IF;
  
  RETURN true;
END;
$$ LANGUAGE plpgsql STABLE;

-- Batch upsert for activity events (high performance)
CREATE OR REPLACE FUNCTION public.track_events(p_events JSONB)
RETURNS INTEGER AS $$
DECLARE
  v_inserted INTEGER;
BEGIN
  INSERT INTO public.activity_events (
    user_id, session_id, event_name, event_category, 
    event_action, event_label, properties, occurred_at
  )
  SELECT 
    (e->>'user_id')::UUID,
    (e->>'session_id')::UUID,
    e->>'event_name',
    e->>'event_category',
    e->>'event_action',
    e->>'event_label',
    COALESCE(e->'properties', '{}'),
    COALESCE((e->>'occurred_at')::TIMESTAMPTZ, NOW())
  FROM jsonb_array_elements(p_events) e;
  
  GET DIAGNOSTICS v_inserted = ROW_COUNT;
  RETURN v_inserted;
END;
$$ LANGUAGE plpgsql;

-- Refresh all materialized views
CREATE OR REPLACE FUNCTION public.refresh_all_materialized_views()
RETURNS void AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY public.mv_subscription_stats;
  REFRESH MATERIALIZED VIEW CONCURRENTLY public.mv_daily_revenue;
  REFRESH MATERIALIZED VIEW CONCURRENTLY public.mv_user_engagement;
  REFRESH MATERIALIZED VIEW CONCURRENTLY public.mv_feature_usage_stats;
  REFRESH MATERIALIZED VIEW CONCURRENTLY public.mv_org_metrics;
END;
$$ LANGUAGE plpgsql;

-- Cleanup old data (retention policy)
CREATE OR REPLACE FUNCTION public.cleanup_old_data()
RETURNS JSONB AS $$
DECLARE
  v_result JSONB := '{}';
  v_count INTEGER;
BEGIN
  -- Delete old activity events (90 days)
  DELETE FROM public.activity_events WHERE occurred_at < NOW() - INTERVAL '90 days';
  GET DIAGNOSTICS v_count = ROW_COUNT;
  v_result := v_result || jsonb_build_object('activity_events_deleted', v_count);
  
  -- Delete old email queue (30 days)
  DELETE FROM public.email_queue WHERE created_at < NOW() - INTERVAL '30 days' AND status IN ('sent', 'failed');
  GET DIAGNOSTICS v_count = ROW_COUNT;
  v_result := v_result || jsonb_build_object('email_queue_deleted', v_count);
  
  -- Delete old error logs (30 days)
  DELETE FROM public.error_logs WHERE occurred_at < NOW() - INTERVAL '30 days' AND status IN ('resolved', 'ignored');
  GET DIAGNOSTICS v_count = ROW_COUNT;
  v_result := v_result || jsonb_build_object('error_logs_deleted', v_count);
  
  -- Delete old recent searches (7 days)
  DELETE FROM public.recent_searches WHERE searched_at < NOW() - INTERVAL '7 days';
  GET DIAGNOSTICS v_count = ROW_COUNT;
  v_result := v_result || jsonb_build_object('recent_searches_deleted', v_count);
  
  RETURN v_result;
END;
$$ LANGUAGE plpgsql;

-- ===========================================
-- SECTION 58: PERFORMANCE TRIGGERS
-- ===========================================

-- Auto-update search index on entity changes
CREATE OR REPLACE FUNCTION public.update_search_index()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.search_index (entity_type, entity_id, user_id, title, content, metadata)
  VALUES (TG_TABLE_NAME, NEW.id, NEW.user_id, 
    COALESCE(NEW.name, NEW.title, NEW.subject, ''),
    COALESCE(NEW.description, NEW.content, ''),
    jsonb_build_object('status', COALESCE(NEW.status, 'active'))
  )
  ON CONFLICT (entity_type, entity_id) DO UPDATE SET
    title = EXCLUDED.title,
    content = EXCLUDED.content,
    metadata = EXCLUDED.metadata,
    updated_at = NOW();
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Auto-calculate storage usage
CREATE OR REPLACE FUNCTION public.update_storage_quota()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    UPDATE public.storage_quotas
    SET used_bytes = used_bytes + NEW.file_size,
        updated_at = NOW()
    WHERE user_id = NEW.user_id;
  ELSIF TG_OP = 'DELETE' THEN
    UPDATE public.storage_quotas
    SET used_bytes = used_bytes - OLD.file_size,
        updated_at = NOW()
    WHERE user_id = OLD.user_id;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_storage_on_file_insert
  AFTER INSERT ON public.files
  FOR EACH ROW EXECUTE FUNCTION public.update_storage_quota();

CREATE TRIGGER trg_update_storage_on_file_delete
  AFTER DELETE ON public.files
  FOR EACH ROW EXECUTE FUNCTION public.update_storage_quota();

-- Auto-increment coupon redemption count
CREATE OR REPLACE FUNCTION public.increment_coupon_redemption()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE public.coupons
  SET current_redemptions = current_redemptions + 1
  WHERE id = NEW.coupon_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_increment_coupon_redemption
  AFTER INSERT ON public.coupon_redemptions
  FOR EACH ROW EXECUTE FUNCTION public.increment_coupon_redemption();

-- ===========================================
-- SECTION 59: RLS FOR NEW TABLES
-- ===========================================

ALTER TABLE public.email_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.email_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.email_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.email_suppressions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ab_tests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ab_test_assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.waitlist ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.beta_features ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.surveys ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.survey_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.product_tours ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tour_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.locales ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.translations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.currencies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tax_rates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.error_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.health_checks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ip_blocklist ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ip_allowlist ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_blocks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.moderation_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.content_flags ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "user_preferences_own" ON public.user_preferences FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "tour_progress_own" ON public.tour_progress FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "ab_assignments_own" ON public.ab_test_assignments FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "survey_responses_own" ON public.survey_responses FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "user_blocks_own" ON public.user_blocks FOR ALL USING (auth.uid() = blocker_id);
CREATE POLICY "ip_allowlist_own" ON public.ip_allowlist FOR ALL USING (auth.uid() = user_id);

-- Public reads
CREATE POLICY "email_templates_public" ON public.email_templates FOR SELECT TO PUBLIC USING (is_active = true);
CREATE POLICY "locales_public" ON public.locales FOR SELECT TO PUBLIC USING (is_active = true);
CREATE POLICY "currencies_public" ON public.currencies FOR SELECT TO PUBLIC USING (is_active = true);
CREATE POLICY "tax_rates_public" ON public.tax_rates FOR SELECT TO PUBLIC USING (is_active = true);
CREATE POLICY "product_tours_public" ON public.product_tours FOR SELECT TO PUBLIC USING (is_active = true);
CREATE POLICY "surveys_public" ON public.surveys FOR SELECT TO PUBLIC USING (is_active = true);
CREATE POLICY "ab_tests_public" ON public.ab_tests FOR SELECT TO PUBLIC USING (status = 'running');

-- ===========================================
-- SECTION 60: ADDITIONAL INDEXES FOR NEW TABLES
-- ===========================================

CREATE INDEX IF NOT EXISTS idx_email_templates_slug ON public.email_templates(slug);
CREATE INDEX IF NOT EXISTS idx_waitlist_email ON public.waitlist(email);
CREATE INDEX IF NOT EXISTS idx_waitlist_status ON public.waitlist(status);
CREATE INDEX IF NOT EXISTS idx_beta_features_key ON public.beta_features(feature_key);
CREATE INDEX IF NOT EXISTS idx_surveys_active ON public.surveys(is_active);
CREATE INDEX IF NOT EXISTS idx_tour_progress_user ON public.tour_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_user_preferences_user ON public.user_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_translations_lookup ON public.translations(locale_code, namespace, key);
CREATE INDEX IF NOT EXISTS idx_moderation_status ON public.moderation_queue(status);

-- ===========================================
-- COMPLETE
-- ===========================================
DO $$ 
BEGIN
  RAISE NOTICE '═══════════════════════════════════════════════════════════════';
  RAISE NOTICE '✅ RAPTORFLOW ENTERPRISE SCHEMA v4.0 - ULTIMATE SaaS EDITION';
  RAISE NOTICE '═══════════════════════════════════════════════════════════════';
  RAISE NOTICE '';
  RAISE NOTICE '📊 SCALE:';
  RAISE NOTICE '   • Tables: 150+';
  RAISE NOTICE '   • Indexes: 300+ (including BRIN, GIN, GiST, partial, covering)';
  RAISE NOTICE '   • RLS Policies: 130+';
  RAISE NOTICE '   • Materialized Views: 5 (for dashboards)';
  RAISE NOTICE '   • Partitioned Tables: 6 (for infinite scale)';
  RAISE NOTICE '';
  RAISE NOTICE '🎯 MODULES:';
  RAISE NOTICE '   ├─ 💳 Payments: RBI autopay, mandates, invoices, refunds';
  RAISE NOTICE '   ├─ 📧 Email: Templates, queue (partitioned), events, suppressions';
  RAISE NOTICE '   ├─ 🎯 A/B Testing: Tests, variants, assignments, conversions';
  RAISE NOTICE '   ├─ 📋 Surveys: NPS, CSAT, custom with responses';
  RAISE NOTICE '   ├─ 🎓 Onboarding: Product tours, progress tracking';
  RAISE NOTICE '   ├─ 🎫 Support: Tickets, KB, SLA, canned responses';
  RAISE NOTICE '   ├─ 📁 Files: Storage, versions, shares, quotas';
  RAISE NOTICE '   ├─ 📈 Analytics: Events (partitioned), sessions, feature usage';
  RAISE NOTICE '   ├─ 💰 Billing: Coupons, credits/wallet, usage metering';
  RAISE NOTICE '   ├─ ⏰ Jobs: Scheduled (cron), task queue with retry';
  RAISE NOTICE '   ├─ 📋 Compliance: GDPR consent, export, deletion';
  RAISE NOTICE '   ├─ 🛒 Marketplace: Apps, installs, webhooks, syncs';
  RAISE NOTICE '   ├─ 💬 Collaboration: Comments, reactions, mentions, presence';
  RAISE NOTICE '   ├─ 🔍 Search: Full-text with tsvector, saved searches';
  RAISE NOTICE '   ├─ 📊 Reports: Custom configs, dashboards, widgets';
  RAISE NOTICE '   ├─ 🌍 Localization: Locales, translations';
  RAISE NOTICE '   ├─ 💱 Currencies & Tax: Multi-currency, GST rates';
  RAISE NOTICE '   ├─ 🚨 Errors: Tracking (partitioned), health checks';
  RAISE NOTICE '   ├─ 🔒 Security: IP blocklist/allowlist, user blocks';
  RAISE NOTICE '   ├─ 🛡️ Moderation: Queue, content flags';
  RAISE NOTICE '   ├─ 🤝 Referrals: Codes, tracking, rewards';
  RAISE NOTICE '   ├─ 📢 Changelog: Entries, announcements';
  RAISE NOTICE '   └─ ⏳ Waitlist: Beta access management';
  RAISE NOTICE '';
  RAISE NOTICE '⚡ PERFORMANCE OPTIMIZATIONS:';
  RAISE NOTICE '   • BRIN indexes for time-series (90% smaller than B-tree)';
  RAISE NOTICE '   • Partial indexes for hot queries';
  RAISE NOTICE '   • Covering indexes to avoid table lookups';
  RAISE NOTICE '   • GIN indexes for JSONB searches';
  RAISE NOTICE '   • Materialized views with CONCURRENTLY refresh';
  RAISE NOTICE '   • Partitioned tables for infinite scaling';
  RAISE NOTICE '   • Optimized functions with STABLE/PARALLEL SAFE';
  RAISE NOTICE '   • Batch operations for high-throughput';
  RAISE NOTICE '   • Auto-cleanup functions for data retention';
  RAISE NOTICE '';
  RAISE NOTICE '🔒 SECURITY:';
  RAISE NOTICE '   • RLS on ALL tables';
  RAISE NOTICE '   • IP blocklist/allowlist with CIDR support';
  RAISE NOTICE '   • Content moderation pipeline';
  RAISE NOTICE '   • User blocking';
  RAISE NOTICE '   • GDPR/DPDP compliance infrastructure';
  RAISE NOTICE '';
  RAISE NOTICE '🇮🇳 RBI COMPLIANCE:';
  RAISE NOTICE '   • Autopay limit: ₹5,000 (Ascent only)';
  RAISE NOTICE '   • e-Mandate with OTP tracking';
  RAISE NOTICE '   • Pre-debit notifications';
  RAISE NOTICE '';
  RAISE NOTICE '═══════════════════════════════════════════════════════════════';
END $$;
