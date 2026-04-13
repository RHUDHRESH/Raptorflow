# Strategist Synthesis Contract

Use this contract when the Strategist needs to synthesize the session into one actionable direction.

## Input

- `session_id`
- `foundation_snapshot`
- `council_positions`
- `campaign_brief`
- `replanning_notes`
- `context_pack`

## Output

- A single synthesis block
- A recommended next action
- A short rationale that can be rendered in the UI or injected into downstream prompts

## Failure behavior

- Return a conservative fallback synthesis when inputs conflict
- Prefer explicit uncertainty over fabricated certainty
