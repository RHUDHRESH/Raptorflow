"""
Advanced threat intelligence system with real-time analysis and pattern recognition.
Provides enterprise-grade threat detection, analysis, and response capabilities.
"""

import asyncio
import hashlib
import json
import logging
import re
import time
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from enum import Enum
import aiohttp
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class ThreatCategory(Enum):
    """Threat categories for classification."""
    INJECTION = "injection"
    XSS = "xss"
    CSRF = "csrf"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_EXFILTRATION = "data_exfiltration"
    DENIAL_OF_SERVICE = "denial_of_service"
    RECONNAISSANCE = "reconnaissance"
    MALWARE = "malware"
    SOCIAL_ENGINEERING = "social_engineering"
    MISCONFIGURATION = "misconfiguration"
    UNKNOWN = "unknown"


class ThreatSeverity(Enum):
    """Threat severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatSource(Enum):
    """Sources of threat intelligence."""
    SIGNATURE_BASED = "signature_based"
    ANOMALY_DETECTION = "anomaly_detection"
    BEHAVIORAL_ANALYSIS = "behavioral_analysis"
    THREAT_FEEDS = "threat_feeds"
    HONEYPOT = "honeypot"
    USER_REPORTING = "user_reporting"
    MACHINE_LEARNING = "machine_learning"
    MANUAL_ANALYSIS = "manual_analysis"


@dataclass
class ThreatIndicator:
    """Individual threat indicator."""
    
    id: str
    type: str  # ip, domain, url, hash, pattern, etc.
    value: str
    category: ThreatCategory
    severity: ThreatSeverity
    confidence: float
    source: ThreatSource
    description: str
    first_seen: datetime
    last_seen: datetime
    count: int
    active: bool = True
    tags: Set[str] = None
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = set()
        if self.context is None:
            self.context = {}


@dataclass
class ThreatEvent:
    """Threat event occurrence."""
    
    id: str
    timestamp: datetime
    indicator_id: str
    source_ip: Optional[str]
    user_id: Optional[str]
    workspace_id: Optional[str]
    request_data: Dict[str, Any]
    severity: ThreatSeverity
    category: ThreatCategory
    description: str
    blocked: bool
    action_taken: Optional[str]
    metadata: Dict[str, Any]


@dataclass
class ThreatPattern:
    """Recognized threat pattern."""
    
    id: str
    name: str
    pattern: str
    category: ThreatCategory
    severity: ThreatSeverity
    confidence: float
    description: str
    mitigation: str
    references: List[str]
    created_at: datetime
    updated_at: datetime
    active: bool = True
    false_positive_rate: float = 0.0
    true_positive_rate: float = 0.0


@dataclass
class ThreatCampaign:
    """Coordinated threat campaign."""
    
    id: str
    name: str
    description: str
    threat_actors: List[str]
    tactics: List[str]
    techniques: List[str]
    indicators: List[str]
    start_date: datetime
    end_date: Optional[datetime]
    status: str  # active, dormant, terminated
    severity: ThreatSeverity
    confidence: float


class ThreatFeeds:
    """External threat feeds integration."""
    
    def __init__(self):
        self.feeds = {
            "malware_domains": "https://example.com/malware-domains.txt",
            "phishing_urls": "https://example.com/phishing-urls.txt",
            "malicious_ips": "https://example.com/malicious-ips.txt",
            "botnet_ips": "https://example.com/botnet-ips.txt"
        }
        self.update_interval = 3600  # 1 hour
        self.last_update = datetime.now()
        self.feed_data: Dict[str, Set[str]] = {}
    
    async def update_feeds(self):
        """Update threat feeds from external sources."""
        try:
            async with aiohttp.ClientSession() as session:
                tasks = []
                for feed_name, feed_url in self.feeds.items():
                    task = self._fetch_feed(session, feed_name, feed_url)
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, Exception):
                        logger.error(f"Failed to update threat feed: {result}")
            
            self.last_update = datetime.now()
            logger.info("Threat feeds updated successfully")
            
        except Exception as e:
            logger.error(f"Failed to update threat feeds: {e}")
    
    async def _fetch_feed(self, session: aiohttp.ClientSession, feed_name: str, feed_url: str):
        """Fetch individual threat feed."""
        try:
            async with session.get(feed_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    content = await response.text()
                    indicators = set(line.strip() for line in content.split('\n') if line.strip())
                    self.feed_data[feed_name] = indicators
                    logger.info(f"Updated {feed_name} with {len(indicators)} indicators")
                else:
                    logger.warning(f"Failed to fetch {feed_name}: HTTP {response.status}")
        
        except Exception as e:
            logger.error(f"Error fetching {feed_name}: {e}")
    
    def check_indicator(self, indicator_type: str, value: str) -> bool:
        """Check if indicator exists in threat feeds."""
        for feed_name, indicators in self.feed_data.items():
            if indicator_type in feed_name and value in indicators:
                return True
        return False


class ThreatClustering:
    """Threat clustering and pattern recognition."""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.clustering_model = DBSCAN(eps=0.3, min_samples=2)
        self.feature_cache: Dict[str, np.ndarray] = {}
    
    def cluster_threats(self, threats: List[ThreatEvent]) -> Dict[int, List[ThreatEvent]]:
        """Cluster similar threats together."""
        if len(threats) < 2:
            return {0: threats}
        
        try:
            # Extract text features
            texts = []
            for threat in threats:
                text = self._extract_threat_text(threat)
                texts.append(text)
            
            # Vectorize
            features = self.vectorizer.fit_transform(texts).toarray()
            
            # Cluster
            cluster_labels = self.clustering_model.fit_predict(features)
            
            # Group threats by cluster
            clusters = defaultdict(list)
            for i, label in enumerate(cluster_labels):
                clusters[label].append(threats[i])
            
            return dict(clusters)
            
        except Exception as e:
            logger.error(f"Threat clustering failed: {e}")
            return {0: threats}
    
    def _extract_threat_text(self, threat: ThreatEvent) -> str:
        """Extract text features from threat event."""
        text_parts = []
        
        # Add description
        text_parts.append(threat.description)
        
        # Add request data text
        request_text = json.dumps(threat.request_data, sort_keys=True)
        text_parts.append(request_text)
        
        # Add category and source info
        text_parts.append(threat.category.value)
        text_parts.append(threat.source_ip or "")
        text_parts.append(threat.user_id or "")
        
        return " ".join(text_parts)
    
    def find_similar_threats(self, target_threat: ThreatEvent, 
                           threat_database: List[ThreatEvent], 
                           threshold: float = 0.8) -> List[Tuple[ThreatEvent, float]]:
        """Find threats similar to target threat."""
        if not threat_database:
            return []
        
        try:
            # Extract features
            target_text = self._extract_threat_text(target_threat)
            database_texts = [self._extract_threat_text(threat) for threat in threat_database]
            
            # Vectorize
            all_texts = [target_text] + database_texts
            features = self.vectorizer.fit_transform(all_texts)
            
            # Calculate similarity
            target_features = features[0:1]
            database_features = features[1:]
            
            similarities = cosine_similarity(target_features, database_features)[0]
            
            # Find similar threats above threshold
            similar_threats = []
            for i, similarity in enumerate(similarities):
                if similarity >= threshold:
                    similar_threats.append((threat_database[i], float(similarity)))
            
            # Sort by similarity (descending)
            similar_threats.sort(key=lambda x: x[1], reverse=True)
            
            return similar_threats
            
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []


class ThreatIntelligence:
    """Main threat intelligence system."""
    
    def __init__(self):
        self.indicators: Dict[str, ThreatIndicator] = {}
        self.events: deque = deque(maxlen=10000)
        self.patterns: Dict[str, ThreatPattern] = {}
        self.campaigns: Dict[str, ThreatCampaign] = {}
        
        # Subsystems
        self.threat_feeds = ThreatFeeds()
        self.clustering = ThreatClustering()
        
        # Analytics
        self.threat_statistics = defaultdict(int)
        self.category_trends: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.severity_trends: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Configuration
        self.auto_block_threshold = 0.9
        self.similarity_threshold = 0.8
        
        # Background tasks
        self._feed_update_task: Optional[asyncio.Task] = None
        self._analysis_task: Optional[asyncio.Task] = None
        self._is_running = False
        
        # Initialize with default patterns
        self._initialize_default_patterns()
        
        logger.info("ThreatIntelligence system initialized")
    
    def _initialize_default_patterns(self):
        """Initialize with default threat patterns."""
        default_patterns = [
            ThreatPattern(
                id="sql_injection_union",
                name="Union-based SQL Injection",
                pattern=r"(?i)(union\s+select|select\s+.*\s+from\s+.*\s+union)",
                category=ThreatCategory.INJECTION,
                severity=ThreatSeverity.HIGH,
                confidence=0.95,
                description="Union-based SQL injection attack detected",
                mitigation="Use parameterized queries and input validation",
                references=["OWASP-SQLI", "CWE-89"],
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            ThreatPattern(
                id="xss_script_injection",
                name="Script-based XSS",
                pattern=r"(?i)(<script[^>]*>.*?</script>|javascript:|on\w+\s*=)",
                category=ThreatCategory.XSS,
                severity=ThreatSeverity.HIGH,
                confidence=0.90,
                description="Cross-site scripting attack detected",
                mitigation="Implement output encoding and CSP headers",
                references=["OWASP-XSS", "CWE-79"],
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            ThreatPattern(
                id="command_injection_shell",
                name="Shell Command Injection",
                pattern=r"(?i)(;\s*(cat|ls|dir|whoami|id|pwd)\s*|`\s*[^`]*\s*`)",
                category=ThreatCategory.INJECTION,
                severity=ThreatSeverity.CRITICAL,
                confidence=0.98,
                description="Command injection attack detected",
                mitigation="Use command whitelisting and avoid shell execution",
                references=["OWASP-CMDI", "CWE-78"],
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            ThreatPattern(
                id="path_traversal_basic",
                name="Basic Path Traversal",
                pattern=r"(?i)(\.\./|\.\.\\|%2e%2e%2f|%2e%2e%5c)",
                category=ThreatCategory.AUTHORIZATION,
                severity=ThreatSeverity.HIGH,
                confidence=0.92,
                description="Path traversal attack detected",
                mitigation="Validate file paths and use chroot jails",
                references=["OWASP-PATH", "CWE-22"],
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            ThreatPattern(
                id="ssrf_localhost",
                name="SSRF Localhost",
                pattern=r"(?i)(http://localhost|https://localhost|http://127\.0\.0\.1|file://)",
                category=ThreatCategory.AUTHORIZATION,
                severity=ThreatSeverity.HIGH,
                confidence=0.88,
                description="Server-side request forgery detected",
                mitigation="Validate URLs and use allowlist approach",
                references=["OWASP-SSRF", "CWE-918"],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        
        for pattern in default_patterns:
            self.patterns[pattern.id] = pattern
    
    async def analyze_request(self, request_data: Dict[str, Any], 
                           source_ip: Optional[str] = None,
                           user_id: Optional[str] = None,
                           workspace_id: Optional[str] = None) -> List[ThreatEvent]:
        """Analyze request for threats."""
        threats = []
        
        try:
            # Pattern-based detection
            pattern_threats = await self._pattern_detection(request_data, source_ip, user_id, workspace_id)
            threats.extend(pattern_threats)
            
            # Indicator-based detection
            indicator_threats = await self._indicator_detection(request_data, source_ip, user_id, workspace_id)
            threats.extend(indicator_threats)
            
            # Behavioral analysis
            behavioral_threats = await self._behavioral_analysis(request_data, source_ip, user_id, workspace_id)
            threats.extend(behavioral_threats)
            
            # Store events
            for threat in threats:
                self.events.append(threat)
                self._update_statistics(threat)
            
            # Auto-block critical threats
            for threat in threats:
                if threat.severity == ThreatSeverity.CRITICAL and threat.confidence >= self.auto_block_threshold:
                    await self._auto_block_threat(threat)
            
            return threats
            
        except Exception as e:
            logger.error(f"Threat analysis failed: {e}")
            return []
    
    async def _pattern_detection(self, request_data: Dict[str, Any], 
                              source_ip: Optional[str], user_id: Optional[str], 
                              workspace_id: Optional[str]) -> List[ThreatEvent]:
        """Pattern-based threat detection."""
        threats = []
        request_text = json.dumps(request_data, sort_keys=True)
        
        for pattern in self.patterns.values():
            if not pattern.active:
                continue
            
            try:
                matches = re.finditer(pattern.pattern, request_text, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    threat = ThreatEvent(
                        id=f"pattern_{pattern.id}_{int(time.time())}_{hash(match.group()) % 10000}",
                        timestamp=datetime.now(),
                        indicator_id=pattern.id,
                        source_ip=source_ip,
                        user_id=user_id,
                        workspace_id=workspace_id,
                        request_data=request_data,
                        severity=pattern.severity,
                        category=pattern.category,
                        description=f"Pattern '{pattern.name}' detected: {pattern.description}",
                        blocked=False,
                        action_taken=None,
                        metadata={
                            "pattern_id": pattern.id,
                            "matched_text": match.group(),
                            "match_position": match.span(),
                            "confidence": pattern.confidence
                        }
                    )
                    threats.append(threat)
                    
            except re.error as e:
                logger.warning(f"Regex error in pattern {pattern.id}: {e}")
        
        return threats
    
    async def _indicator_detection(self, request_data: Dict[str, Any],
                                source_ip: Optional[str], user_id: Optional[str],
                                workspace_id: Optional[str]) -> List[ThreatEvent]:
        """Indicator-based threat detection."""
        threats = []
        
        # Check IP indicators
        if source_ip:
            if self.threat_feeds.check_indicator("ip", source_ip):
                threat = ThreatEvent(
                    id=f"ip_indicator_{int(time.time())}",
                    timestamp=datetime.now(),
                    indicator_id=f"ip_{source_ip}",
                    source_ip=source_ip,
                    user_id=user_id,
                    workspace_id=workspace_id,
                    request_data=request_data,
                    severity=ThreatSeverity.HIGH,
                    category=ThreatCategory.RECONNAISSANCE,
                    description=f"Malicious IP detected: {source_ip}",
                    blocked=False,
                    action_taken=None,
                    metadata={
                        "indicator_type": "ip",
                        "indicator_value": source_ip,
                        "source": "threat_feed"
                    }
                )
                threats.append(threat)
        
        # Check URL indicators in request
        request_text = json.dumps(request_data)
        urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', request_text)
        
        for url in urls:
            if self.threat_feeds.check_indicator("url", url):
                threat = ThreatEvent(
                    id=f"url_indicator_{int(time.time())}_{hash(url) % 1000}",
                    timestamp=datetime.now(),
                    indicator_id=f"url_{hashlib.md5(url.encode()).hexdigest()[:8]}",
                    source_ip=source_ip,
                    user_id=user_id,
                    workspace_id=workspace_id,
                    request_data=request_data,
                    severity=ThreatSeverity.MEDIUM,
                    category=ThreatCategory.PHISHING,
                    description=f"Malicious URL detected: {url}",
                    blocked=False,
                    action_taken=None,
                    metadata={
                        "indicator_type": "url",
                        "indicator_value": url,
                        "source": "threat_feed"
                    }
                )
                threats.append(threat)
        
        return threats
    
    async def _behavioral_analysis(self, request_data: Dict[str, Any],
                                source_ip: Optional[str], user_id: Optional[str],
                                workspace_id: Optional[str]) -> List[ThreatEvent]:
        """Behavioral threat detection."""
        threats = []
        
        # Analyze request frequency
        if user_id:
            recent_requests = [
                event for event in self.events
                if event.user_id == user_id and 
                (datetime.now() - event.timestamp).total_seconds() < 300  # 5 minutes
            ]
            
            if len(recent_requests) > 100:  # More than 100 requests in 5 minutes
                threat = ThreatEvent(
                    id=f"behavioral_frequency_{int(time.time())}",
                    timestamp=datetime.now(),
                    indicator_id=f"frequency_{user_id}",
                    source_ip=source_ip,
                    user_id=user_id,
                    workspace_id=workspace_id,
                    request_data=request_data,
                    severity=ThreatSeverity.MEDIUM,
                    category=ThreatCategory.DENIAL_OF_SERVICE,
                    description=f"High request frequency detected: {len(recent_requests)} requests in 5 minutes",
                    blocked=False,
                    action_taken=None,
                    metadata={
                        "behavior_type": "frequency",
                        "request_count": len(recent_requests),
                        "time_window": 300
                    }
                )
                threats.append(threat)
        
        # Analyze request patterns
        if user_id:
            recent_user_requests = [
                event for event in self.events
                if event.user_id == user_id and 
                (datetime.now() - event.timestamp).total_seconds() < 3600  # 1 hour
            ]
            
            if len(recent_user_requests) >= 3:
                # Cluster similar requests
                clusters = self.clustering.cluster_threats(recent_user_requests)
                
                # Look for large clusters (potential automated attacks)
                for cluster_id, cluster_threats in clusters.items():
                    if len(cluster_threats) >= 5:  # 5 or more similar threats
                        threat = ThreatEvent(
                            id=f"behavioral_cluster_{int(time.time())}_{cluster_id}",
                            timestamp=datetime.now(),
                            indicator_id=f"cluster_{cluster_id}",
                            source_ip=source_ip,
                            user_id=user_id,
                            workspace_id=workspace_id,
                            request_data=request_data,
                            severity=ThreatSeverity.HIGH,
                            category=ThreatCategory.AUTHORIZATION,
                            description=f"Automated attack pattern detected: {len(cluster_threats)} similar threats",
                            blocked=False,
                            action_taken=None,
                            metadata={
                                "behavior_type": "clustering",
                                "cluster_id": cluster_id,
                                "cluster_size": len(cluster_threats)
                            }
                        )
                        threats.append(threat)
        
        return threats
    
    def _update_statistics(self, threat: ThreatEvent):
        """Update threat statistics."""
        self.threat_statistics[threat.category.value] += 1
        self.threat_statistics[threat.severity.value] += 1
        
        # Update trends
        current_hour = datetime.now().strftime("%Y-%m-%d %H:00:00")
        self.category_trends[threat.category.value].append({
            "timestamp": current_hour,
            "count": 1
        })
        self.severity_trends[threat.severity.value].append({
            "timestamp": current_hour,
            "count": 1
        })
    
    async def _auto_block_threat(self, threat: ThreatEvent):
        """Automatically block critical threats."""
        try:
            # Add to blocked indicators
            indicator = ThreatIndicator(
                id=f"auto_block_{threat.id}",
                type="auto_generated",
                value=threat.source_ip or threat.user_id or "unknown",
                category=threat.category,
                severity=threat.severity,
                confidence=threat.confidence,
                source=ThreatSource.MACHINE_LEARNING,
                description=f"Auto-blocked based on threat: {threat.description}",
                first_seen=threat.timestamp,
                last_seen=threat.timestamp,
                count=1
            )
            self.indicators[indicator.id] = indicator
            
            # Update threat event
            threat.blocked = True
            threat.action_taken = "auto_blocked"
            
            logger.critical(f"Auto-blocked critical threat: {threat.description}")
            
        except Exception as e:
            logger.error(f"Auto-block failed: {e}")
    
    async def start_monitoring(self):
        """Start threat intelligence monitoring."""
        if self._is_running:
            logger.warning("Threat intelligence monitoring already running")
            return
        
        self._is_running = True
        self._feed_update_task = asyncio.create_task(self._feed_update_loop())
        self._analysis_task = asyncio.create_task(self._analysis_loop())
        
        logger.info("Started threat intelligence monitoring")
    
    async def stop_monitoring(self):
        """Stop threat intelligence monitoring."""
        if not self._is_running:
            return
        
        self._is_running = False
        
        if self._feed_update_task:
            self._feed_update_task.cancel()
        if self._analysis_task:
            self._analysis_task.cancel()
        
        await asyncio.gather(
            self._feed_update_task,
            self._analysis_task,
            return_exceptions=True
        )
        
        logger.info("Stopped threat intelligence monitoring")
    
    async def _feed_update_loop(self):
        """Background loop for updating threat feeds."""
        while self._is_running:
            try:
                await self.threat_feeds.update_feeds()
                await asyncio.sleep(self.threat_feeds.update_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Feed update loop error: {e}")
                await asyncio.sleep(60)  # Retry after 1 minute
    
    async def _analysis_loop(self):
        """Background loop for threat analysis."""
        while self._is_running:
            try:
                await self._periodic_analysis()
                await asyncio.sleep(300)  # Analyze every 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Analysis loop error: {e}")
                await asyncio.sleep(60)
    
    async def _periodic_analysis(self):
        """Perform periodic threat analysis."""
        try:
            # Analyze recent threats for patterns
            recent_threats = [
                event for event in self.events
                if (datetime.now() - event.timestamp).total_seconds() < 3600  # Last hour
            ]
            
            if len(recent_threats) >= 10:
                # Cluster threats to identify campaigns
                clusters = self.clustering.cluster_threats(recent_threats)
                
                # Large clusters might indicate campaigns
                for cluster_id, cluster_threats in clusters.items():
                    if len(cluster_threats) >= 20:  # Potential campaign
                        await self._identify_campaign(cluster_threats)
            
        except Exception as e:
            logger.error(f"Periodic analysis failed: {e}")
    
    async def _identify_campaign(self, threats: List[ThreatEvent]):
        """Identify potential threat campaign from clustered threats."""
        try:
            # Analyze common characteristics
            common_sources = set()
            common_categories = set()
            common_patterns = set()
            
            for threat in threats:
                if threat.source_ip:
                    common_sources.add(threat.source_ip)
                common_categories.add(threat.category.value)
                if "pattern_id" in threat.metadata:
                    common_patterns.add(threat.metadata["pattern_id"])
            
            # Create campaign if significant patterns found
            if len(common_sources) <= 5 and len(common_categories) == 1:  # Focused attack
                campaign = ThreatCampaign(
                    id=f"campaign_{int(time.time())}",
                    name=f"Automated Campaign {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    description=f"Coordinated attack using {len(common_patterns)} patterns",
                    threat_actors=["unknown"],
                    tactics=["automated_attack"],
                    techniques=list(common_patterns),
                    indicators=[threat.indicator_id for threat in threats],
                    start_date=min(threat.timestamp for threat in threats),
                    end_date=None,
                    status="active",
                    severity=ThreatSeverity.HIGH,
                    confidence=0.7
                )
                
                self.campaigns[campaign.id] = campaign
                logger.warning(f"Identified potential threat campaign: {campaign.name}")
                
        except Exception as e:
            logger.error(f"Campaign identification failed: {e}")
    
    def get_threat_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get threat intelligence summary."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Filter recent events
        recent_events = [
            event for event in self.events
            if event.timestamp >= cutoff_time
        ]
        
        # Calculate statistics
        total_threats = len(recent_events)
        blocked_threats = sum(1 for event in recent_events if event.blocked)
        
        category_counts = defaultdict(int)
        severity_counts = defaultdict(int)
        source_counts = defaultdict(int)
        
        for event in recent_events:
            category_counts[event.category.value] += 1
            severity_counts[event.severity.value] += 1
            if event.source_ip:
                source_counts[event.source_ip] += 1
        
        # Get top sources
        top_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Active campaigns
        active_campaigns = [
            campaign for campaign in self.campaigns.values()
            if campaign.status == "active"
        ]
        
        return {
            "period_hours": hours,
            "total_threats": total_threats,
            "blocked_threats": blocked_threats,
            "block_rate": blocked_threats / max(total_threats, 1),
            "category_distribution": dict(category_counts),
            "severity_distribution": dict(severity_counts),
            "top_sources": top_sources,
            "active_campaigns": len(active_campaigns),
            "total_indicators": len(self.indicators),
            "active_patterns": sum(1 for pattern in self.patterns.values() if pattern.active),
            "feeds_last_updated": self.threat_feeds.last_update.isoformat()
        }
    
    def get_similar_threats(self, threat_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Find threats similar to a given threat."""
        target_threat = None
        for event in self.events:
            if event.id == threat_id:
                target_threat = event
                break
        
        if not target_threat:
            return []
        
        # Find similar threats
        similar_threats = self.clustering.find_similar_threats(
            target_threat, 
            list(self.events),
            self.similarity_threshold
        )
        
        return [
            {
                "threat_id": threat.id,
                "similarity": similarity,
                "timestamp": threat.timestamp.isoformat(),
                "category": threat.category.value,
                "severity": threat.severity.value,
                "description": threat.description
            }
            for threat, similarity in similar_threats[:limit]
        ]
    
    def add_threat_pattern(self, pattern: ThreatPattern):
        """Add a new threat pattern."""
        self.patterns[pattern.id] = pattern
        logger.info(f"Added threat pattern: {pattern.name}")
    
    def update_pattern_performance(self, pattern_id: str, 
                               true_positives: int, false_positives: int,
                               total_samples: int):
        """Update pattern performance metrics."""
        if pattern_id in self.patterns:
            pattern = self.patterns[pattern_id]
            pattern.true_positive_rate = true_positives / max(total_samples, 1)
            pattern.false_positive_rate = false_positives / max(total_samples, 1)
            pattern.updated_at = datetime.now()
            logger.info(f"Updated performance for pattern {pattern_id}")


# Global threat intelligence instance
_threat_intelligence: Optional[ThreatIntelligence] = None


def get_threat_intelligence() -> ThreatIntelligence:
    """Get the global threat intelligence instance."""
    global _threat_intelligence
    if _threat_intelligence is None:
        _threat_intelligence = ThreatIntelligence()
    return _threat_intelligence


async def analyze_request_threats(request_data: Dict[str, Any],
                                source_ip: Optional[str] = None,
                                user_id: Optional[str] = None,
                                workspace_id: Optional[str] = None) -> List[ThreatEvent]:
    """Analyze request for threats (convenience function)."""
    intel = get_threat_intelligence()
    return await intel.analyze_request(request_data, source_ip, user_id, workspace_id)


def get_threat_summary(hours: int = 24) -> Dict[str, Any]:
    """Get threat intelligence summary (convenience function)."""
    intel = get_threat_intelligence()
    return intel.get_threat_summary(hours)


async def start_threat_intelligence():
    """Start threat intelligence monitoring (convenience function)."""
    intel = get_threat_intelligence()
    await intel.start_monitoring()


async def stop_threat_intelligence():
    """Stop threat intelligence monitoring (convenience function)."""
    intel = get_threat_intelligence()
    await intel.stop_monitoring()
