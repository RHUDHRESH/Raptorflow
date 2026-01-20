# Implementation Plan - Sentry Configuration & Ultimate Monitoring

## Phase 1: Foundation & SDK Integration
Establish the basic connection between RaptorFlow and Sentry across all environments.

- [x] Task: Initialize Sentry SDKs in Next.js and Python (8e26a9e)
    - [x] Add Sentry DSN to `.env` and configure `sentry.client.config.ts`, `sentry.server.config.ts`, and `sentry.edge.config.ts`.
    - [x] Initialize `sentry-sdk` in the Python FastAPI app entry point.
- [x] Task: Verify Basic Error Capture (8e26a9e)
    - [x] [RED] Create a temporary route/endpoint in both Next.js and FastAPI that throws a manual error.
    - [x] [GREEN] Verify that these errors appear in the Sentry dashboard with correct environment tags.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Foundation & SDK Integration' (Protocol in workflow.md)

## Phase 2: Advanced Monitoring & Performance
Enable high-fidelity features like Replay, Profiling, and Trace linking.

- [x] Task: Configure Session Replay & CPU Profiling (8e26a9e)
    - [x] Enable `Sentry.replayIntegration` in the frontend with a 100% sample rate for initial audit.
    - [x] Enable `profiles_sample_rate` in the Python backend to capture agent performance.
- [x] Task: Implement Distributed Tracing (8e26a9e)
    - [x] [RED] Execute a frontend action that calls a backend API and observe two disconnected traces in Sentry.
    - [x] [GREEN] Configure `tracePropagationTargets` in the frontend and ensure CORS headers allow `sentry-trace` and `baggage`.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Advanced Monitoring & Performance' (Protocol in workflow.md)

## Phase 3: Security Hardening & Alerting [checkpoint: 43fdd8b]
Ensure data privacy and establish the notification spine.

- [x] Task: Implement PII Scrubbing & Data Security (8e26a9e)
    - [x] [RED] Trigger an error containing a simulated sensitive field (e.g., `api_key` or `email`) and verify it appears in Sentry.
    - [x] [GREEN] Implement `beforeSend` and `beforeSendTransaction` hooks to filter out sensitive patterns.
- [x] Task: Configure Ultimate Alerting Rules (8e26a9e)
    - [x] Create Sentry Alert Rules for high-frequency errors and AI inference performance regressions.
    - [x] Verify environment-specific noise reduction (filtering dev errors from urgent alerts).
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Security Hardening & Alerting' (Protocol in workflow.md)

## Phase 4: Final Audit & Cleanup
Perform a complete end-to-end verification of the monitoring system.

- [x] Task: End-to-End Monitoring Verification (8e26a9e)
    - [x] Execute a full user journey (Onboarding -> Strategy -> Moves) and verify the unified trace in Sentry.
    - [x] Verify that Session Replays correctly capture the interactions without leaking sensitive UI data.
- [x] Task: Legacy Monitoring Cleanup (8e26a9e)
    - [x] Remove any temporary error-triggering routes or debug logs used during setup.
- [x] Task: Conductor - User Manual Verification 'Phase 4: Final Audit & Cleanup' (Protocol in workflow.md) (8e26a9e)
