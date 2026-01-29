# Environment Variables - Complete Guide

## Overview
This document outlines all environment variables required for the RaptorFlow payment system to function correctly in both development and production environments.

## 🚀 Required Environment Variables

### PhonePe Configuration
```bash
# PhonePe SDK Configuration
PHONEPE_MERCHANT_ID=your_merchant_id
PHONEPE_SALT_KEY=your_salt_key
PHONEPE_SALT_INDEX=1
PHONEPE_ENVIRONMENT=sandbox  # sandbox|production
PHONEPE_REDIRECT_URL=https://yourapp.com/onboarding/plans/callback
PHONEPE_WEBHOOK_SECRET=your_webhook_secret
```

**Description:**
- `PHONEPE_MERCHANT_ID`: Your PhonePe merchant ID
- `PHONEPE_SALT_KEY`: Your PhonePe salt key for signature validation
- `PHONEPE_SALT_INDEX`: Salt index (usually 1)
- `PHONEPE_ENVIRONMENT`: Environment (sandbox for testing, production for live)
- `PHONEPE_REDIRECT_URL`: URL where PhonePe redirects users after payment
- `PHONEPE_WEBHOOK_SECRET`: Secret for webhook security (optional but recommended)

### Email Configuration (Resend)
```bash
# Resend Email Service
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxxxxxx
FROM_EMAIL=noreply@raptorflow.com
FROM_NAME=RaptorFlow
```

**Description:**
- `RESEND_API_KEY`: Your Resend API key from dashboard.resend.com
- `FROM_EMAIL`: Email address for sending notifications
- `FROM_NAME`: Display name for email sender

### Application URLs
```bash
# Application URLs
NEXT_PUBLIC_APP_URL=https://yourapp.com
NEXT_PUBLIC_API_URL=https://api.yourapp.com
```

**Description:**
- `NEXT_PUBLIC_APP_URL`: Frontend application URL
- `NEXT_PUBLIC_API_URL`: Backend API URL

### Database Configuration
```bash
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SUPABASE_ANON_KEY=your_anon_key
```

**Description:**
- `NEXT_PUBLIC_SUPABASE_URL`: Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY`: Service role key for admin operations
- `SUPABASE_ANON_KEY`: Anonymous key for public operations

### Redis Configuration
```bash
# Redis Configuration (Upstash)
UPSTASH_REDIS_REST_URL=https://your-redis-url.upstash.io
UPSTASH_REDIS_REST_TOKEN=your_redis_token
```

**Description:**
- `UPSTASH_REDIS_REST_URL`: Upstash Redis URL
- `UPSTASH_REDIS_REST_TOKEN`: Upstash Redis token

### AI Configuration
```bash
# Google Vertex AI
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
VERTEXAI_PROJECT_ID=your-project-id
VERTEXAI_LOCATION=us-central1
```

**Description:**
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to Google Cloud service account JSON
- `VERTEXAI_PROJECT_ID`: Google Cloud project ID
- `VERTEXAI_LOCATION`: Google Cloud region

---

## 📋 Environment Files

### Development (.env.local)
```bash
# Development Environment Variables
PHONEPE_MERCHANT_ID=PGTEST123456
PHONEPE_SALT_KEY=test_salt_key_123456
PHONEPE_SALT_INDEX=1
PHONEPE_ENVIRONMENT=sandbox
PHONEPE_REDIRECT_URL=http://localhost:3000/onboarding/plans/callback
PHONEPE_WEBHOOK_SECRET=test_webhook_secret

RESEND_API_KEY=re_test_xxxxxxxxxxxxxxxxxxxxxxxxx
FROM_EMAIL=noreply@localhost.raptorflow.com
FROM_NAME=RaptorFlow Dev

NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000

NEXT_PUBLIC_SUPABASE_URL=http://localhost:54321
SUPABASE_SERVICE_ROLE_KEY=your_dev_service_role_key
SUPABASE_ANON_KEY=your_dev_anon_key

UPSTASH_REDIS_REST_URL=https://dev-redis.upstash.io/xxxxxxxx
UPSTASH_REDIS_REST_TOKEN=your_dev_redis_token

GOOGLE_APPLICATION_CREDENTIALS=./service-account-dev.json
VERTEXAI_PROJECT_ID=your-dev-project
VERTEXAI_LOCATION=us-central1

NODE_ENV=development
```

### Production (.env.production)
```bash
# Production Environment Variables
PHONEPE_MERCHANT_ID=PGPROD123456
PHONEPE_SALT_KEY=prod_salt_key_123456
PHONEPE_SALT_INDEX=1
PHONEPE_ENVIRONMENT=production
PHONEPE_REDIRECT_URL=https://raptorflow.com/onboarding/plans/callback
PHONEPE_WEBHOOK_SECRET=prod_webhook_secret_very_secure

RESEND_API_KEY=re_prod_xxxxxxxxxxxxxxxxxxxxxxxxx
FROM_EMAIL=noreply@raptorflow.com
FROM_NAME=RaptorFlow

NEXT_PUBLIC_APP_URL=https://raptorflow.com
NEXT_PUBLIC_API_URL=https://api.raptorflow.com

NEXT_PUBLIC_SUPABASE_URL=https://xxxxxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_prod_service_role_key
SUPABASE_ANON_KEY=your_prod_anon_key

UPSTASH_REDIS_REST_URL=https://prod-redis.upstash.io/xxxxxxxx
UPSTASH_REDIS_REST_TOKEN=your_prod_redis_token

GOOGLE_APPLICATION_CREDENTIALS=./service-account-prod.json
VERTEXAI_PROJECT_ID=your-prod-project
VERTEXAI_LOCATION=us-central1

NODE_ENV=production
```

---

## 🔧 Setup Instructions

### 1. PhonePe Setup
1. Create a PhonePe merchant account at [PhonePe Dashboard](https://dashboard.phonepe.com)
2. Get your Merchant ID and Salt Key
3. Set up webhook endpoint in PhonePe dashboard:
   - Webhook URL: `https://yourapp.com/api/webhooks/phonepe`
   - Environment: Sandbox for testing, Production for live

### 2. Resend Setup
1. Create account at [Resend Dashboard](https://resend.com)
2. Get your API key
3. Verify your domain in Resend settings

### 3. Supabase Setup
1. Create project at [Supabase Dashboard](https://supabase.com)
2. Get your project URL and keys
3. Run database migrations

### 4. Upstash Redis Setup
1. Create Redis database at [Upstash Console](https://console.upstash.com)
2. Get your REST URL and token
3. Configure connection settings

### 5. Google Cloud Setup
1. Create project at [Google Cloud Console](https://console.cloud.google.com)
2. Enable Vertex AI API
3. Create service account and download JSON key
4. Set up authentication

---

## 🚨 Security Notes

### Sensitive Variables
- Never commit actual API keys or secrets to version control
- Use environment-specific files (.env.local, .env.production)
- Rotate secrets regularly
- Use different keys for development and production

### Webhook Security
- Always validate PhonePe webhook signatures
- Use HTTPS for all webhook endpoints
- Implement rate limiting for webhook endpoints
- Log all webhook events for audit trails

### Database Security
- Use service role keys only for backend operations
- Implement Row Level Security (RLS) policies
- Regularly rotate database credentials
- Use connection pooling

---

## 🧪 Testing Configuration

### Test Environment Variables
```bash
# Test Environment (for automated testing)
PHONEPE_MERCHANT_ID=PGTEST123456
PHONEPE_SALT_KEY=test_salt_key_123456
PHONEPE_SALT_INDEX=1
PHONEPE_ENVIRONMENT=sandbox
PHONEPE_REDIRECT_URL=http://localhost:3000/onboarding/plans/callback

RESEND_API_KEY=re_test_xxxxxxxxxxxxxxxxxxxxxxxxx
FROM_EMAIL=test@raptorflow.com
FROM_NAME=RaptorFlow Test

NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000

# Mock services for testing
MOCK_PHONEPE_API=true
MOCK_EMAIL_SERVICE=true
MOCK_REDIS=true
```

---

## 📊 Environment Variable Validation

The application includes validation for required environment variables:

### Backend Validation
```python
# services/environment_manager.py
class EnvironmentManager:
    def validate_payment_config(self):
        required_vars = [
            'PHONEPE_MERCHANT_ID',
            'PHONEPE_SALT_KEY',
            'PHONEPE_SALT_INDEX',
            'PHONEPE_ENVIRONMENT'
        ]

        for var in required_vars:
            if not os.getenv(var):
                raise EnvironmentError(f"Missing required environment variable: {var}")
```

### Frontend Validation
```typescript
// lib/environment.ts
export const validateEnvironment = () => {
  const required = ['NEXT_PUBLIC_APP_URL', 'NEXT_PUBLIC_SUPABASE_URL'];

  for (const envVar of required) {
    if (!process.env[envVar]) {
      throw new Error(`Missing required environment variable: ${envVar}`);
    }
  }
};
```

---

## 🔍 Troubleshooting

### Common Issues

#### 1. Payment Initiation Fails
- Check PhonePe credentials are correct
- Verify webhook URL is accessible
- Ensure environment is set correctly (sandbox vs production)

#### 2. Email Not Sending
- Verify Resend API key is valid
- Check domain is verified in Resend
- Ensure FROM_EMAIL is verified

#### 3. Database Connection Issues
- Verify Supabase URL and keys
- Check network connectivity
- Ensure migrations are applied

#### 4. Redis Connection Issues
- Verify Upstash URL and token
- Check network connectivity
- Ensure Redis is running

---

## 📞 Support

For help with environment variable setup:
- Check the documentation for each service
- Review error logs for specific error messages
- Contact support if issues persist

---

## 📋 Checklist

Before deploying to production:

- [ ] All required environment variables are set
- [ ] PhonePe webhook endpoint is accessible
- [ ] Email domain is verified with Resend
- [ ] Database migrations are applied
- [ ] Redis connection is working
- [ ] All services are running
- [ ] Test payment flow works end-to-end
- [ ] Error monitoring is configured
- [ ] Backup systems are in place

---

**Last Updated:** January 28, 2026
**Version:** 1.0
