"""
Database Automation API Endpoints
Production-ready endpoints for database automation and scaling
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, Optional, List
import logging

from backend.core.database_automation import (
    get_database_automation,
    start_database_automation,
    stop_database_automation
)
from backend.core.database_scaling import (
    get_database_scaling_engine,
    start_database_scaling,
    stop_database_scaling
)
from backend.core.database_integration import get_database_integration

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/database/automation", tags=["database-automation"])

@router.get("/status")
async def get_automation_status() -> Dict[str, Any]:
    """Get database automation status"""
    try:
        automation = get_database_automation()
        scaling_engine = get_database_scaling_engine()
        
        automation_status = await automation.get_automation_status()
        scaling_status = scaling_engine.get_scaling_status()
        
        return {
            "status": "success",
            "data": {
                "automation": automation_status,
                "scaling": scaling_status,
                "timestamp": automation_status.get("current_time")
            }
        }
        
    except Exception as e:
        logger.error(f"Automation status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start")
async def start_automation(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Start database automation and scaling"""
    try:
        # Start automation in background
        background_tasks.add_task(start_database_automation)
        background_tasks.add_task(start_database_scaling)
        
        return {
            "status": "success",
            "message": "Database automation and scaling started",
            "timestamp": "starting"
        }
        
    except Exception as e:
        logger.error(f"Start automation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop")
async def stop_automation(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Stop database automation and scaling"""
    try:
        # Stop automation in background
        background_tasks.add_task(stop_database_automation)
        background_tasks.add_task(stop_database_scaling)
        
        return {
            "status": "success",
            "message": "Database automation and scaling stopped",
            "timestamp": "stopping"
        }
        
    except Exception as e:
        logger.error(f"Stop automation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/maintenance/run")
async def run_maintenance(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Run manual maintenance tasks"""
    try:
        automation = get_database_automation()
        
        # Run maintenance in background
        background_tasks.add_task(automation._perform_daily_maintenance)
        
        return {
            "status": "success",
            "message": "Maintenance tasks started",
            "timestamp": "running"
        }
        
    except Exception as e:
        logger.error(f"Manual maintenance error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/maintenance/status")
async def get_maintenance_status() -> Dict[str, Any]:
    """Get maintenance status and history"""
    try:
        automation = get_database_automation()
        status = await automation.get_automation_status()
        
        return {
            "status": "success",
            "data": {
                "last_maintenance": status.get("last_maintenance"),
                "next_maintenance": status.get("next_maintenance"),
                "automation_active": status.get("automation_active")
            }
        }
        
    except Exception as e:
        logger.error(f"Maintenance status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scaling/patterns")
async def get_scaling_patterns() -> Dict[str, Any]:
    """Get scaling patterns and predictions"""
    try:
        scaling_engine = get_database_scaling_engine()
        patterns = scaling_engine.get_scaling_status()
        
        return {
            "status": "success",
            "data": patterns
        }
        
    except Exception as e:
        logger.error(f"Scaling patterns error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scaling/evaluate")
async def evaluate_scaling() -> Dict[str, Any]:
    """Evaluate current scaling needs"""
    try:
        scaling_engine = get_database_scaling_engine()
        evaluation = await scaling_engine._evaluate_scaling_needs()
        
        return {
            "status": "success",
            "data": evaluation
        }
        
    except Exception as e:
        logger.error(f"Scaling evaluation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scaling/history")
async def get_scaling_history() -> Dict[str, Any]:
    """Get scaling history"""
    try:
        scaling_engine = get_database_scaling_engine()
        history = scaling_engine.scaling_history
        
        return {
            "status": "success",
            "data": {
                "history": history[-50:],  # Last 50 scaling events
                "total_events": len(history)
            }
        }
        
    except Exception as e:
        logger.error(f"Scaling history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scaling/predict")
async def predict_scaling() -> Dict[str, Any]:
    """Get scaling predictions"""
    try:
        scaling_engine = get_database_scaling_engine()
        
        # Get predictions
        next_hour = await scaling_engine._predict_next_hour_load()
        daily = await scaling_engine._predict_daily_load()
        
        return {
            "status": "success",
            "data": {
                "next_hour": next_hour,
                "daily": daily,
                "timestamp": "current"
            }
        }
        
    except Exception as e:
        logger.error(f"Scaling prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/load/history")
async def get_load_history(hours: int = 24) -> Dict[str, Any]:
    """Get load history for analysis"""
    try:
        scaling_engine = get_database_scaling_engine()
        all_history = scaling_engine.load_history
        
        # Filter by time period
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_history = [
            h for h in all_history 
            if h.get("timestamp", datetime.utcnow()) > cutoff_time
        ]
        
        return {
            "status": "success",
            "data": {
                "history": recent_history,
                "period_hours": hours,
                "data_points": len(recent_history)
            }
        }
        
    except Exception as e:
        logger.error(f"Load history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize")
async def optimize_database() -> Dict[str, Any]:
    """Run database optimization tasks"""
    try:
        automation = get_database_automation()
        
        # Run optimization tasks
        optimization_results = await automation._perform_hourly_optimization()
        
        return {
            "status": "success",
            "data": optimization_results
        }
        
    except Exception as e:
        logger.error(f"Database optimization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations")
async def get_recommendations() -> Dict[str, Any]:
    """Get database optimization recommendations"""
    try:
        automation = get_database_automation()
        scaling_engine = get_database_scaling_engine()
        
        # Get current load and scaling recommendations
        current_load = await scaling_engine._evaluate_scaling_needs()
        load_data = current_load.get("current_load", {})
        
        # Get contextual recommendations
        recommendations = await scaling_engine._get_contextual_recommendations(load_data)
        
        # Add scaling decision recommendations
        scaling_decision = current_load.get("scaling_decision", {})
        recommendations.extend(scaling_decision.get("recommendations", []))
        
        return {
            "status": "success",
            "data": {
                "recommendations": recommendations,
                "current_utilization": load_data.get("utilization", 0),
                "active_connections": load_data.get("active_connections", 0),
                "total_connections": load_data.get("total_connections", 0),
                "timestamp": datetime.utcnow()
            }
        }
        
    except Exception as e:
        logger.error(f"Recommendations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_automation_metrics() -> Dict[str, Any]:
    """Get comprehensive automation metrics"""
    try:
        automation = get_database_automation()
        scaling_engine = get_database_scaling_engine()
        
        # Get automation metrics
        automation_status = await automation.get_automation_status()
        scaling_status = scaling_engine.get_scaling_status()
        
        # Calculate metrics
        metrics = {
            "automation": {
                "active": automation_status.get("automation_active", False),
                "last_maintenance": automation_status.get("last_maintenance"),
                "next_maintenance": automation_status.get("next_maintenance"),
                "uptime_percentage": 0.95  # Placeholder
            },
            "scaling": {
                "active": scaling_status.get("scaling_active", False),
                "total_scaling_events": len(scaling_engine.scaling_history),
                "scale_up_events": len([s for s in scaling_engine.scaling_history if "scale_up" in s.get("action", "")]),
                "scale_down_events": len([s for s in scaling_engine.scaling_history if "scale_down" in s.get("action", "")]),
                "current_thresholds": scaling_status.get("current_config", {})
            },
            "performance": {
                "load_history_size": len(scaling_engine.load_history),
                "avg_utilization": 0.0,  # Calculate from load history
                "peak_utilization": 0.0,  # Calculate from load history
                "baseline_load": scaling_status.get("patterns", {}).get("baseline_load", 0.0)
            }
        }
        
        # Calculate actual performance metrics
        if scaling_engine.load_history:
            utilizations = [h["utilization"] for h in scaling_engine.load_history]
            metrics["performance"]["avg_utilization"] = sum(utilizations) / len(utilizations)
            metrics["performance"]["peak_utilization"] = max(utilizations)
        
        return {
            "status": "success",
            "data": metrics
        }
        
    except Exception as e:
        logger.error(f"Automation metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/emergency/scale-up")
async def emergency_scale_up() -> Dict[str, Any]:
    """Emergency scale-up for critical situations"""
    try:
        scaling_engine = get_database_scaling_engine()
        
        # Force scale-up to maximum
        current_status = await scaling_engine._evaluate_scaling_needs()
        current_load = current_status.get("current_load", {})
        current_size = current_load.get("total_connections", 10)
        
        # Scale to maximum
        emergency_decision = {
            "action": "scale_up_emergency",
            "reason": "Emergency scale-up requested",
            "new_pool_size": scaling_engine.max_pool_size,
            "confidence": 1.0,
            "utilization": current_load.get("utilization", 0)
        }
        
        success = await scaling_engine._execute_scaling_action(emergency_decision)
        
        if success:
            return {
                "status": "success",
                "message": f"Emergency scale-up completed: {scaling_engine.max_pool_size} connections",
                "data": emergency_decision
            }
        else:
            raise HTTPException(status_code=500, detail="Emergency scale-up failed")
        
    except Exception as e:
        logger.error(f"Emergency scale-up error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
