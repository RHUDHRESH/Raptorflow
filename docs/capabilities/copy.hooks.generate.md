# Capability: `copy.hooks.generate`

## Summary

| Field         | Value                            |
| ------------- | -------------------------------- |
| Key           | `copy.hooks.generate`            |
| Name          | Generate Copy Hooks              |
| Domain        | Copy                             |
| Artifact Type | `hook_set`                       |
| Risk Level    | **Low**                          |
| Tools         | `bedrock.fast`                   |
| Ripple Types  | `copy_learning`, `hook_learning` |
| Max Ripples   | 3                                |

## Description

Generate compelling copy hooks for ads, emails, or content based on offer and ICP.

## Input Schema

```json
{
  "type": "object",
  "properties": {
    "platform": {
      "type": "string",
      "enum": ["linkedin", "twitter", "email", "facebook", "instagram", "google"]
    },
    "count": { "type": "integer", "minimum": 5, "maximum": 30, "default": 20 },
    "angle": {
      "type": "string",
      "enum": ["founder_led", "proof_led", "benefit_led", "pain_led", "contrast", "question"],
      "default": "benefit_led"
    },
    "offer_summary": { "type": "string", "description": "Brief summary of the offer" },
    "tone": {
      "type": "string",
      "enum": ["bold", "curious", "empathetic", "provocative", "educational"],
      "default": "bold"
    }
  },
  "required": ["platform", "offer_summary"]
}
```

## Output Schema

```json
{
  "type": "object",
  "properties": {
    "hooks": [
      {
        "text": "string",
        "type": "string",
        "angle": "string",
        "salience": { "type": "number", "minimum": 0, "maximum": 1 }
      }
    ],
    "winning_angles": ["string"],
    "proof_gaps": ["string"],
    "learnings": ["string"]
  }
}
```

## Required Context

| Source     | Sections                               |
| ---------- | -------------------------------------- |
| Foundation | `target_audience`, `value_proposition` |
| Intel      | Not required                           |
| Campaign   | **Required**                           |
| Ripples    | **Required**                           |

## Guardrails

- Output is draft copy — requires human review for brand compliance
- Platform-specific character limits are not enforced by the capability — caller should validate
- No external linking or CTA finalization — all CTAs are suggested placeholders
- `proof_gaps` identifies what proof points would strengthen hook claims
- Ripple extraction limited to 3 items of types `copy_learning` or `hook_learning`
