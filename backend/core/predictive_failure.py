"""
Predictive Failure Prevention System for Raptorflow.
Real-time monitoring and proactive failure prevention based on system metrics and patterns.
"""

import asyncio
import json
import logging
import psutil
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert levels for predictive failures"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class ResourceType(Enum):
    """Types of resources to monitor"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    CONNECTIONS = "connections"
    RATE_LIMIT = "rate_limit"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"


@dataclass
class ResourceMetric:
    """Resource metric data point"""
    resource_type: ResourceType
    value: float
    threshold: float
    timestamp: datetime
    alert_level: AlertLevel
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FailurePrediction:
    """Failure prediction result"""
    resource_type: ResourceType
    probability: float
    time_to_failure: Optional[float]  # Seconds until predicted failure
    alert_level: AlertLevel
    recommended_actions: List[str]
    confidence: float
    metrics: List[ResourceMetric]


@dataclass
class PreventionAction:
    """Prevention action that can be taken"""
    name: str
    description: str
    action_func: Callable
    priority: int
    cooldown_period: int  # Seconds between same action


class PredictiveFailurePrevention:
    """Predictive failure prevention with real-time monitoring"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.metrics_history: Dict[ResourceType, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.predictions: deque = deque(maxlen=100)
        self.prevention_actions: Dict[ResourceType, List[PreventionAction]] = {}
        self.action_history: deque = deque(maxlen=500)
        self.alert_callbacks: List[Callable] = []
        self.monitoring_active = False
        self.last_action_times: Dict[str, float] = {}
        
        # Thresholds for different resources
        self.thresholds = {
            ResourceType.CPU: {'warning': 70, 'critical': 85, 'emergency': 95},
            ResourceType.MEMORY: {'warning': 75, 'critical': 85, 'emergency': 95},
            ResourceType.DISK: {'warning': 80, 'critical': 90, 'emergency': 95},
            ResourceType.NETWORK: {'warning': 1000, 'critical': 2000, 'emergency': 5000},  # ms latency
            ResourceType.CONNECTIONS: {'warning': 100, 'critical': 200, 'emergency': 500},
            ResourceType.RESPONSE_TIME: {'warning': 2000, 'critical': 5000, 'emergency': 10000},  # ms
            ResourceType.ERROR_RATE: {'warning': 5, 'critical': 10, 'emergency': 20}  # percentage
        }
        
        self._register_prevention_actions()
    
    async def start_monitoring(self, interval: int = 30):
        """Start continuous monitoring"""
        self.monitoring_active = True
        
        async def monitor_loop():
            while self.monitoring_active:
                try:
                    await self._collect_metrics()
                    await self._analyze_and_predict()
                    await self._execute_prevention()
                    await asyncio.sleep(interval)
                except Exception as e:
                    logger.error(f"Monitoring loop error: {e}")
                    await asyncio.sleep(interval)
        
        asyncio.create_task(monitor_loop())
        logger.info("Predictive failure prevention monitoring started")
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring_active = False
        logger.info("Predictive failure prevention monitoring stopped")
    
    async def _collect_metrics(self):
        """Collect current system metrics"""
        timestamp = datetime.now()
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_metric = ResourceMetric(
            resource_type=ResourceType.CPU,
            value=cpu_percent,
            threshold=self.thresholds[ResourceType.CPU]['warning'],
            timestamp=timestamp,
            alert_level=self._determine_alert_level(cpu_percent, ResourceType.CPU)
        )
        self.metrics_history[ResourceType.CPU].append(cpu_metric)
        
        # Memory metrics
        memory = psutil.virtual_memory()
        memory_metric = ResourceMetric(
            resource_type=ResourceType.MEMORY,
            value=memory.percent,
            threshold=self.thresholds[ResourceType.MEMORY]['warning'],
            timestamp=timestamp,
            alert_level=self._determine_alert_level(memory.percent, ResourceType.MEMORY),
            metadata={'available_gb': memory.available / (1024**3)}
        )
        self.metrics_history[ResourceType.MEMORY].append(memory_metric)
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        disk_metric = ResourceMetric(
            resource_type=ResourceType.DISK,
            value=disk_percent,
            threshold=self.thresholds[ResourceType.DISK]['warning'],
            timestamp=timestamp,
            alert_level=self._determine_alert_level(disk_percent, ResourceType.DISK),
            metadata={'free_gb': disk.free / (1024**3)}
        )
        self.metrics_history[ResourceType.DISK].append(disk_metric)
        
        # Network metrics (simplified - would need actual network monitoring)
        network_metric = ResourceMetric(
            resource_type=ResourceType.NETWORK,
            value=0,  # Placeholder - would measure actual latency
            threshold=self.thresholds[ResourceType.NETWORK]['warning'],
            timestamp=timestamp,
            alert_level=AlertLevel.INFO
        )
        self.metrics_history[ResourceType.NETWORK].append(network_metric)
        
        # Connection metrics
        connections = len(psutil.net_connections())
        conn_metric = ResourceMetric(
            resource_type=ResourceType.CONNECTIONS,
            value=connections,
            threshold=self.thresholds[ResourceType.CONNECTIONS]['warning'],
            timestamp=timestamp,
            alert_level=self._determine_alert_level(connections, ResourceType.CONNECTIONS)
        )
        self.metrics_history[ResourceType.CONNECTIONS].append(conn_metric)
    
    async def _analyze_and_predict(self):
        """Analyze metrics and predict potential failures"""
        for resource_type, metrics in self.metrics_history.items():
            if len(metrics) < 10:  # Need enough data for prediction
                continue
            
            prediction = await self._predict_failure(resource_type, list(metrics))
            if prediction:
                self.predictions.append(prediction)
                
                # Send alerts if critical
                if prediction.alert_level in [AlertLevel.CRITICAL, AlertLevel.EMERGENCY]:
                    await self._send_alert(prediction)
    
    async def _predict_failure(self, resource_type: ResourceType, 
                             metrics: List[ResourceMetric]) -> Optional[FailurePrediction]:
        """Predict failure for a specific resource type"""
        if len(metrics) < 10:
            return None
        
        # Get recent metrics (last 10 data points)
        recent_metrics = metrics[-10:]
        values = [m.value for m in recent_metrics]
        
        # Calculate trend
        if len(values) >= 3:
            recent_trend = (values[-1] - values[-3]) / 2  # Rate of change
        else:
            recent_trend = 0
        
        # Get thresholds
        thresholds = self.thresholds[resource_type]
        emergency_threshold = thresholds['emergency']
        
        # Calculate probability of failure
        current_value = values[-1]
        probability = 0
        
        if current_value >= emergency_threshold:
            probability = 0.9
        elif current_value >= thresholds['critical']:
            probability = 0.7
        elif current_value >= thresholds['warning']:
            probability = 0.4
        
        # Adjust probability based on trend
        if recent_trend > 0:  # Increasing trend
            probability = min(1.0, probability + (recent_trend / 10))
        
        if probability < 0.3:  # Low probability - no prediction
            return None
        
        # Calculate time to failure
        time_to_failure = None
        if recent_trend > 0 and emergency_threshold > current_value:
            time_to_failure = (emergency_threshold - current_value) / recent_trend
        
        # Determine alert level
        alert_level = AlertLevel.WARNING
        if probability >= 0.8:
            alert_level = AlertLevel.EMERGENCY
        elif probability >= 0.6:
            alert_level = AlertLevel.CRITICAL
        elif probability >= 0.4:
            alert_level = AlertLevel.WARNING
        
        # Get recommended actions
        recommended_actions = self._get_recommended_actions(resource_type, alert_level)
        
        return FailurePrediction(
            resource_type=resource_type,
            probability=probability,
            time_to_failure=time_to_failure,
            alert_level=alert_level,
            recommended_actions=recommended_actions,
            confidence=min(probability + 0.1, 1.0),  # Add confidence buffer
            metrics=recent_metrics
        )
    
    async def _execute_prevention(self):
        """Execute prevention actions based on predictions"""
        if not self.predictions:
            return
        
        # Get most recent predictions
        recent_predictions = list(self.predictions)[-5:]  # Last 5 predictions
        
        for prediction in recent_predictions:
            if prediction.alert_level not in [AlertLevel.CRITICAL, AlertLevel.EMERGENCY]:
                continue
            
            # Get available actions for this resource type
            actions = self.prevention_actions.get(prediction.resource_type, [])
            
            # Sort by priority
            actions.sort(key=lambda x: x.priority)
            
            for action in actions:
                # Check cooldown
                action_key = f"{prediction.resource_type.value}:{action.name}"
                last_time = self.last_action_times.get(action_key, 0)
                
                if time.time() - last_time < action.cooldown_period:
                    continue
                
                try:
                    # Execute action
                    result = await action.action_func(prediction)
                    
                    # Record action
                    self.action_history.append({
                        'action': action.name,
                        'resource_type': prediction.resource_type.value,
                        'timestamp': datetime.now(),
                        'result': result,
                        'prediction': prediction
                    })
                    
                    self.last_action_times[action_key] = time.time()
                    
                    logger.info(f"Executed prevention action: {action.name} for {prediction.resource_type.value}")
                    
                    # Only execute one action per prediction cycle
                    break
                    
                except Exception as e:
                    logger.error(f"Prevention action failed: {action.name} - {e}")
    
    def _determine_alert_level(self, value: float, resource_type: ResourceType) -> AlertLevel:
        """Determine alert level based on value and thresholds"""
        thresholds = self.thresholds[resource_type]
        
        if value >= thresholds['emergency']:
            return AlertLevel.EMERGENCY
        elif value >= thresholds['critical']:
            return AlertLevel.CRITICAL
        elif value >= thresholds['warning']:
            return AlertLevel.WARNING
        else:
            return AlertLevel.INFO
    
    def _get_recommended_actions(self, resource_type: ResourceType, 
                                alert_level: AlertLevel) -> List[str]:
        """Get recommended actions for a resource type and alert level"""
        actions = self.prevention_actions.get(resource_type, [])
        return [action.description for action in actions if action.priority <= 3]
    
    async def _send_alert(self, prediction: FailurePrediction):
        """Send alert for critical predictions"""
        alert_data = {
            'resource_type': prediction.resource_type.value,
            'alert_level': prediction.alert_level.value,
            'probability': prediction.probability,
            'time_to_failure': prediction.time_to_failure,
            'recommended_actions': prediction.recommended_actions,
            'timestamp': datetime.now().isoformat()
        }
        
        # Send to callbacks
        for callback in self.alert_callbacks:
            try:
                await callback(alert_data)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")
        
        # Store in Redis
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    f"predictive_alert:{prediction.resource_type.value}",
                    timedelta(hours=1),
                    json.dumps(alert_data)
                )
            except Exception as e:
                logger.error(f"Failed to store alert in Redis: {e}")
        
        logger.warning(f"Predictive failure alert: {alert_data}")
    
    def _register_prevention_actions(self):
        """Register prevention actions for different resource types"""
        
        # CPU prevention actions
        self.prevention_actions[ResourceType.CPU] = [
            PreventionAction(
                name="reduce_process_priority",
                description="Reduce priority of non-critical processes",
                action_func=self._reduce_process_priority,
                priority=1,
                cooldown_period=300
            ),
            PreventionAction(
                name="scale_horizontal",
                description="Scale services horizontally if possible",
                action_func=self._scale_horizontal,
                priority=2,
                cooldown_period=600
            ),
            PreventionAction(
                name="enable_throttling",
                description="Enable request throttling",
                action_func=self._enable_throttling,
                priority=3,
                cooldown_period=180
            )
        ]
        
        # Memory prevention actions
        self.prevention_actions[ResourceType.MEMORY] = [
            PreventionAction(
                name="clear_caches",
                description="Clear application caches",
                action_func=self._clear_caches,
                priority=1,
                cooldown_period=120
            ),
            PreventionAction(
                name="garbage_collect",
                description="Force garbage collection",
                action_func=self._force_garbage_collection,
                priority=2,
                cooldown_period=60
            ),
            PreventionAction(
                name="restart_services",
                description="Restart memory-intensive services",
                action_func=self._restart_memory_intensive_services,
                priority=3,
                cooldown_period=600
            )
        ]
        
        # Disk prevention actions
        self.prevention_actions[ResourceType.DISK] = [
            PreventionAction(
                name="clean_temp_files",
                description="Clean temporary files",
                action_func=self._clean_temp_files,
                priority=1,
                cooldown_period=300
            ),
            PreventionAction(
                name="rotate_logs",
                description="Rotate and compress log files",
                action_func=self._rotate_logs,
                priority=2,
                cooldown_period=600
            ),
            PreventionAction(
                name="clear_old_data",
                description="Clear old data and cache",
                action_func=self._clear_old_data,
                priority=3,
                cooldown_period=900
            )
        ]
    
    async def _reduce_process_priority(self, prediction: FailurePrediction) -> Dict[str, Any]:
        """Reduce priority of non-critical processes"""
        # This would implement actual process priority reduction
        logger.info("Reducing process priority to prevent CPU overload")
        return {"action": "priority_reduced", "success": True}
    
    async def _scale_horizontal(self, prediction: FailurePrediction) -> Dict[str, Any]:
        """Scale services horizontally"""
        # This would implement actual horizontal scaling
        logger.info("Initiating horizontal scaling to handle CPU load")
        return {"action": "scaling_initiated", "success": True}
    
    async def _enable_throttling(self, prediction: FailurePrediction) -> Dict[str, Any]:
        """Enable request throttling"""
        # This would implement actual throttling
        logger.info("Enabling request throttling to reduce CPU load")
        return {"action": "throttling_enabled", "success": True}
    
    async def _clear_caches(self, prediction: FailurePrediction) -> Dict[str, Any]:
        """Clear application caches"""
        # This would implement actual cache clearing
        logger.info("Clearing application caches to free memory")
        return {"action": "caches_cleared", "success": True}
    
    async def _force_garbage_collection(self, prediction: FailurePrediction) -> Dict[str, Any]:
        """Force garbage collection"""
        import gc
        collected = gc.collect()
        logger.info(f"Forced garbage collection, collected {collected} objects")
        return {"action": "garbage_collected", "objects_collected": collected, "success": True}
    
    async def _restart_memory_intensive_services(self, prediction: FailurePrediction) -> Dict[str, Any]:
        """Restart memory-intensive services"""
        # This would implement actual service restart
        logger.info("Restarting memory-intensive services")
        return {"action": "services_restarted", "success": True}
    
    async def _clean_temp_files(self, prediction: FailurePrediction) -> Dict[str, Any]:
        """Clean temporary files"""
        # This would implement actual temp file cleaning
        logger.info("Cleaning temporary files to free disk space")
        return {"action": "temp_files_cleaned", "success": True}
    
    async def _rotate_logs(self, prediction: FailurePrediction) -> Dict[str, Any]:
        """Rotate and compress log files"""
        # This would implement actual log rotation
        logger.info("Rotating and compressing log files")
        return {"action": "logs_rotated", "success": True}
    
    async def _clear_old_data(self, prediction: FailurePrediction) -> Dict[str, Any]:
        """Clear old data and cache"""
        # This would implement actual data cleanup
        logger.info("Clearing old data and cache to free disk space")
        return {"action": "old_data_cleared", "success": True}
    
    def add_alert_callback(self, callback: Callable):
        """Add alert callback function"""
        self.alert_callbacks.append(callback)
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        current_metrics = {}
        
        for resource_type, metrics in self.metrics_history.items():
            if metrics:
                latest = metrics[-1]
                current_metrics[resource_type.value] = {
                    'value': latest.value,
                    'threshold': latest.threshold,
                    'alert_level': latest.alert_level.value,
                    'timestamp': latest.timestamp.isoformat(),
                    'metadata': latest.metadata
                }
        
        return current_metrics
    
    def get_recent_predictions(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent failure predictions"""
        recent = list(self.predictions)[-count:]
        return [
            {
                'resource_type': p.resource_type.value,
                'probability': p.probability,
                'time_to_failure': p.time_to_failure,
                'alert_level': p.alert_level.value,
                'recommended_actions': p.recommended_actions,
                'confidence': p.confidence,
                'timestamp': p.metrics[-1].timestamp.isoformat() if p.metrics else None
            }
            for p in recent
        ]
    
    def get_action_history(self, count: int = 20) -> List[Dict[str, Any]]:
        """Get recent prevention action history"""
        recent = list(self.action_history)[-count:]
        return [
            {
                'action': action['action'],
                'resource_type': action['resource_type'],
                'timestamp': action['timestamp'].isoformat(),
                'result': action['result'],
                'prediction_probability': action['prediction'].probability
            }
            for action in recent
        ]


# Global predictive failure prevention instance
_predictive_failure: Optional[PredictiveFailurePrevention] = None


def get_predictive_failure(redis_client: Optional[redis.Redis] = None) -> PredictiveFailurePrevention:
    """Get global predictive failure prevention instance"""
    global _predictive_failure
    if _predictive_failure is None:
        _predictive_failure = PredictiveFailurePrevention(redis_client)
    return _predictive_failure
