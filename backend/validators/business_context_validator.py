"""
Business Context Validator

Comprehensive validation module for business context data
with schema validation, quality assessment, and consistency checks.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import json
import re

from schemas.business_context import BusinessContext, ValidationError

logger = logging.getLogger(__name__)


class BusinessContextValidationError(Exception):
    """Business context validation error."""

    def __init__(
        self, message: str, errors: List[str] = None, warnings: List[str] = None
    ):
        self.message = message
        self.errors = errors or []
        self.warnings = warnings or []
        super().__init__(message)


class BusinessContextValidator:
    """Comprehensive business context validator."""

    def __init__(self):
        """Initialize validator."""
        self.logger = logging.getLogger(__name__)

    def validate_from_dict(
        self, data: Dict[str, Any]
    ) -> Tuple[BusinessContext, Dict[str, Any]]:
        """
        Validate business context from dictionary data.

        Args:
            data: Dictionary data to validate

        Returns:
            Tuple of (validated BusinessContext, validation results)

        Raises:
            BusinessContextValidationError: If validation fails
        """
        try:
            # Create BusinessContext instance
            context = BusinessContext(**data)

            # Perform additional validation
            validation_results = self._validate_comprehensive(context)

            # Update context with calculated values
            context.completion_percentage = context.calculate_completion_percentage()
            context.updated_at = datetime.utcnow()

            # Check if context is valid enough
            if not validation_results["is_valid"]:
                raise BusinessContextValidationError(
                    "Business context validation failed",
                    validation_results["issues"],
                    validation_results["warnings"],
                )

            return context, validation_results

        except ValidationError as e:
            raise BusinessContextValidationError(
                f"Schema validation failed: {str(e)}", [str(e)]
            )
        except Exception as e:
            raise BusinessContextValidationError(
                f"Validation failed: {str(e)}", [str(e)]
            )

    def validate_from_json(
        self, json_str: str
    ) -> Tuple[BusinessContext, Dict[str, Any]]:
        """
        Validate business context from JSON string.

        Args:
            json_str: JSON string to validate

        Returns:
            Tuple of (validated BusinessContext, validation results)

        Raises:
            BusinessContextValidationError: If validation fails
        """
        try:
            data = json.loads(json_str)
            return self.validate_from_dict(data)
        except json.JSONDecodeError as e:
            raise BusinessContextValidationError(
                f"Invalid JSON: {str(e)}", [f"JSON parsing error: {str(e)}"]
            )

    def _validate_comprehensive(self, context: BusinessContext) -> Dict[str, Any]:
        """
        Perform comprehensive validation of business context.

        Args:
            context: BusinessContext to validate

        Returns:
            Validation results dictionary
        """
        results = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "score": 1.0,
            "completeness": 0.0,
            "consistency": 0.0,
            "quality": 0.0,
        }

        # 1. Schema validation (already done by Pydantic)
        # 2. Business logic validation
        self._validate_business_logic(context, results)

        # 3. Data quality validation
        self._validate_data_quality(context, results)

        # 4. Consistency validation
        self._validate_consistency(context, results)

        # 5. Completeness validation
        completeness = self._calculate_completeness(context)
        results["completeness"] = completeness

        # 6. Calculate overall scores
        results["quality"] = context.validate_quality()["score"]
        results["score"] = self._calculate_overall_score(results)
        results["is_valid"] = len(results["errors"]) == 0

        return results

    def _validate_business_logic(
        self, context: BusinessContext, results: Dict[str, Any]
    ):
        """Validate business logic rules."""
        errors = []
        warnings = []

        # Check brand identity
        if not context.identity.name or len(context.identity.name.strip()) < 2:
            errors.append("Brand name is required and must be at least 2 characters")

        if (
            not context.identity.core_promise
            or len(context.identity.core_promise.strip()) < 10
        ):
            errors.append("Core promise is required and must be at least 10 characters")

        # Check audience definition
        if (
            not context.audience.primary_segment
            or len(context.audience.primary_segment.strip()) < 5
        ):
            errors.append(
                "Primary audience segment is required and must be at least 5 characters"
            )

        if len(context.audience.pain_points) < 2:
            warnings.append(
                "Consider adding more pain points for better audience understanding"
            )

        if len(context.audience.desires) < 2:
            warnings.append(
                "Consider adding more desires for better audience understanding"
            )

        # Check market positioning
        if not context.positioning.category:
            errors.append("Market category is required")

        if (
            not context.positioning.differentiator
            or len(context.positioning.differentiator.strip()) < 10
        ):
            errors.append(
                "Market differentiator is required and must be at least 10 characters"
            )

        # Check ICP profiles
        if context.icp_profiles:
            for i, icp in enumerate(context.icp_profiles):
                if not icp.name or len(icp.name.strip()) < 2:
                    errors.append(f"ICP profile {i+1} name is required")

                if not icp.value_proposition or len(icp.value_proposition.strip()) < 10:
                    errors.append(f"ICP profile {i+1} value proposition is required")

                if icp.priority not in [1, 2, 3]:
                    errors.append(f"ICP profile {i+1} priority must be 1, 2, or 3")

        # Check channel strategies
        if context.channel_strategies:
            for i, strategy in enumerate(context.channel_strategies):
                if not strategy.channel or len(strategy.channel.strip()) < 2:
                    errors.append(f"Channel strategy {i+1} channel name is required")

                if strategy.budget_allocation and (
                    strategy.budget_allocation < 0 or strategy.budget_allocation > 100
                ):
                    errors.append(
                        f"Channel strategy {i+1} budget allocation must be between 0 and 100"
                    )

        results["errors"].extend(errors)
        results["warnings"].extend(warnings)

    def _validate_data_quality(self, context: BusinessContext, results: Dict[str, Any]):
        """Validate data quality and completeness."""
        warnings = []

        # Check for empty or minimal content
        if context.identity.name and len(context.identity.name.strip()) < 3:
            warnings.append("Brand name seems too short for a professional business")

        if (
            context.identity.core_promise
            and len(context.identity.core_promise.strip()) < 20
        ):
            warnings.append(
                "Core promise seems too brief for meaningful differentiation"
            )

        # Check for generic or placeholder content
        generic_terms = [
            "test",
            "example",
            "sample",
            "placeholder",
            "todo",
            "coming soon",
        ]
        content_fields = [
            context.identity.name,
            context.identity.core_promise,
            context.audience.primary_segment,
            context.positioning.category,
            context.positioning.differentiator,
        ]

        for field in content_fields:
            if field and any(term in field.lower() for term in generic_terms):
                warnings.append(
                    f"Generic content detected: '{field}' - please provide specific business information"
                )

        # Check for sufficient detail
        if len(context.audience.pain_points) < 3:
            warnings.append(
                "Consider adding more pain points for comprehensive audience understanding"
            )

        if len(context.audience.desires) < 3:
            warnings.append(
                "Consider adding more desires for comprehensive audience understanding"
            )

        # Check messaging framework
        if context.messaging_framework:
            if (
                not context.messaging_framework.core_message
                or len(context.messaging_framework.core_message.strip()) < 15
            ):
                warnings.append(
                    "Core message should be more descriptive for effective communication"
                )

            if len(context.messaging_framework.supporting_points) < 2:
                warnings.append(
                    "Add more supporting points to strengthen the messaging framework"
                )

        results["warnings"].extend(warnings)

    def _validate_consistency(self, context: BusinessContext, results: Dict[str, Any]):
        """Validate consistency across different components."""
        warnings = []
        consistency_score = 1.0

        # Check brand name consistency
        brand_name = context.identity.name.lower() if context.identity.name else ""

        if context.positioning.positioning_statement:
            if (
                brand_name
                and brand_name not in context.positioning.positioning_statement.lower()
            ):
                warnings.append(
                    "Consider including brand name in positioning statement for consistency"
                )
                consistency_score -= 0.1

        if context.messaging_framework.core_message:
            if (
                brand_name
                and brand_name not in context.messaging_framework.core_message.lower()
            ):
                warnings.append(
                    "Consider including brand name in core message for consistency"
                )
                consistency_score -= 0.1

        # Check audience-ICP alignment
        if context.icp_profiles and context.audience.primary_segment:
            audience_keywords = context.audience.primary_segment.lower().split()
            icp_alignment = False

            for icp in context.icp_profiles:
                icp_keywords = (
                    icp.description.lower().split() if icp.description else []
                )
                if any(keyword in icp_keywords for keyword in audience_keywords):
                    icp_alignment = True
                    break

            if not icp_alignment:
                warnings.append(
                    "Consider aligning ICP profiles with primary audience segment"
                )
                consistency_score -= 0.15

        # Check positioning-messaging alignment
        if (
            context.positioning.differentiator
            and context.messaging_framework.value_proposition
        ):
            differentiator_keywords = set(
                context.positioning.differentiator.lower().split()
            )
            value_prop_keywords = set(
                context.messaging_framework.value_proposition.lower().split()
            )

            if not differentiator_keywords.intersection(value_prop_keywords):
                warnings.append(
                    "Consider aligning value proposition with market differentiator"
                )
                consistency_score -= 0.1

        # Check channel-audience alignment
        if context.channel_strategies and context.audience.media_consumption:
            channel_names = [
                strategy.channel.lower() for strategy in context.channel_strategies
            ]
            media_channels = [
                media.lower() for media in context.audience.media_consumption
            ]

            if not any(channel in media_channels for channel in channel_names):
                warnings.append(
                    "Consider aligning channel strategies with audience media consumption habits"
                )
                consistency_score -= 0.1

        results["warnings"].extend(warnings)
        results["consistency"] = max(0.0, consistency_score)

    def _calculate_completeness(self, context: BusinessContext) -> float:
        """Calculate completeness score based on filled fields."""
        return context.calculate_completion_percentage() / 100.0

    def _calculate_overall_score(self, results: Dict[str, Any]) -> float:
        """Calculate overall validation score."""
        # Weight different aspects
        weights = {"completeness": 0.3, "consistency": 0.3, "quality": 0.4}

        score = (
            results["completeness"] * weights["completeness"]
            + results["consistency"] * weights["consistency"]
            + results["quality"] * weights["quality"]
        )

        # Penalize errors heavily
        if results["errors"]:
            score -= len(results["errors"]) * 0.2

        # Penalize warnings lightly
        if results["warnings"]:
            score -= len(results["warnings"]) * 0.05

        return max(0.0, min(1.0, score))

    def generate_validation_report(
        self, context: BusinessContext, results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        return {
            "validation_timestamp": datetime.utcnow().isoformat(),
            "context_summary": context.to_summary(),
            "validation_results": results,
            "recommendations": self._generate_recommendations(results),
            "next_steps": self._generate_next_steps(context, results),
            "quality_metrics": {
                "completeness_percentage": context.calculate_completion_percentage(),
                "validation_score": results["score"],
                "error_count": len(results["errors"]),
                "warning_count": len(results["warnings"]),
                "is_ready_for_use": results["is_valid"] and results["score"] >= 0.7,
            },
        }

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations based on validation results."""
        recommendations = []

        if results["completeness"] < 0.8:
            recommendations.append(
                "Complete missing required fields to improve completeness"
            )

        if results["consistency"] < 0.8:
            recommendations.append("Align different components for better consistency")

        if results["quality"] < 0.7:
            recommendations.append(
                "Enhance data quality with more specific and detailed information"
            )

        # Specific recommendations based on errors
        for error in results["errors"]:
            if "required" in error.lower():
                recommendations.append(f"Add required information: {error}")
            elif "must be at least" in error.lower():
                recommendations.append(
                    f"Expand content to meet minimum requirements: {error}"
                )

        # Specific recommendations based on warnings
        for warning in results["warnings"]:
            if "consider adding" in warning.lower():
                recommendations.append(warning)
            elif "generic content" in warning.lower():
                recommendations.append(
                    "Replace placeholder content with specific business information"
                )

        return recommendations

    def _generate_next_steps(
        self, context: BusinessContext, results: Dict[str, Any]
    ) -> List[str]:
        """Generate next steps based on validation results."""
        next_steps = []

        if not results["is_valid"]:
            next_steps.append("Fix all validation errors before proceeding")
            return next_steps

        if results["score"] < 0.7:
            next_steps.append(
                "Improve data quality to achieve a better validation score"
            )

        if not context.icp_profiles:
            next_steps.append("Add Ideal Customer Profiles for better targeting")

        if not context.channel_strategies:
            next_steps.append("Define channel strategies for go-to-market planning")

        if not context.competitive_position.primary_competitors:
            next_steps.append("Identify primary competitors for competitive analysis")

        if context.status == "draft":
            next_steps.append("Review and publish the business context when ready")

        next_steps.append("Schedule regular reviews to keep business context updated")

        return next_steps


# Global validator instance
business_context_validator = BusinessContextValidator()
