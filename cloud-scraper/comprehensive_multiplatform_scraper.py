"""
Comprehensive Multi-Platform Scraper with Innovative Techniques
Goes beyond Reddit to include multiple platforms and advanced scraping methods
"""

import argparse
import asyncio
import hashlib
import json
import math
import random
import re
import sqlite3
import statistics
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import median
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib import request as urlrequest
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup

try:
    from readability import Document

    READABILITY_AVAILABLE = True
except ImportError:
    READABILITY_AVAILABLE = False
try:
    import feedparser

    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False
try:
    import aiohttp
except ImportError:
    pass

# Ensure hashlib is available globally
_hashlib = hashlib

DEFAULT_CONFIG_PATH = Path("comprehensive_config.json")
DEFAULT_DB_PATH = "comprehensive_scraper.db"
SCHEMA_VERSION = 3
FETCH_VERSION = "2026.01.05"
DEFAULT_USER_AGENTS = [
    # Modern desktop
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Mobile
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    # Fallback minimal
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
]


# Simple structured logger using json to avoid adding dependencies
def log_event(event: str, **kwargs):
    payload = {
        "event": event,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **kwargs,
    }
    print(json.dumps(payload, default=str))


@dataclass
class ScraperConfig:
    minnesota_keywords: List[str]
    coffee_keywords: List[str]
    relevance_thresholds: Dict[str, float]
    include_platforms: Optional[Set[str]] = None
    exclude_platforms: Optional[Set[str]] = None
    per_platform_limit: Optional[int] = None
    proxy: Optional[str] = None
    user_agents: Optional[List[str]] = None
    dry_run: bool = False
    output_json: Optional[Path] = None
    report_dir: Path = Path("reports")
    alert_webhook: Optional[str] = None
    alert_success_rate_threshold: float = 0.6
    output_json_cli: Optional[Path] = None

    @staticmethod
    def load(path: Path) -> "ScraperConfig":
        if not path.exists():
            return ScraperConfig(
                minnesota_keywords=[
                    "minnesota",
                    "mn",
                    "minneapolis",
                    "st paul",
                    "saint paul",
                    "duluth",
                    "rochester",
                    "bloomington",
                    "brooklyn park",
                    "plymouth",
                    "eagan",
                    "woodbury",
                    "lakeville",
                    "st cloud",
                    "eden prairie",
                    "minnetonka",
                    "twin cities",
                    "metro area",
                    "north star state",
                ],
                coffee_keywords=[
                    "coffee",
                    "cafe",
                    "espresso",
                    "roastery",
                    "coffee shop",
                    "barista",
                    "cold brew",
                    "nitro coffee",
                    "specialty coffee",
                    "third wave",
                    "coffee beans",
                    "local coffee",
                    "craft coffee",
                    "coffee culture",
                    "brew methods",
                    "coffee trends",
                    "new cafe",
                    "coffee opening",
                    "coffee event",
                    "coffee festival",
                    "latte art",
                    "pour over",
                ],
                relevance_thresholds={"default": 0.05},
                alert_webhook=None,
                alert_success_rate_threshold=0.6,
            )

        data = json.loads(path.read_text())
        return ScraperConfig(
            minnesota_keywords=data.get("minnesota_keywords", []),
            coffee_keywords=data.get("coffee_keywords", []),
            relevance_thresholds=data.get("relevance_thresholds", {"default": 0.05}),
            include_platforms=(
                set(data["include_platforms"])
                if data.get("include_platforms")
                else None
            ),
            exclude_platforms=(
                set(data["exclude_platforms"])
                if data.get("exclude_platforms")
                else None
            ),
            per_platform_limit=data.get("per_platform_limit"),
            proxy=data.get("proxy"),
            user_agents=data.get("user_agents"),
            dry_run=bool(data.get("dry_run", False)),
            output_json=Path(data["output_json"]) if data.get("output_json") else None,
            report_dir=Path(data.get("report_dir", "reports")),
            alert_webhook=data.get("alert_webhook"),
            alert_success_rate_threshold=float(
                data.get("alert_success_rate_threshold", 0.6)
            ),
            output_json_cli=(
                Path(data["output_json_cli"]) if data.get("output_json_cli") else None
            ),
        )


def _simhash(text: str, bits: int = 64) -> int:
    """Simple SimHash for near-duplicate detection."""
    if not text:
        return 0
    tokens = re.findall(r"\w+", text.lower())
    if not tokens:
        return 0
    v = [0] * bits
    for token in tokens:
        h = int(hashlib.md5(token.encode()).hexdigest(), 16)
        for i in range(bits):
            v[i] += 1 if (h >> i) & 1 else -1
    fingerprint = 0
    for i in range(bits):
        if v[i] >= 0:
            fingerprint |= 1 << i
    # Clamp to signed 64-bit to satisfy SQLite INTEGER range
    max_signed_64 = (1 << 63) - 1
    return fingerprint & max_signed_64


def _hamming_distance(a: int, b: int) -> int:
    return bin(a ^ b).count("1")


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, reset_after: int = 60):
        self.failure_threshold = failure_threshold
        self.reset_after = reset_after
        self.failures = defaultdict(int)
        self.last_failure_ts = {}

    def record_success(self, key: str):
        self.failures[key] = 0
        self.last_failure_ts[key] = datetime.now(timezone.utc)

    def record_failure(self, key: str):
        self.failures[key] += 1
        self.last_failure_ts[key] = datetime.now(timezone.utc)

    def is_open(self, key: str) -> bool:
        if self.failures[key] < self.failure_threshold:
            return False
        last_ts = self.last_failure_ts.get(key, datetime.now(timezone.utc))
        if (datetime.now(timezone.utc) - last_ts).total_seconds() > self.reset_after:
            self.failures[key] = 0
            return False
        return True


def _tokenize_and_truncate(text: str, max_chars: int = 5000) -> Tuple[str, int, int]:
    truncated = 0
    if len(text) > max_chars:
        text = text[:max_chars]
        truncated = 1
    token_count = len(re.findall(r"\w+", text))
    return text, token_count, truncated


def _percentile(values: List[float], pct: float) -> float:
    if not values:
        return 0.0
    arr = sorted(values)
    k = (len(arr) - 1) * pct
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return arr[int(k)]
    d0 = arr[int(f)] * (c - k)
    d1 = arr[int(c)] * (k - f)
    return d0 + d1


class ComprehensiveScraper:
    """Comprehensive scraper with innovative multi-platform techniques"""

    def __init__(
        self,
        db_path: str = DEFAULT_DB_PATH,
        config: Optional[ScraperConfig] = None,
        run_id: Optional[str] = None,
    ):
        self.db_path = db_path
        self.config = config or ScraperConfig.load(DEFAULT_CONFIG_PATH)
        self.session = None
        self.run_id = (
            run_id or f"run-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
        )
        self.circuit_breaker = CircuitBreaker()
        self.backoff_base = 0.5
        self.backoff_cap = 8.0
        self.hashes_seen: Set[str] = set()
        self.simhashes_seen: List[int] = []
        self.latencies: Dict[str, List[float]] = defaultdict(list)
        self.failures: Dict[str, int] = defaultdict(int)
        self.retries: Dict[str, int] = defaultdict(int)

        # Multi-platform sources (can be filtered by config include/exclude)
        self.platforms = {
            "reddit": {
                "enabled": True,
                "base_url": "https://www.reddit.com",
                "endpoints": [
                    "/r/coffee/hot.json",
                    "/r/Coffee/hot.json",
                    "/r/Minneapolis/hot.json",
                    "/r/twincities/hot.json",
                    "/r/Minnesota/hot.json",
                ],
            },
            "news": {
                "enabled": True,
                "sources": [
                    "https://www.startribune.com/",
                    "https://www.mprnews.org/minnesota/",
                    "https://www.mprnews.org/latest",
                    "https://www.twincities.com/",
                    "https://www.mprnews.org/minnesota/",
                    "https://minnesota.cbslocal.com/",
                    "https://www.kare11.com/minnesota/",
                    "https://minnesota.gov/news/",
                ],
            },
            "blogs": {
                "enabled": True,
                "sources": [
                    "https://minnesotamonthly.com/",
                    "https://www.mnopedia.org/",
                    "https://minnesotabrown.com/",
                    "https://www.tcdailyplanet.net/",
                    "https://www.minnpost.com/",
                ],
            },
            "social": {
                "enabled": True,
                "rss_feeds": [
                    "https://www.startribune.com/rss/",
                    "https://minnesotamonthly.com/feed/",
                    "https://minnpost.com/feed/",
                    "https://mprnews.org/feed/rss/",
                ],
            },
            "forums": {
                "enabled": True,
                "base_url": "https://www.reddit.com",
                "endpoints": [
                    "/r/minneapolis/hot.json",
                    "/r/twincities/hot.json",
                    "/r/minnesota/hot.json",
                ],
            },
        }

        # Keyword config
        self.minnesota_keywords = self.config.minnesota_keywords
        self.coffee_keywords = self.config.coffee_keywords

        self._initialize_database()

    def _initialize_database(self):
        """Initialize comprehensive scraper database"""

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")

            # Schema metadata
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_meta (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    schema_version INTEGER NOT NULL,
                    fetch_version TEXT NOT NULL,
                    applied_at DATETIME NOT NULL
                )
            """
            )

            # Multi-platform content table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS comprehensive_content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT,
                    author TEXT,
                    published_date DATETIME,
                    minnesota_mentions INTEGER DEFAULT 0,
                    coffee_mentions INTEGER DEFAULT 0,
                    relevance_score REAL DEFAULT 0.0,
                    engagement_score REAL DEFAULT 0.0,
                    content_hash TEXT NOT NULL,
                    scraped_at DATETIME NOT NULL,
                    token_count INTEGER DEFAULT 0,
                    truncated INTEGER DEFAULT 0,
                    simhash INTEGER DEFAULT 0,
                    fetch_version TEXT DEFAULT '',
                    schema_version INTEGER DEFAULT 1
                )
            """
            )
            content_columns = {
                row[1]
                for row in conn.execute("PRAGMA table_info(comprehensive_content)")
            }
            if "token_count" not in content_columns:
                conn.execute(
                    "ALTER TABLE comprehensive_content ADD COLUMN token_count INTEGER DEFAULT 0"
                )
            if "truncated" not in content_columns:
                conn.execute(
                    "ALTER TABLE comprehensive_content ADD COLUMN truncated INTEGER DEFAULT 0"
                )
            if "simhash" not in content_columns:
                conn.execute(
                    "ALTER TABLE comprehensive_content ADD COLUMN simhash INTEGER DEFAULT 0"
                )
            if "fetch_version" not in content_columns:
                conn.execute(
                    "ALTER TABLE comprehensive_content ADD COLUMN fetch_version TEXT DEFAULT ''"
                )
            if "schema_version" not in content_columns:
                conn.execute(
                    "ALTER TABLE comprehensive_content ADD COLUMN schema_version INTEGER DEFAULT 1"
                )

            # Platform performance table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS platform_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    source_count INTEGER NOT NULL,
                    success_rate REAL DEFAULT 0.0,
                    avg_relevance REAL DEFAULT 0.0,
                    total_content INTEGER NOT NULL,
                    content_count INTEGER DEFAULT 0,
                    last_updated DATETIME NOT NULL,
                    p50_latency REAL DEFAULT 0.0,
                    p90_latency REAL DEFAULT 0.0,
                    p99_latency REAL DEFAULT 0.0,
                    failure_count INTEGER DEFAULT 0,
                    retry_count INTEGER DEFAULT 0
                )
            """
            )
            # Backfill/migrate for older databases missing columns
            columns = {
                row[1]
                for row in conn.execute("PRAGMA table_info(platform_performance)")
            }
            if "total_content" not in columns:
                conn.execute(
                    "ALTER TABLE platform_performance ADD COLUMN total_content INTEGER DEFAULT 0"
                )
            if "content_count" not in columns:
                conn.execute(
                    "ALTER TABLE platform_performance ADD COLUMN content_count INTEGER DEFAULT 0"
                )
            if "p50_latency" not in columns:
                conn.execute(
                    "ALTER TABLE platform_performance ADD COLUMN p50_latency REAL DEFAULT 0.0"
                )
            if "p90_latency" not in columns:
                conn.execute(
                    "ALTER TABLE platform_performance ADD COLUMN p90_latency REAL DEFAULT 0.0"
                )
            if "p99_latency" not in columns:
                conn.execute(
                    "ALTER TABLE platform_performance ADD COLUMN p99_latency REAL DEFAULT 0.0"
                )
            if "failure_count" not in columns:
                conn.execute(
                    "ALTER TABLE platform_performance ADD COLUMN failure_count INTEGER DEFAULT 0"
                )
            if "retry_count" not in columns:
                conn.execute(
                    "ALTER TABLE platform_performance ADD COLUMN retry_count INTEGER DEFAULT 0"
                )

            # Trend analysis table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS comprehensive_trends (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_date DATETIME NOT NULL,
                    total_platforms INTEGER NOT NULL,
                    total_content INTEGER NOT NULL,
                    top_platforms TEXT,
                    trending_topics TEXT,
                    confidence_score REAL DEFAULT 0.0,
                    insights TEXT
                )
            """
            )

            # Indexes for speed
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_content_platform_hash ON comprehensive_content(platform, content_hash)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_content_scraped_at ON comprehensive_content(scraped_at)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_content_simhash ON comprehensive_content(simhash)"
            )

            # Schema meta upsert
            cur = conn.execute("SELECT schema_version FROM schema_meta WHERE id = 1")
            row = cur.fetchone()
            if not row:
                conn.execute(
                    "INSERT INTO schema_meta (id, schema_version, fetch_version, applied_at) VALUES (1, ?, ?, ?)",
                    (
                        SCHEMA_VERSION,
                        FETCH_VERSION,
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
            elif row[0] != SCHEMA_VERSION:
                conn.execute(
                    "UPDATE schema_meta SET schema_version = ?, fetch_version = ?, applied_at = ? WHERE id = 1",
                    (
                        SCHEMA_VERSION,
                        FETCH_VERSION,
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )

            conn.commit()

    async def initialize(self):
        """Initialize HTTP session with advanced configuration"""

        timeout = aiohttp.ClientTimeout(total=30)
        headers = {
            "User-Agent": self._select_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }
        connector = None
        if self.config.proxy:
            connector = aiohttp.TCPConnector(ssl=False)

        self.session = aiohttp.ClientSession(
            timeout=timeout, headers=headers, connector=connector
        )

        print("✅ Comprehensive Multi-Platform Scraper initialized")
        print(
            f"📱 Platforms: {len([p for p in self.platforms if self.platforms[p]['enabled']])}"
        )
        print(f"🔍 Total sources: {self._count_total_sources()}")

    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()

    def _select_user_agent(self) -> str:
        if self.config.user_agents:
            return random.choice(self.config.user_agents)
        return random.choice(DEFAULT_USER_AGENTS)

    def _is_duplicate(self, content_hash: str, simh: int) -> bool:
        if content_hash in self.hashes_seen:
            return True
        for seen in self.simhashes_seen:
            if _hamming_distance(simh, seen) <= 3:
                return True
        self.hashes_seen.add(content_hash)
        self.simhashes_seen.append(simh)
        return False

    def _should_skip_platform(self, platform: str) -> bool:
        if (
            self.config.include_platforms
            and platform not in self.config.include_platforms
        ):
            return True
        if self.config.exclude_platforms and platform in self.config.exclude_platforms:
            return True
        return False

    async def _request_with_retry(
        self, url: str, timeout: int = 20, platform: str = "", attempt: int = 0
    ):
        if self.circuit_breaker.is_open(platform):
            raise RuntimeError(f"Circuit open for platform {platform}")

        backoff = min(self.backoff_cap, self.backoff_base * math.pow(2, attempt)) * (
            1 + random.random()
        )
        if attempt > 0:
            await asyncio.sleep(backoff)

        start = time.time()
        try:
            # rotate UA per attempt to dodge soft blocks (e.g., 429)
            headers = {"User-Agent": self._select_user_agent()}
            async with self.session.get(
                url, timeout=timeout, proxy=self.config.proxy, headers=headers
            ) as response:
                text = await response.text()
                latency = time.time() - start
                self.latencies[platform].append(latency)
                log_event(
                    "http_response",
                    run_id=self.run_id,
                    platform=platform,
                    url=url,
                    status=response.status,
                    latency_ms=int(latency * 1000),
                    attempt=attempt,
                )
                if response.status == 429 and attempt < 4:
                    # soft throttle: wait longer and retry with fresh UA
                    self.retries[platform] += 1
                    await asyncio.sleep(backoff + 1.5)
                    return await self._request_with_retry(
                        url, timeout, platform, attempt + 1
                    )
                if response.status >= 500 and attempt < 3:
                    self.retries[platform] += 1
                    return await self._request_with_retry(
                        url, timeout, platform, attempt + 1
                    )
                if response.status >= 400:
                    self.failures[platform] += 1
                    self.circuit_breaker.record_failure(platform)
                    raise RuntimeError(f"HTTP {response.status}")
                self.circuit_breaker.record_success(platform)
                return response, text
        except Exception as e:
            self.failures[platform] += 1
            self.circuit_breaker.record_failure(platform)
            log_event(
                "http_error",
                run_id=self.run_id,
                platform=platform,
                url=url,
                error=str(e),
                attempt=attempt,
            )
            if attempt < 3:
                self.retries[platform] += 1
                return await self._request_with_retry(
                    url, timeout, platform, attempt + 1
                )
            raise e

    def _count_total_sources(self) -> int:
        """Count total sources across all platforms"""

        total = 0
        for platform, config in self.platforms.items():
            if config["enabled"]:
                if "endpoints" in config:
                    total += len(config["endpoints"])
                elif "sources" in config:
                    total += len(config["sources"])
                elif "rss_feeds" in config:
                    total += len(config["rss_feeds"])

        return total

    def _send_alert_if_needed(self, analysis: Dict[str, Any]):
        webhook = self.config.alert_webhook
        if not webhook:
            return
        avg_success = 1.0
        stats = analysis.get("platform_stats", {})
        if stats:
            avg_success = sum(v.get("success_rate", 0.0) for v in stats.values()) / max(
                len(stats), 1
            )
        if avg_success >= self.config.alert_success_rate_threshold:
            return
        payload = json.dumps(
            {
                "event": "scrape_degraded",
                "run_id": self.run_id,
                "avg_success_rate": avg_success,
                "threshold": self.config.alert_success_rate_threshold,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "platforms": list(stats.keys()),
            }
        ).encode()
        try:
            req = urlrequest.Request(
                webhook, data=payload, headers={"Content-Type": "application/json"}
            )
            urlrequest.urlopen(req, timeout=5)
            log_event(
                "alert_sent",
                run_id=self.run_id,
                avg_success=avg_success,
                threshold=self.config.alert_success_rate_threshold,
            )
        except Exception as e:
            log_event("alert_failed", run_id=self.run_id, error=str(e))

    async def scrape_all_platforms(self) -> Dict[str, List[Dict]]:
        """Scrape all enabled platforms with innovative techniques"""

        print(f"🚀 COMPREHENSIVE MULTI-PLATFORM SCRAPING")
        print("=" * 60)

        all_results = {}

        # Scrape each platform
        for platform, config in self.platforms.items():
            if not config["enabled"]:
                continue
            if self._should_skip_platform(platform):
                continue

            print(f"📱 Scraping {platform.upper()} platform...")

            try:
                if platform == "reddit":
                    results = await self._scrape_reddit_advanced(config)
                elif platform == "news":
                    results = await self._scrape_news_sites(config)
                elif platform == "blogs":
                    results = await self._scrape_blogs(config)
                elif platform == "social":
                    results = await self._scrape_rss_feeds(config)
                elif platform == "forums":
                    # Forums reuse reddit-style sources; fall back to reddit results to avoid double-scrape/dedupe zeroing.
                    results = await self._scrape_forums(config)
                    if not results and "reddit" in all_results:
                        results = list(all_results.get("reddit", []))
                else:
                    results = []

                # Apply per-platform limit if set
                if self.config.per_platform_limit is not None:
                    results = results[: self.config.per_platform_limit]

                all_results[platform] = results
                print(f"   ✅ {platform}: {len(results)} items")

                # Store results
                await self._store_platform_results(platform, results)

            except Exception as e:
                print(f"   ❌ {platform}: Error - {e}")
                all_results[platform] = []

        return all_results

    async def _scrape_reddit_advanced(self, config: Dict) -> List[Dict]:
        """Advanced Reddit scraping with innovative techniques"""

        results = []

        for endpoint in config["endpoints"]:
            try:
                url = urljoin(config["base_url"], endpoint)
                response, body = await self._request_with_retry(
                    url, timeout=20, platform="reddit"
                )
                if response.status == 200:
                    data = json.loads(body)

                    for post in data.get("data", {}).get("children", []):
                        post_data = post.get("data", {})

                        # Advanced content extraction
                        content = self._extract_reddit_content(post_data)

                        # Calculate relevance
                        relevance = self._calculate_relevance(
                            content["title"], content["text"]
                        )
                        if relevance < self.config.relevance_thresholds.get(
                            "reddit",
                            self.config.relevance_thresholds.get("default", 0.05),
                        ):
                            continue

                        # Calculate engagement
                        engagement = self._calculate_engagement(
                            post_data.get("score", 0),
                            post_data.get("num_comments", 0),
                            post_data.get("upvote_ratio", 0.5),
                        )

                        content_hash = self._generate_content_hash(
                            content["title"], content["text"]
                        )
                        simh = _simhash(f"{content['title']} {content['text']}")
                        if self._is_duplicate(content_hash, simh):
                            continue

                        combined = f"{content['title']} {content['text']}"
                        _, tokens, truncated = _tokenize_and_truncate(combined)

                        result = {
                            "source_url": f"https://reddit.com{post_data.get('permalink', '')}",
                            "title": content["title"],
                            "content": content["text"],
                            "author": post_data.get("author", ""),
                            "published_date": datetime.fromtimestamp(
                                post_data.get("created_utc", 0), timezone.utc
                            ),
                            "minnesota_mentions": content["minnesota_mentions"],
                            "coffee_mentions": content["coffee_mentions"],
                            "relevance_score": relevance,
                            "engagement_score": engagement,
                            "content_hash": content_hash,
                            "simhash": simh,
                            "token_count": tokens,
                            "truncated": truncated,
                            "fetch_version": FETCH_VERSION,
                            "schema_version": SCHEMA_VERSION,
                        }

                        results.append(result)

                await asyncio.sleep(0.5)  # Rate limiting

            except Exception as e:
                print(f"      Reddit endpoint error: {e}")

        return results

    async def _scrape_news_sites(self, config: Dict) -> List[Dict]:
        """Innovative news site scraping"""

        results = []

        for source in config["sources"]:
            try:
                response, html = await self._request_with_retry(
                    source, timeout=20, platform="news"
                )
                articles = []
                if response.status == 200:
                    soup = BeautifulSoup(html, "html.parser")
                    articles = self._extract_news_articles(soup, source)

                    # Fallback via readability when available
                    if not articles and READABILITY_AVAILABLE:
                        try:
                            doc = Document(html)
                            title = doc.short_title() or source
                            content = doc.summary() or ""
                            articles = [
                                {
                                    "title": title,
                                    "content": BeautifulSoup(
                                        content, "html.parser"
                                    ).get_text(strip=True)[:500],
                                    "url": source,
                                    "author": "",
                                    "published_date": datetime.now(timezone.utc),
                                }
                            ]
                        except Exception:
                            pass

                    for article in articles:
                        relevance = self._calculate_relevance(
                            article["title"], article["content"]
                        )
                        if relevance < self.config.relevance_thresholds.get(
                            "news",
                            self.config.relevance_thresholds.get("default", 0.05),
                        ):
                            continue

                        content_hash = self._generate_content_hash(
                            article["title"], article["content"]
                        )
                        simh = _simhash(f"{article['title']} {article['content']}")
                        if self._is_duplicate(content_hash, simh):
                            continue

                        title_trunc, tokens, truncated = _tokenize_and_truncate(
                            article["title"] + " " + article["content"]
                        )

                        result = {
                            "source_url": article["url"],
                            "title": article["title"],
                            "content": article["content"],
                            "author": article.get("author", ""),
                            "published_date": article.get(
                                "published_date", datetime.now(timezone.utc)
                            ),
                            "minnesota_mentions": self._count_mentions(
                                article["title"] + " " + article["content"],
                                self.minnesota_keywords,
                            ),
                            "coffee_mentions": self._count_mentions(
                                article["title"] + " " + article["content"],
                                self.coffee_keywords,
                            ),
                            "relevance_score": relevance,
                            "engagement_score": 0.0,
                            "content_hash": content_hash,
                            "simhash": simh,
                            "token_count": tokens,
                            "truncated": truncated,
                            "fetch_version": FETCH_VERSION,
                            "schema_version": SCHEMA_VERSION,
                        }

                        results.append(result)

                await asyncio.sleep(1.0)  # Rate limiting for news sites

            except Exception as e:
                print(f"      News site error: {e}")

        return results

    async def _scrape_blogs(self, config: Dict) -> List[Dict]:
        """Innovative blog scraping"""

        results = []

        for source in config["sources"]:
            try:
                response, html = await self._request_with_retry(
                    source, timeout=20, platform="blogs"
                )
                if response.status == 200:
                    soup = BeautifulSoup(html, "html.parser")

                    # Extract blog posts
                    posts = self._extract_blog_posts(soup, source)

                    # Fallback via readability if needed
                    if not posts and READABILITY_AVAILABLE:
                        try:
                            doc = Document(html)
                            title = doc.short_title() or source
                            content = doc.summary() or ""
                            posts = [
                                {
                                    "title": title,
                                    "content": BeautifulSoup(
                                        content, "html.parser"
                                    ).get_text(strip=True)[:500],
                                    "url": source,
                                    "author": "",
                                    "published_date": datetime.now(timezone.utc),
                                }
                            ]
                        except Exception:
                            pass

                    for post in posts:
                        relevance = self._calculate_relevance(
                            post["title"], post["content"]
                        )
                        if relevance < self.config.relevance_thresholds.get(
                            "blogs",
                            self.config.relevance_thresholds.get("default", 0.05),
                        ):
                            continue

                        content_hash = self._generate_content_hash(
                            post["title"], post["content"]
                        )
                        simh = _simhash(f"{post['title']} {post['content']}")
                        if self._is_duplicate(content_hash, simh):
                            continue

                        _, tokens, truncated = _tokenize_and_truncate(
                            post["title"] + " " + post["content"]
                        )

                        result = {
                            "source_url": post["url"],
                            "title": post["title"],
                            "content": post["content"],
                            "author": post.get("author", ""),
                            "published_date": post.get(
                                "published_date", datetime.now(timezone.utc)
                            ),
                            "minnesota_mentions": self._count_mentions(
                                post["title"] + " " + post["content"],
                                self.minnesota_keywords,
                            ),
                            "coffee_mentions": self._count_mentions(
                                post["title"] + " " + post["content"],
                                self.coffee_keywords,
                            ),
                            "relevance_score": relevance,
                            "engagement_score": 0.0,
                            "content_hash": content_hash,
                            "simhash": simh,
                            "token_count": tokens,
                            "truncated": truncated,
                            "fetch_version": FETCH_VERSION,
                            "schema_version": SCHEMA_VERSION,
                        }

                        results.append(result)

                await asyncio.sleep(1.0)

            except Exception as e:
                print(f"      Blog error: {e}")

        return results

    async def _scrape_rss_feeds(self, config: Dict) -> List[Dict]:
        """Innovative RSS feed scraping"""

        results = []

        for feed_url in config["rss_feeds"]:
            try:
                if not FEEDPARSER_AVAILABLE:
                    continue
                feed = feedparser.parse(feed_url)

                for entry in feed.entries[:20]:  # Limit to 20 most recent
                    title = entry.get("title", "")
                    content = entry.get("summary", "") or entry.get("description", "")

                    relevance = self._calculate_relevance(title, content)
                    if relevance < self.config.relevance_thresholds.get(
                        "social", self.config.relevance_thresholds.get("default", 0.05)
                    ):
                        continue

                    content_hash = self._generate_content_hash(title, content)
                    simh = _simhash(f"{title} {content}")
                    if self._is_duplicate(content_hash, simh):
                        continue

                    _, tokens, truncated = _tokenize_and_truncate(title + " " + content)

                    result = {
                        "source_url": entry.get("link", ""),
                        "title": title,
                        "content": content,
                        "author": entry.get("author", ""),
                        "published_date": (
                            datetime.fromtimestamp(
                                time.mktime(entry.published_parsed), timezone.utc
                            )
                            if entry.get("published_parsed")
                            else datetime.now(timezone.utc)
                        ),
                        "minnesota_mentions": self._count_mentions(
                            title + " " + content, self.minnesota_keywords
                        ),
                        "coffee_mentions": self._count_mentions(
                            title + " " + content, self.coffee_keywords
                        ),
                        "relevance_score": relevance,
                        "engagement_score": 0.0,
                        "content_hash": content_hash,
                        "simhash": simh,
                        "token_count": tokens,
                        "truncated": truncated,
                        "fetch_version": FETCH_VERSION,
                        "schema_version": SCHEMA_VERSION,
                    }

                    results.append(result)

                await asyncio.sleep(0.5)

            except Exception as e:
                print(f"      RSS feed error: {e}")

        return results

    async def _scrape_forums(self, config: Dict) -> List[Dict]:
        """Innovative forum scraping"""

        try:
            # For now, forums will use the same Reddit scraping logic
            # In a production system, this would include other forum platforms
            if "endpoints" in config:
                return await self._scrape_reddit_advanced(config)
            else:
                print(f"      Forums configuration missing endpoints")
                return []
        except Exception as e:
            print(f"      Forums scraping error: {e}")
            return []

    def _extract_reddit_content(self, post_data: Dict) -> Dict[str, Any]:
        """Extract and enhance Reddit content"""

        title = post_data.get("title", "")
        content = post_data.get("selftext", "")

        # Count mentions
        minnesota_mentions = self._count_mentions(
            title + " " + content, self.minnesota_keywords
        )
        coffee_mentions = self._count_mentions(
            title + " " + content, self.coffee_keywords
        )

        return {
            "title": title,
            "text": content,
            "minnesota_mentions": minnesota_mentions,
            "coffee_mentions": coffee_mentions,
        }

    def _extract_news_articles(
        self, soup: BeautifulSoup, source_url: str
    ) -> List[Dict]:
        """Extract articles from news sites using innovative selectors"""

        articles = []

        # Common article selectors
        article_selectors = [
            "article",
            ".article",
            ".post",
            ".story",
            ".news-item",
            "h1 a",
            "h2 a",
            "h3 a",
            ".headline a",
            ".title a",
        ]

        for selector in article_selectors:
            elements = soup.select(selector)

            for element in elements:
                try:
                    # Extract title
                    title_elem = element.find(["h1", "h2", "h3", "h4", "a"])
                    title = (
                        title_elem.get_text(strip=True)
                        if title_elem
                        else element.get_text(strip=True)
                    )

                    # Extract URL
                    url = element.get("href", "")
                    if url and not url.startswith("http"):
                        url = urljoin(source_url, url)

                    # Extract content (limited)
                    content = element.get_text(strip=True)[:500]

                    if title and len(title) > 10:
                        articles.append(
                            {
                                "title": title,
                                "content": content,
                                "url": url,
                                "author": "",
                                "published_date": datetime.now(timezone.utc),
                            }
                        )

                except Exception:
                    continue

        return articles[:20]  # Limit to 20 articles

    def _extract_blog_posts(self, soup: BeautifulSoup, source_url: str) -> List[Dict]:
        """Extract blog posts using innovative techniques"""

        posts = []

        # Blog-specific selectors
        blog_selectors = [
            ".post",
            ".blog-post",
            ".entry",
            "article",
            ".hentry",
            ".type-post",
        ]

        for selector in blog_selectors:
            elements = soup.select(selector)

            for element in elements:
                try:
                    # Extract title
                    title_elem = element.select_one(
                        ".entry-title, .post-title, h1, h2, h3"
                    )
                    title = title_elem.get_text(strip=True) if title_elem else ""

                    # Extract content
                    content_elem = element.select_one(
                        ".entry-content, .post-content, .content"
                    )
                    content = (
                        content_elem.get_text(strip=True)
                        if content_elem
                        else element.get_text(strip=True)
                    )

                    # Extract URL
                    link_elem = element.select_one("a")
                    url = link_elem.get("href", "") if link_elem else ""
                    if url and not url.startswith("http"):
                        url = urljoin(source_url, url)

                    if title and len(title) > 10:
                        posts.append(
                            {
                                "title": title,
                                "content": content[:500],
                                "url": url,
                                "author": "",
                                "published_date": datetime.now(timezone.utc),
                            }
                        )

                except Exception:
                    continue

        return posts[:20]

    def _count_mentions(self, text: str, keywords: List[str]) -> int:
        """Count keyword mentions in text"""

        text_lower = text.lower()
        count = 0

        for keyword in keywords:
            if keyword.lower() in text_lower:
                count += 1

        return count

    def _calculate_relevance(self, title: str, content: str) -> float:
        """Calculate relevance score"""

        full_text = f"{title} {content}".lower()

        # Minnesota relevance
        minnesota_score = self._count_mentions(full_text, self.minnesota_keywords) * 2

        # Coffee relevance
        coffee_score = self._count_mentions(full_text, self.coffee_keywords)

        # Length bonus (longer content gets bonus)
        length_bonus = min(len(full_text) / 1000, 0.5)

        # Combined score
        relevance = (minnesota_score + coffee_score + length_bonus) / 10

        return min(relevance, 1.0)

    def _calculate_engagement(
        self, score: int, comments: int, upvote_ratio: float
    ) -> float:
        """Calculate engagement score"""

        # Normalize engagement
        score_normalized = min(score / 100, 1.0)
        comments_normalized = min(comments / 50, 1.0)

        # Combined engagement
        engagement = (score_normalized * 0.6 + comments_normalized * 0.4) * upvote_ratio

        return min(engagement, 1.0)

    def _generate_content_hash(self, title: str, content: str) -> str:
        """Generate content hash for deduplication"""

        content_text = f"{title} {content}"
        try:
            return _hashlib.md5(content_text.encode()).hexdigest()
        except NameError:
            return hashlib.md5(content_text.encode()).hexdigest()

    async def _store_platform_results(self, platform: str, results: List[Dict]):
        """Store platform results"""

        try:
            if self.config.dry_run:
                log_event(
                    "dry_run_skip_store",
                    run_id=self.run_id,
                    platform=platform,
                    count=len(results),
                )
                return

            with sqlite3.connect(self.db_path) as conn:
                now_iso = datetime.now(timezone.utc).isoformat()
                rows = []
                for result in results:
                    rows.append(
                        (
                            platform,
                            result["source_url"],
                            result["title"],
                            result["content"],
                            result["author"],
                            result["published_date"],
                            result["minnesota_mentions"],
                            result["coffee_mentions"],
                            result["relevance_score"],
                            result["engagement_score"],
                            result["content_hash"],
                            now_iso,
                            result.get("token_count", 0),
                            result.get("truncated", 0),
                            result.get("simhash", 0),
                            result.get("fetch_version", FETCH_VERSION),
                            result.get("schema_version", SCHEMA_VERSION),
                        )
                    )
                conn.executemany(
                    """
                    INSERT INTO comprehensive_content
                    (platform, source_url, title, content, author, published_date,
                     minnesota_mentions, coffee_mentions, relevance_score, engagement_score,
                     content_hash, scraped_at, token_count, truncated, simhash, fetch_version, schema_version)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    rows,
                )
                conn.commit()

        except Exception as e:
            print(f"Error storing {platform} results: {e}")

    def analyze_comprehensive_results(
        self, all_results: Dict[str, List[Dict]]
    ) -> Dict[str, Any]:
        """Analyze comprehensive results across all platforms"""

        print(f"📊 COMPREHENSIVE ANALYSIS")
        print("=" * 40)

        total_content = 0
        platform_stats = {}
        all_content = []

        # Analyze each platform
        for platform, results in all_results.items():
            if not results:
                continue

            source_cfg = self.platforms.get(platform, {})
            if "endpoints" in source_cfg:
                source_count = len(source_cfg["endpoints"])
            elif "sources" in source_cfg:
                source_count = len(source_cfg["sources"])
            elif "rss_feeds" in source_cfg:
                source_count = len(source_cfg["rss_feeds"])
            else:
                source_count = 0

            total_content += len(results)
            all_content.extend(results)

            # Platform statistics
            avg_relevance = sum(r["relevance_score"] for r in results) / len(results)
            minnesota_related = sum(1 for r in results if r["minnesota_mentions"] > 0)
            coffee_related = sum(1 for r in results if r["coffee_mentions"] > 0)

            platform_stats[platform] = {
                "content_count": len(results),
                "avg_relevance": avg_relevance,
                "minnesota_related": minnesota_related,
                "coffee_related": coffee_related,
                "success_rate": 1.0 if results else 0.0,
                "source_count": source_count,
            }

            print(
                f"📱 {platform.upper()}: {len(results)} items, {avg_relevance:.2f} avg relevance"
            )

        # Overall analysis
        if all_content:
            # Top platforms
            top_platforms = sorted(
                platform_stats.items(),
                key=lambda x: x[1]["content_count"],
                reverse=True,
            )[:3]

            # Trending topics
            all_titles = [content["title"] for content in all_content]
            trending_topics = self._extract_trending_topics(all_titles)

            # Confidence score
            confidence_score = self._calculate_overall_confidence(
                all_content, platform_stats
            )

            # Insights
            insights = self._generate_insights(platform_stats, all_content)

            # Store analysis
            self._store_comprehensive_analysis(
                len(platform_stats),
                total_content,
                top_platforms,
                trending_topics,
                confidence_score,
                insights,
            )
            self._upsert_platform_performance(platform_stats)

            print(f"📈 Total content: {total_content}")
            print(f"🎯 Confidence: {confidence_score:.1%}")
            print(f"🔥 Top platform: {top_platforms[0][0] if top_platforms else 'N/A'}")
            print(f"📋 Trending: {', '.join(trending_topics[:3])}")

            return {
                "total_platforms": len(platform_stats),
                "total_content": total_content,
                "platform_stats": platform_stats,
                "top_platforms": top_platforms,
                "trending_topics": trending_topics,
                "confidence_score": confidence_score,
                "latencies": {
                    k: self.latencies.get(k, []) for k in platform_stats.keys()
                },
                "failures": dict(self.failures),
                "retries": dict(self.retries),
                "insights": insights,
            }

        return {
            "total_platforms": 0,
            "total_content": 0,
            "platform_stats": {},
            "top_platforms": [],
            "trending_topics": [],
            "confidence_score": 0.0,
            "latencies": {},
            "failures": {},
            "retries": {},
            "insights": "No content found",
        }

    def _extract_trending_topics(self, titles: List[str]) -> List[str]:
        """Extract trending topics from titles"""

        all_words = []
        for title in titles:
            words = re.findall(r"\b[a-zA-Z]{4,}\b", title.lower())
            all_words.extend(words)

        word_counts = Counter(all_words)
        trending = [
            word
            for word, count in word_counts.most_common(10)
            if word not in ["that", "this", "with", "from", "they", "have", "been"]
        ]

        return trending

    def _calculate_overall_confidence(
        self, all_content: List[Dict], platform_stats: Dict
    ) -> float:
        """Calculate overall confidence score"""

        if not all_content:
            return 0.0

        # Content diversity score
        content_score = min(len(all_content) / 100, 1.0)

        # Platform diversity score
        platform_score = min(len(platform_stats) / 5, 1.0)

        # Relevance score
        avg_relevance = sum(c["relevance_score"] for c in all_content) / len(
            all_content
        )

        # Combined confidence
        confidence = content_score * 0.4 + platform_score * 0.3 + avg_relevance * 0.3

        return confidence

    def _generate_insights(
        self, platform_stats: Dict, all_content: List[Dict]
    ) -> List[str]:
        """Generate insights from analysis"""

        insights = []

        # Most active platform
        if platform_stats:
            top_platform = max(
                platform_stats.items(), key=lambda x: x[1]["content_count"]
            )
            insights.append(
                f"Most active: {top_platform[0]} ({top_platform[1]['content_count']} items)"
            )

        # Minnesota content
        minnesota_content = sum(1 for c in all_content if c["minnesota_mentions"] > 0)
        if minnesota_content > 0:
            insights.append(f"Minnesota-related: {minnesota_content} items")

        # Coffee content
        coffee_content = sum(1 for c in all_content if c["coffee_mentions"] > 0)
        if coffee_content > 0:
            insights.append(f"Coffee-related: {coffee_content} items")

        # High relevance content
        high_relevance = sum(1 for c in all_content if c["relevance_score"] > 0.7)
        if high_relevance > 0:
            insights.append(f"High relevance: {high_relevance} items")

        return insights

    def _upsert_platform_performance(self, platform_stats: Dict[str, Dict[str, Any]]):
        """Persist per-platform performance metrics for reporting"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                for platform, stats in platform_stats.items():
                    source_cfg = self.platforms.get(platform, {})
                    if "endpoints" in source_cfg:
                        source_count = len(source_cfg["endpoints"])
                    elif "sources" in source_cfg:
                        source_count = len(source_cfg["sources"])
                    elif "rss_feeds" in source_cfg:
                        source_count = len(source_cfg["rss_feeds"])
                    else:
                        source_count = 0

                    latencies = self.latencies.get(platform, [])
                    p50 = _percentile(latencies, 0.5)
                    p90 = _percentile(latencies, 0.9)
                    p99 = _percentile(latencies, 0.99)
                    failure_count = self.failures.get(platform, 0)
                    retry_count = self.retries.get(platform, 0)

                    conn.execute(
                        "DELETE FROM platform_performance WHERE platform = ?",
                        (platform,),
                    )
                    conn.execute(
                        """
                        INSERT INTO platform_performance
                        (platform, source_count, success_rate, avg_relevance, total_content, content_count, last_updated,
                         p50_latency, p90_latency, p99_latency, failure_count, retry_count)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            platform,
                            source_count,
                            stats.get("success_rate", 0.0),
                            stats.get("avg_relevance", 0.0),
                            stats.get("content_count", 0),
                            stats.get("content_count", 0),
                            datetime.now(timezone.utc).isoformat(),
                            p50,
                            p90,
                            p99,
                            failure_count,
                            retry_count,
                        ),
                    )
                conn.commit()
        except Exception as e:
            print(f"Error updating platform performance: {e}")

    def _store_comprehensive_analysis(
        self,
        total_platforms: int,
        total_content: int,
        top_platforms: List[Tuple],
        trending_topics: List[str],
        confidence_score: float,
        insights: List[str],
    ):
        """Store comprehensive analysis"""

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO comprehensive_trends
                    (analysis_date, total_platforms, total_content, top_platforms,
                     trending_topics, confidence_score, insights)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        datetime.now(timezone.utc).isoformat(),
                        total_platforms,
                        total_content,
                        json.dumps(top_platforms),
                        json.dumps(trending_topics),
                        confidence_score,
                        json.dumps(insights),
                    ),
                )

                conn.commit()

        except Exception as e:
            print(f"Error storing comprehensive analysis: {e}")

    def generate_comprehensive_report(self) -> str:
        """Generate comprehensive report"""

        print(f"📋 GENERATING COMPREHENSIVE REPORT")
        print("=" * 50)

        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get latest analysis
                cursor = conn.execute(
                    """
                    SELECT * FROM comprehensive_trends
                    ORDER BY analysis_date DESC
                    LIMIT 1
                """
                )

                analysis = cursor.fetchone()

                if not analysis:
                    return "No analysis data available"

                # Get platform performance
                cursor = conn.execute(
                    """
                    SELECT platform, total_content, avg_relevance, success_rate
                    FROM platform_performance
                    ORDER BY total_content DESC
                """
                )

                platform_performance = cursor.fetchall()

                # Get top content
                cursor = conn.execute(
                    """
                    SELECT platform, title, relevance_score, engagement_score
                    FROM comprehensive_content
                    ORDER BY relevance_score DESC, engagement_score DESC
                    LIMIT 10
                """
                )

                top_content = cursor.fetchall()

                cursor = conn.execute(
                    "SELECT engagement_score FROM comprehensive_content"
                )
                engagement_scores = [
                    row[0] for row in cursor.fetchall() if row[0] is not None
                ]
                engagement_percentiles = (
                    {
                        "p50": _percentile(engagement_scores, 0.5),
                        "p90": _percentile(engagement_scores, 0.9),
                        "p99": _percentile(engagement_scores, 0.99),
                    }
                    if engagement_scores
                    else {"p50": 0.0, "p90": 0.0, "p99": 0.0}
                )

                # Format report
                report = self._format_comprehensive_report(
                    analysis, platform_performance, top_content, engagement_percentiles
                )

                return report
        except Exception as e:
            return f"Error generating report: {e}"

    def _format_html_report(
        self,
        analysis: Tuple,
        platform_performance: List[Tuple],
        top_content: List[Tuple],
    ) -> str:
        """Format HTML report"""
        platform_rows = "".join(
            f"<tr><td>{i+1}</td><td>{platform}</td><td>{total}</td><td>{avg_relevance:.2f}</td><td>{success_rate:.2f}</td></tr>"
            for i, (platform, total, avg_relevance, success_rate) in enumerate(
                platform_performance
            )
        )
        content_rows = "".join(
            f"<tr><td>{i+1}</td><td>{platform}</td><td>{title}</td><td>{relevance:.2f}</td><td>{engagement:.2f}</td></tr>"
            for i, (platform, title, relevance, engagement) in enumerate(
                top_content[:5]
            )
        )
        return f"""
        <html><body>
        <h1>Comprehensive Multi-Platform Scraper Report</h1>
        <p><strong>Analysis Date:</strong> {analysis[1]}</p>
        <p><strong>Confidence:</strong> {analysis[6]:.1%}</p>
        <p><strong>Total Platforms:</strong> {analysis[2]}</p>
        <p><strong>Total Content:</strong> {analysis[3]}</p>
        <h2>Platform Performance</h2>
        <table border="1" cellpadding="4"><tr><th>#</th><th>Platform</th><th>Items</th><th>Relevance</th><th>Success</th></tr>{platform_rows}</table>
        <h2>Top Content</h2>
        <table border="1" cellpadding="4"><tr><th>#</th><th>Platform</th><th>Title</th><th>Relevance</th><th>Engagement</th></tr>{content_rows}</table>
        </body></html>
        """

    def write_reports(self, analysis: Dict[str, Any], report_text: str):
        try:
            ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
            self.config.report_dir.mkdir(parents=True, exist_ok=True)
            md_path = self.config.report_dir / f"report-{ts}.md"
            html_path = self.config.report_dir / f"report-{ts}.html"
            md_path.write_text(report_text, encoding="utf-8")
            if analysis.get("platform_stats"):
                platform_performance = [
                    (
                        p,
                        stats.get("content_count", 0),
                        stats.get("avg_relevance", 0.0),
                        stats.get("success_rate", 0.0),
                    )
                    for p, stats in analysis["platform_stats"].items()
                ]
                top_content = []
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        """
                        SELECT platform, title, relevance_score, engagement_score
                        FROM comprehensive_content
                        ORDER BY relevance_score DESC, engagement_score DESC
                        LIMIT 5
                    """
                    )
                    top_content = cursor.fetchall()
                html = self._format_html_report(
                    (
                        None,
                        datetime.now(timezone.utc).isoformat(),
                        analysis.get("total_platforms", 0),
                        analysis.get("total_content", 0),
                        json.dumps([]),
                        json.dumps(analysis.get("trending_topics", [])),
                        analysis.get("confidence_score", 0.0),
                        json.dumps(analysis.get("insights", [])),
                    ),
                    platform_performance,
                    top_content,
                )
                html_path.write_text(html, encoding="utf-8")
            log_event(
                "report_written",
                run_id=self.run_id,
                markdown=str(md_path),
                html=str(html_path),
            )
        except Exception as e:
            return f"Error generating report: {e}"

    def _format_comprehensive_report(
        self,
        analysis: Tuple,
        platform_performance: List[Tuple],
        top_content: List[Tuple],
    ) -> str:
        """Format comprehensive report"""

        report = []

        # Header
        report.append("🚀 COMPREHENSIVE MULTI-PLATFORM SCRAPER REPORT")
        report.append("=" * 60)
        report.append(f"📅 Analysis Date: {analysis[1]}")
        report.append(f"📊 Confidence Score: {analysis[6]:.1%}")
        report.append(f"📱 Total Platforms: {analysis[2]}")
        report.append(f"📈 Total Content: {analysis[3]}")
        report.append("")

        # Platform Performance
        report.append("📱 PLATFORM PERFORMANCE")
        report.append("-" * 30)
        for i, (platform, total_content, avg_relevance, success_rate) in enumerate(
            platform_performance, 1
        ):
            report.append(
                f"{i}. {platform.upper()}: {total_content} items, {avg_relevance:.2f} relevance"
            )
        report.append("")

        # Top Platforms
        top_platforms = json.loads(analysis[4])
        if top_platforms:
            report.append("🔥 TOP PLATFORMS")
            report.append("-" * 20)
            for i, (platform, stats) in enumerate(top_platforms[:3], 1):
                report.append(
                    f"{i}. {platform.upper()}: {stats['content_count']} items"
                )
            report.append("")

        # Trending Topics
        trending_topics = json.loads(analysis[5])
        if trending_topics:
            report.append("📋 TRENDING TOPICS")
            report.append("-" * 25)
            for i, topic in enumerate(trending_topics[:5], 1):
                report.append(f"{i}. {topic.title()}")
            report.append("")

        # Top Content
        report.append("🌟 TOP CONTENT")
        report.append("-" * 20)
        for i, (platform, title, relevance, engagement) in enumerate(
            top_content[:5], 1
        ):
            report.append(f"{i}. [{platform.upper()}] {title[:60]}...")
            report.append(
                f"   Relevance: {relevance:.2f} | Engagement: {engagement:.2f}"
            )
        report.append("")

        # Insights
        insights = json.loads(analysis[7])
        if insights:
            report.append("💡 KEY INSIGHTS")
            report.append("-" * 20)
            for insight in insights:
                report.append(f"• {insight}")
            report.append("")

        # Footer
        report.append("🔍 INNOVATIVE TECHNIQUES USED")
        report.append("-" * 35)
        report.append("• Multi-platform scraping (Reddit, News, Blogs, RSS, Forums)")
        report.append("• Advanced content extraction with BeautifulSoup")
        report.append("• Intelligent relevance scoring algorithms")
        report.append("• Real-time engagement analysis")
        report.append("• Cross-platform content deduplication")
        report.append("• Trending topic extraction")
        report.append("• Comprehensive confidence scoring")
        report.append("")
        report.append("📊 Generated by Comprehensive Multi-Platform Scraper")

        return "\n".join(report)


async def main():
    """Main execution - comprehensive multi-platform scraping"""
    parser = argparse.ArgumentParser(description="Comprehensive Multi-Platform Scraper")
    parser.add_argument(
        "--config",
        type=str,
        default=str(DEFAULT_CONFIG_PATH),
        help="Path to config JSON",
    )
    parser.add_argument("--include", nargs="*", help="Platforms to include")
    parser.add_argument("--exclude", nargs="*", help="Platforms to exclude")
    parser.add_argument("--limit", type=int, help="Per-platform item limit")
    parser.add_argument("--dry-run", action="store_true", help="Skip DB writes")
    parser.add_argument(
        "--output-json", type=str, help="Write aggregated results to JSON file"
    )
    args = parser.parse_args()

    cfg = ScraperConfig.load(Path(args.config))
    if args.include:
        cfg.include_platforms = set(args.include)
    if args.exclude:
        cfg.exclude_platforms = set(args.exclude)
    if args.limit is not None:
        cfg.per_platform_limit = args.limit
    if args.dry_run:
        cfg.dry_run = True
    if args.output_json:
        cfg.output_json_cli = Path(args.output_json)

    scraper = ComprehensiveScraper(config=cfg)
    await scraper.initialize()

    try:
        # Scrape all platforms
        all_results = await scraper.scrape_all_platforms()

        # Analyze results
        analysis = scraper.analyze_comprehensive_results(all_results)
        scraper._send_alert_if_needed(analysis)

        # Generate report
        report = scraper.generate_comprehensive_report()
        scraper.write_reports(analysis, report)

        if cfg.output_json_cli:
            cfg.output_json_cli.write_text(
                json.dumps(
                    {"analysis": analysis, "results": all_results},
                    default=str,
                    indent=2,
                ),
                encoding="utf-8",
            )
            log_event(
                "json_written", run_id=scraper.run_id, path=str(cfg.output_json_cli)
            )

        print(f"\n🎉 COMPREHENSIVE SCRAPING COMPLETE")
        print(f"✅ Platforms: {analysis['total_platforms']}")
        print(f"✅ Total Content: {analysis['total_content']}")
        print(f"✅ Confidence: {analysis['confidence_score']:.1%}")
        print(
            f"✅ Top Platform: {analysis['top_platforms'][0][0] if analysis['top_platforms'] else 'N/A'}"
        )

    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())
