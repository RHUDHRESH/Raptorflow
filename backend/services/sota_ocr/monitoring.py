"""
OCR Monitoring and Analytics
Comprehensive monitoring and analytics for the SOTA OCR system
"""

import asyncio
import json
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from ..models import (
    DocumentCharacteristics,
    EnsembleResult,
    ModelPerformanceResponse,
    OCRModelResult,
    ProcessingStats,
    QualityMetrics,
)


@dataclass
class SystemMetrics:
    """Real-time system metrics."""

    timestamp: datetime
    total_documents: int
    successful_extractions: int
    failed_extractions: int
    average_confidence: float
    average_processing_time: float
    current_queue_size: int
    active_models: List[str]
    system_load: float
    memory_usage: float
    gpu_utilization: float


@dataclass
class ModelMetrics:
    """Individual model performance metrics."""

    model_name: str
    timestamp: datetime
    accuracy_score: float
    throughput_pages_per_sec: float
    error_rate: float
    average_confidence: float
    processing_time: float
    gpu_memory_usage: float
    cost_per_page: float
    uptime_percentage: float
    recent_performance: List[Dict[str, Any]]


@dataclass
class AlertConfig:
    """Configuration for alerts."""

    metric_name: str
    threshold: float
    comparison: str  # "gt", "lt", "eq"
    severity: str  # "critical", "warning", "info"
    enabled: bool
    cooldown_minutes: int


@dataclass
class Alert:
    """System alert."""

    id: str
    metric_name: str
    current_value: float
    threshold: float
    severity: str
    message: str
    timestamp: datetime
    resolved: bool
    resolved_at: Optional[datetime]


class MetricsCollector:
    """Collects and aggregates OCR system metrics."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.retention_hours = config.get("retention_hours", 24)
        self.collection_interval = config.get("collection_interval", 60)  # seconds

        # Metrics storage
        self.system_metrics = deque(
            maxlen=self.retention_hours * 60 // self.collection_interval
        )
        self.model_metrics = defaultdict(
            lambda: deque(maxlen=self.retention_hours * 60 // self.collection_interval)
        )

        # Aggregated counters
        self.total_documents = 0
        self.successful_extractions = 0
        self.failed_extractions = 0
        self.total_processing_time = 0.0
        self.total_confidence = 0.0

        # Model-specific counters
        self.model_usage = defaultdict(int)
        self.model_errors = defaultdict(int)
        self.model_processing_time = defaultdict(float)
        self.model_confidence = defaultdict(float)

    def record_document_processing(
        self,
        result: Union[OCRModelResult, EnsembleResult],
        success: bool,
        processing_time: float,
    ):
        """Record document processing metrics."""
        self.total_documents += 1

        if success:
            self.successful_extractions += 1
            self.total_confidence += result.confidence_score
        else:
            self.failed_extractions += 1

        self.total_processing_time += processing_time

        # Model-specific metrics
        if isinstance(result, OCRModelResult):
            self.record_model_usage(
                result.model_name, result.confidence_score, processing_time, success
            )
        elif isinstance(result, EnsembleResult):
            for model_result in result.model_results:
                self.record_model_usage(
                    model_result.model_name,
                    model_result.confidence_score,
                    model_result.processing_time,
                    success,
                )

    def record_model_usage(
        self, model_name: str, confidence: float, processing_time: float, success: bool
    ):
        """Record model-specific usage metrics."""
        self.model_usage[model_name] += 1
        self.model_processing_time[model_name] += processing_time
        self.model_confidence[model_name] += confidence

        if not success:
            self.model_errors[model_name] += 1

    def get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics."""
        if self.total_documents == 0:
            return SystemMetrics(
                timestamp=datetime.utcnow(),
                total_documents=0,
                successful_extractions=0,
                failed_extractions=0,
                average_confidence=0.0,
                average_processing_time=0.0,
                current_queue_size=0,
                active_models=[],
                system_load=0.0,
                memory_usage=0.0,
                gpu_utilization=0.0,
            )

        return SystemMetrics(
            timestamp=datetime.utcnow(),
            total_documents=self.total_documents,
            successful_extractions=self.successful_extractions,
            failed_extractions=self.failed_extractions,
            average_confidence=(
                self.total_confidence / self.successful_extractions
                if self.successful_extractions > 0
                else 0.0
            ),
            average_processing_time=self.total_processing_time / self.total_documents,
            current_queue_size=0,  # Would need queue implementation
            active_models=list(self.model_usage.keys()),
            system_load=self._get_system_load(),
            memory_usage=self._get_memory_usage(),
            gpu_utilization=self._get_gpu_utilization(),
        )

    def get_model_metrics(self, model_name: str) -> ModelMetrics:
        """Get metrics for a specific model."""
        usage_count = self.model_usage[model_name]
        error_count = self.model_errors[model_name]

        if usage_count == 0:
            return ModelMetrics(
                model_name=model_name,
                timestamp=datetime.utcnow(),
                accuracy_score=0.0,
                throughput_pages_per_sec=0.0,
                error_rate=0.0,
                average_confidence=0.0,
                processing_time=0.0,
                gpu_memory_usage=0.0,
                cost_per_page=0.0,
                uptime_percentage=0.0,
                recent_performance=[],
            )

        total_time = self.model_processing_time[model_name]
        total_confidence = self.model_confidence[model_name]

        return ModelMetrics(
            model_name=model_name,
            timestamp=datetime.utcnow(),
            accuracy_score=total_confidence / usage_count,
            throughput_pages_per_sec=(
                1.0 / (total_time / usage_count) if total_time > 0 else 0.0
            ),
            error_rate=error_count / usage_count,
            average_confidence=total_confidence / usage_count,
            processing_time=total_time / usage_count,
            gpu_memory_usage=self._get_model_gpu_memory(model_name),
            cost_per_page=self._get_model_cost_per_page(model_name),
            uptime_percentage=self._get_model_uptime(model_name),
            recent_performance=self._get_recent_performance(model_name),
        )

    def _get_system_load(self) -> float:
        """Get current system load."""
        # Placeholder implementation
        # In production, would use psutil or similar
        return 0.5

    def _get_memory_usage(self) -> float:
        """Get current memory usage."""
        # Placeholder implementation
        # In production, would use psutil or similar
        return 0.6

    def _get_gpu_utilization(self) -> float:
        """Get current GPU utilization."""
        # Placeholder implementation
        # In production, would use nvidia-ml-py or similar
        return 0.7

    def _get_model_gpu_memory(self, model_name: str) -> float:
        """Get GPU memory usage for specific model."""
        # Placeholder implementation
        # Would track actual GPU memory per model
        gpu_memory_map = {
            "chandra_ocr_8b": 16.0,
            "olm_ocr_2_7b": 12.0,
            "dots_ocr": 8.0,
            "deepseek_ocr_3b": 6.0,
            "lighton_ocr": 4.0,
        }
        return gpu_memory_map.get(model_name, 8.0)

    def _get_model_cost_per_page(self, model_name: str) -> float:
        """Get cost per page for specific model."""
        cost_map = {
            "chandra_ocr_8b": 0.456,  # $456 per million pages
            "olm_ocr_2_7b": 0.0,  # Open source
            "dots_ocr": 0.200,  # $200 per million pages
            "deepseek_ocr_3b": 0.234,  # $234 per million pages
            "lighton_ocr": 0.141,  # $141 per million pages
        }
        return cost_map.get(model_name, 0.0)

    def _get_model_uptime(self, model_name: str) -> float:
        """Get uptime percentage for specific model."""
        # Placeholder implementation
        # Would track actual model availability
        return 99.5

    def _get_recent_performance(self, model_name: str) -> List[Dict[str, Any]]:
        """Get recent performance data for model."""
        # Placeholder implementation
        # Would return actual recent metrics
        return [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "accuracy": 0.85,
                "throughput": 2.1,
            },
            {
                "timestamp": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                "accuracy": 0.83,
                "throughput": 2.0,
            },
            {
                "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                "accuracy": 0.87,
                "throughput": 2.2,
            },
        ]

    def get_processing_stats(self) -> ProcessingStats:
        """Get overall processing statistics."""
        if self.total_documents == 0:
            return ProcessingStats(
                total_documents=0,
                successful_extractions=0,
                failed_extractions=0,
                average_confidence=0.0,
                average_processing_time=0.0,
                model_usage_stats=dict(self.model_usage),
                document_type_stats={},
                language_distribution={},
                cost_per_page=0.0,
                throughput_pages_per_hour=0.0,
                error_rate=0.0,
            )

        return ProcessingStats(
            total_documents=self.total_documents,
            successful_extractions=self.successful_extractions,
            failed_extractions=self.failed_extractions,
            average_confidence=(
                self.total_confidence / self.successful_extractions
                if self.successful_extractions > 0
                else 0.0
            ),
            average_processing_time=self.total_processing_time / self.total_documents,
            model_usage_stats=dict(self.model_usage),
            document_type_stats={},  # Would track document types
            language_distribution={},  # Would track languages
            cost_per_page=self._calculate_average_cost_per_page(),
            throughput_pages_per_hour=self._calculate_throughput(),
            error_rate=self.failed_extractions / self.total_documents,
        )

    def _calculate_average_cost_per_page(self) -> float:
        """Calculate average cost per page across all models."""
        total_cost = 0.0
        total_pages = self.total_documents

        for model_name, usage_count in self.model_usage.items():
            cost_per_page = self._get_model_cost_per_page(model_name)
            total_cost += cost_per_page * usage_count

        return total_cost / total_pages if total_pages > 0 else 0.0

    def _calculate_throughput(self) -> float:
        """Calculate throughput in pages per hour."""
        if self.total_processing_time == 0:
            return 0.0

        # Calculate based on last hour of processing
        return (
            self.total_documents / self.total_processing_time
        ) * 3600  # Convert to per hour


class AlertSystem:
    """Manages alerts based on system metrics."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.alert_configs = self._initialize_alert_configs(config.get("alerts", {}))
        self.active_alerts = {}
        self.alert_history = deque(maxlen=1000)
        self.cooldown_periods = {}

    def _initialize_alert_configs(
        self, alert_configs: Dict[str, Any]
    ) -> Dict[str, AlertConfig]:
        """Initialize alert configurations."""
        defaults = {
            "accuracy_degradation": AlertConfig(
                metric_name="average_confidence",
                threshold=0.85,
                comparison="lt",
                severity="warning",
                enabled=True,
                cooldown_minutes=15,
            ),
            "high_error_rate": AlertConfig(
                metric_name="error_rate",
                threshold=0.05,
                comparison="gt",
                severity="critical",
                enabled=True,
                cooldown_minutes=5,
            ),
            "slow_processing": AlertConfig(
                metric_name="average_processing_time",
                threshold=10.0,
                comparison="gt",
                severity="warning",
                enabled=True,
                cooldown_minutes=10,
            ),
            "system_overload": AlertConfig(
                metric_name="system_load",
                threshold=0.9,
                comparison="gt",
                severity="critical",
                enabled=True,
                cooldown_minutes=5,
            ),
            "gpu_memory_high": AlertConfig(
                metric_name="gpu_utilization",
                threshold=0.95,
                comparison="gt",
                severity="warning",
                enabled=True,
                cooldown_minutes=10,
            ),
        }

        # Override with user configurations
        for name, user_config in alert_configs.items():
            if name in defaults:
                defaults[name] = AlertConfig(**user_config)

        return defaults

    async def check_alerts(
        self, metrics: SystemMetrics, model_metrics: Dict[str, ModelMetrics]
    ):
        """Check for alert conditions."""
        current_time = datetime.utcnow()

        # Check system-level alerts
        for alert_name, alert_config in self.alert_configs.items():
            if not alert_config.enabled:
                continue

            # Check cooldown
            if alert_name in self.cooldown_periods:
                if current_time < self.cooldown_periods[alert_name]:
                    continue

            # Get metric value
            metric_value = self._get_metric_value(
                metrics, model_metrics, alert_config.metric_name
            )

            if metric_value is None:
                continue

            # Check alert condition
            should_alert = self._evaluate_condition(
                metric_value, alert_config.threshold, alert_config.comparison
            )

            if should_alert and alert_name not in self.active_alerts:
                # Trigger new alert
                alert = self._create_alert(
                    alert_name, alert_config, metric_value, current_time
                )
                self.active_alerts[alert_name] = alert
                self.alert_history.append(alert)
                self.cooldown_periods[alert_name] = current_time + timedelta(
                    minutes=alert_config.cooldown_minutes
                )

                # Send notification (placeholder)
                await self._send_notification(alert)

            elif not should_alert and alert_name in self.active_alerts:
                # Resolve alert
                alert = self.active_alerts[alert_name]
                alert.resolved = True
                alert.resolved_at = current_time
                del self.active_alerts[alert_name]

    def _get_metric_value(
        self,
        system_metrics: SystemMetrics,
        model_metrics: Dict[str, ModelMetrics],
        metric_name: str,
    ) -> Optional[float]:
        """Get metric value by name."""
        if hasattr(system_metrics, metric_name):
            return getattr(system_metrics, metric_name)

        # Check model metrics
        for model_metric in model_metrics.values():
            if hasattr(model_metric, metric_name):
                return getattr(model_metric, metric_name)

        return None

    def _evaluate_condition(
        self, value: float, threshold: float, comparison: str
    ) -> bool:
        """Evaluate alert condition."""
        if comparison == "gt":
            return value > threshold
        elif comparison == "lt":
            return value < threshold
        elif comparison == "eq":
            return abs(value - threshold) < 0.001
        else:
            return False

    def _create_alert(
        self, alert_name: str, config: AlertConfig, value: float, timestamp: datetime
    ) -> Alert:
        """Create new alert."""
        alert_id = f"{alert_name}_{int(timestamp.timestamp())}"
        message = self._generate_alert_message(alert_name, config, value)

        return Alert(
            id=alert_id,
            metric_name=config.metric_name,
            current_value=value,
            threshold=config.threshold,
            severity=config.severity,
            message=message,
            timestamp=timestamp,
            resolved=False,
            resolved_at=None,
        )

    def _generate_alert_message(
        self, alert_name: str, config: AlertConfig, value: float
    ) -> str:
        """Generate alert message."""
        comparison_symbols = {"gt": ">", "lt": "<", "eq": "="}
        symbol = comparison_symbols.get(config.comparison, "?")

        messages = {
            "accuracy_degradation": f"OCR accuracy degraded to {value:.3f} {symbol} {config.threshold:.3f}",
            "high_error_rate": f"Error rate is {value:.3f} {symbol} {config.threshold:.3f}",
            "slow_processing": f"Processing time is {value:.2f}s {symbol} {config.threshold:.2f}s",
            "system_overload": f"System load is {value:.3f} {symbol} {config.threshold:.3f}",
            "gpu_memory_high": f"GPU utilization is {value:.3f} {symbol} {config.threshold:.3f}",
        }

        return messages.get(alert_name, f"Alert: {config.metric_name} is {value:.3f}")

    async def _send_notification(self, alert: Alert):
        """Send alert notification (placeholder)."""
        # In production, would send to Slack, email, PagerDuty, etc.
        print(f"ALERT: {alert.message} (Severity: {alert.severity})")

    def get_active_alerts(self) -> List[Alert]:
        """Get currently active alerts."""
        return list(self.active_alerts.values())

    def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """Get alert history."""
        return list(self.alert_history)[-limit:]


class AnalyticsDashboard:
    """Analytics dashboard for OCR system monitoring."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics_collector = MetricsCollector(config.get("metrics", {}))
        self.alert_system = AlertSystem(config.get("alerts", {}))

        # Start background monitoring
        self.monitoring_task = None

    async def start_monitoring(self):
        """Start background monitoring."""
        if self.monitoring_task is None:
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())

    async def stop_monitoring(self):
        """Stop background monitoring."""
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            self.monitoring_task = None

    async def _monitoring_loop(self):
        """Background monitoring loop."""
        while True:
            try:
                # Collect metrics
                system_metrics = self.metrics_collector.get_system_metrics()
                model_metrics = {}

                for model_name in [
                    "chandra_ocr_8b",
                    "olm_ocr_2_7b",
                    "dots_ocr",
                    "deepseek_ocr_3b",
                    "lighton_ocr",
                ]:
                    model_metrics[model_name] = (
                        self.metrics_collector.get_model_metrics(model_name)
                    )

                # Check alerts
                await self.alert_system.check_alerts(system_metrics, model_metrics)

                # Sleep until next collection
                await asyncio.sleep(self.metrics_collector.collection_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Monitoring error: {e}")
                await asyncio.sleep(60)  # Wait before retrying

    def record_processing_result(
        self,
        result: Union[OCRModelResult, EnsembleResult],
        success: bool,
        processing_time: float,
    ):
        """Record processing result for analytics."""
        self.metrics_collector.record_document_processing(
            result, success, processing_time
        )

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data."""
        system_metrics = self.metrics_collector.get_system_metrics()
        processing_stats = self.metrics_collector.get_processing_stats()
        active_alerts = self.alert_system.get_active_alerts()

        # Model performance data
        model_performance = {}
        for model_name in [
            "chandra_ocr_8b",
            "olm_ocr_2_7b",
            "dots_ocr",
            "deepseek_ocr_3b",
            "lighton_ocr",
        ]:
            model_metrics = self.metrics_collector.get_model_metrics(model_name)
            model_performance[model_name] = ModelPerformanceResponse(
                model_name=model_metrics.model_name,
                accuracy_score=model_metrics.accuracy_score,
                throughput_pages_per_sec=model_metrics.throughput_pages_per_sec,
                cost_per_million_pages=model_metrics.cost_per_page * 1000000,
                uptime_percentage=model_metrics.uptime_percentage,
                error_rate=model_metrics.error_rate,
                average_confidence=model_metrics.average_confidence,
                supported_languages=self._get_supported_languages(model_name),
                specializations=self._get_model_specializations(model_name),
                recent_performance=model_metrics.recent_performance,
            )

        return {
            "system_metrics": asdict(system_metrics),
            "processing_stats": asdict(processing_stats),
            "model_performance": {
                name: asdict(perf) for name, perf in model_performance.items()
            },
            "active_alerts": [asdict(alert) for alert in active_alerts],
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _get_supported_languages(self, model_name: str) -> List[str]:
        """Get supported languages for model."""
        language_map = {
            "chandra_ocr_8b": [
                "eng",
                "chi_sim",
                "spa",
                "fra",
                "deu",
                "jpn",
                "kor",
                "ara",
                "hin",
                "rus",
                "por",
                "ita",
                "tur",
                "pol",
                "nld",
            ],
            "olm_ocr_2_7b": [
                "eng",
                "chi_sim",
                "spa",
                "fra",
                "deu",
                "jpn",
                "kor",
                "ara",
                "hin",
                "rus",
                "por",
                "ita",
                "tur",
                "pol",
                "nld",
                "tha",
                "vie",
                "ind",
                "heb",
                "ben",
                "tam",
                "tel",
                "mar",
            ],
            "dots_ocr": [
                "eng",
                "chi_sim",
                "chi_tra",
                "spa",
                "fra",
                "deu",
                "jpn",
                "kor",
                "ara",
                "hin",
                "rus",
                "por",
                "ita",
                "tur",
                "pol",
                "nld",
                "tha",
                "vie",
                "ind",
                "heb",
                "ben",
                "tam",
                "tel",
                "mar",
                "guj",
                "kan",
                "mal",
                "ori",
                "pun",
                "urd",
                "mya",
                "khm",
                "lao",
                "sin",
                "tib",
            ],
            "deepseek_ocr_3b": ["eng", "chi_sim", "spa", "fra", "deu", "jpn", "kor"],
            "lighton_ocr": ["eng", "spa", "fra", "deu"],
        }
        return language_map.get(model_name, [])

    def _get_model_specializations(self, model_name: str) -> List[str]:
        """Get model specializations."""
        specialization_map = {
            "chandra_ocr_8b": ["complex", "form", "table", "technical", "mathematical"],
            "olm_ocr_2_7b": ["pdf", "image", "business_card"],
            "dots_ocr": ["multilingual", "id_document", "receipt"],
            "deepseek_ocr_3b": ["simple", "invoice", "receipt"],
            "lighton_ocr": ["simple", "invoice"],
        }
        return specialization_map.get(model_name, [])


class OCRMonitoring:
    """Main OCR monitoring system."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.dashboard = AnalyticsDashboard(config)
        self.is_running = False

    async def start(self):
        """Start monitoring system."""
        if not self.is_running:
            await self.dashboard.start_monitoring()
            self.is_running = True

    async def stop(self):
        """Stop monitoring system."""
        if self.is_running:
            await self.dashboard.stop_monitoring()
            self.is_running = False

    def record_processing(
        self,
        result: Union[OCRModelResult, EnsembleResult],
        success: bool,
        processing_time: float,
    ):
        """Record processing result."""
        self.dashboard.record_processing_result(result, success, processing_time)

    def get_monitoring_data(self) -> Dict[str, Any]:
        """Get comprehensive monitoring data."""
        return self.dashboard.get_dashboard_data()

    def get_system_health(self) -> Dict[str, Any]:
        """Get system health summary."""
        data = self.dashboard.get_dashboard_data()

        # Calculate health score
        health_score = self._calculate_health_score(data)

        return {
            "health_score": health_score,
            "status": (
                "healthy"
                if health_score > 0.8
                else "degraded" if health_score > 0.6 else "unhealthy"
            ),
            "active_alerts": len(data["active_alerts"]),
            "critical_alerts": len(
                [a for a in data["active_alerts"] if a["severity"] == "critical"]
            ),
            "last_updated": data["timestamp"],
        }

    def _calculate_health_score(self, data: Dict[str, Any]) -> float:
        """Calculate overall system health score."""
        score = 1.0

        # Penalize for active alerts
        critical_alerts = len(
            [a for a in data["active_alerts"] if a["severity"] == "critical"]
        )
        warning_alerts = len(
            [a for a in data["active_alerts"] if a["severity"] == "warning"]
        )

        score -= critical_alerts * 0.3
        score -= warning_alerts * 0.1

        # Penalize for low accuracy
        avg_confidence = data["system_metrics"]["average_confidence"]
        if avg_confidence < 0.8:
            score -= (0.8 - avg_confidence) * 0.5

        # Penalize for high error rate
        error_rate = data["processing_stats"]["error_rate"]
        if error_rate > 0.05:
            score -= (error_rate - 0.05) * 2.0

        return max(0.0, min(1.0, score))
