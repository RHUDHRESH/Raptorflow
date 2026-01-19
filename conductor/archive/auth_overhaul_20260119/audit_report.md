# Database Audit Report - Auth Overhaul 2026

## Existing Tables (The "17" identified)
The following tables were identified across various migrations as the "current" working set, though many overlap:

1.  `users` / `user_profiles` / `profiles` (Redundant user identity)
2.  `workspaces` / `workspace_settings` (Workspace management)
3.  `icp_profiles` (Strategy)
4.  `campaigns` (Execution)
5.  `moves` (Execution)
6.  `muse_assets` (AI Content)
7.  `blackbox_strategies` (AI Learning)
8.  `foundations` (Brand Context)
9.  `rate_limits` (Security)
10. `user_sessions` (Security)
11. `payments` / `payment_transactions` (Billing)
12. `subscription_plans` (Billing)
13. `audit_logs` (Security)
14. `move_tasks` (Execution)
15. `onboarding_sessions` (Onboarding)
16. `business_context_manifests` (Business Data)
17. `user_uploads` (Storage)

## Redundancies & Issues
- **User Proliferation**: Identity is spread across `users`, `profiles`, and `user_profiles`. This causes sync issues and confusion in RLS policies.
- **Over-engineered Security**: `user_sessions`, `jwt_sessions`, `mfa_sessions`, and `impersonation_sessions` create massive complexity for a "personal account" model.
- **Fragmented Strategy Data**: Brand data is split between `foundations`, `business_context_manifests`, and `icp_profiles`.
- **Inconsistent Execution Logic**: `moves` and `campaigns` have overlapping fields but separate tables, making unified progress tracking difficult.

## Unified Minimalist Schema Design
The goal is to consolidate the above into 5-6 core tables:

1.  **`profiles`**: The single source of truth for users.
    - Fields: `id`, `email`, `full_name`, `avatar_url`, `ucid` (RF-YYYY-XXXX), `onboarding_status`, `role`.
2.  **`workspaces`**: 1-to-1 relationship with profiles (Personal accounts).
    - Fields: `id`, `owner_id`, `name`, `slug`, `settings`.
3.  **`business_context`**: Unified strategic data.
    - Fields: `workspace_id`, `brand_kit` (JSONB), `icp_data` (JSONB), `positioning` (JSONB).
4.  **`execution_units`**: Unified table for Moves and Campaigns.
    - Fields: `id`, `workspace_id`, `type` (move/campaign), `parent_id`, `status`, `data` (JSONB).
5.  **`payments`**: Simplified transaction tracking.
    - Fields: `id`, `user_id`, `status`, `amount`, `transaction_id`.
6.  **`system_logs`**: Consolidated `audit_logs`, `error_logs`, and `security_events`.
    - Fields: `id`, `category`, `event`, `metadata` (JSONB).

## Migration Strategy
1.  **Preparation**: Create new schema tables.
2.  **UCID Generation**: Assign UCIDs to all existing users in the new `profiles` table.
3.  **Data Porting**: Move data from `users`/`user_profiles` to `profiles`.
4.  **Hard Migration**: Drop redundant tables after verification.
