# KOA Move System - Implementation Blueprint

## ✅ Phase 1 & 2 Complete

This document outlines what has been implemented and what's next.

## What's Been Created

### 1. TypeScript Type Definitions (`src/types/move-system.ts`)
- Complete type system for all Move System entities
- Includes database row types for Supabase integration
- Type-safe interfaces for:
  - ManeuverType
  - CapabilityNode
  - Move
  - Sprint
  - LineOfOperation
  - MoveAnomaly
  - MoveLog
  - Quest

### 2. Database Schema (`database/migrations/001_move_system_schema.sql`)
- Complete PostgreSQL/Supabase schema
- All tables with proper constraints and indexes
- Foreign key relationships
- JSONB fields for flexible configuration
- Triggers for automatic timestamp updates

### 3. Seed Data
- **Capability Nodes** (`src/lib/seed-data/capability-nodes.ts`)
  - Foundation tier nodes (Analytics Core, ICP Definition, etc.)
  - Traction tier nodes (Lead Magnet, Email Nurture, etc.)
  - Scale tier nodes (Paid Ads, A/B Testing, etc.)
  - Dominance tier nodes (Referral Engine, Predictive Analytics, etc.)

- **Maneuver Types** (`src/lib/seed-data/maneuver-types.ts`)
  - Offensive maneuvers (Authority Sprint, Scarcity Flank, etc.)
  - Defensive maneuvers (Garrison, Win-Back Raid, etc.)
  - Logistical maneuvers (Asset Forge, Content Calendar)
  - Recon maneuvers (Intel Sweep, Competitor Recon)

### 4. Service Layer
- **Tech Tree Service** (`src/lib/services/tech-tree-service.ts`)
  - Capability unlocking logic
  - Dependency checking
  - Auto-unlock functionality
  - Maneuver unlock validation

- **Move Service** (`src/lib/services/move-service.ts`)
  - CRUD operations for Moves
  - Maneuver type queries
  - Anomaly management
  - Logging functionality
  - (Ready for Supabase integration)

### 5. Database Documentation (`database/README.md`)
- Setup instructions
- Migration guide
- Seeding examples
- RLS policy examples
- Troubleshooting guide

## Integration Steps

### Step 1: Set Up Supabase
1. Create a Supabase project
2. Run the migration SQL file
3. Configure environment variables
4. Set up Row Level Security policies

### Step 2: Connect Frontend to Backend
1. Install Supabase client: `npm install @supabase/supabase-js`
2. Create `src/lib/supabase/client.ts` with your credentials
3. Update `move-service.ts` to use actual Supabase queries
4. Replace mock data in components with service calls

### Step 3: Seed Initial Data
1. Create a seeding script
2. Run it to populate maneuver_types and initial capability_nodes
3. Link capability nodes to maneuver types via prerequisites

### Step 4: Update Frontend Components
1. Replace mock data generators with service calls
2. Add loading states
3. Add error handling
4. Implement real-time updates (optional)

## File Structure

```
src/
├── types/
│   └── move-system.ts          # TypeScript type definitions
├── lib/
│   ├── seed-data/
│   │   ├── capability-nodes.ts  # Tech Tree seed data
│   │   └── maneuver-types.ts    # Maneuver template seed data
│   └── services/
│       ├── tech-tree-service.ts # Tech Tree logic
│       └── move-service.ts      # Move CRUD operations
database/
├── migrations/
│   └── 001_move_system_schema.sql  # Database schema
└── README.md                       # Setup documentation
```

## Next Steps (Phase 3+)

### Phase 3: Backend Integration
- [ ] Set up Supabase client configuration
- [ ] Implement actual database queries in services
- [ ] Add authentication and workspace management
- [ ] Set up Row Level Security policies
- [ ] Create seeding scripts

### Phase 4: Real-time Features
- [ ] Supabase real-time subscriptions for Moves
- [ ] Live anomaly detection
- [ ] Auto-unlock capability nodes
- [ ] Sprint capacity tracking

### Phase 5: Advanced Features
- [ ] AI anomaly detection service
- [ ] Automated OODA loop progression
- [ ] Move recommendation engine
- [ ] Performance analytics

## Migration from Mock Data

The existing frontend uses mock data generators in `src/utils/moveSystemTypes.js`. To migrate:

1. **Keep both for now** - The JS file works with existing components
2. **Gradually migrate** - Update components one by one to use the service layer
3. **Type safety** - Import types from `move-system.ts` for better TypeScript support

Example migration:
```typescript
// Old
import { generateMockManeuverTypes } from '../utils/moveSystemTypes'

// New
import { moveService } from '../lib/services/move-service'
const maneuverTypes = await moveService.getManeuverTypes()
```

## Testing

Create test files for:
- `src/lib/services/__tests__/tech-tree-service.test.ts`
- `src/lib/services/__tests__/move-service.test.ts`
- Database integration tests

## Notes

- All database fields use snake_case (PostgreSQL convention)
- Frontend types use camelCase (TypeScript convention)
- Service layer handles the conversion
- JSONB fields allow flexible configuration without schema changes
- Array fields (UUID[]) are used for many-to-many relationships


