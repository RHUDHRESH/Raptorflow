"""
Canonical LLM Cost Logging Service

This service provides the single entrypoint for logging all LLM/model calls
in a budget-aware manner. Writes to the normalized cost_logs table.
"""

from typing import Optional
from decimal import Decimal
from backend.config.settings import settings
from backend.services.cost_tracker import CostTrackerService
from backend.services.supabase_client import supabase_client
from backend.utils.logging_config import get_logger

logger = get_logger("cost")

# Model pricing configuration (USD per 1K tokens)
# Based on approximate Gemini pricing as of late 2024
MODEL_PRICING = {
    # Gemini models
    "gemini-1.5-flash": {"input": 0.000075, "output": 0.0003},  # $0.075 per 1K input, $0.30 per 1K output
    "gemini-1.5-flash-8b": {"input": 0.0000375, "output": 0.00015},  # $0.0375 per 1K input, $0.15 per 1K output
    "gemini-1.5-flash-002": {"input": 0.000075, "output": 0.0003},  # Same pricing
    "gemini-1.5-pro": {"input": 0.00125, "output": 0.005},  # $1.25 per 1K input, $5.00 per 1K output
    "gemini-1.5-pro-002": {"input": 0.00125, "output": 0.005},  # Same as pro

    # Palmyra X4 - WRITER self-deploy model (approximate pricing based on enterprise tier)
    # Using conservative estimates since exact pricing is subscription-based
    "palmyra-x4": {"input": 0.002, "output": 0.008},  # $2.00 per 1K input, $8.00 per 1K output

    # AI21 Jamba Large 1.6 - Self-deploy enterprise model (estimation based on AI21's model family)
    # Using conservative estimates for enterprise long-context model
    "jamba-large-1.6": {"input": 0.0025, "output": 0.010},  # $2.50 per 1K input, $10.00 per 1K output

    # Anthropic Claude models via Vertex (based on standard pricing, may vary)
    "claude-haiku-4-5@20251001": {"input": 0.00025, "output": 0.00125},  # Haiku pricing
    "claude-sonnet-4-5@20250929": {"input": 0.003, "output": 0.015},     # Sonnet pricing
    "claude-haiku-4-5": {"input": 0.00025, "output": 0.00125},           # Alias
    "claude-sonnet-4-5": {"input": 0.003, "output": 0.015},              # Alias

    # Latest Gemini models
    "gemini-2.5-flash-lite": {"input": 0.000075, "output": 0.0003},      # Low cost, high throughput
    "gemini-2.5-flash-preview-09-2025": {"input": 0.000075, "output": 0.0003},  # Balanced thinking model
    "gemini-3-pro-preview": {"input": 0.00125, "output": 0.005},         # Most powerful, multimodal

    # Mistral models
    "mistral-ocr-2505": {"input": 0.001, "output": 0.001},               # Page-based pricing accounted for in tokens

    # Fallback for unknown models (use highest tier to overestimate, never underestimate)
    "unknown": {"input": 0.003, "output": 0.015},  # Use highest tier (Claude Sonnet) as conservative fallback
}


class CostLoggingService:
    """
    Canonical service for logging LLM costs.

    All model calls must go through this service to ensure:
    - Consistent cost tracking
    - Proper workspace/agent linkage
    - Correlation ID tracing
    """

    def __init__(self):
        self.db = supabase_client

    def estimate_cost_usd(self, model: str, total_tokens: int) -> Decimal:
        """
        Estimate cost for a model call.

        Args:
            model: Model identifier (e.g., "gemini-1.5-flash")
            total_tokens: Total tokens (input + output)

        Returns:
            Estimated cost in USD as Decimal
        """
        pricing = MODEL_PRICING.get(model, MODEL_PRICING["unknown"])

        if model not in MODEL_PRICING:
            logger.warning(
                "Unknown model for pricing, using fallback",
                model=model,
                fallback_pricing=pricing
            )

        # For simplicity, assume 50/50 input/output split
        # In production, you'd want actual token breakdowns
        input_tokens = total_tokens // 2
        output_tokens = total_tokens - input_tokens

        input_cost = Decimal(str(input_tokens)) * Decimal(str(pricing["input"]))
        output_cost = Decimal(str(output_tokens)) * Decimal(str(pricing["output"]))

        total_cost = input_cost + output_cost

        return total_cost.quantize(Decimal("0.000001"))  # 6 decimal places

    async def log_llm_call(
        self,
        *,
        workspace_id: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        agent_id: Optional[str] = None,
        agent_run_id: Optional[str] = None,
    ) -> None:
        """
        Log an LLM call to the cost_logs table.

        Args:
            workspace_id: Workspace identifier (required)
            model: Model identifier (e.g., "gemini-1.5-flash")
            prompt_tokens: Input tokens used
            completion_tokens: Output tokens generated
            agent_id: Associated agent UUID (optional)
            agent_run_id: Associated agent run UUID (optional)
        """
        try:
            total_tokens = prompt_tokens + completion_tokens
            estimated_cost_usd = self.estimate_cost_usd(model, total_tokens)

            # Prepare data for cost_logs table (normalized schema)
            log_data = {
                "workspace_id": workspace_id,
                "agent_id": agent_id,
                "agent_run_id": agent_run_id,
                "model": model,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "estimated_cost_usd": float(estimated_cost_usd),  # Store as float for database
            }

            # Insert into normalized cost_logs table
            result = await self.db.insert("cost_logs", log_data)

            logger.info(
                "LLM call logged",
                workspace_id=workspace_id,
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                estimated_cost_usd=float(estimated_cost_usd),
                agent_id=agent_id,
                agent_run_id=agent_run_id,
            )

        except Exception as e:
            logger.error(
                "Failed to log LLM call",
                workspace_id=workspace_id,
                model=model,
                error=str(e),
                # Don't log sensitive details on failure
            )
            # Continue execution - cost logging failure shouldn't crash the app

    async def log_llm_call_from_response(
        self,
        *,
        workspace_id: str,
        model: str,
        agent_id: Optional[str] = None,
        agent_run_id: Optional[str] = None,
        # Future: Add raw_response parameter to extract tokens automatically
    ) -> None:
        """
        Convenience wrapper for logging from model response.

        Currently a stub - will be implemented when ModelDispatcher provides
        actual response structures with token metadata.
        """
        logger.warning("log_llm_call_from_response not yet implemented - use log_llm_call directly")


# Global service instance
cost_logger = CostLoggingService()

# Export the main function for convenience
log_llm_call = cost_logger.log_llm_call
