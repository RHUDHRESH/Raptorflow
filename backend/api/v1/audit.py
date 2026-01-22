"""
Audit trail API endpoints
Provides access to audit logs and compliance reporting
"""

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.core.audit import get_audit_logger
from backend.core.auth import get_current_user, get_workspace_id
from backend.core.models import User

router = APIRouter()


@router.get("/audit/trail")
async def get_audit_trail(
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
):
    """
    Get audit trail for workspace with filtering options

    Args:
        limit: Maximum number of records to return
        offset: Number of records to skip
        action: Filter by specific action
        resource_type: Filter by resource type
        start_date: Filter by start date
        end_date: Filter by end date
    """
    audit_logger = get_audit_logger()

    # Get workspace audit trail
    audit_trail = await audit_logger.get_workspace_audit_trail(
        workspace_id=workspace_id, limit=limit, offset=offset
    )

    # Apply filters if specified
    if action:
        audit_trail = [
            record for record in audit_trail if record.get("action") == action
        ]

    if resource_type:
        audit_trail = [
            record
            for record in audit_trail
            if record.get("resource_type") == resource_type
        ]

    if start_date:
        audit_trail = [
            record
            for record in audit_trail
            if datetime.fromisoformat(record.get("created_at", "")) >= start_date
        ]

    if end_date:
        audit_trail = [
            record
            for record in audit_trail
            if datetime.fromisoformat(record.get("created_at", "")) <= end_date
        ]

    return {
        "audit_trail": audit_trail,
        "total": len(audit_trail),
        "limit": limit,
        "offset": offset,
        "filters": {
            "action": action,
            "resource_type": resource_type,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
        },
    }


@router.get("/audit/user/{user_id}")
async def get_user_audit_trail(
    user_id: str,
    current_user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """
    Get audit trail for specific user (admin only)

    Args:
        user_id: Target user ID
        limit: Maximum number of records
        offset: Number of records to skip
    """
    # Check if user has admin permissions
    if not current_user.subscription_tier in ["pro", "enterprise"]:
        raise HTTPException(
            status_code=403, detail="Admin access required for user audit trails"
        )

    audit_logger = get_audit_logger()

    # Get user audit trail
    audit_trail = await audit_logger.get_user_audit_trail(
        user_id=user_id, workspace_id=workspace_id, limit=limit, offset=offset
    )

    return {
        "user_id": user_id,
        "audit_trail": audit_trail,
        "total": len(audit_trail),
        "limit": limit,
        "offset": offset,
    }


@router.get("/audit/stats")
async def get_audit_statistics(
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    days: int = Query(30, ge=1, le=365),
):
    """
    Get audit statistics for compliance reporting

    Args:
        days: Number of days to analyze
    """
    audit_logger = get_audit_logger()

    # Get audit trail for the specified period
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    audit_trail = await audit_logger.get_workspace_audit_trail(
        workspace_id=workspace_id,
        limit=10000,  # Get more records for statistics
        offset=0,
    )

    # Filter by date range
    filtered_trail = [
        record
        for record in audit_trail
        if start_date
        <= datetime.fromisoformat(record.get("created_at", ""))
        <= end_date
    ]

    # Calculate statistics
    stats = {
        "period_days": days,
        "total_events": len(filtered_trail),
        "successful_events": len([r for r in filtered_trail if r.get("success", True)]),
        "failed_events": len([r for r in filtered_trail if not r.get("success", True)]),
        "unique_users": len(
            set(r.get("user_id") for r in filtered_trail if r.get("user_id"))
        ),
        "actions_by_type": {},
        "resources_by_type": {},
        "events_by_day": {},
        "top_ip_addresses": {},
        "error_summary": {},
    }

    # Calculate action breakdown
    for record in filtered_trail:
        action = record.get("action", "unknown")
        stats["actions_by_type"][action] = stats["actions_by_type"].get(action, 0) + 1

        resource_type = record.get("resource_type", "unknown")
        stats["resources_by_type"][resource_type] = (
            stats["resources_by_type"].get(resource_type, 0) + 1
        )

        # Daily breakdown
        created_at = record.get("created_at", "")
        if created_at:
            date = datetime.fromisoformat(created_at).date().isoformat()
            stats["events_by_day"][date] = stats["events_by_day"].get(date, 0) + 1

        # IP address tracking
        ip_address = record.get("ip_address")
        if ip_address:
            stats["top_ip_addresses"][ip_address] = (
                stats["top_ip_addresses"].get(ip_address, 0) + 1
            )

        # Error summary
        if not record.get("success", True):
            error_msg = record.get("error_message", "Unknown error")
            stats["error_summary"][error_msg] = (
                stats["error_summary"].get(error_msg, 0) + 1
            )

    # Sort and limit top items
    stats["top_ip_addresses"] = dict(
        sorted(stats["top_ip_addresses"].items(), key=lambda x: x[1], reverse=True)[:10]
    )
    stats["error_summary"] = dict(
        sorted(stats["error_summary"].items(), key=lambda x: x[1], reverse=True)[:10]
    )

    return stats


@router.get("/audit/compliance")
async def get_compliance_report(
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    report_type: str = Query("summary", regex="^(summary|detailed|export)$"),
    format: str = Query("json", regex="^(json|csv)$"),
):
    """
    Generate compliance reports for audit purposes

    Args:
        report_type: Type of report (summary, detailed, export)
        format: Output format (json, csv)
    """
    audit_logger = get_audit_logger()

    # Get comprehensive audit data
    audit_trail = await audit_logger.get_workspace_audit_trail(
        workspace_id=workspace_id,
        limit=50000,  # Large limit for compliance reports
        offset=0,
    )

    if report_type == "summary":
        # Generate summary report
        report = {
            "workspace_id": workspace_id,
            "report_type": "summary",
            "generated_at": datetime.utcnow().isoformat(),
            "total_events": len(audit_trail),
            "date_range": {
                "earliest": (
                    min(r.get("created_at") for r in audit_trail)
                    if audit_trail
                    else None
                ),
                "latest": (
                    max(r.get("created_at") for r in audit_trail)
                    if audit_trail
                    else None
                ),
            },
            "user_activity": {
                "unique_users": len(
                    set(r.get("user_id") for r in audit_trail if r.get("user_id"))
                ),
                "total_actions": len(audit_trail),
                "success_rate": (
                    len([r for r in audit_trail if r.get("success", True)])
                    / len(audit_trail)
                    * 100
                    if audit_trail
                    else 0
                ),
            },
            "security_events": {
                "failed_authentications": len(
                    [r for r in audit_trail if r.get("action") == "failed_auth"]
                ),
                "rate_limit_violations": len(
                    [r for r in audit_trail if r.get("action") == "rate_limit_exceeded"]
                ),
                "suspicious_activities": len(
                    [r for r in audit_trail if not r.get("success", True)]
                ),
            },
        }

    elif report_type == "detailed":
        # Generate detailed report
        report = {
            "workspace_id": workspace_id,
            "report_type": "detailed",
            "generated_at": datetime.utcnow().isoformat(),
            "audit_events": audit_trail,
            "statistics": {
                "actions_by_type": {},
                "resources_by_type": {},
                "users_by_activity": {},
                "ip_addresses": {},
            },
        }

        # Calculate detailed statistics
        for record in audit_trail:
            action = record.get("action", "unknown")
            report["statistics"]["actions_by_type"][action] = (
                report["statistics"]["actions_by_type"].get(action, 0) + 1
            )

            resource_type = record.get("resource_type", "unknown")
            report["statistics"]["resources_by_type"][resource_type] = (
                report["statistics"]["resources_by_type"].get(resource_type, 0) + 1
            )

            user_id = record.get("user_id")
            if user_id:
                report["statistics"]["users_by_activity"][user_id] = (
                    report["statistics"]["users_by_activity"].get(user_id, 0) + 1
                )

            ip_address = record.get("ip_address")
            if ip_address:
                report["statistics"]["ip_addresses"][ip_address] = (
                    report["statistics"]["ip_addresses"].get(ip_address, 0) + 1
                )

    else:  # export
        # Generate export report
        report = {
            "workspace_id": workspace_id,
            "report_type": "export",
            "generated_at": datetime.utcnow().isoformat(),
            "export_data": audit_trail,
        }

    # Handle CSV format if requested
    if format == "csv":
        import csv
        import io

        output = io.StringIO()

        if report_type == "summary":
            writer = csv.writer(output)
            writer.writerow(["Metric", "Value"])
            for key, value in report.items():
                if isinstance(value, (str, int, float)):
                    writer.writerow([key, value])
                elif isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        writer.writerow([f"{key}.{sub_key}", sub_value])

        elif report_type in ["detailed", "export"]:
            writer = csv.writer(output)
            # Write header
            if audit_trail:
                headers = list(audit_trail[0].keys())
                writer.writerow(headers)

                # Write data
                for record in audit_trail:
                    writer.writerow([record.get(h, "") for h in headers])

        return {
            "format": "csv",
            "data": output.getvalue(),
            "filename": f"audit_report_{workspace_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv",
        }

    return report


@router.post("/audit/export")
async def export_audit_data(
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    include_sensitive: bool = Query(False),
):
    """
    Export audit data for external analysis

    Args:
        start_date: Export start date
        end_date: Export end date
        include_sensitive: Whether to include sensitive data
    """
    # Check if user has export permissions
    if not current_user.subscription_tier in ["pro", "enterprise"]:
        raise HTTPException(
            status_code=403, detail="Export requires pro or enterprise subscription"
        )

    audit_logger = get_audit_logger()

    # Get audit trail for date range
    audit_trail = await audit_logger.get_workspace_audit_trail(
        workspace_id=workspace_id, limit=100000, offset=0  # Large limit for export
    )

    # Filter by date range
    filtered_trail = [
        record
        for record in audit_trail
        if start_date
        <= datetime.fromisoformat(record.get("created_at", ""))
        <= end_date
    ]

    # Remove sensitive data if requested
    if not include_sensitive:
        for record in filtered_trail:
            # Remove potentially sensitive fields
            record.pop("details", None)
            record.pop("user_agent", None)
            if "ip_address" in record:
                # Mask IP address
                ip = record["ip_address"]
                if "." in ip:
                    parts = ip.split(".")
                    record["ip_address"] = f"{parts[0]}.{parts[1]}.***.***"

    return {
        "export_info": {
            "workspace_id": workspace_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_records": len(filtered_trail),
            "include_sensitive": include_sensitive,
            "exported_at": datetime.utcnow().isoformat(),
        },
        "data": filtered_trail,
    }
