# Infrastructure: Views & Functions

## Materialized Views
Used to cache heavy aggregations for dashboards.

### `public.mv_subscription_stats`
-   Aggregates subscriptions by plan and status.
-   Used for: Admin dashboard revenue overview.

### `public.mv_org_metrics`
-   Aggregates generic stats per organization (member count, campaign count).
-   Used for: Platform stats.

### Refresh Policy
Trigger or scheduled job calls `refresh_materialized_views()` to update data concurrently.

## Core Functions

### Logic
-   `handle_new_user()`: Trigger on `auth.users` insert. Creates public profile.
-   `update_storage_quota()`: Trigger on `assets` table. Updates usage stats.

### Utilities
-   `update_updated_at()`: Standard timestamp updater.
