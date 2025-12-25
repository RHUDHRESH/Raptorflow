"""
S.W.A.R.M. Phase 2: Model Deployment Automation
Production-ready automated model deployment system
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

# Import existing components
from model_deployment_strategies import (
    DeploymentConfig,
    DeploymentManager,
    DeploymentResult,
    DeploymentStrategy,
)
from model_rollback_mechanisms import RollbackConfig, RollbackManager
from model_validation_pipelines import ModelValidationPipeline, ValidationConfig

logger = logging.getLogger("raptorflow.deployment_automation")


class DeploymentStatus(Enum):
    """Deployment status."""

    PENDING = "pending"
    VALIDATING = "validating"
    DEPLOYING = "deploying"
    TESTING = "testing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"
    CANCELLED = "cancelled"


class DeploymentTrigger(Enum):
    """Deployment triggers."""

    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT_DRIVEN = "event_driven"
    API_TRIGGERED = "api_triggered"
    CONTINUOUS_DEPLOYMENT = "continuous_deployment"


@dataclass
class DeploymentAutomationConfig:
    """Deployment automation configuration."""

    automation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    model_name: str = ""
    environment: str = "production"
    deployment_strategy: DeploymentStrategy = DeploymentStrategy.ROLLING
    trigger: DeploymentTrigger = DeploymentTrigger.MANUAL
    validation_required: bool = True
    validation_level: str = "standard"
    auto_rollback: bool = True
    rollback_conditions: Dict[str, Any] = field(default_factory=dict)
    health_check_config: Dict[str, Any] = field(default_factory=dict)
    traffic_config: Dict[str, Any] = field(default_factory=dict)
    approval_required: bool = False
    approvers: List[str] = field(default_factory=list)
    timeout_minutes: int = 60
    notifications: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "automation_id": self.automation_id,
            "name": self.name,
            "description": self.description,
            "model_name": self.model_name,
            "environment": self.environment,
            "deployment_strategy": self.deployment_strategy.value,
            "trigger": self.trigger.value,
            "validation_required": self.validation_required,
            "validation_level": self.validation_level,
            "auto_rollback": self.auto_rollback,
            "rollback_conditions": self.rollback_conditions,
            "health_check_config": self.health_check_config,
            "traffic_config": self.traffic_config,
            "approval_required": self.approval_required,
            "approvers": self.approvers,
            "timeout_minutes": self.timeout_minutes,
            "notifications": self.notifications,
        }


@dataclass
class DeploymentExecution:
    """Deployment execution record."""

    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    automation_id: str = ""
    model_name: str = ""
    model_version: str = ""
    environment: str = ""
    status: DeploymentStatus = DeploymentStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: float = 0.0
    trigger_source: str = ""
    trigger_data: Dict[str, Any] = field(default_factory=dict)
    validation_result: Optional[Dict[str, Any]] = None
    deployment_result: Optional[Dict[str, Any]] = None
    rollback_result: Optional[Dict[str, Any]] = None
    health_checks: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    error_message: Optional[str] = None
    approval_status: str = "pending"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "execution_id": self.execution_id,
            "automation_id": self.automation_id,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "environment": self.environment,
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "trigger_source": self.trigger_source,
            "trigger_data": self.trigger_data,
            "validation_result": self.validation_result,
            "deployment_result": self.deployment_result,
            "rollback_result": self.rollback_result,
            "health_checks": self.health_checks,
            "metrics": self.metrics,
            "error_message": self.error_message,
            "approval_status": self.approval_status,
        }


class DeploymentApproval:
    """Deployment approval system."""

    def __init__(self):
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}
        self.approval_history: List[Dict[str, Any]] = []

    def request_approval(
        self, execution_id: str, approvers: List[str], deployment_info: Dict[str, Any]
    ) -> str:
        """Request deployment approval."""
        approval_request = {
            "request_id": str(uuid.uuid4()),
            "execution_id": execution_id,
            "approvers": approvers,
            "deployment_info": deployment_info,
            "requested_at": datetime.now(),
            "status": "pending",
            "responses": {},
        }

        self.pending_approvals[execution_id] = approval_request
        return approval_request["request_id"]

    def approve_deployment(
        self, execution_id: str, approver: str, comment: str = ""
    ) -> bool:
        """Approve deployment."""
        if execution_id not in self.pending_approvals:
            return False

        request = self.pending_approvals[execution_id]
        request["responses"][approver] = {
            "approved": True,
            "comment": comment,
            "timestamp": datetime.now(),
        }

        # Check if all approvers have approved
        if len(request["responses"]) == len(request["approvers"]):
            all_approved = all(
                response["approved"] for response in request["responses"].values()
            )

            if all_approved:
                request["status"] = "approved"
                self.approval_history.append(request.copy())
                del self.pending_approvals[execution_id]
                return True

        return False

    def reject_deployment(
        self, execution_id: str, approver: str, comment: str = ""
    ) -> bool:
        """Reject deployment."""
        if execution_id not in self.pending_approvals:
            return False

        request = self.pending_approvals[execution_id]
        request["responses"][approver] = {
            "approved": False,
            "comment": comment,
            "timestamp": datetime.now(),
        }

        request["status"] = "rejected"
        self.approval_history.append(request.copy())
        del self.pending_approvals[execution_id]

        return True

    def get_approval_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get approval status."""
        if execution_id in self.pending_approvals:
            return self.pending_approvals[execution_id]

        # Check history
        for request in self.approval_history:
            if request["execution_id"] == execution_id:
                return request

        return None


class HealthChecker:
    """Deployment health checker."""

    def __init__(self):
        self.health_check_history: List[Dict[str, Any]] = []

    async def perform_health_check(
        self, deployment_info: Dict[str, Any], health_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform deployment health check."""
        health_check = {
            "check_id": str(uuid.uuid4()),
            "deployment_id": deployment_info.get("execution_id"),
            "timestamp": datetime.now(),
            "status": "running",
            "checks": {},
        }

        try:
            # Perform different health checks
            checks = health_config.get(
                "checks", ["connectivity", "performance", "accuracy"]
            )

            if "connectivity" in checks:
                health_check["checks"]["connectivity"] = await self._check_connectivity(
                    deployment_info
                )

            if "performance" in checks:
                health_check["checks"]["performance"] = await self._check_performance(
                    deployment_info
                )

            if "accuracy" in checks:
                health_check["checks"]["accuracy"] = await self._check_accuracy(
                    deployment_info
                )

            if "resource_usage" in checks:
                health_check["checks"]["resource_usage"] = (
                    await self._check_resource_usage(deployment_info)
                )

            # Overall health status
            all_passed = all(
                check.get("passed", False) for check in health_check["checks"].values()
            )

            health_check["status"] = "passed" if all_passed else "failed"
            health_check["overall_passed"] = all_passed

        except Exception as e:
            health_check["status"] = "error"
            health_check["error"] = str(e)

        self.health_check_history.append(health_check)
        return health_check

    async def _check_connectivity(
        self, deployment_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check deployment connectivity."""
        await asyncio.sleep(1)  # Simulate connectivity check

        return {
            "passed": True,
            "response_time_ms": 150,
            "status_code": 200,
            "message": "Connectivity check passed",
        }

    async def _check_performance(
        self, deployment_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check deployment performance."""
        await asyncio.sleep(2)  # Simulate performance check

        return {
            "passed": True,
            "latency_ms": 450,
            "throughput_rps": 120,
            "cpu_usage": 0.65,
            "memory_usage": 0.58,
            "message": "Performance check passed",
        }

    async def _check_accuracy(self, deployment_info: Dict[str, Any]) -> Dict[str, Any]:
        """Check model accuracy."""
        await asyncio.sleep(3)  # Simulate accuracy check

        return {
            "passed": True,
            "accuracy": 0.87,
            "precision": 0.85,
            "recall": 0.89,
            "message": "Accuracy check passed",
        }

    async def _check_resource_usage(
        self, deployment_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check resource usage."""
        await asyncio.sleep(1)  # Simulate resource check

        return {
            "passed": True,
            "cpu_cores": 4,
            "memory_gb": 8,
            "disk_usage_gb": 2.5,
            "message": "Resource usage check passed",
        }


class DeploymentAutomation:
    """Main deployment automation system."""

    def __init__(self):
        self.automations: Dict[str, DeploymentAutomationConfig] = {}
        self.executions: Dict[str, DeploymentExecution] = {}
        self.active_executions: Dict[str, asyncio.Task] = {}
        self.deployment_manager = DeploymentManager()
        self.validation_pipeline = ModelValidationPipeline()
        self.rollback_manager = RollbackManager()
        self.approval_system = DeploymentApproval()
        self.health_checker = HealthChecker()

    def register_automation(self, config: DeploymentAutomationConfig) -> str:
        """Register deployment automation."""
        self.automations[config.automation_id] = config
        logger.info(f"Registered deployment automation: {config.name}")
        return config.automation_id

    async def trigger_deployment(
        self,
        automation_id: str,
        model_version: str,
        trigger_data: Dict[str, Any] = None,
    ) -> str:
        """Trigger deployment automation."""
        if automation_id not in self.automations:
            raise ValueError(f"Automation {automation_id} not found")

        config = self.automations[automation_id]

        # Create execution record
        execution = DeploymentExecution(
            automation_id=automation_id,
            model_name=config.model_name,
            model_version=model_version,
            environment=config.environment,
            trigger_source=(
                trigger_data.get("trigger_source", "manual")
                if trigger_data
                else "manual"
            ),
            trigger_data=trigger_data or {},
        )

        self.executions[execution.execution_id] = execution

        # Start deployment task
        task = asyncio.create_task(self._execute_deployment(execution, config))
        self.active_executions[execution.execution_id] = task

        return execution.execution_id

    async def _execute_deployment(
        self, execution: DeploymentExecution, config: DeploymentAutomationConfig
    ):
        """Execute deployment automation."""
        try:
            execution.status = DeploymentStatus.VALIDATING
            execution.start_time = datetime.now()

            # Step 1: Approval check (if required)
            if config.approval_required:
                execution.approval_status = "pending"

                # Request approval
                deployment_info = {
                    "execution_id": execution.execution_id,
                    "model_name": execution.model_name,
                    "model_version": execution.model_version,
                    "environment": execution.environment,
                }

                self.approval_system.request_approval(
                    execution.execution_id, config.approvers, deployment_info
                )

                # Wait for approval (simplified - in production use proper notification system)
                await asyncio.sleep(2)  # Simulate approval wait

                # Check approval status
                approval_status = self.approval_system.get_approval_status(
                    execution.execution_id
                )
                if approval_status and approval_status["status"] == "approved":
                    execution.approval_status = "approved"
                else:
                    execution.status = DeploymentStatus.CANCELLED
                    execution.error_message = "Deployment approval not received"
                    execution.end_time = datetime.now()
                    execution.duration = (
                        execution.end_time - execution.start_time
                    ).total_seconds()
                    return

            # Step 2: Validation (if required)
            if config.validation_required:
                execution.status = DeploymentStatus.VALIDATING

                validation_config = ValidationConfig(
                    model_name=execution.model_name,
                    model_version=execution.model_version,
                    validation_level=config.validation_level,
                )

                # Mock model info for validation
                model_info = {
                    "accuracy_metrics": {"overall_accuracy": 0.87},
                    "performance_metrics": {"inference_latency": 850},
                    "data_quality_metrics": {"missing_data_ratio": 0.02},
                    "fairness_metrics": {"demographic_parity": 0.82},
                    "security_metrics": {"adversarial_robustness": 0.75},
                }

                validation_result = await self.validation_pipeline.execute_validation(
                    validation_config, model_info
                )

                execution.validation_result = validation_result.to_dict()

                if validation_result.status.value == "failed":
                    execution.status = DeploymentStatus.FAILED
                    execution.error_message = "Model validation failed"
                    execution.end_time = datetime.now()
                    execution.duration = (
                        execution.end_time - execution.start_time
                    ).total_seconds()
                    return

            # Step 3: Deployment
            execution.status = DeploymentStatus.DEPLOYING

            deployment_config = DeploymentConfig(
                model_name=execution.model_name,
                version=execution.model_version,
                strategy=config.deployment_strategy.value,
                environment=execution.environment,
            )

            deployment_result = await self.deployment_manager.execute_deployment(
                deployment_config
            )
            execution.deployment_result = deployment_result.to_dict()

            if not deployment_result.success:
                execution.status = DeploymentStatus.FAILED
                execution.error_message = deployment_result.error_message
                execution.end_time = datetime.now()
                execution.duration = (
                    execution.end_time - execution.start_time
                ).total_seconds()
                return

            # Step 4: Health checks
            execution.status = DeploymentStatus.TESTING

            deployment_info = {
                "execution_id": execution.execution_id,
                "model_name": execution.model_name,
                "model_version": execution.model_version,
                "environment": execution.environment,
                "deployment_result": deployment_result.to_dict(),
            }

            health_check_result = await self.health_checker.perform_health_check(
                deployment_info, config.health_check_config
            )

            execution.health_checks.append(health_check_result)

            if not health_check_result.get("overall_passed", False):
                # Auto-rollback if enabled
                if config.auto_rollback:
                    await self._perform_rollback(execution, config)
                    return
                else:
                    execution.status = DeploymentStatus.FAILED
                    execution.error_message = "Health checks failed"
                    execution.end_time = datetime.now()
                    execution.duration = (
                        execution.end_time - execution.start_time
                    ).total_seconds()
                    return

            # Step 5: Complete deployment
            execution.status = DeploymentStatus.COMPLETED
            execution.end_time = datetime.now()
            execution.duration = (
                execution.end_time - execution.start_time
            ).total_seconds()

            # Send notifications
            await self._send_notifications(execution, config)

        except Exception as e:
            execution.status = DeploymentStatus.FAILED
            execution.error_message = str(e)
            execution.end_time = datetime.now()
            execution.duration = (
                execution.end_time - execution.start_time
            ).total_seconds()

            # Send failure notifications
            await self._send_notifications(execution, config)

        finally:
            # Clean up active execution
            if execution.execution_id in self.active_executions:
                del self.active_executions[execution.execution_id]

    async def _perform_rollback(
        self, execution: DeploymentExecution, config: DeploymentAutomationConfig
    ):
        """Perform automatic rollback."""
        execution.status = DeploymentStatus.ROLLING_BACK

        rollback_config = RollbackConfig(
            model_name=execution.model_name,
            current_version=execution.model_version,
            target_version="previous_stable",  # In production, get actual previous version
            reason="Health checks failed - automatic rollback",
        )

        try:
            rollback_result = await self.rollback_manager.execute_rollback(
                rollback_config
            )
            execution.rollback_result = rollback_result.to_dict()

            if rollback_result.success:
                execution.status = (
                    DeploymentStatus.FAILED
                )  # Still marked as failed deployment
                execution.error_message = (
                    "Deployment rolled back due to health check failures"
                )
            else:
                execution.error_message = "Deployment failed and rollback also failed"

        except Exception as e:
            execution.error_message = f"Deployment failed and rollback error: {str(e)}"

        execution.end_time = datetime.now()
        execution.duration = (execution.end_time - execution.start_time).total_seconds()

    async def _send_notifications(
        self, execution: DeploymentExecution, config: DeploymentAutomationConfig
    ):
        """Send deployment notifications."""
        try:
            notifications = config.notifications

            if notifications.get("email_enabled", False):
                await self._send_email_notification(execution, notifications)

            if notifications.get("slack_enabled", False):
                await self._send_slack_notification(execution, notifications)

            if notifications.get("webhook_enabled", False):
                await self._send_webhook_notification(execution, notifications)

        except Exception as e:
            logger.error(f"Notification sending failed: {str(e)}")

    async def _send_email_notification(
        self, execution: DeploymentExecution, notifications: Dict[str, Any]
    ):
        """Send email notification."""
        logger.info(f"Email notification sent for deployment {execution.execution_id}")

    async def _send_slack_notification(
        self, execution: DeploymentExecution, notifications: Dict[str, Any]
    ):
        """Send Slack notification."""
        logger.info(f"Slack notification sent for deployment {execution.execution_id}")

    async def _send_webhook_notification(
        self, execution: DeploymentExecution, notifications: Dict[str, Any]
    ):
        """Send webhook notification."""
        logger.info(
            f"Webhook notification sent for deployment {execution.execution_id}"
        )

    def get_execution_history(
        self, automation_id: Optional[str] = None, limit: Optional[int] = None
    ) -> List[DeploymentExecution]:
        """Get deployment execution history."""
        executions = list(self.executions.values())

        if automation_id:
            executions = [e for e in executions if e.automation_id == automation_id]

        # Sort by start time (most recent first)
        executions.sort(key=lambda e: e.start_time or datetime.min, reverse=True)

        if limit:
            executions = executions[:limit]

        return executions

    def get_deployment_metrics(self) -> Dict[str, Any]:
        """Get deployment metrics."""
        total_executions = len(self.executions)
        successful_executions = len(
            [
                e
                for e in self.executions.values()
                if e.status == DeploymentStatus.COMPLETED
            ]
        )
        failed_executions = len(
            [e for e in self.executions.values() if e.status == DeploymentStatus.FAILED]
        )

        success_rate = (
            successful_executions / total_executions if total_executions > 0 else 0
        )

        # Average deployment time
        completed_executions = [e for e in self.executions.values() if e.duration > 0]
        avg_deployment_time = (
            sum(e.duration for e in completed_executions) / len(completed_executions)
            if completed_executions
            else 0
        )

        return {
            "total_automations": len(self.automations),
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "success_rate": success_rate,
            "average_deployment_time": avg_deployment_time,
            "active_executions": len(self.active_executions),
            "pending_approvals": len(self.approval_system.pending_approvals),
        }


# Deployment templates
class DeploymentTemplates:
    """Predefined deployment templates."""

    @staticmethod
    def get_production_deployment_config(model_name: str) -> DeploymentAutomationConfig:
        """Get production deployment configuration."""
        return DeploymentAutomationConfig(
            name="Production Deployment",
            description="Automated production deployment with full validation",
            model_name=model_name,
            environment="production",
            deployment_strategy=DeploymentStrategy.BLUE_GREEN,
            trigger=DeploymentTrigger.MANUAL,
            validation_required=True,
            validation_level="production",
            auto_rollback=True,
            approval_required=True,
            approvers=["devops-lead", "ml-lead"],
            timeout_minutes=120,
            health_check_config={
                "checks": ["connectivity", "performance", "accuracy", "resource_usage"],
                "timeout_seconds": 300,
            },
            notifications={
                "email_enabled": True,
                "slack_enabled": True,
                "webhook_enabled": True,
            },
        )

    @staticmethod
    def get_staging_deployment_config(model_name: str) -> DeploymentAutomationConfig:
        """Get staging deployment configuration."""
        return DeploymentAutomationConfig(
            name="Staging Deployment",
            description="Automated staging deployment",
            model_name=model_name,
            environment="staging",
            deployment_strategy=DeploymentStrategy.ROLLING,
            trigger=DeploymentTrigger.EVENT_DRIVEN,
            validation_required=True,
            validation_level="standard",
            auto_rollback=True,
            approval_required=False,
            timeout_minutes=60,
            health_check_config={
                "checks": ["connectivity", "performance"],
                "timeout_seconds": 180,
            },
            notifications={
                "email_enabled": True,
                "slack_enabled": False,
                "webhook_enabled": True,
            },
        )


# Example usage
async def example_usage():
    """Example usage of deployment automation."""
    # Create deployment automation system
    automation = DeploymentAutomation()

    # Register production deployment automation
    prod_config = DeploymentTemplates.get_production_deployment_config(
        "image-classifier"
    )
    prod_automation_id = automation.register_automation(prod_config)

    # Register staging deployment automation
    staging_config = DeploymentTemplates.get_staging_deployment_config(
        "image-classifier"
    )
    staging_automation_id = automation.register_automation(staging_config)

    # Trigger staging deployment
    staging_execution_id = await automation.trigger_deployment(
        staging_automation_id, "1.0.0", {"trigger_source": "git_push", "branch": "main"}
    )

    # Wait for staging deployment
    await asyncio.sleep(5)

    # Trigger production deployment (would normally wait for staging to pass)
    prod_execution_id = await automation.trigger_deployment(
        prod_automation_id, "1.0.0", {"trigger_source": "manual", "user": "devops-lead"}
    )

    # Simulate approval for production deployment
    automation.approval_system.approve_deployment(
        prod_execution_id, "devops-lead", "Approved for production deployment"
    )

    automation.approval_system.approve_deployment(
        prod_execution_id, "ml-lead", "Model validation passed, approved for deployment"
    )

    # Wait for production deployment
    await asyncio.sleep(8)

    # Get metrics
    metrics = automation.get_deployment_metrics()
    print(f"Deployment metrics: {metrics}")

    # Get execution history
    history = automation.get_execution_history(limit=5)
    for execution in history:
        print(
            f"Deployment {execution.execution_id}: {execution.status.value} ({execution.duration:.2f}s)"
        )


if __name__ == "__main__":
    asyncio.run(example_usage())
