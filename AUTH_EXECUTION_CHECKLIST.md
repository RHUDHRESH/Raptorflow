# 🚀 RAPTORFLOW AUTH EXECUTION CHECKLIST

**Created:** January 16, 2026  
**Status:** Ready for Implementation

This checklist provides step-by-step instructions to complete the authentication overhaul.

---

## 🔴 PHASE 1: IMMEDIATE CRITICAL FIXES (Do First!)

### Step 1.1: Apply Database Migration
```bash
# Navigate to project root
cd c:\Users\hp\OneDrive\Desktop\Raptorflow

# Apply the auth overhaul migration to Supabase
# Option A: Using Supabase CLI
supabase db push

# Option B: Manual - Copy contents of this file into Supabase SQL Editor:
# supabase/migrations/20260116_auth_overhaul_complete.sql
```

**Verification:**
```sql
-- Run in Supabase SQL Editor to verify pricing:
SELECT name, price_monthly/100 as price_inr FROM subscription_plans;

-- Expected output:
-- Ascent | 5000
-- Glide  | 7000
-- Soar   | 10000
```

### Step 1.2: Remove Auth Bypass Code
**CRITICAL:** The files `src/lib/auth.ts` and `frontend/src/lib/auth.ts` contain bypass code that must be removed.

**Option A:** Delete the bypass files and use the new unified auth library:
```typescript
// In your components, replace:
import { isAuthenticated } from '@/lib/auth'

// With:
import { isAuthenticated } from '@/lib/supabase-auth'
```

**Option B:** Replace the bypass code in `src/lib/auth.ts` with a redirect to the new library:
```typescript
// src/lib/auth.ts - Replace entire contents with:
export * from './supabase-auth'
```

### Step 1.3: Verify RLS is Enabled
```sql
-- Run in Supabase SQL Editor:
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'workspaces', 'icp_profiles', 'campaigns', 'moves');

-- All should show rowsecurity = true
```

---

## 🟡 PHASE 2: CONFIGURE SUPABASE SETTINGS

### Step 2.1: Configure Email (Supabase Dashboard)
1. Go to **Supabase Dashboard → Authentication → Email Templates**
2. Update each template with RaptorFlow branding:

**Confirmation Email:**
```html
<h2>Welcome to RaptorFlow! 🦅</h2>
<p>Click below to confirm your email address:</p>
<p><a href="{{ .ConfirmationURL }}">Confirm Email</a></p>
<p>This link expires in 24 hours.</p>
```

**Password Reset Email:**
```html
<h2>Reset Your RaptorFlow Password</h2>
<p>Click below to reset your password:</p>
<p><a href="{{ .ConfirmationURL }}">Reset Password</a></p>
<p>This link expires in 1 hour.</p>
```

**Magic Link Email:**
```html
<h2>Your RaptorFlow Login Link</h2>
<p>Click below to sign in:</p>
<p><a href="{{ .ConfirmationURL }}">Sign In</a></p>
<p>This link expires in 1 hour.</p>
```

### Step 2.2: Configure SMTP (Optional but Recommended)
1. Go to **Supabase Dashboard → Project Settings → Auth**
2. Scroll to **SMTP Settings**
3. Enable custom SMTP and fill in:
   - **Host:** `smtp.resend.com` (or your SMTP provider)
   - **Port:** `465`
   - **User:** `resend` (or your username)
   - **Password:** Your Resend API key
   - **Sender Email:** `noreply@yourdomain.com`
   - **Sender Name:** `RaptorFlow`

### Step 2.3: Configure Google OAuth (Optional)
1. Go to **Google Cloud Console → APIs & Services → Credentials**
2. Create OAuth 2.0 Client ID
3. Add authorized redirect URI: `https://your-supabase-project.supabase.co/auth/v1/callback`
4. Go to **Supabase Dashboard → Authentication → Providers → Google**
5. Enable and add Client ID + Secret

---

## 🟢 PHASE 3: UPDATE FRONTEND COMPONENTS

### Step 3.1: Update Login Page to Use New Auth
The login page at `src/app/login/page.tsx` already uses `signInWithEmail` from `auth-client.ts` which is correct. Verify it works:

```bash
# Start the dev server
npm run dev

# Test login flow:
# 1. Go to http://localhost:3000/login
# 2. Try to login with a real user
# 3. Should redirect based on subscription/onboarding status
```

### Step 3.2: Add Magic Link Option to Login
Edit `src/app/login/page.tsx` to add magic link button:

```tsx
// Add import
import { signInWithMagicLink } from '@/lib/supabase-auth'

// Add state
const [showMagicLink, setShowMagicLink] = useState(false)

// Add button below Google OAuth
<BlueprintButton
  variant="secondary"
  className="w-full mt-4"
  onClick={() => setShowMagicLink(true)}
  type="button"
>
  <Mail size={16} className="mr-2" />
  Sign in with Magic Link
</BlueprintButton>
```

### Step 3.3: Test Password Reset Flow
```bash
# Test the forgot password flow:
# 1. Go to http://localhost:3000/forgot-password
# 2. Enter email address
# 3. Check email for reset link
# 4. Click link and set new password
```

---

## 🔵 PHASE 4: RUN SECURITY TESTS

### Step 4.1: Run Red-Team Tests
```bash
# Install test dependencies
pip install pytest httpx python-dotenv

# Set test environment variables
export TEST_USER_EMAIL="your-test-user@example.com"
export TEST_USER_PASSWORD="YourTestPassword123!"

# Run tests
cd c:\Users\hp\OneDrive\Desktop\Raptorflow
pytest tests/auth/test_auth_redteam.py -v
```

### Step 4.2: Manual Security Verification

**Test 1: Unauthenticated Access**
- [ ] Open incognito browser
- [ ] Go to `http://localhost:3000/dashboard`
- [ ] Should redirect to `/login`

**Test 2: Data Isolation**
- [ ] Create two test accounts (User A and User B)
- [ ] Login as User A, create a workspace
- [ ] Login as User B
- [ ] Should NOT see User A's workspace

**Test 3: Rate Limiting**
- [ ] Try to login with wrong password 10+ times
- [ ] Should eventually get blocked (429 error)

---

## 🟣 PHASE 5: PHONOPE PAYMENT INTEGRATION

### Step 5.1: Verify PhonePe Configuration
Check `.env` has correct PhonePe credentials:
```env
PHONEPE_CLIENT_ID=your_client_id
PHONEPE_CLIENT_SECRET=your_client_secret
PHONEPE_MERCHANT_ID=MERCHANTXXXXX
PHONEPE_ENV=UAT  # Change to PRODUCTION when ready
```

### Step 5.2: Test Payment Flow
```bash
# 1. Start the app
npm run dev

# 2. Go to pricing page
# http://localhost:3000/pricing

# 3. Select a plan and complete payment
# In UAT mode, use test cards

# 4. Verify webhook updates subscription
# Check Supabase: user_subscriptions table should have new row
```

### Step 5.3: Verify Subscription Creates Onboarding
After successful payment:
- [ ] `user_subscriptions` row created with `status: 'active'`
- [ ] `user_onboarding` row created
- [ ] User redirected to `/onboarding`

---

## 📋 FINAL VERIFICATION CHECKLIST

### Authentication
- [ ] Email/Password signup works
- [ ] Email/Password login works
- [ ] Google OAuth works (if configured)
- [ ] Magic Links work (if configured)
- [ ] Password reset works
- [ ] Email verification sent on signup
- [ ] Logout works and clears session

### Authorization
- [ ] Protected routes redirect to login
- [ ] RLS isolates user data
- [ ] Users cannot access other users' data
- [ ] Admin routes protected (if applicable)

### Subscription
- [ ] Pricing shows ₹5000/₹7000/₹10000
- [ ] PhonePe payment initiates correctly
- [ ] Webhook processes payment
- [ ] Subscription status updates in database
- [ ] Users without subscription go to /pricing

### Onboarding
- [ ] Users with subscription but no onboarding go to /onboarding
- [ ] Completed onboarding updates `onboarding_status` to 'active'
- [ ] Dashboard accessible after onboarding

### Security
- [ ] No bypass/demo users in production
- [ ] Rate limiting active
- [ ] HTTPS enforced in production
- [ ] Tokens expire correctly
- [ ] Sessions invalidate on logout

---

## 🆘 TROUBLESHOOTING

### "Supabase client not available"
- Check `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` are set
- Restart dev server after changing `.env`

### "RLS policy violation"
- Run the migration again: `supabase db push`
- Check RLS policies in Supabase Dashboard

### "Email not sending"
- Configure SMTP in Supabase Dashboard
- Or use Supabase's built-in email (limited rate)

### "Payment webhook not working"
- Check webhook URL is correct in PhonePe dashboard
- Verify webhook credentials in `.env`
- Check server logs for errors

---

## 📞 NEED HELP?

If you get stuck:
1. Check `AUTHENTICATION_OVERHAUL_MASTERPLAN.md` for detailed documentation
2. Run red-team tests to identify specific issues
3. Check Supabase logs in Dashboard → Logs
4. Check browser console for frontend errors

**Files Created/Modified:**
- `AUTHENTICATION_OVERHAUL_MASTERPLAN.md` - Complete documentation
- `supabase/migrations/20260116_auth_overhaul_complete.sql` - Database migration
- `src/lib/supabase-auth.ts` - New unified auth library
- `src/app/auth/callback/route.ts` - Updated auth callback
- `tests/auth/test_auth_redteam.py` - Security test suite
- `AUTH_EXECUTION_CHECKLIST.md` - This file
