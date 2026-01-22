"""
EmailSpecialist specialist agent for Raptorflow marketing automation.
Handles email campaign creation, optimization, and performance analysis.
"""

import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..base import BaseAgent
from backend.agents.config import ModelTier
from ..exceptions import DatabaseError, ValidationError
from ..state import AgentState, add_message, update_state

logger = logging.getLogger(__name__)


@dataclass
class EmailCampaignRequest:
    """Email campaign creation request."""

    campaign_type: str  # newsletter, promotional, transactional, automation
    objective: str  # awareness, conversion, retention, engagement
    target_segment: str
    subject_line_focus: str
    content_focus: str
    tone: str  # professional, casual, urgent, friendly
    personalization_level: str  # low, medium, high
    urgency: str  # normal, high, urgent
    call_to_action: str
    keywords: List[str]


@dataclass
class EmailContent:
    """Email content structure."""

    subject_line: str
    preheader: str
    greeting: str
    body_content: str
    call_to_action: str
    signature: str
    personalization_tokens: List[str]
    spam_score: float
    engagement_prediction: float


@dataclass
class EmailCampaign:
    """Complete email campaign."""

    campaign_id: str
    campaign_name: str
    campaign_type: str
    objective: str
    target_segment: str
    content: EmailContent
    sending_strategy: Dict[str, Any]
    performance_prediction: Dict[str, Any]
    optimization_recommendations: List[str]
    a_b_test_variants: List[Dict[str, Any]]
    compliance_check: Dict[str, Any]
    created_at: datetime
    metadata: Dict[str, Any]


class EmailSpecialist(BaseAgent):
    """Specialist agent for email marketing campaigns."""

    def __init__(self):
        super().__init__(
            name="EmailSpecialist",
            description="Creates and optimizes email marketing campaigns",
            model_tier=ModelTier.FLASH,
            tools=["web_search", "database", "content_gen"],
        )

        # Email campaign templates
        self.campaign_templates = {
            "newsletter": {
                "purpose": "inform and engage subscribers",
                "typical_subjects": ["Weekly Update", "Industry News", "Tips & Tricks"],
                "content_structure": [
                    "greeting",
                    "main_content",
                    "highlights",
                    "call_to_action",
                ],
                "optimal_send_times": ["Tuesday 9:00 AM", "Thursday 2:00 PM"],
                "engagement_benchmarks": {
                    "open_rate": 0.25,
                    "click_rate": 0.03,
                    "conversion_rate": 0.01,
                },
            },
            "promotional": {
                "purpose": "drive sales and conversions",
                "typical_subjects": [
                    "Limited Offer",
                    "Special Discount",
                    "New Product",
                ],
                "content_structure": [
                    "greeting",
                    "offer",
                    "benefits",
                    "urgency",
                    "call_to_action",
                ],
                "optimal_send_times": ["Monday 10:00 AM", "Friday 4:00 PM"],
                "engagement_benchmarks": {
                    "open_rate": 0.20,
                    "click_rate": 0.04,
                    "conversion_rate": 0.02,
                },
            },
            "transactional": {
                "purpose": "confirm transactions and provide service updates",
                "typical_subjects": [
                    "Order Confirmation",
                    "Shipping Update",
                    "Password Reset",
                ],
                "content_structure": [
                    "greeting",
                    "transaction_details",
                    "next_steps",
                    "support",
                ],
                "optimal_send_times": ["immediate", "business_hours"],
                "engagement_benchmarks": {
                    "open_rate": 0.60,
                    "click_rate": 0.10,
                    "conversion_rate": 0.05,
                },
            },
            "automation": {
                "purpose": "nurture leads and maintain engagement",
                "typical_subjects": [
                    "Welcome Series",
                    "Re-engagement",
                    "Abandoned Cart",
                ],
                "content_structure": [
                    "greeting",
                    "personalized_content",
                    "recommendations",
                    "call_to_action",
                ],
                "optimal_send_times": ["triggered", "behavioral"],
                "engagement_benchmarks": {
                    "open_rate": 0.35,
                    "click_rate": 0.06,
                    "conversion_rate": 0.03,
                },
            },
        }

        # Subject line formulas
        self.subject_formulas = {
            "question": "What if {benefit}?",
            "statistic": "{number}% of {audience} {action}",
            "urgency": "Only {time} left to {action}",
            "benefit": "Get {benefit} in {timeframe}",
            "curiosity": "The secret to {desired_outcome}",
            "personalization": "{name}, {personalized_message}",
            "social_proof": "Join {number} {audience} who {action}",
            "problem_solution": "Tired of {problem}? Try {solution}",
        }

        # Spam trigger words
        self.spam_triggers = {
            "high_risk": [
                "free",
                "money",
                "cash",
                "winner",
                "congratulations",
                "guarantee",
            ],
            "medium_risk": ["buy", "order", "purchase", "discount", "sale", "offer"],
            "low_risk": ["deal", "save", "promotion", "special", "limited"],
        }

        # Personalization tokens
        self.personalization_tokens = [
            "{first_name}",
            "{last_name}",
            "{company}",
            "{industry}",
            "{location}",
            "{recent_purchase}",
            "{browse_history}",
            "{preferences}",
            "{segment}",
            "{loyalty_status}",
            "{last_visit}",
            "{cart_value}",
            "{engagement_score}",
        ]

        # Email compliance rules
        self.compliance_rules = {
            "can_spam": {
                "required_elements": [
                    "physical_address",
                    "unsubscribe_link",
                    "clear_subject",
                ],
                "prohibited_elements": ["misleading_subject", "false_headers"],
                "penalties": ["fines", "blacklisting", "legal_action"],
            },
            "gdpr": {
                "required_elements": [
                    "explicit_consent",
                    "data_protection",
                    "right_to_withdraw",
                ],
                "prohibited_elements": [
                    "non_consensual_marketing",
                    "data_retention_beyond_necessity",
                ],
                "penalties": ["heavy_fines", "reputation_damage"],
            },
        }

        # Engagement prediction factors
        self.engagement_factors = {
            "subject_line": 0.3,
            "personalization": 0.25,
            "content_relevance": 0.2,
            "timing": 0.15,
            "sender_reputation": 0.1,
        }

    def get_system_prompt(self) -> str:
        """Get the system prompt for the EmailSpecialist."""
        return """
You are the EmailSpecialist, a specialist agent for Raptorflow marketing automation platform.

Your role is to create high-performing email campaigns that drive engagement and conversions while maintaining compliance and best practices.

Key responsibilities:
1. Design effective email campaigns for different objectives
2. Craft compelling subject lines and content
3. Implement personalization and segmentation strategies
4. Ensure compliance with email regulations (CAN-SPAM, GDPR)
5. Predict and optimize email performance
6. Provide A/B testing recommendations

Campaign types you can create:
- Newsletter (informative, engaging, brand building)
- Promotional (sales, offers, conversions)
- Transactional (confirmations, updates, service)
- Automation (nurture sequences, triggered emails)

For each email campaign, you should:
- Create compelling subject lines with high open rates
- Write engaging body content with clear value proposition
- Implement personalization for relevance
- Include clear calls-to-action
- Ensure compliance with regulations
- Predict performance metrics
- Provide optimization recommendations
- Suggest A/B testing opportunities

Always focus on creating emails that provide value to recipients while achieving business objectives. Consider deliverability, engagement, and conversion optimization.
"""

    async def execute(self, state: AgentState) -> AgentState:
        """Execute email campaign creation."""
        try:
            # Validate workspace context
            if not state.get("workspace_id"):
                return self._set_error(
                    state, "Workspace ID is required for email campaign creation"
                )

            # Extract email campaign request from state
            campaign_request = self._extract_campaign_request(state)

            if not campaign_request:
                return self._set_error(state, "No email campaign request provided")

            # Validate campaign request
            self._validate_campaign_request(campaign_request)

            # Create email campaign
            email_campaign = await self._create_email_campaign(campaign_request, state)

            # Store email campaign
            await self._store_email_campaign(email_campaign, state)

            # Add assistant message
            response = self._format_campaign_response(email_campaign)
            state = self._add_assistant_message(state, response)

            # Set output
            return self._set_output(
                state,
                {
                    "email_campaign": email_campaign.__dict__,
                    "campaign_type": email_campaign.campaign_type,
                    "subject_line": email_campaign.content.subject_line,
                    "engagement_prediction": email_campaign.performance_prediction[
                        "overall_engagement"
                    ],
                    "spam_score": email_campaign.content.spam_score,
                    "optimization_recommendations": email_campaign.optimization_recommendations,
                },
            )

        except Exception as e:
            logger.error(f"Email campaign creation failed: {e}")
            return self._set_error(state, f"Email campaign creation failed: {str(e)}")

    def _extract_campaign_request(
        self, state: AgentState
    ) -> Optional[EmailCampaignRequest]:
        """Extract email campaign request from state."""
        # Check if campaign request is in state
        if "email_campaign_request" in state:
            request_data = state["email_campaign_request"]
            return EmailCampaignRequest(**request_data)

        # Extract from user message
        user_input = self._extract_user_input(state)
        if not user_input:
            return None

        # Parse campaign request from user input
        return self._parse_campaign_request(user_input, state)

    def _parse_campaign_request(
        self, user_input: str, state: AgentState
    ) -> Optional[EmailCampaignRequest]:
        """Parse email campaign request from user input."""
        # Check for explicit campaign type mention
        campaign_types = list(self.campaign_templates.keys())
        detected_type = None

        for campaign_type in campaign_types:
            if campaign_type.lower() in user_input.lower():
                detected_type = campaign_type
                break

        if not detected_type:
            # Default to newsletter
            detected_type = "newsletter"

        # Extract other parameters
        objective = self._extract_parameter(
            user_input, ["objective", "goal", "purpose"], "engagement"
        )
        segment = self._extract_parameter(
            user_input, ["segment", "audience", "target"], "general"
        )
        tone = self._extract_parameter(
            user_input, ["tone", "voice", "style"], "professional"
        )
        personalization = self._extract_parameter(
            user_input, ["personalization", "personalize"], "medium"
        )
        urgency = self._extract_parameter(
            user_input, ["urgency", "priority", "timeline"], "normal"
        )

        # Extract keywords
        keywords = self._extract_keywords(user_input)

        # Create campaign request
        return EmailCampaignRequest(
            campaign_type=detected_type,
            objective=objective,
            target_segment=segment,
            subject_line_focus=user_input[:50],  # First 50 chars as focus
            content_focus=user_input[:100],  # First 100 chars as content focus
            tone=tone,
            personalization_level=personalization,
            urgency=urgency,
            call_to_action="learn_more",
            keywords=keywords,
        )

    def _extract_parameter(
        self, text: str, param_names: List[str], default: str
    ) -> str:
        """Extract parameter value from text."""
        for param_name in param_names:
            for pattern in [f"{param_name}:", f"{param_name} is", f"{param_name} ="]:
                if pattern in text.lower():
                    start_idx = text.lower().find(pattern)
                    if start_idx != -1:
                        start_idx += len(pattern)
                        remaining = text[start_idx:].strip()
                        # Get first word or phrase
                        words = remaining.split()
                        if words:
                            return words[0].strip(".,!?")
        return default

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        # Simple keyword extraction
        import re

        # Remove common words and extract meaningful terms
        common_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "as",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "can",
            "shall",
            "email",
            "campaign",
            "send",
            "create",
            "generate",
        }

        # Extract words that are not common words
        words = re.findall(r"\b\w+\b", text.lower())
        keywords = [
            word for word in words if word not in common_words and len(word) > 2
        ]

        return keywords[:8]  # Limit to 8 keywords

    def _validate_campaign_request(self, request: EmailCampaignRequest):
        """Validate email campaign request."""
        if request.campaign_type not in self.campaign_templates:
            raise ValidationError(f"Unsupported campaign type: {request.campaign_type}")

        if request.objective not in [
            "awareness",
            "conversion",
            "retention",
            "engagement",
        ]:
            raise ValidationError(f"Invalid objective: {request.objective}")

        if request.tone not in ["professional", "casual", "urgent", "friendly"]:
            raise ValidationError(f"Invalid tone: {request.tone}")

        if request.personalization_level not in ["low", "medium", "high"]:
            raise ValidationError(
                f"Invalid personalization level: {request.personalization_level}"
            )

        if request.urgency not in ["normal", "high", "urgent"]:
            raise ValidationError(f"Invalid urgency: {request.urgency}")

    async def _create_email_campaign(
        self, request: EmailCampaignRequest, state: AgentState
    ) -> EmailCampaign:
        """Create email campaign based on request."""
        try:
            # Get template
            template = self.campaign_templates[request.campaign_type]

            # Generate campaign ID
            campaign_id = f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Generate campaign name
            campaign_name = f"{request.campaign_type.title()} - {request.objective.title()} - {datetime.now().strftime('%Y-%m-%d')}"

            # Create email content
            content = await self._create_email_content(request, template, state)

            # Create sending strategy
            sending_strategy = self._create_sending_strategy(request, template)

            # Create performance prediction
            performance_prediction = self._predict_performance(
                request, content, template
            )

            # Create optimization recommendations
            optimization_recommendations = self._create_optimization_recommendations(
                request, content, template
            )

            # Create A/B test variants
            a_b_test_variants = self._create_ab_test_variants(request, content)

            # Create compliance check
            compliance_check = self._check_compliance(content)

            # Create email campaign
            email_campaign = EmailCampaign(
                campaign_id=campaign_id,
                campaign_name=campaign_name,
                campaign_type=request.campaign_type,
                objective=request.objective,
                target_segment=request.target_segment,
                content=content,
                sending_strategy=sending_strategy,
                performance_prediction=performance_prediction,
                optimization_recommendations=optimization_recommendations,
                a_b_test_variants=a_b_test_variants,
                compliance_check=compliance_check,
                created_at=datetime.now(),
                metadata={
                    "tone": request.tone,
                    "personalization_level": request.personalization_level,
                    "urgency": request.urgency,
                    "keywords": request.keywords,
                },
            )

            return email_campaign

        except Exception as e:
            logger.error(f"Email campaign creation failed: {e}")
            raise DatabaseError(f"Email campaign creation failed: {str(e)}")

    async def _create_email_content(
        self, request: EmailCampaignRequest, template: Dict[str, Any], state: AgentState
    ) -> EmailContent:
        """Create email content."""
        # Generate subject line
        subject_line = self._generate_subject_line(request)

        # Generate preheader
        preheader = self._generate_preheader(request, subject_line)

        # Generate greeting
        greeting = self._generate_greeting(request)

        # Generate body content
        body_content = await self._generate_body_content(request, template, state)

        # Generate call to action
        call_to_action = self._generate_call_to_action(request)

        # Generate signature
        signature = self._generate_signature(state)

        # Determine personalization tokens
        personalization_tokens = self._determine_personalization_tokens(request)

        # Calculate spam score
        spam_score = self._calculate_spam_score(subject_line, body_content)

        # Calculate engagement prediction
        engagement_prediction = self._calculate_engagement_prediction(
            request, subject_line, body_content
        )

        return EmailContent(
            subject_line=subject_line,
            preheader=preheader,
            greeting=greeting,
            body_content=body_content,
            call_to_action=call_to_action,
            signature=signature,
            personalization_tokens=personalization_tokens,
            spam_score=spam_score,
            engagement_prediction=engagement_prediction,
        )

    def _generate_subject_line(self, request: EmailCampaignRequest) -> str:
        """Generate compelling subject line."""
        # Select formula based on campaign type and urgency
        if request.urgency == "urgent":
            formula_type = "urgency"
        elif request.campaign_type == "promotional":
            formula_type = random.choice(["benefit", "social_proof", "curiosity"])
        elif request.campaign_type == "newsletter":
            formula_type = random.choice(["question", "curiosity", "benefit"])
        else:
            formula_type = "benefit"

        formula = self.subject_formulas.get(
            formula_type, "Get {benefit} in {timeframe}"
        )

        # Generate subject line
        if formula_type == "question":
            subject = f"What if you could {request.objective}?"
        elif formula_type == "statistic":
            subject = f"75% of {request.target_segment} miss this opportunity"
        elif formula_type == "urgency":
            subject = f"Only 24 hours left to {request.objective}"
        elif formula_type == "benefit":
            subject = f"Get {request.objective} in just 5 minutes"
        elif formula_type == "curiosity":
            subject = f"The secret to successful {request.objective}"
        elif formula_type == "personalization":
            subject = f"Hi there, we have something special for you"
        elif formula_type == "social_proof":
            subject = f"Join 1,000+ {request.target_segment} who {request.objective}"
        else:
            subject = f"Tired of mediocre results? Try our solution"

        # Ensure subject line length (optimal: 41-50 characters)
        if len(subject) > 60:
            subject = subject[:57] + "..."
        elif len(subject) < 20:
            subject += f" - {request.objective.title()}"

        return subject

    def _generate_preheader(
        self, request: EmailCampaignRequest, subject_line: str
    ) -> str:
        """Generate preheader text."""
        # Preheader should complement subject line
        if request.campaign_type == "promotional":
            preheader = (
                f"Limited time offer for {request.target_segment}. Don't miss out!"
            )
        elif request.campaign_type == "newsletter":
            preheader = f"This week's top insights for {request.target_segment}. Click to learn more."
        elif request.campaign_type == "transactional":
            preheader = f"Important information about your recent activity."
        else:
            preheader = f"Personalized content for {request.target_segment}."

        # Ensure preheader length (optimal: 85-100 characters)
        if len(preheader) > 120:
            preheader = preheader[:117] + "..."

        return preheader

    def _generate_greeting(self, request: EmailCampaignRequest) -> str:
        """Generate greeting."""
        if request.personalization_level == "high":
            greeting = "Hi {first_name},"
        elif request.personalization_level == "medium":
            greeting = "Hello {first_name},"
        else:
            greeting = "Hello,"

        return greeting

    async def _generate_body_content(
        self, request: EmailCampaignRequest, template: Dict[str, Any], state: AgentState
    ) -> str:
        """Generate email body content."""
        # Build content generation prompt
        prompt = f"""
Create compelling email content with the following specifications:

CAMPAIGN TYPE: {request.campaign_type}
OBJECTIVE: {request.objective}
TARGET SEGMENT: {request.target_segment}
TONE: {request.tone}
PERSONALIZATION LEVEL: {request.personalization_level}
URGENCY: {request.urgency}
KEYWORDS: {", ".join(request.keywords)}

CONTENT STRUCTURE: {", ".join(template["content_structure"])}
PURPOSE: {template["purpose"]}

Create email content that:
- Follows the specified content structure
- Uses appropriate tone for {request.tone} communication
- Incorporates the keywords naturally
- Provides clear value to {request.target_segment}
- Includes relevant personalization tokens
- Drives the {request.objective} objective
- Maintains compliance with email regulations

The content should be engaging, valuable, and drive action. Use proper formatting with paragraphs and clear sections.
"""

        # Generate content
        content = await self.llm.generate(prompt)

        # Add personalization tokens if applicable
        if request.personalization_level != "low":
            content = self._add_personalization_tokens(
                content, request.personalization_level
            )

        return content

    def _add_personalization_tokens(self, content: str, level: str) -> str:
        """Add personalization tokens to content."""
        if level == "high":
            # Add multiple personalization tokens
            tokens = ["{first_name}", "{company}", "{industry}", "{recent_purchase}"]
        elif level == "medium":
            # Add basic personalization tokens
            tokens = ["{first_name}", "{company}"]
        else:
            # No personalization tokens
            return content

        # Replace generic placeholders with tokens
        for token in tokens:
            if "you" in content.lower():
                content = re.sub(r"\byou\b", token, content, flags=re.IGNORECASE)
            elif "your" in content.lower():
                content = re.sub(
                    r"\byour\b", token + "'s", content, flags=re.IGNORECASE
                )

        return content

    def _generate_call_to_action(self, request: EmailCampaignRequest) -> str:
        """Generate call to action."""
        cta_templates = {
            "conversion": [
                "Shop Now ΓåÆ",
                "Get Started Today",
                "Claim Your Offer",
                "Buy Now",
            ],
            "engagement": [
                "Learn More ΓåÆ",
                "Read Full Article",
                "Watch Video",
                "Explore More",
            ],
            "retention": [
                "Update Preferences",
                "Manage Account",
                "View Recommendations",
                "Check Your Status",
            ],
            "awareness": [
                "Discover More",
                "See How It Works",
                "Get Free Trial",
                "Learn About Us",
            ],
        }

        cta_options = cta_templates.get(request.objective, ["Learn More"])
        selected_cta = random.choice(cta_options)

        return f"{selected_cta}"

    def _generate_signature(self, state: AgentState) -> str:
        """Generate email signature."""
        company_name = state.get("company_name", "Your Company")

        signature = f"""
Best regards,
The {company_name} Team
"""

        return signature.strip()

    def _determine_personalization_tokens(
        self, request: EmailCampaignRequest
    ) -> List[str]:
        """Determine personalization tokens to use."""
        if request.personalization_level == "high":
            return [
                "{first_name}",
                "{last_name}",
                "{company}",
                "{industry}",
                "{location}",
            ]
        elif request.personalization_level == "medium":
            return ["{first_name}", "{company}"]
        else:
            return []

    def _calculate_spam_score(self, subject_line: str, body_content: str) -> float:
        """Calculate spam score."""
        spam_score = 0.0

        # Check for spam trigger words
        content_lower = (subject_line + " " + body_content).lower()

        for word, risk_level in self.spam_triggers.items():
            word_count = sum(
                1
                for trigger_word in self.spam_triggers[risk_level]
                if trigger_word in content_lower
            )

            if risk_level == "high_risk":
                spam_score += word_count * 0.3
            elif risk_level == "medium_risk":
                spam_score += word_count * 0.2
            else:
                spam_score += word_count * 0.1

        # Check for other spam indicators
        if subject_line.count("!") > 1:
            spam_score += 0.2

        if subject_line.isupper():
            spam_score += 0.3

        if len(subject_line) < 10:
            spam_score += 0.2

        # Check for excessive capitalization
        caps_ratio = (
            sum(1 for c in subject_line if c.isupper()) / len(subject_line)
            if subject_line
            else 0
        )
        if caps_ratio > 0.5:
            spam_score += 0.2

        return min(1.0, spam_score)

    def _calculate_engagement_prediction(
        self, request: EmailCampaignRequest, subject_line: str, body_content: str
    ) -> float:
        """Calculate engagement prediction."""
        base_engagement = 0.25  # Base engagement rate

        # Apply engagement factors
        engagement_score = base_engagement

        # Subject line factor
        subject_length = len(subject_line)
        if 40 <= subject_length <= 50:
            engagement_score *= 1.2  # Optimal length boost

        # Personalization factor
        personalization_multipliers = {"low": 1.0, "medium": 1.3, "high": 1.5}
        engagement_score *= personalization_multipliers.get(
            request.personalization_level, 1.0
        )

        # Urgency factor
        urgency_multipliers = {"normal": 1.0, "high": 1.2, "urgent": 1.3}
        engagement_score *= urgency_multipliers.get(request.urgency, 1.0)

        # Content length factor
        content_length = len(body_content)
        if 200 <= content_length <= 800:
            engagement_score *= 1.1  # Optimal content length

        # Spam score penalty
        spam_score = self._calculate_spam_score(subject_line, body_content)
        engagement_score *= 1 - spam_score

        return min(1.0, engagement_score)

    def _create_sending_strategy(
        self, request: EmailCampaignRequest, template: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create sending strategy."""
        optimal_times = template["optimal_send_times"]

        return {
            "optimal_send_times": optimal_times,
            "send_frequency": (
                "weekly" if request.campaign_type == "newsletter" else "triggered"
            ),
            "segmentation": request.target_segment,
            "personalization_level": request.personalization_level,
            "automation_triggers": self._get_automation_triggers(request.campaign_type),
            "list_cleaning": True,
            "a_b_testing": True,
            "performance_monitoring": True,
        }

    def _get_automation_triggers(self, campaign_type: str) -> List[str]:
        """Get automation triggers for campaign type."""
        triggers = {
            "newsletter": ["weekly_schedule"],
            "promotional": ["campaign_launch", "inventory_low"],
            "transactional": ["purchase", "signup", "password_reset"],
            "automation": ["welcome_series", "abandoned_cart", "re_engagement"],
        }

        return triggers.get(campaign_type, [])

    def _predict_performance(
        self,
        request: EmailCampaignRequest,
        content: EmailContent,
        template: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Predict campaign performance."""
        benchmarks = template["engagement_benchmarks"]

        # Adjust benchmarks based on content quality
        engagement_multiplier = (
            content.engagement_prediction / 0.25
        )  # Normalize to base

        return {
            "open_rate": benchmarks["open_rate"] * engagement_multiplier,
            "click_rate": benchmarks["click_rate"] * engagement_multiplier,
            "conversion_rate": benchmarks["conversion_rate"] * engagement_multiplier,
            "bounce_rate": 0.02,  # Typical bounce rate
            "unsubscribe_rate": 0.01,  # Typical unsubscribe rate
            "spam_complaint_rate": content.spam_score * 0.01,  # Based on spam score
            "overall_engagement": content.engagement_prediction,
            "roi_prediction": self._calculate_roi_prediction(request, benchmarks),
        }

    def _calculate_roi_prediction(
        self, request: EmailCampaignRequest, benchmarks: Dict[str, Any]
    ) -> float:
        """Calculate ROI prediction."""
        # Simplified ROI calculation
        if request.objective == "conversion":
            return 3.5  # High ROI for conversion campaigns
        elif request.objective == "engagement":
            return 2.0  # Medium ROI for engagement
        elif request.objective == "retention":
            return 4.0  # High ROI for retention
        else:
            return 1.5  # Lower ROI for awareness

    def _create_optimization_recommendations(
        self,
        request: EmailCampaignRequest,
        content: EmailContent,
        template: Dict[str, Any],
    ) -> List[str]:
        """Create optimization recommendations."""
        recommendations = []

        # Subject line recommendations
        if content.spam_score > 0.3:
            recommendations.append("Reduce spam triggers in subject line")

        if len(content.subject_line) < 20 or len(content.subject_line) > 60:
            recommendations.append("Optimize subject line length (40-50 characters)")

        # Personalization recommendations
        if request.personalization_level == "low":
            recommendations.append("Increase personalization to improve engagement")

        # Content recommendations
        if len(content.body_content) < 200:
            recommendations.append("Add more valuable content to increase engagement")

        # Timing recommendations
        recommendations.append(
            f"Test different send times: {', '.join(template['optimal_send_times'])}"
        )

        # General recommendations
        recommendations.extend(
            [
                "Monitor spam score and adjust content accordingly",
                "A/B test subject lines for better open rates",
                "Track engagement metrics and optimize based on performance",
            ]
        )

        return recommendations[:5]  # Limit to 5 recommendations

    def _create_ab_test_variants(
        self, request: EmailCampaignRequest, content: EmailContent
    ) -> List[Dict[str, Any]]:
        """Create A/B test variants."""
        variants = []

        # Subject line variants
        subject_variants = [
            f"Alternative: {content.subject_line}",
            f"Question: What if you could {request.objective}?",
            f"Urgent: Only 24 hours left!",
        ]

        for i, variant in enumerate(subject_variants[:2]):
            variants.append(
                {
                    "variant_id": f"subject_variant_{i+1}",
                    "test_type": "subject_line",
                    "variant": variant,
                    "confidence_level": 0.8,
                    "expected_improvement": 0.15,
                }
            )

        # CTA variants
        cta_variants = ["Shop Now ΓåÆ", "Get Started Today", "Learn More ΓåÆ"]

        for i, variant in enumerate(cta_variants[:1]):
            variants.append(
                {
                    "variant_id": f"cta_variant_{i+1}",
                    "test_type": "call_to_action",
                    "variant": variant,
                    "confidence_level": 0.7,
                    "expected_improvement": 0.10,
                }
            )

        return variants

    def _check_compliance(self, content: EmailContent) -> Dict[str, Any]:
        """Check email compliance."""
        compliance_status = {
            "can_spam": {
                "compliant": True,
                "issues": [],
                "required_elements": [
                    "physical_address",
                    "unsubscribe_link",
                    "clear_subject",
                ],
            },
            "gdpr": {
                "compliant": True,
                "issues": [],
                "required_elements": [
                    "explicit_consent",
                    "data_protection",
                    "right_to_withdraw",
                ],
            },
            "overall_score": 0.95,
        }

        # Check for compliance issues
        if content.spam_score > 0.5:
            compliance_status["can_spam"]["compliant"] = False
            compliance_status["can_spam"]["issues"].append("High spam score")
            compliance_status["overall_score"] -= 0.2

        if not content.unsubscribe_link:
            compliance_status["can_spam"]["compliant"] = False
            compliance_status["can_spam"]["issues"].append("Missing unsubscribe link")
            compliance_status["overall_score"] -= 0.3

        return compliance_status

    async def _store_email_campaign(self, campaign: EmailCampaign, state: AgentState):
        """Store email campaign in database."""
        try:
            # Store in database with workspace isolation
            database_tool = self._get_tool("database")
            if database_tool:
                await database_tool.arun(
                    table="email_campaigns",
                    workspace_id=state["workspace_id"],
                    data={
                        "campaign_id": campaign.campaign_id,
                        "campaign_name": campaign.campaign_name,
                        "campaign_type": campaign.campaign_type,
                        "objective": campaign.objective,
                        "target_segment": campaign.target_segment,
                        "content": campaign.content.__dict__,
                        "sending_strategy": campaign.sending_strategy,
                        "performance_prediction": campaign.performance_prediction,
                        "optimization_recommendations": campaign.optimization_recommendations,
                        "a_b_test_variants": campaign.a_b_test_variants,
                        "compliance_check": campaign.compliance_check,
                        "status": "created",
                        "created_at": campaign.created_at.isoformat(),
                        "metadata": campaign.metadata,
                    },
                )

        except Exception as e:
            logger.error(f"Failed to store email campaign: {e}")

    def _format_campaign_response(self, campaign: EmailCampaign) -> str:
        """Format email campaign response for user."""
        response = f"≡ƒôº **Email Campaign Created**\n\n"
        response += f"**Campaign Name:** {campaign.campaign_name}\n"
        response += f"**Campaign Type:** {campaign.campaign_type.title()}\n"
        response += f"**Objective:** {campaign.objective.title()}\n"
        response += f"**Target Segment:** {campaign.target_segment}\n"
        response += f"**Subject Line:** {campaign.content.subject_line}\n"
        response += f"**Engagement Prediction:** {campaign.performance_prediction['overall_engagement']:.1%}\n"
        response += f"**Spam Score:** {campaign.content.spam_score:.2f}/1.0\n"
        response += f"**Compliance Score:** {campaign.compliance_check['overall_score']:.1%}\n\n"

        response += f"**Preheader:** {campaign.content.preheader}\n\n"

        response += f"**Email Content:**\n"
        response += f"{campaign.content.greeting}\n\n"
        response += f"{campaign.content.body_content}\n\n"
        response += f"{campaign.content.call_to_action}\n\n"
        response += f"{campaign.content.signature}\n\n"

        if campaign.optimization_recommendations:
            response += f"**Optimization Recommendations:**\n"
            for recommendation in campaign.optimization_recommendations:
                response += f"ΓÇó {recommendation}\n"
            response += "\n"

        if campaign.a_b_test_variants:
            response += f"**A/B Test Variants:** {len(campaign.a_b_test_variants)} variants available\n\n"

        response += f"**Optimal Send Times:** {', '.join(campaign.sending_strategy['optimal_send_times'])}\n"

        return response
