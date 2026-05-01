# OpenTofu Infrastructure

Production AWS infrastructure defined in code. All changes go through `tofu plan` / `tofu apply` — no manual AWS console changes for anything in this directory.

---

## Structure

```
infra/tofu/
    ├── modules/                  ← Reusable components
    │   ├── compute/            ← ECS cluster, service, task definitions
    │   ├── data/               ← Aurora, ElastiCache, S3, Qdrant on ECS
    │   └── network/            ← VPC, subnets, NAT gateways, security groups, ALB
    │
    └── environments/
        ├── dev/                ← ap-south-1 dev
        ├── staging/            ← ap-south-1 staging
        └── prod/               ← ap-south-1 production
```

Each environment (`environments/<env>/`) instantiates the modules with environment-specific variables. Modules are never applied directly — always through an environment overlay.

---

## Module inventory

| Module                    | What it defines                                           |
| ------------------------- | --------------------------------------------------------- |
| `compute/ecs-cluster`     | ECS cluster, IAM roles, autoscaling                       |
| `compute/ecs-service`     | ECS service definition, task definition, health checks    |
| `compute/ecs-task`        | One-off task definition (migrations, admin jobs)          |
| `data/aurora`             | Aurora Serverless v2, subnet group, parameter group       |
| `data/s3`                 | S3 buckets with versioning, encryption, lifecycle rules   |
| `data/qdrant`             | Qdrant on ECS with EFS-backed storage                     |
| `network/vpc`             | VPC, public/private subnets, NAT gateways                 |
| `network/alb`             | Application Load Balancer, target groups, HTTPS listeners |
| `network/security-groups` | Security group rules for each service                     |
| `secrets/`                | Secrets Manager secret definitions                        |
| `vercel/`                 | Vercel project linkage and metadata                       |

---

## Working with an environment

```bash
cd infra/tofu/environments/dev

# See what would change (always run this first — it's read-only)
tofu plan

# Apply changes (requires AWS credentials with the right IAM permissions)
tofu apply
```

**In CI:** `tofu plan`/`apply` is not yet automated in GitHub Actions. Run `tofu plan` locally before any PR that changes infrastructure. `tofu apply` must be run manually with appropriate AWS credentials.

---

## Before the first apply

Three values must be set before running `tofu apply` in any environment. They are in `environments/<env>/terraform.tfvars`:

```hcl
github_oidc_thumbprints = ["<real GitHub Actions OIDC thumbprint>"]
certificate_arn          = "arn:aws:acm:ap-south-1:123456789012:certificate/<real-cert>"
```

See `docs/runbooks/infra-hardening-stubs.md` for details on each.

---

## Adding a new AWS resource

1. Add a module in `infra/tofu/modules/<category>/`
2. Instantiate it in `infra/tofu/environments/<env>/main.tf`
3. Add the variable to `infra/tofu/environments/<env>/variables.tf`
4. Set the value in `infra/tofu/environments/<env>/terraform.tfvars`
5. PR → review with `tofu plan` output → merge → apply

Never hardcode ARNs or account IDs in modules. Use variables.

---

## Secrets management

All production secrets live in AWS Secrets Manager. They are not in the Tofu state file as values — only as references.

The ECS task definition receives secrets via the `secrets` block in the task definition module. The task role must have `secretsmanager:GetSecretValue` permission for each secret.

See `infra/tofu/modules/compute/ecs-task.tf` for the pattern.

---

## What the scaffold covers (and doesn't)

### Covered

- ALB HTTP → HTTPS redirect, access logging, idle timeout, deregistration delay
- ECS autoscaling for the API service
- Secrets Manager ARN injection into ECS task definitions
- Multi-AZ EFS mount targets for Qdrant persistence
- S3 public-access blocking, versioning, encryption, lifecycle rules
- Security group least-privilege rules

### NOT covered (operator responsibility)

- Real GitHub OIDC thumbprints
- Hardened AMIs for ElastiCache
- Domain registration and ACM certificate validation
- Vercel project setup
- Cost alarms and billing alerts
- Disaster recovery procedures
