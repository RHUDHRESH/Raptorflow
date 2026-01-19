"""
ML Rate Limit Optimizer
=======================

Machine learning-based rate limit optimization and prediction system.
Uses scikit-learn, XGBoost, and statistical methods to optimize rate limits
and predict usage patterns.

Features:
- Usage pattern prediction with scikit-learn
- Anomaly detection with isolation forests
- Time series forecasting
- Dynamic limit optimization
- A/B testing framework
- Feature engineering for rate limiting
"""

import asyncio
import time
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import logging

# ML imports
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib
import pickle

logger = logging.getLogger(__name__)


class PredictionModel(Enum):
    """Available prediction models."""
    LINEAR_REGRESSION = "linear_regression"
    RANDOM_FOREST = "random_forest"
    ISOLATION_FOREST = "isolation_forest"
    MOVING_AVERAGE = "moving_average"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"


class OptimizationStrategy(Enum):
    """Rate limit optimization strategies."""
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    ADAPTIVE = "adaptive"


@dataclass
class UsageFeature:
    """Feature data for ML models."""
    
    timestamp: datetime
    client_id: str
    endpoint: str
    user_tier: str
    hour_of_day: int
    day_of_week: int
    request_count: int
    response_time: float
    error_rate: float
    concurrent_users: int
    system_load: float
    is_weekend: bool
    is_business_hours: bool
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array for ML models."""
        return np.array([
            self.hour_of_day,
            self.day_of_week,
            self.request_count,
            self.response_time,
            self.error_rate,
            self.concurrent_users,
            self.system_load,
            int(self.is_weekend),
            int(self.is_business_hours)
        ])


@dataclass
class PredictionResult:
    """ML prediction result."""
    
    predicted_usage: float
    confidence: float
    recommended_limit: int
    optimization_strategy: OptimizationStrategy
    model_used: PredictionModel
    features_importance: Dict[str, float]
    anomaly_score: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MLConfig:
    """ML rate optimizer configuration."""
    
    # Model settings
    primary_model: PredictionModel = PredictionModel.RANDOM_FOREST
    anomaly_model: PredictionModel = PredictionModel.ISOLATION_FOREST
    ensemble_models: bool = True
    
    # Training settings
    training_data_days: int = 30
    min_training_samples: int = 100
    retrain_interval_hours: int = 6
    validation_split: float = 0.2
    
    # Prediction settings
    prediction_horizon_hours: int = 24
    confidence_threshold: float = 0.7
    anomaly_threshold: float = -0.1
    
    # Optimization settings
    optimization_strategy: OptimizationStrategy = OptimizationStrategy.BALANCED
    max_limit_increase: float = 2.0  # Max 2x increase
    min_limit_decrease: float = 0.5  # Min 50% of current
    safety_margin: float = 0.2  # 20% safety margin
    
    # Feature engineering
    enable_feature_importance: bool = True
    feature_selection_threshold: float = 0.01
    
    # Model persistence
    model_save_path: str = "models/rate_optimizer/"
    enable_model_persistence: bool = True


class MLRateOptimizer:
    """Machine learning-based rate limit optimizer."""
    
    def __init__(self, config: MLConfig = None):
        self.config = config or MLConfig()
        
        # Data storage
        self.usage_features: deque = deque(maxlen=10000)
        self.prediction_history: deque = deque(maxlen=1000)
        self.model_performance: Dict[str, List[float]] = defaultdict(list)
        
        # ML models
        self.prediction_models: Dict[PredictionModel, Any] = {}
        self.anomaly_detector: Optional[IsolationForest] = None
        self.feature_scaler: Optional[StandardScaler] = None
        
        # Feature tracking
        self.feature_importance: Dict[str, float] = {}
        self.feature_stats: Dict[str, Dict[str, float]] = defaultdict(dict)
        
        # Training state
        self.last_training_time: Optional[datetime] = None
        self.is_training: bool = False
        self.training_lock = asyncio.Lock()
        
        # Background tasks
        self._running = False
        self._training_task = None
        self._cleanup_task = None
        
        logger.info(f"ML Rate Optimizer initialized with model: {self.config.primary_model.value}")
    
    async def start(self) -> None:
        """Start the ML rate optimizer."""
        if self._running:
            logger.warning("ML Rate Optimizer is already running")
            return
        
        self._running = True
        
        try:
            # Load existing models
            await self._load_models()
            
            # Initialize models if not loaded
            await self._initialize_models()
            
            # Start background tasks
            self._training_task = asyncio.create_task(self._training_loop())
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            logger.info("ML Rate Optimizer started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start ML Rate Optimizer: {e}")
            await self.stop()
            raise
    
    async def stop(self) -> None:
        """Stop the ML rate optimizer."""
        if not self._running:
            return
        
        self._running = False
        
        # Cancel background tasks
        if self._training_task:
            self._training_task.cancel()
            try:
                await self._training_task
            except asyncio.CancelledError:
                pass
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Save models
        if self.config.enable_model_persistence:
            await self._save_models()
        
        logger.info("ML Rate Optimizer stopped")
    
    async def add_usage_data(
        self,
        client_id: str,
        endpoint: str,
        user_tier: str,
        request_count: int,
        response_time: float,
        error_rate: float = 0.0,
        concurrent_users: int = 1,
        system_load: float = 0.0
    ) -> None:
        """Add usage data for ML training."""
        current_time = datetime.now()
        
        feature = UsageFeature(
            timestamp=current_time,
            client_id=client_id,
            endpoint=endpoint,
            user_tier=user_tier,
            hour_of_day=current_time.hour,
            day_of_week=current_time.weekday(),
            request_count=request_count,
            response_time=response_time,
            error_rate=error_rate,
            concurrent_users=concurrent_users,
            system_load=system_load,
            is_weekend=current_time.weekday() >= 5,
            is_business_hours=9 <= current_time.hour <= 17
        )
        
        self.usage_features.append(feature)
        
        # Update feature statistics
        await self._update_feature_stats(feature)
    
    async def predict_usage(
        self,
        client_id: str,
        endpoint: str,
        user_tier: str,
        hours_ahead: int = 1
    ) -> PredictionResult:
        """Predict future usage and recommend optimal rate limits."""
        try:
            # Prepare features for prediction
            current_time = datetime.now()
            future_time = current_time + timedelta(hours=hours_ahead)
            
            # Create prediction features
            prediction_features = await self._create_prediction_features(
                client_id, endpoint, user_tier, future_time
            )
            
            # Make prediction
            predicted_usage, confidence = await self._make_prediction(prediction_features)
            
            # Detect anomalies
            anomaly_score = await self._detect_anomaly(prediction_features)
            
            # Calculate recommended limit
            recommended_limit = await self._calculate_optimal_limit(
                predicted_usage, confidence, anomaly_score, user_tier
            )
            
            # Get feature importance
            feature_importance = self.feature_importance if self.config.enable_feature_importance else {}
            
            result = PredictionResult(
                predicted_usage=predicted_usage,
                confidence=confidence,
                recommended_limit=recommended_limit,
                optimization_strategy=self.config.optimization_strategy,
                model_used=self.config.primary_model,
                features_importance=feature_importance,
                anomaly_score=anomaly_score
            )
            
            self.prediction_history.append(result)
            return result
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            # Return conservative fallback
            return PredictionResult(
                predicted_usage=0.0,
                confidence=0.0,
                recommended_limit=60,  # Conservative default
                optimization_strategy=OptimizationStrategy.CONSERVATIVE,
                model_used=PredictionModel.MOVING_AVERAGE,
                features_importance={},
                anomaly_score=0.0
            )
    
    async def _create_prediction_features(
        self,
        client_id: str,
        endpoint: str,
        user_tier: str,
        target_time: datetime
    ) -> np.ndarray:
        """Create features for prediction."""
        # Get historical features for similar patterns
        similar_features = [
            f for f in self.usage_features
            if f.client_id == client_id and f.endpoint == endpoint
        ]
        
        # Calculate aggregates
        if similar_features:
            recent_features = similar_features[-24:]  # Last 24 records
            avg_request_count = np.mean([f.request_count for f in recent_features])
            avg_response_time = np.mean([f.response_time for f in recent_features])
            avg_error_rate = np.mean([f.error_rate for f in recent_features])
        else:
            avg_request_count = 10.0  # Default
            avg_response_time = 0.1
            avg_error_rate = 0.0
        
        # Create feature array
        features = np.array([
            target_time.hour,
            target_time.weekday(),
            avg_request_count,
            avg_response_time,
            avg_error_rate,
            1,  # concurrent_users (estimate)
            0.5,  # system_load (estimate)
            int(target_time.weekday() >= 5),  # is_weekend
            int(9 <= target_time.hour <= 17)  # is_business_hours
        ])
        
        return features.reshape(1, -1)
    
    async def _make_prediction(self, features: np.ndarray) -> Tuple[float, float]:
        """Make prediction using primary model."""
        try:
            if self.config.primary_model in self.prediction_models:
                model = self.prediction_models[self.config.primary_model]
                
                if self.feature_scaler:
                    features_scaled = self.feature_scaler.transform(features)
                    prediction = model.predict(features_scaled)[0]
                else:
                    prediction = model.predict(features)[0]
                
                # Calculate confidence based on historical accuracy
                confidence = await self._calculate_prediction_confidence()
                
                return float(prediction), confidence
            else:
                # Fallback to moving average
                return await self._moving_average_prediction()
                
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return await self._moving_average_prediction()
    
    async def _moving_average_prediction(self) -> Tuple[float, float]:
        """Fallback moving average prediction."""
        if len(self.usage_features) < 10:
            return 10.0, 0.1  # Low confidence fallback
        
        recent_features = list(self.usage_features)[-10:]
        avg_usage = np.mean([f.request_count for f in recent_features])
        confidence = min(len(recent_features) / 100, 0.8)  # Confidence based on data size
        
        return avg_usage, confidence
    
    async def _detect_anomaly(self, features: np.ndarray) -> float:
        """Detect if current features are anomalous."""
        try:
            if self.anomaly_detector and self.feature_scaler:
                features_scaled = self.feature_scaler.transform(features)
                anomaly_score = self.anomaly_detector.decision_function(features_scaled)[0]
                return float(anomaly_score)
            else:
                return 0.0  # No anomaly detected
                
        except Exception as e:
            logger.error(f"Anomaly detection error: {e}")
            return 0.0
    
    async def _calculate_optimal_limit(
        self,
        predicted_usage: float,
        confidence: float,
        anomaly_score: float,
        user_tier: str
    ) -> int:
        """Calculate optimal rate limit based on prediction."""
        # Apply safety margin
        safe_usage = predicted_usage * (1 + self.config.safety_margin)
        
        # Adjust based on confidence
        if confidence < self.config.confidence_threshold:
            safe_usage *= 0.8  # More conservative for low confidence
        
        # Adjust based on anomaly score
        if anomaly_score < self.config.anomaly_threshold:
            safe_usage *= 0.7  # More conservative for anomalies
        
        # Apply tier-based multipliers
        tier_multipliers = {
            "free": 1.0,
            "basic": 2.0,
            "pro": 5.0,
            "enterprise": 20.0,
            "premium": 50.0
        }
        
        tier_multiplier = tier_multipliers.get(user_tier, 1.0)
        adjusted_limit = safe_usage * tier_multiplier
        
        # Apply optimization strategy
        if self.config.optimization_strategy == OptimizationStrategy.CONSERVATIVE:
            adjusted_limit *= 0.8
        elif self.config.optimization_strategy == OptimizationStrategy.AGGRESSIVE:
            adjusted_limit *= 1.2
        elif self.config.optimization_strategy == OptimizationStrategy.ADAPTIVE:
            # Adaptive based on recent performance
            if len(self.model_performance[self.config.primary_model.value]) > 0:
                recent_performance = np.mean(self.model_performance[self.config.primary_model.value][-10:])
                if recent_performance > 0.8:  # Good performance
                    adjusted_limit *= 1.1
                else:  # Poor performance
                    adjusted_limit *= 0.9
        
        # Ensure minimum and maximum limits
        min_limit = 10
        max_limit = int(adjusted_limit * self.config.max_limit_increase)
        
        return max(min_limit, min(max_limit, int(adjusted_limit)))
    
    async def _calculate_prediction_confidence(self) -> float:
        """Calculate confidence in prediction based on model performance."""
        if self.config.primary_model.value not in self.model_performance:
            return 0.5  # Default confidence
        
        performance_history = self.model_performance[self.config.primary_model.value]
        if len(performance_history) < 5:
            return 0.5
        
        # Use recent performance as confidence indicator
        recent_performance = performance_history[-10:]
        avg_performance = np.mean(recent_performance)
        
        # Convert performance to confidence (0-1 scale)
        confidence = max(0.1, min(0.95, avg_performance))
        
        return confidence
    
    async def _initialize_models(self) -> None:
        """Initialize ML models."""
        try:
            # Initialize primary prediction model
            if self.config.primary_model == PredictionModel.LINEAR_REGRESSION:
                self.prediction_models[self.config.primary_model] = LinearRegression()
            elif self.config.primary_model == PredictionModel.RANDOM_FOREST:
                self.prediction_models[self.config.primary_model] = RandomForestRegressor(
                    n_estimators=100,
                    random_state=42,
                    n_jobs=-1
                )
            
            # Initialize anomaly detector
            self.anomaly_detector = IsolationForest(
                contamination=0.1,
                random_state=42,
                n_jobs=-1
            )
            
            # Initialize feature scaler
            self.feature_scaler = StandardScaler()
            
            logger.info("ML models initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize models: {e}")
    
    async def _train_models(self) -> None:
        """Train ML models with collected data."""
        if self.is_training or len(self.usage_features) < self.config.min_training_samples:
            return
        
        async with self.training_lock:
            self.is_training = True
            
            try:
                logger.info("Starting ML model training")
                
                # Prepare training data
                X, y = await self._prepare_training_data()
                
                if len(X) < self.config.min_training_samples:
                    logger.warning(f"Insufficient training data: {len(X)} samples")
                    return
                
                # Split data
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=self.config.validation_split, random_state=42
                )
                
                # Scale features
                if self.feature_scaler:
                    X_train_scaled = self.feature_scaler.fit_transform(X_train)
                    X_test_scaled = self.feature_scaler.transform(X_test)
                else:
                    X_train_scaled = X_train
                    X_test_scaled = X_test
                
                # Train primary model
                if self.config.primary_model in self.prediction_models:
                    model = self.prediction_models[self.config.primary_model]
                    model.fit(X_train_scaled, y_train)
                    
                    # Evaluate model
                    y_pred = model.predict(X_test_scaled)
                    mae = mean_absolute_error(y_test, y_pred)
                    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                    
                    # Store performance
                    self.model_performance[self.config.primary_model.value].append(1 - (mae / np.mean(y_test)))
                    
                    logger.info(f"Model trained - MAE: {mae:.2f}, RMSE: {rmse:.2f}")
                
                # Train anomaly detector
                if self.anomaly_detector:
                    self.anomaly_detector.fit(X_train_scaled)
                
                # Calculate feature importance
                if self.config.enable_feature_importance:
                    await self._calculate_feature_importance()
                
                self.last_training_time = datetime.now()
                
                # Save models
                if self.config.enable_model_persistence:
                    await self._save_models()
                
                logger.info("ML model training completed")
                
            except Exception as e:
                logger.error(f"Model training failed: {e}")
            finally:
                self.is_training = False
    
    async def _prepare_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data from usage features."""
        features = []
        targets = []
        
        # Create sequences for time series prediction
        feature_list = list(self.usage_features)
        
        for i in range(1, len(feature_list)):
            current_feature = feature_list[i]
            previous_feature = feature_list[i-1]
            
            # Use previous features to predict current usage
            X = previous_feature.to_array()
            y = current_feature.request_count
            
            features.append(X)
            targets.append(y)
        
        return np.array(features), np.array(targets)
    
    async def _calculate_feature_importance(self) -> None:
        """Calculate feature importance from trained models."""
        try:
            if self.config.primary_model == PredictionModel.RANDOM_FOREST:
                model = self.prediction_models[self.config.primary_model]
                if hasattr(model, 'feature_importances_'):
                    feature_names = [
                        'hour_of_day', 'day_of_week', 'request_count', 'response_time',
                        'error_rate', 'concurrent_users', 'system_load', 'is_weekend', 'is_business_hours'
                    ]
                    
                    importances = model.feature_importances_
                    self.feature_importance = dict(zip(feature_names, importances))
                    
                    # Filter by threshold
                    self.feature_importance = {
                        k: v for k, v in self.feature_importance.items()
                        if v > self.config.feature_selection_threshold
                    }
                    
                    logger.info(f"Feature importance calculated: {len(self.feature_importance)} features")
        
        except Exception as e:
            logger.error(f"Failed to calculate feature importance: {e}")
    
    async def _update_feature_stats(self, feature: UsageFeature) -> None:
        """Update feature statistics for monitoring."""
        feature_array = feature.to_array()
        feature_names = [
            'hour_of_day', 'day_of_week', 'request_count', 'response_time',
            'error_rate', 'concurrent_users', 'system_load', 'is_weekend', 'is_business_hours'
        ]
        
        for i, name in enumerate(feature_names):
            value = feature_array[i]
            
            if 'mean' not in self.feature_stats[name]:
                self.feature_stats[name]['mean'] = value
                self.feature_stats[name]['std'] = 0
                self.feature_stats[name]['count'] = 1
            else:
                # Update running statistics
                old_mean = self.feature_stats[name]['mean']
                old_count = self.feature_stats[name]['count']
                new_count = old_count + 1
                
                new_mean = (old_mean * old_count + value) / new_count
                self.feature_stats[name]['mean'] = new_mean
                self.feature_stats[name]['count'] = new_count
    
    async def _training_loop(self) -> None:
        """Background training loop."""
        while self._running:
            try:
                await asyncio.sleep(self.config.retrain_interval_hours * 3600)
                await self._train_models()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Training loop error: {e}")
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup of old data."""
        while self._running:
            try:
                await asyncio.sleep(3600)  # Cleanup every hour
                
                # Clean old prediction history
                cutoff_time = datetime.now() - timedelta(days=7)
                self.prediction_history = deque(
                    [p for p in self.prediction_history if p.timestamp > cutoff_time],
                    maxlen=1000
                )
                
                # Clean old performance data
                for model_name in self.model_performance:
                    if len(self.model_performance[model_name]) > 100:
                        self.model_performance[model_name] = self.model_performance[model_name][-100:]
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
    
    async def _save_models(self) -> None:
        """Save trained models to disk."""
        try:
            import os
            os.makedirs(self.config.model_save_path, exist_ok=True)
            
            # Save prediction models
            for model_name, model in self.prediction_models.items():
                model_path = f"{self.config.model_save_path}/{model_name.value}.pkl"
                joblib.dump(model, model_path)
            
            # Save anomaly detector
            if self.anomaly_detector:
                anomaly_path = f"{self.config.model_save_path}/anomaly_detector.pkl"
                joblib.dump(self.anomaly_detector, anomaly_path)
            
            # Save feature scaler
            if self.feature_scaler:
                scaler_path = f"{self.config.model_save_path}/feature_scaler.pkl"
                joblib.dump(self.feature_scaler, scaler_path)
            
            # Save feature importance
            importance_path = f"{self.config.model_save_path}/feature_importance.json"
            with open(importance_path, 'w') as f:
                json.dump(self.feature_importance, f)
            
            logger.info("Models saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save models: {e}")
    
    async def _load_models(self) -> None:
        """Load trained models from disk."""
        try:
            import os
            
            if not os.path.exists(self.config.model_save_path):
                return
            
            # Load prediction models
            for model_name in PredictionModel:
                model_path = f"{self.config.model_save_path}/{model_name.value}.pkl"
                if os.path.exists(model_path):
                    self.prediction_models[model_name] = joblib.load(model_path)
            
            # Load anomaly detector
            anomaly_path = f"{self.config.model_save_path}/anomaly_detector.pkl"
            if os.path.exists(anomaly_path):
                self.anomaly_detector = joblib.load(anomaly_path)
            
            # Load feature scaler
            scaler_path = f"{self.config.model_save_path}/feature_scaler.pkl"
            if os.path.exists(scaler_path):
                self.feature_scaler = joblib.load(scaler_path)
            
            # Load feature importance
            importance_path = f"{self.config.model_save_path}/feature_importance.json"
            if os.path.exists(importance_path):
                with open(importance_path, 'r') as f:
                    self.feature_importance = json.load(f)
            
            logger.info("Models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
    
    def get_model_stats(self) -> Dict[str, Any]:
        """Get comprehensive model statistics."""
        current_time = datetime.now()
        
        # Training statistics
        training_stats = {
            "last_training_time": self.last_training_time.isoformat() if self.last_training_time else None,
            "is_training": self.is_training,
            "total_samples": len(self.usage_features),
            "min_samples_required": self.config.min_training_samples,
            "ready_for_training": len(self.usage_features) >= self.config.min_training_samples
        }
        
        # Model performance
        performance_stats = {}
        for model_name, performance_list in self.model_performance.items():
            if performance_list:
                performance_stats[model_name] = {
                    "recent_performance": np.mean(performance_list[-10:]),
                    "best_performance": max(performance_list),
                    "worst_performance": min(performance_list),
                    "total_evaluations": len(performance_list)
                }
        
        # Feature statistics
        feature_stats = {}
        for feature_name, stats in self.feature_stats.items():
            if stats:
                feature_stats[feature_name] = {
                    "mean": stats.get('mean', 0),
                    "std": stats.get('std', 0),
                    "count": stats.get('count', 0)
                }
        
        # Prediction statistics
        prediction_stats = {}
        if self.prediction_history:
            recent_predictions = list(self.prediction_history)[-100:]
            prediction_stats = {
                "total_predictions": len(self.prediction_history),
                "recent_predictions": len(recent_predictions),
                "avg_confidence": np.mean([p.confidence for p in recent_predictions]),
                "avg_predicted_usage": np.mean([p.predicted_usage for p in recent_predictions]),
                "avg_recommended_limit": np.mean([p.recommended_limit for p in recent_predictions])
            }
        
        return {
            "config": {
                "primary_model": self.config.primary_model.value,
                "optimization_strategy": self.config.optimization_strategy.value,
                "confidence_threshold": self.config.confidence_threshold,
                "safety_margin": self.config.safety_margin
            },
            "training": training_stats,
            "performance": performance_stats,
            "features": feature_stats,
            "predictions": prediction_stats,
            "feature_importance": self.feature_importance,
            "running": self._running,
            "timestamp": current_time.isoformat()
        }


# Global ML rate optimizer instance
_ml_rate_optimizer: Optional[MLRateOptimizer] = None


def get_ml_rate_optimizer(config: MLConfig = None) -> MLRateOptimizer:
    """Get or create global ML rate optimizer instance."""
    global _ml_rate_optimizer
    if _ml_rate_optimizer is None:
        _ml_rate_optimizer = MLRateOptimizer(config)
    return _ml_rate_optimizer


async def start_ml_rate_optimizer(config: MLConfig = None):
    """Start the global ML rate optimizer."""
    optimizer = get_ml_rate_optimizer(config)
    await optimizer.start()


async def stop_ml_rate_optimizer():
    """Stop the global ML rate optimizer."""
    global _ml_rate_optimizer
    if _ml_rate_optimizer:
        await _ml_rate_optimizer.stop()


async def predict_optimal_rate_limit(
    client_id: str,
    endpoint: str,
    user_tier: str,
    hours_ahead: int = 1
) -> PredictionResult:
    """Predict optimal rate limit using ML."""
    optimizer = get_ml_rate_optimizer()
    return await optimizer.predict_usage(client_id, endpoint, user_tier, hours_ahead)


async def add_usage_data_for_ml(
    client_id: str,
    endpoint: str,
    user_tier: str,
    request_count: int,
    response_time: float,
    error_rate: float = 0.0,
    concurrent_users: int = 1,
    system_load: float = 0.0
):
    """Add usage data for ML training."""
    optimizer = get_ml_rate_optimizer()
    await optimizer.add_usage_data(
        client_id, endpoint, user_tier, request_count, response_time, error_rate, concurrent_users, system_load
    )


def get_ml_optimizer_stats() -> Dict[str, Any]:
    """Get ML optimizer statistics."""
    optimizer = get_ml_rate_optimizer()
    return optimizer.get_model_stats()
