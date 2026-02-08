# 🚀 RAPTORFLOW EXTERNAL SERVICES SETUP GUIDE

## 📋 **QUICK SETUP CHECKLIST**

### ✅ **ALREADY CONFIGURED:**
- [x] **Supabase Database**: Connected and working
- [x] **PhonePe Test Mode**: Ready for testing
- [x] **Next.js Application**: Running on localhost:3001

### 🔧 **NEEDS YOUR CONFIGURATION:**
- [ ] **Resend API Key** (Critical for emails)
- [ ] **Google Cloud Platform** (For storage & APIs)
- [ ] **Upstash Redis** (For sessions)
- [ ] **Sentry** (For error tracking)

---

## 🎯 **STEP 1: RESEND EMAIL SETUP (CRITICAL)**

### Why needed: Email verification, password reset, transactional emails

#### 1.1 Create Resend Account
1. Go to: https://resend.com/signup
2. Sign up for free account
3. Verify your email

#### 1.2 Get API Key
1. Go to: https://resend.com/api-keys
2. Click "Create API Key"
3. Copy the API key (starts with `re_`)

#### 1.3 Configure Domain
1. Go to: https://resend.com/domains
2. Add your domain: `raptorflow.com`
3. Verify DNS records (they'll provide them)

#### 1.4 Update Environment
```bash
# In frontend/.env.local
RESEND_API_KEY=re_your_real_api_key_here
RESEND_FROM_EMAIL=noreply@raptorflow.com
```

#### 1.5 Test It
```bash
# Restart your app
npm run dev
# Go to: http://localhost:3001/setup-database.html
# Click "Test Email" button
```

---

## ☁️ **STEP 2: GOOGLE CLOUD PLATFORM SETUP**

### Why needed: File storage, APIs, authentication

#### 2.1 Create GCP Project
1. Go to: https://console.cloud.google.com/
2. Click "Select a project" → "NEW PROJECT"
3. Name: `raptorflow-production`
4. Click "CREATE"

#### 2.2 Enable APIs
Enable these APIs in your project:
```
# Required APIs:
- Cloud Storage API
- Cloud Firestore API
- Identity and Access Management (IAM) API
- Cloud Resource Manager API
- OAuth2 API
```

#### 2.3 Create Service Account
1. Go to: IAM & Admin → Service Accounts
2. Click "CREATE SERVICE ACCOUNT"
3. Name: `raptorflow-service`
4. Role: `Project Owner` (for development)
5. Click "CREATE AND CONTINUE"
6. Click "DONE"

#### 2.4 Get Service Account Key
1. Find your service account
2. Click on it → "KEYS" tab
3. "ADD KEY" → "Create new key"
4. Choose "JSON"
5. Download the JSON file

#### 2.5 Update Environment
```bash
# In frontend/.env.local
NEXT_PUBLIC_GCP_PROJECT_ID=raptorflow-production
GOOGLE_APPLICATION_CREDENTIALS_JSON={"type":"service_account","project_id":"raptorflow-production",...}
```

---

## 🗄️ **STEP 3: GOOGLE CLOUD STORAGE SETUP**

### Why needed: File uploads, user assets, campaign assets

#### 3.1 Create Storage Bucket
1. Go to: Cloud Storage → Browser
2. Click "CREATE BUCKET"
3. Name: `raptorflow-assets`
4. Location: Choose your region
5. Storage class: Standard
6. Control access: "Uniform"
7. Click "CREATE"

#### 3.2 Set Permissions
```bash
# Grant public access for static assets
gsutil iam ch allUsers:objectViewer gs://raptorflow-assets
```

---

## 🔴 **STEP 4: UPSTASH REDIS SETUP**

### Why needed: Session management, caching

#### 4.1 Create Upstash Account
1. Go to: https://upstash.com/
2. Sign up for free account
3. Verify email

#### 4.2 Create Redis Database
1. Go to: Dashboard → "Create Database"
2. Name: `raptorflow-sessions`
3. Region: Choose closest to your users
4. Click "Create"

#### 4.3 Get Connection Details
1. Click on your database
2. Copy "REST URL" and "REST Token"

#### 4.4 Update Environment
```bash
# In frontend/.env.local
UPSTASH_REDIS_REST_URL=https://your-redis-url.upstash.io
UPSTASH_REDIS_REST_TOKEN=your-redis-token
```

---

## 📊 **STEP 5: SENTRY ERROR TRACKING**

### Why needed: Error monitoring, performance tracking

#### 5.1 Create Sentry Account
1. Go to: https://sentry.io/
2. Sign up for free account
3. Choose "JavaScript" as platform

#### 5.2 Create Project
1. Name: `RaptorFlow Frontend`
2. Platform: Next.js
3. Click "Create Project"

#### 5.3 Get DSN
1. In your project settings → "Client Keys (DSN)"
2. Copy the DSN URL

#### 5.4 Update Environment
```bash
# In frontend/.env.local
NEXT_PUBLIC_SENTRY_DSN=https://your-dsn@sentry.io/project-id
SENTRY_AUTH_TOKEN=your-auth-token
```

---

## 🗄️ **STEP 6: COMPLETE DATABASE SETUP**

### Already partially done, let's complete it:

#### 6.1 Execute Complete Schema
1. Go to: http://localhost:3001/setup-database.html
2. Click "🔗 Open Supabase"
3. Copy ALL the SQL and run it in Supabase SQL Editor

#### 6.2 Create Additional Tables
```sql
-- Add these tables to your SQL:

-- Workspaces table
CREATE TABLE IF NOT EXISTS public.workspaces (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,
    owner_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    max_icp_profiles INTEGER DEFAULT 3,
    max_campaigns INTEGER DEFAULT 5,
    max_team_members INTEGER DEFAULT 1,
    is_trial BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Subscriptions table
CREATE TABLE IF NOT EXISTS public.subscriptions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    workspace_id UUID REFERENCES public.workspaces(id) ON DELETE CASCADE NOT NULL,
    plan TEXT DEFAULT 'trial',
    status TEXT DEFAULT 'trial',
    amount INTEGER DEFAULT 0,
    currency TEXT DEFAULT 'INR',
    is_trial BOOLEAN DEFAULT true,
    current_period_start TIMESTAMPTZ DEFAULT NOW(),
    current_period_end TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Payments table
CREATE TABLE IF NOT EXISTS public.payments (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    subscription_id UUID REFERENCES public.subscriptions(id) ON DELETE SET NULL,
    transaction_id TEXT UNIQUE NOT NULL,
    phonepe_transaction_id TEXT,
    plan_id TEXT NOT NULL,
    amount INTEGER NOT NULL,
    currency TEXT DEFAULT 'INR',
    status TEXT DEFAULT 'pending',
    payment_method TEXT DEFAULT 'phonepe',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 🧪 **STEP 7: TEST EVERYTHING**

#### 7.1 Test Database
```bash
# Go to: http://localhost:3001/setup-database.html
# Click "Test Database"
```

#### 7.2 Test Email (after Resend setup)
```bash
# Go to: http://localhost:3001/test-email-direct.html
# Send test email
```

#### 7.3 Test Account Creation
```bash
# Go to: http://localhost:3001/signup
# Create account with real email
# Check email for verification link
```

#### 7.4 Test PhonePe (test mode works)
```bash
# Go to: http://localhost:3001/payment?plan=soar
# Should show payment page (test mode)
```

---

## 🚀 **STEP 8: DEPLOYMENT PREPARATION**

#### 8.1 Install Dependencies
```bash
npm install @sentry/nextjs upstash redis
```

#### 8.2 Update package.json
```json
{
  "dependencies": {
    "@sentry/nextjs": "^7.0.0",
    "upstash-redis": "^1.0.0",
    "resend": "^3.0.0"
  }
}
```

#### 8.3 Create Production Build
```bash
npm run build
npm run start
```

---

## 📞 **STEP 9: GET HELP**

### If you get stuck:
1. **Resend Issues**: Check DNS records, domain verification
2. **GCP Issues**: Make sure APIs are enabled, service account has permissions
3. **Redis Issues**: Check REST URL and token are correct
4. **Database Issues**: Run the complete SQL schema

### Support Resources:
- Resend Docs: https://resend.com/docs
- GCP Docs: https://cloud.google.com/docs
- Upstash Docs: https://upstash.com/docs
- Sentry Docs: https://docs.sentry.io

---

## ✅ **FINAL VERIFICATION CHECKLIST**

After setup, verify these work:
- [ ] User signup sends verification email
- [ ] Password reset sends reset email  
- [ ] Login works with verified email
- [ ] PhonePe payment page loads
- [ ] Admin dashboard accessible (if admin user)
- [ ] Error tracking captures issues
- [ ] File uploads work (if implemented)

**Once all external services are configured, you'll have a production-ready application!** 🎉
