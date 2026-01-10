# PhonePe Payment Gateway Integration

## Overview
This integration provides a complete PhonePe payment gateway solution for Raptorflow, replacing any existing payment providers with PhonePe as the sole payment partner.

## Features Implemented

### ✅ Core Payment Services
- **Payment Initiation**: Create and initiate payment transactions
- **Status Checking**: Real-time payment status verification
- **Webhook Handling**: Secure webhook processing and validation
- **Refund Processing**: Complete refund workflow
- **Error Handling**: Comprehensive error management

### ✅ API Endpoints
- `POST /api/payments/initiate` - Initiate new payment
- `GET /api/payments/status/{transaction_id}` - Check payment status
- `POST /api/payments/webhook` - Handle PhonePe webhooks
- `POST /api/payments/refund` - Process refunds
- `GET /api/payments/health` - Service health check

### ✅ Database Schema
- **payment_transactions**: Main transaction records
- **payment_refunds**: Refund tracking
- **payment_webhook_logs**: Webhook audit logs
- **payment_events_log**: Event audit trail

### ✅ Security Features
- Webhook signature validation
- Row-level security policies
- Secure credential management
- Request/response logging

## Configuration

### Environment Variables
Add these to your `.env` file:

```bash
# PhonePe API Credentials
PHONEPE_CLIENT_ID=your_phonepe_client_id
PHONEPE_CLIENT_SECRET=your_phonepe_client_secret
PHONEPE_CLIENT_VERSION=1
PHONEPE_MERCHANT_ID=your_phonepe_merchant_id
PHONEPE_SALT_KEY=your_phonepe_salt_key
PHONEPE_KEY_INDEX=1

# Environment
PHONEPE_ENV=sandbox  # or production

# Webhook Configuration
PHONEPE_WEBHOOK_USERNAME=your_webhook_username
PHONEPE_WEBHOOK_PASSWORD=your_webhook_password

# Callback URLs
PHONEPE_SUCCESS_URL=http://localhost:3000/payment/success
PHONEPE_FAILURE_URL=http://localhost:3000/payment/failure
PHONEPE_WEBHOOK_URL=http://localhost:8000/api/payments/webhook
```

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Database Migration
```bash
psql -d your_database -f backend/backend-clean/core/migrations/001_phonepe_payment_schema.sql
```

### 3. Configure Environment
Copy `.env.example` to `.env` and fill in your PhonePe credentials.

## Usage Examples

### Initiate Payment
```python
import requests

payment_data = {
    "amount": 10000,  # 100 INR in paise
    "merchant_order_id": "ORDER123",
    "redirect_url": "https://your-app.com/payment/success",
    "callback_url": "https://your-app.com/api/webhook",
    "customer_info": {
        "id": "CUST123",
        "name": "John Doe",
        "email": "john@example.com",
        "mobile": "9876543210"
    }
}

response = requests.post(
    "http://localhost:8000/api/payments/initiate",
    json=payment_data
)

if response.json()['success']:
    checkout_url = response.json()['checkout_url']
    # Redirect user to checkout_url
```

### Check Payment Status
```python
transaction_id = "TXN123456789"
response = requests.get(f"http://localhost:8000/api/payments/status/{transaction_id}")

status_data = response.json()
print(f"Payment Status: {status_data['status']}")
```

### Process Refund
```python
refund_data = {
    "transaction_id": "TXN123456789",
    "refund_amount": 10000,
    "refund_reason": "Customer requested refund"
}

response = requests.post(
    "http://localhost:8000/api/payments/refund",
    json=refund_data
)
```

## PhonePe Dashboard Setup

### 1. Get PhonePe Credentials
1. Sign up at [PhonePe Business Dashboard](https://business.phonepe.com)
2. Complete onboarding and KYC
3. Get your API credentials from the dashboard
4. Configure webhook URLs in the PhonePe dashboard

### 2. Webhook Configuration
- Set webhook URL: `https://your-domain.com/api/payments/webhook`
- Configure username and password for webhook authentication
- Test webhook endpoints in sandbox mode

## Testing

### Sandbox Testing
Use the sandbox environment for testing:
```bash
PHONEPE_ENV=sandbox
```

### Test Cards/UPI
PhonePe sandbox provides test payment methods:
- UPI: test@phonepe (any 4-digit PIN)
- Cards: Use test card numbers provided in PhonePe documentation

## Monitoring

### Health Check
```bash
curl http://localhost:8000/api/payments/health
```

### Logs
Payment events are logged to:
- Application logs
- Database `payment_events_log` table
- Webhook logs in `payment_webhook_logs` table

## Security Notes

### 🔐 Credential Security
- Store PhonePe credentials in environment variables
- Never commit credentials to version control
- Use different credentials for sandbox and production

### 🔒 Webhook Security
- Always validate webhook signatures
- Use HTTPS for webhook endpoints
- Implement rate limiting for webhook endpoints

### 🛡️ Data Protection
- Customer data is encrypted at rest
- Payment logs are retained according to PCI DSS
- Row-level security restricts data access

## Troubleshooting

### Common Issues

#### 1. Payment Initiation Failed
- Check PhonePe credentials
- Verify webhook configuration
- Ensure sufficient account balance

#### 2. Webhook Not Received
- Verify webhook URL is accessible
- Check firewall settings
- Validate webhook authentication

#### 3. Refund Processing Failed
- Check original transaction status
- Verify refund amount limits
- Ensure sufficient merchant balance

### Error Codes
- `400`: Bad request - invalid parameters
- `401`: Unauthorized - invalid credentials
- `404`: Not found - transaction doesn't exist
- `500`: Internal server error - contact support

## Support

### PhonePe Support
- Merchant support: support@phonepe.com
- Technical documentation: https://developer.phonepe.com
- API status: https://status.phonepe.com

### Internal Support
- Check application logs for detailed errors
- Monitor database for failed transactions
- Use health check endpoint for service status

## Migration Notes

This integration completely replaces any existing payment gateways:
- ❌ Stripe removed
- ❌ Razorpay removed
- ❌ PayPal removed
- ✅ PhonePe only payment provider

All payment flows now route through PhonePe exclusively.
