# Daily Wins Contract

Use this contract when generating the Daily Wins briefing or prioritizing what should surface first.

## Input

- `org_id`
- `session_count`
- `campaign_context`
- `intel_alerts`
- `pending_tasks`
- `voice_fingerprint`
- `performance_signals`

## Output

- A briefing block with a lead summary and next action
- A prioritized list of wins
- Optional campaign-ranking metadata for multi-campaign days

## Failure behavior

- Return a lean briefing when the signal set is sparse
- Prefer clear prioritization over breadth
