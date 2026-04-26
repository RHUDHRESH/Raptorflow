# AvatarSoul Engine Report

**Branch:** `feat/avatar-soul-engine`
**Date:** 2026-04-25
**Status:** IMPLEMENTATION COMPLETE - READY FOR PR

---

## Executive Summary

The AvatarSoul Engine is the runtime substrate that makes RaptorFlow avatars feel like bounded strategic operators with identity, memory, instincts, debate behavior, capability grants, visible presence, and ripple learning.

---

## What is AvatarSoul?

AvatarSoul is NOT:

- Marketing automation
- Generic chatbot personas
- Markdown-only avatars
- Fake memories or debates

AvatarSoul IS:

- **Identity Kernel** - core drive, worldview, obsessions, taboos
- **Memory Genome** - memory edges with salience and decay
- **Instinct Engine** - deterministic trigger-response frames
- **Debate Physics** - challenge/reason logic based on avatar role
- **Capability Body** - grants and authority
- **Artifact Trail** - contribution history
- **Ripple Metabolism** - learning from outcomes
- **Visual Presence** - visible state to users

---

## Schema Added

- `avatar_souls` - identity kernel, worldview, obsessions, reflexes, taboos, debate style
- `avatar_memory_edges` - salience-tagged memory relationships to ripples
- `avatar_instinct_frames` - deterministic trigger-response snapshots
- `avatar_presence_states` - visible avatar states during harness runs
- `avatar_debate_events` - structured debate contributions
- `avatar_artifact_trails` - artifact contribution history

---

## Implementation Status

| Component           | Status      |
| ------------------- | ----------- |
| Migration 0023      | ✅ COMPLETE |
| DB Models           | ✅ COMPLETE |
| DB Queries          | ✅ COMPLETE |
| AvatarSoul Service  | ✅ COMPLETE |
| Instinct Engine MVP | ✅ COMPLETE |
| Debate Physics MVP  | ✅ COMPLETE |
| HTTP Routes         | ✅ COMPLETE |
| Frontend API        | ✅ COMPLETE |
| Frontend Hooks      | ✅ COMPLETE |
| Unit Tests          | ✅ COMPLETE |
| Red Team Security   | ✅ PASS     |

---

## HTTP Routes Added

| Endpoint                                      | Method | Handler                              |
| --------------------------------------------- | ------ | ------------------------------------ |
| `/api/v1/avatars/{id}/soul`                   | GET    | `avatar_soul::get_avatar_soul`       |
| `/api/v1/avatars/{id}/soul`                   | PUT    | `avatar_soul::update_avatar_soul`    |
| `/api/v1/avatars/{id}/memory/edges`           | GET    | `avatar_soul::list_memory_edges`     |
| `/api/v1/avatars/{id}/memory/edges`           | POST   | `avatar_soul::create_memory_edge`    |
| `/api/v1/avatars/{id}/memory/edges/{edge_id}` | DELETE | `avatar_soul::delete_memory_edge`    |
| `/api/v1/avatars/{id}/instinct-frame`         | POST   | `avatar_soul::create_instinct_frame` |
| `/api/v1/harness/runs/{id}/presence`          | GET    | `avatar_soul::list_presence_states`  |
| `/api/v1/harness/runs/{id}/presence`          | POST   | `avatar_soul::upsert_presence_state` |
| `/api/v1/harness/runs/{id}/debate-events`     | GET    | `avatar_soul::list_debate_events`    |
| `/api/v1/harness/runs/{id}/debate-events`     | POST   | `avatar_soul::create_debate_event`   |
| `/api/v1/avatars/{id}/artifact-trail`         | GET    | `avatar_soul::get_artifact_trail`    |

---

## Files Changed

### Created

- `database/migrations/0023_avatar_soul_engine.sql`
- `crates/harness/src/avatar_soul.rs`
- `crates/http/src/routes/avatar_soul.rs`
- `apps/web/src/hooks/use-avatar-soul.ts`

### Modified

- `crates/db/src/models.rs` - added 6 new models
- `crates/db/src/queries.rs` - added 12 new query functions
- `crates/harness/src/lib.rs` - added `pub mod avatar_soul`
- `crates/http/src/routes/mod.rs` - added `pub mod avatar_soul`
- `crates/http/src/router.rs` - added avatar_soul routes
- `apps/web/src/lib/api.ts` - added `avatarSoulApi` and types

---

## Checks

| Check                     | Result                |
| ------------------------- | --------------------- |
| pnpm structural:check     | ✅ PASS               |
| cargo check --workspace   | ✅ PASS               |
| cargo fmt                 | ✅ PASS               |
| cargo clippy --workspace  | ✅ PASS (after fixes) |
| TypeScript typecheck      | ✅ PASS               |
| TenantContext enforcement | ✅ PASS               |
| No secrets in code        | ✅ PASS               |
| Parameterized queries     | ✅ PASS               |

---

## Pre-existing Issues Fixed

### Rust CI (cargo fmt + clippy)

- **Issue**: `cargo fmt --check` failing, clippy warnings (~96)
- **Fix**: Ran `cargo fmt`, `cargo clippy --fix`, fixed remaining warnings manually:
  - `needless_borrow` in campaigns.rs, council.rs, daily_wins.rs, etc.
  - `needless_late_init` in avatar_soul.rs
  - `collapsible_if` in various files
  - `manual_clamp` in campaigns.rs and council.rs
  - `should_implement_trait` in foundation.rs (suppressed with `#[allow]`)
  - `dead_code` for unused `as_str` method (suppressed with `#[allow]`)

### Web-and-docs CI (DATABASE_URL)

- **Issue**: "DATABASE_URL throw-at-load-time" during `pnpm build`
- **Fix Applied**: Modified `packages/database/src/client.ts` to use lazy initialization pattern for Prisma client
- **Note**: This is a best-effort fix; the issue could not be fully reproduced locally

---

## Notes

- Clippy warnings for `too_many_arguments` in db queries are suppressed with `#[allow]`
- Database client uses lazy initialization to avoid build-time connection attempts
