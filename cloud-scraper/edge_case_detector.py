"""
Edge Case Detection and Prevention System
Identifies and handles edge cases before they become failures
"""

import asyncio
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

# Import existing components
from robust_error_handling import ErrorSeverity, ScrapingErrorType


@dataclass
class EdgeCase:
    """Edge case definition and handling strategy"""

    case_id: str
    name: str
    description: str
    detection_patterns: List[str]
    severity: ErrorSeverity
    prevention_strategy: str
    handling_strategy: str
    examples: List[str]


class EdgeCaseDetector:
    """Detects and prevents edge cases in web scraping"""

    def __init__(self):
        self.edge_cases = self._initialize_edge_cases()
        self.url_patterns = self._compile_patterns()
        self.detection_history = []

    def _initialize_edge_cases(self) -> Dict[str, EdgeCase]:
        """Initialize known edge cases"""
        return {
            "infinite_scroll": EdgeCase(
                case_id="infinite_scroll",
                name="Infinite Scroll Detection",
                description="Websites with infinite scroll that can cause endless scraping",
                detection_patterns=[r"scroll", r"lazy", r"load-more", r"infinite"],
                severity=ErrorSeverity.MEDIUM,
                prevention_strategy="Limit scroll depth and time",
                handling_strategy="Implement scroll limits and timeout mechanisms",
                examples=["twitter.com", "facebook.com", "instagram.com"],
            ),
            "single_page_app": EdgeCase(
                case_id="single_page_app",
                name="Single Page Application",
                description="SPAs that load content dynamically without page reloads",
                detection_patterns=[r"react", r"angular", r"vue", r"spa", r"#/"],
                severity=ErrorSeverity.MEDIUM,
                prevention_strategy="Wait for dynamic content loading",
                handling_strategy="Use browser automation with wait conditions",
                examples=["gmail.com", "trello.com", "notion.so"],
            ),
            "anti_bot_protection": EdgeCase(
                case_id="anti_bot_protection",
                name="Anti-Bot Protection Systems",
                description="Advanced bot detection and protection mechanisms",
                detection_patterns=[
                    r"cloudflare",
                    r"akamai",
                    r"incapsula",
                    r"perimeterx",
                ],
                severity=ErrorSeverity.HIGH,
                prevention_strategy="Mimic real browser behavior",
                handling_strategy="Use undetected browsers and rotate user agents",
                examples=["linkedin.com", "instagram.com", "booking.com"],
            ),
            "login_required": EdgeCase(
                case_id="login_required",
                name="Authentication Required",
                description="Content behind authentication walls",
                detection_patterns=[r"login", r"signin", r"authenticate", r"401"],
                severity=ErrorSeverity.HIGH,
                prevention_strategy="Check for authentication requirements",
                handling_strategy="Implement authentication flow or skip gated content",
                examples=["facebook.com", "gmail.com", "netflix.com"],
            ),
            "geo_restricted": EdgeCase(
                case_id="geo_restricted",
                name="Geographic Restrictions",
                description="Content restricted by geographic location",
                detection_patterns=[r"geo", r"region", r"location", r"country"],
                severity=ErrorSeverity.MEDIUM,
                prevention_strategy="Use proxy rotation or VPN",
                handling_strategy="Implement geo-location bypass or respect restrictions",
                examples=["youtube.com", "netflix.com", "hulu.com"],
            ),
            "rate_limited": EdgeCase(
                case_id="rate_limited",
                name="Rate Limiting",
                description="Sites with strict rate limiting",
                detection_patterns=[r"429", r"rate.limit", r"too.many", r"throttle"],
                severity=ErrorSeverity.HIGH,
                prevention_strategy="Implement intelligent rate limiting",
                handling_strategy="Use exponential backoff and request queuing",
                examples=["twitter.com", "google.com", "github.com"],
            ),
            "large_content": EdgeCase(
                case_id="large_content",
                name="Large Content Pages",
                description="Pages with excessive content size",
                detection_patterns=[r"large", r"huge", r"massive", r"big"],
                severity=ErrorSeverity.MEDIUM,
                prevention_strategy="Check content size before processing",
                handling_strategy="Implement content size limits and pagination",
                examples=["wikipedia.org", "reddit.com", "news sites"],
            ),
            "malformed_html": EdgeCase(
                case_id="malformed_html",
                name="Malformed HTML",
                description="Invalid or broken HTML structure",
                detection_patterns=[r"html.error", r"malformed", r"invalid"],
                severity=ErrorSeverity.LOW,
                prevention_strategy="Use lenient HTML parsers",
                handling_strategy="Implement multiple parsing fallbacks",
                examples=["old websites", "broken sites", "legacy systems"],
            ),
            "cookie_consent": EdgeCase(
                case_id="cookie_consent",
                name="Cookie Consent Overlays",
                description="Cookie consent banners blocking content",
                detection_patterns=[r"cookie", r"consent", r"gdpr", r"privacy"],
                severity=ErrorSeverity.LOW,
                prevention_strategy="Detect and handle cookie banners",
                handling_strategy="Auto-accept or dismiss consent dialogs",
                examples=["eu websites", "news sites", "ecommerce"],
            ),
            "captcha_challenge": EdgeCase(
                case_id="captcha_challenge",
                name="CAPTCHA Challenges",
                description="CAPTCHA or human verification challenges",
                detection_patterns=[r"captcha", r"challenge", r"verify", r"human"],
                severity=ErrorSeverity.HIGH,
                prevention_strategy="Avoid triggering CAPTCHAs",
                handling_strategy="Implement CAPTCHA solving or skip challenges",
                examples=["google.com", "recaptcha sites", "protection systems"],
            ),
            "javascript_heavy": EdgeCase(
                case_id="javascript_heavy",
                name="JavaScript Heavy Sites",
                description="Sites requiring extensive JavaScript execution",
                detection_patterns=[r"javascript", r"js", r"dynamic", r"ajax"],
                severity=ErrorSeverity.MEDIUM,
                prevention_strategy="Check for JS requirements",
                handling_strategy="Use headless browsers with proper wait conditions",
                examples=["spa applications", "modern websites", "web apps"],
            ),
            "session_based": EdgeCase(
                case_id="session_based",
                name="Session-Based Content",
                description="Content requiring session management",
                detection_patterns=[r"session", r"token", r"csrf", r"auth"],
                severity=ErrorSeverity.MEDIUM,
                prevention_strategy="Check for session requirements",
                handling_strategy="Implement session management and token handling",
                examples=["banking sites", "applications", "secure portals"],
            ),
            "mobile_redirect": EdgeCase(
                case_id="mobile_redirect",
                name="Mobile Redirect Issues",
                description="Sites that redirect mobile users",
                detection_patterns=[r"mobile", r"m\.", r"redirect", r"user.agent"],
                severity=ErrorSeverity.LOW,
                prevention_strategy="Use desktop user agents",
                handling_strategy="Handle redirects and maintain user agent consistency",
                examples=["responsive sites", "mobile-first sites"],
            ),
            "api_based": EdgeCase(
                case_id="api_based",
                name="API-Based Content Loading",
                description="Content loaded via API calls",
                detection_patterns=[r"api", r"ajax", r"xhr", r"fetch"],
                severity=ErrorSeverity.MEDIUM,
                prevention_strategy="Detect API usage patterns",
                handling_strategy="Monitor network calls and replicate API requests",
                examples=["spa applications", "modern sites", "dynamic content"],
            ),
        }

    def _compile_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Compile regex patterns for efficient matching"""
        compiled_patterns = {}

        for case_id, edge_case in self.edge_cases.items():
            compiled_patterns[case_id] = [
                re.compile(pattern, re.IGNORECASE)
                for pattern in edge_case.detection_patterns
            ]

        return compiled_patterns

    async def detect_edge_cases(
        self, url: str, html_content: str = None, headers: Dict[str, str] = None
    ) -> List[EdgeCase]:
        """Detect potential edge cases for a given URL"""
        detected_cases = []

        # Check URL patterns
        for case_id, patterns in self.url_patterns.items():
            edge_case = self.edge_cases[case_id]

            for pattern in patterns:
                if pattern.search(url):
                    detected_cases.append(edge_case)
                    break

        # Check HTML content if provided
        if html_content:
            for case_id, patterns in self.url_patterns.items():
                edge_case = self.edge_cases[case_id]

                if edge_case not in detected_cases:  # Avoid duplicates
                    for pattern in patterns:
                        if pattern.search(html_content):
                            detected_cases.append(edge_case)
                            break

        # Check headers if provided
        if headers:
            headers_text = json.dumps(headers, default=str).lower()

            for case_id, patterns in self.url_patterns.items():
                edge_case = self.edge_cases[case_id]

                if edge_case not in detected_cases:  # Avoid duplicates
                    for pattern in patterns:
                        if pattern.search(headers_text):
                            detected_cases.append(edge_case)
                            break

        # Store detection history
        self.detection_history.append(
            {
                "url": url,
                "detected_cases": [case.case_id for case in detected_cases],
                "timestamp": datetime.now(timezone.utc),
            }
        )

        return detected_cases

    def get_prevention_recommendations(
        self, detected_cases: List[EdgeCase]
    ) -> List[str]:
        """Get prevention recommendations for detected edge cases"""
        recommendations = []

        for case in detected_cases:
            recommendations.append(f"{case.name}: {case.prevention_strategy}")

        return recommendations

    def get_handling_strategies(self, detected_cases: List[EdgeCase]) -> List[str]:
        """Get handling strategies for detected edge cases"""
        strategies = []

        for case in detected_cases:
            strategies.append(f"{case.name}: {case.handling_strategy}")

        return strategies

    def assess_risk_level(self, detected_cases: List[EdgeCase]) -> str:
        """Assess overall risk level based on detected edge cases"""
        if not detected_cases:
            return "low"

        severity_scores = {
            ErrorSeverity.LOW: 1,
            ErrorSeverity.MEDIUM: 2,
            ErrorSeverity.HIGH: 3,
            ErrorSeverity.CRITICAL: 4,
        }

        total_score = sum(severity_scores[case.severity] for case in detected_cases)

        if total_score <= 2:
            return "low"
        elif total_score <= 5:
            return "medium"
        elif total_score <= 8:
            return "high"
        else:
            return "critical"

    def get_edge_case_statistics(self) -> Dict[str, Any]:
        """Get statistics about edge case detections"""
        case_counts = {}
        severity_counts = {}

        for detection in self.detection_history:
            for case_id in detection["detected_cases"]:
                case_counts[case_id] = case_counts.get(case_id, 0) + 1
                edge_case = self.edge_cases[case_id]
                severity = edge_case.severity.value
                severity_counts[severity] = severity_counts.get(severity, 0) + 1

        return {
            "total_detections": len(self.detection_history),
            "case_counts": case_counts,
            "severity_counts": severity_counts,
            "most_common_cases": sorted(
                case_counts.items(), key=lambda x: x[1], reverse=True
            )[:5],
        }


class ContentValidator:
    """Validates content quality and detects potential issues"""

    def __init__(self):
        self.validation_rules = self._initialize_validation_rules()

    def _initialize_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize content validation rules"""
        return {
            "content_size": {
                "min_length": 100,
                "max_length": 10000000,  # 10MB
                "warning_threshold": 5000000,  # 5MB
                "severity": "medium",
            },
            "text_ratio": {
                "min_ratio": 0.1,  # At least 10% text
                "max_ratio": 0.95,  # At most 95% text
                "severity": "low",
            },
            "link_density": {
                "max_density": 0.3,  # At most 30% links
                "severity": "low",
            },
            "script_content": {
                "max_ratio": 0.5,  # At most 50% script content
                "severity": "medium",
            },
            "encoding_issues": {"check_encoding": True, "severity": "medium"},
            "malformed_structure": {"check_structure": True, "severity": "low"},
        }

    def validate_content(self, html_content: str, url: str = None) -> Dict[str, Any]:
        """Validate content and return validation results"""
        validation_result = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "metrics": {},
            "recommendations": [],
        }

        # Check content size
        content_length = len(html_content)
        validation_result["metrics"]["content_length"] = content_length

        size_rule = self.validation_rules["content_size"]
        if content_length < size_rule["min_length"]:
            validation_result["warnings"].append(
                {
                    "type": "content_too_small",
                    "message": f"Content is too small: {content_length} bytes",
                    "severity": "low",
                }
            )
        elif content_length > size_rule["max_length"]:
            validation_result["errors"].append(
                {
                    "type": "content_too_large",
                    "message": f"Content is too large: {content_length} bytes",
                    "severity": "high",
                }
            )
            validation_result["is_valid"] = False
        elif content_length > size_rule["warning_threshold"]:
            validation_result["warnings"].append(
                {
                    "type": "content_large",
                    "message": f"Content is large: {content_length} bytes",
                    "severity": "medium",
                }
            )

        # Check text ratio (basic implementation)
        try:
            import re

            text_content = re.sub(r"<[^>]+>", "", html_content)
            text_length = len(text_content.strip())

            if content_length > 0:
                text_ratio = text_length / content_length
                validation_result["metrics"]["text_ratio"] = text_ratio

                text_rule = self.validation_rules["text_ratio"]
                if text_ratio < text_rule["min_ratio"]:
                    validation_result["warnings"].append(
                        {
                            "type": "low_text_ratio",
                            "message": f"Low text ratio: {text_ratio:.2%}",
                            "severity": text_rule["severity"],
                        }
                    )
                elif text_ratio > text_rule["max_ratio"]:
                    validation_result["warnings"].append(
                        {
                            "type": "high_text_ratio",
                            "message": f"High text ratio: {text_ratio:.2%}",
                            "severity": text_rule["severity"],
                        }
                    )
        except Exception as e:
            validation_result["warnings"].append(
                {
                    "type": "text_extraction_error",
                    "message": f"Error extracting text: {str(e)}",
                    "severity": "low",
                }
            )

        # Check for script content
        try:
            script_matches = re.findall(
                r"<script[^>]*>.*?</script>", html_content, re.DOTALL | re.IGNORECASE
            )
            script_length = sum(len(match) for match in script_matches)

            if content_length > 0:
                script_ratio = script_length / content_length
                validation_result["metrics"]["script_ratio"] = script_ratio

                script_rule = self.validation_rules["script_content"]
                if script_ratio > script_rule["max_ratio"]:
                    validation_result["warnings"].append(
                        {
                            "type": "high_script_ratio",
                            "message": f"High script content ratio: {script_ratio:.2%}",
                            "severity": script_rule["severity"],
                        }
                    )
        except Exception as e:
            validation_result["warnings"].append(
                {
                    "type": "script_analysis_error",
                    "message": f"Error analyzing scripts: {str(e)}",
                    "severity": "low",
                }
            )

        # Generate recommendations
        if validation_result["warnings"]:
            validation_result["recommendations"].append(
                "Review content quality warnings"
            )

        if validation_result["errors"]:
            validation_result["recommendations"].append(
                "Address content validation errors"
            )

        return validation_result


class URLValidator:
    """Validates URLs and detects potential issues"""

    def __init__(self):
        self.url_patterns = self._compile_url_patterns()
        self.blocked_domains = set()
        self.suspicious_patterns = self._compile_suspicious_patterns()

    def _compile_url_patterns(self) -> Dict[str, re.Pattern]:
        """Compile URL validation patterns"""
        return {
            "http": re.compile(r"^https?://"),
            "domain": re.compile(r"^https?://([^/]+)"),
            "path": re.compile(r"^https?://[^/]+(/.*)?$"),
            "file_extension": re.compile(r"\.([a-zA-Z0-9]+)(?:\?.*)?$"),
            "query_params": re.compile(r"\?(.+)$"),
        }

    def _compile_suspicious_patterns(self) -> List[re.Pattern]:
        """Compile patterns for suspicious URLs"""
        return [
            re.compile(r"(malware|virus|phishing|spam)", re.IGNORECASE),
            re.compile(r"(adult|xxx|porn)", re.IGNORECASE),
            re.compile(r"(illegal|black.market|dark.web)", re.IGNORECASE),
            re.compile(r"(\.tk|\.ml|\.ga|\.cf)$"),  # Suspicious TLDs
        ]

    def validate_url(self, url: str) -> Dict[str, Any]:
        """Validate URL and return validation results"""
        validation_result = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "metadata": {},
            "recommendations": [],
        }

        # Check URL format
        if not self.url_patterns["http"].match(url):
            validation_result["errors"].append(
                {
                    "type": "invalid_protocol",
                    "message": "URL must start with http:// or https://",
                    "severity": "high",
                }
            )
            validation_result["is_valid"] = False
            return validation_result

        # Extract domain
        domain_match = self.url_patterns["domain"].match(url)
        if domain_match:
            domain = domain_match.group(1)
            validation_result["metadata"]["domain"] = domain

            # Check against blocked domains
            if domain in self.blocked_domains:
                validation_result["errors"].append(
                    {
                        "type": "blocked_domain",
                        "message": f"Domain {domain} is blocked",
                        "severity": "high",
                    }
                )
                validation_result["is_valid"] = False
                return validation_result

            # Check for suspicious patterns
            for pattern in self.suspicious_patterns:
                if pattern.search(url):
                    validation_result["warnings"].append(
                        {
                            "type": "suspicious_url",
                            "message": f"URL matches suspicious pattern: {pattern.pattern}",
                            "severity": "medium",
                        }
                    )

        # Check URL length
        if len(url) > 2048:
            validation_result["warnings"].append(
                {
                    "type": "url_too_long",
                    "message": f"URL is very long: {len(url)} characters",
                    "severity": "low",
                }
            )

        # Check for file extensions
        ext_match = self.url_patterns["file_extension"].search(url)
        if ext_match:
            extension = ext_match.group(1).lower()
            validation_result["metadata"]["file_extension"] = extension

            # Warn about non-HTML extensions
            non_html_extensions = ["pdf", "doc", "docx", "xls", "xlsx", "zip", "exe"]
            if extension in non_html_extensions:
                validation_result["warnings"].append(
                    {
                        "type": "non_html_file",
                        "message": f"URL points to non-HTML file: .{extension}",
                        "severity": "medium",
                    }
                )

        return validation_result

    def add_blocked_domain(self, domain: str):
        """Add a domain to the blocked list"""
        self.blocked_domains.add(domain.lower())

    def remove_blocked_domain(self, domain: str):
        """Remove a domain from the blocked list"""
        self.blocked_domains.discard(domain.lower())


# Global instances
edge_case_detector = EdgeCaseDetector()
content_validator = ContentValidator()
url_validator = URLValidator()
