# Security

## Reporting a vulnerability

**Do not open a public issue for security findings.** Report privately to the maintainers.

If you find a security issue — SQL injection, auth bypass, tenant isolation failure, credential leakage, prompt injection, anything exploitable — report it directly. Include steps to reproduce and a proof of concept if possible.

## Threat model

RaptorFlow's core trust boundaries:

```
Untrusted internet
       │
       ▼
ALB (TLS termination)
       │
       ├── /health              ← public
       ├── /api/v1/webhooks/*  ← signature-verified only
       └── /api/v1/*           ← JWT-verified, tenant-scoped
              │
              └── PostgreSQL RLS (org_id enforcement)
              └── S3 (org-prefixed paths)
              └── AWS Bedrock (AI inference)
```

---

## Implemented controls

### Tenant isolation ✅

Tenant-owned tables carry `org_id` and are covered by PostgreSQL Row Level Security policies against `app.current_org_id()`. New migrations are checked by a database validation test that fails when an `org_id` table is created without `ENABLE ROW LEVEL SECURITY`. Code paths that need database-enforced RLS should use a tenant transaction (`TenantDbPool::begin_for_tenant`) so `app.current_org_id` is scoped to the transaction. S3 paths follow `{bucket}/{org_id}/`.

### JWT authentication ✅

Clerk JWTs are validated on every `/api/v1/*` request via `JwtValidator` using RS256 and Clerk's JWKS endpoint. The `Kid` header is matched to a cached key. Tokens without a valid `org_id` claim are rejected with `403 Forbidden`.

### Webhook signatures ✅

**Clerk:** HMAC-SHA256 verification via `ClerkClient::verify_webhook_signature`.

**Razorpay:** HMAC-SHA256 with constant-time comparison (`diff == 0`) via `RazorpayWebhookRuntime::verify`.

### Secrets ✅

All secrets come from environment variables. In production, `Settings::from_env()` reads from AWS Secrets Manager via ECS task definition injection. No secrets are hardcoded in source.

### CORS (production) ✅

In `APP_ENV=prod`, CORS allows only `RAPTORFLOW_FRONTEND_URL`. In `dev`, `Any` origin is allowed for local development.

### Input validation ✅

UUID path parameters (`session_id`, `conversation_id`, etc.) are parsed with `uuid::Uuid::parse_str`. Invalid UUIDs return `400 Bad Request`. JSON body parsing uses serde with typed structs.

### SQL injection ✅

All queries use sqlx with compile-time query checking. No raw SQL strings. No user input interpolated into queries.

### Audit logging ✅

All mutations write to `audit_logs` with `org_id`, `actor_id`, `operation_type`, `target_type`, and a JSON `payload`.

---

## Known security gaps

These are known gaps in the scaffold. Each requires implementation work before production.

### [HIGH] Clerk webhook — no replay protection

**Finding:** Clerk webhook handler processes `event_id` but does not check for duplicates. A valid signed webhook can be replayed by any party who has captured it.

**Current status:** The handler logs and processes every valid webhook. Replaying the same payload results in duplicate user/membership upserts.

**Remediation:** Before processing, check if `event_id` exists in a processed-events set (PostgreSQL table `clerk_processed_events`). After successful processing, insert the event_id. Reject duplicates with `200 OK` (idempotent).

### [HIGH] Public endpoints — no rate limiting

**Finding:** `/api/v1/webhooks/clerk` and `/api/v1/webhooks/razorpay` have no rate limiting. An attacker with a valid webhook signature could flood either endpoint.

**Current status:** The `RateLimitLayer` exists in `crates/http/src/middleware/rate_limit.rs` but is not applied to public webhook routes.

**Remediation:** Apply `RateLimitLayer::per_ip()` to the public router. Set `requests_per_minute: 60, burst_size: 10`.

### [MEDIUM] Prompt injection — no input sanitisation on AI outputs

**Finding:** User-provided strings (from `muse` prompts, `intel` scraped content, `office` snark messages) are passed directly into AWS Bedrock prompts. No allowlist filtering on the output.

**Current status:** The `voice-compliance.md` prompt contract defines expected output shapes, but the Bedrock client does not validate that model output conforms before storing or acting on it.

**Remediation:** Implement output validation in `crates/aws/src/bedrock.rs` — parse the model's response against the expected schema in `docs/prompt-contracts/`. Reject and retry if the output doesn't conform.

### [MEDIUM] Razorpay — no idempotency on payment processing

**Finding:** Payment-related webhook events (order creation, payment success) can be replayed. The handler upserts state but does not check for a unique `event_id` on payment entities.

**Current status:** `razorpay_webhook` parses and logs events but doesn't persist payment state.

**Remediation:** Add a `razorpay_events` table. Store processed `event_id + event` pairs. Skip processing if the event was already handled.

### [LOW] `Sentry` context not validated in all paths

**Finding:** `tracing` fields (`org_id`, `session_id`) are attached by middleware, but not all handler paths reliably include them. PRL and council paths may log without `org_id`.

**Current status:** The `TraceLayer` in `http/src/middleware/trace.rs` attaches context, but handlers that spawn async tasks may lose the context.

**Remediation:** Audit all handler functions. Ensure `org_id` is on every error log and async span. Add a clippy lint that flags `tracing::info/error!` calls without `org_id` in the fields.

---

## Secure development checklist

Before opening a PR that touches auth, data access, or external calls:

- [ ] New database query — is `org_id` the first filter?
- [ ] New external API call — is the response validated against a schema?
- [ ] New webhook handler — does it check for duplicate `event_id` before processing?
- [ ] New prompt — is user input passed through a structured schema, not raw string interpolation?
- [ ] New environment variable — is it documented in `crates/config/src/lib.rs`?
- [ ] New error path — does it log with `org_id` in the fields?
- [ ] New public endpoint — does it have rate limiting?
- [ ] New secrets handling — does it go through `Settings`, not raw `env::var`?
- [ ] Changed auth/JWT — does `cargo clippy` pass with zero warnings?
