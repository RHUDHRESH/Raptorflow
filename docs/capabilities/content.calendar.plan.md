# Capability: `content.calendar.plan`

## Summary

| Field         | Value                   |
| ------------- | ----------------------- |
| Key           | `content.calendar.plan` |
| Name          | Plan Content Calendar   |
| Domain        | Content                 |
| Artifact Type | `calendar_plan`         |
| Risk Level    | **Low**                 |
| Tools         | `bedrock.fast`          |
| Ripple Types  | `content_learning`      |
| Max Ripples   | 2                       |

## Description

Generate a content calendar aligned with campaigns and marketing motions.

## Input Schema

```json
{
  "type": "object",
  "properties": {
    "campaign_goal": { "type": "string", "description": "Primary campaign or marketing goal" },
    "duration_weeks": { "type": "integer", "minimum": 2, "maximum": 12, "default": 4 },
    "content_types": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["blog", "social", "email", "video", "podcast", "webinar"]
      }
    },
    "platforms": { "type": "array", "items": { "type": "string" } },
    "cadence": {
      "type": "string",
      "enum": ["daily", "every_other_day", "weekly", "biweekly"],
      "default": "weekly"
    }
  },
  "required": ["campaign_goal", "duration_weeks"]
}
```

## Output Schema

```json
{
  "type": "object",
  "properties": {
    "calendar": [
      {
        "week": "integer",
        "date": "string",
        "content_type": "string",
        "platform": "string",
        "topic": "string",
        "angle": "string",
        "call_to_action": "string"
      }
    ],
    "themes": ["string"],
    "coverage_analysis": {
      "platform_coverage": "object",
      "content_type_coverage": "object",
      "gaps": ["string"]
    },
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

- Output is a planning draft — topics and CTAs require human review before publishing
- No actual publishing or scheduling — this is a planning tool only
- `gaps` in coverage_analysis identifies what content types/platforms are not covered
- Ripple extraction limited to 2 items of type `content_learning`
- All topics and angles are suggestions — final content must go through review workflow
