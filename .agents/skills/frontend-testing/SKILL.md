---
name: frontend-testing
description: THE COMPLETE FRONTEND TESTING SKILL FOR RAPTORFLOW — Build exhaustive test suites for every component, page, form, animation, route, calendar, drawer, lock flow, and full app using Vitest + React Testing Library + Cypress + Playwright. Always redesign the entire test file and component under test from scratch — delete old test code completely, rewrite fresh per RaptorFlow v1.0. Enforce 100% coverage on critical paths (Clarity/Control/Momentum). Test GSAP animations, Lottie bird, token usage, layout skeleton, accessibility, performance regression. Invoke all 8 MCP servers in every test generation. Combine with raptorflow-design-vibe, frontend-design, vision-to-frontend, mcp-frontend-tools, frontend-animations, form-handling, nextjs-app-router, performance-optimization. Never ship untested code.
license: Complete terms in LICENSE.txt (adapt for your repo)
---

# Frontend Testing Skill for Kimi (Vitest + RTL + Cypress + Playwright — RaptorFlow Edition)

This skill is mandatory whenever any UI, component, page, route, form, animation, or flow is generated. Always redesign the test files from scratch — delete old __tests__ or .spec files completely and rewrite fresh. Enforce RaptorFlow Design System v1.0 in every test (tokens, layout skeleton, quiet power vibe, GSAP motion, Lottie bird, lock states, daily wins calendar). Achieve 100% coverage on critical user paths.

## Locked Testing Rules (Painfully Enforced)
- Framework: Vitest + React Testing Library (unit/component) + Cypress/Playwright (E2E)
- Test every RaptorFlow rule: colors, typography, spacing, buttons, inputs, cards, tables, right drawer, lock/draft/diff, proposals, daily wins reveals
- Accessibility: axe-core + RTL userEvent + keyboard navigation
- Animations: Test GSAP timelines with @testing-library/user-event and jest.mock for gsap
- Visual regression: Playwright snapshots against RaptorFlow skeleton
- Performance regression: Lighthouse scores inside tests via MCP
- Lock flows: Test Draft → Locked → Live with github MCP diff verification
- Reduced-motion: Test @media (prefers-reduced-motion)
- Coverage: 100% on all critical paths

## MCP Server Invocation (Mandatory — List in Every Test)
Activating all 8 MCP servers for testing:
- playwright → run E2E tests, visual snapshots, multi-device
- lighthouse → run performance/accessibility audits inside CI
- chrome-devtools → debug test failures, GSAP timeline inspection
- shadcn → test shadcn-adapted components
- magicui → test micro-interactions
- context7 → retrieve RaptorFlow spec for expected assertions
- github → commit tests + create PR with test results
- browserbase → cloud browser testing for CI

## Test Structure (Always Follow)
__tests__/
├── components/
│   ├── Button.spec.tsx          # RTL + GSAP hover test
│   ├── MovesCalendar.spec.tsx   # Virtualized + daily wins GSAP stagger
│   └── LockButton.spec.tsx      # Lottie bird + lock flow
├── pages/
│   ├── moves/page.spec.tsx
│   └── campaigns/page.cy.tsx    # Cypress E2E
├── e2e/
│   └── full-flow.cy.ts          # End-to-end: Brief → Lock → Deploy
└── utils/
    └── renderWithProviders.tsx  # Custom renderer with RaptorFlow theme + GSAP mock

## Workflow (Integrate With All Previous Skills)
1. Plan: Delete old test files. Redesign tests for the newly redesigned component/page
2. Activate MCPs: List all 8
3. Write unit tests with Vitest + RTL (render, userEvent, screen, waitFor)
4. Add animation tests (GSAP mock + timeline assertions)
5. Write E2E with Cypress/Playwright (visual diff against RaptorFlow skeleton)
6. Run lighthouse inside tests
7. Commit via github MCP with coverage report
8. Grade: 100% pass + lighthouse thresholds + Feel Contract coverage
9. Output: Full test files + component code under test + run commands + MCP summary

## Example Test Snippets (Always Include)
- Test primary button hover uses GSAP and correct Charcoal token
- Test daily wins calendar rows stagger with GSAP and are virtualized
- Test right drawer proposals appear only when pulled (not pushed)
- Test Lock button shows bird Lottie and creates github diff

## Final Instruction for Every Generation
Your job is to rethink and redesign every test suite from scratch for RaptorFlow. Pay attention to testing every button, every daily wins animation, every lock flow, every drawer proposal, every token usage, every GSAP timeline. Invoke all 8 MCP servers. Delete old test code completely. No edits. Guarantee 100% coverage on Clarity/Control/Momentum paths. Make sure nothing ships without being battle-tested.

Godspeed.
