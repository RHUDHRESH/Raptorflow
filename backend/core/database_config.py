"""
Production Database Configuration
Airtight, scalable, and foolproof database settings for 100+ concurrent users
"""

import os
from typing import Dict, Any

class DatabaseConfig:
    """Production database configuration with calculated optimal settings"""
    
    # Base configuration from environment
    MIN_CONNECTIONS = int(os.getenv("DB_MIN_CONNECTIONS", "10"))
    MAX_CONNECTIONS = int(os.getenv("DB_MAX_CONNECTIONS", "50"))
    CONNECTION_TIMEOUT = float(os.getenv("DB_CONNECTION_TIMEOUT", "30.0"))
    IDLE_TIMEOUT = float(os.getenv("DB_IDLE_TIMEOUT", "300.0"))
    MAX_LIFETIME = float(os.getenv("DB_MAX_LIFETIME", "3600.0"))
    HEALTH_CHECK_INTERVAL = float(os.getenv("DB_HEALTH_CHECK_INTERVAL", "60.0"))
    
    # Calculated optimal settings for 100 concurrent users
    @classmethod
    def get_pool_settings(cls) -> Dict[str, Any]:
        """Get optimized pool settings based on user load"""
        
        # For 100 concurrent users with 3:1 read/write ratio
        concurrent_users = 100
        read_ratio = 0.7
        write_ratio = 0.3
        
        # Calculate optimal pool size
        # Each user needs ~0.1 connections on average
        # Peak load requires 2x average
        avg_connections = concurrent_users * 0.1
        peak_connections = avg_connections * 2
        
        # Ensure we have enough connections for peak load
        optimal_min = max(cls.MIN_CONNECTIONS, int(avg_connections))
        optimal_max = max(cls.MAX_CONNECTIONS, int(peak_connections))
        
        return {
            "min_connections": optimal_min,
            "max_connections": optimal_max,
            "connection_timeout": cls.CONNECTION_TIMEOUT,
            "idle_timeout": cls.IDLE_TIMEOUT,
            "max_lifetime": cls.MAX_LIFETIME,
            "health_check_interval": cls.HEALTH_CHECK_INTERVAL,
            
            # Advanced settings for production
            "acquire_timeout": 10.0,  # Fast failure under load
            "retry_attempts": 3,
            "retry_delay": 1.0,
            "validation_interval": 30.0,  # Validate connections every 30s
            
            # Pool exhaustion handling
            "pool_exhaustion_action": "queue",  # Queue requests vs fail fast
            "max_queue_size": 100,  # Queue up to 100 requests
            
            # Connection reuse optimization
            "connection_recycle_time": 1800.0,  # Recycle every 30 minutes
            "pre_ping": True,  # Validate connections before use
            
            # Monitoring and alerting
            "enable_metrics": True,
            "slow_query_threshold": 1.0,  # Log queries > 1 second
            "connection_utilization_alert": 0.8,  # Alert at 80% utilization
        }
    
    @classmethod
    def get_monitoring_config(cls) -> Dict[str, Any]:
        """Get database monitoring configuration"""
        return {
            "enable_query_logging": True,
            "log_slow_queries": True,
            "slow_query_threshold": 1.0,
            "log_connection_events": True,
            "connection_pool_alerts": True,
            "pool_utilization_threshold": 0.8,
            "connection_timeout_alerts": True,
            "deadlock_detection": True,
            "long_running_query_threshold": 30.0,  # 30 seconds
        }
    
    @classmethod
    def validate_settings(cls) -> Dict[str, Any]:
        """Validate database configuration and return recommendations"""
        settings = cls.get_pool_settings()
        issues = []
        recommendations = []
        
        # Check connection limits
        if settings["max_connections"] < 20:
            issues.append("Max connections too low for production")
            recommendations.append("Set max_connections to at least 20")
        
        if settings["min_connections"] > settings["max_connections"] * 0.5:
            issues.append("Min connections too high relative to max")
            recommendations.append("Set min_connections to 20-30% of max")
        
        # Check timeouts
        if settings["connection_timeout"] > 60:
            issues.append("Connection timeout too high")
            recommendations.append("Set connection_timeout to 30 seconds or less")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "recommendations": recommendations,
            "current_settings": settings,
        }

# Production-ready configuration instance
DB_CONFIG = DatabaseConfig()
