# Infrastructure

- Local development uses Docker Compose for PostgreSQL, PgBouncer, and Qdrant.
- Prisma 7 is the TypeScript-side database package.
- Rust uses SQLx directly.
- Production infrastructure is defined in `infra/tofu/`.
- The active stack uses AWS Bedrock, Aurora PostgreSQL/PgBouncer, Qdrant, S3, and SQS.
