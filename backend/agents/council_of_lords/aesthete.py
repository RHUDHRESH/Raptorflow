# backend/agents/council_of_lords/aesthete.py
# RaptorFlow Codex - Aesthete Lord Agent
# Phase 2A Week 5 - Brand Quality & Design Consistency

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import json
import logging
from abc import ABC

from agents.base_agent import BaseAgent, AgentType, AgentStatus, Capability, AgentRole

logger = logging.getLogger(__name__)

# ==============================================================================
# ENUMS
# ==============================================================================

class QualityLevel(str, Enum):
    """Quality assessment levels"""
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"
    OUTSTANDING = "outstanding"


class ContentType(str, Enum):
    """Types of content to review"""
    COPY = "copy"
    VISUAL = "visual"
    DESIGN = "design"
    MESSAGING = "messaging"
    BRANDING = "branding"
    VIDEO = "video"
    AUDIO = "audio"
    INTERACTIVE = "interactive"


class FeedbackCategory(str, Enum):
    """Categories of feedback"""
    BRAND_ALIGNMENT = "brand_alignment"
    VISUAL_CONSISTENCY = "visual_consistency"
    TONE_VOICE = "tone_voice"
    CLARITY = "clarity"
    ENGAGING = "engaging"
    TECHNICAL = "technical"
    ACCESSIBILITY = "accessibility"
    MOBILE_RESPONSIVE = "mobile_responsive"


# ==============================================================================
# DATA STRUCTURES
# ==============================================================================

class BrandGuideline:
    """Represents a brand guideline or rule"""

    def __init__(
        self,
        guideline_id: str,
        name: str,
        category: str,
        description: str,
        rules: List[str],
        examples: Dict[str, str] = None,
        weight: float = 1.0
    ):
        self.id = guideline_id
        self.name = name
        self.category = category
        self.description = description
        self.rules = rules
        self.examples = examples or {}
        self.weight = weight  # Importance weight (0.5-2.0)
        self.created_at = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "rules": self.rules,
            "examples": self.examples,
            "weight": self.weight,
            "created_at": self.created_at
        }


class QualityReview:
    """Represents a quality review of content"""

    def __init__(
        self,
        review_id: str,
        content_id: str,
        content_type: ContentType,
        guild_name: str,
        reviewed_by: str,
        overall_score: float,
        quality_level: QualityLevel,
        feedback_items: List[Dict[str, Any]] = None
    ):
        self.id = review_id
        self.content_id = content_id
        self.content_type = content_type
        self.guild_name = guild_name
        self.reviewed_by = reviewed_by
        self.overall_score = overall_score  # 0.0-100.0
        self.quality_level = quality_level
        self.feedback_items = feedback_items or []
        self.strengths: List[str] = []
        self.improvements: List[str] = []
        self.action_items: List[str] = []
        self.approved = False
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content_id": self.content_id,
            "content_type": self.content_type.value,
            "guild_name": self.guild_name,
            "reviewed_by": self.reviewed_by,
            "overall_score": self.overall_score,
            "quality_level": self.quality_level.value,
            "feedback_items": self.feedback_items,
            "strengths": self.strengths,
            "improvements": self.improvements,
            "action_items": self.action_items,
            "approved": self.approved,
            "created_at": self.created_at
        }


class ConsistencyReport:
    """Report on design/brand consistency"""

    def __init__(
        self,
        report_id: str,
        scope: str,  # e.g., "campaign", "guild", "organization"
        scope_id: str,
        items_reviewed: int,
        consistent_items: int,
        inconsistency_type: List[str]
    ):
        self.id = report_id
        self.scope = scope
        self.scope_id = scope_id
        self.items_reviewed = items_reviewed
        self.consistent_items = consistent_items
        self.inconsistency_type = inconsistency_type
        self.consistency_percent = (consistent_items / items_reviewed * 100) if items_reviewed > 0 else 0.0
        self.issues: List[Dict[str, Any]] = []
        self.recommendations: List[str] = []
        self.created_at = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "scope": self.scope,
            "scope_id": self.scope_id,
            "items_reviewed": self.items_reviewed,
            "consistent_items": self.consistent_items,
            "consistency_percent": self.consistency_percent,
            "inconsistency_types": self.inconsistency_type,
            "issues": self.issues,
            "recommendations": self.recommendations,
            "created_at": self.created_at
        }


# ==============================================================================
# AESTHETE LORD AGENT
# ==============================================================================

class AestheteLord(BaseAgent):
    """
    The Aesthete Lord ensures brand consistency, design quality, and content
    excellence across all organizational outputs. Maintains visual identity,
    brand voice, and quality standards.

    Key Responsibilities:
    - Assess brand and design quality
    - Enforce brand guidelines
    - Check visual consistency
    - Provide design feedback
    - Monitor brand compliance
    - Support guild improvement
    """

    def __init__(self):
        super().__init__(
            name="Aesthete",
            agent_type=AgentType.INTELLIGENCE,
            role=AgentRole.AESTHETE
        )

        # Brand and quality storage
        self.brand_guidelines: Dict[str, BrandGuideline] = {}
        self.quality_reviews: Dict[str, QualityReview] = {}
        self.consistency_reports: Dict[str, ConsistencyReport] = {}

        # Metrics
        self.total_reviews_conducted = 0
        self.total_guidelines_maintained = 0
        self.average_quality_score = 0.0
        self.brand_consistency_score = 0.0
        self.approval_rate = 0.0

        # Register capabilities
        self.register_capability(
            Capability(
                name="assess_quality",
                description="Assess content quality against standards",
                handler=self._assess_quality
            )
        )

        self.register_capability(
            Capability(
                name="check_brand_compliance",
                description="Check compliance with brand guidelines",
                handler=self._check_brand_compliance
            )
        )

        self.register_capability(
            Capability(
                name="evaluate_visual_consistency",
                description="Evaluate design consistency",
                handler=self._evaluate_visual_consistency
            )
        )

        self.register_capability(
            Capability(
                name="provide_design_feedback",
                description="Provide constructive design feedback",
                handler=self._provide_design_feedback
            )
        )

        self.register_capability(
            Capability(
                name="approve_content",
                description="Approve content for publication",
                handler=self._approve_content
            )
        )

        logger.info(f"✅ Aesthete Lord initialized with {len(self.capabilities)} capabilities")

    # ========================================================================
    # CAPABILITY HANDLERS
    # ========================================================================

    async def _assess_quality(self, **kwargs) -> Dict[str, Any]:
        """Assess content quality"""
        try:
            content_id = kwargs.get("content_id", "")
            content_type_str = kwargs.get("content_type", "copy")
            guild_name = kwargs.get("guild_name", "")
            content_metrics = kwargs.get("content_metrics", {})

            content_type = ContentType(content_type_str)

            # Generate review ID
            review_id = f"review_{self.total_reviews_conducted + 1}_{int(datetime.utcnow().timestamp())}"

            # Calculate quality score (simplified)
            quality_score = self._calculate_quality_score(content_metrics)
            quality_level = self._get_quality_level(quality_score)

            # Create review
            review = QualityReview(
                review_id=review_id,
                content_id=content_id,
                content_type=content_type,
                guild_name=guild_name,
                reviewed_by=self.name,
                overall_score=quality_score,
                quality_level=quality_level
            )

            # Add feedback based on metrics
            if content_metrics.get("readability_score", 0) < 70:
                review.improvements.append("Improve content readability")
                review.action_items.append("Simplify complex sentences")

            if content_metrics.get("brand_adherence", 0) < 80:
                review.improvements.append("Strengthen brand alignment")
                review.action_items.append("Review brand guidelines")

            if content_metrics.get("engagement_potential", 0) > 80:
                review.strengths.append("High engagement potential")

            # Store review
            self.quality_reviews[review_id] = review
            self.total_reviews_conducted += 1

            logger.info(f"⭐ Quality review completed: {review_id} - Score: {quality_score}")

            return {
                "review_id": review_id,
                "content_id": content_id,
                "quality_level": quality_level.value,
                "overall_score": quality_score,
                "strengths": review.strengths,
                "improvements": review.improvements,
                "action_items": review.action_items,
                "created_at": review.created_at
            }

        except Exception as e:
            logger.error(f"❌ Error assessing quality: {e}")
            return {"error": str(e), "success": False}

    async def _check_brand_compliance(self, **kwargs) -> Dict[str, Any]:
        """Check brand compliance"""
        try:
            content_id = kwargs.get("content_id", "")
            guild_name = kwargs.get("guild_name", "")
            content_elements = kwargs.get("content_elements", {})

            # Check against guidelines
            compliance_issues = []
            compliance_score = 100.0

            # Brand tone check
            if "tone" in content_elements:
                if content_elements["tone"] not in ["professional", "friendly", "authoritative", "conversational"]:
                    compliance_issues.append("Tone doesn't match brand voice")
                    compliance_score -= 15

            # Visual identity check
            if "colors" in content_elements:
                brand_colors = ["#002147", "#0066CC", "#FFFFFF", "#F0F0F0"]
                for color in content_elements.get("colors", []):
                    if color not in brand_colors:
                        compliance_issues.append(f"Color {color} outside brand palette")
                        compliance_score -= 10

            # Logo usage check
            if "has_logo" in content_elements and not content_elements["has_logo"]:
                compliance_issues.append("Logo not properly placed")
                compliance_score -= 20

            compliance_score = max(0, min(100, compliance_score))

            logger.info(f"✅ Brand compliance check: {content_id} - Score: {compliance_score}")

            return {
                "content_id": content_id,
                "compliance_score": compliance_score,
                "is_compliant": compliance_score >= 80,
                "issues": compliance_issues,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Error checking brand compliance: {e}")
            return {"error": str(e), "success": False}

    async def _evaluate_visual_consistency(self, **kwargs) -> Dict[str, Any]:
        """Evaluate visual consistency"""
        try:
            scope = kwargs.get("scope", "campaign")  # campaign, guild, organization
            scope_id = kwargs.get("scope_id", "")
            items_count = kwargs.get("items_count", 0)
            consistency_data = kwargs.get("consistency_data", {})

            # Analyze consistency
            consistent_items = 0
            inconsistency_types = set()

            # Typography consistency
            font_variants = consistency_data.get("font_families", set())
            if len(font_variants) > 2:
                inconsistency_types.add("Too many font families")
            else:
                consistent_items += 1

            # Color consistency
            color_count = len(consistency_data.get("unique_colors", []))
            if color_count > 8:
                inconsistency_types.add("Too many colors")
            else:
                consistent_items += 1

            # Spacing consistency
            if consistency_data.get("spacing_consistent", False):
                consistent_items += 1
            else:
                inconsistency_types.add("Inconsistent spacing")

            # Generate report
            report_id = f"consistency_{int(datetime.utcnow().timestamp())}"
            report = ConsistencyReport(
                report_id=report_id,
                scope=scope,
                scope_id=scope_id,
                items_reviewed=items_count,
                consistent_items=consistent_items,
                inconsistency_type=list(inconsistency_types)
            )

            # Add recommendations
            if "Too many font families" in inconsistency_types:
                report.recommendations.append("Limit fonts to 2-3 families for consistency")

            if "Too many colors" in inconsistency_types:
                report.recommendations.append("Restrict palette to 5-8 brand colors")

            self.consistency_reports[report_id] = report
            self.brand_consistency_score = report.consistency_percent

            logger.info(f"📊 Consistency evaluated: {scope}/{scope_id} - {report.consistency_percent}%")

            return report.to_dict()

        except Exception as e:
            logger.error(f"❌ Error evaluating consistency: {e}")
            return {"error": str(e), "success": False}

    async def _provide_design_feedback(self, **kwargs) -> Dict[str, Any]:
        """Provide design feedback"""
        try:
            content_id = kwargs.get("content_id", "")
            content_type_str = kwargs.get("content_type", "design")
            design_elements = kwargs.get("design_elements", {})
            guild_name = kwargs.get("guild_name", "")

            feedback = {
                "strengths": [],
                "areas_for_improvement": [],
                "specific_suggestions": [],
                "priority_recommendations": []
            }

            # Analyze design elements
            layout = design_elements.get("layout", "")
            if layout == "balanced":
                feedback["strengths"].append("Good visual balance and hierarchy")
            elif layout == "cluttered":
                feedback["areas_for_improvement"].append("Reduce visual clutter")
                feedback["specific_suggestions"].append("Increase white space")

            # Color analysis
            color_harmony = design_elements.get("color_harmony", "")
            if color_harmony == "cohesive":
                feedback["strengths"].append("Strong color cohesion")
            else:
                feedback["areas_for_improvement"].append("Improve color harmony")

            # Typography
            typog_hierarchy = design_elements.get("typography_hierarchy", "")
            if not typog_hierarchy:
                feedback["priority_recommendations"].append("Establish clear typography hierarchy")

            logger.info(f"💬 Design feedback provided for {content_id}")

            return {
                "content_id": content_id,
                "guild_name": guild_name,
                "feedback": feedback,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Error providing feedback: {e}")
            return {"error": str(e), "success": False}

    async def _approve_content(self, **kwargs) -> Dict[str, Any]:
        """Approve content for publication"""
        try:
            review_id = kwargs.get("review_id", "")
            approval_notes = kwargs.get("approval_notes", "")

            if review_id not in self.quality_reviews:
                return {"error": f"Review {review_id} not found", "success": False}

            review = self.quality_reviews[review_id]

            # Approve if quality score >= 75
            if review.overall_score >= 75:
                review.approved = True
                review.updated_at = datetime.utcnow().isoformat()
                self.approval_rate = sum(1 for r in self.quality_reviews.values() if r.approved) / len(self.quality_reviews)

                logger.info(f"✅ Content approved: {review_id}")

                return {
                    "review_id": review_id,
                    "approved": True,
                    "approval_notes": approval_notes,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "review_id": review_id,
                    "approved": False,
                    "reason": f"Quality score {review.overall_score} below threshold of 75",
                    "recommendations": review.action_items
                }

        except Exception as e:
            logger.error(f"❌ Error approving content: {e}")
            return {"error": str(e), "success": False}

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def _calculate_quality_score(self, metrics: Dict[str, float]) -> float:
        """Calculate quality score from metrics"""
        score = 80.0  # Base score

        # Adjust based on metrics
        if metrics.get("readability_score", 100) < 70:
            score -= 10
        if metrics.get("brand_adherence", 100) < 80:
            score -= 15
        if metrics.get("engagement_potential", 0) > 85:
            score += 10
        if metrics.get("error_count", 0) > 0:
            score -= (metrics["error_count"] * 2)

        return min(100, max(0, score))

    def _get_quality_level(self, score: float) -> QualityLevel:
        """Determine quality level from score"""
        if score >= 90:
            return QualityLevel.OUTSTANDING
        elif score >= 80:
            return QualityLevel.EXCELLENT
        elif score >= 70:
            return QualityLevel.GOOD
        elif score >= 50:
            return QualityLevel.FAIR
        else:
            return QualityLevel.POOR

    async def get_recent_reviews(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent reviews"""
        sorted_reviews = sorted(
            self.quality_reviews.values(),
            key=lambda x: x.created_at,
            reverse=True
        )
        return [r.to_dict() for r in sorted_reviews[:limit]]

    async def get_approved_content(self) -> List[str]:
        """Get approved content IDs"""
        return [r.content_id for r in self.quality_reviews.values() if r.approved]

    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get Aesthete performance summary"""
        approved_count = sum(1 for r in self.quality_reviews.values() if r.approved)

        if self.quality_reviews:
            self.average_quality_score = sum(r.overall_score for r in self.quality_reviews.values()) / len(self.quality_reviews)
            self.approval_rate = approved_count / len(self.quality_reviews) * 100

        return {
            "total_reviews_conducted": self.total_reviews_conducted,
            "average_quality_score": self.average_quality_score,
            "approval_rate": self.approval_rate,
            "brand_consistency_score": self.brand_consistency_score,
            "approved_content_count": approved_count,
            "total_guidelines": len(self.brand_guidelines)
        }
