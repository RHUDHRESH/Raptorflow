"""
Google Cloud Platform (GCP) client singleton.

Provides centralized access to GCP services with authentication,
project management, and configuration handling.
"""

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from google.auth import default
from google.auth.exceptions import DefaultCredentialsError
from google.oauth2 import service_account

try:
    import google.cloud.resourcemanager_v3 as resource_manager
except Exception:  # pragma: no cover - optional dependency
    resource_manager = None

try:
    from google.cloud import bigquery
except Exception:  # pragma: no cover - optional dependency
    bigquery = None

try:
    from google.cloud import logging as cloud_logging
except Exception:  # pragma: no cover - optional dependency
    cloud_logging = None

try:
    from google.cloud import pubsub_v1
except Exception:  # pragma: no cover - optional dependency
    pubsub_v1 = None

try:
    from google.cloud import storage
except Exception:  # pragma: no cover - optional dependency
    storage = None

try:
    from google.cloud import tasks_v2
except Exception:  # pragma: no cover - optional dependency
    tasks_v2 = None

logger = logging.getLogger(__name__)


@dataclass
class GCPConfig:
    """GCP configuration settings."""

    project_id: str
    region: str
    zone: str
    service_account_path: Optional[str] = None
    credentials: Optional[Any] = None

    # Service configurations
    storage_bucket: Optional[str] = None
    bigquery_dataset: Optional[str] = None
    pubsub_topic: Optional[str] = None
    cloud_tasks_queue: Optional[str] = None

    # Feature flags
    enable_storage: bool = True
    enable_bigquery: bool = True
    enable_pubsub: bool = True
    enable_cloud_tasks: bool = True

    # Performance settings
    storage_timeout: int = 30
    bigquery_timeout: int = 60
    pubsub_timeout: int = 30
    cloud_tasks_timeout: int = 30

    @classmethod
    def from_env(cls) -> "GCPConfig":
        """Create configuration from environment variables."""
        return cls(
            project_id=os.getenv("GCP_PROJECT_ID", ""),
            region=os.getenv("GCP_REGION", "us-central1"),
            zone=os.getenv("GCP_ZONE", "us-central1-a"),
            service_account_path=os.getenv("GCP_SERVICE_ACCOUNT_PATH"),
            storage_bucket=os.getenv("GCP_STORAGE_BUCKET"),
            bigquery_dataset=os.getenv("GCP_BIGQUERY_DATASET"),
            pubsub_topic=os.getenv("GCP_PUBSUB_TOPIC"),
            cloud_tasks_queue=os.getenv("GCP_CLOUD_TASKS_QUEUE"),
            enable_storage=os.getenv("GCP_ENABLE_STORAGE", "true").lower() == "true",
            enable_bigquery=os.getenv("GCP_ENABLE_BIGQUERY", "true").lower() == "true",
            enable_pubsub=os.getenv("GCP_ENABLE_PUBSUB", "true").lower() == "true",
            enable_cloud_tasks=os.getenv("GCP_ENABLE_CLOUD_TASKS", "true").lower()
            == "true",
            storage_timeout=int(os.getenv("GCP_STORAGE_TIMEOUT", "30")),
            bigquery_timeout=int(os.getenv("GCP_BIGQUERY_TIMEOUT", "60")),
            pubsub_timeout=int(os.getenv("GCP_PUBSUB_TIMEOUT", "30")),
            cloud_tasks_timeout=int(os.getenv("GCP_CLOUD_TASKS_TIMEOUT", "30")),
        )


@dataclass
class GCPServiceStatus:
    """Status of GCP services."""

    service_name: str
    enabled: bool
    available: bool
    error_message: Optional[str] = None
    last_checked: datetime = None

    def __post_init__(self):
        if self.last_checked is None:
            self.last_checked = datetime.now()


class GCPClient:
    """Singleton GCP client for managing Google Cloud services."""

    _instance: Optional["GCPClient"] = None

    def __new__(cls) -> "GCPClient":
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize GCP client."""
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.config = GCPConfig.from_env()
        self.logger = logging.getLogger("gcp_client")

        # Service clients
        self.storage_client: Optional[Any] = None
        self.bigquery_client: Optional[Any] = None
        self.pubsub_client: Optional[Any] = None
        self.cloud_tasks_client: Optional[Any] = None
        self.logging_client: Optional[Any] = None
        self.resource_manager_client: Optional[Any] = None

        # Service status
        self.service_status: Dict[str, GCPServiceStatus] = {}

        # Initialize
        self._initialize_credentials()
        self._initialize_services()
        self._check_service_availability()

        self._initialized = True
        self.logger.info(f"GCPClient initialized for project: {self.config.project_id}")

    def _initialize_credentials(self):
        """Initialize GCP credentials."""
        try:
            # Try service account first
            if self.config.service_account_path and os.path.exists(
                self.config.service_account_path
            ):
                self.config.credentials = (
                    service_account.Credentials.from_service_account_file(
                        self.config.service_account_path
                    )
                )
                self.logger.info(
                    f"Using service account: {self.config.service_account_path}"
                )
            else:
                # Try default credentials
                self.config.credentials, _ = default()
                self.logger.info("Using default GCP credentials")

        except DefaultCredentialsError as e:
            self.logger.error(f"Failed to initialize GCP credentials: {e}")
            self.config.credentials = None
        except Exception as e:
            self.logger.error(f"Unexpected error initializing credentials: {e}")
            self.config.credentials = None

    def _initialize_services(self):
        """Initialize GCP service clients."""
        if not self.config.credentials:
            self.logger.warning(
                "No credentials available, skipping service initialization"
            )
            return

        try:
            # Initialize Storage client
            if self.config.enable_storage and storage is not None:
                self.storage_client = storage.Client(
                    project=self.config.project_id, credentials=self.config.credentials
                )
                self.service_status["storage"] = GCPServiceStatus(
                    service_name="storage",
                    enabled=True,
                    available=False,  # Will be checked later
                )

            # Initialize BigQuery client
            if self.config.enable_bigquery and bigquery is not None:
                self.bigquery_client = bigquery.Client(
                    project=self.config.project_id, credentials=self.config.credentials
                )
                self.service_status["bigquery"] = GCPServiceStatus(
                    service_name="bigquery", enabled=True, available=False
                )

            # Initialize Pub/Sub client
            if self.config.enable_pubsub and pubsub_v1 is not None:
                self.pubsub_client = pubsub_v1.PublisherClient(
                    credentials=self.config.credentials
                )
                self.service_status["pubsub"] = GCPServiceStatus(
                    service_name="pubsub", enabled=True, available=False
                )

            # Initialize Cloud Tasks client
            if self.config.enable_cloud_tasks and tasks_v2 is not None:
                self.cloud_tasks_client = tasks_v2.CloudTasksClient(
                    credentials=self.config.credentials
                )
                self.service_status["cloud_tasks"] = GCPServiceStatus(
                    service_name="cloud_tasks", enabled=True, available=False
                )

            # Initialize Resource Manager client
            if resource_manager is not None:
                self.resource_manager_client = resource_manager.ProjectsClient(
                    credentials=self.config.credentials
                )

        except Exception as e:
            self.logger.error(f"Failed to initialize GCP services: {e}")

    def _check_service_availability(self):
        """Check availability of enabled services."""
        if not self.config.credentials:
            return

        # Check Storage
        if self.storage_client and self.config.enable_storage:
            try:
                # Try to list buckets
                list(self.storage_client.list_buckets(max_results=1))
                self.service_status["storage"].available = True
                self.service_status["storage"].last_checked = datetime.now()
            except Exception as e:
                self.service_status["storage"].available = False
                self.service_status["storage"].error_message = str(e)
                self.service_status["storage"].last_checked = datetime.now()

        # Check BigQuery
        if self.bigquery_client and self.config.enable_bigquery:
            try:
                # Try to get project info
                self.bigquery_client.get_project(self.config.project_id)
                self.service_status["bigquery"].available = True
                self.service_status["bigquery"].last_checked = datetime.now()
            except Exception as e:
                self.service_status["bigquery"].available = False
                self.service_status["bigquery"].error_message = str(e)
                self.service_status["bigquery"].last_checked = datetime.now()

        # Check Pub/Sub
        if self.pubsub_client and self.config.enable_pubsub:
            try:
                # Try to list topics
                self.pubsub_client.list_topics(
                    project=f"projects/{self.config.project_id}"
                )
                self.service_status["pubsub"].available = True
                self.service_status["pubsub"].last_checked = datetime.now()
            except Exception as e:
                self.service_status["pubsub"].available = False
                self.service_status["pubsub"].error_message = str(e)
                self.service_status["pubsub"].last_checked = datetime.now()

        # Check Cloud Tasks
        if self.cloud_tasks_client and self.config.enable_cloud_tasks:
            try:
                # Try to list queues
                parent = (
                    f"projects/{self.config.project_id}/locations/{self.config.region}"
                )
                self.cloud_tasks_client.list_queues(parent=parent)
                self.service_status["cloud_tasks"].available = True
                self.service_status["cloud_tasks"].last_checked = datetime.now()
            except Exception as e:
                self.service_status["cloud_tasks"].available = False
                self.service_status["cloud_tasks"].error_message = str(e)
                self.service_status["cloud_tasks"].last_checked = datetime.now()

    def get_project_id(self) -> str:
        """Get GCP project ID."""
        return self.config.project_id

    def get_region(self) -> str:
        """Get GCP region."""
        return self.config.region

    def get_zone(self) -> str:
        """Get GCP zone."""
        return self.config.zone

    def get_credentials(self) -> Optional[Any]:
        """Get GCP credentials."""
        return self.config.credentials

    def is_authenticated(self) -> bool:
        """Check if GCP client is authenticated."""
        return self.config.credentials is not None

    def get_service_status(self, service_name: str) -> Optional[GCPServiceStatus]:
        """Get status of a specific service."""
        return self.service_status.get(service_name)

    def get_all_service_status(self) -> Dict[str, GCPServiceStatus]:
        """Get status of all services."""
        return self.service_status.copy()

    def is_service_available(self, service_name: str) -> bool:
        """Check if a service is available."""
        status = self.service_status.get(service_name)
        return status is not None and status.available

    def get_storage_client(self) -> Optional[Any]:
        """Get Storage client."""
        if self.is_service_available("storage"):
            return self.storage_client
        return None

    def get_bigquery_client(self) -> Optional[Any]:
        """Get BigQuery client."""
        if self.is_service_available("bigquery"):
            return self.bigquery_client
        return None

    def get_pubsub_client(self) -> Optional[Any]:
        """Get Pub/Sub client."""
        if self.is_service_available("pubsub"):
            return self.pubsub_client
        return None

    def get_cloud_tasks_client(self) -> Optional[Any]:
        """Get Cloud Tasks client."""
        if self.is_service_available("cloud_tasks"):
            return self.cloud_tasks_client
        return None

    def get_logging_client(self) -> Optional[Any]:
        """Get Cloud Logging client."""
        if self.logging_client:
            return self.logging_client

        if cloud_logging is None:
            return None

        if self.is_authenticated():
            try:
                self.logging_client = cloud_logging.Client(
                    project=self.config.project_id, credentials=self.config.credentials
                )
                return self.logging_client
            except Exception as e:
                self.logger.error(f"Failed to create logging client: {e}")
        return None

    def get_resource_manager_client(self) -> Optional[Any]:
        """Get Resource Manager client."""
        if self.is_authenticated():
            return self.resource_manager_client
        return None

    async def refresh_service_status(self):
        """Refresh service availability status."""
        self._check_service_availability()

    def get_project_info(self) -> Dict[str, Any]:
        """Get project information."""
        if not self.is_authenticated():
            return {"error": "Not authenticated"}

        try:
            if self.resource_manager_client:
                project_name = f"projects/{self.config.project_id}"
                project = self.resource_manager_client.get_project(name=project_name)

                return {
                    "project_id": self.config.project_id,
                    "project_number": project.name.split("/")[-1],
                    "display_name": project.display_name,
                    "state": project.state.name,
                    "create_time": (
                        project.create_time.isoformat() if project.create_time else None
                    ),
                    "region": self.config.region,
                    "zone": self.config.zone,
                }
        except Exception as e:
            return {"error": str(e)}

        return {"error": "Resource manager not available"}

    def get_service_config(self, service_name: str) -> Dict[str, Any]:
        """Get configuration for a specific service."""
        config = {
            "project_id": self.config.project_id,
            "region": self.config.region,
            "zone": self.config.zone,
            "enabled": False,
            "available": False,
            "timeout": 30,
        }

        if service_name == "storage":
            config.update(
                {
                    "enabled": self.config.enable_storage,
                    "available": self.is_service_available("storage"),
                    "timeout": self.config.storage_timeout,
                    "bucket": self.config.storage_bucket,
                }
            )
        elif service_name == "bigquery":
            config.update(
                {
                    "enabled": self.config.enable_bigquery,
                    "available": self.is_service_available("bigquery"),
                    "timeout": self.config.bigquery_timeout,
                    "dataset": self.config.bigquery_dataset,
                }
            )
        elif service_name == "pubsub":
            config.update(
                {
                    "enabled": self.config.enable_pubsub,
                    "available": self.is_service_available("pubsub"),
                    "timeout": self.config.pubsub_timeout,
                    "topic": self.config.pubsub_topic,
                }
            )
        elif service_name == "cloud_tasks":
            config.update(
                {
                    "enabled": self.config.enable_cloud_tasks,
                    "available": self.is_service_available("cloud_tasks"),
                    "timeout": self.config.cloud_tasks_timeout,
                    "queue": self.config.cloud_tasks_queue,
                }
            )

        return config

    def get_all_service_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get configuration for all services."""
        services = ["storage", "bigquery", "pubsub", "cloud_tasks"]
        return {service: self.get_service_config(service) for service in services}

    def update_config(self, **kwargs):
        """Update configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                self.logger.info(f"Updated config: {key} = {value}")

        # Reinitialize services if credentials changed
        if "service_account_path" in kwargs or "project_id" in kwargs:
            self._initialize_credentials()
            self._initialize_services()
            self._check_service_availability()

    def enable_service(self, service_name: str):
        """Enable a service."""
        if service_name == "storage":
            self.config.enable_storage = True
        elif service_name == "bigquery":
            self.config.enable_bigquery = True
        elif service_name == "pubsub":
            self.config.enable_pubsub = True
        elif service_name == "cloud_tasks":
            self.config.enable_cloud_tasks = True

        self._initialize_services()
        self._check_service_availability()

    def disable_service(self, service_name: str):
        """Disable a service."""
        if service_name == "storage":
            self.config.enable_storage = False
            self.storage_client = None
        elif service_name == "bigquery":
            self.config.enable_bigquery = False
            self.bigquery_client = None
        elif service_name == "pubsub":
            self.config.enable_pubsub = False
            self.pubsub_client = None
        elif service_name == "cloud_tasks":
            self.config.enable_cloud_tasks = False
            self.cloud_tasks_client = None

        if service_name in self.service_status:
            self.service_status[service_name].enabled = False
            self.service_status[service_name].available = False

    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status."""
        if not self.is_authenticated():
            return {
                "status": "unhealthy",
                "message": "Not authenticated",
                "services": {},
            }

        services = {}
        overall_healthy = True

        for service_name, status in self.service_status.items():
            if status.enabled:
                services[service_name] = {
                    "enabled": status.enabled,
                    "available": status.available,
                    "last_checked": status.last_checked.isoformat(),
                    "error": status.error_message,
                }

                if not status.available:
                    overall_healthy = False

        return {
            "status": "healthy" if overall_healthy else "degraded",
            "project_id": self.config.project_id,
            "region": self.config.region,
            "authenticated": True,
            "services": services,
        }

    async def test_connection(self, service_name: str) -> Dict[str, Any]:
        """Test connection to a specific service."""
        if not self.is_authenticated():
            return {"success": False, "error": "Not authenticated"}

        try:
            if service_name == "storage" and self.storage_client:
                # Test storage by listing buckets
                buckets = list(self.storage_client.list_buckets(max_results=1))
                return {
                    "success": True,
                    "message": f"Storage connection OK, found {len(buckets)} buckets",
                }

            elif service_name == "bigquery" and self.bigquery_client:
                # Test bigquery by getting project info
                project = self.bigquery_client.get_project(self.config.project_id)
                return {
                    "success": True,
                    "message": f"BigQuery connection OK, project: {project.project_id}",
                }

            elif service_name == "pubsub" and self.pubsub_client:
                # Test pubsub by listing topics
                topics = list(
                    self.pubsub_client.list_topics(
                        project=f"projects/{self.config.project_id}", max_results=1
                    )
                )
                return {
                    "success": True,
                    "message": f"Pub/Sub connection OK, found {len(topics)} topics",
                }

            elif service_name == "cloud_tasks" and self.cloud_tasks_client:
                # Test cloud tasks by listing queues
                parent = (
                    f"projects/{self.config.project_id}/locations/{self.config.region}"
                )
                queues = list(
                    self.cloud_tasks_client.list_queues(parent=parent, max_results=1)
                )
                return {
                    "success": True,
                    "message": f"Cloud Tasks connection OK, found {len(queues)} queues",
                }

            else:
                return {
                    "success": False,
                    "error": f"Service {service_name} not available",
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def export_config(self) -> Dict[str, Any]:
        """Export current configuration."""
        return {
            "project_id": self.config.project_id,
            "region": self.config.region,
            "zone": self.config.zone,
            "service_account_path": self.config.service_account_path,
            "storage_bucket": self.config.storage_bucket,
            "bigquery_dataset": self.config.bigquery_dataset,
            "pubsub_topic": self.config.pubsub_topic,
            "cloud_tasks_queue": self.config.cloud_tasks_queue,
            "enable_storage": self.config.enable_storage,
            "enable_bigquery": self.config.enable_bigquery,
            "enable_pubsub": self.config.enable_pubsub,
            "enable_cloud_tasks": self.config.enable_cloud_tasks,
            "storage_timeout": self.config.storage_timeout,
            "bigquery_timeout": self.config.bigquery_timeout,
            "pubsub_timeout": self.config.pubsub_timeout,
            "cloud_tasks_timeout": self.config.cloud_tasks_timeout,
        }

    def import_config(self, config_data: Dict[str, Any]):
        """Import configuration from dictionary."""
        for key, value in config_data.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

        # Reinitialize with new config
        self._initialize_credentials()
        self._initialize_services()
        self._check_service_availability()

    def validate_config(self) -> List[str]:
        """Validate current configuration."""
        errors = []

        if not self.config.project_id:
            errors.append("GCP_PROJECT_ID is required")

        if not self.config.region:
            errors.append("GCP_REGION is required")

        if self.config.enable_storage and not self.config.storage_bucket:
            errors.append("GCP_STORAGE_BUCKET is required when storage is enabled")

        if self.config.enable_bigquery and not self.config.bigquery_dataset:
            errors.append("GCP_BIGQUERY_DATASET is required when BigQuery is enabled")

        if self.config.enable_pubsub and not self.config.pubsub_topic:
            errors.append("GCP_PUBSUB_TOPIC is required when Pub/Sub is enabled")

        if self.config.enable_cloud_tasks and not self.config.cloud_tasks_queue:
            errors.append(
                "GCP_CLOUD_TASKS_QUEUE is required when Cloud Tasks is enabled"
            )

        return errors


# Global GCP client instance
_gcp_client: Optional[GCPClient] = None


def get_gcp_client() -> GCPClient:
    """Get global GCP client instance."""
    global _gcp_client
    if _gcp_client is None:
        _gcp_client = GCPClient()
    return _gcp_client


def initialize_gcp_client(config: Optional[GCPConfig] = None) -> GCPClient:
    """Initialize GCP client with optional config."""
    global _gcp_client
    _gcp_client = GCPClient()

    if config:
        _gcp_client.import_config(config.__dict__)

    return _gcp_client


# Convenience functions
def get_project_id() -> str:
    """Get GCP project ID."""
    return get_gcp_client().get_project_id()


def get_region() -> str:
    """Get GCP region."""
    return get_gcp_client().get_region()


def is_gcp_authenticated() -> bool:
    """Check if GCP is authenticated."""
    return get_gcp_client().is_authenticated()


def get_gcp_health_status() -> Dict[str, Any]:
    """Get GCP health status."""
    return get_gcp_client().get_health_status()
