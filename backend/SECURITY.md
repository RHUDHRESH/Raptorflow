# RaptorFlow Security Audit: GCP Secret Manager

## Overview
This document outlines the required IAM permissions for the RaptorFlow backend (Spine) to securely access secrets in Production.

## Required Permissions
The service account running the backend (on Cloud Run) must have the following role:
- **Role:** `roles/secretmanager.secretAccessor`
- **Scope:** Individual secrets (Preferred) or Project-level (Discouraged).

## Secrets List
The following secrets MUST be configured in GCP Secret Manager:

| Secret ID | Purpose | Required For |
|-----------|---------|--------------|
| `SERPER_API_KEY` | Google Search results | Researcher Agent |
| `SUPABASE_SERVICE_ROLE_KEY` | Admin DB access | All services |
| `OPENAI_API_KEY` | LLM Inference (Fallback) | Specialist Agents |
| `ANTHROPIC_API_KEY` | LLM Inference (Fallback) | Specialist Agents |
| `UPSTASH_REDIS_REST_TOKEN` | Redis Authentication | Memory Layer |

## Audit Procedure
1. Verify service account exists: `gcloud iam service-accounts list`
2. Check IAM bindings:
   ```bash
   gcloud projects get-iam-policy raptorflow-481505 \
     --flatten="bindings[].members" \
     --format='table(bindings.role)' \
     --filter="bindings.members:serviceAccount:raptorflow-spine@raptorflow-481505.iam.gserviceaccount.com"
   ```
3. Ensure `roles/secretmanager.secretAccessor` is present.

## Remediation
If permission is missing, run:
```bash
gcloud projects add-iam-policy-binding raptorflow-481505 \
  --member="serviceAccount:raptorflow-spine@raptorflow-481505.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```
