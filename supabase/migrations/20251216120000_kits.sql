DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'kit_type') THEN
    CREATE TYPE public.kit_type AS ENUM ('brand','offer','proof','audience','channel','ops');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'kit_status') THEN
    CREATE TYPE public.kit_status AS ENUM ('draft','review','locked');
  END IF;
END
$$;

CREATE TABLE IF NOT EXISTS public.kits (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
  kit_type public.kit_type NOT NULL,
  schema_version TEXT NOT NULL,
  version INTEGER NOT NULL CHECK (version > 0),
  status public.kit_status NOT NULL DEFAULT 'draft',
  locked_at TIMESTAMPTZ,
  locked_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  data JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT kits_version_unique UNIQUE (organization_id, kit_type, version)
);

CREATE TABLE IF NOT EXISTS public.kit_version_counters (
  organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
  kit_type public.kit_type NOT NULL,
  next_version INTEGER NOT NULL DEFAULT 1 CHECK (next_version > 0),
  PRIMARY KEY (organization_id, kit_type)
);

CREATE TABLE IF NOT EXISTS public.kit_current (
  organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
  kit_type public.kit_type NOT NULL,
  kit_id UUID NOT NULL REFERENCES public.kits(id) ON DELETE RESTRICT,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (organization_id, kit_type)
);

CREATE INDEX IF NOT EXISTS kits_org_idx ON public.kits (organization_id, kit_type);
CREATE INDEX IF NOT EXISTS kits_locked_idx
  ON public.kits (organization_id, kit_type, version DESC)
  INCLUDE (id, schema_version, updated_at)
  WHERE status = 'locked';

CREATE OR REPLACE FUNCTION public.kits_enforce_state_and_shape()
RETURNS TRIGGER
LANGUAGE plpgsql
SET search_path = pg_catalog, public
AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    IF NEW.status IS DISTINCT FROM 'draft' THEN
      RAISE EXCEPTION 'kits must be inserted with status draft';
    END IF;

    IF NEW.locked_at IS NOT NULL OR NEW.locked_by IS NOT NULL THEN
      RAISE EXCEPTION 'locked fields must be null on insert';
    END IF;

    IF NEW.created_by IS NULL THEN
      NEW.created_by = auth.uid();
    END IF;

    RETURN NEW;
  END IF;

  IF TG_OP = 'UPDATE' THEN
    IF OLD.status = 'locked' THEN
      RAISE EXCEPTION 'locked kit rows are immutable';
    END IF;

    IF NEW.status IS DISTINCT FROM OLD.status THEN
      IF NOT (
        (OLD.status = 'draft' AND NEW.status = 'review') OR
        (OLD.status = 'review' AND NEW.status = 'locked')
      ) THEN
        RAISE EXCEPTION 'invalid kit status transition: % -> %', OLD.status, NEW.status;
      END IF;
    END IF;

    IF NEW.status = 'locked' AND OLD.status IS DISTINCT FROM 'locked' THEN
      IF NEW.locked_at IS NULL THEN
        NEW.locked_at = NOW();
      END IF;

      IF NEW.locked_by IS NULL THEN
        NEW.locked_by = auth.uid();
      END IF;

      IF NEW.kit_type = 'brand' THEN
        IF jsonb_typeof(NEW.data->'voice_profile') IS DISTINCT FROM 'object' THEN
          RAISE EXCEPTION 'brand kit requires data.voice_profile object when locking';
        END IF;
        IF jsonb_typeof(NEW.data->'lexicon'->'taboo_words') IS DISTINCT FROM 'array' THEN
          RAISE EXCEPTION 'brand kit requires data.lexicon.taboo_words array when locking';
        END IF;
      ELSIF NEW.kit_type = 'offer' THEN
        IF jsonb_typeof(NEW.data->'pricing_tiers') IS DISTINCT FROM 'array' OR jsonb_array_length(NEW.data->'pricing_tiers') = 0 THEN
          RAISE EXCEPTION 'offer kit requires non-empty data.pricing_tiers array when locking';
        END IF;
      ELSIF NEW.kit_type = 'proof' THEN
        IF jsonb_typeof(NEW.data->'claims') IS DISTINCT FROM 'array' THEN
          RAISE EXCEPTION 'proof kit requires data.claims array when locking';
        END IF;
      ELSIF NEW.kit_type = 'audience' THEN
        IF jsonb_typeof(NEW.data->'cohorts') IS DISTINCT FROM 'array' OR jsonb_array_length(NEW.data->'cohorts') = 0 THEN
          RAISE EXCEPTION 'audience kit requires non-empty data.cohorts array when locking';
        END IF;
      ELSIF NEW.kit_type = 'channel' THEN
        IF jsonb_typeof(NEW.data->'channels') IS DISTINCT FROM 'array' OR jsonb_array_length(NEW.data->'channels') = 0 THEN
          RAISE EXCEPTION 'channel kit requires non-empty data.channels array when locking';
        END IF;
      ELSIF NEW.kit_type = 'ops' THEN
        IF jsonb_typeof(NEW.data->'team') IS DISTINCT FROM 'array' OR jsonb_array_length(NEW.data->'team') = 0 THEN
          RAISE EXCEPTION 'ops kit requires non-empty data.team array when locking';
        END IF;
        IF jsonb_typeof(NEW.data->'approval_workflow'->'steps') IS DISTINCT FROM 'array' OR jsonb_array_length(NEW.data->'approval_workflow'->'steps') = 0 THEN
          RAISE EXCEPTION 'ops kit requires non-empty data.approval_workflow.steps array when locking';
        END IF;
      ELSE
        RAISE EXCEPTION 'unknown kit_type: %', NEW.kit_type;
      END IF;
    END IF;

    RETURN NEW;
  END IF;

  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_kits_enforce ON public.kits;
CREATE TRIGGER trg_kits_enforce
  BEFORE INSERT OR UPDATE ON public.kits
  FOR EACH ROW EXECUTE FUNCTION public.kits_enforce_state_and_shape();

DROP TRIGGER IF EXISTS trg_kits_updated ON public.kits;
CREATE TRIGGER trg_kits_updated
  BEFORE UPDATE ON public.kits
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

DROP TRIGGER IF EXISTS trg_kit_current_updated ON public.kit_current;
CREATE TRIGGER trg_kit_current_updated
  BEFORE UPDATE ON public.kit_current
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

ALTER TABLE public.kits ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.kit_version_counters ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.kit_current ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS kits_select ON public.kits;
CREATE POLICY kits_select ON public.kits
  FOR SELECT
  USING (public.is_org_member(organization_id));

DROP POLICY IF EXISTS kits_insert ON public.kits;
CREATE POLICY kits_insert ON public.kits
  FOR INSERT
  WITH CHECK (
    status = 'draft'
    AND EXISTS (
      SELECT 1
      FROM public.organization_members om
      WHERE om.organization_id = organization_id
        AND om.user_id = auth.uid()
        AND om.is_active = true
        AND om.removed_at IS NULL
        AND om.role IN ('owner','admin','editor')
    )
  );

DROP POLICY IF EXISTS kits_update ON public.kits;
CREATE POLICY kits_update ON public.kits
  FOR UPDATE
  USING (
    status <> 'locked'
    AND EXISTS (
      SELECT 1
      FROM public.organization_members om
      WHERE om.organization_id = organization_id
        AND om.user_id = auth.uid()
        AND om.is_active = true
        AND om.removed_at IS NULL
        AND om.role IN ('owner','admin','editor')
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1
      FROM public.organization_members om
      WHERE om.organization_id = organization_id
        AND om.user_id = auth.uid()
        AND om.is_active = true
        AND om.removed_at IS NULL
        AND om.role IN ('owner','admin','editor')
    )
  );

DROP POLICY IF EXISTS kit_current_select ON public.kit_current;
CREATE POLICY kit_current_select ON public.kit_current
  FOR SELECT
  USING (public.is_org_member(organization_id));
