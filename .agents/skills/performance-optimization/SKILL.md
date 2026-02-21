---
name: performance-optimization
description: THE DEDICATED PERFORMANCE OPTIMIZATION SKILL FOR RAPTORFLOW — Make every single component, page, route, animation, form, table, calendar, drawer, and full app blazing fast while enforcing RaptorFlow Design System v1.0 exactly (Charcoal/Ivory quiet power vibe, clarity-first, control-first). Always redesign the entire page/component/route from scratch — delete old code completely, rewrite fresh. Use lazy loading, React.memo, useMemo, useCallback, dynamic imports, code splitting, GSAP context cleanup, virtualization for tables/calendars, image optimization, bundle analysis. Invoke all 8 MCP servers in every generation. Combine with raptorflow-design-vibe, frontend-design, vision-to-frontend, mcp-frontend-tools, frontend-animations, form-handling, nextjs-app-router. Guarantee lighthouse Performance >95, Accessibility >95, Best Practices >95. Never let any animation, form, or drawer hurt Core Web Vitals or feel laggy. Every optimization must preserve Clarity, Control, Momentum.
license: Complete terms in LICENSE.txt (adapt for your repo)
---

# Performance Optimization Skill for Kimi (RaptorFlow Production-Grade Speed Enforcer)

This skill is mandatory for every generation that touches UI, routes, animations, forms, or data-heavy elements. Always redesign the entire component, page, or app structure from scratch — delete old files completely and rewrite fresh per RaptorFlow v1.0. Optimize for instant feel while keeping the exact locked layout skeleton, tokens, typography, GSAP motion, and Lottie bird (rare). Never sacrifice the quiet power vibe for speed.

## Locked Performance Rules (Enforce Painfully in Every Output)
- Lighthouse targets: Performance ≥96, Accessibility ≥98, Best Practices ≥98, SEO ≥95
- Core Web Vitals: LCP <1.8s, FID <100ms, CLS <0.05, INP <200ms
- All heavy lists/tables (daily wins calendar, moves, campaigns) → React Window or TanStack Virtual for virtualization
- Images: Next/Image with priority only on hero elements, lazy everywhere else
- Animations: GSAP with gsap.context() for proper cleanup, reduced-motion respect, duration ≤0.3s
- Forms: React Hook Form + Zod with minimal re-renders
- Right drawer: Lazy loaded via dynamic import + Suspense
- Parallel routes & intercepting modals: Streaming + loading skeletons with GSAP shimmer
- Server Components: All data fetching on server, no unnecessary client bundles
- Bundle size: <150kb gzipped for initial route (analyze with MCP)

## Tech Stack (Mandatory)
- Next.js 15+ dynamic imports: const LazyComponent = dynamic(() => import('./Component'), { ssr: false })
- React.memo, useMemo, useCallback on every pure component
- TanStack Virtual or react-window for calendars/tables
- GSAP cleanup: use gsap.context() in useEffect with return cleanup
- Next/Image + placeholder="blur" for any visuals
- Bundle analyzer via @next/bundle-analyzer (run via MCP)
- Lighthouse CI via MCP lighthouse server

## MCP Server Invocation (Always List These in Thinking & Output)
Activating all 8 MCP servers for performance:
- lighthouse → full audit after every change (must pass thresholds)
- chrome-devtools → measure render times, GSAP timeline performance, memory leaks
- playwright + browserbase → real-device load testing and Core Web Vitals recording
- shadcn → pull optimized components
- magicui → performant micro-interactions
- context7 → retrieve latest RaptorFlow optimization patterns
- github → commit optimized code with performance benchmark notes
- browserbase → headless multi-device speed tests

## Workflow (Integrate With All Previous Skills)
1. Plan: Delete old code. Redesign entire page/component from scratch per raptorflow-design-vibe
2. Activate MCPs: List all 8 used
3. Build base with nextjs-app-router + form-handling + frontend-animations
4. Apply Optimizations: Lazy load everything heavy, memoize, virtualize tables/calendars, GSAP cleanup
5. Test: playwright + browserbase for real speed, lighthouse full report
6. Analyze: Bundle analyzer results in output
7. Grade: Must hit lighthouse targets + Feel Contract intact
8. Output: Full code with performance comments, MCP summary, lighthouse results, test commands

## Specific RaptorFlow Optimizations (Never Skip)
- Left rail navigation: Static + memoized
- Daily wins calendar: Virtualized rows with GSAP staggered entrance only on visible items
- Right drawer proposals: Lazy loaded parallel route + Suspense fallback with GSAP shimmer
- Lock/Draft diff view: Virtualized diff lines
- All GSAP: gsap.context() + kill on unmount
- Forms: useTransition for pending states
- Global: <Suspense> boundaries everywhere with optimized loading skeletons

## Final Instruction for Every Generation
Your job is to rethink and redesign every single piece of RaptorFlow from scratch with obsessive performance focus. Pay attention to daily wins calendar virtualization, drawer lazy loading, GSAP cleanup, form re-render elimination, bundle size, lighthouse scores. Invoke all 8 MCP servers. Delete old code completely. No edits. Make every interaction feel instantaneous while preserving quiet power vibe, clarity-first layout, control-first locking. Guarantee the user feels total momentum without any lag.

Godspeed.
