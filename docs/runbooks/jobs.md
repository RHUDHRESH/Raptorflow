# Jobs Runbook

- Use org-scoped job execution.
- Keep locks in the database or queue layer, not in an external cache service.
- Any job that touches user state must include `org_id`.
- Realtime fan-out uses the Rust websocket layer. This repo does not currently wire Prisma Pulse into runtime event delivery.
- Vercel cron routes under `/api/*/cron` are still TypeScript/Prisma scheduled-job gaps and must keep `CRON_SECRET` configured. They are reported by `pnpm structural:check` until they move behind Rust job endpoints.
