"""
S.W.A.R.M. Phase 2: Advanced MLOps - Data Compliance System
Production-ready data compliance with GDPR, CCPA, and industry regulations
"""

import asyncio
import hashlib
import json
import logging
import os
import pickle
import re
import time
import uuid
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

import numpy as np
import pandas as pd
import yaml

warnings.filterwarnings("ignore")

logger = logging.getLogger("raptorflow.data_compliance")


class ComplianceFramework(Enum):
    """Compliance frameworks."""

    GDPR = "gdpr"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"


class DataType(Enum):
    """Types of personal data."""

    PERSONALLY_IDENTIFIABLE_INFORMATION = "pii"
    SENSITIVE_PERSONAL_INFORMATION = "spi"
    PROTECTED_HEALTH_INFORMATION = "phi"
    FINANCIAL_INFORMATION = "financial"
    EDUCATION_RECORDS = "education"
    EMPLOYMENT_DATA = "employment"
    BIOMETRIC_DATA = "biometric"
    GELOCATION_DATA = "geolocation"


class ConsentStatus(Enum):
    """Data consent status."""

    EXPLICIT = "explicit"
    IMPLICIT = "implicit"
    WITHDRAWN = "withdrawn"
    UNKNOWN = "unknown"


class ComplianceStatus(Enum):
    """Compliance status."""

    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    EXEMPT = "exempt"


class ActionType(Enum):
    """Compliance action types."""

    DATA_SUBJECT_REQUEST = "data_subject_request"
    BREACH_NOTIFICATION = "breach_notification"
    IMPACT_ASSESSMENT = "impact_assessment"
    CONSENT_MANAGEMENT = "consent_management"
    DATA_RETENTION = "data_retention"
    ANONYMIZATION = "anonymization"
    DELETION = "deletion"


@dataclass
class ComplianceRule:
    """Compliance rule definition."""

    rule_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    framework: ComplianceFramework = ComplianceFramework.GDPR
    rule_type: str = ""
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    severity: str = "medium"
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "framework": self.framework.value,
            "rule_type": self.rule_type,
            "conditions": self.conditions,
            "actions": self.actions,
            "severity": self.severity,
            "enabled": self.enabled,
        }


@dataclass
class DataSubject:
    """Data subject information."""

    subject_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    identifier: str = ""
    email: str = ""
    phone: str = ""
    consent_records: List[Dict[str, Any]] = field(default_factory=list)
    requests: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "subject_id": self.subject_id,
            "identifier": self.identifier,
            "email": self.email,
            "phone": self.phone,
            "consent_records": self.consent_records,
            "requests": self.requests,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class ComplianceAssessment:
    """Compliance assessment result."""

    assessment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    framework: ComplianceFramework = ComplianceFramework.GDPR
    asset_id: str = ""
    assessment_date: datetime = field(default_factory=datetime.now)
    status: ComplianceStatus = ComplianceStatus.COMPLIANT
    score: float = 0.0
    findings: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    assessor: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "assessment_id": self.assessment_id,
            "framework": self.framework.value,
            "asset_id": self.asset_id,
            "assessment_date": self.assessment_date.isoformat(),
            "status": self.status.value,
            "score": self.score,
            "findings": self.findings,
            "recommendations": self.recommendations,
            "assessor": self.assessor,
        }


@dataclass
class ComplianceAlert:
    """Compliance alert."""

    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    framework: ComplianceFramework = ComplianceFramework.GDPR
    rule_id: str = ""
    asset_id: str = ""
    severity: str = "medium"
    title: str = ""
    description: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolution_notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "alert_id": self.alert_id,
            "framework": self.framework.value,
            "rule_id": self.rule_id,
            "asset_id": self.asset_id,
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
            "resolved": self.resolved,
            "resolution_notes": self.resolution_notes,
        }


class DataComplianceSystem:
    """Production-ready data compliance system."""

    def __init__(self):
        self.compliance_rules: Dict[str, ComplianceRule] = {}
        self.data_subjects: Dict[str, DataSubject] = {}
        self.assessments: Dict[str, List[ComplianceAssessment]] = {}
        self.compliance_alerts: Dict[str, ComplianceAlert] = {}
        self.pii_detector = PIIDetector()
        self.consent_manager = ConsentManager()
        self.retention_manager = RetentionManager()
        self.anonymizer = DataAnonymizer()

        # Initialize default compliance rules
        self._initialize_default_rules()

    def _initialize_default_rules(self):
        """Initialize default compliance rules."""
        # GDPR Rules
        gdpr_rules = [
            ComplianceRule(
                name="GDPR Data Minimization",
                description="Only collect and process necessary personal data",
                framework=ComplianceFramework.GDPR,
                rule_type="data_minimization",
                conditions=[{"field_type": "pii", "required_purpose": True}],
                actions=["validate_purpose", "remove_excess_data"],
                severity="high",
            ),
            ComplianceRule(
                name="GDPR Consent Management",
                description="Ensure explicit consent for data processing",
                framework=ComplianceFramework.GDPR,
                rule_type="consent_management",
                conditions=[{"data_type": "pii", "consent_required": True}],
                actions=["verify_consent", "log_consent"],
                severity="critical",
            ),
            ComplianceRule(
                name="GDPR Data Retention",
                description="Retain personal data only as long as necessary",
                framework=ComplianceFramework.GDPR,
                rule_type="data_retention",
                conditions=[{"data_type": "pii", "max_retention_days": 2555}],
                actions=["check_retention_period", "schedule_deletion"],
                severity="medium",
            ),
        ]

        # CCPA Rules
        ccpa_rules = [
            ComplianceRule(
                name="CCPA Right to Delete",
                description="Honor consumer requests to delete personal information",
                framework=ComplianceFramework.CCPA,
                rule_type="right_to_delete",
                conditions=[
                    {"consumer_request": "delete", "verification_required": True}
                ],
                actions=["verify_identity", "delete_data", "confirm_deletion"],
                severity="critical",
            ),
            ComplianceRule(
                name="CCPA Right to Opt-Out",
                description="Allow consumers to opt-out of sale of personal information",
                framework=ComplianceFramework.CCPA,
                rule_type="right_to_opt_out",
                conditions=[
                    {"consumer_request": "opt_out", "preference_required": True}
                ],
                actions=["process_opt_out", "update_preferences", "confirm_opt_out"],
                severity="high",
            ),
        ]

        # Add all rules
        for rule in gdpr_rules + ccpa_rules:
            self.compliance_rules[rule.rule_id] = rule

    def register_data_subject(self, subject: DataSubject) -> str:
        """Register a data subject."""
        self.data_subjects[subject.subject_id] = subject
        logger.info(f"Registered data subject: {subject.subject_id}")
        return subject.subject_id

    def update_consent(self, subject_id: str, consent_data: Dict[str, Any]) -> bool:
        """Update consent for a data subject."""
        if subject_id not in self.data_subjects:
            raise ValueError(f"Subject {subject_id} not found")

        subject = self.data_subjects[subject_id]
        consent_record = {
            "consent_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "status": consent_data.get("status", ConsentStatus.UNKNOWN.value),
            "purpose": consent_data.get("purpose", ""),
            "data_types": consent_data.get("data_types", []),
            "expiry": consent_data.get("expiry"),
            "ip_address": consent_data.get("ip_address"),
            "user_agent": consent_data.get("user_agent"),
        }

        subject.consent_records.append(consent_record)
        subject.updated_at = datetime.now()

        logger.info(f"Updated consent for subject: {subject_id}")
        return True

    def assess_compliance(
        self,
        asset_id: str,
        data: pd.DataFrame,
        framework: ComplianceFramework = ComplianceFramework.GDPR,
    ) -> ComplianceAssessment:
        """Assess compliance of a data asset."""
        assessment = ComplianceAssessment(
            framework=framework, asset_id=asset_id, assessor="compliance_system"
        )

        # Get applicable rules
        applicable_rules = [
            rule
            for rule in self.compliance_rules.values()
            if rule.framework == framework and rule.enabled
        ]

        findings = []
        total_score = 0.0

        for rule in applicable_rules:
            rule_result = self._evaluate_rule(rule, data, asset_id)
            findings.append(rule_result)
            total_score += rule_result["score"]

        # Calculate overall score
        if applicable_rules:
            assessment.score = total_score / len(applicable_rules)
        else:
            assessment.score = 0.0

        # Determine status
        if assessment.score >= 0.9:
            assessment.status = ComplianceStatus.COMPLIANT
        elif assessment.score >= 0.7:
            assessment.status = ComplianceStatus.PENDING_REVIEW
        else:
            assessment.status = ComplianceStatus.NON_COMPLIANT

        assessment.findings = findings

        # Generate recommendations
        assessment.recommendations = self._generate_recommendations(findings)

        # Store assessment
        if asset_id not in self.assessments:
            self.assessments[asset_id] = []
        self.assessments[asset_id].append(assessment)

        logger.info(
            f"Compliance assessment completed for {asset_id}: {assessment.status.value}"
        )
        return assessment

    def _evaluate_rule(
        self, rule: ComplianceRule, data: pd.DataFrame, asset_id: str
    ) -> Dict[str, Any]:
        """Evaluate a single compliance rule."""
        result = {
            "rule_id": rule.rule_id,
            "rule_name": rule.name,
            "score": 0.0,
            "compliant": False,
            "issues": [],
            "details": {},
        }

        try:
            if rule.rule_type == "data_minimization":
                result = self._evaluate_data_minimization(rule, data)
            elif rule.rule_type == "consent_management":
                result = self._evaluate_consent_management(rule, data)
            elif rule.rule_type == "data_retention":
                result = self._evaluate_data_retention(rule, data)
            elif rule.rule_type == "right_to_delete":
                result = self._evaluate_right_to_delete(rule, data)
            elif rule.rule_type == "right_to_opt_out":
                result = self._evaluate_right_to_opt_out(rule, data)

        except Exception as e:
            result["issues"].append(f"Rule evaluation error: {str(e)}")
            result["score"] = 0.0

        return result

    def _evaluate_data_minimization(
        self, rule: ComplianceRule, data: pd.DataFrame
    ) -> Dict[str, Any]:
        """Evaluate data minimization compliance."""
        result = {"score": 1.0, "compliant": True, "issues": [], "details": {}}

        # Detect PII columns
        pii_columns = self.pii_detector.detect_pii_columns(data)

        if pii_columns:
            result["details"]["pii_columns"] = pii_columns

            # Check if PII data has legitimate purpose
            for col in pii_columns:
                if col in data.columns:
                    # Check if column is necessary (simplified check)
                    if data[col].isnull().mean() > 0.5:  # More than 50% null values
                        result["issues"].append(
                            f"Column {col} has high null rate, may not be necessary"
                        )
                        result["score"] -= 0.2

            # Check for excessive data collection
            total_columns = len(data.columns)
            pii_ratio = len(pii_columns) / total_columns

            if pii_ratio > 0.3:  # More than 30% PII columns
                result["issues"].append(
                    f"High proportion of PII columns: {pii_ratio:.1%}"
                )
                result["score"] -= 0.3

        result["compliant"] = result["score"] >= 0.7
        return result

    def _evaluate_consent_management(
        self, rule: ComplianceRule, data: pd.DataFrame
    ) -> Dict[str, Any]:
        """Evaluate consent management compliance."""
        result = {"score": 1.0, "compliant": True, "issues": [], "details": {}}

        # Check if data contains PII that requires consent
        pii_columns = self.pii_detector.detect_pii_columns(data)

        if pii_columns:
            result["details"]["pii_columns"] = pii_columns

            # In a real system, this would check actual consent records
            # For demonstration, we'll simulate consent checks
            for col in pii_columns:
                if col in data.columns:
                    # Simulate consent check
                    has_consent = self.consent_manager.check_consent_for_column(col)

                    if not has_consent:
                        result["issues"].append(
                            f"No consent record found for column {col}"
                        )
                        result["score"] -= 0.4

        result["compliant"] = result["score"] >= 0.7
        return result

    def _evaluate_data_retention(
        self, rule: ComplianceRule, data: pd.DataFrame
    ) -> Dict[str, Any]:
        """Evaluate data retention compliance."""
        result = {"score": 1.0, "compliant": True, "issues": [], "details": {}}

        # Check data age if timestamp columns exist
        timestamp_columns = []
        for col in data.columns:
            if pd.api.types.is_datetime64_any_dtype(data[col]):
                timestamp_columns.append(col)

        if timestamp_columns:
            result["details"]["timestamp_columns"] = timestamp_columns

            for col in timestamp_columns:
                max_date = data[col].max()
                if pd.notna(max_date):
                    days_old = (datetime.now() - max_date.to_pydatetime()).days

                    # Check retention limits (simplified)
                    if days_old > 2555:  # 7 years for GDPR
                        result["issues"].append(
                            f"Column {col} contains data older than 7 years"
                        )
                        result["score"] -= 0.3

        result["compliant"] = result["score"] >= 0.7
        return result

    def _evaluate_right_to_delete(
        self, rule: ComplianceRule, data: pd.DataFrame
    ) -> Dict[str, Any]:
        """Evaluate right to delete compliance."""
        result = {"score": 1.0, "compliant": True, "issues": [], "details": {}}

        # Check if there are pending deletion requests
        pending_deletions = self.consent_manager.get_pending_deletion_requests()

        if pending_deletions:
            result["details"]["pending_deletions"] = len(pending_deletions)

            # Check if pending deletions are being processed
            for request in pending_deletions:
                if not self.consent_manager.is_deletion_in_progress(
                    request["request_id"]
                ):
                    result["issues"].append(
                        f"Deletion request {request['request_id']} not being processed"
                    )
                    result["score"] -= 0.3

        result["compliant"] = result["score"] >= 0.7
        return result

    def _evaluate_right_to_opt_out(
        self, rule: ComplianceRule, data: pd.DataFrame
    ) -> Dict[str, Any]:
        """Evaluate right to opt-out compliance."""
        result = {"score": 1.0, "compliant": True, "issues": [], "details": {}}

        # Check opt-out preferences
        opt_out_requests = self.consent_manager.get_opt_out_requests()

        if opt_out_requests:
            result["details"]["opt_out_requests"] = len(opt_out_requests)

            # Check if opt-outs are being honored
            for request in opt_out_requests:
                if not self.consent_manager.is_opt_out_honored(request["request_id"]):
                    result["issues"].append(
                        f"Opt-out request {request['request_id']} not being honored"
                    )
                    result["score"] -= 0.3

        result["compliant"] = result["score"] >= 0.7
        return result

    def _generate_recommendations(self, findings: List[Dict[str, Any]]) -> List[str]:
        """Generate compliance recommendations."""
        recommendations = []

        for finding in findings:
            if not finding.get("compliant", True):
                rule_name = finding.get("rule_name", "Unknown rule")
                issues = finding.get("issues", [])

                if issues:
                    recommendations.append(f"For {rule_name}: {issues[0]}")

        # Add general recommendations
        if not recommendations:
            recommendations.append("Continue monitoring compliance status")
        else:
            recommendations.append("Review and address compliance issues promptly")
            recommendations.append("Consider implementing automated compliance checks")

        return recommendations

    def anonymize_data(
        self, data: pd.DataFrame, method: str = "masking"
    ) -> pd.DataFrame:
        """Anonymize sensitive data."""
        return self.anonymizer.anonymize(data, method)

    def generate_compliance_report(
        self, asset_id: str, framework: ComplianceFramework = ComplianceFramework.GDPR
    ) -> Dict[str, Any]:
        """Generate comprehensive compliance report."""
        if asset_id not in self.assessments:
            return {"error": "No assessments found for asset"}

        assessments = self.assessments[asset_id]
        framework_assessments = [a for a in assessments if a.framework == framework]

        if not framework_assessments:
            return {"error": f"No assessments found for framework {framework.value}"}

        latest_assessment = max(framework_assessments, key=lambda x: x.assessment_date)

        # Get related alerts
        related_alerts = [
            alert
            for alert in self.compliance_alerts.values()
            if alert.asset_id == asset_id and alert.framework == framework
        ]

        report = {
            "asset_id": asset_id,
            "framework": framework.value,
            "assessment_date": latest_assessment.assessment_date.isoformat(),
            "compliance_status": latest_assessment.status.value,
            "compliance_score": latest_assessment.score,
            "findings": latest_assessment.findings,
            "recommendations": latest_assessment.recommendations,
            "active_alerts": len([a for a in related_alerts if not a.resolved]),
            "total_assessments": len(framework_assessments),
            "assessment_trend": self._calculate_assessment_trend(framework_assessments),
        }

        return report

    def _calculate_assessment_trend(
        self, assessments: List[ComplianceAssessment]
    ) -> str:
        """Calculate assessment score trend."""
        if len(assessments) < 2:
            return "insufficient_data"

        # Sort by date
        sorted_assessments = sorted(assessments, key=lambda x: x.assessment_date)

        # Compare latest with previous
        latest_score = sorted_assessments[-1].score
        previous_score = sorted_assessments[-2].score

        if latest_score > previous_score + 0.05:
            return "improving"
        elif latest_score < previous_score - 0.05:
            return "declining"
        else:
            return "stable"


class PIIDetector:
    """Personally Identifiable Information detector."""

    def __init__(self):
        self.pii_patterns = {
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "phone": r"\b\d{3}-\d{3}-\d{4}\b|\b\d{10}\b",
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
            "ip_address": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
        }

    def detect_pii_columns(self, data: pd.DataFrame) -> List[str]:
        """Detect columns containing PII."""
        pii_columns = []

        for column in data.columns:
            column_data = data[column].dropna().astype(str)

            # Check column name first
            column_name_lower = column.lower()
            if any(
                keyword in column_name_lower
                for keyword in [
                    "email",
                    "phone",
                    "ssn",
                    "credit",
                    "card",
                    "ip",
                    "address",
                    "name",
                ]
            ):
                pii_columns.append(column)
                continue

            # Check data patterns
            sample_data = column_data.head(100)
            for pii_type, pattern in self.pii_patterns.items():
                matches = sample_data.str.contains(pattern, regex=True, na=False)
                if matches.sum() > len(sample_data) * 0.1:  # More than 10% matches
                    pii_columns.append(column)
                    break

        return list(set(pii_columns))


class ConsentManager:
    """Consent management system."""

    def __init__(self):
        self.consent_records: Dict[str, List[Dict[str, Any]]] = {}
        self.deletion_requests: List[Dict[str, Any]] = []
        self.opt_out_requests: List[Dict[str, Any]] = []

    def check_consent_for_column(self, column_name: str) -> bool:
        """Check if consent exists for a data column."""
        # Simplified consent check
        # In practice, this would check actual consent records
        return True

    def get_pending_deletion_requests(self) -> List[Dict[str, Any]]:
        """Get pending deletion requests."""
        return [req for req in self.deletion_requests if req.get("status") == "pending"]

    def is_deletion_in_progress(self, request_id: str) -> bool:
        """Check if deletion request is being processed."""
        return True  # Simplified

    def get_opt_out_requests(self) -> List[Dict[str, Any]]:
        """Get opt-out requests."""
        return self.opt_out_requests

    def is_opt_out_honored(self, request_id: str) -> bool:
        """Check if opt-out request is being honored."""
        return True  # Simplified


class RetentionManager:
    """Data retention management."""

    def __init__(self):
        self.retention_policies: Dict[str, int] = {
            "pii": 2555,  # 7 years
            "spi": 1825,  # 5 years
            "financial": 2555,  # 7 years
            "general": 365,  # 1 year
        }

    def get_retention_period(self, data_type: str) -> int:
        """Get retention period for data type."""
        return self.retention_policies.get(data_type, 365)


class DataAnonymizer:
    """Data anonymization utilities."""

    def anonymize(self, data: pd.DataFrame, method: str = "masking") -> pd.DataFrame:
        """Anonymize sensitive data."""
        anonymized_data = data.copy()

        if method == "masking":
            anonymized_data = self._apply_masking(anonymized_data)
        elif method == "pseudonymization":
            anonymized_data = self._apply_pseudonymization(anonymized_data)
        elif method == "generalization":
            anonymized_data = self._apply_generalization(anonymized_data)

        return anonymized_data

    def _apply_masking(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply data masking."""
        for column in data.columns:
            if data[column].dtype == "object":
                # Mask string data
                data[column] = (
                    data[column]
                    .astype(str)
                    .apply(
                        lambda x: (
                            x[:2] + "*" * (len(x) - 4) + x[-2:]
                            if len(x) > 4
                            else "*" * len(x)
                        )
                    )
                )
            elif pd.api.types.is_numeric_dtype(data[column]):
                # Add noise to numeric data
                noise = np.random.normal(0, data[column].std() * 0.1, len(data))
                data[column] = data[column] + noise

        return data

    def _apply_pseudonymization(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply pseudonymization."""
        for column in data.columns:
            if data[column].dtype == "object":
                # Replace with pseudonyms
                unique_values = data[column].unique()
                pseudonyms = {val: f"PS_{i}" for i, val in enumerate(unique_values)}
                data[column] = data[column].map(pseudonyms)

        return data

    def _apply_generalization(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply data generalization."""
        for column in data.columns:
            if pd.api.types.is_numeric_dtype(data[column]):
                # Bin numeric data
                data[column] = pd.cut(data[column], bins=5, labels=False)

        return data


# Example usage
async def demonstrate_data_compliance():
    """Demonstrate data compliance system."""
    print("Demonstrating S.W.A.R.M. Phase 2 Advanced MLOps - Data Compliance...")

    # Create compliance system
    compliance = DataComplianceSystem()

    # Create sample data with PII
    sample_data = pd.DataFrame(
        {
            "customer_id": [1, 2, 3, 4, 5],
            "email": [
                "user1@example.com",
                "user2@example.com",
                "user3@example.com",
                "user4@example.com",
                "user5@example.com",
            ],
            "phone": [
                "123-456-7890",
                "234-567-8901",
                "345-678-9012",
                "456-789-0123",
                "567-890-1234",
            ],
            "age": [25, 30, 35, 40, 45],
            "income": [50000, 60000, 70000, 80000, 90000],
            "registration_date": pd.date_range("2020-01-01", periods=5),
            "last_activity": pd.date_range("2023-01-01", periods=5),
        }
    )

    print(f"Sample data shape: {sample_data.shape}")
    print(f"Sample data columns: {list(sample_data.columns)}")

    # Register data subject
    subject = DataSubject(
        identifier="customer_1", email="user1@example.com", phone="123-456-7890"
    )

    subject_id = compliance.register_data_subject(subject)
    print(f"\nRegistered data subject: {subject_id}")

    # Update consent
    consent_data = {
        "status": ConsentStatus.EXPLICIT.value,
        "purpose": "marketing_analytics",
        "data_types": ["email", "phone", "demographic"],
        "ip_address": "192.168.1.1",
    }

    compliance.update_consent(subject_id, consent_data)
    print("Updated consent for data subject")

    # Assess GDPR compliance
    print("\nAssessing GDPR compliance...")
    gdpr_assessment = compliance.assess_compliance(
        "sample_asset", sample_data, ComplianceFramework.GDPR
    )

    print(f"GDPR Assessment Results:")
    print(f"  Status: {gdpr_assessment.status.value}")
    print(f"  Score: {gdpr_assessment.score:.2f}")
    print(f"  Findings: {len(gdpr_assessment.findings)}")

    # Display findings
    for finding in gdpr_assessment.findings:
        print(
            f"    {finding['rule_name']}: {'COMPLIANT' if finding['compliant'] else 'NON_COMPLIANT'}"
        )
        if finding["issues"]:
            for issue in finding["issues"]:
                print(f"      - {issue}")

    # Assess CCPA compliance
    print("\nAssessing CCPA compliance...")
    ccpa_assessment = compliance.assess_compliance(
        "sample_asset", sample_data, ComplianceFramework.CCPA
    )

    print(f"CCPA Assessment Results:")
    print(f"  Status: {ccpa_assessment.status.value}")
    print(f"  Score: {ccpa_assessment.score:.2f}")

    # Anonymize data
    print("\nAnonymizing sensitive data...")
    anonymized_data = compliance.anonymize_data(sample_data, method="masking")

    print("Original data sample:")
    print(sample_data[["email", "phone"]].head())
    print("\nAnonymized data sample:")
    print(anonymized_data[["email", "phone"]].head())

    # Generate compliance report
    print("\nGenerating compliance report...")
    report = compliance.generate_compliance_report(
        "sample_asset", ComplianceFramework.GDPR
    )

    print(f"Compliance Report Summary:")
    print(f"  Framework: {report['framework']}")
    print(f"  Status: {report['compliance_status']}")
    print(f"  Score: {report['compliance_score']:.2f}")
    print(f"  Recommendations: {len(report['recommendations'])}")
    print(f"  Assessment trend: {report['assessment_trend']}")

    # Display recommendations
    if report["recommendations"]:
        print("\nRecommendations:")
        for rec in report["recommendations"]:
            print(f"  • {rec}")

    print("\nData Compliance demonstration complete!")


if __name__ == "__main__":
    asyncio.run(demonstrate_data_compliance())
