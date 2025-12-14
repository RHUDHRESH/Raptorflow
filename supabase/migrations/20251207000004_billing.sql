-- =====================================================
-- MIGRATION 004: Billing & Subscriptions (RBI-Compliant)
-- =====================================================

-- Plans
CREATE TABLE public.plans (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code plan_type UNIQUE NOT NULL,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  price_monthly_paise BIGINT NOT NULL,
  price_yearly_paise BIGINT,
  autopay_eligible BOOLEAN GENERATED ALWAYS AS (price_monthly_paise <= 500000) STORED,
  cohort_limit INTEGER NOT NULL DEFAULT 1,
  member_limit INTEGER NOT NULL DEFAULT 1,
  storage_limit_mb INTEGER NOT NULL DEFAULT 100,
  features JSONB DEFAULT '[]',
  is_active BOOLEAN DEFAULT true,
  is_featured BOOLEAN DEFAULT false,
  sort_order INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Subscriptions
CREATE TABLE public.subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
  plan_id UUID NOT NULL REFERENCES public.plans(id),
  amount_paise BIGINT NOT NULL,
  currency VARCHAR(3) DEFAULT 'INR',
  billing_cycle VARCHAR(20) DEFAULT 'monthly' CHECK (billing_cycle IN ('monthly', 'yearly')),
  current_period_start TIMESTAMPTZ NOT NULL,
  current_period_end TIMESTAMPTZ NOT NULL,
  trial_end TIMESTAMPTZ,
  cancelled_at TIMESTAMPTZ,
  status subscription_status NOT NULL DEFAULT 'active',
  cancel_at_period_end BOOLEAN DEFAULT false,
  autopay_enabled BOOLEAN DEFAULT false,
  mandate_id UUID,
  deleted_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Payment mandates (RBI e-Mandate)
CREATE TABLE public.payment_mandates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
  subscription_id UUID REFERENCES public.subscriptions(id) ON DELETE SET NULL,
  mandate_type payment_method_type NOT NULL,
  provider VARCHAR(50) NOT NULL,
  provider_mandate_id TEXT UNIQUE,
  max_amount_paise BIGINT NOT NULL,
  frequency VARCHAR(20) DEFAULT 'monthly',
  is_within_autopay_limit BOOLEAN GENERATED ALWAYS AS (max_amount_paise <= 500000) STORED,
  valid_from TIMESTAMPTZ NOT NULL,
  valid_until TIMESTAMPTZ NOT NULL,
  status mandate_status DEFAULT 'pending_authorization',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Invoices (GST-compliant)
CREATE TABLE public.invoices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
  subscription_id UUID REFERENCES public.subscriptions(id) ON DELETE SET NULL,
  invoice_number VARCHAR(50) UNIQUE NOT NULL,
  billing_name TEXT NOT NULL,
  billing_email TEXT NOT NULL,
  billing_address JSONB,
  billing_gstin VARCHAR(15),
  subtotal_paise BIGINT NOT NULL,
  tax_paise BIGINT DEFAULT 0,
  total_paise BIGINT NOT NULL,
  amount_paid_paise BIGINT DEFAULT 0,
  cgst_paise BIGINT DEFAULT 0,
  sgst_paise BIGINT DEFAULT 0,
  igst_paise BIGINT DEFAULT 0,
  invoice_date DATE NOT NULL DEFAULT CURRENT_DATE,
  due_date DATE NOT NULL,
  paid_at TIMESTAMPTZ,
  status invoice_status DEFAULT 'pending',
  pdf_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Payments
CREATE TABLE public.payments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
  invoice_id UUID REFERENCES public.invoices(id) ON DELETE SET NULL,
  subscription_id UUID REFERENCES public.subscriptions(id) ON DELETE SET NULL,
  amount_paise BIGINT NOT NULL,
  currency VARCHAR(3) DEFAULT 'INR',
  payment_method payment_method_type,
  provider VARCHAR(50) NOT NULL,
  provider_payment_id TEXT UNIQUE,
  provider_order_id TEXT,
  status payment_status DEFAULT 'initiated',
  response_code TEXT,
  response_message TEXT,
  ip_address INET,
  idempotency_key VARCHAR(64) UNIQUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_subscriptions_org ON public.subscriptions(organization_id);
CREATE INDEX idx_subscriptions_status ON public.subscriptions(status);
CREATE INDEX idx_subscriptions_active ON public.subscriptions(organization_id) WHERE status = 'active' AND deleted_at IS NULL;
CREATE INDEX idx_payments_org ON public.payments(organization_id);
CREATE INDEX idx_payments_status ON public.payments(status);
CREATE INDEX idx_payments_provider ON public.payments(provider_payment_id);
CREATE INDEX idx_invoices_org ON public.invoices(organization_id);
CREATE INDEX idx_invoices_status ON public.invoices(status);
