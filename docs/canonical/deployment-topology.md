# Deployment Topology

## Regions

- AWS: `ap-south-1` (Mumbai)
- GCP API: `asia-south1`
- Vercel: managed edge deployment for the frontend

## Network shape

- Public subnets: ALB, NAT gateways
- Private subnets: ECS tasks, PgBouncer, Qdrant, Dragonfly access path
- Database subnets: Aurora

## Runtime shape

- ECS service `raptorflow-api` runs at least two tasks for availability
- ALB terminates TLS and forwards to the API target group
- Target group stickiness is enabled so long-lived WebSocket sessions remain task-affine
- One-off ECS task definitions are reserved for migrations, Daily Wins, backfills, and admin operations

## Deployment sequence

1. GitHub Actions validates code and builds the backend image
2. Image is pushed to ECR
3. Migration task runs
4. ECS rolling deployment updates the API service
5. Vercel auto-deploys the frontend from the same push
