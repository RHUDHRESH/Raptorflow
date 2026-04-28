# Frontend Phase 2 — App Shell, Navigation, and Page Frame Integration

## Summary

This phase uses the Phase 1 brand/window system to make the RaptorFlow app shell feel coherent and production-grade. It creates the unified frame that every future page will live inside.

This is NOT the Office rebuild yet.
This is NOT campaign contract repair.
This is NOT billing/payments.

## Files Created

### App Page Frame Components

- `apps/web/src/components/layout/AppPageFrame.tsx` — Standard page wrapper with BrandHeader, paper texture, optional rail, max-width control
- `apps/web/src/components/layout/AppPageSection.tsx` — Section wrapper using RfWindow
- `apps/web/src/components/layout/AppPageToolbar.tsx` — Toolbar for filters, search, quick actions
- `apps/web/src/components/layout/AppEmptyState.tsx` — Quiet empty state with optional action
- `apps/web/src/components/layout/AppErrorState.tsx` — Error state with destructive tone
- `apps/web/src/components/layout/AppLoadingState.tsx` — Subtle amber pulse loading indicator
- `apps/web/src/components/layout/index.ts` — Barrel export for layout components

### Modified Files

- `apps/web/src/components/layout/shell-sidebar.tsx` — Integrated route metadata from `@/brand/routes`, updated active state styling to amber/paper theme, kept brand components
- `apps/web/src/app/(app)/content/page.tsx` — Wrapped with AppPageFrame, AppPageSection, AppEmptyState, AppLoadingState, AppErrorState
- `apps/web/src/app/(app)/settings/page.tsx` — Wrapped with AppPageFrame, AppPageSection, AppLoadingState
- `apps/web/src/app/(app)/uploads/page.tsx` — Wrapped with AppPageFrame, AppPageSection
- `apps/web/src/app/(app)/ripples/page.tsx` — Wrapped with AppPageFrame, AppPageSection, AppEmptyState, AppLoadingState, AppErrorState, AppPageToolbar

## How to Use AppPageFrame

```tsx
import { AppPageFrame } from "@/components/layout";

<AppPageFrame
  eyebrow="Section"
  title="Page Title"
  description="Optional description."
  actions={<button className="btn-primary">Action</button>}
  maxWidth="wide"
>
  Content here
</AppPageFrame>;
```

## How to Use AppPageSection

```tsx
import { AppPageSection } from "@/components/layout";

<AppPageSection
  title="Section Title"
  eyebrow="Subsection"
  actions={<StatusPill status="Live" tone="success" />}
  variant="default"
>
  Section content
</AppPageSection>;
```

Variants: `default` | `quiet` | `highlight` | `danger`

## When to Use Empty/Error/Loading States

| State   | Component         | Use When                                    |
| ------- | ----------------- | ------------------------------------------- |
| Loading | `AppLoadingState` | Data is fetching, no content yet            |
| Empty   | `AppEmptyState`   | Data loaded, array is empty                 |
| Error   | `AppErrorState`   | Query failed, show retry or contact support |

## Routes Aligned

- `/app/dashboard` — Phase 1 proof of concept (BrandHeader, RfWindowGrid)
- `/content` — AppPageFrame, AppPageSection, AppEmptyState, AppLoadingState, AppErrorState
- `/settings` — AppPageFrame, AppPageSection, AppLoadingState
- `/uploads` — AppPageFrame, AppPageSection
- `/ripples` — AppPageFrame, AppPageSection, AppEmptyState, AppLoadingState, AppErrorState, AppPageToolbar

## Routes Intentionally Untouched

These need dedicated phases and were not modified:

- `/office` — Needs Office rebuild (Phase 3)
- `/campaigns` and campaign detail — Needs campaign contract repair
- `/moves` — Complex product flow
- `/billing` — Payment flow
- `/landing` — Marketing page
- `/foundation` — Complex form flow
- `/council` — War room, complex real-time UI

## Sidebar Changes

- Uses `routeGroups` from `@/brand/routes` for navigation structure
- Active state uses amber wash (`--amber-wash`) instead of violet
- Icon colors use ink scale instead of slate
- Preserved: notification bell, mobile behavior, OfficeMiniStrip, SidebarBadge for intel/nudges

## Known Limitations

- `AppPageFrame` does not yet support collapsible rails
- `AppPageToolbar` is a simple flex wrapper; advanced filter patterns may need custom builds
- Pages not in the "safe routes" list still use their original styling

## Next Phase Recommendation

**Phase 3: Office Rebuild**

Transform the Office page (`/office`) into a premium founder operating desk experience using the full brand system. This is where the Paper/Amber identity should shine most.

## Commands Run

| Command                   | Result                    |
| ------------------------- | ------------------------- |
| `pnpm typecheck`          | PASS                      |
| `pnpm lint`               | PASS                      |
| `pnpm structural:check`   | PASS (pre-existing WARNs) |
| `cargo fmt --all --check` | PASS                      |
| `cargo check --workspace` | PASS                      |

## Confirmations

- [x] No product logic changed
- [x] No fake data added
- [x] No route behavior changed
- [x] No Office rebuild yet
- [x] No force push used
- [x] No stale PR merge
