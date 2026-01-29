"""
RevisionAgent specialist agent for Raptorflow marketing automation.
Handles content revision, optimization, and iterative improvement.
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
class RevisionRequest:
    """Content revision request."""

    original_content: str
    content_type: str  # blog, email, social, ad, landing_page
    revision_type: str  # grammar, style, seo, engagement, comprehensive
    target_audience: str
    objective: str  # awareness, engagement, conversion, retention
    brand_voice: str
    feedback: List[str]  # Specific feedback or issues to address
    constraints: Dict[str, Any]  # Length, tone, format constraints
    keywords: List[str]


@dataclass
class RevisionChange:
    """Individual revision change made."""

    change_id: str
    type: str  # addition, deletion, modification, restructure
    location: str  # Description of where change was made
    original_text: str
    revised_text: str
    reason: str  # Why the change was made
    impact: str  # Expected impact of the change
    confidence: float


@dataclass
class RevisionMetrics:
    """Revision performance metrics."""

    original_score: float
    revised_score: float
    improvement_percentage: float
    grammar_improvement: float
    readability_improvement: float
    seo_improvement: float
    engagement_improvement: float


@dataclass
class RevisionResult:
    """Complete revision result."""

    revision_id: str
    original_content: str
    revised_content: str
    changes: List[RevisionChange]
    metrics: RevisionMetrics
    revision_summary: str
    next_steps: List[str]
    revision_count: int
    revised_at: datetime
    metadata: Dict[str, Any]


class RevisionAgent(BaseAgent):
    """Specialist agent for content revision and optimization."""

    def __init__(self):
        super().__init__(
            name="RevisionAgent",
            description="Revises and optimizes content for better performance and quality",
            model_tier=ModelTier.FLASH,
            tools=["web_search", "database", "content_gen"],
        )

        # Revision strategies by type
        self.revision_strategies = {
            "grammar": {
                "focus": "correcting errors and improving clarity",
                "techniques": [
                    "spelling_correction",
                    "grammar_fixes",
                    "punctuation",
                    "sentence_structure",
                ],
                "priority": "high",
            },
            "style": {
                "focus": "improving tone, flow, and readability",
                "techniques": [
                    "voice_consistency",
                    "sentence_variety",
                    "word_choice",
                    "transitions",
                ],
                "priority": "medium",
            },
            "seo": {
                "focus": "optimizing for search engines",
                "techniques": [
                    "keyword_optimization",
                    "meta_tags",
                    "headings",
                    "internal_linking",
                ],
                "priority": "medium",
            },
            "engagement": {
                "focus": "increasing reader engagement",
                "techniques": [
                    "hook_improvement",
                    "emotional_appeal",
                    "cta_optimization",
                    "social_proof",
                ],
                "priority": "high",
            },
            "comprehensive": {
                "focus": "holistic content improvement",
                "techniques": ["grammar", "style", "seo", "engagement", "structure"],
                "priority": "high",
            },
        }

        # Content type specific revision rules
        self.content_revision_rules = {
            "blog": {
                "max_paragraph_length": 5,  # sentences
                "min_word_count": 500,
                "required_elements": ["title", "introduction", "body", "conclusion"],
                "seo_priority": "high",
                "engagement_elements": ["questions", "statistics", "examples"],
            },
            "email": {
                "max_sentence_length": 15,
                "min_word_count": 100,
                "required_elements": ["subject", "body", "cta", "unsubscribe"],
                "spam_prevention": "high",
                "personalization": "medium",
            },
            "social": {
                "max_character_count": 280,  # Twitter standard
                "min_word_count": 10,
                "required_elements": ["hook", "message", "hashtag"],
                "engagement_priority": "high",
                "visual_consideration": "medium",
            },
            "ad": {
                "max_character_count": 90,
                "min_word_count": 5,
                "required_elements": ["headline", "offer", "cta"],
                "conversion_focus": "high",
                "urgency_elements": "medium",
            },
            "landing_page": {
                "max_paragraph_length": 4,
                "min_word_count": 300,
                "required_elements": [
                    "headline",
                    "subheadline",
                    "benefits",
                    "cta",
                    "social_proof",
                ],
                "conversion_priority": "high",
                "trust_elements": "high",
            },
        }

        # Common revision patterns
        self.revision_patterns = {
            "passive_to_active": {
                "pattern": r"\b(is|are|was|were|been|being)\s+(\w+ed)\b",
                "replacement": lambda m: f"{m.group(2).capitalize()} {m.group(1)}",
                "reason": "Convert passive voice to active voice for stronger writing",
            },
            "double_negatives": {
                "pattern": r"\b(no|not|never)\s+\w+\s+(no|not|never)\b",
                "replacement": lambda m: re.sub(
                    r"\b(no|not|never)\b", "", m.group(0), count=1
                ),
                "reason": "Remove double negatives for clarity",
            },
            "wordy_phrases": {
                "pattern": r"\b(in order to|due to the fact that|at this point in time)\b",
                "replacement": lambda m: {
                    "in order to": "to",
                    "due to the fact that": "because",
                    "at this point in time": "now",
                }[m.group(0)],
                "reason": "Replace wordy phrases with concise alternatives",
            },
            "redundant_words": {
                "pattern": r"\b(very|really|quite|rather|absolutely)\s+(\w+)\b",
                "replacement": lambda m: f"{m.group(2)}",
                "reason": "Remove redundant intensifiers",
            },
        }

        # Engagement enhancement patterns
        self.engagement_patterns = {
            "add_questions": {
                "insertion_points": ["after_introduction", "before_conclusion"],
                "templates": [
                    "Have you ever wondered...?",
                    "What if you could...?",
                    "Did you know that...?",
                ],
                "reason": "Add rhetorical questions to engage readers",
            },
            "add_statistics": {
                "insertion_points": ["supporting_points", "benefit_statements"],
                "templates": [
                    "{percentage}% of users report...",
                    "Studies show that {number} out of {total}...",
                ],
                "reason": "Add statistics for credibility",
            },
            "add_emotional_words": {
                "insertion_points": ["throughout_content"],
                "templates": [
                    "amazing",
                    "incredible",
                    "powerful",
                    "transformative",
                    "life-changing",
                ],
                "reason": "Add emotional language for connection",
            },
        }

        # SEO optimization patterns
        self.seo_patterns = {
            "keyword_placement": {
                "positions": ["title", "first_paragraph", "headings", "conclusion"],
                "density_target": 0.02,  # 2% keyword density
                "reason": "Optimize keyword placement for SEO",
            },
            "heading_optimization": {
                "structure": ["H1", "H2", "H3"],
                "max_h2_count": 5,
                "reason": "Optimize heading structure for SEO and readability",
            },
            "meta_optimization": {
                "title_length": (50, 60),
                "description_length": (150, 160),
                "reason": "Optimize meta tags for search results",
            },
        }

    def get_system_prompt(self) -> str:
        """Get the system prompt for the RevisionAgent."""
        return """
You are the RevisionAgent, a specialist agent for Raptorflow marketing automation platform.

Your role is to revise and optimize content to improve quality, performance, and effectiveness across multiple dimensions.

Key responsibilities:
1. Analyze content for improvement opportunities
2. Apply targeted revision strategies based on content type and objectives
3. Fix grammar, spelling, and style issues
4. Optimize content for SEO and engagement
5. Maintain brand voice and messaging consistency
6. Track and measure revision improvements
7. Provide clear explanations of changes made

Revision types you can perform:
- Grammar Revision (correcting errors and improving clarity)
- Style Revision (improving tone, flow, and readability)
- SEO Revision (optimizing for search engines)
- Engagement Revision (increasing reader engagement)
- Comprehensive Revision (holistic content improvement)

Content types you can revise:
- Blog Posts (articles, thought leadership)
- Email Content (newsletters, campaigns)
- Social Media Posts (platform-specific content)
- Ad Copy (paid advertising content)
- Landing Pages (conversion-focused content)

For each revision, you should:
- Analyze the original content for issues and opportunities
- Apply appropriate revision techniques and strategies
- Make specific, targeted improvements
- Track all changes made with explanations
- Measure improvement in quality metrics
- Maintain the original intent and brand voice
- Provide next steps for further optimization

Always focus on making meaningful improvements that enhance content effectiveness while preserving the author's voice and message.
"""

    async def execute(self, state: AgentState) -> AgentState:
        """Execute content revision."""
        try:
            # Validate workspace context
            if not state.get("workspace_id"):
                return self._set_error(
                    state, "Workspace ID is required for content revision"
                )

            # Extract revision request from state
            revision_request = self._extract_revision_request(state)

            if not revision_request:
                return self._set_error(state, "No revision request provided")

            # Validate revision request
            self._validate_revision_request(revision_request)

            # Perform content revision
            revision_result = await self._perform_content_revision(
                revision_request, state
            )

            # Store revision result
            await self._store_revision_result(revision_result, state)

            # Add assistant message
            response = self._format_revision_response(revision_result)
            state = self._add_assistant_message(state, response)

            # Set output
            return self._set_output(
                state,
                {
                    "revision_result": revision_result.__dict__,
                    "revised_content": revision_result.revised_content,
                    "improvement_percentage": revision_result.metrics.improvement_percentage,
                    "changes_count": len(revision_result.changes),
                },
            )

        except Exception as e:
            logger.error(f"Content revision failed: {e}")
            return self._set_error(state, f"Content revision failed: {str(e)}")

    def _extract_revision_request(self, state: AgentState) -> Optional[RevisionRequest]:
        """Extract revision request from state."""
        # Check if revision request is in state
        if "revision_request" in state:
            request_data = state["revision_request"]
            return RevisionRequest(**request_data)

        # Extract from user message
        user_input = self._extract_user_input(state)
        if not user_input:
            return None

        # Parse revision request from user input
        return self._parse_revision_request(user_input, state)

    def _parse_revision_request(
        self, user_input: str, state: AgentState
    ) -> Optional[RevisionRequest]:
        """Parse revision request from user input."""
        # Check for explicit content type mention
        content_types = list(self.content_revision_rules.keys())
        detected_type = None

        for content_type in content_types:
            if content_type.lower() in user_input.lower():
                detected_type = content_type
                break

        if not detected_type:
            # Default to blog
            detected_type = "blog"

        # Extract other parameters
        revision_type = self._extract_parameter(
            user_input, ["revision", "type", "focus"], "comprehensive"
        )
        objective = self._extract_parameter(
            user_input, ["objective", "goal", "purpose"], "engagement"
        )

        # Extract keywords
        keywords = self._extract_keywords(user_input)

        # Get context from state
        brand_voice = state.get("brand_voice", "professional")
        target_audience = state.get("target_audience", "general")

        # Create revision request
        return RevisionRequest(
            original_content=user_input,
            content_type=detected_type,
            revision_type=revision_type,
            target_audience=target_audience,
            objective=objective,
            brand_voice=brand_voice,
            feedback=[],  # No specific feedback provided
            constraints={},  # No specific constraints
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
            "revise",
            "revision",
            "content",
        }

        # Extract words that are not common words
        words = re.findall(r"\b\w+\b", text.lower())
        keywords = [
            word for word in words if word not in common_words and len(word) > 2
        ]

        return keywords[:8]  # Limit to 8 keywords

    def _validate_revision_request(self, request: RevisionRequest):
        """Validate revision request."""
        if request.content_type not in self.content_revision_rules:
            raise ValidationError(f"Unsupported content type: {request.content_type}")

        if request.revision_type not in self.revision_strategies:
            raise ValidationError(f"Unsupported revision type: {request.revision_type}")

        if request.objective not in [
            "awareness",
            "engagement",
            "conversion",
            "retention",
        ]:
            raise ValidationError(f"Invalid objective: {request.objective}")

        if not request.original_content or len(request.original_content.strip()) < 10:
            raise ValidationError(
                "Original content is required and must be at least 10 characters"
            )

    async def _perform_content_revision(
        self, request: RevisionRequest, state: AgentState
    ) -> RevisionResult:
        """Perform comprehensive content revision."""
        try:
            # Generate revision ID
            revision_id = f"revision_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Get revision strategy
            strategy = self.revision_strategies[request.revision_type]

            # Get content rules
            content_rules = self.content_revision_rules[request.content_type]

            # Calculate original content metrics
            original_metrics = self._calculate_content_metrics(
                request.original_content, request
            )

            # Apply revision techniques
            revised_content = request.original_content
            changes = []

            # Apply grammar fixes
            if (
                "grammar" in strategy["techniques"]
                or request.revision_type == "comprehensive"
            ):
                revised_content, grammar_changes = self._apply_grammar_fixes(
                    revised_content
                )
                changes.extend(grammar_changes)

            # Apply style improvements
            if (
                "style" in strategy["techniques"]
                or request.revision_type == "comprehensive"
            ):
                revised_content, style_changes = self._apply_style_improvements(
                    revised_content, request, content_rules
                )
                changes.extend(style_changes)

            # Apply SEO optimization
            if (
                "seo" in strategy["techniques"]
                or request.revision_type == "comprehensive"
            ):
                revised_content, seo_changes = self._apply_seo_optimization(
                    revised_content, request, content_rules
                )
                changes.extend(seo_changes)

            # Apply engagement enhancements
            if (
                "engagement" in strategy["techniques"]
                or request.revision_type == "comprehensive"
            ):
                revised_content, engagement_changes = (
                    self._apply_engagement_enhancements(
                        revised_content, request, content_rules
                    )
                )
                changes.extend(engagement_changes)

            # Apply structural improvements
            if (
                "structure" in strategy["techniques"]
                or request.revision_type == "comprehensive"
            ):
                revised_content, structure_changes = (
                    self._apply_structural_improvements(
                        revised_content, request, content_rules
                    )
                )
                changes.extend(structure_changes)

            # Calculate revised content metrics
            revised_metrics = self._calculate_content_metrics(revised_content, request)

            # Calculate improvement metrics
            metrics = self._calculate_improvement_metrics(
                original_metrics, revised_metrics
            )

            # Generate revision summary
            revision_summary = self._generate_revision_summary(changes, metrics)

            # Generate next steps
            next_steps = self._generate_next_steps(metrics, request)

            # Create revision result
            revision_result = RevisionResult(
                revision_id=revision_id,
                original_content=request.original_content,
                revised_content=revised_content,
                changes=changes,
                metrics=metrics,
                revision_summary=revision_summary,
                next_steps=next_steps,
                revision_count=len(changes),
                revised_at=datetime.now(),
                metadata={
                    "content_type": request.content_type,
                    "revision_type": request.revision_type,
                    "target_audience": request.target_audience,
                    "objective": request.objective,
                    "brand_voice": request.brand_voice,
                    "feedback": request.feedback,
                    "constraints": request.constraints,
                    "keywords": request.keywords,
                },
            )

            return revision_result

        except Exception as e:
            logger.error(f"Content revision failed: {e}")
            raise DatabaseError(f"Content revision failed: {str(e)}")

    def _calculate_content_metrics(
        self, content: str, request: RevisionRequest
    ) -> Dict[str, float]:
        """Calculate content quality metrics."""
        metrics = {}

        # Basic metrics
        word_count = len(content.split())
        sentence_count = len(content.split(". "))
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0

        # Grammar score (simplified)
        grammar_errors = 0
        for pattern_name, pattern in self.revision_patterns.items():
            if pattern_name in ["passive_to_active", "double_negatives"]:
                matches = re.findall(pattern["pattern"], content, re.IGNORECASE)
                grammar_errors += len(matches)

        grammar_score = max(0.0, 1.0 - (grammar_errors / max(word_count, 1)))

        # Readability score (simplified)
        readability_score = 1.0
        if avg_sentence_length > 20:
            readability_score -= 0.2
        if avg_sentence_length > 25:
            readability_score -= 0.3

        # SEO score (simplified)
        seo_score = 0.5  # Base score
        if request.keywords:
            keyword_density = (
                sum(content.lower().count(kw.lower()) for kw in request.keywords)
                / word_count
            )
            if 0.01 <= keyword_density <= 0.03:
                seo_score += 0.3
            elif 0.005 <= keyword_density <= 0.05:
                seo_score += 0.2

        if re.search(r"^#+\s", content, re.MULTILINE):
            seo_score += 0.2  # Has headings

        # Engagement score (simplified)
        engagement_score = 0.5  # Base score
        if "?" in content:
            engagement_score += 0.2
        if "!" in content:
            engagement_score += 0.1
        if re.search(r"\d+%", content):
            engagement_score += 0.2

        metrics.update(
            {
                "word_count": word_count,
                "sentence_count": sentence_count,
                "avg_sentence_length": avg_sentence_length,
                "grammar_score": grammar_score,
                "readability_score": readability_score,
                "seo_score": seo_score,
                "engagement_score": engagement_score,
                "overall_score": (
                    grammar_score + readability_score + seo_score + engagement_score
                )
                / 4,
            }
        )

        return metrics

    def _apply_grammar_fixes(self, content: str) -> tuple[str, List[RevisionChange]]:
        """Apply grammar and spelling fixes."""
        changes = []
        revised_content = content

        for pattern_name, pattern in self.revision_patterns.items():
            if pattern_name in [
                "passive_to_active",
                "double_negatives",
                "wordy_phrases",
                "redundant_words",
            ]:
                matches = list(
                    re.finditer(pattern["pattern"], revised_content, re.IGNORECASE)
                )

                for match in reversed(
                    matches
                ):  # Process in reverse to maintain positions
                    original_text = match.group(0)

                    try:
                        revised_text = pattern["replacement"](match)

                        change = RevisionChange(
                            change_id=f"grammar_{pattern_name}_{match.start()}",
                            type="modification",
                            location=f"Position {match.start()}",
                            original_text=original_text,
                            revised_text=revised_text,
                            reason=pattern["reason"],
                            impact="Improved clarity and readability",
                            confidence=0.8,
                        )
                        changes.append(change)

                        # Apply the change
                        revised_content = (
                            revised_content[: match.start()]
                            + revised_text
                            + revised_content[match.end() :]
                        )

                    except Exception as e:
                        logger.warning(
                            f"Failed to apply grammar fix {pattern_name}: {e}"
                        )

        return revised_content, changes

    def _apply_style_improvements(
        self, content: str, request: RevisionRequest, content_rules: Dict[str, Any]
    ) -> tuple[str, List[RevisionChange]]:
        """Apply style and tone improvements."""
        changes = []
        revised_content = content

        # Check sentence length
        sentences = content.split(". ")
        max_length = content_rules.get("max_sentence_length", 20)

        for i, sentence in enumerate(sentences):
            word_count = len(sentence.split())
            if word_count > max_length:
                # Split long sentence
                clauses = sentence.split(", ")
                if len(clauses) > 1:
                    new_sentence = ". ".join(clauses[:-1]) + ". " + clauses[-1]

                    change = RevisionChange(
                        change_id=f"style_sentence_{i}",
                        type="modification",
                        location=f"Sentence {i+1}",
                        original_text=sentence,
                        revised_text=new_sentence,
                        reason=f"Split long sentence ({word_count} words) for better readability",
                        impact="Improved readability and flow",
                        confidence=0.7,
                    )
                    changes.append(change)

                    revised_content = revised_content.replace(sentence, new_sentence)

        return revised_content, changes

    def _apply_seo_optimization(
        self, content: str, request: RevisionRequest, content_rules: Dict[str, Any]
    ) -> tuple[str, List[RevisionChange]]:
        """Apply SEO optimizations."""
        changes = []
        revised_content = content

        # Add headings if missing
        if not re.search(
            r"^#+\s", revised_content, re.MULTILINE
        ) and request.content_type in ["blog", "landing_page"]:
            # Add H1 and H2 structure
            lines = revised_content.split("\n")
            if lines:
                first_line = lines[0].strip()
                if len(first_line) > 10:
                    # Convert first line to H1
                    revised_content = f"# {first_line}\n\n" + "\n".join(lines[1:])

                    change = RevisionChange(
                        change_id="seo_heading_h1",
                        type="addition",
                        location="Beginning of content",
                        original_text=first_line,
                        revised_text=f"# {first_line}",
                        reason="Add H1 heading for SEO structure",
                        impact="Improved SEO and content organization",
                        confidence=0.9,
                    )
                    changes.append(change)

        # Optimize keyword placement
        if request.keywords and len(request.keywords) > 0:
            primary_keyword = request.keywords[0]
            content_lower = revised_content.lower()

            # Add keyword to first paragraph if missing
            first_paragraph = revised_content.split("\n\n")[0]
            if primary_keyword.lower() not in first_paragraph.lower():
                # Insert keyword naturally
                sentences = first_paragraph.split(". ")
                if sentences:
                    enhanced_sentence = f"{sentences[0]} {primary_keyword}"
                    revised_content = revised_content.replace(
                        sentences[0], enhanced_sentence
                    )

                    change = RevisionChange(
                        change_id="seo_keyword_first",
                        type="addition",
                        location="First paragraph",
                        original_text=sentences[0],
                        revised_text=enhanced_sentence,
                        reason="Add primary keyword to first paragraph",
                        impact="Improved SEO keyword placement",
                        confidence=0.8,
                    )
                    changes.append(change)

        return revised_content, changes

    def _apply_engagement_enhancements(
        self, content: str, request: RevisionRequest, content_rules: Dict[str, Any]
    ) -> tuple[str, List[RevisionChange]]:
        """Apply engagement enhancements."""
        changes = []
        revised_content = content

        # Add questions if missing
        if "?" not in revised_content and request.content_type in ["blog", "email"]:
            # Add question after introduction
            paragraphs = revised_content.split("\n\n")
            if len(paragraphs) > 1:
                question_templates = [
                    "Have you ever wondered how to achieve this?",
                    "What if you could transform your approach?",
                    "Did you know that there's a better way?",
                ]
                question = random.choice(question_templates)

                # Insert question after first paragraph
                new_content = (
                    paragraphs[0]
                    + f"\n\n{question}"
                    + "\n\n"
                    + "\n\n".join(paragraphs[1:])
                )

                change = RevisionChange(
                    change_id="engagement_question",
                    type="addition",
                    location="After introduction",
                    original_text="",
                    revised_text=question,
                    reason="Add engaging question to increase reader interaction",
                    impact="Improved engagement and reader retention",
                    confidence=0.7,
                )
                changes.append(change)

                revised_content = new_content

        # Add call to action if missing
        if request.objective in ["conversion", "engagement"]:
            cta_patterns = [
                "Learn more",
                "Discover how",
                "Get started",
                "Find out more",
            ]
            if not any(cta in revised_content for cta in cta_patterns):
                # Add CTA at the end
                cta = f" {random.choice(cta_patterns)} today!"
                revised_content += cta

                change = RevisionChange(
                    change_id="engagement_cta",
                    type="addition",
                    location="End of content",
                    original_text="",
                    revised_text=cta,
                    reason="Add call to action for conversion",
                    impact="Improved conversion potential",
                    confidence=0.8,
                )
                changes.append(change)

        return revised_content, changes

    def _apply_structural_improvements(
        self, content: str, request: RevisionRequest, content_rules: Dict[str, Any]
    ) -> tuple[str, List[RevisionChange]]:
        """Apply structural improvements."""
        changes = []
        revised_content = content

        # Check paragraph length
        paragraphs = revised_content.split("\n\n")
        max_paragraph_length = content_rules.get("max_paragraph_length", 5)

        for i, paragraph in enumerate(paragraphs):
            sentence_count = len(paragraph.split(". "))
            if sentence_count > max_paragraph_length:
                # Split long paragraph
                sentences = paragraph.split(". ")
                mid_point = len(sentences) // 2

                new_paragraph1 = ". ".join(sentences[:mid_point]) + "."
                new_paragraph2 = ". ".join(sentences[mid_point:])

                # Replace in content
                old_paragraph = paragraph
                revised_content = revised_content.replace(
                    old_paragraph, f"{new_paragraph1}\n\n{new_paragraph2}"
                )

                change = RevisionChange(
                    change_id=f"structure_paragraph_{i}",
                    type="restructure",
                    location=f"Paragraph {i+1}",
                    original_text=old_paragraph,
                    revised_text=f"{new_paragraph1}\n\n{new_paragraph2}",
                    reason=f"Split long paragraph ({sentence_count} sentences) for better readability",
                    impact="Improved content structure and readability",
                    confidence=0.8,
                )
                changes.append(change)

        return revised_content, changes

    def _calculate_improvement_metrics(
        self, original_metrics: Dict[str, float], revised_metrics: Dict[str, float]
    ) -> RevisionMetrics:
        """Calculate improvement metrics."""
        original_score = original_metrics["overall_score"]
        revised_score = revised_metrics["overall_score"]

        improvement_percentage = (
            ((revised_score - original_score) / original_score * 100)
            if original_score > 0
            else 0
        )

        return RevisionMetrics(
            original_score=original_score,
            revised_score=revised_score,
            improvement_percentage=improvement_percentage,
            grammar_improvement=revised_metrics["grammar_score"]
            - original_metrics["grammar_score"],
            readability_improvement=revised_metrics["readability_score"]
            - original_metrics["readability_score"],
            seo_improvement=revised_metrics["seo_score"]
            - original_metrics["seo_score"],
            engagement_improvement=revised_metrics["engagement_score"]
            - original_metrics["engagement_score"],
        )

    def _generate_revision_summary(
        self, changes: List[RevisionChange], metrics: RevisionMetrics
    ) -> str:
        """Generate revision summary."""
        summary = f"Content revision completed with {len(changes)} changes made. "
        summary += (
            f"Overall quality improved by {metrics.improvement_percentage:.1f}%. "
        )

        # Categorize changes
        change_types = {}
        for change in changes:
            if change.type not in change_types:
                change_types[change.type] = 0
            change_types[change.type] += 1

        summary += "Changes include: "
        for change_type, count in change_types.items():
            summary += f"{count} {change_type}s, "

        summary = summary.rstrip(", ") + "."

        return summary

    def _generate_next_steps(
        self, metrics: RevisionMetrics, request: RevisionRequest
    ) -> List[str]:
        """Generate next steps for further optimization."""
        next_steps = []

        if metrics.improvement_percentage < 10:
            next_steps.append("Consider additional revisions for greater improvement")

        if metrics.grammar_improvement < 0.1:
            next_steps.append("Review for additional grammar and style improvements")

        if metrics.seo_improvement < 0.1 and request.content_type in [
            "blog",
            "landing_page",
        ]:
            next_steps.append("Further SEO optimization may be beneficial")

        if metrics.engagement_improvement < 0.1 and request.objective in [
            "engagement",
            "conversion",
        ]:
            next_steps.append("Consider adding more engagement elements")

        if metrics.revised_score < 0.8:
            next_steps.append("Content quality could still be improved")
        else:
            next_steps.append("Content quality is now excellent")

        return next_steps[:3]  # Limit to 3 next steps

    async def _store_revision_result(self, result: RevisionResult, state: AgentState):
        """Store revision result in database."""
        try:
            # Store in database with workspace isolation
            database_tool = self._get_tool("database")
            if database_tool:
                await database_tool.arun(
                    table="revision_results",
                    workspace_id=state["workspace_id"],
                    data={
                        "revision_id": result.revision_id,
                        "original_content": result.original_content,
                        "revised_content": result.revised_content,
                        "changes": [change.__dict__ for change in result.changes],
                        "metrics": result.metrics.__dict__,
                        "revision_summary": result.revision_summary,
                        "next_steps": result.next_steps,
                        "revision_count": result.revision_count,
                        "revised_at": result.revised_at.isoformat(),
                        "metadata": result.metadata,
                    },
                )

        except Exception as e:
            logger.error(f"Failed to store revision result: {e}")

    def _format_revision_response(self, result: RevisionResult) -> str:
        """Format revision result response for user."""
        response = f"Γ£Å∩╕Å **Content Revision Completed**\n\n"
        response += f"**Revision Type:** {result.metadata['revision_type'].title()}\n"
        response += f"**Content Type:** {result.metadata['content_type'].title()}\n"
        response += f"**Changes Made:** {result.revision_count}\n"
        response += (
            f"**Improvement:** {result.metrics.improvement_percentage:+.1f}%\n\n"
        )

        response += f"**Quality Scores:**\n"
        response += f"ΓÇó Original: {result.metrics.original_score:.1%}\n"
        response += f"ΓÇó Revised: {result.metrics.revised_score:.1%}\n\n"

        response += f"**Improvement Breakdown:**\n"
        response += f"ΓÇó Grammar: {result.metrics.grammar_improvement:+.1%}\n"
        response += f"ΓÇó Readability: {result.metrics.readability_improvement:+.1%}\n"
        response += f"ΓÇó SEO: {result.metrics.seo_improvement:+.1%}\n"
        response += f"ΓÇó Engagement: {result.metrics.engagement_improvement:+.1%}\n\n"

        if result.changes:
            response += f"**Key Changes:**\n"
            # Show top 5 changes
            top_changes = result.changes[:5]
            for change in top_changes:
                response += f"ΓÇó {change.reason}\n"
            response += "\n"

        if result.next_steps:
            response += f"**Next Steps:**\n"
            for step in result.next_steps:
                response += f"ΓÇó {step}\n"
            response += "\n"

        response += f"**Revision Summary:**\n{result.revision_summary}\n\n"

        response += f"**Revised Content:**\n"
        response += (
            result.revised_content[:500] + "..."
            if len(result.revised_content) > 500
            else result.revised_content
        )

        return response
