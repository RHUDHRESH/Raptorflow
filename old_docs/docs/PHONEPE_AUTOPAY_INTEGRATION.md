# PhonePe Autopay Integration Guide

This guide covers the PhonePe Autopay (recurring payments) integration in RaptorFlow 2.0.

## Overview

PhonePe Autopay enables recurring subscription payments for RaptorFlow's subscription plans:
- **Ascent Plan**: ₹2,499/month or ₹24,999/year
- **Glide Plan**: ₹6,499/month or ₹64,999/year
- **Soar Plan**: ₹16,499/month or ₹164,999/year

## Architecture

### Components

1. **PhonePe SDK**: Official Python SDK (v2.1.5+) for autopay
2. **Service Layer**: `backend/services/phonepe_autopay_service.py`
3. **Models**: `backend/models/payment.py` (Autopay section)
4. **API Router**: `backend/routers/autopay.py`
5. **Configuration**: Environment variables in `.env`

### Flow

```
User → Frontend → API Endpoint → Autopay Service → PhonePe SDK → PhonePe Gateway
                                                                        ↓
                                                                   Webhook
                                                                        ↓
                                                    Backend ← Process Event
```

## Setup

### 1. Prerequisites

- PhonePe Business Account
- Autopay credentials (Client ID, Client Secret, Client Version)
- Python 3.9 or higher

### 2. Install Dependencies

```bash
cd backend
pip install --index-url https://phonepe.mycloudrepo.io/public/repositories/phonepe-pg-sdk-python --extra-index-url https://pypi.org/simple phonepe_sdk
```

### 3. Environment Configuration

Add these variables to your `.env` file:

```env
# PhonePe Autopay (Recurring Payments)
PHONEPE_AUTOPAY_CLIENT_ID=your_phonepe_autopay_client_id
PHONEPE_AUTOPAY_CLIENT_SECRET=your_phonepe_autopay_client_secret
PHONEPE_AUTOPAY_CLIENT_VERSION=1
PHONEPE_AUTOPAY_ENABLED=True

# Environment (affects SDK mode)
ENVIRONMENT=development  # or production
```

**Important**:
- Use UAT credentials for `development` environment
- Use production credentials for `production` environment
- The SDK automatically switches between UAT and PROD based on `ENVIRONMENT`

### 4. Test Credentials

Contact PhonePe Integration team for:
- UAT Client ID
- UAT Client Secret
- Production credentials (after testing)

## API Endpoints

### 1. Create Autopay Checkout Session

**Endpoint**: `POST /api/v1/autopay/checkout/create`

**Description**: Creates a new autopay subscription and returns authorization URL

**Request Body**:
```json
{
  "plan": "ascent",
  "billing_period": "monthly",
  "mobile_number": "+919876543210",
  "success_url": "https://yourapp.com/success",
  "cancel_url": "https://yourapp.com/cancel"
}
```

**Response**:
```json
{
  "authorization_url": "https://mercury-uat.phonepe.com/autopay/...",
  "subscription_id": "SUB123...",
  "merchant_subscription_id": "SUB456...",
  "expires_at": "2025-11-23T12:00:00Z"
}
```

**Usage**:
1. Call this endpoint to create a subscription
2. Redirect user to `authorization_url`
3. User authorizes the autopay mandate
4. PhonePe redirects to `success_url` or `cancel_url`
5. Webhook notifies your backend of activation

### 2. Check Subscription Status

**Endpoint**: `GET /api/v1/autopay/subscription/status/{merchant_subscription_id}`

**Description**: Get current status of a subscription

**Response**:
```json
{
  "subscription_id": "SUB123...",
  "merchant_subscription_id": "SUB456...",
  "status": "active",
  "amount": 249900,
  "start_date": "2025-11-23T00:00:00Z",
  "end_date": "2026-11-23T00:00:00Z",
  "billing_frequency": "MONTHLY",
  "next_billing_date": "2025-12-23T00:00:00Z",
  "payment_stats": {
    "total": 5,
    "successful": 4,
    "failed": 1
  }
}
```

**Status Values**:
- `pending`: Awaiting user authorization
- `active`: Subscription is active and billing
- `paused`: Temporarily paused
- `cancelled`: Cancelled by user or system
- `expired`: Subscription period ended

### 3. Cancel Subscription

**Endpoint**: `POST /api/v1/autopay/subscription/cancel`

**Request Body**:
```json
{
  "merchant_subscription_id": "SUB456...",
  "reason": "User requested cancellation"
}
```

**Response**:
```json
{
  "message": "Autopay subscription cancelled successfully",
  "cancelled": true,
  "merchant_subscription_id": "SUB456...",
  "correlation_id": "corr_123..."
}
```

### 4. Pause Subscription

**Endpoint**: `POST /api/v1/autopay/subscription/pause`

**Request Body**:
```json
{
  "merchant_subscription_id": "SUB456...",
  "reason": "Temporary pause requested"
}
```

### 5. Resume Subscription

**Endpoint**: `POST /api/v1/autopay/subscription/resume`

**Request Body**:
```json
{
  "merchant_subscription_id": "SUB456..."
}
```

### 6. Get User Subscriptions

**Endpoint**: `GET /api/v1/autopay/subscriptions`

**Description**: Get all subscriptions for authenticated user

**Response**:
```json
{
  "subscriptions": [
    {
      "subscription_id": "SUB123...",
      "merchant_subscription_id": "SUB456...",
      "plan": "ascent",
      "status": "active",
      "amount": 249900,
      "billing_period": "monthly"
    }
  ],
  "total_count": 1
}
```

### 7. Webhook Handler

**Endpoint**: `POST /api/v1/autopay/webhook`

**Description**: Receives PhonePe autopay event notifications

**Events Handled**:
- `SUBSCRIPTION_ACTIVATED`: User authorized mandate
- `PAYMENT_SUCCESS`: Recurring payment succeeded
- `PAYMENT_FAILED`: Recurring payment failed
- `SUBSCRIPTION_CANCELLED`: Subscription cancelled

**Webhook Configuration**:
Configure this URL in PhonePe Dashboard:
```
https://your-domain.com/api/v1/autopay/webhook
```

## Service Layer

### PhonePeAutopayService

Located in `backend/services/phonepe_autopay_service.py`

**Key Methods**:

1. **`create_subscription(request)`**
   - Creates autopay subscription
   - Returns authorization URL
   - Stores pending subscription

2. **`check_subscription_status(merchant_subscription_id)`**
   - Checks subscription status with PhonePe
   - Returns detailed status including payment history

3. **`cancel_subscription(merchant_subscription_id)`**
   - Cancels active subscription
   - Updates database

4. **`pause_subscription(merchant_subscription_id)`**
   - Pauses recurring billing

5. **`resume_subscription(merchant_subscription_id)`**
   - Resumes paused subscription

## Database Schema

### autopay_subscriptions Table

```sql
CREATE TABLE autopay_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    workspace_id UUID NOT NULL REFERENCES workspaces(id),
    subscription_id VARCHAR(255) NOT NULL,
    merchant_subscription_id VARCHAR(255) NOT NULL UNIQUE,
    amount INTEGER NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    status VARCHAR(50) NOT NULL,
    plan VARCHAR(50) NOT NULL,
    billing_period VARCHAR(20) NOT NULL,
    billing_frequency VARCHAR(20) NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    next_billing_date TIMESTAMP,
    mobile_number VARCHAR(20),
    activated_at TIMESTAMP,
    paused_at TIMESTAMP,
    resumed_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    cancellation_reason TEXT,
    pause_reason TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_autopay_user_id ON autopay_subscriptions(user_id);
CREATE INDEX idx_autopay_merchant_sub_id ON autopay_subscriptions(merchant_subscription_id);
CREATE INDEX idx_autopay_status ON autopay_subscriptions(status);
```

### autopay_payments Table

```sql
CREATE TABLE autopay_payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_subscription_id VARCHAR(255) NOT NULL,
    payment_id VARCHAR(255) NOT NULL UNIQUE,
    amount INTEGER NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    status VARCHAR(50) NOT NULL,
    payment_date TIMESTAMP NOT NULL,
    failure_reason TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_autopay_payments_sub_id ON autopay_payments(merchant_subscription_id);
CREATE INDEX idx_autopay_payments_status ON autopay_payments(status);
```

## Error Handling

### Common Errors

1. **Autopay client not initialized**
   - Check environment variables
   - Verify credentials

2. **Subscription creation failed**
   - Validate mobile number format
   - Check amount and plan details
   - Verify callback/redirect URLs

3. **Status check failed**
   - Subscription may not exist
   - Check merchant_subscription_id

4. **Cancellation failed**
   - Subscription may already be cancelled
   - Invalid subscription ID

### Error Response Format

```json
{
  "detail": "Error message description",
  "status_code": 400
}
```

## Testing

### UAT Environment

1. Use UAT credentials in `.env`
2. Set `ENVIRONMENT=development`
3. Test subscription flow:
   ```bash
   curl -X POST http://localhost:8000/api/v1/autopay/checkout/create \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{
       "plan": "ascent",
       "billing_period": "monthly",
       "mobile_number": "+919876543210",
       "success_url": "http://localhost:3000/success",
       "cancel_url": "http://localhost:3000/cancel"
     }'
   ```

4. Visit authorization URL
5. Complete authorization flow
6. Check webhook logs

### Production

1. Switch to production credentials
2. Set `ENVIRONMENT=production`
3. Update webhook URL in PhonePe Dashboard
4. Monitor logs for errors

## Frontend Integration

### React Example

```typescript
// Create autopay checkout
const createAutopaySubscription = async (plan: string, billingPeriod: string) => {
  try {
    const response = await fetch('/api/v1/autopay/checkout/create', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        plan,
        billing_period: billingPeriod,
        mobile_number: user.mobileNumber,
        success_url: `${window.location.origin}/subscription/success`,
        cancel_url: `${window.location.origin}/subscription/cancel`
      })
    });

    const data = await response.json();

    // Redirect to PhonePe authorization page
    window.location.href = data.authorization_url;
  } catch (error) {
    console.error('Subscription creation failed:', error);
  }
};

// Check subscription status
const checkSubscriptionStatus = async (merchantSubId: string) => {
  const response = await fetch(
    `/api/v1/autopay/subscription/status/${merchantSubId}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  return response.json();
};

// Cancel subscription
const cancelSubscription = async (merchantSubId: string, reason: string) => {
  const response = await fetch('/api/v1/autopay/subscription/cancel', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      merchant_subscription_id: merchantSubId,
      reason
    })
  });
  return response.json();
};
```

## Security Best Practices

1. **Never expose credentials**
   - Keep credentials in `.env`
   - Never commit credentials to git
   - Use different credentials for UAT and production

2. **Validate webhook signatures**
   - PhonePe SDK handles signature verification
   - Always verify webhook authenticity

3. **Secure endpoints**
   - Require authentication for all endpoints
   - Validate user ownership of subscriptions
   - Rate limit webhook endpoint

4. **HTTPS only**
   - Use HTTPS in production
   - Secure callback and webhook URLs

## Monitoring

### Key Metrics

1. **Subscription Creation Rate**
2. **Authorization Completion Rate**
3. **Payment Success Rate**
4. **Payment Failure Rate**
5. **Cancellation Rate**

### Logging

All operations log to structured logger:

```python
logger.info(f"Creating autopay subscription for user {user_id}")
logger.error(f"Autopay payment failed: {error}")
```

## Support

### PhonePe Support
- Documentation: https://developer.phonepe.com/
- Support: integration@phonepe.com

### Internal Support
- Backend Team: Check `backend/services/phonepe_autopay_service.py`
- Issues: GitHub Issues

## Changelog

### v2.1.0 (2025-11-23)
- Initial PhonePe Autopay integration
- Support for monthly and yearly subscriptions
- Webhook handling for autopay events
- Pause/Resume functionality
- Comprehensive error handling

## License

Proprietary - RaptorFlow 2.0
