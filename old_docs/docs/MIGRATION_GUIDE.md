# 🚀 Raptorflow Migration Guide

## Quick Start: Apply New Database Schema

You have a new migration file ready: `004_core_missing_tables.sql`

This migration adds critical tables for the enhanced features:
- ✅ `cohorts` - Enhanced ICP management
- ✅ `global_strategies` - Strategy Wizard data
- ✅ `quick_wins` - Daily Sweep opportunities
- ✅ `workspaces` - Multi-user support
- ✅ `user_workspaces` - Team collaboration
- ✅ `support_feedback` - Support loop
- ✅ `move_decisions` - Weekly Review decisions
- ✅ `notifications` - Notification system

---

## Option 1: Supabase Dashboard (Recommended)

### Step 1: Open Supabase SQL Editor

1. Go to [Supabase Dashboard](https://app.supabase.com/)
2. Select your Raptorflow project
3. Navigate to **SQL Editor** (left sidebar)

### Step 2: Run the Migration

1. Click **New Query**
2. Copy the entire contents of `database/migrations/004_core_missing_tables.sql`
3. Paste into the SQL Editor
4. Click **Run** (or press Ctrl+Enter)

### Step 3: Verify Success

You should see:
```
Success. No rows returned
```

Then verify tables were created:
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
  'cohorts', 
  'global_strategies', 
  'quick_wins', 
  'workspaces', 
  'user_workspaces',
  'support_feedback',
  'move_decisions',
  'notifications'
)
ORDER BY table_name;
```

Expected output: 8 tables listed.

---

## Option 2: Supabase CLI (Advanced)

If you have Supabase CLI installed:

```bash
# Login to Supabase
npx supabase login

# Link to your project
npx supabase link --project-ref <your-project-ref>

# Apply the migration
npx supabase db push --file database/migrations/004_core_missing_tables.sql
```

---

## Post-Migration Setup

### 1. Create Your First Workspace

After migration, you need to create a workspace and assign yourself:

```sql
-- Insert a default workspace
INSERT INTO workspaces (name, slug, plan, cohorts_limit, moves_per_sprint_limit)
VALUES ('My Workspace', 'my-workspace', 'Ascent', 3, 5)
RETURNING id;

-- Assign yourself to the workspace (replace YOUR_USER_ID and WORKSPACE_ID)
INSERT INTO user_workspaces (user_id, workspace_id, role)
VALUES ('<YOUR_USER_ID>', '<WORKSPACE_ID>', 'Owner');
```

**To find your user ID:**
```sql
SELECT id, email FROM auth.users;
```

### 2. Test the New Features

Once the workspace is set up, test these new pages:

1. **Strategy Wizard**: http://localhost:3000/strategy/wizard
2. **Weekly Review**: http://localhost:3000/review
3. **Enhanced ICP Builder**: http://localhost:3000/cohorts/create
4. **Dashboard**: http://localhost:3000/ (with new layout)

---

## Troubleshooting

### Error: "function update_updated_at_column() does not exist"

This function should exist from previous migrations. If not, add it:

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### Error: "relation 'moves' does not exist"

You need to run previous migrations first:
1. `001_move_system_schema.sql`
2. `002_assets_table.sql`
3. `003_quests_table.sql`
4. Then `004_core_missing_tables.sql`

### Error: "policy already exists"

If you've run this migration before, drop the policies first:

```sql
-- Drop all policies on new tables
DROP POLICY IF EXISTS "Users can view cohorts in their workspace" ON cohorts;
-- ... (repeat for all policies)

-- Or drop and recreate tables
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS move_decisions CASCADE;
-- ... etc
```

---

## Verification Checklist

After running the migration, verify:

- [ ] All 8 new tables exist
- [ ] RLS is enabled on all tables
- [ ] Indexes are created
- [ ] Triggers are working
- [ ] `get_user_workspace_id()` function exists
- [ ] You have a workspace created
- [ ] You're assigned to the workspace as Owner

---

## Next Steps

Once migration is complete:

1. **Test Strategy Wizard**: Create your first global strategy
2. **Test Weekly Review**: Review some moves (you may need to create test data)
3. **Test ICP Builder**: Create a cohort with psychographic blueprint
4. **Deploy**: Once tested locally, apply migration to production

---

## Support

If you encounter issues:
1. Check Supabase logs in Dashboard > Logs
2. Verify environment variables in `.env.local`
3. Ensure you're on the latest version of Supabase client
4. Check that previous migrations (001-003) ran successfully

---

**Ready to apply? Let's go! 🚀**

