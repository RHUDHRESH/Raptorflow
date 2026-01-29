# PhonePe + Resend Environment Variables Setup Guide

This document provides comprehensive setup instructions for PhonePe payment gateway and Resend email service integration in Raptorflow.

## Overview

Raptorflow uses PhonePe for payment processing and Resend for transactional emails. Both services require proper environment variable configuration for secure and reliable operation.

## PhonePe Environment Variables

### Required Variables

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `PHONEPE_MERCHANT_ID` | PhonePe merchant ID provided by PhonePe | `MERCHANT123456` | ✅ Yes |
| `PHONEPE_SALT_KEY` | Salt key for signature validation | `salt_key_abc123` | ✅ Yes |
| `PHONEPE_SALT_INDEX` | Salt index (usually 1) | `1` | ✅ Yes |
| `PHONEPE_ENVIRONMENT` | Environment (sandbox/production) | `sandbox` | ✅ Yes |

### Optional Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|----------|
| `PHONEPE_TIMEOUT` | API request timeout in seconds | `30` | `30` |
| `PHONEPE_RETRY_COUNT` | Number of retry attempts | `3` | `3` |
| `PHONEPE_WEBHOOK_SECRET` | Additional webhook security secret | - | `webhook_secret_123` |

### Configuration Examples

#### Development (.env.local)
```bash
# PhonePe Sandbox Configuration
PHONEPE_MERCHANT_ID=PGTESTPAYUAT
PHONEPE_SALT_KEY=099eb0cd692a5a511174e0d2bfa5da59
PHONEPE_SALT_INDEX=1
PHONEPE_ENVIRONMENT=sandbox
PHONEPE_TIMEOUT=30
PHONEPE_RETRY_COUNT=3
```

#### Production (.env.production)
```bash
# PhonePe Production Configuration
PHONEPE_MERCHANT_ID=YOUR_PROD_MERCHANT_ID
PHONEPE_SALT_KEY=YOUR_PROD_SALT_KEY
PHONEPE_SALT_INDEX=1
PHONEPE_ENVIRONMENT=production
PHONEPE_TIMEOUT=30
PHONEPE_RETRY_COUNT=3
PHONEPE_WEBHOOK_SECRET=your_webhook_secret_here
```

## Resend Environment Variables

### Required Variables

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `RESEND_API_KEY` | Resend API key for email sending | `re_123456789` | ✅ Yes |
| `RESEND_FROM_EMAIL` | Default sender email address | `noreply@yourdomain.com` | ✅ Yes |

### Optional Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|----------|
| `RESEND_FROM_NAME` | Default sender name | `Raptorflow` | `Your Company` |
| `RESEND_REPLY_TO` | Reply-to email address | `support@yourdomain.com` | `support@yourdomain.com` |
| `RESEND_TIMEOUT` | API request timeout in seconds | `10` | `10` |

### Configuration Examples

#### Development (.env.local)
```bash
# Resend Configuration
RESEND_API_KEY=re_123456789abcdefghijk
RESEND_FROM_EMAIL=noreply@raptorflow.dev
RESEND_FROM_NAME=Raptorflow Development
RESEND_REPLY_TO=dev-support@raptorflow.dev
RESEND_TIMEOUT=10
```

#### Production (.env.production)
```bash
# Resend Production Configuration
RESEND_API_KEY=re_prod_123456789abcdefghijk
RESEND_FROM_EMAIL=noreply@raptorflow.com
RESEND_FROM_NAME=Raptorflow
RESEND_REPLY_TO=support@raptorflow.com
RESEND_TIMEOUT=10
```

## Frontend Environment Variables

### Required for Payment Flow

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `NEXT_PUBLIC_APP_URL` | Frontend application URL | `http://localhost:3000` | ✅ Yes |
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` | ✅ Yes |

### Configuration Examples

#### Development (.env.local)
```bash
# Frontend URLs
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### Production (.env.production)
```bash
# Production URLs
NEXT_PUBLIC_APP_URL=https://app.raptorflow.com
NEXT_PUBLIC_API_URL=https://api.raptorflow.com
```

## Backend Environment Variables

### Database Connection

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `SUPABASE_URL` | Supabase project URL | `https://your-project.supabase.co` | ✅ Yes |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key | `your-service-role-key` | ✅ Yes |

### Redis Configuration

| Variable | Description | Example | Default | Required |
|----------|-------------|---------|---------|----------|
| `REDIS_HOST` | Redis server host | `localhost` | `localhost` | ✅ Yes |
| `REDIS_PORT` | Redis server port | `6379` | `6379` | ✅ Yes |
| `REDIS_PASSWORD` | Redis password | `your_redis_password` | - | ❌ No |
| `REDIS_DB` | Redis database number | `0` | `0` | ❌ No |

## Setup Instructions

### 1. PhonePe Setup

#### Sandbox Environment
1. Register on [PhonePe Developer Portal](https://developer.phonepe.com/)
2. Create a new app in sandbox mode
3. Note down the merchant ID and salt key
4. Configure webhook URLs:
   - Success: `https://your-domain.com/api/webhooks/phonepe`
   - Failure: `https://your-domain.com/api/webhooks/phonepe`

#### Production Environment
1. Complete KYC and compliance requirements
2. Request production credentials
3. Update webhook URLs to production endpoints
4. Test with small amounts before going live

### 2. Resend Setup

1. Sign up at [Resend](https://resend.com/)
2. Verify your domain
3. Create API keys for development and production
4. Configure sender email addresses
5. Test email templates

### 3. Environment Configuration

#### Backend Configuration
```bash
# Copy example environment file
cp backend/.env.example backend/.env.local

# Edit with your credentials
nano backend/.env.local
```

#### Frontend Configuration
```bash
# Copy example environment file
cp frontend/.env.example frontend/.env.local

# Edit with your URLs
nano frontend/.env.local
```

## Security Considerations

### PhonePe Security
1. **Never commit salt keys to version control**
2. **Use different keys for development and production**
3. **Implement webhook signature validation**
4. **Monitor webhook delivery and failures**
5. **Set up IP whitelisting if available**

### Resend Security
1. **Keep API keys secure**
2. **Use domain verification**
3. **Monitor email delivery rates**
4. **Set up bounce and complaint handling**
5. **Implement rate limiting**

### General Security
1. **Use environment-specific keys**
2. **Rotate keys periodically**
3. **Monitor usage and costs**
4. **Implement proper error handling**
5. **Set up logging and alerts**

## Testing Checklist

### PhonePe Testing
- [ ] Sandbox payment initiation works
- [ ] Payment status polling functions correctly
- [ ] Webhook signature validation passes
- [ ] Subscription activation triggers
- [ ] Email notifications are sent
- [ ] Error handling works for failed payments
- [ ] Timeout scenarios are handled

### Resend Testing
- [ ] Payment confirmation emails are sent
- [ ] Payment failure emails are sent
- [ ] Email templates render correctly
- [ ] Sender verification passes
- [ ] Bounce handling works
- [ ] Rate limiting is respected

### Integration Testing
- [ ] End-to-end payment flow works
- [ ] Webhook processing is reliable
- [ ] Database updates are consistent
- [ ] Frontend polling updates UI correctly
- [ ] Error recovery mechanisms work
- [ ] Performance meets requirements

## Troubleshooting

### Common PhonePe Issues

#### Invalid Signature
```
Error: WEBHOOK_SIGNATURE_MISMATCH
Solution: Check salt key and signature calculation
```

#### Merchant ID Not Found
```
Error: MERCHANT_NOT_FOUND
Solution: Verify merchant ID and environment
```

#### Webhook Not Received
```
Error: Webhook timeout
Solution: Check webhook URL and server availability
```

### Common Resend Issues

#### API Key Invalid
```
Error: Invalid API key
Solution: Verify API key and permissions
```

#### Domain Not Verified
```
Error: Domain not verified
Solution: Complete domain verification in Resend dashboard
```

#### Email Not Delivered
```
Error: Delivery failed
Solution: Check spam settings and sender reputation
```

## Monitoring and Maintenance

### PhonePe Monitoring
- Monitor payment success rates
- Track webhook delivery times
- Watch for API rate limits
- Monitor subscription activations
- Set up alerts for failures

### Resend Monitoring
- Track email delivery rates
- Monitor bounce and complaint rates
- Watch API usage limits
- Track email engagement
- Set up alerts for delivery failures

### Regular Maintenance
- Weekly: Review payment and email metrics
- Monthly: Rotate API keys if needed
- Quarterly: Update contact information
- Annually: Review security practices

## Support Contacts

### PhonePe Support
- Developer Portal: https://developer.phonepe.com/
- Support Email: support@phonepe.com
- Documentation: https://developer.phonepe.com/docs

### Resend Support
- Dashboard: https://resend.com/dashboard
- Support Email: support@resend.com
- Documentation: https://resend.com/docs

## Additional Resources

### PhonePe Resources
- [PhonePe Integration Guide](https://developer.phonepe.com/docs/guides/integration)
- [Webhook Documentation](https://developer.phonepe.com/docs/guides/webhooks)
- [API Reference](https://developer.phonepe.com/docs/apis)

### Resend Resources
- [Getting Started Guide](https://resend.com/docs/get-started)
- [Email Templates](https://resend.com/docs/send-email-with-templates)
- [API Reference](https://resend.com/docs/api-reference)

---

**Last Updated**: January 29, 2026
**Version**: 1.0
**Maintainer**: Raptorflow Development Team
