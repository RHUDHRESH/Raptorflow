# Audit Logs & Activity Tracking

RaptorFlow maintains a comprehensive audit trail for compliance and security.

## Architecture
Audit logs are stored in a **partitioned table** (`public.audit_logs`) to handle high write volume.
-   **Partitioning**: By range on `created_at` (Quarterly partitions: `audit_logs_2025_q1`, etc.)
-   **Storage**: Uses BRIN indexes for efficiency.

## Schema

### `public.audit_logs`
-   `id`: UUID
-   `created_at`: TIMESTAMPTZ (Partition Key)
-   `actor`: `user_id`, `organization_id`
-   `action`: `audit_action` (`create`, `read`, `update`, `delete`, `login`)
-   `resource`: `resource_type` (e.g., 'campaign'), `resource_id`
-   `changes`:
    -   `old_values`: JSONB (snapshot before update)
    -   `new_values`: JSONB (snapshot after update)
-   `context`: `ip_address`, `user_agent`

## Trigger Implementation
Use the `audit_log_trigger` (if implemented) or application level logic to insert into this table.
For critical computations, `activity_events` tracks lower-level user interactions (page views, button clicks) separate from compliance audit logs.
