# PhonePe Payment Gateway & Subscription Management

This document describes the complete PhonePe payment gateway integration and subscription management system for RaptorFlow.

## Overview

The payment system provides:
- PhonePe Standard Checkout v2 integration
- Subscription lifecycle management
- Role-based access control for billing operations
- Webhook handling for asynchronous payment notifications
- Usage tracking and quota management
- Comprehensive test coverage

## Architecture

### Database Schema

The system uses three main tables:

1. **`plans`** - Subscription plans and their entitlements
2. **`subscriptions`** - Active subscriptions per workspace
3. **`payment_transactions`** - All payment attempts and their status
4. **`subscription_usage`** - Usage tracking for quota management

### API Endpoints

#### Payment Endpoints
- `POST /v1/payments/create` - Create payment session
- `GET /v1/payments/callback` - Handle PhonePe callback
- `POST /v1/payments/webhook` - Webhook for async notifications
- `GET /v1/payments/status/{order_id}` - Check payment status

#### Subscription Endpoints
- `GET /v1/subscriptions` - Get subscription details and usage
- `PUT /v1/subscriptions/cancel` - Cancel subscription

## Setup Instructions

### 1. Database Migration

Run the migration to create the payment tables:

```sql
-- File: migrations/011_subscription_payment_schema.sql
```

### 2. Environment Configuration

Copy the PhonePe environment template:

```bash
cp .env.phonepe.example .env.phonepe
```

Configure the following variables:

```bash
# PhonePe Configuration
PHONEPE_CLIENT_ID=your_client_id
PHONEPE_CLIENT_SECRET=your_client_secret
PHONEPE_ENV=SANDBOX  # or PRODUCTION
PHONEPE_WEBHOOK_USERNAME=webhook_user
PHONEPE_WEBHOOK_PASSWORD=webhook_pass

# Callback URLs
PHONEPE_CALLBACK_URL=https://your-domain.com/v1/payments/callback
PAYMENT_REDIRECT_ALLOWLIST=https://your-domain.com
```

### 3. PhonePe Dashboard Configuration

In your PhonePe dashboard:

1. Set the callback URL to: `https://your-domain.com/v1/payments/webhook`
2. Configure the redirect URLs for success/failure
3. Enable webhooks for payment status updates
4. Set up webhook authentication with username/password

### 4. Frontend Integration

The frontend should:

1. Call `POST /v1/payments/create` to start payment
2. Redirect user to the returned `payment_url`
3. Handle success/failure redirects
4. Poll payment status or rely on webhooks

## API Usage Examples

### Create Payment Session

```bash
curl -X POST "https://api.raptorflow.com/v1/payments/create" \
  -H "Authorization: Bearer {jwt_token}" \
  -H "X-Tenant-ID: {workspace_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_id": "plan_uuid",
    "amount": 2999.00,
    "currency": "INR",
    "return_url": "https://app.raptorflow.com/billing/success"
  }'
```

Response:
```json
{
  "status": "success",
  "payment_url": "https://phonepe.com/pay/merchant_order_123",
  "order_id": "merchant_order_123",
  "transaction_id": "txn_uuid"
}
```

### Get Subscription Details

```bash
curl -X GET "https://api.raptorflow.com/v1/subscriptions" \
  -H "Authorization: Bearer {jwt_token}" \
  -H "X-Tenant-ID: {workspace_id}"
```

Response:
```json
{
  "status": "success",
  "data": {
    "subscription": {
      "id": "sub_uuid",
      "plan_name": "Professional",
      "status": "active",
      "current_period_end": "2024-12-31T23:59:59Z",
      "limits": {
        "icp_profiles": 10,
        "campaigns": 50,
        "users": 10
      }
    },
    "usage": {
      "icp_profiles": {
        "current": 2,
        "limit": 10,
        "percentage": 20.0
      }
    }
  }
}
```

### Cancel Subscription

```bash
curl -X PUT "https://api.raptorflow.com/v1/subscriptions/cancel" \
  -H "Authorization: Bearer {jwt_token}" \
  -H "X-Tenant-ID: {workspace_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "cancellation_reason": "Downgrading to free plan"
  }'
```

## Security Features

### Role-Based Access Control

Only workspace owners can manage billing operations. The system validates:

1. JWT token authentication
2. Workspace ownership via `X-Tenant-ID` header
3. User role permissions

### Payment Security

1. **Amount Validation**: Ensures payment amount matches plan price
2. **Signature Verification**: PhonePe webhook signatures are validated
3. **RBI Compliance**: Autopay limited to ₹5,000 per regulations
4. **Redirect Allowlist**: Only allowed domains can be used for redirects

### Database Security

1. **Row-Level Security**: Tables use RLS policies for workspace isolation
2. **Transaction Integrity**: All operations use database transactions
3. **Audit Trail**: Complete payment history maintained

## Webhook Handling

The system handles PhonePe webhooks for:

- Payment completion notifications
- Payment failure notifications
- Subscription status updates
- Refund processing

### Webhook Flow

1. PhonePe sends webhook to `/v1/payments/webhook`
2. System validates webhook signature
3. Updates payment transaction status
4. Creates/updates subscription if payment successful
5. Sends notification to user
6. Returns acknowledgment to PhonePe

## Testing

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run payment tests
pytest tests/test_phonepe_payments.py -v

# Run with coverage
pytest tests/test_phonepe_payments.py --cov=services/payment_service
```

### Test Coverage

The test suite covers:

- Payment session creation
- Callback handling
- Subscription management
- Role-based access control
- Error scenarios
- Webhook processing

### Mock PhonePe Responses

Tests use mocked PhonePe API responses to ensure:

- No external dependencies during testing
- Consistent test results
- Edge case coverage
- Performance testing

## Monitoring and Logging

### Payment Events Logged

- Payment session creation
- Callback processing
- Subscription changes
- Failed transactions
- Webhook errors

### Monitoring Metrics

Track these metrics for payment health:

- Payment success rate
- Callback processing time
- Webhook delivery success
- Subscription churn rate
- Revenue metrics

## Troubleshooting

### Common Issues

1. **Payment Creation Fails**
   - Check PhonePe API credentials
   - Verify plan exists and is active
   - Ensure workspace ownership

2. **Webhook Not Processing**
   - Verify webhook URL in PhonePe dashboard
   - Check webhook authentication credentials
   - Review webhook logs

3. **Subscription Not Created**
   - Check payment status is "COMPLETED"
   - Verify database connectivity
   - Review transaction records

### Debug Commands

```bash
# Check payment transaction
SELECT * FROM payment_transactions WHERE merchant_order_id = 'order_id';

# Check subscription status
SELECT * FROM subscriptions WHERE workspace_id = 'workspace_id';

# Check webhook logs
grep "webhook" /var/log/raptorflow/payments.log
```

## Production Deployment

### Environment Variables

Set these in production:

```bash
PHONEPE_ENV=PRODUCTION
DATABASE_URL=postgresql://prod_user:pass@db:5432/raptorflow_prod
FRONTEND_URL=https://app.raptorflow.com
```

### Database Considerations

1. Use connection pooling (configured in db.py)
2. Enable row-level security
3. Set up proper indexes for performance
4. Configure backup strategy

### Scaling Considerations

1. **Horizontal Scaling**: Payment service is stateless
2. **Webhook Reliability**: Implement retry mechanism
3. **Database Performance**: Consider read replicas for subscription queries
4. **Caching**: Cache subscription details to reduce database load

## Compliance

### RBI Regulations

- Autopay payments limited to ₹5,000
- Proper transaction logging
- User consent for recurring payments
- Refund policy compliance

### Data Protection

- PCI compliance considerations
- User data encryption
- Audit trail maintenance
- Data retention policies

## Future Enhancements

1. **Multiple Payment Gateways**: Support for Razorpay, Stripe
2. **Subscription Upgrades**: In-place plan upgrades
3. **Usage Analytics**: Detailed usage reporting
4. **Automated Renewals**: Handle subscription renewals
5. **Refund Management**: Automated refund processing

## Support

For payment-related issues:

1. Check application logs
2. Review PhonePe dashboard
3. Verify database connectivity
4. Contact support with transaction IDs

---

**Note**: This implementation follows PhonePe's Standard Checkout v2 documentation and complies with Indian payment regulations.
