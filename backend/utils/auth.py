"""
Authentication and authorization utilities for RaptorFlow backend.
MOCKED for development/running without full dependencies.
"""

import structlog
from typing import Optional, Annotated
from uuid import UUID
from datetime import datetime, timezone

from fastapi import HTTPException, status, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Mock logger
logger = structlog.get_logger(__name__)
security = HTTPBearer()

async def verify_jwt_token(token: str) -> dict:
    return {
        "user_id": "00000000-0000-0000-0000-000000000000",
        "email": "dev@raptorflow.com",
        "role": "owner",
        "exp": 9999999999,
        "jti": "mock-jti"
    }

async def get_user_workspace(user_id: str) -> Optional[UUID]:
    return UUID("00000000-0000-0000-0000-000000000000")

async def get_current_user_and_workspace(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    return {
        "user_id": "00000000-0000-0000-0000-000000000000",
        "workspace_id": UUID("00000000-0000-0000-0000-000000000000"),
        "email": "dev@raptorflow.com",
        "role": "owner"
    }

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Optional[dict]:
    if not credentials:
        return None
    return await get_current_user_and_workspace(credentials)

async def verify_admin(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    return await get_current_user_and_workspace(credentials)
