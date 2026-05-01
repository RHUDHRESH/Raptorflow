# Phase 5 — Content + Artifact Ledger Audit

## Current State Summary

The content/artifact system has a working foundation but significant gaps in renderer coverage, content type naming consistency, and artifact discoverability.

## Frontend Routes

| Route                   | File        | Status                   | Issues                                                                    |
| ----------------------- | ----------- | ------------------------ | ------------------------------------------------------------------------- |
| `/content`              | `page.tsx`  | Uses `contentApi.list()` | Dead filter/export buttons, no search, no source links, basic list layout |
| `/content/[artifactId]` | **MISSING** | No detail route          | Cannot view single artifact                                               |

## Content API (`lib/api.ts`)

| Method               | Endpoint                  | Status                                        |
| -------------------- | ------------------------- | --------------------------------------------- |
| `contentApi.list()`  | `GET /api/v1/content`     | Real, returns `GeneratedContentRecord[]`      |
| `contentApi.get(id)` | `GET /api/v1/content/:id` | Real, returns single `GeneratedContentRecord` |

`GeneratedContentRecord` shape:

- `contentId` — UUID
- `orgId` — UUID
- `campaignId` — optional UUID
- `taskId` — optional UUID
- `contentType` — string (from backend `content_type`)
- `status` — string
- `body` — `Record<string, unknown>`
- `createdAt` — ISO string

## Backend Validation (`crates/http/src/routes/validation.rs`)

**CRITICAL NAMING MISMATCH:**

Backend validators use **underscore** names:

- `hook_set`
- `icp_refined`
- `positioning`
- `offer_design`
- `calendar_plan`
- `council_synthesis`

Frontend registry uses **hyphenated** names:

- `council-synthesis`
- `hook-set`
- `positioning`
- `icp-refined`
- `offer-design`
- `calendar-plan`

**Problem:** When backend stores content with underscore type, frontend registry won't match it. The `UnknownContentRenderer` will show instead.

Also:

- Unknown content types silently pass validation (`_ => return Ok(())`)
- No `campaign-evaluation` or `campaign-move-plan` validators
- No `campaign_evaluation` or `campaign_move_plan` validators

## Renderers (`components/content/`)

| Renderer                     | Content Type          | Status      | Issues                             |
| ---------------------------- | --------------------- | ----------- | ---------------------------------- |
| `CouncilSynthesisRenderer`   | `council-synthesis`   | Exists      | Uses type guards, good             |
| `HookSetRenderer`            | `hook-set`            | Exists      | Uses type guards, good             |
| `PositioningRenderer`        | `positioning`         | Exists      | Uses type guards, good             |
| `IcpRefinedRenderer`         | `icp-refined`         | Exists      | Uses type guards, good             |
| `OfferDesignRenderer`        | `offer-design`        | Exists      | Uses type guards, good             |
| `CalendarPlanRenderer`       | `calendar-plan`       | Exists      | Uses type guards, good             |
| `UnknownContentRenderer`     | fallback              | Exists      | Shows JSON dump                    |
| `CampaignEvaluationRenderer` | `campaign-evaluation` | **MISSING** | Needed for campaign eval artifacts |
| `CampaignMovePlanRenderer`   | `campaign-move-plan`  | **MISSING** | Needed for move plan artifacts     |

## Schema Files (`schemas/content/`)

All schemas use hyphenated filenames but backend validation uses underscore names:

- `hook-set.json` — loaded for `hook_set`
- `icp-refined.json` — loaded for `icp_refined`
- `positioning.json` — loaded for `positioning`
- `offer-design.json` — loaded for `offer_design`
- `calendar-plan.json` — loaded for `calendar_plan`
- `council-synthesis.json` — loaded for `council_synthesis`

## What This PR Will Fix

1. **Add missing renderers** — `CampaignEvaluationRenderer`, `CampaignMovePlanRenderer`
2. **Fix content type naming** — Add underscore aliases to frontend registry, or normalize at boundary
3. **Rebuild content ledger page** — Searchable, filterable, source-linked
4. **Add artifact detail route** — `/content/[artifactId]` using existing `contentApi.get(id)`
5. **Add source links** — Campaign, move, council backlinks
6. **Harden unknown content handling** — Better unknown renderer, no crashes

## What Remains for Later

1. **Backend validation hardening** — Reject unknown types with 422, add campaign-evaluation/move-plan validators
2. **Backend content type normalization** — Standardize on hyphenated or underscore
3. **Search/filter backend** — Current search will be client-side only
4. **Artifact creation from campaign evaluation** — Backend may not auto-create content record
