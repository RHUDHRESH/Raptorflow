"""
Google BigQuery integration for Raptorflow analytics.

Provides data warehouse capabilities for analytics, reporting,
and business intelligence with workspace isolation.
"""

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from google.api_core import exceptions
from google.api_core.retry import Retry
from google.cloud import bigquery, bigquery_storage_v1

from .gcp import get_gcp_client

logger = logging.getLogger(__name__)


class QueryJobStatus(Enum):
    """Query job status."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


@dataclass
class QueryResult:
    """Result of a BigQuery query."""

    success: bool
    rows: List[Dict[str, Any]]
    total_rows: int
    total_bytes_processed: int
    job_id: str
    execution_time_ms: int
    error_message: Optional[str] = None
    schema: Optional[List[Dict[str, Any]]] = None


@dataclass
class InsertResult:
    """Result of BigQuery insert operation."""

    success: bool
    rows_inserted: int
    errors: List[str]
    error_message: Optional[str] = None


@dataclass
class TableInfo:
    """BigQuery table information."""

    table_id: str
    dataset_id: str
    project_id: str
    num_rows: int
    num_bytes: int
    created_at: datetime
    modified_at: datetime
    schema: List[Dict[str, Any]]
    partitioning: Optional[str] = None
    clustering: Optional[List[str]] = None


class BigQueryClient:
    """Google BigQuery client for Raptorflow."""

    def __init__(self, dataset_id: Optional[str] = None):
        self.dataset_id = dataset_id or os.getenv(
            "GCP_BIGQUERY_DATASET", "raptorflow_analytics"
        )
        self.gcp_client = get_gcp_client()
        self.logger = logging.getLogger("bigquery_client")

        # Get BigQuery client
        self.client = self.gcp_client.get_bigquery_client()

        if not self.client:
            raise RuntimeError("BigQuery client not available")

        # Get BigQuery Storage client for fast results
        self.storage_client = bigquery_storage_v1.BigQueryReadClient(
            credentials=self.gcp_client.get_credentials()
        )

        # Initialize dataset
        self._ensure_dataset_exists()

    def _ensure_dataset_exists(self):
        """Ensure BigQuery dataset exists."""
        try:
            dataset_ref = self.client.dataset(self.dataset_id)
            dataset = self.client.get_dataset(dataset_ref)
            self.logger.info(f"Using existing dataset: {self.dataset_id}")
        except exceptions.NotFound:
            try:
                # Create dataset
                dataset_ref = self.client.dataset(self.dataset_id)
                dataset = bigquery.Dataset(dataset_ref)
                dataset.location = self.gcp_client.get_region()
                dataset = self.client.create_dataset(dataset)
                self.logger.info(f"Created new dataset: {self.dataset_id}")
            except Exception as e:
                self.logger.error(f"Failed to create dataset: {e}")
                raise

    def _get_table_ref(self, table_id: str):
        """Get table reference."""
        return self.client.dataset(self.dataset_id).table(table_id)

    async def execute_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        use_legacy_sql: bool = False,
        timeout_seconds: int = 60,
        dry_run: bool = False,
    ) -> QueryResult:
        """Execute BigQuery query."""
        try:
            job_config = bigquery.QueryJobConfig(
                use_legacy_sql=use_legacy_sql, use_query_cache=True, dry_run=dry_run
            )

            # Add query parameters if provided
            if params:
                job_config.query_parameters = [
                    bigquery.ScalarQueryParameter(
                        key, self._infer_param_type(value), value
                    )
                    for key, value in params.items()
                ]

            # Start query job
            query_job = self.client.query(query, job_config=job_config)

            if dry_run:
                return QueryResult(
                    success=True,
                    rows=[],
                    total_rows=0,
                    total_bytes_processed=query_job.total_bytes_processed,
                    job_id=query_job.job_id,
                    execution_time_ms=0,
                    schema=None,
                )

            # Wait for job completion
            start_time = datetime.now()
            results = query_job.result(timeout=timeout_seconds)
            execution_time_ms = int(
                (datetime.now() - start_time).total_seconds() * 1000
            )

            # Convert results to list of dictionaries
            rows = []
            for row in results:
                row_dict = {}
                for field, value in zip(results.schema, row):
                    row_dict[field.name] = value
                rows.append(row_dict)

            # Get schema
            schema = [
                {"name": field.name, "type": field.field_type, "mode": field.mode}
                for field in results.schema
            ]

            self.logger.info(
                f"Query executed successfully: {len(rows)} rows, {query_job.total_bytes_processed} bytes"
            )

            return QueryResult(
                success=True,
                rows=rows,
                total_rows=results.total_rows,
                total_bytes_processed=query_job.total_bytes_processed,
                job_id=query_job.job_id,
                execution_time_ms=execution_time_ms,
                schema=schema,
            )

        except exceptions.GoogleAPICallError as e:
            self.logger.error(f"BigQuery API error: {e}")
            return QueryResult(
                success=False,
                rows=[],
                total_rows=0,
                total_bytes_processed=0,
                job_id="",
                execution_time_ms=0,
                error_message=str(e),
            )
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            return QueryResult(
                success=False,
                rows=[],
                total_rows=0,
                total_bytes_processed=0,
                job_id="",
                execution_time_ms=0,
                error_message=str(e),
            )

    def _infer_param_type(self, value: Any) -> str:
        """Infer BigQuery parameter type from Python value."""
        if isinstance(value, bool):
            return "BOOL"
        elif isinstance(value, int):
            return "INT64"
        elif isinstance(value, float):
            return "FLOAT64"
        elif isinstance(value, str):
            return "STRING"
        elif isinstance(value, datetime):
            return "TIMESTAMP"
        elif isinstance(value, list):
            return "ARRAY"
        elif isinstance(value, dict):
            return "STRUCT"
        else:
            return "STRING"

    async def insert_rows(
        self,
        table_id: str,
        rows: List[Dict[str, Any]],
        skip_invalid_rows: bool = False,
        ignore_unknown_values: bool = False,
        timeout_seconds: int = 60,
    ) -> InsertResult:
        """Insert rows into BigQuery table."""
        try:
            table_ref = self._get_table_ref(table_id)

            errors = []
            rows_inserted = 0

            # Insert rows in batches
            batch_size = 1000
            for i in range(0, len(rows), batch_size):
                batch = rows[i : i + batch_size]

                try:
                    errors_batch = self.client.insert_rows_json(
                        table_ref,
                        batch,
                        skip_invalid_rows=skip_invalid_rows,
                        ignore_unknown_values=ignore_unknown_values,
                        timeout=timeout_seconds,
                    )

                    if errors_batch:
                        errors.extend([str(error) for error in errors_batch])
                    else:
                        rows_inserted += len(batch)

                except exceptions.GoogleAPICallError as e:
                    errors.append(f"Batch {i//batch_size + 1} failed: {str(e)}")

            success = len(errors) == 0 and rows_inserted > 0

            self.logger.info(f"Inserted {rows_inserted} rows into {table_id}")

            return InsertResult(
                success=success,
                rows_inserted=rows_inserted,
                errors=errors,
                error_message=None if success else "; ".join(errors),
            )

        except Exception as e:
            self.logger.error(f"Failed to insert rows into {table_id}: {e}")
            return InsertResult(
                success=False, rows_inserted=0, errors=[str(e)], error_message=str(e)
            )

    async def create_table_if_not_exists(
        self,
        table_id: str,
        schema: List[Dict[str, Any]],
        partitioning: Optional[str] = None,
        clustering: Optional[List[str]] = None,
        description: Optional[str] = None,
    ) -> bool:
        """Create BigQuery table if it doesn't exist."""
        try:
            table_ref = self._get_table_ref(table_id)

            try:
                # Check if table exists
                self.client.get_table(table_ref)
                self.logger.info(f"Table {table_id} already exists")
                return True
            except exceptions.NotFound:
                pass

            # Create schema
            schema_fields = []
            for field in schema:
                schema_field = bigquery.SchemaField(
                    name=field["name"],
                    field_type=field["type"],
                    mode=field.get("mode", "NULLABLE"),
                )

                # Add fields for nested structures
                if field["type"] == "RECORD" and "fields" in field:
                    schema_field.fields = [
                        bigquery.SchemaField(
                            name=sub_field["name"],
                            field_type=sub_field["type"],
                            mode=sub_field.get("mode", "NULLABLE"),
                        )
                        for sub_field in field["fields"]
                    ]

                schema_fields.append(schema_field)

            # Create table
            table = bigquery.Table(table_ref, schema=schema_fields)

            # Add partitioning
            if partitioning:
                table.time_partitioning = bigquery.TimePartitioning(
                    type_=bigquery.TimePartitioningType.DAY, field=partitioning
                )

            # Add clustering
            if clustering:
                table.clustering_fields = clustering

            # Add description
            if description:
                table.description = description

            # Create table
            table = self.client.create_table(table)

            self.logger.info(f"Created table {table_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to create table {table_id}: {e}")
            return False

    async def get_table_info(self, table_id: str) -> Optional[TableInfo]:
        """Get table information."""
        try:
            table_ref = self._get_table_ref(table_id)
            table = self.client.get_table(table_ref)

            # Convert schema
            schema = []
            for field in table.schema:
                field_info = {
                    "name": field.name,
                    "type": field.field_type,
                    "mode": field.mode,
                }

                if field.fields:
                    field_info["fields"] = [
                        {
                            "name": sub_field.name,
                            "type": sub_field.field_type,
                            "mode": sub_field.mode,
                        }
                        for sub_field in field.fields
                    ]

                schema.append(field_info)

            return TableInfo(
                table_id=table.table_id,
                dataset_id=table.dataset_id,
                project_id=table.project,
                num_rows=table.num_rows,
                num_bytes=table.num_bytes,
                created_at=table.created,
                modified_at=table.modified,
                schema=schema,
                partitioning=(
                    table.time_partitioning.field if table.time_partitioning else None
                ),
                clustering=table.clustering_fields if table.clustering_fields else None,
            )

        except exceptions.NotFound:
            self.logger.warning(f"Table {table_id} not found")
            return None
        except Exception as e:
            self.logger.error(f"Failed to get table info for {table_id}: {e}")
            return None

    async def list_tables(self) -> List[str]:
        """List all tables in the dataset."""
        try:
            dataset_ref = self.client.dataset(self.dataset_id)
            tables = list(self.client.list_tables(dataset_ref))

            return [table.table_id for table in tables]

        except Exception as e:
            self.logger.error(f"Failed to list tables: {e}")
            return []

    async def delete_table(self, table_id: str) -> bool:
        """Delete BigQuery table."""
        try:
            table_ref = self._get_table_ref(table_id)
            self.client.delete_table(table_ref)

            self.logger.info(f"Deleted table {table_id}")
            return True

        except exceptions.NotFound:
            self.logger.warning(f"Table {table_id} not found for deletion")
            return False
        except Exception as e:
            self.logger.error(f"Failed to delete table {table_id}: {e}")
            return False

    async def get_query_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get query job status."""
        try:
            job = self.client.get_job(job_id)

            return {
                "job_id": job.job_id,
                "state": job.state,
                "error_result": str(job.error_result) if job.error_result else None,
                "created_at": job.created.isoformat() if job.created else None,
                "started_at": job.started.isoformat() if job.started else None,
                "ended_at": job.ended.isoformat() if job.ended else None,
                "total_bytes_processed": job.total_bytes_processed,
                "destination_table": (
                    f"{job.destination_table.project}.{job.destination_table.dataset_id}.{job.destination_table.table_id}"
                    if job.destination_table
                    else None
                ),
            }

        except Exception as e:
            self.logger.error(f"Failed to get job status for {job_id}: {e}")
            return {"error": str(e)}

    async def cancel_query_job(self, job_id: str) -> bool:
        """Cancel query job."""
        try:
            job = self.client.get_job(job_id)
            job.cancel()

            self.logger.info(f"Cancelled query job {job_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to cancel job {job_id}: {e}")
            return False

    async def get_dataset_usage(self) -> Dict[str, Any]:
        """Get dataset usage statistics."""
        try:
            dataset_ref = self.client.dataset(self.dataset_id)

            # Get all tables
            tables = list(self.client.list_tables(dataset_ref))

            total_rows = 0
            total_bytes = 0
            table_info = {}

            for table in tables:
                try:
                    full_table = self.client.get_table(table.reference)
                    total_rows += full_table.num_rows
                    total_bytes += full_table.num_bytes

                    table_info[table.table_id] = {
                        "num_rows": full_table.num_rows,
                        "num_bytes": full_table.num_bytes,
                        "created_at": (
                            full_table.created.isoformat()
                            if full_table.created
                            else None
                        ),
                        "modified_at": (
                            full_table.modified.isoformat()
                            if full_table.modified
                            else None
                        ),
                        "partitioning": (
                            full_table.time_partitioning.field
                            if full_table.time_partitioning
                            else None
                        ),
                        "clustering": (
                            full_table.clustering_fields
                            if full_table.clustering_fields
                            else None
                        ),
                    }

                except Exception as e:
                    self.logger.warning(
                        f"Failed to get info for table {table.table_id}: {e}"
                    )

            return {
                "dataset_id": self.dataset_id,
                "total_tables": len(tables),
                "total_rows": total_rows,
                "total_bytes": total_bytes,
                "total_bytes_gb": total_bytes / (1024**3),
                "tables": table_info,
            }

        except Exception as e:
            self.logger.error(f"Failed to get dataset usage: {e}")
            return {}

    async def run_analytics_query(
        self,
        workspace_id: str,
        start_date: datetime,
        end_date: datetime,
        metrics: List[str] = None,
    ) -> QueryResult:
        """Run analytics query for workspace."""
        if metrics is None:
            metrics = ["agent_executions", "user_events", "usage_events"]

        # Build query based on requested metrics
        query_parts = []

        if "agent_executions" in metrics:
            query_parts.append(
                f"""
                SELECT
                    'agent_executions' as metric_type,
                    DATE(created_at) as date,
                    agent_type,
                    status,
                    COUNT(*) as count,
                    AVG(execution_time_ms) as avg_execution_time
                FROM `{self.dataset_id}.agent_executions`
                WHERE workspace_id = @workspace_id
                    AND created_at BETWEEN @start_date AND @end_date
                GROUP BY DATE(created_at), agent_type, status
            """
            )

        if "user_events" in metrics:
            query_parts.append(
                f"""
                SELECT
                    'user_events' as metric_type,
                    DATE(created_at) as date,
                    event_type,
                    COUNT(*) as count
                FROM `{self.dataset_id}.user_events`
                WHERE workspace_id = @workspace_id
                    AND created_at BETWEEN @start_date AND @end_date
                GROUP BY DATE(created_at), event_type
            """
            )

        if "usage_events" in metrics:
            query_parts.append(
                f"""
                SELECT
                    'usage_events' as metric_type,
                    DATE(created_at) as date,
                    feature,
                    COUNT(*) as count,
                    SUM(usage_amount) as total_usage
                FROM `{self.dataset_id}.usage_events`
                WHERE workspace_id = @workspace_id
                    AND created_at BETWEEN @start_date AND @end_date
                GROUP BY DATE(created_at), feature
            """
            )

        if not query_parts:
            return QueryResult(
                success=False,
                rows=[],
                total_rows=0,
                total_bytes_processed=0,
                job_id="",
                execution_time_ms=0,
                error_message="No valid metrics specified",
            )

        query = " UNION ALL ".join(query_parts)

        params = {
            "workspace_id": workspace_id,
            "start_date": start_date,
            "end_date": end_date,
        }

        return await self.execute_query(query, params)

    async def export_table_to_gcs(
        self,
        table_id: str,
        gcs_bucket: str,
        gcs_path: str,
        format: str = "CSV",
        compression: str = "GZIP",
    ) -> bool:
        """Export table to Google Cloud Storage."""
        try:
            table_ref = self._get_table_ref(table_id)
            destination_uri = f"gs://{gcs_bucket}/{gcs_path}/*"

            job_config = bigquery.ExtractJobConfig(
                destination_uris=[destination_uri],
                format=format,
                compression=compression,
            )

            # Start extract job
            extract_job = self.client.extract_table(table_ref, job_config=job_config)

            # Wait for completion
            extract_job.result()

            self.logger.info(f"Exported table {table_id} to {destination_uri}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to export table {table_id}: {e}")
            return False

    async def import_table_from_gcs(
        self,
        table_id: str,
        gcs_bucket: str,
        gcs_path: str,
        format: str = "CSV",
        skip_leading_rows: int = 1,
    ) -> bool:
        """Import table from Google Cloud Storage."""
        try:
            table_ref = self._get_table_ref(table_id)
            source_uri = f"gs://{gcs_bucket}/{gcs_path}/*"

            job_config = bigquery.LoadJobConfig(
                source_format=format,
                skip_leading_rows=skip_leading_rows,
                autodetect=True,
                write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            )

            # Start load job
            load_job = self.client.load_table_from_uri(
                source_uri, table_ref, job_config=job_config
            )

            # Wait for completion
            load_job.result()

            self.logger.info(f"Imported table {table_id} from {source_uri}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to import table {table_id}: {e}")
            return False


# Global BigQuery client instance
_bigquery_client: Optional[BigQueryClient] = None


def get_bigquery_client(dataset_id: Optional[str] = None) -> BigQueryClient:
    """Get global BigQuery client instance."""
    global _bigquery_client
    if _bigquery_client is None:
        _bigquery_client = BigQueryClient(dataset_id)
    return _bigquery_client


def initialize_bigquery_client(dataset_id: str) -> BigQueryClient:
    """Initialize BigQuery client with dataset ID."""
    global _bigquery_client
    _bigquery_client = BigQueryClient(dataset_id)
    return _bigquery_client


# Convenience functions
async def execute_query(
    query: str, params: Optional[Dict[str, Any]] = None
) -> QueryResult:
    """Execute BigQuery query."""
    client = get_bigquery_client()
    return await client.execute_query(query, params)


async def insert_rows(table_id: str, rows: List[Dict[str, Any]]) -> InsertResult:
    """Insert rows into BigQuery table."""
    client = get_bigquery_client()
    return await client.insert_rows(table_id, rows)


async def create_table_if_not_exists(
    table_id: str, schema: List[Dict[str, Any]]
) -> bool:
    """Create BigQuery table if it doesn't exist."""
    client = get_bigquery_client()
    return await client.create_table_if_not_exists(table_id, schema)
