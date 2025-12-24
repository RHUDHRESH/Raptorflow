# GCP IAM & Cloud Run Security Audit (2025-12-24)

## Findings
- Cloud Run service `raptorflow-spine` currently uses a broad deployment command (`--allow-unauthenticated`).
- Deployment script doesn't explicitly define a dedicated Service Account, defaulting to the highly-privileged Compute Engine default service account.

## Recommendations

### 1. Dedicated Service Account
Create a dedicated service account for the RaptorFlow backend:
`raptorflow-backend@raptorflow-481505.iam.gserviceaccount.com`

### 2. Principle of Least Privilege (IAM Roles)
Assign the following roles to the service account:
- **Secret Manager Secret Accessor:** `roles/secretmanager.secretAccessor` (Scoped to project)
- **Storage Object Admin:** `roles/storage.objectAdmin` (Scoped to `raptorflow-*` buckets)
- **Logging Log Writer:** `roles/logging.logWriter`
- **Vertex AI User:** `roles/aiplatform.user`

### 3. Updated Deployment Command
Modify `deploy_cloud_run.py` to include the `--service-account` flag and remove `--allow-unauthenticated` if a Load Balancer/IAP is used.

```bash
gcloud run deploy raptorflow-spine \
  --service-account="raptorflow-backend@raptorflow-481505.iam.gserviceaccount.com" \
  ...
```

### 4. GCS Hardening
- CORS should be restricted to production domains in `setup_gcs_policies.py` before final release.
- Ensure Public Access Prevention (PAP) is enabled on all buckets.
