# Capability: `foundation.icp.refine`

## Summary

| Field         | Value                                      |
| ------------- | ------------------------------------------ |
| Key           | `foundation.icp.refine`                    |
| Name          | Refine Ideal Customer Profile              |
| Domain        | Foundation                                 |
| Artifact Type | `icp_refined`                              |
| Risk Level    | **Low**                                    |
| Tools         | `bedrock.fast`                             |
| Ripple Types  | `audience_learning`, `foundation_learning` |
| Max Ripples   | 3                                          |

## Description

Refine and validate the Ideal Customer Profile based on company info and market signals.

## Input Schema

```json
{
  "type": "object",
  "properties": {
    "company_description": {
      "type": "string",
      "description": "Current company description or positioning"
    },
    "existing_icp": {
      "type": "object",
      "description": "Existing ICP if available"
    },
    "refinement_focus": {
      "type": "string",
      "enum": ["demographics", "psychographics", "behaviors", "pain_points", "all"],
      "default": "all"
    }
  },
  "required": ["company_description"]
}
```

## Output Schema

```json
{
  "type": "object",
  "properties": {
    "refined_icp": {
      "demographics": {
        "role": "string",
        "industry": "string",
        "company_size": "string",
        "seniority": "string"
      },
      "psychographics": { "values": ["string"], "fears": ["string"], "aspirations": ["string"] },
      "behaviors": { "content_consumption": ["string"], "purchase_patterns": ["string"] },
      "pain_points": ["string"]
    },
    "confidence": { "type": "number", "minimum": 0, "maximum": 1 },
    "learnings": ["string"]
  }
}
```

## Required Context

| Source     | Sections                          |
| ---------- | --------------------------------- |
| Foundation | `company_info`, `target_audience` |
| Intel      | Not required                      |
| Campaign   | Not required                      |
| Ripples    | **Required**                      |

## Guardrails

- Output is marked as draft/refinement — requires human review before use
- No external data fetching — uses only provided inputs and org context
- No PII extraction or external enrichment
- Ripple extraction limited to 3 items of types `audience_learning` or `foundation_learning`
