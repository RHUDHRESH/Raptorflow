# Raptorflow Move System - Database Setup Guide

This guide will help you set up the complete database schema for the Move System in Supabase.

## Prerequisites

- Supabase account and project created
- Supabase credentials (URL and anon key)
- Basic SQL knowledge (helpful but not required)

## Step 1: Run the Main Schema Migration

1. Log in to your Supabase Dashboard at [app.supabase.com](https://app.supabase.com)
2. Select your project
3. Navigate to **SQL Editor** in the left sidebar
4. Click **New Query**
5. Copy the contents of `migrations/001_move_system_schema.sql`
6. Paste into the SQL editor
7. Click **Run** to execute

This creates all the tables, indexes, and triggers for the Move System.

## Step 2: Set Up Row Level Security (RLS)

1. In the SQL Editor, create another **New Query**
2. Copy the contents of `rls-policies.sql`
3. **IMPORTANT**: Before running, you need to adapt the `get_user_workspace_id()` function to your auth setup
   - Option A: If you have a `user_workspaces` table, use the first function
   - Option B: If workspace_id is in user metadata, use the second function
   - Option C: For development, you can temporarily return a fixed UUID
4. Paste into editor and click **Run**

### Development Shortcut (Single Workspace)

For development/testing, you can use this simplified approach:

```sql
-- Temporary: Return a fixed workspace ID for development
CREATE OR REPLACE FUNCTION get_user_workspace_id()
RETURNS UUID AS $$
  SELECT 'YOUR_DEV_WORKSPACE_ID'::uuid;
$$ LANGUAGE sql SECURITY DEFINER;
```

Replace `YOUR_DEV_WORKSPACE_ID` with a UUID (generate one at [uuidgenerator.net](https://www.uuidgenerator.net/)).

## Step 3: Seed Maneuver Types (Templates)

1. Create a **New Query** in SQL Editor
2. Copy contents of `seed-maneuver-types.sql`
3. Click **Run**

This populates 25+ maneuver templates across all categories (Offensive, Defensive, Logistical, Recon).

## Step 4: Seed Capability Nodes (Tech Tree)

1. Create a **New Query**
2. Copy contents of `seed-capability-nodes.sql`
3. **IMPORTANT**: Replace `'YOUR_WORKSPACE_ID'` with your actual workspace UUID
   - If using the dev shortcut above, use the same UUID
4. Click **Run**

This creates the Tech Tree with 20 capability nodes across 4 tiers.

## Step 5: Create Initial Data for Your Workspace

You'll need to manually create some initial records:

### Create a Line of Operation

```sql
INSERT INTO lines_of_operation (workspace_id, name, strategic_objective, seasonality_tag, status)
VALUES (
  'YOUR_WORKSPACE_ID'::uuid,
  'Q1 Growth Initiative',
  'Acquire first 100 customers',
  'Harvest',
  'Active'
);
```

### Create Your First Sprint

```sql
INSERT INTO sprints (workspace_id, name, start_date, end_date, theme, capacity_budget, season_type, status)
VALUES (
  'YOUR_WORKSPACE_ID'::uuid,
  'Sprint 1 - Foundation',
  CURRENT_DATE,
  CURRENT_DATE + INTERVAL '14 days',
  'Build marketing foundation',
  100,
  'Shoulder',
  'Active'
);
```

## Step 6: Verify Setup

Run these queries to verify everything is set up correctly:

```sql
-- Check maneuver types
SELECT COUNT(*) as maneuver_count FROM maneuver_types;
-- Should return ~25

-- Check capability nodes
SELECT COUNT(*) as capability_count FROM capability_nodes;
-- Should return ~20

-- Check tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('moves', 'sprints', 'capability_nodes', 'maneuver_types');
-- Should return 4 rows

-- Check RLS is enabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('moves', 'sprints', 'capability_nodes');
-- All should show rowsecurity = true
```

## Step 7: Update Frontend Environment Variables

Create or update `.env.local` in your project root:

```bash
VITE_SUPABASE_URL=https://your-project-ref.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here
VITE_VERTEX_AI_API_KEY=your-vertex-ai-key (optional, for AI features)
VITE_VERTEX_AI_ENDPOINT=us-central1-aiplatform.googleapis.com (optional)
```

Get your Supabase URL and anon key from:
**Project Settings > API > Project URL** and **Project API keys > anon public**

## Troubleshooting

### Error: "relation does not exist"

- Make sure you ran the main schema migration first
- Check that you're in the correct Supabase project

### Error: "permission denied"

- RLS policies may be blocking access
- For development, temporarily disable RLS on a table:
  ```sql
  ALTER TABLE table_name DISABLE ROW LEVEL SECURITY;
  ```

### Error: "workspace_id cannot be null"

- You need to pass a valid workspace_id when inserting records
- Make sure you replaced `'YOUR_WORKSPACE_ID'` in seed files

### No Data Showing in Frontend

- Check that the `get_user_workspace_id()` function returns the correct UUID
- Verify RLS policies are set up correctly
- Check browser console for API errors

## Production Considerations

Before going to production:

1. **Implement proper workspace management**
   - Create `workspaces` and `user_workspaces` tables
   - Update `get_user_workspace_id()` to use real data

2. **Set up proper authentication**
   - Configure auth providers (Google, email, etc.)
   - Set up user profiles and workspace assignment

3. **Enable RLS on all tables**
   - Never disable RLS in production
   - Test policies thoroughly

4. **Set up backups**
   - Enable point-in-time recovery in Supabase
   - Export schema and seed data

5. **Monitor performance**
   - Check slow queries in Supabase dashboard
   - Add indexes as needed

## Next Steps

Once your database is set up:

1. Test the connection from your frontend (check `src/lib/supabase.ts`)
2. Verify you can fetch maneuver types and capability nodes
3. Try creating a move through the UI
4. Monitor the logs in Supabase Dashboard > Logs

## Need Help?

- Supabase Docs: https://supabase.com/docs
- SQL Reference: https://www.postgresql.org/docs/
- Check the project README for troubleshooting tips


