# Move System - Implementation Complete

## What's Been Implemented

I've completed the foundation for the complete Move System with real Supabase backend integration. Here's what's ready:

### ✅ Phase 1: Database Foundation (COMPLETE)

**Files Created:**
- `database/migrations/001_move_system_schema.sql` - Complete database schema
- `database/seed-capability-nodes.sql` - 20 capability nodes across 4 tiers
- `database/seed-maneuver-types.sql` - 25+ maneuver templates
- `database/rls-policies.sql` - Row Level Security policies
- `database/DATABASE_SETUP_GUIDE.md` - Step-by-step setup instructions
- `.env.example` - Environment variables template

**What It Includes:**
- Full database schema for moves, sprints, capability nodes, maneuver types, anomalies, logs
- Tech tree with Foundation → Traction → Scale → Dominance progression
- Maneuver types: Offensive, Defensive, Logistical, Recon
- RLS policies for multi-tenant workspace isolation
- Indexes for performance
- Triggers for automatic timestamp updates

### ✅ Phase 2: Services Layer (COMPLETE)

**Files Created:**
- `src/lib/services/icp-service.ts` - ICP/Cohort CRUD operations
- `src/lib/services/sprint-service.ts` - Sprint management & capacity calculations
- `src/lib/services/analytics-service.ts` - Metrics aggregation & health status
- `src/lib/services/move-service.ts` - Move CRUD & maneuver operations (UPDATED)
- `src/lib/services/tech-tree-service.ts` - Capability unlocking logic (UPDATED)
- `src/hooks/useMoveSystem.ts` - React hooks for easy data access

**What It Provides:**
- Full CRUD operations for all entities
- Real-time Supabase integration
- Capacity management and sprint load calculations
- Health status calculations for moves
- Anomaly detection and logging
- Tech tree progression logic
- React hooks with loading/error states

### ⏳ Phase 3-7: UI Integration (PARTIAL)

The UI components exist but need to be connected to the new services. Here's the roadmap:

## Getting Started - Quick Setup

### Step 1: Set Up Supabase

1. **Create Supabase Project**
   ```bash
   # Go to https://app.supabase.com
   # Create a new project
   # Note your project URL and anon key
   ```

2. **Run Database Migrations**
   - Follow `database/DATABASE_SETUP_GUIDE.md`
   - Run the schema migration SQL
   - Run the seed data SQL
   - Set up RLS policies

3. **Configure Environment Variables**
   ```bash
   # Create .env.local in project root
   VITE_SUPABASE_URL=https://your-project.supabase.co
   VITE_SUPABASE_ANON_KEY=your-anon-key-here
   
   # Optional: AI features
   VITE_VERTEX_AI_API_KEY=your-key
   ```

### Step 2: Install Dependencies

```bash
npm install
```

### Step 3: Update Workspace ID

The system uses workspace-based multi-tenancy. You need to:

1. **Get a workspace ID** (generate at https://www.uuidgenerator.net/)

2. **Update seed files** - Replace `'YOUR_WORKSPACE_ID'` in:
   - `database/seed-capability-nodes.sql`

3. **Update the helper function** in `src/hooks/useMoveSystem.ts`:
   ```typescript
   const getWorkspaceId = (): string => {
     return 'your-actual-workspace-id';
   };
   ```

### Step 4: Run the Application

```bash
npm run dev
```

## Integration Guide - Connecting UI to Services

### Example: Updating Move Library

Here's how to connect the existing UI to real data:

```jsx
// src/pages/MoveLibrary.jsx (updated version)
import { useManeuverTypes, useCapabilityNodes } from '../hooks/useMoveSystem';

export default function MoveLibrary() {
  // Replace mock data with real data
  const { maneuverTypes, loading: maneuversLoading } = useManeuverTypes();
  const { capabilityNodes, loading: capabilitiesLoading } = useCapabilityNodes();
  
  const loading = maneuversLoading || capabilitiesLoading;
  
  if (loading) {
    return <LoadingSpinner />;
  }
  
  // Use maneuverTypes and capabilityNodes as before
  // ...rest of component
}
```

### Example: Creating a Move

```jsx
import { useMoves, useICPs } from '../hooks/useMoveSystem';

function CreateMoveButton({ maneuverTypeId }) {
  const { createMove } = useMoves();
  const { icps } = useICPs();
  
  const handleCreate = async () => {
    const newMove = await createMove({
      maneuver_type_id: maneuverTypeId,
      name: 'My New Move',
      primary_icp_id: icps[0].id,
      status: 'Planning',
      start_date: new Date().toISOString().split('T')[0],
      end_date: /* calculate end date */,
    });
    
    // Navigate to move detail or sprint
    navigate(`/moves/${newMove.id}`);
  };
  
  return <button onClick={handleCreate}>Create Move</button>;
}
```

### Example: War Room with Real Data

```jsx
import { useSprints, useMoves } from '../hooks/useMoveSystem';

export default function WarRoom() {
  const { activeSprint, loading: sprintLoading } = useSprints();
  const { moves, loading: movesLoading } = useMoves();
  
  const sprintMoves = moves.filter(m => m.sprint_id === activeSprint?.id);
  
  // Render sprint lanes with sprintMoves
}
```

## Architecture Overview

```
┌─────────────────────────────────────────┐
│           React Components              │
│  (MoveLibrary, WarRoom, TechTree, etc)  │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│         React Hooks Layer               │
│    (useMoveSystem, useManeuverTypes)    │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│          Services Layer                 │
│  (moveService, techTreeService, etc)    │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│        Supabase Client                  │
│         (src/lib/supabase.ts)           │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│         Supabase Database               │
│  (PostgreSQL with RLS policies)         │
└─────────────────────────────────────────┘
```

## Key Data Flows

### 1. Move Creation Flow

```
User clicks "Instantiate" in Move Library
  ↓
UI checks if maneuver is unlocked (techTreeService)
  ↓
Creates move with moveService.createMove()
  ↓
Supabase inserts into moves table
  ↓
RLS policy checks workspace_id
  ↓
Move is created and returned
  ↓
UI navigates to War Room or Move Detail
```

### 2. Tech Tree Unlock Flow

```
User clicks "Unlock" on capability node
  ↓
UI calls techTreeService.unlockNode()
  ↓
Service updates capability_nodes.status = 'Unlocked'
  ↓
Service checks maneuver_prerequisites table
  ↓
Returns newly unlocked maneuvers
  ↓
UI updates to show available maneuvers
```

### 3. Sprint Capacity Flow

```
User adds move to sprint
  ↓
sprintService.updateLoad() called
  ↓
Recalculates sprint.current_load
  ↓
Checks against sprint.capacity_budget
  ↓
Updates UI with new capacity %
  ↓
Shows warning if overloaded
```

## What Still Needs Connection

### High Priority UI Updates

1. **Move Library** (`src/pages/MoveLibrary.jsx`)
   - Replace `generateMockManeuverTypes()` with `useManeuverTypes()`
   - Replace `generateMockCapabilityNodes()` with `useCapabilityNodes()`
   - Update instantiate flow to call `moveService.createMove()`

2. **War Room** (`src/pages/WarRoom.jsx`)
   - Use `useSprints()` and `useMoves()` hooks
   - Implement drag-and-drop with database persistence
   - Real-time capacity calculations

3. **Move Detail** (`src/pages/MoveDetail.jsx`)
   - Fetch move data with `moveService.getMove(id)`
   - Make OODA config editable
   - Connect to analytics-service for metrics

4. **Tech Tree** (`src/pages/TechTree.jsx`)
   - Use `useCapabilityNodes()` hook
   - Implement unlock functionality
   - Show dependency chains

5. **Dashboard** (`src/pages/Dashboard.jsx`)
   - Connect to real sprint and move data
   - Show actual metrics from analyticsService

### Medium Priority Features

6. **Asset Factory** - New page for content/asset tracking
7. **Quest System** - Gamified move sequences
8. **Strategy Wizard** - Enhanced with move recommendations
9. **Daily Sweep** - AI-powered quick wins
10. **Weekly Review** - Scale/Tweak/Kill interface

### AI Features

11. **Anomaly Detection** - Tone clash, fatigue, drift detection
12. **Content Suggestions** - 50 auto-tags per ICP
13. **Smart Recommendations** - Next moves, capacity adjustments

## Testing Your Setup

### 1. Test Database Connection

```typescript
// In browser console on any page:
const { data, error } = await window.supabase
  .from('maneuver_types')
  .select('count');

console.log('Maneuver types count:', data);
```

### 2. Test Service Layer

```typescript
import { moveService } from './lib/services/move-service';

// Test fetching maneuver types
const types = await moveService.getManeuverTypes();
console.log('Maneuver types:', types);
```

### 3. Test UI Integration

1. Navigate to `/moves/library`
2. Open DevTools console
3. Check for "Supabase not configured" warnings
4. If you see data, integration is working!

## Troubleshooting

### "Supabase not configured"

- Check `.env.local` file exists with correct keys
- Restart dev server after adding env vars
- Verify keys in Supabase dashboard

### "No rows returned" / Empty data

- Run seed data SQL scripts
- Check RLS policies are set up correctly
- Verify workspace_id matches in seed data and code

### "Permission denied"

- RLS policies may be blocking access
- Check `get_user_workspace_id()` function returns correct ID
- For development, can temporarily disable RLS on specific tables

### TypeScript errors in services

- Run `npm install @supabase/supabase-js`
- Ensure TypeScript is configured correctly
- Some type mismatches may need adjustment based on your exact schema

## Next Steps

1. **Complete Database Setup** - Follow `DATABASE_SETUP_GUIDE.md`
2. **Configure Environment** - Set up `.env.local`
3. **Update Workspace IDs** - Replace placeholders
4. **Test Connection** - Verify data flows
5. **Update UI Components** - Connect to services one by one
6. **Build Missing Features** - Asset Factory, Quests, etc.
7. **Add AI Features** - Anomaly detection, recommendations
8. **Polish & Test** - End-to-end testing

## File Structure Summary

```
raptorflow/
├── database/
│   ├── migrations/
│   │   └── 001_move_system_schema.sql      ✅ Created
│   ├── seed-capability-nodes.sql            ✅ Created
│   ├── seed-maneuver-types.sql             ✅ Created
│   ├── rls-policies.sql                     ✅ Created
│   └── DATABASE_SETUP_GUIDE.md              ✅ Created
├── src/
│   ├── hooks/
│   │   └── useMoveSystem.ts                 ✅ Created
│   ├── lib/
│   │   └── services/
│   │       ├── icp-service.ts               ✅ Created
│   │       ├── sprint-service.ts            ✅ Created
│   │       ├── analytics-service.ts         ✅ Created
│   │       ├── move-service.ts              ✅ Updated
│   │       └── tech-tree-service.ts         ✅ Updated
│   └── pages/
│       ├── MoveLibrary.jsx                  ⏳ Needs update
│       ├── WarRoom.jsx                      ⏳ Needs update
│       ├── MoveDetail.jsx                   ⏳ Needs update
│       ├── TechTree.jsx                     ⏳ Needs update
│       └── Dashboard.jsx                    ⏳ Needs update
└── .env.example                             ✅ Created
```

## Support & Resources

- **Supabase Docs**: https://supabase.com/docs
- **Database Guide**: `database/DATABASE_SETUP_GUIDE.md`
- **Type Definitions**: `src/types/move-system.ts`
- **Service Examples**: `src/hooks/useMoveSystem.ts`

---

**Status**: Backend complete, UI integration in progress. The foundation is solid - now it's about connecting the dots!

