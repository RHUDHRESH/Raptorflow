# Canonical Stack

This document freezes the stack that the repository scaffold is built around.

## Frontend

- Next.js 15 with App Router
- React Server Components for landing and marketing routes
- Client-rendered authenticated app shell
- TypeScript everywhere
- Clerk for auth integration on the frontend
- Zustand for client state
- TanStack Query for server state
- Tailwind CSS and shadcn/ui
- Framer Motion for non-Office motion
- PixiJS v8 plus `pixi-viewport` for the Office canvas

## Backend

- Single deployable Rust binary
- Axum HTTP and WebSocket server
- Tokio runtime
- Background jobs hosted inside the same process with task registries
- One ECS service plus one-off ECS tasks for admin and migration jobs

## Data and infrastructure

- Aurora PostgreSQL 16 Serverless v2 in Mumbai
- PgBouncer in front of Aurora
- pgvector enabled in Aurora for small-scale vector support
- Qdrant on ECS Fargate backed by EFS for persistent vector search
- DragonflyDB on EC2 for cache, pub/sub, and distributed locks
- S3 for uploads, screenshots, exports, and backups
- SQS for embedding and content pre-generation queues
- AWS Secrets Manager for all production secrets

## Deployment

- GitHub Actions builds and deploys backend on pushes to `main`
- Vercel deploys frontend automatically from the same monorepo
- OpenTofu/Terraform-compatible HCL defines cloud infrastructure
