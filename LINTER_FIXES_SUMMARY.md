# Supabase Linter Fixes

The following issues reported by the Supabase linter have been resolved:

## 1. Security: Function Search Path Mutable
- **Issue:** Function `public.update_updated_at_column` had a mutable search path.
- **Fix:** Altered function to set `search_path = ''`.

## 2. Performance: Auth RLS Initialization Plan
- **Issue:** RLS policies were re-evaluating `auth.uid()` for every row.
- **Fix:** Wrapped all `auth.uid()` calls with `(select auth.uid())` to allow Postgres to cache the result per query.
- **Affected Tables:** `onboarding_intake`, `agent_executions`, `shared_links`.

## 3. Performance: Multiple Permissive Policies
- **Issue:** Multiple permissive policies existed for the same role/action, causing redundant checks.
- **Fix:** Combined overlapping policies into single optimized policies.
  - `onboarding_intake`: Combined "Sales reps can view/update" and "Users can view/update" into unified "View/Update onboarding intake" policies.
  - `shared_links`: Removed redundant "Users can view own shared links" policy (covered by "Anyone can read shared links by token").

## 4. Performance: Unindexed Foreign Keys
- **Issue:** Foreign keys were missing covering indexes.
- **Fix:** Created indexes for:
  - `maneuver_prerequisites(required_capability_id)`
  - `moves(line_of_operation_id, maneuver_type_id)`
  - `onboarding_analyses(user_id)`
  - `onboarding_intake(sales_rep_id)`
  - `plans(project_id)`
  - `positioning_blueprints(analysis_id, user_id)`
  - `projects(user_id)`
  - `shared_links(sales_rep_id)`

## Outstanding Issues
- **Security: Leaked Password Protection**: This must be enabled in the Supabase Dashboard (Authentication > Security > Password protection).
- **Performance: Unused Indexes**: Most unused indexes reported by the linter have been removed to clean up the schema and improve write performance.
    - **Removed:** Indexes on `billing_history`, `autopay_subscriptions`, `assets`, `quests`, `moves` (legacy), and others.
    - **Kept:** Indexes critical for RLS (e.g., `idx_onboarding_intake_user_id`) or Foreign Keys, even if reported as unused, to prevent performance degradation on SELECT queries.
