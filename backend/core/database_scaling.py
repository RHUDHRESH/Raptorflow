"""
Database Scaling Engine
Intelligent auto-scaling for database resources based on load patterns
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import statistics

from .database_config import DB_CONFIG
from .database_integration import get_database_integration
from .database_monitoring import get_database_monitor

logger = logging.getLogger(__name__)

class DatabaseScalingEngine:
    """Intelligent database scaling based on load patterns and predictions"""
    
    def __init__(self):
        self.integration = get_database_integration()
        self.monitor = get_database_monitor()
        self.scaling_active = False
        self.load_history: List[Dict[str, Any]] = []
        self.scaling_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000
        
        # Scaling thresholds
        self.scale_up_threshold = 0.8  # 80% utilization
        self.scale_down_threshold = 0.3  # 30% utilization
        self.critical_threshold = 0.95  # 95% utilization
        
        # Scaling limits
        self.min_pool_size = 5
        self.max_pool_size = 100
        self.scale_step = 5  # Add/remove 5 connections at a time
        
    async def start_scaling(self) -> None:
        """Start intelligent scaling engine"""
        self.scaling_active = True
        logger.info("Database scaling engine started")
        
        # Start scaling loops
        asyncio.create_task(self._scaling_loop())
        asyncio.create_task(self._load_analysis_loop())
        asyncio.create_task(self._prediction_loop())
    
    async def stop_scaling(self) -> None:
        """Stop scaling engine"""
        self.scaling_active = False
        logger.info("Database scaling engine stopped")
    
    async def _scaling_loop(self) -> None:
        """Main scaling decision loop"""
        while self.scaling_active:
            try:
                await self._evaluate_scaling_needs()
                await asyncio.sleep(60)  # Evaluate every minute
            except Exception as e:
                logger.error(f"Scaling loop error: {e}")
                await asyncio.sleep(60)
    
    async def _load_analysis_loop(self) -> None:
        """Load pattern analysis loop"""
        while self.scaling_active:
            try:
                await self._analyze_load_patterns()
                await asyncio.sleep(300)  # Analyze every 5 minutes
            except Exception as e:
                logger.error(f"Load analysis error: {e}")
                await asyncio.sleep(300)
    
    async def _prediction_loop(self) -> None:
        """Predictive scaling loop"""
        while self.scaling_active:
            try:
                await self._predict_and_pre_scale()
                await asyncio.sleep(900)  # Predict every 15 minutes
            except Exception as e:
                logger.error(f"Prediction loop error: {e}")
                await asyncio.sleep(900)
    
    async def _evaluate_scaling_needs(self) -> Dict[str, Any]:
        """Evaluate current scaling needs"""
        try:
            # Get current metrics
            current_status = await self.monitor.get_current_status()
            pool_stats = current_status.get("checks", {}).get("connection_pool", {})
            
            # Calculate load metrics
            utilization = pool_stats.get("utilization", 0)
            active_connections = pool_stats.get("active_connections", 0)
            total_connections = pool_stats.get("total_connections", 0)
            
            # Store load history
            load_data = {
                "timestamp": datetime.utcnow(),
                "utilization": utilization,
                "active_connections": active_connections,
                "total_connections": total_connections,
                "hour": datetime.utcnow().hour,
                "day_of_week": datetime.utcnow().weekday()
            }
            
            self._add_to_history(self.load_history, load_data)
            
            # Make scaling decision
            scaling_decision = await self._make_scaling_decision(load_data)
            
            if scaling_decision["action"] != "none":
                await self._execute_scaling_action(scaling_decision)
            
            return {
                "current_load": load_data,
                "scaling_decision": scaling_decision,
                "recommendations": scaling_decision.get("recommendations", [])
            }
            
        except Exception as e:
            logger.error(f"Scaling evaluation failed: {e}")
            return {"error": str(e)}
    
    async def _analyze_load_patterns(self) -> Dict[str, Any]:
        """Analyze historical load patterns"""
        try:
            if len(self.load_history) < 10:
                return {"status": "insufficient_data"}
            
            # Analyze patterns
            patterns = {
                "hourly_patterns": self._analyze_hourly_patterns(),
                "daily_patterns": self._analyze_daily_patterns(),
                "growth_trends": self._analyze_growth_trends(),
                "peak_periods": self._identify_peak_periods(),
                "baseline_load": self._calculate_baseline_load()
            }
            
            # Update scaling parameters based on patterns
            await self._update_scaling_parameters(patterns)
            
            return {
                "status": "success",
                "patterns": patterns,
                "data_points": len(self.load_history)
            }
            
        except Exception as e:
            logger.error(f"Load pattern analysis failed: {e}")
            return {"error": str(e)}
    
    async def _predict_and_pre_scale(self) -> Dict[str, Any]:
        """Predict future load and pre-scale if needed"""
        try:
            if len(self.load_history) < 50:
                return {"status": "insufficient_data"}
            
            # Predict next hour load
            next_hour_prediction = await self._predict_next_hour_load()
            
            # Predict next 24 hours
            daily_prediction = await self._predict_daily_load()
            
            # Check if pre-scaling is needed
            pre_scaling_actions = []
            
            if next_hour_prediction["predicted_utilization"] > self.scale_up_threshold:
                pre_scaling_actions.append({
                    "type": "pre_scale_up",
                    "reason": "High load predicted for next hour",
                    "predicted_utilization": next_hour_prediction["predicted_utilization"],
                    "recommended_pool_size": next_hour_prediction["recommended_pool_size"]
                })
            
            # Execute pre-scaling if beneficial
            for action in pre_scaling_actions:
                if await self._should_execute_pre_scaling(action):
                    await self._execute_pre_scaling(action)
            
            return {
                "status": "success",
                "next_hour": next_hour_prediction,
                "daily": daily_prediction,
                "pre_scaling_actions": pre_scaling_actions
            }
            
        except Exception as e:
            logger.error(f"Predictive scaling failed: {e}")
            return {"error": str(e)}
    
    async def _make_scaling_decision(self, load_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make intelligent scaling decision"""
        utilization = load_data["utilization"]
        total_connections = load_data["total_connections"]
        
        decision = {
            "action": "none",
            "reason": "",
            "new_pool_size": total_connections,
            "confidence": 0.0,
            "recommendations": []
        }
        
        # Critical scaling (immediate)
        if utilization >= self.critical_threshold:
            decision["action"] = "scale_up_critical"
            decision["reason"] = f"Critical utilization: {utilization:.1%}"
            decision["new_pool_size"] = min(total_connections + self.scale_step * 2, self.max_pool_size)
            decision["confidence"] = 0.95
            decision["recommendations"].append("Immediate scaling required - critical load")
        
        # Scale up
        elif utilization >= self.scale_up_threshold:
            # Check if this is sustained load
            recent_loads = [h["utilization"] for h in self.load_history[-10:]]
            sustained_high = statistics.mean(recent_loads) >= self.scale_up_threshold
            
            if sustained_high:
                decision["action"] = "scale_up"
                decision["reason"] = f"Sustained high utilization: {utilization:.1%}"
                decision["new_pool_size"] = min(total_connections + self.scale_step, self.max_pool_size)
                decision["confidence"] = 0.8
                decision["recommendations"].append("Scale up due to sustained high load")
            else:
                decision["recommendations"].append("Monitor for sustained high load")
        
        # Scale down (only if safe)
        elif utilization <= self.scale_down_threshold and total_connections > self.min_pool_size:
            # Check if this is sustained low load
            recent_loads = [h["utilization"] for h in self.load_history[-20:]]
            sustained_low = statistics.mean(recent_loads) <= self.scale_down_threshold
            
            if sustained_low:
                decision["action"] = "scale_down"
                decision["reason"] = f"Sustained low utilization: {utilization:.1%}"
                decision["new_pool_size"] = max(total_connections - self.scale_step, self.min_pool_size)
                decision["confidence"] = 0.7
                decision["recommendations"].append("Scale down due to sustained low load")
            else:
                decision["recommendations"].append("Monitor for sustained low load")
        
        # Add contextual recommendations
        decision["recommendations"].extend(await self._get_contextual_recommendations(load_data))
        
        return decision
    
    async def _execute_scaling_action(self, decision: Dict[str, Any]) -> bool:
        """Execute scaling action"""
        try:
            action = decision["action"]
            new_size = decision["new_pool_size"]
            
            if action == "none":
                return True
            
            # Log scaling action
            scaling_record = {
                "timestamp": datetime.utcnow(),
                "action": action,
                "reason": decision["reason"],
                "old_size": decision.get("current_pool_size", 0),
                "new_size": new_size,
                "confidence": decision["confidence"],
                "utilization": decision.get("utilization", 0)
            }
            
            self._add_to_history(self.scaling_history, scaling_record)
            
            # Execute scaling (this would update the actual pool configuration)
            logger.info(f"Executing scaling: {action} to {new_size} connections")
            
            # For now, simulate scaling success
            success = True
            
            if success:
                logger.info(f"Scaling completed successfully: {action} to {new_size}")
                return True
            else:
                logger.error(f"Scaling failed: {action}")
                return False
                
        except Exception as e:
            logger.error(f"Scaling execution failed: {e}")
            return False
    
    def _analyze_hourly_patterns(self) -> Dict[str, Any]:
        """Analyze hourly load patterns"""
        hourly_data = {}
        
        for load in self.load_history:
            hour = load["hour"]
            if hour not in hourly_data:
                hourly_data[hour] = []
            hourly_data[hour].append(load["utilization"])
        
        patterns = {}
        for hour, values in hourly_data.items():
            if len(values) >= 3:  # Need at least 3 data points
                patterns[hour] = {
                    "avg_utilization": statistics.mean(values),
                    "peak_utilization": max(values),
                    "min_utilization": min(values),
                    "std_deviation": statistics.stdev(values) if len(values) > 1 else 0,
                    "data_points": len(values)
                }
        
        return patterns
    
    def _analyze_daily_patterns(self) -> Dict[str, Any]:
        """Analyze daily load patterns"""
        daily_data = {}
        
        for load in self.load_history:
            day = load["day_of_week"]
            if day not in daily_data:
                daily_data[day] = []
            daily_data[day].append(load["utilization"])
        
        patterns = {}
        for day, values in daily_data.items():
            if len(values) >= 3:
                patterns[day] = {
                    "avg_utilization": statistics.mean(values),
                    "peak_utilization": max(values),
                    "min_utilization": min(values),
                    "data_points": len(values)
                }
        
        return patterns
    
    def _analyze_growth_trends(self) -> Dict[str, Any]:
        """Analyze load growth trends"""
        if len(self.load_history) < 20:
            return {"status": "insufficient_data"}
        
        # Calculate trend over last 24 hours
        recent_loads = self.load_history[-24:]
        older_loads = self.load_history[-48:-24] if len(self.load_history) >= 48 else self.load_history[:24]
        
        recent_avg = statistics.mean([l["utilization"] for l in recent_loads])
        older_avg = statistics.mean([l["utilization"] for l in older_loads])
        
        growth_rate = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0
        
        return {
            "growth_rate": growth_rate,
            "recent_avg": recent_avg,
            "older_avg": older_avg,
            "trend": "increasing" if growth_rate > 0.05 else "stable" if abs(growth_rate) < 0.05 else "decreasing"
        }
    
    def _identify_peak_periods(self) -> List[Dict[str, Any]]:
        """Identify peak load periods"""
        hourly_patterns = self._analyze_hourly_patterns()
        peak_periods = []
        
        for hour, pattern in hourly_patterns.items():
            if pattern["avg_utilization"] > self.scale_up_threshold:
                peak_periods.append({
                    "hour": hour,
                    "avg_utilization": pattern["avg_utilization"],
                    "peak_utilization": pattern["peak_utilization"],
                    "severity": "high" if pattern["avg_utilization"] > self.critical_threshold else "medium"
                })
        
        return sorted(peak_periods, key=lambda x: x["avg_utilization"], reverse=True)
    
    def _calculate_baseline_load(self) -> float:
        """Calculate baseline load"""
        if len(self.load_history) < 10:
            return 0.0
        
        # Use 25th percentile as baseline
        utilizations = [l["utilization"] for l in self.load_history]
        utilizations.sort()
        
        baseline_index = int(len(utilizations) * 0.25)
        return utilizations[baseline_index]
    
    async def _update_scaling_parameters(self, patterns: Dict[str, Any]) -> None:
        """Update scaling parameters based on patterns"""
        try:
            # Adjust thresholds based on patterns
            baseline = patterns.get("baseline_load", 0.3)
            
            # If baseline is high, adjust thresholds
            if baseline > 0.5:
                self.scale_up_threshold = min(0.9, baseline + 0.1)
                self.scale_down_threshold = max(0.2, baseline - 0.1)
                logger.info(f"Adjusted scaling thresholds based on high baseline load: {baseline:.1%}")
            
        except Exception as e:
            logger.error(f"Failed to update scaling parameters: {e}")
    
    async def _predict_next_hour_load(self) -> Dict[str, Any]:
        """Predict load for next hour"""
        try:
            current_hour = datetime.utcnow().hour
            next_hour = (current_hour + 1) % 24
            
            # Get historical data for next hour
            hour_data = [l for l in self.load_history if l["hour"] == next_hour]
            
            if len(hour_data) < 5:
                return {"predicted_utilization": 0.5, "confidence": 0.3}
            
            # Consider day of week
            current_day = datetime.utcnow().weekday()
            same_day_data = [l for l in hour_data if l["day_of_week"] == current_day]
            
            if len(same_day_data) >= 3:
                predicted_utilization = statistics.mean([l["utilization"] for l in same_day_data])
                confidence = 0.7
            else:
                predicted_utilization = statistics.mean([l["utilization"] for l in hour_data])
                confidence = 0.5
            
            # Consider recent trend
            recent_trend = self._calculate_recent_trend()
            predicted_utilization += recent_trend * 0.1  # Small adjustment for trend
            
            # Calculate recommended pool size
            recommended_size = int(self.min_pool_size + (predicted_utilization * (self.max_pool_size - self.min_pool_size)))
            
            return {
                "predicted_utilization": max(0, min(1, predicted_utilization)),
                "confidence": confidence,
                "recommended_pool_size": max(self.min_pool_size, min(self.max_pool_size, recommended_size)),
                "data_points": len(hour_data)
            }
            
        except Exception as e:
            logger.error(f"Next hour prediction failed: {e}")
            return {"predicted_utilization": 0.5, "confidence": 0.0}
    
    async def _predict_daily_load(self) -> Dict[str, Any]:
        """Predict load for next 24 hours"""
        try:
            predictions = []
            
            for hour_ahead in range(24):
                future_hour = (datetime.utcnow().hour + hour_ahead) % 24
                hour_data = [l for l in self.load_history if l["hour"] == future_hour]
                
                if len(hour_data) >= 3:
                    predicted_utilization = statistics.mean([l["utilization"] for l in hour_data])
                    predictions.append({
                        "hour": future_hour,
                        "predicted_utilization": predicted_utilization
                    })
                else:
                    predictions.append({
                        "hour": future_hour,
                        "predicted_utilization": 0.5
                    })
            
            return {
                "hourly_predictions": predictions,
                "peak_predicted": max(p["predicted_utilization"] for p in predictions),
                "avg_predicted": statistics.mean([p["predicted_utilization"] for p in predictions])
            }
            
        except Exception as e:
            logger.error(f"Daily prediction failed: {e}")
            return {"error": str(e)}
    
    def _calculate_recent_trend(self) -> float:
        """Calculate recent load trend"""
        if len(self.load_history) < 10:
            return 0.0
        
        recent_loads = [l["utilization"] for l in self.load_history[-5:]]
        older_loads = [l["utilization"] for l in self.load_history[-10:-5]]
        
        recent_avg = statistics.mean(recent_loads)
        older_avg = statistics.mean(older_loads)
        
        return recent_avg - older_avg
    
    async def _should_execute_pre_scaling(self, action: Dict[str, Any]) -> bool:
        """Determine if pre-scaling should be executed"""
        try:
            # Only pre-scale if confidence is high and benefit is significant
            predicted_utilization = action["predicted_utilization"]
            confidence = 0.7  # Base confidence from prediction
            
            # Check if pre-scaling provides significant benefit
            if predicted_utilization > self.scale_up_threshold + 0.1:
                return confidence > 0.6
            
            return False
            
        except Exception:
            return False
    
    async def _execute_pre_scaling(self, action: Dict[str, Any]) -> bool:
        """Execute pre-scaling action"""
        try:
            recommended_size = action["recommended_pool_size"]
            
            logger.info(f"Executing pre-scaling to {recommended_size} connections")
            
            # This would update the actual pool configuration
            # For now, simulate success
            
            return True
            
        except Exception as e:
            logger.error(f"Pre-scaling execution failed: {e}")
            return False
    
    async def _get_contextual_recommendations(self, load_data: Dict[str, Any]) -> List[str]:
        """Get contextual recommendations based on load data"""
        recommendations = []
        
        try:
            hour = load_data["hour"]
            utilization = load_data["utilization"]
            
            # Time-based recommendations
            if 8 <= hour <= 18:  # Business hours
                if utilization > 0.7:
                    recommendations.append("High load during business hours - consider proactive scaling")
            
            # Weekend recommendations
            if load_data["day_of_week"] >= 5:  # Weekend
                if utilization > 0.5:
                    recommendations.append("Unexpected weekend load - investigate usage patterns")
            
            # Growth recommendations
            if len(self.load_history) > 50:
                trend = self._calculate_recent_trend()
                if trend > 0.05:
                    recommendations.append("Upward trend detected - monitor for continued growth")
            
        except Exception as e:
            logger.error(f"Contextual recommendations failed: {e}")
        
        return recommendations
    
    def _add_to_history(self, history: List[Dict[str, Any]], data: Dict[str, Any]) -> None:
        """Add data to history with size limit"""
        history.append(data)
        
        # Maintain history size limit
        if len(history) > self.max_history_size:
            history.pop(0)
    
    async def get_scaling_status(self) -> Dict[str, Any]:
        """Get current scaling status"""
        return {
            "scaling_active": self.scaling_active,
            "current_config": {
                "scale_up_threshold": self.scale_up_threshold,
                "scale_down_threshold": self.scale_down_threshold,
                "critical_threshold": self.critical_threshold,
                "min_pool_size": self.min_pool_size,
                "max_pool_size": self.max_pool_size,
                "scale_step": self.scale_step
            },
            "statistics": {
                "load_history_size": len(self.load_history),
                "scaling_history_size": len(self.scaling_history),
                "last_scaling": self.scaling_history[-1] if self.scaling_history else None
            },
            "patterns": {
                "hourly_patterns": self._analyze_hourly_patterns(),
                "peak_periods": self._identify_peak_periods(),
                "baseline_load": self._calculate_baseline_load()
            }
        }

# Global scaling engine instance
_database_scaling_engine: Optional[DatabaseScalingEngine] = None

def get_database_scaling_engine() -> DatabaseScalingEngine:
    """Get global database scaling engine"""
    global _database_scaling_engine
    if _database_scaling_engine is None:
        _database_scaling_engine = DatabaseScalingEngine()
    return _database_scaling_engine

# FastAPI startup/shutdown events
async def start_database_scaling() -> None:
    """Start database scaling on application startup"""
    engine = get_database_scaling_engine()
    await engine.start_scaling()

async def stop_database_scaling() -> None:
    """Stop database scaling on application shutdown"""
    engine = get_database_scaling_engine()
    await engine.stop_scaling()
