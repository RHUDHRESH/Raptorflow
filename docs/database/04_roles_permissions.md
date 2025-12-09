# Roles & Permissions

RaptorFlow uses a Role-Based Access Control (RBAC) system scoped to Organizations.

## Roles (`org_role` ENUM)

| Role | Description | Capabilities |
|------|-------------|--------------|
| `owner` | Organization Creator | Full access. Can delete organization. Cannot be removed easily. |
| `admin` | Administrator | Full access to resources, billing, and member management. |
| `member` | Standard User | Can create/edit campaigns, cohorts, assets. Cannot manage billing or users. |
| `viewer` | Read-Only | Can view all data but cannot modify anything. |
| `billing` | Finance User | Can only access billing, invoices, and subscription settings. |

## Permission Matrix

| Feature | Owner | Admin | Member | Viewer | Billing |
|:--------|:-----:|:-----:|:------:|:------:|:-------:|
| **Organization Settings** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Manage Members** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **View Audit Logs** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Manage Billing** | ✅ | ✅ | ❌ | ❌ | ✅ |
| **Create Campaigns** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Edit Campaigns** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **View Reports** | ✅ | ✅ | ✅ | ✅ | ❌ |

## Implementation
Roles are stored in `public.organization_members`. RLS policies use `public.is_org_admin()` (checks for owner/admin) to enforce high-level security. Application-level logic (API/Frontend) enforces granular feature access.
