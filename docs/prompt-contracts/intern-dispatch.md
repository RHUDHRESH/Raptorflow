# Intern Dispatch Contract

Use this contract when a Council avatar delegates work to an intern.

## Input

- `task_type`
- `urgency`
- `query`
- `specific_requirements`
- `output_format`

## Output

- A dispatch envelope with the same task identity
- A clear indication of whether the work is blocking or background

## Notes

- Blocking tasks are resolved before final generation.
- Background tasks may return later and be injected into a later context pass.
