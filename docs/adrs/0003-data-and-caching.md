# ADR 0003 - Data and caching

Current decision:

- Aurora PostgreSQL 16 is the system of record.
- Qdrant is the vector engine.
- PgBouncer handles PostgreSQL connection pooling.
- AWS SQS handles durable background job delivery.
- Realtime fan-out is handled by the Rust websocket layer.
- Prisma is limited to TypeScript-side database tooling; Prisma Accelerate and Prisma Pulse are not active runtime dependencies in this repo.
- Rust uses SQLx directly.
- No removed cache or external inference layer remains in the active stack.
