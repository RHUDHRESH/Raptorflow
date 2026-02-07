import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger("raptorflow.security")


class SecurityHeaderType(Enum):
    """Types of security headers."""

    CSP = "content-security-policy"
    HSTS = "strict-transport-security"
    X_FRAME_OPTIONS = "x-frame-options"
    X_CONTENT_TYPE_OPTIONS = "x-content-type-options"
    X_XSS_PROTECTION = "x-xss-protection"
    REFERRER_POLICY = "referrer-policy"
    PERMISSIONS_POLICY = "permissions-policy"


class SecurityConfig:
    """Security configuration for headers."""

    def __init__(
        self,
        enable_hsts: bool = True,
        hsts_max_age: int = 31536000,  # 1 year
        hsts_include_subdomains: bool = True,
        hsts_preload: bool = False,
        enable_csp: bool = True,
        csp_directives: Optional[Dict[str, List[str]]] = None,
        enable_frame_options: bool = True,
        frame_option: str = "DENY",
        enable_content_type_options: bool = True,
        enable_xss_protection: bool = True,
        enable_referrer_policy: bool = True,
        referrer_policy: str = "strict-origin-when-cross-origin",
        enable_permissions_policy: bool = True,
        permissions_directives: Optional[Dict[str, str]] = None,
    ):
        self.enable_hsts = enable_hsts
        self.hsts_max_age = hsts_max_age
        self.hsts_include_subdomains = hsts_include_subdomains
        self.hsts_preload = hsts_preload
        self.enable_csp = enable_csp
        self.csp_directives = csp_directives or self._default_csp_directives()
        self.enable_frame_options = enable_frame_options
        self.frame_option = frame_option
        self.enable_content_type_options = enable_content_type_options
        self.enable_xss_protection = enable_xss_protection
        self.enable_referrer_policy = enable_referrer_policy
        self.referrer_policy = referrer_policy
        self.enable_permissions_policy = enable_permissions_policy
        self.permissions_directives = (
            permissions_directives or self._default_permissions_directives()
        )

    def _default_csp_directives(self) -> Dict[str, List[str]]:
        """Default Content Security Policy directives."""
        return {
            "default-src": ["'self'"],
            "script-src": ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
            "style-src": ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
            "font-src": ["'self'", "https://fonts.gstatic.com"],
            "img-src": ["'self'", "data:", "https:"],
            "connect-src": ["'self'"],
            "frame-ancestors": ["'none'"],
            "base-uri": ["'self'"],
            "form-action": ["'self'"],
        }

    def _default_permissions_directives(self) -> Dict[str, str]:
        """Default Permissions Policy directives."""
        return {
            "geolocation": "()",
            "microphone": "()",
            "camera": "()",
            "payment": "()",
            "usb": "()",
            "magnetometer": "()",
            "gyroscope": "()",
            "accelerometer": "()",
        }


class SecurityHeadersMiddleware:
    """
    FastAPI middleware for security headers.
    """

    def __init__(self, app, config: SecurityConfig = None):
        self.app = app
        self.config = config or SecurityConfig()
        self.stats = {
            "requests_processed": 0,
            "headers_added": 0,
            "security_violations": 0,
        }

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Process request and add security headers
            await self._process_with_security_headers(scope, receive, send)
        else:
            await self.app(scope, receive, send)

    async def _process_with_security_headers(self, scope, receive, send):
        """Process request and add security headers to response."""
        response_headers = []

        # Intercept response
        async def send_wrapper(message):
            nonlocal response_headers

            if message["type"] == "http.response.start":
                response_headers = message["headers"]

                # Add security headers
                security_headers = self._generate_security_headers(scope)

                # Merge security headers with existing headers
                merged_headers = response_headers.copy()
                for name, value in security_headers:
                    merged_headers.append((name, value))

                # Update message with merged headers
                message["headers"] = merged_headers

                self.stats["headers_added"] += len(security_headers)

                await send(message)
            else:
                await send(message)

        # Process the request
        await self.app(scope, receive, send_wrapper)

        self.stats["requests_processed"] += 1

    def _generate_security_headers(self, scope: Dict[str, Any]) -> List[tuple]:
        """Generate security headers based on configuration."""
        headers = []

        # Content Security Policy
        if self.config.enable_csp:
            csp_value = self._build_csp_header()
            headers.append((b"content-security-policy", csp_value.encode()))

        # HTTP Strict Transport Security
        if self.config.enable_hsts:
            hsts_value = f"max-age={self.config.hsts_max_age}"
            if self.config.hsts_include_subdomains:
                hsts_value += "; includeSubDomains"
            if self.config.hsts_preload:
                hsts_value += "; preload"
            headers.append((b"strict-transport-security", hsts_value.encode()))

        # X-Frame-Options
        if self.config.enable_frame_options:
            headers.append((b"x-frame-options", self.config.frame_option.encode()))

        # X-Content-Type-Options
        if self.config.enable_content_type_options:
            headers.append((b"x-content-type-options", b"nosniff"))

        # X-XSS-Protection
        if self.config.enable_xss_protection:
            headers.append((b"x-xss-protection", b"1; mode=block"))

        # Referrer Policy
        if self.config.enable_referrer_policy:
            headers.append((b"referrer-policy", self.config.referrer_policy.encode()))

        # Permissions Policy
        if self.config.enable_permissions_policy:
            permissions_value = self._build_permissions_header()
            headers.append((b"permissions-policy", permissions_value.encode()))

        # Additional security headers
        headers.extend(
            [
                (b"x-dns-prefetch-control", b"off"),
                (b"x-download-options", b"noopen"),
                (b"x-permitted-cross-domain-policies", b"none"),
                (b"cross-origin-embedder-policy", b"require-corp"),
                (b"cross-origin-opener-policy", b"same-origin"),
                (b"cross-origin-resource-policy", b"same-origin"),
            ]
        )

        return headers

    def _build_csp_header(self) -> str:
        """Build Content Security Policy header value."""
        directives = []

        for directive, sources in self.config.csp_directives.items():
            if sources:
                directive_value = f"{directive} {' '.join(sources)}"
                directives.append(directive_value)

        return "; ".join(directives)

    def _build_permissions_header(self) -> str:
        """Build Permissions Policy header value."""
        directives = []

        for feature, value in self.config.permissions_directives.items():
            directives.append(f"{feature}={value}")

        return ", ".join(directives)

    def get_stats(self) -> Dict[str, Any]:
        """Get security headers statistics."""
        return self.stats.copy()


class SecurityValidator:
    """Validate security headers and detect potential issues."""

    def __init__(self, config: SecurityConfig):
        self.config = config

    def validate_headers(self, headers: List[tuple]) -> Dict[str, Any]:
        """Validate security headers and report issues."""
        issues = []
        warnings = []
        headers_dict = {
            name.decode().lower(): value.decode() for name, value in headers
        }

        # Check CSP
        if self.config.enable_csp:
            if "content-security-policy" not in headers_dict:
                issues.append("Missing Content Security Policy header")
            else:
                csp = headers_dict["content-security-policy"]
                if "unsafe-inline" in csp:
                    warnings.append("CSP contains 'unsafe-inline' - consider removing")
                if "unsafe-eval" in csp:
                    warnings.append("CSP contains 'unsafe-eval' - consider removing")

        # Check HSTS
        if self.config.enable_hsts:
            if "strict-transport-security" not in headers_dict:
                issues.append("Missing HSTS header")
            else:
                hsts = headers_dict["strict-transport-security"]
                if "max-age=" in hsts:
                    max_age = int(hsts.split("max-age=")[1].split(";")[0])
                    if max_age < 31536000:  # Less than 1 year
                        warnings.append("HSTS max-age should be at least 1 year")

        # Check other essential headers
        essential_headers = {
            "x-frame-options": "Missing X-Frame-Options header",
            "x-content-type-options": "Missing X-Content-Type-Options header",
            "x-xss-protection": "Missing X-XSS-Protection header",
            "referrer-policy": "Missing Referrer-Policy header",
        }

        for header, message in essential_headers.items():
            if header.replace("-", "_") in [
                "enable_frame_options",
                "enable_content_type_options",
                "enable_xss_protection",
                "enable_referrer_policy",
            ]:
                if header not in headers_dict:
                    issues.append(message)

        return {
            "issues": issues,
            "warnings": warnings,
            "score": self._calculate_security_score(issues, warnings),
        }

    def _calculate_security_score(self, issues: List[str], warnings: List[str]) -> int:
        """Calculate security score (0-100)."""
        base_score = 100
        base_score -= len(issues) * 10  # Each issue reduces score by 10
        base_score -= len(warnings) * 3  # Each warning reduces score by 3
        return max(0, base_score)


class SecurityAuditor:
    """Audit security configuration and headers."""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.validator = SecurityValidator(config)

    async def audit_configuration(self) -> Dict[str, Any]:
        """Audit the security configuration."""
        audit_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "configuration": {
                "hsts_enabled": self.config.enable_hsts,
                "csp_enabled": self.config.enable_csp,
                "frame_options_enabled": self.config.enable_frame_options,
                "content_type_options_enabled": self.config.enable_content_type_options,
                "xss_protection_enabled": self.config.enable_xss_protection,
                "referrer_policy_enabled": self.config.enable_referrer_policy,
                "permissions_policy_enabled": self.config.enable_permissions_policy,
            },
            "recommendations": [],
            "security_level": "medium",
        }

        # Generate recommendations
        if not self.config.enable_hsts:
            audit_results["recommendations"].append("Enable HSTS for HTTPS protection")

        if not self.config.enable_csp:
            audit_results["recommendations"].append("Enable Content Security Policy")

        if self.config.hsts_max_age < 31536000:
            audit_results["recommendations"].append(
                "Set HSTS max-age to at least 1 year"
            )

        if "unsafe-inline" in str(self.config.csp_directives):
            audit_results["recommendations"].append("Remove 'unsafe-inline' from CSP")

        # Calculate security level
        enabled_count = sum(
            [
                self.config.enable_hsts,
                self.config.enable_csp,
                self.config.enable_frame_options,
                self.config.enable_content_type_options,
                self.config.enable_xss_protection,
                self.config.enable_referrer_policy,
                self.config.enable_permissions_policy,
            ]
        )

        if enabled_count >= 6:
            audit_results["security_level"] = "high"
        elif enabled_count >= 4:
            audit_results["security_level"] = "medium"
        else:
            audit_results["security_level"] = "low"

        return audit_results

    async def audit_response_headers(self, headers: List[tuple]) -> Dict[str, Any]:
        """Audit response headers."""
        validation_result = self.validator.validate_headers(headers)

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "header_validation": validation_result,
            "security_score": validation_result["score"],
            "grade": self._get_grade_from_score(validation_result["score"]),
        }

    def _get_grade_from_score(self, score: int) -> str:
        """Get security grade from score."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"


# Global security middleware
_security_middleware: Optional[SecurityHeadersMiddleware] = None


def get_security_middleware() -> SecurityHeadersMiddleware:
    """Get the global security middleware instance."""
    global _security_middleware
    if _security_middleware is None:
        _security_middleware = SecurityHeadersMiddleware(None)
    return _security_middleware


def set_security_config(config: SecurityConfig):
    """Set security configuration."""
    global _security_middleware
    _security_middleware = SecurityHeadersMiddleware(None, config)


async def audit_security_headers(headers: List[tuple]) -> Dict[str, Any]:
    """Audit security headers."""
    middleware = get_security_middleware()
    auditor = SecurityAuditor(middleware.config)
    return await auditor.audit_response_headers(headers)


async def audit_security_configuration() -> Dict[str, Any]:
    """Audit security configuration."""
    middleware = get_security_middleware()
    auditor = SecurityAuditor(middleware.config)
    return await auditor.audit_configuration()


def get_security_stats() -> Dict[str, Any]:
    """Get security headers statistics."""
    middleware = get_security_middleware()
    return middleware.get_stats()
