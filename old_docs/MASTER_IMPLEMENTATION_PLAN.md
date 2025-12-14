# RaptorFlow Master Implementation Plan

**Goal**: Production-grade multi-agent marketing OS with 7 Lords, 60+ Sub-Agents, and full frontend integration.
**Target**: Google Cloud Run (Backend) + Vercel (Frontend) + Supabase (DB) + Upstash (Redis)

---

## Phase 2.1: Core Plumbing (Database & Auth) - "The Kernel"

This phase locks the schema and ensures multi-tenancy works perfectly before adding features.

### A. Database Schema (Supabase)
- [x] **Audit**: Verify `profiles` table exists and links to `auth.users`.
- [x] **Audit**: Verify `workspaces` table exists with `owner_id`.
- [x] **Audit**: Verify `workspace_members` table exists with `role` enum.
- [x] **Audit**: Verify `workspace_invites` table exists.
- [x] **RLS Policy**: Enforce `profiles` visibility (self only).
- [x] **RLS Policy**: Enforce `workspaces` visibility (members only).
- [x] **RLS Policy**: Enforce `workspace_members` visibility (workspace peers).
- [x] **Migration**: Create `020_enforce_workspace_rls.sql` to lock these policies.

### B. Backend Workspace API
- [x] **Endpoint**: `GET /api/v1/workspaces` - List user's workspaces.
- [x] **Endpoint**: `POST /api/v1/workspaces` - Create new workspace (transactional with member insert).
- [x] **Endpoint**: `GET /api/v1/workspaces/{id}` - Get details (RLS protected).
- [x] **Endpoint**: `POST /api/v1/workspaces/{id}/invite` - Invite member by email.
- [x] **Middleware**: Ensure `verify_token` correctly populates `request.state.user`.

### C. Frontend Workspace Context
- [x] **Context**: Update `WorkspaceContext.tsx` to fetch real workspaces from API on load.
- [x] **Routing**: Implement `AuthGuard` that redirects to `/login` if no session.
- [x] **Routing**: Implement `WorkspaceGuard` that redirects to `/workspaces/create` if no workspace found.
- [x] **UI**: Create `WorkspaceSelector` component for the sidebar.
- [x] **UI**: Create `CreateWorkspace` page.

---

## Phase 2.2: Agent Infrastructure Standardization

Ensure all 60+ agents speak the same language (RaptorBus) and follow the same rules.

### A. Base Agent Enhancements
- [x] **Event Bus**: Added `publish_event` to `BaseAgent`.
- [x] **Standardization**: Refactored `HookGeneratorAgent` and `AnalyticsAgent`.
- [x] **Refactor**: Update `BlogWriterAgent` to inherit `BaseAgent`.
- [x] **Refactor**: Update `EmailWriterAgent` to inherit `BaseAgent`.
- [x] **Refactor**: Update `IcpBuilderAgent` to inherit `BaseAgent`.
- [x] **Refactor**: Update `CampaignPlannerAgent` to inherit `BaseAgent`.
- [x] **Refactor**: Update `SchedulerAgent` to inherit `BaseAgent`.
- [x] **Validation**: Ensure all agents use `get_correlation_id()` for logs.

### B. Supervisor Hardening
- [x] **Onboarding**: Implemented `OnboardingSupervisor`.
- [x] **Safety**: Implemented `SafetySupervisor`.
- [x] **Content**: Updated `ContentSupervisor` with event publishing.
- [x] **Research**: Review `CustomerIntelligenceSupervisor` for event publishing.
- [x] **Strategy**: Review `StrategySupervisor` for event publishing.
- [x] **Execution**: Review `ExecutionSupervisor` for event publishing.
- [x] **Analytics**: Review `AnalyticsSupervisor` for event publishing.

---

## Phase 2.3: Frontend-Backend Integration (The 7 Lords)

Connect the React dashboards to the FastAPI endpoints via WebSocket and REST.

### A. Architect Lord
- [x] **API Client**: Verify `api/architect.ts` exists and matches backend.
- [x] **Socket**: Verify `useArchitectSocket` hook.
- [x] **UI**: Connect "Create Initiative" form to `POST /lords/architect/initiatives/design`.
- [x] **UI**: Connect "Architecture Diagram" to `GET /lords/architect/architecture/analyze`.

### B. Cognition Lord
- [x] **API Client**: Verify `api/cognition.ts`.
- [x] **Socket**: Verify `useCognitionSocket` hook.
- [x] **UI**: Render "Learning Journal" from `GET /lords/cognition/learning/recent`.
- [x] **UI**: Connect "Make Decision" button to `POST /lords/cognition/decisions/make`.

### C. Strategos Lord
- [x] **API Client**: Verify `api/strategos.ts`.
- [x] **Socket**: Verify `useStrategosSocket` hook.
- [x] **UI**: Connect "Create Plan" wizard to `POST /lords/strategos/plans/create`.
- [x] **UI**: Render Gantt chart from `GET /lords/strategos/plans/{id}`.

### D. Aesthete Lord
- [x] **API Client**: Verify `api/aesthete.ts`.
- [x] **Socket**: Verify `useAestheteSocket` hook.
- [x] **UI**: Connect "Review Content" upload to `POST /lords/aesthete/assess-quality`.
- [x] **UI**: Display "Brand Score" gauge from real-time metrics.

### E. Seer Lord
- [x] **API Client**: Verify `api/seer.ts`.
- [x] **Socket**: Verify `useSeerSocket` hook.
- [x] **UI**: Render trend charts from `GET /lords/seer/predictions`.
- [x] **UI**: Display "Market Threats" list.

### F. Arbiter Lord
- [x] **Dashboard**: `ArbiterDashboard.tsx` scaffolded.
- [x] **API Client**: Create `api/arbiter.ts`.
- [x] **Socket**: Verify `useArbiterSocket` hook.
- [x] **Integration**: Wire `handleRegisterConflict` to API.
- [x] **Integration**: Wire `handleMakeDecision` to API.

### G. Herald Lord
- [x] **Dashboard**: `HeraldDashboard.tsx` scaffolded.
- [x] **API Client**: Create `api/herald.ts`.
- [x] **Socket**: Verify `useHeraldSocket` hook.
- [x] **Integration**: Wire `handleSendMessage` to API.
- [x] **Integration**: Wire `handleScheduleAnnouncement` to API.

---

## Phase 2.4: Production Readiness & DevOps

### A. Configuration
- [x] **Env Validator**: Created `scripts/validate_env.py`.
- [x] **Config**: Verify `backend/core/config.py` `is_production` logic.
- [x] **CORS**: Set `BACKEND_CORS_ORIGINS` to production Vercel domain.

### B. Infrastructure
- [ ] **Supabase**: Enable Point-in-Time Recovery (PITR).
- [x] **Supabase**: Confirm `pgvector` extension is enabled.
- [ ] **Upstash**: Configure eviction policy (volatile-lru).
- [ ] **Vertex AI**: Increase quota for `textembedding-gecko` if needed.

### C. Security
- [ ] **Secrets**: Rotate `SECRET_KEY`.
- [ ] **API Keys**: Restrict Google Maps API key referrer.
- [x] **Headers**: Add security headers (HSTS, X-Frame-Options) in FastAPI middleware.

---

## Phase 2.5: Deployment Execution

### A. Backend (Cloud Run)
1.  Authenticate: `gcloud auth login`
2.  Build: `docker build -f Dockerfile.cloudrun -t gcr.io/...`
3.  Push: `docker push gcr.io/...`
4.  Deploy: `gcloud run deploy ...`
5.  Verify: `curl https://.../health`

### B. Frontend (Vercel)
1.  Env Vars: Set `VITE_BACKEND_API_URL`, `VITE_SUPABASE_URL`, etc.
2.  Build: `vercel build --prod`
3.  Deploy: `vercel deploy --prod`
4.  Verify: Login flow -> Dashboard -> Create Campaign.

---

## Final Sign-off
- [ ] All 7 Lords operational.
- [ ] Agents publishing events to RaptorBus.
- [ ] Multi-tenancy enforced via RLS.
- [ ] Production environment validated.
