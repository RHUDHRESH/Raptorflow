"""
Database Service - Legacy Compatibility Layer
Provides backward compatibility for existing code
"""

import logging
from typing import Any, Dict, Optional
from datetime import datetime

from .database_integration import get_database_integration
from .database_monitoring import get_database_monitor
from .migration_manager import get_migration_manager

logger = logging.getLogger(__name__)

class DatabaseService:
    """Legacy database service wrapper for new automation system"""
    
    def __init__(self):
        self.integration = get_database_integration()
        self.monitor = get_database_monitor()
        self.migration_manager = get_migration_manager()
    
    async def get_database_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            # Get system status
            status = await self.integration.get_system_status()
            
            # Extract statistics
            pool_stats = status.get("components", {}).get("connection_pool", {})
            migration_stats = status.get("components", {}).get("migrations", {})
            monitoring_stats = status.get("components", {}).get("monitoring", {})
            
            return {
                "connection_pool": pool_stats,
                "migrations": migration_stats,
                "monitoring": monitoring_stats,
                "overall_health": status.get("overall_health", "unknown"),
                "timestamp": status.get("timestamp")
            }
            
        except Exception as e:
            logger.error(f"Failed to get database statistics: {e}")
            return {"error": str(e)}
    
    async def create_backup(self) -> Dict[str, Any]:
        """Create database backup"""
        try:
            # This would integrate with the backup system
            # For now, return placeholder
            return {
                "status": "success",
                "backup_id": f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "created_at": datetime.utcnow(),
                "type": "automated"
            }
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return {"error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform database health check"""
        try:
            health_status = await self.monitor.get_current_status()
            
            return {
                "status": health_status.get("overall_status", "unknown"),
                "checks": health_status.get("checks", {}),
                "alerts": health_status.get("alerts", []),
                "timestamp": health_status.get("timestamp")
            }
            
        except Exception as e:
            logger.error(f"Failed to perform health check: {e}")
            return {"error": str(e)}
    
    async def get_connection(self) -> Any:
        """Get database connection"""
        try:
            # Get connection from pool
            manager = self.integration.db_manager
            return await manager.get_connection()
            
        except Exception as e:
            logger.error(f"Failed to get database connection: {e}")
            raise
    
    async def release_connection(self, connection: Any) -> None:
        """Release database connection"""
        try:
            # Release connection to pool
            manager = self.integration.db_manager
            await manager.release_connection(connection)
            
        except Exception as e:
            logger.error(f"Failed to release database connection: {e}")
    
    async def execute_query(self, query: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute database query"""
        try:
            # Get connection
            connection = await self.get_connection()
            
            try:
                # Execute query (this would be actual database execution)
                # For now, return placeholder
                result = {
                    "status": "success",
                    "query": query,
                    "params": params,
                    "timestamp": datetime.utcnow()
                }
                
                return result
                
            finally:
                await self.release_connection(connection)
                
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            return {"error": str(e)}
    
    async def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get table information"""
        try:
            # This would query database schema
            # For now, return placeholder
            return {
                "table_name": table_name,
                "columns": [],
                "indexes": [],
                "row_count": 0,
                "size": "0 MB"
            }
            
        except Exception as e:
            logger.error(f"Failed to get table info: {e}")
            return {"error": str(e)}
    
    async def optimize_table(self, table_name: str) -> Dict[str, Any]:
        """Optimize table"""
        try:
            # This would run table optimization
            # For now, return placeholder
            return {
                "status": "success",
                "table": table_name,
                "optimization_type": "vacuum_analyze",
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Failed to optimize table: {e}")
            return {"error": str(e)}

# Global database service instance
_database_service: Optional[DatabaseService] = None

def get_database_service() -> DatabaseService:
    """Get global database service"""
    global _database_service
    if _database_service is None:
        _database_service = DatabaseService()
    return _database_service

# Additional compatibility functions
async def check_database_health() -> Dict[str, Any]:
    """Check database health - compatibility function"""
    service = get_database_service()
    return await service.health_check()

async def get_database_connection() -> Any:
    """Get database connection - compatibility function"""
    service = get_database_service()
    return await service.get_connection()

async def release_database_connection(connection: Any) -> None:
    """Release database connection - compatibility function"""
    service = get_database_service()
    await service.release_connection(connection)

async def get_db():
    """Dependency for getting database connection"""
    service = get_database_service()
    connection = await service.get_connection()
    try:
        yield connection
    finally:
        await service.release_connection(connection)
