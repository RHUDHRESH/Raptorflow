# Spec: Service Integrity & API Key Audit (Chore)

## Overview
This chore is a "deep deep" audit and functional verification of all third-party services and API keys used in RaptorFlow. The goal is to ensure that Vertex AI, Supabase, Redis, Resend, and PhonePe are fully operational and that no hardcoded or missing secrets remain in the environment configuration.

## Functional Requirements
- **Environment Audit:** Scan all `.env` and `.env.*` files against `.env.example` to identify missing or empty variables.
- **Secret Management:** Identify any hardcoded keys that should be migrated to GCP Secret Manager.
- **Service Inference Verification:**
    - **Vertex AI:** Execute a test prompt to ensure Gemini model access is active.
    - **Supabase:** Verify database connectivity and successful authentication.
    - **Redis (Upstash):** Test read/write connectivity and cache purging.
    - **Resend:** Send a test email (or verify API status) to ensure transactional mail is ready.
    - **PhonePe:** Verify integration is set to **Test Mode** and API keys are recognized.

## Acceptance Criteria
- [ ] A comprehensive report of missing or invalid API keys is generated.
- [ ] All required services pass a functional "ping" or "inference" test.
- [ ] PhonePe is explicitly confirmed to be in Test Mode.
- [ ] No critical secrets are found hardcoded in the codebase.
- [ ] The user has updated all identified missing keys and they are verified as working.

## Out of Scope
- Fixing business logic within the services (e.g., rewriting Soundbite Studio prompts).
- Setting up the Native Search Engine (Brave/DDG) as it is already handled.
