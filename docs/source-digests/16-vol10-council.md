# Digest: `Vol10_Council.md`

## Intent

- Define Council session types, debate flow, synthesis, and economics.

## Key requirements

- Tactical, operational, strategic, and war-room sessions are distinct.
- Debate phases and strategist synthesis are structured artifacts.
- Session cost tracking is part of the domain, not an observability afterthought.

## Scaffold implications

- Added `council` crate, REST stubs, websocket stubs, and migration placeholders for sessions and positions.
- Added billing/cost-tracking room in contracts and database layers.
- Prompt contracts reserve synthesis and reflection interfaces.
