# Technology Stack ΓÇö RaptorFlow

## Frontend Core
- **Framework:** [Next.js](https://nextjs.org/) (App Router)
- **Language:** [TypeScript](https://www.typescriptlang.org/)
- **UI Library:** [React 19](https://react.dev/)
- **Deployment:** [Vercel](https://vercel.com/)

## AI & LLM
- **Platform:** [Google Vertex AI](https://cloud.google.com/vertex-ai) (Gemini models)
- **Universal Agent Architecture:** Single-agent orchestration for complex onboarding workflows (22+ steps). Uses YAML-defined dynamic skills with tunable prompts and automated retry logic.
- **Titan SOTA Intelligence Engine:**
  - **Modes:** LITE (snippet search), RESEARCH (parallel scraping), DEEP (recursive traversal).
  - **Discovery:** Parallel Search Multiplexing (Native Bing + Reddit .json + SearXNG).
  - **Extraction:** Stealth Scraper Pool (Playwright Stealth + Fingerprint Randomization).
  - **Ranking:** Semantic Ranking & Link Scoring via Gemini 1.5 Flash.
- **Orchestration:** [LangGraph](https://langchain-ai.github.io/langgraph/) with **Supabase Checkpointing** for industrial-grade state persistence.
- **Context Management:**
  - **DCM (Distance Context Management):** Semantic vector sorting for BCM and Market Intel.
  - **MacM (Memory Augmented Context Hub):** Session-based hot context integration.

## Backend & Infrastructure
- **Cloud Provider:** [Google Cloud Platform (GCP)](https://cloud.google.com/)
- **Compute:** [Cloud Run](https://cloud.google.com/run)
- **Architecture:** Modular Node.js hierarchy (Module > Service > Domain) for core business logic.
- **Database & Auth:** [Supabase](https://supabase.com/) (Unified PostgreSQL schema for all strategic state, including Arcs, Instances, and Agent Logs).
  - **Security:** Hardened RLS policies using centralized `check_membership` for multi-tenant isolation.
- **API Standard:** "RaptorFlow" Bespoke Standard for unified JSON responses and global error handling.
- **Caching & Messaging:** [Upstash](https://upstash.com/) (Redis)
  - **Caching Logic:** SOTA Global `@cached` decorator and `CacheService` with workspace-level isolation, surgical pattern invalidation, and automated dependency-based purging.
  - **Message Bus:** Redis-based state synchronization for real-time AI agent updates.
  - **Job Queue:** Managed Redis task queue for reliable asynchronous execution.
- **Stealth Networking:** [Gluetun](https://github.com/qdm12/gluetun) (VPN-based IP rotation for Search Cluster)
- **Secrets Management:** Zero-trust policy via [GCP Secret Manager](https://cloud.google.com/secret-manager) (Production) and local `.env` (Development).
- **Data Warehouse & Analytics:** [BigQuery](https://cloud.google.com/bigquery) (Longitudinal Analysis)
- **Blob Storage:** [Google Cloud Storage (GCS)](https://cloud.google.com/storage)

## Payments
- **Gateway:** [PhonePe SDK v3.2.1](https://www.phonepe.com/business-solutions/payment-gateway/) (Standard Checkout)

## Styling & Motion
- **Styling:** [Tailwind CSS](https://tailwindcss.com/)
- **Components:** [Shadcn UI](https://ui.shadcn.com/) (Radix UI primitives)
- **Animations:** [Framer Motion](https://www.framer.com/motion/)

## Utilities
- **Icons:** [Lucide React](https://lucide.dev/)
- **Forms/Validation:** [React Hook Form](https://react-hook-form.com/)
- **Toast/Notifications:** [Sonner](https://sonner.stevenly.me/)
- **Monitoring & Observability:** [Sentry](https://sentry.io/) (Full-stack Error Tracking, Performance, Session Replay, and Profiling).

## Development Tools
- **Linter:** ESLint
- **Testing:** [Vitest](https://vitest.dev/) (Unit/Integration) and [Playwright](https://playwright.dev/) (E2E).
- **Package Manager:** npm
