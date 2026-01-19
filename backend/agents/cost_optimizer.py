"""
Agent Cost Optimization for Raptorflow Backend
======================================

This module provides comprehensive cost optimization for agent operations
with token counting, provider selection, caching, and request batching.

Features:
- Token counting and cost tracking per agent and model
- Dynamic provider selection based on cost and performance
- Intelligent caching strategies to reduce LLM costs
- Request batching for efficiency
- Cost budget management and alerts
- Performance-based model routing
- Cost optimization recommendations
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field, from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from collections import defaultdict

from .exceptions import CostOptimizationError

logger = logging.getLogger(__name__)


class ModelTier(Enum):
    """Model tiers for cost calculation."""
    FLASH_LITE = "flash_lite"
    FLASH = "flash"
    PRO = "pro"


class ProviderType(Enum):
    """LLM provider types."""
    GOOGLE = "google"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"


@dataclass
class CostMetrics:
    """Cost metrics for tracking."""
    
    agent_name: str
    model_tier: ModelTier
    provider: ProviderType
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cost: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    request_id: str = ""
    session_id: str = ""
    user_id: str = ""


@dataclass
class CostBudget:
    """Cost budget configuration."""
    
    daily_budget: float = 100.0  # USD
    monthly_budget: float = 3000.0  # USD
    per_user_budget: float = 50.0  # USD
    per_request_budget: float = 0.1  # USD
    alert_threshold: float = 0.8  # 80% of budget
    cooldown_period: int = 300  # 5 minutes
    user_blacklist: List[str] = field(default_factory=list)


@dataclass
class CostOptimizationConfig:
    """Configuration for cost optimization."""
    
    enable_optimization: bool = True
    default_provider: ProviderType = ProviderType.GOOGLE
    cost_threshold_per_request: float = 1.0  # USD
    cache_ttl: int = 3600  # 1 hour
    batch_size: int = 10
    max_batch_wait_time: int = 5  # seconds
    enable_budget_management: bool = True
    enable_provider_selection: bool = True
    enable_request_batching: bool = True
    performance_weight: float = 0.7  # Weight for performance vs cost
    enable_alerts: bool = True


class CostOptimizer:
    """Cost optimization manager for agent operations."""
    
    def __init__(self, config: CostOptimizationConfig):
        self.config = config
        self.cost_metrics: List[CostMetrics] = []
        self.cost_budgets: Dict[str, CostBudget] = {}
        self.provider_costs: Dict[ModelTier, Dict[ProviderType, float]] = {
            ModelTier.FLASH_LITE: {
                ProviderType.GOOGLE: 0.000075,
                ProviderType.OPENAI: 0.00015,
                ProviderType.ANTHROPIC: 0.00025,
                ProviderType.AZURE: 0.0002,
            },
            ModelTier.FLASH: {
                ProviderType.GOOGLE: 0.00015,
                ProviderType.OPENAI: 0.0003,
                ProviderType.ANTHROPIC: 0.0005,
                ProviderType.AZURE: 0.0004,
            },
            ModelTier.PRO: {
                ProviderType.GOOGLE: 0.0025,
                ProviderType.OPENAI: 0.005,
                ProviderType.ANTHROPIC: 0.0075,
                ProviderType.AZURE: 0.01,
            },
        }
        self.request_batch: List[Dict[str, Any]] = []
        self.batch_timer: Optional[float] = None
        self._load_cost_data()
    
    def _load_cost_data(self) -> None:
        """Load cost data from storage."""
        try:
            import os
            os.makedirs("./data/cost_optimization", exist_ok=True)
            
            costs_file = os.path.join("./data/cost_optimization", "costs.json")
            if os.path.exists(costs_file):
                with open(costs_file, 'r') as f:
                    data = json.load(f)
                    self.provider_costs = data.get("provider_costs", {})
            
            budgets_file = os.path.join("./data/cost_optimization", "budgets.json")
            if os.path.exists(budgets_file):
                with open(budgets_file, 'r') as f:
                    data = json.load(f)
                    self.cost_budgets = data.get("budgets", {})
            
            logger.info("Cost data loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load cost data: {e}")
    
    def _save_cost_data(self) -> None:
        """Save cost data to storage."""
        try:
            import os
            os.makedirs("./data/cost_optimization", exist_ok=True)
            
            costs_file = os.path.join("./data/cost_optimization", "costs.json")
            with open(costs_file, 'w') as f:
                json.dump(self.provider_costs, f, indent=2)
            
            budgets_file = os.path.join("./data/cost_optimization", "budgets.json")
            with open(budgets_file, 'w') as f:
                json.dump(self.cost_budgets, f, indent=2)
            
            logger.info("Cost data saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save cost data: {e}")
            raise CostOptimizationError(f"Failed to save cost data: {e}")
    
    def calculate_cost(self, provider: ProviderType, model_tier: ModelTier, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for a request."""
        try:
            if provider not in self.provider_costs or model_tier not in self.provider_costs[provider]:
                logger.warning(f"Unknown provider or model tier: {provider}/{model_tier}")
                return 0.0
            
            cost_per_1k = self.provider_costs[provider][model_tier]
            total_tokens = input_tokens + output_tokens
            cost = (total_tokens / 1000) * cost_per_1k
            
            return cost
            
        except Exception as e:
            logger.error(f"Failed to calculate cost: {e}")
            return 0.0
    
    def get_optimal_provider(self, model_tier: ModelTier, request_data: Dict[str, Any]) -> ProviderType:
        """Get optimal provider based on cost and performance."""
        try:
            if not self.config.enable_provider_selection:
                return self.config.default_provider
            
            # Calculate expected costs for each provider
            provider_costs = {}
            for provider in [ProviderType.GOOGLE, ProviderType.OPENAI, ProviderType.ANTHROPIC]:
                if provider in self.provider_costs and model_tier in self.provider_costs[provider]:
                    provider_costs[provider] = self.calculate_cost(provider, model_tier, 1000, 1000)
            
            # Simple selection based on lowest cost
            # In a real implementation, this would consider performance too
            optimal_provider = min(provider_costs, key=provider_costs.get)
            
            return optimal_provider
            
        except Exception as e:
            logger.error(f"Failed to get optimal provider: {e}")
            return self.config.default_provider
    
    async def track_cost(self, agent_name: str, model_tier: ModelTier, provider: ProviderType,
                    input_tokens: int, output_tokens: int, request_id: str = "",
                    session_id: str = "", user_id: str = "") -> None:
        """Track cost for an agent request."""
        try:
            cost = self.calculate_cost(provider, model_tier, input_tokens, output_tokens)
            
            cost_metric = CostMetrics(
                agent_name=agent_name,
                model_tier=model_tier,
                provider=provider,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                cost=cost,
                timestamp=datetime.now(),
                request_id=request_id,
                session_id=session_id,
                user_id=user_id
            )
            
            self.cost_metrics.append(cost_metric)
            
            # Check budget constraints
            if self.config.enable_budget_management:
                await self._check_budget_constraints(user_id, cost)
            
            logger.debug(f"Tracked cost for {agent_name}: ${cost:.6f}")
            return cost_metric
            
        except Exception as e:
            logger.error(f"Failed to track cost: {e}")
            return None
    
    async def _check_budget_constraints(self, user_id: str, cost: float) -> None:
        """Check if cost exceeds budget constraints."""
        try:
            if not user_id or user_id not in self.cost_budgets:
                return
            
            budget = self.cost_budgets[user_id]
            current_time = datetime.now()
            
            # Check daily budget
            daily_start = current_time.replace(hour=0, minute=0, second=0)
            daily_cost = sum(
                metric.cost for metric in self.cost_metrics
                if metric.user_id == user_id and 
                metric.timestamp >= daily_start and
                metric.timestamp < daily_start + timedelta(days=1)
            )
            
            if daily_cost > budget.daily_budget * budget.alert_threshold:
                logger.warning(f"User {user_id} exceeded daily budget threshold: ${daily_cost:.2f} / ${budget.daily_budget:.2f}")
                # In a real implementation, this would send alerts
            
            # Check monthly budget
            monthly_start = current_time.replace(day=1, hour=0, minute=0, second=0)
            monthly_cost = sum(
                metric.cost for metric in self.cost_metrics
                if metric.user_id == user_id and 
                metric.timestamp >= monthly_start and
                metric.timestamp < monthly_start + timedelta(days=30)
            )
            
            if monthly_cost > budget.monthly_budget * budget.alert_threshold:
                logger.warning(f"User {user_id} exceeded monthly budget threshold: ${monthly_cost:.2f} / ${budget.monthly_budget:.2f}")
            
        except Exception as e:
            logger.error(f"Failed to check budget constraints: {e}")
    
    def should_cache_response(self, request_data: Dict[str, Any], agent_name: str) -> bool:
        """Determine if response should be cached based on cost optimization."""
        try:
            if not self.config.enable_optimization:
                return False
            
            # Cache expensive or frequently repeated requests
            request_hash = hash(json.dumps(request_data, sort_keys=True))
            
            # Check if this is a high-cost request
            estimated_tokens = self._estimate_tokens(request_data)
            if estimated_tokens > 1000:  # High cost request
                return True
            
            # Check cache hit rate for this request pattern
            cache_hit_rate = self._get_cache_hit_rate(request_hash)
            if cache_hit_rate < 0.3:  # Low cache hit rate
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to determine caching decision: {e}")
            return False
    
    def _estimate_tokens(self, request_data: Dict[str, Any]) -> int:
        """Estimate token count for a request."""
        try:
            # Simple estimation based on request length
            text_length = len(str(request_data.get("request", "")))
            
            # Rough estimation: ~4 characters per token
            return max(100, text_length // 4)
            
        except Exception as e:
            logger.error(f"Failed to estimate tokens: {e}")
            return 100
    
    def _get_cache_hit_rate(self, request_hash: str) -> float:
        """Get cache hit rate for a request pattern."""
        try:
            # Simple cache hit rate calculation
            # In a real implementation, this would track actual cache hits
            return 0.5  # Placeholder
            
        except Exception as e:
            logger.error(f"Failed to get cache hit rate: {e}")
            return 0.0
    
    async def batch_requests(self, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Batch multiple requests for efficiency."""
        try:
            if not self.config.enable_request_batching or len(requests) <= 1:
                return requests
            
            logger.info(f"Batching {len(requests)} requests")
            
            # Simple batching logic
            # In a real implementation, this would group compatible requests
            batched_requests = []
            
            for request in requests:
                # Add batching metadata
                batched_request = request.copy()
                batched_request["batch_id"] = f"batch_{int(time.time())}"
                batched_request["batched"] = True
                batched_requests.append(batched_request)
            
            return batched_requests
            
        except Exception as e:
            logger.error(f"Failed to batch requests: {e}")
            return requests
    
    async def process_batch(self, batched_requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a batch of requests."""
        try:
            logger.info(f"Processing batch with {len(batched_requests)} requests")
            
            results = []
            
            # Simple batch processing
            # In a real implementation, this would optimize the batch processing
            for request in batched_requests:
                # Remove batching metadata
                clean_request = {k: v for k, v in request.items() if k not in ["batch_id", "batched"]}
                results.append({"request": clean_request, "result": {"status": "processed"}})
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to process batch: {e}")
            return []
    
    def get_cost_metrics(self, agent_name: Optional[str] = None, user_id: Optional[str] = None,
                     start_time: Optional[datetime] = None, end_time: Optional[datetime] = None,
                     limit: int = 100) -> List[CostMetrics]:
        """Get cost metrics."""
        try:
            filtered_metrics = self.cost_metrics
            
            if agent_name:
                filtered_metrics = [m for m in filtered_metrics if m.agent_name == agent_name]
            
            if user_id:
                filtered_metrics = [m for m in filtered_metrics if m.user_id == user_id]
            
            if start_time:
                filtered_metrics = [m for m in filtered_metrics if m.timestamp >= start_time]
            
            if end_time:
                filtered_metrics = [m for m in filtered_metrics if m.timestamp <= end_time]
            
            # Sort by timestamp (most recent first)
            filtered_metrics.sort(key=lambda x: x.timestamp, reverse=True)
            
            return filtered_metrics[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get cost metrics: {e}")
            return []
    
    def get_cost_summary(self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Get cost summary for a time period."""
        try:
            filtered_metrics = self.cost_metrics
            
            if start_time:
                filtered_metrics = [m for m in filtered_metrics if m.timestamp >= start_time]
            else:
                filtered_metrics = self.cost_metrics
            
            if end_time:
                filtered_metrics = [m for m in filtered_metrics if m.timestamp <= end_time]
            
            if not filtered_metrics:
                return {
                    "total_cost": 0.0,
                    "total_tokens": 0,
                    "total_requests": 0,
                    "avg_cost_per_request": 0.0,
                    "providers": {},
                    "models": {},
                    "period": "No data available"
                }
            
            total_cost = sum(m.cost for m in filtered_metrics)
            total_tokens = sum(m.total_tokens for m in filtered_metrics)
            total_requests = len(set(m.request_id for m in filtered_metrics))
            
            provider_costs = defaultdict(float)
            model_costs = defaultdict(int)
            
            for m in filtered_metrics:
                provider_costs[m.provider] += m.cost
                model_costs[m.model_tier] += 1
            
            avg_cost_per_request = total_cost / total_requests if total_requests > 0 else 0
            
            return {
                "total_cost": total_cost,
                "total_tokens": total_tokens,
                "total_requests": total_requests,
                "avg_cost_per_request": avg_cost_per_request,
                "providers": dict(provider_costs),
                "models": dict(model_costs),
                "period": {
                    "start_time": start_time.isoformat() if start_time else None,
                    "end_time": end_time.isoformat() if end_time else None,
                    "duration_hours": (end_time - start_time).total_seconds() / 3600 if start_time and end_time else 0
                }
                "cost_trends": self._calculate_cost_trends(filtered_metrics)
            }
            
        except Exception as e:
            logger.error(f"Failed to get cost summary: {e}")
            return {"error": str(e)}
    
    def _calculate_cost_trends(self, metrics: List[CostMetrics]) -> Dict[str, Any]:
        """Calculate cost trends from metrics."""
        try:
            if not metrics:
                return {"trends": {}}
            
            # Group by day
            daily_costs = defaultdict(float)
            daily_tokens = defaultdict(int)
            
            for metric in metrics:
                date_key = metric.timestamp.strftime("%Y-%m-%d")
                daily_costs[date_key] += metric.cost
                daily_tokens[date_key] += metric.total_tokens
            
            # Calculate trends
            sorted_dates = sorted(daily_costs.keys())
            if len(sorted_dates) > 1:
                cost_trend = "increasing" if daily_costs[sorted_dates[-1]] > daily_costs[sorted_dates[-2]] else "stable"
                token_trend = "increasing" if daily_tokens[sorted_dates[-1]] > daily_tokens[sorted_dates[-2]] else "stable"
            else:
                cost_trend = "stable"
                token_trend = "stable"
            
            return {
                "trends": {
                    "cost_trend": cost_trend,
                    "token_trend": token_trend,
                    "daily_costs": dict(sorted(daily_costs.items())),
                    "daily_tokens": dict(sorted(daily_tokens.items()))
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate cost trends: {e}")
            return {"trends": {}}
    
    def get_optimization_recommendations(self) -> Dict[str, Any]:
        """Get cost optimization recommendations."""
        try:
            recommendations = []
            
            # Analyze cost metrics
            if self.cost_metrics:
                total_cost = sum(m.cost for m in self.cost_metrics)
                total_tokens = sum(m.total_tokens for m in self.cost_metrics)
                
                # High-cost agents
                agent_costs = defaultdict(float)
                for m in self.cost_metrics:
                    agent_costs[m.agent_name] += m.cost
                
                high_cost_agents = [
                    agent for agent, cost in agent_costs.items() 
                    if cost > total_cost / len(agent_costs) * 1.5
                ]
                
                if high_cost_agents:
                    recommendations.append({
                        "type": "high_cost_agents",
                        "message": f"Agents with high costs: {[agent}: ${cost:.2f} for agent, cost in agent_costs.items()}",
                        "suggestion": "Consider using cheaper model tiers or implementing response caching"
                    })
            
                # Low cache hit rate
                cacheable_requests = 0
                total_requests = len(self.cost_metrics)
                
                if total_requests > 0:
                    cacheable_requests = sum(1 for m in self.cost_metrics if self.should_cache_response({}, m.agent_name))
                
                if cacheable_requests / total_requests < 0.5:
                    recommendations.append({
                        "type": "low_cache_hit_rate",
                        "message": f"Low cache hit rate: {cacheable_requests}/{total_requests:.2f}. Consider implementing more aggressive caching strategies",
                        "suggestion": "Increase cache TTL or implement request deduplication"
                    })
            
                # Inefficient providers
                provider_efficiency = defaultdict(float)
                provider_requests = defaultdict(int)
                
                for m in self.cost_metrics:
                    provider_requests[m.provider] += 1
                    provider_efficiency[m.provider] += m.total_tokens
                
                avg_tokens_per_request = {
                    provider: provider_efficiency[provider] / provider_requests[provider] if provider_requests[provider] > 0 else 1
                    for provider in provider_efficiency
                }
                
                inefficient_providers = [
                    provider for provider, efficiency in avg_tokens_per_request.items()
                    if efficiency < 500  # Less than 500 tokens per request
                ]
                
                if inefficient_providers:
                    recommendations.append({
                        "type": "inefficient_providers",
                        "message": f"Inefficient providers: {inefficient_providers}. Consider optimizing prompts or using more efficient models",
                        "suggestion": f"Average tokens per request: {dict(avg_tokens_per_request)}"
                    })
            
            return {
                "recommendations": recommendations,
                "summary": {
                    "total_cost": total_cost,
                    "total_tokens": total_tokens,
                    "total_requests": len(self.cost_metrics),
                    "avg_cost_per_request": total_cost / len(self.cost_metrics) if self.cost_metrics else 0,
                    "high_cost_agents": len(high_cost_agents),
                    "cache_hit_rate": cacheable_requests / total_requests if total_requests > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get optimization recommendations: {e}")
            return {"recommendations": [], "summary": {}}


# Global cost optimizer instance
_cost_optimizer: Optional[CostOptimizer] = None


def get_cost_optimizer(config: Optional[CostOptimizationConfig] = None) -> CostOptimizer:
    """Get or create cost optimizer."""
    global _cost_optimizer
    if _cost_optimizer is None:
        _cost_optimizer = CostOptimizer(config)
    return _cost_optimizer


# Convenience functions for backward compatibility
async def track_cost(agent_name: str, model_tier: ModelTier, provider: ProviderType,
                 input_tokens: int, output_tokens: int, request_id: str = "",
                 session_id: str = "", user_id: str = "") -> None:
    """Track cost for an agent request."""
    optimizer = get_cost_optimizer()
    return await optimizer.track_cost(agent_name, model_tier, provider, input_tokens, output_tokens, request_id, session_id, user_id)


def get_cost_metrics(agent_name: Optional[str] = None, user_id: Optional[str] = None,
                 start_time: Optional[datetime] = None, end_time: Optional[datetime] = None,
                 limit: int = 100) -> List[CostMetrics]:
    """Get cost metrics."""
    optimizer = get_cost_optimizer()
    return optimizer.get_cost_metrics(agent_name, user_id, start_time, end_time, limit)


def get_cost_summary(start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> Dict[str, Any]:
    """Get cost summary for a time period."""
    optimizer = get_cost_optimizer()
    return optimizer.get_cost_summary(start_time, end_time)


def get_optimization_recommendations() -> Dict[str, Any]:
    """Get cost optimization recommendations."""
    optimizer = get_cost_optimizer()
    return optimizer.get_optimization_recommendations()


def should_cache_response(request_data: Dict[str, Any], agent_name: str) -> bool:
    """Determine if response should be cached."""
    optimizer = get_cost_optimizer()
    return optimizer.should_cache_response(request_data, agent_name)


async def batch_requests(requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Batch multiple requests for efficiency."""
    optimizer = get_cost_optimizer()
    return await optimizer.batch_requests(requests)
