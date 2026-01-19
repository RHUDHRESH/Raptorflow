# Track Specification: Auth Overhaul & Schema Consolidation

## Overview
This track focuses on streamlining the authentication system and database schema. We will shift to an exclusive Google OAuth flow, implement a standardized "Unique Customer ID" (UCID), and consolidate the current 17-table database structure into a minimalist, efficient schema.

## Functional Requirements
1.  **Authentication:**
    -   Restrict login/signup exclusively to **Google OAuth** via Supabase.
    -   Remove all Email/Password login paths and UI elements.
    -   Returning users must be redirected directly to the Dashboard.
    -   New users must be handed off to the existing 22-step onboarding flow (no modifications to the onboarding logic itself).

2.  **User & Workspace Management:**
    -   Every account is strictly a "Personal" account.
    -   Implement a **Unique Customer ID (UCID)** generator (Format: `RF-YYYY-XXXX`, e.g., `RF-2026-0001`).
    -   The UCID must be assigned upon the first successful login.

3.  **Database Consolidation:**
    -   Audit the 17 existing Supabase tables to identify redundancies.
    -   Design a unified schema centering on essential entities (e.g., `users`, `profiles`, `workspaces`).
    -   Execute a **Hard Migration**:
        -   Migrate active user data and session info to the new schema.
        -   Drop redundant tables once migration is verified.

## Non-Functional Requirements
-   **Security:** Ensure RLS (Row Level Security) policies in Supabase are updated for the new schema.
-   **Performance:** Minimize database joins by optimizing the core user/profile relationship.
-   **Maintainability:** Document the new schema clearly to prevent "table bloat" in the future.

## Acceptance Criteria
-   [ ] Login page only shows "Continue with Google".
-   [ ] Existing users can log in with Google and land on the dashboard.
-   [ ] New users can log in with Google and are redirected to the onboarding start.
-   [ ] Every user in the `profiles` table has a valid, unique UCID in the `RF-YYYY-XXXX` format.
-   [ ] The database consists only of the audited, essential tables.
-   [ ] No legacy data is lost during the Hard Migration.

## Out of Scope
-   Modifying the logic or UI of the existing 22-step onboarding flow.
-   Implementing MFA (Multi-Factor Authentication).
-   Supporting Team/Enterprise workspace features.
