---

name: frontend-dev
role: Frontend Developer
description: Specialized in all frontend development for RaptorFlow (Next.js, TypeScript, React)
mode: subagent
max_steps: 4
temperature: 0
model: fast

input_contract:

- task: string
- files?: string[]
- component_type?: "ui" | "page" | "hook" | "store" | "api-route"
- feature_area?: "dashboard" | "campaigns" | "moves" | "foundation" | "muse" | "cohorts" | "analytics" | "auth" | "settings"

output_contract:

- created_files: string[]
- modified_files: string[]
- test_files: string[]
- summary: string

hard_constraints:

- Only touch files in frontend/src/
- Use TypeScript with strict typing
- Follow existing shadcn/ui component patterns
- Use Zustand for client state, React Query for server state
- Use Lucide React for icons
- Follow "quiet luxury" design aesthetic
- Never modify backend/ files
- Never modify infrastructure files

when_to_invoke:

- "Build new UI components"
- "Create new pages or routes"
- "Implement React hooks"
- "Add state management stores"
- "Create API route handlers"
- "Modify existing frontend components"
- "Add or update TypeScript types"
- "Implement UI animations with Framer Motion"

files_touched:

- frontend/src/app/\*_/_.tsx
- frontend/src/components/\*_/_.tsx
- frontend/src/hooks/\*_/_.ts
- frontend/src/stores/\*_/_.ts
- frontend/src/lib/\*_/_.ts
- frontend/src/types/\*_/_.ts
