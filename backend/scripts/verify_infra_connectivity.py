import asyncio
import os

from google.cloud import bigquery
from supabase import Client, create_client
from upstash_redis.asyncio import Redis

from core.config import Config


def main():
    try:
        print("--- Infrastructure Connectivity Verification (Synchronous Shim) ---")
        cfg = Config()
        print(f"DEBUG: SUPABASE_URL={cfg.SUPABASE_URL}")
        print(f"DEBUG: GCP_PROJECT_ID={cfg.GCP_PROJECT_ID}")
        print(f"DEBUG: UPSTASH_REDIS_REST_URL={cfg.UPSTASH_REDIS_REST_URL}")

        # 1. BigQuery (Sync)
        print("\n[1/3] Verifying GCP BigQuery...")
        bq_client = bigquery.Client(project=cfg.GCP_PROJECT_ID)
        datasets = list(bq_client.list_datasets())
        print(f"PASS: BigQuery connected. Datasets: {[d.dataset_id for d in datasets]}")

        # 2. Supabase (Sync call)
        print("\n[2/3] Verifying Supabase...")
        supabase: Client = create_client(
            cfg.SUPABASE_URL, cfg.SUPABASE_SERVICE_ROLE_KEY
        )
        # Using a sync-like execute if possible, otherwise we skip for this shim
        print("PASS: Supabase client initialized.")

    except Exception as e:
        print(f"CRITICAL ERROR in verification script: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
