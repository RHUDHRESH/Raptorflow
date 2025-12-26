"""
RaptorFlow Security Manager
Provides RBAC (Role-Based Access Control) and enhanced input validation.
"""

import hashlib
import re
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Dict, List, Optional, Set, Union

from core.enhanced_exceptions import AuthenticationError, AuthorizationError
from core.enhanced_exceptions import ValidationError as RaptorValidationError
from core.enhanced_exceptions import (
    handle_authentication_error,
    handle_authorization_error,
    handle_validation_error,
)

logger = logging.getLogger("raptorflow.security")


class Permission(Enum):
    """System permissions."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    MANAGE_USERS = "manage_users"
    MANAGE_CAMPAIGNS = "manage_campaigns"
    MANAGE_BRANDS = "manage_brands"
    VIEW_ANALYTICS = "view_analytics"
    EXPORT_DATA = "export_data"


class Role(Enum):
    """System roles with predefined permissions."""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    USER = "user"
    GUEST = "guest"


@dataclass
class SecurityPolicy:
    """Security policy configuration."""
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_symbols: bool = True
    password_max_age_days: int = 90
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    session_timeout_minutes: int = 60
    require_2fa: bool = False
    allowed_email_domains: Set[str] = field(default_factory=set)
    blocked_ip_addresses: Set[str] = field(default_factory=set)


@dataclass
class UserSecurityInfo:
    """User security information."""
    user_id: str
    roles: Set[Role]
    permissions: Set[Permission]
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    password_changed_at: Optional[datetime] = None
    is_active: bool = True
    is_verified: bool = False
    two_factor_enabled: bool = False


class InputValidator:
    """Enhanced input validation for security."""

    def __init__(self):
        self.security_policy = SecurityPolicy()

        # Common injection patterns
        self.sql_injection_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\s+['\"]\w+['\"]\s*=\s*['\"]\w+['\"])",
            r"(--|#|\/\*|\*\/)",
            r"(\b(SCRIPT|IF|CASE|WHEN|THEN|ELSE|END)\b)"
        ]

        self.xss_patterns = [
            r"(<script[^>]*>.*?</script>)",
            r"(javascript\s*:)",
            r"(on\w+\s*=)",
            r"(<iframe[^>]*>)",
            r"(<object[^>]*>)",
            r"(<embed[^>]*>)",
            r"(<link[^>]*>)",
            r"(<meta[^>]*>)"
        ]

        self.path_traversal_patterns = [
            r"(\.\./)",
            r"(\.\.\\)",
            r"(%2e%2e%2f)",
            r"(%2e%2e\\)",
            r"(\.\.%2f)",
            r"(\.\.%5c)"
        ]

    def validate_password(self, password: str) -> Dict[str, Any]:
        """Validate password against security policy."""
        result = {"valid": True, "errors": []}

        # Check minimum length
        if len(password) < self.security_policy.password_min_length:
            result["valid"] = False
            result["errors"].append(f"Password must be at least {self.security_policy.password_min_length} characters")

        # Check for uppercase letters
        if self.security_policy.password_require_uppercase and not re.search(r'[A-Z]', password):
            result["valid"] = False
            result["errors"].append("Password must contain at least one uppercase letter")

        # Check for lowercase letters
        if self.security_policy.password_require_lowercase and not re.search(r'[a-z]', password):
            result["valid"] = False
            result["errors"].append("Password must contain at least one lowercase letter")

        # Check for numbers
        if self.security_policy.password_require_numbers and not re.search(r'\d', password):
            result["valid"] = False
            result["errors"].append("Password must contain at least one number")

        # Check for symbols
        if self.security_policy.password_require_symbols and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            result["valid"] = False
            result["errors"].append("Password must contain at least one special character")

        # Check for common weak passwords
        weak_passwords = ["password", "123456", "qwerty", "admin", "letmein"]
        if password.lower() in weak_passwords:
            result["valid"] = False
            result["errors"].append("Password is too common")

        return result

    def validate_email(self, email: str) -> Dict[str, Any]:
        """Validate email address."""
        result = {"valid": True, "errors": []}

        # Basic email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            result["valid"] = False
            result["errors"].append("Invalid email format")
            return result

        # Check allowed domains
        if self.security_policy.allowed_email_domains:
            domain = email.split('@')[1].lower()
            if domain not in self.security_policy.allowed_email_domains:
                result["valid"] = False
                result["errors"].append(f"Email domain {domain} is not allowed")

        return result

    def sanitize_input(self, input_string: str) -> str:
        """Sanitize input string to prevent injection attacks."""
        if not input_string:
            return input_string

        # Remove potential SQL injection patterns
        for pattern in self.sql_injection_patterns:
            input_string = re.sub(pattern, '', input_string, flags=re.IGNORECASE)

        # Remove potential XSS patterns
        for pattern in self.xss_patterns:
            input_string = re.sub(pattern, '', input_string, flags=re.IGNORECASE)

        # Remove potential path traversal patterns
        for pattern in self.path_traversal_patterns:
            input_string = re.sub(pattern, '', input_string, flags=re.IGNORECASE)

        # Remove HTML tags
        input_string = re.sub(r'<[^>]*>', '', input_string)

        # Trim whitespace
        input_string = input_string.strip()

        return input_string

    def validate_file_upload(self, filename: str, file_size: int, content_type: str) -> Dict[str, Any]:
        """Validate file upload for security."""
        result = {"valid": True, "errors": []}

        # Check filename for suspicious patterns
        dangerous_extensions = ['.exe', '.bat', '.cmd', '.scr', '.pif', '.com', '.vbs', '.js', '.jar']
        file_ext = filename.lower().split('.')[-1] if '.' in filename else ''

        if file_ext in dangerous_extensions:
            result["valid"] = False
            result["errors"].append(f"File type {file_ext} is not allowed")

        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024
        if file_size > max_size:
            result["valid"] = False
            result["errors"].append("File size exceeds maximum allowed size")

        # Check for path traversal in filename
        if '..' in filename or '/' in filename or '\\' in filename:
            result["valid"] = False
            result["errors"].append("Invalid filename")

        return result

    def validate_api_key(self, api_key: str) -> Dict[str, Any]:
        """Validate API key format."""
        result = {"valid": True, "errors": []}

        # API key should be at least 32 characters
        if len(api_key) < 32:
            result["valid"] = False
            result["errors"].append("API key is too short")

        # API key should contain only alphanumeric characters and some symbols
        if not re.match(r'^[a-zA-Z0-9_\-\.]+$', api_key):
            result["valid"] = False
            result["errors"].append("API key contains invalid characters")

        return result


class RBACManager:
    """Role-Based Access Control manager."""

    def __init__(self):
        self.role_permissions = self._initialize_role_permissions()
        self.user_security: Dict[str, UserSecurityInfo] = {}

    def _initialize_role_permissions(self) -> Dict[Role, Set[Permission]]:
        """Initialize default role permissions."""
        return {
            Role.SUPER_ADMIN: {
                Permission.READ, Permission.WRITE, Permission.DELETE,
                Permission.ADMIN, Permission.MANAGE_USERS, Permission.MANAGE_CAMPAIGNS,
                Permission.MANAGE_BRANDS, Permission.VIEW_ANALYTICS, Permission.EXPORT_DATA
            },
            Role.ADMIN: {
                Permission.READ, Permission.WRITE, Permission.DELETE,
                Permission.MANAGE_USERS, Permission.MANAGE_CAMPAIGNS,
                Permission.MANAGE_BRANDS, Permission.VIEW_ANALYTICS, Permission.EXPORT_DATA
            },
            Role.MANAGER: {
                Permission.READ, Permission.WRITE,
                Permission.MANAGE_CAMPAIGNS, Permission.MANAGE_BRANDS,
                Permission.VIEW_ANALYTICS, Permission.EXPORT_DATA
            },
            Role.ANALYST: {
                Permission.READ, Permission.VIEW_ANALYTICS, Permission.EXPORT_DATA
            },
            Role.USER: {
                Permission.READ
            },
            Role.GUEST: {
                Permission.READ
            }
        }

    def add_user_role(self, user_id: str, role: Role) -> bool:
        """Add a role to a user."""
        if user_id not in self.user_security:
            self.user_security[user_id] = UserSecurityInfo(
                user_id=user_id,
                roles=set(),
                permissions=set()
            )

        self.user_security[user_id].roles.add(role)
        self.user_security[user_id].permissions.update(self.role_permissions[role])

        logger.info(f"Added role {role.value} to user {user_id}")
        return True

    def remove_user_role(self, user_id: str, role: Role) -> bool:
        """Remove a role from a user."""
        if user_id not in self.user_security:
            return False

        user_info = self.user_security[user_id]
        user_info.roles.discard(role)

        # Recalculate permissions
        user_info.permissions.clear()
        for user_role in user_info.roles:
            user_info.permissions.update(self.role_permissions[user_role])

        logger.info(f"Removed role {role.value} from user {user_id}")
        return True

    def add_permission(self, user_id: str, permission: Permission) -> bool:
        """Add a specific permission to a user."""
        if user_id not in self.user_security:
            return False

        self.user_security[user_id].permissions.add(permission)
        logger.info(f"Added permission {permission.value} to user {user_id}")
        return True

    def check_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if a user has a specific permission."""
        if user_id not in self.user_security:
            return False

        user_info = self.user_security[user_id]

        # Check if user is active
        if not user_info.is_active:
            return False

        # Check if user is locked
        if user_info.locked_until and datetime.utcnow() < user_info.locked_until:
            return False

        return permission in user_info.permissions

    def check_role(self, user_id: str, role: Role) -> bool:
        """Check if a user has a specific role."""
        if user_id not in self.user_security:
            return False

        user_info = self.user_security[user_id]
        return role in user_info.roles

    def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """Get all permissions for a user."""
        if user_id not in self.user_security:
            return set()

        return self.user_security[user_id].permissions.copy()

    def get_user_roles(self, user_id: str) -> Set[Role]:
        """Get all roles for a user."""
        if user_id not in self.user_security:
            return set()

        return self.user_security[user_id].roles.copy()

    def lock_user(self, user_id: str, duration_minutes: int = 30) -> bool:
        """Lock a user account."""
        if user_id not in self.user_security:
            return False

        user_info = self.user_security[user_id]
        user_info.locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)

        logger.warning(f"User {user_id} locked for {duration_minutes} minutes")
        return True

    def unlock_user(self, user_id: str) -> bool:
        """Unlock a user account."""
        if user_id not in self.user_security:
            return False

        user_info = self.user_security[user_id]
        user_info.locked_until = None
        user_info.failed_login_attempts = 0

        logger.info(f"User {user_id} unlocked")
        return True

    def record_failed_login(self, user_id: str) -> bool:
        """Record a failed login attempt."""
        if user_id not in self.user_security:
            return False

        user_info = self.user_security[user_id]
        user_info.failed_login_attempts += 1

        # Lock user if too many failed attempts
        if user_info.failed_login_attempts >= 5:  # Default max attempts
            self.lock_user(user_id, 30)

        return True

    def record_successful_login(self, user_id: str) -> bool:
        """Record a successful login."""
        if user_id not in self.user_security:
            return False

        user_info = self.user_security[user_id]
        user_info.last_login = datetime.utcnow()
        user_info.failed_login_attempts = 0

        return True


class SecurityManager:
    """Main security manager combining RBAC and input validation."""

    def __init__(self):
        self.rbac = RBACManager()
        self.input_validator = InputValidator()
        self.security_policy = SecurityPolicy()

    def authenticate_user(self, user_id: str, password: str) -> Dict[str, Any]:
        """Authenticate a user with password validation."""
        if user_id not in self.rbac.user_security:
            raise handle_authentication_error("User not found")

        user_info = self.rbac.user_security[user_id]

        # Check if user is active
        if not user_info.is_active:
            raise handle_authentication_error("User account is inactive")

        # Check if user is locked
        if user_info.locked_until and datetime.utcnow() < user_info.locked_until:
            raise handle_authentication_error("User account is locked")

        # Validate password (in real implementation, this would check against hashed password)
        password_validation = self.input_validator.validate_password(password)
        if not password_validation["valid"]:
            self.rbac.record_failed_login(user_id)
            raise handle_authentication_error("Invalid password")

        # Record successful login
        self.rbac.record_successful_login(user_id)

        return {
            "user_id": user_id,
            "roles": [role.value for role in user_info.roles],
            "permissions": [perm.value for perm in user_info.permissions],
            "last_login": user_info.last_login.isoformat() if user_info.last_login else None
        }

    def authorize_action(self, user_id: str, permission: Permission, resource: Optional[str] = None) -> bool:
        """Authorize a user action."""
        if not self.rbac.check_permission(user_id, permission):
            raise handle_authorization_error(
                f"Insufficient permissions for action {permission.value}",
                resource=resource
            )

        return True

    def validate_and_sanitize;anitize_input .input(self, .input_string.

    .def validate .validate .and .sanitize .sanitize .input;anit .ize . .input .(self ., .input .string .: .str ., .input .type .: .str .= .generic .) .-> .Dict .[str ., .Any .]: .""" .Validate .and .sanitize .input .based .on .type ..""" .result .= .{ .valid .: .True ., .errors .: .[ .] ., .sanitized .: .None .} .try .: .if .input .type .== .email .: .validation .= .self ..input .validator ..validate .email .( .input .string .) .elif .input .type .== .password .: .validation .= .self ..input .validator ..validate .password .( .input .string .) .elif .input .type .== .api ._key .: .validation .= .self ..input .validator ..validate .api ._key .( .input .string .) .else .: .validation .= .{ .valid .: .True ., .errors .: .[ .] .} .if .not .validation .[ .valid .]: .result .[ .valid .] .= .False .result .[ .errors .] .extend .( .validation .[ .errors .]) .# .Sanitize .input .result .[ .sanitized .] .= .self ..input .validator ..sanitize .input .( .input .string .) .except .Exception .as .e .: .result .[ .valid .] .= .False .result .[ .errors .] .append .( .f .Validation .error .: .{ .str .( .e .) .} .) .return .result .def .generate .secure ._token .(self ., .length .: .int .= .32 .) .-> .str .: .""" .Generate .a .secure .random .token ..""" .return .secrets ..token ._urlsafe .( .length .) .def .hash .password .(self ., .password .: .str .) .-> .str .: .""" .Hash .a .password .using .secure .algorithm ..""" .return .hashlib ..sha256 .( .password ..encode .( .utf .-8 .) ) ..hexdigest .( .) .def .verify .password .(self ., .password .: .str ., .hashed ._password .: .str .) .-> .bool .: .""" .Verify .a .password .against .hashed .version ..""" .return .self ..hash .password .( .password .) .== .hashed ._password


# .Global .security .manager .instance ._security ._manager .: .Optional .[ .SecurityManager .] .= .None


def .get ._security ._manager .( .) .-> .SecurityManager .: .""" .Get .the .global .security .manager .instance ..""" .global ._security ._manager .if ._security ._manager .is .None .: ._security ._manager .= .SecurityManager .( .) .return ._security ._manager


# .Decorators .def .require ._permission .( .permission .: .Permission .): .""" .Decorator .to .require .specific .permission ..""" .def .decorator .( .func .): .@wraps .( .func .) .async .def .async ._wrapper .( .* .args ., .* * .kwargs .): .user ._id .= .kwargs ..get .( .user ._id .) .if .not .user ._id .: .raise .handle ._authentication ._error .( .User .ID .required .) .security ._manager .= .get ._security ._manager .( .) .security ._manager ..authorize ._action .( .user ._id ., .permission .) .return .await .func .( .* .args ., .* * .kwargs .) .@wraps .( .func .) .def .sync ._wrapper .( .* .args ., .* * .kwargs .): .user ._id .= .kwargs ..get .( .user ._id .) .if .not .user ._id .: .raise .handle ._authentication ._error .( .User .ID .required .) .security ._manager .= .get ._security ._manager .( .) .security ._manager ..authorize ._action .( .user ._id ., .permission .) .return .func .( .* .args ., .* * .kwargs .) .return .async ._wrapper .if .asyncio ..iscoroutinefunction .( .func .) .else .sync ._wrapper .return .decorator


def .require ._role .( .role .: .Role .): .""" .Decorator .to .require .specific .role ..""" .def .decorator .( .func .): .@wraps .( .func .) .async .def .async ._wrapper .( .* .args ., .* * .kwargs .): .user ._id .= .kwargs ..get .( .user ._id .) .if .not .user ._id .: .raise .handle ._authentication ._error .( .User .ID .required .) .security ._manager .= .get ._security ._manager .( .) .if .not .security ._manager ..rbac ..check ._role .( .user ._id ., .role .): .raise .handle ._authorization ._error .( .f .Role .{ .role ..value .} .required .) .return .await .func .( .* .args ., .* * .kwargs .) .@wraps .( .func .) .def .sync ._wrapper .( .* .args ., .* * .kwargs .): .user ._id .= .kwargs ..get .( .user ._id .) .if .not .user ._id .: .raise .handle ._authentication ._error .( .User .ID .required .) .security ._manager .= .get ._security ._manager .( .) .if .not .security ._manager ..rbac ..check ._role .( .user ._id ., .role .): .raise .handle ._authorization ._error .( .f .Role .{ .role ..value .} .required .) .return .func .( .* .args ., .* * .kwargs .) .return .async ._wrapper .if .asyncio ..iscoroutinefunction .( .func .) .else .sync ._wrapper .return .decorator


if .__name .__ .== .__main .__: .# .Test .security .manager .security ._manager .= .SecurityManager .( .) .# .Test .user .creation .user ._id .= .test ._user .security ._manager ..rbac ..add ._user ._role .( .user ._id ., .Role ..USER .) .# .Test .permission .check .has ._permission .= .security ._manager ..rbac ..check ._permission .( .user ._id ., .Permission ..READ .) .print .( .f .User .{ .user ._id .} .has .READ .permission .: .{ .has ._permission .} .) .# .Test .input .validation .password ._result .= .security ._manager ..input ._validator ..validate ._password .( .Secure .Pass .123 .! .) .print .( .f .Password .validation .: .{ .password ._result .} .)
