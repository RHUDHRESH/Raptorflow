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

## 3. Upstash Configuration
- Provision Global Redis (HTTP).
- Set `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN` in Secret Manager.

```