# Authentication Setup Guide

## ✅ What I Fixed

1. **Profile Creation on OAuth Sign-In**
   - Added `ensureProfile()` function that checks if profile exists, creates it if not
   - Handles edge cases where database trigger might fail
   - Falls back gracefully if profile already exists

2. **OAuth Callback Handler**
   - Created `/auth/callback` route to properly handle Google OAuth redirects
   - Extracts tokens from URL hash and sets session
   - Automatically creates profile if missing

3. **Better Error Handling**
   - Profile creation now handles duplicate key errors
   - Multiple fallback attempts to fetch/create profile
   - Console logging for debugging

4. **Protected Route Updates**
   - Now waits for profile to be created before allowing access
   - Shows "Setting up your account..." message during profile creation

## 🔧 Setup Steps

### 1. Run Database Migration

Go to your Supabase Dashboard → SQL Editor and run the migration:

```sql
-- Copy and paste the entire contents of:
-- supabase/migrations/001_initial_schema.sql
```

This creates:
- `profiles` table
- `payments` table  
- `plan_prices` table
- Database triggers for auto-creating profiles
- Row Level Security policies

### 2. Enable Google OAuth

1. Go to Supabase Dashboard → Authentication → Providers
2. Enable **Google** provider
3. Add your Google OAuth credentials:
   - Client ID
   - Client Secret
4. Add redirect URL: `http://localhost:3000/auth/callback` (and your production URL)

### 3. Set Environment Variables

Create a `.env` file in the root:

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here
```

### 4. Test the Flow

1. Go to `/login`
2. Click "Continue with Google"
3. Sign in with Google
4. You should be redirected to `/auth/callback` then `/app`
5. Your profile should be automatically created in the database

## 🐛 Debugging

If account creation still fails:

1. **Check Browser Console** - Look for error messages
2. **Check Supabase Logs** - Dashboard → Logs → Postgres Logs
3. **Verify Database Trigger** - Run this query:
   ```sql
   SELECT * FROM auth.users;
   SELECT * FROM public.profiles;
   ```
4. **Check RLS Policies** - Make sure policies allow profile creation

## 📊 Verify Account Creation

After signing in, check your database:

```sql
-- See all users
SELECT id, email, created_at FROM auth.users;

-- See all profiles  
SELECT id, email, plan, plan_status, created_at FROM public.profiles;

-- Match them up
SELECT 
  u.id as user_id,
  u.email,
  p.id as profile_id,
  p.plan,
  p.plan_status
FROM auth.users u
LEFT JOIN public.profiles p ON u.id = p.id;
```

If profiles are missing, the `ensureProfile()` function will create them automatically on next sign-in.

