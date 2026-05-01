# Frontend Phase 3 — Rebuild Office as Command Desk

## Summary

Bombed the existing dark/cyber Office and rebuilt it as a Paper / Amber / Editorial SaaS command desk.

The Office is now the central operating surface of RaptorFlow:

> "The Office — where campaigns become moves."

## Old Office Problems Removed

1. **Full-screen PixiJS canvas** — Removed. No more dark `#08081a` background, fake avatar sprites, or decorative orbs.
2. **Fake "6 council members present"** — Removed. Replaced with real API data.
3. **Fake avatar names** — Cortex, Sentinel, Maven, Oracle, Wraith, Axiom removed. Replaced with canonical roster.
4. **Dead input box** — "Ask your council anything..." that did nothing. Replaced with real Muse command input that routes to `/muse`.
5. **Dark cyber styling** — Entire page now uses Paper/Amber identity via AppPageFrame.
6. **Negative margin sidebar bypass** — Page now properly uses app shell layout.

## New Office Layout

### Header

- Eyebrow: WORKSPACE
- Title: The Office
- Description: Where campaigns become moves.
- Status pill: Online / Unavailable based on real API
- Actions: Open Council War Room, New Campaign

### Morning Briefing

- Real counts from `GET /api/v1/office`:
  - Active Campaigns
  - Active Council Sessions
  - Open Nudges
  - Muse Conversations (7d)

### Campaign Fronts

- Real campaigns from `GET /api/v1/campaigns`
- Shows title, goal, status, move count
- Links to campaign detail

### Council Activity

- Real council sessions from `GET /api/v1/council`
- Shows latest session mode, status
- Link to War Room

### Move Ladder

- Honest empty state: "Move ladder will appear after campaign contract repair"
- No fake data

### Artifact Ledger

- Real content artifacts from `GET /api/v1/content`
- Shows title, type, date
- Links to Content Ledger

### Muse Command

- Real text input
- Submits to `/muse?prompt=<encoded>`
- No dead input

### Right Rail

- **Avatar Roster** — Canonical 7 avatars with honest "unknown" status
- **System Signals** — Office API online/offline, Council active/idle
- **Quick Links** — Campaigns, War Room, Content, Muse, Foundation, Ripples

## APIs Used

| Endpoint                | Data                                                           |
| ----------------------- | -------------------------------------------------------------- |
| `GET /api/v1/office`    | Office state summary (campaigns, council, nudges, muse counts) |
| `GET /api/v1/campaigns` | Campaign fronts list                                           |
| `GET /api/v1/council`   | Council sessions                                               |
| `GET /api/v1/content`   | Content artifacts                                              |

## Unavailable/Missing APIs

- **Rich move ladder** — Campaign contract repair needed. Honest empty state shown.
- **Avatar presence real-time** — WebSocket exists but no per-avatar status endpoint. Shows "unknown" honestly.

## Fake Assumptions Removed

- No fake KPIs
- No fake avatar presence
- No fake "6 council members present"
- No fake snark feed
- No fake event log seeding

## Responsive Behavior

- Mobile: windows stack vertically, rail moves below main content
- Tablet: 2-column grids
- Desktop: full layout with right rail
- Sidebar mobile behavior preserved

## Files Changed

### Created

- `apps/web/src/features/office/types.ts` — Office feature types
- `apps/web/src/features/office/hooks.ts` — TanStack Query hooks
- `apps/web/src/features/office/index.ts` — Barrel export
- `docs/frontend-phase-3-office-audit.md` — Audit documentation

### Rewritten

- `apps/web/src/app/(app)/office/page.tsx` — Full rewrite (479 lines)

### Updated

- `apps/web/src/brand/copy.ts` — Added Office section titles

## Commands Run

| Command                   | Result                    |
| ------------------------- | ------------------------- |
| `pnpm typecheck`          | PASS                      |
| `pnpm lint`               | PASS                      |
| `pnpm structural:check`   | PASS (pre-existing WARNs) |
| `cargo fmt --all --check` | PASS                      |
| `cargo check --workspace` | PASS                      |

## Confirmations

- [x] No fake data added
- [x] No product contracts changed
- [x] No billing/landing work
- [x] No campaign contract repair in this phase
- [x] No force push
- [x] No stale PR merge

## Next Phase Recommendation

**Phase 4: Campaign Contract Repair**

Fix the campaign moves/tasks API so the Move Ladder can show real data. This is a backend-heavy phase.
