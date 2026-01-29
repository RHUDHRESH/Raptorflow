# TODO – Task `new-task-3ec9`

> Updated: 2026-01-29

This file tracks the remaining implementation and verification work. Each item references the relevant files or evidence already in the repo. Check off items in-place as they land.

## Phase 2 – Payments & PhonePe SDK
1. [ ] Re-review `backend/services/payment_service.py` + `backend/services/phonepe_official_gateway.py` to confirm retry logic, subscription activation, idempotent DB updates, and signature validation. Add missing unit tests.
2. [ ] Document PhonePe + Resend environment variables in README/spec; ensure `.env.*` files include required keys (merchant IDs, RESEND API key, FROM email).
3. [ ] Add integration tests for initiation/status/webhook/polling flows.
4. [ ] Create manual test plan for PhonePe sandbox verification.

## Phase 3 – Onboarding System
1. [ ] Implement JSON schema + validator module for business_context with versioning and required fields.
2. [ ] Enhance `backend/redis/session_manager.py` with schema-driven validation, draft markers, TTL refresh, and cleanup job.
3. [ ] Update `backend/api/v1/onboarding.py` finalize endpoint to: aggregate 23 steps, validate schema, call BCM service, update onboarding status, clear Redis.
4. [ ] Apply migration `004_onboarding_status.sql` and backfill existing users.
5. [ ] Add AI timeout handling and per-step validation to onboarding API.
6. [ ] Add tests for session manager, API endpoints, and finalize flow.

## Phase 4 – BCM Generation & Storage
1. [ ] Verify `backend/integration/bcm_reducer.py` includes `_extract_icps`, `_extract_competitive`, `_extract_messaging`, token-budget compression, checksum calculation.
2. [ ] Audit `backend/redis/bcm_storage.py` for tiered storage TTLs, fallback to Supabase, invalidation helpers.
3. [ ] Verify `backend/services/bcm_service.py` methods align with spec (create/store/get/rebuild/validate + semantic versioning).
4. [ ] Verify `backend/api/v1/context.py` offers manifest/rebuild/history/export endpoints with auth + rate limit.
5. [ ] Add tests covering reducer, storage fallbacks, checksums.

## Phase 5 – Feature Integration
1. [ ] Verify `src/stores/bcmStore.ts` is properly wired to BCM API.
2. [ ] Verify `src/lib/bcm-client.ts` client utilities are functional.
3. [ ] Verify `src/components/bcm/*.tsx` components are connected to store/API.
4. [ ] Wire BCM data + guards into Dashboard, Moves, Campaigns, Analytics, Settings pages.
5. [ ] Add freshness indicators and error handling for stale/absent BCM states.
6. [ ] Add component and integration tests for BCM data flows.

## Phase 6 – Testing, Performance & Security
1. [ ] Create environment validation script verifying all required secrets (Supabase, PhonePe, Redis, Vertex AI, Resend).
2. [ ] Apply migrations 001–005 in lower environments and document results.
3. [ ] Create end-to-end journey test (Signup → Payment → Onboarding → BCM → Dashboard).
4. [ ] Design error recovery scenarios and tests (profile retries, webhook delays, Redis failure, AI timeout, BCM rebuild failure).
5. [ ] Run frontend lint/type-check and backend tests; ensure >80% coverage.
6. [ ] Implement performance benchmarks and monitoring.
7. [ ] Run security verification (RLS, webhook signature, rate limits, secret hygiene).
8. [ ] Create deployment/rollback checklist + monitoring alerts.

## Phase 7 – Coordination & Documentation
1. [ ] Assign owners for backend, frontend, QA, and operations.
2. [ ] Create environment matrix documenting all variables per deployment target.
3. [ ] Update plan.md to reflect actual completion status (remove false ✅ marks).
4. [ ] Fix any pre-commit/lint issues preventing clean commits.
5. [ ] Update README with PhonePe integration documentation.
6. [ ] Create final verification report template.

## Immediate Next Steps (Priority Order)
1. **Phase 2 QA** - Complete PhonePe backend/frontend audit and documentation
2. **Phase 3 Schema** - Implement business context JSON schema and validator
3. **Phase 3 Finalize** - Complete onboarding finalize endpoint with BCM integration
4. **Phase 4 Verification** - Audit BCM reducer, storage, service, and API implementations
5. **Phase 5 Integration** - Verify and complete BCM store/components/client wiring
6. **Phase 6 Testing** - Run comprehensive test suite and security verification

## Evidence Links
- Payment page: @src/app/onboarding/payment/page.tsx#1-400
- Session manager: @backend/redis/session_manager.py
- Onboarding API: @backend/api/v1/onboarding.py
- BCM storage: @backend/redis/bcm_storage.py
- BCM service: @backend/services/bcm_service.py
- Context API: @backend/api/v1/context.py
- BCM store: @src/stores/bcmStore.ts
- BCM components: @src/components/bcm/*.tsx
- BCM client: @src/lib/bcm-client.ts
