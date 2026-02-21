# Deployment Guide

RaptorFlow uses a multi-tiered deployment approach.

## 1. Frontend Deployment (Vercel)
The Next.js frontend (`src/`) is optimized for Vercel.
- Deployments are triggered automatically on push to the `main` branch.
- Ensure all environment variables strictly match those required in production within the Vercel dashboard.

## 2. Infrastructure Deployment (Docker)
For self-hosting or backend components, we use Docker.
- The root `Dockerfile` and `docker-compose.prod.yml` define the services.
- `deploy_production.sh` is used to orchestrate server-side updates.

**To deploy manually:**
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

## 3. Database Migrations (Supabase)
Never modify the production database manually.
- Use Supabase CLI to push migrations.
- `supabase db push` will apply pending changes located in `supabase/migrations/` to the connected remote project.

## Monitoring
Check the `infrastructure/prometheus` and your logging setups to ensure health checks pass post-deployment.
