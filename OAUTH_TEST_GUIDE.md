# OAuth Flow Test Guide

## ✅ Current Status
- Mock Auth: DISABLED
- Plans API: WORKING (returns correct pricing)
- Database: POPULATED with 3 plans
- Environment: Development

## 🔧 Manual Test Steps

### Step 1: Verify App is Running
```bash
# Make sure your dev server is running
npm run dev
# Should be on http://localhost:3000
```

### Step 2: Test Plans API
```bash
# Test plans endpoint
curl http://localhost:3000/api/plans
# Should return 3 plans with correct pricing
```

### Step 3: Test OAuth Flow
1. **Navigate to**: http://localhost:3000/login
2. **Check Auth Debug** (top-right corner):
   - Mock Auth: DISABLED (green)
   - Session: NONE (red)
   - User: NONE (red)

3. **Click "Continue with Google"**
4. **Authenticate with Google** (use your Google account)
5. **After redirect**, check Auth Debug:
   - Mock Auth: DISABLED (green)
   - Session: ACTIVE (green)
   - User: your-email@gmail.com (green)

6. **Navigate to**: http://localhost:3000/onboarding/plans
7. **Verify pricing cards show**:
   - Ascent: ₹5,000/month
   - Glide: ₹7,000/month
   - Soar: ₹10,000/month

8. **Click on any plan** (e.g., Ascent)
9. **Should redirect to payment page** without errors

### Step 4: Test Plan Selection API
```bash
# This should fail without auth (401)
curl -X POST http://localhost:3000/api/onboarding/select-plan \
  -H "Content-Type: application/json" \
  -d '{"planId":"ascent","billingCycle":"monthly"}'
```

## 🐛 Troubleshooting

### If you see "Plan not found":
- Check if plans table exists in Supabase
- Run the SQL migration: `20260126_populate_plans.sql`

### If you see "₹NaN":
- Check if plans API returns `price_monthly_paise` field
- Refresh the page after API changes

### If OAuth doesn't work:
- Check Supabase OAuth settings in dashboard
- Verify redirect URL: `http://localhost:3000/auth/callback`
- Check Google OAuth client configuration

### If auth fails:
- Check environment variables in `.env.local`
- Verify `NEXT_PUBLIC_MOCK_GOOGLE_LOGIN=false`
- Restart dev server after env changes

## 📊 Expected Results

✅ **Working Flow:**
1. Login with Google OAuth → Real session created
2. Navigate to plans → See correct pricing (₹5,000, ₹7,000, ₹10,000)
3. Select plan → Redirect to payment
4. Complete payment → Access dashboard

❌ **Broken Flow:**
1. Mock auth enabled → Fake session, plan selection fails
2. Wrong field names → ₹NaN pricing
3. Database empty → "Plan not found" error
4. OAuth misconfigured → Authentication fails

## 🔍 Debug Information

Use the Auth Debug widget (top-right) to see:
- Mock Auth status
- Session status  
- User email
- Any errors

Check browser console for:
- OAuth errors
- API errors
- Network issues
