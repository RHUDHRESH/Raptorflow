# Architectural Overview

RaptorFlow separates its architecture into a few distinct domains to ensure scalability and clarity.

## System Components

### 1. Frontend (`src/`)
- Built with **Next.js** (App Router).
- Communicates directly with Supabase for data fetching and authentication where possible, and passes complex logic to the Backend API.
- Stores global state (Zustand/Context) and manages UI components under `src/components`.

### 2. Backend API (`backend/`)
- Handles heavy computational logic, AI inferences, or third-party API orchestrations.
- Serves as the primary controller for complex workflows that shouldn't reside on the client.

### 3. Database & Auth (`supabase/`)
- **Supabase** acts as the primary Postgres database and Authentication provider.
- All schema migrations and RLS (Row Level Security) policies are stored within `supabase/migrations/`.

### 4. Infrastructure (`infrastructure/`)
- Contains configurations for:
  - **Nginx**: Reverse proxying and load balancing.
  - **Redis**: Caching and background job queue handling.
  - **Prometheus**: Metrics and monitoring.
