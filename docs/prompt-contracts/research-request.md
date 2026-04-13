# Research Request Contract

Use this contract when an agent needs factual support before or during generation.

## Input

- `query`
- `request_kind`
- `urgency`
- `required_sources`
- `output_format`

## Output

- A structured research result block or a parser-friendly JSON object
- Source list with enough detail to trace where the answer came from
- Explicit blocking/background behavior

## Failure behavior

- Return a short failure block when no reliable source is found
- Never fabricate citations or sources
