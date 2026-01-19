"""
Database Health API Endpoints
Production-ready endpoints for database monitoring and management
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
import logging

from backend.core.database_integration import (
    get_database_status,
    run_database_migrations,
    get_database_integration
)
from backend.core.database_monitoring import (
    get_database_monitoring_status,
    get_database_performance_report
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/database", tags=["database"])

@router.get("/health")
async def get_health(
    status: Dict[str, Any] = Depends(get_database_status)
) -> Dict[str, Any]:
    """Get comprehensive database health status"""
    return {
        "status": "success",
        "data": status
    }

@router.get("/status")
async def get_status(
    status: Dict[str, Any] = Depends(get_database_status)
) -> Dict[str, Any]:
    """Get database system status"""
    return {
        "status": "success",
        "data": status
    }

@router.get("/monitoring")
async def get_monitoring_status() -> Dict[str, Any]:
    """Get database monitoring status"""
    try:
        monitoring_status = await get_database_monitoring_status()
        return {
            "status": "success",
            "data": monitoring_status
        }
    except Exception as e:
        logger.error(f"Monitoring status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance")
async def get_performance_report() -> Dict[str, Any]:
    """Get database performance report"""
    try:
        report = await get_database_performance_report()
        return {
            "status": "success",
            "data": report
        }
    except Exception as e:
        logger.error(f"Performance report error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/migrations/run")
async def run_migrations(
    target_version: Optional[str] = None
) -> Dict[str, Any]:
    """Run database migrations"""
    try:
        result = await run_database_migrations(target_version)
        
        if result["status"] == "success":
            return {
                "status": "success",
                "message": result["message"],
                "data": result
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get("message", "Migration failed")
            )
            
    except Exception as e:
        logger.error(f"Migration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/migrations/status")
async def get_migration_status() -> Dict[str, Any]:
    """Get migration status"""
    try:
        integration = get_database_integration()
        status = await integration.migration_manager.get_migration_status()
        return {
            "status": "success",
            "data": status
        }
    except Exception as e:
        logger.error(f"Migration status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate")
async def validate_database() -> Dict[str, Any]:
    """Validate database configuration and setup"""
    try:
        integration = get_database_integration()
        
        # Validate migrations
        migration_validation = await integration.migration_manager.validate_migrations()
        
        # Get current health
        health_status = await integration.monitor.get_current_status()
        
        return {
            "status": "success",
            "data": {
                "migration_validation": migration_validation,
                "health_status": health_status
            }
        }
        
    except Exception as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_database_metrics() -> Dict[str, Any]:
    """Get database metrics for monitoring"""
    try:
        integration = get_database_integration()
        status = await integration.get_system_status()
        
        # Extract key metrics
        metrics = {
            "connection_pool": status.get("components", {}).get("connection_pool", {}),
            "health": status.get("components", {}).get("monitoring", {}),
            "migrations": status.get("components", {}).get("migrations", {}),
            "timestamp": status.get("timestamp")
        }
        
        return {
            "status": "success",
            "data": metrics
        }
        
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
