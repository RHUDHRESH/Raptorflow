# src/ - Frontend Root

**Parent:** `./AGENTS.md`

## OVERVIEW
Next.js 14 frontend root containing all TypeScript/React code, routing, components, and state management.

## STRUCTURE
```
src/
├── app/              # Next.js App Router (39 pages)
├── components/       # React components (20+ subdirs)
├── hooks/            # Custom React hooks
├── lib/              # Utilities (Supabase, GSAP, AI)
├── stores/           # Zustand state management
├── middleware/       # Next.js middleware
└── styles/          # Global styles
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| UI Components | `src/components/` | 20+ subdirs (ui, dashboard, workspace, etc.) |
| Page routes | `src/app/` | App Router pages |
| State | `src/stores/` | Zustand stores |
| API clients | `src/lib/supabase/` | Supabase client wrapper |
| Animations | `src/components/animation/` | GSAP/Framer Motion |

## CONVENTIONS
- Use `src/lib/supabase/` for Supabase access (NOT direct client)
- Components: `*.tsx` for complex, `*.jsx` for simple
- Hooks: `use*.ts` naming convention
- Stores: Zustand with TypeScript interfaces

## ANTI-PATTERNS
- NO direct `createClient()` in components
- NO `process.env` in components - use `NEXT_PUBLIC_*` vars
- NO large components - extract subcomponents
