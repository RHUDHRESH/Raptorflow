# ADR 0003: Data and Caching

## Status

Accepted

## Decision

Use Aurora PostgreSQL 16 as the primary system of record, Qdrant as the dedicated vector engine, and DragonflyDB as the cache/pub-sub/lock layer.

## Rationale

- Aurora provides transactional storage and tenant-safe RLS
- Qdrant handles filtered ANN search better than relying solely on pgvector
- DragonflyDB supports Redis-compatible semantics with better multi-core throughput for streaming workloads
