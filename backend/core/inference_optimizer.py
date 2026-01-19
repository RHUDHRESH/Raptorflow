"""
AI Inference Cost Optimization System
====================================

Intelligent cost optimization for AI inference with real-time token counting,
provider selection, and cost-aware caching strategies.

Features:
- Real-time token counting and cost estimation
- Intelligent provider selection based on cost and performance
- Cost-aware caching decisions
- Budget management and alerts
- Performance vs cost trade-offs
- Dynamic pricing updates
- Usage analytics and forecasting
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
import uuid

import numpy as np
import structlog
import tiktoken

logger = structlog.get_logger(__name__)


class ProviderTier(str, Enum):
    """Provider pricing tiers."""
    
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class OptimizationStrategy(str, Enum):
    """Cost optimization strategies."""
    
    LOWEST_COST = "lowest_cost"
    FASTEST_RESPONSE = "fastest_response"
    BALANCED = "balanced"
    QUALITY_FOCUSED = "quality_focused"
    BUDGET_CONSTRAINED = "budget_constrained"


@dataclass
class ProviderPricing:
    """Provider pricing configuration."""
    
    provider: str
    model: str
    tier: ProviderTier
    
    # Pricing per 1K tokens
    input_token_price: float  # USD per 1K input tokens
    output_token_price: float  # USD per 1K output tokens
    
    # Performance metrics
    avg_response_time: float  # seconds
    reliability_score: float  # 0-1
    quality_score: float  # 0-1
    
    # Limits and quotas
    max_tokens_per_request: int
    requests_per_minute: int
    tokens_per_minute: int
    
    # Additional costs
    context_window_cost: float = 0.0  # Additional cost for large context
    fine_tuning_cost: float = 0.0  # Cost for fine-tuned models
    
    # Metadata
    region: str = "global"
    currency: str = "USD"
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for given token counts."""
        input_cost = (input_tokens / 1000) * self.input_token_price
        output_cost = (output_tokens / 1000) * self.output_token_price
        total_cost = input_cost + output_cost + self.context_window_cost
        return round(total_cost, 6)
    
    def get_cost_per_token(self) -> float:
        """Get average cost per token."""
        return (self.input_token_price + self.output_token_price) / 2000  # Average per token
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "provider": self.provider,
            "model": self.model,
            "tier": self.tier.value,
            "input_token_price": self.input_token_price,
            "output_token_price": self.output_token_price,
            "avg_response_time": self.avg_response_time,
            "reliability_score": self.reliability_score,
            "quality_score": self.quality_score,
            "max_tokens_per_request": self.max_tokens_per_request,
            "requests_per_minute": self.requests_per_minute,
            "tokens_per_minute": self.tokens_per_minute,
            "context_window_cost": self.context_window_cost,
            "fine_tuning_cost": self.fine_tuning_cost,
            "region": self.region,
            "currency": self.currency,
            "last_updated": self.last_updated.isoformat(),
        }


@dataclass
class TokenUsage:
    """Token usage tracking."""
    
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    
    # Cost tracking
    estimated_cost: float = 0.0
    actual_cost: float = 0.0
    
    # Performance tracking
    response_time: float = 0.0
    model_used: str = ""
    provider_used: str = ""
    
    # Metadata
    request_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Calculate total tokens and update timestamp."""
        self.total_tokens = self.input_tokens + self.output_tokens
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "estimated_cost": self.estimated_cost,
            "actual_cost": self.actual_cost,
            "response_time": self.response_time,
            "model_used": self.model_used,
            "provider_used": self.provider_used,
            "request_id": self.request_id,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class BudgetAlert:
    """Budget alert configuration."""
    
    id: str
    user_id: str
    workspace_id: Optional[str] = None
    
    # Budget thresholds
    daily_budget: float = 10.0
    weekly_budget: float = 50.0
    monthly_budget: float = 200.0
    
    # Alert thresholds (percentage)
    daily_alert_threshold: float = 0.8  # 80%
    weekly_alert_threshold: float = 0.8
    monthly_alert_threshold: float = 0.8
    
    # Alert settings
    email_alerts: bool = True
    webhook_url: Optional[str] = None
    slack_webhook: Optional[str] = None
    
    # State
    daily_spent: float = 0.0
    weekly_spent: float = 0.0
    monthly_spent: float = 0.0
    
    last_daily_reset: datetime = field(default_factory=datetime.utcnow)
    last_weekly_reset: datetime = field(default_factory=datetime.utcnow)
    last_monthly_reset: datetime = field(default_factory=datetime.utcnow)
    
    def should_alert(self, period: str) -> Tuple[bool, float]:
        """Check if alert should be triggered for period."""
        if period == "daily":
            spent = self.daily_spent
            budget = self.daily_budget
            threshold = self.daily_alert_threshold
        elif period == "weekly":
            spent = self.weekly_spent
            budget = self.weekly_budget
            threshold = self.weekly_alert_threshold
        elif period == "monthly":
            spent = self.monthly_spent
            budget = self.monthly_budget
            threshold = self.monthly_alert_threshold
        else:
            return False, 0.0
        
        percentage = spent / budget if budget > 0 else 0.0
        return percentage >= threshold, percentage
    
    def add_spending(self, amount: float):
        """Add spending to current period."""
        self.daily_spent += amount
        self.weekly_spent += amount
        self.monthly_spent += amount
    
    def reset_daily(self):
        """Reset daily spending."""
        self.daily_spent = 0.0
        self.last_daily_reset = datetime.utcnow()
    
    def reset_weekly(self):
        """Reset weekly spending."""
        self.weekly_spent = 0.0
        self.last_weekly_reset = datetime.utcnow()
    
    def reset_monthly(self):
        """Reset monthly spending."""
        self.monthly_spent = 0.0
        self.last_monthly_reset = datetime.utcnow()


class TokenCounter:
    """Token counting utility using tiktoken."""
    
    def __init__(self):
        self.encoders: Dict[str, tiktoken.Encoding] = {}
    
    def _get_encoder(self, model_name: str) -> tiktoken.Encoding:
        """Get or create encoder for model."""
        if model_name not in self.encoders:
            try:
                # Map common model names to tiktoken encoders
                if "gpt-4" in model_name:
                    encoder_name = "cl100k_base"
                elif "gpt-3.5" in model_name:
                    encoder_name = "cl100k_base"
                elif "claude" in model_name:
                    encoder_name = "cl100k_base"  # Approximation
                else:
                    encoder_name = "cl100k_base"  # Default
                
                self.encoders[model_name] = tiktoken.get_encoding(encoder_name)
            except Exception as e:
                logger.error(f"Error creating encoder for {model_name}: {e}")
                # Fallback to a basic encoder
                self.encoders[model_name] = tiktoken.get_encoding("cl100k_base")
        
        return self.encoders[model_name]
    
    def count_tokens(self, text: str, model_name: str = "gpt-3.5-turbo") -> int:
        """Count tokens in text for given model."""
        try:
            encoder = self._get_encoder(model_name)
            return len(encoder.encode(text))
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            # Fallback: rough estimation (1 token ~ 4 characters)
            return len(text) // 4
    
    def count_messages_tokens(self, messages: List[Dict[str, str]], model_name: str = "gpt-3.5-turbo") -> int:
        """Count tokens in message list."""
        try:
            total_tokens = 0
            for message in messages:
                content = message.get("content", "")
                total_tokens += self.count_tokens(content, model_name)
            
            # Add overhead for message formatting (rough estimate)
            total_tokens += len(messages) * 4  # 4 tokens per message for formatting
            
            return total_tokens
        except Exception as e:
            logger.error(f"Error counting message tokens: {e}")
            # Fallback estimation
            total_text = "".join(msg.get("content", "") for msg in messages)
            return self.count_tokens(total_text, model_name)


class CostOptimizer:
    """Intelligent cost optimization system."""
    
    def __init__(
        self,
        strategy: OptimizationStrategy = OptimizationStrategy.BALANCED,
        budget_alerts: Optional[List[BudgetAlert]] = None,
    ):
        self.strategy = strategy
        self.budget_alerts = budget_alerts or []
        
        # Provider pricing database
        self.provider_pricing: Dict[str, ProviderPricing] = {}
        
        # Token counter
        self.token_counter = TokenCounter()
        
        # Usage tracking
        self.usage_history: List[TokenUsage] = []
        self.daily_usage: Dict[str, float] = {}  # date -> cost
        self.provider_usage: Dict[str, float] = {}  # provider -> cost
        
        # Performance tracking
        self.provider_performance: Dict[str, Dict[str, float]] = {}  # provider -> metrics
        
        # Lock for thread safety
        self._lock = asyncio.Lock()
        
        # Initialize default pricing
        self._initialize_default_pricing()
        
        # Background tasks
        self._cleanup_task = None
        self._running = False
    
    def _initialize_default_pricing(self):
        """Initialize default provider pricing."""
        # OpenAI pricing
        self.provider_pricing["openai:gpt-3.5-turbo"] = ProviderPricing(
            provider="openai",
            model="gpt-3.5-turbo",
            tier=ProviderTier.BASIC,
            input_token_price=0.0015,  # $0.0015 per 1K input tokens
            output_token_price=0.002,  # $0.002 per 1K output tokens
            avg_response_time=1.5,
            reliability_score=0.95,
            quality_score=0.85,
            max_tokens_per_request=4096,
            requests_per_minute=3500,
            tokens_per_minute=90000,
        )
        
        self.provider_pricing["openai:gpt-4"] = ProviderPricing(
            provider="openai",
            model="gpt-4",
            tier=ProviderTier.PRO,
            input_token_price=0.03,  # $0.03 per 1K input tokens
            output_token_price=0.06,  # $0.06 per 1K output tokens
            avg_response_time=3.0,
            reliability_score=0.98,
            quality_score=0.95,
            max_tokens_per_request=8192,
            requests_per_minute=200,
            tokens_per_minute=40000,
        )
        
        self.provider_pricing["openai:gpt-4-turbo"] = ProviderPricing(
            provider="openai",
            model="gpt-4-turbo",
            tier=ProviderTier.PRO,
            input_token_price=0.01,  # $0.01 per 1K input tokens
            output_token_price=0.03,  # $0.03 per 1K output tokens
            avg_response_time=2.0,
            reliability_score=0.97,
            quality_score=0.93,
            max_tokens_per_request=128000,
            requests_per_minute=500,
            tokens_per_minute=150000,
        )
        
        # Google pricing
        self.provider_pricing["google:gemini-pro"] = ProviderPricing(
            provider="google",
            model="gemini-pro",
            tier=ProviderTier.BASIC,
            input_token_price=0.0005,  # $0.0005 per 1K input tokens
            output_token_price=0.0015,  # $0.0015 per 1K output tokens
            avg_response_time=1.2,
            reliability_score=0.94,
            quality_score=0.88,
            max_tokens_per_request=32768,
            requests_per_minute=60,
            tokens_per_minute=32000,
        )
        
        # Anthropic pricing
        self.provider_pricing["anthropic:claude-3-sonnet"] = ProviderPricing(
            provider="anthropic",
            model="claude-3-sonnet",
            tier=ProviderTier.PRO,
            input_token_price=0.003,  # $0.003 per 1K input tokens
            output_token_price=0.015,  # $0.015 per 1K output tokens
            avg_response_time=2.5,
            reliability_score=0.96,
            quality_score=0.92,
            max_tokens_per_request=200000,
            requests_per_minute=1000,
            tokens_per_minute=80000,
        )
    
    async def start(self):
        """Start cost optimizer."""
        if self._running:
            return
        
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_usage_history())
        logger.info("Cost optimizer started")
    
    async def stop(self):
        """Stop cost optimizer."""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("Cost optimizer stopped")
    
    async def estimate_tokens(
        self,
        prompt: str,
        model_name: str = "gpt-3.5-turbo",
        messages: Optional[List[Dict[str, str]]] = None
    ) -> int:
        """Estimate token count for prompt or messages."""
        if messages:
            return self.token_counter.count_messages_tokens(messages, model_name)
        else:
            return self.token_counter.count_tokens(prompt, model_name)
    
    async def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model_name: str,
        provider: str = "openai"
    ) -> float:
        """Estimate cost for given token counts."""
        pricing_key = f"{provider}:{model_name}"
        pricing = self.provider_pricing.get(pricing_key)
        
        if not pricing:
            logger.warning(f"No pricing found for {pricing_key}, using default")
            # Default pricing estimation
            return (input_tokens * 0.001 + output_tokens * 0.002) / 1000
        
        return pricing.calculate_cost(input_tokens, output_tokens)
    
    async def select_optimal_provider(
        self,
        input_tokens: int,
        output_tokens: int,
        requirements: Optional[Dict[str, Any]] = None,
        user_budget: Optional[float] = None
    ) -> Tuple[str, str, float]:
        """Select optimal provider and model based on strategy."""
        requirements = requirements or {}
        
        # Filter available providers based on requirements
        candidates = []
        
        for pricing_key, pricing in self.provider_pricing.items():
            # Check token limits
            if input_tokens + output_tokens > pricing.max_tokens_per_request:
                continue
            
            # Check quality requirements
            if "min_quality" in requirements and pricing.quality_score < requirements["min_quality"]:
                continue
            
            # Check reliability requirements
            if "min_reliability" in requirements and pricing.reliability_score < requirements["min_reliability"]:
                continue
            
            # Check budget constraints
            estimated_cost = pricing.calculate_cost(input_tokens, output_tokens)
            if user_budget and estimated_cost > user_budget:
                continue
            
            candidates.append((pricing_key, pricing, estimated_cost))
        
        if not candidates:
            logger.warning("No suitable providers found, using default")
            return "openai", "gpt-3.5-turbo", 0.0
        
        # Select based on strategy
        if self.strategy == OptimizationStrategy.LOWEST_COST:
            selected = min(candidates, key=lambda x: x[2])
        elif self.strategy == OptimizationStrategy.FASTEST_RESPONSE:
            selected = min(candidates, key=lambda x: x[1].avg_response_time)
        elif self.strategy == OptimizationStrategy.QUALITY_FOCUSED:
            selected = max(candidates, key=lambda x: x[1].quality_score)
        elif self.strategy == OptimizationStrategy.BUDGET_CONSTRAINED:
            selected = min(candidates, key=lambda x: x[2])
        else:  # BALANCED
            # Score based on cost, speed, and quality
            def score(candidate):
                pricing, cost = candidate[1], candidate[2]
                # Normalize scores (lower is better for cost and time, higher for quality)
                cost_score = 1.0 / (1.0 + cost)
                speed_score = 1.0 / (1.0 + pricing.avg_response_time)
                quality_score = pricing.quality_score
                return (cost_score + speed_score + quality_score) / 3
            
            selected = max(candidates, key=lambda x: score(x))
        
        pricing_key, pricing, cost = selected
        provider, model = pricing_key.split(":", 1)
        
        logger.info(f"Selected optimal provider: {provider}:{model} (cost: ${cost:.6f})")
        return provider, model, cost
    
    async def track_usage(
        self,
        input_tokens: int,
        output_tokens: int,
        actual_cost: float,
        response_time: float,
        model_used: str,
        provider_used: str,
        request_id: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Track token usage and cost."""
        async with self._lock:
            usage = TokenUsage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                actual_cost=actual_cost,
                response_time=response_time,
                model_used=model_used,
                provider_used=provider_used,
                request_id=request_id,
                metadata=metadata or {},
            )
            
            # Add to history
            self.usage_history.append(usage)
            
            # Update daily usage
            date_str = usage.timestamp.strftime("%Y-%m-%d")
            self.daily_usage[date_str] = self.daily_usage.get(date_str, 0.0) + actual_cost
            
            # Update provider usage
            provider_key = f"{provider_used}:{model_used}"
            self.provider_usage[provider_key] = self.provider_usage.get(provider_key, 0.0) + actual_cost
            
            # Update provider performance
            if provider_key not in self.provider_performance:
                self.provider_performance[provider_key] = {
                    "total_requests": 0,
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "avg_response_time": 0.0,
                    "success_rate": 1.0,
                }
            
            perf = self.provider_performance[provider_key]
            perf["total_requests"] += 1
            perf["total_tokens"] += usage.total_tokens
            perf["total_cost"] += actual_cost
            
            # Update average response time
            total_requests = perf["total_requests"]
            current_avg = perf["avg_response_time"]
            perf["avg_response_time"] = (current_avg * (total_requests - 1) + response_time) / total_requests
            
            # Update budget alerts
            for alert in self.budget_alerts:
                alert.add_spending(actual_cost)
                await self._check_budget_alert(alert)
    
    async def _check_budget_alert(self, alert: BudgetAlert):
        """Check and trigger budget alerts."""
        # Reset counters if needed
        now = datetime.utcnow()
        
        if (now - alert.last_daily_reset).days >= 1:
            alert.reset_daily()
        
        if (now - alert.last_weekly_reset).days >= 7:
            alert.reset_weekly()
        
        if (now - alert.last_monthly_reset).days >= 30:
            alert.reset_monthly()
        
        # Check alerts
        for period in ["daily", "weekly", "monthly"]:
            should_alert, percentage = alert.should_alert(period)
            if should_alert:
                await self._trigger_budget_alert(alert, period, percentage)
    
    async def _trigger_budget_alert(self, alert: BudgetAlert, period: str, percentage: float):
        """Trigger budget alert."""
        logger.warning(
            f"Budget alert for user {alert.user_id}: "
            f"{period} spending at {percentage:.1%}"
        )
        
        # Here you would implement actual alert sending
        # Email, webhook, Slack, etc.
    
    async def _cleanup_usage_history(self):
        """Background task to cleanup old usage history."""
        while self._running:
            try:
                # Keep only last 30 days of usage history
                cutoff_date = datetime.utcnow() - timedelta(days=30)
                
                async with self._lock:
                    self.usage_history = [
                        usage for usage in self.usage_history
                        if usage.timestamp > cutoff_date
                    ]
                
                await asyncio.sleep(3600)  # Check every hour
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in usage history cleanup: {e}")
                await asyncio.sleep(3600)
    
    async def get_cost_analysis(self, days: int = 30) -> Dict[str, Any]:
        """Get cost analysis for the last N days."""
        async with self._lock:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            recent_usage = [
                usage for usage in self.usage_history
                if usage.timestamp > cutoff_date
            ]
            
            if not recent_usage:
                return {"error": "No usage data available"}
            
            # Calculate statistics
            total_cost = sum(usage.actual_cost for usage in recent_usage)
            total_tokens = sum(usage.total_tokens for usage in recent_usage)
            total_requests = len(recent_usage)
            avg_response_time = sum(usage.response_time for usage in recent_usage) / total_requests
            
            # Provider breakdown
            provider_costs = {}
            for usage in recent_usage:
                provider_key = f"{usage.provider_used}:{usage.model_used}"
                provider_costs[provider_key] = provider_costs.get(provider_key, 0.0) + usage.actual_cost
            
            # Daily breakdown
            daily_costs = {}
            for usage in recent_usage:
                date_str = usage.timestamp.strftime("%Y-%m-%d")
                daily_costs[date_str] = daily_costs.get(date_str, 0.0) + usage.actual_cost
            
            return {
                "period_days": days,
                "total_cost": round(total_cost, 6),
                "total_tokens": total_tokens,
                "total_requests": total_requests,
                "avg_cost_per_request": round(total_cost / total_requests, 6),
                "avg_cost_per_token": round(total_cost / total_tokens, 6) if total_tokens > 0 else 0,
                "avg_response_time": round(avg_response_time, 2),
                "provider_breakdown": provider_costs,
                "daily_costs": daily_costs,
                "cost_per_day": round(total_cost / days, 6),
            }
    
    async def get_provider_recommendations(
        self,
        input_tokens: int,
        output_tokens: int,
        requirements: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get provider recommendations with cost analysis."""
        recommendations = []
        
        for pricing_key, pricing in self.provider_pricing.items():
            # Check if provider can handle the request
            if input_tokens + output_tokens > pricing.max_tokens_per_request:
                continue
            
            cost = pricing.calculate_cost(input_tokens, output_tokens)
            provider, model = pricing_key.split(":", 1)
            
            # Get performance data
            perf = self.provider_performance.get(pricing_key, {})
            
            recommendation = {
                "provider": provider,
                "model": model,
                "estimated_cost": cost,
                "estimated_time": pricing.avg_response_time,
                "reliability_score": pricing.reliability_score,
                "quality_score": pricing.quality_score,
                "tier": pricing.tier.value,
                "actual_performance": {
                    "total_requests": perf.get("total_requests", 0),
                    "avg_response_time": perf.get("avg_response_time", pricing.avg_response_time),
                    "success_rate": perf.get("success_rate", 1.0),
                },
                "pricing": pricing.to_dict(),
            }
            
            recommendations.append(recommendation)
        
        # Sort by cost (lowest first)
        recommendations.sort(key=lambda x: x["estimated_cost"])
        
        return recommendations
    
    async def update_pricing(self, pricing_updates: List[ProviderPricing]):
        """Update provider pricing."""
        async with self._lock:
            for pricing in pricing_updates:
                pricing_key = f"{pricing.provider}:{pricing.model}"
                self.provider_pricing[pricing_key] = pricing
                logger.info(f"Updated pricing for {pricing_key}")


# Global cost optimizer
_cost_optimizer: Optional[CostOptimizer] = None


async def get_cost_optimizer() -> CostOptimizer:
    """Get or create global cost optimizer."""
    global _cost_optimizer
    if _cost_optimizer is None:
        _cost_optimizer = CostOptimizer()
        await _cost_optimizer.start()
    return _cost_optimizer


async def shutdown_cost_optimizer():
    """Shutdown cost optimizer."""
    global _cost_optimizer
    if _cost_optimizer:
        await _cost_optimizer.stop()
        _cost_optimizer = None
