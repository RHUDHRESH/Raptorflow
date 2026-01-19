"""
Agent Auto-scaling for Raptorflow Backend
==========================================

This module provides auto-scaling capabilities for agent instances
based on load metrics and system performance.

Features:
- Dynamic agent scaling based on queue depth and response times
- Performance-based scaling triggers
- Cost optimization through intelligent scaling decisions
- Graceful scale-up and scale-down operations
- Resource utilization monitoring
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from enum import Enum

from .load_balancing import LoadBalancer, get_load_balancer, LoadBalancingStrategy
from .metrics import get_metrics_collector
from .exceptions import AutoScalingError

logger = logging.getLogger(__name__)


class ScalingTrigger(Enum):
    """Auto-scaling triggers."""
    QUEUE_DEPTH = "queue_depth"
    RESPONSE_TIME = "response_time"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    ERROR_RATE = "error_rate"
    TIME_BASED = "time_based"


@dataclass
class AutoScalingConfig:
    """Configuration for auto-scaling."""
    
    min_workers: int = 1
    max_workers: int = 10
    scale_up_threshold: float = 5.0  # Queue depth
    scale_down_threshold: float = 1.0  # Queue depth
    scale_up_cooldown: int = 300  # seconds
    scale_down_cooldown: int = 600  # seconds
    target_response_time: float = 10.0  # seconds
    max_scale_up_steps: int = 2  # Max workers per scaling event
    enable_cost_optimization: bool = True
    cost_threshold_per_hour: float = 10.0  # USD
    metrics_window: int = 300  # seconds for averaging


@dataclass
class ScalingDecision:
    """Decision made by auto-scaler."""
    
    action: str  # scale_up, scale_down, no_action
    reason: str
    timestamp: datetime
    metrics: Dict[str, Any]
    worker_count_before: int
    worker_count_after: int


@dataclass
class AutoScaler:
    """Auto-scaling manager for agent instances."""
    
    def __init__(self, config: AutoScalingConfig):
        self.config = config
        self.load_balancer = get_load_balancer()
        self.metrics_collector = get_metrics_collector()
        self.current_scale = 0
        self.last_scale_time = datetime.now()
        self.scale_history: List[ScalingDecision] = []
        self._is_running = False
        self._monitoring_task: Optional[asyncio.Task] = None
        
        # Scaling state
        self.scale_up_cooldown_until = None
        self.scale_down_cooldown_until = None
    
    async def start(self) -> None:
        """Start auto-scaling."""
        if self._is_running:
            logger.warning("Auto-scaler is already running")
            return
        
        self._is_running = True
        
        # Start monitoring
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        logger.info(f"Auto-scaler started with {self.config.min_workers}-{self.config.max_workers} workers")
    
    async def stop(self) -> None:
        """Stop auto-scaling."""
        if not self._is_running:
            return
        
        self._is_running = False
        
        # Cancel monitoring
        if self._monitoring_task:
            self._monitoring_task.cancel()
            self._monitoring_task = None
        
        logger.info("Auto-scaler stopped")
    
    async def _monitoring_loop(self) -> None:
        """Monitor metrics and make scaling decisions."""
        while self._is_running:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                # Get current metrics
                metrics = await self._get_current_metrics()
                
                # Make scaling decision
                decision = await self._make_scaling_decision(metrics)
                
                if decision.action != "no_action":
                    await self._execute_scaling_decision(decision)
                
                # Record decision
                self.scale_history.append(decision)
                
                logger.info(f"Scaling decision: {decision.action} - {decision.reason}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Auto-scaling monitoring error: {e}")
    
    async def _get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        # Get load balancer metrics
        lb_metrics = await self.load_balancer.get_metrics()
        
        # Get system metrics
        system_metrics = self.metrics_collector.get_system_metrics()
        
        # Calculate averages
        avg_response_time = lb_metrics.get("avg_response_time", 0)
        queue_depth = lb_metrics.get("queue_depth", 0)
        error_rate = lb_metrics.get("error_rate", 0)
        
        return {
            "queue_depth": queue_depth,
            "avg_response_time": avg_response_time,
            "error_rate": error_rate,
            "total_requests": lb_metrics.get("total_requests", 0),
            "active_workers": lb_metrics.get("active_workers", 0),
            "system_metrics": system_metrics,
            "current_scale": self.current_scale,
            "time_since_last_scale": (datetime.now() - self.last_scale_time).total_seconds(),
        }
    
    async def _make_scaling_decision(self, metrics: Dict[str, Any]) -> ScalingDecision:
        """Make scaling decision based on metrics."""
        now = datetime.now()
        
        # Check cooldowns
        if self.scale_up_cooldown_until and now < self.scale_up_cooldown_until:
            return ScalingDecision(
                action="no_action",
                reason="Scale-up cooldown active",
                timestamp=now,
                metrics=metrics,
                worker_count_before=self.current_scale,
                worker_count_after=self.current_scale,
            )
        
        if self.scale_down_cooldown_until and now < self.scale_down_cooldown_until:
            return ScalingDecision(
                action="no_action",
                reason="Scale-down cooldown active",
                timestamp=now,
                metrics=metrics,
                worker_count_before=self.current_scale,
                worker_count_after=self.current_scale,
            )
        
        # Scale up triggers
        scale_up_triggers = [
            metrics["queue_depth"] >= self.config.scale_up_threshold,
            metrics["avg_response_time"] > self.config.target_response_time,
            metrics["error_rate"] > 0.1,  # 10% error rate
        ]
        
        # Scale down triggers
        scale_down_triggers = [
            metrics["queue_depth"] <= self.config.scale_down_threshold,
            metrics["avg_response_time"] < self.config.target_response_time / 2,
            metrics["error_rate"] < 0.05,  # 5% error rate
        ]
        
        # Check scale-up conditions
        if any(scale_up_triggers) and self.current_scale < self.config.max_workers:
            scale_steps = min(
                self.config.max_scale_up_steps,
                self.config.max_workers - self.current_scale
            )
            
            return ScalingDecision(
                action="scale_up",
                reason=f"Scale up triggered: queue_depth={metrics['queue_depth']}, avg_response_time={metrics['avg_response_time']:.2f}s",
                timestamp=now,
                metrics=metrics,
                worker_count_before=self.current_scale,
                worker_count_after=self.current_scale + scale_steps,
            )
        
        # Check scale-down conditions
        elif any(scale_down_triggers) and self.current_scale > self.config.min_workers:
            scale_steps = min(
                self.current_scale - self.config.min_workers,
                2  # Max scale down steps
            )
            
            return ScalingDecision(
                action="scale_down",
                reason=f"Scale down triggered: queue_depth={metrics['queue_depth']}, avg_response_time={metrics['avg_response_time']:.2f}s",
                timestamp=now,
                metrics=metrics,
                worker_count_before=self.current_scale,
                worker_count_after=self.current_scale - scale_steps,
            )
        
        # Cost optimization check
        if self.config.enable_cost_optimization:
            cost_per_hour = await self._calculate_cost_per_hour()
            if cost_per_hour > self.config.cost_threshold_per_hour:
                return ScalingDecision(
                    action="scale_down",
                    reason=f"Cost optimization: cost_per_hour=${cost_per_hour:.2f}",
                    timestamp=now,
                    metrics=metrics,
                    worker_count_before=self.current_scale,
                    worker_count_after=self.current_scale,
                )
        
        return ScalingDecision(
            action="no_action",
            reason="No scaling triggers met",
            timestamp=now,
            metrics=metrics,
            worker_count_before=self.current_scale,
            worker_count_after=self.current_scale,
        )
    
    async def _calculate_cost_per_hour(self) -> float:
        """Calculate cost per hour based on current scale."""
        # This would integrate with billing system
        # For now, use a simple estimation based on worker count
        base_cost_per_worker = 0.50  # $0.50 per hour per worker
        return self.current_scale * base_cost_per_worker
    
    async def _execute_scaling_decision(self, decision: ScalingDecision) -> None:
        """Execute a scaling decision."""
        try:
            if decision.action == "scale_up":
                await self._scale_up(decision.worker_count_after)
            elif decision.action == "scale_down":
                await self._scale_down(decision.worker_count_after)
            
            # Update timing
            self.last_scale_time = datetime.now()
            self.current_scale = decision.worker_count_after
            
            logger.info(f"Executed scaling: {decision.action} to {decision.worker_count_after} workers")
            
        except Exception as e:
            logger.error(f"Failed to execute scaling decision: {e}")
    
    async def _scale_up(self, target_count: int) -> None:
        """Scale up by adding workers."""
        # This would integrate with the load balancer
        # For now, we'll simulate the scaling
        logger.info(f"Scaling up from {self.current_scale} to {target_count} workers")
        
        # In a real implementation, this would:
        # 1. Create new worker instances
        # 2. Add them to the load balancer
        # 3. Update load balancer configuration
        
        # For simulation, just update the scale
        self.current_scale = target_count
        self.scale_up_cooldown_until = datetime.now() + timedelta(seconds=self.config.scale_up_cooldown)
    
    async def _scale_down(self, target_count: int) -> None:
        """Scale down by removing workers."""
        # This would integrate with the load balancer
        # For now, we'll simulate the scaling
        logger.info(f"Scaling down from {self.current_scale} to {target_count} workers")
        
        # In a real implementation, this would:
        # 1. Identify least utilized workers
        # 2. Remove them from the load balancer
        # 3. Update load balancer configuration
        
        # For simulation, just update the scale
        self.current_scale = target_count
        self.scale_down_cooldown_until = datetime.now() + timedelta(seconds=self.config.scale_down_cooldown)
    
    def get_scaling_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get scaling decision history."""
        return [
            {
                "action": decision.action,
                "reason": decision.reason,
                "timestamp": decision.timestamp.isoformat(),
                "worker_count_before": decision.worker_count_before,
                "worker_count_after": decision.worker_count_after,
                "metrics": decision.metrics,
            }
            for decision in self.scale_history[-limit:]
        ]
    
    def get_current_config(self) -> Dict[str, Any]:
        """Get current auto-scaling configuration."""
        return {
            "min_workers": self.config.min_workers,
            "max_workers": self.config.max_workers,
            "current_scale": self.current_scale,
            "scale_up_threshold": self.config.scale_up_threshold,
            "scale_down_threshold": self.config.scale_down_threshold,
            "scale_up_cooldown": self.config.scale_up_cooldown,
            "scale_down_cooldown": self.config.scale_down_cooldown,
            "target_response_time": self.config.target_response_time,
            "enable_cost_optimization": self.config.enable_cost_optimization,
            "cost_threshold_per_hour": self.config.cost_threshold_per_hour,
            "metrics_window": self.config.metrics_window,
        }


# Global auto-scaler instance
_auto_scaler: Optional[AutoScaler] = None


def get_auto_scaler(config: Optional[AutoScalingConfig] = None) -> AutoScaler:
    """Get or create auto-scaler instance."""
    global _auto_scaler
    if _auto_scaler is None:
        _auto_scaler = AutoScaler(config or AutoScalingConfig())
    return _auto_scaler


# Convenience functions for backward compatibility
async def initialize_auto_scaler(agent_registry: AgentRegistry) -> None:
    """Initialize the global auto-scaler."""
    scaler = get_auto_scaler()
    await scaler.start()


async def submit_scaling_request(request_data: Dict[str, Any]) -> str:
    """Submit a request that may trigger scaling."""
    scaler = get_auto_scaler()
    # This would check if scaling is needed
    return await scaler.submit_request(request_data)


async def get_auto_scaler_metrics() -> Dict[str, Any]:
    """Get auto-scaler metrics."""
    scaler = get_auto_scaler()
    return scaler.get_current_config()


async def get_scaling_history() -> List[Dict[str, Any]]:
    """Get auto-scaling history."""
    scaler = get_auto_scaler()
    return scaler.get_scaling_history()
