"""
Advanced health monitoring system with predictive analytics and real-time monitoring.
Provides enterprise-grade health monitoring with AI-powered insights and alerting.
"""

import asyncio
import logging
import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable, Tuple
from enum import Enum
import numpy as np
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(Enum):
    """Types of health metrics."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class HealthMetric:
    """Individual health metric."""
    
    name: str
    value: float
    timestamp: datetime
    metric_type: MetricType
    unit: str
    tags: Dict[str, str]
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    
    def is_warning(self) -> bool:
        """Check if metric exceeds warning threshold."""
        return self.threshold_warning is not None and self.value > self.threshold_warning
    
    def is_critical(self) -> bool:
        """Check if metric exceeds critical threshold."""
        return self.threshold_critical is not None and self.value > self.threshold_critical


@dataclass
class HealthAlert:
    """Health alert notification."""
    
    id: str
    severity: AlertSeverity
    title: str
    description: str
    metric_name: str
    current_value: float
    threshold: float
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None


@dataclass
class HealthPrediction:
    """Health status prediction."""
    
    metric_name: str
    predicted_value: float
    confidence: float
    prediction_horizon: timedelta
    timestamp: datetime
    model_version: str
    features_used: List[str]


@dataclass
class SystemHealthReport:
    """Comprehensive system health report."""
    
    timestamp: datetime
    overall_status: HealthStatus
    health_score: float
    metrics: Dict[str, HealthMetric]
    alerts: List[HealthAlert]
    predictions: List[HealthPrediction]
    uptime_percentage: float
    performance_summary: Dict[str, Any]
    recommendations: List[str]


class PredictiveAnalytics:
    """Predictive analytics for health monitoring."""
    
    def __init__(self):
        self.models: Dict[str, RandomForestRegressor] = {}
        self.anomaly_detectors: Dict[str, IsolationForest] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.feature_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.prediction_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.is_trained = False
        
        # Model parameters
        self.lookback_window = 50  # Number of historical points to use
        self.prediction_horizon = 5  # Number of points to predict ahead
        self.anomaly_contamination = 0.1  # Expected anomaly rate
        
    def add_metric_data(self, metric_name: str, value: float, timestamp: datetime):
        """Add metric data for training and prediction."""
        self.feature_history[metric_name].append({
            'value': value,
            'timestamp': timestamp
        })
    
    def prepare_features(self, metric_name: str) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features for ML training."""
        history = list(self.feature_history[metric_name])
        if len(history) < self.lookback_window + self.prediction_horizon:
            return np.array([]), np.array([])
        
        # Create sliding window features
        X, y = [], []
        
        for i in range(len(history) - self.lookback_window - self.prediction_horizon + 1):
            # Features: last lookback_window values
            window = history[i:i + self.lookback_window]
            features = [point['value'] for point in window]
            
            # Add statistical features
            features.extend([
                statistics.mean(features),
                statistics.stdev(features) if len(set(features)) > 1 else 0,
                min(features),
                max(features),
                np.median(features)
            ])
            
            # Add time-based features
            timestamp = history[i + self.lookback_window]['timestamp']
            features.extend([
                timestamp.hour,
                timestamp.dayofweek,
                timestamp.day,
                timestamp.month
            ])
            
            X.append(features)
            
            # Target: prediction_horizon steps ahead
            target_value = history[i + self.lookback_window + self.prediction_horizon - 1]['value']
            y.append(target_value)
        
        return np.array(X), np.array(y)
    
    def train_model(self, metric_name: str) -> bool:
        """Train predictive model for a specific metric."""
        try:
            X, y = self.prepare_features(metric_name)
            if len(X) == 0:
                logger.warning(f"Insufficient data to train model for {metric_name}")
                return False
            
            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Train regression model
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            model.fit(X_scaled, y)
            
            # Train anomaly detector
            anomaly_detector = IsolationForest(
                contamination=self.anomaly_contamination,
                random_state=42
            )
            anomaly_detector.fit(X_scaled)
            
            # Store models
            self.models[metric_name] = model
            self.anomaly_detectors[metric_name] = anomaly_detector
            self.scalers[metric_name] = scaler
            
            logger.info(f"Trained predictive model for {metric_name} with {len(X)} samples")
            return True
            
        except Exception as e:
            logger.error(f"Failed to train model for {metric_name}: {e}")
            return False
    
    def predict_metric(self, metric_name: str, horizon_minutes: int = 30) -> Optional[HealthPrediction]:
        """Predict future metric values."""
        if metric_name not in self.models:
            return None
        
        try:
            history = list(self.feature_history[metric_name])
            if len(history) < self.lookback_window:
                return None
            
            # Prepare latest features
            window = history[-self.lookback_window:]
            features = [point['value'] for point in window]
            
            # Add statistical features
            features.extend([
                statistics.mean(features),
                statistics.stdev(features) if len(set(features)) > 1 else 0,
                min(features),
                max(features),
                np.median(features)
            ])
            
            # Add time-based features
            future_timestamp = datetime.now() + timedelta(minutes=horizon_minutes)
            features.extend([
                future_timestamp.hour,
                future_timestamp.dayofweek,
                future_timestamp.day,
                future_timestamp.month
            ])
            
            # Scale features
            X = np.array(features).reshape(1, -1)
            X_scaled = self.scalers[metric_name].transform(X)
            
            # Make prediction
            predicted_value = self.models[metric_name].predict(X_scaled)[0]
            
            # Calculate confidence based on historical accuracy
            confidence = self._calculate_prediction_confidence(metric_name, predicted_value)
            
            # Create prediction
            prediction = HealthPrediction(
                metric_name=metric_name,
                predicted_value=predicted_value,
                confidence=confidence,
                prediction_horizon=timedelta(minutes=horizon_minutes),
                timestamp=datetime.now(),
                model_version="1.0",
                features_used=[f"feature_{i}" for i in range(len(features))]
            )
            
            # Store prediction
            self.prediction_history[metric_name].append(prediction)
            
            return prediction
            
        except Exception as e:
            logger.error(f"Prediction failed for {metric_name}: {e}")
            return None
    
    def detect_anomaly(self, metric_name: str, value: float) -> bool:
        """Detect if current metric value is anomalous."""
        if metric_name not in self.anomaly_detectors:
            return False
        
        try:
            history = list(self.feature_history[metric_name])
            if len(history) < self.lookback_window:
                return False
            
            # Prepare features
            window = history[-self.lookback_window:]
            features = [point['value'] for point in window]
            features.extend([
                statistics.mean(features),
                statistics.stdev(features) if len(set(features)) > 1 else 0,
                min(features),
                max(features),
                np.median(features)
            ])
            
            # Add time-based features
            timestamp = datetime.now()
            features.extend([
                timestamp.hour,
                timestamp.dayofweek,
                timestamp.day,
                timestamp.month
            ])
            
            # Scale and predict
            X = np.array(features).reshape(1, -1)
            X_scaled = self.scalers[metric_name].transform(X)
            
            # Anomaly detection (-1 for anomaly, 1 for normal)
            prediction = self.anomaly_detectors[metric_name].predict(X_scaled)[0]
            return prediction == -1
            
        except Exception as e:
            logger.error(f"Anomaly detection failed for {metric_name}: {e}")
            return False
    
    def _calculate_prediction_confidence(self, metric_name: str, predicted_value: float) -> float:
        """Calculate confidence score for prediction."""
        try:
            predictions = list(self.prediction_history[metric_name])
            if len(predictions) < 5:
                return 0.5  # Default confidence
            
            # Calculate historical prediction accuracy
            actual_values = []
            predicted_values = []
            
            for i, pred in enumerate(predictions[:-1]):
                # Find actual value at prediction time
                pred_time = pred.timestamp + pred.prediction_horizon
                actual_value = None
                
                for point in self.feature_history[metric_name]:
                    if abs((point['timestamp'] - pred_time).total_seconds()) < 60:  # Within 1 minute
                        actual_value = point['value']
                        break
                
                if actual_value is not None:
                    actual_values.append(actual_value)
                    predicted_values.append(pred.predicted_value)
            
            if len(actual_values) < 3:
                return 0.5
            
            # Calculate accuracy metrics
            mae = mean_absolute_error(actual_values, predicted_values)
            rmse = np.sqrt(mean_squared_error(actual_values, predicted_values))
            
            # Convert to confidence (lower error = higher confidence)
            avg_value = np.mean(actual_values)
            relative_error = mae / max(avg_value, 1.0)
            confidence = max(0.1, 1.0 - relative_error)
            
            return min(confidence, 0.95)  # Cap at 95%
            
        except Exception as e:
            logger.error(f"Confidence calculation failed: {e}")
            return 0.5


class HealthMonitorAdvanced:
    """Advanced health monitoring with predictive analytics."""
    
    def __init__(self):
        self.metrics: Dict[str, HealthMetric] = {}
        self.alerts: Dict[str, HealthAlert] = {}
        self.predictive_analytics = PredictiveAnalytics()
        self.health_checks: Dict[str, Callable] = {}
        self.metric_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.start_time = datetime.now()
        
        # Monitoring configuration
        self.monitoring_interval = 60  # seconds
        self.prediction_interval = 300  # seconds
        self.alert_cooldown = 300  # seconds
        
        # Performance tracking
        self.downtime_periods: List[Tuple[datetime, datetime]] = []
        self.last_health_check = datetime.now()
        
        # Background tasks
        self._monitoring_task: Optional[asyncio.Task] = None
        self._prediction_task: Optional[asyncio.Task] = None
        self._is_monitoring = False
        
        # Register default health checks
        self._register_default_health_checks()
        
        logger.info("HealthMonitorAdvanced initialized")
    
    def _register_default_health_checks(self):
        """Register default health check functions."""
        self.register_health_check("system_resources", self._check_system_resources)
        self.register_health_check("database", self._check_database_health)
        self.register_health_check("redis", self._check_redis_health)
        self.register_health_check("llm_services", self._check_llm_services)
        self.register_health_check("memory_usage", self._check_memory_usage)
        self.register_health_check("response_times", self._check_response_times)
        self.register_health_check("error_rates", self._check_error_rates)
    
    def register_health_check(self, name: str, check_func: Callable):
        """Register a health check function."""
        self.health_checks[name] = check_func
        logger.info(f"Registered health check: {name}")
    
    def record_metric(self, name: str, value: float, unit: str = "", 
                     tags: Optional[Dict[str, str]] = None,
                     threshold_warning: Optional[float] = None,
                     threshold_critical: Optional[float] = None):
        """Record a health metric."""
        metric = HealthMetric(
            name=name,
            value=value,
            timestamp=datetime.now(),
            metric_type=MetricType.GAUGE,
            unit=unit,
            tags=tags or {},
            threshold_warning=threshold_warning,
            threshold_critical=threshold_critical
        )
        
        self.metrics[name] = metric
        self.metric_history[name].append(metric)
        
        # Add to predictive analytics
        self.predictive_analytics.add_metric_data(name, value, metric.timestamp)
        
        # Check for alerts
        self._check_metric_alerts(metric)
        
        # Check for anomalies
        if self.predictive_analytics.detect_anomaly(name, value):
            self._create_anomaly_alert(name, value)
    
    def _check_metric_alerts(self, metric: HealthMetric):
        """Check if metric triggers alerts."""
        alert_id = f"{metric.name}_{metric.timestamp.timestamp()}"
        
        # Check critical threshold
        if metric.is_critical():
            alert = HealthAlert(
                id=alert_id,
                severity=AlertSeverity.CRITICAL,
                title=f"Critical threshold exceeded for {metric.name}",
                description=f"Metric {metric.name} value {metric.value} exceeds critical threshold {metric.threshold_critical}",
                metric_name=metric.name,
                current_value=metric.value,
                threshold=metric.threshold_critical,
                timestamp=metric.timestamp
            )
            self.alerts[alert_id] = alert
            logger.critical(f"Critical alert: {alert.title}")
        
        # Check warning threshold
        elif metric.is_warning():
            alert = HealthAlert(
                id=alert_id,
                severity=AlertSeverity.WARNING,
                title=f"Warning threshold exceeded for {metric.name}",
                description=f"Metric {metric.name} value {metric.value} exceeds warning threshold {metric.threshold_warning}",
                metric_name=metric.name,
                current_value=metric.value,
                threshold=metric.threshold_warning,
                timestamp=metric.timestamp
            )
            self.alerts[alert_id] = alert
            logger.warning(f"Warning alert: {alert.title}")
    
    def _create_anomaly_alert(self, metric_name: str, value: float):
        """Create alert for anomalous metric."""
        alert_id = f"anomaly_{metric_name}_{datetime.now().timestamp()}"
        
        alert = HealthAlert(
            id=alert_id,
            severity=AlertSeverity.WARNING,
            title=f"Anomalous behavior detected for {metric_name}",
            description=f"Metric {metric_name} value {value} is anomalous based on historical patterns",
            metric_name=metric_name,
            current_value=value,
            threshold=0.0,  # Anomaly detection doesn't use fixed thresholds
            timestamp=datetime.now()
        )
        
        self.alerts[alert_id] = alert
        logger.warning(f"Anomaly alert: {alert.title}")
    
    async def run_health_checks(self) -> SystemHealthReport:
        """Run all registered health checks and generate report."""
        start_time = time.time()
        
        # Run health checks
        check_results = {}
        for name, check_func in self.health_checks.items():
            try:
                result = await check_func()
                check_results[name] = result
            except Exception as e:
                logger.error(f"Health check {name} failed: {e}")
                check_results[name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "response_time": 0.0
                }
        
        # Calculate overall health score
        health_score = self._calculate_health_score(check_results)
        overall_status = self._determine_overall_status(health_score)
        
        # Generate predictions
        predictions = await self._generate_predictions()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(check_results, predictions)
        
        # Calculate uptime
        uptime_percentage = self._calculate_uptime_percentage()
        
        # Performance summary
        performance_summary = self._generate_performance_summary()
        
        report = SystemHealthReport(
            timestamp=datetime.now(),
            overall_status=overall_status,
            health_score=health_score,
            metrics=self.metrics.copy(),
            alerts=list(self.alerts.values()),
            predictions=predictions,
            uptime_percentage=uptime_percentage,
            performance_summary=performance_summary,
            recommendations=recommendations
        )
        
        self.last_health_check = datetime.now()
        return report
    
    def _calculate_health_score(self, check_results: Dict[str, Any]) -> float:
        """Calculate overall health score from check results."""
        if not check_results:
            return 0.0
        
        scores = []
        for name, result in check_results.items():
            if isinstance(result, dict):
                status = result.get("status", "unknown")
                if status == "healthy":
                    scores.append(1.0)
                elif status == "degraded":
                    scores.append(0.6)
                elif status == "unhealthy":
                    scores.append(0.3)
                else:
                    scores.append(0.0)
            else:
                scores.append(0.5)  # Default for non-dict results
        
        return statistics.mean(scores) if scores else 0.0
    
    def _determine_overall_status(self, health_score: float) -> HealthStatus:
        """Determine overall health status from score."""
        if health_score >= 0.9:
            return HealthStatus.HEALTHY
        elif health_score >= 0.7:
            return HealthStatus.DEGRADED
        elif health_score >= 0.4:
            return HealthStatus.UNHEALTHY
        else:
            return HealthStatus.CRITICAL
    
    async def _generate_predictions(self) -> List[HealthPrediction]:
        """Generate health predictions."""
        predictions = []
        
        for metric_name in self.metrics.keys():
            # Train model if not already trained
            if metric_name not in self.predictive_analytics.models:
                self.predictive_analytics.train_model(metric_name)
            
            # Generate prediction
            prediction = self.predictive_analytics.predict_metric(metric_name)
            if prediction:
                predictions.append(prediction)
        
        return predictions
    
    def _generate_recommendations(self, check_results: Dict[str, Any], 
                                predictions: List[HealthPrediction]) -> List[str]:
        """Generate health recommendations."""
        recommendations = []
        
        # Based on check results
        for name, result in check_results.items():
            if isinstance(result, dict):
                status = result.get("status", "unknown")
                if status == "unhealthy":
                    recommendations.append(f"Investigate {name} service - currently unhealthy")
                elif status == "degraded":
                    recommendations.append(f"Monitor {name} service - performance degraded")
        
        # Based on predictions
        for prediction in predictions:
            if prediction.confidence > 0.7:
                if prediction.predicted_value > 80:  # Assuming higher is worse
                    recommendations.append(
                        f"Proactive action needed for {prediction.metric_name} - "
                        f"predicted to reach {prediction.predicted_value:.2f} in {prediction.prediction_horizon}"
                    )
        
        # Based on alerts
        active_alerts = [alert for alert in self.alerts.values() if not alert.resolved]
        if len(active_alerts) > 5:
            recommendations.append("High number of active alerts - consider system-wide investigation")
        
        return recommendations
    
    def _calculate_uptime_percentage(self) -> float:
        """Calculate system uptime percentage."""
        total_time = (datetime.now() - self.start_time).total_seconds()
        downtime = sum(
            (end - start).total_seconds()
            for start, end in self.downtime_periods
        )
        uptime = max(0, total_time - downtime)
        return (uptime / total_time * 100) if total_time > 0 else 100.0
    
    def _generate_performance_summary(self) -> Dict[str, Any]:
        """Generate performance summary statistics."""
        summary = {}
        
        for metric_name, history in self.metric_history.items():
            if len(history) > 0:
                values = [m.value for m in history]
                summary[metric_name] = {
                    "current": values[-1],
                    "average": statistics.mean(values),
                    "min": min(values),
                    "max": max(values),
                    "std_dev": statistics.stdev(values) if len(set(values)) > 1 else 0,
                    "trend": self._calculate_trend(values)
                }
        
        return summary
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for metric values."""
        if len(values) < 2:
            return "stable"
        
        # Simple linear regression for trend
        x = list(range(len(values)))
        n = len(values)
        
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    # Default health check implementations
    async def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage."""
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.record_metric("cpu_usage", cpu_percent, "%", 
                             threshold_warning=70, threshold_critical=90)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.record_metric("memory_usage", memory.percent, "%",
                             threshold_warning=80, threshold_critical=95)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.record_metric("disk_usage", disk_percent, "%",
                             threshold_warning=80, threshold_critical=95)
            
            status = "healthy"
            if cpu_percent > 90 or memory.percent > 95 or disk_percent > 95:
                status = "unhealthy"
            elif cpu_percent > 70 or memory.percent > 80 or disk_percent > 80:
                status = "degraded"
            
            return {
                "status": status,
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk_percent,
                "response_time": 0.1
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time": 0.0
            }
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance."""
        try:
            start_time = time.time()
            
            # This would be implemented based on actual database connection
            # For now, simulating the check
            await asyncio.sleep(0.1)  # Simulate database query
            
            response_time = time.time() - start_time
            self.record_metric("database_response_time", response_time * 1000, "ms",
                             threshold_warning=500, threshold_critical=1000)
            
            # Simulate connection status
            connection_status = "healthy"  # Would be actual check
            
            return {
                "status": connection_status,
                "response_time": response_time,
                "connections": 10  # Would be actual connection count
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time": 0.0
            }
    
    async def _check_redis_health(self) -> Dict[str, Any]:
        """Check Redis connectivity and performance."""
        try:
            start_time = time.time()
            
            # This would be implemented based on actual Redis connection
            # For now, simulating the check
            await asyncio.sleep(0.05)  # Simulate Redis ping
            
            response_time = time.time() - start_time
            self.record_metric("redis_response_time", response_time * 1000, "ms",
                             threshold_warning=100, threshold_critical=500)
            
            return {
                "status": "healthy",
                "response_time": response_time,
                "memory_usage": "45MB"  # Would be actual Redis memory usage
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time": 0.0
            }
    
    async def _check_llm_services(self) -> Dict[str, Any]:
        """Check LLM service availability and performance."""
        try:
            start_time = time.time()
            
            # This would check actual LLM service endpoints
            # For now, simulating the check
            await asyncio.sleep(0.2)  # Simulate LLM API call
            
            response_time = time.time() - start_time
            self.record_metric("llm_response_time", response_time * 1000, "ms",
                             threshold_warning=2000, threshold_critical=5000)
            
            return {
                "status": "healthy",
                "response_time": response_time,
                "services": ["vertex_ai", "openai"]  # Would be actual services
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time": 0.0
            }
    
    async def _check_memory_usage(self) -> Dict[str, Any]:
        """Check application memory usage."""
        try:
            import psutil
            
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            self.record_metric("app_memory_usage", memory_mb, "MB",
                             threshold_warning=1000, threshold_critical=2000)
            
            status = "healthy"
            if memory_mb > 2000:
                status = "unhealthy"
            elif memory_mb > 1000:
                status = "degraded"
            
            return {
                "status": status,
                "memory_mb": memory_mb,
                "response_time": 0.05
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time": 0.0
            }
    
    async def _check_response_times(self) -> Dict[str, Any]:
        """Check average response times."""
        try:
            # This would track actual response times
            # For now, using simulated data
            avg_response_time = 150  # ms
            
            self.record_metric("avg_response_time", avg_response_time, "ms",
                             threshold_warning=500, threshold_critical=1000)
            
            status = "healthy"
            if avg_response_time > 1000:
                status = "unhealthy"
            elif avg_response_time > 500:
                status = "degraded"
            
            return {
                "status": status,
                "avg_response_time": avg_response_time,
                "response_time": 0.05
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time": 0.0
            }
    
    async def _check_error_rates(self) -> Dict[str, Any]:
        """Check error rates."""
        try:
            # This would track actual error rates
            # For now, using simulated data
            error_rate = 2.5  # percentage
            
            self.record_metric("error_rate", error_rate, "%",
                             threshold_warning=5, threshold_critical=10)
            
            status = "healthy"
            if error_rate > 10:
                status = "unhealthy"
            elif error_rate > 5:
                status = "degraded"
            
            return {
                "status": status,
                "error_rate": error_rate,
                "response_time": 0.05
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time": 0.0
            }
    
    async def start_monitoring(self):
        """Start continuous health monitoring."""
        if self._is_monitoring:
            logger.warning("Health monitoring already started")
            return
        
        self._is_monitoring = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        self._prediction_task = asyncio.create_task(self._prediction_loop())
        
        logger.info("Started advanced health monitoring")
    
    async def stop_monitoring(self):
        """Stop continuous health monitoring."""
        if not self._is_monitoring:
            return
        
        self._is_monitoring = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
        if self._prediction_task:
            self._prediction_task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(
            self._monitoring_task,
            self._prediction_task,
            return_exceptions=True
        )
        
        logger.info("Stopped advanced health monitoring")
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self._is_monitoring:
            try:
                await self.run_health_checks()
                await asyncio.sleep(self.monitoring_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _prediction_loop(self):
        """Prediction generation loop."""
        while self._is_monitoring:
            try:
                # Train models periodically
                for metric_name in self.metrics.keys():
                    if metric_name not in self.predictive_analytics.models:
                        self.predictive_analytics.train_model(metric_name)
                
                await asyncio.sleep(self.prediction_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Prediction loop error: {e}")
                await asyncio.sleep(self.prediction_interval)
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str):
        """Acknowledge a health alert."""
        if alert_id in self.alerts:
            self.alerts[alert_id].acknowledged = True
            self.alerts[alert_id].acknowledged_by = acknowledged_by
            self.alerts[alert_id].acknowledged_at = datetime.now()
            logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
    
    def resolve_alert(self, alert_id: str):
        """Resolve a health alert."""
        if alert_id in self.alerts:
            self.alerts[alert_id].resolved = True
            self.alerts[alert_id].resolved_at = datetime.now()
            logger.info(f"Alert {alert_id} resolved")
    
    def get_health_dashboard_data(self) -> Dict[str, Any]:
        """Get data for health monitoring dashboard."""
        return {
            "current_metrics": {name: asdict(metric) for name, metric in self.metrics.items()},
            "active_alerts": [asdict(alert) for alert in self.alerts.values() if not alert.resolved],
            "recent_predictions": [asdict(pred) for preds in self.predictive_analytics.prediction_history.values() for pred in list(preds)[-5:]],
            "uptime_percentage": self._calculate_uptime_percentage(),
            "last_check": self.last_health_check.isoformat(),
            "monitoring_status": "active" if self._is_monitoring else "inactive"
        }


# Global health monitor instance
_health_monitor_advanced: Optional[HealthMonitorAdvanced] = None


def get_health_monitor_advanced() -> HealthMonitorAdvanced:
    """Get the global advanced health monitor instance."""
    global _health_monitor_advanced
    if _health_monitor_advanced is None:
        _health_monitor_advanced = HealthMonitorAdvanced()
    return _health_monitor_advanced


async def run_advanced_health_checks() -> SystemHealthReport:
    """Run advanced health checks (convenience function)."""
    monitor = get_health_monitor_advanced()
    return await monitor.run_health_checks()


def record_health_metric(name: str, value: float, unit: str = "", 
                       tags: Optional[Dict[str, str]] = None,
                       threshold_warning: Optional[float] = None,
                       threshold_critical: Optional[float] = None):
    """Record health metric (convenience function)."""
    monitor = get_health_monitor_advanced()
    monitor.record_metric(name, value, unit, tags, threshold_warning, threshold_critical)


async def start_advanced_health_monitoring():
    """Start advanced health monitoring (convenience function)."""
    monitor = get_health_monitor_advanced()
    await monitor.start_monitoring()


async def stop_advanced_health_monitoring():
    """Stop advanced health monitoring (convenience function)."""
    monitor = get_health_monitor_advanced()
    await monitor.stop_monitoring()


def get_health_dashboard_data() -> Dict[str, Any]:
    """Get health dashboard data (convenience function)."""
    monitor = get_health_monitor_advanced()
    return monitor.get_health_dashboard_data()
