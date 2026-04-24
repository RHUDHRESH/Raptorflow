# Roadmap

## Overview

| Phase | Name | Status | Plans |
|-------|------|--------|-------|
| 1 | Frontend Foundation | planned | 0 |

---

## Phase 1: Frontend Foundation

**Status:** planned  
**Goal:** Build the complete RaptorFlow frontend with Charcoal/Ivory design system, all pages wired to real data, and production-grade component library.

### Outcomes

- [ ] Charcoal/Ivory design system implemented as CSS tokens
- [ ] All 31 pages built and wired to TanStack Query hooks
- [ ] Toast notification system
- [ ] Modal/Dialog component
- [ ] Global error/loading/404 states
- [ ] Office canvas with real WebSocket integration
- [ ] AWS Bedrock credentials wired server-side

### Tech Stack

- **Framework:** Next.js 15 (App Router)
- **Styling:** CSS custom properties (no Tailwind per design contract)
- **State:** Zustand + TanStack Query
- **Animation:** GSAP
- **UI Primitives:** Radix + custom components

### Design System

- **Palette:** Charcoal (#2A2529) / Ivory (#F3F0E7) + warm neutrals
- **Typography:** DM Sans (UI) + JetBrains Mono (technical)
- **Spacing:** 4-point scale (4, 8, 12, 16, 20, 24, 32, 40, 48, 64)
- **Radius:** 14px default, 10px small controls
- **Motion:** GSAP-first, functional only

---

## Phase 2: Backend Integration (planned)

Real API wiring, authentication, database integration.

## Phase 3: Office OS (planned)

WebSocket-driven office canvas, agent avatars, nudge system.

## Phase 4: PRL + Council (planned)

Ripple propagation, council deliberation sessions.
