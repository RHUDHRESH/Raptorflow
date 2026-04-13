# Private Reflection Contract

Use this contract when an avatar needs to reflect privately without producing a Council-facing position.

## Input

- `avatar_key`
- `session_id`
- `foundation_sections`
- `recent_events`
- `ripple_candidates`

## Output

- A private reflection block
- A short internal takeaway
- Optional memory candidates for later PRL ingestion

## Failure behavior

- Return a minimal reflection when context is incomplete
- Do not promote private reflection text into public session output
