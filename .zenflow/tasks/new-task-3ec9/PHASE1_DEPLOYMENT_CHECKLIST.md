# Phase 1 Deployment Checklist - CRITICAL REMAINING TASKS

## 🚨 IMMEDIATE ACTION REQUIRED

The Phase 1 handoff is complete but NOTHING IS DEPLOYED YET. We need to apply all changes to the live systems.

---

## Database Deployments (SUPABASE)

### ✅ Migrations to Apply
```bash
# 1. Apply auth triggers migration
supabase db push supabase/migrations/001_auth_triggers.sql

# 2. Apply payment transactions migration (Phase 2 prep)
supabase db push supabase/migrations/002_payment_transactions.sql

# 3. Apply BCM storage migration (Phase 4 prep)
supabase db push supabase/migrations/003_bcm_storage.sql

# 4. Apply onboarding status migration (Phase 3 prep)
supabase db push supabase/migrations/004_add_onboarding_status.sql

# 5. Apply subscriptions migration (Phase 2 prep)
supabase db push supabase/migrations/005_subscriptions.sql
```

### 🔍 Verify Migration Status
```sql
-- Check if migrations are applied
SELECT * FROM supabase_migrations.schema_migrations
ORDER BY version DESC;

-- Verify tables exist
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('users', 'workspaces', 'workspace_members', 'subscriptions', 'payment_transactions');

-- Check RLS policies
SELECT schemaname, tablename, policyname
FROM pg_policies
WHERE schemaname = 'public';
```

---

## Backend Deployment (RENDER)

### 🔄 Code Changes to Deploy
- ✅ ProfileService enhanced with subscription logic
- ✅ Auth API endpoints with proper error handling
- ✅ Workspace helpers updated to owner_id schema
- ✅ Enhanced logging and security

### 🚀 Deploy Commands
```bash
# 1. Push backend changes to main
git add backend/services/profile_service.py
git add backend/api/v1/auth.py
git add backend/core/workspace.py
git commit -m "Phase 1: Enhanced profile verification and workspace consistency"
git push origin main

# 2. Trigger Render deployment (automatic on push)
# Monitor: https://dashboard.render.com/

# 3. Verify backend health
curl https://your-backend-url.onrender.com/health
```

---

## Frontend Deployment (VERCEL)

### 🔄 Code Changes to Deploy
- ✅ AuthProvider with profile verification and caching
- ✅ ProfileGate with redirect state tracking
- ✅ Middleware with direct backend calls
- ✅ Enhanced error handling and retry logic

### 🚀 Deploy Commands
```bash
# 1. Push frontend changes
git add src/components/auth/AuthProvider.tsx
git add src/components/auth/ProfileGate.tsx
git add src/middleware.ts
git commit -m "Phase 1: Frontend auth gating and profile verification"
git push origin main

# 2. Trigger Vercel deployment (automatic)
# Monitor: https://vercel.com/your-project

# 3. Verify frontend deployment
curl https://your-app.vercel.app/api/health
```

---

## Environment Variables (CRITICAL)

### 🔧 Supabase Configuration
```bash
# Verify these are set in Supabase dashboard
SUPABASE_URL=your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-key
SUPABASE_ANON_KEY=your-anon-key
```

### 🔧 Backend Environment (Render)
```bash
# Verify in Render dashboard
DATABASE_URL=postgresql://user:pass@host:port/dbname
SUPABASE_URL=your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-key
JWT_SECRET=your-jwt-secret
```

### 🔧 Frontend Environment (Vercel)
```bash
# Verify in Vercel dashboard
NEXT_PUBLIC_SUPABASE_URL=your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
BACKEND_URL=https://your-backend.onrender.com
```

---

## Integration Testing (POST-DEPLOY)

### 🧪 Critical Test Flows
```bash
# 1. Test auth endpoints
curl -X POST https://your-backend.onrender.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password"}'

# 2. Test profile verification
curl -X GET https://your-backend.onrender.com/api/v1/auth/verify-profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 3. Test frontend auth flow
# Visit: https://your-app.vercel.app/signin
# Test login → profile verification → dashboard flow
```

### 🔍 Health Checks
```bash
# Backend health
curl https://your-backend.onrender.com/health

# Frontend health
curl https://your-app.vercel.app/api/health

# Database connectivity
curl https://your-backend.onrender.com/api/v1/db/health
```

---

## Rollback Plan (IF THINGS BREAK)

### 🔄 Database Rollback
```bash
# Rollback migrations
supabase db rollback --version PREVIOUS_VERSION

# Or manually
supabase db push supabase/migrations/rollback_001_auth_triggers.sql
```

### 🔄 Backend Rollback
```bash
# Revert to previous commit
git checkout PREVIOUS_COMMIT_TAG
git push origin main --force
```

### 🔄 Frontend Rollback
```bash
# Revert to previous deployment
vercel rollback [deployment-url]
```

---

## Monitoring (POST-DEPLOY)

### 📊 Key Metrics to Watch
- Auth success rate
- Profile verification response time
- Database query performance
- Error rates (4xx/5xx)
- User login completion rate

### 🚨 Alerts to Set Up
- High auth failure rates
- Database connection errors
- Profile verification timeouts
- Middleware redirect loops

---

## Documentation Updates

### 📝 Update README
- Add new auth flow documentation
- Document environment variables
- Update deployment instructions

### 📝 Update API Docs
- Add ensure/verify profile endpoints
- Document error response formats
- Update authentication examples

---

## IMMEDIATE NEXT STEPS

### 🎯 TONIGHT (Critical Path)
1. **Apply Supabase migrations** - This is blocking everything
2. **Deploy backend to Render** - Test profile verification endpoints
3. **Deploy frontend to Vercel** - Test auth flow end-to-end
4. **Run integration tests** - Verify complete user journey

### 🎯 TOMORROW
1. **Monitor production** - Watch for errors and performance issues
2. **Fix any issues** - Address bugs discovered in production
3. **Update documentation** - Ensure docs match deployed state
4. **Begin Phase 2** - Start payment integration once Phase 1 is stable

---

## SUCCESS CRITERIA

### ✅ Phase 1 is "DONE" when:
- [ ] All Supabase migrations applied successfully
- [ ] Backend deployed and responding to auth endpoints
- [ ] Frontend deployed and auth flow works end-to-end
- [ ] Users can signup → verify profile → access dashboard
- [ ] No critical errors in production logs
- [ ] Performance benchmarks met (<2s auth response)

---

## CONTACTS IF THINGS GO WRONG

### 🆘 Emergency Contacts
- **Database Issues**: Check Supabase dashboard logs
- **Backend Issues**: Check Render deployment logs
- **Frontend Issues**: Check Vercel deployment logs
- **Auth Issues**: Check JWT configuration and Supabase auth settings

### 🛠️ Debug Commands
```bash
# Check Supabase logs
supabase logs list

# Check Render logs
# Visit Render dashboard → Your service → Logs

# Check Vercel logs
# Visit Vercel dashboard → Your project → Logs
```

---

## FINAL REMINDER

**NOTHING IS LIVE YET** - We've only prepared the code. The actual deployment and migration application is still needed.

**DO NOT START PHASE 2** until Phase 1 is fully deployed and tested in production.

---

**Status**: 🔄 DEPLOYMENT PENDING
**Priority**: 🚨 CRITICAL
**Next Action**: APPLY SUPABASE MIGRATIONS NOW
