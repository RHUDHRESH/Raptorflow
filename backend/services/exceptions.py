from typing import Optional, Dict, Any

class ServiceError(Exception):
    """Base exception for all service errors"""
    def __init__(self, message: str, original_error: Optional[Exception] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.original_error = original_error
        self.details = details or {}

class ServiceUnavailableError(ServiceError):
    """Raised when a service is unreachable or circuit breaker is open"""
    pass

class ResourceNotFoundError(ServiceError):
    """Raised when a requested resource is not found"""
    pass

class ValidationError(ServiceError):
    """Raised when input validation fails"""
    pass

class RateLimitError(ServiceError):
    """Raised when rate limit is exceeded"""
    pass

class DatabaseError(ServiceError):
    """Raised when a database operation fails"""
    pass

class ExternalServiceError(ServiceError):
    """Raised when an external API call fails"""
    pass
