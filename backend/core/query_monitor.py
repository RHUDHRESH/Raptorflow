"""
Database Query Performance Monitor
Tracks slow queries and provides performance insights
"""

import asyncio
import logging
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class QueryStats:
    """Statistics for a specific query"""
    query_hash: str
    query_template: str
    count: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    avg_time: float = 0.0
    slow_count: int = 0  # Queries over threshold


class QueryMonitor:
    """Monitor and track database query performance"""
    
    def __init__(self, slow_query_threshold: float = 1.0):
        """
        Initialize query monitor.
        
        Args:
            slow_query_threshold: Threshold in seconds for slow query logging
        """
        self.slow_query_threshold = slow_query_threshold
        self.stats: Dict[str, QueryStats] = {}
        self.slow_queries: List[dict] = []
        self.max_slow_queries = 100  # Keep last 100 slow queries
        
    def _hash_query(self, query: str) -> str:
        """Generate hash for query (simple version)"""
        import hashlib
        # Normalize query by removing extra whitespace
        normalized = ' '.join(query.split())
        return hashlib.md5(normalized.encode()).hexdigest()[:12]
    
    def _template_query(self, query: str) -> str:
        """Create query template by removing parameter values"""
        # Simple template: replace numbers and strings with placeholders
        import re
        template = re.sub(r"'[^']*'", "'?'", query)
        template = re.sub(r'\b\d+\b', '?', template)
        return ' '.join(template.split())
    
    async def track_query(
        self,
        query: str,
        duration: float,
        params: Optional[tuple] = None,
    ) -> None:
        """
        Track a query execution.
        
        Args:
            query: SQL query string
            duration: Execution time in seconds
            params: Query parameters
        """
        query_hash = self._hash_query(query)
        query_template = self._template_query(query)
        
        # Update or create stats
        if query_hash not in self.stats:
            self.stats[query_hash] = QueryStats(
                query_hash=query_hash,
                query_template=query_template,
            )
        
        stats = self.stats[query_hash]
        stats.count += 1
        stats.total_time += duration
        stats.min_time = min(stats.min_time, duration)
        stats.max_time = max(stats.max_time, duration)
        stats.avg_time = stats.total_time / stats.count
        
        # Track slow queries
        if duration > self.slow_query_threshold:
            stats.slow_count += 1
            
            slow_query_info = {
                "query": query[:200],  # Truncate long queries
                "duration": duration,
                "timestamp": time.time(),
                "params": str(params)[:100] if params else None,
            }
            
            self.slow_queries.append(slow_query_info)
            
            # Keep only recent slow queries
            if len(self.slow_queries) > self.max_slow_queries:
                self.slow_queries = self.slow_queries[-self.max_slow_queries:]
            
            logger.warning(
                f"Slow query detected ({duration:.3f}s): {query[:100]}..."
            )
    
    def get_stats(self, top_n: int = 10) -> List[dict]:
        """
        Get query statistics.
        
        Args:
            top_n: Number of top queries to return
            
        Returns:
            List of query statistics
        """
        # Sort by total time (most expensive queries)
        sorted_stats = sorted(
            self.stats.values(),
            key=lambda s: s.total_time,
            reverse=True
        )
        
        return [
            {
                "query_hash": s.query_hash,
                "query_template": s.query_template[:100],
                "count": s.count,
                "total_time": round(s.total_time, 3),
                "avg_time": round(s.avg_time, 3),
                "min_time": round(s.min_time, 3),
                "max_time": round(s.max_time, 3),
                "slow_count": s.slow_count,
            }
            for s in sorted_stats[:top_n]
        ]
    
    def get_slow_queries(self, limit: int = 20) -> List[dict]:
        """
        Get recent slow queries.
        
        Args:
            limit: Maximum number of slow queries to return
            
        Returns:
            List of slow query information
        """
        return self.slow_queries[-limit:]
    
    def reset_stats(self) -> None:
        """Reset all statistics"""
        self.stats.clear()
        self.slow_queries.clear()
        logger.info("Query monitor statistics reset")


# Global query monitor instance
query_monitor = QueryMonitor(slow_query_threshold=1.0)


async def monitored_query(query: str, *args, executor_func):
    """
    Wrapper to monitor query execution.
    
    Args:
        query: SQL query
        *args: Query parameters
        executor_func: Async function to execute query
        
    Returns:
        Query result
    """
    start_time = time.time()
    
    try:
        result = await executor_func(query, *args)
        duration = time.time() - start_time
        
        # Track query performance
        await query_monitor.track_query(query, duration, args)
        
        return result
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Query failed after {duration:.3f}s: {query[:100]}...")
        raise
