# Digest: `AddendumCDE_OfficeInternClosedLoops (1).md`

## Intent

- Finish three missing systems: Office rendering, intern dispatch, and closed-loop operational updates.

## Key requirements

- Office is a PixiJS canvas with React overlays and `office.event` websocket messages.
- Intern tasks need blocking/background execution contracts.
- Foundation cache invalidation, content feedback loops, and per-org cost tracking require explicit jobs and tables.

## Scaffold implications

- Added frontend Office shell, websocket schemas, and shared `OfficeEventMessage` and `InternTask` types.
- Reserved backend crates for `office`, `intel`, `jobs`, `billing`, and `integrations`.
- Added migration placeholders for snark and `org_monthly_costs`.
