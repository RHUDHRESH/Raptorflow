# Plan: Service Integrity & API Key Audit

This plan outlines the steps for a "deep deep" audit and functional verification of RaptorFlow's infrastructure and service connections.

## Phase 1: Environment Audit & Secret Discovery
- [ ] Task: Audit `.env` files against `.env.example` to identify missing variables.
- [ ] Task: Scan codebase for hardcoded secrets using regex/grep patterns.
- [ ] Task: Compile a list of missing/invalid keys and present it to the user for updating.
- [ ] Task: Conductor - User Manual Verification 'Environment Audit & Secret Discovery' (Protocol in workflow.md)

## Phase 2: Implementation of Deep Verification Scripts
- [ ] Task: Create `verify_vertex.py` to perform model inference with Gemini.
- [ ] Task: Create `verify_supabase.py` to check DB connection and RLS policies.
- [ ] Task: Create `verify_redis.py` to check Upstash connectivity and latency.
- [ ] Task: Create `verify_resend.py` to check transactional email API status.
- [ ] Task: Create `verify_phonepe.py` to confirm Test Mode and merchant ID validity.
- [ ] Task: Conductor - User Manual Verification 'Implementation of Deep Verification Scripts' (Protocol in workflow.md)

## Phase 3: Execution & Final Validation
- [ ] Task: Execute all verification scripts and document success/failure for each service.
- [ ] Task: Verify that the user has updated all identified keys from Phase 1.
- [ ] Task: Ensure PhonePe is strictly in "Test Mode" in the configuration.
- [ ] Task: Conductor - User Manual Verification 'Execution & Final Validation' (Protocol in workflow.md)

## Phase 4: Cleanup & Reporting
- [ ] Task: Remove temporary verification scripts or move them to a diagnostic folder.
- [ ] Task: Generate a final "System Integrity Report" summarizing the health of all services.
- [ ] Task: Conductor - User Manual Verification 'Cleanup & Reporting' (Protocol in workflow.md)
