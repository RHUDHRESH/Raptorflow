# APPLY MIGRATION TO SUPABASE - IMMEDIATE ACTION REQUIRED

## Your Access Token
```
sbp_23be6405f8c238ea5e6218120f12262ac8d04a74
```

## Method 1: SQL Editor (Fastest - 2 minutes)

1. **Open Supabase Dashboard**
   ```
   https://supabase.com/dashboard/project/ywuokqopcfbqwtbzqvgj
   ```

2. **Go to SQL Editor**
   - Left sidebar → `SQL Editor`
   - Click `New Query`

3. **Copy & Paste Migration**
   - Open: `supabase/migrations/20250210_auth_system_fix.sql`
   - Copy entire contents
   - Paste into SQL Editor
   - Click `Run`

4. **Verify Success**
   ```sql
   SELECT table_name
   FROM information_schema.tables
   WHERE table_schema = 'public'
   AND table_name IN ('profiles', 'workspaces', 'workspace_members');
   ```
   Should return 3 rows.

---

## Method 2: Supabase CLI (If you have it installed)

```bash
# Set your access token
export SUPABASE_ACCESS_TOKEN=sbp_23be6405f8c238ea5e6218120f12262ac8d04a74

# Link project
cd supabase
supabase link --project-ref ywuokqopcfbqwtbzqvgj

# Push migration
supabase db push
```

---

## Method 3: Python Script (I created this for you)

```bash
cd backend

# You need SERVICE_ROLE_KEY (not access token)
# Get it from: Supabase Dashboard > Project Settings > API > service_role secret
set SUPABASE_SERVICE_ROLE_KEY=eyJhbG...

python apply_auth_migration.py
```

---

## What Gets Created

### Tables
- `profiles` - User profiles linked to auth.users
- `workspaces` - Workspace/organization data
- `workspace_members` - Membership records
- `user_sessions` - Session tracking

### Security
- Row Level Security (RLS) enabled on all tables
- Users can only access their own data
- Workspace owners have admin control

### Auto-Creation
When a new user signs up:
1. Profile automatically created
2. Personal workspace auto-created
3. User set as workspace owner

---

## After Migration - Test Auth

```bash
# 1. Start backend
cd backend
python main.py

# 2. Test signup
curl -X POST http://localhost:8000/api/v2/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","full_name":"Test User"}'

# 3. Test login
curl -X POST http://localhost:8000/api/v2/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'

# 4. Test get profile (use token from login)
curl http://localhost:8000/api/v2/auth/me \
  -H "Authorization: Bearer <access_token>"
```

---

## Troubleshooting

### "permission denied" errors
- Make sure you're using the Service Role Key, not the anon key
- Service Role Key has admin privileges

### "relation already exists" errors
- Tables already exist from previous migration
- This is OK, data will be preserved

### "function auth.uid() does not exist"
- You're not in the Supabase managed auth schema
- Must run SQL in Supabase SQL Editor, not local PostgreSQL

---

## Need Help?

The migration file is ready at:
`C:\Users\hp\.windsurf\worktrees\Raptorflow\Raptorflow-183794c3\supabase\migrations\20250210_auth_system_fix.sql`

Just copy-paste into Supabase SQL Editor and run it!
