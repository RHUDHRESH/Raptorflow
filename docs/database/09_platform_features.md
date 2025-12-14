# Platform Features: Campaigns & Cohorts

## Cohorts (Segments)
Dynamic groups of users based on rules.

### `public.cohorts`
-   `rules`: JSONB - Stored logic for segmentation (e.g., `{"country": "IN", "ltv_gt": 1000}`).
-   `member_count`: Cached count of members.

### `public.cohort_memberships`
Explicit list of members in a cohort.
-   Snapshot of the rule evaluation.
-   Supports manual additions.

## Campaigns
Marketing or engagement campaigns targeting cohorts.

### `public.campaigns`
-   `cohort_ids`: Array of UUIDs (Multi-cohort targeting).
-   `status`: Draft -> Planned -> Active -> Completed.
-   `config`: JSONB - specific settings for email/push/sms.

## Assets
File management system pointing to storage buckets.
-   `public.assets`: Metadata for files.
-   `public.storage_quotas`: Track usage per organization to enforce plan limits.
