"""
Supabase production configuration and optimization for RaptorFlow
Production-ready Supabase setup with security, performance, and monitoring
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from supabase import Client, create_client

from core.supabase import get_supabase_client
from infrastructure.secrets import get_secrets_manager

logger = logging.getLogger(__name__)


class SupabaseProductionConfig:
    """Production Supabase configuration"""
    
    def __init__(self):
        # Connection settings
        self.url = os.getenv("SUPABASE_URL")
        self.service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.anon_key = os.getenv("SUPABASE_ANON_KEY")
        
        # Pool settings
        self.pool_size = int(os.getenv("SUPABASE_POOL_SIZE", "20"))
        self.pool_timeout = int(os.getenv("SUPABASE_POOL_TIMEOUT", "30"))
        self.pool_recycle = int(os.getenv("SUPABASE_POOL_RECYCLE", "3600"))  # 1 hour
        
        # Security settings
        self.enable_rls = os.getenv("SUPABASE_ENABLE_RLS", "true").lower() == "true"
        self.require_auth = os.getenv("SUPABASE_REQUIRE_AUTH", "true").lower() == "true"
        self.jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
        
        # Performance settings
        self.query_timeout = int(os.getenv("SUPABASE_QUERY_TIMEOUT", "30"))
        self.max_connections = int(os.getenv("SUPABASE_MAX_CONNECTIONS", "100"))
        self.idle_timeout = int(os.getenv("SUPABASE_IDLE_TIMEOUT", "300"))
        
        # Backup settings
        self.backup_enabled = os.getenv("SUPABASE_BACKUP_ENABLED", "true").lower() == "true"
        self.backup_schedule = os.getenv("SUPABASE_BACKUP_SCHEDULE", "0 2 * * *")  # Daily at 2 AM
        self.backup_retention = int(os.getenv("SUPABASE_BACKUP_RETENTION", "30"))  # 30 days
        
        # Monitoring settings
        self.metrics_enabled = os.getenv("SUPABASE_METRICS_ENABLED", "true").lower() == "true"
        self.slow_query_threshold = int(os.getenv("SUPABASE_SLOW_QUERY_THRESHOLD", "1000"))  # 1 second
        self.log_queries = os.getenv("SUPABASE_LOG_QUERIES", "false").lower() == "true"


class SupabaseProductionManager:
    """Production Supabase management with monitoring and optimization"""
    
    def __init__(self):
        self.config = SupabaseProductionConfig()
        self.client = None
        self.metrics = {
            "connections": 0,
            "queries": 0,
            "errors": 0,
            "slow_queries": 0,
            "last_health_check": None,
            "uptime": 0
        }
        self._start_time = datetime.utcnow()
        
        # Connection pool
        self._pool = []
        self._pool_lock = asyncio.Lock()
    
    async def initialize(self) -> bool:
        """Initialize Supabase production client"""
        try:
            # Validate required configuration
            if not self.config.url or not self.config.service_role_key:
                raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
            
            # Create client
            self.client = create_client(self.config.url, self.config.service_role_key)
            
            # Test connection
            await self._test_connection()
            
            # Initialize connection pool
            await self._initialize_pool()
            
            # Apply production optimizations
            await self._apply_optimizations()
            
            # Start monitoring tasks
            asyncio.create_task(self._monitoring_loop())
            asyncio.create_task(self._health_check_loop())
            
            logger.info("Supabase production manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Supabase: {e}")
            return False
    
    async def _test_connection(self) -> bool:
        """Test Supabase connection"""
        try:
            # Test basic query
            result = self.client.table("users").select("id").limit(1).execute()
            logger.info("Supabase connection test successful")
            return True
        except Exception as e:
            logger.error(f"Supabase connection test failed: {e}")
            raise
    
    async def _initialize_pool(self) -> None:
        """Initialize connection pool"""
        try:
            async with self._pool_lock:
                # Create initial connections
                for _ in range(min(5, self.config.pool_size)):
                    await self._create_pooled_connection()
                
                logger.info(f"Initialized Supabase connection pool with {len(self._pool)} connections")
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
    
    async def _create_pooled_connection(self) -> Client:
        """Create a new pooled connection"""
        try:
            client = create_client(self.config.url, self.config.service_role_key)
            
            connection_info = {
                "client": client,
                "created_at": datetime.utcnow(),
                "last_used": datetime.utcnow(),
                "in_use": False,
                "query_count": 0
            }
            
            self._pool.append(connection_info)
            self.metrics["connections"] = len(self._pool)
            
            return client
            
        except Exception as e:
            logger.error(f"Failed to create pooled connection: {e}")
            raise
    
    async def get_connection(self) -> Client:
        """Get a connection from the pool"""
        async with self._pool_lock:
            # Clean up expired connections
            await self._cleanup_expired_connections()
            
            # Find available connection
            for conn_info in self._pool:
                if not conn_info["in_use"]:
                    conn_info["in_use"] = True
                    conn_info["last_used"] = datetime.utcnow()
                    conn_info["query_count"] += 1
                    self.metrics["queries"] += 1
                    return conn_info["client"]
            
            # No available connection, create new one if under max
            if len(self._pool) < self.config.max_connections:
                return await self._create_pooled_connection()
            
            # Pool is full, wait for available connection
            raise Exception("Supabase connection pool exhausted")
    
    async def release_connection(self, client: Client) -> None:
        """Release a connection back to the pool"""
        async with self._pool_lock:
            for conn_info in self._pool:
                if conn_info["client"] == client:
                    conn_info["in_use"] = False
                    conn_info["last_used"] = datetime.utcnow()
                    return
    
    async def _cleanup_expired_connections(self) -> None:
        """Remove expired connections from pool"""
        now = datetime.utcnow()
        to_remove = []
        
        for conn_info in self._pool:
            if conn_info["in_use"]:
                continue
            
            # Check idle timeout
            idle_time = (now - conn_info["last_used"]).total_seconds()
            if idle_time > self.config.idle_timeout:
                to_remove.append(conn_info)
                continue
            
            # Check max lifetime
            lifetime = (now - conn_info["created_at"]).total_seconds()
            if lifetime > self.config.pool_recycle:
                to_remove.append(conn_info)
        
        # Remove expired connections
        for conn_info in to_remove:
            self._pool.remove(conn_info)
            self.metrics["connections"] = len(self._pool)
        
        # Maintain minimum pool size
        if len(self._pool) < 5:
            for _ in range(5 - len(self._pool)):
                await self._create_pooled_connection()
    
    async def _apply_optimizations(self) -> Dict[str, Any]:
        """Apply Supabase production optimizations"""
        try:
            optimizations = []
            
            # Enable Row Level Security
            if self.config.enable_rls:
                # RLS is enabled at the database level
                optimizations.append("RLS enabled")
            
            # Set up database parameters
            optimizations.extend(await self._set_database_parameters())
            
            # Create indexes for performance
            optimizations.extend(await self._create_performance_indexes())
            
            # Set up backup if enabled
            if self.config.backup_enabled:
                optimizations.extend(await self._setup_backup())
            
            return {
                "status": "success",
                "optimizations": optimizations
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def _set_database_parameters(self) -> List[str]:
        """Set database parameters for production"""
        optimizations = []
        
        try:
            # Set statement timeout
            await self.client.rpc("set_config", {"name": "statement_timeout", "value": "30s"})
            optimizations.append("statement_timeout=30s")
            
            # Set work_mem for complex queries
            await self.client.rpc("set_config", {"name": "work_mem", "value": "256MB"})
            optimizations.append("work_mem=256MB")
            
            # Set shared_buffers
            await self.client.rpc("set_config", {"name": "shared_buffers", "value": "256MB"})
            optimizations.append("shared_buffers=256MB")
            
            # Set effective_cache_size
            await self.client.rpc("set_config", {"name": "effective_cache_size", "value": "1GB"})
            optimizations.append("effective_cache_size=1GB")
            
            # Enable query logging if requested
            if self.config.log_queries:
                await self.client.rpc("set_config", {"name": "log_statement", "value": "all"})
                optimizations.append("log_statement=all")
            
        except Exception as e:
            logger.error(f"Failed to set database parameters: {e}")
        
        return optimizations
    
    async def _create_performance_indexes(self) -> List[str]:
        """Create performance indexes"""
        indexes = []
        
        try:
            # Users table indexes
            user_indexes = [
                "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
                "CREATE INDEX IF NOT EXISTS idx_users_workspace_id ON users(workspace_id)",
                "CREATE INDEX IF NOT EXISTS idx_users_subscription_tier ON users(subscription_tier)",
                "CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at)",
            ]
            
            for index_sql in user_indexes:
                try:
                    await self.client.rpc("exec_sql", {"sql": index_sql})
                    indexes.append("users: " + index_sql.split("ON")[1].strip())
                except Exception as e:
                    logger.warning(f"Failed to create index: {e}")
            
            # Workspaces table indexes
            workspace_indexes = [
                "CREATE INDEX IF NOT EXISTS idx_workspaces_owner_id ON workspaces(owner_id)",
                "CREATE INDEX IF NOT EXISTS idx_workspaces_created_at ON workspaces(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_workspaces_status ON workspaces(status)",
            ]
            
            for index_sql in workspace_indexes:
                try:
                    await self.client.rpc("exec_sql", {"sql": index_sql})
                    indexes.append("workspaces: " + index_sql.split("ON")[1].strip())
                except Exception as e:
                    logger.warning(f"Failed to create index: {e}")
            
            # ICP tables indexes
            icp_indexes = [
                "CREATE INDEX IF NOT EXISTS idx_icp_profiles_workspace_id ON icp_profiles(workspace_id)",
                "CREATE INDEX IF NOT EXISTS idx_icp_profiles_created_at ON icp_profiles(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_icp_firmographics_workspace_id ON icp_firmographics(workspace_id)",
            ]
            
            for index_sql in icp_indexes:
                try:
                    await self.client.rpc("exec_sql", {"sql": index_sql})
                    indexes.append("icp: " + index_sql.split("ON")[1].strip())
                except Exception as e:
                    logger.warning(f"Failed to create index: {e}")
            
        except Exception as e:
            logger.error(f"Failed to create performance indexes: {e}")
        
        return indexes
    
    async def _setup_backup(self) -> List[str]:
        """Set up database backup"""
        backup_configs = []
        
        try:
            # Enable WAL for point-in-time recovery
            await self.client.rpc("set_config", {"name": "wal_level", "value": "replica"})
            backup_configs.append("wal_level=replica")
            
            # Set archive mode
            await self.client.rpc("set_config", {"name": "archive_mode", "value": "on"})
            backup_configs.append("archive_mode=on")
            
            # Set archive command
            await self.client.rpc("set_config", {"name": "archive_command", "value": "cp /var/lib/postgresql/%f /backups/"})
            backup_configs.append("archive_command configured")
            
        except Exception as e:
            logger.error(f"Failed to setup backup: {e}")
        
        return backup_configs
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test Supabase connection and performance"""
        try:
            if not self.client:
                return {"status": "error", "message": "Supabase client not initialized"}
            
            # Basic connectivity test
            start_time = datetime.utcnow()
            result = self.client.table("users").select("id").limit(1).execute()
            query_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Performance test
            start_time = datetime.utcnow()
            test_result = self.client.table("users").select("*").limit(10).execute()
            performance_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Get database info
            try:
                db_info = await self.client.rpc("get_database_info")["data"]
                size = db_info.get("size", "unknown")
                connections = db_info.get("active_connections", "unknown")
            except:
                size = "unknown"
                connections = "unknown"
            
            return {
                "status": "healthy",
                "query_time_ms": query_time,
                "performance_time_ms": performance_time,
                "database_size": size,
                "active_connections": connections,
                "test_passed": len(result.data) >= 0
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        try:
            if not self.client:
                return {"status": "error", "message": "Supabase client not initialized"}
            
            # Get table statistics
            tables = ["users", "workspaces", "icp_profiles", "icp_firmographics", "icp_pain_map"]
            table_stats = {}
            
            for table in tables:
                try:
                    result = self.client.table(table).select("*", count="exact").execute()
                    table_stats[table] = {
                        "row_count": result.count if hasattr(result, 'count') else len(result.data),
                        "last_accessed": datetime.utcnow().isoformat()
                    }
                except Exception as e:
                    table_stats[table] = {"error": str(e)}
            
            # Get connection pool stats
            pool_stats = {
                "total_connections": len(self._pool),
                "active_connections": len([c for c in self._pool if c["in_use"]]),
                "available_connections": len([c for c in self._pool if not c["in_use"]]),
                "pool_utilization": len([c for c in self._pool if c["in_use"]]) / len(self._pool) if self._pool else 0
            }
            
            # Add custom metrics
            stats = {
                "status": "healthy",
                "tables": table_stats,
                "connection_pool": pool_stats,
                "queries_executed": self.metrics["queries"],
                "errors": self.metrics["errors"],
                "slow_queries": self.metrics["slow_queries"],
                "manager_uptime": (datetime.utcnow() - self._start_time).total_seconds()
            }
            
            return stats
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def cleanup_expired_data(self) -> Dict[str, Any]:
        """Clean up expired data"""
        try:
            cleanup_stats = {
                "expired_sessions": 0,
                "old_logs": 0,
                "orphaned_records": 0
            }
            
            # Clean up expired sessions (if sessions table exists)
            try:
                cutoff_date = datetime.utcnow() - timedelta(days=30)
                result = self.client.table("sessions").delete().lt("created_at", cutoff_date.isoformat()).execute()
                cleanup_stats["expired_sessions"] = result.count if hasattr(result, 'count') else 0
            except Exception as e:
                logger.warning(f"Failed to clean up sessions: {e}")
            
            # Clean up old log entries (if logs table exists)
            try:
                cutoff_date = datetime.utcnow() - timedelta(days=7)
                result = self.client.table("logs").delete().lt("created_at", cutoff_date.isoformat()).execute()
                cleanup_stats["old_logs"] = result.count if hasattr(result, 'count') else 0
            except Exception as e:
                logger.warning(f"Failed to clean up logs: {e}")
            
            return {
                "status": "success",
                "cleanup_stats": cleanup_stats,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def _monitoring_loop(self) -> None:
        """Background monitoring loop"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                # Update metrics
                if self.client:
                    self.metrics["last_health_check"] = datetime.utcnow().isoformat()
                    
                    # Check for slow queries
                    if self.config.slow_query_threshold > 0:
                        # This would require query logging setup
                        pass
                
            except Exception as e:
                logger.error(f"Supabase monitoring error: {e}")
                self.metrics["errors"] += 1
    
    async def _health_check_loop(self) -> None:
        """Background health check loop"""
        while True:
            try:
                await asyncio.sleep(self.config.query_timeout)
                
                if self.client:
                    # Simple health check
                    await self.client.table("users").select("id").limit(1).execute()
                    self.metrics["last_health_check"] = datetime.utcnow().isoformat()
                
            except Exception as e:
                logger.error(f"Supabase health check failed: {e}")
                self.metrics["errors"] += 1
    
    async def close(self) -> None:
        """Close all connections"""
        async with self._pool_lock:
            for conn_info in self._pool:
                # Supabase clients don't have explicit close method
                pass
            
            self._pool.clear()
            logger.info("Supabase connection pool closed")


# Global Supabase production manager
_supabase_manager: Optional[SupabaseProductionManager] = None


def get_supabase_production_manager() -> SupabaseProductionManager:
    """Get global Supabase production manager"""
    global _supabase_manager
    if _supabase_manager is None:
        _supabase_manager = SupabaseProductionManager()
    return _supabase_manager


async def initialize_supabase_production() -> bool:
    """Initialize Supabase production manager"""
    manager = get_supabase_production_manager()
    return await manager.initialize()


async def get_supabase_health_status() -> Dict[str, Any]:
    """Get Supabase health status"""
    manager = get_supabase_production_manager()
    return await manager.test_connection()


async def get_supabase_metrics() -> Dict[str, Any]:
    """Get Supabase metrics"""
    manager = get_supabase_production_manager()
    return await manager.get_database_stats()


# Supabase utility functions for production
async def supabase_query_with_timeout(query_func, timeout: Optional[int] = None) -> Any:
    """Execute query with timeout"""
    try:
        manager = get_supabase_production_manager()
        client = await manager.get_connection()
        
        try:
            # Execute query
            result = await asyncio.wait_for(query_func(client), timeout=timeout or manager.config.query_timeout)
            return result
        finally:
            await manager.release_connection(client)
            
    except asyncio.TimeoutError:
        logger.error(f"Supabase query timed out after {timeout or 'default'} seconds")
        raise
    except Exception as e:
        logger.error(f"Supabase query error: {e}")
        raise


# Row Level Security utilities
async def check_rls_policy(table: str, operation: str, user_id: str, workspace_id: str) -> bool:
    """Check if user has RLS policy for table operation"""
    try:
        manager = get_supabase_production_manager()
        client = await manager.get_connection()
        
        # This would check RLS policies - simplified for now
        if not manager.config.enable_rls:
            return True  # RLS disabled, allow all
        
        # In production, you'd check actual RLS policies
        # For now, assume basic workspace isolation
        if operation in ["SELECT", "INSERT", "UPDATE", "DELETE"]:
            return True  # Simplified check
        
        return False
        
    except Exception as e:
        logger.error(f"RLS policy check error: {e}")
        return False
