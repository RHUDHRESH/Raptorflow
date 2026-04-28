## Summary

This PR creates the central Paper / Amber / Editorial SaaS brand system for RaptorFlow. It is the foundation for the entire frontend renaissance. No product features were added. No API behavior was changed.

## Brand directory created

- `apps/web/src/brand/index.ts` — Barrel export
- `apps/web/src/brand/tokens.ts` — Canonical colors, typography, radii, shadows, spacing, z-index, semantic states
- `apps/web/src/brand/copy.ts` — Canonical product copy and positioning
- `apps/web/src/brand/motion.ts` — Standard motion constants and reduced-motion helper
- `apps/web/src/brand/routes.ts` — Canonical route metadata and grouped navigation structure
- `apps/web/src/brand/README.md` — Brand system documentation

## Public asset hub created

- `public/brand/.gitkeep`
- `public/brand/textures/.gitkeep`
- `public/brand/logo-full.svg` — Placeholder (amber/ink, no mascot)
- `public/brand/logo-mark.svg` — Placeholder (abstract geometric mark)
- `public/brand/favicon.svg` — Placeholder

## Brand components created

- `RaptorFlowLogo.tsx` — Unified logo with asset fallback
- `RaptorMark.tsx` — Abstract amber/ink geometric mark (no literal bird)
- `BrandWordmark.tsx` — Serif wordmark
- `BrandHeader.tsx` — Reusable page header (eyebrow, title, description, status, actions)
- `PaperTexture.tsx` — Paper texture wrapper

## Window components created

- `RfWindow.tsx` — Paper card/window (default/highlight/quiet/danger variants)
- `RfWindowHeader.tsx` — Window header
- `RfWindowBody.tsx` — Window body (comfortable/compact density)
- `RfWindowGrid.tsx` — Responsive grid (1-4 columns, mobile-first)
- `RfWindowRail.tsx` — Right rail wrapper
- `StatusPill.tsx` — Status badge with canonical tones
- `SignalDot.tsx` — Signal indicator dot with pulse support

## Sidebar branding update

- Replaced generic lightning bolt logo with `RaptorMark` + `BrandWordmark`
- Updated tagline from "EST. 1989" to "AI-NATIVE MARKETING OS"
- Kept all existing nav structure and behavior intact

## Dashboard proof-of-concept update

- `apps/web/src/app/(app)/dashboard/page.tsx`
- Added `BrandHeader` with eyebrow, title, description, and live status pill
- Replaced ad-hoc grid divs with `RfWindowGrid` for stat cards
- No API behavior changed, no fake data added

## Commands run with pass/fail table

| Command                        | Result                                                                |
| ------------------------------ | --------------------------------------------------------------------- |
| `pnpm typecheck`               | PASS                                                                  |
| `pnpm lint`                    | PASS                                                                  |
| `pnpm structural:check`        | PASS (pre-existing WARNs: documented Prisma gaps, unused Rust routes) |
| `pnpm route-parity:check`      | PASS (pre-existing WARNs: unused Rust routes)                         |
| `pnpm runtime-authority:check` | PASS (pre-existing WARNs: documented Prisma gaps)                     |
| `cargo fmt --all --check`      | PASS                                                                  |
| `cargo check --workspace`      | PASS                                                                  |

## Known limitations

- Logo SVGs are placeholders. Final brand assets should be dropped into `public/brand/`.
- `RaptorFlowLogo` falls back to `RaptorMark` + `BrandWordmark` if `logo-full.svg` fails to load.
- `RfWindow` does not yet support collapsible or draggable behavior.
- `PaperTexture` is a thin wrapper around existing CSS classes.

## Where final assets should be dropped

- `public/brand/logo-full.svg`
- `public/brand/logo-mark.svg`
- `public/brand/favicon.svg`
- `public/brand/apple-touch-icon.png`
- `public/brand/og-image.png`
- `public/brand/textures/paper-grain.svg`
- `public/brand/textures/paper-grain-soft.svg`

## Confirmations

- [x] No product logic changed
- [x] No fake data added
- [x] No route behavior changed
- [x] No force push used
- [x] No stale PR merge
