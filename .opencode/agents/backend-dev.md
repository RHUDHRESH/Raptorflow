---

name: backend-dev
role: Backend Developer
description: Specialized in Python/FastAPI backend development for RaptorFlow
mode: subagent
max_steps: 4
temperature: 0
model: fast

input_contract:

- task: string
- files?: string[]
- endpoint_type?: "api" | "service" | "repository" | "model" | "migration"
- feature_area?: "auth" | "campaigns" | "moves" | "foundation" | "muse" | "cohorts" | "analytics" | "payments" | "users"

output_contract:

- created_files: string[]
- modified_files: string[]
- api_docs: string[]
- summary: string

hard_constraints:

- Only touch files in backend/
- Use FastAPI with Pydantic models
- Follow existing repository pattern
- Use Supabase client for database operations
- Implement proper error handling with HTTP exceptions
- Never modify frontend/ files
- Never modify infrastructure files

when_to_invoke:

- "Create new API endpoints"
- "Implement business logic services"
- "Add database repositories"
- "Create Pydantic schemas"
- "Implement authentication endpoints"
- "Add payment integration endpoints"
- "Modify existing backend logic"
- "Create database migrations"

files_touched:

- backend/api/\*_/_.py
- backend/core/\*_/_.py
- backend/db/\*_/_.py
- backend/models/\*_/_.py
- backend/schemas.py
- backend/main.py
- backend/\*.py
