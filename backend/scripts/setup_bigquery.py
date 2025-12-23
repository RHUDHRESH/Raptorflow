import os
import argparse
from google.cloud import bigquery
from google.api_core.exceptions import Conflict


def setup_bigquery(project_id: str, dataset_id: str = "raptorflow_analytics"):
    """
    Setup BigQuery Dataset and Table for Industrial Blackbox Telemetry.
    """
    client = bigquery.Client(project=project_id)

    # 1. Create Dataset
    dataset_ref = bigquery.DatasetReference(project_id, dataset_id)
    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = "US"  # Or your preferred region
    dataset.description = "Analytical store for RaptorFlow Blackbox telemetry and outcomes"

    try:
        dataset = client.create_dataset(dataset, timeout=30)
        print(f"Created dataset {project_id}.{dataset_id}")
    except Conflict:
        print(f"Dataset {project_id}.{dataset_id} already exists")

    # 2. Create telemetry_stream Table
    table_id = f"{project_id}.{dataset_id}.telemetry_stream"
    schema = [
        bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("move_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("agent_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("trace", "JSON", mode="NULLABLE"),
        bigquery.SchemaField("tokens", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("latency", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
    ]

    table = bigquery.Table(table_id, schema=schema)
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="timestamp",  # Partition by timestamp
    )
    table.clustering_fields = ["agent_id", "move_id"]
    table.description = "High-fidelity execution traces for MLOps analysis"

    try:
        table = client.create_table(table)
        print(f"Created table {table_id}")
    except Conflict:
        print(f"Table {table_id} already exists")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Setup BigQuery for RaptorFlow")
    parser.add_argument("--project", help="GCP Project ID", required=True)
    parser.add_argument("--dataset", help="BigQuery Dataset ID", default="raptorflow_analytics")
    
    args = parser.parse_args()
    setup_bigquery(args.project, args.dataset)
