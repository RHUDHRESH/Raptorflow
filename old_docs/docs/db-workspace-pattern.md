# Database Workspace Pattern

## Overview

All business tables in RaptorFlow **MUST** be workspace-aware. This document defines the standard pattern for implementing workspace isolation and multi-user access control.

## Core Principle

**Every table containing user data must:**
1. Include a `workspace_id` column
2. Implement Row Level Security (RLS)
3. Use the standard membership check pattern

## Standard Table Schema

```sql
create table if not exists public.your_table (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  -- your other columns here
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);
```

## Standard RLS Pattern

### 1. Enable RLS

```sql
alter table public.your_table enable row level security;
```

### 2. Select Policy (Read Access)

Users can only read rows from workspaces they belong to:

```sql
create policy "Members can view their workspace data"
on public.your_table
for select
using (
  exists (
    select 1 from public.workspace_members wm
    where wm.workspace_id = your_table.workspace_id
      and wm.user_id = auth.uid()
  )
);
```

### 3. Insert Policy (Create Access)

Users can only create rows in workspaces they belong to:

```sql
create policy "Members can insert into their workspace"
on public.your_table
for insert
with check (
  exists (
    select 1 from public.workspace_members wm
    where wm.workspace_id = your_table.workspace_id
      and wm.user_id = auth.uid()
  )
);
```

### 4. Update Policy (Modify Access)

Users can only update rows in workspaces they belong to:

```sql
create policy "Members can update their workspace data"
on public.your_table
for update
using (
  exists (
    select 1 from public.workspace_members wm
    where wm.workspace_id = your_table.workspace_id
      and wm.user_id = auth.uid()
  )
)
with check (
  exists (
    select 1 from public.workspace_members wm
    where wm.workspace_id = your_table.workspace_id
      and wm.user_id = auth.uid()
  )
);
```

### 5. Delete Policy (Remove Access)

Users can only delete rows in workspaces they belong to:

```sql
create policy "Members can delete their workspace data"
on public.your_table
for delete
using (
  exists (
    select 1 from public.workspace_members wm
    where wm.workspace_id = your_table.workspace_id
      and wm.user_id = auth.uid()
  )
);
```

## Role-Based Variations

For operations that should be restricted to owners or admins, modify the policy:

```sql
-- Owner-only example
create policy "Owners can delete workspace data"
on public.your_table
for delete
using (
  exists (
    select 1 from public.workspace_members wm
    join public.workspaces w on w.id = wm.workspace_id
    where wm.workspace_id = your_table.workspace_id
      and wm.user_id = auth.uid()
      and w.owner_id = auth.uid()
  )
);

-- Owner or Admin example
create policy "Owners and admins can update workspace data"
on public.your_table
for update
using (
  exists (
    select 1 from public.workspace_members wm
    where wm.workspace_id = your_table.workspace_id
      and wm.user_id = auth.uid()
      and wm.role in ('owner', 'admin')
  )
)
with check (
  exists (
    select 1 from public.workspace_members wm
    where wm.workspace_id = your_table.workspace_id
      and wm.user_id = auth.uid()
      and wm.role in ('owner', 'admin')
  )
);
```

## Frontend Integration

### Always Include workspace_id

When creating or querying data from the frontend:

```typescript
// ✅ CORRECT - includes workspace_id
const { data, error } = await supabase
  .from('your_table')
  .insert({
    workspace_id: currentWorkspace.id,
    // other fields...
  });

// ❌ WRONG - missing workspace_id
const { data, error } = await supabase
  .from('your_table')
  .insert({
    // other fields...
  });
```

### RLS Handles Filtering Automatically

You don't need to manually filter by workspace_id in SELECT queries - RLS does it:

```typescript
// ✅ CORRECT - RLS automatically filters by workspace
const { data, error } = await supabase
  .from('your_table')
  .select('*');

// ❌ UNNECESSARY - RLS already filters
const { data, error } = await supabase
  .from('your_table')
  .select('*')
  .eq('workspace_id', currentWorkspace.id);
```

However, you **must** include `workspace_id` when inserting/updating.

## Migration Checklist

When creating a new business table:

- [ ] Add `workspace_id uuid not null references public.workspaces(id) on delete cascade`
- [ ] Enable RLS with `alter table ... enable row level security`
- [ ] Create SELECT policy with membership check
- [ ] Create INSERT policy with membership check
- [ ] Create UPDATE policy with membership check
- [ ] Create DELETE policy with membership check (or owner-only)
- [ ] Add index: `create index idx_your_table_workspace_id on your_table(workspace_id)`
- [ ] Test that users can only see their workspace data
- [ ] Test that users cannot access other workspaces' data

## Security Guarantees

This pattern ensures:

1. **Data Isolation**: Users can only access data from workspaces they belong to
2. **Automatic Enforcement**: Database-level security, not just application-level
3. **No Leaks**: Even if frontend code has bugs, data cannot leak across workspaces
4. **Audit Trail**: All access is tied to authenticated users via `auth.uid()`

## Non-Negotiable Rules

1. **Never disable RLS** on tables with user data
2. **Never use `auth.users` directly** - always use `public.profiles`
3. **Always cascade deletes** when workspace is deleted
4. **Always test RLS policies** before deploying

## Example: Applying to Strategic System Tables

For existing tables like `moves`, `campaigns`, `cohorts`:

```sql
-- Add workspace_id column
alter table public.moves 
  add column workspace_id uuid references public.workspaces(id) on delete cascade;

-- Make it required (after backfilling existing data)
alter table public.moves 
  alter column workspace_id set not null;

-- Enable RLS
alter table public.moves enable row level security;

-- Apply standard policies (see above)
-- ...

-- Add index
create index idx_moves_workspace_id on public.moves(workspace_id);
```

---

**Last Updated**: Phase 2.1 - November 28, 2024
