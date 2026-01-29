-- RLS verification queries for workspace isolation
-- Replace the UUID placeholders with real values from your environment.

-- Example variables:
--   :auth_user_id_a (auth.uid for user A)
--   :auth_user_id_b (auth.uid for user B)
--   :workspace_id_a (workspace owned/joined by user A)
--   :workspace_id_b (workspace owned/joined by user B)

-- Ensure RLS is enforced for authenticated users in workspace A
SELECT set_config('request.jwt.claim.role', 'authenticated', true);
SELECT set_config('request.jwt.claim.sub', ':auth_user_id_a', true);

-- Business contexts (plural)
SELECT * FROM public.business_contexts WHERE workspace_id = ':workspace_id_a';
SELECT * FROM public.business_contexts WHERE workspace_id = ':workspace_id_b';

-- Business context (singular)
SELECT * FROM public.business_context WHERE workspace_id = ':workspace_id_a';
SELECT * FROM public.business_context WHERE workspace_id = ':workspace_id_b';

-- BCM manifests
SELECT * FROM public.bcm_manifests WHERE workspace_id = ':workspace_id_a';
SELECT * FROM public.bcm_manifests WHERE workspace_id = ':workspace_id_b';

-- Onboarding records (user scoped)
SELECT * FROM public.user_onboarding WHERE user_id = ':auth_user_id_a';
SELECT * FROM public.user_onboarding WHERE user_id = ':auth_user_id_b';

-- Payments (user scoped, or workspace if column exists)
SELECT * FROM public.payments WHERE user_id = ':auth_user_id_a';
SELECT * FROM public.payments WHERE user_id = ':auth_user_id_b';

-- Repeat for user B
SELECT set_config('request.jwt.claim.sub', ':auth_user_id_b', true);

SELECT * FROM public.business_contexts WHERE workspace_id = ':workspace_id_b';
SELECT * FROM public.business_contexts WHERE workspace_id = ':workspace_id_a';

SELECT * FROM public.business_context WHERE workspace_id = ':workspace_id_b';
SELECT * FROM public.business_context WHERE workspace_id = ':workspace_id_a';

SELECT * FROM public.bcm_manifests WHERE workspace_id = ':workspace_id_b';
SELECT * FROM public.bcm_manifests WHERE workspace_id = ':workspace_id_a';

SELECT * FROM public.user_onboarding WHERE user_id = ':auth_user_id_b';
SELECT * FROM public.user_onboarding WHERE user_id = ':auth_user_id_a';

SELECT * FROM public.payments WHERE user_id = ':auth_user_id_b';
SELECT * FROM public.payments WHERE user_id = ':auth_user_id_a';
