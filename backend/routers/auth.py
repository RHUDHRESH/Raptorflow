"""
Authentication API Router
Handles login, logout, refresh token, and session management using Redis.
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from uuid import UUID
import structlog

from backend.utils.cache import (
    create_user_session,
    verify_session,
    logout_user,
    logout_all_devices,
    redis_cache
)
from backend.utils.auth import get_current_user_and_workspace
from backend.services.supabase_client import supabase_client

logger = structlog.get_logger(__name__)

router = APIRouter()


# ==================== REQUEST/RESPONSE MODELS ====================

class LoginRequest(BaseModel):
    """Login request"""
    email: str
    password: str


class LoginResponse(BaseModel):
    """Login response"""
    session_id: str
    access_token: str
    refresh_token: str
    user_id: str
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    session_id: str
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """Refresh token response"""
    access_token: str
    expires_in: int


class LogoutRequest(BaseModel):
    """Logout request"""
    session_id: str


class SessionInfo(BaseModel):
    """Session information"""
    session_id: str
    created_at: str
    ip: str
    device: str
    user_agent: str


class UserSessionsResponse(BaseModel):
    """All user sessions"""
    sessions: list[SessionInfo]
    total_count: int


# ==================== AUTHENTICATION ENDPOINTS ====================

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Login with email and password.
    Creates a session and returns tokens.

    Returns:
        session_id: Session ID for this login
        access_token: JWT for API requests
        refresh_token: Token to refresh access token
    """
    try:
        # TODO: Authenticate user with Supabase
        # For now, this is a placeholder showing the flow

        # Verify credentials against Supabase Auth
        # user = await supabase_client.auth.sign_in_with_password(
        #     email=request.email,
        #     password=request.password
        # )

        # For demo purposes, mock user
        user_id = "user-uuid-123"  # Would be from Supabase
        access_token = "access_token_jwt"  # Would be from Supabase
        refresh_token = "refresh_token_jwt"  # Would be from Supabase

        # Get client info for session
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # Create session in Redis
        session_id = await create_user_session(
            user_id=user_id,
            refresh_token=refresh_token,
            ip_address=client_ip,
            user_agent=user_agent,
            device="web",
            ttl=86400  # 24 hours
        )

        if not session_id:
            logger.error("Failed to create session")
            raise HTTPException(status_code=500, detail="Failed to create session")

        logger.info("User logged in", user_id=user_id, session_id=session_id[:8])

        return LoginResponse(
            session_id=session_id,
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user_id,
            expires_in=86400
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Login failed")


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token.
    Extends session TTL.

    Returns:
        New access_token
        expires_in: New expiry time
    """
    try:
        # Verify session exists
        session = await redis_cache.get_session(request.session_id)
        if not session:
            logger.warning("Session not found or expired", session_id=request.session_id[:8])
            raise HTTPException(status_code=401, detail="Session expired")

        # Verify refresh token matches
        stored_refresh_token = session.get("refresh_token")
        if stored_refresh_token != request.refresh_token:
            logger.error("Refresh token mismatch", session_id=request.session_id[:8])
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        # Extend session TTL
        extended = await redis_cache.refresh_session_ttl(
            request.session_id,
            new_ttl=86400
        )

        if not extended:
            logger.warning("Failed to extend session", session_id=request.session_id[:8])
            raise HTTPException(status_code=401, detail="Session expired")

        # TODO: Generate new access token
        # For demo, just return a string
        new_access_token = "new_access_token_jwt"

        logger.info("Token refreshed", session_id=request.session_id[:8])

        return RefreshTokenResponse(
            access_token=new_access_token,
            expires_in=86400
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Token refresh failed")


@router.post("/logout", response_model=Dict[str, Any])
async def logout(request: LogoutRequest):
    """
    Logout from current session.

    Args:
        session_id: Session to destroy
    """
    try:
        # Get session to retrieve user_id for logging
        session = await redis_cache.get_session(request.session_id)
        user_id = session.get("user_id") if session else "unknown"

        # Destroy session
        destroyed = await logout_user(request.session_id)

        if destroyed:
            logger.info("User logged out", user_id=user_id, session_id=request.session_id[:8])
        else:
            logger.warning("Session not found for logout", session_id=request.session_id[:8])

        return {
            "message": "Logged out successfully",
            "logged_out": destroyed
        }

    except Exception as e:
        logger.error(f"Logout failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Logout failed")


@router.post("/logout-all-devices", response_model=Dict[str, Any])
async def logout_all(auth: Dict[str, str] = Depends(get_current_user_and_workspace)):
    """
    Logout from ALL devices (destroy all sessions for user).

    SECURITY: Used when user changes password or detects unauthorized access.
    """
    try:
        user_id = auth["user_id"]

        # Destroy all sessions
        count = await logout_all_devices(user_id)

        logger.warning(
            "All user sessions destroyed",
            user_id=user_id,
            count=count
        )

        return {
            "message": f"Logged out from {count} devices",
            "sessions_destroyed": count
        }

    except Exception as e:
        logger.error(f"Logout all failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Logout all failed")


@router.get("/sessions", response_model=UserSessionsResponse)
async def get_my_sessions(
    auth: Dict[str, str] = Depends(get_current_user_and_workspace)
):
    """
    Get all active sessions for authenticated user.

    SECURITY: Shows user all devices they're logged in from.
    User can logout from any device they see here.

    Returns:
        List of sessions with device info
    """
    try:
        user_id = auth["user_id"]

        # Get all sessions
        sessions = await redis_cache.get_user_sessions(user_id)

        # Format for response
        session_infos = [
            SessionInfo(
                session_id=s.get("session_id", ""),
                created_at=s.get("created_at", ""),
                ip=s.get("ip", "unknown"),
                device=s.get("device", "unknown"),
                user_agent=s.get("user_agent", "unknown")
            )
            for s in sessions
        ]

        logger.info(
            "Sessions retrieved",
            user_id=user_id,
            count=len(session_infos)
        )

        return UserSessionsResponse(
            sessions=session_infos,
            total_count=len(session_infos)
        )

    except Exception as e:
        logger.error(f"Failed to get sessions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve sessions")


@router.delete("/sessions/{session_id}", response_model=Dict[str, Any])
async def logout_from_device(
    session_id: str,
    auth: Dict[str, str] = Depends(get_current_user_and_workspace)
):
    """
    Logout from a specific device (destroy specific session).

    SECURITY: User can only logout their own sessions.

    Args:
        session_id: Session to destroy
    """
    try:
        # Verify session belongs to authenticated user
        session = await redis_cache.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        if session.get("user_id") != auth["user_id"]:
            logger.error(
                "Unauthorized session logout attempt",
                user_id=auth["user_id"],
                target_user_id=session.get("user_id"),
                session_id=session_id[:8]
            )
            raise HTTPException(status_code=403, detail="Not your session")

        # Destroy session
        destroyed = await logout_user(session_id)

        if destroyed:
            logger.info(
                "Device logged out",
                user_id=auth["user_id"],
                session_id=session_id[:8],
                device=session.get("device")
            )
        else:
            raise HTTPException(status_code=404, detail="Session not found")

        return {
            "message": "Logged out from device",
            "device": session.get("device"),
            "destroyed": destroyed
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to logout device: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to logout device")
