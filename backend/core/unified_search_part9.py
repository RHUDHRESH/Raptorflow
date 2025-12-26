"""
Part 9: Configuration and Settings Management
RaptorFlow Unified Search System - Industrial Grade AI Agent Search Infrastructure
===============================================================================
This module implements comprehensive configuration management, settings validation,
and dynamic configuration updates for the unified search system.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional, Set, Union, Type
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
import yaml

from backend.core.unified_search_part1 import SearchProvider, SearchMode, ContentType

logger = logging.getLogger("raptorflow.unified_search.config")


class ConfigFormat(Enum):
    """Supported configuration file formats."""
    JSON = "json"
    YAML = "yaml"
    ENV = "env"


@dataclass
class ProviderConfig:
    """Configuration for a search provider."""
    enabled: bool = True
    priority: int = 1
    timeout_seconds: int = 30
    max_concurrent_requests: int = 5
    rate_limit_requests_per_second: float = 2.0
    retry_attempts: int = 3
    retry_delay_seconds: float = 1.0
    api_key: Optional[str] = None
    api_endpoint: Optional[str] = None
    custom_headers: Dict[str, str] = field(default_factory=dict)
    custom_params: Dict[str, Any] = field(default_factory=dict)
    health_check_enabled: bool = True
    health_check_interval_seconds: int = 60
    
    def validate(self) -> List[str]:
        """Validate provider configuration."""
        errors = []
        
        if self.timeout_seconds <= 0:
            errors.append("timeout_seconds must be positive")
        
        if self.max_concurrent_requests <= 0:
            errors.append("max_concurrent_requests must be positive")
        
        if self.rate_limit_requests_per_second <= 0:
            errors.append("rate_limit_requests_per_second must be positive")
        
        if self.retry_attempts < 0:
            errors.append("retry_attempts cannot be negative")
        
        if self.retry_delay_seconds < 0:
            errors.append("retry_delay_seconds cannot be negative")
        
        if self.health_check_interval_seconds <= 0:
            errors.append("health_check_interval_seconds must be positive")
        
        return errors


@dataclass
class CacheConfig:
    """Configuration for caching system."""
    enabled: bool = True
    max_size: int = 10000
    ttl_hours: int = 24
    cleanup_interval_minutes: int = 60
    cache_directory: Optional[str] = None
    persistent_cache: bool = False
    compression_enabled: bool = True
    memory_limit_mb: int = 512
    
    def validate(self) -> List[str]:
        """Validate cache configuration."""
        errors = []
        
        if self.max_size <= 0:
            errors.append("cache max_size must be positive")
        
        if self.ttl_hours <= 0:
            errors.append("cache ttl_hours must be positive")
        
        if self.cleanup_interval_minutes <= 0:
            errors.append("cache cleanup_interval_minutes must be positive")
        
        if self.memory_limit_mb <= 0:
            errors.append("cache memory_limit_mb must be positive")
        
        return errors


@dataclass
class CrawlerConfig:
    """Configuration for web crawler."""
    enabled: bool = True
    max_concurrent: int = 5
    timeout_seconds: int = 30
    max_content_length: int = 50000
    min_content_length: int = 100
    max_depth: int = 3
    follow_redirects: bool = True
    respect_robots_txt: bool = True
    user_agent: str = "RaptorFlowResearch/3.0"
    allowed_mime_types: Set[str] = field(default_factory=lambda: {
        "text/html", "text/plain", "application/xhtml+xml",
        "text/xml", "application/xml", "application/json"
    })
    blocked_mime_types: Set[str] = field(default_factory=lambda: {
        "application/pdf", "application/zip", "application/octet-stream",
        "image/jpeg", "image/png", "image/gif", "video/mp4"
    })
    blocked_domains: Set[str] = field(default_factory=set)
    allowed_domains: Set[str] = field(default_factory=set)
    blocked_patterns: List[str] = field(default_factory=lambda: [
        r".*\.pdf$", r".*\.zip$", r".*\.exe$", r".*\.dmg$",
        r".*/login.*", r".*/signup.*", r".*/cart.*", r".*/checkout.*"
    ])
    rate_limit_delay: float = 1.0
    retry_attempts: int = 3
    retry_delay: float = 2.0
    enable_js_rendering: bool = True
    extract_images: bool = False
    extract_links: bool = True
    extract_metadata: bool = True
    
    def validate(self) -> List[str]:
        """Validate crawler configuration."""
        errors = []
        
        if self.max_concurrent <= 0:
            errors.append("crawler max_concurrent must be positive")
        
        if self.timeout_seconds <= 0:
            errors.append("crawler timeout_seconds must be positive")
        
        if self.max_content_length <= 0:
            errors.append("crawler max_content_length must be positive")
        
        if self.min_content_length < 0:
            errors.append("crawler min_content_length cannot be negative")
        
        if self.max_depth <= 0:
            errors.append("crawler max_depth must be positive")
        
        if self.rate_limit_delay < 0:
            errors.append("crawler rate_limit_delay cannot be negative")
        
        if self.retry_attempts < 0:
            errors.append("crawler retry_attempts cannot be negative")
        
        if self.retry_delay < 0:
            errors.append("crawler retry_delay cannot be negative")
        
        return errors


@dataclass
class ResearchConfig:
    """Configuration for deep research agent."""
    enabled: bool = True
    max_sources_per_research: int = 50
    default_time_limit_minutes: int = 60
    verification_enabled: bool = True
    quality_threshold: float = 0.6
    synthesis_formats: List[str] = field(default_factory=lambda: ["summary", "detailed", "comprehensive"])
    default_depth: str = "moderate"
    max_concurrent_research: int = 3
    cache_research_results: bool = True
    research_ttl_hours: int = 168  # 1 week
    
    def validate(self) -> List[str]:
        """Validate research configuration."""
        errors = []
        
        if self.max_sources_per_research <= 0:
            errors.append("research max_sources_per_research must be positive")
        
        if self.default_time_limit_minutes <= 0:
            errors.append("research default_time_limit_minutes must be positive")
        
        if self.quality_threshold < 0 or self.quality_threshold > 1:
            errors.append("research quality_threshold must be between 0 and 1")
        
        if self.max_concurrent_research <= 0:
            errors.append("research max_concurrent_research must be positive")
        
        if self.research_ttl_hours <= 0:
            errors.append("research research_ttl_hours must be positive")
        
        return errors


@dataclass
class MonitoringConfig:
    """Configuration for monitoring and analytics."""
    enabled: bool = True
    metrics_retention_hours: int = 168  # 1 week
    performance_tracking: bool = True
    system_monitoring: bool = True
    monitoring_interval_seconds: int = 30
    analytics_enabled: bool = True
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        'error_rate': 0.1,  # 10%
        'avg_response_time_ms': 5000,
        'cpu_usage_percent': 80,
        'memory_usage_percent': 85,
        'disk_usage_percent': 90
    })
    notification_webhooks: List[str] = field(default_factory=list)
    
    def validate(self) -> List[str]:
        """Validate monitoring configuration."""
        errors = []
        
        if self.metrics_retention_hours <= 0:
            errors.append("monitoring metrics_retention_hours must be positive")
        
        if self.monitoring_interval_seconds <= 0:
            errors.append("monitoring monitoring_interval_seconds must be positive")
        
        for threshold_name, threshold_value in self.alert_thresholds.items():
            if threshold_value < 0 or threshold_value > 100:
                errors.append(f"monitoring alert_threshold {threshold_name} must be between 0 and 100")
        
        return errors


@dataclass
class UnifiedSearchConfig:
    """Main configuration for the unified search system."""
    # System settings
    system_name: str = "RaptorFlow Unified Search"
    version: str = "3.0.0"
    environment: str = "production"
    debug: bool = False
    log_level: str = "INFO"
    
    # Provider configurations
    providers: Dict[str, ProviderConfig] = field(default_factory=dict)
    
    # Feature configurations
    cache: CacheConfig = field(default_factory=CacheConfig)
    crawler: CrawlerConfig = field(default_factory=CrawlerConfig)
    research: ResearchConfig = field(default_factory=ResearchConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    # Global settings
    max_total_results: int = 100
    default_search_mode: str = "standard"
    default_language: str = "en"
    default_region: str = "us"
    safe_search_default: bool = True
    
    # Security settings
    api_key_required: bool = False
    rate_limit_global: float = 100.0  # requests per second
    cors_enabled: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    
    # Performance settings
    connection_pool_size: int = 100
    request_timeout_seconds: int = 30
    max_concurrent_searches: int = 50
    
    def validate(self) -> List[str]:
        """Validate entire configuration."""
        errors = []
        
        # Validate system settings
        if self.max_total_results <= 0:
            errors.append("max_total_results must be positive")
        
        if self.rate_limit_global <= 0:
            errors.append("rate_limit_global must be positive")
        
        if self.connection_pool_size <= 0:
            errors.append("connection_pool_size must be positive")
        
        if self.request_timeout_seconds <= 0:
            errors.append("request_timeout_seconds must be positive")
        
        if self.max_concurrent_searches <= 0:
            errors.append("max_concurrent_searches must be positive")
        
        # Validate provider configurations
        for provider_name, provider_config in self.providers.items():
            provider_errors = provider_config.validate()
            for error in provider_errors:
                errors.append(f"provider {provider_name}: {error}")
        
        # Validate feature configurations
        cache_errors = self.cache.validate()
        for error in cache_errors:
            errors.append(f"cache: {error}")
        
        crawler_errors = self.crawler.validate()
        for error in crawler_errors:
            errors.append(f"crawler: {error}")
        
        research_errors = self.research.validate()
        for error in research_errors:
            errors.append(f"research: {error}")
        
        monitoring_errors = self.monitoring.validate()
        for error in monitoring_errors:
            errors.append(f"monitoring: {error}")
        
        return errors


class ConfigManager:
    """Manages configuration loading, validation, and updates."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.config: UnifiedSearchConfig = UnifiedSearchConfig()
        self._last_modified: Optional[datetime] = None
        self._watchers: List[callable] = []
        
    def _get_default_config_path(self) -> str:
        """Get default configuration file path."""
        # Try multiple locations
        possible_paths = [
            "unified_search_config.json",
            "unified_search_config.yaml",
            "config/unified_search.json",
            "config/unified_search.yaml",
            os.path.expanduser("~/.raptorflow/unified_search.json"),
            "/etc/raptorflow/unified_search.json"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Return default path (may not exist)
        return "unified_search_config.json"
    
    async def load_config(self, config_path: Optional[str] = None) -> UnifiedSearchConfig:
        """Load configuration from file."""
        path = config_path or self.config_path
        
        if not os.path.exists(path):
            logger.warning(f"Configuration file not found: {path}. Using defaults.")
            self.config = UnifiedSearchConfig()
            return self.config
        
        try:
            # Determine file format
            file_format = self._detect_format(path)
            
            # Load raw configuration
            raw_config = await self._load_raw_config(path, file_format)
            
            # Convert to configuration object
            self.config = self._parse_config(raw_config)
            
            # Validate configuration
            errors = self.config.validate()
            if errors:
                logger.error(f"Configuration validation failed: {errors}")
                raise ValueError(f"Invalid configuration: {errors}")
            
            # Update last modified time
            self._last_modified = datetime.fromtimestamp(os.path.getmtime(path))
            
            logger.info(f"Configuration loaded from: {path}")
            return self.config
            
        except Exception as e:
            logger.error(f"Failed to load configuration from {path}: {e}")
            raise
    
    def _detect_format(self, file_path: str) -> ConfigFormat:
        """Detect configuration file format."""
        extension = Path(file_path).suffix.lower()
        
        if extension in ['.json']:
            return ConfigFormat.JSON
        elif extension in ['.yaml', '.yml']:
            return ConfigFormat.YAML
        else:
            # Default to JSON
            return ConfigFormat.JSON
    
    async def _load_raw_config(self, file_path: str, format: ConfigFormat) -> Dict[str, Any]:
        """Load raw configuration from file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            if format == ConfigFormat.JSON:
                return json.load(f)
            elif format == ConfigFormat.YAML:
                return yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported configuration format: {format}")
    
    def _parse_config(self, raw_config: Dict[str, Any]) -> UnifiedSearchConfig:
        """Parse raw configuration into configuration object."""
        # Create base configuration
        config = UnifiedSearchConfig()
        
        # Update system settings
        if 'system' in raw_config:
            system_config = raw_config['system']
            config.system_name = system_config.get('name', config.system_name)
            config.version = system_config.get('version', config.version)
            config.environment = system_config.get('environment', config.environment)
            config.debug = system_config.get('debug', config.debug)
            config.log_level = system_config.get('log_level', config.log_level)
        
        # Update provider configurations
        if 'providers' in raw_config:
            config.providers = {}
            for provider_name, provider_data in raw_config['providers'].items():
                config.providers[provider_name] = ProviderConfig(**provider_data)
        
        # Update feature configurations
        if 'cache' in raw_config:
            config.cache = CacheConfig(**raw_config['cache'])
        
        if 'crawler' in raw_config:
            config.crawler = CrawlerConfig(**raw_config['crawler'])
        
        if 'research' in raw_config:
            config.research = ResearchConfig(**raw_config['research'])
        
        if 'monitoring' in raw_config:
            config.monitoring = MonitoringConfig(**raw_config['monitoring'])
        
        # Update global settings
        if 'global' in raw_config:
            global_config = raw_config['global']
            config.max_total_results = global_config.get('max_total_results', config.max_total_results)
            config.default_search_mode = global_config.get('default_search_mode', config.default_search_mode)
            config.default_language = global_config.get('default_language', config.default_language)
            config.default_region = global_config.get('default_region', config.default_region)
            config.safe_search_default = global_config.get('safe_search_default', config.safe_search_default)
        
        # Update security settings
        if 'security' in raw_config:
            security_config = raw_config['security']
            config.api_key_required = security_config.get('api_key_required', config.api_key_required)
            config.rate_limit_global = security_config.get('rate_limit_global', config.rate_limit_global)
            config.cors_enabled = security_config.get('cors_enabled', config.cors_enabled)
            config.cors_origins = security_config.get('cors_origins', config.cors_origins)
        
        # Update performance settings
        if 'performance' in raw_config:
            performance_config = raw_config['performance']
            config.connection_pool_size = performance_config.get('connection_pool_size', config.connection_pool_size)
            config.request_timeout_seconds = performance_config.get('request_timeout_seconds', config.request_timeout_seconds)
            config.max_concurrent_searches = performance_config.get('max_concurrent_searches', config.max_concurrent_searches)
        
        return config
    
    async def save_config(self, config_path: Optional[str] = None, format: ConfigFormat = ConfigFormat.JSON) -> bool:
        """Save current configuration to file."""
        path = config_path or self.config_path
        
        try:
            # Convert configuration to dictionary
            raw_config = self._serialize_config()
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # Save to file
            with open(path, 'w', encoding='utf-8') as f:
                if format == ConfigFormat.JSON:
                    json.dump(raw_config, f, indent=2, default=str)
                elif format == ConfigFormat.YAML:
                    yaml.dump(raw_config, f, default_flow_style=False)
                else:
                    raise ValueError(f"Unsupported format: {format}")
            
            logger.info(f"Configuration saved to: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration to {path}: {e}")
            return False
    
    def _serialize_config(self) -> Dict[str, Any]:
        """Serialize configuration to dictionary."""
        return {
            'system': {
                'name': self.config.system_name,
                'version': self.config.version,
                'environment': self.config.environment,
                'debug': self.config.debug,
                'log_level': self.config.log_level
            },
            'providers': {
                name: asdict(provider_config) 
                for name, provider_config in self.config.providers.items()
            },
            'cache': asdict(self.config.cache),
            'crawler': asdict(self.config.crawler),
            'research': asdict(self.config.research),
            'monitoring': asdict(self.config.monitoring),
            'global': {
                'max_total_results': self.config.max_total_results,
                'default_search_mode': self.config.default_search_mode,
                'default_language': self.config.default_language,
                'default_region': self.config.default_region,
                'safe_search_default': self.config.safe_search_default
            },
            'security': {
                'api_key_required': self.config.api_key_required,
                'rate_limit_global': self.config.rate_limit_global,
                'cors_enabled': self.config.cors_enabled,
                'cors_origins': self.config.cors_origins
            },
            'performance': {
                'connection_pool_size': self.config.connection_pool_size,
                'request_timeout_seconds': self.config.request_timeout_seconds,
                'max_concurrent_searches': self.config.max_concurrent_searches
            }
        }
    
    async def reload_config(self) -> bool:
        """Reload configuration from file."""
        try:
            await self.load_config()
            await self._notify_watchers()
            return True
        except Exception as e:
            logger.error(f"Failed to reload configuration: {e}")
            return False
    
    def add_watcher(self, callback: callable):
        """Add configuration change watcher."""
        self._watchers.append(callback)
    
    def remove_watcher(self, callback: callable):
        """Remove configuration change watcher."""
        if callback in self._watchers:
            self._watchers.remove(callback)
    
    async def _notify_watchers(self):
        """Notify all watchers of configuration change."""
        for watcher in self._watchers:
            try:
                if asyncio.iscoroutinefunction(watcher):
                    await watcher(self.config)
                else:
                    watcher(self.config)
            except Exception as e:
                logger.error(f"Configuration watcher failed: {e}")
    
    def get_provider_config(self, provider: Union[str, SearchProvider]) -> Optional[ProviderConfig]:
        """Get configuration for specific provider."""
        provider_name = provider.value if isinstance(provider, SearchProvider) else provider
        return self.config.providers.get(provider_name)
    
    def update_provider_config(self, provider: Union[str, SearchProvider], config: ProviderConfig):
        """Update configuration for specific provider."""
        provider_name = provider.value if isinstance(provider, SearchProvider) else provider
        self.config.providers[provider_name] = config
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary."""
        return {
            'system_name': self.config.system_name,
            'version': self.config.version,
            'environment': self.config.environment,
            'enabled_providers': [
                name for name, config in self.config.providers.items() 
                if config.enabled
            ],
            'features': {
                'cache_enabled': self.config.cache.enabled,
                'crawler_enabled': self.config.crawler.enabled,
                'research_enabled': self.config.research.enabled,
                'monitoring_enabled': self.config.monitoring.enabled
            },
            'limits': {
                'max_total_results': self.config.max_total_results,
                'max_concurrent_searches': self.config.max_concurrent_searches,
                'rate_limit_global': self.config.rate_limit_global
            }
        }


# Global configuration manager
config_manager = ConfigManager()
