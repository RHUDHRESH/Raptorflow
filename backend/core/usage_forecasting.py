"""
Usage Forecasting Manager
==========================

Advanced usage forecasting and capacity planning system with predictive analytics,
resource optimization, and intelligent scaling recommendations.

Features:
- Time series forecasting with multiple models
- Capacity planning and optimization
- Resource scaling recommendations
- Predictive analytics and trend analysis
- Seasonal pattern forecasting
- Cost optimization insights
"""

import asyncio
import time
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import logging

# ML imports for forecasting
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class ForecastModel(Enum):
    """Available forecasting models."""
    LINEAR_REGRESSION = "linear_regression"
    RANDOM_FOREST = "random_forest"
    MOVING_AVERAGE = "moving_average"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    SEASONAL_DECOMPOSITION = "seasonal_decomposition"


class ForecastHorizon(Enum):
    """Forecast time horizons."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


class CapacityStatus(Enum):
    """Capacity status levels."""
    UNDERUTILIZED = "underutilized"
    OPTIMAL = "optimal"
    NEAR_CAPACITY = "near_capacity"
    AT_CAPACITY = "at_capacity"
    OVERLOADED = "overloaded"


class ScalingAction(Enum):
    """Recommended scaling actions."""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    MAINTAIN = "maintain"
    OPTIMIZE = "optimize"
    INVEST = "invest"


@dataclass
class ForecastResult:
    """Forecast result with predictions and confidence."""
    
    forecast_id: str
    model_used: ForecastModel
    horizon: ForecastHorizon
    
    # Predictions
    predicted_values: List[float]
    confidence_intervals: List[Tuple[float, float]]  # (lower, upper)
    timestamps: List[datetime]
    
    # Model performance
    accuracy_score: float
    mean_absolute_error: float
    mean_squared_error: float
    
    # Metadata
    training_data_points: int
    forecast_period_hours: int
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class CapacityPlan:
    """Capacity planning recommendation."""
    
    plan_id: str
    resource_type: str  # compute, storage, bandwidth, etc.
    current_capacity: float
    forecasted_demand: float
    recommended_capacity: float
    
    # Capacity analysis
    utilization_ratio: float
    buffer_ratio: float
    risk_level: str  # low, medium, high, critical
    
    # Scaling recommendations
    scaling_action: ScalingAction
    scaling_factor: float
    scaling_timeline: str  # immediate, hours, days, weeks
    
    # Cost analysis
    current_cost: float
    projected_cost: float
    cost_savings: float
    roi_estimate: float
    
    # Metadata
    confidence: float
    created_at: datetime = field(default_factory=datetime.now)
    valid_until: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=7))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ResourceMetric:
    """Resource usage metric for forecasting."""
    
    timestamp: datetime
    metric_name: str
    value: float
    unit: str
    resource_id: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class ForecastingConfig:
    """Configuration for usage forecasting."""
    
    # Data requirements
    min_training_days: int = 7
    max_training_days: int = 90
    data_quality_threshold: float = 0.8
    
    # Model settings
    primary_model: ForecastModel = ForecastModel.RANDOM_FOREST
    ensemble_models: bool = True
    cross_validation_folds: int = 5
    
    # Forecast settings
    default_horizon_hours: int = 24
    max_horizon_hours: int = 720  # 30 days
    confidence_level: float = 0.95
    
    # Capacity planning
    capacity_buffer_ratio: float = 0.2  # 20% buffer
    utilization_threshold_high: float = 0.8
    utilization_threshold_low: float = 0.3
    
    # Performance
    forecast_interval_minutes: int = 60
    batch_processing: bool = True
    enable_caching: bool = True
    
    # Retention
    forecast_retention_days: int = 30
    plan_retention_days: int = 90


class UsageForecastingManager:
    """Advanced usage forecasting and capacity planning manager."""
    
    def __init__(self, config: ForecastingConfig = None):
        self.config = config or ForecastingConfig()
        
        # Data storage
        self.historical_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.forecasts: Dict[str, ForecastResult] = {}
        self.capacity_plans: Dict[str, CapacityPlan] = {}
        
        # ML models
        self.models: Dict[ForecastModel, Any] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        
        # Forecasting state
        self.model_performance: Dict[str, List[float]] = defaultdict(list)
        self.forecast_cache: Dict[str, Any] = {}
        
        # Statistics
        self.total_forecasts_generated = 0
        self.total_plans_generated = 0
        self.total_models_trained = 0
        
        # Background tasks
        self._running = False
        self._forecasting_task = None
        self._capacity_planning_task = None
        self._cleanup_task = None
        
        # Initialize models
        self._initialize_models()
        
        logger.info("Usage Forecasting Manager initialized")
    
    def _initialize_models(self) -> None:
        """Initialize forecasting models."""
        try:
            # Initialize primary models
            self.models[ForecastModel.LINEAR_REGRESSION] = LinearRegression()
            self.models[ForecastModel.RANDOM_FOREST] = RandomForestRegressor(
                n_estimators=100,
                random_state=42,
                n_jobs=-1
            )
            
            logger.info("Forecasting models initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize models: {e}")
    
    async def start(self) -> None:
        """Start the forecasting manager."""
        if self._running:
            logger.warning("Usage Forecasting Manager is already running")
            return
        
        self._running = True
        
        # Start background tasks
        self._forecasting_task = asyncio.create_task(self._forecasting_loop())
        self._capacity_planning_task = asyncio.create_task(self._capacity_planning_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("Usage Forecasting Manager started")
    
    async def stop(self) -> None:
        """Stop the forecasting manager."""
        if not self._running:
            return
        
        self._running = False
        
        # Cancel background tasks
        if self._forecasting_task:
            self._forecasting_task.cancel()
            try:
                await self._forecasting_task
            except asyncio.CancelledError:
                pass
        
        if self._capacity_planning_task:
            self._capacity_planning_task.cancel()
            try:
                await self._capacity_planning_task
            except asyncio.CancelledError:
                pass
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Usage Forecasting Manager stopped")
    
    async def add_metric_data(
        self,
        metric_name: str,
        value: float,
        unit: str,
        timestamp: Optional[datetime] = None,
        resource_id: Optional[str] = None,
        tags: Dict[str, str] = None
    ) -> None:
        """Add metric data for forecasting."""
        if timestamp is None:
            timestamp = datetime.now()
        
        metric = ResourceMetric(
            timestamp=timestamp,
            metric_name=metric_name,
            value=value,
            unit=unit,
            resource_id=resource_id,
            tags=tags or {}
        )
        
        self.historical_data[metric_name].append(metric)
    
    async def generate_forecast(
        self,
        metric_name: str,
        horizon_hours: int = None,
        model: ForecastModel = None
    ) -> ForecastResult:
        """Generate usage forecast for a metric."""
        try:
            if horizon_hours is None:
                horizon_hours = self.config.default_horizon_hours
            if model is None:
                model = self.config.primary_model
            
            # Check data availability
            data = list(self.historical_data[metric_name])
            if len(data) < self.config.min_training_days * 24:  # Need at least min days of hourly data
                raise ValueError(f"Insufficient data for forecasting: {len(data)} points")
            
            # Prepare training data
            X, y, timestamps = await self._prepare_forecasting_data(data)
            
            # Train model
            trained_model, scaler = await self._train_forecasting_model(X, y, model)
            
            # Generate predictions
            predictions, confidence_intervals = await self._generate_predictions(
                trained_model, scaler, X, y, horizon_hours
            )
            
            # Calculate performance metrics
            accuracy_score, mae, mse = await self._evaluate_model(trained_model, scaler, X, y)
            
            # Create forecast result
            forecast_id = f"forecast_{metric_name}_{int(time.time())}"
            forecast_timestamps = [
                datetime.now() + timedelta(hours=i) for i in range(horizon_hours)
            ]
            
            forecast = ForecastResult(
                forecast_id=forecast_id,
                model_used=model,
                horizon=ForecastHorizon.HOURLY,
                predicted_values=predictions,
                confidence_intervals=confidence_intervals,
                timestamps=forecast_timestamps,
                accuracy_score=accuracy_score,
                mean_absolute_error=mae,
                mean_squared_error=mse,
                training_data_points=len(X),
                forecast_period_hours=horizon_hours
            )
            
            # Store forecast
            self.forecasts[forecast_id] = forecast
            self.total_forecasts_generated += 1
            
            logger.info(f"Forecast generated for {metric_name}: {accuracy_score:.3f} accuracy")
            return forecast
            
        except Exception as e:
            logger.error(f"Forecast generation failed: {e}")
            raise
    
    async def _prepare_forecasting_data(
        self,
        data: List[ResourceMetric]
    ) -> Tuple[np.ndarray, np.ndarray, List[datetime]]:
        """Prepare data for forecasting."""
        # Convert to DataFrame
        df = pd.DataFrame([{
            'timestamp': m.timestamp,
            'value': m.value
        } for m in data])
        
        # Sort by timestamp
        df = df.sort_values('timestamp')
        
        # Create features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['day_of_month'] = df['timestamp'].dt.day
        df['month'] = df['timestamp'].dt.month
        df['lag_1'] = df['value'].shift(1)
        df['lag_24'] = df['value'].shift(24)  # Previous day same hour
        df['rolling_mean_24'] = df['value'].rolling(window=24).mean()
        df['rolling_std_24'] = df['value'].rolling(window=24).std()
        
        # Drop NaN values
        df = df.dropna()
        
        # Prepare features and target
        feature_columns = ['hour', 'day_of_week', 'day_of_month', 'month', 
                          'lag_1', 'lag_24', 'rolling_mean_24', 'rolling_std_24']
        X = df[feature_columns].values
        y = df['value'].values
        timestamps = df['timestamp'].tolist()
        
        return X, y, timestamps
    
    async def _train_forecasting_model(
        self,
        X: np.ndarray,
        y: np.ndarray,
        model_type: ForecastModel
    ) -> Tuple[Any, StandardScaler]:
        """Train forecasting model."""
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Get model
        model = self.models[model_type]
        
        # Train model
        model.fit(X_scaled, y)
        
        # Store scaler
        self.scalers[model_type.value] = scaler
        
        self.total_models_trained += 1
        return model, scaler
    
    async def _generate_predictions(
        self,
        model: Any,
        scaler: StandardScaler,
        X: np.ndarray,
        y: np.ndarray,
        horizon_hours: int
    ) -> Tuple[List[float], List[Tuple[float, float]]]:
        """Generate predictions with confidence intervals."""
        predictions = []
        confidence_intervals = []
        
        # Start with last known data
        last_features = X[-1:].copy()
        
        for hour in range(horizon_hours):
            # Predict next value
            prediction = model.predict(last_features)[0]
            predictions.append(float(prediction))
            
            # Calculate confidence interval (simplified)
            std_error = np.std(y) / np.sqrt(len(y))
            margin = 1.96 * std_error  # 95% confidence
            confidence_intervals.append((
                max(0, prediction - margin),
                prediction + margin
            ))
            
            # Update features for next prediction
            # This is simplified - in practice, you'd update lag features properly
            last_features[0, 0] = (datetime.now() + timedelta(hours=hour + 1)).hour
            last_features[0, 4] = prediction  # Update lag_1
        
        return predictions, confidence_intervals
    
    async def _evaluate_model(
        self,
        model: Any,
        scaler: StandardScaler,
        X: np.ndarray,
        y: np.ndarray
    ) -> Tuple[float, float, float]:
        """Evaluate model performance."""
        # Split data for evaluation
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Scale features
        X_train_scaled = scaler.transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Make predictions
        y_pred = model.predict(X_test_scaled)
        
        # Calculate metrics
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        
        # Calculate accuracy score (1 - normalized MAE)
        accuracy = 1 - (mae / np.mean(y_test))
        accuracy = max(0, min(1, accuracy))
        
        return accuracy, mae, mse
    
    async def generate_capacity_plan(
        self,
        resource_type: str,
        current_capacity: float,
        current_cost: float,
        forecast_hours: int = 24
    ) -> CapacityPlan:
        """Generate capacity planning recommendation."""
        try:
            # Get forecast for this resource type
            forecast = await self.generate_forecast(
                f"{resource_type}_usage",
                forecast_hours
            )
            
            # Calculate forecasted demand
            forecasted_demand = max(forecast.predicted_values)
            
            # Calculate recommended capacity with buffer
            recommended_capacity = forecasted_demand * (1 + self.config.capacity_buffer_ratio)
            
            # Calculate utilization ratios
            utilization_ratio = forecasted_demand / current_capacity
            buffer_ratio = (recommended_capacity - forecasted_demand) / forecasted_demand
            
            # Determine risk level
            if utilization_ratio > 0.9:
                risk_level = "critical"
            elif utilization_ratio > 0.8:
                risk_level = "high"
            elif utilization_ratio > 0.6:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            # Determine scaling action
            if utilization_ratio > self.config.utilization_threshold_high:
                scaling_action = ScalingAction.SCALE_UP
                scaling_factor = recommended_capacity / current_capacity
                scaling_timeline = "hours"
            elif utilization_ratio < self.config.utilization_threshold_low:
                scaling_action = ScalingAction.SCALE_DOWN
                scaling_factor = recommended_capacity / current_capacity
                scaling_timeline = "days"
            else:
                scaling_action = ScalingAction.MAINTAIN
                scaling_factor = 1.0
                scaling_timeline = "maintain"
            
            # Calculate cost projections
            projected_cost = current_cost * scaling_factor
            cost_savings = max(0, current_cost - projected_cost)
            roi_estimate = (cost_savings / projected_cost * 100) if projected_cost > 0 else 0
            
            # Create capacity plan
            plan_id = f"capacity_{resource_type}_{int(time.time())}"
            plan = CapacityPlan(
                plan_id=plan_id,
                resource_type=resource_type,
                current_capacity=current_capacity,
                forecasted_demand=forecasted_demand,
                recommended_capacity=recommended_capacity,
                utilization_ratio=utilization_ratio,
                buffer_ratio=buffer_ratio,
                risk_level=risk_level,
                scaling_action=scaling_action,
                scaling_factor=scaling_factor,
                scaling_timeline=scaling_timeline,
                current_cost=current_cost,
                projected_cost=projected_cost,
                cost_savings=cost_savings,
                roi_estimate=roi_estimate,
                confidence=forecast.accuracy_score
            )
            
            # Store plan
            self.capacity_plans[plan_id] = plan
            self.total_plans_generated += 1
            
            logger.info(f"Capacity plan generated for {resource_type}: {scaling_action.value}")
            return plan
            
        except Exception as e:
            logger.error(f"Capacity planning failed: {e}")
            raise
    
    async def _forecasting_loop(self) -> None:
        """Background forecasting loop."""
        while self._running:
            try:
                await asyncio.sleep(self.config.forecast_interval_minutes * 60)
                
                # Generate forecasts for key metrics
                key_metrics = ["requests_per_minute", "cpu_usage", "memory_usage", "bandwidth_usage"]
                
                for metric in key_metrics:
                    if len(self.historical_data[metric]) >= self.config.min_training_days * 24:
                        try:
                            await self.generate_forecast(metric)
                        except Exception as e:
                            logger.error(f"Failed to generate forecast for {metric}: {e}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Forecasting loop error: {e}")
    
    async def _capacity_planning_loop(self) -> None:
        """Background capacity planning loop."""
        while self._running:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                # Generate capacity plans for key resources
                resources = [
                    ("compute", 1000, 100.0),  # capacity, cost
                    ("storage", 10000, 50.0),
                    ("bandwidth", 1000, 200.0)
                ]
                
                for resource_type, capacity, cost in resources:
                    try:
                        await self.generate_capacity_plan(resource_type, capacity, cost)
                    except Exception as e:
                        logger.error(f"Failed to generate capacity plan for {resource_type}: {e}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Capacity planning loop error: {e}")
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while self._running:
            try:
                await asyncio.sleep(3600)  # Cleanup every hour
                
                current_time = datetime.now()
                
                # Clean old forecasts
                forecast_cutoff = current_time - timedelta(days=self.config.forecast_retention_days)
                forecast_ids_to_remove = [
                    fid for fid, forecast in self.forecasts.items()
                    if forecast.created_at < forecast_cutoff
                ]
                
                for fid in forecast_ids_to_remove:
                    del self.forecasts[fid]
                
                # Clean old capacity plans
                plan_cutoff = current_time - timedelta(days=self.config.plan_retention_days)
                plan_ids_to_remove = [
                    pid for pid, plan in self.capacity_plans.items()
                    if plan.created_at < plan_cutoff
                ]
                
                for pid in plan_ids_to_remove:
                    del self.capacity_plans[pid]
                
                # Clean old historical data
                data_cutoff = current_time - timedelta(days=self.config.max_training_days)
                for metric_name in list(self.historical_data.keys()):
                    self.historical_data[metric_name] = deque(
                        [m for m in self.historical_data[metric_name] if m.timestamp > data_cutoff],
                        maxlen=10000
                    )
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
    
    def get_forecasting_stats(self) -> Dict[str, Any]:
        """Get comprehensive forecasting statistics."""
        current_time = datetime.now()
        
        # Forecast statistics
        forecast_stats = {
            "total_forecasts": self.total_forecasts_generated,
            "active_forecasts": len(self.forecasts),
            "models_trained": self.total_models_trained,
            "forecast_accuracy": {}
        }
        
        # Calculate average accuracy by model
        model_accuracies = defaultdict(list)
        for forecast in self.forecasts.values():
            model_accuracies[forecast.model_used.value].append(forecast.accuracy_score)
        
        for model, accuracies in model_accuracies.items():
            if accuracies:
                forecast_stats["forecast_accuracy"][model] = {
                    "average": np.mean(accuracies),
                    "best": max(accuracies),
                    "worst": min(accuracies),
                    "count": len(accuracies)
                }
        
        # Capacity planning statistics
        capacity_stats = {
            "total_plans": self.total_plans_generated,
            "active_plans": len(self.capacity_plans),
            "scaling_recommendations": defaultdict(int),
            "risk_distribution": defaultdict(int)
        }
        
        for plan in self.capacity_plans.values():
            capacity_stats["scaling_recommendations"][plan.scaling_action.value] += 1
            capacity_stats["risk_distribution"][plan.risk_level] += 1
        
        # Data statistics
        data_stats = {
            "metrics_tracked": len(self.historical_data),
            "total_data_points": sum(len(data) for data in self.historical_data.values()),
            "data_quality": {}
        }
        
        for metric_name, data in self.historical_data.items():
            if data:
                data_points = len(data)
                expected_points = self.config.max_training_days * 24
                quality_ratio = min(data_points / expected_points, 1.0)
                data_stats["data_quality"][metric_name] = quality_ratio
        
        return {
            "forecast_statistics": forecast_stats,
            "capacity_statistics": capacity_stats,
            "data_statistics": data_stats,
            "config": {
                "primary_model": self.config.primary_model.value,
                "default_horizon_hours": self.config.default_horizon_hours,
                "capacity_buffer_ratio": self.config.capacity_buffer_ratio,
                "forecast_interval_minutes": self.config.forecast_interval_minutes
            },
            "running": self._running,
            "timestamp": current_time.isoformat()
        }
    
    def get_latest_forecast(self, metric_name: str) -> Optional[ForecastResult]:
        """Get latest forecast for a metric."""
        metric_forecasts = [
            forecast for forecast in self.forecasts.values()
            if forecast.model_used.value in metric_name or metric_name in forecast.model_used.value
        ]
        
        if metric_forecasts:
            return max(metric_forecasts, key=lambda x: x.created_at)
        return None
    
    def get_active_capacity_plans(self, resource_type: Optional[str] = None) -> List[CapacityPlan]:
        """Get active capacity plans."""
        plans = list(self.capacity_plans.values())
        
        if resource_type:
            plans = [p for p in plans if p.resource_type == resource_type]
        
        # Filter out expired plans
        current_time = datetime.now()
        valid_plans = [p for p in plans if p.valid_until > current_time]
        
        return sorted(valid_plans, key=lambda x: x.created_at, reverse=True)


# Global usage forecasting manager instance
_usage_forecasting_manager: Optional[UsageForecastingManager] = None


def get_usage_forecasting_manager(config: ForecastingConfig = None) -> UsageForecastingManager:
    """Get or create global usage forecasting manager instance."""
    global _usage_forecasting_manager
    if _usage_forecasting_manager is None:
        _usage_forecasting_manager = UsageForecastingManager(config)
    return _usage_forecasting_manager


async def start_usage_forecasting(config: ForecastingConfig = None):
    """Start the global usage forecasting manager."""
    forecaster = get_usage_forecasting_manager(config)
    await forecaster.start()


async def stop_usage_forecasting():
    """Stop the global usage forecasting manager."""
    global _usage_forecasting_manager
    if _usage_forecasting_manager:
        await _usage_forecasting_manager.stop()


async def add_forecasting_metric(
    metric_name: str,
    value: float,
    unit: str,
    timestamp: Optional[datetime] = None,
    resource_id: Optional[str] = None,
    tags: Dict[str, str] = None
):
    """Add metric data for forecasting."""
    forecaster = get_usage_forecasting_manager()
    await forecaster.add_metric_data(metric_name, value, unit, timestamp, resource_id, tags)


async def generate_usage_forecast(
    metric_name: str,
    horizon_hours: int = 24,
    model: ForecastModel = None
) -> ForecastResult:
    """Generate usage forecast."""
    forecaster = get_usage_forecasting_manager()
    return await forecaster.generate_forecast(metric_name, horizon_hours, model)


async def generate_capacity_plan(
    resource_type: str,
    current_capacity: float,
    current_cost: float,
    forecast_hours: int = 24
) -> CapacityPlan:
    """Generate capacity plan."""
    forecaster = get_usage_forecasting_manager()
    return await forecaster.generate_capacity_plan(resource_type, current_capacity, current_cost, forecast_hours)


def get_forecasting_stats() -> Dict[str, Any]:
    """Get forecasting statistics."""
    forecaster = get_usage_forecasting_manager()
    return forecaster.get_forecasting_stats()
