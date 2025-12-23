# RaptorFlow Industrial Deployment Guide

## 1. Google Cloud Platform (GCP) Setup

### 1.1 Enable Required APIs
Execute the following command to enable all necessary industrial-grade APIs:

```bash
gcloud services enable \
    run.googleapis.com \
    bigquery.googleapis.com \
    storage.googleapis.com \
    secretmanager.googleapis.com \
    cloudbuild.googleapis.com \
    aiplatform.googleapis.com \
    artifactregistry.googleapis.com
```

### 1.2 Service Account Configuration
Create a service account with minimal privileges:

```bash
gcloud iam service-accounts create raptorflow-matrix-sa \
    --display-name="RaptorFlow Matrix Service Account"
```

Assign necessary roles:
- `roles/run.invoker`
- `roles/bigquery.dataEditor`
- `roles/storage.objectAdmin`
- `roles/secretmanager.secretAccessor`
- `roles/aiplatform.user`

## 2. Supabase Configuration
- Enable `pgvector` extension.
- Configure Realtime for `telemetry` tables.
- Set up Auth providers.

## 4. Industrial Security & Protection

### 4.1 Cloud Armor (WAF)
Protect the Matrix API from common web attacks (SQLi, XSS) and DDoS:
```bash
python scripts/setup_cloud_armor.py --project raptorflow-481505
```

### 4.2 IAM Role Pruning
Ensure the `raptorflow-matrix-sa` service account follows the Principle of Least Privilege:
- **Keep:** `roles/run.invoker`, `roles/secretmanager.secretAccessor`, `roles/aiplatform.user`.
- **Remove:** Any `roles/owner` or `roles/editor` bindings.

```bash
# Verify roles
gcloud projects get-iam-policy raptorflow-481505 \
    --flatten="bindings[].members" \
    --format='table(bindings.role)' \
    --filter="bindings.members:raptorflow-matrix-sa"
```
