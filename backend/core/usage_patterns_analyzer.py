"""
Usage Patterns Analyzer
========================

Advanced usage pattern analysis with anomaly detection, trend analysis,
and behavioral insights for rate limiting optimization.

Features:
- Statistical pattern analysis
- Anomaly detection with multiple algorithms
- Trend analysis and forecasting
- Behavioral clustering
- Seasonal pattern detection
- Usage correlation analysis
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
from scipy import stats
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

logger = logging.getLogger(__name__)


class PatternType(Enum):
    """Types of usage patterns."""
    TEMPORAL = "temporal"
    VOLUME = "volume"
    BEHAVIORAL = "behavioral"
    SEASONAL = "seasonal"
    CORRELATIONAL = "correlational"
    ANOMALOUS = "anomalous"


class AnomalyType(Enum):
    """Types of anomalies."""
    SPIKE = "spike"
    DROP = "drop"
    TREND_SHIFT = "trend_shift"
    PATTERN_BREAK = "pattern_break"
    OUTLIER = "outlier"
    CLUSTER_ANOMALY = "cluster_anomaly"


class TrendDirection(Enum):
    """Trend directions."""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"


@dataclass
class UsagePattern:
    """Usage pattern definition."""
    
    pattern_id: str
    pattern_type: PatternType
    name: str
    description: str
    confidence: float  # 0.0 to 1.0
    
    # Pattern data
    metrics: Dict[str, float] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Temporal information
    detected_at: datetime = field(default_factory=datetime.now)
    time_period: str = ""
    duration_hours: float = 0.0
    
    # Pattern strength
    strength: float = 0.0  # 0.0 to 1.0
    frequency: float = 0.0  # Occurrences per time period
    
    # Related entities
    client_ids: List[str] = field(default_factory=list)
    endpoints: List[str] = field(default_factory=list)
    user_tiers: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class AnomalyDetection:
    """Anomaly detection result."""
    
    anomaly_id: str
    anomaly_type: AnomalyType
    severity: str  # low, medium, high, critical
    confidence: float
    
    # Anomaly data
    description: str
    affected_entities: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    
    # Temporal information
    detected_at: datetime = field(default_factory=datetime.now)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: float = 0.0
    
    # Context
    expected_value: Optional[float] = None
    actual_value: Optional[float] = None
    deviation_percent: Optional[float] = None
    
    # Related patterns
    related_patterns: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class TrendAnalysis:
    """Trend analysis result."""
    
    trend_id: str
    metric_name: str
    direction: TrendDirection
    strength: float  # 0.0 to 1.0
    
    # Trend data
    slope: float = 0.0
    correlation: float = 0.0
    p_value: float = 0.0
    
    # Temporal information
    analyzed_at: datetime = field(default_factory=datetime.now)
    time_period: str = ""
    data_points: int = 0
    
    # Forecast
    forecast_value: Optional[float] = None
    forecast_confidence: Optional[float] = None
    forecast_horizon_hours: int = 0
    
    # Change points
    change_points: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class PatternAnalysisConfig:
    """Configuration for pattern analysis."""
    
    # Data settings
    min_data_points: int = 50
    max_data_points: int = 10000
    time_window_hours: int = 24
    
    # Anomaly detection
    anomaly_threshold_sigma: float = 2.5
    anomaly_min_confidence: float = 0.7
    enable_seasonal_anomaly: bool = True
    
    # Pattern detection
    pattern_min_confidence: float = 0.6
    pattern_min_frequency: float = 0.1
    enable_clustering: bool = True
    
    # Trend analysis
    trend_min_correlation: float = 0.5
    trend_min_p_value: float = 0.05
    enable_forecasting: bool = True
    
    # Performance
    analysis_interval_minutes: int = 30
    batch_processing: bool = True
    enable_caching: bool = True
    
    # Retention
    pattern_retention_days: int = 30
    anomaly_retention_days: int = 7
    trend_retention_days: int = 90


class UsagePatternsAnalyzer:
    """Advanced usage patterns analyzer."""
    
    def __init__(self, config: PatternAnalysisConfig = None):
        self.config = config or PatternAnalysisConfig()
        
        # Data storage
        self.usage_data: deque = deque(maxlen=self.config.max_data_points)
        self.detected_patterns: Dict[str, UsagePattern] = {}
        self.anomalies: Dict[str, AnomalyDetection] = {}
        self.trends: Dict[str, TrendAnalysis] = {}
        
        # Analysis state
        self.pattern_cache: Dict[str, Any] = {}
        self.analysis_history: deque = deque(maxlen=1000)
        
        # Statistical models
        self.scaler = StandardScaler()
        self.clustering_model = DBSCAN(eps=0.5, min_samples=5)
        self.pca_model = PCA(n_components=0.95)  # Keep 95% variance
        
        # Background tasks
        self._running = False
        self._analysis_task = None
        self._cleanup_task = None
        
        # Statistics
        self.total_analyses = 0
        self.total_patterns_detected = 0
        self.total_anomalies_detected = 0
        self.total_trends_analyzed = 0
        
        logger.info("Usage Patterns Analyzer initialized")
    
    async def start(self) -> None:
        """Start the patterns analyzer."""
        if self._running:
            logger.warning("Usage Patterns Analyzer is already running")
            return
        
        self._running = True
        
        # Start background tasks
        self._analysis_task = asyncio.create_task(self._analysis_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("Usage Patterns Analyzer started")
    
    async def stop(self) -> None:
        """Stop the patterns analyzer."""
        if not self._running:
            return
        
        self._running = False
        
        # Cancel background tasks
        if self._analysis_task:
            self._analysis_task.cancel()
            try:
                await self._analysis_task
            except asyncio.CancelledError:
                pass
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Usage Patterns Analyzer stopped")
    
    async def add_usage_data(
        self,
        client_id: str,
        endpoint: str,
        user_tier: str,
        request_count: int,
        response_time: float,
        error_rate: float = 0.0,
        timestamp: Optional[datetime] = None
    ) -> None:
        """Add usage data for pattern analysis."""
        if timestamp is None:
            timestamp = datetime.now()
        
        usage_point = {
            "timestamp": timestamp,
            "client_id": client_id,
            "endpoint": endpoint,
            "user_tier": user_tier,
            "request_count": request_count,
            "response_time": response_time,
            "error_rate": error_rate,
            "hour": timestamp.hour,
            "day_of_week": timestamp.weekday(),
            "day_of_month": timestamp.day,
            "month": timestamp.month
        }
        
        self.usage_data.append(usage_point)
    
    async def analyze_patterns(self, force: bool = False) -> Dict[str, Any]:
        """Perform comprehensive pattern analysis."""
        try:
            if len(self.usage_data) < self.config.min_data_points:
                return {"error": "Insufficient data for analysis"}
            
            current_time = datetime.now()
            
            # Check if analysis is needed
            if not force and self.analysis_history:
                last_analysis = self.analysis_history[-1]["timestamp"]
                if (current_time - last_analysis).total_seconds() < self.config.analysis_interval_minutes * 60:
                    return {"message": "Analysis not needed yet"}
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(list(self.usage_data))
            
            # Perform different types of analysis
            results = {
                "analysis_timestamp": current_time.isoformat(),
                "data_points": len(df),
                "temporal_patterns": await self._analyze_temporal_patterns(df),
                "volume_patterns": await self._analyze_volume_patterns(df),
                "behavioral_patterns": await self._analyze_behavioral_patterns(df),
                "anomalies": await self._detect_anomalies(df),
                "trends": await self._analyze_trends(df),
                "correlations": await self._analyze_correlations(df)
            }
            
            # Record analysis
            self.analysis_history.append({
                "timestamp": current_time,
                "results": results
            })
            self.total_analyses += 1
            
            return results
            
        except Exception as e:
            logger.error(f"Pattern analysis failed: {e}")
            return {"error": str(e)}
    
    async def _analyze_temporal_patterns(self, df: pd.DataFrame) -> List[UsagePattern]:
        """Analyze temporal usage patterns."""
        patterns = []
        
        try:
            # Hourly patterns
            hourly_avg = df.groupby("hour")["request_count"].mean()
            if len(hourly_avg) > 0:
                # Find peak hours
                peak_hours = hourly_avg.nlargest(3).index.tolist()
                
                pattern = UsagePattern(
                    pattern_id=f"temporal_hourly_{int(time.time())}",
                    pattern_type=PatternType.TEMPORAL,
                    name="Hourly Usage Pattern",
                    description=f"Peak usage hours: {peak_hours}",
                    confidence=0.8,
                    metrics={
                        "peak_hours": len(peak_hours),
                        "hourly_variance": hourly_avg.var(),
                        "peak_to_trough_ratio": hourly_avg.max() / (hourly_avg.min() + 1)
                    },
                    parameters={"peak_hours": peak_hours},
                    time_period="24h",
                    duration_hours=24.0,
                    strength=min(hourly_avg.std() / (hourly_avg.mean() + 1), 1.0)
                )
                patterns.append(pattern)
                self.detected_patterns[pattern.pattern_id] = pattern
                self.total_patterns_detected += 1
            
            # Day of week patterns
            dow_avg = df.groupby("day_of_week")["request_count"].mean()
            if len(dow_avg) > 0:
                # Find busy days
                busy_days = dow_avg.nlargest(3).index.tolist()
                
                pattern = UsagePattern(
                    pattern_id=f"temporal_dow_{int(time.time())}",
                    pattern_type=PatternType.TEMPORAL,
                    name="Day of Week Pattern",
                    description=f"Busy days: {busy_days}",
                    confidence=0.7,
                    metrics={
                        "busy_days": len(busy_days),
                        "dow_variance": dow_avg.var(),
                        "weekday_weekend_ratio": dow_avg[:5].mean() / (dow_avg[5:].mean() + 1)
                    },
                    parameters={"busy_days": busy_days},
                    time_period="7d",
                    duration_hours=168.0,
                    strength=min(dow_avg.std() / (dow_avg.mean() + 1), 1.0)
                )
                patterns.append(pattern)
                self.detected_patterns[pattern.pattern_id] = pattern
                self.total_patterns_detected += 1
        
        except Exception as e:
            logger.error(f"Temporal pattern analysis failed: {e}")
        
        return patterns
    
    async def _analyze_volume_patterns(self, df: pd.DataFrame) -> List[UsagePattern]:
        """Analyze volume usage patterns."""
        patterns = []
        
        try:
            # Request volume distribution
            volume_stats = df["request_count"].describe()
            
            # High volume pattern
            high_volume_threshold = volume_stats["75%"] + 1.5 * (volume_stats["75%"] - volume_stats["25%"])
            high_volume_clients = df[df["request_count"] > high_volume_threshold]["client_id"].unique()
            
            if len(high_volume_clients) > 0:
                pattern = UsagePattern(
                    pattern_id=f"volume_high_{int(time.time())}",
                    pattern_type=PatternType.VOLUME,
                    name="High Volume Usage",
                    description=f"{len(high_volume_clients)} clients with high volume usage",
                    confidence=0.8,
                    metrics={
                        "high_volume_clients": len(high_volume_clients),
                        "volume_threshold": high_volume_threshold,
                        "max_volume": volume_stats["max"]
                    },
                    parameters={"threshold": high_volume_threshold},
                    client_ids=high_volume_clients.tolist(),
                    strength=min(len(high_volume_clients) / len(df["client_id"].unique()), 1.0)
                )
                patterns.append(pattern)
                self.detected_patterns[pattern.pattern_id] = pattern
                self.total_patterns_detected += 1
        
        except Exception as e:
            logger.error(f"Volume pattern analysis failed: {e}")
        
        return patterns
    
    async def _analyze_behavioral_patterns(self, df: pd.DataFrame) -> List[UsagePattern]:
        """Analyze behavioral patterns using clustering."""
        patterns = []
        
        try:
            if not self.config.enable_clustering:
                return patterns
            
            # Prepare features for clustering
            features = df.groupby("client_id").agg({
                "request_count": ["mean", "std"],
                "response_time": ["mean", "std"],
                "error_rate": "mean",
                "hour": lambda x: x.mode().iloc[0] if not x.mode().empty else 0
            }).fillna(0)
            
            # Flatten column names
            features.columns = ["_".join(col).strip() for col in features.columns.values]
            
            if len(features) > 5:  # Need minimum samples for clustering
                # Scale features
                features_scaled = self.scaler.fit_transform(features)
                
                # Perform clustering
                clusters = self.clustering_model.fit_predict(features_scaled)
                features["cluster"] = clusters
                
                # Analyze clusters
                for cluster_id in np.unique(clusters):
                    if cluster_id == -1:  # Skip noise points
                        continue
                    
                    cluster_clients = features[features["cluster"] == cluster_id].index.tolist()
                    cluster_size = len(cluster_clients)
                    
                    if cluster_size >= 3:  # Minimum cluster size
                        pattern = UsagePattern(
                            pattern_id=f"behavioral_cluster_{cluster_id}_{int(time.time())}",
                            pattern_type=PatternType.BEHAVIORAL,
                            name=f"Behavioral Cluster {cluster_id}",
                            description=f"Cluster of {cluster_size} similar clients",
                            confidence=0.7,
                            metrics={
                                "cluster_size": cluster_size,
                                "cluster_id": int(cluster_id)
                            },
                            parameters={"cluster_algorithm": "DBSCAN"},
                            client_ids=cluster_clients,
                            strength=min(cluster_size / len(features), 1.0)
                        )
                        patterns.append(pattern)
                        self.detected_patterns[pattern.pattern_id] = pattern
                        self.total_patterns_detected += 1
        
        except Exception as e:
            logger.error(f"Behavioral pattern analysis failed: {e}")
        
        return patterns
    
    async def _detect_anomalies(self, df: pd.DataFrame) -> List[AnomalyDetection]:
        """Detect anomalies in usage data."""
        anomalies = []
        
        try:
            # Statistical anomaly detection
            numeric_columns = ["request_count", "response_time", "error_rate"]
            
            for col in numeric_columns:
                if col in df.columns:
                    # Z-score based anomaly detection
                    z_scores = np.abs(stats.zscore(df[col]))
                    anomaly_indices = np.where(z_scores > self.config.anomaly_threshold_sigma)[0]
                    
                    for idx in anomaly_indices:
                        row = df.iloc[idx]
                        
                        anomaly = AnomalyDetection(
                            anomaly_id=f"statistical_{col}_{idx}_{int(time.time())}",
                            anomaly_type=AnomalyType.OUTLIER,
                            severity="high" if z_scores[idx] > 3 else "medium",
                            confidence=min(z_scores[idx] / self.config.anomaly_threshold_sigma, 1.0),
                            description=f"{col} anomaly: {row[col]:.2f} (z-score: {z_scores[idx]:.2f})",
                            affected_entities=[row["client_id"]],
                            metrics={col: row[col], "z_score": z_scores[idx]},
                            start_time=row["timestamp"],
                            expected_value=df[col].mean(),
                            actual_value=row[col],
                            deviation_percent=abs(row[col] - df[col].mean()) / df[col].mean() * 100
                        )
                        anomalies.append(anomaly)
                        self.anomalies[anomaly.anomaly_id] = anomaly
                        self.total_anomalies_detected += 1
            
            # Trend-based anomaly detection
            if len(df) > 20:
                # Check for sudden changes in request count
                request_counts = df.sort_values("timestamp")["request_count"].values
                
                # Simple change point detection
                for i in range(10, len(request_counts) - 10):
                    before_mean = np.mean(request_counts[i-10:i])
                    after_mean = np.mean(request_counts[i:i+10])
                    
                    if before_mean > 0:
                        change_percent = abs(after_mean - before_mean) / before_mean
                        if change_percent > 0.5:  # 50% change
                            anomaly = AnomalyDetection(
                                anomaly_id=f"trend_change_{i}_{int(time.time())}",
                                anomaly_type=AnomalyType.TREND_SHIFT,
                                severity="high" if change_percent > 1.0 else "medium",
                                confidence=min(change_percent, 1.0),
                                description=f"Trend shift detected: {change_percent:.1%} change",
                                affected_entities=[df.iloc[i]["client_id"]],
                                metrics={"change_percent": change_percent},
                                start_time=df.iloc[i]["timestamp"],
                                expected_value=before_mean,
                                actual_value=after_mean,
                                deviation_percent=change_percent * 100
                            )
                            anomalies.append(anomaly)
                            self.anomalies[anomaly.anomaly_id] = anomaly
                            self.total_anomalies_detected += 1
        
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
        
        return anomalies
    
    async def _analyze_trends(self, df: pd.DataFrame) -> List[TrendAnalysis]:
        """Analyze trends in usage data."""
        trends = []
        
        try:
            # Sort by timestamp
            df_sorted = df.sort_values("timestamp")
            
            # Analyze trends for different metrics
            metrics_to_analyze = ["request_count", "response_time", "error_rate"]
            
            for metric in metrics_to_analyze:
                if metric not in df_sorted.columns:
                    continue
                
                # Get time series data
                timestamps = pd.to_datetime(df_sorted["timestamp"])
                values = df_sorted[metric].values
                
                if len(values) < 10:
                    continue
                
                # Linear trend analysis
                x = np.arange(len(values))
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
                
                # Determine trend direction
                if abs(slope) < 0.01:
                    direction = TrendDirection.STABLE
                elif slope > 0:
                    direction = TrendDirection.INCREASING
                else:
                    direction = TrendDirection.DECREASING
                
                # Create trend analysis
                trend = TrendAnalysis(
                    trend_id=f"trend_{metric}_{int(time.time())}",
                    metric_name=metric,
                    direction=direction,
                    strength=min(abs(r_value), 1.0),
                    slope=slope,
                    correlation=r_value,
                    p_value=p_value,
                    time_period=f"{len(values)} data points",
                    data_points=len(values)
                )
                
                # Add forecast if enabled
                if self.config.enable_forecasting and abs(r_value) > self.config.trend_min_correlation:
                    # Simple linear forecast
                    forecast_points = 24  # 24 hours ahead
                    forecast_x = np.arange(len(values), len(values) + forecast_points)
                    forecast_values = slope * forecast_x + intercept
                    trend.forecast_value = forecast_values[-1]
                    trend.forecast_confidence = abs(r_value)
                    trend.forecast_horizon_hours = 24
                
                trends.append(trend)
                self.trends[trend.trend_id] = trend
                self.total_trends_analyzed += 1
        
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
        
        return trends
    
    async def _analyze_correlations(self, df: pd.DataFrame) -> Dict[str, float]:
        """Analyze correlations between metrics."""
        correlations = {}
        
        try:
            # Select numeric columns
            numeric_columns = ["request_count", "response_time", "error_rate"]
            available_columns = [col for col in numeric_columns if col in df.columns]
            
            if len(available_columns) >= 2:
                correlation_matrix = df[available_columns].corr()
                
                # Extract significant correlations
                for i, col1 in enumerate(available_columns):
                    for j, col2 in enumerate(available_columns):
                        if i < j:  # Avoid duplicates
                            corr_value = correlation_matrix.iloc[i, j]
                            if not np.isnan(corr_value):
                                correlations[f"{col1}_vs_{col2}"] = corr_value
        
        except Exception as e:
            logger.error(f"Correlation analysis failed: {e}")
        
        return correlations
    
    async def _analysis_loop(self) -> None:
        """Background analysis loop."""
        while self._running:
            try:
                await asyncio.sleep(self.config.analysis_interval_minutes * 60)
                await self.analyze_patterns()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Analysis loop error: {e}")
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while self._running:
            try:
                await asyncio.sleep(3600)  # Cleanup every hour
                
                current_time = datetime.now()
                
                # Clean old patterns
                pattern_cutoff = current_time - timedelta(days=self.config.pattern_retention_days)
                pattern_ids_to_remove = [
                    pid for pid, pattern in self.detected_patterns.items()
                    if pattern.detected_at < pattern_cutoff
                ]
                
                for pid in pattern_ids_to_remove:
                    del self.detected_patterns[pid]
                
                # Clean old anomalies
                anomaly_cutoff = current_time - timedelta(days=self.config.anomaly_retention_days)
                anomaly_ids_to_remove = [
                    aid for aid, anomaly in self.anomalies.items()
                    if anomaly.detected_at < anomaly_cutoff
                ]
                
                for aid in anomaly_ids_to_remove:
                    del self.anomalies[aid]
                
                # Clean old trends
                trend_cutoff = current_time - timedelta(days=self.config.trend_retention_days)
                trend_ids_to_remove = [
                    tid for tid, trend in self.trends.items()
                    if trend.analyzed_at < trend_cutoff
                ]
                
                for tid in trend_ids_to_remove:
                    del self.trends[tid]
                
                # Clean old analysis history
                history_cutoff = current_time - timedelta(days=7)
                self.analysis_history = deque(
                    [analysis for analysis in self.analysis_history
                     if analysis["timestamp"] > history_cutoff],
                    maxlen=1000
                )
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
    
    def get_pattern_summary(self) -> Dict[str, Any]:
        """Get comprehensive pattern analysis summary."""
        current_time = datetime.now()
        
        # Pattern counts by type
        pattern_type_counts = defaultdict(int)
        for pattern in self.detected_patterns.values():
            pattern_type_counts[pattern.pattern_type.value] += 1
        
        # Anomaly counts by type
        anomaly_type_counts = defaultdict(int)
        severity_counts = defaultdict(int)
        for anomaly in self.anomalies.values():
            anomaly_type_counts[anomaly.anomaly_type.value] += 1
            severity_counts[anomaly.severity] += 1
        
        # Trend counts by direction
        trend_direction_counts = defaultdict(int)
        for trend in self.trends.values():
            trend_direction_counts[trend.direction.value] += 1
        
        # Recent anomalies
        recent_cutoff = current_time - timedelta(hours=24)
        recent_anomalies = [
            anomaly for anomaly in self.anomalies.values()
            if anomaly.detected_at > recent_cutoff
        ]
        
        return {
            "total_analyses": self.total_analyses,
            "total_patterns_detected": self.total_patterns_detected,
            "total_anomalies_detected": self.total_anomalies_detected,
            "total_trends_analyzed": self.total_trends_analyzed,
            "active_patterns_count": len(self.detected_patterns),
            "active_anomalies_count": len(self.anomalies),
            "active_trends_count": len(self.trends),
            "data_points_count": len(self.usage_data),
            "pattern_type_distribution": dict(pattern_type_counts),
            "anomaly_type_distribution": dict(anomaly_type_counts),
            "anomaly_severity_distribution": dict(severity_counts),
            "trend_direction_distribution": dict(trend_direction_counts),
            "recent_anomalies_24h": len(recent_anomalies),
            "last_analysis": self.analysis_history[-1]["timestamp"].isoformat() if self.analysis_history else None,
            "config": {
                "min_data_points": self.config.min_data_points,
                "anomaly_threshold_sigma": self.config.anomaly_threshold_sigma,
                "pattern_min_confidence": self.config.pattern_min_confidence,
                "enable_clustering": self.config.enable_clustering,
                "enable_forecasting": self.config.enable_forecasting
            },
            "running": self._running,
            "timestamp": current_time.isoformat()
        }
    
    def get_recent_anomalies(self, hours: int = 24, severity: Optional[str] = None) -> List[AnomalyDetection]:
        """Get recent anomalies."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        anomalies = [
            anomaly for anomaly in self.anomalies.values()
            if anomaly.detected_at > cutoff_time
        ]
        
        if severity:
            anomalies = [a for a in anomalies if a.severity == severity]
        
        return sorted(anomalies, key=lambda x: x.detected_at, reverse=True)
    
    def get_active_patterns(self, pattern_type: Optional[PatternType] = None) -> List[UsagePattern]:
        """Get active patterns."""
        patterns = list(self.detected_patterns.values())
        
        if pattern_type:
            patterns = [p for p in patterns if p.pattern_type == pattern_type]
        
        return sorted(patterns, key=lambda x: x.confidence, reverse=True)
    
    def get_current_trends(self, metric: Optional[str] = None) -> List[TrendAnalysis]:
        """Get current trends."""
        trends = list(self.trends.values())
        
        if metric:
            trends = [t for t in trends if t.metric_name == metric]
        
        return sorted(trends, key=lambda x: x.strength, reverse=True)


# Global usage patterns analyzer instance
_usage_patterns_analyzer: Optional[UsagePatternsAnalyzer] = None


def get_usage_patterns_analyzer(config: PatternAnalysisConfig = None) -> UsagePatternsAnalyzer:
    """Get or create global usage patterns analyzer instance."""
    global _usage_patterns_analyzer
    if _usage_patterns_analyzer is None:
        _usage_patterns_analyzer = UsagePatternsAnalyzer(config)
    return _usage_patterns_analyzer


async def start_usage_patterns_analyzer(config: PatternAnalysisConfig = None):
    """Start the global usage patterns analyzer."""
    analyzer = get_usage_patterns_analyzer(config)
    await analyzer.start()


async def stop_usage_patterns_analyzer():
    """Stop the global usage patterns analyzer."""
    global _usage_patterns_analyzer
    if _usage_patterns_analyzer:
        await _usage_patterns_analyzer.stop()


async def add_usage_data_for_analysis(
    client_id: str,
    endpoint: str,
    user_tier: str,
    request_count: int,
    response_time: float,
    error_rate: float = 0.0,
    timestamp: Optional[datetime] = None
):
    """Add usage data for pattern analysis."""
    analyzer = get_usage_patterns_analyzer()
    await analyzer.add_usage_data(client_id, endpoint, user_tier, request_count, response_time, error_rate, timestamp)


async def analyze_usage_patterns(force: bool = False) -> Dict[str, Any]:
    """Analyze usage patterns."""
    analyzer = get_usage_patterns_analyzer()
    return await analyzer.analyze_patterns(force)


def get_patterns_analysis_stats() -> Dict[str, Any]:
    """Get patterns analysis statistics."""
    analyzer = get_usage_patterns_analyzer()
    return analyzer.get_pattern_summary()
