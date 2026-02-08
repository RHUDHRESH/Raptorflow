# 🗄️ SUPABASE MIGRATION GUIDE
## Database Setup Instructions

---

## 📋 **MIGRATION OVERVIEW**
- **Database**: Supabase PostgreSQL
- **Project**: Raptorflow Authentication System
- **Migrations Required**: 3 files
- **Status**: Ready for Manual Execution

---

## 🎯 **REQUIRED MIGRATIONS**

### **1. Profiles Table Migration**
**File**: `supabase/migrations/001_profiles.sql`
**Purpose**: Create user profiles with auto-creation trigger
**Tables**: `profiles`
**Features**: RLS policies, triggers, indexes

### **2. Workspaces Migration** 
**File**: `supabase/migrations/002_workspaces_rls.sql`
**Purpose**: Create workspace management system
**Tables**: `workspaces`, `workspace_members`
**Features**: Multi-tenancy, RLS, role-based access

### **3. Password Reset Tokens Migration**
**File**: `supabase/migrations/004_password_reset_tokens.sql`
**Purpose**: Create secure password reset system
**Tables**: `password_reset_tokens`
**Features**: Token expiration, cleanup functions

---

## 🔧 **MANUAL EXECUTION STEPS**

### **Step 1: Access Supabase Dashboard**
1. Go to: https://app.supabase.com
2. Select your Raptorflow project
3. Navigate to: **SQL Editor**

### **Step 2: Execute Profiles Migration**
1. Open: `supabase/migrations/001_profiles.sql`
2. Copy entire SQL content
3. Paste in Supabase SQL Editor
4. Click **Run** (or press Ctrl+Enter)
5. **Expected**: "Success" message

### **Step 3: Execute Workspaces Migration**
1. Open: `supabase/migrations/002_workspaces_rls.sql`
2. Copy entire SQL content
3. Paste in Supabase SQL Editor
4. Click **Run**
5. **Expected**: "Success" message

### **Step 4: Execute Password Reset Migration**
1. Open: `supabase/migrations/004_password_reset_tokens.sql`
2. Copy entire SQL content
3. Paste in Supabase SQL Editor
4. Click **Run**
5. **Expected**: "Success" message

---

## ✅ **VERIFICATION CHECKLIST**

After executing all migrations, verify:

### **Tables Created**
```sql
-- Check tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('profiles', 'workspaces', 'workspace_members', 'password_reset_tokens');
```

### **RLS Enabled**
```sql
-- Check RLS is enabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('profiles', 'workspaces', 'workspace_members', 'password_reset_tokens');
```

### **Functions Created**
```sql
-- Check functions exist
SELECT proname 
FROM pg_proc 
WHERE proname LIKE '%handle_new_user%' 
   OR proname LIKE '%update_updated_at%'
   OR proname LIKE '%cleanup_expired_tokens%';
```

### **Triggers Created**
```sql
-- Check triggers exist
SELECT trigger_name, event_object_table 
FROM information_schema.triggers 
WHERE trigger_schema = 'public';
```

---

## 🔍 **EXPECTED RESULTS**

### **After Successful Migration**
- ✅ 4 tables created with proper structure
- ✅ RLS enabled on all tables
- ✅ Indexes created for performance
- ✅ Triggers for auto-updating timestamps
- ✅ Functions for data management
- ✅ Policies for secure data access

### **Table Structures**
```sql
-- profiles table structure
CREATE TABLE public.profiles (
  id UUID PRIMARY KEY,
  email TEXT NOT NULL,
  full_name TEXT,
  avatar_url TEXT,
  role TEXT NOT NULL DEFAULT 'user',
  workspace_id UUID,
  subscription_plan TEXT DEFAULT 'free',
  subscription_status TEXT DEFAULT 'none',
  onboarding_status TEXT DEFAULT 'pending',
  is_active BOOLEAN DEFAULT true,
  is_banned BOOLEAN DEFAULT false,
  ban_reason TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- workspaces table structure  
CREATE TABLE public.workspaces (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  owner_id UUID NOT NULL,
  settings JSONB DEFAULT '{}',
  plan TEXT NOT NULL DEFAULT 'free',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- password_reset_tokens table structure
CREATE TABLE public.password_reset_tokens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  token TEXT UNIQUE NOT NULL,
  email TEXT NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  used_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## ⚠️ **TROUBLESHOOTING**

### **Error: "relation already exists"**
**Solution**: Table already exists, continue with next migration

### **Error: "permission denied"**
**Solution**: Ensure you're using service role key or have admin permissions

### **Error: "function already exists"**
**Solution**: Function exists, continue with next statement

### **Error: "trigger already exists"**
**Solution**: Trigger exists, continue with next statement

### **Error: "syntax error"**
**Solution**: Check SQL syntax, ensure proper semicolons

---

## 🔄 **ROLLBACK INSTRUCTIONS**

If you need to rollback migrations:

```sql
-- Drop tables (reverse order)
DROP TABLE IF EXISTS public.password_reset_tokens CASCADE;
DROP TABLE IF EXISTS public.workspace_members CASCADE;
DROP TABLE IF EXISTS public.workspaces CASCADE;
DROP TABLE IF EXISTS public.profiles CASCADE;

-- Drop functions
DROP FUNCTION IF EXISTS public.handle_new_user() CASCADE;
DROP FUNCTION IF EXISTS public.update_updated_at() CASCADE;
DROP FUNCTION IF EXISTS public.cleanup_expired_tokens() CASCADE;
DROP FUNCTION IF EXISTS public.update_workspace_updated_at() CASCADE;
DROP FUNCTION IF EXISTS public.update_password_reset_token_updated_at() CASCADE;
```

---

## 📊 **PERFORMANCE CONSIDERATIONS**

### **Indexes Created**
- `profiles`: email, workspace_id, subscription_status, role
- `workspaces`: owner_id, plan, slug
- `workspace_members`: workspace_id, user_id, role
- `password_reset_tokens`: token, email, expires_at

### **Query Optimization**
- RLS policies use user ID for efficient filtering
- Indexes support common query patterns
- Triggers maintain data consistency

---

## 🔐 **SECURITY FEATURES**

### **Row Level Security (RLS)**
- Users can only access their own data
- Admins have elevated privileges
- Workspace isolation enforced

### **Token Security**
- Cryptographically secure tokens
- Automatic expiration (1 hour)
- Cleanup of expired tokens

### **Data Validation**
- Check constraints on enums
- Foreign key relationships
- Not null constraints

---

## 📝 **POST-MIGRATION CHECKLIST**

- [ ] All 3 migration files executed successfully
- [ ] Tables created with correct structure
- [ ] RLS enabled on all tables
- [ ] Indexes created for performance
- [ ] Triggers functioning correctly
- [ ] Test user profile exists
- [ ] Can query tables via API
- [ ] Password reset tokens table accessible

---

## 🎯 **NEXT STEPS**

After successful migration:

1. **Update Environment Variables** (Task 32)
2. **Replace In-Memory Storage** (Task 33)
3. **Implement Error Logging** (Task 34)
4. **Add CSRF Protection** (Task 35)
5. **Configure Rate Limiting** (Task 36)

---

## 📞 **SUPPORT**

If you encounter issues:
1. Check Supabase project permissions
2. Verify service role key is correct
3. Review SQL syntax in migration files
4. Check Supabase logs for errors

---

*Last Updated: January 16, 2026*
*Version: 1.0*
*Status: Ready for Execution* ✅
