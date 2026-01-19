"""
Behavioral Analysis for Advanced Threat Detection
Provides ML-driven anomaly detection, user behavior profiling, and threat intelligence integration.
"""

import asyncio
import json
import logging
import math
import statistics
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from collections import defaultdict, deque
import hashlib
import re

logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    """Types of behavioral anomalies."""
    UNUSUAL_ACCESS_TIME = "unusual_access_time"
    UNUSUAL_LOCATION = "unusual_location"
    UNUSUAL_DEVICE = "unusual_device"
    RAPID_REQUESTS = "rapid_requests"
    UNUSUAL_RESOURCE_ACCESS = "unusual_resource_access"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXFILTRATION = "data_exfiltration"
    BRUTE_FORCE = "brute_force"
    LATERAL_MOVEMENT = "lateral_movement"
    IMPOSSIBLE_TRAVEL = "impossible_travel"


class ThreatLevel(Enum):
    """Threat severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BehaviorPattern(Enum):
    """Behavior pattern types."""
    NORMAL = "normal"
    SUSPICIOUS = "suspicious"
    MALICIOUS = "malicious"
    UNKNOWN = "unknown"


@dataclass
class UserBehaviorProfile:
    """User behavior profile."""
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    # Access patterns
    typical_hours: Set[int]
    typical_days: Set[int]
    typical_locations: Set[str]
    typical_devices: Set[str]
    typical_resources: List[str]
    
    # Behavioral metrics
    avg_requests_per_hour: float
    avg_session_duration: float
    typical_request_intervals: List[float]
    resource_access_frequency: Dict[str, float]
    
    # Risk indicators
    failed_auth_count: int
    suspicious_activity_count: int
    risk_score: float
    
    # Metadata
    total_sessions: int
    total_requests: int
    last_activity: datetime


@dataclass
class BehaviorEvent:
    """Single behavior event."""
    timestamp: datetime
    user_id: str
    session_id: str
    client_ip: str
    user_agent: str
    resource: str
    action: str
    success: bool
    response_time: float
    geo_location: Optional[str]
    device_fingerprint: str
    additional_data: Dict[str, Any]


@dataclass
class AnomalyDetection:
    """Anomaly detection result."""
    timestamp: datetime
    user_id: str
    anomaly_type: AnomalyType
    threat_level: ThreatLevel
    confidence: float
    description: str
    contributing_factors: List[str]
    related_events: List[str]
    recommended_actions: List[str]


@dataclass
class ThreatIntelligence:
    """Threat intelligence data."""
    indicator: str
    indicator_type: str
    threat_type: str
    confidence: float
    source: str
    first_seen: datetime
    last_seen: datetime
    severity: ThreatLevel
    description: str


class BehavioralAnalysis:
    """Behavioral analysis engine for threat detection."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        
        # Storage
        self.user_profiles: Dict[str, UserBehaviorProfile] = {}
        self.behavior_events: deque = deque(maxlen=10000)
        self.anomaly_detections: List[AnomalyDetection] = []
        self.threat_intelligence: Dict[str, ThreatIntelligence] = {}
        
        # Analysis state
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.request_patterns: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.location_tracking: Dict[str, List[Tuple[datetime, str]]] = defaultdict(list)
        
        # ML models (simplified for demonstration)
        self.anomaly_thresholds = self._initialize_thresholds()
        self.behavior_models = self._initialize_behavior_models()
        
        # Threat intelligence sources
        self.malicious_ips: Set[str] = set()
        self.suspicious_user_agents: Set[str] = set()
        self.known_attack_patterns: List[re.Pattern] = []
        
        # Initialize threat intelligence
        self._initialize_threat_intelligence()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration."""
        return {
            "anomaly_threshold": 0.7,
            "min_profile_events": 10,
            "profile_update_interval": 3600,  # 1 hour
            "max_profile_age": 86400 * 30,  # 30 days
            "rapid_request_threshold": 10,  # requests per minute
            "impossible_travel_speed": 900,  # km/h
            "session_timeout": 3600,  # 1 hour
            "behavior_analysis_window": 3600 * 24,  # 24 hours
        }
    
    def _initialize_thresholds(self) -> Dict[str, float]:
        """Initialize anomaly detection thresholds."""
        return {
            "time_deviation": 2.0,  # standard deviations
            "location_deviation": 0.8,  # similarity threshold
            "device_deviation": 0.7,  # similarity threshold
            "request_frequency": 3.0,  # multiples of average
            "resource_deviation": 0.6,  # similarity threshold
            "response_time": 5.0,  # seconds
            "failed_auth_rate": 0.3,  # 30%
        }
    
    def _initialize_behavior_models(self) -> Dict[str, Any]:
        """Initialize behavioral models."""
        return {
            "access_pattern_model": {
                "hour_weights": [0.5] * 24,  # Initial equal weights
                "day_weights": [0.14] * 7,   # Initial equal weights
            },
            "resource_model": {
                "resource_vectors": {},  # Resource embedding vectors
                "access_patterns": {},    # Access pattern history
            },
            "temporal_model": {
                "intervals": deque(maxlen=1000),
                "session_durations": deque(maxlen=100),
            }
        }
    
    def _initialize_threat_intelligence(self):
        """Initialize threat intelligence data."""
        # Sample malicious IPs (in production, this would come from threat feeds)
        self.malicious_ips.update([
            "192.168.1.100",  # Example malicious IP
            "10.0.0.50",      # Example internal threat
        ])
        
        # Sample suspicious user agents
        self.suspicious_user_agents.update([
            "sqlmap", "nikto", "nmap", "masscan", "dirb",
            "python-requests", "curl", "wget"
        ])
        
        # Known attack patterns
        attack_patterns = [
            r"union.*select",  # SQL injection
            r"<script[^>]*>",  # XSS
            r"\.\./",          # Directory traversal
            r"cmd\.exe",       # Command injection
            r"/etc/passwd",    # File inclusion
        ]
        self.known_attack_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in attack_patterns]
    
    async def analyze_behavior_event(self, event: BehaviorEvent) -> List[AnomalyDetection]:
        """Analyze a behavior event for anomalies."""
        # Store event
        self.behavior_events.append(event)
        
        # Update tracking data
        self._update_tracking_data(event)
        
        # Get or create user profile
        profile = await self._get_or_create_profile(event.user_id)
        
        # Detect anomalies
        anomalies = await self._detect_anomalies(event, profile)
        
        # Update profile
        await self._update_profile(profile, event)
        
        # Store anomalies
        for anomaly in anomalies:
            self.anomaly_detections.append(anomaly)
            await self._handle_anomaly(anomaly)
        
        return anomalies
    
    def _update_tracking_data(self, event: BehaviorEvent):
        """Update internal tracking data."""
        # Update session tracking
        if event.session_id not in self.active_sessions:
            self.active_sessions[event.session_id] = {
                "start_time": event.timestamp,
                "request_count": 0,
                "resources_accessed": set(),
                "last_activity": event.timestamp,
            }
        
        session = self.active_sessions[event.session_id]
        session["request_count"] += 1
        session["resources_accessed"].add(event.resource)
        session["last_activity"] = event.timestamp
        
        # Update request patterns
        self.request_patterns[event.user_id].append(event.timestamp)
        
        # Update location tracking
        if event.geo_location:
            self.location_tracking[event.user_id].append((event.timestamp, event.geo_location))
            # Keep only recent locations
            cutoff = datetime.now() - timedelta(days=7)
            self.location_tracking[event.user_id] = [
                (ts, loc) for ts, loc in self.location_tracking[event.user_id]
                if ts >= cutoff
            ]
    
    async def _get_or_create_profile(self, user_id: str) -> UserBehaviorProfile:
        """Get or create user behavior profile."""
        if user_id not in self.user_profiles:
            # Create new profile
            profile = UserBehaviorProfile(
                user_id=user_id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                typical_hours=set(),
                typical_days=set(),
                typical_locations=set(),
                typical_devices=set(),
                typical_resources=[],
                avg_requests_per_hour=0.0,
                avg_session_duration=0.0,
                typical_request_intervals=[],
                resource_access_frequency={},
                failed_auth_count=0,
                suspicious_activity_count=0,
                risk_score=0.0,
                total_sessions=0,
                total_requests=0,
                last_activity=datetime.now(),
            )
            self.user_profiles[user_id] = profile
        
        return self.user_profiles[user_id]
    
    async def _detect_anomalies(self, event: BehaviorEvent, profile: UserBehaviorProfile) -> List[AnomalyDetection]:
        """Detect anomalies in the behavior event."""
        anomalies = []
        
        # Skip analysis for new profiles with insufficient data
        if profile.total_requests < self.config["min_profile_events"]:
            return anomalies
        
        # 1. Unusual access time
        time_anomaly = await self._detect_time_anomaly(event, profile)
        if time_anomaly:
            anomalies.append(time_anomaly)
        
        # 2. Unusual location
        location_anomaly = await self._detect_location_anomaly(event, profile)
        if location_anomaly:
            anomalies.append(location_anomaly)
        
        # 3. Unusual device
        device_anomaly = await self._detect_device_anomaly(event, profile)
        if device_anomaly:
            anomalies.append(device_anomaly)
        
        # 4. Rapid requests
        rapid_anomaly = await self._detect_rapid_requests(event, profile)
        if rapid_anomaly:
            anomalies.append(rapid_anomaly)
        
        # 5. Unusual resource access
        resource_anomaly = await self._detect_resource_anomaly(event, profile)
        if resource_anomaly:
            anomalies.append(resource_anomaly)
        
        # 6. Impossible travel
        travel_anomaly = await self._detect_impossible_travel(event, profile)
        if travel_anomaly:
            anomalies.append(travel_anomaly)
        
        # 7. Threat intelligence match
        threat_anomaly = await self._detect_threat_intelligence_match(event)
        if threat_anomaly:
            anomalies.append(threat_anomaly)
        
        # 8. Attack pattern detection
        attack_anomaly = await self._detect_attack_patterns(event)
        if attack_anomaly:
            anomalies.append(attack_anomaly)
        
        return anomalies
    
    async def _detect_time_anomaly(self, event: BehaviorEvent, profile: UserBehaviorProfile) -> Optional[AnomalyDetection]:
        """Detect unusual access time anomalies."""
        if not profile.typical_hours:
            return None
        
        current_hour = event.timestamp.hour
        current_day = event.timestamp.weekday()
        
        # Calculate time deviation
        hour_deviation = 1.0 - (len([h for h in profile.typical_hours if abs(h - current_hour) <= 1]) / max(len(profile.typical_hours), 1))
        day_deviation = 0.0 if current_day in profile.typical_days else 1.0
        
        combined_deviation = (hour_deviation + day_deviation) / 2
        
        if combined_deviation > self.anomaly_thresholds["time_deviation"] / 3:
            return AnomalyDetection(
                timestamp=event.timestamp,
                user_id=event.user_id,
                anomaly_type=AnomalyType.UNUSUAL_ACCESS_TIME,
                threat_level=ThreatLevel.MEDIUM if combined_deviation < 0.8 else ThreatLevel.HIGH,
                confidence=combined_deviation,
                description=f"Unusual access time: {current_hour}:00 on day {current_day}",
                contributing_factors=[
                    f"Hour deviation: {hour_deviation:.2f}",
                    f"Day deviation: {day_deviation:.2f}",
                    f"Typical hours: {sorted(profile.typical_hours)}",
                ],
                related_events=[],
                recommended_actions=["Verify user identity", "Check for legitimate reasons"],
            )
        
        return None
    
    async def _detect_location_anomaly(self, event: BehaviorEvent, profile: UserBehaviorProfile) -> Optional[AnomalyDetection]:
        """Detect unusual location anomalies."""
        if not event.geo_location or not profile.typical_locations:
            return None
        
        # Simple location similarity check
        location_similarity = 1.0 if event.geo_location in profile.typical_locations else 0.0
        
        if location_similarity < self.anomaly_thresholds["location_deviation"]:
            return AnomalyDetection(
                timestamp=event.timestamp,
                user_id=event.user_id,
                anomaly_type=AnomalyType.UNUSUAL_LOCATION,
                threat_level=ThreatLevel.HIGH,
                confidence=1.0 - location_similarity,
                description=f"Unusual access location: {event.geo_location}",
                contributing_factors=[
                    f"New location: {event.geo_location}",
                    f"Typical locations: {list(profile.typical_locations)}",
                ],
                related_events=[],
                recommended_actions=["Require MFA", "Verify user location", "Check for VPN/proxy usage"],
            )
        
        return None
    
    async def _detect_device_anomaly(self, event: BehaviorEvent, profile: UserBehaviorProfile) -> Optional[AnomalyDetection]:
        """Detect unusual device anomalies."""
        device_similarity = 1.0 if event.device_fingerprint in profile.typical_devices else 0.0
        
        if device_similarity < self.anomaly_thresholds["device_deviation"]:
            return AnomalyDetection(
                timestamp=event.timestamp,
                user_id=event.user_id,
                anomaly_type=AnomalyType.UNUSUAL_DEVICE,
                threat_level=ThreatLevel.MEDIUM,
                confidence=1.0 - device_similarity,
                description=f"Unusual device: {event.device_fingerprint[:16]}...",
                contributing_factors=[
                    f"New device fingerprint",
                    f"Device count: {len(profile.typical_devices)}",
                ],
                related_events=[],
                recommended_actions=["Require device verification", "Check user agent string"],
            )
        
        return None
    
    async def _detect_rapid_requests(self, event: BehaviorEvent, profile: UserBehaviorProfile) -> Optional[AnomalyDetection]:
        """Detect rapid request anomalies."""
        user_requests = self.request_patterns[event.user_id]
        recent_requests = [
            req_time for req_time in user_requests
            if (event.timestamp - req_time).total_seconds() <= 60
        ]
        
        if len(recent_requests) > self.config["rapid_request_threshold"]:
            # Calculate how many times above normal
            normal_rate = profile.avg_requests_per_hour / 60  # per minute
            current_rate = len(recent_requests)
            rate_multiplier = current_rate / max(normal_rate, 1)
            
            if rate_multiplier > self.anomaly_thresholds["request_frequency"]:
                return AnomalyDetection(
                    timestamp=event.timestamp,
                    user_id=event.user_id,
                    anomaly_type=AnomalyType.RAPID_REQUESTS,
                    threat_level=ThreatLevel.HIGH if rate_multiplier > 5 else ThreatLevel.MEDIUM,
                    confidence=min(rate_multiplier / 10, 1.0),
                    description=f"Rapid requests detected: {len(recent_requests)} in 1 minute",
                    contributing_factors=[
                        f"Current rate: {current_rate}/min",
                        f"Normal rate: {normal_rate:.2f}/min",
                        f"Rate multiplier: {rate_multiplier:.2f}x",
                    ],
                    related_events=[],
                    recommended_actions=["Apply rate limiting", "Monitor for automated attacks", "Consider CAPTCHA"],
                )
        
        return None
    
    async def _detect_resource_anomaly(self, event: BehaviorEvent, profile: UserBehaviorProfile) -> Optional[AnomalyDetection]:
        """Detect unusual resource access anomalies."""
        if not profile.typical_resources:
            return None
        
        # Calculate resource similarity
        resource_similarity = 0.0
        for typical_resource in profile.typical_resources:
            # Simple string similarity (could be enhanced with embeddings)
            similarity = self._calculate_string_similarity(event.resource, typical_resource)
            resource_similarity = max(resource_similarity, similarity)
        
        if resource_similarity < self.anomaly_thresholds["resource_deviation"]:
            return AnomalyDetection(
                timestamp=event.timestamp,
                user_id=event.user_id,
                anomaly_type=AnomalyType.UNUSUAL_RESOURCE_ACCESS,
                threat_level=ThreatLevel.MEDIUM,
                confidence=1.0 - resource_similarity,
                description=f"Unusual resource access: {event.resource}",
                contributing_factors=[
                    f"Resource similarity: {resource_similarity:.2f}",
                    f"Typical resources: {profile.typical_resources[:5]}",
                ],
                related_events=[],
                recommended_actions=["Verify access authorization", "Check for data reconnaissance"],
            )
        
        return None
    
    async def _detect_impossible_travel(self, event: BehaviorEvent, profile: UserBehaviorProfile) -> Optional[AnomalyDetection]:
        """Detect impossible travel anomalies."""
        if not event.geo_location or not self.location_tracking[event.user_id]:
            return None
        
        # Get recent locations
        recent_locations = [
            (ts, loc) for ts, loc in self.location_tracking[event.user_id]
            if (event.timestamp - ts).total_seconds() <= 3600  # Last hour
        ]
        
        if len(recent_locations) < 2:
            return None
        
        # Check for impossible travel
        for prev_time, prev_location in recent_locations[:-1]:
            distance = self._calculate_distance(prev_location, event.geo_location)
            time_diff = (event.timestamp - prev_time).total_seconds() / 3600  # hours
            
            if time_diff > 0:
                speed = distance / time_diff  # km/h
                
                if speed > self.config["impossible_travel_speed"]:
                    return AnomalyDetection(
                        timestamp=event.timestamp,
                        user_id=event.user_id,
                        anomaly_type=AnomalyType.IMPOSSIBLE_TRAVEL,
                        threat_level=ThreatLevel.CRITICAL,
                        confidence=min(speed / self.config["impossible_travel_speed"], 1.0),
                        description=f"Impossible travel detected: {speed:.1f} km/h",
                        contributing_factors=[
                            f"Distance: {distance:.1f} km",
                            f"Time: {time_diff:.1f} hours",
                            f"Speed: {speed:.1f} km/h",
                            f"From: {prev_location} to {event.geo_location}",
                        ],
                        related_events=[],
                        recommended_actions=["Block session", "Require immediate re-authentication", "Investigate account compromise"],
                    )
        
        return None
    
    async def _detect_threat_intelligence_match(self, event: BehaviorEvent) -> Optional[AnomalyDetection]:
        """Detect threat intelligence matches."""
        # Check malicious IP
        if event.client_ip in self.malicious_ips:
            return AnomalyDetection(
                timestamp=event.timestamp,
                user_id=event.user_id,
                anomaly_type=AnomalyType.BRUTE_FORCE,
                threat_level=ThreatLevel.CRITICAL,
                confidence=1.0,
                description=f"Access from malicious IP: {event.client_ip}",
                contributing_factors=["IP in threat intelligence database"],
                related_events=[],
                recommended_actions=["Block IP address", "Investigate all activities from this IP"],
            )
        
        # Check suspicious user agent
        for suspicious_ua in self.suspicious_user_agents:
            if suspicious_ua.lower() in event.user_agent.lower():
                return AnomalyDetection(
                    timestamp=event.timestamp,
                    user_id=event.user_id,
                    anomaly_type=AnomalyType.BRUTE_FORCE,
                    threat_level=ThreatLevel.HIGH,
                    confidence=0.8,
                    description=f"Suspicious user agent: {event.user_agent}",
                    contributing_factors=["User agent matches known attack tools"],
                    related_events=[],
                    recommended_actions=["Monitor for automated attacks", "Consider CAPTCHA"],
                )
        
        return None
    
    async def _detect_attack_patterns(self, event: BehaviorEvent) -> Optional[AnomalyDetection]:
        """Detect known attack patterns."""
        # Check in resource and additional data
        content_to_check = event.resource + " " + json.dumps(event.additional_data)
        
        for pattern in self.known_attack_patterns:
            if pattern.search(content_to_check):
                return AnomalyDetection(
                    timestamp=event.timestamp,
                    user_id=event.user_id,
                    anomaly_type=AnomalyType.PRIVILEGE_ESCALATION,
                    threat_level=ThreatLevel.HIGH,
                    confidence=0.9,
                    description=f"Attack pattern detected: {pattern.pattern}",
                    contributing_factors=[f"Pattern matched in: {event.resource}"],
                    related_events=[],
                    recommended_actions=["Block request", "Investigate attack attempt", "Update security rules"],
                )
        
        return None
    
    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """Calculate string similarity using simple character overlap."""
        set1 = set(str1.lower())
        set2 = set(str2.lower())
        intersection = set1 & set2
        union = set1 | set2
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_distance(self, location1: str, location2: str) -> float:
        """Calculate distance between two locations."""
        # Simplified distance calculation
        # In production, use geolocation API with lat/lon coordinates
        if location1 == location2:
            return 0.0
        
        # Mock distance based on location difference
        return 1000.0 if location1 != location2 else 0.0
    
    async def _update_profile(self, profile: UserBehaviorProfile, event: BehaviorEvent):
        """Update user behavior profile."""
        profile.updated_at = datetime.now()
        profile.total_requests += 1
        profile.last_activity = event.timestamp
        
        # Update typical hours
        profile.typical_hours.add(event.timestamp.hour)
        
        # Update typical days
        profile.typical_days.add(event.timestamp.weekday())
        
        # Update typical locations
        if event.geo_location:
            profile.typical_locations.add(event.geo_location)
        
        # Update typical devices
        profile.typical_devices.add(event.device_fingerprint)
        
        # Update typical resources
        if event.resource not in profile.typical_resources:
            profile.typical_resources.append(event.resource)
            # Keep only recent resources
            if len(profile.typical_resources) > 100:
                profile.typical_resources = profile.typical_resources[-50:]
        
        # Update resource access frequency
        profile.resource_access_frequency[event.resource] = profile.resource_access_frequency.get(event.resource, 0) + 1
        
        # Update failed auth count
        if not event.success:
            profile.failed_auth_count += 1
        
        # Recalculate metrics periodically
        if profile.total_requests % 100 == 0:
            await self._recalculate_profile_metrics(profile)
    
    async def _recalculate_profile_metrics(self, profile: UserBehaviorProfile):
        """Recalculate profile metrics."""
        # Calculate average requests per hour
        if profile.total_requests > 0:
            time_span = (profile.updated_at - profile.created_at).total_seconds() / 3600
            profile.avg_requests_per_hour = profile.total_requests / max(time_span, 1)
        
        # Calculate average session duration
        session_durations = []
        for session_id, session_data in self.active_sessions.items():
            if session_data.get("user_id") == profile.user_id:
                duration = (session_data["last_activity"] - session_data["start_time"]).total_seconds()
                session_durations.append(duration)
        
        if session_durations:
            profile.avg_session_duration = statistics.mean(session_durations)
        
        # Update risk score based on anomalies
        recent_anomalies = [
            anomaly for anomaly in self.anomaly_detections
            if (anomaly.user_id == profile.user_id and
                (datetime.now() - anomaly.timestamp).total_seconds() <= 86400)  # Last 24 hours
        ]
        
        if recent_anomalies:
            anomaly_weights = {ThreatLevel.LOW: 0.1, ThreatLevel.MEDIUM: 0.3, ThreatLevel.HIGH: 0.6, ThreatLevel.CRITICAL: 1.0}
            profile.risk_score = sum(anomaly_weights.get(anomaly.threat_level, 0.5) for anomaly in recent_anomalies) / len(recent_anomalies)
            profile.suspicious_activity_count = len(recent_anomalies)
    
    async def _handle_anomaly(self, anomaly: AnomalyDetection):
        """Handle detected anomaly."""
        # Log anomaly
        logger.warning(
            f"Behavioral Anomaly [{anomaly.threat_level.value.upper()}] "
            f"{anomaly.user_id}: {anomaly.description}"
        )
        
        # Take automatic actions for critical threats
        if anomaly.threat_level == ThreatLevel.CRITICAL:
            # In production, this would trigger automated response
            logger.critical(f"CRITICAL THREAT DETECTED: {anomaly.user_id} - {anomaly.description}")
    
    def get_user_profile(self, user_id: str) -> Optional[UserBehaviorProfile]:
        """Get user behavior profile."""
        return self.user_profiles.get(user_id)
    
    def get_recent_anomalies(
        self,
        hours: int = 24,
        user_id: Optional[str] = None,
        threat_level: Optional[ThreatLevel] = None,
    ) -> List[AnomalyDetection]:
        """Get recent anomalies with filtering."""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        anomalies = [
            anomaly for anomaly in self.anomaly_detections
            if anomaly.timestamp >= cutoff
        ]
        
        if user_id:
            anomalies = [a for a in anomalies if a.user_id == user_id]
        
        if threat_level:
            anomalies = [a for a in anomalies if a.threat_level == threat_level]
        
        return sorted(anomalies, key=lambda x: x.timestamp, reverse=True)
    
    def get_behavioral_metrics(self) -> Dict[str, Any]:
        """Get behavioral analysis metrics."""
        now = datetime.now()
        last_hour = now - timedelta(hours=1)
        last_day = now - timedelta(days=1)
        
        # Count recent anomalies
        anomalies_hour = [a for a in self.anomaly_detections if a.timestamp >= last_hour]
        anomalies_day = [a for a in self.anomaly_detections if a.timestamp >= last_day]
        
        # Calculate threat distribution
        threat_distribution = {}
        for anomaly in anomalies_day:
            level = anomaly.threat_level.value
            threat_distribution[level] = threat_distribution.get(level, 0) + 1
        
        # Calculate anomaly type distribution
        type_distribution = {}
        for anomaly in anomalies_day:
            anomaly_type = anomaly.anomaly_type.value
            type_distribution[anomaly_type] = type_distribution.get(anomaly_type, 0) + 1
        
        # Calculate risk scores
        user_risk_scores = {
            user_id: profile.risk_score
            for user_id, profile in self.user_profiles.items()
        ]
        
        avg_risk_score = statistics.mean(user_risk_scores.values()) if user_risk_scores else 0.0
        
        return {
            "total_profiles": len(self.user_profiles),
            "active_sessions": len(self.active_sessions),
            "total_events": len(self.behavior_events),
            "anomalies_last_hour": len(anomalies_hour),
            "anomalies_last_day": len(anomalies_day),
            "threat_distribution": threat_distribution,
            "anomaly_type_distribution": type_distribution,
            "average_risk_score": avg_risk_score,
            "high_risk_users": len([score for score in user_risk_scores.values() if score > 0.7]),
            "malicious_ips": len(self.malicious_ips),
            "suspicious_user_agents": len(self.suspicious_user_agents),
        }
    
    def update_threat_intelligence(self, indicators: List[ThreatIntelligence]):
        """Update threat intelligence data."""
        for indicator in indicators:
            self.threat_intelligence[indicator.indicator] = indicator
            
            # Update relevant collections
            if indicator.indicator_type == "ip":
                if indicator.severity in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                    self.malicious_ips.add(indicator.indicator)
            elif indicator.indicator_type == "user_agent":
                self.suspicious_user_agents.add(indicator.indicator)
    
    def export_profile_data(self, user_id: str) -> Dict[str, Any]:
        """Export user profile data for analysis."""
        profile = self.user_profiles.get(user_id)
        if not profile:
            return {}
        
        # Get user's events
        user_events = [
            event for event in self.behavior_events
            if event.user_id == user_id
        ]
        
        # Get user's anomalies
        user_anomalies = [
            anomaly for anomaly in self.anomaly_detections
            if anomaly.user_id == user_id
        ]
        
        return {
            "profile": asdict(profile),
            "events_count": len(user_events),
            "anomalies_count": len(user_anomalies),
            "recent_anomalies": [
                asdict(anomaly) for anomaly in user_anomalies[-10:]
            ],
            "behavioral_metrics": self._calculate_user_metrics(user_events),
        }
    
    def _calculate_user_metrics(self, events: List[BehaviorEvent]) -> Dict[str, Any]:
        """Calculate behavioral metrics for a user."""
        if not events:
            return {}
        
        # Time-based metrics
        hours = [event.timestamp.hour for event in events]
        days = [event.timestamp.weekday() for event in events]
        
        # Resource access metrics
        resources = [event.resource for event in events]
        unique_resources = len(set(resources))
        
        # Success rate
        successful_events = [e for e in events if e.success]
        success_rate = len(successful_events) / len(events)
        
        # Response time metrics
        response_times = [event.response_time for event in events if event.response_time]
        avg_response_time = statistics.mean(response_times) if response_times else 0.0
        
        return {
            "total_events": len(events),
            "unique_resources": unique_resources,
            "success_rate": success_rate,
            "average_response_time": avg_response_time,
            "most_active_hours": statistics.mode(hours) if hours else None,
            "most_active_days": statistics.mode(days) if days else None,
            "event_span_days": (max(events, key=lambda e: e.timestamp).timestamp - min(events, key=lambda e: e.timestamp).timestamp).days,
        }


# Global behavioral analysis instance
_behavioral_analysis: Optional[BehavioralAnalysis] = None


def get_behavioral_analysis() -> BehavioralAnalysis:
    """Get the global behavioral analysis instance."""
    global _behavioral_analysis
    if _behavioral_analysis is None:
        _behavioral_analysis = BehavioralAnalysis()
    return _behavioral_analysis
