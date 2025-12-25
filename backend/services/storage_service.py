import logging
from datetime import datetime
from typing import Any, Optional

from google.cloud import storage

from backend.core.config import get_settings

logger = logging.getLogger("raptorflow.services.storage")


class GCSLifecycleManager:
    """
    Manager for GCS object lifecycle and archival.
    Moves data between raw, gold, and archival zones.
    """

    def __init__(self, source_bucket: str, target_bucket: str):
        self.source_bucket_name = source_bucket
        self.target_bucket_name = target_bucket
        self._client: Optional[storage.Client] = None

    @property
    def client(self) -> storage.Client:
        if self._client is None:
            self._client = storage.Client()
        return self._client

    def archive_logs(self, prefix: str) -> bool:
        """
        Moves blobs from source bucket to target bucket under the same prefix.
        """
        try:
            source_bucket = self.client.get_bucket(self.source_bucket_name)
            target_bucket = self.client.get_bucket(self.target_bucket_name)

            blobs = source_bucket.list_blobs(prefix=prefix)

            count = 0
            for blob in blobs:
                # Copy to target
                source_bucket.copy_blob(blob, target_bucket, blob.name)
                # Delete from source
                source_bucket.delete_blob(blob.name)
                count += 1

            logger.info(
                f"Archived {count} blobs from {self.source_bucket_name} to {self.target_bucket_name}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to archive logs: {e}")
            return False


class BigQueryMatrixLoader:
    """
    Loader for syncing Parquet data from GCS to BigQuery.
    Enables high-scale longitudinal analysis for the Matrix.
    """

    def __init__(self, dataset_id: str, table_id: str):
        self.dataset_id = dataset_id
        self.table_id = table_id
        self._client: Optional[Any] = (
            None  # Using Any to avoid import crash during setup
        )

    @property
    def client(self):
        if self._client is None:
            from google.cloud import bigquery

            self._client = bigquery.Client()
        return self._client

    def sync_parquet_to_bq(self, uri: str) -> bool:
        """
        Loads a Parquet URI from GCS into a BigQuery table.
        """
        try:
            from google.cloud import bigquery

            job_config = bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.PARQUET,
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            )

            table_ref = f"{self.client.project}.{self.dataset_id}.{self.table_id}"
            load_job = self.client.load_table_from_uri(
                uri, table_ref, job_config=job_config
            )

            load_job.result()  # Wait for completion
            logger.info(f"Successfully loaded {uri} into {table_ref}")
            return True
        except Exception as e:
            logger.error(f"Failed to load Parquet to BigQuery: {e}")
            return False

    def sync_partition(self, partition_date: str) -> bool:
        """
        Syncs a specific daily partition from GCS to BigQuery.
        """
        # In a real build, this resolves gs://bucket/logs/YYYY-MM-DD/*.parquet
        uri = f"gs://{get_settings().GCS_GOLD_BUCKET}/telemetry/{partition_date}/*.parquet"
        return self.sync_parquet_to_bq(uri)

    def create_performance_view(self, view_id: str) -> bool:
        """
        Creates or updates a BigQuery view for longitudinal analysis.
        """
        try:
            from google.cloud import bigquery

            view_ref = f"{self.client.project}.{self.dataset_id}.{view_id}"
            view = bigquery.Table(view_ref)

            # Example SQL for performance analysis
            sql = f"""
                SELECT
                    source,
                    event_type,
                    AVG(CAST(JSON_VALUE(payload.latency_ms) AS FLOAT64)) as avg_latency,
                    COUNT(*) as event_count,
                    TIMESTAMP_TRUNC(timestamp, HOUR) as hour
                FROM `{self.client.project}.{self.dataset_id}.{self.table_id}`
                GROUP BY 1, 2, 5
            """

            view.view_query = sql
            self.client.create_table(view, exists_ok=True)
            logger.info(f"Successfully created view {view_ref}")
            return True
        except Exception as e:
            logger.error(f"Failed to create BigQuery view: {e}")
            return False


class StorageEfficiencyAuditor:
    """
    Auditor for tracking GCS storage costs and efficiency.
    Follows Osipov's patterns for cloud resource governance.
    """

    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self._client: Optional[storage.Client] = None

    @property
    def client(self) -> storage.Client:
        if self._client is None:
            self._client = storage.Client()
        return self._client

    def generate_efficiency_report(self) -> dict:
        """
        Calculates storage metrics and estimated costs.
        """
        try:
            bucket = self.client.get_bucket(self.bucket_name)
            blobs = bucket.list_blobs()

            total_bytes = 0
            blob_count = 0
            for blob in blobs:
                total_bytes += blob.size
                blob_count += 1

            total_mb = total_bytes / (1024 * 1024)
            # Rough estimate based on GCP Standard Storage ($0.02 per GB)
            monthly_cost = (total_bytes / (1024**3)) * 0.02

            return {
                "bucket": self.bucket_name,
                "total_size_mb": total_mb,
                "blob_count": blob_count,
                "estimated_monthly_cost": monthly_cost,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to generate storage efficiency report: {e}")
            return {"error": str(e)}


class BrandAssetManager:
    """
    Industrial Manager for Brand Assets (Logos, Fonts, etc.).
    Handles uploads to GCS and public URL resolution.
    """

    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self._client: Optional[storage.Client] = None

    @property
    def client(self) -> storage.Client:
        if self._client is None:
            self._client = storage.Client()
        return self._client

    def upload_logo(
        self, file_content: bytes, filename: str, content_type: str, tenant_id: str
    ) -> str:
        """
        Uploads a logo to GCS and returns the public URL.
        """
        try:
            bucket = self.client.get_bucket(self.bucket_name)
            # Isolated path: {tenant_id}/assets/logos/{filename}
            blob = bucket.blob(f"{tenant_id}/assets/logos/{filename}")

            blob.upload_from_string(file_content, content_type=content_type)

            # Make public if required, or use signed URLs
            # For this build, we use public access for simplicity in demo
            blob.make_public()

            logger.info(f"Successfully uploaded logo: {filename} to {self.bucket_name}")
            return blob.public_url
        except Exception as e:
            logger.error(f"Failed to upload logo: {e}")
            raise e

    def upload_raw_asset(
        self, file_content: bytes, filename: str, content_type: str, tenant_id: str
    ) -> str:
        """
        Uploads a raw asset (PDF, PPTX, DOCX) to GCS and returns the public URL.
        """
        try:
            bucket = self.client.get_bucket(self.bucket_name)
            blob = bucket.blob(f"{tenant_id}/assets/raw/{filename}")

            blob.upload_from_string(file_content, content_type=content_type)
            blob.make_public()

            logger.info(
                f"Successfully uploaded raw asset: {filename} to {self.bucket_name}"
            )
            return blob.public_url
        except Exception as e:
            logger.error(f"Failed to upload raw asset: {e}")
            raise e
