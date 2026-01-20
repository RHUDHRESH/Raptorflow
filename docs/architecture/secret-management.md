# Secret Management Policy

## Overview
RaptorFlow enforces a strict policy of zero hardcoded secrets. All sensitive credentials must be managed via environment variables.

## Secret Storage
- **Development:** Managed via a local `.env` file (git-ignored).
- **Production:** Injected into Cloud Run / Vercel via **GCP Secret Manager**.

## Critical Secrets
The following secrets must NEVER be hardcoded:
- `SUPABASE_URL` & `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY` (High Sensitivity)
- `GOOGLE_APPLICATION_CREDENTIALS` (GCP Service Account)
- `VERTEX_AI_API_KEY` / `GEMINI_API_KEY`
- `PHONEPE_SALT_KEY` & `PHONEPE_MERCHANT_ID`
- `UPSTASH_REDIS_REST_URL` & `UPSTASH_REDIS_REST_TOKEN`

## Enforcement
- **Pre-commit Hooks:** All commits are scanned for sensitive patterns (regex matching for keys/tokens).
- **CI/CD:** Production deployments fail if required environment variables are missing.
- **Audit:** Periodic automated scans of the codebase for potential leaks.
