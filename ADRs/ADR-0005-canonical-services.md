# ADR-0005: Canonical External Services

## Status
Accepted

## Date
2026-02-08

## Context
The Raptorflow backend had accumulated references to multiple conflicting services:
- **Storage**: GCS was "disabled" in env but still present in requirements, settings, and package.json. No Supabase Storage client existed either.
- **Email**: SendGrid in requirements.txt, SMTP fields in settings.py, Resend API key in .env.production — but zero email service code.
- **Redis**: 6+ env var names, 3 different Redis packages (redis, aioredis, upstash-redis), no centralized client.
- **Monitoring**: Sentry configured on frontend, but zero backend initialization.
- **AI**: OpenAI, Anthropic, HuggingFace, and Google all listed as LLM providers in settings — only Google/Vertex AI was ever used.

Environment files were scattered (8 files, contradictory contents) and 166 markdown files cluttered the repo root.

## Decision
Establish exactly **5 canonical external services** and remove all alternatives:

| Service | Provider | Purpose |
|---------|----------|---------|
| Database + Storage | **Supabase** (Postgres + Storage buckets) | All data persistence and file storage |
| AI Inference | **Vertex AI** (Gemini) | LLM generation via `vertex_ai_service.py` |
| Caching + Rate Limiting | **Upstash Redis** (REST API) | BCM cache, session data, rate limits |
| Email | **Resend** | All transactional emails (6 templates) |
| Monitoring | **Sentry** | Error tracking + performance on both frontend and backend |

### Removed
- Google Cloud Storage (GCS) — replaced by Supabase Storage
- Google BigQuery — not used
- Google Secret Manager — not used
- SendGrid — replaced by Resend
- SMTP — replaced by Resend
- OpenAI, Anthropic, HuggingFace SDK — only Vertex AI used
- redis, aioredis packages — using upstash-redis REST client only
- Celery/Kombu — no task queue implemented
- Pandas, NumPy, Playwright, etc. — not used in backend

### Env Consolidation
- Backend: 6 files → 4 (`.env`, `.env.example`, `.env.production`, `.env.test`)
- Root: 2 templates → 1 (`.env.example`)
- All env files follow consistent section format

## Alternatives Considered
1. **Keep GCS for large files, Supabase for small** — rejected: adds complexity for no current need
2. **Keep multi-provider LLM support** — rejected: only Google is used, YAGNI
3. **Keep SendGrid** — rejected: Resend already chosen, has API key, simpler SDK

## Consequences
- Single canonical client per service in `backend/core/` or `backend/services/`
- Settings.py reduced from ~210 fields to ~45
- requirements.txt reduced from 111 lines to 42
- Any future service additions require a new ADR
