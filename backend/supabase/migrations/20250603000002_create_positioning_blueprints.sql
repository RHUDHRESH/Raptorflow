create table if not exists public.positioning_blueprints (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references auth.users(id) not null,
  analysis_id uuid references public.onboarding_analyses(id) not null,
  primary_focus text not null,
  user_confidence text not null,
  blueprint jsonb not null,
  created_at timestamptz default now()
);

-- Enable RLS
alter table public.positioning_blueprints enable row level security;

-- Policies
create policy "Users can view own blueprints"
  on public.positioning_blueprints for select
  using (auth.uid() = user_id);

create policy "Users can insert own blueprints"
  on public.positioning_blueprints for insert
  with check (auth.uid() = user_id);
