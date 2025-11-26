# RaptorFlow Database Migration Guide

## Running the Strategic System Migrations

### Prerequisites
- Supabase project set up
- Database connection configured
- Migrations 001-008 already applied

### Migration Files
1. **009_strategic_system_foundation.sql** - Creates 6 new tables for strategic system
2. **010_enhance_existing_tables.sql** - Adds strategic attributes to existing tables

### How to Run

#### Option 1: Supabase Dashboard (Recommended)
1. Open your Supabase project dashboard
2. Navigate to **SQL Editor**
3. Create a new query
4. Copy the contents of `009_strategic_system_foundation.sql`
5. Click **Run**
6. Wait for completion
7. Repeat steps 3-6 for `010_enhance_existing_tables.sql`

#### Option 2: Command Line (psql)
```bash
# Navigate to database directory
cd database/migrations

# Run migration 009
psql -h <your-supabase-host> -U postgres -d postgres -f 009_strategic_system_foundation.sql

# Run migration 010
psql -h <your-supabase-host> -U postgres -d postgres -f 010_enhance_existing_tables.sql
```

#### Option 3: Supabase CLI
```bash
# Link to your project (if not already linked)
supabase link --project-ref <your-project-ref>

# Run migrations
supabase db push
```

### Verification

After running migrations, verify tables were created:

```sql
-- Check new tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
  'positioning', 
  'message_architecture', 
  'campaigns', 
  'campaign_cohorts', 
  'strategy_insights', 
  'competitors',
  'journey_stages',
  'channel_roles'
);

-- Check cohorts table has new columns
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'cohorts' 
AND column_name IN (
  'buying_triggers', 
  'decision_criteria', 
  'objection_map', 
  'journey_distribution'
);

-- Check moves table has new columns
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'moves' 
AND column_name IN (
  'campaign_id', 
  'journey_stage_from', 
  'journey_stage_to'
);

-- Check views were created
SELECT table_name 
FROM information_schema.views 
WHERE table_schema = 'public' 
AND table_name IN (
  'campaign_health_summary', 
  'cohort_journey_summary'
);
```

### Expected Results
- ✅ 8 new tables created
- ✅ 9 new columns added to cohorts table
- ✅ 6 new columns added to moves table
- ✅ 2 new views created
- ✅ All RLS policies applied
- ✅ All indexes created

### Rollback (if needed)

If you need to rollback these migrations:

```sql
-- Drop new tables (in reverse order due to foreign keys)
DROP TABLE IF EXISTS public.strategy_insights CASCADE;
DROP TABLE IF EXISTS public.competitors CASCADE;
DROP TABLE IF EXISTS public.campaign_cohorts CASCADE;
DROP TABLE IF EXISTS public.campaigns CASCADE;
DROP TABLE IF EXISTS public.message_architecture CASCADE;
DROP TABLE IF EXISTS public.positioning CASCADE;
DROP TABLE IF EXISTS public.channel_roles CASCADE;
DROP TABLE IF EXISTS public.journey_stages CASCADE;

-- Drop views
DROP VIEW IF EXISTS public.campaign_health_summary;
DROP VIEW IF EXISTS public.cohort_journey_summary;

-- Drop validation functions
DROP FUNCTION IF EXISTS validate_decision_criteria_weights(JSONB);
DROP FUNCTION IF EXISTS validate_journey_distribution(JSONB);

-- Remove columns from cohorts (optional - may want to keep data)
ALTER TABLE public.cohorts 
  DROP COLUMN IF EXISTS buying_triggers,
  DROP COLUMN IF EXISTS decision_criteria,
  DROP COLUMN IF EXISTS objection_map,
  DROP COLUMN IF EXISTS attention_windows,
  DROP COLUMN IF EXISTS journey_distribution,
  DROP COLUMN IF EXISTS competitive_frame,
  DROP COLUMN IF EXISTS decision_making_unit,
  DROP COLUMN IF EXISTS health_score,
  DROP COLUMN IF EXISTS last_validated;

-- Remove columns from moves (optional - may want to keep data)
ALTER TABLE public.moves 
  DROP COLUMN IF EXISTS campaign_id,
  DROP COLUMN IF EXISTS journey_stage_from,
  DROP COLUMN IF EXISTS journey_stage_to,
  DROP COLUMN IF EXISTS message_variant,
  DROP COLUMN IF EXISTS asset_requirements,
  DROP COLUMN IF EXISTS intensity;
```

### Troubleshooting

**Error: "function get_user_workspace_id() does not exist"**
- This function should exist from migration 004. If not, you need to run that migration first.

**Error: "relation 'workspaces' does not exist"**
- You need to run earlier migrations first (001-008).

**Error: "constraint violation"**
- Check that you don't have existing data that conflicts with new constraints.

**Error: "permission denied"**
- Ensure you're connected as a user with sufficient privileges (postgres user recommended).

### Next Steps

After successful migration:
1. ✅ Database foundation complete
2. ⏭️ Proceed to Phase 2: Positioning Workshop UI
3. ⏭️ Create backend services for new tables
4. ⏭️ Update frontend to use new schema

### Support

If you encounter issues:
1. Check Supabase logs in dashboard
2. Verify all previous migrations (001-008) are applied
3. Ensure database user has proper permissions
4. Review the SQL files for any syntax errors
