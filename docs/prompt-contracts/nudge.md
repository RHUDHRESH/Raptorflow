# Nudge Contract

Use this contract when converting system state into a user-facing nudge.

## Input

- `source_type`
- `source_id`
- `nudge_type`
- `priority`
- `title`
- `body`
- `action_type`
- `action_data`

## Output

- A concise nudge payload
- Delivery metadata
- Optional suppression hints for repeated or low-value nudges

## Failure behavior

- Suppress when the nudge is redundant or weakly supported
- Never generate alarmist copy without a clear source
