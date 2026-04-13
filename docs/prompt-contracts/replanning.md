# Replanning Contract

Use this contract when the current campaign plan needs to be reevaluated.

## Input

- `campaign_id`
- `move_id`
- `task_statuses`
- `performance_signals`
- `foundation_snapshot`
- `intel_alerts`

## Output

- A replanning brief
- A recommendation to continue, pause, or pivot
- A short justification suitable for Council review

## Failure behavior

- Return `continue` when the signal is not strong enough to justify a pivot
- Keep the output stable across repeated evaluations of the same inputs
