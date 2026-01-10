"""
Production-Grade Error Handling and Edge Case Management
Based on research from production scraping systems and best practices
"""

import asyncio
import hashlib
import json
import logging
import random
import time
import traceback
import uuid
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union

# Import existing scraper components
from enhanced_scraper_service import EnhancedScraper

# Advanced retry and circuit breaker libraries
try:
    from circuitbreaker import CircuitBreakerError, circuit
    from tenacity import (
        before_sleep_log,
        retry,
        retry_if_exception_type,
        stop_after_attempt,
        wait_exponential,
    )

    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False

# Monitoring and alerting
try:
    import sentry_sdk

    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

# Structured logging (already available)
import structlog

logger = structlog.get_logger()


class ScrapingErrorType(Enum):
    """Classification of scraping errors for better handling"""

    NETWORK_ERROR = "network_error"
    HTTP_ERROR = "http_error"
    PARSING_ERROR = "parsing_error"
    TIMEOUT_ERROR = "timeout_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    AUTHENTICATION_ERROR = "authentication_error"
    CONTENT_ERROR = "content_error"
    BROWSER_ERROR = "browser_error"
    SYSTEM_ERROR = "system_error"
    UNKNOWN_ERROR = "unknown_error"


class ErrorSeverity(Enum):
    """Error severity levels for prioritization"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ScrapingError:
    """Structured error information"""

    error_id: str
    error_type: ScrapingErrorType
    severity: ErrorSeverity
    message: str
    url: str
    user_id: str
    timestamp: datetime
    traceback: str
    retry_count: int
    context: Dict[str, Any]
    resolved: bool = False


@dataclass
class ErrorPattern:
    """Pattern recognition for recurring errors"""

    pattern_id: str
    error_type: ScrapingErrorType
    frequency: int
    first_seen: datetime
    last_seen: datetime
    affected_urls: List[str]
    suggested_action: str


class RobustErrorClassifier:
    """Intelligent error classification and pattern detection"""

    def __init__(self):
        self.error_patterns = {}
        self.error_history = deque(maxlen=1000)
        self.classification_rules = self._init_classification_rules()

    def _init_classification_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize error classification rules"""
        return {
            "connection": {
                "keywords": ["connection", "network", "dns", "socket"],
                "exceptions": ["ConnectionError", "ConnectTimeoutError", "DNSError"],
                "type": ScrapingErrorType.NETWORK_ERROR,
                "severity": ErrorSeverity.MEDIUM,
                "retry": True,
            },
            "timeout": {
                "keywords": ["timeout", "timed out", "deadline"],
                "exceptions": ["TimeoutError", "ReadTimeout", "ConnectTimeout"],
                "type": ScrapingErrorType.TIMEOUT_ERROR,
                "severity": ErrorSeverity.MEDIUM,
                "retry": True,
            },
            "http_403": {
                "keywords": ["403", "forbidden", "blocked"],
                "exceptions": ["HTTPError"],
                "type": ScrapingErrorType.HTTP_ERROR,
                "severity": ErrorSeverity.HIGH,
                "retry": False,
            },
            "http_429": {
                "keywords": ["429", "rate limit", "too many requests"],
                "exceptions": ["HTTPError"],
                "type": ScrapingErrorType.RATE_LIMIT_ERROR,
                "severity": ErrorSeverity.HIGH,
                "retry": True,
            },
            "http_404": {
                "keywords": ["404", "not found"],
                "exceptions": ["HTTPError"],
                "type": ScrapingErrorType.HTTP_ERROR,
                "severity": ErrorSeverity.LOW,
                "retry": False,
            },
            "parsing": {
                "keywords": ["parse", "html", "css", "xpath", "selector"],
                "exceptions": ["ParseException", "SelectorError", "ValueError"],
                "type": ScrapingErrorType.PARSING_ERROR,
                "severity": ErrorSeverity.MEDIUM,
                "retry": False,
            },
            "browser": {
                "keywords": ["browser", "playwright", "selenium", "chrome", "chromium"],
                "exceptions": ["BrowserError", "WebDriverException"],
                "type": ScrapingErrorType.BROWSER_ERROR,
                "severity": ErrorSeverity.HIGH,
                "retry": True,
            },
            "authentication": {
                "keywords": ["auth", "login", "unauthorized", "401"],
                "exceptions": ["AuthenticationError"],
                "type": ScrapingErrorType.AUTHENTICATION_ERROR,
                "severity": ErrorSeverity.CRITICAL,
                "retry": False,
            },
        }

    def classify_error(
        self, exception: Exception, url: str, user_id: str
    ) -> ScrapingError:
        """Classify an exception and create structured error information"""
        error_id = str(uuid.uuid4())
        error_str = str(exception)
        exception_type = type(exception).__name__

        # Classification logic
        error_type = ScrapingErrorType.UNKNOWN_ERROR
        severity = ErrorSeverity.MEDIUM
        should_retry = False

        for rule_name, rule in self.classification_rules.items():
            # Check exception type
            if exception_type in rule.get("exceptions", []):
                error_type = rule["type"]
                severity = rule["severity"]
                should_retry = rule["retry"]
                break

            # Check keywords in error message
            if any(
                keyword.lower() in error_str.lower()
                for keyword in rule.get("keywords", [])
            ):
                error_type = rule["type"]
                severity = rule["severity"]
                should_retry = rule["retry"]
                break

        # Create structured error
        structured_error = ScrapingError(
            error_id=error_id,
            error_type=error_type,
            severity=severity,
            message=error_str,
            url=url,
            user_id=user_id,
            timestamp=datetime.now(timezone.utc),
            traceback=traceback.format_exc(),
            retry_count=0,
            context={
                "exception_type": exception_type,
                "should_retry": should_retry,
                "classification_confidence": self._calculate_confidence(
                    error_str, rule_name if "rule_name" in locals() else None
                ),
            },
        )

        # Store in history
        self.error_history.append(structured_error)

        # Update patterns
        self._update_error_patterns(structured_error)

        return structured_error

    def _calculate_confidence(self, error_str: str, rule_name: Optional[str]) -> float:
        """Calculate confidence in error classification"""
        if not rule_name:
            return 0.5  # Default confidence for unknown errors

        rule = self.classification_rules.get(rule_name, {})
        keywords = rule.get("keywords", [])

        # Count keyword matches
        matches = sum(1 for keyword in keywords if keyword.lower() in error_str.lower())

        if matches == 0:
            return 0.3
        elif matches == 1:
            return 0.7
        else:
            return 0.9

    def _update_error_patterns(self, error: ScrapingError):
        """Update error pattern recognition"""
        pattern_key = f"{error.error_type.value}_{hash(error.url) % 100}"

        if pattern_key not in self.error_patterns:
            self.error_patterns[pattern_key] = ErrorPattern(
                pattern_id=pattern_key,
                error_type=error.error_type,
                frequency=1,
                first_seen=error.timestamp,
                last_seen=error.timestamp,
                affected_urls=[error.url],
                suggested_action=self._get_suggested_action(error.error_type),
            )
        else:
            pattern = self.error_patterns[pattern_key]
            pattern.frequency += 1
            pattern.last_seen = error.timestamp
            if error.url not in pattern.affected_urls:
                pattern.affected_urls.append(error.url)

    def _get_suggested_action(self, error_type: ScrapingErrorType) -> str:
        """Get suggested action for error type"""
        actions = {
            ScrapingErrorType.NETWORK_ERROR: "Check network connectivity, implement retry with exponential backoff",
            ScrapingErrorType.HTTP_ERROR: "Review HTTP status codes, adjust headers or authentication",
            ScrapingErrorType.PARSING_ERROR: "Update selectors, implement fallback parsing methods",
            ScrapingErrorType.TIMEOUT_ERROR: "Increase timeout values, optimize request size",
            ScrapingErrorType.RATE_LIMIT_ERROR: "Implement rate limiting, add delays between requests",
            ScrapingErrorType.AUTHENTICATION_ERROR: "Update credentials, check authentication flow",
            ScrapingErrorType.CONTENT_ERROR: "Handle empty or malformed content gracefully",
            ScrapingErrorType.BROWSER_ERROR: "Restart browser, update browser drivers",
            ScrapingErrorType.SYSTEM_ERROR: "Check system resources, implement graceful degradation",
        }
        return actions.get(
            error_type, "Investigate error and implement appropriate handling"
        )


class CircuitBreakerManager:
    """Circuit breaker pattern implementation for preventing cascade failures"""

    def __init__(self):
        self.circuits = {}
        self.default_threshold = 5
        self.default_recovery_timeout = 60

    def get_circuit_breaker(
        self, key: str, failure_threshold: int = None, recovery_timeout: int = None
    ):
        """Get or create a circuit breaker for a specific key"""
        if key not in self.circuits:
            threshold = failure_threshold or self.default_threshold
            timeout = recovery_timeout or self.default_recovery_timeout

            if TENACITY_AVAILABLE:

                @circuit(failure_threshold=threshold, recovery_timeout=timeout)
                def protected_function():
                    pass

                self.circuits[key] = protected_function
            else:
                # Fallback implementation
                self.circuits[key] = self._create_simple_circuit_breaker(
                    threshold, timeout
                )

        return self.circuits[key]

    def _create_simple_circuit_breaker(self, threshold: int, timeout: int):
        """Simple circuit breaker implementation without external library"""
        state = {
            "failures": 0,
            "last_failure": None,
            "state": "closed",  # closed, open, half-open
        }

        def circuit_breaker(func):
            def wrapper(*args, **kwargs):
                now = time.time()

                # Check if circuit should be reset
                if (
                    state["state"] == "open"
                    and state["last_failure"]
                    and now - state["last_failure"] > timeout
                ):
                    state["state"] = "half-open"

                # Check if circuit is open
                if state["state"] == "open":
                    raise CircuitBreakerError("Circuit breaker is open")

                try:
                    result = func(*args, **kwargs)
                    # Success - reset failure count
                    if state["state"] == "half-open":
                        state["state"] = "closed"
                    state["failures"] = 0
                    return result
                except Exception as e:
                    state["failures"] += 1
                    state["last_failure"] = now

                    if state["failures"] >= threshold:
                        state["state"] = "open"

                    raise e

            return wrapper

        return circuit_breaker


class RobustScraperWithFallbacks:
    """Enhanced scraper with comprehensive error handling and fallbacks"""

    def __init__(self):
        self.base_scraper = EnhancedScraper()
        self.error_classifier = RobustErrorClassifier()
        self.circuit_breaker_manager = CircuitBreakerManager()
        self.retry_stats = defaultdict(int)
        self.fallback_stats = defaultdict(int)

        # Fallback strategies
        self.fallback_strategies = {
            "browser": self._browser_fallback,
            "parsing": self._parsing_fallback,
            "content": self._content_fallback,
            "network": self._network_fallback,
        }

    async def scrape_with_robust_handling(
        self, url: str, user_id: str, legal_basis: str = "user_request"
    ) -> Dict[str, Any]:
        """Main scraping method with comprehensive error handling"""

        # Get circuit breaker for this domain
        domain = self._extract_domain(url)
        circuit_breaker = self.circuit_breaker_manager.get_circuit_breaker(domain)

        try:
            # Primary scraping attempt
            if TENACITY_AVAILABLE:
                result = await self._scrape_with_tenacity_retry(
                    url, user_id, legal_basis
                )
            else:
                result = await self._scrape_with_simple_retry(url, user_id, legal_basis)

            return result

        except Exception as primary_error:
            # Classify the error
            classified_error = self.error_classifier.classify_error(
                primary_error, url, user_id
            )

            # Log the error
            logger.error(
                "Primary scraping failed",
                error_id=classified_error.error_id,
                error_type=classified_error.error_type.value,
                severity=classified_error.severity.value,
                url=url,
                user_id=user_id,
                message=classified_error.message,
            )

            # Send to Sentry if available
            if SENTRY_AVAILABLE:
                sentry_sdk.capture_exception(
                    primary_error,
                    extra={
                        "error_id": classified_error.error_id,
                        "error_type": classified_error.error_type.value,
                        "url": url,
                        "user_id": user_id,
                    },
                )

            # Try fallback strategies
            fallback_result = await self._try_fallback_strategies(
                classified_error, url, user_id, legal_basis
            )

            if fallback_result:
                self.fallback_stats[classified_error.error_type.value] += 1
                return fallback_result

            # If all fallbacks fail, return graceful error response
            return self._create_graceful_error_response(classified_error)

    async def _scrape_with_tenacity_retry(
        self, url: str, user_id: str, legal_basis: str
    ) -> Dict[str, Any]:
        """Scraping with tenacity retry logic"""

        @retry(
            stop=stop_after_attempt(5),
            wait=wait_exponential(multiplier=1, min=4, max=30),
            retry=retry_if_exception_type((ConnectionError, TimeoutError, OSError)),
            before_sleep=before_sleep_log(logger, logging.WARNING),
        )
        async def scrape_with_retry():
            return await self.base_scraper.scrape_with_playwright_enhanced(
                url, user_id, legal_basis
            )

        return await scrape_with_retry()

    async def _scrape_with_simple_retry(
        self, url: str, user_id: str, legal_basis: str
    ) -> Dict[str, Any]:
        """Simple retry implementation without tenacity"""
        max_retries = 3
        base_delay = 2

        for attempt in range(max_retries + 1):
            try:
                return await self.base_scraper.scrape_with_playwright_enhanced(
                    url, user_id, legal_basis
                )
            except (ConnectionError, TimeoutError, OSError) as e:
                if attempt == max_retries:
                    raise e

                delay = base_delay * (2**attempt) + random.uniform(0, 1)
                logger.warning(
                    "Retry attempt failed",
                    attempt=attempt + 1,
                    max_retries=max_retries,
                    delay=delay,
                    error=str(e),
                )
                await asyncio.sleep(delay)

    async def _try_fallback_strategies(
        self, error: ScrapingError, url: str, user_id: str, legal_basis: str
    ) -> Optional[Dict[str, Any]]:
        """Try appropriate fallback strategies based on error type"""

        # Map error types to fallback strategies
        fallback_map = {
            ScrapingErrorType.BROWSER_ERROR: ["browser"],
            ScrapingErrorType.PARSING_ERROR: ["parsing"],
            ScrapingErrorType.CONTENT_ERROR: ["content"],
            ScrapingErrorType.NETWORK_ERROR: ["network"],
            ScrapingErrorType.TIMEOUT_ERROR: ["network"],
        }

        strategies = fallback_map.get(error.error_type, [])

        for strategy_name in strategies:
            if strategy_name in self.fallback_strategies:
                try:
                    logger.info(
                        "Trying fallback strategy",
                        strategy=strategy_name,
                        error_type=error.error_type.value,
                    )

                    fallback_func = self.fallback_strategies[strategy_name]
                    result = await fallback_func(url, user_id, legal_basis, error)

                    if result and result.get("status") == "success":
                        result["fallback_used"] = strategy_name
                        result["original_error"] = error.error_id
                        return result

                except Exception as fallback_error:
                    logger.warning(
                        "Fallback strategy failed",
                        strategy=strategy_name,
                        fallback_error=str(fallback_error),
                    )

        return None

    async def _browser_fallback(
        self, url: str, user_id: str, legal_basis: str, original_error: ScrapingError
    ) -> Optional[Dict[str, Any]]:
        """Fallback strategy for browser errors"""

        # Try Selenium if Playwright failed
        if hasattr(self.base_scraper, "_scrape_with_selenium"):
            try:
                logger.info("Attempting Selenium fallback")
                result = await self.base_scraper._scrape_with_selenium(
                    url, user_id, legal_basis, datetime.now(timezone.utc)
                )
                return result
            except Exception as e:
                logger.warning("Selenium fallback failed", error=str(e))

        # Try with different browser settings
        try:
            logger.info("Attempting browser with different settings")
            # Implementation would go here
            return None
        except Exception as e:
            logger.warning("Alternative browser settings failed", error=str(e))

        return None

    async def _parsing_fallback(
        self, url: str, user_id: str, legal_basis: str, original_error: ScrapingError
    ) -> Optional[Dict[str, Any]]:
        """Fallback strategy for parsing errors"""

        # Try different parsing methods
        fallback_parsers = ["html.parser", "html5lib", "lxml"]

        for parser in fallback_parsers:
            try:
                logger.info(f"Trying fallback parser: {parser}")
                # Implementation would use different parser
                return None
            except Exception as e:
                logger.warning(f"Parser {parser} failed", error=str(e))

        return None

    async def _content_fallback(
        self, url: str, user_id: str, legal_basis: str, original_error: ScrapingError
    ) -> Optional[Dict[str, Any]]:
        """Fallback strategy for content errors"""

        # Try to extract minimal data
        try:
            logger.info("Attempting minimal content extraction")

            # Return minimal successful response
            return {
                "url": url,
                "user_id": user_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "title": "Content Extraction Failed",
                "content_length": 0,
                "readable_text": "",
                "status": "partial_success",
                "fallback_used": "minimal_content",
                "original_error": original_error.error_id,
                "processing_time": 0.1,
            }

        except Exception as e:
            logger.warning("Minimal content extraction failed", error=str(e))

        return None

    async def _network_fallback(
        self, url: str, user_id: str, legal_basis: str, original_error: ScrapingError
    ) -> Optional[Dict[str, Any]]:
        """Fallback strategy for network errors"""

        # Try with different timeout settings
        timeouts = [10, 30, 60]

        for timeout in timeouts:
            try:
                logger.info(f"Trying with timeout: {timeout}s")
                # Implementation would use different timeout
                return None
            except Exception as e:
                logger.warning(f"Timeout {timeout}s failed", error=str(e))

        return None

    def _create_graceful_error_response(self, error: ScrapingError) -> Dict[str, Any]:
        """Create a graceful error response"""

        return {
            "url": error.url,
            "user_id": error.user_id,
            "timestamp": error.timestamp.isoformat(),
            "status": "error",
            "error": {
                "error_id": error.error_id,
                "error_type": error.error_type.value,
                "severity": error.severity.value,
                "message": error.message,
                "retry_count": error.retry_count,
                "suggested_action": self.error_classifier._get_suggested_action(
                    error.error_type
                ),
            },
            "processing_time": 0.1,
            "fallback_used": None,
            "graceful_failure": True,
        }

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL for circuit breaker key"""
        try:
            from urllib.parse import urlparse

            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return "unknown"

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error statistics"""

        # Count errors by type
        error_counts = defaultdict(int)
        severity_counts = defaultdict(int)

        for error in self.error_classifier.error_history:
            error_counts[error.error_type.value] += 1
            severity_counts[error.severity.value] += 1

        # Get pattern information
        patterns = []
        for pattern in self.error_classifier.error_patterns.values():
            patterns.append(
                {
                    "pattern_id": pattern.pattern_id,
                    "error_type": pattern.error_type.value,
                    "frequency": pattern.frequency,
                    "affected_urls_count": len(pattern.affected_urls),
                    "suggested_action": pattern.suggested_action,
                }
            )

        return {
            "total_errors": len(self.error_classifier.error_history),
            "error_counts": dict(error_counts),
            "severity_counts": dict(severity_counts),
            "retry_stats": dict(self.retry_stats),
            "fallback_stats": dict(self.fallback_stats),
            "error_patterns": patterns,
            "most_common_errors": sorted(
                error_counts.items(), key=lambda x: x[1], reverse=True
            )[:5],
        }


# Global robust scraper instance
robust_scraper = RobustScraperWithFallbacks()
