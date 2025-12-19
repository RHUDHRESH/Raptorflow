# RAPTORFLOW: QUICK START GUIDE

**Estimated Setup Time:** 10 minutes
**Status:** Ready for development

## 1. Install Dependencies

```bash
npm install
```

This installs all required packages:
- Next.js 15
- React 18
- TanStack Query
- Jotai
- Supabase client
- Tailwind CSS
- Type utilities

## 2. Set Up Supabase Project

Go to [supabase.com](https://supabase.com) and:

1. Create new project or use existing one
2. Go to Project Settings → API
3. Copy:
   - Project URL → `NEXT_PUBLIC_SUPABASE_URL`
   - Anon Key → `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - Service Role Key → `SUPABASE_SERVICE_ROLE_KEY`

## 3. Configure Environment Variables

Create `.env.local`:

```bash
cp .env.example .env.local
```

Then edit `.env.local` with your Supabase credentials:

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
```

## 4. Run Database Migrations

1. Go to Supabase dashboard
2. Click "SQL Editor"
3. Click "New Query"
4. Open `supabase/migrations/001_init_schema.sql`
5. Copy all content and paste into SQL editor
6. Click "Run"

Verify tables created:
- `users`
- `campaigns`
- `moves`
- `assets`

## 5. Start Local Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

You should see:
- Redirect to login page
- Login/Signup forms working

## 6. Create Your First Account

1. Click "Sign up"
2. Use test email: `test@raptorflow.local`
3. Password: `TestPassword123`
4. Click "Create Account"
5. Go to Supabase dashboard → Authentication
6. Find your user in the users list
7. Copy user ID (UUID)
8. Go to SQL Editor and run:

```sql
INSERT INTO public.users (id, email)
VALUES ('<your-user-id>', 'test@raptorflow.local');
```

9. Sign out and sign back in
10. You should now see the dashboard

## 7. Test Core Features

**Dashboard Page** (`/app/dashboard`)
- Shows "Today's Moves"
- Empty state message (no moves created yet)
- Quick stats panel

**Campaigns Page** (`/app/campaigns`)
- Shows empty state
- "Create Campaign" button (not functional yet - Phase 1)

**Moves Page** (`/app/moves`)
- Shows empty state
- "Create Move" button (not functional yet - Phase 1)

**Settings Page** (`/app/settings`)
- Shows settings panels
- Quota meter (shows 0% usage)

## 8. Project Structure Quick Reference

| Path | Purpose |
|------|---------|
| `app/` | Next.js pages and layouts |
| `components/` | Reusable React components |
| `lib/api/` | Supabase database calls |
| `lib/hooks/` | TanStack Query hooks |
| `lib/store/` | Jotai atoms (global state) |
| `lib/utils/` | Utility functions |
| `lib/types/` | TypeScript type definitions |
| `styles/` | Tailwind CSS global styles |
| `supabase/` | Database migrations |

## 9. Key Files to Know

| File | Purpose |
|------|---------|
| `app/app/layout.tsx` | App shell, auth check, providers |
| `app/auth/login/page.tsx` | Login form |
| `app/auth/signup/page.tsx` | Signup form |
| `lib/api/supabase.ts` | Supabase client init |
| `lib/store/atoms.ts` | Global state definitions |
| `components/layout/Sidebar.tsx` | Navigation sidebar |

## 10. Common Tasks

**Add a new page:**
```bash
mkdir -p app/app/new-page
echo "export default function NewPage() { return <div>Hello</div> }" > app/app/new-page/page.tsx
```

**Add a new component:**
```bash
echo "export function MyComponent() { return <div>Component</div> }" > components/custom/MyComponent.tsx
```

**Run TypeScript check:**
```bash
npm run type-check
```

**Build for production:**
```bash
npm run build
npm start
```

## 11. Debugging Tips

**Jotai State:**
- Import atom: `import { userAtom } from "@/lib/store/atoms"`
- Use in component: `const [user] = useAtom(userAtom)`

**TanStack Query:**
- Open browser DevTools → Network
- Look for API calls to Supabase
- Check `useQuery` return value: `{ data, isLoading, error }`

**Supabase:**
- Go to Supabase dashboard → SQL Editor
- Run queries to check data
- Check Authentication → Users tab for auth accounts

**Next.js:**
- Check terminal for build errors
- React DevTools browser extension useful for component tree

## 12. Next Phase (Phase 1)

Once MVP foundation is running, Phase 1 focuses on:

1. **Campaign Creation** - 30-min setup flow
2. **Move Management** - Create, edit, delete moves
3. **Shipping** - Mark moves as shipped, upload proof
4. **Data Connection** - Hook up real data to dashboard

See `IMPLEMENTATION_BLUEPRINT.md` Section 11 for detailed Phase 1 roadmap.

## 13. Support & Documentation

- **Framework:** [Next.js Docs](https://nextjs.org/docs)
- **Database:** [Supabase Docs](https://supabase.com/docs)
- **State:** [Jotai Docs](https://jotai.org)
- **Data:** [TanStack Query Docs](https://tanstack.com/query)
- **Styling:** [Tailwind CSS Docs](https://tailwindcss.com)

## Troubleshooting

**"Cannot find module '@/components/ui/button'"**
- Run `npm install` again
- Check that all UI components exist in `components/ui/`

**"Supabase authentication failed"**
- Check `.env.local` has correct credentials
- Verify project URL and keys match your Supabase project
- Check Supabase project is active (not paused)

**"TypeError: Cannot read property 'user' of undefined"**
- Supabase client not initialized
- Check `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` are set
- Restart dev server: `Ctrl+C` then `npm run dev`

**Port 3000 already in use**
```bash
npm run dev -- -p 3001
```

---

**Ready to build?** Start with Phase 1:
- Connect dashboard to `useTodaysMoves()` hook
- Create campaign form
- Implement move shipping flow

See `IMPLEMENTATION_BLUEPRINT.md` for complete roadmap.
