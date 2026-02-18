# src/app/ - Next.js App Router

**Parent:** `src/AGENTS.md`

## OVERVIEW
Next.js 14 App Router with 39 pages covering public pages, authenticated routes, and API endpoints.

## STRUCTURE
```
src/app/
├── page.tsx                    # Root page
├── login/page.tsx              # Login page
├── signup/page.tsx             # Signup page
├── (public)/                   # Public routes (landing, pricing, docs)
├── (shell)/                    # Authenticated routes
│   ├── dashboard/page.tsx
│   ├── campaigns/page.tsx
│   ├── settings/page.tsx
│   └── [feature]/page.tsx
└── api/                        # API routes
    └── analytics/
```

## WHERE TO LOOK
| Route | File | Purpose |
|-------|------|---------|
| Landing | `page.tsx` | Marketing landing page |
| Auth | `login/`, `signup/` | Authentication pages |
| Dashboard | `(shell)/dashboard/` | Main dashboard |
| Campaigns | `(shell)/campaigns/` | Campaign management |
| API | `api/` | Backend API proxies |

## CONVENTIONS
- Use `(group)` folders for route grouping
- Server components by default
- `"use client"` for interactive components
- Server Actions for mutations when applicable

## ANTI-PATTERNS
- NO API keys in client components
- NO direct backend calls - use Next.js API routes
- NO `useEffect` for data fetching - use Server Components or SWR/React Query patterns
