"""
Cost Optimization Monitoring and Intelligence Module
Real-time cost tracking, prediction, and optimization recommendations
"""

import asyncio
import hashlib
import json
import logging
import sqlite3
import statistics
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

# Data processing for analytics
try:
    import numpy as np
    import pandas as pd
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler

    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False

# Monitoring
try:
    import psutil

    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class CostMetrics:
    """Cost tracking metrics"""

    timestamp: datetime
    user_id: str
    url: str
    processing_time: float
    cpu_usage: float
    memory_usage_mb: float
    bandwidth_bytes: int
    cache_hit: bool
    method: str
    content_size: int
    estimated_cost: float


@dataclass
class CostThresholds:
    """Cost thresholds and limits"""

    max_cost_per_user_hour: float = 10.0  # $10 per user per hour
    max_cost_per_day: float = 100.0  # $100 per day total
    budget_alert_threshold: float = 0.8  # Alert at 80% of budget
    performance_cost_ratio_threshold: float = (
        0.5  # Alert if cost/performance ratio too high
    )


@dataclass
class CostRecommendation:
    """Cost optimization recommendation"""

    type: str
    description: str
    potential_savings: float
    priority: str  # low, medium, high
    implementation_effort: str  # low, medium, high
    impact_score: float


class CostOptimizer:
    """Cost optimization and monitoring engine"""

    def __init__(self, db_path: str = "cost_optimization.db"):
        self.db_path = db_path
        self.thresholds = CostThresholds()
        self.cost_history = deque(maxlen=10000)  # Keep last 10k records
        self.user_costs = defaultdict(float)
        self.hourly_costs = defaultdict(float)
        self.daily_costs = defaultdict(float)

        # Cost calculation parameters (based on Cloud Run pricing)
        self.cost_per_vcpu_second = 0.000024  # $0.000024 per vCPU-second
        self.cost_per_gb_second = 0.0000025  # $0.0000025 per GB-second
        self.cost_per_gb_storage = 0.020  # $0.020 per GB-month
        self.cost_per_gb_egress = 0.12  # $0.12 per GB egress

        # Initialize database
        self._init_database()

        # Start background monitoring
        self._start_monitoring()

    def _init_database(self):
        """Initialize cost optimization database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Cost metrics table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cost_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                user_id TEXT,
                url TEXT,
                processing_time REAL,
                cpu_usage REAL,
                memory_usage_mb REAL,
                bandwidth_bytes INTEGER,
                cache_hit BOOLEAN,
                method TEXT,
                content_size INTEGER,
                estimated_cost REAL,
                content_hash TEXT
            )
        """
        )

        # User cost tracking
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_costs (
                user_id TEXT,
                date DATE,
                hourly_cost REAL,
                daily_cost REAL,
                scrape_count INTEGER,
                avg_processing_time REAL,
                cache_hit_rate REAL,
                PRIMARY KEY (user_id, date)
            )
        """
        )

        # Cost recommendations
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cost_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                type TEXT,
                description TEXT,
                potential_savings REAL,
                priority TEXT,
                implementation_effort TEXT,
                impact_score REAL,
                status TEXT DEFAULT 'pending'
            )
        """
        )

        # Budget alerts
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS budget_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                alert_type TEXT,
                user_id TEXT,
                current_cost REAL,
                budget_limit REAL,
                message TEXT,
                acknowledged BOOLEAN DEFAULT FALSE
            )
        """
        )

        conn.commit()
        conn.close()

    def _start_monitoring(self):
        """Start background cost monitoring"""
        if MONITORING_AVAILABLE:
            self.monitoring_task = asyncio.create_task(self._monitor_system_costs())

    async def _monitor_system_costs(self):
        """Background task to monitor system costs"""
        while True:
            try:
                # Get system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_info = psutil.virtual_memory()
                disk_info = psutil.disk_usage("/")

                # Calculate current system cost
                system_cost = self._calculate_system_cost(
                    cpu_percent,
                    memory_info.used / 1024 / 1024,  # MB
                    disk_info.used / 1024 / 1024 / 1024,  # GB
                )

                # Store system metrics
                await self._store_system_metrics(system_cost)

                # Check for budget alerts
                await self._check_budget_alerts()

                # Sleep for 60 seconds
                await asyncio.sleep(60)

            except Exception as e:
                logger.error("System monitoring error", error=str(e))
                await asyncio.sleep(60)

    def calculate_scrape_cost(self, metrics: CostMetrics) -> float:
        """Calculate cost for a single scrape operation"""

        # Compute cost
        vcpu_cost = metrics.processing_time * self.cost_per_vcpu_second
        memory_cost = (
            (metrics.memory_usage_mb / 1024)
            * metrics.processing_time
            * self.cost_per_gb_second
        )
        storage_cost = (
            (metrics.content_size / 1024 / 1024 / 1024)
            * self.cost_per_gb_storage
            / (30 * 24 * 3600)
        )  # Per second cost
        egress_cost = (
            metrics.bandwidth_bytes / 1024 / 1024 / 1024
        ) * self.cost_per_gb_egress

        total_cost = vcpu_cost + memory_cost + storage_cost + egress_cost

        # Apply cache discount
        if metrics.cache_hit:
            total_cost *= 0.1  # 90% discount for cache hits

        return round(total_cost, 6)

    def _calculate_system_cost(
        self, cpu_percent: float, memory_mb: float, disk_gb: float
    ) -> float:
        """Calculate current system running cost"""
        # Estimate based on current usage
        estimated_vcpus = cpu_percent / 100.0  # Assuming 1 vCPU = 100% CPU
        estimated_memory_gb = memory_mb / 1024

        # Cost per second
        system_cost = (
            estimated_vcpus * self.cost_per_vcpu_second
            + estimated_memory_gb * self.cost_per_gb_second
        )

        return system_cost

    async def track_scrape_cost(self, scrape_result: Dict[str, Any]) -> float:
        """Track cost for a scrape operation"""

        # Extract metrics
        metrics = CostMetrics(
            timestamp=datetime.now(timezone.utc),
            user_id=scrape_result.get("user_id", "unknown"),
            url=scrape_result.get("url", ""),
            processing_time=scrape_result.get("processing_time", 0),
            cpu_usage=scrape_result.get("system_info", {}).get("cpu_usage_percent", 0),
            memory_usage_mb=scrape_result.get("system_info", {}).get(
                "memory_usage_mb", 0
            ),
            bandwidth_bytes=scrape_result.get("content_length", 0),
            cache_hit=scrape_result.get("performance", {}).get("cache_hit", False),
            method=scrape_result.get("performance", {}).get("method", "unknown"),
            content_size=scrape_result.get("content_length", 0),
            estimated_cost=0.0,  # Will be calculated
        )

        # Calculate cost
        metrics.estimated_cost = self.calculate_scrape_cost(metrics)

        # Store in database
        await self._store_cost_metrics(metrics)

        # Update tracking
        self._update_cost_tracking(metrics)

        # Check for alerts
        await self._check_user_budget_alerts(metrics)

        # Generate recommendations
        await self._generate_cost_recommendations(metrics)

        return metrics.estimated_cost

    async def _store_cost_metrics(self, metrics: CostMetrics):
        """Store cost metrics in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO cost_metrics
            (timestamp, user_id, url, processing_time, cpu_usage, memory_usage_mb,
             bandwidth_bytes, cache_hit, method, content_size, estimated_cost, content_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                metrics.timestamp,
                metrics.user_id,
                metrics.url,
                metrics.processing_time,
                metrics.cpu_usage,
                metrics.memory_usage_mb,
                metrics.bandwidth_bytes,
                metrics.cache_hit,
                metrics.method,
                metrics.content_size,
                metrics.estimated_cost,
                hashlib.md5(metrics.url.encode()).hexdigest(),
            ),
        )

        conn.commit()
        conn.close()

    def _update_cost_tracking(self, metrics: CostMetrics):
        """Update cost tracking dictionaries"""
        # Add to history
        self.cost_history.append(metrics)

        # Update user costs
        current_hour = metrics.timestamp.replace(minute=0, second=0, microsecond=0)
        current_day = metrics.timestamp.date()

        self.user_costs[metrics.user_id] += metrics.estimated_cost
        self.hourly_costs[current_hour] += metrics.estimated_cost
        self.daily_costs[current_day] += metrics.estimated_cost

    async def _check_user_budget_alerts(self, metrics: CostMetrics):
        """Check if user is approaching budget limits"""
        current_hour = datetime.now(timezone.utc).replace(
            minute=0, second=0, microsecond=0
        )
        current_day = datetime.now(timezone.utc).date()

        # Calculate hourly and daily costs for user
        hourly_user_cost = self._calculate_user_cost(
            metrics.user_id, current_hour, "hourly"
        )
        daily_user_cost = self._calculate_user_cost(
            metrics.user_id, current_day, "daily"
        )

        # Check hourly limit
        if hourly_user_cost > self.thresholds.max_cost_per_user_hour:
            await self._create_budget_alert(
                "hourly_limit_exceeded",
                metrics.user_id,
                hourly_user_cost,
                self.thresholds.max_cost_per_user_hour,
                f"Hourly cost ${hourly_user_cost:.2f} exceeds limit ${self.thresholds.max_cost_per_user_hour:.2f}",
            )

        # Check daily limit
        if (
            daily_user_cost > self.thresholds.max_cost_per_user_hour * 24
        ):  # 24x hourly limit
            await self._create_budget_alert(
                "daily_limit_exceeded",
                metrics.user_id,
                daily_user_cost,
                self.thresholds.max_cost_per_user_hour * 24,
                f"Daily cost ${daily_user_cost:.2f} exceeds limit ${self.thresholds.max_cost_per_user_hour * 24:.2f}",
            )

        # Check budget threshold
        if (
            hourly_user_cost
            > self.thresholds.max_cost_per_user_hour
            * self.thresholds.budget_alert_threshold
        ):
            await self._create_budget_alert(
                "budget_warning",
                metrics.user_id,
                hourly_user_cost,
                self.thresholds.max_cost_per_user_hour,
                f"Approaching budget limit: ${hourly_user_cost:.2f} / ${self.thresholds.max_cost_per_user_hour:.2f}",
            )

    async def _check_budget_alerts(self):
        """Check overall budget alerts"""
        current_day = datetime.now(timezone.utc).date()
        total_daily_cost = sum(
            cost for day, cost in self.daily_costs.items() if day == current_day
        )

        # Check total daily budget
        if total_daily_cost > self.thresholds.max_cost_per_day:
            await self._create_budget_alert(
                "total_daily_limit_exceeded",
                "system",
                total_daily_cost,
                self.thresholds.max_cost_per_day,
                f"Total daily cost ${total_daily_cost:.2f} exceeds limit ${self.thresholds.max_cost_per_day:.2f}",
            )

    async def _create_budget_alert(
        self,
        alert_type: str,
        user_id: str,
        current_cost: float,
        budget_limit: float,
        message: str,
    ):
        """Create budget alert"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO budget_alerts
            (timestamp, alert_type, user_id, current_cost, budget_limit, message)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                datetime.now(timezone.utc),
                alert_type,
                user_id,
                current_cost,
                budget_limit,
                message,
            ),
        )

        conn.commit()
        conn.close()

        logger.warning(
            "Budget alert created",
            alert_type=alert_type,
            user_id=user_id,
            message=message,
        )

    async def _generate_cost_recommendations(self, metrics: CostMetrics):
        """Generate cost optimization recommendations"""
        recommendations = []

        # Check for high processing time
        if metrics.processing_time > 10.0:  # 10 seconds
            potential_savings = self._calculate_processing_time_savings(metrics)
            recommendations.append(
                CostRecommendation(
                    type="processing_time_optimization",
                    description=f"High processing time ({metrics.processing_time:.1f}s). Consider optimizing JavaScript execution or using cache.",
                    potential_savings=potential_savings,
                    priority="high",
                    implementation_effort="medium",
                    impact_score=0.8,
                )
            )

        # Check for low cache hit rate
        recent_user_scrapes = [
            m for m in self.cost_history if m.user_id == metrics.user_id
        ][-10:]
        if len(recent_user_scrapes) >= 5:
            cache_hit_rate = sum(1 for m in recent_user_scrapes if m.cache_hit) / len(
                recent_user_scrapes
            )
            if cache_hit_rate < 0.3:  # Less than 30% cache hits
                potential_savings = self._calculate_cache_savings(
                    metrics, cache_hit_rate
                )
                recommendations.append(
                    CostRecommendation(
                        type="cache_optimization",
                        description=f"Low cache hit rate ({cache_hit_rate:.1%}). Implement better caching strategies.",
                        potential_savings=potential_savings,
                        priority="high",
                        implementation_effort="low",
                        impact_score=0.9,
                    )
                )

        # Check for high memory usage
        if metrics.memory_usage_mb > 512:  # 512MB
            potential_savings = self._calculate_memory_savings(metrics)
            recommendations.append(
                CostRecommendation(
                    type="memory_optimization",
                    description=f"High memory usage ({metrics.memory_usage_mb:.1f}MB). Optimize memory allocation.",
                    potential_savings=potential_savings,
                    priority="medium",
                    implementation_effort="medium",
                    impact_score=0.6,
                )
            )

        # Check for inefficient method
        if metrics.method == "selenium" and metrics.processing_time > 5.0:
            recommendations.append(
                CostRecommendation(
                    type="method_optimization",
                    description="Selenium is slower than Playwright. Consider using Playwright as primary method.",
                    potential_savings=0.3,  # Estimated 30% savings
                    priority="medium",
                    implementation_effort="low",
                    impact_score=0.7,
                )
            )

        # Store recommendations
        for rec in recommendations:
            await self._store_recommendation(rec)

    async def _store_recommendation(self, recommendation: CostRecommendation):
        """Store cost recommendation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO cost_recommendations
            (timestamp, type, description, potential_savings, priority, implementation_effort, impact_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                datetime.now(timezone.utc),
                recommendation.type,
                recommendation.description,
                recommendation.potential_savings,
                recommendation.priority,
                recommendation.implementation_effort,
                recommendation.impact_score,
            ),
        )

        conn.commit()
        conn.close()

    def _calculate_processing_time_savings(self, metrics: CostMetrics) -> float:
        """Calculate potential savings from processing time optimization"""
        # Assume 50% reduction in processing time is achievable
        optimized_time = metrics.processing_time * 0.5
        current_cost = metrics.estimated_cost
        optimized_cost = self.calculate_scrape_cost(
            CostMetrics(
                timestamp=metrics.timestamp,
                user_id=metrics.user_id,
                url=metrics.url,
                processing_time=optimized_time,
                cpu_usage=metrics.cpu_usage,
                memory_usage_mb=metrics.memory_usage_mb,
                bandwidth_bytes=metrics.bandwidth_bytes,
                cache_hit=metrics.cache_hit,
                method=metrics.method,
                content_size=metrics.content_size,
                estimated_cost=0.0,
            )
        )

        return current_cost - optimized_cost

    def _calculate_cache_savings(
        self, metrics: CostMetrics, cache_hit_rate: float
    ) -> float:
        """Calculate potential savings from cache optimization"""
        # Assume cache hit rate can be improved to 80%
        target_cache_rate = 0.8
        current_cost = metrics.estimated_cost

        # Calculate cost with improved cache
        non_cached_cost = (
            current_cost / (1 - cache_hit_rate * 0.9)
            if cache_hit_rate < 1
            else current_cost
        )
        optimized_cost = non_cached_cost * (1 - target_cache_rate * 0.9)

        return current_cost - optimized_cost

    def _calculate_memory_savings(self, metrics: CostMetrics) -> float:
        """Calculate potential savings from memory optimization"""
        # Assume memory can be reduced by 50%
        optimized_memory = metrics.memory_usage_mb * 0.5
        current_cost = metrics.estimated_cost

        optimized_cost = self.calculate_scrape_cost(
            CostMetrics(
                timestamp=metrics.timestamp,
                user_id=metrics.user_id,
                url=metrics.url,
                processing_time=metrics.processing_time,
                cpu_usage=metrics.cpu_usage,
                memory_usage_mb=optimized_memory,
                bandwidth_bytes=metrics.bandwidth_bytes,
                cache_hit=metrics.cache_hit,
                method=metrics.method,
                content_size=metrics.content_size,
                estimated_cost=0.0,
            )
        )

        return current_cost - optimized_cost

    def _calculate_user_cost(
        self, user_id: str, period: datetime, period_type: str
    ) -> float:
        """Calculate cost for a user in a specific period"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if period_type == "hourly":
            cursor.execute(
                """
                SELECT SUM(estimated_cost) FROM cost_metrics
                WHERE user_id = ? AND timestamp >= ? AND timestamp < ?
            """,
                (user_id, period, period + timedelta(hours=1)),
            )
        else:  # daily
            cursor.execute(
                """
                SELECT SUM(estimated_cost) FROM cost_metrics
                WHERE user_id = ? AND date(timestamp) = ?
            """,
                (user_id, period),
            )

        result = cursor.fetchone()
        conn.close()

        return result[0] if result and result[0] else 0.0

    async def get_cost_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get comprehensive cost analytics"""
        conn = sqlite3.connect(self.db_path)

        # Get cost trends
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT DATE(timestamp) as date,
                   SUM(estimated_cost) as total_cost,
                   COUNT(*) as scrape_count,
                   AVG(processing_time) as avg_processing_time,
                   AVG(CASE WHEN cache_hit THEN 1 ELSE 0 END) as cache_hit_rate
            FROM cost_metrics
            WHERE timestamp >= date('now', '-{} days')
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
        """.format(
                days
            )
        )

        daily_costs = cursor.fetchall()

        # Get user cost breakdown
        cursor.execute(
            """
            SELECT user_id,
                   SUM(estimated_cost) as total_cost,
                   COUNT(*) as scrape_count,
                   AVG(processing_time) as avg_processing_time,
                   AVG(CASE WHEN cache_hit THEN 1 ELSE 0 END) as cache_hit_rate
            FROM cost_metrics
            WHERE timestamp >= date('now', '-{} days')
            GROUP BY user_id
            ORDER BY total_cost DESC
            LIMIT 10
        """.format(
                days
            )
        )

        user_costs = cursor.fetchall()

        # Get method cost comparison
        cursor.execute(
            """
            SELECT method,
                   COUNT(*) as scrape_count,
                   SUM(estimated_cost) as total_cost,
                   AVG(processing_time) as avg_processing_time
            FROM cost_metrics
            WHERE timestamp >= date('now', '-{} days')
            GROUP BY method
        """.format(
                days
            )
        )

        method_costs = cursor.fetchall()

        conn.close()

        # Calculate trends
        if len(daily_costs) >= 2:
            recent_avg = statistics.mean(
                [row[1] for row in daily_costs[:3]]
            )  # Last 3 days
            older_avg = statistics.mean(
                [row[1] for row in daily_costs[3:]]
            )  # Previous days
            cost_trend = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0
        else:
            cost_trend = 0

        return {
            "period_days": days,
            "daily_costs": [
                {
                    "date": str(row[0]),
                    "total_cost": row[1],
                    "scrape_count": row[2],
                    "avg_processing_time": row[3],
                    "cache_hit_rate": row[4],
                }
                for row in daily_costs
            ],
            "top_users": [
                {
                    "user_id": row[0],
                    "total_cost": row[1],
                    "scrape_count": row[2],
                    "avg_processing_time": row[3],
                    "cache_hit_rate": row[4],
                }
                for row in user_costs
            ],
            "method_costs": [
                {
                    "method": row[0],
                    "scrape_count": row[1],
                    "total_cost": row[2],
                    "avg_processing_time": row[3],
                    "cost_per_scrape": row[2] / row[1] if row[1] > 0 else 0,
                }
                for row in method_costs
            ],
            "cost_trend": cost_trend,
            "total_cost": sum(row[1] for row in daily_costs),
            "total_scrapes": sum(row[2] for row in daily_costs),
            "avg_cost_per_scrape": (
                sum(row[1] for row in daily_costs) / sum(row[2] for row in daily_costs)
                if sum(row[2] for row in daily_costs) > 0
                else 0
            ),
        }

    async def get_cost_recommendations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get cost optimization recommendations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT type, description, potential_savings, priority,
                   implementation_effort, impact_score, timestamp
            FROM cost_recommendations
            WHERE status = 'pending'
            ORDER BY impact_score DESC, potential_savings DESC
            LIMIT ?
        """,
            (limit,),
        )

        recommendations = cursor.fetchall()
        conn.close()

        return [
            {
                "type": row[0],
                "description": row[1],
                "potential_savings": row[2],
                "priority": row[3],
                "implementation_effort": row[4],
                "impact_score": row[5],
                "timestamp": row[6],
            }
            for row in recommendations
        ]

    async def get_budget_alerts(
        self, acknowledged: bool = False
    ) -> List[Dict[str, Any]]:
        """Get budget alerts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if acknowledged:
            cursor.execute(
                """
                SELECT alert_type, user_id, current_cost, budget_limit, message, timestamp
                FROM budget_alerts
                WHERE acknowledged = FALSE
                ORDER BY timestamp DESC
            """
            )
        else:
            cursor.execute(
                """
                SELECT alert_type, user_id, current_cost, budget_limit, message, timestamp
                FROM budget_alerts
                ORDER BY timestamp DESC
                LIMIT 20
            """
            )

        alerts = cursor.fetchall()
        conn.close()

        return [
            {
                "alert_type": row[0],
                "user_id": row[1],
                "current_cost": row[2],
                "budget_limit": row[3],
                "message": row[4],
                "timestamp": row[5],
            }
            for row in alerts
        ]

    async def predict_monthly_cost(self) -> Dict[str, Any]:
        """Predict monthly cost based on current trends"""
        if not ANALYTICS_AVAILABLE or len(self.cost_history) < 10:
            return {
                "prediction_available": False,
                "message": "Insufficient data for prediction",
            }

        try:
            # Prepare data for prediction
            recent_data = list(self.cost_history)[-100:]  # Last 100 records

            df = pd.DataFrame(
                [
                    {
                        "timestamp": m.timestamp,
                        "cost": m.estimated_cost,
                        "hour": m.timestamp.hour,
                        "day_of_week": m.timestamp.weekday(),
                        "user_id": m.user_id,
                        "processing_time": m.processing_time,
                        "cache_hit": int(m.cache_hit),
                    }
                    for m in recent_data
                ]
            )

            # Create features
            df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
            df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
            df["dow_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
            df["dow_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)

            # Prepare features and target
            features = [
                "hour_sin",
                "hour_cos",
                "dow_sin",
                "dow_cos",
                "processing_time",
                "cache_hit",
            ]
            X = df[features]
            y = df["cost"]

            # Train model
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            model = LinearRegression()
            model.fit(X_scaled, y)

            # Predict next 30 days
            predictions = []
            current_date = datetime.now(timezone.utc)

            for day_ahead in range(30):
                future_date = current_date + timedelta(days=day_ahead)

                # Create features for prediction
                hour_features = []
                for hour in range(24):
                    hour_sin = np.sin(2 * np.pi * hour / 24)
                    hour_cos = np.cos(2 * np.pi * hour / 24)
                    dow_sin = np.sin(2 * np.pi * future_date.weekday() / 7)
                    dow_cos = np.cos(2 * np.pi * future_date.weekday() / 7)

                    # Use average processing time and cache hit rate
                    avg_processing_time = df["processing_time"].mean()
                    avg_cache_hit = df["cache_hit"].mean()

                    features = [
                        [
                            hour_sin,
                            hour_cos,
                            dow_sin,
                            dow_cos,
                            avg_processing_time,
                            avg_cache_hit,
                        ]
                    ]
                    features_scaled = scaler.transform(features)

                    predicted_cost = model.predict(features_scaled)[0]
                    hour_features.append(predicted_cost)

                daily_prediction = sum(hour_features)
                predictions.append(
                    {
                        "date": future_date.date(),
                        "predicted_cost": daily_prediction,
                        "predicted_scrapes": len(hour_features),
                    }
                )

            total_monthly_cost = sum(p["predicted_cost"] for p in predictions)

            return {
                "prediction_available": True,
                "monthly_prediction": total_monthly_cost,
                "daily_predictions": predictions,
                "confidence": "medium",  # Based on linear regression
                "model_score": model.score(X_scaled, y),
            }

        except Exception as e:
            logger.error("Cost prediction failed", error=str(e))
            return {
                "prediction_available": False,
                "message": f"Prediction failed: {str(e)}",
            }

    async def acknowledge_recommendation(self, recommendation_id: int) -> bool:
        """Acknowledge a cost recommendation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE cost_recommendations
            SET status = 'acknowledged'
            WHERE id = ?
        """,
            (recommendation_id,),
        )

        conn.commit()
        conn.close()

        return cursor.rowcount > 0

    async def acknowledge_alert(self, alert_id: int) -> bool:
        """Acknowledge a budget alert"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE budget_alerts
            SET acknowledged = TRUE
            WHERE id = ?
        """,
            (alert_id,),
        )

        conn.commit()
        conn.close()

        return cursor.rowcount > 0


# Global cost optimizer instance
cost_optimizer = CostOptimizer()
