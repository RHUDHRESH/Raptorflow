# Digest: `Vol8_Campaigns_FULL.docx`

## Intent

- Define campaign creation, moves, tasks, execution, replanning, and performance feedback.

## Key requirements

- Campaigns are living systems with briefs, moves, tasks, generated content, replanning sessions, and performance logs.
- Replanning is triggered by task misses, intelligence changes, and KPI deviations.
- Campaigns connect deeply to PRL, Muse, Office, and intel.

## Scaffold implications

- Added `campaigns` crate, route group, and migration placeholders for campaign tables.
- Added queue placeholder for content pre-generation.
- Added contract types for `Campaign`, `Move`, `Task`, and `CampaignBrief`.
