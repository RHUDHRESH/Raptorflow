"""
FeedbackTool for Raptorflow agent system.
Handles feedback collection, analysis, and improvement recommendations.
"""

import json
import logging
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from ..base import BaseTool
from ..exceptions import ToolError, ValidationError

logger = logging.getLogger(__name__)


@dataclass
class FeedbackRequest:
    """Feedback collection request."""

    feedback_type: str  # content, campaign, agent, system, user_experience
    source: str  # user, agent, system, survey, review
    content: str
    rating: Optional[int]  # 1-5 scale
    sentiment: Optional[str]  # positive, negative, neutral
    categories: List[str]
    metadata: Dict[str, Any]
    workspace_id: str
    user_id: Optional[str] = None
    timestamp: Optional[datetime] = None


@dataclass
class FeedbackAnalysis:
    """Feedback analysis result."""

    feedback_id: str
    sentiment_score: float  # -1 to 1
    sentiment_label: str
    key_themes: List[str]
    urgency_level: str  # low, medium, high, critical
    action_items: List[str]
    confidence_score: float
    metadata: Dict[str, Any]


@dataclass
class FeedbackSummary:
    """Feedback summary report."""

    summary_type: str  # daily, weekly, monthly, custom
    period_start: datetime
    period_end: datetime
    total_feedback: int
    average_rating: float
    sentiment_distribution: Dict[str, int]
    top_themes: List[Dict[str, Any]]
    improvement_areas: List[str]
    recommendations: List[str]
    metadata: Dict[str, Any]


class FeedbackTool(BaseTool):
    """Advanced feedback collection and analysis tool."""

    def __init__(self):
        super().__init__(
            name="feedback_tool",
            description="Feedback collection, analysis, and improvement recommendations",
            version="1.0.0",
        )

        # Feedback categories
        self.feedback_categories = {
            "content": {
                "subcategories": ["quality", "relevance", "format", "length", "tone"],
                "keywords": ["content", "article", "post", "blog", "copy", "text"],
            },
            "campaign": {
                "subcategories": [
                    "performance",
                    "targeting",
                    "messaging",
                    "timing",
                    "budget",
                ],
                "keywords": ["campaign", "ad", "promotion", "marketing", "conversion"],
            },
            "agent": {
                "subcategories": [
                    "accuracy",
                    "helpfulness",
                    "speed",
                    "understanding",
                    "reliability",
                ],
                "keywords": ["agent", "ai", "assistant", "bot", "response", "answer"],
            },
            "system": {
                "subcategories": [
                    "performance",
                    "usability",
                    "features",
                    "bugs",
                    "stability",
                ],
                "keywords": ["system", "platform", "interface", "ui", "feature", "bug"],
            },
            "user_experience": {
                "subcategories": [
                    "navigation",
                    "design",
                    "accessibility",
                    "onboarding",
                    "support",
                ],
                "keywords": ["experience", "ux", "design", "navigation", "usability"],
            },
        }

        # Sentiment analysis patterns
        self.sentiment_patterns = {
            "positive": [
                r"\b(good|great|excellent|amazing|awesome|fantastic|wonderful|perfect|love|like|helpful|useful|effective)\b",
                r"\b(improved|better|success|achieved|accomplished|solved|resolved)\b",
                r"\b(thanks|thank you|appreciate|grateful|satisfied|happy|pleased)\b",
            ],
            "negative": [
                r"\b(bad|poor|terrible|awful|hate|dislike|useless|helpless|ineffective|failed|broken)\b",
                r"\b(worse|worst|problem|issue|error|bug|glitch|crash|slow|difficult)\b",
                r"\b(frustrated|annoyed|disappointed|unsatisfied|unhappy|confused|lost)\b",
            ],
            "neutral": [
                r"\b(okay|ok|fine|average|normal|standard|typical|regular|moderate)\b",
                r"\b(neither|either|balanced|mixed|neutral|objective)\b",
            ],
        }

        # Urgency indicators
        self.urgency_indicators = {
            "critical": [
                r"\b(urgent|critical|emergency|immediate|asap|crash|broken|down|failure)\b",
                r"\b(cannot|unable|impossible|stuck|blocked|prevented|stopped)\b",
            ],
            "high": [
                r"\b(important|priority|serious|significant|major|concerning)\b",
                r"\b(need|require|must|should|expect|waiting|delayed)\b",
            ],
            "medium": [
                r"\b(would|could|might|suggest|recommend|prefer|consider)\b",
                r"\b(improvement|enhancement|optimization|refinement)\b",
            ],
            "low": [
                r"\b(nice|good|helpful|useful|convenient|optional)\b",
                r"\b(minor|small|tiny|slight|cosmetic)\b",
            ],
        }

        # Action item patterns
        self.action_patterns = [
            r"\b(fix|resolve|address|correct|repair|solve)\b",
            r"\b(improve|enhance|optimize|upgrade|update)\b",
            r"\b(add|implement|create|develop|build)\b",
            r"\b(remove|delete|disable|deprecate)\b",
            r"\b(investigate|research|analyze|review)\b",
        ]

        # Theme extraction patterns
        self.theme_patterns = {
            "performance": [r"\b(slow|fast|performance|speed|responsive|lag|delay)\b"],
            "usability": [r"\b(easy|difficult|confusing|intuitive|user|interface)\b"],
            "features": [r"\b(feature|functionality|capability|option|setting)\b"],
            "quality": [r"\b(quality|accuracy|precision|reliability|consistency)\b"],
            "support": [r"\b(support|help|assistance|guidance|documentation)\b"],
            "design": [r"\b(design|layout|appearance|visual|aesthetic)\b"],
            "content": [r"\b(content|text|copy|message|communication)\b"],
            "integration": [r"\b(integration|connection|api|sync|link)\b"],
        }

        # Improvement recommendations
        self.improvement_recommendations = {
            "performance": [
                "Optimize database queries and caching",
                "Implement lazy loading for large datasets",
                "Add performance monitoring and alerts",
                "Review and optimize critical code paths",
            ],
            "usability": [
                "Conduct user experience testing",
                "Simplify complex workflows",
                "Add onboarding tutorials and tooltips",
                "Improve navigation and information architecture",
            ],
            "features": [
                "Prioritize feature requests based on user feedback",
                "Implement most requested functionality",
                "Add configuration options for flexibility",
                "Create feature documentation and guides",
            ],
            "quality": [
                "Implement comprehensive testing suite",
                "Add automated quality checks",
                "Improve error handling and logging",
                "Establish code review processes",
            ],
            "support": [
                "Create comprehensive knowledge base",
                "Implement chatbot for common issues",
                "Add in-app help and tutorials",
                "Improve customer support response times",
            ],
            "design": [
                "Conduct design system audit",
                "Implement consistent design patterns",
                "Improve accessibility compliance",
                "Add responsive design optimizations",
            ],
        }

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute feedback operation."""
        try:
            operation = kwargs.get("operation", "collect")

            if operation == "collect":
                return await self._collect_feedback(**kwargs)
            elif operation == "analyze":
                return await self._analyze_feedback(**kwargs)
            elif operation == "summarize":
                return await self._generate_summary(**kwargs)
            elif operation == "trends":
                return await self._analyze_trends(**kwargs)
            elif operation == "recommendations":
                return await self._generate_recommendations(**kwargs)
            else:
                raise ValidationError(f"Unsupported operation: {operation}")

        except Exception as e:
            logger.error(f"Feedback operation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": kwargs.get("operation", "unknown"),
                "timestamp": datetime.now().isoformat(),
            }

    async def _collect_feedback(self, **kwargs) -> Dict[str, Any]:
        """Collect feedback from various sources."""
        try:
            # Parse feedback request
            request = self._parse_feedback_request(kwargs)

            # Validate request
            self._validate_feedback_request(request)

            # Store feedback
            feedback_id = await self._store_feedback(request)

            # Analyze feedback
            analysis = await self._analyze_feedback_content(request)

            # Update feedback with analysis
            await self._update_feedback_analysis(feedback_id, analysis)

            return {
                "success": True,
                "feedback_id": feedback_id,
                "analysis": analysis.__dict__,
                "collected_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Feedback collection failed: {e}")
            raise ToolError(f"Feedback collection failed: {str(e)}")

    async def _analyze_feedback(self, **kwargs) -> Dict[str, Any]:
        """Analyze existing feedback."""
        try:
            feedback_id = kwargs.get("feedback_id", "")
            workspace_id = kwargs.get("workspace_id", "")

            if not feedback_id:
                raise ValidationError("Feedback ID is required")

            # Get feedback
            feedback = await self._get_feedback(feedback_id, workspace_id)

            # Analyze content
            analysis = await self._analyze_feedback_content(feedback)

            return {
                "success": True,
                "feedback_id": feedback_id,
                "analysis": analysis.__dict__,
                "analyzed_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Feedback analysis failed: {e}")
            raise ToolError(f"Feedback analysis failed: {str(e)}")

    async def _generate_summary(self, **kwargs) -> Dict[str, Any]:
        """Generate feedback summary report."""
        try:
            workspace_id = kwargs.get("workspace_id", "")
            summary_type = kwargs.get("summary_type", "weekly")
            period_start = kwargs.get("period_start")
            period_end = kwargs.get("period_end")

            # Determine period
            if not period_start or not period_end:
                period_start, period_end = self._calculate_period(summary_type)

            # Get feedback data
            feedback_data = await self._get_feedback_data(
                workspace_id, period_start, period_end
            )

            # Generate summary
            summary = self._create_summary(
                feedback_data, summary_type, period_start, period_end
            )

            return {
                "success": True,
                "summary": summary.__dict__,
                "generated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            raise ToolError(f"Summary generation failed: {str(e)}")

    async def _analyze_trends(self, **kwargs) -> Dict[str, Any]:
        """Analyze feedback trends over time."""
        try:
            workspace_id = kwargs.get("workspace_id", "")
            trend_period = kwargs.get("trend_period", "monthly")
            categories = kwargs.get("categories", [])

            # Get historical data
            historical_data = await self._get_historical_feedback(
                workspace_id, trend_period, categories
            )

            # Analyze trends
            trends = self._analyze_trend_patterns(historical_data)

            return {
                "success": True,
                "trends": trends,
                "analyzed_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            raise ToolError(f"Trend analysis failed: {str(e)}")

    async def _generate_recommendations(self, **kwargs) -> Dict[str, Any]:
        """Generate improvement recommendations."""
        try:
            workspace_id = kwargs.get("workspace_id", "")
            focus_areas = kwargs.get("focus_areas", [])

            # Get recent feedback
            recent_feedback = await self._get_recent_feedback(workspace_id, focus_areas)

            # Generate recommendations
            recommendations = self._create_recommendations(recent_feedback, focus_areas)

            return {
                "success": True,
                "recommendations": recommendations,
                "generated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            raise ToolError(f"Recommendation generation failed: {str(e)}")

    def _parse_feedback_request(self, kwargs: Dict[str, Any]) -> FeedbackRequest:
        """Parse feedback request from kwargs."""
        return FeedbackRequest(
            feedback_type=kwargs.get("feedback_type", "user_experience"),
            source=kwargs.get("source", "user"),
            content=kwargs.get("content", ""),
            rating=kwargs.get("rating"),
            sentiment=kwargs.get("sentiment"),
            categories=kwargs.get("categories", []),
            metadata=kwargs.get("metadata", {}),
            workspace_id=kwargs.get("workspace_id", ""),
            user_id=kwargs.get("user_id"),
            timestamp=kwargs.get("timestamp", datetime.now()),
        )

    def _validate_feedback_request(self, request: FeedbackRequest):
        """Validate feedback request."""
        if not request.content:
            raise ValidationError("Feedback content is required")

        if not request.workspace_id:
            raise ValidationError("Workspace ID is required")

        if request.feedback_type not in self.feedback_categories:
            raise ValidationError(f"Invalid feedback type: {request.feedback_type}")

        if request.rating and (request.rating < 1 or request.rating > 5):
            raise ValidationError("Rating must be between 1 and 5")

        if request.sentiment and request.sentiment not in [
            "positive",
            "negative",
            "neutral",
        ]:
            raise ValidationError("Invalid sentiment value")

    async def _store_feedback(self, request: FeedbackRequest) -> str:
        """Store feedback in database."""
        try:
            # Generate feedback ID
            feedback_id = f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(request.content) % 10000}"

            # This would integrate with the database tool
            logger.info(
                f"Storing feedback {feedback_id} in workspace {request.workspace_id}"
            )

            return feedback_id

        except Exception as e:
            logger.error(f"Failed to store feedback: {e}")
            raise ToolError(f"Failed to store feedback: {str(e)}")

    async def _analyze_feedback_content(
        self, request: FeedbackRequest
    ) -> FeedbackAnalysis:
        """Analyze feedback content."""
        content = request.content.lower()

        # Sentiment analysis
        sentiment_score = self._calculate_sentiment_score(content)
        sentiment_label = self._get_sentiment_label(sentiment_score)

        # Extract key themes
        key_themes = self._extract_key_themes(content)

        # Determine urgency
        urgency_level = self._determine_urgency(content)

        # Extract action items
        action_items = self._extract_action_items(content)

        # Calculate confidence
        confidence_score = self._calculate_confidence_score(
            content, sentiment_score, key_themes
        )

        return FeedbackAnalysis(
            feedback_id="",  # Will be set by caller
            sentiment_score=sentiment_score,
            sentiment_label=sentiment_label,
            key_themes=key_themes,
            urgency_level=urgency_level,
            action_items=action_items,
            confidence_score=confidence_score,
            metadata={
                "feedback_type": request.feedback_type,
                "source": request.source,
                "rating": request.rating,
                "categories": request.categories,
                "analyzed_at": datetime.now().isoformat(),
            },
        )

    def _calculate_sentiment_score(self, content: str) -> float:
        """Calculate sentiment score from content."""
        positive_score = 0
        negative_score = 0
        neutral_score = 0

        # Count sentiment indicators
        for pattern in self.sentiment_patterns["positive"]:
            matches = len(re.findall(pattern, content, re.IGNORECASE))
            positive_score += matches

        for pattern in self.sentiment_patterns["negative"]:
            matches = len(re.findall(pattern, content, re.IGNORECASE))
            negative_score += matches

        for pattern in self.sentiment_patterns["neutral"]:
            matches = len(re.findall(pattern, content, re.IGNORECASE))
            neutral_score += matches

        # Calculate normalized score
        total_indicators = positive_score + negative_score + neutral_score
        if total_indicators == 0:
            return 0.0  # Neutral

        # Weight positive and negative more heavily than neutral
        weighted_positive = positive_score * 1.0
        weighted_negative = negative_score * -1.0
        weighted_neutral = neutral_score * 0.1

        score = (weighted_positive + weighted_negative + weighted_neutral) / (
            positive_score + negative_score + neutral_score * 0.1
        )

        return max(-1.0, min(1.0, score))

    def _get_sentiment_label(self, score: float) -> str:
        """Get sentiment label from score."""
        if score > 0.3:
            return "positive"
        elif score < -0.3:
            return "negative"
        else:
            return "neutral"

    def _extract_key_themes(self, content: str) -> List[str]:
        """Extract key themes from content."""
        themes = []

        for theme, patterns in self.theme_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    themes.append(theme)
                    break

        return themes

    def _determine_urgency(self, content: str) -> str:
        """Determine urgency level from content."""
        urgency_scores = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        max_score = 0
        urgency_level = "medium"

        for level, patterns in self.urgency_indicators.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, content, re.IGNORECASE))
                score += matches

            if score > max_score:
                max_score = score
                urgency_level = level

        return urgency_level

    def _extract_action_items(self, content: str) -> List[str]:
        """Extract action items from content."""
        action_items = []

        # Find sentences with action patterns
        sentences = re.split(r"[.!?]+", content)
        for sentence in sentences:
            sentence = sentence.strip()
            if any(
                re.search(pattern, sentence, re.IGNORECASE)
                for pattern in self.action_patterns
            ):
                action_items.append(sentence)

        return action_items[:5]  # Limit to 5 action items

    def _calculate_confidence_score(
        self, content: str, sentiment_score: float, themes: List[str]
    ) -> float:
        """Calculate confidence score for analysis."""
        base_confidence = 0.7

        # Adjust based on content length
        if len(content) > 50:
            base_confidence += 0.1
        if len(content) > 200:
            base_confidence += 0.1

        # Adjust based on sentiment strength
        if abs(sentiment_score) > 0.5:
            base_confidence += 0.05

        # Adjust based on themes found
        if len(themes) > 0:
            base_confidence += 0.05
        if len(themes) > 2:
            base_confidence += 0.05

        return min(1.0, base_confidence)

    async def _update_feedback_analysis(
        self, feedback_id: str, analysis: FeedbackAnalysis
    ):
        """Update feedback with analysis results."""
        try:
            # This would integrate with the database tool
            logger.info(f"Updating feedback analysis for {feedback_id}")

        except Exception as e:
            logger.error(f"Failed to update feedback analysis: {e}")

    async def _get_feedback(
        self, feedback_id: str, workspace_id: str
    ) -> FeedbackRequest:
        """Get feedback by ID."""
        # This would integrate with the database tool
        # For now, return a placeholder
        return FeedbackRequest(
            feedback_id=feedback_id,
            feedback_type="user_experience",
            source="user",
            content="Sample feedback content",
            rating=4,
            sentiment="positive",
            categories=["usability"],
            metadata={},
            workspace_id=workspace_id,
        )

    def _calculate_period(self, summary_type: str) -> tuple:
        """Calculate period based on summary type."""
        now = datetime.now()

        if summary_type == "daily":
            start = now - timedelta(days=1)
            end = now
        elif summary_type == "weekly":
            start = now - timedelta(weeks=1)
            end = now
        elif summary_type == "monthly":
            start = now - timedelta(days=30)
            end = now
        else:
            start = now - timedelta(weeks=1)
            end = now

        return start, end

    async def _get_feedback_data(
        self, workspace_id: str, period_start: datetime, period_end: datetime
    ) -> List[Dict[str, Any]]:
        """Get feedback data for period."""
        # This would integrate with the database tool
        # For now, return sample data
        return [
            {
                "feedback_id": "sample_1",
                "rating": 4,
                "sentiment": "positive",
                "themes": ["usability", "performance"],
                "urgency": "medium",
                "timestamp": datetime.now(),
            }
        ]

    def _create_summary(
        self,
        feedback_data: List[Dict[str, Any]],
        summary_type: str,
        period_start: datetime,
        period_end: datetime,
    ) -> FeedbackSummary:
        """Create feedback summary."""
        if not feedback_data:
            return FeedbackSummary(
                summary_type=summary_type,
                period_start=period_start,
                period_end=period_end,
                total_feedback=0,
                average_rating=0.0,
                sentiment_distribution={},
                top_themes=[],
                improvement_areas=[],
                recommendations=[],
                metadata={"no_data": True},
            )

        # Calculate metrics
        total_feedback = len(feedback_data)
        ratings = [f.get("rating", 0) for f in feedback_data if f.get("rating")]
        average_rating = sum(ratings) / len(ratings) if ratings else 0.0

        # Sentiment distribution
        sentiments = [f.get("sentiment", "neutral") for f in feedback_data]
        sentiment_distribution = Counter(sentiments)

        # Top themes
        all_themes = []
        for f in feedback_data:
            all_themes.extend(f.get("themes", []))
        theme_counts = Counter(all_themes)
        top_themes = [
            {"theme": theme, "count": count}
            for theme, count in theme_counts.most_common(5)
        ]

        # Improvement areas (themes with negative sentiment)
        improvement_areas = []
        negative_themes = set()
        for f in feedback_data:
            if f.get("sentiment") == "negative":
                negative_themes.update(f.get("themes", []))
        improvement_areas = list(negative_themes)

        # Generate recommendations
        recommendations = []
        for area in improvement_areas[:3]:
            if area in self.improvement_recommendations:
                recommendations.extend(self.improvement_recommendations[area][:2])

        return FeedbackSummary(
            summary_type=summary_type,
            period_start=period_start,
            period_end=period_end,
            total_feedback=total_feedback,
            average_rating=average_rating,
            sentiment_distribution=dict(sentiment_distribution),
            top_themes=top_themes,
            improvement_areas=improvement_areas,
            recommendations=recommendations[:5],  # Limit to 5 recommendations
            metadata={
                "generated_at": datetime.now().isoformat(),
                "data_quality": "sample",
            },
        )

    async def _get_historical_feedback(
        self, workspace_id: str, trend_period: str, categories: List[str]
    ) -> List[Dict[str, Any]]:
        """Get historical feedback data."""
        # This would integrate with the database tool
        # For now, return sample data
        return []

    def _analyze_trend_patterns(
        self, historical_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Analyze trend patterns in historical data."""
        # This would implement actual trend analysis
        return []

    async def _get_recent_feedback(
        self, workspace_id: str, focus_areas: List[str]
    ) -> List[Dict[str, Any]]:
        """Get recent feedback for focus areas."""
        # This would integrate with the database tool
        # For now, return sample data
        return []

    def _create_recommendations(
        self, feedback_data: List[Dict[str, Any]], focus_areas: List[str]
    ) -> List[Dict[str, Any]]:
        """Create improvement recommendations."""
        recommendations = []

        # Group feedback by themes
        theme_feedback = defaultdict(list)
        for feedback in feedback_data:
            for theme in feedback.get("themes", []):
                theme_feedback[theme].append(feedback)

        # Generate recommendations for each theme
        for theme, feedback_list in theme_feedback.items():
            if theme in self.improvement_recommendations:
                theme_recommendations = self.improvement_recommendations[theme]

                # Calculate priority based on negative feedback
                negative_count = sum(
                    1 for f in feedback_list if f.get("sentiment") == "negative"
                )
                priority = (
                    "high"
                    if negative_count > 2
                    else "medium" if negative_count > 0 else "low"
                )

                recommendations.append(
                    {
                        "theme": theme,
                        "priority": priority,
                        "recommendations": theme_recommendations[:2],
                        "feedback_count": len(feedback_list),
                        "negative_feedback_count": negative_count,
                    }
                )

        # Sort by priority and feedback count
        recommendations.sort(
            key=lambda x: (
                {"high": 3, "medium": 2, "low": 1}[x["priority"]],
                x["feedback_count"],
            ),
            reverse=True,
        )

        return recommendations[:10]  # Limit to 10 recommendations

    def get_feedback_categories(self) -> Dict[str, Any]:
        """Get available feedback categories."""
        return self.feedback_categories.copy()

    def get_sentiment_patterns(self) -> Dict[str, List[str]]:
        """Get sentiment analysis patterns."""
        return self.sentiment_patterns.copy()

    def get_improvement_recommendations(self) -> Dict[str, List[str]]:
        """Get improvement recommendations."""
        return self.improvement_recommendations.copy()
