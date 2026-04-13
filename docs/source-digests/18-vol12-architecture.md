# Digest: `Vol12_Architecture.md`

## Intent

- Define the runtime stack, cloud topology, economics, security posture, and runbooks.

## Key requirements

- Rust + Axum, Next.js 15 + Vercel, Aurora, Qdrant, DragonflyDB, GCP API, Clerk, Razorpay, S3, SQS, ECS Fargate, and CloudWatch/Sentry form the production platform.
- Multi-AZ VPC shape and deployment sequencing are core architecture.
- Security and operations are part of build scope from day one.

## Scaffold implications

- Added `infra/tofu`, Docker, CI/CD, env examples, and runbooks to mirror the stated topology.
- Added machine-readable decision register to freeze stack choices.
- Added health, internal jobs, monitoring, and secret-management placeholders from the outset.
