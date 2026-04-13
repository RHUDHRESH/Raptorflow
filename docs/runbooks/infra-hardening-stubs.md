# Infra Hardening Stubs

This repository now treats a few values as explicit operator inputs instead of hidden placeholders.

## Required before apply

- `github_oidc_thumbprints`: set the real GitHub Actions OIDC thumbprint list for the AWS account before applying the security module.
- `dragonfly_ami_id`: point this at a hardened private AMI for the Dragonfly EC2 host.
- `qdrant_image_uri`: pin this to the approved Qdrant container image for the environment.

## What the scaffold already covers

- ALB HTTP to HTTPS redirect, access logging, idle timeout, and target-group deregistration delay.
- ECS autoscaling for the API service.
- Secrets Manager ARN injection into the API task definition.
- Multi-AZ EFS mount targets for Qdrant persistence.
- S3 public-access blocking, versioning, encryption, and lifecycle rules for the primary artifact bucket.

## Notes

- The `infra/tofu/environments/*/terraform.tfvars.example` files intentionally contain placeholders for account-specific values.
- Replace those placeholders before running `tofu apply`; they are stubs, not defaults for production.
- The ECS execution role supplied to the `compute` module must allow `secretsmanager:GetSecretValue` for the injected secret ARNs and `kms:Decrypt` if the account uses a customer-managed key.
- ALB and S3 logging buckets are configured with explicit bucket policies, but those policies still require the load balancer and source buckets to stay in the same account and Region.
