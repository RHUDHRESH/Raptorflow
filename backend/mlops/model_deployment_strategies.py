"""
S.W.A.R.M. Phase 2: Model Deployment Strategies
Production-ready deployment strategies for ML models
"""

import asyncio
import json
import logging
import os
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import yaml

# Kubernetes imports
try:
    from kubernetes import client, config
    from kubernetes.client.rest import ApiException

    K8S_AVAILABLE = True
except ImportError:
    K8S_AVAILABLE = False

# Docker imports
try:
    import docker
    from docker.models.containers import Container
    from docker.models.images import Image

    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False

# Cloud imports
try:
    import boto3
    from botocore.exceptions import ClientError

    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

try:
    from google.api_core.exceptions import GoogleAPICallError
    from google.cloud import run_v2, storage

    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False

# Monitoring imports
try:
    import prometheus_client
    from prometheus_client import Counter, Gauge, Histogram

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

logger = logging.getLogger("raptorflow.model_deployment")


class DeploymentStrategy(Enum):
    """Deployment strategies."""

    ROLLING = "rolling"
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    SHADOW = "shadow"
    A_B_TEST = "a_b_test"
    MIRROR = "mirror"


class DeploymentStatus(Enum):
    """Deployment status."""

    PENDING = "pending"
    RUNNING = "running"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"
    TERMINATED = "terminated"


class CloudProvider(Enum):
    """Cloud providers."""

    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    ON_PREM = "on_prem"


class ModelFramework(Enum):
    """ML frameworks."""

    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    SKLEARN = "sklearn"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    CUSTOM = "custom"


@dataclass
class ModelConfig:
    """Model configuration."""

    model_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    version: str = "1.0.0"
    framework: ModelFramework = ModelFramework.PYTORCH
    model_path: str = ""
    requirements: List[str] = field(default_factory=list)
    environment: Dict[str, str] = field(default_factory=dict)
    resources: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model_id": self.model_id,
            "name": self.name,
            "version": self.version,
            "framework": self.framework.value,
            "model_path": self.model_path,
            "requirements": self.requirements,
            "environment": self.environment,
            "resources": self.resources,
            "metadata": self.metadata,
        }


@dataclass
class DeploymentConfig:
    """Deployment configuration."""

    deployment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    strategy: DeploymentStrategy = DeploymentStrategy.ROLLING
    cloud_provider: CloudProvider = CloudProvider.AWS
    target_environment: str = "production"
    model_config: ModelConfig = field(default_factory=ModelConfig)
    replicas: int = 1
    cpu_request: str = "100m"
    memory_request: str = "256Mi"
    cpu_limit: str = "500m"
    memory_limit: str = "512Mi"
    autoscaling: Dict[str, Any] = field(default_factory=dict)
    health_check: Dict[str, Any] = field(default_factory=dict)
    traffic_splitting: Dict[str, float] = field(default_factory=dict)
    rollback_policy: Dict[str, Any] = field(default_factory=dict)
    monitoring: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "deployment_id": self.deployment_id,
            "name": self.name,
            "strategy": self.strategy.value,
            "cloud_provider": self.cloud_provider.value,
            "target_environment": self.target_environment,
            "model_config": self.model_config.to_dict(),
            "replicas": self.replicas,
            "cpu_request": self.cpu_request,
            "memory_request": self.memory_request,
            "cpu_limit": self.cpu_limit,
            "memory_limit": self.memory_limit,
            "autoscaling": self.autoscaling,
            "health_check": self.health_check,
            "traffic_splitting": self.traffic_splitting,
            "rollback_policy": self.rollback_policy,
            "monitoring": self.monitoring,
        }


@dataclass
class DeploymentResult:
    """Deployment result."""

    deployment_id: str
    status: DeploymentStatus
    start_time: datetime
    end_time: Optional[datetime]
    endpoint_url: Optional[str]
    metrics: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    rollback_info: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "deployment_id": self.deployment_id,
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "endpoint_url": self.endpoint_url,
            "metrics": self.metrics,
            "error_message": self.error_message,
            "rollback_info": self.rollback_info,
        }


class DeploymentStrategyBase(ABC):
    """Abstract base class for deployment strategies."""

    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.status = DeploymentStatus.PENDING
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.error_message: Optional[str] = None
        self.metrics: Dict[str, Any] = {}

    @abstractmethod
    async def deploy(self) -> DeploymentResult:
        """Deploy the model."""
        pass

    @abstractmethod
    async def rollback(self) -> bool:
        """Rollback the deployment."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check deployment health."""
        pass

    def get_deployment_result(
        self, endpoint_url: Optional[str] = None
    ) -> DeploymentResult:
        """Create deployment result."""
        return DeploymentResult(
            deployment_id=self.config.deployment_id,
            status=self.status,
            start_time=self.start_time or datetime.now(),
            end_time=self.end_time,
            endpoint_url=endpoint_url,
            metrics=self.metrics,
            error_message=self.error_message,
        )


class RollingDeployment(DeploymentStrategyBase):
    """Rolling deployment strategy."""

    async def deploy(self) -> DeploymentResult:
        """Execute rolling deployment."""
        try:
            self.status = DeploymentStatus.RUNNING
            self.start_time = datetime.now()

            logger.info(f"Starting rolling deployment: {self.config.name}")

            # Initialize cloud client
            if self.config.cloud_provider == CloudProvider.AWS:
                endpoint_url = await self._deploy_aws_rolling()
            elif self.config.cloud_provider == CloudProvider.GCP:
                endpoint_url = await self._deploy_gcp_rolling()
            else:
                raise ValueError(
                    f"Unsupported cloud provider: {self.config.cloud_provider}"
                )

            # Wait for health check
            await self._wait_for_health()

            self.status = DeploymentStatus.HEALTHY
            self.end_time = datetime.now()

            logger.info(f"Rolling deployment completed: {self.config.name}")

            return self.get_deployment_result(endpoint_url)

        except Exception as e:
            self.status = DeploymentStatus.FAILED
            self.error_message = str(e)
            self.end_time = datetime.now()
            logger.error(f"Rolling deployment failed: {str(e)}")
            raise

    async def rollback(self) -> bool:
        """Rollback rolling deployment."""
        try:
            self.status = DeploymentStatus.ROLLING_BACK
            logger.info(f"Starting rollback: {self.config.name}")

            # Implement rollback logic
            if self.config.cloud_provider == CloudProvider.AWS:
                success = await self._rollback_aws_rolling()
            elif self.config.cloud_provider == CloudProvider.GCP:
                success = await self._rollback_gcp_rolling()
            else:
                success = False

            if success:
                self.status = DeploymentStatus.ROLLED_BACK
                logger.info(f"Rollback completed: {self.config.name}")
            else:
                self.status = DeploymentStatus.FAILED
                logger.error(f"Rollback failed: {self.config.name}")

            return success

        except Exception as e:
            self.status = DeploymentStatus.FAILED
            self.error_message = str(e)
            logger.error(f"Rollback error: {str(e)}")
            return False

    async def health_check(self) -> bool:
        """Check deployment health."""
        try:
            # Implement health check logic
            if self.config.cloud_provider == CloudProvider.AWS:
                return await self._health_check_aws()
            elif self.config.cloud_provider == CloudProvider.GCP:
                return await self._health_check_gcp()
            else:
                return False
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False

    async def _deploy_aws_rolling(self) -> str:
        """Deploy to AWS with rolling strategy."""
        # Simulate AWS deployment
        logger.info("Deploying to AWS ECS/EKS with rolling update")

        # Create deployment resources
        deployment_time = time.time()

        # Simulate deployment steps
        await asyncio.sleep(2)  # Create task/service
        await asyncio.sleep(3)  # Pull container image
        await asyncio.sleep(2)  # Start new instances
        await asyncio.sleep(1)  # Terminate old instances

        endpoint_url = f"https://{self.config.name}-{self.config.deployment_id[:8]}.us-west-2.elb.amazonaws.com"

        self.metrics.update(
            {
                "deployment_time": time.time() - deployment_time,
                "instances_deployed": self.config.replicas,
                "endpoint": endpoint_url,
            }
        )

        return endpoint_url

    async def _deploy_gcp_rolling(self) -> str:
        """Deploy to GCP with rolling strategy."""
        # Simulate GCP deployment
        logger.info("Deploying to GCP Cloud Run with rolling update")

        deployment_time = time.time()

        # Simulate deployment steps
        await asyncio.sleep(1)  # Build container
        await asyncio.sleep(2)  # Push to Artifact Registry
        await asyncio.sleep(2)  # Deploy to Cloud Run
        await asyncio.sleep(1)  # Configure traffic

        endpoint_url = (
            f"https://{self.config.name}-{self.config.deployment_id[:8]}.a.run.app"
        )

        self.metrics.update(
            {
                "deployment_time": time.time() - deployment_time,
                "instances_deployed": self.config.replicas,
                "endpoint": endpoint_url,
            }
        )

        return endpoint_url

    async def _rollback_aws_rolling(self) -> bool:
        """Rollback AWS deployment."""
        logger.info("Rolling back AWS deployment")
        await asyncio.sleep(3)  # Simulate rollback time
        return True

    async def _rollback_gcp_rolling(self) -> bool:
        """Rollback GCP deployment."""
        logger.info("Rolling back GCP deployment")
        await asyncio.sleep(2)  # Simulate rollback time
        return True

    async def _health_check_aws(self) -> bool:
        """Health check for AWS deployment."""
        await asyncio.sleep(1)  # Simulate health check
        return True

    async def _health_check_gcp(self) -> bool:
        """Health check for GCP deployment."""
        await asyncio.sleep(1)  # Simulate health check
        return True

    async def _wait_for_health(self):
        """Wait for deployment to become healthy."""
        max_wait_time = self.config.rollback_policy.get("health_check_timeout", 300)
        start_time = time.time()

        while time.time() - start_time < max_wait_time:
            if await self.health_check():
                break
            await asyncio.sleep(5)
        else:
            raise TimeoutError("Health check timeout")


class BlueGreenDeployment(DeploymentStrategyBase):
    """Blue-Green deployment strategy."""

    def __init__(self, config: DeploymentConfig):
        super().__init__(config)
        self.blue_endpoint: Optional[str] = None
        self.green_endpoint: Optional[str] = None
        self.active_color: str = "blue"

    async def deploy(self) -> DeploymentResult:
        """Execute blue-green deployment."""
        try:
            self.status = DeploymentStatus.RUNNING
            self.start_time = datetime.now()

            logger.info(f"Starting blue-green deployment: {self.config.name}")

            # Deploy green environment
            await self._deploy_green()

            # Health check green environment
            await self._wait_for_green_health()

            # Switch traffic to green
            await self._switch_traffic_to_green()

            # Keep blue for rollback
            self.blue_endpoint = self.green_endpoint
            self.active_color = "green"

            self.status = DeploymentStatus.HEALTHY
            self.end_time = datetime.now()

            logger.info(f"Blue-green deployment completed: {self.config.name}")

            return self.get_deployment_result(self.green_endpoint)

        except Exception as e:
            self.status = DeploymentStatus.FAILED
            self.error_message = str(e)
            self.end_time = datetime.now()
            logger.error(f"Blue-green deployment failed: {str(e)}")
            raise

    async def rollback(self) -> bool:
        """Rollback blue-green deployment."""
        try:
            self.status = DeploymentStatus.ROLLING_BACK
            logger.info(f"Starting blue-green rollback: {self.config.name}")

            # Switch traffic back to blue
            await self._switch_traffic_to_blue()

            # Terminate green environment
            await self._terminate_green()

            self.active_color = "blue"
            self.status = DeploymentStatus.ROLLED_BACK

            logger.info(f"Blue-green rollback completed: {self.config.name}")
            return True

        except Exception as e:
            self.status = DeploymentStatus.FAILED
            self.error_message = str(e)
            logger.error(f"Blue-green rollback failed: {str(e)}")
            return False

    async def health_check(self) -> bool:
        """Check deployment health."""
        try:
            if self.active_color == "green" and self.green_endpoint:
                return await self._check_endpoint_health(self.green_endpoint)
            elif self.active_color == "blue" and self.blue_endpoint:
                return await self._check_endpoint_health(self.blue_endpoint)
            return False
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False

    async def _deploy_green(self):
        """Deploy green environment."""
        logger.info("Deploying green environment")

        if self.config.cloud_provider == CloudProvider.AWS:
            self.green_endpoint = f"https://green-{self.config.name}-{self.config.deployment_id[:8]}.us-west-2.elb.amazonaws.com"
        elif self.config.cloud_provider == CloudProvider.GCP:
            self.green_endpoint = f"https://green-{self.config.name}-{self.config.deployment_id[:8]}.a.run.app"
        else:
            raise ValueError(
                f"Unsupported cloud provider: {self.config.cloud_provider}"
            )

        await asyncio.sleep(5)  # Simulate deployment time

    async def _wait_for_green_health(self):
        """Wait for green environment to be healthy."""
        logger.info("Waiting for green environment health check")
        max_wait_time = 300
        start_time = time.time()

        while time.time() - start_time < max_wait_time:
            if await self._check_endpoint_health(self.green_endpoint):
                break
            await asyncio.sleep(5)
        else:
            raise TimeoutError("Green environment health check timeout")

    async def _switch_traffic_to_green(self):
        """Switch traffic to green environment."""
        logger.info("Switching traffic to green environment")
        await asyncio.sleep(2)  # Simulate traffic switching

    async def _switch_traffic_to_blue(self):
        """Switch traffic to blue environment."""
        logger.info("Switching traffic to blue environment")
        await asyncio.sleep(2)  # Simulate traffic switching

    async def _terminate_green(self):
        """Terminate green environment."""
        logger.info("Terminating green environment")
        await asyncio.sleep(2)  # Simulate termination

    async def _check_endpoint_health(self, endpoint: str) -> bool:
        """Check endpoint health."""
        await asyncio.sleep(1)  # Simulate health check
        return True


class CanaryDeployment(DeploymentStrategyBase):
    """Canary deployment strategy."""

    def __init__(self, config: DeploymentConfig):
        super().__init__(config)
        self.stable_endpoint: Optional[str] = None
        self.canary_endpoint: Optional[str] = None
        self.current_traffic_split: float = 0.0

    async def deploy(self) -> DeploymentResult:
        """Execute canary deployment."""
        try:
            self.status = DeploymentStatus.RUNNING
            self.start_time = datetime.now()

            logger.info(f"Starting canary deployment: {self.config.name}")

            # Deploy canary with initial traffic split
            initial_split = self.config.traffic_splitting.get("initial", 0.05)
            await self._deploy_canary(initial_split)

            # Gradually increase traffic
            await self._gradual_traffic_increase()

            # Promote canary to stable
            await self._promote_canary()

            self.status = DeploymentStatus.HEALTHY
            self.end_time = datetime.now()

            logger.info(f"Canary deployment completed: {self.config.name}")

            return self.get_deployment_result(self.canary_endpoint)

        except Exception as e:
            self.status = DeploymentStatus.FAILED
            self.error_message = str(e)
            self.end_time = datetime.now()
            logger.error(f"Canary deployment failed: {str(e)}")
            raise

    async def rollback(self) -> bool:
        """Rollback canary deployment."""
        try:
            self.status = DeploymentStatus.ROLLING_BACK
            logger.info(f"Starting canary rollback: {self.config.name}")

            # Switch all traffic back to stable
            await self._switch_all_traffic_to_stable()

            # Terminate canary
            await self._terminate_canary()

            self.status = DeploymentStatus.ROLLED_BACK
            logger.info(f"Canary rollback completed: {self.config.name}")
            return True

        except Exception as e:
            self.status = DeploymentStatus.FAILED
            self.error_message = str(e)
            logger.error(f"Canary rollback failed: {str(e)}")
            return False

    async def health_check(self) -> bool:
        """Check deployment health."""
        try:
            # Check both stable and canary endpoints
            stable_healthy = await self._check_endpoint_health(self.stable_endpoint)
            canary_healthy = await self._check_endpoint_health(self.canary_endpoint)
            return stable_healthy and canary_healthy
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False

    async def _deploy_canary(self, traffic_split: float):
        """Deploy canary with traffic split."""
        logger.info(f"Deploying canary with {traffic_split:.1%} traffic")

        if self.config.cloud_provider == CloudProvider.AWS:
            self.canary_endpoint = f"https://canary-{self.config.name}-{self.config.deployment_id[:8]}.us-west-2.elb.amazonaws.com"
            self.stable_endpoint = (
                f"https://stable-{self.config.name}.us-west-2.elb.amazonaws.com"
            )
        elif self.config.cloud_provider == CloudProvider.GCP:
            self.canary_endpoint = f"https://canary-{self.config.name}-{self.config.deployment_id[:8]}.a.run.app"
            self.stable_endpoint = f"https://stable-{self.config.name}.a.run.app"
        else:
            raise ValueError(
                f"Unsupported cloud provider: {self.config.cloud_provider}"
            )

        await asyncio.sleep(3)  # Simulate deployment
        await self._update_traffic_split(traffic_split)

    async def _gradual_traffic_increase(self):
        """Gradually increase traffic to canary."""
        logger.info("Gradually increasing traffic to canary")

        steps = self.config.traffic_splitting.get(
            "steps", [0.05, 0.25, 0.50, 0.75, 1.0]
        )
        step_duration = self.config.traffic_splitting.get(
            "step_duration", 300
        )  # 5 minutes

        for split in steps:
            logger.info(f"Increasing canary traffic to {split:.1%}")
            await self._update_traffic_split(split)
            await asyncio.sleep(
                step_duration / 10
            )  # Simulate wait time (shortened for demo)

            # Health check
            if not await self.health_check():
                raise RuntimeError(f"Canary health check failed at {split:.1%} traffic")

    async def _promote_canary(self):
        """Promote canary to stable."""
        logger.info("Promoting canary to stable")
        await asyncio.sleep(2)  # Simulate promotion

    async def _switch_all_traffic_to_stable(self):
        """Switch all traffic to stable."""
        logger.info("Switching all traffic to stable")
        await self._update_traffic_split(0.0)
        await asyncio.sleep(2)  # Simulate traffic switching

    async def _terminate_canary(self):
        """Terminate canary."""
        logger.info("Terminating canary")
        await asyncio.sleep(2)  # Simulate termination

    async def _update_traffic_split(self, canary_split: float):
        """Update traffic split."""
        self.current_traffic_split = canary_split
        logger.info(
            f"Traffic split: stable={1-canary_split:.1%}, canary={canary_split:.1%}"
        )
        await asyncio.sleep(1)  # Simulate traffic update

    async def _check_endpoint_health(self, endpoint: str) -> bool:
        """Check endpoint health."""
        await asyncio.sleep(1)  # Simulate health check
        return True


class ShadowDeployment(DeploymentStrategyBase):
    """Shadow deployment strategy."""

    def __init__(self, config: DeploymentConfig):
        super().__init__(config)
        self.production_endpoint: Optional[str] = None
        self.shadow_endpoint: Optional[str] = None

    async def deploy(self) -> DeploymentResult:
        """Execute shadow deployment."""
        try:
            self.status = DeploymentStatus.RUNNING
            self.start_time = datetime.now()

            logger.info(f"Starting shadow deployment: {self.config.name}")

            # Deploy shadow instance
            await self._deploy_shadow()

            # Configure traffic mirroring
            await self._configure_traffic_mirroring()

            # Monitor shadow performance
            await self._monitor_shadow_performance()

            self.status = DeploymentStatus.HEALTHY
            self.end_time = datetime.now()

            logger.info(f"Shadow deployment completed: {self.config.name}")

            return self.get_deployment_result(self.production_endpoint)

        except Exception as e:
            self.status = DeploymentStatus.FAILED
            self.error_message = str(e)
            self.end_time = datetime.now()
            logger.error(f"Shadow deployment failed: {str(e)}")
            raise

    async def rollback(self) -> bool:
        """Rollback shadow deployment."""
        try:
            self.status = DeploymentStatus.ROLLING_BACK
            logger.info(f"Starting shadow rollback: {self.config.name}")

            # Disable traffic mirroring
            await self._disable_traffic_mirroring()

            # Terminate shadow
            await self._terminate_shadow()

            self.status = DeploymentStatus.ROLLED_BACK
            logger.info(f"Shadow rollback completed: {self.config.name}")
            return True

        except Exception as e:
            self.status = DeploymentStatus.FAILED
            self.error_message = str(e)
            logger.error(f"Shadow rollback failed: {str(e)}")
            return False

    async def health_check(self) -> bool:
        """Check deployment health."""
        try:
            # Shadow deployment doesn't affect production traffic
            # Just check if shadow is running properly
            return await self._check_shadow_health()
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False

    async def _deploy_shadow(self):
        """Deploy shadow instance."""
        logger.info("Deploying shadow instance")

        if self.config.cloud_provider == CloudProvider.AWS:
            self.production_endpoint = (
                f"https://prod-{self.config.name}.us-west-2.elb.amazonaws.com"
            )
            self.shadow_endpoint = f"https://shadow-{self.config.name}-{self.config.deployment_id[:8]}.us-west-2.elb.amazonaws.com"
        elif self.config.cloud_provider == CloudProvider.GCP:
            self.production_endpoint = f"https://prod-{self.config.name}.a.run.app"
            self.shadow_endpoint = f"https://shadow-{self.config.name}-{self.config.deployment_id[:8]}.a.run.app"
        else:
            raise ValueError(
                f"Unsupported cloud provider: {self.config.cloud_provider}"
            )

        await asyncio.sleep(4)  # Simulate deployment

    async def _configure_traffic_mirroring(self):
        """Configure traffic mirroring."""
        logger.info("Configuring traffic mirroring")
        await asyncio.sleep(2)  # Simulate configuration

    async def _monitor_shadow_performance(self):
        """Monitor shadow performance."""
        logger.info("Monitoring shadow performance")
        await asyncio.sleep(3)  # Simulate monitoring

    async def _disable_traffic_mirroring(self):
        """Disable traffic mirroring."""
        logger.info("Disabling traffic mirroring")
        await asyncio.sleep(1)  # Simulate disabling

    async def _terminate_shadow(self):
        """Terminate shadow."""
        logger.info("Terminating shadow")
        await asyncio.sleep(2)  # Simulate termination

    async def _check_shadow_health(self) -> bool:
        """Check shadow health."""
        await asyncio.sleep(1)  # Simulate health check
        return True


class DeploymentManager:
    """Main deployment manager."""

    def __init__(self):
        self.deployments: Dict[str, DeploymentStrategyBase] = {}
        self.deployment_history: List[DeploymentResult] = []
        self.strategy_registry = {
            DeploymentStrategy.ROLLING: RollingDeployment,
            DeploymentStrategy.BLUE_GREEN: BlueGreenDeployment,
            DeploymentStrategy.CANARY: CanaryDeployment,
            DeploymentStrategy.SHADOW: ShadowDeployment,
        }

    def create_deployment(self, config: DeploymentConfig) -> DeploymentStrategyBase:
        """Create deployment from configuration."""
        strategy_class = self.strategy_registry.get(config.strategy)
        if strategy_class is None:
            raise ValueError(f"Unknown deployment strategy: {config.strategy}")

        return strategy_class(config)

    async def deploy_model(self, config: DeploymentConfig) -> DeploymentResult:
        """Deploy model with specified strategy."""
        deployment = self.create_deployment(config)
        self.deployments[config.deployment_id] = deployment

        try:
            result = await deployment.deploy()
            self.deployment_history.append(result)
            return result
        except Exception as e:
            # Create failed result
            failed_result = DeploymentResult(
                deployment_id=config.deployment_id,
                status=DeploymentStatus.FAILED,
                start_time=datetime.now(),
                end_time=datetime.now(),
                endpoint_url=None,
                error_message=str(e),
            )
            self.deployment_history.append(failed_result)
            raise

    async def rollback_deployment(self, deployment_id: str) -> bool:
        """Rollback deployment."""
        if deployment_id not in self.deployments:
            raise ValueError(f"Deployment {deployment_id} not found")

        deployment = self.deployments[deployment_id]
        return await deployment.rollback()

    def get_deployment_status(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """Get deployment status."""
        if deployment_id not in self.deployments:
            return None

        deployment = self.deployments[deployment_id]
        return {
            "deployment_id": deployment_id,
            "status": deployment.status.value,
            "strategy": deployment.config.strategy.value,
            "start_time": (
                deployment.start_time.isoformat() if deployment.start_time else None
            ),
            "end_time": (
                deployment.end_time.isoformat() if deployment.end_time else None
            ),
            "metrics": deployment.metrics,
            "error_message": deployment.error_message,
        }

    def get_deployment_metrics(self) -> Dict[str, Any]:
        """Get deployment metrics."""
        total_deployments = len(self.deployment_history)
        successful_deployments = len(
            [d for d in self.deployment_history if d.status == DeploymentStatus.HEALTHY]
        )
        failed_deployments = len(
            [d for d in self.deployment_history if d.status == DeploymentStatus.FAILED]
        )

        success_rate = (
            successful_deployments / total_deployments if total_deployments > 0 else 0
        )

        # Metrics by strategy
        strategy_metrics = {}
        for strategy in DeploymentStrategy:
            strategy_deployments = [
                d
                for d in self.deployment_history
                if d.metrics.get("strategy") == strategy.value
            ]
            if strategy_deployments:
                strategy_successful = len(
                    [
                        d
                        for d in strategy_deployments
                        if d.status == DeploymentStatus.HEALTHY
                    ]
                )
                strategy_metrics[strategy.value] = {
                    "total": len(strategy_deployments),
                    "successful": strategy_successful,
                    "failed": len(strategy_deployments) - strategy_successful,
                    "success_rate": strategy_successful / len(strategy_deployments),
                }

        return {
            "total_deployments": total_deployments,
            "successful_deployments": successful_deployments,
            "failed_deployments": failed_deployments,
            "success_rate": success_rate,
            "strategy_metrics": strategy_metrics,
            "active_deployments": len(self.deployments),
        }


# Deployment templates
class DeploymentTemplates:
    """Predefined deployment templates."""

    @staticmethod
    def get_production_deployment() -> DeploymentConfig:
        """Get production deployment template."""
        return DeploymentConfig(
            name="production-model",
            strategy=DeploymentStrategy.BLUE_GREEN,
            cloud_provider=CloudProvider.AWS,
            target_environment="production",
            replicas=3,
            cpu_request="500m",
            memory_request="1Gi",
            cpu_limit="2000m",
            memory_limit="4Gi",
            autoscaling={
                "enabled": True,
                "min_replicas": 3,
                "max_replicas": 10,
                "target_cpu_utilization": 70,
            },
            health_check={
                "path": "/health",
                "interval": 30,
                "timeout": 5,
                "failure_threshold": 3,
            },
            rollback_policy={
                "enabled": True,
                "health_check_timeout": 300,
                "automatic_rollback": True,
            },
            monitoring={
                "enabled": True,
                "metrics": ["latency", "throughput", "error_rate"],
                "alerts": ["high_latency", "high_error_rate"],
            },
        )

    @staticmethod
    def get_staging_deployment() -> DeploymentConfig:
        """Get staging deployment template."""
        return DeploymentConfig(
            name="staging-model",
            strategy=DeploymentStrategy.ROLLING,
            cloud_provider=CloudProvider.GCP,
            target_environment="staging",
            replicas=2,
            cpu_request="200m",
            memory_request="512Mi",
            cpu_limit="1000m",
            memory_limit="2Gi",
            autoscaling={
                "enabled": True,
                "min_replicas": 2,
                "max_replicas": 5,
                "target_cpu_utilization": 80,
            },
        )

    @staticmethod
    def get_canary_deployment() -> DeploymentConfig:
        """Get canary deployment template."""
        return DeploymentConfig(
            name="canary-model",
            strategy=DeploymentStrategy.CANARY,
            cloud_provider=CloudProvider.AWS,
            target_environment="production",
            replicas=1,
            traffic_splitting={
                "initial": 0.05,
                "steps": [0.05, 0.25, 0.50, 0.75, 1.0],
                "step_duration": 300,
            },
            rollback_policy={"enabled": True, "automatic_rollback": True},
        )


# Example usage
async def example_usage():
    """Example usage of model deployment strategies."""
    # Create deployment manager
    manager = DeploymentManager()

    # Create deployment configuration
    config = DeploymentTemplates.get_production_deployment()
    config.model_config = ModelConfig(
        name="image-classifier",
        version="1.0.0",
        framework=ModelFramework.PYTORCH,
        model_path="/models/image_classifier_v1.0.0.pth",
    )

    # Deploy model
    result = await manager.deploy_model(config)

    print(f"Deployment: {result.deployment_id}")
    print(f"Status: {result.status.value}")
    print(f"Endpoint: {result.endpoint_url}")
    print(
        f"Deployment time: {(result.end_time - result.start_time).total_seconds():.2f}s"
    )

    # Get metrics
    metrics = manager.get_deployment_metrics()
    print(f"Deployment metrics: {metrics}")


if __name__ == "__main__":
    asyncio.run(example_usage())
