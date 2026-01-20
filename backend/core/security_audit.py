"""
Security Audit Logging and Compliance Reporting
Provides comprehensive audit trails, compliance reporting, and regulatory adherence monitoring.
"""

import asyncio
import hashlib
import json
import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from collections import defaultdict, deque
import csv
import io
import base64

logger = logging.getLogger(__name__)


class ComplianceStandard(Enum):
    """Compliance standards and frameworks."""
    SOC2 = "soc2"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"
    NIST = "nist"
    CCPA = "ccpa"


class AuditEventType(Enum):
    """Audit event types."""
    USER_AUTHENTICATION = "user_authentication"
    USER_AUTHORIZATION = "user_authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    SYSTEM_CONFIGURATION = "system_configuration"
    SECURITY_INCIDENT = "security_incident"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    API_ACCESS = "api_access"
    ADMIN_ACTION = "admin_action"
    POLICY_CHANGE = "policy_change"
    EXPORT_OPERATION = "export_operation"
    BACKUP_OPERATION = "backup_operation"


class RiskLevel(Enum):
    """Risk levels for audit events."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DataClassification(Enum):
    """Data classification levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


@dataclass
class AuditEvent:
    """Comprehensive audit event record."""
    timestamp: datetime
    event_id: str
    event_type: AuditEventType
    user_id: Optional[str]
    session_id: Optional[str]
    client_ip: str
    user_agent: str
    resource: str
    action: str
    outcome: str  # success, failure, error
    risk_level: RiskLevel
    data_classification: DataClassification
    
    # Contextual information
    workspace_id: Optional[str]
    organization_id: Optional[str]
    tenant_id: Optional[str]
    
    # Detailed information
    description: str
    details: Dict[str, Any]
    before_state: Optional[Dict[str, Any]]
    after_state: Optional[Dict[str, Any]]
    
    # Compliance and security
    compliance_standards: List[ComplianceStandard]
    retention_period_days: int
    requires_immediate_reporting: bool
    
    # Technical details
    api_endpoint: Optional[str]
    http_method: Optional[str]
    response_code: Optional[int]
    response_time_ms: Optional[int]
    
    # Integrity and verification
    checksum: str
    digital_signature: Optional[str]


@dataclass
class ComplianceReport:
    """Compliance report structure."""
    report_id: str
    standard: ComplianceStandard
    period_start: datetime
    period_end: datetime
    generated_at: datetime
    generated_by: str
    
    # Report content
    summary: Dict[str, Any]
    findings: List[Dict[str, Any]]
    violations: List[Dict[str, Any]]
    recommendations: List[str]
    
    # Metrics
    total_events: int
    high_risk_events: int
    compliance_score: float
    
    # Status
    status: str  # draft, review, approved, submitted
    reviewed_by: Optional[str]
    approved_by: Optional[str]


@dataclass
class RetentionPolicy:
    """Data retention policy."""
    policy_id: str
    name: str
    description: str
    data_classification: DataClassification
    retention_days: int
    compliance_standards: List[ComplianceStandard]
    auto_delete: bool
    notification_before_days: int


class SecurityAudit:
    """Security audit and compliance management system."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        
        # Storage
        self.audit_events: deque = deque(maxlen=100000)  # Last 100k events
        self.compliance_reports: Dict[str, ComplianceReport] = {}
        self.retention_policies: Dict[str, RetentionPolicy] = {}
        
        # Indexing for fast queries
        self.events_by_user: Dict[str, List[str]] = defaultdict(list)
        self.events_by_type: Dict[AuditEventType, List[str]] = defaultdict(list)
        self.events_by_risk: Dict[RiskLevel, List[str]] = defaultdict(list)
        self.events_by_compliance: Dict[ComplianceStandard, List[str]] = defaultdict(list)
        
        # Compliance requirements
        self.compliance_requirements = self._initialize_compliance_requirements()
        
        # Initialize retention policies
        self._initialize_retention_policies()
        
        # Background tasks
        self._cleanup_task = None
        self._report_generation_task = None
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration."""
        return {
            "enable_digital_signatures": True,
            "checksum_algorithm": "sha256",
            "max_events_in_memory": 100000,
            "cleanup_interval_hours": 24,
            "report_generation_interval_hours": 24,
            "immediate_notification_threshold": RiskLevel.HIGH,
            "default_retention_days": 2555,  # 7 years
            "enable_compliance_monitoring": True,
        }
    
    def _initialize_compliance_requirements(self) -> Dict[ComplianceStandard, Dict[str, Any]]:
        """Initialize compliance requirements for different standards."""
        return {
            ComplianceStandard.SOC2: {
                "required_fields": [
                    "timestamp", "user_id", "event_type", "resource", 
                    "action", "outcome", "client_ip"
                ],
                "retention_days": 2555,  # 7 years
                "monitoring_events": [
                    AuditEventType.USER_AUTHENTICATION,
                    AuditEventType.DATA_ACCESS,
                    AuditEventType.DATA_MODIFICATION,
                    AuditEventType.SYSTEM_CONFIGURATION,
                ],
                "immediate_reporting": [
                    AuditEventType.SECURITY_INCIDENT,
                    AuditEventType.PRIVILEGE_ESCALATION,
                ],
            },
            ComplianceStandard.GDPR: {
                "required_fields": [
                    "timestamp", "user_id", "event_type", "resource",
                    "action", "outcome", "data_classification"
                ],
                "retention_days": 2555,  # 7 years
                "monitoring_events": [
                    AuditEventType.DATA_ACCESS,
                    AuditEventType.DATA_MODIFICATION,
                    AuditEventType.DATA_DELETION,
                    AuditEventType.EXPORT_OPERATION,
                ],
                "immediate_reporting": [
                    AuditEventType.DATA_DELETION,
                    AuditEventType.SECURITY_INCIDENT,
                ],
                "special_categories": [
                    DataClassification.RESTRICTED,
                    DataClassification.CONFIDENTIAL,
                ],
            },
            ComplianceStandard.HIPAA: {
                "required_fields": [
                    "timestamp", "user_id", "event_type", "resource",
                    "action", "outcome", "user_id", "client_ip"
                ],
                "retention_days": 2190,  # 6 years
                "monitoring_events": [
                    AuditEventType.DATA_ACCESS,
                    AuditEventType.DATA_MODIFICATION,
                    AuditEventType.DATA_DELETION,
                    AuditEventType.USER_AUTHENTICATION,
                ],
                "immediate_reporting": [
                    AuditEventType.SECURITY_INCIDENT,
                    AuditEventType.DATA_DELETION,
                ],
            },
            ComplianceStandard.PCI_DSS: {
                "required_fields": [
                    "timestamp", "user_id", "event_type", "resource",
                    "action", "outcome", "client_ip", "response_code"
                ],
                "retention_days": 365,  # 1 year
                "monitoring_events": [
                    AuditEventType.DATA_ACCESS,
                    AuditEventType.DATA_MODIFICATION,
                    AuditEventType.USER_AUTHENTICATION,
                    AuditEventType.API_ACCESS,
                ],
                "immediate_reporting": [
                    AuditEventType.SECURITY_INCIDENT,
                    AuditEventType.DATA_DELETION,
                ],
            },
        }
    
    def _initialize_retention_policies(self):
        """Initialize default retention policies."""
        policies = [
            RetentionPolicy(
                policy_id="public_data",
                name="Public Data Retention",
                description="Retention policy for public data",
                data_classification=DataClassification.PUBLIC,
                retention_days=365,
                compliance_standards=[ComplianceStandard.SOC2],
                auto_delete=True,
                notification_before_days=30,
            ),
            RetentionPolicy(
                policy_id="internal_data",
                name="Internal Data Retention",
                description="Retention policy for internal data",
                data_classification=DataClassification.INTERNAL,
                retention_days=1095,  # 3 years
                compliance_standards=[ComplianceStandard.SOC2],
                auto_delete=True,
                notification_before_days=60,
            ),
            RetentionPolicy(
                policy_id="confidential_data",
                name="Confidential Data Retention",
                description="Retention policy for confidential data",
                data_classification=DataClassification.CONFIDENTIAL,
                retention_days=2555,  # 7 years
                compliance_standards=[ComplianceStandard.GDPR, ComplianceStandard.HIPAA],
                auto_delete=False,
                notification_before_days=90,
            ),
            RetentionPolicy(
                policy_id="restricted_data",
                name="Restricted Data Retention",
                description="Retention policy for restricted data",
                data_classification=DataClassification.RESTRICTED,
                retention_days=2555,  # 7 years
                compliance_standards=[ComplianceStandard.GDPR, ComplianceStandard.HIPAA],
                auto_delete=False,
                notification_before_days=180,
            ),
        ]
        
        for policy in policies:
            self.retention_policies[policy.policy_id] = policy
    
    async def log_audit_event(
        self,
        event_type: AuditEventType,
        user_id: Optional[str],
        resource: str,
        action: str,
        outcome: str,
        risk_level: RiskLevel,
        data_classification: DataClassification,
        description: str,
        details: Optional[Dict[str, Any]] = None,
        before_state: Optional[Dict[str, Any]] = None,
        after_state: Optional[Dict[str, Any]] = None,
        compliance_standards: Optional[List[ComplianceStandard]] = None,
        client_ip: str = "unknown",
        user_agent: str = "unknown",
        session_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        api_endpoint: Optional[str] = None,
        http_method: Optional[str] = None,
        response_code: Optional[int] = None,
        response_time_ms: Optional[int] = None,
        requires_immediate_reporting: Optional[bool] = None,
    ) -> str:
        """Log an audit event."""
        # Generate unique event ID
        event_id = self._generate_event_id()
        
        # Determine compliance standards
        if compliance_standards is None:
            compliance_standards = self._determine_compliance_standards(
                event_type, data_classification
            )
        
        # Determine retention period
        retention_period = self._determine_retention_period(
            data_classification, compliance_standards
        )
        
        # Determine if immediate reporting is required
        if requires_immediate_reporting is None:
            requires_immediate_reporting = self._requires_immediate_reporting(
                event_type, risk_level, compliance_standards
            )
        
        # Create audit event
        event = AuditEvent(
            timestamp=datetime.now(),
            event_id=event_id,
            event_type=event_type,
            user_id=user_id,
            session_id=session_id,
            client_ip=client_ip,
            user_agent=user_agent,
            resource=resource,
            action=action,
            outcome=outcome,
            risk_level=risk_level,
            data_classification=data_classification,
            workspace_id=workspace_id,
            organization_id=organization_id,
            tenant_id=tenant_id,
            description=description,
            details=details or {},
            before_state=before_state,
            after_state=after_state,
            compliance_standards=compliance_standards,
            retention_period_days=retention_period,
            requires_immediate_reporting=requires_immediate_reporting,
            api_endpoint=api_endpoint,
            http_method=http_method,
            response_code=response_code,
            response_time_ms=response_time_ms,
            checksum="",  # Will be calculated
            digital_signature=None,  # Will be added if enabled
        )
        
        # Calculate checksum
        event.checksum = self._calculate_checksum(event)
        
        # Add digital signature if enabled
        if self.config["enable_digital_signatures"]:
            event.digital_signature = self._generate_digital_signature(event)
        
        # Store event
        self.audit_events.append(event)
        
        # Update indexes
        self._update_indexes(event)
        
        # Log to system logger
        self._log_audit_event(event)
        
        # Handle immediate reporting if required
        if requires_immediate_reporting:
            await self._handle_immediate_reporting(event)
        
        # Trigger compliance monitoring
        if self.config["enable_compliance_monitoring"]:
            asyncio.create_task(self._monitor_compliance(event))
        
        return event_id
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        timestamp = str(int(time.time() * 1000))
        random_bytes = str(time.time()).encode() + str(id(self)).encode()
        hash_value = hashlib.sha256(random_bytes).hexdigest()[:8]
        return f"audit_{timestamp}_{hash_value}"
    
    def _determine_compliance_standards(
        self,
        event_type: AuditEventType,
        data_classification: DataClassification,
    ) -> List[ComplianceStandard]:
        """Determine applicable compliance standards."""
        standards = []
        
        # Check based on data classification
        if data_classification in [DataClassification.CONFIDENTIAL, DataClassification.RESTRICTED]:
            standards.extend([ComplianceStandard.GDPR, ComplianceStandard.HIPAA])
        
        # Check based on event type
        if event_type in [
            AuditEventType.USER_AUTHENTICATION,
            AuditEventType.DATA_ACCESS,
            AuditEventType.DATA_MODIFICATION,
        ]:
            standards.append(ComplianceStandard.SOC2)
        
        # Always include SOC2 for most events
        if event_type not in [AuditEventType.SYSTEM_CONFIGURATION]:
            standards.append(ComplianceStandard.SOC2)
        
        return list(set(standards))  # Remove duplicates
    
    def _determine_retention_period(
        self,
        data_classification: DataClassification,
        compliance_standards: List[ComplianceStandard],
    ) -> int:
        """Determine retention period based on classification and standards."""
        # Get retention policies
        policy = self.retention_policies.get(f"{data_classification.value}_data")
        if policy:
            return policy.retention_days
        
        # Get maximum retention from compliance standards
        retention_periods = []
        for standard in compliance_standards:
            if standard in self.compliance_requirements:
                retention_periods.append(
                    self.compliance_requirements[standard]["retention_days"]
                )
        
        return max(retention_periods) if retention_periods else self.config["default_retention_days"]
    
    def _requires_immediate_reporting(
        self,
        event_type: AuditEventType,
        risk_level: RiskLevel,
        compliance_standards: List[ComplianceStandard],
    ) -> bool:
        """Determine if event requires immediate reporting."""
        # Check risk level
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            return True
        
        # Check compliance requirements
        for standard in compliance_standards:
            if standard in self.compliance_requirements:
                if event_type in self.compliance_requirements[standard]["immediate_reporting"]:
                    return True
        
        return False
    
    def _calculate_checksum(self, event: AuditEvent) -> str:
        """Calculate checksum for event integrity."""
        # Create a string representation of the event (excluding checksum and signature)
        event_data = {
            "timestamp": event.timestamp.isoformat(),
            "event_id": event.event_id,
            "event_type": event.event_type.value,
            "user_id": event.user_id,
            "resource": event.resource,
            "action": event.action,
            "outcome": event.outcome,
            "risk_level": event.risk_level.value,
            "data_classification": event.data_classification.value,
            "description": event.description,
            "details": event.details,
        }
        
        event_string = json.dumps(event_data, sort_keys=True)
        algorithm = self.config["checksum_algorithm"]
        
        if algorithm == "sha256":
            return hashlib.sha256(event_string.encode()).hexdigest()
        elif algorithm == "md5":
            return hashlib.md5(event_string.encode()).hexdigest()
        else:
            return hashlib.sha256(event_string.encode()).hexdigest()
    
    def _generate_digital_signature(self, event: AuditEvent) -> str:
        """Generate real HMAC-SHA256 digital signature for event integrity."""
        import hmac
        from backend.config.settings import get_settings
        
        settings = get_settings()
        secret = settings.SECRET_KEY.encode()
        
        # Data to sign: event_id, timestamp, and checksum
        data_to_sign = f"{event.event_id}:{event.timestamp.isoformat()}:{event.checksum}".encode()
        
        signature = hmac.new(secret, data_to_sign, hashlib.sha256).digest()
        return base64.b64encode(signature).decode()
    
    def _update_indexes(self, event: AuditEvent):
        """Update search indexes."""
        # User index
        if event.user_id:
            self.events_by_user[event.user_id].append(event.event_id)
        
        # Type index
        self.events_by_type[event.event_type].append(event.event_id)
        
        # Risk index
        self.events_by_risk[event.risk_level].append(event.event_id)
        
        # Compliance index
        for standard in event.compliance_standards:
            self.events_by_compliance[standard].append(event.event_id)
    
    def _log_audit_event(self, event: AuditEvent):
        """Log audit event to system logger."""
        log_level = {
            RiskLevel.LOW: logging.INFO,
            RiskLevel.MEDIUM: logging.WARNING,
            RiskLevel.HIGH: logging.ERROR,
            RiskLevel.CRITICAL: logging.CRITICAL,
        }.get(event.risk_level, logging.INFO)
        
        logger.log(
            log_level,
            f"Audit Event [{event.risk_level.value.upper()}] "
            f"{event.event_type.value}: {event.description} "
            f"(User: {event.user_id}, Resource: {event.resource})"
        )
    
    async def _handle_immediate_reporting(self, event: AuditEvent):
        """Handle immediate reporting for critical events."""
        # In production, this would send notifications, create incidents, etc.
        logger.critical(
            f"IMMEDIATE REPORTING REQUIRED: {event.event_id} - {event.description}"
        )
        
        # Trigger compliance alerts
        for standard in event.compliance_standards:
            await self._trigger_compliance_alert(standard, event)
    
    async def _monitor_compliance(self, event: AuditEvent):
        """Monitor compliance for the event."""
        for standard in event.compliance_standards:
            if standard in self.compliance_requirements:
                requirements = self.compliance_requirements[standard]
                
                # Check required fields
                missing_fields = []
                for field in requirements["required_fields"]:
                    if not hasattr(event, field) or getattr(event, field) is None:
                        missing_fields.append(field)
                
                if missing_fields:
                    logger.warning(
                        f"Compliance violation for {standard.value}: "
                        f"Missing required fields {missing_fields} in event {event.event_id}"
                    )
    
    async def _trigger_compliance_alert(self, standard: ComplianceStandard, event: AuditEvent):
        """Trigger compliance alert."""
        # In production, this would integrate with alerting systems
        logger.error(
            f"COMPLIANCE ALERT [{standard.value}]: "
            f"Critical event {event.event_id} requires immediate attention"
        )
    
    def search_audit_events(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        risk_level: Optional[RiskLevel] = None,
        compliance_standard: Optional[ComplianceStandard] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        resource_pattern: Optional[str] = None,
        limit: int = 100,
    ) -> List[AuditEvent]:
        """Search audit events with filters."""
        events = list(self.audit_events)
        
        # Apply filters
        if user_id:
            events = [e for e in events if e.user_id == user_id]
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if risk_level:
            events = [e for e in events if e.risk_level == risk_level]
        
        if compliance_standard:
            events = [e for e in events if compliance_standard in e.compliance_standards]
        
        if start_time:
            events = [e for e in events if e.timestamp >= start_time]
        
        if end_time:
            events = [e for e in events if e.timestamp <= end_time]
        
        if resource_pattern:
            import re
            pattern = re.compile(resource_pattern, re.IGNORECASE)
            events = [e for e in events if pattern.search(e.resource)]
        
        # Sort by timestamp (most recent first)
        events.sort(key=lambda x: x.timestamp, reverse=True)
        
        return events[:limit]
    
    async def generate_compliance_report(
        self,
        standard: ComplianceStandard,
        period_start: datetime,
        period_end: datetime,
        generated_by: str,
    ) -> str:
        """Generate compliance report for a specific standard."""
        report_id = f"report_{standard.value}_{int(time.time())}"
        
        # Get events for the period
        events = self.search_audit_events(
            start_time=period_start,
            end_time=period_end,
            compliance_standard=standard,
            limit=10000,
        )
        
        # Analyze events
        summary = self._analyze_events_for_compliance(events, standard)
        findings = self._generate_findings(events, standard)
        violations = self._identify_violations(events, standard)
        recommendations = self._generate_recommendations(violations, standard)
        
        # Calculate compliance score
        compliance_score = self._calculate_compliance_score(events, violations, standard)
        
        # Create report
        report = ComplianceReport(
            report_id=report_id,
            standard=standard,
            period_start=period_start,
            period_end=period_end,
            generated_at=datetime.now(),
            generated_by=generated_by,
            summary=summary,
            findings=findings,
            violations=violations,
            recommendations=recommendations,
            total_events=len(events),
            high_risk_events=len([e for e in events if e.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]),
            compliance_score=compliance_score,
            status="draft",
            reviewed_by=None,
            approved_by=None,
        )
        
        self.compliance_reports[report_id] = report
        
        return report_id
    
    def _analyze_events_for_compliance(
        self,
        events: List[AuditEvent],
        standard: ComplianceStandard,
    ) -> Dict[str, Any]:
        """Analyze events for compliance summary."""
        if standard not in self.compliance_requirements:
            return {}
        
        # Event type distribution
        event_types = defaultdict(int)
        for event in events:
            event_types[event.event_type.value] += 1
        
        # Risk level distribution
        risk_levels = defaultdict(int)
        for event in events:
            risk_levels[event.risk_level.value] += 1
        
        # User activity
        user_activity = defaultdict(int)
        for event in events:
            if event.user_id:
                user_activity[event.user_id] += 1
        
        # Resource access
        resource_access = defaultdict(int)
        for event in events:
            resource_access[event.resource] += 1
        
        return {
            "event_types": dict(event_types),
            "risk_levels": dict(risk_levels),
            "total_users": len(user_activity),
            "top_active_users": sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:10],
            "total_resources": len(resource_access),
            "top_accessed_resources": sorted(resource_access.items(), key=lambda x: x[1], reverse=True)[:10],
            "period_start": min(events, key=lambda x: x.timestamp).timestamp.isoformat() if events else None,
            "period_end": max(events, key=lambda x: x.timestamp).timestamp.isoformat() if events else None,
        }
    
    def _generate_findings(
        self,
        events: List[AuditEvent],
        standard: ComplianceStandard,
    ) -> List[Dict[str, Any]]:
        """Generate findings from events."""
        findings = []
        
        # High-risk events
        high_risk_events = [e for e in events if e.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]
        if high_risk_events:
            findings.append({
                "type": "security_risks",
                "severity": "high",
                "description": f"Found {len(high_risk_events)} high-risk events",
                "events": [e.event_id for e in high_risk_events[:10]],
            })
        
        # Failed authentication attempts
        failed_auth = [e for e in events if e.event_type == AuditEventType.USER_AUTHENTICATION and e.outcome == "failure"]
        if len(failed_auth) > 10:
            findings.append({
                "type": "authentication_issues",
                "severity": "medium",
                "description": f"Found {len(failed_auth)} failed authentication attempts",
                "events": [e.event_id for e in failed_auth[:10]],
            })
        
        # Data access patterns
        data_access = [e for e in events if e.event_type == AuditEventType.DATA_ACCESS]
        if len(data_access) > 1000:
            findings.append({
                "type": "high_data_access",
                "severity": "low",
                "description": f"High volume of data access: {len(data_access)} events",
                "events": [],
            })
        
        return findings
    
    def _identify_violations(
        self,
        events: List[AuditEvent],
        standard: ComplianceStandard,
    ) -> List[Dict[str, Any]]:
        """Identify compliance violations."""
        violations = []
        
        if standard not in self.compliance_requirements:
            return violations
        
        requirements = self.compliance_requirements[standard]
        
        # Check for missing required fields
        for event in events:
            missing_fields = []
            for field in requirements["required_fields"]:
                if not hasattr(event, field) or getattr(event, field) is None:
                    missing_fields.append(field)
            
            if missing_fields:
                violations.append({
                    "event_id": event.event_id,
                    "type": "missing_required_fields",
                    "severity": "high",
                    "description": f"Missing required fields: {missing_fields}",
                    "timestamp": event.timestamp.isoformat(),
                })
        
        # Check for unmonitored event types
        monitored_types = set(requirements["monitoring_events"])
        for event in events:
            if event.event_type not in monitored_types:
                violations.append({
                    "event_id": event.event_id,
                    "type": "unmonitored_event_type",
                    "severity": "medium",
                    "description": f"Event type {event.event_type.value} not monitored for {standard.value}",
                    "timestamp": event.timestamp.isoformat(),
                })
        
        return violations
    
    def _generate_recommendations(
        self,
        violations: List[Dict[str, Any]],
        standard: ComplianceStandard,
    ) -> List[str]:
        """Generate recommendations based on violations."""
        recommendations = []
        
        violation_types = set(v["type"] for v in violations)
        
        if "missing_required_fields" in violation_types:
            recommendations.append(
                "Update event logging to include all required fields for compliance"
            )
        
        if "unmonitored_event_type" in violation_types:
            recommendations.append(
                f"Expand monitoring to cover all event types required by {standard.value}"
            )
        
        if not violations:
            recommendations.append("No compliance violations detected - maintain current practices")
        
        return recommendations
    
    def _calculate_compliance_score(
        self,
        events: List[AuditEvent],
        violations: List[Dict[str, Any]],
        standard: ComplianceStandard,
    ) -> float:
        """Calculate compliance score (0-100)."""
        if not events:
            return 100.0
        
        # Base score starts at 100
        score = 100.0
        
        # Deduct points for violations
        for violation in violations:
            if violation["severity"] == "critical":
                score -= 20
            elif violation["severity"] == "high":
                score -= 10
            elif violation["severity"] == "medium":
                score -= 5
            elif violation["severity"] == "low":
                score -= 2
        
        # Deduct points for high-risk events
        high_risk_count = len([e for e in events if e.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]])
        score -= min(high_risk_count * 0.5, 20)  # Max 20 points deduction
        
        return max(0.0, score)
    
    def export_audit_data(
        self,
        format: str = "json",
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Union[str, bytes]:
        """Export audit data in various formats."""
        events = self.search_audit_events(
            start_time=start_time,
            end_time=end_time,
            limit=10000,
            **(filters or {})
        )
        
        if format.lower() == "json":
            return self._export_json(events)
        elif format.lower() == "csv":
            return self._export_csv(events)
        elif format.lower() == "xml":
            return self._export_xml(events)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_json(self, events: List[AuditEvent]) -> str:
        """Export events as JSON."""
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "total_events": len(events),
            "events": [asdict(event) for event in events],
        }
        return json.dumps(export_data, indent=2, default=str)
    
    def _export_csv(self, events: List[AuditEvent]) -> bytes:
        """Export events as CSV."""
        output = io.StringIO()
        
        if not events:
            return output.getvalue().encode()
        
        # Define CSV headers
        headers = [
            "timestamp", "event_id", "event_type", "user_id", "session_id",
            "client_ip", "resource", "action", "outcome", "risk_level",
            "data_classification", "description", "workspace_id", "organization_id"
        ]
        
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        
        for event in events:
            row = {
                "timestamp": event.timestamp.isoformat(),
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "user_id": event.user_id,
                "session_id": event.session_id,
                "client_ip": event.client_ip,
                "resource": event.resource,
                "action": event.action,
                "outcome": event.outcome,
                "risk_level": event.risk_level.value,
                "data_classification": event.data_classification.value,
                "description": event.description,
                "workspace_id": event.workspace_id,
                "organization_id": event.organization_id,
            }
            writer.writerow(row)
        
        return output.getvalue().encode()
    
    def _export_xml(self, events: List[AuditEvent]) -> str:
        """Export events as XML."""
        # Simple XML export
        xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml_lines.append('<audit_export>')
        xml_lines.append(f'  <export_timestamp>{datetime.now().isoformat()}</export_timestamp>')
        xml_lines.append(f'  <total_events>{len(events)}</total_events>')
        xml_lines.append('  <events>')
        
        for event in events:
            xml_lines.append('    <event>')
            xml_lines.append(f'      <timestamp>{event.timestamp.isoformat()}</timestamp>')
            xml_lines.append(f'      <event_id>{event.event_id}</event_id>')
            xml_lines.append(f'      <event_type>{event.event_type.value}</event_type>')
            xml_lines.append(f'      <user_id>{event.user_id or ""}</user_id>')
            xml_lines.append(f'      <resource>{event.resource}</resource>')
            xml_lines.append(f'      <action>{event.action}</action>')
            xml_lines.append(f'      <outcome>{event.outcome}</outcome>')
            xml_lines.append(f'      <risk_level>{event.risk_level.value}</risk_level>')
            xml_lines.append(f'      <description>{event.description}</description>')
            xml_lines.append('    </event>')
        
        xml_lines.append('  </events>')
        xml_lines.append('</audit_export>')
        
        return '\n'.join(xml_lines)
    
    async def apply_retention_policies(self):
        """Apply retention policies and clean up old events."""
        current_time = datetime.now()
        events_to_remove = []
        
        for event in self.audit_events:
            # Calculate age based on retention period
            age_days = (current_time - event.timestamp).days
            
            if age_days > event.retention_period_days:
                events_to_remove.append(event)
        
        # Remove old events
        for event in events_to_remove:
            self.audit_events.remove(event)
            self._remove_from_indexes(event)
        
        if events_to_remove:
            logger.info(f"Cleaned up {len(events_to_remove)} old audit events")
    
    def _remove_from_indexes(self, event: AuditEvent):
        """Remove event from search indexes."""
        if event.user_id and event.user_id in self.events_by_user:
            self.events_by_user[event.user_id] = [
                eid for eid in self.events_by_user[event.user_id]
                if eid != event.event_id
            ]
        
        if event.event_type in self.events_by_type:
            self.events_by_type[event.event_type] = [
                eid for eid in self.events_by_type[event.event_type]
                if eid != event.event_id
            ]
        
        if event.risk_level in self.events_by_risk:
            self.events_by_risk[event.risk_level] = [
                eid for eid in self.events_by_risk[event.risk_level]
                if eid != event.event_id
            ]
        
        for standard in event.compliance_standards:
            if standard in self.events_by_compliance:
                self.events_by_compliance[standard] = [
                    eid for eid in self.events_by_compliance[standard]
                    if eid != event.event_id
                ]
    
    def get_audit_metrics(self) -> Dict[str, Any]:
        """Get audit system metrics."""
        current_time = datetime.now()
        last_24h = current_time - timedelta(hours=24)
        last_7d = current_time - timedelta(days=7)
        
        # Count events by time period
        events_24h = [e for e in self.audit_events if e.timestamp >= last_24h]
        events_7d = [e for e in self.audit_events if e.timestamp >= last_7d]
        
        # Risk level distribution
        risk_distribution = defaultdict(int)
        for event in events_24h:
            risk_distribution[event.risk_level.value] += 1
        
        # Compliance standard coverage
        compliance_coverage = defaultdict(int)
        for event in events_24h:
            for standard in event.compliance_standards:
                compliance_coverage[standard.value] += 1
        
        return {
            "total_events": len(self.audit_events),
            "events_last_24h": len(events_24h),
            "events_last_7d": len(events_7d),
            "risk_distribution_24h": dict(risk_distribution),
            "compliance_coverage_24h": dict(compliance_coverage),
            "total_reports": len(self.compliance_reports),
            "retention_policies": len(self.retention_policies),
            "indexed_users": len(self.events_by_user),
            "indexed_event_types": len(self.events_by_type),
        }
    
    def get_compliance_report(self, report_id: str) -> Optional[ComplianceReport]:
        """Get compliance report by ID."""
        return self.compliance_reports.get(report_id)
    
    def list_compliance_reports(self, standard: Optional[ComplianceStandard] = None) -> List[ComplianceReport]:
        """List compliance reports."""
        reports = list(self.compliance_reports.values())
        
        if standard:
            reports = [r for r in reports if r.standard == standard]
        
        return sorted(reports, key=lambda x: x.generated_at, reverse=True)


# Global security audit instance
_security_audit: Optional[SecurityAudit] = None


def get_security_audit() -> SecurityAudit:
    """Get the global security audit instance."""
    global _security_audit
    if _security_audit is None:
        _security_audit = SecurityAudit()
    return _security_audit
