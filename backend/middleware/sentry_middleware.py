"""
Comprehensive Sentry Middleware for Raptorflow Backend
====================================================

Automatic API monitoring, error capture, and performance tracking
middleware for FastAPI applications.

Features:
- Automatic request/response tracking
- Error capture with context
- Performance monitoring
- Session correlation
- User tracking
- Request body/response body capture
- Custom breadcrumb generation
"""

import uuid
import time
import json
import logging
from typing import Dict, List, Optional, Any, Callable
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import StreamingResponse
import asyncio

from backend.core.sentry_integration import get_sentry_manager
from backend.core.sentry_error_tracking import get_error_tracker, ErrorContext
from backend.core.sentry_performance import get_performance_monitor
from backend.core.sentry_sessions import get_session_manager, SessionType


class SentryMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive Sentry middleware for automatic API monitoring.
    """
    
    def __init__(self, 
                 app,
                 capture_request_body: bool = True,
                 capture_response_body: bool = True,
                 capture_headers: bool = True,
                 session_tracking: bool = True,
                 performance_tracking: bool = True,
                 error_tracking: bool = True):
        """
        Initialize Sentry middleware.
        
        Args:
            app: FastAPI application
            capture_request_body: Whether to capture request bodies
            capture_response_body: Whether to capture response bodies
            capture_headers: Whether to capture headers
            session_tracking: Whether to enable session tracking
            performance_tracking: Whether to enable performance tracking
            error_tracking: Whether to enable error tracking
        """
        super().__init__(app)
        
        self.capture_request_body = capture_request_body
        self.capture_response_body = capture_response_body
        self.capture_headers = capture_headers
        self.session_tracking = session_tracking
        self.performance_tracking = performance_tracking
        self.error_tracking = error_tracking
        
        # Get managers
        self.sentry_manager = get_sentry_manager()
        self.error_tracker = get_error_tracker()
        self.performance_monitor = get_performance_monitor()
        self.session_manager = get_session_manager()
        
        self._logger = logging.getLogger(__name__)
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        Process request and response with Sentry monitoring.
        """
        # Skip monitoring if Sentry is not enabled
        if not self.sentry_manager.is_enabled():
            return await call_next(request)
        
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Start timing
        start_time = time.time()
        
        # Extract request information
        request_info = await self._extract_request_info(request)
        
        # Initialize session if enabled
        session_id = None
        if self.session_tracking:
            session_id = self._get_or_create_session(request, request_info)
        
        # Set up Sentry context
        self._setup_sentry_context(request, request_info, session_id)
        
        # Track request start
        if self.performance_tracking:
            self._track_request_start(request_info)
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate response time
            response_time_ms = (time.time() - start_time) * 1000
            
            # Extract response information
            response_info = self._extract_response_info(response, response_time_ms)
            
            # Track successful request
            if self.performance_tracking:
                self._track_request_success(request_info, response_info, session_id)
            
            # Track session activity
            if self.session_tracking and session_id:
                self.session_manager.track_session_request(
                    session_id=session_id,
                    endpoint=request_info["endpoint"],
                    method=request_info["method"],
                    status_code=response_info["status_code"],
                    response_time_ms=response_time_ms,
                    success=response_info["status_code"] < 400
                )
            
            # Add success breadcrumb
            self._add_request_breadcrumb(request_info, response_info, "success")
            
            return response
            
        except Exception as e:
            # Calculate response time for error
            response_time_ms = (time.time() - start_time) * 1000
            
            # Create error context
            error_context = ErrorContext(
                request_id=request_id,
                endpoint=request_info["endpoint"],
                method=request_info["method"],
                ip_address=request_info["ip_address"],
                user_agent=request_info["user_agent"],
                component="api_middleware"
            )
            
            # Track error
            if self.error_tracking:
                error_id = self.error_tracker.track_exception(e, error_context)
            
            # Track failed request
            if self.performance_tracking:
                self._track_request_error(request_info, e, response_time_ms, session_id)
            
            # Track session error
            if self.session_tracking and session_id:
                self.session_manager.track_session_error(
                    error_id=error_id or "unknown",
                    session_id=session_id,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    severity="high",
                    user_impacted=True
                )
            
            # Add error breadcrumb
            self._add_request_breadcrumb(request_info, None, "error", str(e))
            
            # Re-raise the exception
            raise
    
    async def _extract_request_info(self, request: Request) -> Dict[str, Any]:
        """Extract request information for monitoring."""
        request_info = {
            "method": request.method,
            "url": str(request.url),
            "endpoint": f"{request.method} {request.url.path}",
            "query_params": dict(request.query_params),
            "ip_address": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", ""),
            "content_type": request.headers.get("content-type", ""),
            "content_length": request.headers.get("content-length", "0"),
        }
        
        # Capture headers if enabled
        if self.capture_headers:
            request_info["headers"] = dict(request.headers)
        
        # Capture request body if enabled and appropriate
        if self.capture_request_body and self._should_capture_body(request):
            try:
                body = await request.body()
                if body:
                    # Try to parse as JSON first
                    if request_info["content_type"].startswith("application/json"):
                        try:
                            request_info["body"] = json.loads(body.decode())
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            request_info["body"] = body.decode(errors="ignore")
                    else:
                        # For other content types, capture as text (with size limit)
                        body_text = body.decode(errors="ignore")
                        if len(body_text) <= 10000:  # 10KB limit
                            request_info["body"] = body_text
                        else:
                            request_info["body"] = f"[Body too large: {len(body)} bytes]"
            except Exception as e:
                self._logger.warning(f"Failed to capture request body: {e}")
                request_info["body"] = "[Failed to capture body]"
        
        return request_info
    
    def _extract_response_info(self, response: Response, response_time_ms: float) -> Dict[str, Any]:
        """Extract response information for monitoring."""
        response_info = {
            "status_code": response.status_code,
            "response_time_ms": response_time_ms,
            "content_type": response.headers.get("content-type", ""),
            "content_length": response.headers.get("content-length", "0"),
        }
        
        # Capture response headers if enabled
        if self.capture_headers:
            response_info["headers"] = dict(response.headers)
        
        # Capture response body if enabled and appropriate
        if self.capture_response_body and self._should_capture_response_body(response):
            try:
                # Note: This is tricky with streaming responses
                # For now, we'll capture the content-type and length
                if hasattr(response, 'body'):
                    body = response.body
                    if body and len(body) <= 10000:  # 10KB limit
                        if response_info["content_type"].startswith("application/json"):
                            try:
                                response_info["body"] = json.loads(body.decode())
                            except (json.JSONDecodeError, UnicodeDecodeError):
                                response_info["body"] = body.decode(errors="ignore")
                        else:
                            response_info["body"] = body.decode(errors="ignore")
                    else:
                        response_info["body"] = f"[Response body too large: {len(body)} bytes]"
            except Exception as e:
                self._logger.warning(f"Failed to capture response body: {e}")
                response_info["body"] = "[Failed to capture response body]"
        
        return response_info
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request."""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()
        
        # Fall back to client IP
        return request.client.host if request.client else "unknown"
    
    def _should_capture_body(self, request: Request) -> bool:
        """Determine if request body should be captured."""
        # Don't capture for large requests
        content_length = request.headers.get("content-length", "0")
        try:
            if int(content_length) > 10000:  # 10KB limit
                return False
        except ValueError:
            pass
        
        # Don't capture certain content types
        content_type = request.headers.get("content-type", "").lower()
        skip_types = [
            "multipart/form-data",
            "application/octet-stream",
            "image/",
            "video/",
            "audio/",
        ]
        
        return not any(skip_type in content_type for skip_type in skip_types)
    
    def _should_capture_response_body(self, response: Response) -> bool:
        """Determine if response body should be captured."""
        # Don't capture for large responses
        content_length = response.headers.get("content-length", "0")
        try:
            if int(content_length) > 10000:  # 10KB limit
                return False
        except ValueError:
            pass
        
        # Don't capture certain content types
        content_type = response.headers.get("content-type", "").lower()
        skip_types = [
            "image/",
            "video/",
            "audio/",
            "application/octet-stream",
        ]
        
        return not any(skip_type in content_type for skip_type in skip_types)
    
    def _get_or_create_session(self, request: Request, request_info: Dict[str, Any]) -> Optional[str]:
        """Get or create session for the request."""
        # Try to get existing session from headers
        session_id = request.headers.get("x-session-id")
        
        if session_id:
            # Update existing session
            session = self.session_manager.get_session_info(session_id)
            if session:
                self.session_manager.update_session(
                    session_id=session_id,
                    endpoint=request_info["endpoint"],
                    metadata={"last_request": request_info}
                )
                return session_id
        
        # Create new session
        user_id = self._extract_user_id(request)
        
        session_id = self.session_manager.create_session(
            user_id=user_id,
            session_type=SessionType.API,
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            endpoint=request_info["endpoint"],
            metadata={"request_info": request_info}
        )
        
        return session_id
    
    def _extract_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from request."""
        # Try various methods to get user ID
        
        # 1. From Authorization header (JWT token)
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            # This would require JWT decoding - simplified for now
            pass
        
        # 2. From custom headers
        user_id = request.headers.get("x-user-id")
        if user_id:
            return user_id
        
        # 3. From request state (set by authentication middleware)
        if hasattr(request.state, "user_id"):
            return request.state.user_id
        
        # 4. From query parameters
        user_id = request.query_params.get("user_id")
        if user_id:
            return user_id
        
        return None
    
    def _setup_sentry_context(self, 
                             request: Request, 
                             request_info: Dict[str, Any], 
                             session_id: Optional[str]) -> None:
        """Set up Sentry context for the request."""
        try:
            from sentry_sdk import configure_scope, set_tag, set_context
            
            configure_scope(lambda scope: set_tag("request_id", getattr(request.state, "request_id", "unknown")))
            configure_scope(lambda scope: set_tag("http.method", request_info["method"]))
            configure_scope(lambda scope: set_tag("http.url", request_info["url"]))
            configure_scope(lambda scope: set_tag("endpoint", request_info["endpoint"]))
            
            if session_id:
                configure_scope(lambda scope: set_tag("session_id", session_id))
            
            # Set request context
            request_context = {
                "method": request_info["method"],
                "url": request_info["url"],
                "query_params": request_info["query_params"],
                "ip_address": request_info["ip_address"],
                "user_agent": request_info["user_agent"],
            }
            
            if self.capture_headers and "headers" in request_info:
                # Filter sensitive headers
                filtered_headers = self._filter_sensitive_headers(request_info["headers"])
                request_context["headers"] = filtered_headers
            
            if self.capture_request_body and "body" in request_info:
                request_context["body"] = request_info["body"]
            
            configure_scope(lambda scope: set_context("request", request_context))
            
        except Exception as e:
            self._logger.error(f"Failed to setup Sentry context: {e}")
    
    def _filter_sensitive_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Filter sensitive headers for Sentry."""
        sensitive_headers = [
            "authorization", "cookie", "set-cookie", "x-api-key",
            "x-auth-token", "x-session-token", "password"
        ]
        
        filtered = {}
        for key, value in headers.items():
            if key.lower() in sensitive_headers:
                filtered[key] = "[FILTERED]"
            else:
                filtered[key] = value
        
        return filtered
    
    def _track_request_start(self, request_info: Dict[str, Any]) -> None:
        """Track request start for performance monitoring."""
        try:
            # Add breadcrumb for request start
            self.error_tracker.add_breadcrumb(
                message=f"Request started: {request_info['endpoint']}",
                level="info",
                category="http.request",
                data={
                    "method": request_info["method"],
                    "url": request_info["url"],
                    "ip_address": request_info["ip_address"],
                }
            )
        except Exception as e:
            self._logger.error(f"Failed to track request start: {e}")
    
    def _track_request_success(self, 
                               request_info: Dict[str, Any], 
                               response_info: Dict[str, Any],
                               session_id: Optional[str]) -> None:
        """Track successful request for performance monitoring."""
        try:
            # Track API performance
            self.performance_monitor.track_api_request(
                method=request_info["method"],
                endpoint=request_info["endpoint"],
                status_code=response_info["status_code"],
                response_time_ms=response_info["response_time_ms"],
                request_size_bytes=int(request_info.get("content_length", "0") or "0"),
                response_size_bytes=int(response_info.get("content_length", "0") or "0"),
                user_id=None,  # Would be extracted from session
                ip_address=request_info["ip_address"],
                user_agent=request_info["user_agent"]
            )
        except Exception as e:
            self._logger.error(f"Failed to track request success: {e}")
    
    def _track_request_error(self, 
                            request_info: Dict[str, Any], 
                            error: Exception,
                            response_time_ms: float,
                            session_id: Optional[str]) -> None:
        """Track failed request for performance monitoring."""
        try:
            # Track API performance (failed request)
            self.performance_monitor.track_api_request(
                method=request_info["method"],
                endpoint=request_info["endpoint"],
                status_code=500,  # Internal server error
                response_time_ms=response_time_ms,
                request_size_bytes=int(request_info.get("content_length", "0") or "0"),
                response_size_bytes=0,
                user_id=None,
                ip_address=request_info["ip_address"],
                user_agent=request_info["user_agent"]
            )
            
            # Track custom metric for errors
            self.performance_monitor.track_custom_metric(
                "api_errors",
                1,
                "count",
                {
                    "endpoint": request_info["endpoint"],
                    "method": request_info["method"],
                    "error_type": type(error).__name__
                }
            )
        except Exception as e:
            self._logger.error(f"Failed to track request error: {e}")
    
    def _add_request_breadcrumb(self, 
                               request_info: Dict[str, Any], 
                               response_info: Optional[Dict[str, Any]],
                               status: str,
                               error_message: str = "") -> None:
        """Add breadcrumb for request processing."""
        try:
            breadcrumb_data = {
                "method": request_info["method"],
                "url": request_info["url"],
                "ip_address": request_info["ip_address"],
            }
            
            if response_info:
                breadcrumb_data.update({
                    "status_code": response_info["status_code"],
                    "response_time_ms": response_info["response_time_ms"],
                })
            
            if error_message:
                breadcrumb_data["error"] = error_message
            
            level = "error" if status == "error" else "info"
            
            self.error_tracker.add_breadcrumb(
                message=f"Request {status}: {request_info['endpoint']}",
                level=level,
                category="http",
                data=breadcrumb_data
            )
        except Exception as e:
            self._logger.error(f"Failed to add request breadcrumb: {e}")


def add_sentry_middleware(app, 
                         capture_request_body: bool = True,
                         capture_response_body: bool = True,
                         capture_headers: bool = True,
                         session_tracking: bool = True,
                         performance_tracking: bool = True,
                         error_tracking: bool = True) -> None:
    """
    Add Sentry middleware to FastAPI application.
    
    Args:
        app: FastAPI application
        capture_request_body: Whether to capture request bodies
        capture_response_body: Whether to capture response bodies
        capture_headers: Whether to capture headers
        session_tracking: Whether to enable session tracking
        performance_tracking: Whether to enable performance tracking
        error_tracking: Whether to enable error tracking
    """
    app.add_middleware(
        SentryMiddleware,
        capture_request_body=capture_request_body,
        capture_response_body=capture_response_body,
        capture_headers=capture_headers,
        session_tracking=session_tracking,
        performance_tracking=performance_tracking,
        error_tracking=error_tracking
    )
