import time
from functools import wraps
from typing import List
from uuid import UUID

from backend.core.vault import Vault
from backend.inference import InferenceProvider
from backend.models.blackbox import BlackboxLearning, BlackboxOutcome, BlackboxTelemetry


def trace_agent(service, agent_id: str):
    """
    Synchronous decorator to automatically log agent execution to Blackbox.
    Expects the first argument of the decorated function to be move_id (UUID).
    """

    def decorator(func):
        @wraps(func)
        def wrapper(move_id, *args, **kwargs):
            start_time = time.time()
            try:
                result = func(move_id, *args, **kwargs)
                latency = time.time() - start_time

                # Extract token usage if available in result
                tokens = 0
                if isinstance(result, dict):
                    usage = result.get("usage", {})
                    tokens = usage.get("total_tokens", usage.get("tokens", 0))

                # Log telemetry
                telemetry = BlackboxTelemetry(
                    move_id=move_id,
                    agent_id=agent_id,
                    trace={"input": args, "kwargs": kwargs, "output": result},
                    tokens=tokens,
                    latency=latency,
                )
                service.log_telemetry(telemetry)
                return result
            except Exception as e:
                # Log failure telemetry
                latency = time.time() - start_time
                telemetry = BlackboxTelemetry(
                    move_id=move_id,
                    agent_id=agent_id,
                    trace={"error": str(e), "status": "failed"},
                    latency=latency,
                )
                service.log_telemetry(telemetry)
                raise e

        return wrapper

    return decorator


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

    def get_agent_audit_log(self, agent_id: str, limit: int = 100):
        """Retrieves latest telemetry logs for a specific agent."""
        session = self.vault.get_session()
        result = (
            session.table("blackbox_telemetry_industrial")
            .select("*")
            .eq("agent_id", agent_id)
            .order("timestamp", ascending=False)
            .limit(limit)
            .execute()
        )
        return result.data

    def calculate_move_cost(self, move_id: str):
        """Aggregates total token cost for a specific move."""
        session = self.vault.get_session()
        result = (
            session.table("blackbox_telemetry_industrial")
            .select("tokens")
            .eq("move_id", str(move_id))
            .execute()
        )
        return sum(row.get("tokens", 0) for row in result.data)

    def attribute_outcome(self, outcome: BlackboxOutcome):
        """Attributes a business outcome to specific campaign/move."""
        pass

    def generate_learning(self, learning: BlackboxLearning):
        """Persists a new strategic learning into vectorized memory."""
        pass

    def upsert_learning_embedding(
        self, content: str, learning_type: str, source_ids: List[UUID] = None
    ):
        """Generates embedding for a learning and persists to Supabase."""
        # 1. Generate Embedding (Vertex AI)
        embed_model = InferenceProvider.get_embeddings()
        embedding = embed_model.embed_query(content)

        # 2. Persist to Supabase
        session = self.vault.get_session()
        learning_data = {
            "content": content,
            "embedding": embedding,
            "source_ids": [str(sid) for sid in (source_ids or [])],
            "learning_type": learning_type,
        }
        session.table("blackbox_learnings_industrial").insert(learning_data).execute()

    def search_strategic_memory(self, query: str, limit: int = 5):
        """Performs vector similarity search on strategic learnings."""
        # 1. Generate Query Embedding
        embed_model = InferenceProvider.get_embeddings()
        query_embedding = embed_model.embed_query(query)

        # 2. Search via Supabase RPC
        session = self.vault.get_session()
        result = session.rpc(
            "match_blackbox_learnings",
            params={
                "query_embedding": query_embedding,
                "match_threshold": 0.5,
                "match_count": limit,
            },
        ).execute()
        return result.data

    def link_learning_to_evidence(self, learning_id: UUID, trace_ids: List[UUID]):
        """Links a strategic learning to specific execution traces."""
        session = self.vault.get_session()
        session.table("blackbox_learnings_industrial").update(
            {"source_ids": [str(tid) for tid in trace_ids]}
        ).eq("id", str(learning_id)).execute()
