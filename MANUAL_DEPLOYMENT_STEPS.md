# MANUAL DEPLOYMENT STEPS FOR SUPABASE

## 🚀 IMMEDIATE ACTION REQUIRED

The automated push failed because Supabase doesn't allow direct SQL execution via REST API without the `exec_sql` function. However, I can see that **some tables already exist**!

## 📊 CURRENT STATUS
- ✅ `profiles` table - ACCESSIBLE
- ✅ `workspaces` table - ACCESSIBLE
- ✅ `subscriptions` table - ACCESSIBLE
- ❌ `payments` table - MISSING
- ❌ `email_logs` table - MISSING

## 🔧 STEP-BY-STEP DEPLOYMENT

### Step 1: Open Supabase Dashboard
1. Go to: https://app.supabase.com/project/vpwwzsanuyhpkvgorcnc
2. Navigate to **SQL Editor** in the left sidebar

### Step 2: Execute Missing Tables SQL

Copy and paste this SQL to create the missing tables:

```sql
-- Create missing payments table
CREATE TABLE IF NOT EXISTS public.payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    transaction_id TEXT UNIQUE NOT NULL,
    phonepe_transaction_id TEXT,
    amount INTEGER NOT NULL,
    currency TEXT DEFAULT 'INR',
    status TEXT NOT NULL CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
    plan_id TEXT CHECK (plan_id IN ('ascent', 'glide', 'soar')),
    invoice_url TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    verified_at TIMESTAMPTZ
);

-- Create missing email_logs table
CREATE TABLE IF NOT EXISTS public.email_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    email_type TEXT NOT NULL,
    recipient_email TEXT NOT NULL,
    resend_id TEXT,
    status TEXT DEFAULT 'sent',
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Step 3: Add RLS Policies

```sql
-- Enable RLS
ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.email_logs ENABLE ROW LEVEL SECURITY;

-- Payments policy
CREATE POLICY "payments_self_view" ON public.payments FOR SELECT USING (auth.uid() = user_id);

-- Email logs policy
CREATE POLICY "email_logs_self_view" ON public.email_logs FOR SELECT USING (auth.uid() = user_id);
```

### Step 4: Add Indexes

```sql
-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON public.payments(user_id);
CREATE INDEX IF NOT EXISTS idx_email_logs_user_id ON public.email_logs(user_id);
```

### Step 5: Verify All Tables

Run this verification query:

```sql
-- Check all tables exist
SELECT table_name, table_type
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('profiles', 'workspaces', 'subscriptions', 'payments', 'email_logs')
ORDER BY table_name;
```

### Step 6: Test the Fixed Schema

Test the critical workspace query that was causing issues:

```sql
-- This should work now (no user_id column)
SELECT id, name, owner_id
FROM public.workspaces
WHERE owner_id = '00000000-0000-0000-0000-000000000000'
LIMIT 1;
```

## 🎯 EXPECTED RESULTS

After execution, you should see:
- All 5 tables listed in the verification query
- No errors in the workspace query test
- RLS policies enabled on all tables

## 🚀 NEXT STEPS AFTER DEPLOYMENT

1. **Test Authentication Flow**:
   ```bash
   npm run dev
   ```
   Navigate to `http://localhost:3000/login`

2. **Run Verification Script**:
   ```bash
   node scripts/pull_and_verify_schema.js
   ```

3. **Test User Registration**:
   - Try creating a new account
   - Check if profile is created automatically
   - Verify workspace creation

## 🆘 TROUBLESHOOTING

### If you get "column user_id does not exist" error:
- The workspace query is still using old column name
- Check that middleware.ts was fixed (should be using owner_id)

### If tables don't create:
- Ensure you have admin permissions
- Check SQL syntax carefully
- Execute each section separately

### If RLS policies fail:
- Run the RLS enable statements separately
- Check policy syntax

## 📞 SUPPORT

If you encounter issues:
1. Copy the error message
2. Check the browser console
3. Verify the SQL was executed successfully
4. Test with a fresh browser session

## ✅ SUCCESS CRITERIA

Deployment is successful when:
- [ ] All 5 tables exist
- [ ] No errors in workspace query
- [ ] Authentication works without redirect loops
- [ ] User can register and login
- [ ] Profile is created automatically
- [ ] Workspace is created for new users

**Ready to proceed! Execute the SQL in Supabase Dashboard now.**
