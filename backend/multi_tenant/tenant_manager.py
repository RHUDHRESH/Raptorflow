"""
Multi-Tenant Architecture
Advanced multi-tenant management system for Raptorflow
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import asyncio
import uuid
import hashlib
from collections import defaultdict
from functools import wraps

logger = logging.getLogger(__name__)


class TenantStatus(str, Enum):
    """Tenant status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    CANCELLED = "cancelled"


class TenantTier(str, Enum):
    """Tenant subscription tiers"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class TenantIsolationLevel(str, Enum):
    """Data isolation levels"""
    SHARED = "shared"
    SCHEMA = "schema"
    DATABASE = "database"


@dataclass
class TenantConfig:
    """Tenant configuration"""
    max_users: int
    max_workspaces: int
    max_storage_gb: int
    max_api_calls_per_day: int
    features: List[str]
    custom_limits: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "max_users": self.max_users,
            "max_workspaces": self.max_workspaces,
            "max_storage_gb": self.max_storage_gb,
            "max_api_calls_per_day": self.max_api_calls_per_day,
            "features": self.features,
            "custom_limits": self.custom_limits
        }


@dataclass
class Tenant:
    """Multi-tenant organization"""
    id: str
    name: str
    domain: str
    tier: TenantTier
    status: TenantStatus
    isolation_level: TenantIsolationLevel
    config: TenantConfig
    created_at: datetime
    updated_at: datetime
    trial_ends_at: Optional[datetime] = None
    subscription_id: Optional[str] = None
    billing_email: str = ""
    admin_user_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "domain": self.domain,
            "tier": self.tier.value,
            "status": self.status.value,
            "isolation_level": self.isolation_level.value,
            "config": self.config.to_dict(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "trial_ends_at": self.trial_ends_at.isoformat() if self.trial_ends_at else None,
            "subscription_id": self.subscription_id,
            "billing_email": self.billing_email,
            "admin_user_id": self.admin_user_id,
            "metadata": self.metadata
        }


@dataclass
class TenantContext:
    """Tenant context for request processing"""
    tenant_id: str
    tenant: Tenant
    user_id: str
    workspace_id: str
    request_id: str
    permissions: List[str] = field(default_factory=list)
    session_data: Dict[str, Any] = field(default_factory=dict)
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has permission"""
        return permission in self.permissions
    
    def has_feature(self, feature: str) -> bool:
        """Check if tenant has feature"""
        return feature in self.tenant.config.features


class TenantManager:
    """Multi-tenant management system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Tenant storage
        self.tenants: Dict[str, Tenant] = {}
        
        # Domain to tenant mapping
        self.domain_mapping: Dict[str, str] = {}
        
        # User to tenant mapping
        self.user_tenant_mapping: Dict[str, str] = {}
        
        # Tier configurations
        self.tier_configs: Dict[TenantTier, TenantConfig] = self._initialize_tier_configs()
        
        # Usage tracking
        self.usage_tracking: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Request context
        self.request_context: Dict[str, TenantContext] = {}
    
    def _initialize_tier_configs(self) -> Dict[TenantTier, TenantConfig]:
        """Initialize tier configurations"""
        return {
            TenantTier.FREE: TenantConfig(
                max_users=3,
                max_workspaces=1,
                max_storage_gb=1,
                max_api_calls_per_day=100,
                features=["basic_onboarding", "evidence_upload", "basic_reports"]
            ),
            TenantTier.STARTER: TenantConfig(
                max_users=10,
                max_workspaces=3,
                max_storage_gb=10,
                max_api_calls_per_day=1000,
                features=["basic_onboarding", "evidence_upload", "basic_reports", "ai_agents", "analytics"]
            ),
            TenantTier.PROFESSIONAL: TenantConfig(
                max_users=50,
                max_workspaces=10,
                max_storage_gb=100,
                max_api_calls_per_day=10000,
                features=["basic_onboarding", "evidence_upload", "basic_reports", "ai_agents", "analytics", "advanced_ai", "collaboration", "api_access"]
            ),
            TenantTier.ENTERPRISE: TenantConfig(
                max_users=500,
                max_workspaces=50,
                max_storage_gb=1000,
                max_api_calls_per_day=100000,
                features=["basic_onboarding", "evidence_upload", "basic_reports", "ai_agents", "analytics", "advanced_ai", "collaboration", "api_access", "custom_integrations", "priority_support", "white_label"]
            ),
            TenantTier.CUSTOM: TenantConfig(
                max_users=1000,
                max_workspaces=100,
                max_storage_gb=5000,
                max_api_calls_per_day=500000,
                features=["all_features"],
                custom_limits={"unlimited_api": True, "custom_integrations": True}
            )
        }
    
    async def create_tenant(self, name: str, domain: str, tier: TenantTier, admin_user_id: str, billing_email: str, trial_days: int = 30) -> Tenant:
        """Create a new tenant"""
        # Generate tenant ID
        tenant_id = f"tenant_{uuid.uuid4().hex[:8]}"
        
        # Check domain availability
        if domain in self.domain_mapping:
            raise ValueError(f"Domain {domain} is already taken")
        
        # Create tenant
        now = datetime.now()
        trial_ends_at = now + timedelta(days=trial_days) if trial_days > 0 else None
        
        tenant = Tenant(
            id=tenant_id,
            name=name,
            domain=domain,
            tier=tier,
            status=TenantStatus.TRIAL if trial_days > 0 else TenantStatus.ACTIVE,
            isolation_level=TenantIsolationLevel.SCHEMA,  # Default to schema isolation
            config=self.tier_configs[tier],
            created_at=now,
            updated_at=now,
            trial_ends_at=trial_ends_at,
            billing_email=billing_email,
            admin_user_id=admin_user_id
        )
        
        # Store tenant
        self.tenants[tenant_id] = tenant
        self.domain_mapping[domain] = tenant_id
        self.user_tenant_mapping[admin_user_id] = tenant_id
        
        # Initialize usage tracking
        self.usage_tracking[tenant_id] = {
            "api_calls": 0,
            "storage_used_gb": 0,
            "users_count": 1,
            "workspaces_count": 0,
            "last_reset": now.date()
        }
        
        self.logger.info(f"Created tenant: {tenant_id} ({name})")
        return tenant
    
    async def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID"""
        return self.tenants.get(tenant_id)
    
    async def get_tenant_by_domain(self, domain: str) -> Optional[Tenant]:
        """Get tenant by domain"""
        tenant_id = self.domain_mapping.get(domain)
        if tenant_id:
            return self.tenants.get(tenant_id)
        return None
    
    async def get_tenant_by_user(self, user_id: str) -> Optional[Tenant]:
        """Get tenant by user ID"""
        tenant_id = self.user_tenant_mapping.get(user_id)
        if tenant_id:
            return self.tenants.get(tenant_id)
        return None
    
    async def update_tenant(self, tenant_id: str, updates: Dict[str, Any]) -> bool:
        """Update tenant information"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
        
        # Update tenant
        for key, value in updates.items():
            if hasattr(tenant, key):
                setattr(tenant, key, value)
        
        tenant.updated_at = datetime.now()
        
        # Update domain mapping if domain changed
        if "domain" in updates:
            # Remove old domain mapping
            old_domain = next((d for d, tid in self.domain_mapping.items() if tid == tenant_id), None)
            if old_domain:
                del self.domain_mapping[old_domain]
            
            # Add new domain mapping
            self.domain_mapping[updates["domain"]] = tenant_id
        
        self.logger.info(f"Updated tenant: {tenant_id}")
        return True
    
    async def upgrade_tenant(self, tenant_id: str, new_tier: TenantTier) -> bool:
        """Upgrade tenant to higher tier"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
        
        # Check if upgrade is valid
        tier_hierarchy = [TenantTier.FREE, TenantTier.STARTER, TenantTier.PROFESSIONAL, TenantTier.ENTERPRISE, TenantTier.CUSTOM]
        current_index = tier_hierarchy.index(tenant.tier)
        new_index = tier_hierarchy.index(new_tier)
        
        if new_index <= current_index:
            raise ValueError(f"Cannot downgrade from {tenant.tier} to {new_tier}")
        
        # Update tenant
        tenant.tier = new_tier
        tenant.config = self.tier_configs[new_tier]
        tenant.updated_at = datetime.now()
        
        self.logger.info(f"Upgraded tenant {tenant_id} to {new_tier.value}")
        return True
    
    async def add_user_to_tenant(self, tenant_id: str, user_id: str) -> bool:
        """Add user to tenant"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
        
        # Check user limit
        current_users = len([uid for uid, tid in self.user_tenant_mapping.items() if tid == tenant_id])
        if current_users >= tenant.config.max_users:
            raise ValueError(f"Tenant {tenant_id} has reached maximum user limit")
        
        # Remove user from previous tenant if exists
        old_tenant_id = self.user_tenant_mapping.get(user_id)
        if old_tenant_id:
            del self.user_tenant_mapping[user_id]
        
        # Add to new tenant
        self.user_tenant_mapping[user_id] = tenant_id
        
        # Update usage tracking
        self.usage_tracking[tenant_id]["users_count"] = current_users + 1
        
        self.logger.info(f"Added user {user_id} to tenant {tenant_id}")
        return True
    
    async def remove_user_from_tenant(self, tenant_id: str, user_id: str) -> bool:
        """Remove user from tenant"""
        if self.user_tenant_mapping.get(user_id) != tenant_id:
            return False
        
        # Remove mapping
        del self.user_tenant_mapping[user_id]
        
        # Update usage tracking
        current_users = len([uid for uid, tid in self.user_tenant_mapping.items() if tid == tenant_id])
        self.usage_tracking[tenant_id]["users_count"] = max(0, current_users - 1)
        
        self.logger.info(f"Removed user {user_id} from tenant {tenant_id}")
        return True
    
    async def check_tenant_limits(self, tenant_id: str, resource_type: str, amount: int = 1) -> Tuple[bool, str]:
        """Check if tenant has not exceeded limits"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False, "Tenant not found"
        
        # Check tenant status
        if tenant.status == TenantStatus.SUSPENDED:
            return False, "Tenant is suspended"
        elif tenant.status == TenantStatus.CANCELLED:
            return False, "Tenant is cancelled"
        elif tenant.status == TenantStatus.INACTIVE:
            return False, "Tenant is inactive"
        
        # Check trial status
        if tenant.status == TenantStatus.TRIAL and tenant.trial_ends_at:
            if datetime.now() > tenant.trial_ends_at:
                return False, "Trial has expired"
        
        # Check specific limits
        usage = self.usage_tracking[tenant_id]
        
        if resource_type == "api_calls":
            daily_limit = tenant.config.max_api_calls_per_day
            if usage["api_calls"] + amount > daily_limit:
                return False, f"API call limit exceeded ({daily_limit} per day)"
        
        elif resource_type == "storage":
            storage_limit = tenant.config.max_storage_gb
            if usage["storage_used_gb"] + amount > storage_limit:
                return False, f"Storage limit exceeded ({storage_limit} GB)"
        
        elif resource_type == "users":
            user_limit = tenant.config.max_users
            if usage["users_count"] + amount > user_limit:
                return False, f"User limit exceeded ({user_limit} users)"
        
        elif resource_type == "workspaces":
            workspace_limit = tenant.config.max_workspaces
            if usage["workspaces_count"] + amount > workspace_limit:
                return False, f"Workspace limit exceeded ({workspace_limit} workspaces)"
        
        return True, "Limits OK"
    
    async def track_usage(self, tenant_id: str, resource_type: str, amount: int = 1):
        """Track resource usage"""
        if tenant_id not in self.usage_tracking:
            return
        
        usage = self.usage_tracking[tenant_id]
        
        # Reset daily counters if needed
        today = datetime.now().date()
        if usage["last_reset"] < today:
            usage["api_calls"] = 0
            usage["last_reset"] = today
        
        # Update usage
        if resource_type == "api_calls":
            usage["api_calls"] += amount
        elif resource_type == "storage":
            usage["storage_used_gb"] += amount
        elif resource_type == "users":
            usage["users_count"] += amount
        elif resource_type == "workspaces":
            usage["workspaces_count"] += amount
    
    async def get_tenant_usage(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant usage statistics"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return {}
        
        usage = self.usage_tracking[tenant_id]
        
        return {
            "tenant_id": tenant_id,
            "tenant_name": tenant.name,
            "tier": tenant.tier.value,
            "api_calls": {
                "used": usage["api_calls"],
                "limit": tenant.config.max_api_calls_per_day,
                "percentage": (usage["api_calls"] / tenant.config.max_api_calls_per_day) * 100
            },
            "storage": {
                "used_gb": usage["storage_used_gb"],
                "limit_gb": tenant.config.max_storage_gb,
                "percentage": (usage["storage_used_gb"] / tenant.config.max_storage_gb) * 100
            },
            "users": {
                "count": usage["users_count"],
                "limit": tenant.config.max_users,
                "percentage": (usage["users_count"] / tenant.config.max_users) * 100
            },
            "workspaces": {
                "count": usage["workspaces_count"],
                "limit": tenant.config.max_workspaces,
                "percentage": (usage["workspaces_count"] / tenant.config.max_workspaces) * 100
            },
            "last_updated": datetime.now().isoformat()
        }
    
    async def get_all_tenants(self, status: Optional[TenantStatus] = None) -> List[Tenant]:
        """Get all tenants, optionally filtered by status"""
        tenants = list(self.tenants.values())
        
        if status:
            tenants = [t for t in tenants if t.status == status]
        
        return tenants
    
    async def suspend_tenant(self, tenant_id: str, reason: str = "") -> bool:
        """Suspend tenant"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
        
        tenant.status = TenantStatus.SUSPENDED
        tenant.updated_at = datetime.now()
        tenant.metadata["suspension_reason"] = reason
        tenant.metadata["suspended_at"] = datetime.now().isoformat()
        
        self.logger.warning(f"Suspended tenant {tenant_id}: {reason}")
        return True
    
    async def activate_tenant(self, tenant_id: str) -> bool:
        """Activate tenant"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
        
        tenant.status = TenantStatus.ACTIVE
        tenant.updated_at = datetime.now()
        
        # Clear suspension metadata
        tenant.metadata.pop("suspension_reason", None)
        tenant.metadata.pop("suspended_at", None)
        
        self.logger.info(f"Activated tenant {tenant_id}")
        return True
    
    async def cancel_tenant(self, tenant_id: str) -> bool:
        """Cancel tenant"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
        
        tenant.status = TenantStatus.CANCELLED
        tenant.updated_at = datetime.now()
        tenant.metadata["cancelled_at"] = datetime.now().isoformat()
        
        self.logger.info(f"Cancelled tenant {tenant_id}")
        return True
    
    def create_tenant_context(self, tenant_id: str, user_id: str, workspace_id: str, request_id: str) -> TenantContext:
        """Create tenant context for request"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} not found")
        
        # Get user permissions (simplified)
        permissions = ["read", "write"]  # Would be fetched from user service
        
        return TenantContext(
            tenant_id=tenant_id,
            tenant=tenant,
            user_id=user_id,
            workspace_id=workspace_id,
            request_id=request_id,
            permissions=permissions
        )


# Decorator for tenant-aware functions
def tenant_required(func):
    """Decorator to require tenant context"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract tenant context from request
        # This would typically come from request headers or middleware
        tenant_id = kwargs.get("tenant_id")
        user_id = kwargs.get("user_id")
        
        if not tenant_id:
            raise ValueError("Tenant ID required")
        
        tenant_manager = TenantManager()
        tenant = await tenant_manager.get_tenant(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} not found")
        
        # Add tenant context to kwargs
        kwargs["tenant_context"] = tenant_manager.create_tenant_context(
            tenant_id, user_id, kwargs.get("workspace_id", ""), kwargs.get("request_id", "")
        )
        
        return await func(*args, **kwargs)
    
    return wrapper


# Global tenant manager instance
tenant_manager = TenantManager()

# Export manager
__all__ = ["TenantManager", "Tenant", "TenantContext", "TenantConfig", "tenant_required", "tenant_manager"]
