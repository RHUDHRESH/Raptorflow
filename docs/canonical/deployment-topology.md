# Deployment Topology

## Regions

- AWS primary region: `ap-south-1`
- Frontend: Vercel

## Network shape

- Public subnets: ALB and NAT
- Private subnets: API tasks, PgBouncer, Qdrant
- Database subnets: Aurora

## Runtime shape

- API runs at least two tasks
- ALB terminates TLS
- WebSocket sessions stay task-affine via stickiness
- Separate migration tasks handle schema changes

## Deployment sequence

1. GitHub Actions builds the backend image
2. Image is pushed to ECR
3. Migration task runs
4. ECS rolls the API service
5. Vercel deploys the frontend
