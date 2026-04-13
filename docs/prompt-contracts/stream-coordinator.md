# Stream Coordinator Contract

Use this contract to describe how a session should move from precheck to generation.

## Input

- `phase`
- `blocking_research`
- `background_research`
- `tool_requests`
- `foundation_sections`

## Output

- A routing decision
- A list of queued follow-up actions
- A stable marker for the current phase
