# 🚀 Complete Setup Guide - Get Raptorflow Running

## Problem: User accounts not being created after login

This happens because the **database tables don't exist yet** in your Supabase project.

## ✅ Solution: Run the Database Setup Script

### Step 1: Open Supabase SQL Editor

1. Go to your Supabase Dashboard: https://app.supabase.com/project/vpwwzsanuyhpkvgorcnc
2. Click on **SQL Editor** in the left sidebar
3. Click **New Query**

### Step 2: Run the Setup Script

Copy and paste the entire contents of `database/QUICK_SETUP.sql` into the SQL Editor and click **Run**.

**OR** use this direct link:
- Open: `database/QUICK_SETUP.sql`
- Copy all contents (Ctrl+A, Ctrl+C)
- Paste into Supabase SQL Editor
- Click **Run** (or press Ctrl+Enter)

### Step 3: Verify Tables Were Created

Run this query to check:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('user_profiles', 'subscriptions', 'workspaces');
```

You should see 3 tables listed.

### Step 4: Test the Auto-Creation Trigger

The setup script includes a trigger that **automatically creates**:
- ✅ User profile
- ✅ Default workspace
- ✅ Free trial subscription (14 days)

**When a new user signs up!**

## What Happens After Setup

### 1. **New User Signs Up**
   - User registers with email/password or Google OAuth
   - Trigger fires automatically

### 2. **Auto-Created Records**
   ```
   user_profiles:
   - id: [user_id]
   - full_name: "John Doe" (from signup)
   - onboarding_completed: false
   
   subscriptions:
   - user_id: [user_id]
   - plan: "free"
   - status: "trialing"
   - trial_end: [14 days from now]
   
   workspaces:
   - owner_id: [user_id]
   - name: "My Workspace"
   ```

### 3. **User Redirected**
   - If `onboarding_completed = false` → Onboarding flow
   - If `onboarding_completed = true` → Dashboard

## Testing the Flow

### Option 1: Create New Account
1. Go to `/register`
2. Sign up with a new email
3. Should auto-create profile + subscription
4. Should redirect to onboarding or dashboard

### Option 2: Use Dev Bypass
1. Go to `/login`
2. Click **"[DEV] Bypass Authentication"** button
3. You'll be logged in as a dev user
4. Can test the dashboard without database

### Option 3: Check Existing Users
If you already have users in `auth.users` but no profiles:

```sql
-- Run this to create profiles for existing users
INSERT INTO public.user_profiles (id, full_name)
SELECT id, COALESCE(raw_user_meta_data->>'full_name', email)
FROM auth.users
WHERE id NOT IN (SELECT id FROM public.user_profiles);

-- Create subscriptions for existing users
INSERT INTO public.subscriptions (user_id, plan, status, trial_start, trial_end)
SELECT 
  id, 
  'free', 
  'trialing',
  CURRENT_TIMESTAMP,
  CURRENT_TIMESTAMP + INTERVAL '14 days'
FROM auth.users
WHERE id NOT IN (SELECT user_id FROM public.subscriptions);
```

## Troubleshooting

### "User profile not found" error
- Run the SQL setup script
- Check if tables exist: `SELECT * FROM public.user_profiles;`
- Manually create profile for your user (see Option 3 above)

### "Subscription not found" error
- Run the SQL setup script
- Check if subscriptions table exists
- Manually create subscription (see Option 3 above)

### Still redirecting to login after signup
- Check browser console for errors
- Verify `.env` file has correct Supabase credentials
- Restart dev server: `npm run dev`

### Onboarding not showing
- Check `user_profiles.onboarding_completed` is `false`
- Verify `ProtectedRoute` component is checking onboarding status
- Check `AuthContext` is fetching user status correctly

## Quick Commands

```bash
# Restart dev server (REQUIRED after .env changes)
npm run dev

# Check if .env exists
ls .env

# View Supabase URL
cat .env | grep VITE_SUPABASE_URL

# Open Supabase Dashboard
start https://app.supabase.com/project/vpwwzsanuyhpkvgorcnc
```

## Expected User Flow

```
1. User visits /register
   ↓
2. Signs up with email/Google
   ↓
3. Supabase trigger fires
   ↓
4. Creates: user_profile + subscription + workspace
   ↓
5. AuthContext fetches user data
   ↓
6. Checks onboarding_completed
   ↓
7a. If FALSE → Redirect to /onboarding
7b. If TRUE → Redirect to /dashboard
   ↓
8. User completes onboarding
   ↓
9. onboarding_completed = TRUE
   ↓
10. Redirect to /dashboard
```

## Payment & Subscription Info

The subscription system is set up with:
- **Free Trial**: 14 days (automatically set on signup)
- **Plans**: free, Ascent, Surge, Raptor
- **Status**: trialing, active, past_due, canceled

You can view/manage subscriptions in:
- Dashboard → Account Settings
- Or directly in Supabase: `SELECT * FROM subscriptions;`

---

**Need Help?** 
- Check Supabase logs: Dashboard → Logs
- Check browser console: F12 → Console
- Check network requests: F12 → Network
