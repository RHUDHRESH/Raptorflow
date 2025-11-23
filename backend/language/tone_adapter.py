"""
Tone Adapter - Analyzes and adapts content tone.
Rewrites content to match target tone profiles.
"""

import structlog
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

logger = structlog.get_logger(__name__)


class ToneProfile:
    """Defines a specific tone profile with parameters."""

    def __init__(
        self,
        name: str,
        description: str,
        formality_level: int,  # 1-10 (1=very casual, 10=very formal)
        allow_contractions: bool,
        emoji_usage: str,  # "none", "minimal", "moderate", "frequent"
        jargon_level: str,  # "none", "minimal", "moderate", "heavy"
        require_citations: bool,
        sentence_style: str,  # "simple", "varied", "complex"
        vocabulary_level: str,  # "basic", "intermediate", "advanced", "expert"
        person: str,  # "first", "second", "third"
        examples: Optional[List[str]] = None
    ):
        self.name = name
        self.description = description
        self.formality_level = formality_level
        self.allow_contractions = allow_contractions
        self.emoji_usage = emoji_usage
        self.jargon_level = jargon_level
        self.require_citations = require_citations
        self.sentence_style = sentence_style
        self.vocabulary_level = vocabulary_level
        self.person = person
        self.examples = examples or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "formality_level": self.formality_level,
            "allow_contractions": self.allow_contractions,
            "emoji_usage": self.emoji_usage,
            "jargon_level": self.jargon_level,
            "require_citations": self.require_citations,
            "sentence_style": self.sentence_style,
            "vocabulary_level": self.vocabulary_level,
            "person": self.person
        }


class ToneAdapter:
    """
    Analyzes current content tone and adapts it to target tones.
    Supports multiple tone profiles for different use cases.
    """

    def __init__(self):
        """Initialize the tone adapter with predefined profiles."""
        self.tone_profiles = self._load_tone_profiles()
        logger.info(
            "Tone adapter initialized",
            profiles_count=len(self.tone_profiles)
        )

    def _load_tone_profiles(self) -> Dict[str, ToneProfile]:
        """Load predefined tone profiles."""
        return {
            "professional": ToneProfile(
                name="Professional",
                description="Formal business communication",
                formality_level=8,
                allow_contractions=False,
                emoji_usage="none",
                jargon_level="moderate",
                require_citations=True,
                sentence_style="varied",
                vocabulary_level="advanced",
                person="third",
                examples=[
                    "We are pleased to announce...",
                    "Our analysis indicates...",
                    "According to recent research..."
                ]
            ),
            "conversational": ToneProfile(
                name="Conversational",
                description="Friendly and approachable",
                formality_level=4,
                allow_contractions=True,
                emoji_usage="minimal",
                jargon_level="minimal",
                require_citations=False,
                sentence_style="simple",
                vocabulary_level="intermediate",
                person="second",
                examples=[
                    "You'll love this...",
                    "Here's the thing...",
                    "Let me show you..."
                ]
            ),
            "thought_leadership": ToneProfile(
                name="Thought Leadership",
                description="Authoritative and insightful",
                formality_level=7,
                allow_contractions=False,
                emoji_usage="none",
                jargon_level="moderate",
                require_citations=True,
                sentence_style="complex",
                vocabulary_level="expert",
                person="first",
                examples=[
                    "In my experience...",
                    "The industry must recognize...",
                    "As we navigate this shift..."
                ]
            ),
            "friendly": ToneProfile(
                name="Friendly",
                description="Warm and personable",
                formality_level=3,
                allow_contractions=True,
                emoji_usage="moderate",
                jargon_level="none",
                require_citations=False,
                sentence_style="simple",
                vocabulary_level="basic",
                person="second",
                examples=[
                    "Hey there!",
                    "We're excited to share...",
                    "Thanks for being awesome!"
                ]
            ),
            "educational": ToneProfile(
                name="Educational",
                description="Clear and instructive",
                formality_level=6,
                allow_contractions=False,
                emoji_usage="none",
                jargon_level="minimal",
                require_citations=True,
                sentence_style="simple",
                vocabulary_level="intermediate",
                person="second",
                examples=[
                    "First, you need to understand...",
                    "This concept works by...",
                    "Consider the following example..."
                ]
            ),
            "persuasive": ToneProfile(
                name="Persuasive",
                description="Compelling and action-oriented",
                formality_level=5,
                allow_contractions=True,
                emoji_usage="minimal",
                jargon_level="minimal",
                require_citations=True,
                sentence_style="varied",
                vocabulary_level="intermediate",
                person="second",
                examples=[
                    "Imagine if you could...",
                    "Don't miss this opportunity...",
                    "Join thousands who have already..."
                ]
            ),
            "empathetic": ToneProfile(
                name="Empathetic",
                description="Understanding and supportive",
                formality_level=4,
                allow_contractions=True,
                emoji_usage="minimal",
                jargon_level="none",
                require_citations=False,
                sentence_style="simple",
                vocabulary_level="basic",
                person="first",
                examples=[
                    "We understand how you feel...",
                    "You're not alone in this...",
                    "We're here to help..."
                ]
            ),
            "technical": ToneProfile(
                name="Technical",
                description="Precise and detailed",
                formality_level=7,
                allow_contractions=False,
                emoji_usage="none",
                jargon_level="heavy",
                require_citations=True,
                sentence_style="complex",
                vocabulary_level="expert",
                person="third",
                examples=[
                    "The system architecture comprises...",
                    "Implementation requires...",
                    "Performance metrics indicate..."
                ]
            )
        }

    async def analyze_tone(
        self,
        content: str,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze the current tone of content.

        Args:
            content: Text to analyze
            correlation_id: Request correlation ID

        Returns:
            Tone analysis with detected characteristics
        """
        logger.info(
            "Analyzing content tone",
            content_length=len(content),
            correlation_id=correlation_id
        )

        start_time = datetime.utcnow()

        # Analyze tone characteristics
        formality = self._assess_formality(content)
        has_contractions = self._detect_contractions(content)
        emoji_count = self._count_emojis(content)
        jargon_density = self._assess_jargon_density(content)
        sentence_complexity = self._assess_sentence_complexity(content)
        vocabulary_level = self._assess_vocabulary_level(content)
        person_perspective = self._detect_person_perspective(content)

        # Match against known profiles
        profile_matches = self._match_tone_profiles(
            formality,
            has_contractions,
            emoji_count,
            jargon_density,
            sentence_complexity,
            vocabulary_level,
            person_perspective
        )

        duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

        result = {
            "detected_characteristics": {
                "formality_level": formality,
                "has_contractions": has_contractions,
                "emoji_count": emoji_count,
                "jargon_density": jargon_density,
                "sentence_complexity": sentence_complexity,
                "vocabulary_level": vocabulary_level,
                "person_perspective": person_perspective
            },
            "profile_matches": profile_matches,
            "best_match": profile_matches[0] if profile_matches else None,
            "duration_ms": duration_ms,
            "analyzed_at": start_time.isoformat()
        }

        logger.info(
            "Tone analysis completed",
            best_match=result["best_match"]["profile"] if result["best_match"] else "unknown",
            duration_ms=duration_ms,
            correlation_id=correlation_id
        )

        return result

    async def adapt_tone(
        self,
        content: str,
        target_tone: str,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Rewrite content to match target tone profile.

        Args:
            content: Original text
            target_tone: Name of target tone profile
            correlation_id: Request correlation ID

        Returns:
            Adapted content and transformation details
        """
        logger.info(
            "Adapting content tone",
            target_tone=target_tone,
            content_length=len(content),
            correlation_id=correlation_id
        )

        start_time = datetime.utcnow()

        # Validate target tone
        if target_tone not in self.tone_profiles:
            available_tones = ", ".join(self.tone_profiles.keys())
            raise ValueError(
                f"Unknown tone '{target_tone}'. Available: {available_tones}"
            )

        profile = self.tone_profiles[target_tone]

        # Analyze current tone
        current_tone_analysis = await self.analyze_tone(content, correlation_id)

        # Rewrite using LLM
        adapted_content = await self._rewrite_with_llm(content, profile, correlation_id)

        # Verify adapted tone
        adapted_tone_analysis = await self.analyze_tone(adapted_content, correlation_id)

        duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

        result = {
            "original_content": content,
            "adapted_content": adapted_content,
            "target_tone": target_tone,
            "tone_profile": profile.to_dict(),
            "current_tone": current_tone_analysis,
            "adapted_tone": adapted_tone_analysis,
            "transformation_applied": True,
            "duration_ms": duration_ms,
            "adapted_at": start_time.isoformat()
        }

        logger.info(
            "Tone adaptation completed",
            target_tone=target_tone,
            duration_ms=duration_ms,
            correlation_id=correlation_id
        )

        return result

    async def _rewrite_with_llm(
        self,
        content: str,
        profile: ToneProfile,
        correlation_id: Optional[str]
    ) -> str:
        """Use LLM to rewrite content matching tone profile."""
        try:
            from backend.services.vertex_ai_client import vertex_ai_client

            # Build detailed tone instructions
            tone_instructions = f"""
**Target Tone Profile**: {profile.name}
**Description**: {profile.description}

**Requirements**:
- Formality Level: {profile.formality_level}/10
- Contractions: {'Allowed' if profile.allow_contractions else 'Not allowed'}
- Emoji Usage: {profile.emoji_usage}
- Jargon Level: {profile.jargon_level}
- Citations: {'Required' if profile.require_citations else 'Not required'}
- Sentence Style: {profile.sentence_style}
- Vocabulary Level: {profile.vocabulary_level}
- Perspective: {profile.person} person

**Examples of {profile.name} tone**:
{chr(10).join('- ' + ex for ex in profile.examples)}
"""

            prompt = f"""Rewrite the following content to match the target tone profile exactly.

{tone_instructions}

**Original Content**:
{content}

**Task**: Rewrite this content to perfectly match the {profile.name} tone profile. Maintain the core message and key information, but adjust the language, style, and presentation to match the tone requirements above.

Output ONLY the rewritten content, nothing else."""

            messages = [
                {
                    "role": "system",
                    "content": f"You are an expert copywriter specializing in tone adaptation. Your rewrites perfectly capture the target tone while preserving the original message."
                },
                {"role": "user", "content": prompt}
            ]

            adapted_content = await vertex_ai_client.chat_completion(
                messages,
                model_type="creative",
                temperature=0.7
            )

            return adapted_content.strip()

        except Exception as e:
            logger.error(
                f"Failed to adapt tone with LLM: {e}",
                correlation_id=correlation_id
            )
            return content  # Return original on failure

    def _assess_formality(self, content: str) -> int:
        """Assess formality level (1-10)."""
        import re

        formality_score = 5  # Start neutral

        # Formal indicators
        formal_patterns = [
            r'\b(furthermore|moreover|consequently|therefore|accordingly)\b',
            r'\b(utilize|facilitate|implement|establish|demonstrate)\b',
            r'\b(shall|must|ought)\b'
        ]

        # Casual indicators
        casual_patterns = [
            r'\b(hey|yeah|cool|awesome|stuff|thing)\b',
            r'[!]{2,}',
            r'\b(gonna|wanna|gotta)\b'
        ]

        for pattern in formal_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                formality_score += 1

        for pattern in casual_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                formality_score -= 1

        return max(1, min(10, formality_score))

    def _detect_contractions(self, content: str) -> bool:
        """Detect if content uses contractions."""
        import re
        contraction_pattern = r"\b\w+'\w+\b"
        matches = re.findall(contraction_pattern, content)
        # Filter out possessives
        contractions = [m for m in matches if not m.endswith("'s")]
        return len(contractions) > 0

    def _count_emojis(self, content: str) -> int:
        """Count emoji usage."""
        import re
        # Simple emoji detection (can be enhanced)
        emoji_pattern = r'[😀-🙏🌀-🗿🚀-🛿]'
        return len(re.findall(emoji_pattern, content))

    def _assess_jargon_density(self, content: str) -> str:
        """Assess jargon/technical term density."""
        # Simplified jargon detection
        import re

        technical_terms = [
            'implement', 'leverage', 'utilize', 'paradigm', 'synergy',
            'optimize', 'bandwidth', 'scalable', 'infrastructure', 'architecture',
            'methodology', 'framework', 'ecosystem', 'granular', 'stakeholder'
        ]

        words = re.findall(r'\b\w+\b', content.lower())
        if not words:
            return "none"

        jargon_count = sum(1 for word in words if word in technical_terms)
        jargon_percentage = (jargon_count / len(words)) * 100

        if jargon_percentage > 5:
            return "heavy"
        elif jargon_percentage > 2:
            return "moderate"
        elif jargon_percentage > 0:
            return "minimal"
        else:
            return "none"

    def _assess_sentence_complexity(self, content: str) -> str:
        """Assess sentence structure complexity."""
        import re

        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return "simple"

        avg_words = sum(len(s.split()) for s in sentences) / len(sentences)

        if avg_words > 25:
            return "complex"
        elif avg_words > 15:
            return "varied"
        else:
            return "simple"

    def _assess_vocabulary_level(self, content: str) -> str:
        """Assess vocabulary sophistication level."""
        import re

        # Simple heuristic based on word length
        words = re.findall(r'\b\w+\b', content.lower())
        if not words:
            return "basic"

        avg_word_length = sum(len(w) for w in words) / len(words)

        if avg_word_length > 6.5:
            return "expert"
        elif avg_word_length > 5.5:
            return "advanced"
        elif avg_word_length > 4.5:
            return "intermediate"
        else:
            return "basic"

    def _detect_person_perspective(self, content: str) -> str:
        """Detect the grammatical person used."""
        import re

        first_person = len(re.findall(r'\b(I|me|my|we|us|our)\b', content, re.IGNORECASE))
        second_person = len(re.findall(r'\b(you|your)\b', content, re.IGNORECASE))
        third_person = len(re.findall(r'\b(he|she|it|they|them|their)\b', content, re.IGNORECASE))

        max_count = max(first_person, second_person, third_person)

        if max_count == 0:
            return "neutral"
        elif first_person == max_count:
            return "first"
        elif second_person == max_count:
            return "second"
        else:
            return "third"

    def _match_tone_profiles(
        self,
        formality: int,
        has_contractions: bool,
        emoji_count: int,
        jargon_density: str,
        sentence_complexity: str,
        vocabulary_level: str,
        person: str
    ) -> List[Dict[str, Any]]:
        """Match content characteristics against tone profiles."""
        matches = []

        for profile_name, profile in self.tone_profiles.items():
            # Calculate match score
            score = 0
            max_score = 7

            # Formality (most important)
            formality_diff = abs(profile.formality_level - formality)
            if formality_diff <= 1:
                score += 2
            elif formality_diff <= 2:
                score += 1

            # Contractions
            if profile.allow_contractions == has_contractions:
                score += 1

            # Jargon
            if profile.jargon_level == jargon_density:
                score += 1

            # Sentence complexity
            if profile.sentence_style == sentence_complexity:
                score += 1

            # Vocabulary
            if profile.vocabulary_level == vocabulary_level:
                score += 1

            # Person
            if profile.person == person:
                score += 1

            confidence = (score / max_score) * 100

            matches.append({
                "profile": profile_name,
                "confidence": round(confidence, 1),
                "score": score,
                "max_score": max_score
            })

        # Sort by confidence
        matches.sort(key=lambda x: x["confidence"], reverse=True)

        return matches


# Singleton instance
tone_adapter = ToneAdapter()
