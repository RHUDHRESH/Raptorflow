import hashlib
from typing import Optional
from datetime import datetime
import jwt


class TokenBlacklist:
    def __init__(self):
        self.blacklist_prefix = "blacklist:"
        self._redis = None

    async def _get_redis(self):
        if self._redis is None:
            from backend.infrastructure.cache.redis_sentinel import (
                get_redis_sentinel_manager,
            )

            sentinel = await get_redis_sentinel_manager()
            if sentinel:
                self._redis = sentinel.redis
        return self._redis

    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()[:32]

    def _make_key(self, token_hash: str) -> str:
        return f"{self.blacklist_prefix}{token_hash}"

    async def verify_token(self, token: str, secret_key: str) -> dict:
        """
        Verify token with blacklist check - blacklist is checked BEFORE signature verification.
        This prevents race conditions where a token could be used in the gap between
        blacklist check and signature verification.
        """
        try:
            redis = await self._get_redis()

            token_hash = self._hash_token(token)
            key = self._make_key(token_hash)

            if redis and await redis.exists(key):
                raise jwt.InvalidTokenError("Token has been revoked")

            payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            return payload

        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError("Token has expired")
        except jwt.InvalidTokenError:
            raise

    async def blacklist_token(self, token: str) -> bool:
        try:
            redis = await self._get_redis()
            if not redis:
                return False

            payload = jwt.decode(
                token, options={"verify_signature": False, "verify_exp": False}
            )

            exp = payload.get("exp")
            if not exp:
                ttl = 7 * 24 * 3600
            else:
                ttl = max(0, exp - int(datetime.utcnow().timestamp()))

            if ttl > 0:
                token_hash = self._hash_token(token)
                key = self._make_key(token_hash)
                await redis.setex(key, ttl, "1")
                return True

            return False
        except jwt.InvalidTokenError:
            return False

    async def is_blacklisted(self, token: str) -> bool:
        try:
            redis = await self._get_redis()
            if not redis:
                return False

            token_hash = self._hash_token(token)
            key = self._make_key(token_hash)
            return await redis.exists(key) > 0
        except Exception:
            return True

    async def blacklist_refresh_token(self, user_id: str, token_id: str):
        redis = await self._get_redis()
        if redis:
            key = f"{self.blacklist_prefix}user:{user_id}:{token_id}"
            await redis.setex(key, 7 * 24 * 3600, "1")


token_blacklist = TokenBlacklist()
