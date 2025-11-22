"""
Critic Agent - Reviews generated content against quality rubrics.
Implements generate-review loop for iterative improvement.
Enhanced with comprehensive language excellence engine.
"""

import json
import structlog
from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime

from backend.services.vertex_ai_client import vertex_ai_client
from backend.utils.correlation import get_correlation_id
from backend.language import optimize_language, BrandStyleGuide

logger = structlog.get_logger(__name__)


class CriticAgent:
    """
    Reviews content quality using structured rubrics.
    Provides feedback and revision suggestions.
    """
    
    def __init__(self, enable_language_engine: bool = True):
        self.llm = vertex_ai_client
        self.enable_language_engine = enable_language_engine
        self.quality_rubric = {
            "clarity": "Is the message clear and easy to understand?",
            "accuracy": "Are facts and claims accurate and verifiable?",
            "tone": "Is the tone appropriate for the target audience?",
            "engagement": "Will this capture and hold attention?",
            "cta": "Is there a clear call-to-action (if needed)?",
            "brand_alignment": "Does it align with brand voice and values?",
            "grammar": "Is it free of spelling and grammar errors?",
            "value": "Does it provide value to the reader?",
            "readability": "Is the content readable for the target audience?",
            "linguistic_quality": "Does it demonstrate linguistic excellence?"
        }
        # Memory for learning from language analysis
        self.language_analysis_history = []
    
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
        Reviews content and provides structured feedback.
        Enhanced with comprehensive language analysis.

        Args:
            content: The text to review
            content_type: blog, email, social_post, etc.
            target_icp: ICP profile for relevance check
            brand_voice: Brand voice guidelines
            style_guide: Optional brand style guide for enforcement
            target_grade_level: Optional target reading level

        Returns:
            Review dict with scores and feedback (enhanced with language analysis)
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Reviewing content", content_type=content_type, correlation_id=correlation_id)

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
                    "timestamp": datetime.utcnow().isoformat(),
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
        
        # Build review prompt
        rubric_text = "\n".join([f"- **{k.title()}**: {v}" for k, v in self.quality_rubric.items()])

        icp_context = f"\n**Target ICP**: {json.dumps(target_icp, indent=2)}" if target_icp else ""
        brand_context = f"\n**Brand Voice**: {json.dumps(brand_voice, indent=2)}" if brand_voice else ""

        # Add language analysis context if available
        language_context = ""
        if language_analysis and "error" not in language_analysis:
            summary = language_analysis.get("executive_summary", {})
            language_context = f"""
**Language Excellence Analysis**:
- Overall Language Quality Score: {language_analysis.get('overall_score', 'N/A')}/100
- Key Strengths: {', '.join(summary.get('key_strengths', ['None']))}
- Key Issues: {', '.join(summary.get('key_issues', ['None']))}
- Grammar Issues: {language_analysis.get('results', {}).get('grammar', {}).get('total_issues', 0)}
- Style Violations: {language_analysis.get('results', {}).get('style', {}).get('total_violations', 0)}
- Readability Grade Level: {language_analysis.get('results', {}).get('readability', {}).get('average_grade_level', 'N/A')}
- Diversity Score: {language_analysis.get('results', {}).get('diversity', {}).get('diversity_score', 'N/A')}/100
"""
        
        prompt = f"""Review this {content_type} content against the quality rubric.

**Content to Review**:
{content}

{icp_context}
{brand_context}
{language_context}

**Quality Rubric**:
{rubric_text}

**Review Task**:
1. Score each rubric dimension from 1-10
2. Provide specific feedback for each dimension
3. Identify top 3 strengths
4. Identify top 3 areas for improvement
5. Suggest specific revisions
6. Give an overall quality score (1-100)
7. Recommend: "approve", "revise_minor", or "revise_major"

Output as JSON:
{{
  "scores": {{"clarity": 8, "accuracy": 9, ...}},
  "feedback": {{"clarity": "Specific feedback", ...}},
  "strengths": ["strength 1", ...],
  "improvements": ["improvement 1", ...],
  "revision_suggestions": ["suggestion 1", ...],
  "overall_score": 85,
  "recommendation": "approve|revise_minor|revise_major",
  "rationale": "Why this recommendation"
}}
"""
        
        messages = [
            {"role": "system", "content": "You are a senior content editor reviewing marketing materials. Be thorough, constructive, and specific."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            # Use reasoning model for thorough critique
            llm_response = await self.llm.chat_completion(
                messages,
                model_type="reasoning",
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            review = json.loads(llm_response)
            review["content_type"] = content_type
            review["reviewed_at"] = datetime.utcnow().isoformat()

            # Attach language analysis results
            if language_analysis and "error" not in language_analysis:
                review["language_analysis"] = language_analysis

                # Enhance scores with language metrics
                if "scores" in review:
                    # Add language-specific scores
                    review["scores"]["grammar_quality"] = max(0, 10 - (language_analysis.get('results', {}).get('grammar', {}).get('critical_count', 0) * 2))
                    review["scores"]["readability"] = min(10, language_analysis.get('results', {}).get('readability', {}).get('metrics', {}).get('flesch_reading_ease', 50) / 10)
                    review["scores"]["linguistic_diversity"] = language_analysis.get('results', {}).get('diversity', {}).get('diversity_score', 50) / 10

            logger.info("Content reviewed", overall_score=review.get("overall_score"), recommendation=review.get("recommendation"), correlation_id=correlation_id)
            return review
            
        except Exception as e:
            logger.error(f"Failed to review content: {e}", correlation_id=correlation_id)
            return {
                "error": str(e),
                "overall_score": 0,
                "recommendation": "revise_major",
                "rationale": "Review failed due to system error"
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


critic_agent = CriticAgent()



