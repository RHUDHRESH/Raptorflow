# Database Migrations

Run these migrations in order in your Supabase SQL Editor:

1. `001_move_system_schema.sql` - Core Move System tables
2. `002_assets_table.sql` - Asset Factory support
3. `003_quests_table.sql` - Quests and gamification
4. `004_core_missing_tables.sql` - Cohorts, Strategy, Quick Wins, Workspaces, etc.

## Running Migration 004

1. Log into Supabase Dashboard
2. Go to SQL Editor
3. Create New Query
4. Copy contents of `004_core_missing_tables.sql`
5. **IMPORTANT**: Before running, ensure the `get_user_workspace_id()` function is properly configured for your setup
6. Click Run

## Notes on get_user_workspace_id()

The function at the end of migration 004 has two options:

**Option 1 (Production)**: Uses the `user_workspaces` table (default in the migration)
```sql
RETURN (
  SELECT workspace_id 
  FROM user_workspaces 
  WHERE user_id = auth.uid() 
  LIMIT 1
);
```

**Option 2 (Development)**: Returns a fixed workspace ID
```sql
RETURN 'YOUR_DEV_WORKSPACE_ID'::uuid;
```

For initial development, you can generate a UUID at https://www.uuidgenerator.net/ and use Option 2.

## After Running Migrations

Test with these queries:

```sql
-- Verify tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('cohorts', 'global_strategies', 'quick_wins', 'workspaces', 'user_workspaces');

-- Check RLS is enabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('cohorts', 'global_strategies', 'quick_wins');
```

