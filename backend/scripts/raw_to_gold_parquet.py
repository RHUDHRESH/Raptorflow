import glob

import pandas as pd
from google.cloud import bigquery, storage

from agents.vacuum_node import VacuumNode
from core.config import Config


def raw_to_gold_etl():
    print("--- PySpark-style ETL: Raw to Gold Parquet ---")
    cfg = Config()

    instruction_files = glob.glob("Instruction/*.md")
    processed_records = []

    for file_path in instruction_files:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                clean_line = line.strip()
                if not clean_line:
                    continue

                record = {
                    "tenant_id": "raptor-prod-001",
                    "source_file": file_path,
                    "line_number": i,
                    "content": clean_line,
                    "created_at": pd.Timestamp.now().isoformat(),
                }

                # Apply VACUUM Valid
                valid_report = VacuumNode.validate_record(
                    record, ["tenant_id", "content"], {"tenant_id": str, "content": str}
                )
                if valid_report.is_valid:
                    processed_records.append(record)

    df = pd.DataFrame(processed_records)
    parquet_path = "gold_business_context.parquet"
    df.to_parquet(parquet_path, index=False)
    print(f"PASS: Created local Parquet with {len(df)} records.")

    # Upload to GCS (Gold Bucket)
    try:
        storage_client = storage.Client(project=cfg.GCP_PROJECT_ID)
        bucket = storage_client.bucket(cfg.GCS_GOLD_BUCKET)
        blob = bucket.blob(
            f"context/gold_{pd.Timestamp.now().strftime('%Y%m%d')}.parquet"
        )
        blob.upload_from_filename(parquet_path)
        print(f"PASS: Uploaded Gold Parquet to gs://{cfg.GCS_GOLD_BUCKET}/{blob.name}")

        # Task 18: Indexing Preparation
        print(
            f"INFO: Preparing {len(df)} records for pgvector indexing (Semantic Memory)."
        )
        # In a real environment, we would iterate through df and call save_memory for each row.
        # For now, we verify the data is structured correctly for indexing.
        if "content" in df.columns and "tenant_id" in df.columns:
            print("PASS: Data structure verified for pgvector indexing.")

    except Exception as e:
        print(f"FAIL: GCS Upload failed: {e}")


if __name__ == "__main__":
    raw_to_gold_etl()
