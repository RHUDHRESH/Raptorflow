"""
Comprehensive request validation for agent requests.
Includes security checks, input sanitization, and validation rules.
"""

import re
import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom validation error."""
    pass


class SecurityValidator:
    """Security validation for agent requests."""
    
    # Blocked patterns for injection attacks
    MALICIOUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',  # JavaScript URLs
        r'on\w+\s*=',  # Event handlers
        r'eval\s*\(',  # eval() calls
        r'document\.',  # Document access
        r'window\.',  # Window access
        r'localStorage',  # Local storage
        r'sessionStorage',  # Session storage
        r'__import__',  # Dynamic imports
        r'exec\s*\(',  # exec() calls
        r'import\s+',  # Import statements
        r'from\s+\w+\s+import',  # From imports
        r'base64',  # Base64 encoding
        r'data:text/html',  # Data URLs
        r'file://',  # File URLs
        r'ftp://',  # FTP URLs
    ]
    
    # Suspicious keywords
    SUSPICIOUS_KEYWORDS = [
        'password', 'token', 'secret', 'key', 'auth', 'credential',
        'admin', 'root', 'sudo', 'privilege', 'escalate',
        'exploit', 'payload', 'shell', 'cmd', 'command',
        'hack', 'crack', 'bypass', 'override', 'inject'
    ]
    
    @classmethod
    def validate_input(cls, input_str: str) -> tuple[bool, Optional[str]]:
        """Validate input for malicious content."""
        if not input_str:
            return True, None
        
        # Check for malicious patterns
        for pattern in cls.MALICIOUS_PATTERNS:
            if re.search(pattern, input_str, re.IGNORECASE | re.DOTALL):
                return False, f"Potentially malicious pattern detected: {pattern}"
        
        # Check for suspicious keywords
        lower_input = input_str.lower()
        for keyword in cls.SUSPICIOUS_KEYWORDS:
            if keyword in lower_input:
                logger.warning(f"Suspicious keyword detected: {keyword}")
                # Don't block, but log for monitoring
        
        # Check for excessive length (potential DoS)
        if len(input_str) > 50000:  # 50KB limit
            return False, "Input too large"
        
        # Check for excessive repetition (potential DoS)
        if len(set(input_str)) < len(input_str) * 0.1:  # Less than 10% unique chars
            return False, "Input contains excessive repetition"
        
        return True, None
    
    @classmethod
    def sanitize_input(cls, input_str: str) -> str:
        """Sanitize input by removing potentially harmful content."""
        if not input_str:
            return input_str
        
        # Remove HTML tags
        sanitized = re.sub(r'<[^>]+>', '', input_str)
        
        # Remove excessive whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        
        # Limit length
        if len(sanitized) > 10000:
            sanitized = sanitized[:10000] + "..."
        
        return sanitized


class EnhancedAgentRequest(BaseModel):
    """Enhanced request model with comprehensive validation."""
    
    request: str = Field(
        ..., 
        min_length=1, 
        max_length=10000, 
        description="User request"
    )
    workspace_id: str = Field(
        ..., 
        min_length=3, 
        max_length=100, 
        description="Workspace ID",
        pattern=r'^[a-zA-Z0-9_-]+$'  # Alphanumeric, underscore, dash only
    )
    user_id: str = Field(
        ..., 
        min_length=3, 
        max_length=100, 
        description="User ID",
        pattern=r'^[a-zA-Z0-9_-]+$'  # Alphanumeric, underscore, dash only
    )
    session_id: str = Field(
        ..., 
        min_length=3, 
        max_length=100, 
        description="Session ID",
        pattern=r'^[a-zA-Z0-9_-]+$'  # Alphanumeric, underscore, dash only
    )
    context: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional context"
    )
    agent_hint: Optional[str] = Field(
        None, 
        max_length=50, 
        description="Agent name hint",
        pattern=r'^[a-zA-Z]*$'  # Letters only
    )
    fast_mode: bool = Field(False, description="Use fast routing mode")
    
    @validator('request')
    def validate_request_content(cls, v):
        """Validate request content for security."""
        is_valid, error = SecurityValidator.validate_input(v)
        if not is_valid:
            raise ValueError(error)
        
        # Additional content validation
        if len(v.strip()) < 3:
            raise ValueError("Request too short")
        
        # Check for non-printable characters
        if not all(ord(c) >= 32 or c in '\t\n\r' for c in v):
            raise ValueError("Request contains invalid characters")
        
        return SecurityValidator.sanitize_input(v)
    
    @validator('context')
    def validate_context(cls, v):
        """Validate context dictionary."""
        if v is None:
            return v
        
        if not isinstance(v, dict):
            raise ValueError("Context must be a dictionary")
        
        # Limit context size
        if len(str(v)) > 5000:
            raise ValueError("Context too large")
        
        # Validate context keys
        for key in v.keys():
            if not isinstance(key, str) or len(key) > 50:
                raise ValueError("Invalid context key")
        
        # Validate context values
        for value in v.values():
            if isinstance(value, str):
                is_valid, error = SecurityValidator.validate_input(value)
                if not is_valid:
                    raise ValueError(f"Invalid context value: {error}")
        
        return v
    
    @validator('agent_hint')
    def validate_agent_hint(cls, v):
        """Validate agent hint."""
        if v is None:
            return v
        
        # Convert to lowercase for consistency
        return v.lower()


class RequestValidator:
    """Main request validator with comprehensive checks."""
    
    def __init__(self):
        self.request_count: Dict[str, int] = {}
        self.blocked_ips: set[str] = set()
    
    def validate_agent_request(
        self, 
        request_data: Dict[str, Any],
        client_ip: Optional[str] = None
    ) -> EnhancedAgentRequest:
        """Validate and process agent request."""
        try:
            # Check IP blocking
            if client_ip and client_ip in self.blocked_ips:
                raise HTTPException(
                    status_code=403,
                    detail="IP address blocked"
                )
            
            # Validate with Pydantic model
            validated_request = EnhancedAgentRequest(**request_data)
            
            # Additional business logic validation
            self._validate_business_rules(validated_request, client_ip)
            
            return validated_request
            
        except ValueError as e:
            logger.warning(f"Request validation failed: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid request: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected validation error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Validation error"
            )
    
    def _validate_business_rules(
        self, 
        request: EnhancedAgentRequest,
        client_ip: Optional[str] = None
    ):
        """Validate business rules for requests."""
        # Rate limiting per user
        user_key = f"user:{request.user_id}"
        self.request_count[user_key] = self.request_count.get(user_key, 0) + 1
        
        if self.request_count[user_key] > 1000:  # 1000 requests per session
            raise HTTPException(
                status_code=429,
                detail="Too many requests"
            )
        
        # Check for suspicious patterns
        if self._is_suspicious_request(request):
            logger.warning(f"Suspicious request from user {request.user_id}: {request.request[:100]}")
            
            # Block if too many suspicious requests
            if client_ip:
                ip_key = f"ip:{client_ip}"
                self.request_count[ip_key] = self.request_count.get(ip_key, 0) + 1
                if self.request_count[ip_key] > 50:
                    self.blocked_ips.add(client_ip)
                    raise HTTPException(
                        status_code=403,
                        detail="Too many suspicious requests"
                    )
    
    def _is_suspicious_request(self, request: EnhancedAgentRequest) -> bool:
        """Check if request is suspicious."""
        suspicious_indicators = 0
        
        # Check for system commands
        system_commands = ['ls', 'dir', 'cat', 'type', 'del', 'rm', 'sudo', 'admin']
        for cmd in system_commands:
            if cmd in request.request.lower():
                suspicious_indicators += 1
        
        # Check for file operations
        file_patterns = ['/', '\\', '..', 'etc/', 'bin/', 'sys/', 'proc/']
        for pattern in file_patterns:
            if pattern in request.request.lower():
                suspicious_indicators += 1
        
        # Check for network operations
        network_patterns = ['http://', 'https://', 'ftp://', 'telnet', 'ssh']
        for pattern in network_patterns:
            if pattern in request.request.lower():
                suspicious_indicators += 1
        
        return suspicious_indicators >= 2
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics."""
        return {
            "total_requests": sum(self.request_count.values()),
            "blocked_ips": len(self.blocked_ips),
            "request_counts": dict(self.request_count),
        }


# Global validator instance
_validator: Optional[RequestValidator] = None


def get_validator() -> RequestValidator:
    """Get the global request validator instance."""
    global _validator
    if _validator is None:
        _validator = RequestValidator()
    return _validator


def validate_agent_request(
    request_data: Dict[str, Any],
    client_ip: Optional[str] = None
) -> EnhancedAgentRequest:
    """Validate agent request (convenience function)."""
    validator = get_validator()
    return validator.validate_agent_request(request_data, client_ip)


# Validation middleware helper
def create_validation_middleware():
    """Create FastAPI middleware for request validation."""
    from fastapi import Request
    from starlette.middleware.base import BaseHTTPMiddleware
    
    class ValidationMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            # Skip validation for health checks
            if request.url.path in ["/health", "/api/v1/agents/health"]:
                return await call_next(request)
            
            # Get client IP
            client_ip = request.client.host if request.client else None
            
            # Validate request body for agent endpoints
            if "/api/v1/agents" in request.url.path:
                try:
                    body = await request.json()
                    validate_agent_request(body, client_ip)
                except Exception as e:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Request validation failed: {str(e)}"
                    )
            
            return await call_next(request)
    
    return ValidationMiddleware
