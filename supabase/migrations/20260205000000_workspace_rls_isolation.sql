-- Workspace-based RLS isolation for business contexts, BCM, onboarding, and payments

BEGIN;

-- Helper: match auth user to internal user identifiers
CREATE OR REPLACE FUNCTION public.auth_user_matches(p_user_id uuid)
RETURNS boolean
LANGUAGE plpgsql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    matches boolean := false;
BEGIN
    IF p_user_id IS NULL OR auth.uid() IS NULL THEN
        RETURN false;
    END IF;

    IF p_user_id = auth.uid() THEN
        RETURN true;
    END IF;

    IF to_regclass('public.users') IS NOT NULL THEN
        SELECT EXISTS (
            SELECT 1 FROM public.users u
            WHERE u.id = p_user_id
              AND u.auth_user_id = auth.uid()
        ) INTO matches;
        IF matches THEN
            RETURN true;
        END IF;
    END IF;

    IF to_regclass('public.profiles') IS NOT NULL THEN
        SELECT p_user_id = auth.uid() INTO matches;
        IF matches THEN
            RETURN true;
        END IF;
    END IF;

    RETURN false;
END;
$$;

-- Helper: verify auth user is in the workspace
CREATE OR REPLACE FUNCTION public.is_workspace_member(p_workspace_id uuid)
RETURNS boolean
LANGUAGE plpgsql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    member_match boolean := false;
    owner_match boolean := false;
BEGIN
    IF p_workspace_id IS NULL OR auth.uid() IS NULL THEN
        RETURN false;
    END IF;

    IF to_regclass('public.workspace_members') IS NOT NULL THEN
        IF to_regclass('public.users') IS NOT NULL THEN
            EXECUTE
                'SELECT EXISTS (
                    SELECT 1
                    FROM public.workspace_members wm
                    JOIN public.users u ON u.id = wm.user_id
                    WHERE wm.workspace_id = $1
                      AND wm.is_active = TRUE
                      AND u.auth_user_id = auth.uid()
                )'
            INTO member_match
            USING p_workspace_id;
        ELSIF to_regclass('public.profiles') IS NOT NULL THEN
            EXECUTE
                'SELECT EXISTS (
                    SELECT 1
                    FROM public.workspace_members wm
                    JOIN public.profiles p ON p.id = wm.user_id
                    WHERE wm.workspace_id = $1
                      AND wm.is_active = TRUE
                      AND p.id = auth.uid()
                )'
            INTO member_match
            USING p_workspace_id;
        END IF;
    END IF;

    IF to_regclass('public.workspaces') IS NULL THEN
        RETURN member_match;
    END IF;

    IF to_regclass('public.users') IS NOT NULL THEN
        EXECUTE
            'SELECT EXISTS (
                SELECT 1
                FROM public.workspaces w
                JOIN public.users u ON u.id = w.owner_id
                WHERE w.id = $1
                  AND u.auth_user_id = auth.uid()
            )'
        INTO owner_match
        USING p_workspace_id;
    ELSIF to_regclass('public.profiles') IS NOT NULL THEN
        EXECUTE
            'SELECT EXISTS (
                SELECT 1
                FROM public.workspaces w
                WHERE w.id = $1
                  AND w.owner_id = auth.uid()
            )'
        INTO owner_match
        USING p_workspace_id;
    ELSE
        EXECUTE
            'SELECT EXISTS (
                SELECT 1
                FROM public.workspaces w
                WHERE w.id = $1
                  AND w.owner_id = auth.uid()
            )'
        INTO owner_match
        USING p_workspace_id;
    END IF;

    RETURN member_match OR owner_match;
END;
$$;

-- RLS for business_contexts (plural)
DO $$
DECLARE
    has_workspace_id boolean;
    has_user_id boolean;
    policy_check text;
BEGIN
    IF to_regclass('public.business_contexts') IS NOT NULL THEN
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'business_contexts'
              AND column_name = 'workspace_id'
        ) INTO has_workspace_id;
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'business_contexts'
              AND column_name = 'user_id'
        ) INTO has_user_id;

        EXECUTE 'ALTER TABLE public.business_contexts ENABLE ROW LEVEL SECURITY';
        EXECUTE 'DROP POLICY IF EXISTS "business_contexts_workspace_isolation_select" ON public.business_contexts';
        EXECUTE 'DROP POLICY IF EXISTS "business_contexts_workspace_isolation_insert" ON public.business_contexts';
        EXECUTE 'DROP POLICY IF EXISTS "business_contexts_workspace_isolation_update" ON public.business_contexts';
        EXECUTE 'DROP POLICY IF EXISTS "business_contexts_workspace_isolation_delete" ON public.business_contexts';

        IF has_workspace_id THEN
            policy_check := 'auth.uid() IS NOT NULL AND public.is_workspace_member(workspace_id)';
        ELSIF has_user_id THEN
            policy_check := 'auth.uid() IS NOT NULL AND public.auth_user_matches(user_id)';
        ELSE
            policy_check := 'false';
        END IF;

        EXECUTE format(
            'CREATE POLICY "business_contexts_workspace_isolation_select" ON public.business_contexts FOR SELECT USING (%s)',
            policy_check
        );
        EXECUTE format(
            'CREATE POLICY "business_contexts_workspace_isolation_insert" ON public.business_contexts FOR INSERT WITH CHECK (%s)',
            policy_check
        );
        EXECUTE format(
            'CREATE POLICY "business_contexts_workspace_isolation_update" ON public.business_contexts FOR UPDATE USING (%s)',
            policy_check
        );
        EXECUTE format(
            'CREATE POLICY "business_contexts_workspace_isolation_delete" ON public.business_contexts FOR DELETE USING (%s)',
            policy_check
        );
    END IF;
END $$;

-- RLS for business_context (singular)
DO $$
DECLARE
    has_workspace_id boolean;
    has_user_id boolean;
    policy_check text;
BEGIN
    IF to_regclass('public.business_context') IS NOT NULL THEN
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'business_context'
              AND column_name = 'workspace_id'
        ) INTO has_workspace_id;
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'business_context'
              AND column_name = 'user_id'
        ) INTO has_user_id;

        EXECUTE 'ALTER TABLE public.business_context ENABLE ROW LEVEL SECURITY';
        EXECUTE 'DROP POLICY IF EXISTS "business_context_workspace_isolation_select" ON public.business_context';
        EXECUTE 'DROP POLICY IF EXISTS "business_context_workspace_isolation_insert" ON public.business_context';
        EXECUTE 'DROP POLICY IF EXISTS "business_context_workspace_isolation_update" ON public.business_context';
        EXECUTE 'DROP POLICY IF EXISTS "business_context_workspace_isolation_delete" ON public.business_context';

        IF has_workspace_id THEN
            policy_check := 'auth.uid() IS NOT NULL AND public.is_workspace_member(workspace_id)';
        ELSIF has_user_id THEN
            policy_check := 'auth.uid() IS NOT NULL AND public.auth_user_matches(user_id)';
        ELSE
            policy_check := 'false';
        END IF;

        EXECUTE format(
            'CREATE POLICY "business_context_workspace_isolation_select" ON public.business_context FOR SELECT USING (%s)',
            policy_check
        );
        EXECUTE format(
            'CREATE POLICY "business_context_workspace_isolation_insert" ON public.business_context FOR INSERT WITH CHECK (%s)',
            policy_check
        );
        EXECUTE format(
            'CREATE POLICY "business_context_workspace_isolation_update" ON public.business_context FOR UPDATE USING (%s)',
            policy_check
        );
        EXECUTE format(
            'CREATE POLICY "business_context_workspace_isolation_delete" ON public.business_context FOR DELETE USING (%s)',
            policy_check
        );
    END IF;
END $$;

-- RLS for bcm_manifests
DO $$
DECLARE
    has_workspace_id boolean;
    has_user_id boolean;
    policy_check text;
BEGIN
    IF to_regclass('public.bcm_manifests') IS NOT NULL THEN
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'bcm_manifests'
              AND column_name = 'workspace_id'
        ) INTO has_workspace_id;
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'bcm_manifests'
              AND column_name = 'user_id'
        ) INTO has_user_id;

        EXECUTE 'ALTER TABLE public.bcm_manifests ENABLE ROW LEVEL SECURITY';
        EXECUTE 'DROP POLICY IF EXISTS "bcm_manifests_workspace_isolation_select" ON public.bcm_manifests';
        EXECUTE 'DROP POLICY IF EXISTS "bcm_manifests_workspace_isolation_insert" ON public.bcm_manifests';
        EXECUTE 'DROP POLICY IF EXISTS "bcm_manifests_workspace_isolation_update" ON public.bcm_manifests';
        EXECUTE 'DROP POLICY IF EXISTS "bcm_manifests_workspace_isolation_delete" ON public.bcm_manifests';

        IF has_workspace_id THEN
            policy_check := 'auth.uid() IS NOT NULL AND public.is_workspace_member(workspace_id)';
        ELSIF has_user_id THEN
            policy_check := 'auth.uid() IS NOT NULL AND public.auth_user_matches(user_id)';
        ELSE
            policy_check := 'false';
        END IF;

        EXECUTE format(
            'CREATE POLICY "bcm_manifests_workspace_isolation_select" ON public.bcm_manifests FOR SELECT USING (%s)',
            policy_check
        );
        EXECUTE format(
            'CREATE POLICY "bcm_manifests_workspace_isolation_insert" ON public.bcm_manifests FOR INSERT WITH CHECK (%s)',
            policy_check
        );
        EXECUTE format(
            'CREATE POLICY "bcm_manifests_workspace_isolation_update" ON public.bcm_manifests FOR UPDATE USING (%s)',
            policy_check
        );
        EXECUTE format(
            'CREATE POLICY "bcm_manifests_workspace_isolation_delete" ON public.bcm_manifests FOR DELETE USING (%s)',
            policy_check
        );
    END IF;
END $$;

-- RLS for user_onboarding
DO $$
DECLARE
    has_user_id boolean;
BEGIN
    IF to_regclass('public.user_onboarding') IS NOT NULL THEN
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'user_onboarding'
              AND column_name = 'user_id'
        ) INTO has_user_id;

        EXECUTE 'ALTER TABLE public.user_onboarding ENABLE ROW LEVEL SECURITY';
        EXECUTE 'DROP POLICY IF EXISTS "user_onboarding_owner_select" ON public.user_onboarding';
        EXECUTE 'DROP POLICY IF EXISTS "user_onboarding_owner_insert" ON public.user_onboarding';
        EXECUTE 'DROP POLICY IF EXISTS "user_onboarding_owner_update" ON public.user_onboarding';
        EXECUTE 'DROP POLICY IF EXISTS "user_onboarding_owner_delete" ON public.user_onboarding';

        IF has_user_id THEN
            EXECUTE 'CREATE POLICY "user_onboarding_owner_select" ON public.user_onboarding FOR SELECT USING (auth.uid() IS NOT NULL AND public.auth_user_matches(user_id))';
            EXECUTE 'CREATE POLICY "user_onboarding_owner_insert" ON public.user_onboarding FOR INSERT WITH CHECK (auth.uid() IS NOT NULL AND public.auth_user_matches(user_id))';
            EXECUTE 'CREATE POLICY "user_onboarding_owner_update" ON public.user_onboarding FOR UPDATE USING (auth.uid() IS NOT NULL AND public.auth_user_matches(user_id))';
            EXECUTE 'CREATE POLICY "user_onboarding_owner_delete" ON public.user_onboarding FOR DELETE USING (auth.uid() IS NOT NULL AND public.auth_user_matches(user_id))';
        END IF;
    END IF;
END $$;

-- RLS for payments
DO $$
DECLARE
    has_workspace_id boolean;
    has_user_id boolean;
    policy_check text;
BEGIN
    IF to_regclass('public.payments') IS NOT NULL THEN
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'payments'
              AND column_name = 'workspace_id'
        ) INTO has_workspace_id;
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'payments'
              AND column_name = 'user_id'
        ) INTO has_user_id;

        EXECUTE 'ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY';
        EXECUTE 'DROP POLICY IF EXISTS "payments_workspace_isolation_select" ON public.payments';
        EXECUTE 'DROP POLICY IF EXISTS "payments_workspace_isolation_insert" ON public.payments';
        EXECUTE 'DROP POLICY IF EXISTS "payments_workspace_isolation_update" ON public.payments';
        EXECUTE 'DROP POLICY IF EXISTS "payments_workspace_isolation_delete" ON public.payments';

        IF has_workspace_id THEN
            policy_check := 'auth.uid() IS NOT NULL AND public.is_workspace_member(workspace_id)';
        ELSIF has_user_id THEN
            policy_check := 'auth.uid() IS NOT NULL AND public.auth_user_matches(user_id)';
        ELSE
            policy_check := 'false';
        END IF;

        EXECUTE format(
            'CREATE POLICY "payments_workspace_isolation_select" ON public.payments FOR SELECT USING (%s)',
            policy_check
        );
        EXECUTE format(
            'CREATE POLICY "payments_workspace_isolation_insert" ON public.payments FOR INSERT WITH CHECK (%s)',
            policy_check
        );
        EXECUTE format(
            'CREATE POLICY "payments_workspace_isolation_update" ON public.payments FOR UPDATE USING (%s)',
            policy_check
        );
        EXECUTE format(
            'CREATE POLICY "payments_workspace_isolation_delete" ON public.payments FOR DELETE USING (%s)',
            policy_check
        );
    END IF;
END $$;

COMMIT;
