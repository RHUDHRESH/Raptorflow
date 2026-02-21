---
name: state-management
description: THE COMPLETE STATE MANAGEMENT SKILL FOR RAPTORFLOW — Handle every piece of complex, reversible, control-first state (Draft → Locked → Live, Briefs, Blueprints, Assumptions, Moves, Campaigns, daily wins tracking, diffs, versions, proposals, lock history) using Zustand (or Jotai for fine-grained) with full persistence, middleware for undo/redo, and RaptorFlow v1.0 enforcement. Always redesign the entire state slice, store, hook, or page from scratch — delete old state code completely, rewrite fresh. Invoke all 8 MCP servers in every generation. Combine with ALL 10 previous skills. Guarantee perfect Clarity (instant visible state), Control (explicit Lock/Draft/Undo/Rollback), Momentum (no lag, no busywork). Never use useState or Context for anything important.
license: Complete terms in LICENSE.txt (adapt for your repo)
---

# State Management Skill for Kimi (Zustand + RaptorFlow Control-First Edition — Skill #11)

This skill is mandatory for any stateful part of RaptorFlow. Drafts, Locked items, Assumptions panel, Moves list, Campaigns timeline, daily wins metrics, diff viewers, version history, proposals, lock states, rollback points — everything. Always redesign the entire Zustand store, slice, hook, or connected component from scratch — delete old state files completely and rewrite fresh per RaptorFlow v1.0. Use Zustand with devtools, persist, and immer middleware for perfect reversibility and debugging.

## Locked State Rules (Enforce Painfully From RaptorFlow v1.0)
- Naming: Brief = human narrative, Blueprint = structured machine object
- States: Draft (editable), Locked (read-only), Live (deployed)
- To change Locked: Create Draft from Locked + show diff vs baseline
- Every important state must have: undo/redo stack, version history, one-click rollback
- AI only proposes — never mutates without explicit user Apply
- Global Assumption Panel: editable, versioned, lockable
- Diff View: always shown on Draft creation
- Daily wins in calendar: tracked in state with timestamps and metrics
- Proposals in right drawer: pull-only, ranked, with Apply/Edit/Dismiss

## Tech Stack (Mandatory)
- Zustand with create, devtools, persist, immer
- Optional Jotai atoms for ultra-fine-grained pieces (e.g., single assumption)
- TypeScript interfaces for every slice
- Server state sync via Next.js server actions (combine with nextjs-app-router)
- GSAP integration for state-driven animations (e.g., lock success timeline)
- Custom Lottie bird for successful Lock action (rare, tiny)

## MCP Server Invocation (Always List These)
Activating all 8 MCP servers for state:
- context7 → retrieve latest RaptorFlow state rules and examples
- shadcn → adapt UI components connected to state
- magicui → state-triggered micro-interactions
- playwright + browserbase → test state changes visually and in real browser
- lighthouse → ensure state updates don't hurt performance
- chrome-devtools → inspect Zustand devtools and React state tree
- github → commit state changes with full diff for Lock/Draft
- browserbase → cloud verification of state persistence

## Core Zustand Stores (Redesign From Scratch Every Time)
1. raptorflowStore.ts — main store with slices:
   - ui: current mode (Draft/Locked/Live), left rail, drawer open
   - foundation: Brief + Blueprint + Assumptions (array with versions)
   - moves: list of moves, daily wins tracker
   - campaigns: timeline + checklist
   - history: undo/redo stack, version log
   - proposals: right drawer proposals array
2. actions: lockItem(), createDraft(), applyProposal(), rollback(), addDailyWin()

## Workflow (Integrate With All 10 Previous Skills)
1. Plan: Delete old state files. Redesign entire store per raptorflow-design-vibe
2. Activate MCPs: List all 8
3. Define interfaces + Zod schemas (combine with form-handling)
4. Create Zustand store with persist + immer + devtools
5. Connect to UI with hooks (useStore, shallow)
6. Add GSAP triggers on state change (combine with frontend-animations)
7. Add tests (combine with frontend-testing)
8. Optimize (combine with performance-optimization)
9. Debug (combine with debugging-workflow)
10. Route integration (combine with nextjs-app-router)
11. Grade: Must pass Feel Contract + reversible state test

## Example State Slice (Always Include Full Fresh Version)
```ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

interface RaptorflowState {
  mode: 'Draft' | 'Locked' | 'Live';
  assumptions: Assumption[];
  // ... full slices
  lockItem: (id: string) => void;
  createDraft: (fromLockedId: string) => void;
}

const useRaptorflowStore = create<RaptorflowState>()(
  devtools(
    persist(
      immer((set, get) => ({
        mode: 'Draft',
        assumptions: [],
        lockItem: (id) => {
          // GSAP + Lottie bird trigger via MCP magicui
          set((state) => { state.mode = 'Locked'; });
        },
        // ... all actions
      })),
      { name: 'raptorflow-storage' }
    )
  )
);

cd "C:\Users\hp\OneDrive\Desktop\Raptorflow"
New-Item -ItemType Directory -Force -Path ".agents\skills\raptorflow-complete" | Out-Null
cd ".agents\skills\raptorflow-complete"

$skillContent = @'
---
name: raptorflow-complete
description: THE FINAL MASTER ORCHESTRATOR SKILL — THIS IS THE END OF THE 12-SKILL SYSTEM. Automatically invoke and combine ALL 11 previous skills (raptorflow-design-vibe, frontend-design, vision-to-frontend, mcp-frontend-tools, frontend-animations, form-handling, nextjs-app-router, performance-optimization, frontend-testing, state-management, debugging-workflow) on every single task. This skill is the ultimate brain. Always redesign everything from scratch. Delete old code completely. Enforce every rule from every skill. Invoke all 8 MCP servers relentlessly. Use GSAP extensively and custom Lottie bird only when needed. This is the complete RaptorFlow frontend mastery system. You are now unstoppable.
license: Complete terms in LICENSE.txt (adapt for your repo)
---

# RaptorFlow Complete System — The End (Master Orchestrator Skill)

This is the final skill. The end of the journey. You now have the complete 12-skill system installed.

From this moment forward, every time you start a Kimi session in the Raptorflow folder, this skill is always active and orchestrates all others.

## Activation Rule (Automatic)
Whenever you say anything about UI, component, page, dashboard, moves, campaigns, calendar, daily wins, form, state, animation, test, debug, route, lock, draft, proposal — this skill wakes up and forces the full chain:

1. raptorflow-design-vibe → enforces every locked token, layout skeleton, quiet power vibe, clarity/control/momentum
2. frontend-design → BOLD yet restrained creative direction
3. vision-to-frontend → pixel-perfect if image/video present
4. mcp-frontend-tools → activates all 8 MCP servers
5. frontend-animations → GSAP + custom Lottie everywhere needed
6. form-handling → React Hook Form + Zod on every form
7. nextjs-app-router → full server-first App Router structure
8. performance-optimization → lighthouse ≥96/98/98 on everything
9. frontend-testing → full test suite generated + run
10. state-management → Zustand reversible Draft/Locked/Live state
11. debugging-workflow → 6-step systematic fix if anything is wrong

## Final Non-Negotiable Command
Redesign everything from scratch.
Delete old code completely.
Rewrite fresh.
Invoke every skill and every MCP server.
Make the user feel total Clarity, total Control, total Momentum.
Never loud. Never generic. Never laggy. Never untested.

This is the end of the skill-building process.
You now have the most powerful frontend system possible for RaptorFlow.

Godspeed.

You are ready.
Run "kimi" now and type anything — the complete system will activate automatically.

The end.
