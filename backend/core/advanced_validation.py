"""
Advanced AI-powered request validation system with threat intelligence.
Provides enterprise-grade security validation with machine learning capabilities.
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
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ValidationMode(Enum):
    """Validation operation modes."""
    STRICT = "strict"
    BALANCED = "balanced"
    PERMISSIVE = "permissive"
    LEARNING = "learning"


class AttackPattern(Enum):
    """Common attack patterns."""
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    COMMAND_INJECTION = "command_injection"
    PATH_TRAVERSAL = "path_traversal"
    LDAP_INJECTION = "ldap_injection"
    XXE = "xxe"
    SSRF = "ssrf"
    BUFFER_OVERFLOW = "buffer_overflow"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXFILTRATION = "data_exfiltration"
    DENIAL_OF_SERVICE = "denial_of_service"


@dataclass
class ThreatSignature:
    """Threat signature for pattern matching."""
    
    pattern_id: str
    name: str
    pattern: str
    attack_type: AttackPattern
    severity: ThreatLevel
    confidence: float
    description: str
    mitigation: str
    created_at: datetime
    updated_at: datetime
    active: bool = True


@dataclass
class ValidationResult:
    """Result of validation operation."""
    
    is_valid: bool
    threat_level: ThreatLevel
    confidence: float
    threats_detected: List[Dict[str, Any]]
    risk_score: float
    processing_time: float
    recommendations: List[str]
    metadata: Dict[str, Any]


@dataclass
class ValidationMetrics:
    """Validation performance metrics."""
    
    total_requests: int
    blocked_requests: int
    false_positives: int
    false_negatives: int
    average_processing_time: float
    threat_distribution: Dict[str, int]
    accuracy_rate: float
    precision_rate: float
    recall_rate: float


class ThreatIntelligence:
    """Threat intelligence and pattern recognition system."""
    
    def __init__(self):
        self.threat_signatures: Dict[str, ThreatSignature] = {}
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.scaler = StandardScaler()
        self.threat_history: deque = deque(maxlen=10000)
        self.pattern_frequency = defaultdict(int)
        self._is_trained = False
        
        # Initialize with common threat patterns
        self._initialize_threat_signatures()
    
    def _initialize_threat_signatures(self):
        """Initialize with common attack patterns."""
        signatures = [
            # SQL Injection patterns
            ThreatSignature(
                pattern_id="sql_injection_1",
                name="Union-based SQL Injection",
                pattern=r"(?i)(union\s+select|select\s+.*\s+from\s+.*\s+union)",
                attack_type=AttackPattern.SQL_INJECTION,
                severity=ThreatLevel.HIGH,
                confidence=0.95,
                description="Union-based SQL injection attempt detected",
                mitigation="Parameterized queries and input validation",
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            ThreatSignature(
                pattern_id="sql_injection_2",
                name="Boolean-based SQL Injection",
                pattern=r"(?i)(\s+and\s+1\s*=\s*1|\s+or\s+1\s*=\s*1|'\s*or\s*'1'\s*=\s*'1)",
                attack_type=AttackPattern.SQL_INJECTION,
                severity=ThreatLevel.HIGH,
                confidence=0.90,
                description="Boolean-based SQL injection attempt detected",
                mitigation="Input validation and parameterized queries",
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            
            # XSS patterns
            ThreatSignature(
                pattern_id="xss_1",
                name="Script Injection",
                pattern=r"(?i)(<script[^>]*>.*?</script>|javascript:|on\w+\s*=)",
                attack_type=AttackPattern.XSS,
                severity=ThreatLevel.HIGH,
                confidence=0.95,
                description="Cross-site scripting attempt detected",
                mitigation="Output encoding and CSP headers",
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            ThreatSignature(
                pattern_id="xss_2",
                name="DOM-based XSS",
                pattern=r"(?i)(document\.|window\.|eval\s*\(|setTimeout\s*\(|setInterval\s*\()",
                attack_type=AttackPattern.XSS,
                severity=ThreatLevel.MEDIUM,
                confidence=0.85,
                description="DOM-based XSS attempt detected",
                mitigation="Input validation and output encoding",
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            
            # Command Injection patterns
            ThreatSignature(
                pattern_id="command_injection_1",
                name="Shell Command Injection",
                pattern=r"(?i)(;\s*(cat|ls|dir|whoami|id|pwd)\s*|;\s*(rm|del|mv|cp)\s*|`\s*[^`]*\s*`)",
                attack_type=AttackPattern.COMMAND_INJECTION,
                severity=ThreatLevel.CRITICAL,
                confidence=0.98,
                description="Command injection attempt detected",
                mitigation="Input validation and command whitelisting",
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            
            # Path Traversal patterns
            ThreatSignature(
                pattern_id="path_traversal_1",
                name="Directory Traversal",
                pattern=r"(?i)(\.\./|\.\.\\|%2e%2e%2f|%2e%2e%5c|\.\.%2f|\.\.%5c)",
                attack_type=AttackPattern.PATH_TRAVERSAL,
                severity=ThreatLevel.HIGH,
                confidence=0.92,
                description="Path traversal attempt detected",
                mitigation="Input validation and path normalization",
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            
            # SSRF patterns
            ThreatSignature(
                pattern_id="ssrf_1",
                name="Server-Side Request Forgery",
                pattern=r"(?i)(http://localhost|https://localhost|http://127\.0\.0\.1|https://127\.0\.0\.1|file://)",
                attack_type=AttackPattern.SSRF,
                severity=ThreatLevel.HIGH,
                confidence=0.88,
                description="SSRF attempt detected",
                mitigation="URL validation and allowlist",
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            
            # Data Exfiltration patterns
            ThreatSignature(
                pattern_id="data_exfil_1",
                name="Data Exfiltration",
                pattern=r"(?i)(select\s+.*\s+from\s+users|dump\s+database|export\s+all|backup\s+.*\s+to)",
                attack_type=AttackPattern.DATA_EXFILTRATION,
                severity=ThreatLevel.CRITICAL,
                confidence=0.90,
                description="Data exfiltration attempt detected",
                mitigation="Access controls and data loss prevention",
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
        ]
        
        for sig in signatures:
            self.threat_signatures[sig.pattern_id] = sig
    
    def analyze_request(self, request_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze request for threats using pattern matching."""
        threats = []
        request_text = self._extract_text_from_request(request_data)
        
        for signature in self.threat_signatures.values():
            if not signature.active:
                continue
            
            try:
                matches = re.finditer(signature.pattern, request_text, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    threat = {
                        "pattern_id": signature.pattern_id,
                        "attack_type": signature.attack_type.value,
                        "severity": signature.severity.value,
                        "confidence": signature.confidence,
                        "description": signature.description,
                        "mitigation": signature.mitigation,
                        "matched_text": match.group(),
                        "position": match.span(),
                        "timestamp": datetime.now().isoformat()
                    }
                    threats.append(threat)
                    self.pattern_frequency[signature.pattern_id] += 1
            except re.error as e:
                logger.warning(f"Regex error in pattern {signature.pattern_id}: {e}")
        
        return threats
    
    def _extract_text_from_request(self, request_data: Dict[str, Any]) -> str:
        """Extract text content from request data."""
        text_parts = []
        
        def extract_text(obj):
            if isinstance(obj, str):
                text_parts.append(obj)
            elif isinstance(obj, dict):
                for value in obj.values():
                    extract_text(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_text(item)
        
        extract_text(request_data)
        return " ".join(text_parts)
    
    def detect_anomalies(self, request_features: List[float]) -> bool:
        """Detect anomalies in request patterns."""
        if not self._is_trained or len(request_features) == 0:
            return False
        
        try:
            # Reshape for sklearn
            features_array = np.array(request_features).reshape(1, -1)
            
            # Predict anomaly (-1 for anomaly, 1 for normal)
            prediction = self.anomaly_detector.predict(features_array)[0]
            return prediction == -1
        except Exception as e:
            logger.error(f"Anomaly detection error: {e}")
            return False
    
    def train_anomaly_detector(self, training_data: List[List[float]]):
        """Train the anomaly detection model."""
        if len(training_data) < 10:
            logger.warning("Insufficient training data for anomaly detection")
            return
        
        try:
            # Prepare training data
            X = np.array(training_data)
            
            # Train the model
            self.anomaly_detector.fit(X)
            self._is_trained = True
            
            logger.info(f"Anomaly detector trained with {len(training_data)} samples")
        except Exception as e:
            logger.error(f"Failed to train anomaly detector: {e}")
    
    def add_threat_signature(self, signature: ThreatSignature):
        """Add a new threat signature."""
        self.threat_signatures[signature.pattern_id] = signature
        logger.info(f"Added threat signature: {signature.name}")
    
    def update_threat_signature(self, pattern_id: str, **kwargs):
        """Update an existing threat signature."""
        if pattern_id not in self.threat_signatures:
            logger.warning(f"Threat signature {pattern_id} not found")
            return
        
        signature = self.threat_signatures[pattern_id]
        for key, value in kwargs.items():
            if hasattr(signature, key):
                setattr(signature, key, value)
        
        signature.updated_at = datetime.now()
        logger.info(f"Updated threat signature: {pattern_id}")
    
    def get_threat_statistics(self) -> Dict[str, Any]:
        """Get threat intelligence statistics."""
        total_signatures = len(self.threat_signatures)
        active_signatures = sum(1 for sig in self.threat_signatures.values() if sig.active)
        
        severity_distribution = defaultdict(int)
        attack_type_distribution = defaultdict(int)
        
        for sig in self.threat_signatures.values():
            if sig.active:
                severity_distribution[sig.severity.value] += 1
                attack_type_distribution[sig.attack_type.value] += 1
        
        return {
            "total_signatures": total_signatures,
            "active_signatures": active_signatures,
            "severity_distribution": dict(severity_distribution),
            "attack_type_distribution": dict(attack_type_distribution),
            "pattern_frequency": dict(self.pattern_frequency),
            "is_trained": self._is_trained,
            "threat_history_size": len(self.threat_history)
        }


class AdvancedValidator:
    """Advanced AI-powered request validator."""
    
    def __init__(self, mode: ValidationMode = ValidationMode.BALANCED):
        self.mode = mode
        self.threat_intel = ThreatIntelligence()
        self.validation_cache: Dict[str, Tuple[ValidationResult, datetime]] = {}
        self.metrics = ValidationMetrics(
            total_requests=0,
            blocked_requests=0,
            false_positives=0,
            false_negatives=0,
            average_processing_time=0.0,
            threat_distribution={},
            accuracy_rate=0.0,
            precision_rate=0.0,
            recall_rate=0.0
        )
        
        # Performance tracking
        self.request_history: deque = deque(maxlen=1000)
        self.threat_history: deque = deque(maxlen=1000)
        
        # AI Model components
        self.risk_calculator = self._initialize_risk_calculator()
        
        logger.info(f"AdvancedValidator initialized in {mode.value} mode")
    
    def _initialize_risk_calculator(self):
        """Initialize risk calculation model."""
        # This would typically load a trained model
        # For now, using rule-based risk calculation
        return {
            "weights": {
                "threat_count": 0.3,
                "severity": 0.25,
                "confidence": 0.2,
                "anomaly_score": 0.15,
                "reputation": 0.1
            },
            "thresholds": {
                "low": 0.3,
                "medium": 0.6,
                "high": 0.8,
                "critical": 0.9
            }
        }
    
    async def validate_request(
        self,
        request_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Perform comprehensive request validation."""
        start_time = time.time()
        
        try:
            # Generate request fingerprint for caching
            fingerprint = self._generate_fingerprint(request_data)
            
            # Check cache first
            if fingerprint in self.validation_cache:
                cached_result, cached_time = self.validation_cache[fingerprint]
                if (datetime.now() - cached_time).total_seconds() < 300:  # 5 minutes cache
                    return cached_result
            
            # Extract features for ML analysis
            features = self._extract_features(request_data, context)
            
            # Pattern-based threat detection
            threats = self.threat_intel.analyze_request(request_data)
            
            # Anomaly detection
            is_anomaly = self.threat_intel.detect_anomalies(features)
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(threats, features, is_anomaly, context)
            
            # Determine threat level
            threat_level = self._determine_threat_level(risk_score)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(threats, risk_score)
            
            # Create validation result
            result = ValidationResult(
                is_valid=risk_score < self._get_mode_threshold(),
                threat_level=threat_level,
                confidence=self._calculate_confidence(threats, risk_score),
                threats_detected=threats,
                risk_score=risk_score,
                processing_time=time.time() - start_time,
                recommendations=recommendations,
                metadata={
                    "fingerprint": fingerprint,
                    "features": features,
                    "is_anomaly": is_anomaly,
                    "mode": self.mode.value
                }
            )
            
            # Cache result
            self.validation_cache[fingerprint] = (result, datetime.now())
            
            # Update metrics
            self._update_metrics(result)
            
            # Store in history
            self.request_history.append({
                "timestamp": datetime.now(),
                "fingerprint": fingerprint,
                "result": asdict(result)
            })
            
            if threats:
                self.threat_history.extend(threats)
            
            return result
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            # Fail safe - block on validation errors
            return ValidationResult(
                is_valid=False,
                threat_level=ThreatLevel.HIGH,
                confidence=1.0,
                threats_detected=[],
                risk_score=1.0,
                processing_time=time.time() - start_time,
                recommendations=["Validation system error - request blocked"],
                metadata={"error": str(e)}
            )
    
    def _generate_fingerprint(self, request_data: Dict[str, Any]) -> str:
        """Generate unique fingerprint for request caching."""
        # Create normalized representation
        normalized = json.dumps(request_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]
    
    def _extract_features(self, request_data: Dict[str, Any], context: Optional[Dict[str, Any]]) -> List[float]:
        """Extract numerical features for ML analysis."""
        features = []
        
        # Text-based features
        text_content = self.threat_intel._extract_text_from_request(request_data)
        features.append(len(text_content))  # Text length
        features.append(len(text_content.split()))  # Word count
        features.append(len(set(text_content.lower().split())))  # Unique words
        features.append(text_content.count('<'))  # HTML tags
        features.append(text_content.count('('))  # Parentheses
        features.append(text_content.count(';'))  # Semicolons
        features.append(text_content.count('='))  # Equals signs
        features.append(text_content.count('/'))  # Forward slashes
        features.append(text_content.count('\\'))  # Backslashes
        features.append(text_content.count('.'))  # Dots
        
        # Structural features
        features.append(len(str(request_data)))  # Request size
        features.append(len(request_data.keys()))  # Number of fields
        
        # Context features
        if context:
            features.append(float(context.get("user_trust_score", 0.5)))
            features.append(float(context.get("session_age", 0)))
            features.append(float(context.get("request_frequency", 0)))
        else:
            features.extend([0.5, 0, 0])  # Default context values
        
        return features
    
    def _calculate_risk_score(
        self,
        threats: List[Dict[str, Any]],
        features: List[float],
        is_anomaly: bool,
        context: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate overall risk score."""
        weights = self.risk_calculator["weights"]
        
        # Threat count component
        threat_score = min(len(threats) / 10.0, 1.0) * weights["threat_count"]
        
        # Severity component
        severity_score = 0.0
        for threat in threats:
            severity_multiplier = {
                "low": 0.1,
                "medium": 0.3,
                "high": 0.6,
                "critical": 1.0
            }.get(threat["severity"], 0.0)
            severity_score = max(severity_score, severity_multiplier)
        severity_score *= weights["severity"]
        
        # Confidence component
        avg_confidence = np.mean([t.get("confidence", 0.0) for t in threats]) if threats else 0.0
        confidence_score = avg_confidence * weights["confidence"]
        
        # Anomaly component
        anomaly_score = 1.0 if is_anomaly else 0.0
        anomaly_score *= weights["anomaly_score"]
        
        # Reputation component (from context)
        reputation_score = 0.0
        if context:
            user_trust = context.get("user_trust_score", 0.5)
            reputation_score = (1.0 - user_trust) * weights["reputation"]
        
        total_score = threat_score + severity_score + confidence_score + anomaly_score + reputation_score
        return min(total_score, 1.0)
    
    def _determine_threat_level(self, risk_score: float) -> ThreatLevel:
        """Determine threat level from risk score."""
        thresholds = self.risk_calculator["thresholds"]
        
        if risk_score >= thresholds["critical"]:
            return ThreatLevel.CRITICAL
        elif risk_score >= thresholds["high"]:
            return ThreatLevel.HIGH
        elif risk_score >= thresholds["medium"]:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW
    
    def _calculate_confidence(self, threats: List[Dict[str, Any]], risk_score: float) -> float:
        """Calculate confidence in validation result."""
        if not threats:
            return 0.5  # Low confidence for clean requests
        
        # Average confidence from detected threats
        threat_confidence = np.mean([t.get("confidence", 0.0) for t in threats])
        
        # Adjust based on risk score
        confidence_adjustment = min(risk_score * 0.2, 0.2)
        
        return min(threat_confidence + confidence_adjustment, 1.0)
    
    def _generate_recommendations(self, threats: List[Dict[str, Any]], risk_score: float) -> List[str]:
        """Generate security recommendations."""
        recommendations = []
        
        if risk_score >= 0.8:
            recommendations.append("Block request immediately - critical threat detected")
        elif risk_score >= 0.6:
            recommendations.append("Require additional authentication")
        elif risk_score >= 0.3:
            recommendations.append("Monitor request closely")
        
        # Specific recommendations based on threat types
        threat_types = set(t.get("attack_type") for t in threats)
        
        if "sql_injection" in threat_types:
            recommendations.append("Implement parameterized queries")
        
        if "xss" in threat_types:
            recommendations.append("Apply output encoding and CSP headers")
        
        if "command_injection" in threat_types:
            recommendations.append("Use command whitelisting and input validation")
        
        if "path_traversal" in threat_types:
            recommendations.append("Normalize file paths and validate input")
        
        if "ssrf" in threat_types:
            recommendations.append("Implement URL allowlist and validation")
        
        return recommendations
    
    def _get_mode_threshold(self) -> float:
        """Get risk threshold based on validation mode."""
        thresholds = {
            ValidationMode.STRICT: 0.2,
            ValidationMode.BALANCED: 0.5,
            ValidationMode.PERMISSIVE: 0.7,
            ValidationMode.LEARNING: 0.9
        }
        return thresholds.get(self.mode, 0.5)
    
    def _update_metrics(self, result: ValidationResult):
        """Update validation metrics."""
        self.metrics.total_requests += 1
        
        if not result.is_valid:
            self.metrics.blocked_requests += 1
        
        # Update threat distribution
        for threat in result.threats_detected:
            attack_type = threat.get("attack_type", "unknown")
            self.metrics.threat_distribution[attack_type] = \
                self.metrics.threat_distribution.get(attack_type, 0) + 1
        
        # Update average processing time
        total_time = self.metrics.average_processing_time * (self.metrics.total_requests - 1)
        self.metrics.average_processing_time = \
            (total_time + result.processing_time) / self.metrics.total_requests
    
    def get_metrics(self) -> ValidationMetrics:
        """Get current validation metrics."""
        return self.metrics
    
    def get_validation_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Filter recent requests
        recent_requests = [
            req for req in self.request_history
            if req["timestamp"] >= cutoff_time
        ]
        
        # Filter recent threats
        recent_threats = [
            threat for threat in self.threat_history
            if datetime.fromisoformat(threat["timestamp"]) >= cutoff_time
        ]
        
        # Calculate statistics
        total_requests = len(recent_requests)
        blocked_requests = sum(1 for req in recent_requests if not req["result"]["is_valid"])
        
        threat_distribution = defaultdict(int)
        severity_distribution = defaultdict(int)
        
        for threat in recent_threats:
            attack_type = threat.get("attack_type", "unknown")
            severity = threat.get("severity", "unknown")
            threat_distribution[attack_type] += 1
            severity_distribution[severity] += 1
        
        return {
            "period_hours": hours,
            "total_requests": total_requests,
            "blocked_requests": blocked_requests,
            "block_rate": blocked_requests / max(total_requests, 1),
            "threat_distribution": dict(threat_distribution),
            "severity_distribution": dict(severity_distribution),
            "average_processing_time": self.metrics.average_processing_time,
            "validation_mode": self.mode.value,
            "cache_size": len(self.validation_cache),
            "threat_intelligence": self.threat_intel.get_threat_statistics()
        }
    
    def train_models(self, training_data: List[Dict[str, Any]]):
        """Train ML models with historical data."""
        try:
            # Extract features for anomaly detection
            features_list = []
            for data in training_data:
                features = self._extract_features(
                    data.get("request", {}),
                    data.get("context")
                )
                features_list.append(features)
            
            # Train anomaly detector
            self.threat_intel.train_anomaly_detector(features_list)
            
            logger.info(f"Models trained with {len(training_data)} samples")
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
    
    def update_mode(self, mode: ValidationMode):
        """Update validation mode."""
        self.mode = mode
        logger.info(f"Validation mode updated to {mode.value}")
    
    def clear_cache(self):
        """Clear validation cache."""
        self.validation_cache.clear()
        logger.info("Validation cache cleared")


# Global validator instance
_advanced_validator: Optional[AdvancedValidator] = None


def get_advanced_validator(mode: ValidationMode = ValidationMode.BALANCED) -> AdvancedValidator:
    """Get the global advanced validator instance."""
    global _advanced_validator
    if _advanced_validator is None:
        _advanced_validator = AdvancedValidator(mode)
    return _advanced_validator


async def validate_request_advanced(
    request_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None,
    mode: ValidationMode = ValidationMode.BALANCED
) -> ValidationResult:
    """Validate request using advanced AI-powered validation (convenience function)."""
    validator = get_advanced_validator(mode)
    return await validator.validate_request(request_data, context)


def get_validation_metrics() -> ValidationMetrics:
    """Get validation metrics (convenience function)."""
    validator = get_advanced_validator()
    return validator.get_metrics()


def get_validation_report(hours: int = 24) -> Dict[str, Any]:
    """Get validation report (convenience function)."""
    validator = get_advanced_validator()
    return validator.get_validation_report(hours)
