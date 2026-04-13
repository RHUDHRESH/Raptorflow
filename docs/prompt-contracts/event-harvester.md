# Event Harvester Contract

Use this contract when external events or agent events are captured for ripple ingestion.

## Input

- `source_type`
- `source_id`
- `event_type`
- `payload`
- `ingested_at`

## Output

- A normalized ingestion acknowledgment
- Enough metadata to link the record to later ripples or analytics
