# PhonePe Payment Integration Guide

## Overview

RaptorFlow uses PhonePe payment gateway for subscription payments with comprehensive webhook handling, retry logic, and email notifications.

## Architecture

```
Frontend (Next.js) → API Proxy → Backend (FastAPI) → PhonePe API
                    ↓                 ↓                ↓
                Payment Poller → Payment Service → PhonePe Gateway
                    ↓                 ↓                ↓
                Webhook Proxy ← Webhook Handler ← PhonePe Webhooks
```

## Environment Variables

### Required Environment Variables

```bash
# PhonePe Configuration
PHONEPE_MERCHANT_ID=your_merchant_id
PHONEPE_SALT_KEY=your_salt_key
PHONEPE_SALT_INDEX=1
PHONEPE_ENVIRONMENT=sandbox  # or production

# API Endpoints
NEXT_PUBLIC_APP_URL=http://localhost:3000  # Frontend URL
NEXT_PUBLIC_API_URL=http://localhost:8000  # Backend URL

# Email Service (Resend)
RESEND_API_KEY=your_resend_api_key
FROM_EMAIL=noreply@yourapp.com
```

### PhonePe Sandbox Setup

1. Create a PhonePe developer account
2. Get sandbox merchant ID and salt key
3. Configure webhook URL: `https://yourdomain.com/api/webhooks/phonepe`
4. Test with sandbox environment first

## Payment Flow

### 1. Payment Initiation

```typescript
// Frontend: POST /api/payments/v2/initiate
{
  "plan": "starter",  // starter, growth, enterprise
  "redirect_url": "https://yourapp.com/onboarding/plans/callback",
  "webhook_url": "https://yourapp.com/api/webhooks/phonepe"
}
```

### 2. Payment Processing

- User redirected to PhonePe payment page
- Payment polling starts on frontend (2s intervals, exponential backoff)
- PhonePe processes payment

### 3. Webhook Handling

- PhonePe sends webhook to `/api/webhooks/phonepe`
- Frontend proxy forwards to backend `/api/payments/v2/webhook`
- Backend validates signature and processes payment
- Subscription activated on success

### 4. Status Polling

- Frontend polls `/api/payments/status/{merchant_order_id}`
- Stops when payment completed/failed or timeout (5 minutes)
- Updates UI in real-time

## Security Features

### Signature Validation

```python
# Webhook signature validation
verify_string = f"{webhook_body}{salt_key}"
expected_signature = sha256(verify_string) + f"###{salt_index}"
```

### Idempotency

- Unique merchant order IDs prevent duplicate payments
- Webhook replay protection (TODO: implement Redis tracking)
- Idempotency keys for API requests (TODO: implement Redis caching)

### Rate Limiting

- Payment initiation limited by workspace tier
- Webhook processing with background tasks
- Status polling with exponential backoff

## Payment Plans

```python
PLANS = {
    "starter": {
        "amount": 4900,      # ₹49/month
        "name": "STARTER",
        "trial_days": 7
    },
    "growth": {
        "amount": 14900,     # ₹149/month
        "name": "GROWTH",
        "trial_days": 7
    },
    "enterprise": {
        "amount": 49900,     # ₹499/month
        "name": "ENTERPRISE",
        "trial_days": 7
    }
}
```

## Database Schema

### payment_transactions Table

```sql
CREATE TABLE payment_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id),
    merchant_order_id VARCHAR(50) UNIQUE NOT NULL,
    phonepe_transaction_id VARCHAR(100),
    amount INTEGER NOT NULL,  -- in paise
    currency VARCHAR(3) DEFAULT 'INR',
    status VARCHAR(20) DEFAULT 'pending',  -- pending, completed, failed
    plan VARCHAR(20) NOT NULL,
    customer_email VARCHAR(255) NOT NULL,
    customer_name VARCHAR(255),
    payment_method VARCHAR(50) DEFAULT 'phonepe',
    phonepe_response JSONB,
    payment_url TEXT,
    expires_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    failed_at TIMESTAMP WITH TIME ZONE,
    webhook_processed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### subscriptions Table

```sql
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id),
    plan VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',  -- active, cancelled, expired
    current_period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    current_period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    trial_end TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(workspace_id)
);
```

## API Endpoints

### Frontend API Routes

- `POST /api/webhooks/phonepe` - Webhook proxy
- `GET /api/payments/status/{order_id}` - Status check (proxied)

### Backend API Routes

- `POST /api/payments/v2/initiate` - Initiate payment
- `GET /api/payments/v2/status/{order_id}` - Check status
- `POST /api/payments/v2/webhook` - Handle webhook
- `GET /api/payments/v2/plans` - Get plans
- `GET /api/payments/v2/health` - Health check

## Error Handling

### Payment Errors

- `INVALID_PLAN` - Plan not found
- `AMOUNT_MISMATCH` - Amount doesn't match plan
- `PAYMENT_INITIATION_FAILED` - PhonePe API error
- `TRANSACTION_NOT_FOUND` - Order ID not found
- `WEBHOOK_SIGNATURE_MISMATCH` - Invalid webhook signature

### Retry Logic

- Payment initiation: No retry (user must retry)
- Status polling: Exponential backoff, max 30 attempts
- Webhook processing: Background task, logged on failure

## Testing

### Manual Testing Checklist

1. **Sandbox Testing**
   - [ ] Test all three plans (starter, growth, enterprise)
   - [ ] Test successful payment flow
   - [ ] Test failed payment flow
   - [ ] Test webhook signature validation
   - [ ] Test email notifications

2. **Edge Cases**
   - [ ] Test duplicate webhook handling
   - [ ] Test timeout scenarios
   - [ ] Test network failures
   - [ ] Test invalid signatures

3. **Integration Testing**
   - [ ] Test end-to-end payment flow
   - [ ] Test subscription activation
   - [ ] Test payment polling
   - [ ] Test email delivery

### Automated Tests

```bash
# Backend tests
cd backend
python -m pytest tests/test_payment_service.py -v
python -m pytest tests/test_phonepe_gateway.py -v

# Frontend tests
cd frontend
npm run test payment-polling
npm run test payment-api
```

## Monitoring

### Key Metrics

- Payment initiation success rate
- Payment completion rate
- Webhook processing time
- Email delivery rate
- Error rates by type

### Alerts

- Payment initiation failure rate > 5%
- Webhook processing failures
- Email service failures
- PhonePe API errors

## Troubleshooting

### Common Issues

1. **Webhook signature validation failed**
   - Check salt key and index
   - Verify webhook body encoding
   - Check PhonePe sandbox vs production

2. **Payment not completing**
   - Check webhook URL configuration
   - Verify PhonePe merchant setup
   - Check backend logs for errors

3. **Email not sending**
   - Verify Resend API key
   - Check FROM email configuration
   - Check email templates

### Debug Commands

```bash
# Check payment transaction
psql "SELECT * FROM payment_transactions WHERE merchant_order_id = 'ORD123';"

# Check subscription
psql "SELECT * FROM subscriptions WHERE workspace_id = 'workspace-123';"

# Check logs
tail -f backend/logs/payment.log
```

## Deployment

### Production Checklist

- [ ] Update PhonePe credentials to production
- [ ] Configure production webhook URLs
- [ ] Update email templates with production domain
- [ ] Set up monitoring and alerts
- [ ] Test production payment flow
- [ ] Verify SSL certificates
- [ ] Configure rate limiting

### Rollback Plan

1. Switch to sandbox environment
2. Disable payment initiation
3. Keep webhook processing active
4. Monitor existing payments
5. Communicate with users

## Security Considerations

- Never log sensitive payment data
- Use HTTPS for all payment endpoints
- Validate all webhook signatures
- Implement rate limiting
- Monitor for suspicious activity
- Keep PhonePe credentials secure
- Use environment variables for secrets

## Compliance

- PCI DSS compliance for payment handling
- Data privacy regulations
- Audit logging for all payment events
- Secure storage of payment records
