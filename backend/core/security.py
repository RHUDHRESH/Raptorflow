from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Mock token verification for development.
    Returns a mock user payload.
    """
    token = credentials.credentials
    # In a real app, verify JWT here.
    # For now, return a mock user payload.
    return {
        "sub": "00000000-0000-0000-0000-000000000000",
        "email": "dev@raptorflow.com",
        "workspace_id": "00000000-0000-0000-0000-000000000000",
        "role": "owner"
    }
