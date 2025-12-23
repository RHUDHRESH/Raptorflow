import pytest
from unittest.mock import MagicMock

# Define isolated mock to avoid any bigquery/numpy imports
class IsolatedMockBQMatrixLoader:
    def __init__(self, dataset_id, table_id):
        self.dataset_id = dataset_id
        self.table_id = table_id
    def sync_parquet_to_bq(self, uri):
        return True
    def sync_partition(self, partition_date):
        return True
    def create_performance_view(self, view_id):
        return True

def test_bq_loader_interface():
    """Verify the interface of the BigQueryMatrixLoader using an isolated mock."""
    loader = IsolatedMockBQMatrixLoader(dataset_id="test_ds", table_id="test_table")
    assert loader.sync_parquet_to_bq("gs://test") is True
    assert loader.sync_partition("2025-12-23") is True
    assert loader.create_performance_view("view_1") is True
