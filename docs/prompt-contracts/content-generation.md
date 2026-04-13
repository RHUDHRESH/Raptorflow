# Content Generation Contract

Use this contract when the system generates content for a campaign, channel, or asset.

## Input

- `campaign_id`
- `move_id`
- `channel`
- `format`
- `voice_constraints`
- `foundation_sections`
- `reference_assets`

## Output

- The generated content block
- A short provenance marker
- Any follow-up metadata needed for downstream review or scheduling

## Failure behavior

- Return a safe fallback when the requested format is unsupported
- Preserve voice constraints even in degraded outputs
