# Frontend Phase 1 — RaptorFlow Brand System

## Summary

This phase creates the central Paper / Amber / Editorial SaaS brand system for RaptorFlow. It is the foundation for the entire frontend renaissance. No product features were added. No API behavior was changed.

## Files Created

### Brand Directory

- `apps/web/src/brand/index.ts` — Barrel export
- `apps/web/src/brand/tokens.ts` — Canonical colors, typography, radii, shadows, spacing, z-index, semantic states
- `apps/web/src/brand/copy.ts` — Canonical product copy and positioning
- `apps/web/src/brand/motion.ts` — Standard motion constants and reduced-motion helper
- `apps/web/src/brand/routes.ts` — Canonical route metadata and grouped navigation structure
- `apps/web/src/brand/README.md` — Brand system documentation

### Public Asset Hub

- `public/brand/.gitkeep`
- `public/brand/textures/.gitkeep`
- `public/brand/logo-full.svg` — Placeholder
- `public/brand/logo-mark.svg` — Placeholder
- `public/brand/favicon.svg` — Placeholder

### Brand Components

- `apps/web/src/components/brand/RaptorFlowLogo.tsx` — Unified logo component with asset fallback
- `apps/web/src/components/brand/RaptorMark.tsx` — Abstract amber/ink geometric mark
- `apps/web/src/components/brand/BrandWordmark.tsx` — Serif wordmark
- `apps/web/src/components/brand/BrandHeader.tsx` — Reusable page header
- `apps/web/src/components/brand/PaperTexture.tsx` — Paper texture wrapper
- `apps/web/src/components/brand/index.ts` — Barrel export

### Window Components

- `apps/web/src/components/windows/RfWindow.tsx` — Paper card/window
- `apps/web/src/components/windows/RfWindowHeader.tsx` — Window header
- `apps/web/src/components/windows/RfWindowBody.tsx` — Window body
- `apps/web/src/components/windows/RfWindowGrid.tsx` — Responsive grid
- `apps/web/src/components/windows/RfWindowRail.tsx` — Right rail wrapper
- `apps/web/src/components/windows/StatusPill.tsx` — Status badge
- `apps/web/src/components/windows/SignalDot.tsx` — Signal indicator dot
- `apps/web/src/components/windows/index.ts` — Barrel export

### Modified Files

- `apps/web/src/components/layout/shell-sidebar.tsx` — Replaced generic lightning logo with `RaptorMark` + `BrandWordmark`
- `apps/web/src/app/(app)/dashboard/page.tsx` — Added `BrandHeader`, `RfWindowGrid`, `StatusPill` as proof of concept

## How Later Phases Should Use This

1. **Import from `@/brand`** for tokens, copy, motion, and route metadata.
2. **Use `RaptorFlowLogo`** instead of inline logo fragments.
3. **Wrap page content with `RfWindow`** and `RfWindowGrid` instead of ad-hoc card divs.
4. **Use `BrandHeader`** for consistent page headers.
5. **Reference `globals.css`** for the canonical CSS design system; use `tokens.ts` only when JS-level access is required.

## Known Limitations

- Logo SVGs are placeholders. Final brand assets should be dropped into `public/brand/`.
- `RaptorFlowLogo` falls back to `RaptorMark` + `BrandWordmark` if `logo-full.svg` fails to load.
- `RfWindow` does not yet support collapsible or draggable behavior.
- `PaperTexture` is a thin wrapper around existing CSS classes.

## Next Phase Recommendation

**Phase 2: Page-by-Page Brand Application**

Transform each major page (Office, Campaigns, Content, Billing, Landing) to use the brand system consistently. Replace ad-hoc card styles with `RfWindow`, standardize headers with `BrandHeader`, and eliminate one-off color usage.

## Commands Run

| Command                        | Result                                                                |
| ------------------------------ | --------------------------------------------------------------------- |
| `pnpm typecheck`               | PASS                                                                  |
| `pnpm lint`                    | PASS                                                                  |
| `pnpm structural:check`        | PASS (pre-existing WARNs: documented Prisma gaps, unused Rust routes) |
| `pnpm route-parity:check`      | PASS (pre-existing WARNs: unused Rust routes)                         |
| `pnpm runtime-authority:check` | PASS (pre-existing WARNs: documented Prisma gaps)                     |
| `cargo fmt --all --check`      | PASS                                                                  |
| `cargo check --workspace`      | PASS                                                                  |

## Confirmations

- No product logic changed.
- No fake data added.
- No route behavior changed.
- No force push used.
- No stale PR merge.
