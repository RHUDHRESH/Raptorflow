# Digest: `AddendumA_RippleCreation.md`

## Intent

- Close the PRL implementation gap with concrete ripple ingestion artifacts.

## Key requirements

- `MemoryEvent` is a first-class contract.
- Ripple creation has both real-time and post-session entrypoints.
- Salience, SimHash, embedding queue, prediction resolution, and edge linking are mandatory subsystems.

## Scaffold implications

- Added shared `MemoryEvent` and `RippleData` types in contracts.
- Reserved backend crates for `prl`, `jobs`, `db`, and `integrations`.
- Added queue schemas and migration slots for ripples, ripple edges, and cost tracking.
