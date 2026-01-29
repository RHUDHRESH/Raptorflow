# RaptorFlow System Overview

## Scope
This document provides a concise architecture overview of RaptorFlow’s frontend, backend, authentication, payments, onboarding, BCM (Business Context Manifest), and data storage layers, including request/response flows, ownership, and key API contracts.

## Module Ownership
| Module | Primary Responsibilities | Owner |
| --- | --- | --- |
| Frontend (Next.js) | UI, client-side state, API consumption, routing | Frontend Team |
| Backend API (FastAPI) | REST APIs, orchestration, integrations, validation | Backend Team |
| Auth (Supabase + API auth context) | Identity, profile/workspace resolution, auth context | Platform/Auth Team |
| Payments (PhonePe integration) | Payment initiation, status, refunds, callbacks | Payments Team |
| Onboarding | Step capture, AI-assisted enrichment, data validation | Product/Onboarding Team |
| BCM | Business Context Manifest creation, versioning, retrieval | Intelligence/BCM Team |
| Data Storage | Postgres/Supabase data, Redis cache, file storage | Platform/Data Team |

## System Overview
- **Frontend**: Next.js app that calls FastAPI endpoints and renders the marketing OS experience. The frontend uses typed API clients and gates navigation based on auth and profile checks.【F:README.md†L1-L123】
- **Backend**: FastAPI service hosting versioned API routes (e.g., `backend/api/v1/*`) for auth, onboarding, BCM, payments, and related modules.【F:backend/api/v1/__init__.py†L1-L21】
- **Auth**: Uses Supabase-backed profile/workspace resolution in the auth routes (`/auth`).【F:backend/api/v1/auth.py†L1-L140】
- **Payments**: PhonePe integration exposed via `/api/payments/*` endpoints with initiation/status/refund models.【F:backend/api/v1/payments.py†L1-L140】
- **Onboarding**: Multi-step onboarding flows with AI agents and structured validation, exposed via `/api/v1/onboarding` routes.【F:backend/api/v1/onboarding.py†L1-L120】
- **BCM**: Business Context Manifest creation and retrieval at `/api/v1/bcm/*` endpoints, backed by a Redis + Supabase storage orchestrator.【F:backend/api/v1/bcm_endpoints.py†L1-L120】
- **Data Storage**: Postgres via SQLAlchemy/asyncpg, Redis for session/cache, and Supabase Storage for file handling (OCR uploads, etc.).【F:backend/database.py†L1-L72】【F:backend/api/v1/bcm_endpoints.py†L41-L90】【F:backend/services/storage.py†L1-L110】

## Request/Response Flows
### 1) Authentication + Profile Readiness
1. **Frontend** calls `GET /auth/me` to load the current user session.
2. **Backend** resolves Supabase user context and returns user details.
3. **Frontend** calls `GET /auth/verify-profile` to confirm profile/workspace readiness.
4. **Backend** returns profile/workspace/subscription readiness and frontend gates onboarding/payment accordingly.【F:backend/api/v1/auth.py†L1-L140】

**Response**: `User` object from `/auth/me`, and readiness payload from `/auth/verify-profile` with `profile_exists`, `workspace_exists`, and `needs_payment` flags.【F:backend/api/v1/auth.py†L1-L140】

### 2) Onboarding → BCM Generation
1. **Frontend** posts onboarding steps to `POST /api/v1/onboarding/{session_id}/steps/{step_id}` (or equivalent step endpoints).
2. **Backend** validates and enriches steps using AI agents and stores interim state in Redis.
3. **Frontend** triggers BCM creation via `POST /api/v1/bcm/create` with workspace/user IDs and raw step data.
4. **BCM service** writes the latest BCM to Redis + database (Supabase) and returns the manifest payload for UI usage.【F:backend/api/v1/onboarding.py†L1-L120】【F:backend/api/v1/bcm_endpoints.py†L1-L120】

**Response**: `BCMCreateResponse` including `bcm`, `version`, and storage flags (Redis/DB).【F:backend/api/v1/bcm_endpoints.py†L20-L86】

### 3) Payments (PhonePe)
1. **Frontend** requests `POST /api/payments/initiate` with amount, redirect/callback URLs, and customer info.
2. **Backend** calls the PhonePe SDK gateway, persists a transaction record, and responds with a checkout URL.
3. **Frontend** redirects the user to the hosted checkout page.
4. **Backend** later receives callbacks/webhooks and exposes status endpoints for reconciliation (e.g., `/api/payments/status`).【F:backend/api/v1/payments.py†L1-L140】

**Response**: `PaymentInitiateResponse` with `transaction_id`, `checkout_url`, `status`, and optional `security_metadata`.【F:backend/api/v1/payments.py†L40-L92】

### 4) Data Storage (Files + Metadata)
1. **Frontend** uploads onboarding evidence or assets to storage endpoints.
2. **Backend** validates the file, performs security scanning, and stores it in Supabase Storage.
3. **Backend** returns a public URL and metadata for frontend rendering or downstream processing (OCR, BCM).【F:backend/services/storage.py†L1-L110】

## API Contracts (Key Endpoints)
### Auth
- `GET /auth/me` → `User` object with ID, email, and metadata.【F:backend/api/v1/auth.py†L1-L40】
- `GET /auth/verify-profile` → readiness payload (`profile_exists`, `workspace_exists`, `needs_payment`).【F:backend/api/v1/auth.py†L60-L140】
- `POST /auth/ensure-profile` → `{ workspace_id, subscription_plan, subscription_status }`.【F:backend/api/v1/auth.py†L31-L90】

### Payments
- `POST /api/payments/initiate`
  - **Request**: `amount`, `redirect_url`, `callback_url`, `customer_info` (id, name, email, mobile), optional `metadata`.
  - **Response**: `transaction_id`, `checkout_url`, `status`, `phonepe_transaction_id` (if present).【F:backend/api/v1/payments.py†L33-L92】

### Onboarding
- `POST /api/v1/onboarding/{session_id}/steps/{step_id}` (step ingestion endpoint)
  - **Request**: `StepUpdateRequest` with `data`, `version`, optional `workspace_id`.
  - **Response**: step validation + enrichment payload (varies by route).【F:backend/api/v1/onboarding.py†L90-L118】

### BCM
- `POST /api/v1/bcm/create`
  - **Request**: `workspace_id`, `raw_step_data`, optional `user_id`, `force_rebuild`.
  - **Response**: `BCMCreateResponse` with `bcm`, `version`, storage flags, and token counts.【F:backend/api/v1/bcm_endpoints.py†L20-L86】
- `GET /api/v1/bcm/{workspace_id}`
  - **Response**: `BusinessContextManifest` JSON payload for the workspace.【F:backend/api/v1/bcm_endpoints.py†L96-L134】

### Data Storage
- Storage endpoints are backed by `EnhancedStorageService` which validates files, performs security scans, and returns metadata for persisted assets.【F:backend/services/storage.py†L1-L110】

## Notes
- Route prefixes (e.g., `/auth`, `/api/v1/bcm`) are registered in `backend/api/v1` with FastAPI routers.【F:backend/api/v1/__init__.py†L1-L21】
- For full endpoint lists, see `backend/api/v1/` in the backend service folder.【F:backend/api/v1/__init__.py†L1-L21】
