import time
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, Dict, List
from uuid import UUID

from backend.core.vault import Vault
from backend.inference import InferenceProvider
from backend.models.blackbox import BlackboxLearning, BlackboxOutcome, BlackboxTelemetry


class AttributionModel(str, Enum):
    """Supported attribution models for business outcomes."""

    FIRST_TOUCH = "first_touch"
    LAST_TOUCH = "last_touch"
    LINEAR = "linear"


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

    def get_telemetry_by_move(self, move_id: str) -> List[Dict]:
        """Retrieves all telemetry traces associated with a specific move."""
        session = self.vault.get_session()
        result = (
            session.table("blackbox_telemetry_industrial")
            .select("*")
            .eq("move_id", str(move_id))
            .execute()
        )
        return result.data

    def get_outcomes_for_move(self, move_id: str, limit: int = 10) -> List[Dict]:
        """
        Retrieves business outcomes associated with a move.
        In production, this would use complex JOINs or probabilistic attribution.
        """
        session = self.vault.get_session()
        # For now, we fetch recent outcomes as a placeholder for attribution
        result = (
            session.table("blackbox_outcomes_industrial")
            .select("*")
            .limit(limit)
            .execute()
        )
        return result.data

    def compute_roi(
        self, campaign_id: UUID, model: AttributionModel = AttributionModel.LINEAR
    ) -> Dict[str, Any]:
        """
        Calculates the Return on Investment for a campaign.
        Aggregates costs from all moves and compares against attributed outcomes.
        """
        session = self.vault.get_session()

        # 1. Get all moves for this campaign, ordered by timestamp
        moves_res = (
            session.table("moves")
            .select("id", "created_at")
            .eq("campaign_id", str(campaign_id))
            .order("created_at", ascending=True)
            .execute()
        )
        moves = moves_res.data
        move_ids = [m["id"] for m in moves]

        if not move_ids:
            return {
                "roi": 0.0,
                "total_cost": 0.0,
                "total_value": 0.0,
                "status": "no_moves",
            }

        # 2. Aggregate costs (tokens * estimated price)
        # Using a fixed price per 1k tokens for ROI calculation placeholder
        PRICE_PER_1K_TOKENS = 0.02
        total_tokens = 0
        for mid in move_ids:
            cost_tokens = self.calculate_move_cost(mid)
            total_tokens += cost_tokens

        total_cost = (total_tokens / 1000.0) * PRICE_PER_1K_TOKENS

        # 3. Aggregate Outcomes based on model
        # For simplicity in this build, we fetch all outcomes and attribute them to the set of moves.
        outcomes_res = (
            session.table("blackbox_outcomes_industrial").select("value").execute()
        )
        raw_outcomes = outcomes_res.data
        total_raw_value = sum(float(o["value"]) for o in raw_outcomes)

        # Implementation of attribution logic based on model:
        # FIRST_TOUCH: attribute all value to the first move
        # LAST_TOUCH: attribute all value to the last move
        # LINEAR: distribute value equally among all moves (simple sum is linear over moves)
        
        # In this industrial build, since we aggregate at the campaign level, 
        # the total value remains the same regardless of move-level attribution
        # unless we were filtering moves. 
        total_value = total_raw_value 

        # 4. ROI Formula: (Value - Cost) / Cost
        roi = ((total_value - total_cost) / total_cost) if total_cost > 0 else 0.0

        return {
            "campaign_id": str(campaign_id),
            "model": model,
            "roi": roi,
            "total_cost": total_cost,
            "total_value": total_value,
            "token_usage": total_tokens,
        }

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

    def prune_strategic_memory(self, learning_type: str, before: datetime):
        """Removes outdated learnings of a specific type."""
        session = self.vault.get_session()
        session.table("blackbox_learnings_industrial").delete().eq(
            "learning_type", learning_type
        ).lt("timestamp", before.isoformat()).execute()

    def categorize_learning(self, content: str) -> str:
        """Categorizes a learning content into strategic, tactical, or content."""
        from backend.core.prompts import BlackboxPrompts

        # 1. Initialize LLM
        llm = InferenceProvider.get_model(model_tier="driver")

        # 2. Format Prompt
        prompt = BlackboxPrompts.LEARNING_CATEGORIZATION.format(content=content)

        # 3. Invoke LLM
        response = llm.invoke(prompt)
        category = response.content.strip().lower()

        # 4. Validate output
        valid_categories = ["strategic", "tactical", "content"]
        if category not in valid_categories:
            # Default to tactical if uncertain
            return "tactical"

        return category

    def get_memory_context_for_planner(self, move_type: str, limit: int = 5) -> str:
        """Retrieves and formats strategic memory for the move planner."""
        learnings = self.search_strategic_memory(query=move_type, limit=limit)
        if not learnings:
            return "No historical memory found for this move type."

        context_parts = ["### RELEVANT STRATEGIC MEMORY:"]
        for learning in learnings:
            content = learning.get("content", "")
            l_type = learning.get("learning_type", "tactical").upper()
            context_parts.append(f"- [{l_type}] {content}")

        return "\n".join(context_parts)
