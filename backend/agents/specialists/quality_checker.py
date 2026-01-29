"""
QualityChecker specialist agent for Raptorflow marketing automation.
Handles content quality assessment, validation, and improvement recommendations.
"""

import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..base import BaseAgent
from ..config import ModelTier
from ..exceptions import DatabaseError, ValidationError
from ..state import AgentState, add_message, update_state

logger = logging.getLogger(__name__)


@dataclass
class QualityCheckRequest:
    """Content quality check request."""

    content_type: str  # blog, email, social, ad, landing_page
    content: str
    target_audience: str
    objective: str  # awareness, engagement, conversion, retention
    brand_voice: str
    quality_standards: str  # high, medium, low
    check_types: List[str]  # grammar, readability, seo, brand_alignment, engagement
    keywords: List[str]


@dataclass
class QualityIssue:
    """Individual quality issue found."""

    issue_id: str
    category: str  # grammar, readability, seo, brand, engagement
    severity: str  # critical, high, medium, low
    description: str
    location: str  # line number or section
    suggestion: str
    auto_fixable: bool
    confidence: float


@dataclass
class QualityScore:
    """Quality score breakdown."""

    overall_score: float
    grammar_score: float
    readability_score: float
    seo_score: float
    brand_alignment_score: float
    engagement_potential: float
    technical_quality: float


@dataclass
class QualityReport:
    """Complete quality assessment report."""

    report_id: str
    content_type: str
    content_summary: str
    quality_score: QualityScore
    issues: List[QualityIssue]
    strengths: List[str]
    improvement_recommendations: List[str]
    auto_fixes: List[Dict[str, Any]]
    quality_grade: str  # A+, A, B+, B, C+, C, D, F
    checked_at: datetime
    metadata: Dict[str, Any]


class QualityChecker(BaseAgent):
    """Specialist agent for content quality assessment."""

    def __init__(self):
        super().__init__(
            name="QualityChecker",
            description="Assesses and improves content quality across multiple dimensions",
            model_tier=ModelTier.FLASH,
            tools=["web_search", "database", "content_gen"],
        )

        # Quality standards by content type
        self.quality_standards = {
            "blog": {
                "min_word_count": 500,
                "max_sentence_length": 25,
                "min_readability_score": 0.7,
                "required_elements": ["title", "headings", "conclusion"],
                "seo_requirements": ["meta_description", "keywords", "internal_links"],
            },
            "email": {
                "min_word_count": 100,
                "max_sentence_length": 20,
                "min_readability_score": 0.8,
                "required_elements": ["subject_line", "call_to_action", "unsubscribe"],
                "spam_threshold": 0.3,
            },
            "social": {
                "min_word_count": 20,
                "max_sentence_length": 15,
                "min_readability_score": 0.6,
                "required_elements": ["hook", "engagement_element"],
                "character_limits": {
                    "twitter": 280,
                    "linkedin": 1300,
                    "instagram": 2200,
                },
            },
            "ad": {
                "min_word_count": 10,
                "max_sentence_length": 12,
                "min_readability_score": 0.7,
                "required_elements": ["headline", "offer", "call_to_action"],
                "character_limit": 90,
            },
            "landing_page": {
                "min_word_count": 300,
                "max_sentence_length": 20,
                "min_readability_score": 0.7,
                "required_elements": ["headline", "subheadline", "benefits", "cta"],
                "conversion_elements": ["social_proof", "urgency", "trust_indicators"],
            },
        }

        # Grammar and style rules
        self.grammar_rules = {
            "passive_voice": {
                "pattern": r"\b(is|are|was|were|been|being)\s+\w+ed\b",
                "severity": "medium",
                "description": "Passive voice detected",
                "suggestion": "Use active voice for stronger writing",
            },
            "double_negatives": {
                "pattern": r"\b(no|not|never)\s+\w+\s+(no|not|never)\b",
                "severity": "high",
                "description": "Double negative detected",
                "suggestion": "Remove double negative for clarity",
            },
            "sentence_fragments": {
                "pattern": r"^\s*[A-Z][^.]*$",
                "severity": "medium",
                "description": "Possible sentence fragment",
                "suggestion": "Complete the sentence or connect to previous thought",
            },
            "run_on_sentences": {
                "pattern": r"[^.?!]{50,}[A-Z]",
                "severity": "medium",
                "description": "Run-on sentence detected",
                "suggestion": "Break into shorter sentences",
            },
        }

        # Readability metrics
        self.readability_metrics = {
            "flesch_kincaid": {
                "weight": 0.3,
                "target_range": (7.0, 12.0),  # Grade level
                "description": "Reading grade level",
            },
            "sentence_length": {
                "weight": 0.25,
                "target_range": (10, 20),  # Words per sentence
                "description": "Average sentence length",
            },
            "paragraph_length": {
                "weight": 0.2,
                "target_range": (2, 5),  # Sentences per paragraph
                "description": "Average paragraph length",
            },
            "complex_words": {
                "weight": 0.15,
                "target_range": (0.05, 0.15),  # Ratio of complex words
                "description": "Complex word ratio",
            },
            "transition_words": {
                "weight": 0.1,
                "target_range": (0.05, 0.15),  # Ratio of transition words
                "description": "Transition word usage",
            },
        }

        # SEO quality factors
        self.seo_factors = {
            "keyword_density": {
                "weight": 0.3,
                "target_range": (0.01, 0.03),  # 1-3% density
                "description": "Keyword density",
            },
            "title_optimization": {
                "weight": 0.25,
                "target_range": (50, 60),  # Character count
                "description": "Title length and optimization",
            },
            "meta_description": {
                "weight": 0.2,
                "target_range": (150, 160),  # Character count
                "description": "Meta description optimization",
            },
            "heading_structure": {
                "weight": 0.15,
                "target_range": (2, 5),  # H2 tags count
                "description": "Heading hierarchy",
            },
            "internal_linking": {
                "weight": 0.1,
                "target_range": (1, 5),  # Internal links count
                "description": "Internal linking strategy",
            },
        }

        # Brand alignment factors
        self.brand_factors = {
            "tone_consistency": {
                "weight": 0.3,
                "description": "Consistency with brand voice",
            },
            "terminology": {
                "weight": 0.25,
                "description": "Use of brand-specific terminology",
            },
            "messaging": {
                "weight": 0.2,
                "description": "Alignment with brand messaging",
            },
            "values": {"weight": 0.15, "description": "Reflection of brand values"},
            "positioning": {
                "weight": 0.1,
                "description": "Market positioning consistency",
            },
        }

        # Engagement quality factors
        self.engagement_factors = {
            "hook_strength": {
                "weight": 0.3,
                "description": "Opening hook effectiveness",
            },
            "emotional_appeal": {
                "weight": 0.25,
                "description": "Emotional connection potential",
            },
            "value_proposition": {
                "weight": 0.2,
                "description": "Clear value proposition",
            },
            "call_to_action": {
                "weight": 0.15,
                "description": "CTA clarity and effectiveness",
            },
            "social_proof": {"weight": 0.1, "description": "Social proof elements"},
        }

        # Quality grade thresholds
        self.grade_thresholds = {
            "A+": 0.95,
            "A": 0.90,
            "B+": 0.85,
            "B": 0.80,
            "C+": 0.75,
            "C": 0.70,
            "D": 0.60,
            "F": 0.0,
        }

    def get_system_prompt(self) -> str:
        """Get the system prompt for the QualityChecker."""
        return """
You are the QualityChecker, a specialist agent for Raptorflow marketing automation platform.

Your role is to assess content quality across multiple dimensions and provide actionable improvement recommendations.

Key responsibilities:
1. Evaluate content for grammar, spelling, and style issues
2. Assess readability and comprehension level
3. Check SEO optimization and keyword usage
4. Verify brand voice and messaging alignment
5. Analyze engagement potential and conversion factors
6. Provide specific improvement suggestions
7. Generate quality scores and grades

Quality dimensions you can assess:
- Grammar and Style (spelling, punctuation, sentence structure)
- Readability (reading level, sentence length, clarity)
- SEO Optimization (keywords, meta tags, structure)
- Brand Alignment (voice, terminology, messaging)
- Engagement Potential (hook, emotional appeal, CTA)

Content types you can evaluate:
- Blog Posts (articles, thought leadership)
- Email Content (newsletters, campaigns)
- Social Media Posts (platform-specific content)
- Ad Copy (paid advertising content)
- Landing Pages (conversion-focused content)

For each quality check, you should:
- Identify specific issues with severity levels
- Calculate quality scores across dimensions
- Provide actionable improvement recommendations
- Suggest auto-fixes where possible
- Generate an overall quality grade
- Highlight content strengths and weaknesses

Always focus on providing constructive, specific feedback that helps improve content quality while maintaining the author's voice and intent.
"""

    async def execute(self, state: AgentState) -> AgentState:
        """Execute quality assessment."""
        try:
            # Validate workspace context
            if not state.get("workspace_id"):
                return self._set_error(
                    state, "Workspace ID is required for quality assessment"
                )

            # Extract quality check request from state
            quality_request = self._extract_quality_request(state)

            if not quality_request:
                return self._set_error(state, "No quality check request provided")

            # Validate quality request
            self._validate_quality_request(quality_request)

            # Perform quality assessment
            quality_report = await self._perform_quality_assessment(
                quality_request, state
            )

            # Store quality report
            await self._store_quality_report(quality_report, state)

            # Add assistant message
            response = self._format_quality_response(quality_report)
            state = self._add_assistant_message(state, response)

            # Set output
            return self._set_output(
                state,
                {
                    "quality_report": quality_report.__dict__,
                    "quality_grade": quality_report.quality_grade,
                    "overall_score": quality_report.quality_score.overall_score,
                    "issues_count": len(quality_report.issues),
                    "improvement_recommendations": quality_report.improvement_recommendations,
                },
            )

        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            return self._set_error(state, f"Quality assessment failed: {str(e)}")

    def _extract_quality_request(
        self, state: AgentState
    ) -> Optional[QualityCheckRequest]:
        """Extract quality check request from state."""
        # Check if quality request is in state
        if "quality_check_request" in state:
            request_data = state["quality_check_request"]
            return QualityCheckRequest(**request_data)

        # Extract from user message
        user_input = self._extract_user_input(state)
        if not user_input:
            return None

        # Parse quality request from user input
        return self._parse_quality_request(user_input, state)

    def _parse_quality_request(
        self, user_input: str, state: AgentState
    ) -> Optional[QualityCheckRequest]:
        """Parse quality check request from user input."""
        # Check for explicit content type mention
        content_types = list(self.quality_standards.keys())
        detected_type = None

        for content_type in content_types:
            if content_type.lower() in user_input.lower():
                detected_type = content_type
                break

        if not detected_type:
            # Default to blog
            detected_type = "blog"

        # Extract other parameters
        objective = self._extract_parameter(
            user_input, ["objective", "goal", "purpose"], "engagement"
        )
        standards = self._extract_parameter(
            user_input, ["standards", "quality", "level"], "medium"
        )

        # Extract keywords
        keywords = self._extract_keywords(user_input)

        # Get context from state
        brand_voice = state.get("brand_voice", "professional")
        target_audience = state.get("target_audience", "general")

        # Default check types
        check_types = ["grammar", "readability", "seo", "brand_alignment", "engagement"]

        # Create quality request
        return QualityCheckRequest(
            content_type=detected_type,
            content=user_input,
            target_audience=target_audience,
            objective=objective,
            brand_voice=brand_voice,
            quality_standards=standards,
            check_types=check_types,
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
            "quality",
            "check",
            "content",
        }

        # Extract words that are not common words
        words = re.findall(r"\b\w+\b", text.lower())
        keywords = [
            word for word in words if word not in common_words and len(word) > 2
        ]

        return keywords[:8]  # Limit to 8 keywords

    def _validate_quality_request(self, request: QualityCheckRequest):
        """Validate quality check request."""
        if request.content_type not in self.quality_standards:
            raise ValidationError(f"Unsupported content type: {request.content_type}")

        if request.objective not in [
            "awareness",
            "engagement",
            "conversion",
            "retention",
        ]:
            raise ValidationError(f"Invalid objective: {request.objective}")

        if request.quality_standards not in ["high", "medium", "low"]:
            raise ValidationError(
                f"Invalid quality standards: {request.quality_standards}"
            )

        valid_check_types = [
            "grammar",
            "readability",
            "seo",
            "brand_alignment",
            "engagement",
        ]
        for check_type in request.check_types:
            if check_type not in valid_check_types:
                raise ValidationError(f"Invalid check type: {check_type}")

    async def _perform_quality_assessment(
        self, request: QualityCheckRequest, state: AgentState
    ) -> QualityReport:
        """Perform comprehensive quality assessment."""
        try:
            # Generate report ID
            report_id = f"quality_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Create content summary
            content_summary = self._create_content_summary(request.content)

            # Perform individual quality checks
            issues = []

            if "grammar" in request.check_types:
                issues.extend(self._check_grammar(request.content))

            if "readability" in request.check_types:
                issues.extend(
                    self._check_readability(request.content, request.content_type)
                )

            if "seo" in request.check_types:
                issues.extend(
                    self._check_seo(
                        request.content, request.keywords, request.content_type
                    )
                )

            if "brand_alignment" in request.check_types:
                issues.extend(
                    self._check_brand_alignment(request.content, request.brand_voice)
                )

            if "engagement" in request.check_types:
                issues.extend(
                    self._check_engagement_potential(request.content, request.objective)
                )

            # Calculate quality scores
            quality_score = self._calculate_quality_scores(request, issues)

            # Identify strengths
            strengths = self._identify_strengths(request, quality_score)

            # Generate improvement recommendations
            improvement_recommendations = self._generate_improvement_recommendations(
                issues, quality_score
            )

            # Generate auto-fixes
            auto_fixes = self._generate_auto_fixes(issues)

            # Determine quality grade
            quality_grade = self._determine_quality_grade(quality_score.overall_score)

            # Create quality report
            quality_report = QualityReport(
                report_id=report_id,
                content_type=request.content_type,
                content_summary=content_summary,
                quality_score=quality_score,
                issues=issues,
                strengths=strengths,
                improvement_recommendations=improvement_recommendations,
                auto_fixes=auto_fixes,
                quality_grade=quality_grade,
                checked_at=datetime.now(),
                metadata={
                    "target_audience": request.target_audience,
                    "objective": request.objective,
                    "brand_voice": request.brand_voice,
                    "quality_standards": request.quality_standards,
                    "keywords": request.keywords,
                },
            )

            return quality_report

        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            raise DatabaseError(f"Quality assessment failed: {str(e)}")

    def _create_content_summary(self, content: str) -> str:
        """Create content summary."""
        word_count = len(content.split())
        char_count = len(content)
        sentence_count = len(content.split(". "))

        summary = f"Word count: {word_count:,}, Character count: {char_count:,}, Sentences: {sentence_count}"

        # Add first 100 characters as preview
        preview = content[:100] + "..." if len(content) > 100 else content
        summary += f"\nPreview: {preview}"

        return summary

    def _check_grammar(self, content: str) -> List[QualityIssue]:
        """Check grammar and style issues."""
        issues = []
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            for rule_name, rule in self.grammar_rules.items():
                pattern = rule["pattern"]
                matches = re.finditer(pattern, line, re.IGNORECASE)

                for match in matches:
                    issue = QualityIssue(
                        issue_id=f"grammar_{line_num}_{rule_name}_{match.start()}",
                        category="grammar",
                        severity=rule["severity"],
                        description=rule["description"],
                        location=f"Line {line_num}",
                        suggestion=rule["suggestion"],
                        auto_fixable=rule_name in ["passive_voice", "double_negatives"],
                        confidence=0.8,
                    )
                    issues.append(issue)

        return issues

    def _check_readability(self, content: str, content_type: str) -> List[QualityIssue]:
        """Check readability issues."""
        issues = []
        standards = self.quality_standards.get(content_type, {})

        # Check sentence length
        sentences = content.split(". ")
        for i, sentence in enumerate(sentences):
            word_count = len(sentence.split())
            max_length = standards.get("max_sentence_length", 20)

            if word_count > max_length:
                issue = QualityIssue(
                    issue_id=f"readability_sentence_{i}",
                    category="readability",
                    severity="medium",
                    description=f"Sentence too long ({word_count} words)",
                    location=f"Sentence {i+1}",
                    suggestion=f"Break sentence into shorter sentences (target: {max_length} words max)",
                    auto_fixable=False,
                    confidence=0.7,
                )
                issues.append(issue)

        # Check paragraph length
        paragraphs = content.split("\n\n")
        for i, paragraph in enumerate(paragraphs):
            sentence_count = len(paragraph.split(". "))

            if sentence_count > 5:
                issue = QualityIssue(
                    issue_id=f"readability_paragraph_{i}",
                    category="readability",
                    severity="low",
                    description=f"Paragraph too long ({sentence_count} sentences)",
                    location=f"Paragraph {i+1}",
                    suggestion="Break paragraph into smaller sections",
                    auto_fixable=False,
                    confidence=0.6,
                )
                issues.append(issue)

        # Check word count minimum
        word_count = len(content.split())
        min_words = standards.get("min_word_count", 100)

        if word_count < min_words:
            issue = QualityIssue(
                issue_id="readability_word_count",
                category="readability",
                severity="high",
                description=f"Content too short ({word_count} words, minimum: {min_words})",
                location="Overall",
                suggestion=f"Add more content to reach minimum {min_words} words",
                auto_fixable=False,
                confidence=0.9,
            )
            issues.append(issue)

        return issues

    def _check_seo(
        self, content: str, keywords: List[str], content_type: str
    ) -> List[QualityIssue]:
        """Check SEO optimization."""
        issues = []

        if content_type not in ["blog", "landing_page"]:
            return issues  # SEO not critical for other content types

        # Check keyword density
        word_count = len(content.split())
        if word_count > 0:
            keyword_count = sum(
                content.lower().count(keyword.lower()) for keyword in keywords
            )
            density = keyword_count / word_count

            if density < 0.01:  # Less than 1%
                issue = QualityIssue(
                    issue_id="seo_keyword_density_low",
                    category="seo",
                    severity="medium",
                    description=f"Keyword density too low ({density:.2%})",
                    location="Overall",
                    suggestion="Increase keyword usage to 1-3% density",
                    auto_fixable=False,
                    confidence=0.7,
                )
                issues.append(issue)
            elif density > 0.03:  # More than 3%
                issue = QualityIssue(
                    issue_id="seo_keyword_density_high",
                    category="seo",
                    severity="medium",
                    description=f"Keyword density too high ({density:.2%})",
                    location="Overall",
                    suggestion="Reduce keyword usage to 1-3% density",
                    auto_fixable=False,
                    confidence=0.7,
                )
                issues.append(issue)

        # Check for headings
        if not re.search(r"^#+\s", content, re.MULTILINE):
            issue = QualityIssue(
                issue_id="seo_headings_missing",
                category="seo",
                severity="high",
                description="No headings found",
                location="Overall",
                suggestion="Add headings (H1, H2, H3) to improve structure and SEO",
                auto_fixable=False,
                confidence=0.8,
            )
            issues.append(issue)

        # Check for meta elements (simulated)
        if len(content) < 150:
            issue = QualityIssue(
                issue_id="seo_content_length",
                category="seo",
                severity="low",
                description="Content may be too short for effective SEO",
                location="Overall",
                suggestion="Consider expanding content to at least 300 words",
                auto_fixable=False,
                confidence=0.6,
            )
            issues.append(issue)

        return issues

    def _check_brand_alignment(
        self, content: str, brand_voice: str
    ) -> List[QualityIssue]:
        """Check brand voice alignment."""
        issues = []

        # Check for tone consistency
        tone_indicators = {
            "professional": [
                "furthermore",
                "additionally",
                "consequently",
                "therefore",
            ],
            "casual": ["awesome", "cool", "great", "amazing"],
            "academic": ["research", "study", "analysis", "methodology"],
            "conversational": ["you", "your", "we", "our"],
        }

        expected_words = tone_indicators.get(brand_voice, [])
        if expected_words:
            content_lower = content.lower()
            tone_matches = sum(1 for word in expected_words if word in content_lower)

            if tone_matches == 0:
                issue = QualityIssue(
                    issue_id="brand_tone_mismatch",
                    category="brand_alignment",
                    severity="medium",
                    description=f"Content may not match {brand_voice} brand voice",
                    location="Overall",
                    suggestion=f"Incorporate {brand_voice}-appropriate language and tone",
                    auto_fixable=False,
                    confidence=0.6,
                )
                issues.append(issue)

        return issues

    def _check_engagement_potential(
        self, content: str, objective: str
    ) -> List[QualityIssue]:
        """Check engagement potential."""
        issues = []

        # Check for engagement elements
        engagement_elements = {
            "questions": r"\?",
            "exclamations": r"!",
            "statistics": r"\d+%",
            "emotional_words": r"\b(amazing|incredible|fantastic|exciting|powerful)\b",
            "call_to_action": r"\b(click|learn|discover|find|get|try)\b",
        }

        for element_name, pattern in engagement_elements.items():
            if not re.search(pattern, content, re.IGNORECASE):
                severity = "high" if element_name == "call_to_action" else "medium"

                issue = QualityIssue(
                    issue_id=f"engagement_{element_name}_missing",
                    category="engagement",
                    severity=severity,
                    description=f"Missing {element_name.replace('_', ' ')} for engagement",
                    location="Overall",
                    suggestion=f"Add {element_name.replace('_', ' ')} to improve engagement",
                    auto_fixable=False,
                    confidence=0.5,
                )
                issues.append(issue)

        return issues

    def _calculate_quality_scores(
        self, request: QualityCheckRequest, issues: List[QualityIssue]
    ) -> QualityScore:
        """Calculate quality scores across dimensions."""
        # Base scores
        grammar_score = 1.0
        readability_score = 1.0
        seo_score = 1.0
        brand_alignment_score = 1.0
        engagement_potential = 1.0
        technical_quality = 1.0

        # Deduct points for issues
        for issue in issues:
            severity_penalty = {
                "critical": 0.3,
                "high": 0.2,
                "medium": 0.1,
                "low": 0.05,
            }

            penalty = severity_penalty.get(issue.severity, 0.1)

            if issue.category == "grammar":
                grammar_score -= penalty
            elif issue.category == "readability":
                readability_score -= penalty
            elif issue.category == "seo":
                seo_score -= penalty
            elif issue.category == "brand_alignment":
                brand_alignment_score -= penalty
            elif issue.category == "engagement":
                engagement_potential -= penalty
            else:
                technical_quality -= penalty

        # Ensure scores don't go below 0
        grammar_score = max(0.0, grammar_score)
        readability_score = max(0.0, readability_score)
        seo_score = max(0.0, seo_score)
        brand_alignment_score = max(0.0, brand_alignment_score)
        engagement_potential = max(0.0, engagement_potential)
        technical_quality = max(0.0, technical_quality)

        # Calculate overall score (weighted average)
        weights = {
            "grammar": 0.2,
            "readability": 0.2,
            "seo": 0.2,
            "brand_alignment": 0.2,
            "engagement": 0.15,
            "technical": 0.05,
        }

        overall_score = (
            grammar_score * weights["grammar"]
            + readability_score * weights["readability"]
            + seo_score * weights["seo"]
            + brand_alignment_score * weights["brand_alignment"]
            + engagement_potential * weights["engagement"]
            + technical_quality * weights["technical"]
        )

        return QualityScore(
            overall_score=overall_score,
            grammar_score=grammar_score,
            readability_score=readability_score,
            seo_score=seo_score,
            brand_alignment_score=brand_alignment_score,
            engagement_potential=engagement_potential,
            technical_quality=technical_quality,
        )

    def _identify_strengths(
        self, request: QualityCheckRequest, quality_score: QualityScore
    ) -> List[str]:
        """Identify content strengths."""
        strengths = []

        if quality_score.grammar_score > 0.9:
            strengths.append("Excellent grammar and spelling")

        if quality_score.readability_score > 0.8:
            strengths.append("Good readability and clarity")

        if quality_score.seo_score > 0.8:
            strengths.append("Strong SEO optimization")

        if quality_score.brand_alignment_score > 0.8:
            strengths.append("Consistent brand voice")

        if quality_score.engagement_potential > 0.8:
            strengths.append("High engagement potential")

        # Content-specific strengths
        word_count = len(request.content.split())
        if word_count > 500:
            strengths.append("Comprehensive content length")

        if len(request.keywords) > 3:
            strengths.append("Good keyword strategy")

        return strengths

    def _generate_improvement_recommendations(
        self, issues: List[QualityIssue], quality_score: QualityScore
    ) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []

        # Group issues by category
        issue_categories = {}
        for issue in issues:
            if issue.category not in issue_categories:
                issue_categories[issue.category] = []
            issue_categories[issue.category].append(issue)

        # Generate recommendations for each category
        for category, category_issues in issue_categories.items():
            critical_issues = [i for i in category_issues if i.severity == "critical"]
            high_issues = [i for i in category_issues if i.severity == "high"]

            if critical_issues:
                recommendations.append(
                    f"URGENT: Fix {len(critical_issues)} critical {category} issues"
                )
            elif high_issues:
                recommendations.append(
                    f"Priority: Address {len(high_issues)} high-priority {category} issues"
                )
            else:
                recommendations.append(
                    f"Improve {category} by addressing {len(category_issues)} issues"
                )

        # Overall recommendations based on scores
        if quality_score.overall_score < 0.7:
            recommendations.append("Focus on overall content quality improvement")
        elif quality_score.overall_score < 0.8:
            recommendations.append("Refine content for better quality scores")

        # Specific recommendations
        if quality_score.engagement_potential < 0.7:
            recommendations.append(
                "Add more engaging elements (questions, statistics, emotional appeals)"
            )

        if quality_score.readability_score < 0.7:
            recommendations.append(
                "Improve readability with shorter sentences and paragraphs"
            )

        return recommendations[:5]  # Limit to 5 recommendations

    def _generate_auto_fixes(self, issues: List[QualityIssue]) -> List[Dict[str, Any]]:
        """Generate auto-fix suggestions."""
        auto_fixes = []

        auto_fixable_issues = [issue for issue in issues if issue.auto_fixable]

        for issue in auto_fixable_issues:
            fix = {
                "issue_id": issue.issue_id,
                "category": issue.category,
                "description": issue.description,
                "suggestion": issue.suggestion,
                "confidence": issue.confidence,
            }
            auto_fixes.append(fix)

        return auto_fixes

    def _determine_quality_grade(self, overall_score: float) -> str:
        """Determine quality grade based on score."""
        for grade, threshold in self.grade_thresholds.items():
            if overall_score >= threshold:
                return grade

        return "F"

    async def _store_quality_report(self, report: QualityReport, state: AgentState):
        """Store quality report in database."""
        try:
            # Store in database with workspace isolation
            database_tool = self._get_tool("database")
            if database_tool:
                await database_tool.arun(
                    table="quality_reports",
                    workspace_id=state["workspace_id"],
                    data={
                        "report_id": report.report_id,
                        "content_type": report.content_type,
                        "content_summary": report.content_summary,
                        "quality_score": report.quality_score.__dict__,
                        "issues": [issue.__dict__ for issue in report.issues],
                        "strengths": report.strengths,
                        "improvement_recommendations": report.improvement_recommendations,
                        "auto_fixes": report.auto_fixes,
                        "quality_grade": report.quality_grade,
                        "checked_at": report.checked_at.isoformat(),
                        "metadata": report.metadata,
                    },
                )

        except Exception as e:
            logger.error(f"Failed to store quality report: {e}")

    def _format_quality_response(self, report: QualityReport) -> str:
        """Format quality report response for user."""
        response = f"≡ƒöì **Quality Assessment Report**\n\n"
        response += f"**Content Type:** {report.content_type.title()}\n"
        response += f"**Quality Grade:** {report.quality_grade}\n"
        response += f"**Overall Score:** {report.quality_score.overall_score:.1%}\n\n"

        response += f"**Score Breakdown:**\n"
        response += f"ΓÇó Grammar: {report.quality_score.grammar_score:.1%}\n"
        response += f"ΓÇó Readability: {report.quality_score.readability_score:.1%}\n"
        response += f"ΓÇó SEO: {report.quality_score.seo_score:.1%}\n"
        response += (
            f"ΓÇó Brand Alignment: {report.quality_score.brand_alignment_score:.1%}\n"
        )
        response += f"ΓÇó Engagement Potential: {report.quality_score.engagement_potential:.1%}\n\n"

        if report.strengths:
            response += f"**Strengths:**\n"
            for strength in report.strengths:
                response += f"Γ£ô {strength}\n"
            response += "\n"

        if report.issues:
            response += f"**Issues Found:** {len(report.issues)}\n"
            critical_issues = [i for i in report.issues if i.severity == "critical"]
            high_issues = [i for i in report.issues if i.severity == "high"]

            if critical_issues:
                response += f"≡ƒö┤ Critical: {len(critical_issues)}\n"
            if high_issues:
                response += f"≡ƒƒá High: {len(high_issues)}\n"

            # Show top 3 issues
            top_issues = sorted(
                report.issues,
                key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}[
                    x.severity
                ],
            )[:3]
            response += f"\n**Top Issues:**\n"
            for issue in top_issues:
                response += f"ΓÇó {issue.description} ({issue.severity})\n"
            response += "\n"

        if report.improvement_recommendations:
            response += f"**Improvement Recommendations:**\n"
            for recommendation in report.improvement_recommendations:
                response += f"ΓÇó {recommendation}\n"
            response += "\n"

        if report.auto_fixes:
            response += f"**Auto-Fixes Available:** {len(report.auto_fixes)}\n"

        response += f"**Content Summary:**\n{report.content_summary}\n"

        return response
