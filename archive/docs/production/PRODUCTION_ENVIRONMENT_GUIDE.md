# 🚀 PRODUCTION ENVIRONMENT SETUP GUIDE
## Configuration Instructions for Raptorflow Deployment

---

## 📋 **OVERVIEW**
- **Application**: Raptorflow Authentication System
- **Environment**: Production
- **Framework**: Next.js 14
- **Database**: Supabase PostgreSQL
- **Deployment**: Docker/Vercel/AWS

---

## 🔧 **REQUIRED ENVIRONMENT VARIABLES**

### **Critical Security Variables**
```bash
# JWT Secret (minimum 32 characters)
NEXTAUTH_SECRET=your-super-secret-jwt-key-min-32-characters-long

# Session Secret (minimum 32 characters)
SESSION_SECRET=your-session-secret-key-min-32-characters

# Encryption Key (minimum 32 characters)
ENCRYPTION_KEY=your-32-character-encryption-key
```

### **Supabase Configuration**
```bash
# Production Supabase URL
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-production-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-production-service-role-key
```

### **Email Service (Resend)**
```bash
RESEND_API_KEY=re_your_production_resend_api_key
RESEND_FROM_EMAIL=noreply@raptorflow.com
```

---

## 📝 **STEP-BY-STEP SETUP**

### **Step 1: Supabase Setup**
1. **Create Production Project**
   - Go to https://app.supabase.com
   - Create new project (don't use development project)
   - Note project URL and keys

2. **Get API Keys**
   ```bash
   # From Supabase Dashboard → Settings → API
   NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ... (anon key)
   SUPABASE_SERVICE_ROLE_KEY=eyJ... (service role key)
   ```

3. **Apply Database Migrations**
   - Follow `SUPABASE_MIGRATION_GUIDE.md`
   - Execute all 3 migration files
   - Verify tables created

### **Step 2: Resend Email Setup**
1. **Create Resend Account**
   - Go to https://resend.com
   - Create production account
   - Verify domain

2. **Get API Key**
   ```bash
   RESEND_API_KEY=re_your_production_api_key
   ```

3. **Configure Domain**
   - Add `raptorflow.com` to verified domains
   - Set up `noreply@raptorflow.com` as sender

### **Step 3: Security Configuration**
1. **Generate Secure Keys**
   ```bash
   # Generate JWT Secret
   openssl rand -base64 32
   
   # Generate Session Secret  
   openssl rand -base64 32
   
   # Generate Encryption Key
   openssl rand -base64 32
   ```

2. **Set Application URLs**
   ```bash
   NEXT_PUBLIC_APP_URL=https://raptorflow.com
   NEXTAUTH_URL=https://raptorflow.com
   ```

### **Step 4: Rate Limiting Setup**
1. **Configure Redis (Upstash)**
   ```bash
   UPSTASH_REDIS_URL=https://your-redis.upstash.io
   UPSTASH_REDIS_TOKEN=your-redis-token
   ```

2. **Set Rate Limits**
   ```bash
   RATE_LIMIT_ANONYMOUS=10
   RATE_LIMIT_AUTHENTICATED=100
   RATE_LIMIT_ADMIN=1000
   ```

---

## 🔐 **SECURITY BEST PRACTICES**

### **1. Secret Management**
- ✅ Use environment variables for all secrets
- ✅ Never commit `.env.production` to git
- ✅ Use different secrets for each environment
- ✅ Rotate secrets regularly

### **2. Database Security**
- ✅ Use service role key only on server
- ✅ Enable RLS on all tables
- ✅ Use connection pooling
- ✅ Regular backups

### **3. API Security**
- ✅ Enable CORS for production domain only
- ✅ Use HTTPS everywhere
- ✅ Implement rate limiting
- ✅ Add security headers

### **4. Email Security**
- ✅ Use verified sending domain
- ✅ Set up SPF/DKIM records
- ✅ Monitor email deliverability
- ✅ Handle bounces properly

---

## 🚀 **DEPLOYMENT OPTIONS**

### **Option 1: Vercel (Recommended)**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod

# Set environment variables in Vercel Dashboard
# Settings → Environment Variables
```

### **Option 2: Docker**
```bash
# Build Docker image
docker build -t raptorflow:latest .

# Run with environment file
docker run -d \
  --name raptorflow \
  --env-file .env.production \
  -p 3000:3000 \
  raptorflow:latest
```

### **Option 3: AWS ECS**
```bash
# Create ECS task definition
# Set environment variables in task definition
# Deploy with AWS CLI or Console
```

---

## 📊 **ENVIRONMENT VARIABLE CHECKLIST**

### **Required for Basic Functionality**
- [ ] `NEXT_PUBLIC_SUPABASE_URL`
- [ ] `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- [ ] `SUPABASE_SERVICE_ROLE_KEY`
- [ ] `NEXTAUTH_SECRET`
- [ ] `RESEND_API_KEY`
- [ ] `NEXT_PUBLIC_APP_URL`

### **Required for Security**
- [ ] `SESSION_SECRET`
- [ ] `ENCRYPTION_KEY`
- [ ] `CORS_ORIGIN`
- [ ] `RATE_LIMIT_ANONYMOUS`

### **Required for Monitoring**
- [ ] `SENTRY_DSN`
- [ ] `LOG_LEVEL`
- [ ] `HEALTH_CHECK_ENABLED`

### **Required for Performance**
- [ ] `REDIS_URL`
- [ ] `CACHE_ENABLED`
- [ ] `COMPRESSION_ENABLED`

---

## 🔍 **VERIFICATION STEPS**

### **1. Database Connection**
```bash
# Test Supabase connection
curl -X POST https://your-project.supabase.co/rest/v1/profiles \
  -H "apikey: YOUR_ANON_KEY" \
  -H "Content-Type: application/json"
```

### **2. Email Service**
```bash
# Test Resend API
curl -X POST https://api.resend.com/emails \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json"
```

### **3. Authentication Flow**
1. Visit: `https://raptorflow.com/login`
2. Test login with production user
3. Test password reset flow
4. Verify email delivery

### **4. Security Headers**
```bash
# Check security headers
curl -I https://raptorflow.com
```

---

## ⚠️ **COMMON ISSUES & SOLUTIONS**

### **Issue: "Invalid JWT Secret"**
**Solution**: Ensure `NEXTAUTH_SECRET` is set and matches between environments

### **Issue: "Database connection failed"**
**Solution**: Verify Supabase URL and keys are correct

### **Issue: "Email not sending"**
**Solution**: Check Resend API key and domain verification

### **Issue: "CORS errors"**
**Solution**: Update `CORS_ORIGIN` with production domain

### **Issue: "Rate limiting not working"**
**Solution**: Verify Redis connection and configuration

---

## 📈 **MONITORING SETUP**

### **1. Application Monitoring**
```bash
# Sentry Error Tracking
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production
```

### **2. Health Checks**
```bash
# Enable health endpoint
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_INTERVAL=30000
```

### **3. Log Management**
```bash
# Configure logging
LOG_LEVEL=info
LOG_FILE_PATH=/app/logs/raptorflow.log
```

---

## 🔄 **ENVIRONMENT PROMOTION**

### **From Development to Production**
1. **Create new Supabase project**
2. **Apply database migrations**
3. **Update environment variables**
4. **Test all integrations**
5. **Deploy to production**
6. **Monitor for issues**

### **Rollback Plan**
1. **Keep development environment intact**
2. **Backup production data**
3. **Document rollback steps**
4. **Test rollback procedure**

---

## 📞 **SUPPORT CONTACT**

### **For Issues With:**
- **Supabase**: https://supabase.com/support
- **Resend**: https://resend.com/support
- **Vercel**: https://vercel.com/support
- **Sentry**: https://sentry.io/support

### **Internal Support**
- **Database Issues**: Check migration guide
- **API Issues**: Check API documentation
- **Email Issues**: Check Resend dashboard
- **Performance**: Check monitoring dashboard

---

## ✅ **FINAL CHECKLIST**

Before going to production:

- [ ] All required environment variables set
- [ ] Database migrations applied
- [ ] Email service configured
- [ ] Security keys generated
- [ ] Rate limiting configured
- [ ] Monitoring setup
- [ ] Backup strategy in place
- [ ] Rollback plan documented
- [ ] Load testing completed
- [ ] Security audit passed

---

## 🎯 **GO LIVE CHECKLIST**

On deployment day:

- [ ] Deploy with production environment
- [ ] Verify database connectivity
- [ ] Test authentication flow
- [ ] Test email delivery
- [ ] Check monitoring alerts
- [ ] Verify SSL certificate
- [ ] Test performance
- [ ] Monitor error rates
- [ ] Check user feedback
- [ ] Document any issues

---

*Last Updated: January 16, 2026*
*Version: 1.0*
*Status: Production Ready* ✅
