# ADR 0002: Runtime and Deployment

## Status

Accepted

## Decision

Deploy a single Rust binary to AWS ECS Fargate behind an ALB, and deploy the frontend to Vercel.

## Rationale

- The backend must host REST, WebSockets, and background jobs together
- Operational overhead stays lower than a microservice split at this stage
- ALB plus ECS gives websocket-compatible rolling updates and autoscaling
- Vercel is the best fit for the Next.js surface
