# Implementation Plan: Authentication & Database Architecture Overhaul

## Phase 1: Database Schema Audit & Core Foundation
- [~] Task: Audit existing Supabase schema and drop non-functional/obsolete tables
    - [~] Create a migration script to clean up the current database state
    - [ ] Verify core `auth` schema integrity
- [ ] Task: Implement Refactored Core Tables
    - [ ] Write schema for `profiles` table (including UCID field)
    - [ ] Write schema for `subscriptions` and `payments` tables
    - [ ] Write schema for `email_logs` table
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Database Foundation' (Protocol in workflow.md)

## Phase 2: Core Authentication Flow & Gating
- [~] Task: Implement sign-up flow with mandatory email verification
    - [ ] Write failing tests for email registration and verification gate
    - [ ] Implement Supabase Auth sign-up logic in the frontend/backend
    - [ ] Create "Verify Your Email" middleware/gating component
- [ ] Task: Implement Login and Google OAuth
    - [ ] Write tests for credential login and OAuth session persistence
    - [ ] Implement standard login and Google Auth providers
- [ ] Task: Implement Password Recovery
    - [ ] Write tests for forgot password and reset token handling
    - [ ] Implement the password reset request and completion flows
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Core Auth & Gating' (Protocol in workflow.md)

## Phase 3: Identity System (UCID) & Profile Management
- [ ] Task: Implement UCID Generation & Profile Sync
    - [ ] Write unit tests for UCID format (`RF-YYYY-XXXX`) generation
    - [ ] Implement database trigger/service to create profile and UCID on user verification
- [ ] Task: Profile Retrieval & Caching
    - [ ] Write tests for profile fetching with Redis caching
    - [ ] Implement `ProfileService` with `@cached` decorator for sub-100ms retrieval
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Identity & Profiles' (Protocol in workflow.md)

## Phase 4: Email System Integration (Resend)
- [ ] Task: Configure Resend Integration
    - [ ] Set up Resend client and environment variables
    - [ ] Create base email service wrapper
- [ ] Task: Develop Branded Templates
    - [ ] Implement Welcome and Verification templates
    - [ ] Implement Password Reset and Invoice templates
- [ ] Task: Implement Email Triggers
    - [ ] Write tests for automated email triggers (e.g., post-verification)
    - [ ] Connect Auth/Payment events to the email service
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Email Integration' (Protocol in workflow.md)

## Phase 5: Security Hardening & RLS
- [ ] Task: Implement Hardened RLS Policies
    - [ ] Write SQL for `check_membership` function
    - [ ] Apply strict RLS policies to `profiles`, `subscriptions`, and `payments`
- [ ] Task: Security Audit & Sentry Integration
    - [ ] Verify zero-trust isolation between user workspaces
    - [ ] Configure Sentry to capture all authentication-related exceptions
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Security Hardening' (Protocol in workflow.md)

## Phase 6: End-to-End Verification
- [ ] Task: Full User Journey E2E Testing
    - [ ] Create Playwright scripts for Registration -> Verification -> Dashboard
    - [ ] Create Playwright scripts for Password Reset flow
- [ ] Task: Final Production Readiness Check
    - [ ] Verify all Quality Gates (Coverage >80%, Mobile responsiveness, etc.)
- [ ] Task: Conductor - User Manual Verification 'Phase 6: Final Verification' (Protocol in workflow.md)
