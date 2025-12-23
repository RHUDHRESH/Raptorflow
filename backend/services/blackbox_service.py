import time
import math
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
    Uses strictly synchronous operations.
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
        row["timestamp"] = telemetry.timestamp.isoformat()

        errors = client.insert_rows_json(table_id, [row])
        if errors:
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

    def attribute_outcome(self, outcome: BlackboxOutcome):
        """Attributes a business outcome to specific campaign/move."""
        # 1. Persist to Supabase
        session = self.vault.get_session()
        data = outcome.model_dump(mode="json")
        session.table("blackbox_outcomes_industrial").insert(data).execute()

        # 2. Stream to BigQuery
        self.stream_outcome_to_bigquery(outcome)

    def stream_outcome_to_bigquery(self, outcome: BlackboxOutcome):
        """Streams outcome data to BigQuery for analytical processing."""
        client = self._get_bigquery_client()
        table_id = f"{self.vault.project_id}.raptorflow_analytics.outcomes_stream"

        # Format for BQ
        row = outcome.model_dump(mode="json")
        row["timestamp"] = outcome.timestamp.isoformat()

        errors = client.insert_rows_json(table_id, [row])
        if errors:
            print(f"BigQuery outcome insertion errors: {errors}")

    def compute_roi(self, campaign_id: UUID, model: AttributionModel = AttributionModel.LINEAR) -> Dict[str, Any]:
        """
        Calculates the Return on Investment for a campaign.
        Aggregates costs from all moves and compares against attributed outcomes.
        """
        session = self.vault.get_session()

        # 1. Get all moves for this campaign, ordered by creation
        moves_res = (
            session.table("moves")
            .select("id")
            .eq("campaign_id", str(campaign_id))
            .order("created_at")
            .execute()
        )
        move_ids = [m["id"] for m in moves_res.data]

        if not move_ids:
            return {"roi": 0.0, "total_cost": 0.0, "total_value": 0.0, "status": "no_moves"}

        # 2. Aggregate costs (tokens * simulated price $0.02/1k)
        total_tokens = sum(self.calculate_move_cost(mid) for mid in move_ids)
        total_cost = (total_tokens / 1000.0) * 0.02

        # 3. Aggregate Outcomes based on Attribution Model
        outcomes_res = (
            session.table("blackbox_outcomes_industrial")
            .select("value", "move_id")
            .eq("campaign_id", str(campaign_id))
            .execute()
        )
        outcomes = outcomes_res.data
        
        total_value = 0.0
        if model == AttributionModel.LINEAR:
            total_value = sum(float(o["value"]) for o in outcomes)
        elif model == AttributionModel.FIRST_TOUCH:
            first_move_id = move_ids[0]
            total_value = sum(float(o["value"]) for o in outcomes if o.get("move_id") == first_move_id)
        elif model == AttributionModel.LAST_TOUCH:
            last_move_id = move_ids[-1]
            total_value = sum(float(o["value"]) for o in outcomes if o.get("move_id") == last_move_id)

        # 4. ROI Formula: (Value - Cost) / Cost
        roi = ((total_value - total_cost) / total_cost) if total_cost > 0 else 0.0

        return {
            "campaign_id": str(campaign_id),
            "attribution_model": model.value,
            "roi": round(roi, 4),
            "total_cost": round(total_cost, 4),
            "total_value": round(total_value, 4),
            "status": "computed"
        }

    def calculate_momentum_score(self) -> float:
        """
        Calculates a 'Momentum Score' based on outcome-to-token ratio.
        """
        session = self.vault.get_session()
        
        tele_res = session.table("blackbox_telemetry_industrial").select("tokens").execute()
        total_tokens = sum(float(t.get("tokens", 0)) for t in tele_res.data)
        
        out_res = session.table("blackbox_outcomes_industrial").select("value").execute()
        total_value = sum(float(o.get("value", 0)) for o in out_res.data)
        
        if total_tokens == 0:
            return 0.0
            
        return round((total_value / total_tokens) * 1000, 4)

    def calculate_attribution_confidence(self, move_id: str) -> float:
        """Calculates confidence based on telemetry volume."""
        telemetry = self.get_telemetry_by_move(move_id)
        count = len(telemetry)
        if count == 0: return 0.0
        confidence = 0.3 + (0.65 * (math.log10(count) / 2.0))
        return min(round(confidence, 2), 1.0)

    def get_roi_matrix_data(self) -> List[Dict]:
        """Retrieves ROI data for all active campaigns."""
        session = self.vault.get_session()
        camps = session.table("campaigns").select("id", "title").eq("status", "active").execute()
        
        matrix = []
        for c in camps.data:
            roi_res = self.compute_roi(UUID(c["id"]))
            matrix.append({
                "campaign_id": c["id"],
                "title": c["title"],
                "roi": roi_res["roi"],
                "momentum": self.calculate_momentum_score()
            })
        return matrix

    def get_longitudinal_analysis(self, days: int = 90) -> List[Dict[str, Any]]:
        """
        Performs complex longitudinal analysis using BigQuery.
        Aggregates daily costs and outcomes to track performance trends.
        """
        client = self._get_bigquery_client()
        dataset = "raptorflow_analytics"
        project = self.vault.project_id

        query = f"""
            WITH daily_costs AS (
                SELECT 
                    DATE(timestamp) as day,
                    SUM(tokens) as daily_tokens,
                    SUM(tokens / 1000 * 0.02) as estimated_cost
                FROM `{project}.{dataset}.telemetry_stream`
                WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
                GROUP BY day
            ),
            daily_outcomes AS (
                SELECT 
                    DATE(timestamp) as day,
                    SUM(value) as daily_value
                FROM `{project}.{dataset}.outcomes_stream`
                WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
                GROUP BY day
            )
            SELECT 
                c.day,
                c.daily_tokens,
                c.estimated_cost,
                COALESCE(o.daily_value, 0) as daily_value,
                CASE 
                    WHEN c.estimated_cost > 0 THEN (COALESCE(o.daily_value, 0) - c.estimated_cost) / c.estimated_cost
                    ELSE 0 
                END as daily_roi
            FROM daily_costs c
            LEFT JOIN daily_outcomes o ON c.day = o.day
            ORDER BY c.day DESC
        """

        query_job = client.query(query)
        results = query_job.result()

        analysis = []
        for row in results:
            analysis.append({
                "day": str(row.day),
                "tokens": row.daily_tokens,
                "cost": round(row.estimated_cost, 4),
                "value": round(row.daily_value, 4),
                "roi": round(row.daily_roi, 4)
            })

        return analysis

    async def trigger_learning_cycle(self, move_id: str) -> Dict[str, Any]:
        """
        Triggers the multi-agentic learning cycle via LangGraph.
        Summarizes outcomes and telemetry into strategic learnings.
        """
        from backend.graphs.blackbox_analysis import create_blackbox_graph
        
        graph = create_blackbox_graph()
        initial_state = {
            "move_id": move_id,
            "telemetry_data": [],
            "findings": [],
            "outcomes": [],
            "reflection": "",
            "confidence": 0.0,
            "status": []
        }
        
        final_state = await graph.ainvoke(initial_state)
        
        # 1. Process findings into permanent memory
        for finding in final_state.get("findings", []):
            l_type = self.categorize_learning(finding)
            self.upsert_learning_embedding(
                content=finding,
                learning_type=l_type,
                source_ids=[UUID(move_id)]
            )
            
        return {
            "move_id": move_id,
            "findings_count": len(final_state.get("findings", [])),
            "confidence": final_state.get("confidence", 0.0),
            "status": "cycle_complete"
        }

    def attribute_outcome(self, outcome: BlackboxOutcome):
        pass

    def upsert_learning_embedding(self, content: str, learning_type: str, source_ids: List[UUID] = None):
        """Generates embedding and persists learning."""
        embed_model = InferenceProvider.get_embeddings()
        embedding = embed_model.embed_query(content)

        session = self.vault.get_session()
        data = {
            "content": content,
            "embedding": embedding,
            "source_ids": [str(sid) for sid in (source_ids or [])],
            "learning_type": learning_type,
        }
        session.table("blackbox_learnings_industrial").insert(data).execute()

    def search_strategic_memory(self, query: str, limit: int = 5):
        """Vector similarity search on learnings."""
        embed_model = InferenceProvider.get_embeddings()
        query_embedding = embed_model.embed_query(query)

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
        """Links learning to supporting traces."""
        session = self.vault.get_session()
        session.table("blackbox_learnings_industrial").update(
            {"source_ids": [str(tid) for tid in trace_ids]}
        ).eq("id", str(learning_id)).execute()

    def prune_strategic_memory(self, learning_type: str, before: datetime):
        """Removes outdated learnings."""
        session = self.vault.get_session()
        session.table("blackbox_learnings_industrial").delete().eq(
            "learning_type", learning_type
        ).lt("timestamp", before.isoformat()).execute()

    def categorize_learning(self, content: str) -> str:
        """Uses Gemini to classify learning content."""
        llm = InferenceProvider.get_model(model_tier="mundane")
        prompt = f"Categorize this marketing learning as 'strategic', 'tactical', or 'content': {content}"
        response = llm.invoke(prompt)
        category = response.content.strip().lower()
        for label in ["strategic", "tactical", "content"]:
            if label in category: return label
        return "tactical"

    def get_memory_context_for_planner(self, move_type: str, limit: int = 5) -> str:
        """Formats relevant memory for agents."""
        results = self.search_strategic_memory(query=move_type, limit=limit)
        if not results: return ""
        return "\n---\n".join([f"[{r.get('learning_type', '').upper()}] {r.get('content')}" for r in results])