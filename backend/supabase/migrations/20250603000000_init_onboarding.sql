-- Create projects table
create table if not exists public.projects (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references auth.users(id) not null,
  name text not null,
  status text check (status in ('draft', 'active', 'archived')) default 'draft',
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Create intake table
create table if not exists public.intake (
  id uuid default gen_random_uuid() primary key,
  project_id uuid references public.projects(id) on delete cascade not null,
  goals jsonb default '{}'::jsonb,
  audience jsonb default '{}'::jsonb,
  positioning jsonb default '{}'::jsonb,
  execution jsonb default '{}'::jsonb,
  locked_at timestamptz,
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  unique(project_id)
);

-- Create plans table
create table if not exists public.plans (
  id uuid default gen_random_uuid() primary key,
  project_id uuid references public.projects(id) on delete cascade not null,
  status text check (status in ('draft', 'ready', 'in_progress')) default 'draft',
  raw_pillars jsonb default '[]'::jsonb,
  raw_outline jsonb default '{}'::jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Enable RLS
alter table public.projects enable row level security;
alter table public.intake enable row level security;
alter table public.plans enable row level security;

-- Create policies
-- Projects: Users can only see/edit their own projects
create policy "Users can view own projects"
  on public.projects for select
  using (auth.uid() = user_id);

create policy "Users can insert own projects"
  on public.projects for insert
  with check (auth.uid() = user_id);

create policy "Users can update own projects"
  on public.projects for update
  using (auth.uid() = user_id);

-- Intake: Users can only see/edit intake for their own projects
create policy "Users can view intake for own projects"
  on public.intake for select
  using (
    exists (
      select 1 from public.projects
      where projects.id = intake.project_id
      and projects.user_id = auth.uid()
    )
  );

create policy "Users can insert intake for own projects"
  on public.intake for insert
  with check (
    exists (
      select 1 from public.projects
      where projects.id = intake.project_id
      and projects.user_id = auth.uid()
    )
  );

create policy "Users can update intake for own projects"
  on public.intake for update
  using (
    exists (
      select 1 from public.projects
      where projects.id = intake.project_id
      and projects.user_id = auth.uid()
    )
  );

-- Plans: Users can only see/edit plans for their own projects
create policy "Users can view plans for own projects"
  on public.plans for select
  using (
    exists (
      select 1 from public.projects
      where projects.id = plans.project_id
      and projects.user_id = auth.uid()
    )
  );

create policy "Users can insert plans for own projects"
  on public.plans for insert
  with check (
    exists (
      select 1 from public.projects
      where projects.id = plans.project_id
      and projects.user_id = auth.uid()
    )
  );

create policy "Users can update plans for own projects"
  on public.plans for update
  using (
    exists (
      select 1 from public.projects
      where projects.id = plans.project_id
      and projects.user_id = auth.uid()
    )
  );
