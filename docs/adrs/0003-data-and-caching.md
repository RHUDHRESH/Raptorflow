# ADR 0003 - Data and caching

Current decision:

- Aurora PostgreSQL 16 is the system of record.
- Qdrant is the vector engine.
- Prisma Accelerate handles query acceleration.
- Prisma Pulse handles realtime DB events.
- Rust uses SQLx directly.
- No removed cache or external inference layer remains in the active stack.
