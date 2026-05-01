# Phase 3 Office Audit

## Current Office Route Structure

- `/office` — Renders a full-screen PixiJS canvas with fake avatar sprites
- The page is NOT using the app shell layout (bypasses sidebar via negative margin)
- Background is hardcoded `#08081a` (dark cyber)

## Current Components

### Active (in use):

- `OfficeCanvas.tsx` — PixiJS canvas with 6 fake avatars (Cortex, Sentinel, Maven, Oracle, Wraith, Axiom)
- `office-shell.tsx` — Alternative shell with tabs (Floor Plan, Event Trail, Agent Roster), uses office API
- `office-mini-strip.tsx` — Sidebar mini strip (keep)

### PixiJS canvas files (to remove/demote):

- `AvatarSprite.ts` — Fake avatar sprites
- `ConnectionWeb.ts` — Fake connection lines
- `AmbientOrbs.ts` — Decorative orbs
- `OfficeErrorBoundary.tsx` — Canvas error boundary

### Legacy/unused:

- `office-canvas.tsx` — Old canvas variant
- `office-agent-panel.tsx` — Agent panel
- `office-nudge-panel.tsx` — Nudge panel

## Fake Data Found

1. **"6 council members present"** — Hardcoded text in `page.tsx`
2. **Fake avatar names**: Cortex, Sentinel, Maven, Oracle, Wraith, Axiom
3. **Fake avatar colors**: Hardcoded hex colors
4. **"Ask your council anything..."** — Dead input box (does nothing)
5. **OfficeCanvas** — Entirely decorative, no real data

## Real Data Available

### Backend endpoint: `GET /api/v1/office`

Returns:

- `active_campaigns` (real SQL count)
- `active_council_sessions` (real SQL count)
- `open_nudges` (real SQL count)
- `recent_muse_conversations` (real SQL count, last 7 days)
- `event_types` (static list)
- `updated_at`

### Frontend API: `officeApi.getState()`

Already exists in `lib/api.ts:774`

### WebSocket: `/api/v1/office/ws`

Real WebSocket endpoint exists but frontend socket hook may be stale.

## Office Store (`state/office-store.ts`)

Contains:

- `agentStatuses` — keyed by fake AgentKey
- `snarkFeed` — fake chat lines
- `eventLog` — event log (used by sidebar mini-strip)
- `connectionStatus` — websocket connection

The store is used by `office-mini-strip.tsx` which appears in the sidebar. Do not break it.

## What Will Be Removed

1. PixiJS canvas and all related files
2. Fake avatar sprites
3. Fake "6 council members present" text
4. Dead input box
5. Dark `#08081a` background

## What Will Be Rebuilt

1. `/office/page.tsx` — Full rewrite using AppPageFrame
2. Morning Briefing window — real API data
3. Campaign fronts — link to campaigns
4. Council activity — link to council
5. Muse command — real input that routes to /muse
6. Avatar roster — canonical names only, honest status
7. Quick links rail

## APIs Used

- `GET /api/v1/office` — Office state summary
- Campaigns list API (if available via existing hooks)
- Council sessions API (if available)
- Content API (for artifact ledger)

## Missing APIs (documented, not faked)

- Rich campaign move ladder — may need campaign contract repair
- Avatar presence real-time — websocket exists but may not expose per-avatar status
- Artifact ledger — content API exists but may not have "recent artifacts" endpoint
