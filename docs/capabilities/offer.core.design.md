# Capability: `offer.core.design`

## Summary

| Field         | Value               |
| ------------- | ------------------- |
| Key           | `offer.core.design` |
| Name          | Design Core Offer   |
| Domain        | Offer               |
| Artifact Type | `offer_design`      |
| Risk Level    | **Medium**          |
| Tools         | `bedrock.fast`      |
| Ripple Types  | `value_learning`    |
| Max Ripples   | 2                   |

## Description

Design core offer structure including pricing, packaging, and value metrics.

## Input Schema

```json
{
  "type": "object",
  "properties": {
    "positioning_summary": {
      "type": "string",
      "description": "Current positioning or value proposition"
    },
    "target_customer": {
      "type": "string",
      "description": "Description of target customer segment"
    },
    "existing_offer": { "type": "string", "description": "Current offer if any" },
    "pricing_objective": {
      "type": "string",
      "enum": ["premium", "value", "competitive", "penetration"],
      "default": "value"
    }
  },
  "required": ["positioning_summary", "target_customer"]
}
```

## Output Schema

```json
{
  "type": "object",
  "properties": {
    "offer_components": [
      { "name": "string", "description": "string", "included": "boolean", "tier": "string" }
    ],
    "pricing_structure": {
      "entry_price": "number",
      "core_price": "number",
      "premium_price": "number",
      "currency": "USD"
    },
    "value_metrics": ["string"],
    "proof_requirements": ["string"],
    "learnings": ["string"]
  }
}
```

## Required Context

| Source     | Sections                                               |
| ---------- | ------------------------------------------------------ |
| Foundation | `company_info`, `target_audience`, `value_proposition` |
| Intel      | Not required                                           |
| Campaign   | **Required**                                           |
| Ripples    | **Required**                                           |

## Guardrails

- Output marked as draft — requires human review and approval before pricing goes live
- No actual pricing finalization — all prices are recommendations
- `proof_requirements` enumerates what customer evidence would strengthen recommendations
- Ripple extraction limited to 2 items of type `value_learning`
- **Medium risk**: pricing recommendations should be reviewed against market data
