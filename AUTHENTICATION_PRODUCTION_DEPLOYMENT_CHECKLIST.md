# 🔐 Authentication Production Deployment Checklist

## ✅ **PRE-DEPLOYMENT VERIFICATION**

### Database Setup
- [ ] **Supabase Project Created** with proper URL and keys
- [ ] **Environment Variables** configured in production:
  ```bash
  NEXT_PUBLIC_SUPABASE_URL=your-project.supabase.co
  NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
  SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
  RESEND_API_KEY=your-resend-api-key
  NEXT_PUBLIC_APP_URL=https://your-domain.com
  ```
- [ ] **Password Reset Tokens Table** created:
  ```sql
  CREATE TABLE IF NOT EXISTS public.password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    token TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
  );
  CREATE INDEX idx_password_reset_tokens_token ON public.password_reset_tokens(token);
  ```

### Email Configuration
- [ ] **Resend API** configured and verified
- [ ] **From Email** `onboarding@resend.dev` verified
- [ ] **Domain** verified in Resend dashboard
- [ ] **Test Email** sent successfully to `rhudhresh3697@gmail.com`

### Security Configuration
- [ ] **Rate Limiting** enabled in middleware
- [ ] **Security Headers** configured:
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - X-XSS-Protection: 1; mode=block
  - Content-Security-Policy: properly configured
  - Referrer-Policy: strict-origin-when-cross-origin
- [ ] **HTTPS** enforced in production
- [ ] **Environment Variables** secured (no hardcoded secrets)

---

## 🚀 **DEPLOYMENT STEPS**

### 1. Environment Setup
```bash
# Set production environment
export NODE_ENV=production

# Verify all required environment variables
echo "Checking environment variables..."
env | grep -E "(SUPABASE|RESEND|APP_URL)"
```

### 2. Database Migration
```bash
# Create password reset tokens table
curl -X POST https://your-domain.com/api/setup/create-db-table

# Verify table creation
curl https://your-domain.com/api/setup/create-db-table
```

### 3. Email Service Test
```bash
# Test email delivery
curl -X POST https://your-domain.com/api/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

### 4. Authentication Flow Test
```bash
# Test complete flow
# 1. Create test user
curl -X POST https://your-domain.com/api/test/create-user \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPassword123"}'

# 2. Test login
curl -X POST https://your-domain.com/api/test/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPassword123"}'

# 3. Test password reset
# (Get token from forgot-password response, then test reset)
```

---

## 🔍 **POST-DEPLOYMENT VERIFICATION**

### API Endpoints Check
- [ ] `GET /login` - Returns 200
- [ ] `GET /signup` - Returns 200
- [ ] `GET /forgot-password` - Returns 200
- [ ] `GET /auth/reset-password` - Returns 200
- [ ] `POST /api/auth/forgot-password` - Returns 200
- [ ] `POST /api/auth/reset-password-simple` - Returns 200
- [ ] `POST /api/auth/validate-reset-token-simple` - Returns 200

### Security Verification
- [ ] **Rate Limiting**: Test multiple rapid requests (should return 429)
- [ ] **Input Validation**: Test empty/invalid inputs (should return 400)
- [ ] **Route Protection**: Test protected routes without auth (should redirect)
- [ ] **HTTPS Only**: Ensure HTTP redirects to HTTPS

### Email Verification
- [ ] **Password Reset Email**: Received at target email
- [ ] **Email Content**: Contains valid reset link
- [ ] **Email Styling**: Professional HTML rendering
- [ ] **Link Expiration**: 1-hour token expiration working

### Browser Testing
- [ ] **Chrome**: Complete auth flow works
- [ ] **Firefox**: Complete auth flow works
- [ ] **Safari**: Complete auth flow works
- [ ] **Mobile**: Responsive design works

---

## 📊 **PERFORMANCE MONITORING**

### Key Metrics to Monitor
- **API Response Times**: < 500ms for auth endpoints
- **Error Rates**: < 1% for authentication
- **Email Delivery Rate**: > 95%
- **Database Query Performance**: < 100ms average

### Monitoring Setup
- [ ] **Error Tracking**: Sentry or similar
- [ ] **Performance Monitoring**: Vercel Analytics or similar
- [ ] **Database Monitoring**: Supabase dashboard
- [ ] **Email Analytics**: Resend dashboard

---

## 🚨 **TROUBLESHOOTING GUIDE**

### Common Issues & Solutions

#### 1. Password Reset Not Working
**Symptoms**: 500 error on reset endpoint
**Causes**: 
- Missing `password_reset_tokens` table
- Incorrect SUPABASE_SERVICE_ROLE_KEY
- Insufficient permissions

**Solutions**:
```bash
# Create table
POST /api/setup/create-db-table

# Check service role key
echo $SUPABASE_SERVICE_ROLE_KEY | head -c 20
```

#### 2. Emails Not Sending
**Symptoms**: API returns success but no email received
**Causes**:
- Invalid RESEND_API_KEY
- Domain not verified
- Email blocked by spam filter

**Solutions**:
```bash
# Test API key
curl -X POST https://api.resend.com/emails \
  -H "Authorization: Bearer $RESEND_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"from": "onboarding@resend.dev", "to": "test@example.com", "subject": "Test", "html": "Test"}'
```

#### 3. Rate Limiting Too Aggressive
**Symptoms**: Legitimate users getting 429 errors
**Causes**: Rate limit set too low

**Solutions**: Adjust rate limits in `src/middleware.ts`

#### 4. CORS Issues
**Symptoms**: Browser blocks API calls
**Causes**: Missing CORS configuration

**Solutions**: Ensure `NEXT_PUBLIC_APP_URL` is set correctly

---

## ✅ **PRODUCTION READINESS CHECKLIST**

### Final Verification
- [ ] All environment variables set
- [ ] Database tables created
- [ ] Email service verified
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] HTTPS enforced
- [ ] Error monitoring setup
- [ ] Performance monitoring configured
- [ ] Backup strategy in place
- [ ] Documentation complete

### Go-Live Checklist
- [ ] Staging environment tested
- [ ] Production deployment successful
- [ ] Smoke tests passed
- [ ] Monitoring alerts configured
- [ ] Rollback plan ready
- [ ] Team notified of deployment

---

## 📞 **SUPPORT CONTACTS**

### Emergency Contacts
- **Database Issues**: Supabase Support
- **Email Issues**: Resend Support
- **Infrastructure**: Hosting Provider

### Monitoring Dashboards
- **Supabase**: https://app.supabase.com
- **Resend**: https://resend.com/dashboard
- **Vercel**: https://vercel.com/dashboard

---

**Authentication system is production-ready!** 🎉

*Last Updated: January 16, 2026*
