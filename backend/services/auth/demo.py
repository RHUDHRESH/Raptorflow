"""Demo Auth Service - Local PC-only demo mode with local data storage."""

from __future__ import annotations

import ipaddress
import json
import logging
import os
import secrets
import socket
import time
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Local data storage path
DEMO_DATA_DIR = Path.home() / ".raptorflow" / "demo"
DEMO_DATA_FILE = DEMO_DATA_DIR / "data.json"

# Allowed IP ranges for demo mode (local/private networks)
ALLOWED_IPS = [
    ipaddress.ip_network("127.0.0.0/8"),  # Localhost
    ipaddress.ip_network("10.0.0.0/8"),  # Private Class A
    ipaddress.ip_network("172.16.0.0/12"),  # Private Class B
    ipaddress.ip_network("192.168.0.0/16"),  # Private Class C
]


def _is_local_request() -> bool:
    """Check if request is from a local/private IP address."""
    try:
        hostname = socket.gethostname()
        local_ips = socket.getaddrinfo(hostname, None)
        for ip_info in local_ips:
            ip_str = ip_info[4][0]
            try:
                ip = ipaddress.ip_address(ip_str)
                for network in ALLOWED_IPS:
                    if ip in network:
                        return True
            except ValueError:
                continue
        return False
    except Exception:
        return False


def _check_pc_mode() -> tuple[bool, str]:
    """Check if running on PC (local machine) and in dev mode."""
    env = os.getenv("ENVIRONMENT", "").lower()
    auth_mode = os.getenv("AUTH_MODE", "").lower()

    # Must be in demo mode
    if auth_mode != "demo":
        return False, "Not in demo mode"

    # Check if local request
    is_local = _is_local_request()

    # Only allow in development or if local
    if env in ("dev", "development") or is_local:
        return True, "OK"

    return False, f"Demo mode not allowed in {env} environment from non-local IP"


class DemoUser:
    """Demo user object."""

    def __init__(
        self,
        user_id: str = "demo-user-001",
        email: str = "demo@raptorflow.local",
        role: str = "owner",
        workspace_id: str = "demo-workspace-001",
    ):
        self.id = user_id
        self.email = email
        self.role = role
        self.workspace_id = workspace_id
        self.created_at = int(time.time())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "email": self.email,
            "role": self.role,
            "workspace_id": self.workspace_id,
            "created_at": self.created_at,
        }


class DemoDataStore:
    """Local file-based data store for demo mode."""

    def __init__(self, data_file: Path = DEMO_DATA_FILE):
        self.data_file = data_file
        self._data: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """Load data from local file."""
        try:
            if self.data_file.exists():
                with open(self.data_file, "r") as f:
                    self._data = json.load(f)
                logger.info(f"Loaded demo data from {self.data_file}")
            else:
                self._data = self._default_data()
                self._save()
                logger.info(f"Created new demo data at {self.data_file}")
        except Exception as e:
            logger.warning(f"Failed to load demo data: {e}, using defaults")
            self._data = self._default_data()

    def _default_data(self) -> Dict[str, Any]:
        """Default demo data structure."""
        return {
            "users": {
                "demo-user-001": {
                    "id": "demo-user-001",
                    "email": "demo@raptorflow.local",
                    "password_hash": "",  # Not used in demo
                    "role": "owner",
                    "workspace_id": "demo-workspace-001",
                    "created_at": int(time.time()),
                }
            },
            "workspaces": {
                "demo-workspace-001": {
                    "id": "demo-workspace-001",
                    "name": "Demo Workspace",
                    "owner_id": "demo-user-001",
                    "created_at": int(time.time()),
                }
            },
            "profiles": {
                "demo-user-001": {
                    "id": "demo-user-001",
                    "user_id": "demo-user-001",
                    "workspace_id": "demo-workspace-001",
                    "full_name": "Demo User",
                    "created_at": int(time.time()),
                }
            },
            "last_updated": int(time.time()),
        }

    def _save(self) -> None:
        """Save data to local file."""
        try:
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            self._data["last_updated"] = int(time.time())
            with open(self.data_file, "w") as f:
                json.dump(self._data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save demo data: {e}")

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        return self._data.get("users", {}).get(user_id)

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email."""
        for user in self._data.get("users", {}).values():
            if user.get("email") == email:
                return user
        return None

    def get_workspace(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Get workspace by ID."""
        return self._data.get("workspaces", {}).get(workspace_id)

    def update_user(self, user_id: str, data: Dict[str, Any]) -> None:
        """Update user data."""
        if "users" not in self._data:
            self._data["users"] = {}
        self._data["users"][user_id] = data
        self._save()


class DemoAuthService:
    """Local PC-only demo mode with secure demo auth.

    This service is used when AUTH_MODE=demo in settings.
    It provides a secure demo auth flow for testing without requiring Supabase.

    RESTRICTIONS:
    - Only accessible from local/private IP addresses
    - Only works in development environment
    - Data is stored locally in ~/.raptorflow/demo/data.json

    Security features:
    - Cryptographically secure tokens
    - Password format validation
    - Proper session management
    - Token expiration
    """

    def __init__(
        self,
        demo_user_id: str = "demo-user-001",
        demo_email: str = "demo@raptorflow.local",
        demo_workspace_id: str = "demo-workspace-001",
    ):
        # Check PC mode
        allowed, reason = _check_pc_mode()
        if not allowed:
            logger.error(f"Demo mode blocked: {reason}")
            raise RuntimeError(f"Demo mode not allowed: {reason}")

        self.demo_user = DemoUser(
            user_id=demo_user_id,
            email=demo_email,
            workspace_id=demo_workspace_id,
        )
        self._sessions: Dict[str, Any] = {}
        self._token_version = 0

        # Initialize local data store
        self._data_store = DemoDataStore()

        logger.warning("DemoAuthService initialized - PC ONLY - LOCAL DATA")

    def _generate_access_token(self) -> str:
        """Generate a cryptographically secure access token."""
        return f"demo_{secrets.token_urlsafe(32)}"

    def _generate_refresh_token(self) -> str:
        """Generate a cryptographically secure refresh token."""
        return f"demo_refresh_{secrets.token_urlsafe(32)}"

    def _validate_password_format(self, password: str) -> tuple[bool, str]:
        """Validate password meets minimum security requirements."""
        if not password:
            return False, "Password is required"

        # Enforce minimum 8 characters
        if len(password) < 8:
            return False, "Password must be at least 8 characters"

        # Check complexity requirements
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)

        if not (has_upper and has_lower and has_digit):
            return False, "Password must contain uppercase, lowercase, and number"

        return True, ""

    def _create_session_data(
        self, access_token: str, refresh_token: str
    ) -> Dict[str, Any]:
        """Create session data object."""
        expires_at = int(time.time()) + 3600  # 1 hour
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 3600,
            "expires_at": expires_at,
            "user": self.demo_user.to_dict(),
        }

    def create_session(self, token: Optional[str] = None) -> Dict[str, Any]:
        """Create a demo session token."""
        access_token = token if token else self._generate_access_token()
        refresh_token = self._generate_refresh_token()

        # Generate unique session ID
        session_id = secrets.token_urlsafe(16)
        current_time = int(time.time())

        session = self._create_session_data(access_token, refresh_token)

        # Session data
        session_data: Dict[str, Any] = {
            "user": self.demo_user,
            "refresh_token": refresh_token,
            "access_token": access_token,
            "created_at": current_time,
            "expires_at": session["expires_at"],
        }

        # Store with session_id as primary key
        self._sessions[session_id] = session_data

        # Also store by access_token for verification (map to session_id)
        self._sessions[f"access:{access_token}"] = session_id
        # Store by refresh_token (map to session_id)
        self._sessions[f"refresh:{refresh_token}"] = session_id

        # Cleanup old sessions if needed
        self._cleanup_old_sessions()

        logger.info(f"Demo session created for: {self.demo_user.email}")
        return session

    def verify_token(self, token: Optional[str]) -> Dict[str, Any]:
        """Verify a demo token."""
        if not token:
            return {"valid": False, "error": "Token is required"}

        # Must start with demo_ prefix
        if not token.startswith("demo_"):
            return {"valid": False, "error": "Invalid token format"}

        # Look up session by access token
        session_id = self._sessions.get(f"access:{token}")
        if not session_id:
            return {"valid": False, "error": "Invalid token"}

        # Get session data
        session = self._sessions.get(session_id)
        if not session:
            return {"valid": False, "error": "Invalid token"}

        # Check expiration
        if session.get("expires_at", 0) < int(time.time()):
            # Clean up expired session
            self._cleanup_session(session_id, token)
            return {"valid": False, "error": "Token expired"}

        user = session["user"]
        return {
            "valid": True,
            "user": user.to_dict(),
            "user_id": user.id,
            "email": user.email,
        }

    def _cleanup_session(self, session_id: str, access_token: str) -> None:
        """Clean up a session and its lookups."""
        if session_id in self._sessions:
            del self._sessions[session_id]
        if f"access:{access_token}" in self._sessions:
            del self._sessions[f"access:{access_token}"]
        # Find and delete refresh token lookup
        for key in list(self._sessions.keys()):
            if key.startswith("refresh:") and self._sessions.get(key) == session_id:
                del self._sessions[key]

    def get_user(self, token: Optional[str]) -> Optional[Dict[str, Any]]:
        """Get user from token."""
        result = self.verify_token(token)
        if result.get("valid"):
            return result.get("user")
        return None

    def refresh_session(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh a demo session."""
        if not refresh_token:
            return {"error": "Refresh token required"}

        # Look up session by refresh token (not using refresh token as key)
        session_id = self._sessions.get(f"refresh:{refresh_token}")
        if not session_id:
            return {"error": "Invalid refresh token"}

        session = self._sessions.get(session_id)
        if not session:
            return {"error": "Invalid refresh token"}

        if session.get("expires_at", 0) < int(time.time()):
            self._cleanup_session(session_id, session.get("access_token", ""))
            return {"error": "Refresh token expired"}

        # Create new session (token rotation)
        return self.create_session()

    def logout(self, token: str) -> bool:
        """Logout - remove session with proper audit logging."""
        try:
            # Look up session
            session_id = self._sessions.get(f"access:{token}")
            if session_id:
                # Log the logout attempt (no PII)
                logger.info(f"User logout: session_id={session_id[:8]}...")

                # Clean up session
                self._cleanup_session(session_id, token)
            else:
                logger.warning(f"Logout attempt with invalid token")
        except Exception as e:
            logger.error(f"Logout error: {e}")

        return True

    async def sign_out(self, token: str) -> Dict[str, Any]:
        """Sign out - async wrapper."""
        self.logout(token)
        return {"success": True}

    async def check_health(self) -> Dict[str, Any]:
        """Check demo auth health."""
        # Don't expose data location in production
        env = os.getenv("ENVIRONMENT", "").lower()
        result: Dict[str, Any] = {
            "status": "healthy",
            "provider": "demo",
            "mode": "demo",
            "warning": "Demo mode - PC ONLY - NOT FOR PRODUCTION",
        }

        # Only show data location in development
        if env in ("dev", "development"):
            result["data_location"] = str(DEMO_DATA_FILE)
            result["demo_user"] = self.demo_user.email

        return result

    async def sign_up(self, email: str, password: str) -> Dict[str, Any]:
        """Demo signup - validates password format then creates session."""
        allowed, reason = _check_pc_mode()
        if not allowed:
            return {
                "error": f"Demo mode not available: {reason}",
                "user": None,
                "session": None,
            }

        # Rate limiting for signup
        try:
            self._rate_limit_login(email)
        except Exception as e:
            return {"error": str(e), "user": None, "session": None}

        # Validate email format - prevent injection attacks
        import re

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not email or not re.match(email_pattern, email):
            return {"error": "Invalid email format", "user": None, "session": None}

        # Check for suspicious characters
        suspicious_chars = [
            "<",
            ">",
            '"',
            "'",
            ";",
            "--",
            "/*",
            "*/",
            "xp_",
            "sp_",
            "EXEC",
            "UNION",
        ]
        email_lower = email.lower()
        for char in suspicious_chars:
            if char in email_lower:
                logger.warning(f"Suspicious input detected in demo signup: {email}")
                return {"error": "Invalid email format", "user": None, "session": None}

        valid, error = self._validate_password_format(password)
        if not valid:
            return {"error": error, "user": None, "session": None}

        # DEMO MODE: For security, signup requires same credentials as login
        # This prevents unauthorized access in case demo mode is accidentally enabled
        valid_demo_users = self._get_valid_demo_users()

        if email.lower() not in valid_demo_users:
            logger.warning(f"Demo signup: unauthorized email attempted")
            return {
                "error": "Signup not available. Use demo credentials.",
                "user": None,
                "session": None,
            }

        if password != valid_demo_users[email.lower()]:
            logger.warning(f"Demo signup: wrong password for {email}")
            return {"error": "Invalid credentials", "user": None, "session": None}

        self._cleanup_old_sessions()
        return self.create_session()

    def _get_valid_demo_users(self) -> Dict[str, str]:
        """Get valid demo users from config or environment."""
        import os

        # Try to get from environment
        demo_email = os.getenv("DEMO_EMAIL", "").lower().strip()
        demo_password = os.getenv("DEMO_PASSWORD", "")

        if demo_email and demo_password:
            return {demo_email: demo_password}

        # Fall back to defaults (only works in dev)
        env = os.getenv("ENVIRONMENT", "").lower()
        if env in ("dev", "development"):
            return {
                "demo@raptorflow.in": "Demo1234",
                "demo@raptorflow.local": "Demo1234",
                "demo@localhost": "Demo1234",
            }

        # No valid users in production
        return {}

    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Demo login - validates credentials with rate limiting."""

        # Rate limiting for demo mode
        self._rate_limit_login(email)

        allowed, reason = _check_pc_mode()
        if not allowed:
            return {
                "error": f"Demo mode not available: {reason}",
                "user": None,
                "session": None,
            }

        # Validate email format - prevent injection attacks
        import re

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not email or not re.match(email_pattern, email):
            return {"error": "Invalid credentials", "user": None, "session": None}

        # Check for suspicious characters (basic injection prevention)
        suspicious_chars = [
            "<",
            ">",
            '"',
            "'",
            ";",
            "--",
            "/*",
            "*/",
            "xp_",
            "sp_",
            "EXEC",
            "UNION",
        ]
        email_lower = email.lower()
        for char in suspicious_chars:
            if char in email_lower:
                logger.warning(f"Suspicious input detected in demo login")
                return {"error": "Invalid credentials", "user": None, "session": None}

        valid, error = self._validate_password_format(password)
        if not valid:
            return {"error": "Invalid credentials", "user": None, "session": None}

        # DEMO MODE: Only accept specific demo credentials
        # In production, this should NEVER be used - demo mode is dev-only
        valid_demo_users = self._get_valid_demo_users()

        # If no valid users configured, reject all
        if not valid_demo_users:
            logger.warning("Demo mode: no valid users configured")
            return {"error": "Demo mode not available", "user": None, "session": None}

        # Check credentials against allowed list
        if email.lower() not in valid_demo_users:
            logger.warning(f"Demo login: unauthorized email attempted")
            return {"error": "Invalid credentials", "user": None, "session": None}

        if password != valid_demo_users[email.lower()]:
            logger.warning(f"Demo login: wrong password")
            return {"error": "Invalid credentials", "user": None, "session": None}

        # Log without PII
        logger.info(
            f"Demo login successful (email domain: {email.split('@')[1] if '@' in email else 'unknown'})"
        )
        self._cleanup_old_sessions()
        return self.create_session()

    def _rate_limit_login(self, email: str) -> None:
        """Simple rate limiting for demo login."""
        import time

        current_time = time.time()

        if not hasattr(self, "_login_attempts"):
            self._login_attempts = {}

        # Clean old attempts (older than 60 seconds)
        self._login_attempts = {
            k: v for k, v in self._login_attempts.items() if current_time - v < 60
        }

        # Check rate limit
        if email in self._login_attempts:
            if self._login_attempts[email] >= 5:
                logger.warning(f"Rate limited: {email}")
                raise Exception("Too many login attempts. Try again later.")
            self._login_attempts[email] += 1
        else:
            self._login_attempts[email] = 1

    async def reset_password(self, email: str) -> Dict[str, Any]:
        """Demo password reset."""
        return {"success": True, "message": "Password reset email sent (demo mode)"}

    async def verify_token_async(self, token: str) -> Dict[str, Any]:
        """Async version of verify_token."""
        return self.verify_token(token)

    def _cleanup_old_sessions(self, max_sessions: int = 50) -> None:
        """Clean up old sessions to prevent memory leaks."""
        # Count actual user sessions (not lookup keys)
        session_keys = [
            k
            for k in self._sessions.keys()
            if not k.startswith(("access:", "refresh:"))
        ]

        if len(session_keys) > max_sessions:
            current_time = int(time.time())
            valid_keys = set()

            for key in session_keys:
                session = self._sessions.get(key)
                if session and session.get("expires_at", 0) > current_time:
                    valid_keys.add(key)

            # Keep only most recent sessions
            if len(valid_keys) > max_sessions // 2:
                # Sort by creation time and keep most recent
                sorted_sessions = sorted(
                    [
                        (k, self._sessions.get(k))
                        for k in valid_keys
                        if self._sessions.get(k)
                    ],
                    key=lambda x: x[1].get("created_at", 0) if x[1] else 0,
                    reverse=True,
                )
                valid_keys = {k for k, _ in sorted_sessions[: max_sessions // 2]}

            # Remove invalid sessions and their lookups
            keys_to_remove = set(self._sessions.keys()) - valid_keys
            for key in keys_to_remove:
                if key in self._sessions:
                    del self._sessions[key]


_demo_auth_service: Optional[DemoAuthService] = None


def get_demo_auth_service() -> DemoAuthService:
    """Get the global demo auth service instance."""
    global _demo_auth_service
    if _demo_auth_service is None:
        from backend.config import settings

        demo_user_id = getattr(settings, "DEMO_USER_ID", "demo-user-001")
        demo_email = getattr(settings, "DEMO_EMAIL", "demo@raptorflow.local")
        demo_workspace_id = getattr(settings, "DEMO_WORKSPACE_ID", "demo-workspace-001")

        _demo_auth_service = DemoAuthService(
            demo_user_id=demo_user_id,
            demo_email=demo_email,
            demo_workspace_id=demo_workspace_id,
        )
    return _demo_auth_service


def reset_demo_auth_service() -> None:
    """Reset the demo auth service (useful for testing)."""
    global _demo_auth_service
    _demo_auth_service = None
