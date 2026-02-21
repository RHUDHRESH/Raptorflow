import json
import logging
from typing import Optional, Dict, Any
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

_sentinel_manager: Optional["RedisSentinelManager"] = None


class RedisSentinelManager:
    def __init__(self):
        self._sentinel = None
        self._master = None
        self.key_prefix = "session:"
        self.default_ttl = 3600

    async def connect(self) -> bool:
        try:
            from backend.config.settings import get_settings

            settings = get_settings()

            if not settings.REDIS_SENTINEL_ENABLED:
                logger.info("Redis Sentinel disabled")
                return False

            hosts_str = settings.REDIS_SENTINEL_HOSTS
            if not hosts_str:
                logger.warning("REDIS_SENTINEL_ENABLED but no hosts configured")
                return False

            sentinel_hosts = []
            for host_port in hosts_str.split(","):
                host_port = host_port.strip()
                if ":" in host_port:
                    host, port = host_port.split(":")
                    sentinel_hosts.append((host, int(port)))

            if len(sentinel_hosts) < 3:
                logger.warning(
                    f"Need at least 3 Sentinel hosts, got {len(sentinel_hosts)}"
                )

            from redis.asyncio.sentinel import Sentinel

            self._sentinel = Sentinel(
                sentinel_hosts,
                password=settings.REDIS_SENTINEL_PASSWORD,
                socket_connect_timeout=5,
                socket_keepalive=True,
            )

            self._master = self._sentinel.master_for(
                settings.REDIS_SENTINEL_MASTER_NAME,
                password=settings.REDIS_SENTINEL_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
            )

            await self._master.ping()
            logger.info(f"Connected to Redis Sentinel: {sentinel_hosts}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Redis Sentinel: {e}")
            return False

    async def disconnect(self):
        if self._master:
            await self._master.aclose()
            self._master = None
        if self._sentinel:
            await self._sentinel.aclose()
            self._sentinel = None

    @property
    def redis(self):
        if not self._master:
            raise RuntimeError("Redis Sentinel not connected")
        return self._master

    def _make_key(self, session_id: str) -> str:
        return f"{self.key_prefix}{session_id}"

    async def create_session(
        self, data: Dict[str, Any], ttl: Optional[int] = None
    ) -> str:
        session_id = str(uuid.uuid4())
        key = self._make_key(session_id)

        session_data = {
            "data": data,
            "created_at": datetime.utcnow().isoformat(),
        }

        await self.redis.setex(key, ttl or self.default_ttl, json.dumps(session_data))

        return session_id

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        key = self._make_key(session_id)
        data = await self.redis.get(key)

        if data:
            session = json.loads(data)
            await self.redis.expire(key, self.default_ttl)
            return session.get("data")

        return None

    async def delete_session(self, session_id: str):
        key = self._make_key(session_id)
        await self.redis.delete(key)

    async def session_exists(self, session_id: str) -> bool:
        key = self._make_key(session_id)
        return await self.redis.exists(key) > 0


async def get_redis_sentinel_manager() -> RedisSentinelManager:
    global _sentinel_manager
    if _sentinel_manager is None:
        _sentinel_manager = RedisSentinelManager()
    return _sentinel_manager
