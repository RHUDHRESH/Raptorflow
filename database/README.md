# KOA Move System - Database Setup

This directory contains database migrations and setup instructions for the Kinetic Operations Architecture (KOA) Move System.

## Prerequisites

- Supabase account and project
- PostgreSQL access (via Supabase or direct connection)
- Node.js and npm/yarn installed

## Setup Instructions

### 1. Run Database Migration

Execute the SQL migration file to create all required tables:

```bash
# Option 1: Via Supabase Dashboard
# 1. Go to your Supabase project dashboard
# 2. Navigate to SQL Editor
# 3. Copy and paste the contents of `001_move_system_schema.sql`
# 4. Execute the migration

# Option 2: Via Supabase CLI
supabase db push

# Option 3: Via psql (if you have direct database access)
psql -h your-db-host -U your-user -d your-database -f 001_move_system_schema.sql
```

### 2. Seed Initial Data

After running the migration, you'll need to seed the database with:

1. **Maneuver Types** - Pre-defined maneuver templates
2. **Capability Nodes** - Tech Tree foundation nodes

You can use the seed data files in `src/lib/seed-data/`:

```typescript
// Example seeding script (create this as a separate file)
import { MANEUVER_TEMPLATES } from '../src/lib/seed-data/maneuver-types'
import { getAllCapabilityNodes } from '../src/lib/seed-data/capability-nodes'
import { supabase } from './supabase/client'

async function seedDatabase() {
  // Seed maneuver types
  for (const template of MANEUVER_TEMPLATES) {
    await supabase.from('maneuver_types').insert({
      name: template.name,
      category: template.category,
      base_duration_days: template.baseDurationDays,
      fogg_role: template.foggRole,
      intensity_score: template.intensityScore,
      risk_profile: template.riskProfile,
      description: template.description,
      default_config: template.defaultConfig
    })
  }

  // Seed capability nodes (for each workspace)
  // Note: You'll need to set workspace_id and link parent nodes
}
```

### 3. Configure Supabase Client

Create a Supabase client configuration file:

```typescript
// src/lib/supabase/client.ts
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

Add to your `.env` file:
```
VITE_SUPABASE_URL=your-project-url
VITE_SUPABASE_ANON_KEY=your-anon-key
```

### 4. Set Up Row Level Security (RLS)

Create RLS policies to ensure users can only access their workspace data:

```sql
-- Enable RLS on all tables
ALTER TABLE capability_nodes ENABLE ROW LEVEL SECURITY;
ALTER TABLE moves ENABLE ROW LEVEL SECURITY;
ALTER TABLE sprints ENABLE ROW LEVEL SECURITY;
ALTER TABLE lines_of_operation ENABLE ROW LEVEL SECURITY;

-- Example policy for moves table
CREATE POLICY "Users can only see moves in their workspace"
  ON moves FOR SELECT
  USING (
    workspace_id IN (
      SELECT workspace_id FROM workspace_members 
      WHERE user_id = auth.uid()
    )
  );
```

## Database Schema Overview

### Core Tables

- **maneuver_types** - Static maneuver templates (Authority Sprint, Scarcity Flank, etc.)
- **capability_nodes** - Tech Tree nodes (Analytics Core, Lead Magnet, etc.)
- **moves** - Actual Move instances executing in Sprints
- **sprints** - Time-boxed execution windows
- **lines_of_operation** - Strategic groupings of Moves
- **move_anomalies** - AI-detected issues
- **move_logs** - Daily execution tracking

### Relationships

```
Workspace
  ├── Capability Nodes (Tech Tree)
  ├── Lines of Operation
  ├── Sprints
  │     └── Moves
  │           ├── Maneuver Type (template)
  │           ├── Anomalies
  │           └── Logs
  └── ICPs (referenced by Moves)
```

## Next Steps

1. **Set up authentication** - Configure Supabase Auth
2. **Create workspace system** - Multi-tenant workspace support
3. **Implement API endpoints** - Or use Supabase directly from frontend
4. **Add real-time subscriptions** - For live updates on Moves
5. **Set up background jobs** - For anomaly detection and auto-unlocking

## Troubleshooting

### Common Issues

1. **Foreign key constraints** - Make sure to seed maneuver_types before capability_nodes
2. **Array types** - PostgreSQL arrays need proper formatting in inserts
3. **JSONB fields** - Ensure proper JSON structure when inserting

### Useful Queries

```sql
-- Check all maneuver types
SELECT * FROM maneuver_types ORDER BY category, name;

-- Check capability node dependencies
SELECT 
  cn.name,
  cn.tier,
  cn.status,
  array_agg(mt.name) as unlocks_maneuvers
FROM capability_nodes cn
LEFT JOIN maneuver_types mt ON mt.id = ANY(cn.unlocks_maneuver_ids)
GROUP BY cn.id, cn.name, cn.tier, cn.status;

-- Get moves with full relations
SELECT 
  m.*,
  mt.name as maneuver_name,
  s.name as sprint_name,
  lo.name as line_of_operation_name
FROM moves m
LEFT JOIN maneuver_types mt ON m.maneuver_type_id = mt.id
LEFT JOIN sprints s ON m.sprint_id = s.id
LEFT JOIN lines_of_operation lo ON m.line_of_operation_id = lo.id;
```


