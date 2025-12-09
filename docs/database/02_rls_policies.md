# Row Level Security (RLS) Policies

All tables in the `public` schema have RLS enabled to enforce strict multi-tenant isolation.

## Security Model

1.  **Deny by Default**: No access is granted unless an explicit policy allows it.
2.  **Organization Isolation**: A user can only access data belonging to an organization they are a member of.
3.  **Role-Based Access**: Within an organization, actions (INSERT, UPDATE, DELETE) are restricted based on the member's role (e.g., `admin`, `viewer`).

## Helper Functions

These `SECURITY DEFINER` functions are used in policies to encapsulate logic:

-   `get_user_org_ids()`: Returns array of org IDs the user belongs to.
-   `is_org_member(org_id)`: Boolean check for membership.
-   `is_org_admin(org_id)`: Boolean check for admin/owner role.

## Policy Examples

### Organizations
-   **SELECT**: `public.is_org_member(id) OR deleted_at IS NULL` (Members can see their orgs).
-   **UPDATE**: `public.is_org_admin(id)` (Only admins can update settings).

### Subscriptions
-   **SELECT**: `public.is_org_member(organization_id)`
-   **UPDATE**: `public.is_org_admin(organization_id)`

### Campaigns & Assets
-   **SELECT**: `public.is_org_member(organization_id)`
-   **INSERT/UPDATE**: `public.is_org_member(organization_id)` (Editors/Members can contribute).
-   **DELETE**: `public.is_org_admin(organization_id)` (Only admins can delete).

### Audit Logs
-   **SELECT**: `public.is_org_admin(organization_id)` (Strictly limited to admins).

## Testing RLS
To verify isolation:
```sql
-- As User A (Org 1)
SELECT * FROM campaigns; -- Should show Org 1 campaigns
SELECT * FROM campaigns WHERE organization_id = 'org-2-uuid'; -- Should return 0 rows
```
