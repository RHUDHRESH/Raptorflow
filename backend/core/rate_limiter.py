"""
Simple rate limiting implementation for Raptorflow API endpoints.
"""

import asyncio
import time
from collections import defaultdict, deque
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    cleanup_interval_seconds: int = 300  # 5 minutes
    max_clients: int = 10000


class RateLimiter:
    """Simple in-memory rate limiter with multiple time windows."""
    
    def __init__(self, config: RateLimitConfig = None):
        self.config = config or RateLimitConfig()
        
        # Client tracking: client_id -> {window_start_time, request_count}
        self.clients: Dict[str, Dict[str, any]] = defaultdict(lambda: {
            'minute': {'start_time': time.time(), 'count': 0},
            'hour': {'start_time': time.time(), 'count': 0},
            'day': {'start_time': time.time(), 'count': 0}
        })
        
        # Global statistics
        self.total_requests = 0
        self.blocked_requests = 0
        self.start_time = time.time()
        
        # Background cleanup task
        self._cleanup_task = None
        self._running = False
        
        logger.info(f"Rate limiter initialized: {self.config.requests_per_minute}/min, {self.config.requests_per_hour}/hr, {self.config.requests_per_day}/day")
    
    async def start(self):
        """Start the rate limiter background tasks."""
        if self._running:
            return
        
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("Rate limiter started")
    
    async def stop(self):
        """Stop the rate limiter background tasks."""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("Rate limiter stopped")
    
    def is_allowed(self, client_id: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a request from client is allowed.
        
        Returns:
            (allowed, reason) where reason is None if allowed, or error message if blocked
        """
        current_time = time.time()
        
        if client_id not in self.clients:
            # New client, initialize tracking
            self.clients[client_id] = {
                'minute': {'start_time': current_time, 'count': 0},
                'hour': {'start_time': current_time, 'count': 0},
                'day': {'start_time': current_time, 'count': 0}
            }
        
        client_data = self.clients[client_id]
        
        # Check minute limit
        minute_data = client_data['minute']
        if current_time - minute_data['start_time'] >= 60:
            # Reset minute window
            minute_data['start_time'] = current_time
            minute_data['count'] = 0
        
        if minute_data['count'] >= self.config.requests_per_minute:
            return False, f"Rate limit exceeded: {self.config.requests_per_minute} requests per minute"
        
        # Check hour limit
        hour_data = client_data['hour']
        if current_time - hour_data['start_time'] >= 3600:
            # Reset hour window
            hour_data['start_time'] = current_time
            hour_data['count'] = 0
        
        if hour_data['count'] >= self.config.requests_per_hour:
            return False, f"Rate limit exceeded: {self.config.requests_per_hour} requests per hour"
        
        # Check day limit
        day_data = client_data['day']
        if current_time - day_data['start_time'] >= 86400:
            # Reset day window
            day_data['start_time'] = current_time
            day_data['count'] = 0
        
        if day_data['count'] >= self.config.requests_per_day:
            return False, f"Rate limit exceeded: {self.config.requests_per_day} requests per day"
        
        # Check global client limit
        if len(self.clients) >= self.config.max_clients:
            return False, "Maximum number of clients exceeded"
        
        # Request is allowed, increment counters
        minute_data['count'] += 1
        hour_data['count'] += 1
        day_data['count'] += 1
        self.total_requests += 1
        
        return True, None
    
    def record_request(self, client_id: str, endpoint: str = None):
        """Record a request for analytics."""
        self.total_requests += 1
        logger.debug(f"Request recorded for client {client_id} on endpoint {endpoint}")
    
    def record_blocked_request(self, client_id: str, reason: str):
        """Record a blocked request."""
        self.blocked_requests += 1
        logger.warning(f"Request blocked for client {client_id}: {reason}")
    
    def get_client_stats(self, client_id: str) -> Dict[str, any]:
        """Get statistics for a specific client."""
        if client_id not in self.clients:
            return {"error": "Client not found"}
        
        client_data = self.clients[client_id]
        current_time = time.time()
        
        return {
            "client_id": client_id,
            "requests_this_minute": client_data['minute']['count'],
            "requests_this_hour": client_data['hour']['count'],
            "requests_this_day": client_data['day']['count'],
            "minute_window_remaining": max(0, 60 - int(current_time - client_data['minute']['start_time'])),
            "hour_window_remaining": max(0, 3600 - int(current_time - client_data['hour']['start_time'])),
            "day_window_remaining": max(0, 86400 - int(current_time - client_data['day']['start_time'])),
        }
    
    def get_global_stats(self) -> Dict[str, any]:
        """Get global rate limiting statistics."""
        current_time = time.time()
        uptime = current_time - self.start_time
        
        return {
            "total_requests": self.total_requests,
            "blocked_requests": self.blocked_requests,
            "active_clients": len(self.clients),
            "max_clients": self.config.max_clients,
            "uptime_seconds": int(uptime),
            "uptime_formatted": str(timedelta(seconds=int(uptime))),
            "config": {
                "requests_per_minute": self.config.requests_per_minute,
                "requests_per_hour": self.config.requests_per_hour,
                "requests_per_day": self.config.requests_per_day,
            },
            "started_at": datetime.fromtimestamp(self.start_time).isoformat(),
        }
    
    async def _cleanup_loop(self):
        """Background cleanup of expired client data."""
        while self._running:
            try:
                await asyncio.sleep(self.config.cleanup_interval_seconds)
                current_time = time.time()
                cleanup_count = 0
                
                # Clean up inactive clients
                inactive_clients = []
                for client_id, client_data in self.clients.items():
                    last_activity = max(
                        client_data['minute']['start_time'],
                        client_data['hour']['start_time'],
                        client_data['day']['start_time']
                    )
                    
                    # Remove clients inactive for more than 24 hours
                    if current_time - last_activity > 86400:
                        inactive_clients.append(client_id)
                        cleanup_count += 1
                
                # Remove inactive clients
                for client_id in inactive_clients:
                    del self.clients[client_id]
                
                if cleanup_count > 0:
                    logger.info(f"Cleaned up {cleanup_count} inactive clients")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Rate limiter cleanup error: {e}")
    
    def reset_client(self, client_id: str):
        """Reset rate limiting for a specific client."""
        if client_id in self.clients:
            current_time = time.time()
            self.clients[client_id] = {
                'minute': {'start_time': current_time, 'count': 0},
                'hour': {'start_time': current_time, 'count': 0},
                'day': {'start_time': current_time, 'count': 0}
            }
            logger.info(f"Rate limit reset for client {client_id}")
    
    def block_client(self, client_id: str, duration_seconds: int = 3600):
        """Block a client for a specified duration."""
        if client_id not in self.clients:
            return
        
        # Set all counters to max to effectively block
        current_time = time.time()
        self.clients[client_id] = {
            'minute': {'start_time': current_time, 'count': self.config.requests_per_minute},
            'hour': {'start_time': current_time, 'count': self.config.requests_per_hour},
            'day': {'start_time': current_time, 'count': self.config.requests_per_day},
        }
        
        logger.warning(f"Client {client_id} blocked for {duration_seconds} seconds")


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter(config: RateLimitConfig = None) -> RateLimiter:
    """Get or create global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter(config)
    return _rate_limiter


async def start_rate_limiter(config: RateLimitConfig = None):
    """Start the global rate limiter."""
    rate_limiter = get_rate_limiter(config)
    await rate_limiter.start()


async def stop_rate_limiter():
    """Stop the global rate limiter."""
    global _rate_limiter
    if _rate_limiter:
        await _rate_limiter.stop()


def check_rate_limit(client_id: str) -> Tuple[bool, Optional[str]]:
    """Check rate limit for a client."""
    rate_limiter = get_rate_limiter()
    return rate_limiter.is_allowed(client_id)


def get_rate_limit_stats() -> Dict[str, any]:
    """Get global rate limiting statistics."""
    rate_limiter = get_rate_limiter()
    return rate_limiter.get_global_stats()
