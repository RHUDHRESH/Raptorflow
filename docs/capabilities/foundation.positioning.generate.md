# Capability: `foundation.positioning.generate`

## Summary

| Field         | Value                             |
| ------------- | --------------------------------- |
| Key           | `foundation.positioning.generate` |
| Name          | Generate Positioning Statement    |
| Domain        | Positioning                       |
| Artifact Type | `positioning`                     |
| Risk Level    | **Low**                           |
| Tools         | `bedrock.fast`                    |
| Ripple Types  | `positioning_learning`            |
| Max Ripples   | 3                                 |

## Description

Generate positioning statements based on ICP and differentiation vectors.

## Input Schema

```json
{
  "type": "object",
  "properties": {
    "icp_summary": { "type": "string", "description": "Summary of the target ICP" },
    "differentiation": {
      "type": "string",
      "description": "Key differentiator or unique value proposition"
    },
    "competing_alternatives": {
      "type": "array",
      "items": { "type": "string" },
      "description": "What alternatives the ICP considers"
    },
    "tone": {
      "type": "string",
      "enum": ["bold", "empathetic", "rational", "playful"],
      "default": "bold"
    }
  },
  "required": ["icp_summary", "differentiation"]
}
```

## Output Schema

```json
{
  "type": "object",
  "properties": {
    "positioning_statements": [{ "statement": "string", "variant": "string" }],
    "tagline_options": ["string"],
    "proof_requirements": ["string"],
    "learnings": ["string"]
  }
}
```

## Required Context

| Source     | Sections                                                                          |
| ---------- | --------------------------------------------------------------------------------- |
| Foundation | `company_info`, `target_audience`, `value_proposition`, `competitive_positioning` |
| Intel      | **Required**                                                                      |
| Campaign   | Not required                                                                      |
| Ripples    | **Required**                                                                      |

## Guardrails

- Output marked as draft — requires human review
- No fabricated proof or statistics — `proof_requirements` lists what evidence is needed
- Tone must be one of the predefined enum values
- Ripple extraction limited to 3 items of type `positioning_learning`
