"""
Contradiction Detector Agent
Enhanced system for identifying inconsistencies and contradictions in extracted facts from internal documents
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import re
from difflib import SequenceMatcher
import asyncio
from datetime import datetime
from collections import defaultdict, Counter
import hashlib

logger = logging.getLogger(__name__)


class ContradictionType(Enum):
    """Types of contradictions that can be detected"""
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    TEMPORAL = "temporal"
    LOGICAL = "logical"
    SEMANTIC = "semantic"
    FINANCIAL = "financial"
    POSITIONING = "positioning"
    TEAM = "team"
    MARKET = "market"
    PRODUCT = "product"
    COMPETITIVE = "competitive"


class ContradictionSeverity(Enum):
    """Severity levels for contradictions"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Contradiction:
    """Represents a detected contradiction"""
    id: str
    type: ContradictionType
    severity: ContradictionSeverity
    description: str
    conflicting_facts: List[str]  # Fact IDs
    confidence: float
    explanation: str
    suggested_resolution: Optional[str]
    auto_resolvable: bool


@dataclass
class ContradictionReport:
    """Report of all detected contradictions"""
    contradictions: List[Contradiction]
    total_facts_analyzed: int
    contradiction_count: int
    severity_distribution: Dict[str, int]
    type_distribution: Dict[str, int]
    auto_resolvable_count: int
    recommendations: List[str]


class ContradictionDetector:
    """Enhanced AI-powered contradiction detection specialist for internal document analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.contradiction_counter = 0
        self.numerical_patterns = self._load_numerical_patterns()
        self.temporal_patterns = self._load_temporal_patterns()
        self.semantic_groups = self._load_semantic_groups()
        self.financial_patterns = self._load_financial_patterns()
        self.positioning_patterns = self._load_positioning_patterns()
        self.team_patterns = self._load_team_patterns()
        self.detection_history = []
        self.confidence_thresholds = {
            "numerical": 0.7,
            "categorical": 0.6,
            "temporal": 0.8,
            "logical": 0.5,
            "semantic": 0.4,
            "financial": 0.8,
            "positioning": 0.6,
            "team": 0.7,
            "market": 0.5,
            "competitive": 0.6
        }
    
    def _load_numerical_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for numerical contradiction detection"""
        return {
            "revenue": [
                r"\$?([0-9,.]+)\s*(?:million|billion|thousand)?\s*(?:revenue|income|sales|arr|mrr)",
                r"(?:revenue|income|sales|arr|mrr).*?\$?([0-9,.]+)\s*(?:million|billion|thousand)?"
            ],
            "employees": [
                r"([0-9]+)\s*(?:employees|staff|team|people)",
                r"(?:employees|staff|team|people).*?([0-9]+)"
            ],
            "users": [
                r"([0-9,]+)\s*(?:users|customers|clients)",
                r"(?:users|customers|clients).*?([0-9,]+)"
            ],
            "funding": [
                r"\$?([0-9,.]+)\s*(?:million|billion|thousand)?\s*(?:funding|investment|round)",
                r"(?:funding|investment|round).*?\$?([0-9,.]+)\s*(?:million|billion|thousand)?"
            ],
            "growth": [
                r"([0-9]+)%\s*(?:growth|increase|decrease)",
                r"(?:growth|increase|decrease).*?([0-9]+)%"
            ]
        }
    
    def _load_temporal_patterns(self) -> List[str]:
        """Load patterns for temporal contradiction detection"""
        return [
            r"(?:founded|established|started|created|launched)\s*(?:in|on)?\s*([0-9]{4})",
            r"(?:since|from|in|on)\s*([0-9]{4})",
            r"([0-9]{4})\s*(?:to|until|-)\s*([0-9]{4})"
        ]
    
    def _load_semantic_groups(self) -> Dict[str, Set[str]]:
        """Load semantic groups for detecting categorical contradictions"""
        return {
            "company_type": {
                "startup", "company", "business", "enterprise", "corporation", 
                "firm", "organization", "venture", "initiative"
            },
            "product_type": {
                "platform", "software", "app", "application", "tool", "service",
                "solution", "system", "product", "technology"
            },
            "market_segment": {
                "b2b", "b2c", "enterprise", "smb", "small business", "mid-market",
                "large enterprise", "consumer", "commercial"
            },
            "business_model": {
                "saas", "subscription", "freemium", "licensing", "transactional",
                "marketplace", "advertising", "commission"
            }
        }
    
    def _load_financial_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for financial contradiction detection"""
        return {
            "revenue_model": [
                r"(?:revenue|income|sales).*?(?:subscription|recurring|one-time|transactional)",
                r"(?:subscription|recurring|one-time|transactional).*?(?:revenue|income|sales)"
            ],
            "pricing": [
                r"\$?([0-9,.]+)\s*(?:per|\/)\s*(?:month|year|user|seat)",
                r"(?:pricing|price|cost).*?\$?([0-9,.]+)"
            ],
            "profitability": [
                r"(?:profitable|profit|margin).*?(?:positive|negative|break-even)",
                r"(?:positive|negative|break-even).*?(?:profitable|profit|margin)"
            ],
            "funding_status": [
                r"(?:funded|bootstrapped|self-funded|venture|angel)",
                r"(?:seed|series|round).*?\$?([0-9,.]+)"
            ]
        }
    
    def _load_positioning_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for positioning contradiction detection"""
        return {
            "market_position": [
                r"(?:leader|market leader|number one|top|first)",
                r"(?:challenger|follower|niche|specialized)",
                r"(?:disruptor|innovator|game-changer)"
            ],
            "differentiation": [
                r"(?:unique|different|special|proprietary)",
                r"(?:commodity|standard|similar|like)",
                r"(?:better|superior|premium|luxury)"
            ],
            "target_audience": [
                r"(?:for|targeting|serving)\s+([a-z\s]+)",
                r"(?:market|audience|customers).*?(?:enterprise|smb|consumer)"
            ]
        }
    
    def _load_team_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for team contradiction detection"""
        return {
            "team_size": [
                r"([0-9]+)\s*(?:employees|staff|team|people|members)",
                r"(?:team|staff|employees).*?([0-9]+)"
            ],
            "leadership": [
                r"(?:ceo|founder|co-founder|president).*?([A-Za-z\s]+)",
                r"(?:led by|founded by|created by).*?([A-Za-z\s]+)"
            ],
            "experience": [
                r"(?:experience|background|history).*?([0-9]+)\s*(?:years|yrs)",
                r"([0-9]+)\s*(?:years|yrs).*?(?:experience|background)"
            ]
        }
    
    def _generate_contradiction_id(self) -> str:
        """Generate unique contradiction ID"""
        self.contradiction_counter += 1
        return f"CONTR-{self.contradiction_counter:03d}"
    
    def _parse_numerical_value(self, text: str) -> Optional[float]:
        """Parse numerical value from text"""
        # Remove commas and convert to float
        cleaned = re.sub(r'[,$]', '', text)
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    def _normalize_numerical_value(self, value: float, context: str = "") -> float:
        """Normalize numerical values to consistent scale"""
        # Handle millions, billions, thousands
        if "million" in context.lower():
            return value * 1_000_000
        elif "billion" in context.lower():
            return value * 1_000_000_000
        elif "thousand" in context.lower():
            return value * 1_000
        return value
    
    def _detect_numerical_contradictions(self, facts: List[Dict[str, Any]]) -> List[Contradiction]:
        """Detect contradictions in numerical facts"""
        contradictions = []
        
        # Group facts by category
        category_groups = {}
        for fact in facts:
            category = fact.get("category", "").lower()
            if category not in category_groups:
                category_groups[category] = []
            category_groups[category].append(fact)
        
        # Check each category for numerical contradictions
        for category, category_facts in category_groups.items():
            if category in self.numerical_patterns:
                numerical_values = []
                
                for fact in category_facts:
                    value = fact.get("value", "")
                    
                    # Try to extract numerical value
                    for pattern in self.numerical_patterns[category]:
                        matches = re.findall(pattern, value, re.IGNORECASE)
                        for match in matches:
                            if isinstance(match, tuple):
                                match = match[0] if match[0] else match[1]
                            
                            num_value = self._parse_numerical_value(match)
                            if num_value is not None:
                                normalized = self._normalize_numerical_value(num_value, value)
                                numerical_values.append({
                                    "fact_id": fact.get("id"),
                                    "value": normalized,
                                    "original": match,
                                    "confidence": fact.get("confidence", 0.5)
                                })
                
                # Check for contradictions (values that differ significantly)
                if len(numerical_values) > 1:
                    for i in range(len(numerical_values)):
                        for j in range(i + 1, len(numerical_values)):
                            val1, val2 = numerical_values[i], numerical_values[j]
                            
                            # Calculate percentage difference
                            if val1["value"] > 0 and val2["value"] > 0:
                                diff_percent = abs(val1["value"] - val2["value"]) / max(val1["value"], val2["value"])
                                
                                if diff_percent > 0.2:  # 20% difference threshold
                                    severity = ContradictionSeverity.CRITICAL if diff_percent > 0.5 else \
                                              ContradictionSeverity.HIGH if diff_percent > 0.3 else \
                                              ContradictionSeverity.MEDIUM
                                    
                                    contradiction = Contradiction(
                                        id=self._generate_contradiction_id(),
                                        type=ContradictionType.NUMERICAL,
                                        severity=severity,
                                        description=f"Significant difference in {category} values",
                                        conflicting_facts=[val1["fact_id"], val2["fact_id"]],
                                        confidence=min(val1["confidence"], val2["confidence"]),
                                        explanation=f"Values differ by {diff_percent:.1%}: {val1['original']} vs {val2['original']}",
                                        suggested_resolution="Verify which value is correct or if they represent different time periods",
                                        auto_resolvable=False
                                    )
                                    contradictions.append(contradiction)
        
        return contradictions
    
    def _detect_categorical_contradictions(self, facts: List[Dict[str, Any]]) -> List[Contradiction]:
        """Detect contradictions in categorical facts"""
        contradictions = []
        
        # Group facts by semantic groups
        for group_name, semantic_set in self.semantic_groups.items():
            group_facts = []
            
            for fact in facts:
                value = fact.get("value", "").lower()
                category = fact.get("category", "").lower()
                
                # Check if fact belongs to this semantic group
                if any(word in value for word in semantic_set) or \
                   any(word in category for word in semantic_set):
                    group_facts.append(fact)
            
            # Check for mutually exclusive values
            if len(group_facts) > 1:
                # Extract the specific semantic terms from each fact
                fact_terms = []
                for fact in group_facts:
                    value = fact.get("value", "").lower()
                    found_terms = [term for term in semantic_set if term in value]
                    if found_terms:
                        fact_terms.append({
                            "fact_id": fact.get("id"),
                            "terms": found_terms,
                            "confidence": fact.get("confidence", 0.5)
                        })
                
                # Check for contradictions (different terms in same group)
                for i in range(len(fact_terms)):
                    for j in range(i + 1, len(fact_terms)):
                        terms1, terms2 = set(fact_terms[i]["terms"]), set(fact_terms[j]["terms"])
                        
                        # If terms don't overlap significantly, it might be a contradiction
                        overlap = len(terms1.intersection(terms2))
                        if overlap == 0:  # No overlap
                            contradiction = Contradiction(
                                id=self._generate_contradiction_id(),
                                type=ContradictionType.CATEGORICAL,
                                severity=ContradictionSeverity.MEDIUM,
                                description=f"Different {group_name} classifications",
                                conflicting_facts=[fact_terms[i]["fact_id"], fact_terms[j]["fact_id"]],
                                confidence=min(fact_terms[i]["confidence"], fact_terms[j]["confidence"]),
                                explanation=f"One fact mentions {list(fact_terms[i]['terms'])[0]}, another mentions {list(fact_terms[j]['terms'])[0]}",
                                suggested_resolution="Clarify if these represent different aspects or choose the most accurate classification",
                                auto_resolvable=False
                            )
                            contradictions.append(contradiction)
        
        return contradictions
    
    def _detect_temporal_contradictions(self, facts: List[Dict[str, Any]]) -> List[Contradiction]:
        """Detect contradictions in temporal facts"""
        contradictions = []
        
        # Extract years from facts
        temporal_facts = []
        for fact in facts:
            value = fact.get("value", "")
            
            for pattern in self.temporal_patterns:
                matches = re.findall(pattern, value, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        years = [int(year) for year in match if year.isdigit()]
                    else:
                        years = [int(match)] if match.isdigit() else []
                    
                    for year in years:
                        temporal_facts.append({
                            "fact_id": fact.get("id"),
                            "year": year,
                            "context": value,
                            "confidence": fact.get("confidence", 0.5)
                        })
        
        # Check for temporal contradictions
        if len(temporal_facts) > 1:
            for i in range(len(temporal_facts)):
                for j in range(i + 1, len(temporal_facts)):
                    fact1, fact2 = temporal_facts[i], temporal_facts[j]
                    
                    # Check for same event with different years
                    if abs(fact1["year"] - fact2["year"]) > 1:  # More than 1 year difference
                        severity = ContradictionSeverity.HIGH if abs(fact1["year"] - fact2["year"]) > 5 else ContradictionSeverity.MEDIUM
                        
                        contradiction = Contradiction(
                            id=self._generate_contradiction_id(),
                            type=ContradictionType.TEMPORAL,
                            severity=severity,
                            description="Inconsistent temporal information",
                            conflicting_facts=[fact1["fact_id"], fact2["fact_id"]],
                            confidence=min(fact1["confidence"], fact2["confidence"]),
                            explanation=f"One fact mentions {fact1['year']}, another mentions {fact2['year']}",
                            suggested_resolution="Verify the correct date or clarify if they refer to different events",
                            auto_resolvable=False
                        )
                        contradictions.append(contradiction)
        
        return contradictions
    
    def _detect_semantic_contradictions(self, facts: List[Dict[str, Any]]) -> List[Contradiction]:
        """Detect semantic contradictions using text similarity"""
        contradictions = []
        
        # Group facts by category
        category_groups = {}
        for fact in facts:
            category = fact.get("category", "")
            if category not in category_groups:
                category_groups[category] = []
            category_groups[category].append(fact)
        
        # Check for semantic contradictions within each category
        for category, category_facts in category_groups.items():
            if len(category_facts) > 1:
                for i in range(len(category_facts)):
                    for j in range(i + 1, len(category_facts)):
                        fact1, fact2 = category_facts[i], category_facts[j]
                        
                        # Calculate semantic similarity
                        value1, value2 = fact1.get("value", ""), fact2.get("value", "")
                        similarity = SequenceMatcher(None, value1.lower(), value2.lower()).ratio()
                        
                        # If similarity is low but category is same, might be contradiction
                        if similarity < 0.3:  # Low similarity threshold
                            contradiction = Contradiction(
                                id=self._generate_contradiction_id(),
                                type=ContradictionType.SEMANTIC,
                                severity=ContradictionSeverity.LOW,
                                description=f"Low semantic similarity in {category}",
                                conflicting_facts=[fact1.get("id"), fact2.get("id")],
                                confidence=min(fact1.get("confidence", 0.5), fact2.get("confidence", 0.5)),
                                explanation=f"Values in same category have low similarity ({similarity:.2f})",
                                suggested_resolution="Review if these facts should be in different categories or if one is incorrect",
                                auto_resolvable=False
                            )
                            contradictions.append(contradiction)
        
        return contradictions
    
    def _detect_financial_contradictions(self, facts: List[Dict[str, Any]]) -> List[Contradiction]:
        """Detect contradictions in financial facts"""
        contradictions = []
        
        # Group facts by financial category
        financial_facts = defaultdict(list)
        for fact in facts:
            category = fact.get("category", "").lower()
            value = fact.get("value", "").lower()
            
            for pattern_name, patterns in self.financial_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        financial_facts[pattern_name].append(fact)
                        break
        
        # Check for contradictions in each financial category
        for category, category_facts in financial_facts.items():
            if len(category_facts) > 1:
                # Revenue model contradictions
                if category == "revenue_model":
                    models = []
                    for fact in category_facts:
                        value = fact.get("value", "").lower()
                        if "subscription" in value:
                            models.append("subscription")
                        elif "recurring" in value:
                            models.append("recurring")
                        elif "one-time" in value:
                            models.append("one-time")
                        elif "transactional" in value:
                            models.append("transactional")
                    
                    if len(set(models)) > 1:
                        contradiction = Contradiction(
                            id=self._generate_contradiction_id(),
                            type=ContradictionType.FINANCIAL,
                            severity=ContradictionSeverity.HIGH,
                            description="Inconsistent revenue model",
                            conflicting_facts=[f.get("id") for f in category_facts],
                            confidence=sum(f.get("confidence", 0.5) for f in category_facts) / len(category_facts),
                            explanation=f"Multiple revenue models mentioned: {', '.join(set(models))}",
                            suggested_resolution="Clarify the primary revenue model or explain different revenue streams",
                            auto_resolvable=False
                        )
                        contradictions.append(contradiction)
                
                # Pricing contradictions
                elif category == "pricing":
                    prices = []
                    for fact in category_facts:
                        value = fact.get("value", "")
                        price_match = re.search(r'\$?([0-9,.]+)', value)
                        if price_match:
                            price = self._parse_numerical_value(price_match.group(1))
                            if price:
                                prices.append(price)
                    
                    if len(prices) > 1:
                        # Check for significant price differences
                        max_price = max(prices)
                        min_price = min(prices)
                        if max_price / min_price > 2:  # More than 2x difference
                            contradiction = Contradiction(
                                id=self._generate_contradiction_id(),
                                type=ContradictionType.FINANCIAL,
                                severity=ContradictionSeverity.MEDIUM,
                                description="Significant price variation",
                                conflicting_facts=[f.get("id") for f in category_facts],
                                confidence=sum(f.get("confidence", 0.5) for f in category_facts) / len(category_facts),
                                explanation=f"Price range: ${min_price:.2f} - ${max_price:.2f} ({max_price/min_price:.1f}x difference)",
                                suggested_resolution="Clarify if these are different pricing tiers or products",
                                auto_resolvable=False
                            )
                            contradictions.append(contradiction)
        
        return contradictions
    
    def _detect_positioning_contradictions(self, facts: List[Dict[str, Any]]) -> List[Contradiction]:
        """Detect contradictions in positioning facts"""
        contradictions = []
        
        # Group facts by positioning category
        positioning_facts = defaultdict(list)
        for fact in facts:
            category = fact.get("category", "").lower()
            value = fact.get("value", "").lower()
            
            for pattern_name, patterns in self.positioning_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        positioning_facts[pattern_name].append(fact)
                        break
        
        # Check for market position contradictions
        if "market_position" in positioning_facts:
            positions = []
            for fact in positioning_facts["market_position"]:
                value = fact.get("value", "").lower()
                if any(word in value for word in ["leader", "market leader", "number one", "top", "first"]):
                    positions.append("leader")
                elif any(word in value for word in ["challenger", "follower", "niche", "specialized"]):
                    positions.append("challenger")
                elif any(word in value for word in ["disruptor", "innovator", "game-changer"]):
                    positions.append("disruptor")
            
            if len(set(positions)) > 1:
                contradiction = Contradiction(
                    id=self._generate_contradiction_id(),
                    type=ContradictionType.POSITIONING,
                    severity=ContradictionSeverity.HIGH,
                    description="Inconsistent market positioning",
                    conflicting_facts=[f.get("id") for f in positioning_facts["market_position"]],
                    confidence=sum(f.get("confidence", 0.5) for f in positioning_facts["market_position"]) / len(positioning_facts["market_position"]),
                    explanation=f"Multiple positions claimed: {', '.join(set(positions))}",
                    suggested_resolution="Clarify the actual market position or explain different contexts",
                    auto_resolvable=False
                )
                contradictions.append(contradiction)
        
        return contradictions
    
    def _detect_team_contradictions(self, facts: List[Dict[str, Any]]) -> List[Contradiction]:
        """Detect contradictions in team facts"""
        contradictions = []
        
        # Group facts by team category
        team_facts = defaultdict(list)
        for fact in facts:
            category = fact.get("category", "").lower()
            value = fact.get("value", "").lower()
            
            for pattern_name, patterns in self.team_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        team_facts[pattern_name].append(fact)
                        break
        
        # Check for team size contradictions
        if "team_size" in team_facts:
            team_sizes = []
            for fact in team_facts["team_size"]:
                value = fact.get("value", "")
                size_match = re.search(r'([0-9]+)', value)
                if size_match:
                    size = int(size_match.group(1))
                    team_sizes.append(size)
            
            if len(team_sizes) > 1:
                # Check for significant team size differences
                max_size = max(team_sizes)
                min_size = min(team_sizes)
                if max_size / min_size > 3:  # More than 3x difference
                    contradiction = Contradiction(
                        id=self._generate_contradiction_id(),
                        type=ContradictionType.TEAM,
                        severity=ContradictionSeverity.MEDIUM,
                        description="Inconsistent team size",
                        conflicting_facts=[f.get("id") for f in team_facts["team_size"]],
                        confidence=sum(f.get("confidence", 0.5) for f in team_facts["team_size"]) / len(team_facts["team_size"]),
                        explanation=f"Team size range: {min_size} - {max_size} ({max_size/min_size:.1f}x difference)",
                        suggested_resolution="Clarify if these represent different time periods or departments",
                        auto_resolvable=False
                    )
                    contradictions.append(contradiction)
        
        return contradictions
    
    async def detect_contradictions(self, facts: List[Dict[str, Any]]) -> ContradictionReport:
        """
        Enhanced detection of all types of contradictions in the provided facts
        
        Args:
            facts: List of fact dictionaries
        
        Returns:
            ContradictionReport with all detected contradictions
        """
        all_contradictions = []
        
        # Detect different types of contradictions
        numerical_contradictions = self._detect_numerical_contradictions(facts)
        categorical_contradictions = self._detect_categorical_contradictions(facts)
        temporal_contradictions = self._detect_temporal_contradictions(facts)
        financial_contradictions = self._detect_financial_contradictions(facts)
        positioning_contradictions = self._detect_positioning_contradictions(facts)
        team_contradictions = self._detect_team_contradictions(facts)
        
        all_contradictions.extend(numerical_contradictions)
        all_contradictions.extend(categorical_contradictions)
        all_contradictions.extend(temporal_contradictions)
        all_contradictions.extend(financial_contradictions)
        all_contradictions.extend(positioning_contradictions)
        all_contradictions.extend(team_contradictions)
        
        # Sort by severity and confidence
        all_contradictions.sort(key=lambda x: (
            {"critical": 4, "high": 3, "medium": 2, "low": 1}[x.severity.value],
            x.confidence
        ), reverse=True)
        
        # Calculate statistics
        severity_distribution = {}
        type_distribution = {}
        auto_resolvable_count = 0
        
        for contradiction in all_contradictions:
            severity = contradiction.severity.value
            type_name = contradiction.type.value
            
            severity_distribution[severity] = severity_distribution.get(severity, 0) + 1
            type_distribution[type_name] = type_distribution.get(type_name, 0) + 1
            
            if contradiction.auto_resolvable:
                auto_resolvable_count += 1
        
        # Store detection history
        self.detection_history.append({
            "timestamp": datetime.now().isoformat(),
            "facts_count": len(facts),
            "contradictions_count": len(all_contradictions),
            "severity_distribution": severity_distribution,
            "type_distribution": type_distribution
        })
        
        # Generate recommendations
        recommendations = self._generate_recommendations(all_contradictions)
        
        return ContradictionReport(
            contradictions=all_contradictions,
            total_facts_analyzed=len(facts),
            contradiction_count=len(all_contradictions),
            severity_distribution=severity_distribution,
            type_distribution=type_distribution,
            auto_resolvable_count=auto_resolvable_count,
            recommendations=recommendations
        )
    
    def get_contradiction_summary(self, report: ContradictionReport) -> str:
        """Get a human-readable summary of contradictions"""
        if report.contradiction_count == 0:
            return "No contradictions detected in your evidence. All facts appear consistent."
        
        summary = f"Found {report.contradiction_count} potential contradictions in your evidence. "
        
        # Add severity breakdown
        critical = report.severity_distribution.get("critical", 0)
        high = report.severity_distribution.get("high", 0)
        if critical > 0 or high > 0:
            summary += f"{critical} critical and {high} high-priority issues need attention. "
        
        # Add type breakdown
        if report.type_distribution:
            top_type = max(report.type_distribution.items(), key=lambda x: x[1])
            summary += f"Most common issue: {top_type[0]} contradictions ({top_type[1]} cases). "
        
        # Add auto-resolvable info
        if report.auto_resolvable_count > 0:
            summary += f"{report.auto_resolvable_count} can be automatically resolved."
        
        return summary
