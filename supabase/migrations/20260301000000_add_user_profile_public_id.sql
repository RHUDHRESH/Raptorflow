begin;

create sequence if not exists public.user_profile_id_seq start 100000;

alter table if exists public.user_profiles
  add column if not exists user_id text;

update public.user_profiles
set user_id = 'U' || nextval('public.user_profile_id_seq')::text
where user_id is null;

do $$
begin
  if not exists (
    select 1
    from pg_constraint
    where conname = 'user_profiles_user_id_key'
      and conrelid = 'public.user_profiles'::regclass
  ) then
    alter table public.user_profiles
      add constraint user_profiles_user_id_key unique (user_id);
  end if;
end $$;

create or replace function public.assign_user_profile_id()
returns trigger as $$
begin
  if new.user_id is null or new.user_id = '' then
    new.user_id := 'U' || nextval('public.user_profile_id_seq')::text;
  end if;
  return new;
end;
$$ language plpgsql;

drop trigger if exists trg_assign_user_profile_id on public.user_profiles;

create trigger trg_assign_user_profile_id
before insert on public.user_profiles
for each row execute function public.assign_user_profile_id();

create or replace function public.handle_new_auth_user()
returns trigger as $$
declare
    new_user_id uuid;
    existing_workspace_id uuid;
    name_hint text := split_part(new.email, '@', 1);
    display_name text;
    workspace_slug text;
begin
    select id into new_user_id from public.users where auth_user_id = new.id;

    if new_user_id is null then
        insert into public.users (auth_user_id, email, full_name, avatar_url)
        values (
            new.id,
            new.email,
            coalesce(new.raw_user_meta_data->>'full_name', name_hint),
            new.raw_user_meta_data->>'avatar_url'
        ) returning id into new_user_id;
    end if;

    if to_regclass('public.user_profiles') is not null then
        insert into public.user_profiles (id, email, full_name, avatar_url)
        values (
            new.id,
            new.email,
            coalesce(new.raw_user_meta_data->>'full_name', name_hint),
            new.raw_user_meta_data->>'avatar_url'
        )
        on conflict (id) do update
            set email = excluded.email,
                full_name = excluded.full_name,
                avatar_url = excluded.avatar_url;
    end if;

    select id into existing_workspace_id from public.workspaces where owner_id = new_user_id limit 1;

    if existing_workspace_id is null then
        display_name := coalesce(new.raw_user_meta_data->>'full_name', name_hint);
        workspace_slug := public.generate_workspace_slug(name_hint);

        insert into public.workspaces (name, slug, owner_id, is_trial)
        values (
            display_name || '''s Workspace',
            workspace_slug,
            new_user_id,
            true
        ) returning id into existing_workspace_id;
    end if;

    insert into public.workspace_members (workspace_id, user_id, role, is_active)
    values (existing_workspace_id, new_user_id, 'owner', true)
    on conflict (workspace_id, user_id) do update
        set role = excluded.role,
            is_active = true,
            joined_at = coalesce(workspace_members.joined_at, now());

    return new;
end;
$$ language plpgsql security definer set search_path = public, auth;

commit;
