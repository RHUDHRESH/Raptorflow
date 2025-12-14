# Database Indexes & Performance

Overview of the indexing strategy used to ensure high performance at scale.

## Indexing Strategy

1.  **Foreign Keys**: All FK columns (`organization_id`, `user_id`, etc.) are indexed to speed up joins and RLS lookups.
2.  **Partial Indexes**: Used for status flags (e.g., `WHERE deleted_at IS NULL` or `WHERE status = 'active'`) to keep index size small.
3.  **BRIN Indexes**: Block Range INdexes used on timestamp columns (`created_at`, `occurred_at`) for large time-series tables (logs, metrics). This saves significant space compared to B-Tree.
4.  **GIN Indexes**: Used for `JSONB` columns (`settings`, `metadata`) to allow querying specific keys.
5.  **Unique Constraints**: Enforced on business keys (`slug`, `email`, `code`) for data integrity.

## Key Indexes

### High-Traffic
-   `idx_org_members_user`: Critical for initial dashboard load (finding user's orgs).
-   `idx_org_members_org`: Critical for checking membership validity.
-   `idx_audit_created` (BRIN): Efficiently querying log ranges.

### Time-Series (Partitioned)
-   `audit_logs`
-   `activity_events`
-   `metrics`

These tables use **declarative partitioning** by date range (quarterly) to manage table bloat and allow efficient dropping of old data if needed.
