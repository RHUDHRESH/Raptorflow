# ADR-0003: Consolidate Environment Variable Configuration

## Status
Accepted

## Date
2026-02-07

## Context

The repo contained **5 env template/example files** with overlapping and conflicting keys:

| File | Lines | Issues |
|------|-------|--------|
| `.env.example` | 64 | `NEXT_PUBLIC_API_URL=http://localhost:3001` (wrong port — backend runs on 8000) |
| `.env.template` | 58 | Adds `REDIS_URL`, `UPSTASH_API_KEY`, `MODEL_GENERAL` not in `.env.example` |
| `env.example` | 39 | Uses `GCP_PROJECT_ID` and `RF_INTERNAL_KEY` not in other files; `NEXT_PUBLIC_API_URL=http://localhost:8000` (correct) |
| `.env.universal-gemini` | 165 | Adds AWS keys, `JWT_SECRET`, `SESSION_SECRET`, deprecated `PHONEPE_SALT_KEY` |
| `.env.production` | 27 | **Contains real secrets** (Supabase keys, Redis tokens, API keys) committed to repo |

Key conflicts:
- `NEXT_PUBLIC_API_URL`: `3001` vs `8000` — backend actually runs on `8000`
- Redis: `UPSTASH_REDIS_*` vs `REDIS_URL` vs `UPSTASH_API_KEY` — 6 different key names across files
- GCP: `GOOGLE_CLOUD_PROJECT` vs `GCP_PROJECT_ID` vs `GOOGLE_PROJECT_ID` — 3 names for the same value
- Internal auth: `INTERNAL_API_TOKEN` vs `RF_INTERNAL_KEY` — two different keys for two different purposes (not documented)

## Decision

**Single `.env.example` at repo root** is the authoritative template.

Update (Reconstruction Mode):
- `.env.production` contained real secrets and was removed from the working tree. Secrets must be rotated and the file purged from git history.
- `INTERNAL_API_TOKEN` was removed (no internal header auth in reconstruction mode).

### Changes

1. `.env.example` is rewritten as the single source of truth with:
   - `[FE]`/`[BE]`/`[BOTH]` annotations showing which layer consumes each variable
   - Correct default values (e.g., `NEXT_PUBLIC_API_URL=http://localhost:8000`)
   - All Redis key variants documented with their purpose
   - Deprecated keys commented out with explanation

2. `.env.template` — to be deleted (superseded by `.env.example`)
3. `env.example` — to be deleted (superseded by `.env.example`)
4. `.env.universal-gemini` — to be deleted (model config belongs in `backend/config/settings.py`)
5. `.env.production` — **MUST be removed from git history** (contains real secrets). Add to `.gitignore`.

### Backward compatibility

The backend `Settings` class (`backend/config/settings.py`) already uses `pydantic_settings` with `extra = "ignore"`, so old env files with extra keys won't break. The `redis_url` property already falls back through `REDIS_URL → UPSTASH_REDIS_URL → UPSTASH_REDIS_REST_URL`.

## Alternatives Considered

1. **Keep multiple env files for different environments** — rejected; the files were not environment-specific but rather duplicates with drift.
2. **Use a `.env.schema` validation tool** — considered for future; not needed now since `pydantic_settings` validates at startup.

## Consequences

- Developers copy one file instead of guessing which of 5 templates to use.
- Port mismatch (`3001` vs `8000`) is resolved.
- Real secrets in `.env.production` must be rotated after removal from git history.
- `.env.template`, `env.example`, `.env.universal-gemini` are deleted.
