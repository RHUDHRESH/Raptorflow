-- =====================================================
-- MIGRATION 014: Fix Function Search Path Security
-- =====================================================

-- Setting search_path prevents schema injection attacks
-- https://www.postgresql.org/docs/current/ddl-schemas.html#DDL-SCHEMAS-PATH

-- Helper functions
CREATE OR REPLACE FUNCTION public.get_user_org_ids()
RETURNS UUID[] 
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog, public
STABLE
AS $$
  SELECT ARRAY_AGG(organization_id)
  FROM public.organization_members
  WHERE user_id = auth.uid() AND is_active = true AND removed_at IS NULL;
$$;

CREATE OR REPLACE FUNCTION public.is_org_member(org_id UUID)
RETURNS BOOLEAN
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog, public
STABLE
AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.organization_members
    WHERE organization_id = org_id
    AND user_id = auth.uid()
    AND is_active = true
    AND removed_at IS NULL
  );
$$;

CREATE OR REPLACE FUNCTION public.is_org_admin(org_id UUID)
RETURNS BOOLEAN
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog, public
STABLE
AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.organization_members
    WHERE organization_id = org_id
    AND user_id = auth.uid()
    AND role IN ('owner', 'admin')
    AND is_active = true
    AND removed_at IS NULL
  );
$$;

-- Trigger functions
CREATE OR REPLACE FUNCTION public.update_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
SET search_path = pg_catalog, public
AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public
AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name, avatar_url)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email),
    NEW.raw_user_meta_data->>'avatar_url'
  );
  RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION public.update_storage_quota()
RETURNS TRIGGER
LANGUAGE plpgsql
SET search_path = pg_catalog, public
AS $$
DECLARE
  quota_record RECORD;
BEGIN
  SELECT * INTO quota_record
  FROM public.storage_quotas
  WHERE organization_id = NEW.organization_id;

  IF TG_OP = 'INSERT' THEN
    UPDATE public.storage_quotas
    SET used_bytes = used_bytes + NEW.size_bytes
    WHERE organization_id = NEW.organization_id;
  ELSIF TG_OP = 'UPDATE' THEN
    UPDATE public.storage_quotas
    SET used_bytes = used_bytes - OLD.size_bytes + NEW.size_bytes
    WHERE organization_id = NEW.organization_id;
  ELSIF TG_OP = 'DELETE' THEN
    UPDATE public.storage_quotas
    SET used_bytes = used_bytes - OLD.size_bytes
    WHERE organization_id = OLD.organization_id;
  END IF;

  RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION public.refresh_materialized_views()
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public
AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY public.mv_subscription_stats;
  REFRESH MATERIALIZED VIEW CONCURRENTLY public.mv_org_metrics;
END;
$$;
