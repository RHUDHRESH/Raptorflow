# Plan: Supabase Hardening, AI Onboarding, Multi-Payment (Rupees) & Account Management

## Phase 1: Supabase CLI-Driven Schema & Multi-Tenancy
- [x] Task: Initialize Supabase locally and consolidate existing migrations. 2d224e6
- [x] Task: Create `workspaces` and `workspace_members` tables. 2d224e6
- [x] Task: Implement `tenant_id` (workspace_id) migration for all operational tables. 2d224e6
- [x] Task: Configure Row Level Security (RLS) policies for multi-tenant isolation. 2d224e6
- [x] Task: Set up path-isolated Supabase Storage buckets for brand assets. 2d224e6
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Database & Security' (Protocol in workflow.md)

## Phase 2: AI-Enabled Onboarding Agent Spine
- [ ] Task: Implement Architect Node (Validation & Contradiction Detection).
- [ ] Task: Implement Prophet Node (Psychographic ICP Generation).
- [ ] Task: Implement Strategist Node (90-Day Arc & Move Backlog).
- [ ] Task: Implement Model Router with 40/60 Gemini 2.5 Flash/Flash-Lite split.
- [ ] Task: Integrate Onboarding Spine with Supabase persistence.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: AI Onboarding' (Protocol in workflow.md)

## Phase 3: Multi-Provider Payment Gateway & Tier Enforcement
- [ ] Task: Create `PaymentProvider` interface and PhonePe SDK integration.
- [ ] Task: Implement secondary payment provider (Razorpay/Stripe) logic.
- [ ] Task: Create `subscriptions` and `entitlements` tracking system.
- [ ] Task: Implement tier-based feature gating (Ascent, Glide, Soar).
- [ ] Task: Localize all payment UI and logic to Rupees (₹).
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Payments & Tiers' (Protocol in workflow.md)

## Phase 4: Account Management & Invoicing
- [ ] Task: Implement Invoicing Engine for PDF generation.
- [ ] Task: Create "Account" section in Settings with plan and usage details.
- [ ] Task: Build Billing History UI with invoice download capability.
- [ ] Task: Implement Revenue Gate middleware for app access.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Account & Invoicing' (Protocol in workflow.md)
