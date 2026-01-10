# PhonePe Payment Gateway Integration - Latest 2026
## Updated Authentication System: Client ID + Client Secret (No Salt Key)

## 🚀 Major Changes from Old System
- ❌ **REMOVED**: Salt key, salt index, merchant ID (old system)
- ✅ **NEW**: Client ID + Client Secret authentication only
- ✅ **UPDATED**: OAuth token-based authentication
- ✅ **UPDATED**: Latest PhonePe SDK v2.0 (2026)
- ✅ **UPDATED**: New API endpoints and base URLs

## 🔐 Current Authentication System (2026)

### Required Credentials (Get from PhonePe Business Dashboard)
1. **Client ID** - Your unique client identifier
2. **Client Secret** - Your secret key for authentication
3. **Client Version** - SDK version (default: 1)

### Environment Setup
- **UAT/Sandbox**: `https://api-preprod.phonepe.com/apis/pg-sandbox`
- **Production**: `https://api.phonepe.com/apis/pg`

## 📋 Environment Variables (2026)

```bash
# CURRENT SYSTEM - Client ID + Client Secret only (2026)
PHONEPE_CLIENT_ID=YOUR_CLIENT_ID_FROM_DASHBOARD
PHONEPE_CLIENT_SECRET=YOUR_CLIENT_SECRET_FROM_DASHBOARD
PHONEPE_CLIENT_VERSION=1

# Environment
PHONEPE_ENV=UAT  # or PRODUCTION

# Webhook
PHONEPE_WEBHOOK_USERNAME=raptorflow_webhook
PHONEPE_WEBHOOK_PASSWORD=raptorflow_webhook_secure_2026
```

## 🔧 API Changes (2026)

### Authentication Flow
1. Get OAuth token using Client ID + Client Secret:
```bash
curl --location 'https://api-preprod.phonepe.com/apis/pg-sandbox/v1/oauth/token' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'client_id=CLIENT_ID' \
--data-urlencode 'client_version=1' \
--data-urlencode 'client_secret=CLIENT_SECRET' \
--data-urlencode 'grant_type=client_credentials'
```

2. Use token for all subsequent API calls

### Updated Endpoints (2026)
- **Payment Initiation**: Uses new SDK methods
- **Status Check**: Now uses merchant order ID
- **Refund**: Updated request/response format
- **Webhooks**: New payload structure

## 🐍 Python SDK Integration (2026)

### Initialization
```python
from phonepe.sdk.pg.payments.v2.standard_checkout_client import StandardCheckoutClient
from phonepe.sdk.pg.env import Env

client = StandardCheckoutClient.get_instance(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    client_version=1,
    env=Env.UAT,
    should_publish_events=False
)
```

### Payment Initiation (2026)
```python
from phonepe.sdk.pg.payments.v2.models.request.standard_checkout_pay_request import StandardCheckoutPayRequest
from phonepe.sdk.pg.common.models.request.meta_info import MetaInfo

# Build request
payment_request = StandardCheckoutPayRequest.build_request(
    merchant_order_id="unique_order_id",
    amount=10000,  # Amount in paise
    redirect_url="https://your-site.com/redirect",
    meta_info=MetaInfo.builder()
        .udf1("customer_name")
        .udf2("customer_email")
        .build()
)

# Process payment
response = client.pay(payment_request)
checkout_url = response.redirect_url
```

### Status Check (2026)
```python
# Check status using merchant order ID
response = client.get_order_status(merchant_order_id, details=True)
status = response.state
```

### Refund (2026)
```python
from phonepe.sdk.pg.common.models.request.refund_request import RefundRequest

refund_request = RefundRequest.build_refund_request(
    merchant_refund_id="unique_refund_id",
    original_merchant_order_id="original_order_id",
    amount=5000
)

refund_response = client.refund(refund_request)
```

## 🗄️ Database Schema (2026)

The database schema remains the same but note:
- `merchant_order_id` is now the primary identifier
- `phonepe_transaction_id` is returned by PhonePe
- Webhook payload structure has changed

## 🔄 Migration Steps (2026)

### 1. Update Environment Variables
```bash
# Remove old variables
# PHONEPE_MERCHANT_ID, PHONEPE_SALT_KEY, PHONEPE_SALT_INDEX

# Add new variables (2026)
PHONEPE_CLIENT_ID=YOUR_CLIENT_ID_FROM_DASHBOARD
PHONEPE_CLIENT_SECRET=YOUR_CLIENT_SECRET_FROM_DASHBOARD
```

### 2. Update Backend Code (2026)
- Replace old gateway service with new one
- Update API endpoints to use merchant order ID
- Implement OAuth token handling

### 3. Update Frontend (2026)
- Update payment store to use new API responses
- Update status tracking to use merchant order ID
- Test with new webhook format

### 4. Get New Credentials (2026)
1. Login to [PhonePe Business Dashboard](https://business.phonepe.com)
2. Go to Developer Settings
3. Copy Client ID and Client Secret
4. Update environment variables

## 🧪 Testing (2026)

### UAT/Sandbox Testing
- Use UAT environment for initial testing
- Test credentials available from PhonePe integration team
- Webhook testing endpoints available

### Test Payment Flow (2026)
1. Initiate payment → Get checkout URL
2. Complete payment in sandbox
3. Check status using merchant order ID
4. Test refund flow
5. Verify webhook callbacks

## 🚨 Important Notes (2026)

### Security
- **NEVER** expose Client Secret in frontend code
- Use environment variables for credentials
- Implement proper webhook validation

### Breaking Changes (2026)
- Old salt key authentication no longer works
- API response formats have changed
- Webhook payload structure is different

### Support (2026)
- Contact PhonePe integration team for test credentials
- Check [PhonePe Developer Docs](https://developer.phonepe.com) for latest updates
- Use Postman collections for API testing

## ✅ Integration Checklist (2026)

- [ ] Get Client ID and Client Secret from dashboard
- [ ] Update environment variables
- [ ] Install latest PhonePe SDK
- [ ] Update backend authentication logic
- [ ] Test payment initiation in UAT
- [ ] Test status checking
- [ ] Test refund flow
- [ ] Set up webhooks
- [ ] Test end-to-end flow
- [ ] Deploy to production

---

**Last Updated**: January 2026
**PhonePe API Version**: v2.0
**Authentication**: Client ID + Client Secret
**Status**: ✅ Latest 2026 Integration
**Year**: 2026
