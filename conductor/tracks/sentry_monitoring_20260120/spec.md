# Specification - Sentry Configuration & Ultimate Monitoring

## Overview
This track involves the end-to-end configuration and integration of Sentry across the entire RaptorFlow ecosystem. Leveraging "ultimate admin access," we will establish a high-fidelity monitoring spine that captures errors, performance metrics, and user behavior (Session Replay) across the Frontend (Next.js), Backend (Python/FastAPI), and Edge/Middleware layers.

## Functional Requirements

### 1. Full-Stack Integration
- **Frontend (Next.js):**
    - Configure `@sentry/nextjs` to capture client-side and server-side errors.
    - Enable **Session Replay** (100% sample rate for initial hardening, adjustable later) to record user interactions.
    - Enable **Next.js Vitals** monitoring.
- **Backend (Python):**
    - Configure `sentry-sdk` for the FastAPI application.
    - Integrate with **Loguru/Logging** to capture breadcrumbs from AI agent execution chains.
    - Enable **Profiling** to identify CPU-intensive bottlenecks in the strategy and research engines.
- **Edge/Middleware:**
    - Ensure Next.js middleware and any Supabase Edge Functions (if applicable) are instrumented.

### 2. Performance Monitoring
- Implement **Distributed Tracing** to track requests as they move from the frontend through the middleware to the backend AI services.
- Define custom transaction boundaries for critical paths: Onboarding, Strategy Generation (Blackbox), and Market Research (Titan).

### 3. Ultimate Alerting & Environment Strategy
- Implement **Environment Tagging** (`development`, `preview`, `production`) across all SDKs.
- Configure **Alert Rules** in Sentry to trigger notifications for:
    - Any new high-severity error in Production.
    - Performance regressions (latency spikes) in AI inference tasks.
- Establish a "zero-noise" filtered view for Development while maintaining full data capture.

## Non-Functional Requirements
- **Security:** Ensure sensitive data (PII, API keys) is scrubbed before being sent to Sentry using `beforeSend` and `beforeSendTransaction` hooks.
- **Performance:** Ensure Sentry SDK initialization does not significantly impact cold-start times for Cloud Run or Vercel functions.

## Acceptance Criteria
- [ ] Sentry is successfully capturing errors from both the Next.js frontend and Python backend.
- [ ] Session Replays are viewable in the Sentry dashboard for frontend sessions.
- [ ] Performance traces show the full execution path from Frontend to Backend for strategic moves.
- [ ] CPU profiles are available for Python backend tasks.
- [ ] PII scrubbing is verified via a manual audit of captured events.

## Out of Scope
- Integration with other third-party monitoring tools (e.g., Datadog, New Relic).
- Custom Sentry Dashboards (this track focuses on configuration and data capture).
