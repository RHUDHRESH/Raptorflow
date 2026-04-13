# Intern Research Contract

Use this contract when the system delegates a research task to an intern avatar.

## Input

- `parent_session_id`
- `parent_agent_id`
- `intern_avatar_key`
- `task_type`
- `urgency`
- `query`
- `specific_requirements`
- `output_format`

## Output

- A structured intern research envelope
- A clear blocking or background status
- A result format that can be injected back into the session stream

## Failure behavior

- Return a blocking failure when the task cannot be scoped safely
- Never omit the original task identity
