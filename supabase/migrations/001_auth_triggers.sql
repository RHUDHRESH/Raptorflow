-- 001_auth_triggers.sql
-- Purpose: bootstrap automatic profile + workspace creation for new Supabase auth users.
-- Status: schema-aligned trigger referencing canonical users/workspaces/workspace_members tables.

begin;

drop trigger if exists trg_handle_new_auth_user on auth.users;

-- -----------------------------------------------------------------------------
-- Helper to generate unique workspace slugs
-- -----------------------------------------------------------------------------
create or replace function public.generate_workspace_slug(base text)
returns text as $$
declare
    sanitized text := lower(regexp_replace(base, '[^a-z0-9]+', '-', 'g'));
    candidate text;
begin
    loop
        candidate := sanitized || '-' || substr(md5(gen_random_uuid()::text), 1, 8);
        exit when not exists (select 1 from public.workspaces where slug = candidate);
    end loop;
    return candidate;
end;
$$ language plpgsql security definer;

-- -----------------------------------------------------------------------------
-- Function: handle_new_auth_user
-- Creates missing public.users/workspaces/workspace_members rows when auth.users inserts occur
-- -----------------------------------------------------------------------------
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

create trigger trg_handle_new_auth_user
after insert on auth.users
for each row execute function public.handle_new_auth_user();

commit;
