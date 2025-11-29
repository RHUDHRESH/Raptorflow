-- =====================================================
-- Phase 2.1: Core Workspace Schema & Multi-User Support
-- =====================================================
-- This migration creates the foundational workspace-aware
-- multi-user schema for RaptorFlow with proper RLS policies.

-- =====================================================
-- 1. CREATE CORE TABLES
-- =====================================================

-- 1.1 Profiles Table
-- Backed by auth.users - never use auth.users directly in app
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  full_name text,
  avatar_url text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- 1.2 Workspaces Table
-- The core entity for RaptorFlow - everything hangs off this
create table if not exists public.workspaces (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  slug text unique,
  owner_id uuid not null references auth.users(id) on delete cascade,
  plan text not null default 'starter', -- 'starter' | 'pro' | 'max'
  is_active boolean not null default true,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- 1.3 Workspace Role Enum
create type workspace_role as enum ('owner', 'admin', 'member', 'viewer');

-- 1.4 Workspace Members Table
-- Who belongs to what workspace & in what role
create table if not exists public.workspace_members (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  role workspace_role not null default 'member',
  created_at timestamptz default now(),
  unique (workspace_id, user_id)
);

-- 1.5 Workspace Invites Table (stubbed for now)
create table if not exists public.workspace_invites (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  email text not null,
  role workspace_role not null default 'member',
  token text not null,
  accepted boolean not null default false,
  created_at timestamptz default now(),
  expires_at timestamptz
);

-- =====================================================
-- 2. ENABLE ROW LEVEL SECURITY
-- =====================================================

alter table public.profiles enable row level security;
alter table public.workspaces enable row level security;
alter table public.workspace_members enable row level security;
alter table public.workspace_invites enable row level security;

-- =====================================================
-- 3. PROFILES RLS POLICIES
-- =====================================================

-- Users can view their own profile
create policy "Users can view own profile"
on public.profiles
for select
using (auth.uid() = id);

-- Users can update their own profile
create policy "Users can update own profile"
on public.profiles
for update
using (auth.uid() = id)
with check (auth.uid() = id);

-- Users can insert their own profile (for sign-up flows)
create policy "Users can insert own profile"
on public.profiles
for insert
with check (auth.uid() = id);

-- =====================================================
-- 4. WORKSPACES RLS POLICIES
-- =====================================================

-- Members can view workspaces they belong to
create policy "Members can view workspaces they belong to"
on public.workspaces
for select
using (
  exists (
    select 1 from public.workspace_members wm
    where wm.workspace_id = workspaces.id
      and wm.user_id = auth.uid()
  )
);

-- Any logged-in user can create a workspace (they become owner)
create policy "Users can create workspaces"
on public.workspaces
for insert
with check (owner_id = auth.uid());

-- Only owners can update their workspace
create policy "Owners can update workspace"
on public.workspaces
for update
using (owner_id = auth.uid())
with check (owner_id = auth.uid());

-- Only owners can delete their workspace
create policy "Owners can delete workspace"
on public.workspaces
for delete
using (owner_id = auth.uid());

-- =====================================================
-- 5. WORKSPACE_MEMBERS RLS POLICIES
-- =====================================================

-- Users can view membership rows for workspaces they belong to
create policy "Users can view membership rows for their workspaces"
on public.workspace_members
for select
using (
  user_id = auth.uid()
  or exists (
    select 1 from public.workspace_members wm2
    where wm2.workspace_id = workspace_members.workspace_id
      and wm2.user_id = auth.uid()
  )
);

-- Only owners can add members
create policy "Owners can add members"
on public.workspace_members
for insert
with check (
  exists (
    select 1 from public.workspaces w
    where w.id = workspace_members.workspace_id
      and w.owner_id = auth.uid()
  )
);

-- Only owners can update member roles
create policy "Owners can update member roles"
on public.workspace_members
for update
using (
  exists (
    select 1 from public.workspaces w
    where w.id = workspace_members.workspace_id
      and w.owner_id = auth.uid()
  )
)
with check (
  exists (
    select 1 from public.workspaces w
    where w.id = workspace_members.workspace_id
      and w.owner_id = auth.uid()
  )
);

-- Only owners can remove members
create policy "Owners can remove members"
on public.workspace_members
for delete
using (
  exists (
    select 1 from public.workspaces w
    where w.id = workspace_members.workspace_id
      and w.owner_id = auth.uid()
  )
);

-- =====================================================
-- 6. WORKSPACE_INVITES RLS POLICIES
-- =====================================================

-- Members can view invites for their workspaces
create policy "Members can view workspace invites"
on public.workspace_invites
for select
using (
  exists (
    select 1 from public.workspace_members wm
    where wm.workspace_id = workspace_invites.workspace_id
      and wm.user_id = auth.uid()
  )
);

-- Only owners can create invites
create policy "Owners can create invites"
on public.workspace_invites
for insert
with check (
  exists (
    select 1 from public.workspaces w
    where w.id = workspace_invites.workspace_id
      and w.owner_id = auth.uid()
  )
);

-- Only owners can delete invites
create policy "Owners can delete invites"
on public.workspace_invites
for delete
using (
  exists (
    select 1 from public.workspaces w
    where w.id = workspace_invites.workspace_id
      and w.owner_id = auth.uid()
  )
);

-- =====================================================
-- 7. HELPER FUNCTIONS
-- =====================================================

-- Function to auto-update updated_at timestamp
create or replace function public.handle_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

-- Apply updated_at trigger to profiles
create trigger profiles_updated_at
  before update on public.profiles
  for each row
  execute function public.handle_updated_at();

-- Apply updated_at trigger to workspaces
create trigger workspaces_updated_at
  before update on public.workspaces
  for each row
  execute function public.handle_updated_at();

-- =====================================================
-- 8. INDEXES FOR PERFORMANCE
-- =====================================================

-- Index for workspace member lookups
create index if not exists idx_workspace_members_workspace_id 
  on public.workspace_members(workspace_id);

create index if not exists idx_workspace_members_user_id 
  on public.workspace_members(user_id);

-- Index for workspace lookups
create index if not exists idx_workspaces_owner_id 
  on public.workspaces(owner_id);

create index if not exists idx_workspaces_slug 
  on public.workspaces(slug);

-- Index for invite lookups
create index if not exists idx_workspace_invites_workspace_id 
  on public.workspace_invites(workspace_id);

create index if not exists idx_workspace_invites_email 
  on public.workspace_invites(email);

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================
-- Phase 2.1 workspace schema is now ready.
-- All future business tables MUST:
-- 1. Include workspace_id uuid not null references workspaces(id)
-- 2. Use RLS with the standard membership check pattern
-- =====================================================
