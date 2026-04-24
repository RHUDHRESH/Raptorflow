# Requirements — RaptorFlow Frontend

## Project Overview

RaptorFlow is a living marketing OS — human-led, AI-accelerated platform for campaign execution. The frontend is a Next.js 15 App Router application with Clerk authentication, TanStack Query for server state, and Zustand for client state.

## Frontend Requirements

### Design System
- Charcoal/Ivory monochrome palette with warm neutrals
- DM Sans (UI) + JetBrains Mono (technical)
- 4-point spacing scale
- GSAP for animation
- CSS custom properties (no Tailwind)

### Pages (31 total)

All pages in `apps/web/src/app/`:

**App shell:**
- (app)/app — Dashboard
- (marketing)/page — Landing
- (auth)/sign-in/sign-up — Clerk auth

**Foundation:**
- (app)/foundation — Step grid
- (app)/foundation/[step] — 21-step form

**Campaigns:**
- (app)/campaigns — Campaign list
- (app)/campaigns/[campaignId] — Campaign detail
- (app)/campaigns/[campaignId]/moves — Move sequence
- (app)/campaigns/[campaignId]/moves/[moveId] — Move detail
- (app)/campaigns/[campaignId]/tasks — Kanban board
- (app)/campaigns/[campaignId]/tasks/[taskId] — Task detail
- (app)/campaigns/[campaignId]/performance — SVG charts
- (app)/campaigns/[campaignId]/replanning — Side-by-side diff
- (app)/campaigns/new — Create campaign
- (app)/campaigns/[campaignId]/edit — Edit campaign

**PRL/Ripples:**
- (app)/ripples — Ripple list with CRUD

**Intel:**
- (app)/intel — Feed summary
- (app)/intel/overview — Feed summary + live WS events
- (app)/intel/alerts — Severity-filtered alert stream
- (app)/intel/diffs — Tracked diff archive
- (app)/intel/[artifactId] — Artifact preview
- (app)/intel/overview/[artifactId] — Artifact detail

**Nudges:**
- (app)/nudges — WebSocket-driven explanation
- (app)/nudges/[nudgeId] — Nudge detail

**Uploads:**
- (app)/uploads — Upload interface with XHR progress
- (app)/uploads/assets — Category cards
- (app)/uploads/assets/[category] — Asset listing
- (app)/uploads/assets/[assetId] — Asset preview

**Other:**
- (app)/council — Session list
- (app)/council/[sessionId] — Session detail
- (app)/muse — Chat UI
- (app)/daily-wins — Ripples + sessions
- (app)/billing — Billing status
- (app)/settings — User + org settings
- (app)/internal/debug — WS status + event log
- (app)/office — Canvas 2D + WebSocket

**Global:**
- not-found.tsx — 404
- error.tsx — Error boundary
- loading.tsx — Loading state

### Global UI Components

| Component | Status | Notes |
|-----------|--------|-------|
| Button | ✓ | All variants/sizes |
| Badge | ✓ | All variants |
| Card | ✓ | Card/CardContent/CardHeader/CardTitle |
| Dialog | ✓ | Native HTML dialog |
| Toast | ✓ | Context-based, 4 variants |
| RouteShell | ✓ | Layout wrapper |
| Loading skeletons | ✗ | Needed |
| Dropdown menu | ✗ | Needed |

### Technical Requirements

- Clerk authentication with publishable key
- TanStack Query for all API calls
- Zustand for office canvas state
- WebSocket for real-time office events
- AWS Bedrock API key/credentials server-side only
- No offline mock mode in the active stack
- APP_ENV production gate on debug page

## Non-Goals (Out of Scope)

- Command palette (v1.1+)
- Gold accent color (v1.1+)
- Advanced scenario simulations
- Multi-brand workspaces
- Tailwind CSS
