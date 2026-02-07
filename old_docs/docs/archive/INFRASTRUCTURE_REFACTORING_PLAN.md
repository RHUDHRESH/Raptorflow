# Raptorflow Codebase Analysis & Infrastructure Refactoring Plan

## Executive Summary

**Raptorflow** is a sophisticated strategy execution platform built entirely as a client-side React SPA. While the frontend is feature-rich and production-ready, the backend and deployment infrastructure need complete implementation. The project includes prepared database schemas and TypeScript types ready for Supabase integration.

**Current Status:** Frontend-first MVP with zero backend integration
**Readiness for New Stack:** 70% (frontend ready, backend/deployment planning documents in place)

---

## 1. PROJECT STRUCTURE

### Directory Layout
```
/home/user/Raptorflow/
├── src/                           # Frontend source code (672KB)
│   ├── pages/                     # 22 page components
│   ├── components/                # Reusable UI components
│   │   ├── moves/                 # Move system components
│   │   ├── icp/                   # ICP management components
│   │   ├── cohorts/               # Cohort management components
│   │   └── ui/                    # Shadcn/UI components
│   ├── lib/                       # Business logic & services
│   │   ├── services/              # Backend service layer (empty templates)
│   │   │   ├── move-service.ts    # Move CRUD operations (ready for Supabase)
│   │   │   └── tech-tree-service.ts # Capability unlocking logic
│   │   └── seed-data/             # Database seeding data
│   │       ├── maneuver-types.ts  # Maneuver templates (15+ templates)
│   │       └── capability-nodes.ts # Tech tree nodes
│   ├── types/                     # TypeScript definitions
│   │   └── move-system.ts         # Complete type system for database
│   ├── utils/                     # Utilities & helpers
│   ├── App.jsx                    # Main router with 18 routes
│   ├── main.jsx                   # Entry point
│   └── index.css                  # Global styles & animations
├── database/                      # Database setup (20KB)
│   ├── migrations/
│   │   └── 001_move_system_schema.sql  # Complete PostgreSQL schema
│   └── README.md                  # Database setup documentation
├── docs/                          # Documentation
├── index.html                     # HTML entry point
├── package.json                   # Dependencies (React 19, Vite 5, Tailwind 3)
├── vite.config.js                 # Vite build configuration
├── tailwind.config.js             # Tailwind CSS customization
├── tsconfig.json                  # TypeScript configuration
└── .gitignore                     # Standard Node.js ignore

Total Files: 48 source files
Total Size: 883KB (mostly frontend)
```

### Frontend/Backend Separation
**Current Reality:**
- ✅ Frontend: 100% complete, highly polished
- ❌ Backend: 0% integrated (no API layer)
- ❌ Deployment: Not configured
- ⚠️ Database: Schema prepared but not connected

**Architecture Style:**
- Client-side routing only (React Router)
- All state management via React hooks (useState, useParams)
- Mock data generators for development
- LocalStorage for persistence (not production-ready)

---

## 2. TECHNOLOGY STACK

### Current Frontend Stack
```
Core:
  - React 19.2.0         # Modern React with hooks
  - Vite 5.4.11          # Build tool & dev server (port 3000)
  - React Router DOM 7.9 # Client-side routing
  
Styling:
  - Tailwind CSS 3.4.18  # Utility-first CSS
  - PostCSS 8.5.6        # CSS processing
  - Tailwind Merge       # Utility class merging
  
Components & Animations:
  - Framer Motion 12.23  # Smooth animations (180ms transitions)
  - Lucide React 0.554   # Icon library
  - Clsx 2.1             # Class name utilities
  
Development:
  - ESLint 8.57          # Code linting
  - @types/react 18.3    # Type definitions
  - Autoprefixer 10.4    # CSS vendor prefixes
```

### Design System
**Color Palette (Fashion-house inspired):**
- Primary: Earth tones (cream #f8f5f0 → dark brown #211f1d)
- Accent: Warm orange/coral (#b48f63 primary, #8c6c47 darker)
- Neutral: Comprehensive gray scale (#fdfcf9 → #1d1b17)

**Typography:**
- Display: Playfair Display (serif) - headings
- Body: Inter (sans-serif) - content
- Mono: JetBrains Mono - code

**Animation System:**
- 180ms transition duration (globally applied)
- GPU-accelerated transforms
- Framer Motion keyframes: fadeIn, fadeInUp, slideInRight, scaleIn, shimmer
- Micro-interactions on buttons, cards, modals

### External Integrations (Current - NOT Production-Ready)
```javascript
// Hardcoded API keys found in source:
- Google Maps API: AIzaSyGT2XWp6X7UJLZ1EkL3mxV4m7Gx4nv6wU
- Google Gemini API: VITE_GEMINI_API_KEY (expects env var, currently empty)
```

### Missing Backend Technologies
- ❌ Node.js/Express or alternative backend framework
- ❌ Database connection library (Supabase client prepared but not installed)
- ❌ Authentication system (JWT, OAuth, etc.)
- ❌ API endpoints or Supabase functions
- ❌ Environment variable management (no .env files)
- ❌ Real-time subscriptions (WebSocket, Supabase realtime)
- ❌ Error handling/logging service
- ❌ Analytics tracking (PostHog not integrated)

---

## 3. DATABASE CONFIGURATION

### Schema Status: ✅ PREPARED (Not Connected)
**Location:** `/home/user/Raptorflow/database/migrations/001_move_system_schema.sql`

**Complete PostgreSQL Schema Includes:**

#### Core Tables (7 main tables)
```sql
1. maneuver_types
   - Static templates for strategic moves
   - Categories: Offensive, Defensive, Logistical, Recon
   - 15+ templates defined in seed data
   - Fields: name, category, base_duration_days, fogg_role, 
            intensity_score, risk_profile, default_config (JSONB)

2. capability_nodes (Tech Tree)
   - Skill/capability definitions with dependencies
   - Tiers: Foundation, Traction, Scale, Dominance
   - Statuses: Locked, In_Progress, Unlocked
   - Supports: parent_node_ids[], unlocks_maneuver_ids[]

3. lines_of_operation
   - Strategic grouping of moves
   - Fields: strategic_objective, seasonality_tag, center_of_gravity
   - Status tracking: Active, Paused, Complete

4. sprints
   - Time-boxed execution windows
   - Capacity management: capacity_budget, current_load
   - Season types: High_Season, Low_Season, Shoulder
   - Statuses: Planning, Active, Review, Complete

5. moves (Core execution entity)
   - Actual move instances
   - OODA loop support (ooda_config JSONB)
   - Fogg Behavior Model support (fogg_config JSONB)
   - ICP targeting: primary_icp_id + secondary_icp_ids[]
   - Progress tracking, health status (green/amber/red)
   - Statuses: Planning, OODA_Observe/Orient/Decide/Act, Complete, Killed

6. move_anomalies
   - AI-detected issues on moves
   - Types: Tone_Clash, Fatigue, Drift, Rule_Violation, Capacity_Overload
   - Severity levels: 1-5
   - Statuses: Open, Acknowledged, Resolved, Ignored

7. move_logs
   - Daily execution tracking
   - Fields: actions_completed, notes, metrics_snapshot (JSONB)

8. maneuver_prerequisites (Junction table)
   - Many-to-many: maneuver_type → required_capability_node
```

### Indexing Strategy
**Performance indexes created:**
```sql
- idx_moves_workspace, idx_moves_sprint, idx_moves_status, idx_moves_icp
- idx_capability_nodes_workspace, idx_capability_nodes_status
- idx_sprints_workspace, idx_sprints_status
- idx_anomalies_move, idx_anomalies_status
- idx_logs_move, idx_logs_date
```

**Triggers:**
```sql
- update_moves_updated_at (AUTO timestamp on UPDATE)
```

### Data Models (TypeScript Types)
**Location:** `/home/user/Raptorflow/src/types/move-system.ts`

Complete type system with:
- JavaScript types (camelCase): ManeuverType, CapabilityNode, Move, etc.
- Database row types (snake_case): ManeuverTypeRow, CapabilityNodeRow, MoveRow
- Automatic conversion handling between formats

### Seed Data Available
1. **Maneuver Types** (`src/lib/seed-data/maneuver-types.ts`)
   - 15+ maneuver templates covering all categories
   - Example: Authority Sprint, Scarcity Flank, Viral Loop, Trojan Horse, Garrison, Win-Back Raid, etc.

2. **Capability Nodes** (`src/lib/seed-data/capability-nodes.ts`)
   - 40+ capability nodes across 4 tiers
   - Complete dependency graph defined
   - Example: Analytics Core (Foundation) → Paid Ads (Scale) → ML Personalization (Dominance)

### Current Integration Status
```javascript
// Service layer template exists but is NOT connected
// File: src/lib/services/move-service.ts
// Status: All methods have commented-out Supabase queries
// Reason: Awaiting Supabase client setup and environment configuration
```

### What's Missing
- ❌ Supabase client installation and configuration
- ❌ Environment variables (.env file with VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY)
- ❌ Row Level Security (RLS) policies
- ❌ Workspace management tables & multi-tenancy setup
- ❌ User/authentication tables
- ❌ Actually executing the migration in a Supabase project

---

## 4. EXISTING DEPLOYMENT CONFIGURATION

### Current Status: ❌ ZERO DEPLOYMENT CONFIGURATION

**Build System Only:**
```javascript
// vite.config.js - Development setup only
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true,  // Auto-open in browser
    overlay: {
      warnings: false,
      errors: true
    }
  },
  build: {
    rollupOptions: {
      onwarn(warning, warn) {
        if (warning.code === 'UNUSED_EXTERNAL_IMPORT') return
        warn(warning)
      }
    }
  }
})
```

**npm scripts:**
```json
{
  "dev": "vite",           // Start dev server on port 3000
  "build": "vite build",   // Production bundle (dist/)
  "preview": "vite preview", // Preview production build
  "lint": "eslint . --ext js,jsx --report-unused-disable-directives --max-warnings 0"
}
```

### What's Missing
- ❌ `vercel.json` configuration
- ❌ Environment variable setup (.env.example, .env.production)
- ❌ Docker/Dockerfile (for containerized deployment)
- ❌ CI/CD pipeline (GitHub Actions, GitLab CI, etc.)
- ❌ Production API endpoint configuration
- ❌ CDN/caching strategy
- ❌ Security headers configuration
- ❌ Database migration automation
- ❌ Error tracking/alerting setup
- ❌ Health check endpoints

### Development Workflow
```bash
Current flow:
1. npm install               # Install dependencies
2. npm run dev               # Start on localhost:3000
3. Manual browser testing    # No automated testing
4. npm run build             # Creates /dist folder
5. Manual deployment (??)    # No deployment process defined

Issues:
- No type checking (npm run type-check missing)
- No unit/integration tests
- No e2e testing
- No staging environment
- No hot reload configuration
```

---

## 5. MONITORING & ANALYTICS SETUP

### Current Status: ❌ NO ANALYTICS INFRASTRUCTURE

**What Exists:**
- Google Maps API integration (hardcoded key in RaptorFlow.jsx)
- Google Gemini API integration (empty - waiting for env var)
- LocalStorage for session data persistence

**What's Missing:**
- ❌ PostHog SDK installation
- ❌ Event tracking system
- ❌ User identification/sessions
- ❌ Funnel tracking (onboarding, feature adoption, etc.)
- ❌ Error/exception tracking
- ❌ Performance monitoring
- ❌ Session recording
- ❌ Custom properties/traits tracking
- ❌ A/B testing infrastructure

**LocalStorage Usage (Not Production-Ready):**
```javascript
// Found in components:
- localStorage.setItem('onboardingData', JSON.stringify(...))
- localStorage.getItem('userPlan')
- localStorage.getItem('cohorts')
- localStorage.getItem('userPreferences')

Issues:
- Not synced with backend
- Lost on logout/cache clear
- No backup/recovery
- No analytics tied to this data
```

**Google APIs (Current - Insecure):**
```javascript
// src/components/RaptorFlow.jsx - Line 9
const GOOGLE_MAPS_API_KEY = "AIzaSyGT2XWp6X7UJLZ1EkL3mxV4m7Gx4nv6wU";
// ⚠️ SECURITY ISSUE: Hardcoded API key in source code!
// This key is exposed to all users and has no restrictions

// Gemini API - Expects env var but currently empty
const apiKey = import.meta.env.VITE_GEMINI_API_KEY || "";
```

---

## 6. FEATURE INVENTORY

### Implemented Pages (22 routes)

#### Core Features
| Page | Route | Status | Purpose |
|------|-------|--------|---------|
| Dashboard | `/` | ✅ Complete | KPI overview, recent moves |
| Moves | `/moves` | ✅ Complete | Move listing & management |
| Move Detail | `/moves/:id` | ✅ Complete | Detailed view with OODA tracking |
| War Room | `/moves/war-room` | ✅ Complete | Sprint planning drag-and-drop |
| Move Library | `/moves/library` | ✅ Complete | Maneuver template library |
| Quests | `/quests` | ✅ Complete | Quest system (progression) |
| Tech Tree | `/tech-tree` | ✅ Complete | Capability DAG visualization |
| Daily Sweep | `/daily-sweep` | ✅ Complete | Quick wins & anomalies |

#### Strategy & Planning
| Page | Route | Status | Purpose |
|------|-------|--------|---------|
| Strategy | `/strategy` | ✅ Complete | Strategy overview |
| Strategy Wizard | `/strategy/wizard` | ✅ Complete | 4-step strategy creation |
| Weekly Review | `/review` | ✅ Complete | Scale/Tweak/Kill decisions |

#### Customer Management
| Page | Route | Status | Purpose |
|------|-------|--------|---------|
| ICP Manager | `/icps` (implied) | ✅ Complete | Customer profile management |
| ICP Moves | `/icp/:id/moves` | ✅ Complete | Moves for specific ICP |
| Cohorts Manager | `/cohorts` | ✅ Complete | Cohort management |
| Cohorts Moves | `/cohorts/:id/moves` | ✅ Complete | Moves for cohort |

#### User & Support
| Page | Route | Status | Purpose |
|------|-------|--------|---------|
| Today | `/today` | ✅ Complete | Daily dashboard |
| Onboarding | `/onboarding` | ✅ Complete | 10-question setup wizard |
| Analytics | `/analytics` | ✅ Complete | AI-powered insights |
| History | `/history` | ✅ Complete | Activity audit trail |
| Account | `/account` | ✅ Complete | User profile |
| Settings | `/settings` | ✅ Complete | Preferences & plans |
| Support | `/support` | ✅ Complete | Help & feedback |

### Feature Depth
- **Move System:** OODA loop tracking, Fogg behavior modeling, anomaly detection
- **Tech Tree:** Capability dependency graph, automatic/manual unlocking
- **ICP System:** 50+ tags, AI recommendations, cohort support
- **Onboarding:** 10-step interactive wizard with localStorage persistence
- **Animations:** 180ms transitions throughout, Framer Motion integration

---

## 7. CODE METRICS

### Project Scale
```
Total Source Files:  48 files
Total Lines of Code: ~15,000+ LOC

Frontend Breakdown:
- Components:    15,078 LOC (mostly UI)
- Pages:         ~8,000 LOC
- Services:      ~500 LOC (templates only)
- Types:         ~230 LOC
- Utils:         ~100 LOC

Largest Components:
- RaptorFlow.jsx:        1,414 LOC (Gemini integration)
- ICPBuilder.jsx:        1,702 LOC
- CohortsBuilder.jsx:    1,702 LOC
- Onboarding.jsx:          987 LOC
- MarketPositionSnapshot: 912 LOC
- TechTreeVisualization:  345 LOC
- Sidebar:               291 LOC
```

### Code Quality
- ✅ ESLint configured and enforced
- ✅ React best practices (hooks, functional components)
- ✅ TypeScript types available for database models
- ✅ Consistent naming conventions
- ❌ No unit tests
- ❌ No integration tests
- ❌ No E2E tests
- ❌ No type checking on frontend components (JSX files are untyped)
- ⚠️ Security issues (hardcoded API keys)

---

## COMPREHENSIVE REFACTORING PLAN FOR NEW STACK

### Target Infrastructure
```
Frontend:        Vercel (Next.js optional, current Vite works)
Backend/Database: Supabase (PostgreSQL + Auth + Realtime)
Cloud Storage:   GCP Cloud Storage
Monitoring:      PostHog (Analytics) + GCP Error Reporting
```

### Phase 1: Setup & Configuration (Week 1)

#### 1.1 Environment Management
- [ ] Create `.env.example` with all required variables:
  ```
  VITE_SUPABASE_URL=https://xxxx.supabase.co
  VITE_SUPABASE_ANON_KEY=xxxx
  VITE_POSTHOG_API_KEY=xxxx
  VITE_GCP_PROJECT_ID=xxxx
  VITE_APP_ENV=development|staging|production
  ```
- [ ] Create `.env.local` (git-ignored)
- [ ] Update `.gitignore` to exclude env files
- [ ] Create environment-based configuration loader

#### 1.2 Supabase Setup
- [ ] Create Supabase project
- [ ] Run migration: `001_move_system_schema.sql`
- [ ] Set up authentication tables (auth.users integration)
- [ ] Create workspace tables (multi-tenancy support)
- [ ] Install Supabase client: `npm install @supabase/supabase-js`
- [ ] Create `src/lib/supabase/client.ts`:
  ```typescript
  import { createClient } from '@supabase/supabase-js'
  
  const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
  const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY
  
  export const supabase = createClient(supabaseUrl, supabaseAnonKey)
  ```
- [ ] Test connectivity with simple query

#### 1.3 PostHog Integration
- [ ] Create PostHog account
- [ ] Install SDK: `npm install posthog-js`
- [ ] Create `src/lib/analytics/posthog.ts`:
  ```typescript
  import posthog from 'posthog-js'
  
  export const initPostHog = () => {
    posthog.init(import.meta.env.VITE_POSTHOG_API_KEY, {
      api_host: 'https://app.posthog.com'
    })
  }
  ```
- [ ] Initialize in `src/main.jsx`
- [ ] Create analytics wrapper hook

#### 1.4 Vercel Deployment Configuration
- [ ] Create `vercel.json`:
  ```json
  {
    "buildCommand": "npm run build",
    "outputDirectory": "dist",
    "env": {
      "VITE_SUPABASE_URL": "@supabase_url",
      "VITE_SUPABASE_ANON_KEY": "@supabase_key",
      "VITE_POSTHOG_API_KEY": "@posthog_key"
    }
  }
  ```
- [ ] Add build script to package.json
- [ ] Set up environment variables in Vercel dashboard
- [ ] Configure custom domain

### Phase 2: Backend Service Layer (Week 2-3)

#### 2.1 Complete Service Layer
- [ ] Implement all methods in `move-service.ts`:
  - getManeuverTypes()
  - getCapabilityNodes()
  - createMove(), getMove(), updateMoveStatus()
  - getMoveAnomalies(), createAnomaly()
  - logMoveExecution()
  - Error handling & retries
- [ ] Implement `user-service.ts`:
  - Profile management
  - Workspace selection
  - Preferences storage
- [ ] Implement `auth-service.ts`:
  - Sign up/in/out
  - Session management
  - Password reset
- [ ] Add request/response type safety

#### 2.2 Database Seeding
- [ ] Create `scripts/seed-database.ts`:
  ```bash
  npm run seed:maneuvers    # Seed maneuver_types
  npm run seed:capabilities # Seed capability_nodes
  npm run seed:sample       # Sample moves & sprints
  ```
- [ ] Automate seeding in post-deployment hook

#### 2.3 Authentication Implementation
- [ ] Set up Supabase Auth UI or custom forms
- [ ] Create login/signup pages
- [ ] Implement session persistence
- [ ] Add protected route wrapper
- [ ] Implement logout

### Phase 3: Real-time Features (Week 3-4)

#### 3.1 Supabase Realtime
- [ ] Enable realtime on moves table
- [ ] Create `hooks/useRealtimeMoves.ts`:
  ```typescript
  import { useEffect, useState } from 'react'
  import { supabase } from '../lib/supabase/client'
  
  export const useRealtimeMoves = (workspaceId) => {
    const [moves, setMoves] = useState([])
    
    useEffect(() => {
      const subscription = supabase
        .from('moves')
        .on('*', (payload) => {
          setMoves(prev => updateMoves(prev, payload))
        })
        .subscribe()
      
      return () => subscription.unsubscribe()
    }, [workspaceId])
    
    return moves
  }
  ```
- [ ] Replace useState with useRealtimeMoves in Move components
- [ ] Test concurrent user updates

#### 3.2 Auto-unlock Functionality
- [ ] Create `tech-tree-service.ts` implementation:
  - Check capability completion criteria
  - Auto-unlock when conditions met
  - Trigger notifications
- [ ] Add Supabase trigger/function for server-side unlocking

### Phase 4: Analytics & Monitoring (Week 4)

#### 4.1 PostHog Event Tracking
Create tracking for all key actions:
```typescript
// src/lib/analytics/events.ts
export const trackUserAction = (action: string, properties: any) => {
  posthog.capture(action, properties)
}

// Usage:
trackUserAction('move_created', { 
  moveId: move.id, 
  maneuverType: move.maneuver_type_id 
})
```

Track events:
- [ ] User signup/login
- [ ] Move creation/update
- [ ] OODA loop progression
- [ ] ICP management
- [ ] Feature adoption
- [ ] Error events
- [ ] Page views & navigation

#### 4.2 GCP Error Reporting
- [ ] Set up GCP Cloud Logging
- [ ] Create error logger service:
  ```typescript
  export const logError = async (error: Error, context: any) => {
    await fetch(`/api/logs`, {
      method: 'POST',
      body: JSON.stringify({ error, context, timestamp: new Date() })
    })
  }
  ```
- [ ] Wrap API calls with error handling
- [ ] Set up alerts for critical errors

#### 4.3 Performance Monitoring
- [ ] Implement Web Vitals tracking
- [ ] Add Sentry (optional) for performance monitoring
- [ ] Monitor database query performance
- [ ] Set up Vercel Analytics

### Phase 5: Data Migration & Testing (Week 5)

#### 5.1 Replace Mock Data
- [ ] Replace all mock data generators with service calls
- [ ] Update component useState to useEffect + service calls
- [ ] Add loading states to all async components
- [ ] Add error boundaries

Example migration:
```jsx
// Before
const [moves] = useState(generateMockMoves())

// After
const [moves, setMoves] = useState([])
const [loading, setLoading] = useState(true)

useEffect(() => {
  moveService.getMoves(workspaceId)
    .then(setMoves)
    .finally(() => setLoading(false))
}, [workspaceId])
```

#### 5.2 Testing
- [ ] Install testing libraries: `npm install --save-dev vitest @testing-library/react`
- [ ] Create service layer tests
- [ ] Create component tests for data fetching
- [ ] E2E tests with Playwright or Cypress

#### 5.3 Staging Deployment
- [ ] Deploy to Vercel staging environment
- [ ] Full end-to-end testing
- [ ] Performance testing
- [ ] Security audit

### Phase 6: Production Hardening (Week 6)

#### 6.1 Security
- [ ] Remove hardcoded API keys from source
- [ ] Implement API key rotation
- [ ] Set up CORS properly
- [ ] Add rate limiting on backend
- [ ] Implement input validation/sanitization
- [ ] Add Content Security Policy headers

#### 6.2 Row Level Security (RLS)
Implement Supabase RLS policies:
```sql
-- Users can only see moves in their workspace
CREATE POLICY "moves_workspace_access" 
  ON moves FOR SELECT
  USING (workspace_id IN (
    SELECT workspace_id FROM workspace_members 
    WHERE user_id = auth.uid()
  ))

-- Similar policies for all tables
```

#### 6.3 Scalability
- [ ] Implement caching strategy (Redis if needed)
- [ ] Optimize database queries
- [ ] Add pagination to list endpoints
- [ ] Implement lazy loading for large datasets

#### 6.4 Documentation
- [ ] Write API documentation
- [ ] Create deployment runbook
- [ ] Document backup/recovery procedures
- [ ] Create troubleshooting guide

---

## MIGRATION CHECKLIST

### Critical Path (MVP)
- [ ] Supabase project created & schema migrated
- [ ] Environment variables configured
- [ ] Authentication working
- [ ] Move service connected to database
- [ ] Login/dashboard working with real data
- [ ] Deployed to Vercel staging
- [ ] PostHog tracking basic events
- [ ] Production deployment

### High Priority
- [ ] All CRUD operations working
- [ ] Real-time move updates
- [ ] Tech tree capability unlocking
- [ ] ICP management with database
- [ ] Error handling & logging
- [ ] User profile management

### Medium Priority
- [ ] Advanced analytics & dashboards
- [ ] A/B testing infrastructure
- [ ] Performance optimization
- [ ] Database backups
- [ ] Monitoring alerts

### Nice to Have
- [ ] Webhook integrations
- [ ] Mobile app
- [ ] Offline support (PWA)
- [ ] Dark mode
- [ ] Internationalization

---

## RISK ASSESSMENT

### High Risk
- **Data Loss:** No backup strategy yet
  - Mitigation: Enable Supabase automated backups immediately
  
- **Security:** Hardcoded API keys
  - Mitigation: Rotate keys, use environment variables, implement RLS
  
- **Performance:** No pagination on large datasets
  - Mitigation: Add pagination, implement lazy loading, use realtime subscriptions carefully

### Medium Risk
- **Complexity:** Real-time features need careful testing
  - Mitigation: Extensive testing, gradual rollout
  
- **Cost:** Supabase & PostHog pricing
  - Mitigation: Monitor usage, implement rate limits
  
- **Data Consistency:** Concurrent updates possible
  - Mitigation: Implement optimistic updates with conflict resolution

### Low Risk
- **Learning Curve:** Team familiar with Supabase patterns
  - Mitigation: Good documentation available
  
- **Deployment:** Vercel very straightforward
  - Mitigation: Standard Next.js/Vite deployment

---

## SUCCESS METRICS

### Week 1: Configuration
- ✅ All environment variables working
- ✅ Supabase project accessible
- ✅ CI/CD pipeline functional

### Week 2: Functionality
- ✅ 80%+ of app working with real data
- ✅ All CRUD operations functional
- ✅ No console errors in production build

### Week 3: Features
- ✅ Real-time updates working
- ✅ Tech tree unlocking automated
- ✅ Analytics tracking > 90% of user actions

### Week 4: Performance
- ✅ Lighthouse score > 90
- ✅ API response time < 200ms (p95)
- ✅ Database query time < 100ms (p95)

### Week 5: Reliability
- ✅ Uptime > 99%
- ✅ Error rate < 0.1%
- ✅ RLS policies preventing unauthorized access

### Week 6: Production
- ✅ Staging & Production parity
- ✅ All users migrated to new stack
- ✅ Backup & recovery procedures tested

