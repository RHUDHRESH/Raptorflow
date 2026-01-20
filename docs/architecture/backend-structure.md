# Backend Directory Structure

RaptorFlow follows a modular, hierarchical architecture to ensure scalability, maintainability, and clear separation of concerns.

## Hierarchy: Module > Service > Domain

The backend logic is organized into modules under `src/modules/`. Each module follows this internal structure:

```text
src/modules/<module_name>/
├── domain/            # Pure business logic, core entities, and domain-specific rules.
│                      # No external dependencies (DB, APIs, Frameworks).
├── services/          # Orchestration layer. Interacts with DB (Supabase),
│                      # external APIs (Gemini, PhonePe), and the Domain layer.
├── controllers/       # Optional. Adapters for specific transport layers (e.g., Next.js API Routes).
├── types/             # Module-specific TypeScript interfaces and types.
└── __tests__/         # Unit and integration tests for this module.
```

### 1. Domain Layer (`domain/`)
- **Focus:** "What the business does."
- **Content:** Calculation logic, data transformations, strategy synthesis rules.
- **Rules:** Must be framework-agnostic. Should be testable without mocks where possible.

### 2. Service Layer (`services/`)
- **Focus:** "How the business interacts with the world."
- **Content:** Database queries (Supabase client calls), API requests (Vertex AI, Upstash), Cache management.
- **Rules:** Orchestrates domain logic to fulfill a specific use case.

### 3. Modules
Key modules in RaptorFlow:
- **Foundation:** Core branding, positioning, and identity logic.
- **Intelligence (Titan & Blackbox):** Scraping, search multiplexing, and strategy synthesis.
- **Operations (Cohorts, Moves, Campaigns):** User-facing strategic execution tools.
- **Infrastructure:** Shared services (logging, auth, secret management).

## Migration Guidelines
All new backend logic must be implemented in this structure. Legacy logic in `src/lib` or standalone scripts should be incrementally refactored into the appropriate modules during the Consolidation & Audit tracks.
