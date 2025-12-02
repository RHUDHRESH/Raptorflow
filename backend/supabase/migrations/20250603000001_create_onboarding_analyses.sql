create table if not exists public.onboarding_analyses (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references auth.users(id) not null,
  description text not null,
  website_url text,
  geography text,
  industry text,
  analysis jsonb not null,
  created_at timestamptz default now()
);

-- Enable RLS
alter table public.onboarding_analyses enable row level security;

-- Policies
create policy "Users can view own analyses"
  on public.onboarding_analyses for select
  using (auth.uid() = user_id);

create policy "Users can insert own analyses"
  on public.onboarding_analyses for insert
  with check (auth.uid() = user_id);
