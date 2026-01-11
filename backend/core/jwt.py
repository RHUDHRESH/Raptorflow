"""
JWT validation for Supabase authentication
Handles token extraction, validation, refresh rotation, and claims verification
"""

import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

import jwt

logger = logging.getLogger(__name__)

# Import models from same package
try:
    from .models import JWTPayload
except ImportError:
    # Fallback for when models aren't available yet
    @dataclass
    class JWTPayload:
        sub: str
        email: str
        role: str = "authenticated"
        aud: str = "authenticated"
        exp: Optional[int] = None
        iat: Optional[int] = None
        iss: Optional[str] = None
        session_id: Optional[str] = None

        @classmethod
        def from_dict(cls, data: Dict[str, Any]) -> 'JWTPayload':
            return cls(
                sub=data.get('sub'),
                email=data.get('email'),
                role=data.get('role', 'authenticated'),
                aud=data.get('aud', 'authenticated'),
                exp=data.get('exp'),
                iat=data.get('iat'),
                iss=data.get('iss'),
                session_id=data.get('session_id')
            )

@dataclass
    class RefreshTokenResult:
        """Result of token refresh operation"""
        access_token: str
        refresh_token: str
        expires_in: int
        token_type: str = "bearer"

class JWTValidator:
    """Validates Supabase JWT tokens with refresh rotation"""

    def __init__(self):
        self.jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
        if not self.jwt_secret:
            raise ValueError("SUPABASE_JWT_SECRET must be set")

        self.supabase_url = os.getenv("SUPABASE_URL", "").rstrip("/")
        self.refresh_threshold = 300  # 5 minutes before expiry to refresh

        # Supabase JWT algorithm
        self.algorithm = "HS256"

    def extract_token(self, authorization_header: str) -> Optional[str]:
        """Extract JWT from Authorization header"""
        if not authorization_header:
            return None

        # Remove "Bearer " prefix
        if authorization_header.startswith("Bearer "):
            return authorization_header[7:]

        return None

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode JWT token without verification (for debugging)"""
        try:
            return jwt.decode(token, options={"verify_signature": False})
        except Exception as e:
            logger.error(f"JWT decode error: {e}")
            return None

    def verify_token(self, token: str) -> Optional[JWTPayload]:
        """Verify JWT token and return payload"""
        try:
            # Get issuer from environment
            issuer = f"{self.supabase_url}/auth/v1"
            if not issuer or "your-project" in issuer:
                raise ValueError("SUPABASE_URL not properly configured")

            # Decode and verify token
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.algorithm],
                audience="authenticated",
                issuer=issuer
            )

            # Validate required claims
            if not self.validate_claims(payload):
                return None

            return JWTPayload.from_dict(payload)

        except jwt.ExpiredSignatureError:
            logger.error("JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid JWT token: {e}")
            return None
        except Exception as e:
            logger.error(f"JWT verification error: {e}")
            return None

    def should_refresh_token(self, payload: JWTPayload) -> bool:
        """Check if token should be refreshed based on expiry time"""
        if not payload.exp:
            return False

        current_time = datetime.now().timestamp()
        time_until_expiry = payload.exp - current_time

        return time_until_expiry <= self.refresh_threshold

    async def refresh_token(self, refresh_token: str) -> Optional[RefreshTokenResult]:
        """
        Refresh access token using refresh token

        Args:
            refresh_token: The refresh token

        Returns:
            RefreshTokenResult if successful, None otherwise
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.supabase_url}/auth/v1/token?grant_type=refresh_token",
                    headers={
                        "apikey": os.getenv("SUPABASE_ANON_KEY", ""),
                        "Content-Type": "application/json"
                    },
                    json={"refresh_token": refresh_token}
                )

                if response.status_code == 200:
                    data = response.json()
                    return RefreshTokenResult(
                        access_token=data["access_token"],
                        refresh_token=data["refresh_token"],
                        expires_in=data["expires_in"],
                        token_type=data["token_type"]
                    )
                else:
                    logger.error(f"Token refresh failed: {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return None

    async def verify_and_refresh_if_needed(self, token: str, refresh_token: Optional[str] = None) -> Tuple[Optional[JWTPayload], Optional[RefreshTokenResult]]:
        """
        Verify token and refresh if needed

        Args:
            token: Access token to verify
            refresh_token: Optional refresh token for rotation

        Returns:
            Tuple of (payload, refresh_result) where refresh_result is None if no refresh was needed/possible
        """
        payload = self.verify_token(token)

        if not payload:
            return None, None

        # Check if token should be refreshed
        if self.should_refresh_token(payload) and refresh_token:
            logger.info("Token approaching expiry, initiating refresh")
            refresh_result = await self.refresh_token(refresh_token)
            return payload, refresh_result

        return payload, None

    def validate_claims(self, payload: Dict[str, Any]) -> bool:
        """Validate JWT claims"""
        required_claims = ['sub', 'email', 'role', 'aud']

        for claim in required_claims:
            if claim not in payload:
                logger.error(f"Missing required claim: {claim}")
                return False

        # Validate role
        if payload['role'] not in ['authenticated', 'anon']:
            logger.error(f"Invalid role: {payload['role']}")
            return False

        # Validate audience
        if payload['aud'] != 'authenticated':
            logger.error(f"Invalid audience: {payload['aud']}")
            return False

        # Validate subject (user ID)
        if not payload['sub'] or not isinstance(payload['sub'], str):
            logger.error(f"Invalid subject: {payload['sub']}")
            return False

        return True

    def is_token_expired(self, payload: Dict[str, Any]) -> bool:
        """Check if token is expired"""
        if 'exp' not in payload:
            return True

        exp_timestamp = payload['exp']
        current_timestamp = datetime.now().timestamp()

        return current_timestamp > exp_timestamp

# Singleton instance
_jwt_validator: Optional[JWTValidator] = None

def get_jwt_validator() -> JWTValidator:
    """Get JWT validator singleton"""
    global _jwt_validator
    if _jwt_validator is None:
        _jwt_validator = JWTValidator()
    return _jwt_validator
