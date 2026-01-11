"""
Approval Audit - Compliance logging and audit trails

Maintains comprehensive audit trails for all approval decisions
with compliance requirements and reporting capabilities.
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ...redis.client import RedisClient
from .models import AuditEntry

logger = logging.getLogger(__name__)


@dataclass
class AuditReport:
    """Audit report for compliance."""

    workspace_id: str
    period_start: datetime
    period_end: datetime
    total_approvals: int
    total_rejections: int
    auto_approvals: int
    escalations: int
    timeouts: int
    average_response_time: float
    compliance_score: float
    entries: List[AuditEntry]


class ApprovalAudit:
    """Maintains approval audit trails."""

    def __init__(self, redis_client: Optional[RedisClient] = None):
        self.redis = redis_client or RedisClient()
        self.audit_key_prefix = "approval_audit:"
        self.report_key_prefix = "audit_report:"

    async def log_decision(
        self,
        gate_id: str,
        decision: str,
        reason: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> bool:
        """
        Log approval decision for audit.

        Args:
            gate_id: Approval gate identifier
            decision: Decision made
            reason: Reason for decision
            user_id: User who made decision
            ip_address: IP address for security
            user_agent: User agent string

        Returns:
            Success status
        """
        try:
            # Get approval request for context
            gate_key = f"approval_gate:{gate_id}"
            request_data = await self.redis.get(gate_key)

            workspace_id = "unknown"
            if request_data:
                request = json.loads(request_data)
                workspace_id = request.get("workspace_id", "unknown")

            # Create audit entry
            entry = AuditEntry(
                gate_id=gate_id,
                action=decision,
                user_id=user_id or "system",
                timestamp=datetime.now(),
                details={
                    "reason": reason,
                    "workspace_id": workspace_id,
                    "ip_address": ip_address,
                    "user_agent": user_agent,
                },
                ip_address=ip_address,
                user_agent=user_agent,
            )

            # Store audit entry
            audit_key = f"{self.audit_key_prefix}{workspace_id}"
            entry_json = json.dumps(asdict(entry), default=str)

            await self.redis.lpush(audit_key, entry_json)
            await self.redis.ltrim(audit_key, 0, 9999)  # Keep last 10,000 entries
            await self.redis.expire(audit_key, 86400 * 365 * 7)  # Keep for 7 years

            logger.info(f"Logged audit entry for gate {gate_id}: {decision}")
            return True

        except Exception as e:
            logger.error(f"Failed to log audit entry: {e}")
            return False

    async def get_audit_trail(
        self,
        workspace_id: str,
        date_range: Optional[Dict[str, datetime]] = None,
        gate_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> List[AuditEntry]:
        """
        Get audit trail for workspace.

        Args:
            workspace_id: Workspace identifier
            date_range: Date range filter
            gate_id: Specific gate filter
            user_id: Specific user filter

        Returns:
            List of audit entries
        """
        try:
            audit_key = f"{self.audit_key_prefix}{workspace_id}"
            entries_data = await self.redis.lrange(audit_key, 0, -1)

            entries = []
            for entry_data in entries_data:
                entry_dict = json.loads(entry_data)

                # Parse timestamp
                entry_dict["timestamp"] = datetime.fromisoformat(
                    entry_dict["timestamp"].replace("Z", "+00:00")
                )

                entry = AuditEntry(**entry_dict)

                # Apply filters
                if date_range:
                    if entry.timestamp < date_range.get(
                        "start"
                    ) or entry.timestamp > date_range.get("end"):
                        continue

                if gate_id and entry.gate_id != gate_id:
                    continue

                if user_id and entry.user_id != user_id:
                    continue

                entries.append(entry)

            # Sort by timestamp (newest first)
            entries.sort(key=lambda x: x.timestamp, reverse=True)

            return entries

        except Exception as e:
            logger.error(f"Failed to get audit trail: {e}")
            return []

    async def generate_compliance_report(
        self, workspace_id: str, start_date: datetime, end_date: datetime
    ) -> AuditReport:
        """
        Generate compliance report for date range.

        Args:
            workspace_id: Workspace identifier
            start_date: Report start date
            end_date: Report end date

        Returns:
            Compliance report
        """
        try:
            date_range = {"start": start_date, "end": end_date}
            entries = await self.get_audit_trail(workspace_id, date_range)

            # Calculate statistics
            total_approvals = 0
            total_rejections = 0
            auto_approvals = 0
            escalations = 0
            timeouts = 0
            response_times = []

            for entry in entries:
                action = entry.action.lower()

                if "approve" in action:
                    total_approvals += 1
                    if "auto" in action:
                        auto_approvals += 1
                elif "reject" in action:
                    total_rejections += 1
                elif "escalate" in action:
                    escalations += 1
                elif "timeout" in action:
                    timeouts += 1

                # Calculate response time (would need request creation time)
                # For now, placeholder
                response_times.append(300)  # 5 minutes average

            avg_response_time = (
                sum(response_times) / len(response_times) if response_times else 0
            )

            # Calculate compliance score
            total_decisions = total_approvals + total_rejections
            compliance_factors = {
                "auto_approval_rate": auto_approvals / max(total_approvals, 1),
                "escalation_rate": escalations / max(total_decisions, 1),
                "timeout_rate": timeouts / max(total_decisions, 1),
                "response_time_score": min(
                    1.0, 1800 / max(avg_response_time, 1)
                ),  # Prefer < 30min
            }

            compliance_score = (
                compliance_factors["auto_approval_rate"] * 0.2
                + (1 - compliance_factors["escalation_rate"]) * 0.3
                + (1 - compliance_factors["timeout_rate"]) * 0.3
                + compliance_factors["response_time_score"] * 0.2
            ) * 100

            report = AuditReport(
                workspace_id=workspace_id,
                period_start=start_date,
                period_end=end_date,
                total_approvals=total_approvals,
                total_rejections=total_rejections,
                auto_approvals=auto_approvals,
                escalations=escalations,
                timeouts=timeouts,
                average_response_time=avg_response_time,
                compliance_score=compliance_score,
                entries=entries,
            )

            # Cache report
            report_key = f"{self.report_key_prefix}{workspace_id}:{start_date.date()}"
            report_json = json.dumps(asdict(report), default=str)
            await self.redis.set(
                report_key, report_json, ex=86400 * 30
            )  # Keep for 30 days

            return report

        except Exception as e:
            logger.error(f"Failed to generate compliance report: {e}")
            raise

    async def get_compliance_summary(
        self, workspace_id: str, days: int = 30
    ) -> Dict[str, Any]:
        """
        Get compliance summary for recent period.

        Args:
            workspace_id: Workspace identifier
            days: Number of days to analyze

        Returns:
            Compliance summary
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            report = await self.generate_compliance_report(
                workspace_id, start_date, end_date
            )

            summary = {
                "period_days": days,
                "total_decisions": report.total_approvals + report.total_rejections,
                "approval_rate": report.total_approvals
                / max(report.total_approvals + report.total_rejections, 1),
                "auto_approval_rate": report.auto_approvals
                / max(report.total_approvals, 1),
                "escalation_rate": report.escalations
                / max(report.total_approvals + report.total_rejections, 1),
                "timeout_rate": report.timeouts
                / max(report.total_approvals + report.total_rejections, 1),
                "average_response_time_minutes": report.average_response_time / 60,
                "compliance_score": report.compliance_score,
                "compliance_grade": self._get_compliance_grade(report.compliance_score),
            }

            return summary

        except Exception as e:
            logger.error(f"Failed to get compliance summary: {e}")
            return {"error": str(e)}

    async def export_audit_data(
        self,
        workspace_id: str,
        format: str = "json",
        date_range: Optional[Dict[str, datetime]] = None,
    ) -> str:
        """
        Export audit data in specified format.

        Args:
            workspace_id: Workspace identifier
            format: Export format (json, csv)
            date_range: Date range filter

        Returns:
            Exported data string
        """
        try:
            entries = await self.get_audit_trail(workspace_id, date_range)

            if format.lower() == "json":
                return json.dumps(
                    [asdict(entry, default=str) for entry in entries], indent=2
                )

            elif format.lower() == "csv":
                import csv
                import io

                output = io.StringIO()
                writer = csv.writer(output)

                # Header
                writer.writerow(
                    [
                        "gate_id",
                        "action",
                        "user_id",
                        "timestamp",
                        "reason",
                        "ip_address",
                        "user_agent",
                    ]
                )

                # Data rows
                for entry in entries:
                    writer.writerow(
                        [
                            entry.gate_id,
                            entry.action,
                            entry.user_id,
                            entry.timestamp.isoformat(),
                            entry.details.get("reason", ""),
                            entry.ip_address or "",
                            entry.user_agent or "",
                        ]
                    )

                return output.getvalue()

            else:
                raise ValueError(f"Unsupported format: {format}")

        except Exception as e:
            logger.error(f"Failed to export audit data: {e}")
            raise

    async def cleanup_old_audit_data(
        self, workspace_id: str, retention_years: int = 7
    ) -> int:
        """
        Clean up audit data older than retention period.

        Args:
            workspace_id: Workspace identifier
            retention_years: Number of years to retain data

        Returns:
            Number of entries cleaned up
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_years * 365)

            audit_key = f"{self.audit_key_prefix}{workspace_id}"
            entries_data = await self.redis.lrange(audit_key, 0, -1)

            removed_count = 0
            remaining_entries = []

            for entry_data in entries_data:
                entry_dict = json.loads(entry_data)
                timestamp = datetime.fromisoformat(
                    entry_dict["timestamp"].replace("Z", "+00:00")
                )

                if timestamp < cutoff_date:
                    removed_count += 1
                else:
                    remaining_entries.append(entry_data)

            # Update with remaining entries
            await self.redis.delete(audit_key)
            for entry in reversed(remaining_entries):  # Maintain order
                await self.redis.rpush(audit_key, entry)

            logger.info(
                f"Cleaned up {removed_count} old audit entries for workspace {workspace_id}"
            )
            return removed_count

        except Exception as e:
            logger.error(f"Failed to cleanup audit data: {e}")
            return 0

    def _get_compliance_grade(self, score: float) -> str:
        """Get compliance grade from score."""
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "B+"
        elif score >= 80:
            return "B"
        elif score >= 75:
            return "C+"
        elif score >= 70:
            return "C"
        elif score >= 65:
            return "D+"
        elif score >= 60:
            return "D"
        else:
            return "F"
