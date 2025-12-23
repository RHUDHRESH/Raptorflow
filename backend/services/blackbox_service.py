from backend.core.vault import Vault
from backend.models.blackbox import BlackboxTelemetry, BlackboxOutcome, BlackboxLearning


class BlackboxService:
    """
    Industrial-scale Service for the RaptorFlow Blackbox.
    Handles high-volume telemetry, ROI attribution, and strategic learning.
    """

    def __init__(self, vault: Vault):
        self.vault = vault
        self._bigquery_client = None

    def _get_bigquery_client(self):
        """Lazily initializes the BigQuery client."""
        if not self._bigquery_client:
            from google.cloud import bigquery
            self._bigquery_client = bigquery.Client(project=self.vault.project_id)
        return self._bigquery_client

    def log_telemetry(self, telemetry: BlackboxTelemetry):
        """Logs an execution trace to both Supabase and BigQuery."""
        # 1. Persist to Supabase
        session = self.vault.get_session()
        data = telemetry.model_dump(mode="json")
        session.table("blackbox_telemetry_industrial").insert(data).execute()
        
        # 2. Stream to BigQuery
        self.stream_to_bigquery(telemetry)

    def stream_to_bigquery(self, telemetry: BlackboxTelemetry):
        """Streams telemetry data to BigQuery for analytical processing."""
        client = self._get_bigquery_client()
        table_id = f"{self.vault.project_id}.raptorflow_analytics.telemetry_stream"
        
        # Format for BQ
        row = telemetry.model_dump(mode="json")
        # Ensure timestamp is string for JSON ingestion
        row["timestamp"] = telemetry.timestamp.isoformat()
        
        errors = client.insert_rows_json(table_id, [row])
        if errors:
            # In production, we might want to log this to a dead-letter queue
            print(f"BigQuery insertion errors: {errors}")

    def attribute_outcome(self, outcome: BlackboxOutcome):
        """Attributes a business outcome to specific campaign/move."""
        pass

    def generate_learning(self, learning: BlackboxLearning):
        """Persists a new strategic learning into vectorized memory."""
        pass
