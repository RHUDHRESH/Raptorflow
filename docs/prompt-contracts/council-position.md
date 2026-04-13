# Council Position Contract

Use this contract when a Council avatar needs to publish a position, objection, or recommendation.

## Input

- `session_id`
- `avatar_key`
- `round_number`
- `position_type`
- `foundation_sections`
- `context_pack`
- `position_prompt`

## Output

- A parser-friendly council position block
- A concise recommendation or objection
- Enough structured metadata to route the position into the session stream

## Failure behavior

- Return a short failure block when the position cannot be formed from the available context
- Never invent Foundation facts or campaign state
