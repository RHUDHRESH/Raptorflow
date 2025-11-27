"""
Pain Point Miner (RES-004)

Research Guild's customer feedback analyst. Extracts and categorizes
specific user pain points from customer feedback text to provide
actionable product improvement insights.

Features:
- Customer feedback analysis and pain point extraction
- Automatic categorization of identified issues
- Structured output for product development prioritization
- Error handling and response validation

Analysis Flow:
1. Receive customer feedback text
2. Analyze for specific pain points and frustrations
3. Categorize each pain point (usability, pricing, features, etc.)
4. Return structured report with categorized insights
"""

import structlog
from typing import List, Dict, Any

from backend.models.research import PainPointRequest, PainPointReport, PainPoint
from backend.services.vertex_ai_client import vertex_ai_client
from backend.utils.correlation import get_correlation_id

logger = structlog.get_logger(__name__)


class PainPointMinerAgent:
    """
    RES-004: Pain Point Miner Agent for customer feedback analysis.

    This agent specializes in analyzing customer feedback to identify and
    categorize specific user pain points. It helps product teams understand
    customer frustrations, prioritize improvements, and make data-driven
    decisions about product development and feature prioritization.

    Key Capabilities:
    - Customer feedback parsing and analysis
    - Pain point identification and extraction
    - Automatic categorization and classification
    - Product improvement insights generation
    - Structured reporting for development teams

    Analysis Categories:
    - Usability: Interface, navigation, user experience issues
    - Pricing: Cost-related concerns and value perceptions
    - Features: Missing functionality or capability gaps
    - Performance: Speed, reliability, and efficiency problems
    - Reliability: Bugs, crashes, and system stability issues
    - Support: Help, documentation, and assistance needs

    Integration Points:
    - Product teams for feature prioritization
    - UX teams for interface improvements
    - Engineering for bug fixes and performance tuning
    - Marketing for messaging and positioning refinement
    - Customer success for support improvements
    """

    def __init__(self):
        """Initialize the Pain Point Miner Agent."""
        logger.info("Pain Point Miner Agent (RES-004) initialized")

        # Analysis parameters
        self.max_pain_points = 10  # Limit number of pain points per analysis

        # Default categories for pain point classification
        self.categories = [
            "Usability",
            "Pricing",
            "Missing Feature",
            "Performance",
            "Reliability",
            "Support",
            "Design",
            "Compatibility",
            "Security",
            "Other"
        ]

    async def find_pain_points(self, request: PainPointRequest) -> PainPointReport:
        """
        Analyze customer feedback to identify and categorize pain points.

        Main entry point for pain point analysis. Takes customer feedback
        text and extracts specific user frustrations and problems, organizing
        them by category for actionable product insights.

        Args:
            request: PainPointRequest containing customer feedback text

        Returns:
            PainPointReport with categorized pain points for product improvement

        Example:
            request = PainPointRequest(
                customer_feedback="The app crashes when uploading photos and the interface is confusing."
            )
            report = await agent.find_pain_points(request)
            # Returns categorized pain points like:
            # - Reliability: "App crashes when uploading photos"
            # - Usability: "Interface is confusing"
        """
        correlation_id = get_correlation_id()

        logger.info(
            "Analyzing customer feedback for pain points",
            feedback_length=len(request.customer_feedback),
            correlation_id=correlation_id
        )

        try:
            # Build analysis prompt
            prompt = self._build_pain_point_prompt(request.customer_feedback)

            # Generate analysis with LLM
            pain_points = await self._analyze_with_llm(prompt, correlation_id)

            # Create report
            report = PainPointReport(pain_points=pain_points)

            logger.info(
                "Pain point analysis completed successfully",
                pain_points_found=len(pain_points),
                categories_used=len(set(pp.category for pp in pain_points)),
                correlation_id=correlation_id
            )

            return report

        except Exception as e:
            logger.error(
                "Pain point analysis failed",
                error=str(e),
                correlation_id=correlation_id
            )

            # Return minimal report with error indication
            return PainPointReport(
                pain_points=[
                    PainPoint(
                        category="Analysis Error",
                        pain_point=f"Unable to analyze feedback due to processing error: {str(e)}"
                    )
                ]
            )

    def _build_pain_point_prompt(self, customer_feedback: str) -> str:
        """
        Build the LLM prompt for pain point analysis.

        Creates a focused prompt instructing the LLM to act as a product
        research analyst and systematically extract pain points from feedback.

        Args:
            customer_feedback: Raw customer feedback text

        Returns:
            Structured prompt for pain point analysis
        """
        prompt = f"""
You are a product research analyst specializing in customer feedback analysis and user experience research. Your task is to analyze customer feedback and extract specific user pain points that need to be addressed for product improvement.

Analyze the following customer feedback and identify the key pain points:

Customer Feedback: "{customer_feedback}"

Instructions:
1. Identify specific problems, frustrations, or difficulties mentioned by the customer
2. For each pain point, assign an appropriate category from these options:
   - Usability: Interface, navigation, ease-of-use issues
   - Pricing: Cost, value, pricing model concerns
   - Missing Feature: Functionality that users want but doesn't exist
   - Performance: Speed, loading times, responsiveness issues
   - Reliability: Bugs, crashes, system failures, stability problems
   - Support: Help, documentation, customer service needs
   - Design: Visual design, layout, aesthetics issues
   - Compatibility: Platform, device, browser compatibility problems
   - Security: Privacy, data protection, safety concerns
   - Other: Any other category not covered above

3. Each pain point should be:
   - Specific and actionable
   - Written from the customer's perspective
   - Clear and concise
   - Directly tied to something mentioned in the feedback

Return your analysis as a JSON object with a single key "pain_points" containing an array of objects. Each object must have exactly two keys:
- "category": one of the category options listed above
- "pain_point": a clear description of the specific pain point

Example format:
{{
  "pain_points": [
    {{
      "category": "Usability",
      "pain_point": "Navigation menu is difficult to find"
    }},
    {{
      "category": "Performance",
      "pain_point": "Page loading times are too slow"
    }}
  ]
}}

CRITICAL: Return ONLY valid JSON. Limit to maximum 10 most important pain points.
"""
        return prompt

    async def _analyze_with_llm(self, prompt: str, correlation_id: str) -> List[PainPoint]:
        """
        Execute LLM analysis and parse pain point results.

        Args:
            prompt: Complete analysis prompt
            correlation_id: Request correlation ID

        Returns:
            List of categorized PainPoint objects

        Raises:
            Exception: If LLM call fails and can't be recovered
        """
        try:
            response = await vertex_ai_client.generate_json(
                prompt=prompt,
                system_prompt=self._get_research_analyst_prompt(),
                model_type="fast",  # Use fast model for analysis
                temperature=0.2,     # Low creativity for factual analysis
                max_tokens=1000      # Allow for multiple pain points
            )

            # Parse and validate response
            pain_points = self._parse_pain_points(response, correlation_id)

            return pain_points

        except Exception as e:
            logger.warning(
                f"Pain point LLM analysis failed: {e}",
                correlation_id=correlation_id
            )
            raise

    def _parse_pain_points(self, response: Dict[str, Any], correlation_id: str) -> List[PainPoint]:
        """
        Parse and validate pain point analysis response.

        Args:
            response: Raw LLM response containing pain points
            correlation_id: Request correlation ID

        Returns:
            List of validated PainPoint objects

        Raises:
            Exception: If response cannot be properly parsed
        """
        try:
            if not isinstance(response, dict) or "pain_points" not in response:
                raise ValueError("Invalid response format: missing pain_points key")

            pain_points_data = response["pain_points"]

            if not isinstance(pain_points_data, list):
                raise ValueError("pain_points must be a list")

            validated_pain_points = []
            for i, pp_data in enumerate(pain_points_data[:self.max_pain_points]):  # Limit to max
                try:
                    if not isinstance(pp_data, dict):
                        logger.warning(f"Pain point {i} is not an object, skipping", correlation_id=correlation_id)
                        continue

                    category = str(pp_data.get("category", "")).strip()
                    pain_point = str(pp_data.get("pain_point", "")).strip()

                    if not category or not pain_point:
                        logger.warning(f"Pain point {i} missing required fields, skipping", correlation_id=correlation_id)
                        continue

                    # Validate category is in known categories
                    if category not in self.categories:
                        logger.info(f"Unknown category '{category}', adding to 'Other'", correlation_id=correlation_id)
                        category = "Other"

                    # Validate pain point meets minimum requirements
                    if len(pain_point) < 5:
                        logger.warning(f"Pain point {i} too short, skipping", correlation_id=correlation_id)
                        continue

                    validated_pp = PainPoint(
                        category=category,
                        pain_point=pain_point
                    )
                    validated_pain_points.append(validated_pp)

                except Exception as pp_error:
                    logger.warning(
                        f"Failed to parse pain point {i}: {pp_error}",
                        correlation_id=correlation_id
                    )
                    continue

            if not validated_pain_points:
                logger.warning("No valid pain points parsed", correlation_id=correlation_id)
                raise ValueError("No valid pain points found in response")

            logger.debug(
                f"Successfully parsed {len(validated_pain_points)} pain points",
                correlation_id=correlation_id
            )

            return validated_pain_points

        except Exception as e:
            logger.error(
                f"Failed to parse pain point response: {e}",
                correlation_id=correlation_id
            )
            raise

    def _get_research_analyst_prompt(self) -> str:
        """
        Get system prompt defining the LLM's role as a research analyst.

        Returns:
            System instruction for customer feedback analysis behavior
        """
        return """You are an expert product research analyst with 10+ years of experience in customer feedback analysis, user experience research, and product improvement prioritization.

Your expertise includes:
- Customer feedback parsing and sentiment analysis
- Pain point identification and categorization
- User experience issue recognition
- Product improvement insight generation
- Prioritization of customer concerns for development teams

You excel at:
- Extracting actionable insights from qualitative feedback
- Categorizing problems by product area and user impact
- Distinguishing between symptoms and root causes
- Identifying patterns in customer complaints
- Providing constructive, actionable product recommendations

Your analysis is:
- Objective and evidence-based
- Focused on solvable product issues
- Prioritized by user impact and frequency
- Written in clear, professional language
- Directly actionable for product development teams"""

    async def get_category_distribution(self, pain_points: List[PainPoint]) -> Dict[str, int]:
        """
        Get distribution of pain points across categories.

        Useful for understanding the dominant problem areas in customer feedback.

        Args:
            pain_points: List of identified pain points

        Returns:
            Dictionary mapping categories to counts
        """
        distribution = {}
        for pp in pain_points:
            distribution[pp.category] = distribution.get(pp.category, 0) + 1
        return distribution

    async def get_priority_score(self, pain_point: PainPoint) -> int:
        """
        Calculate a priority score for a pain point based on category and severity.

        This is a simple heuristic for prioritizing pain points. In a real implementation,
        this might consider additional factors like user segment, frequency, etc.

        Args:
            pain_point: Individual pain point to score

        Returns:
            Priority score (higher = more urgent)
        """
        category_weights = {
            "Usability": 8,      # High impact on user experience
            "Pricing": 7,        # affects revenue and acquisition
            "Reliability": 9,    # Critical system issues
            "Performance": 7,    # Affects user satisfaction
            "Support": 6,        # Important but not core product
            "Missing Feature": 6, # Nice to have but not urgent
            "Design": 5,         # Important but less critical
            "Compatibility": 5,  # Platform-specific issues
            "Security": 10,      # Extremely high priority
            "Other": 4           # Lower priority unknown issues
        }

        # Base score from category
        base_score = category_weights.get(pain_point.category, 4)

        # Bonus for explicit problem indicators in the pain point text
        problem_indicators = ["crash", "error", "slow", "confusing", "expensive", "missing", "broken"]
        bonus_score = sum(1 for indicator in problem_indicators
                         if indicator in pain_point.pain_point.lower())

        return min(base_score + bonus_score, 10)  # Cap at 10


# Global singleton instance
pain_point_miner_agent = PainPointMinerAgent()
