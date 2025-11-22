# Move System Implementation Status

## ✅ COMPLETED (Phases 1-2)

### Database Foundation
- **001_move_system_schema.sql**: Complete PostgreSQL schema with all tables, indexes, triggers
- **seed-capability-nodes.sql**: 20 capability nodes across 4 tiers (Foundation → Dominance)
- **seed-maneuver-types.sql**: 25+ maneuver templates (Offensive, Defensive, Logistical, Recon)
- **rls-policies.sql**: Row Level Security for multi-tenant workspace isolation
- **DATABASE_SETUP_GUIDE.md**: Step-by-step setup instructions

### Services Layer (100% Complete)
- **icp-service.ts**: Full CRUD for cohorts/ICPs
- **sprint-service.ts**: Sprint management + capacity calculations
- **analytics-service.ts**: Metrics aggregation + health status algorithms
- **move-service.ts**: Move CRUD + maneuver operations
- **tech-tree-service.ts**: Capability unlocking logic + dependency checking

### React Integration Layer
- **useMoveSystem.ts**: Custom hooks with loading/error states for all entities
- **MoveLibraryIntegrated.jsx**: Example of fully integrated component

## 🔄 PARTIALLY COMPLETE (Phase 3)

### UI Components - Need Service Integration

**Current State**: UI components exist with mock data  
**What's Needed**: Replace mock data with service hooks

#### High Priority Updates

1. **MoveLibrary.jsx** (Example provided in MoveLibraryIntegrated.jsx)
   - ✅ Example integration created
   - ⏳ Replace existing file or merge changes
   - Simply swap `generateMockX()` with `useX()` hooks

2. **WarRoom.jsx**
   ```jsx
   // Replace:
   const [sprints] = useState(mockSprints);
   // With:
   const { activeSprint, sprints } = useSprints();
   const { moves } = useMoves();
   ```

3. **MoveDetail.jsx**
   ```jsx
   // Replace:
   const [move] = useState(mockMove);
   // With:
   const { id } = useParams();
   const [move, setMove] = useState(null);
   
   useEffect(() => {
     moveService.getMove(id).then(setMove);
   }, [id]);
   ```

4. **TechTree.jsx**
   ```jsx
   // Replace mock nodes with:
   const { capabilityNodes, unlockNode } = useCapabilityNodes();
   ```

5. **Dashboard.jsx**
   ```jsx
   // Add real metrics:
   const { moves } = useMoves();
   const { activeSprint } = useSprints();
   const { icps } = useICPs();
   ```

## 📋 TODO (Phases 4-7)

### Phase 4: Missing Features

#### Asset Factory (New Feature)
**Status**: Not started  
**What's Needed**: Create new page + service

```typescript
// src/lib/services/asset-service.ts
export interface Asset {
  id: string;
  workspace_id: string;
  move_id?: string;
  icp_id?: string;
  name: string;
  type: 'case_study' | 'whitepaper' | 'video' | 'template' | 'creative';
  status: 'draft' | 'review' | 'approved' | 'published';
  url?: string;
  metadata?: any;
}

// Similar CRUD to other services
```

**Create**:
- `src/pages/AssetFactory.jsx`
- `src/lib/services/asset-service.ts`
- Database table (add to schema)

#### Quest System
**Status**: Not started  
**What's Needed**: Gamified move sequences

```sql
CREATE TABLE quests (
  id UUID PRIMARY KEY,
  workspace_id UUID NOT NULL,
  name VARCHAR(200),
  description TEXT,
  move_ids UUID[],  -- Array of moves in sequence
  reward JSONB,
  status VARCHAR(20),
  completion_percentage INTEGER
);
```

**Files to Create**:
- `src/pages/QuestsEnhanced.jsx` (enhance existing)
- `src/lib/services/quest-service.ts`
- Quest progress tracking UI

#### Strategy Wizard Improvements
**Status**: Exists but needs enhancement  
**What's Needed**: 
- Move recommendations based on ICP
- Line of Operation creation
- Automated sprint planning

```jsx
// In StrategyWizard.jsx
const { maneuverTypes } = useManeuverTypes();
const { icps } = useICPs();

// Recommend maneuvers based on ICP characteristics
const recommendedManeuvers = maneuverTypes.filter(mt => 
  // Match maneuver to ICP based on typical_icps, tier, etc.
);
```

#### Weekly Review Interface
**Status**: Exists but basic  
**What's Needed**:
- Scale/Tweak/Kill decisions
- Performance summaries
- AI recommendations

```jsx
// WeeklyReview.jsx enhancement
const { moves } = useMoves();
const completedMoves = moves.filter(m => m.status === 'Complete');
const activeMoves = moves.filter(m => m.status.includes('OODA'));

// Show metrics, health status, recommendations
```

### Phase 6: AI Features

#### Anomaly Detection
**Status**: Service scaffolding exists, AI logic needed

```typescript
// src/lib/services/anomaly-detection-service.ts
export const detectToneClash = async (content: string, icp: ICP) => {
  // Use Vertex AI to compare content tone against ICP communication.tone
  const prompt = `
    Analyze this content for tone clash:
    Content: ${content}
    Target Audience: ${icp.communication.tone}
    
    Does the tone match? Respond with JSON: {clash: boolean, reason: string}
  `;
  
  // Call Vertex AI API
  return await callVertexAI(prompt);
};
```

**Files to Create**:
- `src/lib/services/anomaly-detection-service.ts`
- Integration with existing `moveService.createAnomaly()`

#### Content Suggestions (50 Auto-Tags per ICP)
**Status**: AI infrastructure exists (vertexAI.js), needs implementation

```typescript
// In ai.js
export const generate50Tags = async (icp: ICP) => {
  const prompt = `
    Generate 50 content tags for this audience:
    Industry: ${icp.demographics.industry}
    Pain Points: ${icp.pain_points.join(', ')}
    
    Return: {
      pain_point_tags: [],
      channel_tags: [],
      format_tags: [],
      emotional_triggers: []
    }
  `;
  
  return await callVertexAI(prompt);
};
```

**Integration Point**: DailySweep.jsx for daily content recommendations

### Phase 7: Polish & Testing

#### Loading States
**Status**: Basic implementation in hooks  
**Improvement Needed**: Skeleton screens, optimistic updates

```jsx
// Example:
{loading ? (
  <div className="animate-pulse">
    <div className="h-4 bg-neutral-200 rounded w-3/4 mb-2" />
    <div className="h-4 bg-neutral-200 rounded w-1/2" />
  </div>
) : (
  <RealContent data={data} />
)}
```

#### Error Handling
**Status**: Basic try/catch  
**Improvement Needed**: User-friendly error boundaries

```jsx
// Create src/components/ErrorBoundary.jsx
class ErrorBoundary extends React.Component {
  // Catch errors, show friendly message, log to service
}

// Wrap app in Layout.jsx
<ErrorBoundary>
  {children}
</ErrorBoundary>
```

#### End-to-End Testing
**Status**: Not started  
**Tests Needed**:
1. Create ICP → Select Maneuver → Instantiate Move
2. Create Sprint → Add Moves → Check Capacity
3. Progress Move through OODA phases
4. Unlock Capability → Verify Maneuver Unlocks
5. Create Anomaly → Display in Daily Sweep

```javascript
// tests/e2e/move-creation.test.js
describe('Move Creation Flow', () => {
  it('creates move from maneuver', async () => {
    // Navigate to Move Library
    // Click instantiate
    // Verify move created in database
    // Verify appears in War Room
  });
});
```

## Quick Start Guide

### 1. Complete Database Setup (15 min)

```bash
# 1. Create Supabase project
# 2. Run migrations
psql $DATABASE_URL < database/migrations/001_move_system_schema.sql

# 3. Get a workspace UUID
# https://www.uuidgenerator.net/

# 4. Update seed files with your workspace ID
# Replace 'YOUR_WORKSPACE_ID' in seed files

# 5. Run seed data
psql $DATABASE_URL < database/seed-capability-nodes.sql
psql $DATABASE_URL < database/seed-maneuver-types.sql
psql $DATABASE_URL < database/rls-policies.sql
```

### 2. Configure Environment (2 min)

```bash
# Create .env.local
VITE_SUPABASE_URL=https://yourproject.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

### 3. Update Workspace ID in Code (2 min)

```typescript
// src/hooks/useMoveSystem.ts
const getWorkspaceId = (): string => {
  return 'your-workspace-uuid-here';
};
```

### 4. Test Connection (1 min)

```bash
npm run dev
# Navigate to /moves/library
# Should load maneuver types from database
```

### 5. Integrate UI Components (30-60 min per page)

Start with these in order:
1. **MoveLibrary**: Copy from MoveLibraryIntegrated.jsx
2. **Dashboard**: Add real data hooks
3. **TechTree**: Connect unlock functionality
4. **WarRoom**: Connect sprints and moves
5. **MoveDetail**: Make OODA config editable

## File Checklist

### ✅ Complete
- [x] database/migrations/001_move_system_schema.sql
- [x] database/seed-capability-nodes.sql
- [x] database/seed-maneuver-types.sql
- [x] database/rls-policies.sql
- [x] database/DATABASE_SETUP_GUIDE.md
- [x] src/lib/services/icp-service.ts
- [x] src/lib/services/sprint-service.ts
- [x] src/lib/services/analytics-service.ts
- [x] src/lib/services/move-service.ts (updated)
- [x] src/lib/services/tech-tree-service.ts (updated)
- [x] src/hooks/useMoveSystem.ts
- [x] src/pages/MoveLibraryIntegrated.jsx (example)

### ⏳ In Progress
- [ ] src/pages/MoveLibrary.jsx (needs integration)
- [ ] src/pages/WarRoom.jsx (needs integration)
- [ ] src/pages/MoveDetail.jsx (needs integration)
- [ ] src/pages/TechTree.jsx (needs integration)
- [ ] src/pages/Dashboard.jsx (needs integration)

### 📝 To Create
- [ ] src/lib/services/asset-service.ts
- [ ] src/lib/services/quest-service.ts
- [ ] src/lib/services/anomaly-detection-service.ts
- [ ] src/pages/AssetFactory.jsx
- [ ] src/pages/QuestsEnhanced.jsx
- [ ] src/components/ErrorBoundary.jsx
- [ ] tests/e2e/move-creation.test.js

## Estimated Time to Complete

- **Database Setup**: 15-30 minutes (one-time)
- **UI Integration**: 2-4 hours (5 main pages)
- **Missing Features**: 4-8 hours (Asset Factory, Quests, etc.)
- **AI Features**: 2-4 hours (anomaly detection, suggestions)
- **Polish & Testing**: 2-4 hours

**Total**: ~10-20 hours of focused development work

## Success Criteria

- [ ] User can browse maneuvers (locked/unlocked) from database
- [ ] User can create a move and it persists to Supabase
- [ ] User can view moves in War Room with real-time data
- [ ] User can unlock capabilities and see new maneuvers
- [ ] User can progress move through OODA phases
- [ ] Capacity calculations work in real-time
- [ ] Health status indicators update based on metrics
- [ ] Anomalies are detected and displayed

## Support Resources

- **Setup Guide**: `database/DATABASE_SETUP_GUIDE.md`
- **Complete Guide**: `MOVE_SYSTEM_SETUP_COMPLETE.md`
- **Example Integration**: `src/pages/MoveLibraryIntegrated.jsx`
- **Service Docs**: Inline comments in all service files
- **Supabase Docs**: https://supabase.com/docs

## Next Steps

1. **Start with database setup** - Follow DATABASE_SETUP_GUIDE.md
2. **Test services** - Open console, try `moveService.getManeuverTypes()`
3. **Integrate one page** - Start with MoveLibrary using the example
4. **Test end-to-end** - Create a move, add to sprint, view in War Room
5. **Expand from there** - Other pages follow same pattern

The hard work (architecture, services, database) is done. Now it's about connecting the dots!

