/**
 * RaptorFlow Landing Page Database Schema
 *
 * Created: 2025-12-19
 * Tables:
 * - landing_leads (Newsletter + CRM data)
 * - waitlist_signups (Waitlist + referral tracking)
 * - contact_submissions (Contact form data)
 * - pricing_selections (Pricing page analytics)
 * - payment_intents (Payment tracking)
 */

-- ============================================================================
-- LANDING LEADS TABLE (Newsletter & CRM)
-- ============================================================================

CREATE TABLE IF NOT EXISTS landing_leads (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,

  -- Contact Information
  email VARCHAR(255) UNIQUE NOT NULL,
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  company VARCHAR(255),
  industry VARCHAR(100),
  role VARCHAR(100),
  phone VARCHAR(20),
  country VARCHAR(100),

  -- Status Tracking
  status VARCHAR(50) DEFAULT 'subscribed', -- subscribed, unsubscribed, bounced, invalid
  unsubscribe_reason VARCHAR(255),

  -- Source & Attribution
  source VARCHAR(100) DEFAULT 'landing_page', -- landing_page, waitlist, referral, organic
  utm_source VARCHAR(100),
  utm_campaign VARCHAR(100),
  utm_medium VARCHAR(100),
  utm_content VARCHAR(100),
  referral_code VARCHAR(255),

  -- Email Verification
  email_verified BOOLEAN DEFAULT false,
  verification_token VARCHAR(255),
  verification_token_expires_at TIMESTAMP,
  verified_at TIMESTAMP,

  -- Engagement Metrics
  first_opened_at TIMESTAMP,
  last_engaged_at TIMESTAMP,
  email_open_count INT DEFAULT 0,
  email_click_count INT DEFAULT 0,

  -- Conversion Tracking
  conversion_status VARCHAR(50) DEFAULT 'lead', -- lead, qualified, trial_started, paid, churned
  converted_at TIMESTAMP,
  conversion_source VARCHAR(100), -- pricing_page, product_demo, contact_form, payment

  -- Device & Browser Data
  ip_address INET,
  user_agent TEXT,
  device_type VARCHAR(50), -- mobile, tablet, desktop
  browser VARCHAR(100),
  os_type VARCHAR(100),

  -- Timestamps
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now(),
  deleted_at TIMESTAMP

  -- Soft delete support
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_landing_leads_email ON landing_leads(email);
CREATE INDEX IF NOT EXISTS idx_landing_leads_status ON landing_leads(status);
CREATE INDEX IF NOT EXISTS idx_landing_leads_conversion_status ON landing_leads(conversion_status);
CREATE INDEX IF NOT EXISTS idx_landing_leads_created_at ON landing_leads(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_landing_leads_country ON landing_leads(country);
CREATE INDEX IF NOT EXISTS idx_landing_leads_utm_campaign ON landing_leads(utm_campaign);

-- ============================================================================
-- WAITLIST SIGNUPS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS waitlist_signups (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,

  -- Basic Info
  email VARCHAR(255) UNIQUE NOT NULL,
  first_name VARCHAR(100) NOT NULL,
  use_case TEXT, -- Why they're interested (max 1000 chars)
  company_size VARCHAR(50), -- 1-10, 10-50, 50-500, 500+
  budget_range VARCHAR(50), -- Self-identified budget range

  -- Priority Scoring
  priority_score INT DEFAULT 0 CHECK (priority_score >= 0 AND priority_score <= 100),
  tier VARCHAR(50) DEFAULT 'standard', -- standard, priority, vip

  -- Invite System
  invite_status VARCHAR(50) DEFAULT 'pending', -- pending, sent, redeemed, expired
  invite_code VARCHAR(255) UNIQUE,
  invite_sent_at TIMESTAMP,
  invite_expires_at TIMESTAMP,
  redeemed_at TIMESTAMP,

  -- Engagement & Referrals
  email_opens INT DEFAULT 0,
  referral_count INT DEFAULT 0,
  referred_by_code VARCHAR(255),

  -- Timestamps
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now(),
  deleted_at TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_waitlist_email ON waitlist_signups(email);
CREATE INDEX IF NOT EXISTS idx_waitlist_tier ON waitlist_signups(tier);
CREATE INDEX IF NOT EXISTS idx_waitlist_invite_code ON waitlist_signups(invite_code);
CREATE INDEX IF NOT EXISTS idx_waitlist_priority_score ON waitlist_signups(priority_score DESC);
CREATE INDEX IF NOT EXISTS idx_waitlist_created_at ON waitlist_signups(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_waitlist_status ON waitlist_signups(invite_status);

-- ============================================================================
-- CONTACT SUBMISSIONS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS contact_submissions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,

  -- Contact Info
  email VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  company VARCHAR(255),
  phone VARCHAR(20),

  -- Submission Details
  subject VARCHAR(255) NOT NULL,
  message TEXT NOT NULL,
  inquiry_type VARCHAR(100) NOT NULL, -- sales, support, partnership, feedback

  -- Status Tracking
  status VARCHAR(50) DEFAULT 'new', -- new, assigned, in_progress, resolved, spam
  assigned_to UUID, -- Team member UUID
  priority VARCHAR(50) DEFAULT 'normal', -- low, normal, high

  -- Response Tracking
  response_sent BOOLEAN DEFAULT false,
  response_sent_at TIMESTAMP,
  response_message TEXT,
  resolution_notes TEXT,

  -- Meta Data
  ip_address INET,
  user_agent TEXT,
  source VARCHAR(100) DEFAULT 'landing_page',

  -- Timestamps
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now(),
  resolved_at TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_contact_email ON contact_submissions(email);
CREATE INDEX IF NOT EXISTS idx_contact_status ON contact_submissions(status);
CREATE INDEX IF NOT EXISTS idx_contact_inquiry_type ON contact_submissions(inquiry_type);
CREATE INDEX IF NOT EXISTS idx_contact_created_at ON contact_submissions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_contact_assigned_to ON contact_submissions(assigned_to);

-- ============================================================================
-- PRICING SELECTIONS TABLE (Analytics)
-- ============================================================================

CREATE TABLE IF NOT EXISTS pricing_selections (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,

  -- Session Tracking
  session_id VARCHAR(255) NOT NULL,

  -- Tier Selection
  selected_tier VARCHAR(50),
  monthly_cost INT,
  billing_cycle VARCHAR(50), -- monthly, annual

  -- User Context
  email VARCHAR(255),

  -- Action Tracking
  action VARCHAR(50) DEFAULT 'viewed', -- viewed, compared, selected, clicked_cta, form_started

  -- Form Completion
  form_completion_percent INT DEFAULT 0 CHECK (form_completion_percent >= 0 AND form_completion_percent <= 100),
  checkout_started_at TIMESTAMP,
  checkout_completed_at TIMESTAMP,

  -- Context
  utm_source VARCHAR(100),
  utm_campaign VARCHAR(100),

  -- Timestamps
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_pricing_session ON pricing_selections(session_id);
CREATE INDEX IF NOT EXISTS idx_pricing_tier ON pricing_selections(selected_tier);
CREATE INDEX IF NOT EXISTS idx_pricing_action ON pricing_selections(action);
CREATE INDEX IF NOT EXISTS idx_pricing_email ON pricing_selections(email);
CREATE INDEX IF NOT EXISTS idx_pricing_created_at ON pricing_selections(created_at DESC);

-- ============================================================================
-- PAYMENT INTENTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS payment_intents (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,

  -- Transaction Info
  transaction_id VARCHAR(255) UNIQUE NOT NULL,
  order_id VARCHAR(255) UNIQUE NOT NULL,

  -- Customer Info
  email VARCHAR(255) NOT NULL,

  -- Payment Details
  amount INT NOT NULL, -- In smallest currency unit (paise)
  currency VARCHAR(10) DEFAULT 'INR',
  tier VARCHAR(50), -- free, starter, pro, enterprise
  billing_cycle VARCHAR(50), -- monthly, annual
  coupon_code VARCHAR(255),
  coupon_discount INT DEFAULT 0,

  -- Status
  status VARCHAR(50) DEFAULT 'pending', -- pending, completed, failed, expired, refunded

  -- PhonePe Integration
  phonepe_reference_id VARCHAR(255),
  phonepe_response_code VARCHAR(50),
  phonepe_response_message TEXT,

  -- Expiry
  created_at TIMESTAMP DEFAULT now(),
  expires_at TIMESTAMP,
  completed_at TIMESTAMP,

  -- Metadata
  user_agent TEXT,
  ip_address INET
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_payment_transaction_id ON payment_intents(transaction_id);
CREATE INDEX IF NOT EXISTS idx_payment_order_id ON payment_intents(order_id);
CREATE INDEX IF NOT EXISTS idx_payment_email ON payment_intents(email);
CREATE INDEX IF NOT EXISTS idx_payment_status ON payment_intents(status);
CREATE INDEX IF NOT EXISTS idx_payment_created_at ON payment_intents(created_at DESC);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE landing_leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE waitlist_signups ENABLE ROW LEVEL SECURITY;
ALTER TABLE contact_submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE pricing_selections ENABLE ROW LEVEL SECURITY;
ALTER TABLE payment_intents ENABLE ROW LEVEL SECURITY;

-- Policy: Anonymous users can read (no individual read permissions)
-- Backend service role handles all writes with validation
CREATE POLICY "allow_service_writes" ON landing_leads
  FOR INSERT
  WITH CHECK (true);

CREATE POLICY "allow_service_writes" ON waitlist_signups
  FOR INSERT
  WITH CHECK (true);

CREATE POLICY "allow_service_writes" ON contact_submissions
  FOR INSERT
  WITH CHECK (true);

CREATE POLICY "allow_service_writes" ON pricing_selections
  FOR INSERT
  WITH CHECK (true);

CREATE POLICY "allow_service_writes" ON payment_intents
  FOR INSERT
  WITH CHECK (true);

-- ============================================================================
-- FUNCTIONS FOR AUTOMATION
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for landing_leads
CREATE TRIGGER update_landing_leads_updated_at
  BEFORE UPDATE ON landing_leads
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Trigger for waitlist_signups
CREATE TRIGGER update_waitlist_signups_updated_at
  BEFORE UPDATE ON waitlist_signups
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Trigger for contact_submissions
CREATE TRIGGER update_contact_submissions_updated_at
  BEFORE UPDATE ON contact_submissions
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Trigger for pricing_selections
CREATE TRIGGER update_pricing_selections_updated_at
  BEFORE UPDATE ON pricing_selections
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Trigger for payment_intents
CREATE TRIGGER update_payment_intents_updated_at
  BEFORE UPDATE ON payment_intents
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- UTILITY VIEWS
-- ============================================================================

-- View: Waitlist statistics by tier
CREATE OR REPLACE VIEW waitlist_statistics AS
SELECT
  tier,
  COUNT(*) as count,
  AVG(priority_score)::INT as avg_priority_score,
  SUM(CASE WHEN invite_status = 'redeemed' THEN 1 ELSE 0 END) as converted_count
FROM waitlist_signups
WHERE deleted_at IS NULL
GROUP BY tier;

-- View: Recent contact submissions requiring response
CREATE OR REPLACE VIEW pending_contact_submissions AS
SELECT
  id,
  name,
  email,
  inquiry_type,
  subject,
  created_at,
  CASE
    WHEN inquiry_type = 'sales' THEN 'high'
    WHEN inquiry_type = 'support' THEN 'normal'
    ELSE 'low'
  END as suggested_priority
FROM contact_submissions
WHERE status IN ('new', 'in_progress')
  AND deleted_at IS NULL
ORDER BY created_at ASC;

-- View: Newsletter subscriber summary
CREATE OR REPLACE VIEW newsletter_summary AS
SELECT
  COUNT(*) as total_subscribers,
  SUM(CASE WHEN status = 'subscribed' THEN 1 ELSE 0 END) as active_subscribers,
  SUM(CASE WHEN email_verified = true THEN 1 ELSE 0 END) as verified_subscribers,
  SUM(CASE WHEN conversion_status = 'paid' THEN 1 ELSE 0 END) as converted_to_paid,
  COUNT(DISTINCT utm_campaign) as campaigns,
  COUNT(DISTINCT country) as countries
FROM landing_leads
WHERE deleted_at IS NULL;
