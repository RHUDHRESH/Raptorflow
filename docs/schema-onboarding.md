# Onboarding Schema Documentation

This document outlines the database schema used for the Raptorflow onboarding flow.

## Tables

### `projects`
Stores the top-level project information.
- `id` (uuid, PK): Unique identifier.
- `user_id` (uuid, FK): Reference to Supabase `auth.users`.
- `name` (text): Project name.
- `status` (enum): 'draft', 'active', 'archived'.
- `created_at`, `updated_at`: Timestamps.

### `intake`
Stores the structured answers from the onboarding flow. One-to-one with `projects`.
- `id` (uuid, PK): Unique identifier.
- `project_id` (uuid, FK): Reference to `projects`. Unique constraint ensures 1:1 relationship.
- `goals` (jsonb): Answers from the "Goals" step.
- `audience` (jsonb): Answers from the "Audience" step.
- `positioning` (jsonb): Answers from the "Positioning" step.
- `execution` (jsonb): Answers from the "Execution" step.
- `locked_at` (timestamptz): When the user clicked "Generate Plan". If set, intake is read-only (enforced by app logic).
- `created_at`, `updated_at`: Timestamps.

### `plans`
Stores the generated marketing plan.
- `id` (uuid, PK): Unique identifier.
- `project_id` (uuid, FK): Reference to `projects`.
- `status` (enum): 'draft', 'ready', 'in_progress'.
- `raw_pillars` (jsonb): Generated pillars (from AI).
- `raw_outline` (jsonb): Generated outline (from AI).
- `created_at`, `updated_at`: Timestamps.

## Row Level Security (RLS)

- **Projects**: Users can only select, insert, and update rows where `user_id` matches their auth UID.
- **Intake**: Users can only access intake records where the parent `project_id` belongs to them.
- **Plans**: Users can only access plans where the parent `project_id` belongs to them.
