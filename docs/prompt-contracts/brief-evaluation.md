# Brief Evaluation Contract

Use this contract when a brief, plan, or generated artifact needs to be evaluated before execution.

## Input

- `brief_id`
- `artifact_type`
- `artifact_text`
- `evaluation_criteria`
- `foundation_snapshot`

## Output

- An evaluation verdict
- A list of issues or gaps
- A short recommendation for accept, revise, or reject

## Failure behavior

- Return `revise` when the evaluator cannot justify acceptance
- Keep the output deterministic and easy to parse
