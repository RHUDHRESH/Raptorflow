# Product Requirements Document (PRD)
## RaptorFlow - Complete System Integration & Deployment

---

## 1. Executive Summary

**Objective**: Fix all broken systems, complete missing integrations, and deliver a fully functional, production-ready RaptorFlow marketing operating system.

**Scope**: End-to-end authentication, payment processing, onboarding, business context management, and all core features (moves, campaigns, calendar, daily wins, blackbox, settings).

**Target Deployment**: Production-ready system on Vercel + Supabase + GCP with PhonePe live payment gateway.

---

## 2. Critical System Requirements

### 2.1 Authentication System
**Current State**: Broken auth flows, inconsistent user identification
**Required State**: Fully functional authentication with proper user identification

**Requirements**:
- Fix Supabase authentication integration
- Implement user identification numbers (auto-generated unique IDs for users)
- Proper session management across frontend and backend
- Auth guards on all protected routes
- Google OAuth + email/password authentication
- Password reset and email verification flows working
- Consistent user ID mapping across `auth.users`, `public.users`, `public.profiles`, and `public.user_profiles` tables

**Success Criteria**:
- User can sign up and receive unique identification number
- User can log in and maintain session
- Protected routes redirect to login when unauthenticated
- User metadata properly synced across all tables

---

### 2.2 Payment System (PhonePe Integration)
**Current State**: Multiple payment gateway implementations, sandbox mode references
**Required State**: Production PhonePe SDK integration, working payment flow

**Requirements**:
- **Production-only PhonePe integration** (NO sandbox mode)
- Use official PhonePe Python SDK v3
- Payment initiation with proper checkout URLs
- Webhook validation and payment confirmation
- Payment status tracking in database
- Integration with subscription plans (Ascent, Glide, Soar)
- Proper error handling and retry mechanisms
- Payment confirmation updates user subscription status
- Transaction logging and audit trails

**Success Criteria**:
- User selects plan and initiates payment
- PhonePe checkout page opens correctly
- Payment completion triggers webhook
- User subscription activated upon successful payment
- Failed payments handled gracefully with retry options
- All payments logged with transaction IDs

---

### 2.3 User Identification System
**Current State**: Missing user identification number generation
**Required State**: Every user gets unique identification number upon creation

**Requirements**:
- Auto-generate unique user identification numbers (format: RF-XXXXXX or similar)
- Store in `user_profiles` or `profiles` table
- Display in user settings/profile
- Use for support and account management
- Ensure uniqueness with database constraints
- Generate on user creation (trigger or function)

**Success Criteria**:
- Every new user automatically gets unique ID
- ID visible in user profile/settings
- ID persists across sessions
- ID used in support tickets and admin operations

---

### 2.4 Onboarding Flow
**Current State**: Partial implementation, not connected to payment flow
**Required State**: Complete onboarding after payment confirmation

**Requirements**:

**Flow**:
1. User signs up → Email verification
2. User selects plan (monthly/yearly) → Payment page
3. Payment confirmation → Redirect to onboarding
4. Onboarding steps (business context collection)
5. Completion → Create workspace → Redirect to dashboard

**Onboarding Steps**:
- Step 1: Company information (name, industry, stage)
- Step 2: Business foundation (mission, vision, positioning)
- Step 3: Target customers (ICP definition)
- Step 4: Market context (competitors, challenges)
- Step 5: Goals and success metrics
- Step 6: Review and confirm

**Technical Requirements**:
- Onboarding state persisted in database
- Resume onboarding if interrupted
- Validation at each step
- Progress indicator
- Skip option for optional fields
- Generate initial business context JSON from onboarding data

**Success Criteria**:
- Payment confirmation automatically triggers onboarding
- User completes all steps
- Workspace created with proper RLS policies
- Business context JSON generated and stored
- User redirected to dashboard with active account

---

### 2.5 Business Context Management (BCM System)
**Current State**: BCM reducer and projector partially implemented
**Required State**: Full business context lifecycle from onboarding to agent usage

**Requirements**:

**Business Context JSON Structure**:
```json
{
  "workspace_id": "uuid",
  "ucid": "unique-context-id",
  "version": 1,
  "foundation": {
    "company_name": "",
    "industry": "",
    "mission": "",
    "vision": "",
    "positioning": ""
  },
  "icps": [
    {
      "id": "uuid",
      "name": "",
      "demographics": {},
      "psychographics": {},
      "pain_points": [],
      "goals": []
    }
  ],
  "competitive": {
    "competitors": [],
    "differentiation": [],
    "market_position": ""
  },
  "messaging": {
    "core_message": "",
    "value_propositions": [],
    "objection_handling": {}
  },
  "meta": {
    "created_at": "timestamp",
    "updated_at": "timestamp",
    "checksum": "sha256"
  }
}
```

**Storage Requirements**:
- Store in Supabase `business_contexts` table (create if missing)
- Implement Row-Level Security (RLS) policies
- Multi-tenant isolation (users only see their own contexts)
- Version tracking for context evolution
- Checksum validation for data integrity

**BCM Context Conversion**:
- Convert business_context.json → BCM format for agent consumption
- Token budget optimization (max 1200 tokens)
- Semantic compression of verbose data
- Cache converted BCM in Redis for performance

**Integration with Agents**:
- Cognitive engine uses BCM for business understanding
- Muse (content generation) uses BCM for context
- All agents access BCM through context builder
- Real-time updates when business context changes

**Success Criteria**:
- Onboarding generates initial business context JSON
- Stored in Supabase with proper RLS
- BCM reducer compresses to optimal format
- Agents receive BCM in their context
- Multi-tenant isolation verified (users can't access other contexts)
- Context updates trigger BCM regeneration

---

### 2.6 Multi-Tenant & RLS Implementation
**Current State**: Partial RLS policies, inconsistent workspace isolation
**Required State**: Complete multi-tenant isolation with comprehensive RLS

**Requirements**:

**Tables Requiring RLS**:
- `workspaces` - Users only access their own workspaces
- `profiles` / `user_profiles` - Users only see their own profile
- `business_contexts` - Workspace-scoped access only
- `foundations` - Workspace-scoped
- `icps` - Workspace-scoped
- `moves` - Workspace-scoped
- `campaigns` - Workspace-scoped
- `daily_wins` - Workspace-scoped
- `user_subscriptions` - User-scoped only
- `subscription_plans` - Public read access

**RLS Policy Requirements**:
- SELECT: Users can only select their own workspace data
- INSERT: Users can only insert into their own workspace
- UPDATE: Users can only update their own workspace data
- DELETE: Users can only delete their own workspace data
- Admin bypass for system operations

**Workspace Isolation**:
- Every user gets a workspace on successful payment + onboarding
- `workspace_id` in user metadata and profiles
- All workspace-scoped queries filter by `workspace_id`
- No cross-workspace data leakage

**Success Criteria**:
- RLS policies applied to all user-scoped tables
- Users cannot query other users' data
- Admin accounts can access all data (for support)
- No SQL injection bypassing RLS
- Performance optimized with proper indexes

---

## 3. Core Feature Requirements

### 3.1 Marketing Moves
**Current State**: API endpoints exist, frontend partially implemented
**Required State**: Fully functional move management system

**Requirements**:
- Create, read, update, delete moves
- Move categories (content, outreach, ads, etc.)
- Status tracking (planned, in_progress, completed, cancelled)
- Link moves to campaigns
- Duration and timeline tracking
- Success metrics and results
- Weekly view of active moves
- Drag-and-drop reordering

**Success Criteria**:
- User creates move with all fields
- Moves display in weekly view
- Status updates persist
- Filtering and search work
- Integration with campaigns

---

### 3.2 Campaigns
**Current State**: Backend API exists, frontend needs completion
**Required State**: Full campaign management with multi-channel support

**Requirements**:
- Campaign creation with goals and budgets
- Multi-channel support (LinkedIn, Email, Social, Ads)
- Campaign status tracking
- Budget allocation and spend tracking
- Performance metrics (CTR, CPL, conversions)
- Link moves to campaigns
- Campaign analytics dashboard

**Success Criteria**:
- User creates campaign with channels
- Moves can be assigned to campaigns
- Performance metrics displayed
- Budget tracking accurate
- Campaign list and detail views work

---

### 3.3 Blackbox (Business Intelligence)
**Current State**: API endpoint exists
**Required State**: Business intelligence dashboard with insights

**Requirements**:
- AI-powered business analysis using BCM
- SWOT analysis generation
- Market insights and trends
- Competitor analysis
- Strategic recommendations
- Integration with cognitive engine

**Success Criteria**:
- Dashboard displays business insights
- AI analysis uses current BCM
- Insights update when context changes
- Visualizations render correctly

---

### 3.4 Calendar
**Current State**: Unknown implementation status
**Required State**: Marketing calendar with move/campaign visualization

**Requirements**:
- Calendar view (month, week, day)
- Display moves and campaigns on timeline
- Drag-and-drop rescheduling
- Color coding by category/status
- Quick add from calendar
- Sync with moves and campaigns

**Success Criteria**:
- Calendar displays scheduled items
- Drag-and-drop updates dates
- Views switch correctly
- Integration with moves/campaigns

---

### 3.5 Settings
**Current State**: Basic settings pages exist
**Required State**: Comprehensive settings management

**Requirements**:
- User profile settings (name, email, avatar)
- Display user identification number
- Workspace settings (name, branding)
- Subscription management (view plan, upgrade/downgrade)
- Billing history
- Team management (if applicable)
- Notification preferences
- Integration settings (APIs, webhooks)

**Success Criteria**:
- User updates profile information
- Subscription details displayed
- Plan upgrades initiate payment flow
- Settings persist across sessions

---

### 3.6 Daily Wins
**Current State**: API endpoint exists
**Required State**: Daily task management and win tracking

**Requirements**:
- Daily task creation and completion
- Win logging with reflection
- Streak tracking
- Daily summary view
- Integration with moves
- Gamification (badges, progress)

**Success Criteria**:
- User adds daily tasks
- Completion tracked
- Wins logged with notes
- Streaks calculated correctly
- Historical view available

---

### 3.7 Checkpoints
**Current State**: Unknown implementation
**Required State**: Milestone and progress tracking

**Requirements**:
- Checkpoint creation for goals
- Progress tracking (0-100%)
- Link to moves and campaigns
- Status updates
- Timeline visualization
- Completion celebration

**Success Criteria**:
- User creates checkpoints
- Progress updates tracked
- Visual progress indicators
- Integration with other features

---

## 4. Technical Architecture Requirements

### 4.1 Frontend (Next.js 14)
**Stack**:
- Next.js 14 with App Router
- TypeScript
- Tailwind CSS v4
- Zustand for state management
- Framer Motion for animations
- Shadcn/ui components

**Requirements**:
- All pages functional with proper routing
- API client with error handling
- Loading states and skeleton screens
- Responsive design (mobile, tablet, desktop)
- Accessibility (WCAG 2.1 AA)
- SEO optimization
- Error boundaries

---

### 4.2 Backend (FastAPI)
**Stack**:
- Python 3.11+
- FastAPI
- Supabase PostgreSQL
- Redis (Upstash)
- Google Cloud Storage
- Vertex AI (Gemini)

**Requirements**:
- RESTful API endpoints for all features
- Authentication middleware
- Request validation (Pydantic)
- Error handling and logging
- Rate limiting
- CORS configuration
- Webhook handling (PhonePe)
- Background jobs (Celery or similar)

---

### 4.3 Database (Supabase PostgreSQL)
**Requirements**:
- Complete schema with all tables
- RLS policies on all user-scoped tables
- Indexes for performance
- Foreign key constraints
- Triggers for automation (timestamps, user creation)
- Functions for complex operations
- Migrations tracked and versioned

---

### 4.4 Storage (Google Cloud Storage)
**Requirements**:
- User file uploads (documents, images)
- Business context JSON storage (backup)
- Asset storage (logos, brand materials)
- Signed URLs for secure access
- Lifecycle policies for old data
- Multi-tenant isolation (workspace-based paths)

---

### 4.5 Redis (Upstash)
**Requirements**:
- Session storage
- BCM cache
- Rate limiting counters
- Real-time feature flags
- Queue management

---

## 5. Deployment Requirements

### 5.1 Vercel Deployment
**Requirements**:
- Next.js frontend deployed to Vercel
- Environment variables configured
- Custom domain (if applicable)
- Preview deployments for testing
- Production deployment with CI/CD

---

### 5.2 Backend Deployment
**Requirements**:
- FastAPI deployed to GCP Cloud Run or similar
- Scalable infrastructure
- Health check endpoints
- Logging and monitoring
- Secret management

---

### 5.3 Monitoring & Observability
**Requirements**:
- Sentry for error tracking
- Application performance monitoring
- Database query performance
- Payment transaction monitoring
- Uptime monitoring
- Alert configuration

---

## 6. Security Requirements

**Requirements**:
- HTTPS everywhere
- Input sanitization and validation
- SQL injection prevention (parameterized queries)
- XSS protection
- CSRF tokens
- Rate limiting on auth endpoints
- Webhook signature validation (PhonePe)
- Secrets in environment variables (no hardcoding)
- Regular security audits
- GDPR compliance for user data

---

## 7. Testing Requirements

**Requirements**:
- Unit tests for critical business logic
- Integration tests for API endpoints
- E2E tests for critical user flows:
  - Sign up → Payment → Onboarding → Dashboard
  - Create move → Assign to campaign → Track progress
  - Settings update → Subscription change
- Payment flow testing (PhonePe sandbox initially, then production)
- RLS policy testing (ensure no data leakage)
- Performance testing (load testing critical endpoints)

---

## 8. Success Metrics

**System Health**:
- 99.9% uptime
- Page load < 2 seconds
- API response time < 500ms (p95)
- Zero critical security vulnerabilities

**User Experience**:
- Sign up to dashboard < 5 minutes
- Payment success rate > 95%
- Onboarding completion rate > 80%
- Feature adoption rate > 60%

**Business Metrics**:
- Successful payment transactions tracked
- Active user retention
- Feature usage analytics
- Support ticket volume

---

## 9. Out of Scope

**Not Included in This Phase**:
- Mobile native apps
- Team collaboration features (multi-user workspaces)
- Advanced integrations (HubSpot, Salesforce)
- White-label/custom branding
- Advanced AI features beyond BCM
- Multi-language support

---

## 10. Assumptions & Dependencies

**Assumptions**:
- PhonePe merchant account approved and credentials available
- Supabase project provisioned
- GCP project with billing enabled
- Vercel account with deployment access
- All API keys and secrets provided

**Dependencies**:
- PhonePe SDK v3 Python package
- Supabase Auth Helpers for Next.js
- Google Cloud Storage client libraries
- Vertex AI access for Gemini

**Risks**:
- PhonePe payment gateway downtime
- Database migration conflicts
- Supabase RLS complexity
- Performance issues with large datasets

---

## 11. User Stories

**Epic 1: User Onboarding**
- As a new user, I want to sign up easily so I can start using RaptorFlow
- As a user, I want to choose a plan that fits my needs
- As a user, I want to pay securely through PhonePe
- As a user, I want to complete onboarding to set up my business context
- As a user, I want my account activated immediately after payment

**Epic 2: Core Features**
- As a user, I want to create marketing moves to plan my activities
- As a user, I want to organize moves into campaigns
- As a user, I want to track daily wins to stay motivated
- As a user, I want to view my marketing calendar
- As a user, I want business insights from the Blackbox

**Epic 3: Account Management**
- As a user, I want to view my subscription details
- As a user, I want to upgrade/downgrade my plan
- As a user, I want to update my profile information
- As a user, I want to see my user identification number

---

## 12. Acceptance Criteria

**System is ready for deployment when**:

✅ Authentication
- User can sign up with email/password and Google OAuth
- User receives unique identification number
- User can log in and maintain session
- Auth guards protect all routes

✅ Payments
- User can select plan and initiate payment
- PhonePe checkout works in production
- Payment confirmation activates subscription
- Failed payments handled gracefully

✅ Onboarding
- User completes onboarding after payment
- Business context JSON generated and stored
- Workspace created with RLS policies
- User redirected to dashboard

✅ Business Context
- BCM stored in Supabase with proper RLS
- Multi-tenant isolation verified
- BCM converted for agent usage
- Context updates reflected in agents

✅ Core Features
- Moves: Create, update, view, delete working
- Campaigns: Full CRUD operations working
- Calendar: Display and interaction working
- Daily Wins: Logging and tracking working
- Blackbox: Insights generation working
- Settings: Profile and subscription management working
- Checkpoints: Progress tracking working

✅ Frontend
- All pages render without errors
- Responsive on mobile/tablet/desktop
- Loading states implemented
- Error handling graceful

✅ Backend
- All API endpoints functional
- Authentication middleware working
- Error logging configured
- Webhooks validated

✅ Database
- All tables created with proper schema
- RLS policies applied and tested
- Indexes optimized for performance
- Multi-tenant isolation verified

✅ Deployment
- Frontend deployed to Vercel
- Backend deployed and accessible
- Environment variables configured
- Monitoring enabled

---

## 13. Timeline & Phases

**Phase 1**: Foundation (Auth + Payments + Onboarding)
**Phase 2**: Business Context & Multi-Tenancy (BCM + RLS)
**Phase 3**: Core Features (Moves, Campaigns, Calendar, Daily Wins, Blackbox, Settings, Checkpoints)
**Phase 4**: Testing & Deployment
**Phase 5**: Monitoring & Optimization

---

## End of Requirements
