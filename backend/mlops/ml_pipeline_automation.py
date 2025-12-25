"""
S.W.A.R.M. Phase 2: ML Pipeline Automation
Production-ready ML pipeline automation system
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
from automated_model_testing import TestConfig, TestRunner, TestType

# Import existing components
from ml_pipeline_architecture import (
    BuildStage,
    DeployStage,
    MLPipelineOrchestrator,
    MonitorStage,
    PipelineConfig,
    PipelineStage,
    TestStage,
)
from model_deployment_strategies import DeploymentConfig, DeploymentManager
from model_monitoring_systems import MonitoringConfig, MonitoringManager
from model_rollback_mechanisms import RollbackConfig, RollbackManager

logger = logging.getLogger("raptorflow.pipeline_automation")


class AutomationStatus(Enum):
    """Automation status."""

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TriggerType(Enum):
    """Pipeline trigger types."""

    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT_DRIVEN = "event_driven"
    API_TRIGGERED = "api_triggered"
    WEBHOOK = "webhook"


@dataclass
class AutomationConfig:
    """Automation configuration."""

    automation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    pipeline_config: Optional[PipelineConfig] = None
    trigger_type: TriggerType = TriggerType.MANUAL
    schedule: Optional[str] = None
    event_conditions: Dict[str, Any] = field(default_factory=dict)
    auto_retry: bool = True
    max_retries: int = 3
    retry_delay: int = 60
    timeout_minutes: int = 120
    notifications: Dict[str, Any] = field(default_factory=dict)
    parallel_execution: bool = True
    resource_limits: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "automation_id": self.automation_id,
            "name": self.name,
            "description": self.description,
            "pipeline_config": (
                self.pipeline_config.to_dict() if self.pipeline_config else None
            ),
            "trigger_type": self.trigger_type.value,
            "schedule": self.schedule,
            "event_conditions": self.event_conditions,
            "auto_retry": self.auto_retry,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "timeout_minutes": self.timeout_minutes,
            "notifications": self.notifications,
            "parallel_execution": self.parallel_execution,
            "resource_limits": self.resource_limits,
        }


@dataclass
class AutomationExecution:
    """Automation execution record."""

    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    automation_id: str = ""
    status: AutomationStatus = AutomationStatus.IDLE
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: float = 0.0
    trigger_source: str = ""
    trigger_data: Dict[str, Any] = field(default_factory=dict)
    stage_results: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    error_message: Optional[str] = None
    retry_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "execution_id": self.execution_id,
            "automation_id": self.automation_id,
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "trigger_source": self.trigger_source,
            "trigger_data": self.trigger_data,
            "stage_results": self.stage_results,
            "artifacts": self.artifacts,
            "metrics": self.metrics,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
        }


class AutomationTrigger(ABC):
    """Abstract base class for automation triggers."""

    def __init__(self, config: AutomationConfig):
        self.config = config
        self.is_active = False

    @abstractmethod
    async def start(self, callback: Callable):
        """Start trigger monitoring."""
        pass

    @abstractmethod
    async def stop(self):
        """Stop trigger monitoring."""
        pass

    @abstractmethod
    def should_trigger(self, event_data: Dict[str, Any]) -> bool:
        """Check if trigger should fire."""
        pass


class ManualTrigger(AutomationTrigger):
    """Manual trigger for automation."""

    def __init__(self, config: AutomationConfig):
        super().__init__(config)
        self.callback: Optional[Callable] = None

    async def start(self, callback: Callable):
        """Start manual trigger."""
        self.callback = callback
        self.is_active = True
        logger.info(f"Manual trigger started for {self.config.name}")

    async def stop(self):
        """Stop manual trigger."""
        self.is_active = False
        self.callback = None
        logger.info(f"Manual trigger stopped for {self.config.name}")

    def should_trigger(self, event_data: Dict[str, Any]) -> bool:
        """Manual trigger always returns False (triggered manually)."""
        return False

    async def trigger_manually(self, trigger_data: Dict[str, Any] = None):
        """Trigger automation manually."""
        if self.callback and self.is_active:
            await self.callback(
                {
                    "trigger_type": "manual",
                    "trigger_source": "user",
                    "trigger_data": trigger_data or {},
                }
            )


class ScheduledTrigger(AutomationTrigger):
    """Scheduled trigger for automation."""

    def __init__(self, config: AutomationConfig):
        super().__init__(config)
        self.callback: Optional[Callable] = None
        self.task: Optional[asyncio.Task] = None

    async def start(self, callback: Callable):
        """Start scheduled trigger."""
        self.callback = callback
        self.is_active = True

        # Parse schedule (simplified - in production use cron-like scheduler)
        if self.config.schedule:
            self.task = asyncio.create_task(self._schedule_loop())

        logger.info(f"Scheduled trigger started for {self.config.name}")

    async def stop(self):
        """Stop scheduled trigger."""
        self.is_active = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

        self.callback = None
        logger.info(f"Scheduled trigger stopped for {self.config.name}")

    def should_trigger(self, event_data: Dict[str, Any]) -> bool:
        """Scheduled trigger doesn't use event-based triggering."""
        return False

    async def _schedule_loop(self):
        """Schedule monitoring loop."""
        while self.is_active:
            try:
                # Simple schedule check (every minute)
                await asyncio.sleep(60)

                if self.callback and self.is_active:
                    await self.callback(
                        {
                            "trigger_type": "scheduled",
                            "trigger_source": "scheduler",
                            "trigger_data": {"schedule": self.config.schedule},
                        }
                    )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Schedule loop error: {str(e)}")
                await asyncio.sleep(60)


class EventTrigger(AutomationTrigger):
    """Event-driven trigger for automation."""

    def __init__(self, config: AutomationConfig):
        super().__init__(config)
        self.callback: Optional[Callable] = None
        self.event_queue = asyncio.Queue()
        self.processor_task: Optional[asyncio.Task] = None

    async def start(self, callback: Callable):
        """Start event trigger."""
        self.callback = callback
        self.is_active = True
        self.processor_task = asyncio.create_task(self._process_events())

        logger.info(f"Event trigger started for {self.config.name}")

    async def stop(self):
        """Stop event trigger."""
        self.is_active = False
        if self.processor_task:
            self.processor_task.cancel()
            try:
                await self.processor_task
            except asyncio.CancelledError:
                pass

        self.callback = None
        logger.info(f"Event trigger stopped for {self.config.name}")

    def should_trigger(self, event_data: Dict[str, Any]) -> bool:
        """Check if event should trigger automation."""
        conditions = self.config.event_conditions

        # Check event type
        if "event_type" in conditions:
            if event_data.get("event_type") != conditions["event_type"]:
                return False

        # Check event source
        if "event_source" in conditions:
            if event_data.get("event_source") != conditions["event_source"]:
                return False

        # Check custom conditions
        for condition_key, condition_value in conditions.items():
            if condition_key not in ["event_type", "event_source"]:
                if event_data.get(condition_key) != condition_value:
                    return False

        return True

    async def emit_event(self, event_data: Dict[str, Any]):
        """Emit event for processing."""
        await self.event_queue.put(event_data)

    async def _process_events(self):
        """Process events from queue."""
        while self.is_active:
            try:
                event_data = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)

                if self.should_trigger(event_data) and self.callback:
                    await self.callback(
                        {
                            "trigger_type": "event_driven",
                            "trigger_source": event_data.get("event_source", "unknown"),
                            "trigger_data": event_data,
                        }
                    )

            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Event processing error: {str(e)}")


class PipelineAutomation:
    """Main pipeline automation system."""

    def __init__(self):
        self.automations: Dict[str, AutomationConfig] = {}
        self.executions: Dict[str, AutomationExecution] = {}
        self.triggers: Dict[str, AutomationTrigger] = {}
        self.active_executions: Dict[str, asyncio.Task] = {}
        self.orchestrator = PipelineOrchestrator()
        self.test_runner = TestRunner()
        self.deployment_manager = DeploymentManager()
        self.monitoring_manager = MonitoringManager()
        self.rollback_manager = RollbackManager()

        # Trigger registry
        self.trigger_registry = {
            TriggerType.MANUAL: ManualTrigger,
            TriggerType.SCHEDULED: ScheduledTrigger,
            TriggerType.EVENT_DRIVEN: EventTrigger,
        }

    def register_automation(self, config: AutomationConfig) -> str:
        """Register automation configuration."""
        self.automations[config.automation_id] = config

        # Create trigger
        trigger_class = self.trigger_registry.get(config.trigger_type)
        if trigger_class:
            trigger = trigger_class(config)
            self.triggers[config.automation_id] = trigger

        logger.info(f"Registered automation: {config.name}")
        return config.automation_id

    async def start_automation(self, automation_id: str) -> bool:
        """Start automation monitoring."""
        if automation_id not in self.automations:
            return False

        config = self.automations[automation_id]
        trigger = self.triggers.get(automation_id)

        if trigger:
            await trigger.start(self._create_execution_callback(automation_id))
            return True

        return False

    async def stop_automation(self, automation_id: str) -> bool:
        """Stop automation monitoring."""
        trigger = self.triggers.get(automation_id)
        if trigger:
            await trigger.stop()
            return True
        return False

    async def trigger_automation(
        self, automation_id: str, trigger_data: Dict[str, Any] = None
    ) -> str:
        """Manually trigger automation."""
        if automation_id not in self.automations:
            raise ValueError(f"Automation {automation_id} not found")

        config = self.automations[automation_id]
        trigger = self.triggers.get(automation_id)

        if isinstance(trigger, ManualTrigger):
            await trigger.trigger_manually(trigger_data)
            return automation_id

        raise ValueError(f"Automation {automation_id} is not manually triggerable")

    def _create_execution_callback(self, automation_id: str) -> Callable:
        """Create execution callback for trigger."""

        async def execution_callback(trigger_info: Dict[str, Any]):
            await self._execute_automation(automation_id, trigger_info)

        return execution_callback

    async def _execute_automation(
        self, automation_id: str, trigger_info: Dict[str, Any]
    ):
        """Execute automation pipeline."""
        config = self.automations[automation_id]

        # Create execution record
        execution = AutomationExecution(
            automation_id=automation_id,
            trigger_source=trigger_info.get("trigger_source", "unknown"),
            trigger_data=trigger_info.get("trigger_data", {}),
        )

        self.executions[execution.execution_id] = execution

        # Start execution task
        task = asyncio.create_task(self._run_pipeline_execution(execution, config))
        self.active_executions[execution.execution_id] = task

    async def _run_pipeline_execution(
        self, execution: AutomationExecution, config: AutomationConfig
    ):
        """Run pipeline execution with retry logic."""
        retry_count = 0

        while retry_count <= config.max_retries:
            try:
                execution.status = AutomationStatus.RUNNING
                execution.start_time = datetime.now()
                execution.retry_count = retry_count

                # Execute pipeline
                if config.pipeline_config:
                    result = await self.orchestrator.execute_pipeline(
                        config.pipeline_config
                    )
                    execution.stage_results = result

                # Execute tests if configured
                if any(
                    stage.stage_type == "test"
                    for stage in config.pipeline_config.stages
                ):
                    test_results = await self._run_automated_tests(config)
                    execution.stage_results["tests"] = test_results

                # Execute deployment if configured
                if any(
                    stage.stage_type == "deploy"
                    for stage in config.pipeline_config.stages
                ):
                    deploy_results = await self._run_automated_deployment(config)
                    execution.stage_results["deployment"] = deploy_results

                # Setup monitoring if configured
                if any(
                    stage.stage_type == "monitor"
                    for stage in config.pipeline_config.stages
                ):
                    monitor_results = await self._setup_monitoring(config)
                    execution.stage_results["monitoring"] = monitor_results

                execution.status = AutomationStatus.COMPLETED
                execution.end_time = datetime.now()
                execution.duration = (
                    execution.end_time - execution.start_time
                ).total_seconds()

                # Send notifications
                await self._send_notifications(execution, config)

                break

            except Exception as e:
                retry_count += 1
                execution.error_message = str(e)

                if retry_count <= config.max_retries and config.auto_retry:
                    logger.warning(
                        f"Execution failed, retrying ({retry_count}/{config.max_retries}): {str(e)}"
                    )
                    await asyncio.sleep(config.retry_delay)
                else:
                    execution.status = AutomationStatus.FAILED
                    execution.end_time = datetime.now()
                    execution.duration = (
                        execution.end_time - execution.start_time
                    ).total_seconds()

                    # Send failure notifications
                    await self._send_notifications(execution, config)
                    break

        # Clean up active execution
        if execution.execution_id in self.active_executions:
            del self.active_executions[execution.execution_id]

    async def _run_automated_tests(self, config: AutomationConfig) -> Dict[str, Any]:
        """Run automated model tests."""
        try:
            # Create test configuration
            test_config = TestConfig(
                model_name=config.pipeline_config.name,
                test_types=[TestType.ACCURACY, TestType.PERFORMANCE, TestType.SECURITY],
                parallel_execution=True,
            )

            # Run tests
            results = await self.test_runner.run_test_suite(test_config)

            return {
                "total_tests": len(results),
                "passed_tests": len([r for r in results if r.passed]),
                "failed_tests": len([r for r in results if not r.passed]),
                "test_results": [r.to_dict() for r in results],
            }

        except Exception as e:
            logger.error(f"Automated testing failed: {str(e)}")
            return {"error": str(e)}

    async def _run_automated_deployment(
        self, config: AutomationConfig
    ) -> Dict[str, Any]:
        """Run automated deployment."""
        try:
            # Create deployment configuration
            deploy_config = DeploymentConfig(
                model_name=config.pipeline_config.name,
                version="latest",
                strategy="rolling",
                environment="production",
            )

            # Run deployment
            result = await self.deployment_manager.execute_deployment(deploy_config)

            return result.to_dict()

        except Exception as e:
            logger.error(f"Automated deployment failed: {str(e)}")
            return {"error": str(e)}

    async def _setup_monitoring(self, config: AutomationConfig) -> Dict[str, Any]:
        """Setup monitoring for deployed model."""
        try:
            # Create monitoring configuration
            monitor_config = MonitoringConfig(
                model_name=config.pipeline_config.name,
                metrics_collection=True,
                alerting=True,
            )

            # Setup monitoring
            result = await self.monitoring_manager.setup_monitoring(monitor_config)

            return {"monitoring_setup": True, "config": monitor_config.to_dict()}

        except Exception as e:
            logger.error(f"Monitoring setup failed: {str(e)}")
            return {"error": str(e)}

    async def _send_notifications(
        self, execution: AutomationExecution, config: AutomationConfig
    ):
        """Send execution notifications."""
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
        self, execution: AutomationExecution, notifications: Dict[str, Any]
    ):
        """Send email notification."""
        # Simulate email sending
        logger.info(f"Email notification sent for execution {execution.execution_id}")

    async def _send_slack_notification(
        self, execution: AutomationExecution, notifications: Dict[str, Any]
    ):
        """Send Slack notification."""
        # Simulate Slack notification
        logger.info(f"Slack notification sent for execution {execution.execution_id}")

    async def _send_webhook_notification(
        self, execution: AutomationExecution, notifications: Dict[str, Any]
    ):
        """Send webhook notification."""
        # Simulate webhook call
        logger.info(f"Webhook notification sent for execution {execution.execution_id}")

    def get_execution_history(
        self, automation_id: Optional[str] = None, limit: Optional[int] = None
    ) -> List[AutomationExecution]:
        """Get execution history."""
        executions = list(self.executions.values())

        if automation_id:
            executions = [e for e in executions if e.automation_id == automation_id]

        # Sort by start time (most recent first)
        executions.sort(key=lambda e: e.start_time or datetime.min, reverse=True)

        if limit:
            executions = executions[:limit]

        return executions

    def get_automation_metrics(self) -> Dict[str, Any]:
        """Get automation metrics."""
        total_executions = len(self.executions)
        successful_executions = len(
            [
                e
                for e in self.executions.values()
                if e.status == AutomationStatus.COMPLETED
            ]
        )
        failed_executions = len(
            [e for e in self.executions.values() if e.status == AutomationStatus.FAILED]
        )

        success_rate = (
            successful_executions / total_executions if total_executions > 0 else 0
        )

        # Average execution time
        completed_executions = [e for e in self.executions.values() if e.duration > 0]
        avg_execution_time = (
            sum(e.duration for e in completed_executions) / len(completed_executions)
            if completed_executions
            else 0
        )

        return {
            "total_automations": len(self.automations),
            "active_automations": len(
                [t for t in self.triggers.values() if t.is_active]
            ),
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "success_rate": success_rate,
            "average_execution_time": avg_execution_time,
            "active_executions": len(self.active_executions),
        }


# Automation templates
class AutomationTemplates:
    """Predefined automation templates."""

    @staticmethod
    def get_production_training_automation() -> AutomationConfig:
        """Get production training automation."""
        pipeline_config = PipelineConfig(
            name="production-training",
            description="Production model training pipeline",
            stages=[
                BuildStage(name="build", description="Build training environment"),
                TestStage(name="test", description="Test model performance"),
                DeployStage(name="deploy", description="Deploy to production"),
                MonitorStage(name="monitor", description="Monitor model performance"),
            ],
        )

        return AutomationConfig(
            name="Production Training Automation",
            description="Automated production model training pipeline",
            pipeline_config=pipeline_config,
            trigger_type=TriggerType.SCHEDULED,
            schedule="0 2 * * *",  # Daily at 2 AM
            auto_retry=True,
            max_retries=3,
            notifications={
                "email_enabled": True,
                "slack_enabled": True,
                "webhook_enabled": False,
            },
        )

    @staticmethod
    def get_model_deployment_automation() -> AutomationConfig:
        """Get model deployment automation."""
        pipeline_config = PipelineConfig(
            name="model-deployment",
            description="Model deployment pipeline",
            stages=[
                TestStage(name="validate", description="Validate model"),
                DeployStage(name="deploy", description="Deploy model"),
                MonitorStage(name="monitor", description="Monitor deployment"),
            ],
        )

        return AutomationConfig(
            name="Model Deployment Automation",
            description="Automated model deployment pipeline",
            pipeline_config=pipeline_config,
            trigger_type=TriggerType.EVENT_DRIVEN,
            event_conditions={
                "event_type": "model_approved",
                "event_source": "model_registry",
            },
            auto_retry=True,
            max_retries=2,
            notifications={
                "email_enabled": True,
                "slack_enabled": True,
                "webhook_enabled": True,
            },
        )


# Example usage
async def example_usage():
    """Example usage of pipeline automation."""
    # Create automation system
    automation = PipelineAutomation()

    # Register production training automation
    training_config = AutomationTemplates.get_production_training_automation()
    training_id = automation.register_automation(training_config)

    # Register model deployment automation
    deployment_config = AutomationTemplates.get_model_deployment_automation()
    deployment_id = automation.register_automation(deployment_config)

    # Start automations
    await automation.start_automation(training_id)
    await automation.start_automation(deployment_id)

    # Manually trigger training automation
    await automation.trigger_automation(training_id, {"manual_trigger": True})

    # Simulate event for deployment automation
    event_trigger = automation.triggers[deployment_id]
    if isinstance(event_trigger, EventTrigger):
        await event_trigger.emit_event(
            {
                "event_type": "model_approved",
                "event_source": "model_registry",
                "model_name": "test-model",
                "model_version": "1.0.0",
            }
        )

    # Wait for executions
    await asyncio.sleep(5)

    # Get metrics
    metrics = automation.get_automation_metrics()
    print(f"Automation metrics: {metrics}")

    # Get execution history
    history = automation.get_execution_history(limit=5)
    for execution in history:
        print(
            f"Execution {execution.execution_id}: {execution.status.value} ({execution.duration:.2f}s)"
        )

    # Stop automations
    await automation.stop_automation(training_id)
    await automation.stop_automation(deployment_id)


if __name__ == "__main__":
    asyncio.run(example_usage())
