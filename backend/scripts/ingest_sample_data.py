import os
import csv
from google.cloud import storage
from backend.core.config import get_settings

def ingest_sample_data():
    """Ingests sample taxi-like data to GCS Raw bucket (No pandas version)."""
    settings = get_settings()
    bucket_name = settings.GCS_INGEST_BUCKET
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    # Create dummy taxi data (Osipov Pattern)
    header = ["vendor_id", "pickup_datetime", "dropoff_datetime", "passenger_count", "trip_distance", "fare_amount"]
    rows = [
        [1, "2025-12-23 10:00:00", "2025-12-23 10:15:00", 1, 2.5, 12.50],
        [2, "2025-12-23 10:05:00", "2025-12-23 10:20:00", 2, 3.0, 15.00],
        [1, "2025-12-23 10:10:00", "2025-12-23 10:25:00", 1, 1.2, 8.00]
    ]
    
    csv_path = "sample_taxi_data.csv"
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    blob = bucket.blob("raw/sample_taxi_data.csv")
    blob.upload_from_filename(csv_path)
    print(f"Uploaded {csv_path} to gs://{bucket_name}/raw/")
    os.remove(csv_path)

if __name__ == "__main__":
    ingest_sample_data()