# Track Specification: Authentication & Database Architecture Overhaul

## 1. Overview
This track focuses on rebuilding and solidifying the core identity and data foundation of RaptorFlow. We are moving from an incomplete/non-functional state to a production-grade system encompassing Supabase Auth, a refactored relational schema, and a polished transactional email system via Resend.

## 2. Functional Requirements

### 2.1 Authentication System (Supabase)
- **Email/Password Flow:** Implementation of sign-up, login, and mandatory email verification.
- **Google OAuth:** Seamless single-tap integration.
- **Strict Gating:** Users must verify their email address before accessing the Matrix (Dashboard) or any Cognitive Engine modules.
- **Password Recovery:** Robust "Forgot Password" flow with secure reset tokens.

### 2.2 Database Schema & Security
- **Audit & Refactor:** Clean out obsolete tables while surgically preserving and migrating core user state.
- **Core Tables:**
    - `profiles`: Linked to `auth.users`, containing UCID (`RF-YYYY-XXXX`), workspace preferences, and onboarding status.
    - `subscriptions`: Tracking tiers, status, and renewal dates.
    - `payments`: Logging PhonePe transaction history and invoice links.
    - `email_logs`: Tracking transactional email delivery and status.
- **Row Level Security (RLS):** Hardened policies using `check_membership` to ensure absolute multi-tenant isolation.

### 2.3 Email Infrastructure (Resend)
- **Domain Configuration:** Setup and verification of sender domains.
- **Template Suite:** Editorial-grade templates with RaptorFlow branding:
    - **Welcome:** Triggered post-registration.
    - **Verification:** Sent during the sign-up gate.
    - **Password Reset:** Triggered by recovery requests.
    - **Invoices:** Sent after successful PhonePe payments.
- **Personalization:** Injection of UCID and user context into all correspondence.

## 3. Non-Functional Requirements
- **Performance:** Sub-100ms retrieval for profile and session data via Redis caching layer.
- **Integrity:** Every user MUST have a unique UCID assigned upon verified registration.
- **Observability:** 100% error capture for auth failures via Sentry.

## 4. Acceptance Criteria
- [ ] New users can register and are blocked from the dashboard until email verification.
- [ ] Existing users can log in via email or Google OAuth.
- [ ] "Forgot Password" successfully sends a branded email and allows password reset.
- [ ] Database schema matches the Modular Node.js hierarchy (Module > Service > Domain).
- [ ] Resend successfully sends all four template types with correct data injection.
- [ ] RLS policies prevent users from accessing data belonging to other UCIDs.

## 5. Out of Scope
- Marketing site content updates.
- Implementation of new AI "Moves" or "Titan" research logic (this track focuses on the *foundation* for those modules).
