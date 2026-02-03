"""
JWT Authentication Middleware
Validates Supabase JWT tokens and extracts user context
"""

import jwt
import logging
import os
from datetime import datetime
from typing import Any, Callable, Dict, Optional

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate Supabase JWT tokens.
    Extracts user_id from token and adds to request.state
    """
    
    def __init__(self, app, jwt_secret: Optional[str] = None):
        super().__init__(app)
        self.jwt_secret = jwt_secret or os.getenv("SUPABASE_JWT_SECRET")
        if not self.jwt_secret:
            logger.warning("SUPABASE_JWT_SECRET not set - JWT validation will fail")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Any:
        # Skip auth for public endpoints
        public_paths = [
            "/",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/signup",
            "/api/v1/auth/callback",
            "/api/v1/auth/refresh",
            "/api/v2/auth/login",
            "/api/v2/auth/signup",
            "/api/v2/auth/callback",
            "/api/v2/auth/refresh",
        ]
        
        # Check if path is public
        path = request.url.path
        if any(path.startswith(public) or path == public for public in public_paths):
            return await call_next(request)
        
        # Extract JWT from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            request.state.user_id = None
            request.state.user_email = None
            return await call_next(request)
        
        # Parse Bearer token
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid authorization header format. Expected 'Bearer <token>'"}
            )
        
        token = parts[1]
        
        try:
            # Verify JWT
            payload = self._verify_token(token)
            
            # Check if token is expired
            if payload.get("exp") and datetime.utcnow().timestamp() > payload["exp"]:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Token expired"}
                )
            
            # Extract user info from payload
            user_id = payload.get("sub")
            user_email = payload.get("email")
            
            # Add to request state
            request.state.user_id = user_id
            request.state.user_email = user_email
            request.state.jwt_payload = payload
            request.state.access_token = token
            
            logger.debug(f"Authenticated user: {user_id}")
            
        except jwt.ExpiredSignatureError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Token expired"}
            )
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid token"}
            )
        except Exception as e:
            logger.error(f"JWT validation error: {e}")
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication failed"}
            )
        
        return await call_next(request)
    
    def _verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        if not self.jwt_secret:
            raise jwt.InvalidTokenError("JWT secret not configured")
        
        return jwt.decode(
            token,
            self.jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "require": ["exp", "iat", "sub"]
            }
        )


class WorkspaceContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract workspace context from headers.
    Runs after JWT middleware to ensure user is authenticated.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Any:
        # Extract workspace ID from header
        workspace_id = request.headers.get("x-workspace-id")
        if workspace_id:
            request.state.workspace_id = workspace_id
        
        # Extract workspace slug from header (alternative)
        workspace_slug = request.headers.get("x-workspace-slug")
        if workspace_slug:
            request.state.workspace_slug = workspace_slug
        
        return await call_next(request)


def get_current_user_id(request: Request) -> Optional[str]:
    """Extract current user ID from request state"""
    return getattr(request.state, "user_id", None)


def get_current_workspace_id(request: Request) -> Optional[str]:
    """Extract current workspace ID from request state"""
    return getattr(request.state, "workspace_id", None)


def require_auth(request: Request) -> str:
    """Require authentication, raise 401 if not authenticated"""
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user_id


def require_workspace(request: Request) -> str:
    """Require workspace ID, raise 400 if not provided"""
    workspace_id = get_current_workspace_id(request)
    if not workspace_id:
        raise HTTPException(status_code=400, detail="Workspace ID required (header: X-Workspace-Id)")
    return workspace_id
