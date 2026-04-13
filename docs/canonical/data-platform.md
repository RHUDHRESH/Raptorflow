# Data Platform Contracts

## Qdrant collection

- Collection name: `ripples`
- Vector size: `64`
- Distance: cosine
- Index: HNSW
- Quantization: scalar
- Persistence: EFS-backed storage on the Qdrant ECS task

## Dragonfly keyspace

- `wm:{org_id}:{agent_id}`: working memory sorted sets
- `foundation:{org_id}:{version}`: serialized Foundation cache
- `stream:{org_id}:{session_id}`: websocket fan-out buffers
- `lock:{org_id}:{job_name}`: distributed locks
- `snark:{org_id}:{batch_id}`: snark cache and presentation state

## S3 layout

- `intelligence/{org_id}/{competitor_id}/ads/{date}/`
- `uploads/{org_id}/foundation/`
- `uploads/{org_id}/assets/`
- `exports/{org_id}/{date}/`
- `backups/aurora/{date}/`

## Secrets Manager contract

- `raptorflow/{env}/database/app`
- `raptorflow/{env}/database/direct`
- `raptorflow/{env}/clerk/jwt`
- `raptorflow/{env}/gcp/api-key`
- `raptorflow/{env}/razorpay/api`
- `raptorflow/{env}/sentry/dsn`
