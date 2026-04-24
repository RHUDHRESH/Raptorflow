# Jobs Runbook

- Use org-scoped job execution.
- Keep locks in the database or queue layer, not in an external cache service.
- Any job that touches user state must include `org_id`.
- Realtime fan-out now uses Prisma Pulse and the existing Rust websocket layer.
