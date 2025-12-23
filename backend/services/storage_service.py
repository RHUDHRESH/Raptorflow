import logging
from typing import Optional, Any
from google.cloud import storage

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
            
            logger.info(f"Archived {count} blobs from {self.source_bucket_name} to {self.target_bucket_name}")
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
        self._client: Optional[Any] = None # Using Any to avoid import crash during setup

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
            
            load_job.result() # Wait for completion
            logger.info(f"Successfully loaded {uri} into {table_ref}")
            return True
        except Exception as e:
            logger.error(f"Failed to load Parquet to BigQuery: {e}")
            return False
