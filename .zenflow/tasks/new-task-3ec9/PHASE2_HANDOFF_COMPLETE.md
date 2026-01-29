# Phase 2 Handoff: Payments & PhonePe Integration - COMPLETE CONTEXT

## Executive Summary

**Phase 1 Status**: ✅ COMPLETE - All authentication, profile verification, and gating systems are production-ready with comprehensive testing, error handling, and security hardening.

**Your Mission**: Implement Phase 2 - Payments & PhonePe SDK integration with the same rigor and quality standards established in Phase 1.

---

## Project Context (What You're Inheriting)

### Project Name: RaptorFlow
**Description**: Founder Marketing Operating System - Clear positioning, 90-day war plans, weekly execution moves.

**Current Stack**:
- Frontend: Next.js 14 on Vercel
- Backend: FastAPI on Render
- Database: Supabase (PostgreSQL)
- Cache: Upstash Redis
- AI: Vertex AI
- Email: Resend
- Payments: PhonePe (YOUR DOMAIN)

### Business Model
- **Free Trial**: 7 days with full features
- **Paid Tiers**: Starter ($49/mo), Growth ($149/mo), Enterprise ($499/mo)
- **Payment Gateway**: PhonePe (Indian market focus)
- **Onboarding Flow**: Signup → Payment → Onboarding → BCM Generation → Dashboard

---

## Phase 1 Achievements (What's Already Done)

### ✅ Authentication System
- **Complete user auth** with email + Google OAuth
- **Profile verification** ensures users have workspace + subscription before access
- **Middleware + client-side gating** blocks unauthorized routes
- **Production-ready error handling** with structured responses
- **Comprehensive testing** (backend + frontend)

### ✅ Database Schema
```sql
-- Key tables already exist:
users (id, auth_user_id, email, subscription_plan, subscription_status, workspace_id)
workspaces (id, owner_id, name, slug, is_trial)
workspace_members (workspace_id, user_id, role, is_active)
subscriptions (workspace_id, plan, status, current_period_start/end)
```

### ✅ API Endpoints
```
POST /api/v1/auth/ensure-profile  # Creates missing profile/workspace
GET  /api/v1/auth/verify-profile  # Returns readiness state
POST /api/v1/auth/login           # Email/password auth
GET  /api/v1/auth/oauth/google    # Google OAuth initiation
```

### ✅ Frontend Components
- **AuthProvider**: Manages auth state + profile verification
- **ProfileGate**: Blocks access until profile/payment ready
- **Middleware**: Server-side route protection
- **Blueprint UI**: Consistent design system

---

## Phase 2 Requirements (What You Must Build)

### 🎯 Primary Objective
Implement complete PhonePe payment integration with:
- Payment initiation flow
- Webhook handling for payment confirmation
- Subscription activation
- Email notifications
- Frontend payment polling UI

### 📋 Required Deliverables

#### 1. Database Migrations
```sql
-- File: supabase/migrations/002_payment_transactions.sql
-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create payment_transactions table
CREATE TABLE payment_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    merchant_order_id VARCHAR(255) UNIQUE NOT NULL,
    phonepe_transaction_id VARCHAR(255),
    amount INTEGER NOT NULL, -- in paise (1 INR = 100 paise)
    currency VARCHAR(3) DEFAULT 'INR',
    status VARCHAR(50) DEFAULT 'pending', -- pending, completed, failed, refunded
    payment_method VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    phonepe_response JSONB,
    metadata JSONB
);

-- Add indexes for performance
CREATE INDEX idx_payment_transactions_workspace_id ON payment_transactions(workspace_id);
CREATE INDEX idx_payment_transactions_merchant_order_id ON payment_transactions(merchant_order_id);
CREATE INDEX idx_payment_transactions_status ON payment_transactions(status);
CREATE INDEX idx_payment_transactions_created_at ON payment_transactions(created_at);

-- Add RLS (Row Level Security)
ALTER TABLE payment_transactions ENABLE ROW LEVEL SECURITY;

-- RLS policies
CREATE POLICY "Users can view their own workspace transactions" ON payment_transactions
    FOR SELECT USING (
        workspace_id IN (
            SELECT id FROM workspaces
            WHERE owner_id = auth.uid()
            OR id IN (
                SELECT workspace_id FROM workspace_members
                WHERE user_id = auth.uid() AND is_active = true
            )
        )
    );

CREATE POLICY "Users can insert their own workspace transactions" ON payment_transactions
    FOR INSERT WITH CHECK (
        workspace_id IN (
            SELECT id FROM workspaces
            WHERE owner_id = auth.uid()
            OR id IN (
                SELECT workspace_id FROM workspace_members
                WHERE user_id = auth.uid() AND is_active = true
            )
        )
    );

-- Function to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for auto-updating updated_at
CREATE TRIGGER update_payment_transactions_updated_at
    BEFORE UPDATE ON payment_transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- File: supabase/migrations/005_subscriptions.sql
-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create subscriptions table
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    plan VARCHAR(50) NOT NULL, -- starter, growth, enterprise
    status VARCHAR(50) NOT NULL DEFAULT 'trial', -- trial, active, past_due, canceled, unpaid
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    trial_end TIMESTAMP WITH TIME ZONE,
    grace_period_end TIMESTAMP WITH TIME ZONE,
    phonepe_subscription_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB
);

-- Add indexes for performance
CREATE INDEX idx_subscriptions_workspace_id ON subscriptions(workspace_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_plan ON subscriptions(plan);
CREATE INDEX idx_subscriptions_current_period_end ON subscriptions(current_period_end);

-- Add RLS (Row Level Security)
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

-- RLS policies
CREATE POLICY "Users can view their own workspace subscriptions" ON subscriptions
    FOR SELECT USING (
        workspace_id IN (
            SELECT id FROM workspaces
            WHERE owner_id = auth.uid()
            OR id IN (
                SELECT workspace_id FROM workspace_members
                WHERE user_id = auth.uid() AND is_active = true
            )
        )
    );

CREATE POLICY "Users can insert their own workspace subscriptions" ON subscriptions
    FOR INSERT WITH CHECK (
        workspace_id IN (
            SELECT id FROM workspaces
            WHERE owner_id = auth.uid()
            OR id IN (
                SELECT workspace_id FROM workspace_members
                WHERE user_id = auth.uid() AND is_active = true
            )
        )
    );

-- Trigger for auto-updating updated_at
CREATE TRIGGER update_subscriptions_updated_at
    BEFORE UPDATE ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to get active subscription for workspace
CREATE OR REPLACE FUNCTION get_active_subscription(p_workspace_id UUID)
RETURNS TABLE (
    id UUID,
    plan VARCHAR(50),
    status VARCHAR(50),
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    trial_end TIMESTAMP WITH TIME ZONE,
    grace_period_end TIMESTAMP WITH TIME ZONE,
    phonepe_subscription_id VARCHAR(255),
    metadata JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.id,
        s.plan,
        s.status,
        s.current_period_start,
        s.current_period_end,
        s.trial_end,
        s.grace_period_end,
        s.phonepe_subscription_id,
        s.metadata
    FROM subscriptions s
    WHERE s.workspace_id = p_workspace_id
    AND s.status IN ('trial', 'active', 'past_due')
    ORDER BY s.created_at DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

#### 2. Backend Services

##### Email Service (`backend/services/email_service.py`)
```python
# Must handle:
- Payment confirmation emails
- Payment failure notifications
- Trial expiration reminders
- Subscription renewal notices
- Invoice delivery

# Use Resend API
# Templates: payment_confirmation.html, payment_failed.html, trial_ending.html
```

##### Payment Service (`backend/services/payment_service.py`)
```python
# Must handle:
- PhonePe payment initiation
- Order ID generation
- Transaction status checking
- Subscription activation
- Webhook signature verification
- Retry logic for failed payments
```

##### Enhanced API Endpoints (`backend/api/v1/payments_v2.py`)
```python
# Required endpoints:
POST /api/v1/payments/initiate     # Start PhonePe payment
GET  /api/v1/payments/status/{id}  # Check payment status
POST /api/v1/payments/webhook      # PhonePe webhook handler
GET  /api/v1/payments/methods      # Available payment methods
POST /api/v1/payments/retry        # Retry failed payment
```

#### 3. Frontend Components

##### Payment Page (`src/app/onboarding/plans/page.tsx`)
```typescript
// Must include:
- Plan selection (Starter/Growth/Enterprise)
- PhonePe payment button
- Payment status polling
- Error handling
- Loading states
- Success redirect
```

##### Payment Polling Utility (`src/lib/payment-polling.ts`)
```typescript
// Must handle:
- Real-time payment status updates
- Exponential backoff retry
- Timeout handling
- Success/failure callbacks
```

##### Webhook Handler (`src/app/api/webhooks/phonepe/route.ts`)
```typescript
// Must include:
- X-VERIFY signature validation
- Idempotency handling
- Supabase updates
- Email triggers
- Security logging
```

#### 4. Integration Points

##### PhonePe SDK Integration
```typescript
// Required environment variables:
PHONEPE_MERCHANT_ID
PHONEPE_SALT_KEY
PHONEPE_SALT_INDEX
PHONEPE_ENVIRONMENT (sandbox/production)
PHONEPE_REDIRECT_URL
```

##### Frontend State Management
```typescript
// Update AuthProvider to handle:
- Payment status tracking
- Plan selection state
- Payment error handling
- Post-payment redirects
```

---

## Technical Standards (Match Phase 1 Quality)

### 🏗️ Architecture Patterns
- **Service Layer**: All business logic in dedicated services
- **Error Handling**: Structured errors with context (like ProfileError)
- **Logging**: Comprehensive logging with user context
- **Security**: Fail-closed behavior, input validation, rate limiting
- **Testing**: Unit + integration tests for all components

### 📝 Code Quality
```python
# Follow existing patterns:
class PaymentError(Exception):
    def __init__(self, message: str, error_type: str, context: Dict[str, Any] = None):
        super().__init__(message)
        self.error_type = error_type
        self.context = context or {}

# Use structured logging:
logger.info("Payment initiated for workspace %s", workspace_id)
logger.error("Payment failed: %s", error, extra={"workspace_id": workspace_id})
```

### 🧪 Testing Requirements
```python
# Backend tests: backend/tests/services/test_payment_service.py
# Frontend tests: src/components/payment/__tests__/PaymentPage.test.tsx
# Integration tests: Full payment flow end-to-end
```

### 🔒 Security Requirements
- **Webhook Signature Validation**: Must validate PhonePe X-VERIFY header
- **Idempotency**: Handle duplicate webhook calls gracefully
- **Rate Limiting**: Prevent payment initiation abuse
- **Input Validation**: Validate all payment amounts and plan IDs
- **Audit Logging**: Log all payment events for compliance

---

## File Structure (What to Create/Modify)

### New Files to Create
```
backend/services/email_service.py
backend/services/payment_service.py
backend/tests/services/test_payment_service.py
backend/tests/api/test_payments_v2.py
src/app/onboarding/plans/page.tsx
src/lib/payment-polling.ts
src/components/payment/PaymentButton.tsx
src/components/payment/PaymentStatus.tsx
src/app/api/webhooks/phonepe/route.ts
supabase/migrations/002_payment_transactions.sql
supabase/migrations/005_subscriptions.sql
```

### Files to Modify
```
backend/api/v1/payments_v2.py (enhance existing)
src/components/auth/AuthProvider.tsx (add payment state)
src/middleware.ts (add payment route protection)
.env.example (add PhonePe variables)
```

---

## Environment Variables (Add These)

```bash
# PhonePe Configuration
PHONEPE_MERCHANT_ID=your_merchant_id
PHONEPE_SALT_KEY=your_salt_key
PHONEPE_SALT_INDEX=1
PHONEPE_ENVIRONMENT=sandbox
PHONEPE_REDIRECT_URL=https://yourapp.com/onboarding/plans/callback
PHONEPE_WEBHOOK_SECRET=your_webhook_secret

# Email Configuration (Resend)
RESEND_API_KEY=your_resend_key
FROM_EMAIL=noreply@yourapp.com
FROM_NAME=RaptorFlow

# Payment URLs
PHONEPE_SANDBOX_URL=https://api.phonepe.com/apis/pg-sandbox
PHONEPE_PRODUCTION_URL=https://api.phonepe.com/apis/pg
```

---

## API Contracts (What to Implement)

### Payment Initiation
```typescript
POST /api/v1/payments/initiate
{
  "plan": "growth", // starter|growth|enterprise
  "amount": 14900,  // in paise
  "currency": "INR",
  "redirect_url": "https://yourapp.com/onboarding/plans/callback",
  "webhook_url": "https://yourapp.com/api/webhooks/phonepe"
}

Response:
{
  "success": true,
  "merchant_order_id": "order_12345",
  "payment_url": "https://api.phonepe.com/apis/pg-sandbox/...",
  "expires_at": "2026-01-28T10:30:00Z"
}
```

### Payment Status
```typescript
GET /api/v1/payments/status/{merchant_order_id}

Response:
{
  "success": true,
  "status": "completed", // pending|completed|failed|refunded
  "transaction_id": "tx_12345",
  "amount": 14900,
  "paid_at": "2026-01-28T10:25:00Z",
  "subscription": {
    "id": "sub_12345",
    "plan": "growth",
    "status": "active",
    "current_period_end": "2026-02-28T10:25:00Z"
  }
}
```

### Webhook Handler
```typescript
POST /api/webhooks/phonepe
Headers: X-VERIFY, X-CODE, X-MERCHANT-ID

Body:
{
  "code": "PAYMENT_SUCCESS",
  "data": {
    "merchantId": "your_merchant_id",
    "merchantTransactionId": "order_12345",
    "transactionId": "tx_12345",
    "amount": 14900,
    "state": "COMPLETED",
    "responseCode": "SUCCESS"
  }
}
```

---

## Testing Strategy (Match Phase 1 Rigor)

### Backend Tests
```python
# Test payment initiation
def test_payment_initiation_success():
    # Mock PhonePe API
    # Verify order ID generation
    # Check database record creation

# Test webhook handling
def test_webhook_signature_validation():
    # Test valid signature
    # Test invalid signature
    # Test duplicate handling

# Test subscription activation
def test_subscription_activation():
    # Verify subscription creation
    # Check user status update
    # Confirm email sent
```

### Frontend Tests
```typescript
// Test payment flow
describe('Payment Flow', () => {
  it('initiates payment successfully')
  it('polls for payment status')
  it('handles payment success')
  it('handles payment failure')
  it('shows appropriate loading states')
})
```

### Integration Tests
```typescript
// Full end-to-end flow
describe('Payment E2E', () => {
  it('completes signup → payment → dashboard flow')
  it('handles payment failure and retry')
  it('activates subscription after payment')
})
```

---

## Success Criteria (What "Done" Looks Like)

### ✅ Functional Requirements
- [ ] User can select a plan and initiate PhonePe payment
- [ ] Payment redirects to PhonePe and returns after completion
- [ ] Webhook processes payment and activates subscription
- [ ] User receives email confirmation
- [ ] Dashboard shows active subscription status
- [ ] Failed payments show retry options

### ✅ Technical Requirements
- [ ] All new code has unit tests (>80% coverage)
- [ ] Integration tests cover payment flow
- [ ] Error handling matches Phase 1 standards
- [ ] Security audit passes (webhook validation, input sanitization)
- [ ] Performance benchmarks met (initiation <2s, status check <1s)

### ✅ Business Requirements
- [ ] Payment conversion rate tracked
- [ ] Failed payment recovery flow works
- [ ] Subscription lifecycle management complete
- [ ] Email notifications deliver reliably
- [ ] Customer support can view payment status

---

## Common Pitfalls (What to Avoid)

### ❌ Don't Do This
- Don't store raw payment details in frontend state
- Don't skip webhook signature validation
- Don't implement payment polling without exponential backoff
- Don't forget idempotency handling for webhooks
- Don't hardcode payment amounts or plan IDs

### ✅ Do This Instead
- Use secure backend storage for payment state
- Validate every webhook signature
- Implement proper retry logic with backoff
- Handle duplicate webhook calls gracefully
- Use configuration for payment plans/pricing

---

## Handoff Checklist (What to Verify First)

### 🔍 Environment Setup
- [ ] PhonePe sandbox credentials configured
- [ ] Resend API key configured
- [ ] Database migrations applied
- [ ] Environment variables validated

### 📋 Code Review Points
- [ ] Follow existing error handling patterns
- [ ] Use structured logging throughout
- [ ] Implement proper input validation
- [ ] Add comprehensive tests
- [ ] Document API endpoints

### 🚀 Deployment Readiness
- [ ] All tests passing
- [ ] Security scan passed
- [ ] Performance benchmarks met
- [ ] Documentation updated
- [ ] Monitoring configured

---

## Next Steps After Phase 2

Once Phase 2 is complete, you'll hand off to Phase 3 (Onboarding System) with:
- Working payment flow
- Active subscription management
- Email notification system
- Comprehensive payment analytics

---

## Emergency Contacts

**For Technical Issues**: Check Phase 1 implementation patterns in `backend/services/profile_service.py` and `src/components/auth/AuthProvider.tsx`

**For Architecture Questions**: Reference `.zenflow/tasks/new-task-3ec9/PHASE1_AUTHENTICATION_COMPLETE.md`

**For Business Logic**: Review subscription plans in `backend/core/models.py`

---

## Final Note

Phase 1 set a high bar for quality, security, and maintainability. Match those standards in Phase 2, and the entire system will be robust and production-ready.

**Good luck! The payment system is critical to our business success.**
