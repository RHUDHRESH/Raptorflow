"""
S.W.A.R.M. Phase 2: Advanced MLOps - Data Governance System
Production-ready data governance with policies, access control, and audit trails
"""

import asyncio
import hashlib
import json
import logging
import os
import pickle
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

logger = logging.getLogger("raptorflow.data_governance")


class DataClassification(Enum):
    """Data classification levels."""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class AccessLevel(Enum):
    """User access levels."""

    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    ADMIN = "admin"
    OWNER = "owner"


class PolicyType(Enum):
    """Types of governance policies."""

    ACCESS_CONTROL = "access_control"
    DATA_RETENTION = "data_retention"
    DATA_QUALITY = "data_quality"
    PRIVACY = "privacy"
    SECURITY = "security"
    COMPLIANCE = "compliance"


class PolicyStatus(Enum):
    """Policy status."""

    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class ActionType(Enum):
    """Types of actions for audit logging."""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    SHARE = "share"
    EXPORT = "export"
    MODIFY = "modify"
    APPROVE = "approve"
    REJECT = "reject"


@dataclass
class DataAsset:
    """Data asset metadata."""

    asset_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    classification: DataClassification = DataClassification.INTERNAL
    owner: str = ""
    steward: str = ""
    tags: List[str] = field(default_factory=list)
    schema: Dict[str, Any] = field(default_factory=dict)
    location: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    size_bytes: int = 0
    row_count: int = 0
    column_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "asset_id": self.asset_id,
            "name": self.name,
            "description": self.description,
            "classification": self.classification.value,
            "owner": self.owner,
            "steward": self.steward,
            "tags": self.tags,
            "schema": self.schema,
            "location": self.location,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "size_bytes": self.size_bytes,
            "row_count": self.row_count,
            "column_count": self.column_count,
        }


@dataclass
class GovernancePolicy:
    """Data governance policy."""

    policy_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    policy_type: PolicyType = PolicyType.ACCESS_CONTROL
    status: PolicyStatus = PolicyStatus.DRAFT
    rules: List[Dict[str, Any]] = field(default_factory=list)
    applies_to: List[str] = field(default_factory=list)  # Asset IDs or classifications
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: int = 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "policy_id": self.policy_id,
            "name": self.name,
            "description": self.description,
            "policy_type": self.policy_type.value,
            "status": self.status.value,
            "rules": self.rules,
            "applies_to": self.applies_to,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
        }


@dataclass
class UserAccess:
    """User access permissions."""

    user_id: str = ""
    asset_id: str = ""
    access_level: AccessLevel = AccessLevel.READ_ONLY
    granted_by: str = ""
    granted_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    conditions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "asset_id": self.asset_id,
            "access_level": self.access_level.value,
            "granted_by": self.granted_by,
            "granted_at": self.granted_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "conditions": self.conditions,
        }


@dataclass
class AuditLog:
    """Audit log entry."""

    log_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    asset_id: str = ""
    action: ActionType = ActionType.READ
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)
    ip_address: str = ""
    user_agent: str = ""
    success: bool = True
    error_message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "log_id": self.log_id,
            "user_id": self.user_id,
            "asset_id": self.asset_id,
            "action": self.action.value,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "success": self.success,
            "error_message": self.error_message,
        }


class DataGovernanceSystem:
    """Production-ready data governance system."""

    def __init__(self):
        self.data_assets: Dict[str, DataAsset] = {}
        self.policies: Dict[str, GovernancePolicy] = {}
        self.user_access: Dict[str, List[UserAccess]] = {}  # user_id -> list of access
        self.audit_logs: List[AuditLog] = []
        self.policy_engine = PolicyEngine(self)
        self.access_manager = AccessManager(self)
        self.audit_logger = AuditLogger(self)

    def register_data_asset(self, asset: DataAsset) -> str:
        """Register a new data asset."""
        self.data_assets[asset.asset_id] = asset
        self.audit_logger.log_action(
            user_id=asset.owner,
            asset_id=asset.asset_id,
            action=ActionType.WRITE,
            details={"action": "register_asset", "asset_name": asset.name},
        )
        logger.info(f"Registered data asset: {asset.asset_id}")
        return asset.asset_id

    def update_data_asset(
        self, asset_id: str, updates: Dict[str, Any], user_id: str
    ) -> bool:
        """Update data asset metadata."""
        if asset_id not in self.data_assets:
            raise ValueError(f"Asset {asset_id} not found")

        asset = self.data_assets[asset_id]

        # Check if user has permission to update
        if not self.access_manager.can_modify_asset(user_id, asset_id):
            self.audit_logger.log_action(
                user_id=user_id,
                asset_id=asset_id,
                action=ActionType.MODIFY,
                success=False,
                error_message="Insufficient permissions",
            )
            raise PermissionError(
                f"User {user_id} does not have permission to modify asset {asset_id}"
            )

        # Update asset
        for key, value in updates.items():
            if hasattr(asset, key):
                setattr(asset, key, value)

        asset.updated_at = datetime.now()

        self.audit_logger.log_action(
            user_id=user_id,
            asset_id=asset_id,
            action=ActionType.MODIFY,
            details={"updates": updates},
        )

        logger.info(f"Updated data asset: {asset_id}")
        return True

    def create_policy(self, policy: GovernancePolicy) -> str:
        """Create a new governance policy."""
        self.policies[policy.policy_id] = policy
        logger.info(f"Created governance policy: {policy.policy_id}")
        return policy.policy_id

    def activate_policy(self, policy_id: str, user_id: str) -> bool:
        """Activate a governance policy."""
        if policy_id not in self.policies:
            raise ValueError(f"Policy {policy_id} not found")

        policy = self.policies[policy_id]
        policy.status = PolicyStatus.ACTIVE
        policy.updated_at = datetime.now()

        self.audit_logger.log_action(
            user_id=user_id,
            asset_id=policy_id,
            action=ActionType.APPROVE,
            details={"action": "activate_policy", "policy_name": policy.name},
        )

        logger.info(f"Activated governance policy: {policy_id}")
        return True

    def grant_access(
        self,
        user_id: str,
        asset_id: str,
        access_level: AccessLevel,
        granted_by: str,
        expires_at: Optional[datetime] = None,
    ) -> bool:
        """Grant access to a data asset."""
        if asset_id not in self.data_assets:
            raise ValueError(f"Asset {asset_id} not found")

        # Check if granter has permission
        if not self.access_manager.can_grant_access(granted_by, asset_id, access_level):
            raise PermissionError(
                f"User {granted_by} cannot grant {access_level.value} access to {asset_id}"
            )

        # Create access record
        access = UserAccess(
            user_id=user_id,
            asset_id=asset_id,
            access_level=access_level,
            granted_by=granted_by,
            expires_at=expires_at,
        )

        # Add to user access
        if user_id not in self.user_access:
            self.user_access[user_id] = []

        # Remove existing access to same asset if any
        self.user_access[user_id] = [
            a for a in self.user_access[user_id] if a.asset_id != asset_id
        ]
        self.user_access[user_id].append(access)

        self.audit_logger.log_action(
            user_id=granted_by,
            asset_id=asset_id,
            action=ActionType.WRITE,
            details={
                "action": "grant_access",
                "target_user": user_id,
                "access_level": access_level.value,
            },
        )

        logger.info(
            f"Granted {access_level.value} access to {asset_id} for user {user_id}"
        )
        return True

    def revoke_access(self, user_id: str, asset_id: str, revoked_by: str) -> bool:
        """Revoke access to a data asset."""
        if user_id not in self.user_access:
            return False

        # Remove access
        original_count = len(self.user_access[user_id])
        self.user_access[user_id] = [
            a for a in self.user_access[user_id] if a.asset_id != asset_id
        ]

        if len(self.user_access[user_id]) < original_count:
            self.audit_logger.log_action(
                user_id=revoked_by,
                asset_id=asset_id,
                action=ActionType.DELETE,
                details={"action": "revoke_access", "target_user": user_id},
            )

            logger.info(f"Revoked access to {asset_id} for user {user_id}")
            return True

        return False

    def check_access(
        self, user_id: str, asset_id: str, required_access: AccessLevel
    ) -> bool:
        """Check if user has required access to asset."""
        return self.access_manager.check_access(user_id, asset_id, required_access)

    def get_asset_metadata(self, asset_id: str, user_id: str) -> Optional[DataAsset]:
        """Get asset metadata if user has access."""
        if not self.check_access(user_id, asset_id, AccessLevel.READ_ONLY):
            self.audit_logger.log_action(
                user_id=user_id,
                asset_id=asset_id,
                action=ActionType.READ,
                success=False,
                error_message="Insufficient permissions",
            )
            return None

        asset = self.data_assets.get(asset_id)
        if asset:
            self.audit_logger.log_action(
                user_id=user_id,
                asset_id=asset_id,
                action=ActionType.READ,
                details={"action": "get_metadata"},
            )

        return asset

    def search_assets(
        self, user_id: str, filters: Dict[str, Any] = None
    ) -> List[DataAsset]:
        """Search data assets based on filters."""
        if filters is None:
            filters = {}

        accessible_assets = []

        for asset in self.data_assets.values():
            # Check access
            if not self.check_access(user_id, asset.asset_id, AccessLevel.READ_ONLY):
                continue

            # Apply filters
            matches = True

            if "classification" in filters:
                if asset.classification.value != filters["classification"]:
                    matches = False

            if "owner" in filters:
                if asset.owner != filters["owner"]:
                    matches = False

            if "tags" in filters:
                required_tags = set(filters["tags"])
                asset_tags = set(asset.tags)
                if not required_tags.issubset(asset_tags):
                    matches = False

            if "name_contains" in filters:
                if filters["name_contains"].lower() not in asset.name.lower():
                    matches = False

            if matches:
                accessible_assets.append(asset)

        self.audit_logger.log_action(
            user_id=user_id,
            asset_id="search",
            action=ActionType.READ,
            details={"filters": filters, "result_count": len(accessible_assets)},
        )

        return accessible_assets

    def get_audit_logs(
        self, user_id: str, filters: Dict[str, Any] = None, limit: int = 100
    ) -> List[AuditLog]:
        """Get audit logs based on filters."""
        if filters is None:
            filters = {}

        # Check if user has admin access
        has_admin_access = any(
            access.access_level in [AccessLevel.ADMIN, AccessLevel.OWNER]
            for access in self.user_access.get(user_id, [])
        )

        if not has_admin_access:
            # Users can only see their own logs
            filtered_logs = [log for log in self.audit_logs if log.user_id == user_id]
        else:
            filtered_logs = self.audit_logs.copy()

        # Apply filters
        if "asset_id" in filters:
            filtered_logs = [
                log for log in filtered_logs if log.asset_id == filters["asset_id"]
            ]

        if "action" in filters:
            filtered_logs = [
                log for log in filtered_logs if log.action.value == filters["action"]
            ]

        if "start_date" in filters:
            start_date = pd.to_datetime(filters["start_date"])
            filtered_logs = [
                log for log in filtered_logs if log.timestamp >= start_date
            ]

        if "end_date" in filters:
            end_date = pd.to_datetime(filters["end_date"])
            filtered_logs = [log for log in filtered_logs if log.timestamp <= end_date]

        # Sort by timestamp descending and limit
        filtered_logs.sort(key=lambda x: x.timestamp, reverse=True)

        return filtered_logs[:limit]

    def get_governance_summary(self) -> Dict[str, Any]:
        """Get governance system summary."""
        total_assets = len(self.data_assets)
        total_policies = len(self.policies)
        active_policies = sum(
            1 for p in self.policies.values() if p.status == PolicyStatus.ACTIVE
        )
        total_users = len(self.user_access)
        total_audit_logs = len(self.audit_logs)

        # Asset classification distribution
        classification_counts = {}
        for asset in self.data_assets.values():
            classification = asset.classification.value
            classification_counts[classification] = (
                classification_counts.get(classification, 0) + 1
            )

        # Policy type distribution
        policy_type_counts = {}
        for policy in self.policies.values():
            policy_type = policy.policy_type.value
            policy_type_counts[policy_type] = policy_type_counts.get(policy_type, 0) + 1

        # Recent activity
        recent_time = datetime.now() - timedelta(days=7)
        recent_logs = [log for log in self.audit_logs if log.timestamp >= recent_time]

        return {
            "total_assets": total_assets,
            "total_policies": total_policies,
            "active_policies": active_policies,
            "total_users": total_users,
            "total_audit_logs": total_audit_logs,
            "classification_distribution": classification_counts,
            "policy_type_distribution": policy_type_counts,
            "recent_activity": {
                "logs_last_7_days": len(recent_logs),
                "unique_users_active": len(set(log.user_id for log in recent_logs)),
                "most_common_actions": self._get_most_common_actions(recent_logs),
            },
        }

    def _get_most_common_actions(self, logs: List[AuditLog]) -> List[Dict[str, Any]]:
        """Get most common actions from logs."""
        action_counts = {}
        for log in logs:
            action = log.action.value
            action_counts[action] = action_counts.get(action, 0) + 1

        return [
            {"action": action, "count": count}
            for action, count in sorted(
                action_counts.items(), key=lambda x: x[1], reverse=True
            )[:5]
        ]


class PolicyEngine:
    """Policy evaluation engine."""

    def __init__(self, governance_system: DataGovernanceSystem):
        self.governance_system = governance_system

    def evaluate_policies(
        self, user_id: str, asset_id: str, action: ActionType
    ) -> Dict[str, Any]:
        """Evaluate applicable policies for an action."""
        asset = self.governance_system.data_assets.get(asset_id)
        if not asset:
            return {"allowed": False, "reason": "Asset not found"}

        applicable_policies = []

        for policy in self.governance_system.policies.values():
            if policy.status != PolicyStatus.ACTIVE:
                continue

            # Check if policy applies to this asset
            if (
                asset_id in policy.applies_to
                or asset.classification.value in policy.applies_to
            ):
                applicable_policies.append(policy)

        # Evaluate each policy
        policy_results = []
        for policy in applicable_policies:
            result = self._evaluate_policy(policy, user_id, asset, action)
            policy_results.append(result)

        # Overall decision (all policies must allow)
        allowed = all(result["allowed"] for result in policy_results)
        blocked_policies = [r for r in policy_results if not r["allowed"]]

        return {
            "allowed": allowed,
            "applicable_policies": len(applicable_policies),
            "policy_results": policy_results,
            "blocked_by": blocked_policies if not allowed else [],
        }

    def _evaluate_policy(
        self,
        policy: GovernancePolicy,
        user_id: str,
        asset: DataAsset,
        action: ActionType,
    ) -> Dict[str, Any]:
        """Evaluate a single policy."""
        # This is a simplified policy evaluation
        # In practice, this would be more sophisticated with rule engines

        for rule in policy.rules:
            if rule.get("action") == action.value:
                if rule.get("allow", True):
                    return {"allowed": True, "policy_id": policy.policy_id}
                else:
                    return {
                        "allowed": False,
                        "policy_id": policy.policy_id,
                        "reason": rule.get("reason", "Policy restriction"),
                    }

        # Default to allow if no specific rule found
        return {"allowed": True, "policy_id": policy.policy_id}


class AccessManager:
    """Access control manager."""

    def __init__(self, governance_system: DataGovernanceSystem):
        self.governance_system = governance_system

    def check_access(
        self, user_id: str, asset_id: str, required_access: AccessLevel
    ) -> bool:
        """Check if user has required access level."""
        if user_id not in self.governance_system.user_access:
            return False

        user_access_list = self.governance_system.user_access[user_id]

        for access in user_access_list:
            if access.asset_id == asset_id:
                # Check if access has expired
                if access.expires_at and access.expires_at < datetime.now():
                    continue

                # Check access level hierarchy
                if self._has_sufficient_access(access.access_level, required_access):
                    return True

        return False

    def can_modify_asset(self, user_id: str, asset_id: str) -> bool:
        """Check if user can modify asset."""
        return self.check_access(user_id, asset_id, AccessLevel.READ_WRITE)

    def can_grant_access(
        self, user_id: str, asset_id: str, grant_level: AccessLevel
    ) -> bool:
        """Check if user can grant specified access level."""
        # Only admins and owners can grant access
        if user_id not in self.governance_system.user_access:
            return False

        user_access_list = self.governance_system.user_access[user_id]

        for access in user_access_list:
            if access.asset_id == asset_id:
                if access.access_level in [AccessLevel.ADMIN, AccessLevel.OWNER]:
                    return True

        return False

    def _has_sufficient_access(
        self, current_access: AccessLevel, required_access: AccessLevel
    ) -> bool:
        """Check if current access level is sufficient for required access."""
        access_hierarchy = {
            AccessLevel.READ_ONLY: 1,
            AccessLevel.READ_WRITE: 2,
            AccessLevel.ADMIN: 3,
            AccessLevel.OWNER: 4,
        }

        return access_hierarchy[current_access] >= access_hierarchy[required_access]


class AuditLogger:
    """Audit logging system."""

    def __init__(self, governance_system: DataGovernanceSystem):
        self.governance_system = governance_system

    def log_action(
        self,
        user_id: str,
        asset_id: str,
        action: ActionType,
        details: Dict[str, Any] = None,
        success: bool = True,
        error_message: str = "",
        ip_address: str = "",
        user_agent: str = "",
    ):
        """Log an action."""
        log_entry = AuditLog(
            user_id=user_id,
            asset_id=asset_id,
            action=action,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            error_message=error_message,
        )

        self.governance_system.audit_logs.append(log_entry)

        # Keep only last 10000 logs to prevent memory issues
        if len(self.governance_system.audit_logs) > 10000:
            self.governance_system.audit_logs = self.governance_system.audit_logs[
                -10000:
            ]


# Example usage
async def demonstrate_data_governance():
    """Demonstrate data governance system."""
    print("Demonstrating S.W.A.R.M. Phase 2 Advanced MLOps - Data Governance...")

    # Create governance system
    governance = DataGovernanceSystem()

    # Create data assets
    customer_asset = DataAsset(
        name="Customer Data",
        description="Customer personal and transaction data",
        classification=DataClassification.CONFIDENTIAL,
        owner="data_owner@example.com",
        steward="data_steward@example.com",
        tags=["customer", "personal", "pii"],
        location="s3://bucket/customer_data/",
        size_bytes=1000000,
        row_count=10000,
        column_count=25,
    )

    product_asset = DataAsset(
        name="Product Catalog",
        description="Product information and pricing",
        classification=DataClassification.INTERNAL,
        owner="product_owner@example.com",
        steward="product_steward@example.com",
        tags=["product", "catalog", "pricing"],
        location="s3://bucket/product_data/",
        size_bytes=500000,
        row_count=5000,
        column_count=15,
    )

    # Register assets
    customer_id = governance.register_data_asset(customer_asset)
    product_id = governance.register_data_asset(product_asset)

    print(f"Registered data assets: {customer_id}, {product_id}")

    # Create governance policies
    access_policy = GovernancePolicy(
        name="Data Access Control",
        description="Controls access to confidential data",
        policy_type=PolicyType.ACCESS_CONTROL,
        status=PolicyStatus.ACTIVE,
        rules=[
            {"action": "read", "allow": True, "conditions": ["approved_training"]},
            {
                "action": "export",
                "allow": False,
                "reason": "Export not allowed for confidential data",
            },
        ],
        applies_to=[DataClassification.CONFIDENTIAL.value],
        created_by="admin@example.com",
    )

    retention_policy = GovernancePolicy(
        name="Data Retention",
        description="Data retention and deletion policies",
        policy_type=PolicyType.DATA_RETENTION,
        status=PolicyStatus.ACTIVE,
        rules=[
            {"classification": "confidential", "retention_days": 2555},  # 7 years
            {"classification": "internal", "retention_days": 1825},  # 5 years
        ],
        applies_to=["all"],
        created_by="admin@example.com",
    )

    # Create policies
    access_policy_id = governance.create_policy(access_policy)
    retention_policy_id = governance.create_policy(retention_policy)

    print(f"Created governance policies: {access_policy_id}, {retention_policy_id}")

    # Grant access to users
    governance.grant_access(
        "analyst@example.com", customer_id, AccessLevel.READ_ONLY, "admin@example.com"
    )
    governance.grant_access(
        "analyst@example.com", product_id, AccessLevel.READ_WRITE, "admin@example.com"
    )
    governance.grant_access(
        "admin@example.com", customer_id, AccessLevel.ADMIN, "data_owner@example.com"
    )

    print("Granted access permissions to users")

    # Test access control
    print("\nTesting access control:")

    # Analyst should have read access to customer data
    can_read_customer = governance.check_access(
        "analyst@example.com", customer_id, AccessLevel.READ_ONLY
    )
    print(f"  Analyst can read customer data: {can_read_customer}")

    # Analyst should not have admin access to customer data
    can_admin_customer = governance.check_access(
        "analyst@example.com", customer_id, AccessLevel.ADMIN
    )
    print(f"  Analyst can admin customer data: {can_admin_customer}")

    # Analyst should have read-write access to product data
    can_write_product = governance.check_access(
        "analyst@example.com", product_id, AccessLevel.READ_WRITE
    )
    print(f"  Analyst can write product data: {can_write_product}")

    # Search assets
    print("\nSearching assets:")
    confidential_assets = governance.search_assets(
        "analyst@example.com", {"classification": "confidential"}
    )
    print(f"  Confidential assets accessible to analyst: {len(confidential_assets)}")

    all_assets = governance.search_assets("admin@example.com")
    print(f"  All assets accessible to admin: {len(all_assets)}")

    # Get governance summary
    summary = governance.get_governance_summary()
    print(f"\nGovernance Summary:")
    print(f"  Total assets: {summary['total_assets']}")
    print(f"  Total policies: {summary['total_policies']}")
    print(f"  Active policies: {summary['active_policies']}")
    print(f"  Total users: {summary['total_users']}")
    print(f"  Total audit logs: {summary['total_audit_logs']}")
    print(f"  Classification distribution: {summary['classification_distribution']}")

    # Get audit logs
    print("\nRecent audit logs:")
    recent_logs = governance.get_audit_logs("admin@example.com", limit=5)
    for log in recent_logs:
        print(
            f"  {log.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {log.user_id} - {log.action.value} - {log.asset_id}"
        )

    print("\nData Governance demonstration complete!")


if __name__ == "__main__":
    asyncio.run(demonstrate_data_governance())
