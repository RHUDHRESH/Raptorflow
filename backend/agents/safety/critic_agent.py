"""
Enhanced Critic Agent - Multi-dimensional content quality evaluation with language excellence engine.

This agent provides comprehensive content critique across multiple dimensions:
- Clarity, brand alignment, audience fit, engagement
- Factual accuracy, SEO optimization, readability
- Grammar, value proposition, linguistic excellence

Features:
- Multi-model evaluation (Gemini + Claude for diverse perspectives)
- Detailed scoring and actionable feedback
- Memory integration for learning from past critiques
- Integrated language excellence engine with grammar, style, and diversity analysis
- Readability metrics (Flesch-Kincaid)
"""

import json
import re
import structlog
import textstat
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from uuid import UUID

from backend.services.vertex_ai_client import vertex_ai_client
from backend.services.supabase_client import supabase_client
from backend.utils.correlation import get_correlation_id
from backend.language import optimize_language, BrandStyleGuide

logger = structlog.get_logger(__name__)


class CriticAgent:
    """
    Advanced content critic with multi-dimensional evaluation.

    Provides detailed critique across:
    - Content quality dimensions (clarity, grammar, value, etc.)
    - Brand and audience alignment
    - SEO optimization
    - Readability metrics
    - Engagement potential
    - Language excellence analysis

    Integrates memory to learn from past critiques and improve over time.
    """

    def __init__(self, enable_language_engine: bool = True):
        self.llm = vertex_ai_client
        self.db = supabase_client
        self.enable_language_engine = enable_language_engine

        # Expanded multi-dimensional rubric
        self.quality_rubric = {
            "clarity": {
                "description": "Is the message clear, concise, and easy to understand?",
                "weight": 1.2,
                "checks": ["logical flow", "jargon usage", "sentence complexity"]
            },
            "brand_alignment": {
                "description": "Does it align with brand voice, values, and positioning?",
                "weight": 1.5,
                "checks": ["tone consistency", "messaging alignment", "visual style"]
            },
            "audience_fit": {
                "description": "Is it tailored to the target audience's needs and preferences?",
                "weight": 1.3,
                "checks": ["relevance", "pain point addressing", "language appropriateness"]
            },
            "engagement": {
                "description": "Will this capture and maintain audience attention?",
                "weight": 1.2,
                "checks": ["hook strength", "storytelling", "emotional resonance"]
            },
            "factual_accuracy": {
                "description": "Are all facts, claims, and statistics accurate and verifiable?",
                "weight": 1.4,
                "checks": ["claim verification", "source credibility", "statistical validity"]
            },
            "seo_optimization": {
                "description": "Is the content optimized for search engines and discoverability?",
                "weight": 1.0,
                "checks": ["keyword usage", "meta data", "header structure", "internal links"]
            },
            "readability": {
                "description": "Is the content easy to read and digest?",
                "weight": 1.1,
                "checks": ["sentence length", "paragraph structure", "formatting"]
            },
            "grammar": {
                "description": "Is it free of spelling, grammar, and punctuation errors?",
                "weight": 1.0,
                "checks": ["spelling", "grammar", "punctuation", "consistency"]
            },
            "value": {
                "description": "Does it provide meaningful value to the reader?",
                "weight": 1.3,
                "checks": ["actionability", "insights", "practical application"]
            },
            "linguistic_quality": {
                "description": "Does it demonstrate linguistic excellence?",
                "weight": 1.0,
                "checks": ["vocabulary diversity", "style sophistication", "rhetorical devices"]
            }
        }

        # Memory for learning from language analysis
        self.language_analysis_history = []

    async def critique_content(
        self,
        content: str,
        content_type: str,
        target_icp: Optional[Dict] = None,
        brand_voice: Optional[Dict] = None,
        workspace_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive content critique with multi-dimensional analysis.

        This is the main API for content evaluation. It:
        1. Calculates readability metrics
        2. Uses multiple LLM models for diverse perspectives
        3. Recalls similar past critiques for consistency
        4. Stores critique results for future learning
        5. Provides detailed, actionable feedback

        Args:
            content: The text content to critique
            content_type: Type of content (blog, email, social_post, landing_page, etc.)
            target_icp: Target audience/ICP profile for relevance checking
            brand_voice: Brand voice guidelines and requirements
            workspace_id: Workspace ID for memory storage
            correlation_id: Request correlation ID for tracking

        Returns:
            Detailed critique structure:
            {
                "overall_score": float (0-100),
                "dimensions": {
                    "clarity": {
                        "score": float (0-10),
                        "issues": List[str],
                        "suggestions": List[str]
                    },
                    ... (all 9 dimensions)
                    "readability": {
                        "score": float (0-10),
                        "flesch_reading_ease": float,
                        "grade_level": str
                    }
                },
                "approval_recommendation": str,  # "approve", "approve_with_revisions", "reject"
                "priority_fixes": List[str],
                "optional_improvements": List[str],
                "critique_metadata": {
                    "content_type": str,
                    "models_used": List[str],
                    "similar_critiques": int,
                    "timestamp": str
                }
            }

        Example:
            critique = await critic_agent.critique_content(
                content="Your blog post here...",
                content_type="blog",
                target_icp={"industry": "SaaS", "role": "Marketing Manager"},
                brand_voice={"tone": "professional", "style": "conversational"}
            )

            if critique["approval_recommendation"] == "approve":
                publish_content()
            elif critique["approval_recommendation"] == "approve_with_revisions":
                apply_fixes(critique["priority_fixes"])
            else:
                rewrite_content()
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info(
            "Starting comprehensive content critique",
            content_type=content_type,
            content_length=len(content),
            correlation_id=correlation_id
        )

        try:
            # Step 1: Calculate readability metrics
            readability_metrics = self._calculate_readability(content)

            # Step 2: Retrieve similar past critiques for context
            past_critiques = await self._recall_similar_critiques(
                content_type,
                workspace_id,
                limit=3
            )

            # Step 3: Multi-model critique for diverse perspectives
            gemini_critique = await self._critique_with_model(
                content=content,
                content_type=content_type,
                target_icp=target_icp,
                brand_voice=brand_voice,
                past_critiques=past_critiques,
                model_type="reasoning",
                correlation_id=correlation_id
            )

            claude_critique = await self._critique_with_model(
                content=content,
                content_type=content_type,
                target_icp=target_icp,
                brand_voice=brand_voice,
                past_critiques=past_critiques,
                model_type="creative",
                correlation_id=correlation_id
            )

            # Step 4: Synthesize critiques from multiple models
            final_critique = self._synthesize_critiques(
                gemini_critique,
                claude_critique,
                readability_metrics
            )

            # Step 5: Add metadata
            final_critique["critique_metadata"] = {
                "content_type": content_type,
                "models_used": ["gemini-reasoning", "claude-creative"],
                "similar_critiques": len(past_critiques),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "correlation_id": correlation_id
            }

            # Step 6: Store critique for future learning
            if workspace_id:
                await self._store_critique(
                    content=content,
                    content_type=content_type,
                    critique=final_critique,
                    workspace_id=workspace_id
                )

            logger.info(
                "Content critique completed",
                overall_score=final_critique["overall_score"],
                recommendation=final_critique["approval_recommendation"],
                correlation_id=correlation_id
            )

            return final_critique

        except Exception as e:
            logger.error(
                f"Failed to critique content: {e}",
                error_type=type(e).__name__,
                correlation_id=correlation_id
            )
            return self._get_fallback_critique(str(e))

    async def _critique_with_model(
        self,
        content: str,
        content_type: str,
        target_icp: Optional[Dict],
        brand_voice: Optional[Dict],
        past_critiques: List[Dict],
        model_type: str,
        correlation_id: str
    ) -> Dict[str, Any]:
        """Use a specific model to critique content."""

        # Build context from past critiques
        past_context = ""
        if past_critiques:
            past_context = "\n**Past Similar Critiques for Consistency**:\n"
            for i, pc in enumerate(past_critiques[:2], 1):
                past_context += f"{i}. Previous {pc.get('content_type', 'content')} scored {pc.get('overall_score', 'N/A')}/100\n"
                past_context += f"   Common issues: {', '.join(pc.get('common_issues', []))}\n"

        # Build rubric description
        rubric_text = "\n".join([
            f"- **{k.replace('_', ' ').title()}** (weight: {v['weight']}): {v['description']}"
            for k, v in self.quality_rubric.items()
        ])

        icp_context = f"\n**Target ICP**: {json.dumps(target_icp, indent=2)}" if target_icp else ""
        brand_context = f"\n**Brand Voice**: {json.dumps(brand_voice, indent=2)}" if brand_voice else ""

        prompt = f"""You are a senior content strategist conducting a comprehensive quality review.

**Content to Critique**:
{content}

**Content Type**: {content_type}
{icp_context}
{brand_context}
{past_context}

**Evaluation Rubric** (10 dimensions):
{rubric_text}

**Your Task**:
For EACH dimension, provide:
1. A score from 0-10
2. Specific issues found (be concrete and cite examples)
3. Actionable suggestions for improvement

Then provide:
- Overall quality score (weighted average, 0-100)
- Approval recommendation: "approve", "approve_with_revisions", or "reject"
- Priority fixes (must-do items)
- Optional improvements (nice-to-have enhancements)

Be thorough, specific, and constructive. Cite examples from the content.

Output as JSON following this exact structure:
{{
  "dimensions": {{
    "clarity": {{"score": 8.5, "issues": ["issue 1", "issue 2"], "suggestions": ["suggestion 1", "suggestion 2"]}},
    "brand_alignment": {{"score": 7.0, "issues": [], "suggestions": []}},
    "audience_fit": {{"score": 9.0, "issues": [], "suggestions": []}},
    "engagement": {{"score": 8.0, "issues": [], "suggestions": []}},
    "factual_accuracy": {{"score": 9.5, "issues": [], "suggestions": []}},
    "seo_optimization": {{"score": 6.0, "issues": [], "suggestions": []}},
    "readability": {{"score": 8.5, "issues": [], "suggestions": []}},
    "grammar": {{"score": 9.0, "issues": [], "suggestions": []}},
    "value": {{"score": 8.0, "issues": [], "suggestions": []}},
    "linguistic_quality": {{"score": 8.0, "issues": [], "suggestions": []}}
  }},
  "priority_fixes": ["fix 1", "fix 2"],
  "optional_improvements": ["improvement 1", "improvement 2"]
}}
"""

        messages = [
            {
                "role": "system",
                "content": "You are a world-class content strategist and editor with expertise in marketing, SEO, and audience engagement. Provide detailed, actionable critiques."
            },
            {"role": "user", "content": prompt}
        ]

        try:
            llm_response = await self.llm.chat_completion(
                messages,
                model_type=model_type,
                temperature=0.2,  # Low temperature for consistent evaluation
                response_format={"type": "json_object"}
            )

            critique = json.loads(llm_response)
            return critique

        except Exception as e:
            logger.error(
                f"Model critique failed ({model_type}): {e}",
                correlation_id=correlation_id
            )
            return {"dimensions": {}, "priority_fixes": [], "optional_improvements": []}

    def _synthesize_critiques(
        self,
        gemini_critique: Dict,
        claude_critique: Dict,
        readability_metrics: Dict
    ) -> Dict[str, Any]:
        """Combine insights from multiple model critiques."""

        dimensions = {}
        all_priority_fixes = []
        all_optional_improvements = []

        # Average scores across models for each dimension
        for dim_name in self.quality_rubric.keys():
            gemini_dim = gemini_critique.get("dimensions", {}).get(dim_name, {})
            claude_dim = claude_critique.get("dimensions", {}).get(dim_name, {})

            # Average scores
            gemini_score = gemini_dim.get("score", 5.0)
            claude_score = claude_dim.get("score", 5.0)
            avg_score = (gemini_score + claude_score) / 2

            # Combine issues and suggestions (deduplicate)
            all_issues = list(set(
                gemini_dim.get("issues", []) +
                claude_dim.get("issues", [])
            ))
            all_suggestions = list(set(
                gemini_dim.get("suggestions", []) +
                claude_dim.get("suggestions", [])
            ))

            dimensions[dim_name] = {
                "score": round(avg_score, 2),
                "issues": all_issues[:5],  # Top 5 issues
                "suggestions": all_suggestions[:5]  # Top 5 suggestions
            }

        # Override readability dimension with actual metrics
        dimensions["readability"] = {
            "score": readability_metrics["score"],
            "issues": readability_metrics.get("issues", []),
            "suggestions": readability_metrics.get("suggestions", []),
            "flesch_reading_ease": readability_metrics["flesch_reading_ease"],
            "grade_level": readability_metrics["grade_level"]
        }

        # Combine priority fixes and improvements
        all_priority_fixes = list(set(
            gemini_critique.get("priority_fixes", []) +
            claude_critique.get("priority_fixes", [])
        ))[:5]

        all_optional_improvements = list(set(
            gemini_critique.get("optional_improvements", []) +
            claude_critique.get("optional_improvements", [])
        ))[:5]

        # Calculate weighted overall score
        weighted_sum = 0
        total_weight = 0
        for dim_name, dim_data in dimensions.items():
            weight = self.quality_rubric[dim_name]["weight"]
            weighted_sum += dim_data["score"] * weight
            total_weight += weight

        overall_score = round((weighted_sum / total_weight) * 10, 2)  # Convert to 0-100 scale

        # Determine approval recommendation
        if overall_score >= 85:
            approval = "approve"
        elif overall_score >= 70:
            approval = "approve_with_revisions"
        else:
            approval = "reject"

        # If there are critical issues, downgrade approval
        critical_dimensions = ["factual_accuracy", "brand_alignment", "grammar"]
        for dim in critical_dimensions:
            if dimensions[dim]["score"] < 6.0:
                approval = "reject" if approval != "reject" else approval

        return {
            "overall_score": overall_score,
            "dimensions": dimensions,
            "approval_recommendation": approval,
            "priority_fixes": all_priority_fixes,
            "optional_improvements": all_optional_improvements
        }

    def _calculate_readability(self, content: str) -> Dict[str, Any]:
        """Calculate readability metrics using Flesch-Kincaid."""

        try:
            # Flesch Reading Ease (higher is easier, 0-100)
            flesch_ease = textstat.flesch_reading_ease(content)

            # Flesch-Kincaid Grade Level
            fk_grade = textstat.flesch_kincaid_grade(content)

            # Determine grade level label
            if fk_grade <= 6:
                grade_label = "Elementary (6th grade or below)"
            elif fk_grade <= 8:
                grade_label = "Middle School (7-8th grade)"
            elif fk_grade <= 12:
                grade_label = "High School (9-12th grade)"
            elif fk_grade <= 16:
                grade_label = "College (13-16th grade)"
            else:
                grade_label = "Graduate+ (17+ grade level)"

            # Score based on Flesch Reading Ease
            # 90-100: Very Easy (score 10)
            # 80-89: Easy (score 9)
            # 70-79: Fairly Easy (score 8)
            # 60-69: Standard (score 7)
            # 50-59: Fairly Difficult (score 6)
            # 30-49: Difficult (score 5)
            # 0-29: Very Difficult (score 3)
            if flesch_ease >= 90:
                score = 10.0
            elif flesch_ease >= 80:
                score = 9.0
            elif flesch_ease >= 70:
                score = 8.0
            elif flesch_ease >= 60:
                score = 7.0
            elif flesch_ease >= 50:
                score = 6.0
            elif flesch_ease >= 30:
                score = 5.0
            else:
                score = 3.0

            issues = []
            suggestions = []

            if flesch_ease < 60:
                issues.append(f"Readability is below standard (Flesch: {flesch_ease:.1f})")
                suggestions.append("Use shorter sentences and simpler words")

            if fk_grade > 12:
                issues.append(f"Grade level is high ({grade_label})")
                suggestions.append("Simplify complex sentences and reduce jargon")

            return {
                "score": score,
                "flesch_reading_ease": round(flesch_ease, 2),
                "flesch_kincaid_grade": round(fk_grade, 1),
                "grade_level": grade_label,
                "issues": issues,
                "suggestions": suggestions
            }

        except Exception as e:
            logger.warning(f"Readability calculation failed: {e}")
            return {
                "score": 7.0,
                "flesch_reading_ease": 60.0,
                "grade_level": "Unknown",
                "issues": ["Could not calculate readability"],
                "suggestions": []
            }

    async def _recall_similar_critiques(
        self,
        content_type: str,
        workspace_id: Optional[str],
        limit: int = 3
    ) -> List[Dict]:
        """Retrieve past critiques for similar content to improve consistency."""

        if not workspace_id:
            return []

        try:
            # Query past critiques from database
            critiques = await self.db.fetch_all(
                "content_critiques",
                filters={
                    "workspace_id": workspace_id,
                    "content_type": content_type
                }
            )

            # Sort by timestamp and return most recent
            critiques = sorted(
                critiques,
                key=lambda x: x.get("created_at", ""),
                reverse=True
            )[:limit]

            return [
                {
                    "content_type": c.get("content_type"),
                    "overall_score": c.get("overall_score"),
                    "common_issues": c.get("common_issues", [])
                }
                for c in critiques
            ]

        except Exception as e:
            logger.warning(f"Failed to recall past critiques: {e}")
            return []

    async def _store_critique(
        self,
        content: str,
        content_type: str,
        critique: Dict,
        workspace_id: str
    ) -> None:
        """Store critique results for future learning."""

        try:
            # Extract common issues for quick retrieval
            common_issues = []
            for dim_data in critique.get("dimensions", {}).values():
                common_issues.extend(dim_data.get("issues", []))

            critique_record = {
                "workspace_id": workspace_id,
                "content_type": content_type,
                "content_hash": str(hash(content[:500])),  # Hash first 500 chars
                "overall_score": critique["overall_score"],
                "approval_recommendation": critique["approval_recommendation"],
                "common_issues": common_issues[:10],
                "dimension_scores": {
                    dim: data["score"]
                    for dim, data in critique.get("dimensions", {}).items()
                },
                "created_at": datetime.now(timezone.utc).isoformat()
            }

            await self.db.insert("content_critiques", critique_record)
            logger.debug(f"Stored critique for {content_type} in workspace {workspace_id}")

        except Exception as e:
            logger.warning(f"Failed to store critique: {e}")

    def _get_fallback_critique(self, error: str) -> Dict[str, Any]:
        """Return a safe fallback critique when evaluation fails."""

        return {
            "overall_score": 0,
            "dimensions": {
                dim: {"score": 0, "issues": ["Critique failed"], "suggestions": []}
                for dim in self.quality_rubric.keys()
            },
            "approval_recommendation": "reject",
            "priority_fixes": [f"System error: {error}"],
            "optional_improvements": [],
            "critique_metadata": {
                "error": error,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }

    async def review_content(
        self,
        content: str,
        content_type: str,
        target_icp: Optional[Dict] = None,
        brand_voice: Optional[Dict] = None,
        style_guide: Optional[BrandStyleGuide] = None,
        target_grade_level: Optional[int] = None,
        correlation_id: str = None
    ) -> Dict[str, Any]:
        """
        Legacy method for backward compatibility with enhanced language analysis.

        This method maintains compatibility with existing code that uses the old
        review_content() API. New code should use critique_content() instead.

        Enhanced with comprehensive language excellence analysis.
        """

        correlation_id = correlation_id or get_correlation_id()
        logger.info("Using enhanced legacy review_content method", correlation_id=correlation_id)

        # Run language excellence engine if enabled
        language_analysis = None
        if self.enable_language_engine:
            try:
                logger.info("Running language excellence engine", correlation_id=correlation_id)
                language_analysis = await optimize_language(
                    content=content,
                    style_guide=style_guide,
                    target_grade_level=target_grade_level,
                    correlation_id=correlation_id
                )

                # Store in memory for learning
                self.language_analysis_history.append({
                    "content_type": content_type,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "overall_score": language_analysis.get("overall_score"),
                    "correlation_id": correlation_id
                })

                # Keep only last 100 analyses
                if len(self.language_analysis_history) > 100:
                    self.language_analysis_history = self.language_analysis_history[-100:]

                logger.info(
                    "Language analysis completed",
                    overall_score=language_analysis.get("overall_score"),
                    correlation_id=correlation_id
                )
            except Exception as e:
                logger.error(f"Language engine failed: {e}", correlation_id=correlation_id)
                language_analysis = {"error": str(e)}

        # Call new critique method and enhance with language results
        critique = await self.critique_content(
            content=content,
            content_type=content_type,
            target_icp=target_icp,
            brand_voice=brand_voice,
            correlation_id=correlation_id
        )

        # Convert to legacy format with language enhancements
        scores = {dim: data["score"] for dim, data in critique["dimensions"].items()}
        feedback = {dim: "; ".join(data["issues"]) for dim, data in critique["dimensions"].items()}

        # Add language-specific scores if available
        if language_analysis and "error" not in language_analysis:
            scores["grammar_quality"] = max(0, 10 - (language_analysis.get('results', {}).get('grammar', {}).get('critical_count', 0) * 2))
            scores["readability"] = min(10, language_analysis.get('results', {}).get('readability', {}).get('metrics', {}).get('flesch_reading_ease', 50) / 10)
            scores["linguistic_diversity"] = language_analysis.get('results', {}).get('diversity', {}).get('diversity_score', 50) / 10
            critique["language_analysis"] = language_analysis

        # Map new recommendation to legacy format
        recommendation_map = {
            "approve": "approve",
            "approve_with_revisions": "revise_minor",
            "reject": "revise_major"
        }

        return {
            "scores": scores,
            "feedback": feedback,
            "overall_score": critique["overall_score"],
            "recommendation": recommendation_map[critique["approval_recommendation"]],
            "revision_suggestions": critique["priority_fixes"],
            "strengths": critique.get("optional_improvements", []),
            "improvements": critique["priority_fixes"],
            "content_type": content_type,
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
            "rationale": f"Overall score: {critique['overall_score']}/100"
        }

    async def iterative_improve(
        self,
        initial_content: str,
        content_type: str,
        max_iterations: int = 3,
        target_score: int = 85,
        target_icp: Optional[Dict] = None,
        brand_voice: Optional[Dict] = None,
        correlation_id: str = None
    ) -> Dict[str, Any]:
        """
        Implements generate-review loop for iterative improvement.

        Returns:
            Final content and review history
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Starting iterative improvement", max_iterations=max_iterations, target_score=target_score, correlation_id=correlation_id)

        current_content = initial_content
        iteration_history = []

        for iteration in range(max_iterations):
            # Review current version
            review = await self.review_content(
                current_content,
                content_type,
                target_icp,
                brand_voice,
                correlation_id
            )

            iteration_history.append({
                "iteration": iteration + 1,
                "content": current_content,
                "review": review
            })

            # Check if we've hit target
            if review.get("overall_score", 0) >= target_score or review.get("recommendation") == "approve":
                logger.info(f"Target reached at iteration {iteration + 1}", score=review.get("overall_score"), correlation_id=correlation_id)
                break

            # Generate improved version
            if iteration < max_iterations - 1:
                current_content = await self._revise_content(
                    current_content,
                    review,
                    content_type,
                    correlation_id
                )

        return {
            "final_content": current_content,
            "final_score": review.get("overall_score"),
            "iterations": len(iteration_history),
            "history": iteration_history
        }

    async def _revise_content(
        self,
        content: str,
        review: Dict,
        content_type: str,
        correlation_id: str
    ) -> str:
        """Generates improved version based on feedback."""

        feedback_text = "\n".join([f"- {k}: {v}" for k, v in review.get("feedback", {}).items()])
        suggestions_text = "\n".join([f"- {s}" for s in review.get("revision_suggestions", [])])

        prompt = f"""Revise this {content_type} based on the feedback provided.

**Original Content**:
{content}

**Feedback**:
{feedback_text}

**Specific Revision Suggestions**:
{suggestions_text}

**Task**: Rewrite the content addressing ALL feedback points. Maintain the core message but improve clarity, engagement, and quality. Output ONLY the revised content.
"""

        messages = [
            {"role": "system", "content": "You are a skilled copywriter revising content based on editorial feedback."},
            {"role": "user", "content": prompt}
        ]

        try:
            # Use creative model for rewriting
            revised_content = await self.llm.chat_completion(
                messages,
                model_type="creative",
                temperature=0.7
            )

            return revised_content.strip()

        except Exception as e:
            logger.error(f"Failed to revise content: {e}", correlation_id=correlation_id)
            return content  # Return original if revision fails


# Global singleton instance
critic_agent = CriticAgent()


