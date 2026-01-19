"""
Agent A/B Testing for Raptorflow Backend
====================================

This module provides comprehensive A/B testing capabilities for agent algorithms and responses
with traffic splitting, performance measurement, and statistical analysis.

Features:
- Traffic splitting between agent versions
- Performance comparison and measurement
- Statistical significance testing
- Automatic winner determination
- Configuration management for experiments
- Real-time monitoring and analytics
"""

import asyncio
import json
import logging
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from collections import defaultdict

from .exceptions import ABTestingError

logger = logging.getLogger(__name__)


class ExperimentStatus(Enum):
    """Experiment status types."""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    STOPPED = "stopped"
    CANCELLED = "cancelled"


class TrafficSplitType(Enum):
    """Traffic split types."""
    PERCENTAGE = "percentage"
    WEIGHTED = "weighted"
    RANDOM = "random"
    USER_BASED = "user_based"


class ExperimentType(Enum):
    """Experiment types."""
    AGENT_ALGORITHM = "agent_algorithm"
    RESPONSE_TEMPLATE = "response_template"
    CONFIGURATION = "configuration"
    PROMPT_OPTIMIZATION = "prompt_optimization"


@dataclass
class ExperimentVariant:
    """Experiment variant configuration."""
    
    variant_id: str
    name: str
    description: str
    configuration: Dict[str, Any]
    traffic_split: float  # 0.0 to 1.0
    is_control: bool = False
    agent_name: Optional[str] = None
    model_tier: Optional[str] = None
    custom_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Experiment:
    """A/B testing experiment."""
    
    experiment_id: str
    name: str
    description: str
    experiment_type: ExperimentType
    status: ExperimentStatus
    variants: List[ExperimentVariant]
    traffic_split_type: TrafficSplitType
    target_metric: str
    success_criteria: Dict[str, Any]
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    sample_size: int = 0
    confidence_level: float = 0.0
    statistical_significance: bool = False
    winner: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ExperimentMetrics:
    """Metrics for experiment variants."""
    
    variant_id: str
    impressions: int = 0
    conversions: int = 0
    conversion_rate: float = 0.0
    avg_response_time: float = 0.0
    success_rate: float = 0.0
    error_rate: float = 0.0
    user_satisfaction: float = 0.0
    cost_per_conversion: float = 0.0
    revenue_per_conversion: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class ABTestingManager:
    """A/B testing manager for agent experiments."""
    
    def __init__(self, storage_path: str = "./data/ab_testing"):
        self.storage_path = storage_path
        self.experiments: Dict[str, Experiment] = {}
        self.active_experiments: Dict[str, Experiment] = {}
        self.metrics: Dict[str, Dict[str, ExperimentMetrics]] = defaultdict(dict)
        self._load_experiments()
    
    def _load_experiments(self) -> None:
        """Load experiments from storage."""
        try:
            import os
            os.makedirs(self.storage_path, exist_ok=True)
            
            experiments_file = os.path.join(self.storage_path, "experiments.json")
            if os.path.exists(experiments_file):
                with open(experiments_file, 'r') as f:
                    data = json.load(f)
                    for exp_id, exp_data in data.items():
                        self.experiments[exp_id] = Experiment(**exp_data)
            
            metrics_file = os.path.join(self.storage_path, "metrics.json")
            if os.path.exists(metrics_file):
                with open(metrics_file, 'r') as f:
                    data = json.load(f)
                    for exp_id, variants_data in data.items():
                        for variant_id, metrics_data in variants_data.items():
                            self.metrics[exp_id][variant_id] = ExperimentMetrics(**metrics_data)
            
            logger.info(f"Loaded {len(self.experiments)} experiments and metrics")
            
        except Exception as e:
            logger.error(f"Failed to load experiments: {e}")
    
    def _save_experiments(self) -> None:
        """Save experiments to storage."""
        try:
            import os
            os.makedirs(self.storage_path, exist_ok=True)
            
            experiments_file = os.path.join(self.storage_path, "experiments.json")
            experiments_data = {
                exp_id: {
                    "experiment_id": exp.experiment_id,
                    "name": exp.name,
                    "description": exp.description,
                    "experiment_type": exp.experiment_type.value,
                    "status": exp.status.value,
                    "variants": [
                        {
                            "variant_id": variant.variant_id,
                            "name": variant.name,
                            "description": variant.description,
                            "configuration": variant.configuration,
                            "traffic_split": variant.traffic_split,
                            "is_control": variant.is_control,
                            "agent_name": variant.agent_name,
                            "model_tier": variant.model_tier,
                            "custom_settings": variant.custom_settings
                        }
                        for variant in exp.variants
                    ],
                    "traffic_split_type": exp.traffic_split_type.value,
                    "target_metric": exp.target_metric,
                    "success_criteria": exp.success_criteria,
                    "start_time": exp.start_time.isoformat() if exp.start_time else None,
                    "end_time": exp.end_time.isoformat() if exp.end_time else None,
                    "sample_size": exp.sample_size,
                    "confidence_level": exp.confidence_level,
                    "statistical_significance": exp.statistical_significance,
                    "winner": exp.winner,
                    "created_at": exp.created_at.isoformat(),
                    "updated_at": exp.updated_at.isoformat()
                }
                for exp_id, exp in self.experiments.items()
            }
            
            with open(experiments_file, 'w') as f:
                json.dump(experiments_data, f, indent=2)
            
            metrics_file = os.path.join(self.storage_path, "metrics.json")
            metrics_data = {
                exp_id: {
                    variant_id: {
                        "impressions": metrics.impressions,
                        "conversions": metrics.conversions,
                        "conversion_rate": metrics.conversion_rate,
                        "avg_response_time": metrics.avg_response_time,
                        "success_rate": metrics.success_rate,
                        "error_rate": metrics.error_rate,
                        "user_satisfaction": metrics.user_satisfaction,
                        "cost_per_conversion": metrics.cost_per_conversion,
                        "revenue_per_conversion": metrics.revenue_per_conversion,
                        "timestamp": metrics.timestamp.isoformat()
                    }
                    for variant_id, metrics in self.metrics[exp_id].items()
                }
                for exp_id, variant_metrics in self.metrics.items()
            }
            
            with open(metrics_file, 'w') as f:
                json.dump(metrics_data, f, indent=2)
            
            logger.info("Experiments and metrics saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save experiments: {e}")
            raise ABTestingError(f"Failed to save experiments: {e}")
    
    def create_experiment(self, name: str, description: str, experiment_type: ExperimentType,
                     variants: List[ExperimentVariant], target_metric: str,
                     success_criteria: Dict[str, Any], traffic_split_type: TrafficSplitType = TrafficSplitType.PERCENTAGE) -> str:
        """Create a new A/B testing experiment."""
        try:
            experiment_id = f"exp_{int(time.time())}"
            
            # Validate traffic splits sum to 1.0
            total_split = sum(variant.traffic_split for variant in variants)
            if abs(total_split - 1.0) > 0.001:
                raise ABTestingError(f"Traffic splits must sum to 1.0, got {total_split}")
            
            experiment = Experiment(
                experiment_id=experiment_id,
                name=name,
                description=description,
                experiment_type=experiment_type,
                status=ExperimentStatus.DRAFT,
                variants=variants,
                traffic_split_type=traffic_split_type,
                target_metric=target_metric,
                success_criteria=success_criteria
            )
            
            self.experiments[experiment_id] = experiment
            self._save_experiments()
            
            logger.info(f"Created experiment {experiment_id}: {name}")
            return experiment_id
            
        except Exception as e:
            logger.error(f"Failed to create experiment: {e}")
            raise ABTestingError(f"Failed to create experiment: {e}")
    
    def start_experiment(self, experiment_id: str) -> bool:
        """Start an A/B testing experiment."""
        try:
            if experiment_id not in self.experiments:
                raise ABTestingError(f"Experiment {experiment_id} not found")
            
            experiment = self.experiments[experiment_id]
            if experiment.status != ExperimentStatus.DRAFT:
                raise ABTestingError(f"Experiment {experiment_id} is not in draft status")
            
            experiment.status = ExperimentStatus.RUNNING
            experiment.start_time = datetime.now()
            self.active_experiments[experiment_id] = experiment
            self._save_experiments()
            
            logger.info(f"Started experiment {experiment_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start experiment {experiment_id}: {e}")
            return False
    
    def stop_experiment(self, experiment_id: str) -> bool:
        """Stop an A/B testing experiment."""
        try:
            if experiment_id not in self.experiments:
                raise ABTestingError(f"Experiment {experiment_id} not found")
            
            experiment = self.experiments[experiment_id]
            experiment.status = ExperimentStatus.COMPLETED
            experiment.end_time = datetime.now()
            
            if experiment_id in self.active_experiments:
                del self.active_experiments[experiment_id]
            
            self._save_experiments()
            
            logger.info(f"Stopped experiment {experiment_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop experiment {experiment_id}: {e}")
            return False
    
    def get_variant_for_request(self, experiment_id: str, user_id: Optional[str] = None,
                           user_properties: Optional[Dict[str, Any]] = None) -> Optional[ExperimentVariant]:
        """Get the appropriate variant for a request based on experiment configuration."""
        try:
            if experiment_id not in self.experiments:
                return None
            
            experiment = self.experiments[experiment_id]
            if experiment.status != ExperimentStatus.RUNNING:
                return None
            
            # Simple random assignment for now
            # In a real implementation, this would use more sophisticated logic
            if experiment.traffic_split_type == TrafficSplitType.PERCENTAGE:
                return self._get_percentage_variant(experiment, user_id, user_properties)
            elif experiment.traffic_split_type == TrafficSplitType.WEIGHTED:
                return self._get_weighted_variant(experiment, user_id, user_properties)
            elif experiment.traffic_split_type == TrafficSplitType.RANDOM:
                return self._get_random_variant(experiment, user_id, user_properties)
            elif experiment.traffic_split_type == TrafficSplitType.USER_BASED:
                return self._get_user_based_variant(experiment, user_id, user_properties)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get variant for experiment {experiment_id}: {e}")
            return None
    
    def _get_percentage_variant(self, experiment: Experiment, user_id: Optional[str],
                           user_properties: Optional[Dict[str, Any]]) -> Optional[ExperimentVariant]:
        """Get variant based on percentage split."""
        try:
            # Simple hash-based assignment
            if user_id:
                hash_value = hash(user_id) % 100
            else:
                hash_value = random.randint(0, 99)
            
            cumulative_percentage = 0.0
            for variant in experiment.variants:
                cumulative_percentage += variant.traffic_split
                if hash_value < cumulative_percentage * 100:
                    return variant
            
            # Fallback to first variant
            return experiment.variants[0] if experiment.variants else None
            
        except Exception as e:
            logger.error(f"Failed to get percentage variant: {e}")
            return None
    
    def _get_weighted_variant(self, experiment: Experiment, user_id: Optional[str],
                          user_properties: Optional[Dict[str, Any]]) -> Optional[ExperimentVariant]:
        """Get variant based on weighted split."""
        try:
            # Simple weighted random selection
            total_weight = sum(variant.traffic_split for variant in experiment.variants)
            
            if total_weight == 0:
                return experiment.variants[0] if experiment.variants else None
            
            random_value = random.random() * total_weight
            cumulative_weight = 0.0
            
            for variant in experiment.variants:
                cumulative_weight += variant.traffic_split
                if random_value < cumulative_weight:
                    return variant
            
            # Fallback to first variant
            return experiment.variants[0] if experiment.variants else None
            
        except Exception as e:
            logger.error(f"Failed to get weighted variant: {e}")
            return None
    
    def _get_random_variant(self, experiment: Experiment, user_id: Optional[str],
                        user_properties: Optional[Dict[str, Any]]) -> Optional[ExperimentVariant]:
        """Get variant based on random split."""
        try:
            if not experiment.variants:
                return None
            
            return random.choice(experiment.variants)
            
        except Exception as e:
            logger.error(f"Failed to get random variant: {e}")
            return None
    
    def _get_user_based_variant(self, experiment: Experiment, user_id: Optional[str],
                           user_properties: Optional[Dict[str, Any]]) -> Optional[ExperimentVariant]:
        """Get variant based on user properties."""
        try:
            if not user_id or not user_properties:
                return experiment.variants[0] if experiment.variants else None
            
            # Simple user segment assignment
            user_segment = user_properties.get("segment", "default")
            
            for variant in experiment.variants:
                if variant.configuration.get("target_segment") == user_segment:
                    return variant
            
            # Fallback to control variant
            for variant in experiment.variants:
                if variant.is_control:
                    return variant
            
            return experiment.variants[0] if experiment.variants else None
            
        except Exception as e:
            logger.error(f"Failed to get user-based variant: {e}")
            return None
    
    async def record_metrics(self, experiment_id: str, variant_id: str, metrics: Dict[str, Any]) -> bool:
        """Record metrics for an experiment variant."""
        try:
            if experiment_id not in self.experiments:
                raise ABTestingError(f"Experiment {experiment_id} not found")
            
            # Update or create metrics
            if variant_id not in self.metrics[experiment_id]:
                self.metrics[experiment_id][variant_id] = ExperimentMetrics(variant_id=variant_id)
            
            variant_metrics = self.metrics[experiment_id][variant_id]
            
            # Update metrics based on provided data
            if "impressions" in metrics:
                variant_metrics.impressions += metrics["impressions"]
            
            if "conversions" in metrics:
                variant_metrics.conversions += metrics["conversions"]
            
            if "avg_response_time" in metrics:
                # Update average response time
                current_avg = variant_metrics.avg_response_time
                new_avg = metrics["avg_response_time"]
                if variant_metrics.impressions > 0:
                    variant_metrics.avg_response_time = (current_avg * (variant_metrics.impressions - 1) + new_avg) / variant_metrics.impressions
            
            if "success_rate" in metrics:
                variant_metrics.success_rate = metrics["success_rate"]
            
            if "error_rate" in metrics:
                variant_metrics.error_rate = metrics["error_rate"]
            
            if "user_satisfaction" in metrics:
                variant_metrics.user_satisfaction = metrics["user_satisfaction"]
            
            if "cost_per_conversion" in metrics:
                variant_metrics.cost_per_conversion = metrics["cost_per_conversion"]
            
            if "revenue_per_conversion" in metrics:
                variant_metrics.revenue_per_conversion = metrics["revenue_per_conversion"]
            
            # Calculate conversion rate
            if variant_metrics.impressions > 0:
                variant_metrics.conversion_rate = variant_metrics.conversions / variant_metrics.impressions
            
            variant_metrics.timestamp = datetime.now()
            
            self._save_experiments()
            
            logger.debug(f"Recorded metrics for {experiment_id}:{variant_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record metrics: {e}")
            return False
    
    def calculate_experiment_results(self, experiment_id: str) -> Dict[str, Any]:
        """Calculate experiment results and determine winner."""
        try:
            if experiment_id not in self.experiments:
                raise ABTestingError(f"Experiment {experiment_id} not found")
            
            experiment = self.experiments[experiment_id]
            if experiment.status != ExperimentStatus.COMPLETED:
                return {"error": "Experiment is not completed"}
            
            results = {}
            best_variant = None
            best_score = 0.0
            
            for variant in experiment.variants:
                if variant.variant_id in self.metrics[experiment_id]:
                    metrics = self.metrics[experiment_id][variant.variant_id]
                    
                    # Calculate score based on target metric
                    score = self._calculate_variant_score(experiment, variant, metrics)
                    results[variant.variant_id] = {
                        "score": score,
                        "impressions": metrics.impressions,
                        "conversions": metrics.conversions,
                        "conversion_rate": metrics.conversion_rate,
                        "avg_response_time": metrics.avg_response_time,
                        "success_rate": metrics.success_rate,
                        "error_rate": metrics.error_rate,
                        "user_satisfaction": metrics.user_satisfaction,
                        "cost_per_conversion": metrics.cost_per_conversion,
                        "revenue_per_conversion": metrics.revenue_per_conversion
                    }
                    
                    if score > best_score:
                        best_score = score
                        best_variant = variant.variant_id
            
            # Determine statistical significance
            statistical_significance = self._calculate_statistical_significance(experiment, results)
            
            # Update experiment with results
            experiment.sample_size = sum(
                self.metrics[experiment_id][variant.variant_id].impressions
                for variant in experiment.variants
                if variant.variant_id in self.metrics[experiment_id]
            )
            experiment.confidence_level = self._calculate_confidence_level(experiment, results)
            experiment.statistical_significance = statistical_significance
            experiment.winner = best_variant
            experiment.updated_at = datetime.now()
            
            self._save_experiments()
            
            return {
                "experiment_id": experiment_id,
                "winner": best_variant,
                "statistical_significance": statistical_significance,
                "confidence_level": experiment.confidence_level,
                "sample_size": experiment.sample_size,
                "results": results,
                "success_criteria_met": self._check_success_criteria(experiment, best_variant, results)
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate experiment results: {e}")
            return {"error": str(e)}
    
    def _calculate_variant_score(self, experiment: Experiment, variant: ExperimentVariant, metrics: ExperimentMetrics) -> float:
        """Calculate score for a variant based on target metric."""
        try:
            target_metric = experiment.target_metric.lower()
            
            if target_metric == "conversion_rate":
                return metrics.conversion_rate
            elif target_metric == "revenue_per_conversion":
                return metrics.revenue_per_conversion
            elif target_metric == "user_satisfaction":
                return metrics.user_satisfaction
            elif target_metric == "success_rate":
                return metrics.success_rate
            elif target_metric == "avg_response_time":
                # Lower response time is better
                return 1.0 / (metrics.avg_response_time + 0.001)  # Avoid division by zero
            else:
                # Default to conversion rate
                return metrics.conversion_rate
                
        except Exception as e:
            logger.error(f"Failed to calculate variant score: {e}")
            return 0.0
    
    def _calculate_statistical_significance(self, experiment: Experiment, results: Dict[str, Any]) -> bool:
        """Calculate statistical significance of experiment results."""
        try:
            if len(results) < 2:
                return False
            
            # Simple chi-square test for conversion rates
            import math
            
            control_metrics = None
            treatment_metrics = None
            
            for variant in experiment.variants:
                if variant.variant_id in results:
                    if variant.is_control:
                        control_metrics = results[variant.variant_id]
                    else:
                        treatment_metrics = results[variant.variant_id]
            
            if not control_metrics or not treatment_metrics:
                return False
            
            # Calculate chi-square statistic
            control_conversions = control_metrics["conversions"]
            control_impressions = control_metrics["impressions"]
            treatment_conversions = treatment_metrics["conversions"]
            treatment_impressions = treatment_metrics["impressions"]
            
            if control_impressions == 0 or treatment_impressions == 0:
                return False
            
            control_rate = control_conversions / control_impressions
            treatment_rate = treatment_conversions / treatment_impressions
            
            expected_control = control_impressions * treatment_rate
            expected_treatment = treatment_impressions * control_rate
            
            chi_square = ((treatment_conversions - expected_treatment) ** 2 / expected_treatment +
                         ((control_conversions - expected_control) ** 2 / expected_control))
            
            degrees_of_freedom = 1
            critical_value = 3.841  # Chi-square critical value at 95% confidence
            
            return chi_square > critical_value
            
        except Exception as e:
            logger.error(f"Failed to calculate statistical significance: {e}")
            return False
    
    def _calculate_confidence_level(self, experiment: Experiment, results: Dict[str, Any]) -> float:
        """Calculate confidence level for experiment results."""
        try:
            if len(results) < 2:
                return 0.0
            
            # Simple confidence calculation based on sample size
            total_sample = sum(
                self.metrics[experiment_id][variant.variant_id].impressions
                for variant in experiment.variants
                if variant.variant_id in results
            )
            
            if total_sample < 100:
                return 0.5  # Low confidence for small samples
            elif total_sample < 1000:
                return 0.8  # Medium confidence
            else:
                return 0.95  # High confidence for large samples
                
        except Exception as e:
            logger.error(f"Failed to calculate confidence level: {e}")
            return 0.0
    
    def _check_success_criteria(self, winner_variant: str, results: Dict[str, Any]) -> bool:
        """Check if success criteria are met."""
        try:
            if winner_variant not in results:
                return False
            
            winner_metrics = results[winner_variant]
            success_criteria = self.experiments.get(winner_variant.split("_")[0], {}).get("success_criteria", {})
            
            for criterion, threshold in success_criteria.items():
                if criterion == "min_conversion_rate":
                    if winner_metrics["conversion_rate"] < threshold:
                        return False
                elif criterion == "min_user_satisfaction":
                    if winner_metrics["user_satisfaction"] < threshold:
                        return False
                elif criterion == "max_avg_response_time":
                    if winner_metrics["avg_response_time"] > threshold:
                        return False
                elif criterion == "min_error_rate":
                    if winner_metrics["error_rate"] > threshold:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check success criteria: {e}")
            return False
    
    def get_experiment(self, experiment_id: str) -> Optional[Experiment]:
        """Get experiment by ID."""
        return self.experiments.get(experiment_id)
    
    def get_active_experiments(self) -> List[Experiment]:
        """Get all active experiments."""
        return list(self.active_experiments.values())
    
    def get_experiment_results(self, experiment_id: str) -> Dict[str, Any]:
        """Get experiment results."""
        return self.calculate_experiment_results(experiment_id)
    
    def get_experiment_metrics(self, experiment_id: str, variant_id: Optional[str] = None) -> Optional[ExperimentMetrics]:
        """Get metrics for experiment variant."""
        if experiment_id not in self.metrics:
            return None
        
        if variant_id:
            return self.metrics[experiment_id].get(variant_id)
        
        # Return all variant metrics if no specific variant requested
        return dict(self.metrics[experiment_id])


# Global A/B testing manager instance
_ab_testing_manager: Optional[ABTestingManager] = None


def get_ab_testing_manager(storage_path: Optional[str] = None) -> ABTestingManager:
    """Get or create A/B testing manager."""
    global _ab_testing_manager
    if _ab_testing_manager is None:
        _ab_testing_manager = ABTestingManager(storage_path)
    return _ab_testing_manager


# Convenience functions for backward compatibility
def create_experiment(name: str, description: str, experiment_type: ExperimentType,
                 variants: List[ExperimentVariant], target_metric: str,
                 success_criteria: Dict[str, Any], traffic_split_type: TrafficSplitType = TrafficSplitType.PERCENTAGE) -> str:
    """Create a new A/B testing experiment."""
    manager = get_ab_testing_manager()
    return manager.create_experiment(name, description, experiment_type, variants, target_metric, success_criteria, traffic_split_type)


def start_experiment(experiment_id: str) -> bool:
    """Start an A/B testing experiment."""
    manager = get_ab_testing_manager()
    return manager.start_experiment(experiment_id)


def stop_experiment(experiment_id: str) -> bool:
    """Stop an A/B testing experiment."""
    manager = get_ab_testing_manager()
    return manager.stop_experiment(experiment_id)


def get_variant_for_request(experiment_id: str, user_id: Optional[str] = None,
                           user_properties: Optional[Dict[str, Any]] = None) -> Optional[ExperimentVariant]:
    """Get the appropriate variant for a request."""
    manager = get_ab_testing_manager()
    return manager.get_variant_for_request(experiment_id, user_id, user_properties)


async def record_metrics(experiment_id: str, variant_id: str, metrics: Dict[str, Any]) -> bool:
    """Record metrics for an experiment variant."""
    manager = get_ab_testing_manager()
    return await manager.record_metrics(experiment_id, variant_id, metrics)


def get_experiment_results(experiment_id: str) -> Dict[str, Any]:
    """Get experiment results."""
    manager = get_ab_testing_manager()
    return manager.get_experiment_results(experiment_id)


def get_active_experiments() -> List[Experiment]:
    """Get all active experiments."""
    manager = get_ab_testing_manager()
    return manager.get_active_experiments()
