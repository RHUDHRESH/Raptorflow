"""
Conversion Optimizer for analyzing and improving CTAs and conversion elements.

This module analyzes content for conversion potential and provides specific
recommendations to improve:
- Call-to-action (CTA) effectiveness
- Urgency signals
- Objection handling
- Mid-content CTAs
- Trust signals
- Conversion flow optimization

Uses best practices from conversion rate optimization (CRO) and behavioral psychology.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import re
import structlog
from backend.performance.performance_memory import performance_memory

logger = structlog.get_logger()


class ConversionOptimizer:
    """
    Analyzes and optimizes content for maximum conversion potential.

    Evaluates conversion elements and provides actionable recommendations
    based on CRO best practices and historical performance data.
    """

    def __init__(self):
        """Initialize the conversion optimizer."""
        self.memory = performance_memory

        # CTA power words and phrases
        self.power_words = {
            "urgency": ["now", "today", "limited", "hurry", "instant", "immediately", "deadline"],
            "value": ["free", "bonus", "exclusive", "guarantee", "proven", "results"],
            "action": ["get", "start", "discover", "learn", "join", "unlock", "access"],
            "social_proof": ["trusted", "verified", "popular", "bestselling", "award-winning"],
            "curiosity": ["secret", "reveal", "discover", "uncover", "insider"]
        }

        # Trust signals keywords
        self.trust_signals = [
            "guarantee", "certified", "secure", "verified", "trusted",
            "money-back", "risk-free", "tested", "proven", "licensed"
        ]

        # Objection handling phrases
        self.objection_handlers = [
            "no credit card required", "cancel anytime", "free trial",
            "money-back guarantee", "risk-free", "no commitment"
        ]

    async def analyze_conversion_potential(
        self,
        content: str,
        content_type: str,
        workspace_id: str,
        cta_text: Optional[str] = None,
        target_action: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze content for conversion potential and optimization opportunities.

        Args:
            content: The content text to analyze
            content_type: Type of content (email, landing_page, blog, etc.)
            workspace_id: Workspace identifier for historical context
            cta_text: Specific CTA text to analyze (optional)
            target_action: Target conversion action (signup, purchase, download, etc.)

        Returns:
            Dictionary containing:
                - conversion_score: Overall conversion potential (0.0-1.0)
                - cta_analysis: Analysis of CTA effectiveness
                - urgency_score: Urgency signal strength
                - trust_score: Trust signal presence
                - objection_handling_score: Objection handling effectiveness
                - recommendations: Specific improvement suggestions
                - optimized_ctas: Alternative CTA suggestions
        """
        logger.info(
            "Analyzing conversion potential",
            content_type=content_type,
            workspace_id=workspace_id
        )

        try:
            # Analyze different conversion elements
            cta_analysis = self._analyze_cta(content, cta_text)
            urgency_analysis = self._analyze_urgency_signals(content)
            trust_analysis = self._analyze_trust_signals(content)
            objection_analysis = self._analyze_objection_handling(content)
            flow_analysis = self._analyze_conversion_flow(content, content_type)

            # Calculate overall conversion score
            conversion_score = self._calculate_conversion_score(
                cta_analysis,
                urgency_analysis,
                trust_analysis,
                objection_analysis,
                flow_analysis
            )

            # Generate recommendations
            recommendations = self._generate_conversion_recommendations(
                cta_analysis,
                urgency_analysis,
                trust_analysis,
                objection_analysis,
                flow_analysis,
                content_type
            )

            # Generate optimized CTA alternatives
            optimized_ctas = self._generate_optimized_ctas(
                cta_text or cta_analysis.get("primary_cta", ""),
                target_action or "convert",
                content_type
            )

            result = {
                "conversion_score": conversion_score,
                "cta_analysis": cta_analysis,
                "urgency_score": urgency_analysis["score"],
                "urgency_signals": urgency_analysis["signals"],
                "trust_score": trust_analysis["score"],
                "trust_signals": trust_analysis["signals"],
                "objection_handling_score": objection_analysis["score"],
                "objection_handlers": objection_analysis["handlers"],
                "flow_analysis": flow_analysis,
                "recommendations": recommendations,
                "optimized_ctas": optimized_ctas,
                "analyzed_at": datetime.utcnow().isoformat()
            }

            return result

        except Exception as e:
            logger.error("Failed to analyze conversion potential", error=str(e))
            raise

    def _analyze_cta(
        self,
        content: str,
        explicit_cta: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze call-to-action effectiveness.

        Args:
            content: Content text
            explicit_cta: Explicit CTA text if provided

        Returns:
            CTA analysis with scores and identified CTAs
        """
        # Find CTAs in content (common patterns)
        cta_patterns = [
            r'(?:click|tap|press)\s+(?:here|now|below)',
            r'(?:sign up|subscribe|register|join)',
            r'(?:get started|start now|begin)',
            r'(?:download|claim|grab)',
            r'(?:buy|purchase|order)\s+now',
            r'(?:learn more|read more|discover)',
            r'(?:try|test)\s+(?:free|now|today)'
        ]

        found_ctas = []
        for pattern in cta_patterns:
            matches = re.findall(pattern, content.lower())
            found_ctas.extend(matches)

        # Use explicit CTA if provided
        primary_cta = explicit_cta if explicit_cta else (found_ctas[0] if found_ctas else "")

        # Score CTA effectiveness
        cta_score = 0.0
        cta_strengths = []
        cta_weaknesses = []

        if primary_cta:
            cta_lower = primary_cta.lower()

            # Check for action words
            has_action_word = any(
                word in cta_lower for word in self.power_words["action"]
            )
            if has_action_word:
                cta_score += 0.3
                cta_strengths.append("Contains action-oriented language")
            else:
                cta_weaknesses.append("Lacks strong action verbs")

            # Check for value proposition
            has_value = any(
                word in cta_lower for word in self.power_words["value"]
            )
            if has_value:
                cta_score += 0.2
                cta_strengths.append("Communicates value")

            # Check for urgency
            has_urgency = any(
                word in cta_lower for word in self.power_words["urgency"]
            )
            if has_urgency:
                cta_score += 0.2
                cta_strengths.append("Creates urgency")

            # Check length (ideal: 2-5 words)
            word_count = len(primary_cta.split())
            if 2 <= word_count <= 5:
                cta_score += 0.15
                cta_strengths.append("Optimal length")
            else:
                cta_weaknesses.append("CTA too long" if word_count > 5 else "CTA too short")

            # Check for first-person language
            if any(word in cta_lower for word in ["my", "i", "me"]):
                cta_score += 0.15
                cta_strengths.append("Uses first-person language")

        else:
            cta_weaknesses.append("No clear CTA found")

        return {
            "primary_cta": primary_cta,
            "all_ctas": found_ctas,
            "cta_count": len(found_ctas),
            "score": min(1.0, cta_score),
            "strengths": cta_strengths,
            "weaknesses": cta_weaknesses
        }

    def _analyze_urgency_signals(self, content: str) -> Dict[str, Any]:
        """
        Analyze urgency signals in content.

        Args:
            content: Content text

        Returns:
            Urgency analysis with score and identified signals
        """
        content_lower = content.lower()
        found_signals = []

        for word in self.power_words["urgency"]:
            if word in content_lower:
                found_signals.append(word)

        # Check for time-based urgency
        time_patterns = [
            r'\d+\s*(?:hour|day|week)s?\s+(?:left|remaining|only)',
            r'(?:expires?|ends?)\s+(?:soon|today|tonight)',
            r'(?:last chance|final|closing)',
            r'limited\s+(?:time|offer|spots?)'
        ]

        for pattern in time_patterns:
            if re.search(pattern, content_lower):
                found_signals.append(f"Time-based urgency: {pattern}")

        # Calculate urgency score
        urgency_score = min(1.0, len(found_signals) * 0.2)

        return {
            "score": urgency_score,
            "signals": found_signals,
            "has_urgency": urgency_score > 0.2
        }

    def _analyze_trust_signals(self, content: str) -> Dict[str, Any]:
        """
        Analyze trust signals in content.

        Args:
            content: Content text

        Returns:
            Trust analysis with score and identified signals
        """
        content_lower = content.lower()
        found_signals = []

        for signal in self.trust_signals:
            if signal in content_lower:
                found_signals.append(signal)

        # Check for social proof patterns
        social_proof_patterns = [
            r'\d+(?:,\d+)*\s+(?:customers?|users?|clients?)',
            r'\d+(?:,\d+)*\+\s+(?:people|businesses|companies)',
            r'(?:testimonial|review|rating)',
            r'\d+(?:\.\d+)?\s*(?:stars?|\/5)'
        ]

        for pattern in social_proof_patterns:
            if re.search(pattern, content_lower):
                found_signals.append(f"Social proof: {pattern}")

        # Calculate trust score
        trust_score = min(1.0, len(found_signals) * 0.25)

        return {
            "score": trust_score,
            "signals": found_signals,
            "has_trust_signals": trust_score > 0.25
        }

    def _analyze_objection_handling(self, content: str) -> Dict[str, Any]:
        """
        Analyze objection handling in content.

        Args:
            content: Content text

        Returns:
            Objection handling analysis
        """
        content_lower = content.lower()
        found_handlers = []

        for handler in self.objection_handlers:
            if handler in content_lower:
                found_handlers.append(handler)

        # Check for FAQ or common objections addressed
        faq_patterns = [
            r'(?:faq|frequently asked|common questions)',
            r'(?:but what if|you might be wondering)',
            r'(?:concern|worried|hesitant)'
        ]

        for pattern in faq_patterns:
            if re.search(pattern, content_lower):
                found_handlers.append(f"Addresses concerns: {pattern}")

        # Calculate objection handling score
        objection_score = min(1.0, len(found_handlers) * 0.3)

        return {
            "score": objection_score,
            "handlers": found_handlers,
            "addresses_objections": objection_score > 0.3
        }

    def _analyze_conversion_flow(
        self,
        content: str,
        content_type: str
    ) -> Dict[str, Any]:
        """
        Analyze the conversion flow structure.

        Args:
            content: Content text
            content_type: Type of content

        Returns:
            Flow analysis
        """
        paragraphs = content.split('\n\n')
        total_length = len(content.split())

        analysis = {
            "has_hook": False,
            "has_value_prop": False,
            "has_mid_content_cta": False,
            "has_final_cta": False,
            "optimal_structure": False
        }

        # Check for hook in first paragraph (first 10% of content)
        hook_section = ' '.join(content.split()[:max(10, total_length // 10)])
        hook_patterns = [
            r'(?:imagine|what if|did you know)',
            r'(?:struggling|tired of|frustrated)',
            r'(?:\d+% |\d+ ways?|secret)'
        ]
        if any(re.search(pattern, hook_section.lower()) for pattern in hook_patterns):
            analysis["has_hook"] = True

        # Check for value proposition (first 25% of content)
        value_section = ' '.join(content.split()[:total_length // 4])
        if any(word in value_section.lower() for word in self.power_words["value"]):
            analysis["has_value_prop"] = True

        # Check for mid-content CTA (middle 50% of content)
        mid_start = total_length // 4
        mid_end = (3 * total_length) // 4
        mid_section = ' '.join(content.split()[mid_start:mid_end])
        if re.search(r'(?:click|sign|start|join)', mid_section.lower()):
            analysis["has_mid_content_cta"] = True

        # Check for final CTA (last 10% of content)
        final_section = ' '.join(content.split()[-max(10, total_length // 10):])
        if re.search(r'(?:click|sign|start|join|get)', final_section.lower()):
            analysis["has_final_cta"] = True

        # Determine if structure is optimal
        analysis["optimal_structure"] = all([
            analysis["has_hook"],
            analysis["has_value_prop"],
            analysis["has_final_cta"]
        ])

        return analysis

    def _calculate_conversion_score(
        self,
        cta_analysis: Dict[str, Any],
        urgency_analysis: Dict[str, Any],
        trust_analysis: Dict[str, Any],
        objection_analysis: Dict[str, Any],
        flow_analysis: Dict[str, Any]
    ) -> float:
        """
        Calculate overall conversion score.

        Args:
            cta_analysis: CTA analysis results
            urgency_analysis: Urgency analysis results
            trust_analysis: Trust analysis results
            objection_analysis: Objection handling analysis
            flow_analysis: Conversion flow analysis

        Returns:
            Overall conversion score (0.0-1.0)
        """
        # Weighted scoring
        weights = {
            "cta": 0.30,
            "urgency": 0.15,
            "trust": 0.20,
            "objection": 0.15,
            "flow": 0.20
        }

        # Calculate flow score
        flow_score = sum([
            0.2 if flow_analysis["has_hook"] else 0,
            0.2 if flow_analysis["has_value_prop"] else 0,
            0.2 if flow_analysis["has_mid_content_cta"] else 0,
            0.3 if flow_analysis["has_final_cta"] else 0,
            0.1 if flow_analysis["optimal_structure"] else 0
        ])

        total_score = (
            cta_analysis["score"] * weights["cta"] +
            urgency_analysis["score"] * weights["urgency"] +
            trust_analysis["score"] * weights["trust"] +
            objection_analysis["score"] * weights["objection"] +
            flow_score * weights["flow"]
        )

        return min(1.0, total_score)

    def _generate_conversion_recommendations(
        self,
        cta_analysis: Dict[str, Any],
        urgency_analysis: Dict[str, Any],
        trust_analysis: Dict[str, Any],
        objection_analysis: Dict[str, Any],
        flow_analysis: Dict[str, Any],
        content_type: str
    ) -> List[Dict[str, str]]:
        """
        Generate specific recommendations to improve conversion.

        Returns:
            List of recommendations with priority and specific actions
        """
        recommendations = []

        # CTA recommendations
        if cta_analysis["score"] < 0.6:
            recommendations.append({
                "priority": "high",
                "category": "CTA",
                "issue": "Weak or missing call-to-action",
                "recommendation": "Add a clear, action-oriented CTA using power words like 'Get', 'Start', 'Unlock'",
                "example": "Get Started Free" if content_type == "landing_page" else "Try it now"
            })

        if not cta_analysis.get("primary_cta"):
            recommendations.append({
                "priority": "critical",
                "category": "CTA",
                "issue": "No CTA detected",
                "recommendation": "Add a prominent call-to-action at the end of your content",
                "example": "Start Your Free Trial Today"
            })

        # Urgency recommendations
        if urgency_analysis["score"] < 0.3:
            recommendations.append({
                "priority": "medium",
                "category": "Urgency",
                "issue": "Lacks urgency signals",
                "recommendation": "Add time-sensitive language to encourage immediate action",
                "example": "Limited time offer - Get 50% off today only"
            })

        # Trust recommendations
        if trust_analysis["score"] < 0.4:
            recommendations.append({
                "priority": "high",
                "category": "Trust",
                "issue": "Insufficient trust signals",
                "recommendation": "Add social proof, guarantees, or certifications",
                "example": "Join 10,000+ satisfied customers" or "100% money-back guarantee"
            })

        # Objection handling
        if objection_analysis["score"] < 0.3:
            recommendations.append({
                "priority": "medium",
                "category": "Objections",
                "issue": "Doesn't address common objections",
                "recommendation": "Proactively address concerns with risk-reversal language",
                "example": "No credit card required" or "Cancel anytime, no questions asked"
            })

        # Flow recommendations
        if not flow_analysis["has_hook"]:
            recommendations.append({
                "priority": "high",
                "category": "Flow",
                "issue": "Missing engaging hook",
                "recommendation": "Start with a compelling hook to grab attention",
                "example": "Tired of losing leads? Here's how to convert 3x more prospects..."
            })

        if not flow_analysis["has_final_cta"]:
            recommendations.append({
                "priority": "critical",
                "category": "Flow",
                "issue": "No final CTA",
                "recommendation": "End with a clear, specific call-to-action",
                "example": "Ready to 10x your conversions? Start your free trial now"
            })

        if not flow_analysis["has_mid_content_cta"] and content_type in ["blog", "landing_page"]:
            recommendations.append({
                "priority": "low",
                "category": "Flow",
                "issue": "No mid-content CTA",
                "recommendation": "Add a soft CTA in the middle of your content",
                "example": "Want to learn more? Download our free guide"
            })

        return recommendations

    def _generate_optimized_ctas(
        self,
        current_cta: str,
        target_action: str,
        content_type: str
    ) -> List[Dict[str, str]]:
        """
        Generate optimized CTA alternatives.

        Args:
            current_cta: Current CTA text
            target_action: Target conversion action
            content_type: Type of content

        Returns:
            List of optimized CTA suggestions with rationale
        """
        cta_templates = {
            "signup": [
                "Get Started Free",
                "Start Your Free Trial",
                "Join Free Today",
                "Sign Up - It's Free"
            ],
            "download": [
                "Download Your Free Guide",
                "Get Instant Access",
                "Claim Your Free Copy",
                "Download Now"
            ],
            "purchase": [
                "Get [Product] Today",
                "Start Saving Now",
                "Unlock [Benefit]",
                "Buy Now & Save"
            ],
            "learn": [
                "Discover How",
                "Learn the Secrets",
                "See How It Works",
                "Get the Details"
            ],
            "convert": [
                "Get Started Now",
                "Try It Free",
                "See It In Action",
                "Start Today"
            ]
        }

        templates = cta_templates.get(target_action.lower(), cta_templates["convert"])

        optimized = []
        for template in templates:
            optimized.append({
                "cta_text": template,
                "type": target_action,
                "rationale": f"Action-oriented, clear value, optimal length ({len(template.split())} words)",
                "includes_power_words": self._count_power_words(template)
            })

        return optimized

    def _count_power_words(self, text: str) -> int:
        """Count power words in text."""
        count = 0
        text_lower = text.lower()
        for category in self.power_words.values():
            for word in category:
                if word in text_lower:
                    count += 1
        return count


# Global instance
conversion_optimizer = ConversionOptimizer()
