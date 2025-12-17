-- =====================================================
-- KITS: RPC SURFACE FOR SAFE VERSIONING + LOCKED-ONLY READS
-- Agents run with service_role, so this RPC surface is the enforcement boundary.
-- =====================================================

CREATE OR REPLACE FUNCTION public.next_kit_version(p_organization_id uuid, p_kit_type public.kit_type)
RETURNS integer
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public
AS $$
DECLARE
  v_next integer;
BEGIN
  INSERT INTO public.kit_version_counters (organization_id, kit_type, next_version)
  VALUES (p_organization_id, p_kit_type, 1)
  ON CONFLICT (organization_id, kit_type) DO NOTHING;

  SELECT next_version
  INTO v_next
  FROM public.kit_version_counters
  WHERE organization_id = p_organization_id
    AND kit_type = p_kit_type
  FOR UPDATE;

  UPDATE public.kit_version_counters
  SET next_version = next_version + 1
  WHERE organization_id = p_organization_id
    AND kit_type = p_kit_type;

  RETURN v_next;
END;
$$;

CREATE OR REPLACE FUNCTION public.create_kit_draft(
  p_organization_id uuid,
  p_kit_type public.kit_type,
  p_schema_version text,
  p_data jsonb
)
RETURNS public.kits
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public
AS $$
DECLARE
  v_role text;
  v_version integer;
  v_row public.kits;
BEGIN
  v_role := auth.role();

  IF v_role <> 'service_role' THEN
    IF auth.uid() IS NULL OR NOT public.is_org_member(p_organization_id) THEN
      RAISE EXCEPTION 'not authorized';
    END IF;

    IF NOT EXISTS (
      SELECT 1
      FROM public.organization_members om
      WHERE om.organization_id = p_organization_id
        AND om.user_id = auth.uid()
        AND om.is_active = true
        AND om.removed_at IS NULL
        AND om.role IN ('owner','admin','editor')
    ) THEN
      RAISE EXCEPTION 'insufficient role';
    END IF;
  END IF;

  v_version := public.next_kit_version(p_organization_id, p_kit_type);

  INSERT INTO public.kits (
    organization_id,
    kit_type,
    schema_version,
    version,
    status,
    created_by,
    data
  )
  VALUES (
    p_organization_id,
    p_kit_type,
    p_schema_version,
    v_version,
    'draft',
    auth.uid(),
    COALESCE(p_data, '{}'::jsonb)
  )
  RETURNING * INTO v_row;

  RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION public.transition_kit_status(
  p_kit_id uuid,
  p_new_status public.kit_status
)
RETURNS public.kits
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public
AS $$
DECLARE
  v_role text;
  v_org_id uuid;
  v_kit_type public.kit_type;
  v_row public.kits;
BEGIN
  v_role := auth.role();

  SELECT organization_id, kit_type
  INTO v_org_id, v_kit_type
  FROM public.kits
  WHERE id = p_kit_id;

  IF v_org_id IS NULL THEN
    RAISE EXCEPTION 'kit not found';
  END IF;

  IF v_role <> 'service_role' THEN
    IF auth.uid() IS NULL OR NOT public.is_org_member(v_org_id) THEN
      RAISE EXCEPTION 'not authorized';
    END IF;

    IF NOT EXISTS (
      SELECT 1
      FROM public.organization_members om
      WHERE om.organization_id = v_org_id
        AND om.user_id = auth.uid()
        AND om.is_active = true
        AND om.removed_at IS NULL
        AND om.role IN ('owner','admin','editor')
    ) THEN
      RAISE EXCEPTION 'insufficient role';
    END IF;
  END IF;

  UPDATE public.kits
  SET status = p_new_status
  WHERE id = p_kit_id
  RETURNING * INTO v_row;

  IF v_row.id IS NULL THEN
    RAISE EXCEPTION 'kit status update failed';
  END IF;

  IF p_new_status = 'locked' THEN
    INSERT INTO public.kit_current (organization_id, kit_type, kit_id)
    VALUES (v_org_id, v_kit_type, p_kit_id)
    ON CONFLICT (organization_id, kit_type)
    DO UPDATE SET kit_id = EXCLUDED.kit_id, updated_at = NOW();
  END IF;

  RETURN v_row;
END;
$$;

CREATE OR REPLACE VIEW public.current_locked_kits AS
SELECT
  kc.organization_id,
  kc.kit_type,
  k.id AS kit_id,
  k.schema_version,
  k.version,
  k.locked_at,
  k.locked_by,
  k.data,
  k.updated_at
FROM public.kit_current kc
JOIN public.kits k
  ON k.id = kc.kit_id
WHERE k.status = 'locked';

CREATE OR REPLACE FUNCTION public.get_locked_kit_bundle(p_organization_id uuid)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public
AS $$
DECLARE
  v_role text;
  v_bundle jsonb;
  v_missing text[];
BEGIN
  v_role := auth.role();

  IF v_role <> 'service_role' THEN
    IF auth.uid() IS NULL OR NOT public.is_org_member(p_organization_id) THEN
      RAISE EXCEPTION 'not authorized';
    END IF;
  END IF;

  v_bundle := (
    SELECT jsonb_build_object(
      'brand', (SELECT to_jsonb(ck) FROM public.current_locked_kits ck WHERE ck.organization_id = p_organization_id AND ck.kit_type = 'brand' LIMIT 1),
      'offer', (SELECT to_jsonb(ck) FROM public.current_locked_kits ck WHERE ck.organization_id = p_organization_id AND ck.kit_type = 'offer' LIMIT 1),
      'proof', (SELECT to_jsonb(ck) FROM public.current_locked_kits ck WHERE ck.organization_id = p_organization_id AND ck.kit_type = 'proof' LIMIT 1),
      'audience', (SELECT to_jsonb(ck) FROM public.current_locked_kits ck WHERE ck.organization_id = p_organization_id AND ck.kit_type = 'audience' LIMIT 1),
      'channel', (SELECT to_jsonb(ck) FROM public.current_locked_kits ck WHERE ck.organization_id = p_organization_id AND ck.kit_type = 'channel' LIMIT 1),
      'ops', (SELECT to_jsonb(ck) FROM public.current_locked_kits ck WHERE ck.organization_id = p_organization_id AND ck.kit_type = 'ops' LIMIT 1)
    )
  );

  v_missing := ARRAY[]::text[];

  IF (v_bundle->'brand') IS NULL OR (v_bundle->'brand') = 'null'::jsonb THEN v_missing := array_append(v_missing, 'brand'); END IF;
  IF (v_bundle->'offer') IS NULL OR (v_bundle->'offer') = 'null'::jsonb THEN v_missing := array_append(v_missing, 'offer'); END IF;
  IF (v_bundle->'proof') IS NULL OR (v_bundle->'proof') = 'null'::jsonb THEN v_missing := array_append(v_missing, 'proof'); END IF;
  IF (v_bundle->'audience') IS NULL OR (v_bundle->'audience') = 'null'::jsonb THEN v_missing := array_append(v_missing, 'audience'); END IF;
  IF (v_bundle->'channel') IS NULL OR (v_bundle->'channel') = 'null'::jsonb THEN v_missing := array_append(v_missing, 'channel'); END IF;
  IF (v_bundle->'ops') IS NULL OR (v_bundle->'ops') = 'null'::jsonb THEN v_missing := array_append(v_missing, 'ops'); END IF;

  IF array_length(v_missing, 1) IS NOT NULL THEN
    RAISE EXCEPTION 'KIT_MISSING_LOCKED:%', array_to_string(v_missing, ',');
  END IF;

  RETURN v_bundle;
END;
$$;

GRANT EXECUTE ON FUNCTION public.next_kit_version(uuid, public.kit_type) TO authenticated;
GRANT EXECUTE ON FUNCTION public.create_kit_draft(uuid, public.kit_type, text, jsonb) TO authenticated;
GRANT EXECUTE ON FUNCTION public.transition_kit_status(uuid, public.kit_status) TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_locked_kit_bundle(uuid) TO authenticated;

GRANT EXECUTE ON FUNCTION public.next_kit_version(uuid, public.kit_type) TO service_role;
GRANT EXECUTE ON FUNCTION public.create_kit_draft(uuid, public.kit_type, text, jsonb) TO service_role;
GRANT EXECUTE ON FUNCTION public.transition_kit_status(uuid, public.kit_status) TO service_role;
GRANT EXECUTE ON FUNCTION public.get_locked_kit_bundle(uuid) TO service_role;

GRANT SELECT ON public.current_locked_kits TO authenticated;
GRANT SELECT ON public.current_locked_kits TO service_role;
