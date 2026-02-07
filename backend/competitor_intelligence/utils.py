"""
Utilities and helper functions for competitor intelligence
"""

import hashlib
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from .config import CompetitorAlertType, CompetitorConfig, CompetitorDataSource

logger = logging.getLogger("raptorflow.competitor_intelligence.utils")


def generate_competitor_id(name: str, website: Optional[str] = None) -> str:
    """Generate a unique competitor ID."""
    base_string = name.lower()
    if website:
        base_string += f"_{website}"

    # Create hash for uniqueness
    hash_obj = hashlib.md5(base_string.encode())
    return f"comp_{hash_obj.hexdigest()[:8]}"


def extract_competitor_mentions(text: str) -> List[str]:
    """Extract competitor mentions from text using @mentions."""
    mentions = re.findall(r"@(\w+)", text)
    return list(set(mentions))  # Remove duplicates


def sanitize_competitor_name(name: str) -> str:
    """Sanitize and normalize competitor name."""
    # Remove extra whitespace and special characters
    sanitized = re.sub(r"[^\w\s-]", "", name.strip())
    # Replace multiple spaces with single space
    sanitized = re.sub(r"\s+", " ", sanitized)
    return sanitized


def calculate_threat_level(
    market_share: Optional[float] = None,
    growth_rate: Optional[float] = None,
    funding_amount: Optional[float] = None,
    feature_similarity: Optional[float] = None,
) -> str:
    """Calculate competitor threat level based on various factors."""
    score = 0

    # Market share factor (0-30 points)
    if market_share:
        if market_share > 20:
            score += 30
        elif market_share > 10:
            score += 20
        elif market_share > 5:
            score += 10

    # Growth rate factor (0-25 points)
    if growth_rate:
        if growth_rate > 50:
            score += 25
        elif growth_rate > 25:
            score += 15
        elif growth_rate > 10:
            score += 10

    # Funding factor (0-20 points)
    if funding_amount:
        if funding_amount > 100000000:  # $100M+
            score += 20
        elif funding_amount > 10000000:  # $10M+
            score += 15
        elif funding_amount > 1000000:  # $1M+
            score += 10

    # Feature similarity factor (0-25 points)
    if feature_similarity:
        if feature_similarity > 0.8:
            score += 25
        elif feature_similarity > 0.6:
            score += 20
        elif feature_similarity > 0.4:
            score += 15
        elif feature_similarity > 0.2:
            score += 10

    # Determine threat level
    if score >= 70:
        return "critical"
    elif score >= 50:
        return "high"
    elif score >= 30:
        return "medium"
    else:
        return "low"


def validate_competitor_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and sanitize competitor data."""
    validated = {}

    # Required fields
    if "name" not in data or not data["name"]:
        raise ValueError("Competitor name is required")

    validated["name"] = sanitize_competitor_name(data["name"])

    # Optional fields with validation
    if "website" in data and data["website"]:
        website = data["website"].strip()
        if not website.startswith(("http://", "https://")):
            website = f"https://{website}"
        validated["website"] = website

    if "market_share" in data and data["market_share"] is not None:
        try:
            market_share = float(data["market_share"])
            validated["market_share"] = max(0, min(100, market_share))
        except (ValueError, TypeError):
            logger.warning(f"Invalid market_share value: {data['market_share']}")

    if "confidence_score" in data and data["confidence_score"] is not None:
        try:
            confidence = float(data["confidence_score"])
            validated["confidence_score"] = max(0.0, min(1.0, confidence))
        except (ValueError, TypeError):
            logger.warning(
                f"Invalid confidence_score value: {data['confidence_score']}"
            )

    # List fields
    for list_field in [
        "target_audience",
        "key_features",
        "strengths",
        "weaknesses",
        "opportunities",
        "threats",
        "marketing_channels",
        "tech_stack",
    ]:
        if list_field in data and data[list_field]:
            if isinstance(data[list_field], str):
                # Convert string to list
                validated[list_field] = [
                    item.strip() for item in data[list_field].split(",")
                ]
            elif isinstance(data[list_field], list):
                validated[list_field] = [
                    str(item).strip() for item in data[list_field] if item
                ]
            else:
                validated[list_field] = []

    return validated


def calculate_competitor_similarity(
    profile1: Dict[str, Any], profile2: Dict[str, Any]
) -> float:
    """Calculate similarity score between two competitor profiles."""
    similarity_score = 0.0
    total_factors = 0

    # Target audience similarity
    if "target_audience" in profile1 and "target_audience" in profile2:
        audience1 = set(profile1["target_audience"])
        audience2 = set(profile2["target_audience"])
        if audience1 or audience2:
            intersection = audience1.intersection(audience2)
            union = audience1.union(audience2)
            similarity_score += len(intersection) / len(union) if union else 0
            total_factors += 1

    # Feature similarity
    if "key_features" in profile1 and "key_features" in profile2:
        features1 = set(profile1["key_features"])
        features2 = set(profile2["key_features"])
        if features1 or features2:
            intersection = features1.intersection(features2)
            union = features1.union(features2)
            similarity_score += len(intersection) / len(union) if union else 0
            total_factors += 1

    # Market segment similarity
    if "competitor_type" in profile1 and "competitor_type" in profile2:
        if profile1["competitor_type"] == profile2["competitor_type"]:
            similarity_score += 1.0
        total_factors += 1

    # Pricing model similarity
    if "pricing_model" in profile1 and "pricing_model" in profile2:
        if profile1["pricing_model"] == profile2["pricing_model"]:
            similarity_score += 1.0
        total_factors += 1

    return similarity_score / total_factors if total_factors > 0 else 0.0


def format_competitor_summary(profile: Dict[str, Any]) -> str:
    """Format a competitor profile into a readable summary."""
    name = profile.get("name", "Unknown Competitor")
    competitor_type = profile.get("competitor_type", "unknown")
    threat_level = profile.get("threat_level", "unknown")

    summary_parts = [f"{name} ({competitor_type}, {threat_level} threat)"]

    if profile.get("market_share"):
        summary_parts.append(f"Market Share: {profile['market_share']}%")

    if profile.get("pricing_model"):
        summary_parts.append(f"Pricing: {profile['pricing_model']}")

    if profile.get("key_features"):
        features = profile["key_features"][:3]  # Limit to top 3
        summary_parts.append(f"Features: {', '.join(features)}")

    if profile.get("strengths"):
        strengths = profile["strengths"][:2]  # Limit to top 2
        summary_parts.append(f"Strengths: {', '.join(strengths)}")

    return " | ".join(summary_parts)


def filter_insights_by_relevance(
    insights: List[Dict[str, Any]], criteria: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Filter competitor insights based on relevance criteria."""
    filtered_insights = []

    for insight in insights:
        relevance_score = 0

        # Time relevance
        if "time_filter" in criteria:
            time_filter = criteria["time_filter"]
            discovered_at = insight.get("discovered_at")
            if discovered_at:
                if isinstance(discovered_at, str):
                    discovered_at = datetime.fromisoformat(discovered_at)

                now = datetime.now()
                if time_filter == "recent" and discovered_at > now - timedelta(days=7):
                    relevance_score += 2
                elif time_filter == "very_recent" and discovered_at > now - timedelta(
                    days=1
                ):
                    relevance_score += 3

        # Impact relevance
        if "impact_filter" in criteria:
            impact_filter = criteria["impact_filter"]
            insight_impact = insight.get("impact_assessment", "").lower()

            if impact_filter == "high" and insight_impact in ["high", "critical"]:
                relevance_score += 3
            elif impact_filter == "medium" and insight_impact in [
                "medium",
                "high",
                "critical",
            ]:
                relevance_score += 2

        # Type relevance
        if "type_filter" in criteria:
            type_filter = criteria["type_filter"]
            if insight.get("insight_type") == type_filter:
                relevance_score += 2

        # Confidence relevance
        if "confidence_filter" in criteria:
            min_confidence = criteria["confidence_filter"]
            insight_confidence = insight.get("confidence", 0)
            if insight_confidence >= min_confidence:
                relevance_score += 1

        # Include insight if it meets minimum relevance threshold
        if relevance_score >= criteria.get("min_relevance", 1):
            insight["relevance_score"] = relevance_score
            filtered_insights.append(insight)

    # Sort by relevance score
    filtered_insights.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

    return filtered_insights


def generate_competitor_alert(
    competitor_id: str,
    alert_type: CompetitorAlertType,
    title: str,
    description: str,
    severity: str = "medium",
    confidence: float = 0.8,
) -> Dict[str, Any]:
    """Generate a standardized competitor alert."""
    return {
        "id": f"alert_{competitor_id}_{int(datetime.now().timestamp())}",
        "competitor_id": competitor_id,
        "alert_type": alert_type.value,
        "title": title,
        "description": description,
        "severity": severity,
        "confidence": confidence,
        "created_at": datetime.now().isoformat(),
        "status": "active",
    }


def export_competitor_data(
    competitor_data: Dict[str, Any], format_type: str = "json"
) -> str:
    """Export competitor data in specified format."""
    if format_type == "json":
        return json.dumps(competitor_data, indent=2, default=str)
    elif format_type == "csv":
        # Simple CSV export for profiles
        if "profiles" in competitor_data:
            import csv
            import io

            output = io.StringIO()
            profiles = competitor_data["profiles"]

            if profiles:
                fieldnames = set()
                for profile in profiles:
                    fieldnames.update(profile.keys())

                writer = csv.DictWriter(output, fieldnames=list(fieldnames))
                writer.writeheader()

                for profile in profiles:
                    # Flatten list fields for CSV
                    flattened = {}
                    for key, value in profile.items():
                        if isinstance(value, list):
                            flattened[key] = "; ".join(str(v) for v in value)
                        else:
                            flattened[key] = value
                    writer.writerow(flattened)

                return output.getvalue()

        return "No profile data available for CSV export"

    else:
        raise ValueError(f"Unsupported export format: {format_type}")


def import_competitor_data(
    data_string: str, format_type: str = "json"
) -> Dict[str, Any]:
    """Import competitor data from specified format."""
    if format_type == "json":
        return json.loads(data_string)
    elif format_type == "csv":
        import csv
        import io

        input_io = io.StringIO(data_string)
        reader = csv.DictReader(input_io)

        profiles = []
        for row in reader:
            # Convert semicolon-separated fields back to lists
            processed_row = {}
            for key, value in row.items():
                if ";" in value:
                    processed_row[key] = [
                        item.strip() for item in value.split(";") if item.strip()
                    ]
                else:
                    processed_row[key] = value
            profiles.append(processed_row)

        return {"profiles": profiles}

    else:
        raise ValueError(f"Unsupported import format: {format_type}")
