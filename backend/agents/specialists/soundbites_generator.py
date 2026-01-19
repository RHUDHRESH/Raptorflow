"""
Soundbites Generator Agent
Creates messaging library with taglines, value props, and soundbites
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import random

logger = logging.getLogger(__name__)


class SoundbiteType(Enum):
    """Types of soundbites"""
    TAGLINE = "tagline"  # Short brand tagline
    VALUE_PROP = "value_prop"  # Value proposition statement
    HEADLINE = "headline"  # Ad/landing page headline
    SUBHEADLINE = "subheadline"  # Supporting headline
    CTA = "cta"  # Call to action
    ELEVATOR_PITCH = "elevator_pitch"  # 30-second pitch
    TWEET = "tweet"  # Social media length
    PAIN_STATEMENT = "pain_statement"  # Problem statement
    SOLUTION_STATEMENT = "solution_statement"  # Solution statement


class AudienceContext(Enum):
    """Audience context for soundbites"""
    DECISION_MAKER = "decision_maker"
    TECHNICAL = "technical"
    END_USER = "end_user"
    GENERAL = "general"


class EmotionalTone(Enum):
    """Emotional tone of soundbite"""
    CONFIDENT = "confident"
    URGENT = "urgent"
    ASPIRATIONAL = "aspirational"
    EMPATHETIC = "empathetic"
    PROVOCATIVE = "provocative"
    REASSURING = "reassuring"


@dataclass
class Soundbite:
    """A single soundbite/messaging element"""
    id: str
    type: SoundbiteType
    content: str
    audience: AudienceContext
    tone: EmotionalTone
    character_count: int
    word_count: int
    use_cases: List[str] = field(default_factory=list)
    variations: List[str] = field(default_factory=list)
    score: float = 0.0  # Quality score 0-1
    notes: str = ""


@dataclass
class SoundbiteLibrary:
    """Complete soundbite library"""
    soundbites: List[Soundbite]
    by_type: Dict[str, List[Soundbite]]
    by_audience: Dict[str, List[Soundbite]]
    recommendations: List[str]
    summary: str


class SoundbitesGenerator:
    """AI-powered soundbites and messaging library generator"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.soundbite_counter = 0
        self.templates = self._load_templates()
    
    def _generate_soundbite_id(self) -> str:
        """Generate unique soundbite ID"""
        self.soundbite_counter += 1
        return f"SND-{self.soundbite_counter:03d}"
    
    def _load_templates(self) -> Dict[str, List[str]]:
        """Load soundbite templates"""
        return {
            "tagline": [
                "{benefit} without {pain}",
                "The {adjective} way to {action}",
                "{action}. {result}.",
                "From {pain} to {benefit}",
                "{audience}'s secret weapon for {goal}",
            ],
            "value_prop": [
                "We help {audience} {action} so they can {benefit}",
                "The only {category} that {unique_feature}",
                "{product} gives you {benefit} without {pain}",
                "Stop {pain}. Start {benefit}.",
                "Unlike {alternative}, we {differentiator}",
            ],
            "headline": [
                "What if {pain} was gone forever?",
                "The {audience} are already using this",
                "{benefit} in {timeframe}",
                "You're leaving {metric} on the table",
                "Finally, {category} that actually works",
            ],
            "cta": [
                "Start {action} today",
                "Get {benefit} now",
                "See {product} in action",
                "Join {number}+ {audience}",
                "Try free for {timeframe}",
            ],
            "elevator_pitch": [
                "You know how {audience} struggle with {pain}? We built {product} to {solution}. Unlike {alternative}, we {differentiator}. That's why {social_proof}.",
            ],
            "pain_statement": [
                "Tired of {pain}?",
                "{pain} is costing you {cost}",
                "If {pain}, you're not alone",
                "Most {audience} waste {metric} on {pain}",
            ],
            "solution_statement": [
                "{product} solves {pain} by {how}",
                "With {product}, you get {benefit}",
                "We turn {pain} into {benefit}",
            ],
        }
    
    def _fill_template(self, template: str, context: Dict[str, Any]) -> str:
        """Fill a template with context values"""
        result = template
        for key, value in context.items():
            placeholder = "{" + key + "}"
            if placeholder in result:
                result = result.replace(placeholder, str(value))
        
        # Remove unfilled placeholders
        import re
        result = re.sub(r'\{[^}]+\}', '[...]', result)
        
        return result
    
    def _generate_from_template(self, soundbite_type: SoundbiteType, context: Dict[str, Any], audience: AudienceContext, tone: EmotionalTone) -> Soundbite:
        """Generate a soundbite from templates"""
        templates = self.templates.get(soundbite_type.value, self.templates["tagline"])
        template = random.choice(templates)
        
        content = self._fill_template(template, context)
        
        # Generate variations
        variations = []
        for _ in range(2):
            other_template = random.choice([t for t in templates if t != template])
            variation = self._fill_template(other_template, context)
            if variation != content:
                variations.append(variation)
        
        # Determine use cases
        use_cases = self._determine_use_cases(soundbite_type)
        
        # Calculate score based on quality metrics
        score = self._calculate_score(content, soundbite_type)
        
        return Soundbite(
            id=self._generate_soundbite_id(),
            type=soundbite_type,
            content=content,
            audience=audience,
            tone=tone,
            character_count=len(content),
            word_count=len(content.split()),
            use_cases=use_cases,
            variations=variations,
            score=score
        )
    
    def _determine_use_cases(self, soundbite_type: SoundbiteType) -> List[str]:
        """Determine use cases for a soundbite type"""
        use_case_map = {
            SoundbiteType.TAGLINE: ["Website hero", "Email signature", "Social media bio"],
            SoundbiteType.VALUE_PROP: ["Sales deck", "Landing page", "Pitch"],
            SoundbiteType.HEADLINE: ["Ads", "Landing pages", "Blog posts"],
            SoundbiteType.SUBHEADLINE: ["Landing pages", "Product pages"],
            SoundbiteType.CTA: ["Buttons", "Ads", "Emails"],
            SoundbiteType.ELEVATOR_PITCH: ["Networking", "Investor meetings", "Cold calls"],
            SoundbiteType.TWEET: ["Twitter/X", "LinkedIn", "Social ads"],
            SoundbiteType.PAIN_STATEMENT: ["Problem section", "Ads", "Cold outreach"],
            SoundbiteType.SOLUTION_STATEMENT: ["Solution section", "Sales calls"],
        }
        return use_case_map.get(soundbite_type, ["General marketing"])
    
    def _calculate_score(self, content: str, soundbite_type: SoundbiteType) -> float:
        """Calculate quality score for a soundbite"""
        score = 0.5  # Base score
        
        # Length appropriateness
        word_count = len(content.split())
        ideal_lengths = {
            SoundbiteType.TAGLINE: (3, 8),
            SoundbiteType.VALUE_PROP: (10, 25),
            SoundbiteType.HEADLINE: (4, 12),
            SoundbiteType.CTA: (2, 6),
            SoundbiteType.ELEVATOR_PITCH: (30, 60),
            SoundbiteType.TWEET: (10, 40),
        }
        
        ideal = ideal_lengths.get(soundbite_type, (5, 20))
        if ideal[0] <= word_count <= ideal[1]:
            score += 0.2
        elif word_count < ideal[0] * 0.5 or word_count > ideal[1] * 1.5:
            score -= 0.1
        
        # No placeholders remaining
        if "[...]" not in content:
            score += 0.15
        
        # Has action words
        action_words = ["get", "start", "join", "try", "discover", "learn", "build", "grow", "achieve"]
        if any(word in content.lower() for word in action_words):
            score += 0.1
        
        # Not too generic
        generic_words = ["solution", "platform", "tool", "software", "system"]
        generic_count = sum(1 for word in generic_words if word in content.lower())
        if generic_count == 0:
            score += 0.05
        
        return min(1.0, max(0.0, score))
    
    async def generate_soundbites(self, company_info: Dict[str, Any], positioning: Dict[str, Any] = None, icp_data: Dict[str, Any] = None) -> SoundbiteLibrary:
        """
        Generate a complete soundbite library
        
        Args:
            company_info: Company information
            positioning: Positioning data
            icp_data: ICP profile data
        
        Returns:
            SoundbiteLibrary with all generated soundbites
        """
        positioning = positioning or {}
        icp_data = icp_data or {}
        
        # Build context for templates
        context = {
            "product": company_info.get("product_name", "Our product"),
            "audience": icp_data.get("name", "teams"),
            "benefit": positioning.get("primary_benefit", "better results"),
            "pain": positioning.get("primary_pain", "wasted time"),
            "action": company_info.get("core_action", "grow"),
            "result": positioning.get("outcome", "success"),
            "goal": positioning.get("goal", "growth"),
            "category": company_info.get("category", "software"),
            "unique_feature": positioning.get("differentiator", "our unique approach"),
            "adjective": random.choice(["smarter", "faster", "easier", "better"]),
            "alternative": "the old way",
            "differentiator": positioning.get("differentiator", "focus on what matters"),
            "timeframe": "minutes",
            "metric": "opportunities",
            "number": random.choice(["1,000", "5,000", "10,000"]),
            "how": positioning.get("how", "automation"),
            "social_proof": "leading companies trust us",
            "cost": "thousands of dollars",
        }
        
        soundbites = []
        
        # Generate soundbites for each type and audience combination
        for soundbite_type in SoundbiteType:
            for audience in [AudienceContext.DECISION_MAKER, AudienceContext.GENERAL]:
                tone = EmotionalTone.CONFIDENT if audience == AudienceContext.DECISION_MAKER else EmotionalTone.ASPIRATIONAL
                
                soundbite = self._generate_from_template(soundbite_type, context, audience, tone)
                soundbites.append(soundbite)
        
        # Organize by type and audience
        by_type: Dict[str, List[Soundbite]] = {}
        by_audience: Dict[str, List[Soundbite]] = {}
        
        for sb in soundbites:
            type_key = sb.type.value
            audience_key = sb.audience.value
            
            if type_key not in by_type:
                by_type[type_key] = []
            by_type[type_key].append(sb)
            
            if audience_key not in by_audience:
                by_audience[audience_key] = []
            by_audience[audience_key].append(sb)
        
        # Recommendations
        recommendations = [
            "Test multiple variations in A/B tests",
            "Customize soundbites for each channel",
            "Update messaging quarterly based on learnings"
        ]
        
        high_score_count = sum(1 for s in soundbites if s.score >= 0.7)
        summary = f"Generated {len(soundbites)} soundbites across {len(SoundbiteType)} types. "
        summary += f"High-quality: {high_score_count}. Ready for use in marketing."
        
        return SoundbiteLibrary(
            soundbites=soundbites,
            by_type=by_type,
            by_audience=by_audience,
            recommendations=recommendations,
            summary=summary
        )
    
    def get_library_summary(self, library: SoundbiteLibrary) -> Dict[str, Any]:
        """Get summary for display"""
        return {
            "total_soundbites": len(library.soundbites),
            "types": list(library.by_type.keys()),
            "audiences": list(library.by_audience.keys()),
            "summary": library.summary,
            "top_soundbites": [{"type": s.type.value, "content": s.content, "score": s.score} for s in sorted(library.soundbites, key=lambda x: x.score, reverse=True)[:5]]
        }
