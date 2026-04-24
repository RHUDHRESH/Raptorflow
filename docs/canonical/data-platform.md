# Data Platform Contracts

## Qdrant collection

- Collection name: `ripples`
- Vector size: `64`
- Distance: cosine
- Index: HNSW
- Quantization: scalar
- Persistence: EFS-backed storage on the Qdrant task

## S3 layout

- `uploads/{org_id}/...`
- `screenshots/{org_id}/...`
- `exports/{org_id}/...`
- `backups/aurora/{date}/`

## Secrets contract

- `raptorflow/{env}/database/app`
- `raptorflow/{env}/database/direct`
- `raptorflow/{env}/clerk/jwt`
- `raptorflow/{env}/razorpay/api`
- `raptorflow/{env}/sentry/dsn`
- `raptorflow/{env}/bedrock/*`
