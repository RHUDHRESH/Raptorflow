# Muse Routing Contract

Use this contract when Muse needs to decide whether to answer strategically, tactically, or with content help.

## Input

- `conversation_id`
- `route_hint`
- `message_text`
- `foundation_sections`
- `campaign_context`

## Output

- A normalized routing decision
- A downstream prompt target
- A short explanation for why that route was selected

## Failure behavior

- Default to the safest route when the classification is ambiguous
- Do not expose internal routing heuristics in user-visible output
