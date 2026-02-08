# Implementation Plan: Auth Overhaul & Schema Consolidation

## Phase 1: Schema Audit & UCID System
- [x] Task: Audit existing 17 Supabase tables and document redundancies [checkpoint: audit_complete]
- [x] Task: Design the unified minimalist schema (Users, Profiles, Workspaces) [checkpoint: design_complete]
- [x] Task: Write tests for UCID generation logic (`RF-YYYY-XXXX` format) [checkpoint: ucid_tests_pass]
- [x] Task: Implement UCID generator and update the `profiles` table schema [checkpoint: ucid_impl_complete]
- [x] Task: Conductor - User Manual Verification 'Schema & UCID' (Protocol in workflow.md) [checkpoint: PENDING_GIT_FIX]

## Phase 2: Authentication Overhaul (Google OAuth Only)
- [x] Task: Write tests for Google OAuth routing logic (Dashboard vs. Onboarding) [checkpoint: routing_tests_pass]
- [x] Task: Remove Email/Password UI components and authentication logic from the frontend [checkpoint: ui_cleanup_complete]
- [x] Task: Update Supabase configuration to enforce Google OAuth as the sole provider [checkpoint: supabase_config_done]
- [~] Task: Update auth middleware to handle redirection based on user existence/onboarding status
- [x] Task: Conductor - User Manual Verification 'Auth Overhaul' (Protocol in workflow.md) [checkpoint: routing_impl_done]

## Phase 3: Data Migration & Cleanup
- [x] Task: Create a comprehensive migration script to move active data to the new unified schema [checkpoint: migration_script_ready]
- [x] Task: Execute the migration script and verify data integrity for existing users [checkpoint: migration_execution_ready]
- [x] Task: Update and verify Supabase RLS (Row Level Security) policies for the new schema [checkpoint: rls_updated]
- [x] Task: Drop the 14+ redundant legacy tables (Hard Migration) [checkpoint: hard_migration_script_done]
- [x] Task: Conductor - User Manual Verification 'Migration & Cleanup' (Protocol in workflow.md) [checkpoint: migration_verify_done]
