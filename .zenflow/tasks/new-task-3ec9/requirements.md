# Product Requirements Document
## Complete RaptorFlow System Integration & Bug Fixes

**Version:** 1.0
**Date:** 2026-01-26
**Status:** Draft
**Priority:** P0 - Critical

---

## Executive Summary

This PRD addresses comprehensive end-to-end system fixes for RaptorFlow, covering the complete user journey from authentication through payment, onboarding, BCM generation, and all core features (news, moves, campaigns, settings, analytics, dashboard). The system must work perfectly as intended with zero errors.

---

## Problem Statement

The current RaptorFlow system has fragmented workflows and integration gaps preventing the complete user journey:

1. **Authentication Flow**: Incomplete user authentication and profile creation
2. **Payment Integration**: PhonePe SDK integration not returning values correctly
3. **Onboarding Process**: Onboarding not completing or generating valid JSON
4. **BCM Generation**: Business Context Manifest not being created from onboarding data
5. **Feature Integration**: Core features not consuming BCM context properly
6. **End-to-End Flow**: No smooth transition from signup → payment → onboarding → active usage

---

## Goals & Success Criteria

### Primary Goals
1. **Seamless Authentication**: User can signup/login via email/password or Google OAuth
2. **Working Payment Flow**: PhonePe SDK initiates payment, processes webhook, and confirms transaction
3. **Complete Onboarding**: All 23 onboarding steps work and generate valid business_context JSON
4. **BCM Creation**: Onboarding JSON is converted to BCM format and stored in memory/DB
5. **Feature Context Awareness**: All features (dashboard, moves, campaigns, analytics, news, settings) consume BCM

### Success Criteria
- ✅ User can register and login without errors
- ✅ Payment initiation returns checkout URL
- ✅ Payment webhook processes and updates user status
- ✅ User is redirected to onboarding after payment
- ✅ All 23 onboarding steps complete successfully
- ✅ Onboarding exports valid business_context.json
- ✅ BCM is generated from onboarding data
- ✅ BCM is stored in Redis (tier0, tier1, tier2) and Supabase
- ✅ Dashboard loads with BCM-aware data
- ✅ Moves feature uses BCM for context
- ✅ Campaigns feature uses BCM for targeting
- ✅ Analytics feature uses BCM for insights
- ✅ News feature filters based on BCM
- ✅ Settings allows BCM refresh/rebuild

---

## User Journey

### Phase 1: Authentication & Registration

**User Story**: As a new user, I want to create an account so that I can access RaptorFlow

**Flow:**
1. User lands on `/login` or `/signup`
2. User can choose:
   - Email/Password signup
   - Google OAuth signup
3. On successful signup:
   - Supabase creates `auth.users` record
   - Database trigger creates `public.users` record with `auth_user_id`
   - Database trigger creates `workspaces` record
   - User profile is linked to workspace
4. User is redirected to `/onboarding/plans`

**Current Issues:**
- Profile creation trigger may fail silently
- Workspace creation not guaranteed
- No error handling for failed profile creation
- OAuth callback doesn't verify profile creation

**Required Fixes:**
- Ensure database triggers are idempotent
- Add profile creation verification in AuthProvider
- Handle edge cases (email verification, duplicate accounts)
- Add retry logic for profile creation
- Verify workspace creation before redirecting

---

### Phase 2: Plan Selection & Payment

**User Story**: As a registered user, I want to select a plan and pay so that I can access premium features

**Flow:**
1. User views available plans on `/onboarding/plans`
2. User selects a plan (Free/Starter/Growth/Enterprise)
3. For paid plans:
   - Frontend calls `/api/payments/v2/initiate`
   - Backend initiates PhonePe payment via SDK
   - User receives `checkout_url`
   - User is redirected to PhonePe payment page
4. User completes payment on PhonePe
5. PhonePe sends webhook to `/api/webhooks/phonepe`
6. Backend:
   - Validates webhook signature
   - Updates `payment_transactions` table
   - Sets user `onboarding_status` = 'payment_confirmed'
   - Activates subscription
   - Sends confirmation email
7. User is redirected to `/onboarding/payment/status`
8. Status page verifies payment and redirects to `/onboarding/session/step/1`

**Current Issues:**
- PhonePe SDK may not return checkout_url correctly
- Webhook validation might fail
- Payment status not updating user properly
- No error recovery if webhook fails
- Frontend doesn't poll payment status
- Missing payment confirmation email

**Required Fixes:**
- Verify PhonePe SDK v2.1.7 integration
- Ensure all environment variables are set correctly
- Add webhook signature validation
- Implement payment status polling on frontend
- Add Supabase RLS bypass for webhook updates (service role key)
- Send email confirmation via Resend
- Add payment retry mechanism
- Handle edge cases (timeout, cancellation, failure)

---

### Phase 3: Onboarding Process

**User Story**: As a paid user, I want to complete onboarding so that the system understands my business

**Flow:**
1. User starts at Step 1: Evidence Vault
2. For each of 23 steps:
   - User uploads documents/URLs (Step 1)
   - Backend processes with SOTA OCR (Step 1)
   - User triggers AI processing (Step 2)
   - Backend uses Titan/LangGraph agents to extract insights
   - Frontend displays results and allows edits
   - User saves step data to Redis session
   - User proceeds to next step
3. Step progression:
   - Step 1: Evidence Vault (file uploads, URL scraping)
   - Step 2: Auto Extraction (Titan Intelligence)
   - Step 3: Contradiction Check
   - Step 4-25: Remaining onboarding steps
4. Final step (Step 25):
   - User clicks "Export & Finalize"
   - Backend calls `/api/v1/onboarding/{session_id}/finalize`
   - Backend aggregates all step data
   - Backend creates `business_context.json`
   - Backend returns JSON to user

**Current Issues:**
- Onboarding steps may not save to Redis properly
- AI processing may fail without error handling
- SOTA OCR service might be unavailable
- Titan Intelligence may timeout
- No progress indicator across steps
- Finalize endpoint doesn't generate proper JSON
- No validation of required fields per step
- Session data may expire before completion

**Required Fixes:**
- Ensure Redis session persistence (TTL = 7 days)
- Add retry logic for AI processing
- Validate OCR service availability on startup
- Add timeout handling for Titan calls (30s max)
- Implement progress bar (% complete)
- Create proper JSON schema for business_context
- Add field validation per step
- Allow session resume if interrupted
- Add save draft functionality per step

---

### Phase 4: BCM Generation

**User Story**: As a system, I want to convert onboarding data to BCM so that all features have business context

**Flow:**
1. After onboarding finalization, backend has `business_context.json`:
   ```json
   {
     "version": "2.0",
     "company_profile": { ... },
     "intelligence": {
       "facts": [ ... ],
       "icps": [ ... ],
       "positioning": { ... }
     },
     "session_id": "...",
     "generated_at": "2026-01-26T..."
   }
   ```
2. Backend calls BCMReducer:
   - Extracts foundation data
   - Extracts ICP data
   - Extracts competitive data
   - Extracts messaging data
   - Compresses to max 1200 tokens
3. Backend creates BCM manifest:
   ```json
   {
     "manifest": {
       "foundation": { ... },
       "icps": [ ... ],
       "competitive": { ... },
       "messaging": { ... },
       "meta": { "source": "onboarding", "token_budget": 1200 }
     },
     "version": 1,
     "checksum": "sha256hash"
   }
   ```
4. Backend stores BCM:
   - Redis tier0 (in-memory cache, 1h TTL)
   - Redis tier1 (persistent cache, 24h TTL)
   - Redis tier2 (cold storage, 7d TTL)
   - Supabase `business_context_manifests` table
5. Backend updates user profile:
   - Set `onboarding_status` = 'active'
   - Set `onboarding_completed_at` = NOW()
6. Backend redirects user to `/dashboard`

**Current Issues:**
- BCMReducer implementation incomplete (only foundation extracted)
- No extraction logic for ICPs, competitive, messaging
- Checksum calculation may be incorrect
- Redis storage might fail silently
- Supabase insert may fail due to RLS policies
- No BCM versioning strategy
- No BCM rebuild capability

**Required Fixes:**
- Implement full BCMReducer extraction methods
- Add proper token counting (tiktoken)
- Ensure compression stays under 1200 tokens
- Add Redis connection pooling
- Use service role key for Supabase inserts
- Implement semantic versioning (major.minor.patch)
- Create `/api/v1/context/rebuild` endpoint
- Add BCM validation before storage
- Handle extraction failures gracefully

---

### Phase 5: Feature Integration with BCM

**User Story**: As an active user, I want all features to understand my business context so that insights are relevant

#### 5.1 Dashboard

**Flow:**
1. User lands on `/dashboard`
2. Dashboard fetches BCM: `GET /api/v1/context/manifest?workspace_id={id}`
3. Dashboard displays:
   - Active moves (from BCM.current_moves)
   - Active campaigns (from BCM.active_campaigns)
   - Metrics (from BCM.kpis)
   - Focus area (from BCM.primary_icp)

**Current Issues:**
- Dashboard doesn't fetch BCM
- Hardcoded metrics instead of BCM-driven
- No connection to actual user data

**Required Fixes:**
- Add BCM fetch in dashboard page
- Use BCM to populate metrics
- Link to real moves/campaigns from Supabase
- Show BCM freshness indicator

#### 5.2 Moves Feature

**Flow:**
1. User creates a move on `/moves`
2. Frontend sends: `POST /api/v1/moves/create` with BCM context
3. Backend enriches move with:
   - Target ICP from BCM
   - Messaging guardrails from BCM
   - Channel recommendations from BCM
4. Move is saved with BCM reference

**Current Issues:**
- Moves don't reference BCM
- No ICP targeting in moves
- No messaging validation

**Required Fixes:**
- Add BCM context to move creation API
- Validate messaging against BCM guardrails
- Suggest channels based on BCM channel mapping
- Store BCM version with move

#### 5.3 Campaigns Feature

**Flow:**
1. User creates campaign on `/campaigns`
2. Frontend sends: `POST /api/v1/campaigns/create` with BCM context
3. Backend enriches campaign with:
   - ICP segmentation from BCM
   - Positioning from BCM
   - Channel mix from BCM
4. Campaign uses BCM for targeting

**Current Issues:**
- Campaigns don't use BCM for targeting
- No ICP-based segmentation
- Hardcoded channel options

**Required Fixes:**
- Add BCM-driven ICP selection
- Use BCM positioning in campaign brief
- Filter channels based on BCM recommendations
- Show BCM context in campaign analytics

#### 5.4 Analytics Feature

**Flow:**
1. User views analytics on `/analytics`
2. Analytics fetches BCM for context
3. Metrics are filtered by:
   - Primary ICP from BCM
   - Active channels from BCM
   - Key messaging themes from BCM

**Current Issues:**
- Analytics not BCM-aware
- Generic metrics not business-specific

**Required Fixes:**
- Fetch BCM in analytics page
- Filter metrics by BCM ICPs
- Show positioning-aligned insights
- Add BCM evolution tracking

#### 5.5 News Feature (If Exists)

**Flow:**
1. User views news on `/news`
2. News is filtered by:
   - Industry from BCM
   - Competitor set from BCM
   - Customer segments from BCM

**Current Issues:**
- No news feature found in codebase

**Required Fixes:**
- Clarify if news feature is required
- If yes: implement news aggregation API
- Filter news by BCM industry/competitors

#### 5.6 Settings Feature

**Flow:**
1. User views settings on `/settings`
2. Settings shows:
   - BCM status (version, last updated)
   - Option to rebuild BCM
   - Option to export BCM
3. User can trigger BCM rebuild:
   - Calls `POST /api/v1/context/rebuild`
   - Shows rebuild progress
   - Updates BCM version

**Current Issues:**
- No BCM management in settings
- No rebuild capability
- No BCM export

**Required Fixes:**
- Add BCM status panel in settings
- Implement BCM rebuild UI
- Add BCM export (JSON download)
- Show BCM version history

---

## Technical Requirements

### Authentication System

**Components:**
- Frontend: `AuthProvider.tsx`, `useAuth` hook
- Backend: `backend/api/v1/auth.py`
- Database: Supabase Auth + `public.users` table

**Requirements:**
1. Email/Password authentication via Supabase Auth
2. Google OAuth via Supabase Auth
3. Profile creation trigger in Supabase
4. Workspace creation trigger in Supabase
5. Session management with JWT tokens
6. Token refresh every 4 minutes
7. Error handling for all auth failures

**Acceptance Criteria:**
- User can signup with email/password
- User can signup with Google
- Profile is created automatically
- Workspace is created automatically
- User is redirected to plans page
- Auth state persists across refreshes
- Logout clears all state

---

### Payment System

**Components:**
- PhonePe SDK v2.1.7 (Python)
- Backend: `backend/api/v1/payments_v2.py`
- Frontend: `/onboarding/payment/page.tsx`
- Webhook: `/api/webhooks/phonepe/route.ts`

**Requirements:**
1. Payment initiation via PhonePe SDK
2. Checkout URL generation
3. Webhook signature validation
4. Payment status updates
5. User status activation
6. Subscription activation
7. Email confirmation

**Environment Variables:**
```env
PHONEPE_CLIENT_ID=your_client_id
PHONEPE_CLIENT_SECRET=your_client_secret
PHONEPE_MERCHANT_ID=MERCHANTXXXXXX
PHONEPE_ENV=UAT
PHONEPE_CLIENT_VERSION=1
PHONEPE_SUCCESS_URL=http://localhost:3000/onboarding/payment/status
PHONEPE_CALLBACK_URL=http://localhost:3000/api/webhooks/phonepe
```

**Acceptance Criteria:**
- Payment initiation returns checkout_url
- User is redirected to PhonePe
- Webhook receives payment confirmation
- Payment status is updated in DB
- User status is activated
- Subscription is activated
- Email is sent to user

---

### Onboarding System

**Components:**
- Frontend: `/onboarding/**/*.tsx`
- Backend: `backend/onboarding_routes.py`, `backend/api/v1/onboarding_v2.py`
- Services: SOTA OCR, Titan Intelligence, LangGraph Agents

**Requirements:**
1. Redis session management (7-day TTL)
2. File upload with SOTA OCR processing
3. URL scraping with Titan Intelligence
4. AI extraction via LangGraph agents
5. Step-by-step data persistence
6. Progress tracking
7. Draft saving
8. Session resume
9. Final JSON export

**Step Schema:**
```typescript
{
  step_id: number,
  step_name: string,
  data: {
    // Step-specific data
  },
  updated_at: string,
  version: number
}
```

**Business Context JSON Schema:**
```json
{
  "version": "2.0",
  "generated_at": "ISO8601",
  "session_id": "uuid",
  "company_profile": {
    "name": "string",
    "industry": "string",
    "stage": "string"
  },
  "intelligence": {
    "evidence_count": number,
    "facts": [
      {
        "id": "string",
        "category": "string",
        "label": "string",
        "value": "string",
        "confidence": number
      }
    ],
    "icps": [ ... ],
    "positioning": { ... },
    "messaging": { ... }
  }
}
```

**Acceptance Criteria:**
- All 23 steps can be completed
- File upload works with OCR
- URL scraping works with Titan
- AI extraction completes without timeout
- Data persists in Redis
- Progress is tracked accurately
- User can save draft and resume
- Final export generates valid JSON

---

### BCM Generation System

**Components:**
- Backend: `backend/integration/bcm_reducer.py`
- Backend: `backend/api/v1/context.py`
- Memory: Redis (tier0, tier1, tier2)
- Storage: Supabase `business_context_manifests`

**Requirements:**
1. Extract foundation data (company, mission, value_prop)
2. Extract ICP data (segments, pain points, buying process)
3. Extract competitive data (category, alternatives, differentiation)
4. Extract messaging data (guardrails, soundbites, hierarchy)
5. Compress to max 1200 tokens
6. Calculate SHA-256 checksum
7. Store in Redis tiers
8. Store in Supabase
9. Support versioning (major.minor.patch)
10. Support rebuild/refresh

**BCM Manifest Schema:**
```json
{
  "manifest": {
    "foundation": {
      "company": "string",
      "mission": "string",
      "value_prop": "string"
    },
    "icps": [
      {
        "segment": "string",
        "pain_points": ["string"],
        "channels": ["string"]
      }
    ],
    "competitive": {
      "category": "string",
      "alternatives": ["string"],
      "differentiation": "string"
    },
    "messaging": {
      "guardrails": ["string"],
      "soundbites": ["string"],
      "hierarchy": { ... }
    },
    "meta": {
      "source": "onboarding",
      "token_budget": 1200
    }
  },
  "version_major": 1,
  "version_minor": 0,
  "version_patch": 0,
  "checksum": "sha256hash",
  "created_at": "ISO8601"
}
```

**Acceptance Criteria:**
- BCM is generated from onboarding JSON
- All sections are extracted correctly
- Token count is under 1200
- Checksum is valid
- BCM is stored in all Redis tiers
- BCM is stored in Supabase
- Version is incremented correctly
- Rebuild endpoint works

---

### Feature BCM Integration

**Components:**
- Dashboard: `src/app/(shell)/dashboard/page.tsx`
- Moves: `src/app/(shell)/moves/page.tsx`
- Campaigns: `src/app/(shell)/campaigns/page.tsx`
- Analytics: `src/app/(shell)/analytics/page.tsx`
- Settings: `src/app/(shell)/settings/page.tsx`

**Requirements:**
1. Fetch BCM on feature load
2. Display BCM freshness indicator
3. Use BCM data to enrich feature
4. Handle missing/stale BCM gracefully
5. Allow BCM refresh from UI

**Acceptance Criteria:**
- Dashboard shows BCM-driven metrics
- Moves use BCM for targeting
- Campaigns use BCM for segmentation
- Analytics filter by BCM context
- Settings allow BCM rebuild

---

## Non-Functional Requirements

### Performance
- Page load < 2s
- API response < 500ms (p95)
- Onboarding step transition < 300ms
- BCM generation < 5s

### Reliability
- 99.9% uptime
- Zero data loss
- Automatic error recovery
- Payment webhook retries (3x)

### Security
- HTTPS only
- JWT token validation
- RLS policies enforced
- Webhook signature validation
- Input sanitization
- XSS protection

### Scalability
- Support 1000+ concurrent users
- Handle 100+ onboarding sessions
- Redis connection pooling
- Database query optimization

---

## Open Questions

1. **News Feature**: Is a news aggregation feature required? Not found in codebase.
2. **BCM Versioning**: Should we support BCM rollback to previous versions?
3. **Payment Plans**: Confirm pricing for Starter/Growth/Enterprise plans.
4. **Email Templates**: Confirm Resend email templates for payment confirmation.
5. **Error Recovery**: Should we support manual intervention for failed payments/onboarding?
6. **Multi-Workspace**: Should a user be able to create multiple workspaces?

---

## Assumptions

1. All environment variables are correctly configured
2. PhonePe credentials are valid for UAT/Production
3. Supabase database has all required tables and triggers
4. Redis is available and persistent
5. SOTA OCR service is running
6. Titan Intelligence service is available
7. LangGraph agents are functional
8. Resend API is configured for emails
9. GCP Vertex AI is accessible for AI processing

---

## Out of Scope

1. Mobile app development
2. Third-party integrations (HubSpot, Salesforce)
3. Multi-language support
4. White-labeling
5. Advanced analytics (ML predictions)
6. Real-time collaboration
7. Custom branding
8. API rate limiting per user

---

## Success Metrics

### User Journey Metrics
- **Signup Completion Rate**: > 90%
- **Payment Success Rate**: > 95%
- **Onboarding Completion Rate**: > 80%
- **BCM Generation Success**: 100%
- **Feature Adoption Rate**: > 70% (within 7 days)

### Technical Metrics
- **API Error Rate**: < 1%
- **Payment Webhook Success**: > 99%
- **Onboarding Step Failure**: < 2%
- **BCM Generation Latency**: < 5s (p95)
- **Dashboard Load Time**: < 2s (p95)

### Business Metrics
- **Time to First Value**: < 20 minutes (signup → dashboard)
- **User Activation Rate**: > 60% (complete onboarding)
- **Feature Usage**: > 3 features used per week
- **BCM Freshness**: < 7 days old (for active users)

---

## Appendix

### A. Database Schema References
- `auth.users` - Supabase Auth
- `public.users` - User profiles
- `public.workspaces` - Workspace management
- `public.payment_transactions` - Payment tracking
- `public.subscriptions` - Subscription management
- `public.business_context_manifests` - BCM storage
- `public.onboarding_sessions` - Onboarding tracking

### B. API Endpoint References
- `POST /api/v1/auth/signup`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/session`
- `POST /api/payments/v2/initiate`
- `GET /api/payments/v2/status/{merchant_order_id}`
- `POST /api/webhooks/phonepe`
- `POST /api/v1/onboarding/{session_id}/vault/upload`
- `POST /api/v1/onboarding/{session_id}/steps/{step_id}/run`
- `POST /api/v1/onboarding/{session_id}/finalize`
- `POST /api/v1/context/rebuild`
- `GET /api/v1/context/manifest`

### C. Environment Variable Checklist
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `PHONEPE_CLIENT_ID`
- `PHONEPE_CLIENT_SECRET`
- `PHONEPE_MERCHANT_ID`
- `PHONEPE_ENV`
- `UPSTASH_REDIS_REST_URL`
- `UPSTASH_REDIS_REST_TOKEN`
- `RESEND_API_KEY`
- `GOOGLE_CLOUD_PROJECT`
- `VERTEX_AI_PROJECT_ID`

---

**End of Requirements Document**
