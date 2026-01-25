# RAPTORFLOW DATABASE DEPLOYMENT GUIDE

## Overview
This guide provides step-by-step instructions to deploy the consolidated database schema to Supabase and verify all components are working correctly.

## Prerequisites
- Supabase Dashboard access
- Project ID: `vpwwzsanuyhpkvgorcnc`
- Service role key (available in `.env.production`)

## Step 1: Execute Schema SQL

### Option A: Using Generated SQL File
1. Open the generated SQL file: `schema_for_manual_execution.sql`
2. Go to [Supabase Dashboard](https://app.supabase.com/project/vpwwzsanuyhpkvgorcnc)
3. Navigate to **SQL Editor**
4. Copy and paste the entire SQL content
5. Click **Run** to execute

### Option B: Using Individual Migration
1. Open `supabase/migrations/20260122074403_final_auth_consolidation.sql`
2. Execute in SQL Editor as above

## Step 2: Verify Schema Creation

Execute these verification queries in the SQL Editor:

```sql
-- Check table creation
SELECT table_name, table_type
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('profiles', 'subscriptions', 'payments', 'email_logs', 'workspaces')
ORDER BY table_name;

-- Check RLS policies
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

-- Check indexes
SELECT indexname, tablename
FROM pg_indexes
WHERE schemaname = 'public'
AND tablename IN ('profiles', 'subscriptions', 'payments', 'email_logs', 'workspaces')
ORDER BY tablename, indexname;
```

## Step 3: Test Database Operations

### Test Profile Creation
```sql
-- Test the trigger by creating a test user (this will fail without auth, but tests the structure)
INSERT INTO public.profiles (id, email, full_name)
VALUES ('00000000-0000-0000-0000-000000000000', 'test@example.com', 'Test User')
ON CONFLICT (id) DO NOTHING;
```

### Test Workspace Query (Fixed Version)
```sql
-- This query should work now (no user_id column)
SELECT id, name, owner_id
FROM public.workspaces
WHERE owner_id = '00000000-0000-0000-0000-000000000000'
LIMIT 1;
```

## Step 4: Update Frontend References

The following files have already been fixed to match the correct schema:

### ✅ Fixed Files
- `src/middleware.ts` - Removed `user_id` reference, using `owner_id`
- `src/contexts/AuthContext.tsx` - Removed `workspace_id` reference from profiles
- `src/app/api/gdpr/data-export/route.ts` - Fixed workspace query

## Step 5: Test Authentication Flow

1. Start the development server:
   ```bash
   npm run dev
   ```

2. Navigate to `http://localhost:3000/login`

3. Test authentication:
   - Try Google OAuth login
   - Try email/password login
   - Check for redirect loops (should be fixed)

## Step 6: Verify Data Flow

### Check User Profile Creation
After successful login, verify:

```sql
-- Check if profile was created for the logged-in user
SELECT id, email, full_name, onboarding_status, subscription_plan
FROM public.profiles
WHERE email = 'your-test-email@example.com';
```

### Check Workspace Creation
```sql
-- Check if workspace was created
SELECT id, name, owner_id, created_at
FROM public.workspaces
WHERE owner_id = 'user-uuid-from-above';
```

## Step 7: Test API Endpoints

### Test Profile API
```bash
curl -X GET "http://localhost:3000/api/user/profile" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Test Workspace Operations
```bash
curl -X GET "http://localhost:3000/api/workspaces" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Expected Schema Structure

### profiles Table
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | Primary key, references auth.users |
| email | TEXT | User email |
| full_name | TEXT | Display name |
| avatar_url | TEXT | Profile picture URL |
| ucid | TEXT | Unique customer ID |
| role | TEXT | 'user' or 'admin' |
| onboarding_status | TEXT | 'pending', 'in_progress', 'active' |
| subscription_plan | TEXT | 'free', 'ascent', 'glide', 'soar' |
| subscription_status | TEXT | 'none', 'active', 'past_due', etc. |
| workspace_preferences | JSONB | User preferences |
| created_at | TIMESTAMPTZ | Creation timestamp |
| updated_at | TIMESTAMPTZ | Last update |

### workspaces Table
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | Primary key |
| owner_id | UUID | References profiles.id |
| name | TEXT | Workspace name |
| settings | JSONB | Workspace settings |
| created_at | TIMESTAMPTZ | Creation timestamp |
| updated_at | TIMESTAMPTZ | Last update |

## Troubleshooting

### Issue: "column user_id does not exist"
**Solution**: The schema has been fixed to use `owner_id` instead of `user_id` in workspaces table.

### Issue: Authentication redirect loops
**Solution**: Middleware has been fixed to query the correct column names.

### Issue: Profile not created after login
**Solution**: Check if the trigger `on_auth_user_created` exists and is working.

### Issue: RLS policies blocking access
**Solution**: Verify policies are correctly set up in Step 2.

## Step 8: Clean Up Old Migration Files (Optional)

After successful deployment, you can archive old migration files:

```bash
mkdir supabase/migrations/archive
mv supabase/migrations/2024*.sql supabase/migrations/archive/
mv supabase/migrations/202501*.sql supabase/migrations/archive/
```

Keep only:
- `20260122074403_final_auth_consolidation.sql`
- Any future migrations

## Step 9: Update Documentation

Update any documentation that references the old schema:
- API documentation
- Developer guides
- Database diagrams

## Verification Checklist

- [ ] Schema SQL executed successfully
- [ ] All tables created (profiles, workspaces, subscriptions, payments, email_logs)
- [ ] RLS policies enabled and working
- [ ] Indexes created correctly
- [ ] Authentication flow works without redirect loops
- [ ] Profile creation trigger works
- [ ] Workspace lookup uses correct column names
- [ ] API endpoints respond correctly
- [ ] Frontend loads user data properly

## Support

If you encounter issues:
1. Check the browser console for errors
2. Review the SQL execution logs in Supabase Dashboard
3. Verify environment variables are correct
4. Test with a fresh browser session

## Next Steps

After successful deployment:
1. Monitor the authentication flow
2. Test payment processing if applicable
3. Set up monitoring for database operations
4. Plan regular backup schedules
