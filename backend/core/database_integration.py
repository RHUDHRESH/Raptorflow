"""
Database Integration Module
Integrates all database components for production deployment
"""

import asyncio
import logging
from typing import Dict, Any, Optional

from .database_config import DB_CONFIG
from .connection_pool import get_db_manager
from .migration_manager import get_migration_manager
from .database_monitoring import get_database_monitor

logger = logging.getLogger(__name__)

class DatabaseIntegration:
    """Production database integration manager"""
    
    def __init__(self):
        self.db_manager = get_db_manager()
        self.migration_manager = get_migration_manager()
        self.monitor = get_database_monitor()
        self._initialized = False
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize all database components"""
        logger.info("Initializing database integration...")
        
        results = {
            "status": "initializing",
            "components": {},
            "errors": []
        }
        
        try:
            # Validate configuration
            config_validation = DB_CONFIG.validate_settings()
            results["components"]["configuration"] = config_validation
            
            if not config_validation["valid"]:
                results["errors"].extend(config_validation["issues"])
                results["status"] = "failed"
                return results
            
            # Initialize connection pool
            logger.info("Initializing connection pool...")
            await self.db_manager.initialize()
            results["components"]["connection_pool"] = {"status": "initialized"}
            
            # Initialize migration manager
            logger.info("Initializing migration manager...")
            await self.migration_manager.initialize()
            results["components"]["migration_manager"] = {"status": "initialized"}
            
            # Check for pending migrations
            migration_status = await self.migration_manager.get_migration_status()
            results["components"]["migrations"] = migration_status
            
            if migration_status["pending_migrations"] > 0:
                logger.warning(f"Found {migration_status['pending_migrations']} pending migrations")
                results["components"]["migrations"]["action_required"] = True
            
            # Start monitoring
            logger.info("Starting database monitoring...")
            await self.monitor.start_monitoring()
            results["components"]["monitoring"] = {"status": "started"}
            
            # Perform initial health check
            health_status = await self.monitor.get_current_status()
            results["components"]["health"] = health_status
            
            self._initialized = True
            results["status"] = "success"
            results["message"] = "Database integration completed successfully"
            
            logger.info("Database integration completed successfully")
            
        except Exception as e:
            logger.error(f"Database integration failed: {e}")
            results["status"] = "failed"
            results["errors"].append(str(e))
        
        return results
    
    async def run_migrations(self, target_version: Optional[str] = None) -> Dict[str, Any]:
        """Run database migrations"""
        if not self._initialized:
            await self.initialize()
        
        logger.info("Running database migrations...")
        
        try:
            result = await self.migration_manager.migrate_up(target_version)
            
            if result["status"] == "success":
                logger.info(f"Migrations completed: {result['message']}")
            else:
                logger.error(f"Migration failed: {result['message']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Migration error: {e}")
            return {
                "status": "failed",
                "message": str(e),
                "migrations": [],
                "failed": [],
                "completed": []
            }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        if not self._initialized:
            await self.initialize()
        
        status = {
            "timestamp": asyncio.get_event_loop().time(),
            "initialized": self._initialized,
            "components": {}
        }
        
        try:
            # Connection pool status
            pool_stats = await self.db_manager.get_stats()
            status["components"]["connection_pool"] = pool_stats
            
            # Migration status
            migration_status = await self.migration_manager.get_migration_status()
            status["components"]["migrations"] = migration_status
            
            # Monitoring status
            monitoring_status = await self.monitor.get_current_status()
            status["components"]["monitoring"] = monitoring_status
            
            # Overall health
            status["overall_health"] = monitoring_status.get("overall_status", "unknown")
            
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            status["error"] = str(e)
        
        return status
    
    async def shutdown(self) -> None:
        """Shutdown database components gracefully"""
        logger.info("Shutting down database integration...")
        
        try:
            # Stop monitoring
            await self.monitor.stop_monitoring()
            
            # Close connection pools
            await self.db_manager.close()
            
            self._initialized = False
            logger.info("Database integration shutdown completed")
            
        except Exception as e:
            logger.error(f"Shutdown error: {e}")

# Global integration instance
_database_integration: Optional[DatabaseIntegration] = None

def get_database_integration() -> DatabaseIntegration:
    """Get global database integration"""
    global _database_integration
    if _database_integration is None:
        _database_integration = DatabaseIntegration()
    return _database_integration

# FastAPI startup/shutdown events
async def startup_database() -> Dict[str, Any]:
    """Initialize database on application startup"""
    integration = get_database_integration()
    return await integration.initialize()

async def shutdown_database() -> None:
    """Cleanup database on application shutdown"""
    integration = get_database_integration()
    await integration.shutdown()

# FastAPI dependencies
async def get_database_status() -> Dict[str, Any]:
    """Get database system status"""
    integration = get_database_integration()
    return await integration.get_system_status()

async def run_database_migrations(target_version: Optional[str] = None) -> Dict[str, Any]:
    """Run database migrations"""
    integration = get_database_integration()
    return await integration.run_migrations(target_version)
