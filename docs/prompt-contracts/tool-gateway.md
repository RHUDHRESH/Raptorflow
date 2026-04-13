# Tool Gateway Contract

Use this contract for deterministic tool execution requests.

## Input

- `tool_name`
- `arguments`
- `timeout_ms`
- Optional `session_id`

## Output

- Accepted/rejected state
- Tool result payload
- Follow-up action when the tool output should be routed back into a stream

## Notes

- Keep the gateway transport-agnostic.
- The gateway only describes shape and policy, not implementation.
