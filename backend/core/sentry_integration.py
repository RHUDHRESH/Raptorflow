"""
Comprehensive Sentry Integration Manager for Raptorflow Backend
============================================================

Enterprise-grade Sentry SDK integration with advanced error tracking,
performance monitoring, and production observability capabilities.

Features:
- SDK initialization and configuration management
- Environment-aware settings
- Health checks and status monitoring
- Graceful degradation and fallback handling
- Integration with existing monitoring systems
"""

import os
import sys
import json
import time
import logging
import threading
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from contextlib import contextmanager
import traceback
from datetime import datetime, timezone

try:
    import sentry_sdk
    from sentry_sdk import (
        configure_scope,
        set_tag,
        set_context,
        add_breadcrumb,
        capture_exception,
        capture_message,
        flush,
        last_event_id,
        get_current_span,
        start_span,
        continue_trace,
    )
    from sentry_sdk.integrations import (
        Integration,
        redis,
        sqlalchemy,
        httpx,
        aiohttp,
        fastapi,
        celery,
        logging as sentry_logging,
        threading as sentry_threading,
        atexit as sentry_atexit,
        modules as sentry_modules,
        stdlib as sentry_stdlib,
    )
    from sentry_sdk.tracing import Span, Transaction
    from sentry_sdk.utils import Dsn
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    sentry_sdk = None

from ..config_simple import get_config


class SentryEnvironment(str, Enum):
    """Sentry environment types."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class SentryLogLevel(str, Enum):
    """Sentry log levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    FATAL = "fatal"


@dataclass
class SentryConfig:
    """Sentry configuration settings."""
    dsn: Optional[str] = None
    environment: SentryEnvironment = SentryEnvironment.DEVELOPMENT
    release: Optional[str] = None
    dist: Optional[str] = None
    server_name: Optional[str] = None
    sample_rate: float = 1.0
    traces_sample_rate: float = 0.1
    profiles_sample_rate: float = 0.1
    debug: bool = False
    max_breadcrumbs: int = 100
    attach_stacktrace: bool = True
    send_default_pii: bool = False
    send_request_payloads: bool = True
    send_response_payloads: bool = True
    before_send: Optional[Callable] = None
    before_breadcrumb: Optional[Callable] = None
    ignore_errors: List[type] = field(default_factory=list)
    in_app_exclude: List[str] = field(default_factory=list)
    in_app_include: List[str] = field(default_factory=list)
    request_bodies: str = "medium"  # never, small, medium, always
    custom_integrations: List[Integration] = field(default_factory=list)


@dataclass
class SentryHealthStatus:
    """Sentry integration health status."""
    is_healthy: bool = False
    is_configured: bool = False
    is_enabled: bool = False
    last_check: Optional[datetime] = None
    error_count: int = 0
    last_error: Optional[str] = None
    configuration_issues: List[str] = field(default_factory=list)
    integration_status: Dict[str, bool] = field(default_factory=dict)


class SentryIntegrationManager:
    """
    Comprehensive Sentry SDK integration manager.
    
    Handles SDK initialization, configuration management, health monitoring,
    and provides a unified interface for all Sentry operations.
    """
    
    def __init__(self, config: Optional[SentryConfig] = None):
        self.config = config or self._load_config_from_env()
        self.health_status = SentryHealthStatus()
        self.is_initialized = False
        self._lock = threading.Lock()
        self._logger = logging.getLogger(__name__)
        
        # Initialize if configuration is valid
        if self._validate_config():
            self._initialize_sdk()
    
    def _load_config_from_env(self) -> SentryConfig:
        """Load Sentry configuration from environment variables."""
        config = get_config()
        
        # Extract Sentry DSN from environment
        sentry_dsn = os.getenv('SENTRY_DSN') or os.getenv('SENTRY_DSN_URL')
        
        return SentryConfig(
            dsn=sentry_dsn,
            environment=self._determine_environment(),
            release=self._get_release_info(),
            server_name=self._get_server_name(),
            sample_rate=float(os.getenv('SENTRY_SAMPLE_RATE', '1.0')),
            traces_sample_rate=float(os.getenv('SENTRY_TRACES_SAMPLE_RATE', '0.1')),
            profiles_sample_rate=float(os.getenv('SENTRY_PROFILES_SAMPLE_RATE', '0.1')),
            debug=config.debug or os.getenv('SENTRY_DEBUG', 'false').lower() == 'true',
            max_breadcrumbs=int(os.getenv('SENTRY_MAX_BREADCRUMBS', '100')),
            attach_stacktrace=os.getenv('SENTRY_ATTACH_STACKTRACE', 'true').lower() == 'true',
            send_default_pii=os.getenv('SENTRY_SEND_DEFAULT_PII', 'false').lower() == 'true',
            send_request_payloads=os.getenv('SENTRY_SEND_REQUEST_PAYLOADS', 'true').lower() == 'true',
            send_response_payloads=os.getenv('SENTRY_SEND_RESPONSE_PAYLOADS', 'true').lower() == 'true',
            request_bodies=os.getenv('SENTRY_REQUEST_BODIES', 'medium'),
        )
    
    def _determine_environment(self) -> SentryEnvironment:
        """Determine Sentry environment from application configuration."""
        config = get_config()
        
        if config.is_production():
            return SentryEnvironment.PRODUCTION
        
        env = os.getenv('ENVIRONMENT', 'development').lower()
        env_mapping = {
            'development': SentryEnvironment.DEVELOPMENT,
            'testing': SentryEnvironment.TESTING,
            'staging': SentryEnvironment.STAGING,
            'production': SentryEnvironment.PRODUCTION,
        }
        
        return env_mapping.get(env, SentryEnvironment.DEVELOPMENT)
    
    def _get_release_info(self) -> Optional[str]:
        """Get release information from various sources."""
        # Try environment variable first
        release = os.getenv('SENTRY_RELEASE')
        if release:
            return release
        
        # Try git information
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'describe', '--tags', '--always'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Try package version
        try:
            from importlib.metadata import version
            return version('raptorflow-backend')
        except ImportError:
            pass
        
        # Fallback to timestamp
        return f"raptorflow-{int(time.time())}"
    
    def _get_server_name(self) -> Optional[str]:
        """Get server name for Sentry identification."""
        # Try environment variable
        server_name = os.getenv('SENTRY_SERVER_NAME')
        if server_name:
            return server_name
        
        # Try hostname
        try:
            import socket
            return socket.gethostname()
        except Exception:
            return None
    
    def _validate_config(self) -> bool:
        """Validate Sentry configuration."""
        issues = []
        
        if not SENTRY_AVAILABLE:
            issues.append("Sentry SDK not installed")
        
        if not self.config.dsn:
            issues.append("No Sentry DSN configured")
        
        # Validate sample rates
        if not 0 <= self.config.sample_rate <= 1:
            issues.append("Sample rate must be between 0 and 1")
        
        if not 0 <= self.config.traces_sample_rate <= 1:
            issues.append("Traces sample rate must be between 0 and 1")
        
        if not 0 <= self.config.profiles_sample_rate <= 1:
            issues.append("Profiles sample rate must be between 0 and 1")
        
        self.health_status.configuration_issues = issues
        self.health_status.is_configured = len(issues) == 0
        
        return len(issues) == 0
    
    def _initialize_sdk(self) -> bool:
        """Initialize Sentry SDK with configuration."""
        if not SENTRY_AVAILABLE or self.is_initialized:
            return False
        
        try:
            with self._lock:
                if self.is_initialized:
                    return True
                
                # Prepare integrations
                integrations = self._prepare_integrations()
                
                # Configure SDK
                sentry_config = {
                    'dsn': self.config.dsn,
                    'environment': self.config.environment.value,
                    'release': self.config.release,
                    'dist': self.config.dist,
                    'server_name': self.config.server_name,
                    'sample_rate': self.config.sample_rate,
                    'traces_sample_rate': self.config.traces_sample_rate,
                    'profiles_sample_rate': self.config.profiles_sample_rate,
                    'debug': self.config.debug,
                    'max_breadcrumbs': self.config.max_breadcrumbs,
                    'attach_stacktrace': self.config.attach_stacktrace,
                    'send_default_pii': self.config.send_default_pii,
                    'send_request_payloads': self.config.send_request_payloads,
                    'send_response_payloads': self.config.send_response_payloads,
                    'request_bodies': self.config.request_bodies,
                    'ignore_errors': self.config.ignore_errors,
                    'in_app_exclude': self.config.in_app_exclude,
                    'in_app_include': self.config.in_app_include,
                    'integrations': integrations,
                    'before_send': self._before_send_handler,
                    'before_breadcrumb': self._before_breadcrumb_handler,
                }
                
                # Remove None values
                sentry_config = {k: v for k, v in sentry_config.items() if v is not None}
                
                # Initialize SDK
                sentry_sdk.init(**sentry_config)
                
                self.is_initialized = True
                self.health_status.is_healthy = True
                self.health_status.is_enabled = True
                self.health_status.last_check = datetime.now(timezone.utc)
                
                self._logger.info(f"Sentry SDK initialized successfully in {self.config.environment.value}")
                self._set_initial_tags()
                
                return True
                
        except Exception as e:
            self.health_status.is_healthy = False
            self.health_status.last_error = str(e)
            self.health_status.error_count += 1
            self._logger.error(f"Failed to initialize Sentry SDK: {e}")
            return False
    
    def _prepare_integrations(self) -> List[Integration]:
        """Prepare Sentry integrations based on available dependencies."""
        integrations = []
        
        try:
            # Core integrations
            integrations.extend([
                sentry_logging.LoggingIntegration(
                    level=logging.INFO,
                    event_level=logging.WARNING
                ),
                sentry_threading.ThreadingIntegration(),
                sentry_modules.ModulesIntegration(),
                sentry_stdlib.StdlibIntegration(),
                sentry_atexit.AtexitIntegration(),
            ])
        except Exception as e:
            self._logger.warning(f"Failed to add core Sentry integrations: {e}")
        
        # Database integrations
        try:
            integrations.append(sqlalchemy.SqlalchemyIntegration())
            self.health_status.integration_status['sqlalchemy'] = True
        except Exception:
            self.health_status.integration_status['sqlalchemy'] = False
        
        try:
            integrations.append(redis.RedisIntegration())
            self.health_status.integration_status['redis'] = True
        except Exception:
            self.health_status.integration_status['redis'] = False
        
        # HTTP client integrations
        try:
            integrations.append(httpx.HttpxIntegration())
            self.health_status.integration_status['httpx'] = True
        except Exception:
            self.health_status.integration_status['httpx'] = False
        
        try:
            integrations.append(aiohttp.AiohttpIntegration())
            self.health_status.integration_status['aiohttp'] = True
        except Exception:
            self.health_status.integration_status['aiohttp'] = False
        
        # Framework integrations
        try:
            integrations.append(fastapi.FastApiIntegration())
            self.health_status.integration_status['fastapi'] = True
        except Exception:
            self.health_status.integration_status['fastapi'] = False
        
        try:
            integrations.append(celery.CeleryIntegration())
            self.health_status.integration_status['celery'] = True
        except Exception:
            self.health_status.integration_status['celery'] = False
        
        # Add custom integrations
        integrations.extend(self.config.custom_integrations)
        
        return integrations
    
    def _before_send_handler(self, event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Custom before_send handler for event processing."""
        try:
            # Add custom context
            event.setdefault('contexts', {})
            event['contexts']['raptorflow'] = {
                'version': self.config.release,
                'environment': self.config.environment.value,
                'component': 'backend',
                'instance_id': os.getenv('INSTANCE_ID', 'unknown'),
            }
            
            # Filter sensitive data
            if not self.config.send_default_pii:
                self._filter_pii_data(event)
            
            # Add custom tags
            event.setdefault('tags', {})
            event['tags'].update({
                'service': 'raptorflow-backend',
                'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            })
            
            return event
            
        except Exception as e:
            self._logger.error(f"Error in before_send handler: {e}")
            return None
    
    def _before_breadcrumb_handler(self, breadcrumb: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Custom before_breadcrumb handler for breadcrumb processing."""
        try:
            # Filter sensitive breadcrumb data
            if not self.config.send_default_pii:
                self._filter_breadcrumb_pii(breadcrumb)
            
            # Add custom metadata
            breadcrumb.setdefault('data', {})
            breadcrumb['data']['service'] = 'raptorflow-backend'
            
            return breadcrumb
            
        except Exception as e:
            self._logger.error(f"Error in before_breadcrumb handler: {e}")
            return None
    
    def _filter_pii_data(self, event: Dict[str, Any]) -> None:
        """Filter personally identifiable information from events."""
        pii_patterns = [
            'email', 'password', 'token', 'key', 'secret', 'auth',
            'ssn', 'social_security', 'credit_card', 'card_number',
            'phone', 'address', 'name', 'user', 'id'
        ]
        
        def filter_dict(d: Dict[str, Any]) -> None:
            for key in list(d.keys()):
                if any(pattern in key.lower() for pattern in pii_patterns):
                    d[key] = '[FILTERED]'
                elif isinstance(d[key], dict):
                    filter_dict(d[key])
                elif isinstance(d[key], list):
                    for item in d[key]:
                        if isinstance(item, dict):
                            filter_dict(item)
        
        # Filter request data
        if 'request' in event and isinstance(event['request'], dict):
            request = event['request']
            if 'cookies' in request:
                request['cookies'] = '[FILTERED]'
            if 'headers' in request and isinstance(request['headers'], dict):
                for key in list(request['headers'].keys()):
                    if any(pattern in key.lower() for pattern in ['authorization', 'cookie', 'token']):
                        request['headers'][key] = '[FILTERED]'
        
        # Filter extra data
        if 'extra' in event and isinstance(event['extra'], dict):
            filter_dict(event['extra'])
        
        # Filter contexts
        if 'contexts' in event and isinstance(event['contexts'], dict):
            for context_name, context_data in event['contexts'].items():
                if isinstance(context_data, dict):
                    filter_dict(context_data)
    
    def _filter_breadcrumb_pii(self, breadcrumb: Dict[str, Any]) -> None:
        """Filter PII from breadcrumb data."""
        pii_patterns = ['email', 'password', 'token', 'key', 'secret', 'auth']
        
        if 'data' in breadcrumb and isinstance(breadcrumb['data'], dict):
            for key in list(breadcrumb['data'].keys()):
                if any(pattern in key.lower() for pattern in pii_patterns):
                    breadcrumb['data'][key] = '[FILTERED]'
    
    def _set_initial_tags(self) -> None:
        """Set initial tags for all events."""
        configure_scope(lambda scope: set_tag("service", "raptorflow-backend"))
        configure_scope(lambda scope: set_tag("component", "backend"))
        configure_scope(lambda scope: set_tag("environment", self.config.environment.value))
    
    def is_enabled(self) -> bool:
        """Check if Sentry integration is enabled and healthy."""
        return self.is_initialized and self.health_status.is_healthy
    
    def get_health_status(self) -> SentryHealthStatus:
        """Get current health status of Sentry integration."""
        self.health_status.last_check = datetime.now(timezone.utc)
        return self.health_status
    
    def force_flush(self, timeout: Optional[float] = None) -> bool:
        """Force flush all pending events to Sentry."""
        if not self.is_enabled():
            return False
        
        try:
            flush(timeout or 5.0)
            return True
        except Exception as e:
            self._logger.error(f"Failed to flush Sentry events: {e}")
            return False
    
    def shutdown(self) -> None:
        """Shutdown Sentry integration gracefully."""
        if self.is_enabled():
            try:
                self.force_flush()
                self._logger.info("Sentry integration shutdown successfully")
            except Exception as e:
                self._logger.error(f"Error during Sentry shutdown: {e}")
        
        self.is_initialized = False
        self.health_status.is_healthy = False
        self.health_status.is_enabled = False
    
    @contextmanager
    def capture_transaction(self, name: str, operation: str = "function"):
        """Context manager for capturing transactions."""
        if not self.is_enabled():
            yield None
            return
        
        transaction = start_span(
            op=operation,
            name=name,
        )
        
        try:
            yield transaction
        except Exception as e:
            if transaction:
                transaction.set_status("internal_error")
                capture_exception(e)
            raise
        finally:
            if transaction:
                transaction.set_status("ok")
                transaction.finish()
    
    def get_dsn_info(self) -> Dict[str, Any]:
        """Get information about the configured DSN."""
        if not self.config.dsn:
            return {"error": "No DSN configured"}
        
        try:
            dsn = Dsn(self.config.dsn)
            return {
                "host": dsn.host,
                "port": dsn.port,
                "path": dsn.path,
                "project_id": dsn.project_id,
                "public_key": dsn.public_key[:8] + "..." if dsn.public_key else None,
                "scheme": dsn.scheme,
            }
        except Exception as e:
            return {"error": f"Invalid DSN: {e}"}


# Global Sentry integration manager instance
_sentry_manager: Optional[SentryIntegrationManager] = None


def get_sentry_manager() -> SentryIntegrationManager:
    """Get the global Sentry integration manager instance."""
    global _sentry_manager
    if _sentry_manager is None:
        _sentry_manager = SentryIntegrationManager()
    return _sentry_manager


def initialize_sentry(config: Optional[SentryConfig] = None) -> bool:
    """Initialize Sentry integration with optional custom configuration."""
    global _sentry_manager
    _sentry_manager = SentryIntegrationManager(config)
    return _sentry_manager.is_enabled()


def shutdown_sentry() -> None:
    """Shutdown Sentry integration."""
    global _sentry_manager
    if _sentry_manager:
        _sentry_manager.shutdown()
        _sentry_manager = None
