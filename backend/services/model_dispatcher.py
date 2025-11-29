"""
Model Dispatcher Service

Canonical entrypoint for all LLM calls in RaptorFlow.
Routes to Vertex AI (Gemini models) and Palmyra X4 with cost logging, caching, and budget enforcement.

Supported model aliases:
- "fast": gemini-2.5-flash-002 (Vertex)
- "standard": gemini-1.5-pro (Vertex)
- "heavy": palmyra-x4 (WRITER)
- "research": palmyra-x4 (WRITER)
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass

from backend.services.vertex_ai_client import vertex_ai_client
from backend.services.palmyra_client import palmyra_client
from backend.services.jamba_client import jamba_client
from backend.services.cost_logging import cost_logger, log_llm_call
from backend.services.supabase_client import supabase_client
from backend.services.agent_registry import agent_registry
from backend.utils.logging_config import get_logger
from backend.utils.cache import cache as redis_cache
from backend.core.config import get_settings
from backend.core.errors import BudgetExceededError

logger = get_logger("model_dispatcher")

# Get config and extract budget
config = get_settings()
MONTHLY_WORKSPACE_BUDGET_USD = config.monthly_workspace_budget_usd

# Model tier mappings (Gemini + Palmyra X4)
MODEL_MAPPINGS = {
    "fast": "gemini-2.5-flash-002",          # Fast, cheap Gemini
    "standard": "gemini-1.5-pro",            # Standard Gemini Pro
    "heavy": "palmyra-x4",                   # Palmyra X4 - superior performance
    "research": "palmyra-x4",                # Palmyra X4 for research tasks
}

# Model provider mapping
MODEL_PROVIDERS = {
    "gemini-2.5-flash-002": "vertex",
    "gemini-1.5-pro": "vertex",
    "gemini-1.5-pro-extended": "vertex",
    "palmyra-x4": "palmyra",
}


@dataclass
class ModelDispatchRequest:
    """Request structure for model dispatch calls."""
    workspace_id: str
    model: str  # Can be alias ("fast", "standard", "heavy") or full model ID
    messages: list[dict]  # [{"role": "user", "content": "..."}]
    cache_key: Optional[str] = None
    cache_ttl_seconds: int = 86400  # 24 hours default
    agent_id: Optional[str] = None
    agent_run_id: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


@dataclass
class ModelDispatchResponse:
    """Response structure from model dispatch calls."""
    raw_response: str
    model: str  # Resolved model ID
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: float
    cached: bool = False





class ModelDispatcher:
    """
    Canonical LLM dispatch service.

    Features:
    - Model alias resolution (fast/standard/heavy → Gemini models)
    - Budget enforcement ($10/month per workspace)
    - Automatic cost logging via cost_logs table
    - Correlation ID support
    """

    def __init__(self):
        self.supabase = supabase_client

    def _resolve_model(self, model: str) -> tuple[str, str]:
        """Resolve model alias to concrete model ID and provider."""
        if model in MODEL_MAPPINGS:
            resolved_model = MODEL_MAPPINGS[model]
        elif "/" in model or model.startswith("gemini") or model.startswith("palmyra"):
            resolved_model = model
        else:
            # Unknown alias - raise error
            raise ValueError(f"Unknown model: {model}. Use: fast, standard, heavy, research, or full model ID")

        # Determine provider
        provider = MODEL_PROVIDERS.get(resolved_model, "vertex")  # Default to vertex for unknown models

        return resolved_model, provider

    async def _get_current_month_spend(self, workspace_id: str) -> float:
        """Get current month's total spend for workspace."""
        # Calculate first day of current month
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        try:
            # Query cost_logs for this workspace this month
            result = self.supabase.client.table("cost_logs").select(
                "estimated_cost_usd"
            ).eq("workspace_id", workspace_id).gte(
                "created_at", month_start.isoformat()
            ).execute()

            total_spend = sum(float(record["estimated_cost_usd"]) for record in result.data)
            return total_spend

        except Exception as e:
            logger.error("Failed to query workspace spend", workspace_id=workspace_id, error=str(e))
            # On query failure, assume max spend to be conservative
            return MONTHLY_WORKSPACE_BUDGET_USD

    async def _check_budget(self, workspace_id: str, estimated_cost_usd: float) -> None:
        """Check if workspace would exceed monthly budget."""
        current_spend = await self._get_current_month_spend(workspace_id)
        projected_total = current_spend + estimated_cost_usd

        if projected_total > MONTHLY_WORKSPACE_BUDGET_USD:
            logger.warning(
                "Budget exceeded",
                workspace_id=workspace_id,
                current_spend=current_spend,
                new_call_cost=estimated_cost_usd,
                projected_total=projected_total,
                cap=MONTHLY_WORKSPACE_BUDGET_USD,
            )
            raise BudgetExceededError(
                details={
                    "workspace_id": workspace_id,
                    "current_spend_usd": float(current_spend),
                    "new_call_cost_usd": float(estimated_cost_usd),
                    "budget_cap_usd": float(MONTHLY_WORKSPACE_BUDGET_USD),
                },
            )

    async def _maybe_get_cached(self, cache_key: Optional[str]) -> Optional[ModelDispatchResponse]:
        """Get cached response if available."""
        if not cache_key:
            return None

        try:
            cached_data = await redis_cache.get("llm_response", cache_key)
            if cached_data:
                return ModelDispatchResponse(**cached_data)
            return None
        except Exception as e:
            logger.warning("Failed to get cached response", cache_key=cache_key, error=str(e))
            return None

    async def _maybe_set_cached(self, cache_key: Optional[str], response: ModelDispatchResponse, ttl: int) -> None:
        """Cache response in Redis."""
        if not cache_key:
            return

        try:
            # Convert dataclass to dict for serialization
            await redis_cache.set("llm_response", cache_key, response.__dict__, ttl)
        except Exception as e:
            logger.warning("Failed to cache response", cache_key=cache_key, error=str(e))

    async def _is_research_guild_agent(self, workspace_id: str, agent_id: str) -> bool:
        """Check if an agent belongs to the Research Guild (lord-cognition)."""
        if not agent_id or not workspace_id:
            return False

        try:
            # First check if it's lord-cognition directly
            agent_record = await agent_registry.get_agent_by_slug(workspace_id, "lord-cognition")
            if agent_record and agent_record["id"] == agent_id:
                return True

            # Check agent record to see if it's associated with research domain
            # Query agents table to get the agent's guild/domain info
            result = self.supabase.client.table("agents").select("slug, guild, config").eq("id", agent_id).eq("workspace_id", workspace_id)
            data = result.execute()

            if not data.data:
                return False

            agent = data.data[0]
            slug = agent["slug"]

            # Direct lord check
            if slug == "lord-cognition":
                return True

            # Guild check - research guild agents
            guild = agent["guild"]
            if guild == "research":
                return True

            # Check config for research capabilities
            try:
                config = json.loads(agent["config"]) if agent["config"] else {}
                domain = config.get("domain", "")
                capabilities = config.get("capabilities", [])

                if "research" in domain.lower() or "cognition" in domain.lower():
                    return True

                # Check if agent has research-oriented capabilities
                research_capabilities = ["research", "learning", "knowledge_synthesis", "knowledge_acquisition"]
                if any(cap in capabilities for cap in research_capabilities):
                    return True
            except Exception:
                pass  # Ignore config parsing errors

            return False

        except Exception as e:
            logger.warning("Failed to check if agent belongs to research guild", agent_id=agent_id, error=str(e))
            return False

    async def dispatch(self, request: ModelDispatchRequest) -> ModelDispatchResponse:
        """
        Main entrypoint for LLM calls.

        Args:
            request: ModelDispatchRequest with call parameters

        Returns:
            ModelDispatchResponse with results and metadata

        Raises:
            BudgetExceededError: If workspace would exceed monthly budget
            ValueError: For invalid model specifications
            Exception: For Vertex AI failures
        """
        # Check cache first
        cached = await self._maybe_get_cached(request.cache_key)
        if cached:
            logger.info("Cache hit", cache_key=request.cache_key, model=request.model)
            return ModelDispatchResponse(
                **cached.__dict__,
                cached=True
            )

        # GUILD-SPECIFIC MODEL ROUTING: Research Guild agents ALWAYS use Palmyra X4
        is_research_guild_agent = await self._is_research_guild_agent(request.workspace_id, request.agent_id)
        if is_research_guild_agent:
            logger.info("Automatically routing Research Guild agent to Palmyra X4",
                       agent_id=request.agent_id, original_model=request.model)
            resolved_model, provider = "palmyra-x4", "palmyra"
        else:
            # Resolve model and provider normally
            resolved_model, provider = self._resolve_model(request.model)

        # Prepare for budget check - estimate cost based on char count
        # (We'll get real token counts after the call)
        prompt_text = ""
        for msg in request.messages:
            if isinstance(msg, dict):
                prompt_text += str(msg.get("content", ""))
            else:
                prompt_text += str(msg)
        
        # Standard heuristic: ~4 characters per token
        estimated_total_tokens = len(prompt_text) // 4
        if estimated_total_tokens == 0:
            estimated_total_tokens = 100 # Minimum fallback

        estimated_cost_usd = cost_logger.estimate_cost_usd(resolved_model, estimated_total_tokens)

        # Check budget before making the call
        await self._check_budget(request.workspace_id, estimated_cost_usd)

        # Route to appropriate client based on provider
        if provider == "palmyra":
            # Use Palmyra X4 client
            raw_response = await palmyra_client.chat_completion(
                messages=request.messages,  # Palmyra client handles message formatting
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=False  # TODO: Add streaming support for Palmyra
            )
        else:
            # Use Vertex AI client (Gemini)
            messages = []
            for msg in request.messages:
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    messages.append({"role": msg["role"], "content": msg["content"]})
                else:
                    # Assume it's a plain string
                    messages.append({"role": "user", "content": str(msg)})

            # Map our model resolution to vertex client's model_type
            if "flash" in resolved_model.lower():
                model_type = "fast"
            elif "extended" in resolved_model.lower():
                model_type = "heavy"
            else:
                model_type = "standard"

            # Make the Vertex AI call
            raw_response = await vertex_ai_client.chat_completion(
                messages=messages,
                model_type=model_type,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )

        # Extract tokens from response (depends on Vertex response structure)
        # For now, we'll stub realistic token counts
        # TODO: Extract real token counts from Vertex response once integration is complete
        prompt_tokens = len(str(messages)) // 4  # Rough character-to-token estimate
        completion_tokens = len(raw_response) // 4
        actual_total_tokens = prompt_tokens + completion_tokens
        actual_cost_usd = cost_logger.estimate_cost_usd(resolved_model, actual_total_tokens)

        # Log the cost (ensure this happens before returning)
        await log_llm_call(
            workspace_id=request.workspace_id,
            model=resolved_model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            agent_id=request.agent_id,
            agent_run_id=request.agent_run_id,
        )

        # Build response
        response = ModelDispatchResponse(
            raw_response=raw_response,
            model=resolved_model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=actual_total_tokens,
            estimated_cost_usd=actual_cost_usd,
            cached=False,
        )

        # Cache if requested
        await self._maybe_set_cached(request.cache_key, response, request.cache_ttl_seconds)

        logger.info(
            "LLM call completed",
            workspace_id=request.workspace_id,
            model=resolved_model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=actual_total_tokens,
            estimated_cost_usd=actual_cost_usd,
            cached=False,
        )

        return response


# Global instance
model_dispatcher = ModelDispatcher()

# Convenience function for backward compatibility
dispatch = model_dispatcher.dispatch
