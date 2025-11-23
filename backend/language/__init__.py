"""
Language Excellence Engine - Unified API for multi-layer language optimization.
Combines grammar, style, readability, tone, and diversity analysis.
"""

import structlog
from typing import Dict, Any, List, Optional
from datetime import datetime

from .grammar_orchestrator import grammar_orchestrator, GrammarOrchestrator
from .style_enforcer import style_enforcer, StyleEnforcer, BrandStyleGuide
from .readability_optimizer import readability_optimizer, ReadabilityOptimizer
from .tone_adapter import tone_adapter, ToneAdapter, ToneProfile
from .linguistic_diversity import linguistic_diversity_analyzer, LinguisticDiversityAnalyzer

logger = structlog.get_logger(__name__)


# Export all classes and singletons
__all__ = [
    'optimize_language',
    'GrammarOrchestrator',
    'StyleEnforcer',
    'ReadabilityOptimizer',
    'ToneAdapter',
    'LinguisticDiversityAnalyzer',
    'BrandStyleGuide',
    'ToneProfile',
    'grammar_orchestrator',
    'style_enforcer',
    'readability_optimizer',
    'tone_adapter',
    'linguistic_diversity_analyzer'
]


async def optimize_language(
    content: str,
    target_tone: Optional[str] = None,
    style_guide: Optional[BrandStyleGuide] = None,
    target_grade_level: Optional[int] = None,
    run_grammar: bool = True,
    run_style: bool = True,
    run_readability: bool = True,
    run_tone: bool = True,
    run_diversity: bool = True,
    correlation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Unified entry point for comprehensive language optimization.

    Runs content through all language analysis engines and returns
    aggregated recommendations.

    Args:
        content: Text to analyze and optimize
        target_tone: Optional target tone for adaptation
        style_guide: Optional brand style guide
        target_grade_level: Optional target reading level (1-18)
        run_grammar: Whether to run grammar check (default: True)
        run_style: Whether to run style enforcement (default: True)
        run_readability: Whether to run readability analysis (default: True)
        run_tone: Whether to run tone analysis (default: True)
        run_diversity: Whether to run diversity analysis (default: True)
        correlation_id: Request correlation ID

    Returns:
        Comprehensive language analysis with scores, issues, and suggestions
    """
    logger.info(
        "Starting comprehensive language optimization",
        content_length=len(content),
        target_tone=target_tone,
        target_grade=target_grade_level,
        correlation_id=correlation_id
    )

    start_time = datetime.utcnow()
    results = {}

    # 1. Grammar Check
    if run_grammar:
        try:
            logger.info("Running grammar check", correlation_id=correlation_id)
            results["grammar"] = await grammar_orchestrator.check_grammar(
                content,
                correlation_id=correlation_id
            )
        except Exception as e:
            logger.error(f"Grammar check failed: {e}", correlation_id=correlation_id)
            results["grammar"] = {"error": str(e)}

    # 2. Style Enforcement
    if run_style:
        try:
            logger.info("Running style enforcement", correlation_id=correlation_id)
            enforcer = StyleEnforcer(style_guide) if style_guide else style_enforcer
            results["style"] = await enforcer.enforce_style(
                content,
                correlation_id=correlation_id
            )
        except Exception as e:
            logger.error(f"Style enforcement failed: {e}", correlation_id=correlation_id)
            results["style"] = {"error": str(e)}

    # 3. Readability Analysis
    if run_readability:
        try:
            logger.info("Running readability analysis", correlation_id=correlation_id)
            results["readability"] = await readability_optimizer.analyze_readability(
                content,
                target_grade_level=target_grade_level,
                correlation_id=correlation_id
            )
        except Exception as e:
            logger.error(f"Readability analysis failed: {e}", correlation_id=correlation_id)
            results["readability"] = {"error": str(e)}

    # 4. Tone Analysis
    if run_tone:
        try:
            logger.info("Running tone analysis", correlation_id=correlation_id)
            results["tone"] = await tone_adapter.analyze_tone(
                content,
                correlation_id=correlation_id
            )

            # If target tone specified, also adapt content
            if target_tone:
                logger.info(f"Adapting to target tone: {target_tone}", correlation_id=correlation_id)
                results["tone_adaptation"] = await tone_adapter.adapt_tone(
                    content,
                    target_tone,
                    correlation_id=correlation_id
                )
        except Exception as e:
            logger.error(f"Tone analysis failed: {e}", correlation_id=correlation_id)
            results["tone"] = {"error": str(e)}

    # 5. Linguistic Diversity Analysis
    if run_diversity:
        try:
            logger.info("Running diversity analysis", correlation_id=correlation_id)
            results["diversity"] = await linguistic_diversity_analyzer.analyze_diversity(
                content,
                correlation_id=correlation_id
            )
        except Exception as e:
            logger.error(f"Diversity analysis failed: {e}", correlation_id=correlation_id)
            results["diversity"] = {"error": str(e)}

    # Calculate overall quality score
    overall_score = _calculate_overall_score(results)

    # Aggregate all suggestions
    all_suggestions = _aggregate_suggestions(results)

    # Generate executive summary
    executive_summary = _generate_executive_summary(results, overall_score)

    duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

    response = {
        "overall_score": overall_score,
        "executive_summary": executive_summary,
        "results": results,
        "aggregated_suggestions": all_suggestions,
        "metadata": {
            "content_length": len(content),
            "engines_run": {
                "grammar": run_grammar,
                "style": run_style,
                "readability": run_readability,
                "tone": run_tone,
                "diversity": run_diversity
            },
            "target_tone": target_tone,
            "target_grade_level": target_grade_level,
            "duration_ms": duration_ms,
            "analyzed_at": start_time.isoformat(),
            "correlation_id": correlation_id
        }
    }

    logger.info(
        "Language optimization completed",
        overall_score=overall_score,
        duration_ms=duration_ms,
        correlation_id=correlation_id
    )

    return response


def _calculate_overall_score(results: Dict[str, Any]) -> int:
    """Calculate overall language quality score (0-100)."""
    scores = []
    weights = []

    # Grammar score (based on issue count)
    if "grammar" in results and "error" not in results["grammar"]:
        total_issues = results["grammar"].get("total_issues", 0)
        critical_issues = results["grammar"].get("critical_count", 0)

        # Deduct points for issues
        grammar_score = 100 - (critical_issues * 5) - (total_issues * 2)
        grammar_score = max(0, min(100, grammar_score))

        scores.append(grammar_score)
        weights.append(0.25)

    # Style score (based on violations)
    if "style" in results and "error" not in results["style"]:
        violations = results["style"].get("total_violations", 0)
        style_score = 100 - (violations * 3)
        style_score = max(0, min(100, style_score))

        scores.append(style_score)
        weights.append(0.15)

    # Readability score (based on grade level match)
    if "readability" in results and "error" not in results["readability"]:
        target_grade = results["readability"].get("target_grade_level")
        avg_grade = results["readability"].get("average_grade_level", 12)

        if target_grade:
            # Score based on proximity to target
            diff = abs(avg_grade - target_grade)
            readability_score = max(0, 100 - (diff * 10))
        else:
            # Score based on Flesch Reading Ease
            flesch_score = results["readability"]["metrics"].get("flesch_reading_ease", 50)
            readability_score = flesch_score

        scores.append(readability_score)
        weights.append(0.25)

    # Tone score (based on confidence)
    if "tone" in results and "error" not in results["tone"]:
        best_match = results["tone"].get("best_match")
        if best_match:
            tone_score = best_match.get("confidence", 50)
        else:
            tone_score = 50

        scores.append(tone_score)
        weights.append(0.15)

    # Diversity score
    if "diversity" in results and "error" not in results["diversity"]:
        diversity_score = results["diversity"].get("diversity_score", 50)
        scores.append(diversity_score)
        weights.append(0.20)

    # Calculate weighted average
    if scores:
        # Normalize weights
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]

        overall = sum(score * weight for score, weight in zip(scores, normalized_weights))
        return round(overall)

    return 50  # Default if no scores available


def _aggregate_suggestions(results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Aggregate suggestions from all engines."""
    all_suggestions = []

    # Grammar suggestions
    if "grammar" in results and "error" not in results["grammar"]:
        auto_fixes = results["grammar"].get("auto_fixes", [])
        for fix in auto_fixes[:5]:  # Top 5
            all_suggestions.append({
                "source": "grammar",
                "type": "auto_fix",
                "priority": "high",
                "issue": fix.get("issue"),
                "suggestion": fix.get("suggestion"),
                "confidence": fix.get("confidence")
            })

    # Style suggestions
    if "style" in results and "error" not in results["style"]:
        violations = results["style"].get("violations", [])
        for violation in violations[:5]:  # Top 5
            all_suggestions.append({
                "source": "style",
                "type": violation.get("type"),
                "priority": "medium",
                "issue": violation.get("message"),
                "suggestion": violation.get("suggestion")
            })

    # Readability suggestions
    if "readability" in results and "error" not in results["readability"]:
        suggestions = results["readability"].get("suggestions", [])
        for suggestion in suggestions[:5]:
            all_suggestions.append({
                "source": "readability",
                "type": suggestion.get("type"),
                "priority": suggestion.get("priority", "medium"),
                "issue": suggestion.get("message"),
                "impact": suggestion.get("impact")
            })

    # Diversity suggestions
    if "diversity" in results and "error" not in results["diversity"]:
        suggestions = results["diversity"].get("suggestions", [])
        for suggestion in suggestions[:5]:
            all_suggestions.append({
                "source": "diversity",
                "type": suggestion.get("type"),
                "priority": suggestion.get("priority", "medium"),
                "issue": suggestion.get("message"),
                "impact": suggestion.get("impact")
            })

    # Sort by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    all_suggestions.sort(key=lambda x: priority_order.get(x.get("priority", "medium"), 1))

    return all_suggestions[:15]  # Return top 15


def _generate_executive_summary(results: Dict[str, Any], overall_score: int) -> Dict[str, Any]:
    """Generate executive summary of language analysis."""
    summary = {
        "overall_quality": "excellent" if overall_score >= 85 else "good" if overall_score >= 70 else "fair" if overall_score >= 50 else "needs improvement",
        "key_strengths": [],
        "key_issues": [],
        "top_recommendations": []
    }

    # Identify strengths
    if "grammar" in results and results["grammar"].get("total_issues", 0) < 3:
        summary["key_strengths"].append("Clean grammar with minimal errors")

    if "readability" in results:
        flesch_score = results["readability"].get("metrics", {}).get("flesch_reading_ease", 0)
        if flesch_score >= 60:
            summary["key_strengths"].append("Good readability and clarity")

    if "diversity" in results and results["diversity"].get("diversity_score", 0) >= 70:
        summary["key_strengths"].append("Rich vocabulary and linguistic diversity")

    # Identify issues
    if "grammar" in results and results["grammar"].get("critical_count", 0) > 0:
        count = results["grammar"]["critical_count"]
        summary["key_issues"].append(f"{count} critical grammar errors require attention")

    if "style" in results and results["style"].get("total_violations", 0) > 5:
        count = results["style"]["total_violations"]
        summary["key_issues"].append(f"{count} style guide violations detected")

    if "readability" in results:
        avg_grade = results["readability"].get("average_grade_level", 0)
        if avg_grade > 14:
            summary["key_issues"].append("Content may be too complex for general audience")

    if "diversity" in results:
        repetition_score = results["diversity"].get("repetition_analysis", {}).get("repetition_score", 100)
        if repetition_score < 60:
            summary["key_issues"].append("Excessive word and phrase repetition")

    # Add top recommendations
    if "grammar" in results and results["grammar"].get("total_issues", 0) > 0:
        summary["top_recommendations"].append("Review and fix grammar issues using auto-fix suggestions")

    if "readability" in results:
        suggestions = results["readability"].get("suggestions", [])
        if suggestions:
            summary["top_recommendations"].append(suggestions[0].get("message", ""))

    if "diversity" in results:
        suggestions = results["diversity"].get("suggestions", [])
        if suggestions:
            summary["top_recommendations"].append(suggestions[0].get("message", ""))

    return summary
