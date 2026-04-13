# Deployments Runbook

## Backend deployment (AWS ECS Fargate)

The backend deploys via GitHub Actions on every merge to `main`.

### Pipeline steps

```
merge to main
    ↓
GitHub Actions: cargo build --release
    ↓
Docker build → ECR push
    ↓
ECS migration task (runs sqlx migrate)
    ↓
ECS rolling deployment (zero-downtime)
    ↓
Health validation (5xx check + smoke test)
```

### Manual deployment (infra engineers only)

```bash
cd infra/tofu/environments/prod

# Preview what would change
tofu plan

# Apply — requires AWS credentials with ECS deploy permissions
tofu apply
```

### Verifying a deployment

```bash
# Check ECS service status
aws ecs describe-services --cluster raptorflow-prod --services raptorflow-api

# Check recent task health
aws ecs list-tasks --cluster raptorflow-prod --service-name raptorflow-api
aws ecs describe-tasks --cluster raptorflow-prod --tasks <task-arn>

# Check application logs
aws logs tail /ecs/raptorflow-api --follow
```

### Health endpoints

```bash
# API liveness (is it running?)
curl https://api.raptorflow.dev/health/live

# API readiness (is it ready to serve traffic?)
curl https://api.raptorflow.dev/health/ready
```

---

## Frontend deployment (Vercel)

Frontend deploys automatically on every push to `main` via Vercel's GitHub integration.

### Manual deployment

```bash
# Via Vercel CLI
vercel --prod
```

### Verifying

```bash
# Check Vercel deployment status
vercel ls

# Open production URL
open https://raptorflow.vercel.app
```

---

## Rollback

### Frontend (Vercel)

```bash
# Via Vercel dashboard: Deployments → find last good deployment → "Promote to Production"
# Or via CLI:
vercel rollback
```

### Backend (ECS)

```bash
# Find the previous task definition revision
aws ecs describe-task-definition --task-definition raptorflow-api

# Update the service to use the previous revision
aws ecs update-service \
  --cluster raptorflow-prod \
  --service-name raptorflow-api \
  --task-definition raptorflow-api:<previous-revision>

# Verify the service stabilises
aws ecs wait services-stable \
  --cluster raptorflow-prod \
  --services raptorflow-api
```

After rolling back, re-run migrations if the rollback crosses a migration boundary:

```bash
# Run the migration ECS task with the previous image
aws ecs run-task \
  --cluster raptorflow-prod \
  --task-definition raptorflow-migrate:<previous-revision>
```

---

## Troubleshooting

### ECS deployment fails — task won't start

Check the task logs first:

```bash
aws ecs describe-tasks --cluster raptorflow-prod --tasks <task-arn>
aws logs tail /ecs/raptorflow-api --task-id <task-id>
```

Common causes:

- **Secrets Manager secret not found** — the secret ARN in the task definition doesn't exist in this account/region. Fix the secret in AWS Secrets Manager.
- **Database connection refused** — Aurora isn't accepting connections from this security group. Check the `raptorflow-prod` security group rules.
- **Migration task failed** — the migration locked the schema. Connect to Aurora directly and run `SELECT * FROM sqlx_migrations;` to see what ran.

### ECS deployment times out — service fails to stabilise

```bash
# Force a new deployment (rolls back to the last good task definition)
aws ecs update-service \
  --cluster raptorflow-prod \
  --service-name raptorflow-api \
  --force-new-deployment
```

### Frontend 500 errors after deployment

Check the Vercel function logs in the Vercel dashboard. Common causes:

- API base URL changed (`NEXT_PUBLIC_API_BASE_URL` not updated)
- Type mismatch after a schema change that hasn't been synced to the frontend

### Vercel build fails

```bash
# Run the build locally first
pnpm build
```

Common causes: missing env vars (copy from Vercel dashboard), TypeScript errors that only appear in CI.

---

## Pre-deployment checklist

Before merging any PR that changes the schema, database, or environment variables:

- [ ] Schema change: run `pnpm contracts:sync && pnpm contracts:check`
- [ ] Migration: tested locally with `sqlx migrate run`
- [ ] New env var: added to `crates/config/src/lib.rs` AND `infra/tofu/environments/<env>/main.tf`
- [ ] New secret: created in AWS Secrets Manager AND added to ECS task definition
- [ ] Frontend still builds: `pnpm build` passes locally
