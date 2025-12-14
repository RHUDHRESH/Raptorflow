# Model Context Protocol (MCP) Providers for RaptorFlow

This reference records the external platforms we treat as MCP resources so the project can surface accurate configuration and authentication details without searching through the archive every time.

Each section links to the primary checklist or docs that describe how credentials are provisioned, what environment variables to set, and what the production behavior depends on.

## Supabase (Database + Auth)
- **Why it matters:** Supabase powers the entire row-level-secure schema, authentication hooks, and profile/payment tables.  It is the glue between the React frontend and the backend services.
- **Key setup steps:** Run `supabase/migrations/001_initial_schema.sql` so the tables, triggers, policies, and indexes from the linter fixes exist (see `SUPABASE_CONFIG_CHECKLIST.md`).  Enable Google OAuth under Authentication ? Providers and add all listed redirect URLs (with and without `www`).
- **Critical env vars:** `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`.  The frontend uses the `VITE_` variants and the backend uses the service role key for elevated access.
- **Post-configuration:** After updating env vars, redeploy Vercel so the frontend picks up the new keys (see `old_docs/VERCEL_DEPLOYMENT.md`), and keep `LOGOUT_URL`/`Site URL` aligned with `https://www.raptorflow.in`.

## Vercel (Frontend Hosting)
- **Why it matters:** Vercel serves the Vite-built frontend. All MCP consumers that call the UI (browser or CLI) expect the project to be live there with the `VITE_` env vars set.
- **Checklist:** Confirm `vercel.json` uses the Vite framework detection, then add every production env var under Dashboard ? Project ? Settings ? Environment Variables (`VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, `VITE_BACKEND_API_URL` when the backend is deployed, `NODE_ENV`, etc.).  Redeploy after changes so the `sitemap` or login flow uses the latest secrets (refer to `SUPABASE_CONFIG_CHECKLIST.md` and `old_docs/VERCEL_DEPLOYMENT.md`).
- **MCP tips:** Provide the Vercel login URL, project name, and env var list to the MCP server so future agents can quickly reference where the frontend lives and what secrets it relies on.

## Google Cloud Run (Backend) + Vertex AI (AI services)
- **Why it matters:** Cloud Run hosts the backend API and is the only place that can safely keep service-role credentials (Supabase, PhonePe, PhonePe webhook secrets, Upstash, Vertex AI). Vertex AI is used by the backend to run Gemini/Claude models through the official SDKs.
- **Key env vars:** `GOOGLE_CLOUD_PROJECT_ID`, `GOOGLE_CLOUD_LOCATION`, `FRONTEND_PUBLIC_URL`, `BACKEND_API_URL` (used in docs as `VITE_BACKEND_API_URL`), plus the Supabase service role key for backend-only queries.  Vertex AI also relies on either Application Default Credentials (`gcloud auth application-default login`) or the `GOOGLE_APPLICATION_CREDENTIALS` file described in `backend/README.md` and `old_docs/docs/IMPLEMENTATION_GUIDE.md`.
- **Deployment notes:** Deploy the backend with `gcloud run deploy raptorflow-backend --region=<region>` and set env vars via `gcloud run services update` (see `old_docs/DEPLOYMENT.md` and `old_docs/PRODUCTION_DEPLOYMENT_PLAN.md`). Once Vercel and Cloud Run share the same domain origin structure and CORS values, MCP consumers can trust the `https://www.raptorflow.in` URLs.

## Additional MCP Resources to Track
1. **Upstash Redis (Queueing + Cache)** – Needed for `job queue` and webhook rate limiting. Env vars: `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`. See `old_docs/UPSTASH_REDIS_SETUP.md` and `ENV_FILE_CONTENTS.md` for how to rotate credentials in production and to confirm the REST API endpoint is reachable from Cloud Run.
2. **PhonePe Payment Gateway (India billing)** – Real payments require `PHONEPE_MERCHANT_ID`, `PHONEPE_SALT_KEY`, `PHONEPE_SALT_INDEX`, and `PHONEPE_ENV`/`VITE_PHONEPE_*`. The frontend and backend expect the same merchant key/salt, so document both `ENV_ANALYSIS_REPORT.md` and `docs/phonepe-integration.md` when adding to MCP.
3. **Vertex AI Models (Gemini + Claude)** – Already configured via `backend/services/vertex_ai_client.ts`. Capture the GCP project, region, and quotas so future MCP reads know which models are allowed and whether Claude (private) or Gemini (public) endpoints are used (see `backend/README.md` and `old_docs/docs/DEPLOYMENT.md`).
4. **PhonePe Autopay (if needed later)** – Additional credentials (`PHONEPE_AUTOPAY_CLIENT_ID`/`SECRET`/`VERSION`) exist in archived docs (`old_docs/docs/PHONEPE_AUTOPAY_INTEGRATION.md`). Track this so MCP can instruct on autopay renewals without exposing secrets in the repo.
5. **Supabase Storage / Functions (future extensions)** – When we add new Supabase Functions or Storage buckets, update this MCP doc with their access URLs and required service roles.

Keeping this MCP registry up to date ensures anyone (or any agent) querying MCP has all the intended providers and knows where to look for credentials and deployment references. If you authenticate Vercel or Google Cloud Run, add their details here and notify the MCP system so it can exchange tokens securely.
