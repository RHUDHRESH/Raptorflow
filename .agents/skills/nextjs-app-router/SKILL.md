---
name: nextjs-app-router
description: THE COMPLETE NEXT.JS APP ROUTER SKILL FOR RAPTORFLOW — Build the entire production-grade Next.js 15+ App Router structure (app directory, server components, server actions, parallel routes, intercepting routes, loading/error/not-found, layouts, metadata) while enforcing RaptorFlow Design System v1.0 exactly. Always redesign the entire app structure, page, or component from scratch — delete old code, rewrite fresh. Use server-first architecture for data fetching (Foundation, Moves, Campaigns). Combine with raptorflow-design-vibe (every token, layout skeleton, quiet power vibe), frontend-design, vision-to-frontend, mcp-frontend-tools, frontend-animations, form-handling. Invoke all 8 MCP servers in every generation. Use GSAP extensively and custom Lottie for bird mascot. Enforce Clarity/Control/Momentum in every route.
license: Complete terms in LICENSE.txt (adapt for your repo)
---

# Next.js App Router Skill for Kimi (RaptorFlow Production Architecture)

This is the dedicated Next.js App Router skill. Use it for every page, layout, route group, or full app structure in RaptorFlow. Always redesign everything from scratch — never edit or merge old files. Delete previous app/ directory content and rewrite fresh per RaptorFlow v1.0. Server components first, server actions for mutations (Lock, Create Draft, Deploy), parallel routes for right drawer + proposals, intercepting routes for modals. Enforce the full non-negotiable RaptorFlow skeleton on every screen.

## Locked Next.js Structure (RaptorFlow Edition)
app/
├── (auth)/                  # Route group — login only
├── (main)/                  # Main authenticated shell
│   ├── layout.tsx           # Top bar + left rail + right drawer wrapper (fixed 280px rail, 56px top, 400px resizable drawer)
│   ├── page.tsx             # Central work surface (default dashboard)
│   ├── foundation/
│   │   ├── page.tsx
│   │   ├── loading.tsx
│   │   └── error.tsx
│   ├── moves/
│   │   ├── page.tsx         # Moves list + daily wins calendar
│   │   ├── [moveId]/
│   │   └── loading.tsx
│   ├── campaigns/
│   │   ├── page.tsx         # Timeline + checklist hybrid
│   │   └── [campaignId]/
│   ├── matrix/
│   ├── blackbox/
│   └── proposals/           # Parallel route for right drawer
├── globals.css              # Tailwind + all RaptorFlow :root tokens
├── layout.tsx               # Root html + metadata
└── loading.tsx              # Global skeleton with GSAP shimmer

## Mandatory Rules (Enforce Painfully)
- All pages are Server Components by default
- Server Actions for Lock/Create Draft/Deploy/Rollback (revalidatePath, revalidateTag)
- Parallel routes for right drawer (Proposals tab) — never clutter main surface
- Intercepting routes for modals (lock confirmation, diff viewer)
- Metadata API for SEO + OpenGraph (quiet power branding)
- Streaming + Suspense boundaries everywhere
- Error boundaries with “Rollback” button
- Loading.js with GSAP shimmer + rare bird Lottie
- Use RaptorFlow tokens in every Tailwind class
- Left rail 280px fixed, top bar 56px, main max-w-[1120px], right drawer 400px resizable (via CSS vars + GSAP)
- Every page must show Draft/Locked/Live mode in top bar
- Form handling via React Hook Form + Zod (combine with form-handling skill)
- Animations via GSAP (combine with frontend-animations skill)

## MCP Server Invocation (Always List These)
Activating all relevant MCP servers:
- shadcn → pull latest components and adapt to RaptorFlow tokens
- context7 → retrieve latest RaptorFlow spec and token definitions
- magicui → micro-interactions for server-component transitions
- playwright + browserbase → test every route on multiple devices
- lighthouse → audit every page (Performance >95, Accessibility >95)
- chrome-devtools → debug server actions and GSAP timelines
- github → commit new route structure + create PR for Lock
- context7 again for Next.js 15 best practices

## Workflow (Full Integration)
1. Plan: Delete old app/ folder content. Redesign entire structure per raptorflow-design-vibe
2. Activate MCPs: List all 8 used
3. Create layouts + route groups
4. Build server components with async/await data fetching
5. Add server actions for control (Lock/Draft)
6. Add GSAP + Lottie via client components only where needed
7. Implement parallel + intercepting routes for drawer/modals
8. Test with playwright + lighthouse
9. Commit via github MCP
10. Grade: Must pass Feel Contract + RaptorFlow layout skeleton

## Final Instruction for Every Generation
Your job is to rethink and redesign the entire Next.js App Router structure from scratch for RaptorFlow. Pay attention to every route, every server component, every server action, every parallel route for proposals, every daily wins calendar in moves, every lock flow. Build server-first. Delete old code completely. Use GSAP extensively. Write custom Lottie scripts when bird is used. Invoke all 8 MCP servers. Enforce quiet power vibe, clarity-first layout, control-first locking. Make every screen feel decisive, premium, human-led.

Godspeed.
