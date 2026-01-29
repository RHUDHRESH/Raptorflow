"""
Export jobs for Raptorflow.

Provides background jobs for workspace exports,
analytics exports, and long-running data export tasks.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from decorators import background_job, daily_job, hourly_job, job, weekly_job
from infrastructure.cloud_monitoring import get_cloud_monitoring
from infrastructure.logging import get_cloud_logging

from .models import JobResult, JobStatus

logger = logging.getLogger(__name__)


@dataclass
class WorkspaceExportResult:
    """Result of workspace export operation."""

    workspace_id: str
    export_id: str
    format: str
    data_types: List[str]
    file_size_mb: float
    file_path: str
    download_url: str
    expires_at: str
    processing_time_seconds: float
    records_exported: int
    errors: List[str]


@dataclass
class AnalyticsExportResult:
    """Result of analytics export operation."""

    workspace_id: str
    export_id: str
    period_start: str
    period_end: str
    metrics: List[str]
    format: str
    file_size_mb: float
    file_path: str
    download_url: str
    expires_at: str
    processing_time_seconds: float
    data_points: int
    errors: List[str]


@dataclass
class BulkExportResult:
    """Result of bulk export operation."""

    export_id: str
    workspaces: List[str]
    data_types: List[str]
    format: str
    total_size_mb: float
    files_created: List[str]
    download_urls: List[str]
    expires_at: str
    processing_time_seconds: float
    total_records: int
    errors: List[str]


@dataclass
class ScheduledExportResult:
    """Result of scheduled export operation."""

    workspace_id: str
    schedule_id: str
    export_type: str
    recipients: List[str]
    format: str
    file_size_mb: float
    file_path: str
    delivery_status: Dict[str, str]
    processing_time_seconds: float
    records_exported: int
    errors: List[str]


class ExportJobs:
    """Export job implementations."""

    def __init__(self):
        self.logger = logging.getLogger("export_jobs")
        self.logging = get_cloud_logging()
        self.monitoring = get_cloud_monitoring()

    async def export_workspace_job(
        self,
        workspace_id: str,
        format: str = "json",
        data_types: Optional[List[str]] = None,
    ) -> WorkspaceExportResult:
        """Export workspace data."""
        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                f"Starting workspace export for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "format": format,
                    "data_types": data_types,
                    "job_type": "export_workspace",
                    "started_at": start_time.isoformat(),
                },
            )

            # Get export service
            from export.export_service import get_export_service

            export_service = get_export_service()

            # Create export record
            export_record = await export_service.create_export_record(
                workspace_id, "workspace", format, data_types
            )
            export_id = export_record.get("export_id")

            # Get workspace data
            if data_types is None:
                data_types = [
                    "users",
                    "sessions",
                    "agents",
                    "executions",
                    "content",
                    "analytics",
                ]

            # Export data
            export_result = await export_service.export_workspace_data(
                workspace_id, data_types, format, export_id
            )

            # Extract results
            file_path = export_result.get("file_path")
            file_size_mb = export_result.get("file_size_mb", 0.0)
            download_url = export_result.get("download_url")
            expires_at = export_result.get("expires_at")
            records_exported = export_result.get("records_exported", 0)

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            result = WorkspaceExportResult(
                workspace_id=workspace_id,
                export_id=export_id,
                format=format,
                data_types=data_types,
                file_size_mb=file_size_mb,
                file_path=file_path,
                download_url=download_url,
                expires_at=expires_at,
                processing_time_seconds=processing_time,
                records_exported=records_exported,
                errors=errors,
            )

            # Record metrics
            await self.monitoring.record_metric(
                "workspace_export_file_size",
                file_size_mb,
                {"workspace_id": workspace_id, "format": format},
            )

            await self.monitoring.record_metric(
                "workspace_export_records",
                records_exported,
                {"workspace_id": workspace_id, "format": format},
            )

            await self.monitoring.record_metric(
                "workspace_export_processing_time",
                processing_time,
                {"workspace_id": workspace_id, "format": format},
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                f"Workspace export completed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "export_id": export_id,
                    "format": format,
                    "file_size_mb": file_size_mb,
                    "records_exported": records_exported,
                    "processing_time_seconds": processing_time,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Workspace export failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                f"Workspace export failed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "format": format,
                    "error": str(e),
                    "processing_time_seconds": processing_time,
                },
            )

            raise

    async def export_analytics_job(
        self,
        workspace_id: str,
        period_start: str,
        period_end: str,
        metrics: Optional[List[str]] = None,
        format: str = "csv",
    ) -> AnalyticsExportResult:
        """Export analytics data."""
        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                f"Starting analytics export for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "period_start": period_start,
                    "period_end": period_end,
                    "metrics": metrics,
                    "format": format,
                    "job_type": "export_analytics",
                    "started_at": start_time.isoformat(),
                },
            )

            # Get export service
            from export.export_service import get_export_service

            export_service = get_export_service()

            # Create export record
            export_record = await export_service.create_export_record(
                workspace_id, "analytics", format, metrics
            )
            export_id = export_record.get("export_id")

            # Get analytics metrics
            if metrics is None:
                metrics = [
                    "sessions",
                    "agent_executions",
                    "api_requests",
                    "usage",
                    "performance",
                    "errors",
                ]

            # Export analytics data
            export_result = await export_service.export_analytics_data(
                workspace_id, period_start, period_end, metrics, format, export_id
            )

            # Extract results
            file_path = export_result.get("file_path")
            file_size_mb = export_result.get("file_size_mb", 0.0)
            download_url = export_result.get("download_url")
            expires_at = export_result.get("expires_at")
            data_points = export_result.get("data_points", 0)

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            result = AnalyticsExportResult(
                workspace_id=workspace_id,
                export_id=export_id,
                period_start=period_start,
                period_end=period_end,
                metrics=metrics,
                format=format,
                file_size_mb=file_size_mb,
                file_path=file_path,
                download_url=download_url,
                expires_at=expires_at,
                processing_time_seconds=processing_time,
                data_points=data_points,
                errors=errors,
            )

            # Record metrics
            await self.monitoring.record_metric(
                "analytics_export_file_size",
                file_size_mb,
                {"workspace_id": workspace_id, "format": format},
            )

            await self.monitoring.record_metric(
                "analytics_export_data_points",
                data_points,
                {"workspace_id": workspace_id, "format": format},
            )

            await self.monitoring.record_metric(
                "analytics_export_processing_time",
                processing_time,
                {"workspace_id": workspace_id, "format": format},
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                f"Analytics export completed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "export_id": export_id,
                    "period_start": period_start,
                    "period_end": period_end,
                    "file_size_mb": file_size_mb,
                    "data_points": data_points,
                    "processing_time_seconds": processing_time,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Analytics export failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                f"Analytics export failed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "period_start": period_start,
                    "period_end": period_end,
                    "error": str(e),
                    "processing_time_seconds": processing_time,
                },
            )

            raise

    async def bulk_export_job(
        self, workspace_ids: List[str], data_types: List[str], format: str = "zip"
    ) -> BulkExportResult:
        """Bulk export multiple workspaces."""
        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                f"Starting bulk export for {len(workspace_ids)} workspaces",
                {
                    "workspace_count": len(workspace_ids),
                    "data_types": data_types,
                    "format": format,
                    "job_type": "bulk_export",
                    "started_at": start_time.isoformat(),
                },
            )

            # Get export service
            from export.export_service import get_export_service

            export_service = get_export_service()

            # Create bulk export record
            export_record = await export_service.create_bulk_export_record(
                workspace_ids, data_types, format
            )
            export_id = export_record.get("export_id")

            # Export each workspace
            files_created = []
            download_urls = []
            total_records = 0
            total_size_mb = 0.0

            for workspace_id in workspace_ids:
                try:
                    # Export workspace
                    workspace_export = await export_service.export_workspace_data(
                        workspace_id, data_types, format, f"{export_id}_{workspace_id}"
                    )

                    files_created.append(workspace_export.get("file_path"))
                    download_urls.append(workspace_export.get("download_url"))
                    total_records += workspace_export.get("records_exported", 0)
                    total_size_mb += workspace_export.get("file_size_mb", 0.0)

                except Exception as e:
                    errors.append(
                        f"Failed to export workspace {workspace_id}: {str(e)}"
                    )

            # Create bulk export package
            if format == "zip":
                package_result = await export_service.create_bulk_package(
                    export_id, files_created
                )
                download_urls = [package_result.get("download_url")]
                total_size_mb = package_result.get("file_size_mb", total_size_mb)

            expires_at = export_record.get("expires_at")

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            result = BulkExportResult(
                export_id=export_id,
                workspaces=workspace_ids,
                data_types=data_types,
                format=format,
                total_size_mb=total_size_mb,
                files_created=files_created,
                download_urls=download_urls,
                expires_at=expires_at,
                processing_time_seconds=processing_time,
                total_records=total_records,
                errors=errors,
            )

            # Record metrics
            await self.monitoring.record_metric(
                "bulk_export_total_size",
                total_size_mb,
                {"format": format, "workspace_count": len(workspace_ids)},
            )

            await self.monitoring.record_metric(
                "bulk_export_total_records",
                total_records,
                {"format": format, "workspace_count": len(workspace_ids)},
            )

            await self.monitoring.record_metric(
                "bulk_export_processing_time",
                processing_time,
                {"format": format, "workspace_count": len(workspace_ids)},
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                f"Bulk export completed for {len(workspace_ids)} workspaces",
                {
                    "export_id": export_id,
                    "workspace_count": len(workspace_ids),
                    "total_size_mb": total_size_mb,
                    "total_records": total_records,
                    "processing_time_seconds": processing_time,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Bulk export failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                f"Bulk export failed for {len(workspace_ids)} workspaces",
                {
                    "workspace_count": len(workspace_ids),
                    "error": str(e),
                    "processing_time_seconds": processing_time,
                },
            )

            raise

    async def scheduled_export_job(
        self, workspace_id: str, schedule_id: str
    ) -> ScheduledExportResult:
        """Execute scheduled export."""
        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                f"Starting scheduled export for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "schedule_id": schedule_id,
                    "job_type": "scheduled_export",
                    "started_at": start_time.isoformat(),
                },
            )

            # Get export service
            from export.export_service import get_export_service

            export_service = get_export_service()

            # Get schedule details
            schedule = await export_service.get_export_schedule(schedule_id)

            if not schedule:
                raise ValueError(f"Export schedule not found: {schedule_id}")

            # Execute export based on schedule
            export_type = schedule.get("export_type")
            format = schedule.get("format", "json")
            recipients = schedule.get("recipients", [])

            if export_type == "workspace":
                # Export workspace
                workspace_export = await self.export_workspace_job(
                    workspace_id, format, schedule.get("data_types")
                )

                file_path = workspace_export.file_path
                file_size_mb = workspace_export.file_size_mb
                records_exported = workspace_export.records_exported

            elif export_type == "analytics":
                # Export analytics
                period_start = schedule.get("period_start")
                period_end = schedule.get("period_end")
                metrics = schedule.get("metrics")

                analytics_export = await self.export_analytics_job(
                    workspace_id, period_start, period_end, metrics, format
                )

                file_path = analytics_export.file_path
                file_size_mb = analytics_export.file_size_mb
                records_exported = analytics_export.data_points

            else:
                raise ValueError(f"Unsupported export type: {export_type}")

            # Deliver to recipients
            delivery_status = {}
            for recipient in recipients:
                try:
                    delivery_result = await export_service.deliver_export(
                        recipient, file_path, export_type, workspace_id
                    )
                    delivery_status[recipient] = delivery_result.get(
                        "status", "delivered"
                    )
                except Exception as e:
                    errors.append(f"Failed to deliver to {recipient}: {str(e)}")
                    delivery_status[recipient] = "failed"

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            result = ScheduledExportResult(
                workspace_id=workspace_id,
                schedule_id=schedule_id,
                export_type=export_type,
                recipients=recipients,
                format=format,
                file_size_mb=file_size_mb,
                file_path=file_path,
                delivery_status=delivery_status,
                processing_time_seconds=processing_time,
                records_exported=records_exported,
                errors=errors,
            )

            # Record metrics
            await self.monitoring.record_metric(
                "scheduled_export_delivered",
                len([s for s in delivery_status.values() if s == "delivered"]),
                {"export_type": export_type, "workspace_id": workspace_id},
            )

            await self.monitoring.record_metric(
                "scheduled_export_processing_time",
                processing_time,
                {"export_type": export_type, "workspace_id": workspace_id},
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                f"Scheduled export completed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "schedule_id": schedule_id,
                    "export_type": export_type,
                    "recipients": len(recipients),
                    "file_size_mb": file_size_mb,
                    "processing_time_seconds": processing_time,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Scheduled export failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                f"Scheduled export failed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "schedule_id": schedule_id,
                    "error": str(e),
                    "processing_time_seconds": processing_time,
                },
            )

            raise

    async def cleanup_exports_job(self) -> Dict[str, Any]:
        """Clean up expired exports."""
        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                "Starting export cleanup",
                {"job_type": "cleanup_exports", "started_at": start_time.isoformat()},
            )

            # Get export service
            from export.export_service import get_export_service

            export_service = get_export_service()

            # Get expired exports
            expired_exports = await export_service.get_expired_exports()

            # Clean up expired exports
            cleaned_count = 0
            space_freed_mb = 0.0

            for export in expired_exports:
                try:
                    cleanup_result = await export_service.cleanup_export(
                        export.get("export_id")
                    )
                    if cleanup_result.get("success", False):
                        cleaned_count += 1
                        space_freed_mb += cleanup_result.get("space_freed_mb", 0.0)
                except Exception as e:
                    errors.append(
                        f"Failed to cleanup export {export.get('export_id')}: {str(e)}"
                    )

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            result = {
                "expired_exports_found": len(expired_exports),
                "exports_cleaned": cleaned_count,
                "space_freed_mb": space_freed_mb,
                "processing_time_seconds": processing_time,
                "errors": errors,
            }

            # Record metrics
            await self.monitoring.record_metric(
                "export_cleanup_count", cleaned_count, {"operation": "cleanup"}
            )

            await self.monitoring.record_metric(
                "export_cleanup_space_freed", space_freed_mb, {"operation": "cleanup"}
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                "Export cleanup completed",
                {
                    "expired_exports_found": len(expired_exports),
                    "exports_cleaned": cleaned_count,
                    "space_freed_mb": space_freed_mb,
                    "processing_time_seconds": processing_time,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Export cleanup failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                "Export cleanup failed",
                {"error": str(e), "processing_time_seconds": processing_time},
            )

            raise


# Create global instance
_export_jobs = ExportJobs()


# Job implementations with decorators
@background_job(
    queue="exports",
    retries=1,
    timeout=3600,  # 1 hour
    description="Export workspace data",
)
async def export_workspace_job(
    workspace_id: str, format: str = "json", data_types: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Export workspace job."""
    result = await _export_jobs.export_workspace_job(workspace_id, format, data_types)
    return result.__dict__


@background_job(
    queue="exports",
    retries=1,
    timeout=3600,  # 1 hour
    description="Export analytics data",
)
async def export_analytics_job(
    workspace_id: str,
    period_start: str,
    period_end: str,
    metrics: Optional[List[str]] = None,
    format: str = "csv",
) -> Dict[str, Any]:
    """Export analytics job."""
    result = await _export_jobs.export_analytics_job(
        workspace_id, period_start, period_end, metrics, format
    )
    return result.__dict__


@background_job(
    queue="exports",
    retries=1,
    timeout=7200,  # 2 hours
    description="Bulk export workspaces",
)
async def bulk_export_job(
    workspace_ids: List[str], data_types: List[str], format: str = "zip"
) -> Dict[str, Any]:
    """Bulk export job."""
    result = await _export_jobs.bulk_export_job(workspace_ids, data_types, format)
    return result.__dict__


@background_job(
    queue="exports",
    retries=1,
    timeout=3600,  # 1 hour
    description="Execute scheduled export",
)
async def scheduled_export_job(workspace_id: str, schedule_id: str) -> Dict[str, Any]:
    """Scheduled export job."""
    result = await _export_jobs.scheduled_export_job(workspace_id, schedule_id)
    return result.__dict__


@daily_job(
    hour=2,
    minute=0,
    queue="exports",
    retries=2,
    timeout=1800,  # 30 minutes
    description="Clean up expired exports",
)
async def cleanup_exports_job() -> Dict[str, Any]:
    """Export cleanup job."""
    result = await _export_jobs.cleanup_exports_job()
    return result


# Convenience functions
async def export_workspace(
    workspace_id: str, format: str = "json", data_types: Optional[List[str]] = None
) -> WorkspaceExportResult:
    """Export workspace data."""
    return await _export_jobs.export_workspace_job(workspace_id, format, data_types)


async def export_analytics(
    workspace_id: str,
    period_start: str,
    period_end: str,
    metrics: Optional[List[str]] = None,
    format: str = "csv",
) -> AnalyticsExportResult:
    """Export analytics data."""
    return await _export_jobs.export_analytics_job(
        workspace_id, period_start, period_end, metrics, format
    )


async def bulk_export_workspaces(
    workspace_ids: List[str], data_types: List[str], format: str = "zip"
) -> BulkExportResult:
    """Bulk export workspaces."""
    return await _export_jobs.bulk_export_job(workspace_ids, data_types, format)


async def execute_scheduled_export(
    workspace_id: str, schedule_id: str
) -> ScheduledExportResult:
    """Execute scheduled export."""
    return await _export_jobs.scheduled_export_job(workspace_id, schedule_id)


async def cleanup_expired_exports() -> Dict[str, Any]:
    """Clean up expired exports."""
    return await _export_jobs.cleanup_exports_job()


# Export all jobs
__all__ = [
    "ExportJobs",
    "export_workspace_job",
    "export_analytics_job",
    "bulk_export_job",
    "scheduled_export_job",
    "cleanup_exports_job",
    "export_workspace",
    "export_analytics",
    "bulk_export_workspaces",
    "execute_scheduled_export",
    "cleanup_expired_exports",
]
