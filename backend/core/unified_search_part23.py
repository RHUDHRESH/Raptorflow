"""
Part 23: Search Quality Assurance and Validation
RaptorFlow Unified Search System - Industrial Grade AI Agent Search Infrastructure
===============================================================================
This module implements comprehensive quality assurance, validation frameworks,
and continuous monitoring for search result quality and system performance.
"""

import asyncio
import hashlib
import json
import logging
import statistics
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from core.unified_search_part1 import ContentType, SearchMode, SearchQuery, SearchResult
from core.unified_search_part2 import SearchProvider

logger = logging.getLogger("raptorflow.unified_search.quality")


class QualityMetric(Enum):
    """Quality metric types."""

    RELEVANCE = "relevance"
    FRESHNESS = "freshness"
    AUTHORITY = "authority"
    COMPLETENESS = "completeness"
    DIVERSITY = "diversity"
    ACCURACY = "accuracy"
    COVERAGE = "coverage"
    CONSISTENCY = "consistency"
    PERFORMANCE = "performance"
    USER_SATISFACTION = "user_satisfaction"


class ValidationLevel(Enum):
    """Validation levels."""

    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    STRICT = "strict"


class QualityThreshold(Enum):
    """Quality threshold levels."""

    POOR = 0.3
    FAIR = 0.5
    GOOD = 0.7
    EXCELLENT = 0.9


@dataclass
class QualityScore:
    """Individual quality score."""

    metric: QualityMetric
    score: float
    confidence: float
    weight: float = 1.0
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metric": self.metric.value,
            "score": self.score,
            "confidence": self.confidence,
            "weight": self.weight,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class QualityAssessment:
    """Comprehensive quality assessment."""

    assessment_id: str
    query: SearchQuery
    results: List[SearchResult]
    overall_score: float
    metric_scores: List[QualityScore]
    quality_level: QualityThreshold
    issues: List[str]
    recommendations: List[str]
    validation_level: ValidationLevel
    assessed_at: datetime = field(default_factory=datetime.now)
    assessor: str = "system"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "assessment_id": self.assessment_id,
            "query": {
                "text": self.query.text,
                "mode": self.query.mode.value,
                "max_results": self.query.max_results,
            },
            "results_count": len(self.results),
            "overall_score": self.overall_score,
            "metric_scores": [score.to_dict() for score in self.metric_scores],
            "quality_level": self.quality_level.value,
            "issues": self.issues,
            "recommendations": self.recommendations,
            "validation_level": self.validation_level.value,
            "assessed_at": self.assessed_at.isoformat(),
            "assessor": self.assessor,
        }


@dataclass
class ValidationRule:
    """Quality validation rule."""

    rule_id: str
    name: str
    description: str
    metric: QualityMetric
    threshold: float
    weight: float
    enabled: bool = True
    conditions: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "metric": self.metric.value,
            "threshold": self.threshold,
            "weight": self.weight,
            "enabled": self.enabled,
            "conditions": self.conditions,
        }


class QualityMetricsCalculator:
    """Calculates various quality metrics."""

    def __init__(self):
        self.metric_weights = {
            QualityMetric.RELEVANCE: 0.3,
            QualityMetric.FRESHNESS: 0.15,
            QualityMetric.AUTHORITY: 0.2,
            QualityMetric.DIVERSITY: 0.15,
            QualityMetric.COMPLETENESS: 0.1,
            QualityMetric.PERFORMANCE: 0.1,
        }

    async def calculate_relevance_score(
        self, query: SearchQuery, results: List[SearchResult]
    ) -> QualityScore:
        """Calculate relevance score."""
        if not results:
            return QualityScore(
                metric=QualityMetric.RELEVANCE, score=0.0, confidence=0.0
            )

        relevance_scores = []
        query_terms = set(query.text.lower().split())

        for result in results:
            score = 0.0

            # Title relevance
            title_terms = set(result.title.lower().split())
            title_overlap = (
                len(query_terms & title_terms) / len(query_terms) if query_terms else 0
            )
            score += title_overlap * 0.4

            # Snippet relevance
            if result.snippet:
                snippet_terms = set(result.snippet.lower().split())
                snippet_overlap = (
                    len(query_terms & snippet_terms) / len(query_terms)
                    if query_terms
                    else 0
                )
                score += snippet_overlap * 0.3

            # Content relevance
            if result.content:
                content_terms = set(result.content.lower().split())
                content_overlap = (
                    len(query_terms & content_terms) / len(query_terms)
                    if query_terms
                    else 0
                )
                score += content_overlap * 0.2

            # Provider relevance
            provider_bonus = 0.1 if result.provider == SearchProvider.NATIVE else 0.05
            score += provider_bonus

            relevance_scores.append(min(1.0, score))

        avg_relevance = statistics.mean(relevance_scores)
        confidence = 0.8 if len(results) >= 5 else 0.6

        return QualityScore(
            metric=QualityMetric.RELEVANCE,
            score=avg_relevance,
            confidence=confidence,
            details={
                "individual_scores": relevance_scores,
                "query_terms": list(query_terms),
                "results_analyzed": len(results),
            },
        )

    async def calculate_freshness_score(
        self, results: List[SearchResult]
    ) -> QualityScore:
        """Calculate freshness score."""
        if not results:
            return QualityScore(
                metric=QualityMetric.FRESHNESS, score=0.0, confidence=0.0
            )

        freshness_scores = []
        now = datetime.now()

        for result in results:
            if result.publish_date:
                days_old = (now - result.publish_date).days

                # Freshness decay function
                if days_old <= 1:
                    freshness = 1.0
                elif days_old <= 7:
                    freshness = 0.8
                elif days_old <= 30:
                    freshness = 0.6
                elif days_old <= 365:
                    freshness = 0.4
                else:
                    freshness = 0.2
            else:
                freshness = 0.3  # Default for unknown dates

            freshness_scores.append(freshness)

        avg_freshness = statistics.mean(freshness_scores)
        confidence = 0.7

        return QualityScore(
            metric=QualityMetric.FRESHNESS,
            score=avg_freshness,
            confidence=confidence,
            details={
                "individual_scores": freshness_scores,
                "days_distribution": [
                    (datetime.now() - r.publish_date).days if r.publish_date else None
                    for r in results
                ],
            },
        )

    async def calculate_authority_score(
        self, results: List[SearchResult]
    ) -> QualityScore:
        """Calculate authority score."""
        if not results:
            return QualityScore(
                metric=QualityMetric.AUTHORITY, score=0.0, confidence=0.0
            )

        authority_scores = []

        for result in results:
            # Domain authority
            domain_score = result.domain_authority or 0.5

            # Provider trust
            provider_scores = {
                SearchProvider.NATIVE: 0.8,
                SearchProvider.SERPER: 0.7,
                SearchProvider.BRAVE: 0.6,
                SearchProvider.DUCKDUCKGO: 0.5,
            }
            provider_score = provider_scores.get(result.provider, 0.5)

            # HTTPS bonus
            https_bonus = 0.1 if result.is_https else 0.0

            # Combined authority score
            authority = (domain_score * 0.6) + (provider_score * 0.3) + https_bonus
            authority_scores.append(min(1.0, authority))

        avg_authority = statistics.mean(authority_scores)
        confidence = 0.8

        return QualityScore(
            metric=QualityMetric.AUTHORITY,
            score=avg_authority,
            confidence=confidence,
            details={
                "individual_scores": authority_scores,
                "domain_authorities": [r.domain_authority for r in results],
                "provider_distribution": {
                    provider.value: sum(1 for r in results if r.provider == provider)
                    for provider in SearchProvider
                },
            },
        )

    async def calculate_diversity_score(
        self, results: List[SearchResult]
    ) -> QualityScore:
        """Calculate diversity score."""
        if len(results) < 2:
            return QualityScore(
                metric=QualityMetric.DIVERSITY, score=0.5, confidence=0.5
            )

        # Domain diversity
        domains = [result.domain for result in results]
        unique_domains = len(set(domains))
        domain_diversity = unique_domains / len(domains)

        # Provider diversity
        providers = [result.provider for result in results]
        unique_providers = len(set(providers))
        provider_diversity = unique_providers / len(providers)

        # Content type diversity
        content_types = [result.content_type for result in results]
        unique_content_types = len(set(content_types))
        content_diversity = unique_content_types / len(content_types)

        # Combined diversity score
        overall_diversity = (
            (domain_diversity * 0.5)
            + (provider_diversity * 0.3)
            + (content_diversity * 0.2)
        )
        confidence = 0.9

        return QualityScore(
            metric=QualityMetric.DIVERSITY,
            score=overall_diversity,
            confidence=confidence,
            details={
                "domain_diversity": domain_diversity,
                "provider_diversity": provider_diversity,
                "content_diversity": content_diversity,
                "unique_domains": unique_domains,
                "unique_providers": unique_providers,
                "unique_content_types": unique_content_types,
            },
        )

    async def calculate_completeness_score(
        self, query: SearchQuery, results: List[SearchResult]
    ) -> QualityScore:
        """Calculate completeness score."""
        if not results:
            return QualityScore(
                metric=QualityMetric.COMPLETENESS, score=0.0, confidence=0.0
            )

        completeness_scores = []

        for result in results:
            score = 0.0

            # Title presence
            if result.title and len(result.title.strip()) > 0:
                score += 0.3

            # Snippet presence
            if result.snippet and len(result.snippet.strip()) > 0:
                score += 0.2

            # Content presence
            if result.content and len(result.content.strip()) > 100:
                score += 0.3
            elif result.content and len(result.content.strip()) > 0:
                score += 0.1

            # Metadata completeness
            metadata_fields = ["url", "domain", "provider", "relevance_score"]
            present_fields = sum(
                1
                for field in metadata_fields
                if getattr(result, field, None) is not None
            )
            score += (present_fields / len(metadata_fields)) * 0.2

            completeness_scores.append(min(1.0, score))

        avg_completeness = statistics.mean(completeness_scores)
        confidence = 0.9

        return QualityScore(
            metric=QualityMetric.COMPLETENESS,
            score=avg_completeness,
            confidence=confidence,
            details={
                "individual_scores": completeness_scores,
                "results_with_content": sum(1 for r in results if r.content),
                "results_with_snippet": sum(1 for r in results if r.snippet),
                "avg_content_length": statistics.mean(
                    [len(r.content or "") for r in results]
                ),
            },
        )

    async def calculate_performance_score(
        self, execution_time_ms: float, result_count: int
    ) -> QualityScore:
        """Calculate performance score."""
        # Performance scoring based on execution time and result count
        if result_count == 0:
            return QualityScore(
                metric=QualityMetric.PERFORMANCE, score=0.0, confidence=0.0
            )

        # Target performance: <1s for 10 results
        target_time = 1000.0  # 1 second
        actual_time = execution_time_ms

        # Performance score based on time efficiency
        if actual_time <= target_time:
            time_score = 1.0
        elif actual_time <= target_time * 2:
            time_score = 0.8
        elif actual_time <= target_time * 5:
            time_score = 0.6
        else:
            time_score = 0.4

        # Adjust for result count (more results = more complex)
        result_factor = min(1.0, result_count / 10.0)

        overall_performance = time_score * (0.7 + 0.3 * result_factor)
        confidence = 0.95

        return QualityScore(
            metric=QualityMetric.PERFORMANCE,
            score=overall_performance,
            confidence=confidence,
            details={
                "execution_time_ms": actual_time_ms,
                "result_count": result_count,
                "target_time_ms": target_time,
                "time_score": time_score,
                "result_factor": result_factor,
            },
        )


class ValidationRuleEngine:
    """Manages and executes validation rules."""

    def __init__(self):
        self.rules: Dict[str, ValidationRule] = {}
        self.rule_templates = self._create_rule_templates()
        self._initialize_default_rules()

    def _create_rule_templates(self) -> Dict[str, Dict[str, Any]]:
        """Create rule templates."""
        return {
            "relevance_minimum": {
                "name": "Minimum Relevance Score",
                "description": "Results must meet minimum relevance threshold",
                "metric": QualityMetric.RELEVANCE,
                "threshold": 0.4,
                "weight": 1.0,
            },
            "freshness_recent": {
                "name": "Recent Content Preference",
                "description": "Prefer recent content for news queries",
                "metric": QualityMetric.FRESHNESS,
                "threshold": 0.6,
                "weight": 0.8,
                "conditions": {"query_types": ["news", "recent"]},
            },
            "authority_high": {
                "name": "High Authority Requirement",
                "description": "Require high authority for academic queries",
                "metric": QualityMetric.AUTHORITY,
                "threshold": 0.8,
                "weight": 1.0,
                "conditions": {"query_types": ["academic", "research"]},
            },
            "diversity_minimum": {
                "name": "Minimum Diversity",
                "description": "Results must show source diversity",
                "metric": QualityMetric.DIVERSITY,
                "threshold": 0.3,
                "weight": 0.7,
            },
            "performance_acceptable": {
                "name": "Acceptable Performance",
                "description": "Search must complete within acceptable time",
                "metric": QualityMetric.PERFORMANCE,
                "threshold": 0.6,
                "weight": 0.5,
            },
        }

    def _initialize_default_rules(self):
        """Initialize default validation rules."""
        for template_id, template in self.rule_templates.items():
            rule = ValidationRule(rule_id=template_id, **template)
            self.rules[template_id] = rule

    def add_rule(self, rule: ValidationRule):
        """Add a new validation rule."""
        self.rules[rule.rule_id] = rule
        logger.info(f"Added validation rule: {rule.name}")

    def remove_rule(self, rule_id: str) -> bool:
        """Remove a validation rule."""
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info(f"Removed validation rule: {rule_id}")
            return True
        return False

    def enable_rule(self, rule_id: str) -> bool:
        """Enable a validation rule."""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = True
            return True
        return False

    def disable_rule(self, rule_id: str) -> bool:
        """Disable a validation rule."""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = False
            return True
        return False

    def get_applicable_rules(
        self, query: SearchQuery, validation_level: ValidationLevel
    ) -> List[ValidationRule]:
        """Get rules applicable to query and validation level."""
        applicable_rules = []

        for rule in self.rules.values():
            if not rule.enabled:
                continue

            # Check validation level
            if validation_level == ValidationLevel.BASIC and rule.weight < 0.5:
                continue
            elif validation_level == ValidationLevel.STANDARD and rule.weight < 0.7:
                continue
            elif (
                validation_level == ValidationLevel.COMPREHENSIVE and rule.weight < 0.9
            ):
                continue

            # Check conditions
            conditions_met = True
            for condition_key, condition_value in rule.conditions.items():
                if condition_key == "query_types":
                    query_type = self._classify_query_type(query)
                    if query_type not in condition_value:
                        conditions_met = False
                        break

            if conditions_met:
                applicable_rules.append(rule)

        return applicable_rules

    def _classify_query_type(self, query: SearchQuery) -> str:
        """Classify query type for rule conditions."""
        query_lower = query.text.lower()

        if any(word in query_lower for word in ["news", "recent", "latest", "today"]):
            return "news"
        elif any(
            word in query_lower for word in ["academic", "research", "study", "paper"]
        ):
            return "academic"
        elif any(word in query_lower for word in ["recent", "new", "latest"]):
            return "recent"
        else:
            return "general"

    def validate_scores(
        self, scores: List[QualityScore], rules: List[ValidationRule]
    ) -> Tuple[bool, List[str]]:
        """Validate quality scores against rules."""
        issues = []
        all_passed = True

        score_dict = {score.metric: score for score in scores}

        for rule in rules:
            score = score_dict.get(rule.metric)
            if not score:
                issues.append(f"Missing score for metric: {rule.metric.value}")
                all_passed = False
                continue

            if score.score < rule.threshold:
                issues.append(
                    f"{rule.name}: Score {score.score:.2f} below threshold {rule.threshold}"
                )
                all_passed = False

        return all_passed, issues


class QualityAssuranceEngine:
    """Main quality assurance engine."""

    def __init__(self):
        self.metrics_calculator = QualityMetricsCalculator()
        self.rule_engine = ValidationRuleEngine()
        self.assessment_history: deque = deque(maxlen=1000)
        self.quality_trends: Dict[str, List[float]] = defaultdict(list)
        self._monitoring_task: Optional[asyncio.Task] = None

    async def start_monitoring(self):
        """Start quality monitoring."""
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Quality assurance monitoring started")

    async def stop_monitoring(self):
        """Stop quality monitoring."""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("Quality assurance monitoring stopped")

    async def assess_quality(
        self,
        query: SearchQuery,
        results: List[SearchResult],
        execution_time_ms: Optional[float] = None,
        validation_level: ValidationLevel = ValidationLevel.STANDARD,
    ) -> QualityAssessment:
        """Perform comprehensive quality assessment."""
        assessment_id = str(uuid.uuid4())

        # Calculate all metric scores
        metric_scores = []

        # Relevance
        relevance_score = await self.metrics_calculator.calculate_relevance_score(
            query, results
        )
        metric_scores.append(relevance_score)

        # Freshness
        freshness_score = await self.metrics_calculator.calculate_freshness_score(
            results
        )
        metric_scores.append(freshness_score)

        # Authority
        authority_score = await self.metrics_calculator.calculate_authority_score(
            results
        )
        metric_scores.append(authority_score)

        # Diversity
        diversity_score = await self.metrics_calculator.calculate_diversity_score(
            results
        )
        metric_scores.append(diversity_score)

        # Completeness
        completeness_score = await self.metrics_calculator.calculate_completeness_score(
            query, results
        )
        metric_scores.append(completeness_score)

        # Performance (if execution time provided)
        if execution_time_ms is not None:
            performance_score = (
                await self.metrics_calculator.calculate_performance_score(
                    execution_time_ms, len(results)
                )
            )
            metric_scores.append(performance_score)

        # Calculate weighted overall score
        overall_score = self._calculate_overall_score(metric_scores)

        # Determine quality level
        quality_level = self._determine_quality_level(overall_score)

        # Validate against rules
        applicable_rules = self.rule_engine.get_applicable_rules(
            query, validation_level
        )
        validation_passed, issues = self.rule_engine.validate_scores(
            metric_scores, applicable_rules
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(metric_scores, issues)

        # Create assessment
        assessment = QualityAssessment(
            assessment_id=assessment_id,
            query=query,
            results=results,
            overall_score=overall_score,
            metric_scores=metric_scores,
            quality_level=quality_level,
            issues=issues,
            recommendations=recommendations,
            validation_level=validation_level,
        )

        # Store assessment
        self.assessment_history.append(assessment)
        self._update_quality_trends(assessment)

        logger.info(
            f"Quality assessment {assessment_id}: score={overall_score:.2f}, level={quality_level.value}"
        )

        return assessment

    def _calculate_overall_score(self, metric_scores: List[QualityScore]) -> float:
        """Calculate weighted overall quality score."""
        total_weighted_score = 0.0
        total_weight = 0.0

        for score in metric_scores:
            weight = self.metrics_calculator.metric_weights.get(score.metric, 1.0)
            total_weighted_score += score.score * weight
            total_weight += weight

        return total_weighted_score / total_weight if total_weight > 0 else 0.0

    def _determine_quality_level(self, overall_score: float) -> QualityThreshold:
        """Determine quality Palmer quality level."""
        if overall_score >= QualityThreshold.EXCELLENT.value:
            return QualityThreshold.EXCELLENT
        elif overall_score >= QualityThreshold.GOOD.value:
            return QualityThreshold.GOOD
        elif overall_score >= QualityThreshold.FAIR.value:
            return QualityThreshold.FAIR
        else:
            return QualityThreshold.POOR

    def _generate_recommendations(
        self, metric_scores: List[QualityScore], issues: List[str]
    ) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []

        # Analyze low-scoring metrics
        low_metrics = [score for score in metric_scores if score.score < 0.5]

        for score in low_metrics:
            if score.metric == QualityMetric.RELEVANCE:
                recommendations.append(
                    "Improve query understanding and result matching"
                )
            elif score.metric == QualityMetric.FRESHNESS:
                recommendations.append("Prioritize more recent content sources")
            elif score.metric == QualityMetric.AUTHORITY:
                recommendations.append("Include more authoritative and trusted sources")
            elif score.metric == QualityMetric.DIVERSITY:
                recommendations.append("Increase source and provider diversity")
            elif score.metric == QualityMetric.COMPLETENESS:
                recommendations.append("Enhance result metadata and content extraction")
            elif score.metric == QualityMetric.PERFORMANCE:
                recommendations.append("Optimize search execution performance")

        # Add issue-specific recommendations
        for issue in issues:
            if "threshold" in issue:
                recommendations.append("Review and adjust quality thresholds")

        return list(set(recommendations))  # Remove duplicates

    def _update_quality_trends(self, assessment: QualityAssessment):
        """Update quality trend data."""
        date_key = assessment.assessed_at.date().isoformat()
        self.quality_trends[date_key].append(assessment.overall_score)

        # Keep only last 30 days
        if len(self.quality_trends) > 30:
            oldest_key = min(self.quality_trends.keys())
            del self.quality_trends[oldest_key]

    async def _monitoring_loop(self):
        """Quality monitoring loop."""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes

                # Analyze quality trends
                await self._analyze_quality_trends()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Quality monitoring error: {e}")

    async def _analyze_quality_trends(self):
        """Analyze quality trends and generate alerts."""
        if len(self.quality_trends) < 7:
            return  # Need at least a week of data

        # Calculate recent trend
        recent_days = sorted(self.quality_trends.keys())[-7:]
        recent_scores = []

        for day in recent_days:
            day_scores = self.quality_trends[day]
            if day_scores:
                recent_scores.append(statistics.mean(day_scores))

        if len(recent_scores) < 2:
            return

        # Calculate trend
        avg_recent = statistics.mean(recent_scores)

        # Check for quality degradation
        if avg_recent < QualityThreshold.FAIR.value:
            logger.warning(f"Quality degradation detected: avg score {avg_recent:.2f}")

        # Check for improvement
        elif avg_recent > QualityThreshold.GOOD.value:
            logger.info(f"Quality improvement: avg score {avg_recent:.2f}")

    def get_quality_report(self, days: int = 7) -> Dict[str, Any]:
        """Generate quality report."""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_assessments = [
            assessment
            for assessment in self.assessment_history
            if assessment.assessed_at >= cutoff_date
        ]

        if not recent_assessments:
            return {"message": f"No assessments in last {days} days"}

        # Calculate statistics
        overall_scores = [assessment.overall_score for assessment in recent_assessments]
        quality_levels = [assessment.quality_level for assessment in recent_assessments]

        level_counts = defaultdict(int)
        for level in quality_levels:
            level_counts[level.value] += 1

        # Metric averages
        metric_averages = defaultdict(list)
        for assessment in recent_assessments:
            for score in assessment.metric_scores:
                metric_averages[score.metric.value].append(score.score)

        metric_stats = {}
        for metric, scores in metric_averages.items():
            metric_stats[metric] = {
                "average": statistics.mean(scores),
                "min": min(scores),
                "max": max(scores),
                "count": len(scores),
            }

        return {
            "period_days": days,
            "total_assessments": len(recent_assessments),
            "overall_stats": {
                "average_score": statistics.mean(overall_scores),
                "min_score": min(overall_scores),
                "max_score": max(overall_scores),
                "score_std": (
                    statistics.stdev(overall_scores) if len(overall_scores) > 1 else 0
                ),
            },
            "quality_distribution": dict(level_counts),
            "metric_stats": metric_stats,
            "top_issues": self._get_top_issues(recent_assessments),
            "recommendations_summary": self._get_recommendations_summary(
                recent_assessments
            ),
        }

    def _get_top_issues(self, assessments: List[QualityAssessment]) -> List[str]:
        """Get most common quality issues."""
        issue_counts = defaultdict(int)

        for assessment in assessments:
            for issue in assessment.issues:
                issue_counts[issue] += 1

        # Sort by frequency and return top 5
        sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        return [issue for issue, count in sorted_issues[:5]]

    def _get_recommendations_summary(
        self, assessments: List[QualityAssessment]
    ) -> List[str]:
        """Get summary of recommendations."""
        recommendation_counts = defaultdict(int)

        for assessment in assessments:
            for recommendation in assessment.recommendations:
                recommendation_counts[recommendation] += 1

        # Sort by frequency and return top 5
        sorted_recommendations = sorted(
            recommendation_counts.items(), key=lambda x: x[1], reverse=True
        )
        return [rec for rec, count in sorted_recommendations[:5]]


# Global quality assurance engine
quality_assurance_engine = QualityAssuranceEngine()
