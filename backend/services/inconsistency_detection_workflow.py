"""
Inconsistency Detection Workflow
Advanced contradiction detection and resolution system for Raptorflow
"""

import asyncio
import json
import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# Import AI agents
from .agents.specialists.contradiction_detector import ContradictionDetector

# Import AI services
try:
    from services.vertex_ai_service import vertex_ai_service
except ImportError:
    vertex_ai_service = None

logger = logging.getLogger(__name__)


class ContradictionType(str, Enum):
    """Types of contradictions"""

    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    TEMPORAL = "temporal"
    SEMANTIC = "semantic"
    LOGICAL = "logical"
    CONTEXTUAL = "contextual"


class ContradictionSeverity(str, Enum):
    """Severity levels for contradictions"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ResolutionStatus(str, Enum):
    """Resolution status"""

    UNRESOLVED = "unresolved"
    RESOLVED = "resolved"
    IGNORED = "ignored"
    ESCALATED = "escalated"


@dataclass
class Contradiction:
    """Individual contradiction"""

    id: str
    type: ContradictionType
    severity: ContradictionSeverity
    description: str
    conflicting_facts: List[Dict[str, Any]]
    confidence: float
    context: str
    resolution_suggestion: str = ""
    resolution_status: ResolutionStatus = ResolutionStatus.UNRESOLVED
    resolution_action: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "type": self.type.value,
            "severity": self.severity.value,
            "description": self.description,
            "conflicting_facts": self.conflicting_facts,
            "confidence": self.confidence,
            "context": (
                self.context[:200] + "..." if len(self.context) > 200 else self.context
            ),
            "resolution_suggestion": self.resolution_suggestion,
            "resolution_status": self.resolution_status.value,
            "resolution_action": self.resolution_action,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class ContradictionAnalysis:
    """Complete contradiction analysis"""

    contradictions: List[Contradiction]
    total_contradictions: int
    contradictions_by_type: Dict[str, int]
    contradictions_by_severity: Dict[str, int]
    resolution_summary: Dict[str, int]
    overall_consistency_score: float
    processing_time: float
    recommendations: List[str]
    analysis_metadata: Dict[str, Any] = field(default_factory=dict)


class InconsistencyDetectionWorkflow:
    """Advanced inconsistency detection and resolution workflow"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Initialize contradiction detector
        self.contradiction_detector = ContradictionDetector()

        # Contradiction counter
        self.contradiction_counter = 0

        # Detection rules
        self.detection_rules = self._initialize_detection_rules()

        # Resolution strategies
        self.resolution_strategies = self._initialize_resolution_strategies()

    def _initialize_detection_rules(
        self,
    ) -> Dict[ContradictionType, List[Dict[str, Any]]]:
        """Initialize detection rules for different contradiction types"""
        return {
            ContradictionType.NUMERICAL: [
                {
                    "name": "revenue_mismatch",
                    "pattern": r"revenue.*?(\$\d+(?:,\d{3})*(?:\.\d{2})?)",
                    "tolerance": 0.1,  # 10% tolerance
                    "description": "Revenue values that differ significantly",
                },
                {
                    "name": "employee_count_mismatch",
                    "pattern": r"(\d+(?:,\d{3})*)\s*(?:employees|staff)",
                    "tolerance": 0.2,  # 20% tolerance
                    "description": "Employee counts that differ significantly",
                },
                {
                    "name": "funding_amount_mismatch",
                    "pattern": r"funding.*?(\$\d+(?:,\d{3})*(?:\.\d{2})?)",
                    "tolerance": 0.05,  # 5% tolerance
                    "description": "Funding amounts that differ significantly",
                },
            ],
            ContradictionType.TEMPORAL: [
                {
                    "name": "founded_year_mismatch",
                    "pattern": r"founded.*?(\d{4})",
                    "tolerance": 0,  # No tolerance for years
                    "description": "Different founding years",
                },
                {
                    "name": "date_inconsistency",
                    "pattern": r"(\d{4}[-/]\d{1,2}[-/]\d{1,2})",
                    "tolerance": 30,  # 30 days tolerance
                    "description": "Dates that are too far apart",
                },
            ],
            ContradictionType.CATEGORICAL: [
                {
                    "name": "industry_mismatch",
                    "keywords": ["industry", "sector", "vertical"],
                    "tolerance": 0,  # No tolerance for categories
                    "description": "Different industry classifications",
                },
                {
                    "name": "business_model_mismatch",
                    "keywords": ["business model", "revenue model", "monetization"],
                    "tolerance": 0,
                    "description": "Different business model descriptions",
                },
            ],
            ContradictionType.SEMANTIC: [
                {
                    "name": "opposite_statements",
                    "antonyms": [
                        ["profitable", "unprofitable"],
                        ["growing", "declining"],
                        ["successful", "failing"],
                        ["expanding", "contracting"],
                    ],
                    "description": "Statements with opposite meanings",
                }
            ],
        }

    def _initialize_resolution_strategies(self) -> Dict[ContradictionType, List[str]]:
        """Initialize resolution strategies for different contradiction types"""
        return {
            ContradictionType.NUMERICAL: [
                "verify_source_credibility",
                "check_for_typographical_errors",
                "consider_time_context",
                "look_for_unit_conversions",
                "verify_calculation_methods",
            ],
            ContradictionType.TEMPORAL: [
                "check_date_formats",
                "verify_time_periods",
                "consider_update_frequency",
                "check for version differences",
            ],
            ContradictionType.CATEGORICAL: [
                "verify_classification_systems",
                "check for hierarchical relationships",
                "consider context specificity",
                "verify source authority",
            ],
            ContradictionType.SEMANTIC: [
                "analyze_contextual meaning",
                "check for nuance differences",
                "consider conditional statements",
                "verify source intent",
            ],
            ContradictionType.LOGICAL: [
                "identify logical fallacies",
                "check for missing premises",
                "verify causal relationships",
                "consider alternative explanations",
            ],
            ContradictionType.CONTEXTUAL: [
                "analyze surrounding context",
                "check for scope differences",
                "consider audience differences",
                "verify temporal context",
            ],
        }

    async def detect_contradictions(
        self, facts: List[Dict[str, Any]]
    ) -> ContradictionAnalysis:
        """Detect contradictions in extracted facts"""
        start_time = datetime.now()

        all_contradictions = []

        # Detect contradictions using multiple methods
        rule_contradictions = await self._detect_with_rules(facts)
        all_contradictions.extend(rule_contradictions)

        # Use AI-powered detection
        if vertex_ai_service:
            try:
                ai_contradictions = await self._detect_with_ai(facts)
                all_contradictions.extend(ai_contradictions)
            except Exception as e:
                self.logger.warning(f"AI contradiction detection failed: {e}")

        # Use contradiction detector agent
        try:
            agent_result = await self.contradiction_detector.detect_contradictions(
                facts
            )
            agent_contradictions = self._convert_agent_contradictions(
                agent_result.contradictions
            )
            all_contradictions.extend(agent_contradictions)
        except Exception as e:
            self.logger.warning(f"Agent contradiction detection failed: {e}")

        # Deduplicate contradictions
        deduplicated_contradictions = self._deduplicate_contradictions(
            all_contradictions
        )

        # Calculate analysis metrics
        contradictions_by_type = self._calculate_type_distribution(
            deduplicated_contradictions
        )
        contradictions_by_severity = self._calculate_severity_distribution(
            deduplicated_contradictions
        )
        resolution_summary = self._calculate_resolution_summary(
            deduplicated_contradictions
        )
        consistency_score = self._calculate_consistency_score(
            deduplicated_contradictions, len(facts)
        )

        # Generate recommendations
        recommendations = self._generate_contradiction_recommendations(
            deduplicated_contradictions, facts
        )

        processing_time = (datetime.now() - start_time).total_seconds()

        return ContradictionAnalysis(
            contradictions=deduplicated_contradictions,
            total_contradictions=len(deduplicated_contradictions),
            contradictions_by_type=contradictions_by_type,
            contradictions_by_severity=contradictions_by_severity,
            resolution_summary=resolution_summary,
            overall_consistency_score=consistency_score,
            processing_time=processing_time,
            recommendations=recommendations,
            analysis_metadata={
                "detection_methods": ["rules", "ai", "agent"],
                "facts_processed": len(facts),
                "contradiction_rate": (
                    len(deduplicated_contradictions) / len(facts) if facts else 0.0
                ),
            },
        )

    async def _detect_with_rules(
        self, facts: List[Dict[str, Any]]
    ) -> List[Contradiction]:
        """Detect contradictions using rule-based approach"""
        contradictions = []

        # Group facts by category and label
        fact_groups = defaultdict(list)
        for fact in facts:
            key = f"{fact.get('category', 'unknown')}:{fact.get('label', 'unknown')}"
            fact_groups[key].append(fact)

        # Check each group for contradictions
        for group_key, group_facts in fact_groups.items():
            if len(group_facts) < 2:
                continue

            # Determine contradiction type from category
            category = group_facts[0].get("category", "other")
            contradiction_type = self._determine_contradiction_type(category)

            # Apply detection rules
            rules = self.detection_rules.get(contradiction_type, [])

            for rule in rules:
                rule_contradictions = self._apply_rule(rule, group_facts)
                contradictions.extend(rule_contradictions)

        return contradictions

    def _determine_contradiction_type(self, category: str) -> ContradictionType:
        """Determine contradiction type from fact category"""
        category_mapping = {
            "financial": ContradictionType.NUMERICAL,
            "company": ContradictionType.CATEGORICAL,
            "market": ContradictionType.SEMANTIC,
            "customer": ContradictionType.CATEGORICAL,
            "product": ContradictionType.SEMANTIC,
            "team": ContradictionType.NUMERICAL,
            "operational": ContradictionType.LOGICAL,
            "strategic": ContradictionType.SEMANTIC,
            "competitive": ContradictionType.SEMANTIC,
            "technology": ContradictionType.CATEGORICAL,
        }

        return category_mapping.get(category, ContradictionType.SEMANTIC)

    def _apply_rule(
        self, rule: Dict[str, Any], facts: List[Dict[str, Any]]
    ) -> List[Contradiction]:
        """Apply detection rule to facts"""
        contradictions = []

        if rule["name"] == "revenue_mismatch":
            contradictions.extend(
                self._check_numerical_contradiction(facts, "revenue", rule)
            )
        elif rule["name"] == "employee_count_mismatch":
            contradictions.extend(
                self._check_numerical_contradiction(facts, "employees", rule)
            )
        elif rule["name"] == "founded_year_mismatch":
            contradictions.extend(self._check_year_contradiction(facts, rule))
        elif rule["name"] == "industry_mismatch":
            contradictions.extend(
                self._check_categorical_contradiction(facts, "industry", rule)
            )
        elif rule["name"] == "opposite_statements":
            contradictions.extend(self._check_semantic_contradiction(facts, rule))

        return contradictions

    def _check_numerical_contradiction(
        self, facts: List[Dict[str, Any]], value_type: str, rule: Dict[str, Any]
    ) -> List[Contradiction]:
        """Check for numerical contradictions"""
        contradictions = []

        # Extract numerical values
        numerical_values = []
        for fact in facts:
            value = fact.get("value", "")
            # Extract numbers from value
            numbers = re.findall(r"\d+(?:,\d{3})*(?:\.\d{2})?", value)
            for num in numbers:
                try:
                    clean_num = float(num.replace(",", ""))
                    numerical_values.append(
                        {"value": clean_num, "fact": fact, "original": value}
                    )
                except ValueError:
                    continue

        # Check for contradictions
        for i, val1 in enumerate(numerical_values):
            for j, val2 in enumerate(numerical_values[i + 1 :], i + 1):
                tolerance = rule["tolerance"]

                # Calculate relative difference
                if val1["value"] > 0:
                    diff = abs(val1["value"] - val2["value"]) / val1["value"]
                else:
                    diff = abs(val1["value"] - val2["value"])

                if diff > tolerance:
                    contradiction = Contradiction(
                        id=self._generate_contradiction_id(),
                        type=ContradictionType.NUMERICAL,
                        severity=self._calculate_severity(diff),
                        description=f"{value_type.title()} values differ by {diff:.1%}",
                        conflicting_facts=[val1["fact"], val2["fact"]],
                        confidence=min(0.9, 0.5 + diff),
                        context=f"Value 1: {val1['original']}, Value 2: {val2['original']}",
                        resolution_suggestion=self._generate_numerical_resolution_suggestion(
                            val1, val2, value_type
                        ),
                        metadata={
                            "rule": rule["name"],
                            "difference": diff,
                            "values": [val1["value"], val2["value"]],
                        },
                    )
                    contradictions.append(contradiction)

        return contradictions

    def _check_year_contradiction(
        self, facts: List[Dict[str, Any]], rule: Dict[str, Any]
    ) -> List[Contradiction]:
        """Check for year contradictions"""
        contradictions = []

        # Extract years
        years = []
        for fact in facts:
            value = fact.get("value", "")
            year_matches = re.findall(r"\b(19|20)\d{2}\b", value)
            for year in year_matches:
                years.append({"year": int(year), "fact": fact, "original": value})

        # Check for contradictions
        for i, year1 in enumerate(years):
            for j, year2 in enumerate(years[i + 1 :], i + 1):
                if year1["year"] != year2["year"]:
                    contradiction = Contradiction(
                        id=self._generate_contradiction_id(),
                        type=ContradictionType.TEMPORAL,
                        severity=ContradictionSeverity.HIGH,
                        description=f"Year values differ: {year1['year']} vs {year2['year']}",
                        conflicting_facts=[year1["fact"], year2["fact"]],
                        confidence=0.8,
                        context=f"Year 1: {year1['original']}, Year 2: {year2['original']}",
                        resolution_suggestion="Verify which year is correct from authoritative source",
                        metadata={
                            "rule": rule["name"],
                            "years": [year1["year"], year2["year"]],
                        },
                    )
                    contradictions.append(contradiction)

        return contradictions

    def _check_categorical_contradiction(
        self, facts: List[Dict[str, Any]], category_type: str, rule: Dict[str, Any]
    ) -> List[Contradiction]:
        """Check for categorical contradictions"""
        contradictions = []

        # Extract categories
        categories = []
        for fact in facts:
            value = fact.get("value", "").lower()
            categories.append({"category": value, "fact": fact, "original": value})

        # Check for contradictions
        for i, cat1 in enumerate(categories):
            for j, cat2 in enumerate(categories[i + 1 :], i + 1):
                # Simple check for different categories
                if (
                    cat1["category"] != cat2["category"]
                    and cat1["category"]
                    and cat2["category"]
                ):
                    # Check if they're actually different (not just wording)
                    similarity = self._calculate_text_similarity(
                        cat1["category"], cat2["category"]
                    )

                    if similarity < 0.7:  # Low similarity indicates contradiction
                        contradiction = Contradiction(
                            id=self._generate_contradiction_id(),
                            type=ContradictionType.CATEGORICAL,
                            severity=ContradictionSeverity.MEDIUM,
                            description=f"{category_type.title()} categories differ: {cat1['category']} vs {cat2['category']}",
                            conflicting_facts=[cat1["fact"], cat2["fact"]],
                            confidence=0.7,
                            context=f"Category 1: {cat1['original']}, Category 2: {cat2['original']}",
                            resolution_suggestion=f"Determine correct {category_type} classification",
                            metadata={
                                "rule": rule["name"],
                                "similarity": similarity,
                                "categories": [cat1["category"], cat2["category"]],
                            },
                        )
                        contradictions.append(contradiction)

        return contradictions

    def _check_semantic_contradiction(
        self, facts: List[Dict[str, Any]], rule: Dict[str, Any]
    ) -> List[Contradiction]:
        """Check for semantic contradictions"""
        contradictions = []

        antonyms = rule["antonyms"]

        for i, fact1 in enumerate(facts):
            for j, fact2 in enumerate(facts[i + 1 :], i + 1):
                value1 = fact1.get("value", "").lower()
                value2 = fact2.get("value", "").lower()

                # Check for antonyms
                for antonym_pair in antonyms:
                    if (antonym_pair[0] in value1 and antonym_pair[1] in value2) or (
                        antonym_pair[1] in value1 and antonym_pair[0] in value2
                    ):

                        contradiction = Contradiction(
                            id=self._generate_contradiction_id(),
                            type=ContradictionType.SEMANTIC,
                            severity=ContradictionSeverity.HIGH,
                            description=f"Opposite statements: {antonym_pair[0]} vs {antonym_pair[1]}",
                            conflicting_facts=[fact1, fact2],
                            confidence=0.8,
                            context=f"Statement 1: {value1}, Statement 2: {value2}",
                            resolution_suggestion="Check context to determine which statement is accurate",
                            metadata={"rule": rule["name"], "antonyms": antonym_pair},
                        )
                        contradictions.append(contradiction)

        return contradictions

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using simple approach"""
        # Simple word overlap similarity
        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    def _calculate_severity(self, difference: float) -> ContradictionSeverity:
        """Calculate contradiction severity from difference"""
        if difference > 0.5:
            return ContradictionSeverity.CRITICAL
        elif difference > 0.3:
            return ContradictionSeverity.HIGH
        elif difference > 0.1:
            return ContradictionSeverity.MEDIUM
        else:
            return ContradictionSeverity.LOW

    def _generate_numerical_resolution_suggestion(
        self, val1: Dict, val2: Dict, value_type: str
    ) -> str:
        """Generate resolution suggestion for numerical contradictions"""
        suggestions = [
            f"Verify {value_type} values from original sources",
            "Check for typographical errors in the numbers",
            "Consider if values represent different time periods",
            "Verify units and currency are consistent",
            "Check if values are estimates vs actual figures",
        ]

        # Choose most relevant suggestion based on context
        if val1["value"] > val2["value"] * 10 or val2["value"] > val1["value"] * 10:
            return "Check for unit conversion errors (e.g., thousands vs millions)"
        else:
            return suggestions[0]

    async def _detect_with_ai(self, facts: List[Dict[str, Any]]) -> List[Contradiction]:
        """Detect contradictions using AI"""
        if not vertex_ai_service:
            return []

        try:
            # Prepare AI prompt
            facts_text = "\n".join(
                [
                    f"- {fact.get('label', 'Unknown')}: {fact.get('value', 'Unknown')} (Category: {fact.get('category', 'Unknown')})"
                    for fact in facts[:20]  # Limit for AI processing
                ]
            )

            prompt = f"""
Analyze the following business facts for contradictions and inconsistencies. Look for:
1. Numerical contradictions (different values for same metric)
2. Temporal contradictions (conflicting dates or timeframes)
3. Categorical contradictions (different classifications)
4. Semantic contradictions (opposite or conflicting statements)
5. Logical contradictions (statements that can't both be true)

Facts:
{facts_text}

Provide contradictions in JSON format:
{{
    "contradictions": [
        {{
            "type": "numerical|temporal|categorical|semantic|logical",
            "description": "Brief description of the contradiction",
            "conflicting_facts": [
                {{"label": "Fact 1 label", "value": "Fact 1 value"}},
                {{"label": "Fact 2 label", "value": "Fact 2 value"}}
            ],
            "confidence": 0.0-1.0,
            "severity": "critical|high|medium|low",
            "resolution_suggestion": "How to resolve this contradiction"
        }}
    ]
}}
"""

            # Call AI service
            response = await vertex_ai_service.generate_text(
                prompt=prompt, max_tokens=1500, temperature=0.3
            )

            if response["status"] == "success":
                return self._parse_ai_contradictions(response["text"], facts)
            else:
                self.logger.warning(
                    f"AI contradiction detection failed: {response.get('error')}"
                )
                return []

        except Exception as e:
            self.logger.error(f"AI contradiction detection error: {e}")
            return []

    def _parse_ai_contradictions(
        self, ai_response: str, facts: List[Dict[str, Any]]
    ) -> List[Contradiction]:
        """Parse AI response into contradictions"""
        contradictions = []

        try:
            # Extract JSON from response
            json_match = re.search(r"\{.*\}", ai_response, re.DOTALL)
            if not json_match:
                return []

            data = json.loads(json_match.group(0))
            ai_contradictions = data.get("contradictions", [])

            for contradiction_data in ai_contradictions:
                try:
                    # Find conflicting facts
                    conflicting_facts = []
                    for fact_data in contradiction_data.get("conflicting_facts", []):
                        # Find matching facts
                        matching_facts = [
                            fact
                            for fact in facts
                            if fact.get("label", "").lower()
                            == fact_data.get("label", "").lower()
                        ]
                        if matching_facts:
                            conflicting_facts.extend(matching_facts)

                    if len(conflicting_facts) >= 2:
                        contradiction = Contradiction(
                            id=self._generate_contradiction_id(),
                            type=ContradictionType(
                                contradiction_data.get("type", "semantic")
                            ),
                            severity=ContradictionSeverity(
                                contradiction_data.get("severity", "medium")
                            ),
                            description=contradiction_data.get(
                                "description", "AI-detected contradiction"
                            ),
                            conflicting_facts=conflicting_facts[:2],  # Limit to 2 facts
                            confidence=float(contradiction_data.get("confidence", 0.5)),
                            context="AI-detected contradiction",
                            resolution_suggestion=contradiction_data.get(
                                "resolution_suggestion", "Manual review required"
                            ),
                            extraction_method="ai_detection",
                            metadata={
                                "ai_confidence": contradiction_data.get(
                                    "confidence", 0.5
                                )
                            },
                        )

                        contradictions.append(contradiction)

                except Exception as e:
                    self.logger.error(f"Error parsing AI contradiction: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Error parsing AI response: {e}")

        return contradictions

    def _convert_agent_contradictions(
        self, agent_contradictions: List[Any]
    ) -> List[Contradiction]:
        """Convert agent contradictions to Contradiction format"""
        converted_contradictions = []

        for contradiction in agent_contradictions:
            try:
                converted = Contradiction(
                    id=self._generate_contradiction_id(),
                    type=ContradictionType(contradiction.get("type", "semantic")),
                    severity=ContradictionSeverity(
                        contradiction.get("severity", "medium")
                    ),
                    description=contradiction.get(
                        "description", "Agent-detected contradiction"
                    ),
                    conflicting_facts=contradiction.get("conflicting_facts", []),
                    confidence=float(contradiction.get("confidence", 0.5)),
                    context=contradiction.get("context", ""),
                    resolution_suggestion=contradiction.get(
                        "resolution_suggestion", ""
                    ),
                    extraction_method="agent_detection",
                    metadata=contradiction.get("metadata", {}),
                )

                converted_contradictions.append(converted)

            except Exception as e:
                self.logger.error(f"Error converting agent contradiction: {e}")
                continue

        return converted_contradictions

    def _deduplicate_contradictions(
        self, contradictions: List[Contradiction]
    ) -> List[Contradiction]:
        """Deduplicate contradictions based on similarity"""
        if not contradictions:
            return []

        deduplicated = []

        for contradiction in contradictions:
            # Check if similar contradiction already exists
            is_duplicate = False
            for existing in deduplicated:
                if self._are_contradictions_similar(contradiction, existing):
                    # Keep the one with higher confidence
                    if contradiction.confidence > existing.confidence:
                        deduplicated.remove(existing)
                        deduplicated.append(contradiction)
                    is_duplicate = True
                    break

            if not is_duplicate:
                deduplicated.append(contradiction)

        return deduplicated

    def _are_contradictions_similar(self, c1: Contradiction, c2: Contradiction) -> bool:
        """Check if two contradictions are similar"""
        # Check type
        if c1.type != c2.type:
            return False

        # Check conflicting facts overlap
        c1_fact_ids = set(f.get("id", "") for f in c1.conflicting_facts)
        c2_fact_ids = set(f.get("id", "") for f in c2.conflicting_facts)

        overlap = len(c1_fact_ids.intersection(c2_fact_ids))

        # If 50% or more facts overlap, consider similar
        total_facts = len(c1_fact_ids.union(c2_fact_ids))
        if total_facts > 0 and overlap / total_facts >= 0.5:
            return True

        # Check description similarity
        desc_similarity = self._calculate_text_similarity(
            c1.description.lower(), c2.description.lower()
        )
        if desc_similarity > 0.8:
            return True

        return False

    def _calculate_type_distribution(
        self, contradictions: List[Contradiction]
    ) -> Dict[str, int]:
        """Calculate contradiction type distribution"""
        distribution = defaultdict(int)
        for contradiction in contradictions:
            distribution[contradiction.type.value] += 1
        return dict(distribution)

    def _calculate_severity_distribution(
        self, contradictions: List[Contradiction]
    ) -> Dict[str, int]:
        """Calculate contradiction severity distribution"""
        distribution = defaultdict(int)
        for contradiction in contradictions:
            distribution[contradiction.severity.value] += 1
        return dict(distribution)

    def _calculate_resolution_summary(
        self, contradictions: List[Contradiction]
    ) -> Dict[str, int]:
        """Calculate resolution status summary"""
        summary = defaultdict(int)
        for contradiction in contradictions:
            summary[contradiction.resolution_status.value] += 1
        return dict(summary)

    def _calculate_consistency_score(
        self, contradictions: List[Contradiction], total_facts: int
    ) -> float:
        """Calculate overall consistency score"""
        if total_facts == 0:
            return 100.0

        # Base score starts at 100
        score = 100.0

        # Deduct points for contradictions
        for contradiction in contradictions:
            if contradiction.severity == ContradictionSeverity.CRITICAL:
                score -= 10
            elif contradiction.severity == ContradictionSeverity.HIGH:
                score -= 7
            elif contradiction.severity == ContradictionSeverity.MEDIUM:
                score -= 5
            elif contradiction.severity == ContradictionSeverity.LOW:
                score -= 3
            else:
                score -= 1

        # Adjust for contradiction rate
        contradiction_rate = len(contradictions) / total_facts
        if contradiction_rate > 0.2:
            score -= 20
        elif contradiction_rate > 0.1:
            score -= 10
        elif contradiction_rate > 0.05:
            score -= 5

        return max(0.0, min(100.0, score))

    def _generate_contradiction_recommendations(
        self, contradictions: List[Contradiction], facts: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations for resolving contradictions"""
        recommendations = []

        if not contradictions:
            recommendations.append(
                "No contradictions detected - data appears consistent"
            )
            return recommendations

        # High-level recommendations
        critical_count = len(
            [c for c in contradictions if c.severity == ContradictionSeverity.CRITICAL]
        )
        if critical_count > 0:
            recommendations.append(
                f"Address {critical_count} critical contradictions immediately"
            )

        # Type-specific recommendations
        type_counts = defaultdict(int)
        for contradiction in contradictions:
            type_counts[contradiction.type.value] += 1

        if type_counts.get("numerical", 0) > 0:
            recommendations.append("Verify numerical data from authoritative sources")

        if type_counts.get("temporal", 0) > 0:
            recommendations.append("Check dates and timeframes for accuracy")

        if type_counts.get("categorical", 0) > 0:
            recommendations.append("Standardize classification systems")

        if type_counts.get("semantic", 0) > 0:
            recommendations.append("Review statements for contextual meaning")

        # Process recommendations
        unresolved_count = len(
            [
                c
                for c in contradictions
                if c.resolution_status == ResolutionStatus.UNRESOLVED
            ]
        )
        if unresolved_count > 0:
            recommendations.append(
                f"Resolve {unresolved_count} unresolved contradictions"
            )

        # Quality recommendations
        contradiction_rate = len(contradictions) / len(facts) if facts else 0
        if contradiction_rate > 0.15:
            recommendations.append(
                "Consider improving data quality and source verification"
            )

        return recommendations

    def _generate_contradiction_id(self) -> str:
        """Generate unique contradiction ID"""
        self.contradiction_counter += 1
        return f"CONTR-{self.contradiction_counter:04d}"

    async def resolve_contradiction(
        self, contradiction_id: str, resolution_action: str, user_context: str = ""
    ) -> bool:
        """Resolve a contradiction"""
        # This would update the contradiction in storage
        # For now, return success
        return True

    async def escalate_contradiction(
        self, contradiction_id: str, escalation_reason: str
    ) -> bool:
        """Escalate a contradiction for manual review"""
        # This would mark the contradiction as escalated
        # For now, return success
        return True


# Export workflow
__all__ = ["InconsistencyDetectionWorkflow", "Contradiction", "ContradictionAnalysis"]
