"""
Neuroscience Copywriter Agent
Generates copy using 6 principles of neuroscience-based marketing
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class NeurosciencePrinciple(Enum):
    """6 principles of neuroscience-based copywriting"""
    LIMBIC = "limbic"  # Emotional appeal to limbic system
    PATTERN = "pattern"  # Pattern recognition and familiarity
    SIMPLICITY = "simplicity"  # Cognitive ease and simplicity
    SOCIAL_PROOF = "social_proof"  # Social validation and herd behavior
    SCARCITY = "scarcity"  # Loss aversion and scarcity
    CONTRAST = "contrast"  # Contrast and anchoring effects


class CopyType(Enum):
    """Types of marketing copy"""
    HEADLINE = "headline"
    TAGLINE = "tagline"
    DESCRIPTION = "description"
    VALUE_PROPOSITION = "value_proposition"
    CALL_TO_ACTION = "call_to_action"
    SOCIAL_PROOF = "social_proof"
    FEATURE_BENEFIT = "feature_benefit"
    PAIN_POINT = "pain_point"


class Tone(Enum):
    """Tone variations for copy"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    URGENT = "urgent"
    EMPATHETIC = "empathetic"
    CONFIDENT = "confident"
    INNOVATIVE = "innovative"


@dataclass
class CopyVariant:
    """Represents a copy variant"""
    id: str
    text: str
    principle: NeurosciencePrinciple
    copy_type: CopyType
    tone: Tone
    effectiveness_score: float
    emotional_impact: float
    clarity_score: float
    persuasion_score: float
    explanation: str


@dataclass
class CopyAnalysis:
    """Analysis of copy effectiveness"""
    total_variants: int
    best_variant: CopyVariant
    principle_distribution: Dict[str, int]
    tone_distribution: Dict[str, int]
    average_scores: Dict[str, float]
    recommendations: List[str]


@dataclass
class CopywritingResult:
    """Result of neuroscience copywriting"""
    variants: List[CopyVariant]
    analysis: CopyAnalysis
    target_audience_insights: List[str]
    psychological_triggers: List[str]
    ab_test_recommendations: List[Dict[str, Any]]
    implementation_guide: Dict[str, str]


class NeuroscienceCopywriter:
    """Neuroscience-based copywriting specialist"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.principle_templates = self._load_principle_templates()
        self.emotional_words = self._load_emotional_words()
        self.power_words = self._load_power_words()
        self.copy_counter = 0
    
    def _load_principle_templates(self) -> Dict[NeurosciencePrinciple, Dict[str, Any]]:
        """Load templates for each neuroscience principle"""
        return {
            NeurosciencePrinciple.LIMBIC: {
                "description": "Appeals to emotions and limbic system",
                "techniques": ["storytelling", "emotional language", "sensory details", "metaphors"],
                "trigger_words": ["feel", "imagine", "experience", "discover", "transform"],
                "effectiveness": 0.85
            },
            NeurosciencePrinciple.PATTERN: {
                "description": "Uses familiar patterns and cognitive shortcuts",
                "techniques": ["repetition", "familiar phrases", "cognitive ease", "mental models"],
                "trigger_words": ["because", "naturally", "obviously", "clearly", "proven"],
                "effectiveness": 0.75
            },
            NeurosciencePrinciple.SIMPLICITY: {
                "description": "Reduces cognitive load and increases clarity",
                "techniques": ["short sentences", "simple words", "clear structure", "white space"],
                "trigger_words": ["simply", "easily", "quickly", "just", "only"],
                "effectiveness": 0.80
            },
            NeurosciencePrinciple.SOCIAL_PROOF: {
                "description": "Leverages social validation and herd behavior",
                "techniques": ["testimonials", "statistics", "social validation", "authority"],
                "trigger_words": ["join", "thousands", "trusted", "recommended", "popular"],
                "effectiveness": 0.90
            },
            NeurosciencePrinciple.SCARCITY: {
                "description": "Creates urgency through loss aversion",
                "techniques": ["limited time", "exclusive access", "fear of missing out", "urgency"],
                "trigger_words": ["limited", "only", "exclusive", "urgent", "don't miss"],
                "effectiveness": 0.88
            },
            NeurosciencePrinciple.CONTRAST: {
                "description": "Uses contrast and anchoring effects",
                "techniques": ["before/after", "comparison", "anchoring", "framing"],
                "trigger_words": ["vs", "instead", "unlike", "better", "superior"],
                "effectiveness": 0.82
            }
        }
    
    def _load_emotional_words(self) -> Dict[str, List[str]]:
        """Load emotional word categories"""
        return {
            "positive": ["amazing", "incredible", "transformative", "breakthrough", "revolutionary", "life-changing"],
            "negative": ["frustrating", "overwhelming", "confusing", "time-consuming", "expensive", "risky"],
            "fear": ["miss", "lose", "fail", "risk", "danger", "threat"],
            "desire": ["want", "need", "dream", "achieve", "succeed", "gain"],
            "trust": ["proven", "tested", "guaranteed", "secure", "reliable", "trusted"],
            "urgency": ["now", "today", "immediately", "urgent", "limited", "ending"]
        }
    
    def _load_power_words(self) -> List[str]:
        """Load high-impact power words"""
        return [
            "free", "new", "instantly", "guaranteed", "limited", "exclusive", "proven", "results",
            "discover", "unlock", "reveal", "secret", "breakthrough", "revolutionary", "ultimate",
            "powerful", "effective", "simple", "easy", "quick", "fast", "save", "gain"
        ]
    
    def _generate_copy_id(self) -> str:
        """Generate unique copy ID"""
        self.copy_counter += 1
        return f"COPY-{self.copy_counter:03d}"
    
    def _calculate_emotional_impact(self, text: str) -> float:
        """Calculate emotional impact score (0-1)"""
        text_lower = text.lower()
        emotional_count = 0
        
        for category, words in self.emotional_words.items():
            for word in words:
                if word in text_lower:
                    emotional_count += 1
        
        # Normalize by text length
        word_count = len(text.split())
        if word_count == 0:
            return 0.0
        
        return min(1.0, emotional_count / word_count * 5)  # Scale to 0-1
    
    def _calculate_clarity_score(self, text: str) -> float:
        """Calculate clarity score based on simplicity"""
        # Factors: sentence length, word complexity, structure
        sentences = text.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        
        # Shorter sentences = higher clarity
        clarity_score = max(0.0, 1.0 - (avg_sentence_length - 10) / 20)  # Optimal around 10 words
        
        # Check for simple words
        simple_words = sum(1 for word in text.split() if len(word) <= 6)
        simplicity_ratio = simple_words / len(text.split()) if text.split() else 0
        
        return (clarity_score + simplicity_ratio) / 2
    
    def _calculate_persuasion_score(self, text: str, principle: NeurosciencePrinciple) -> float:
        """Calculate persuasion score based on principle alignment"""
        text_lower = text.lower()
        principle_info = self.principle_templates[principle]
        
        # Check for trigger words
        trigger_matches = sum(1 for word in principle_info["trigger_words"] if word in text_lower)
        
        # Check for power words
        power_matches = sum(1 for word in self.power_words if word in text_lower)
        
        # Base score from principle effectiveness
        base_score = principle_info["effectiveness"]
        
        # Boost for trigger words
        trigger_boost = min(0.2, trigger_matches * 0.05)
        
        # Boost for power words
        power_boost = min(0.1, power_matches * 0.02)
        
        return min(1.0, base_score + trigger_boost + power_boost)
    
    def _generate_limbic_copy(self, product_info: Dict[str, Any], copy_type: CopyType, tone: Tone) -> str:
        """Generate copy using limbic system principles"""
        product_name = product_info.get("name", "product")
        benefit = product_info.get("key_benefit", "amazing results")
        emotion = product_info.get("target_emotion", "happiness")
        
        templates = {
            CopyType.HEADLINE: [
                f"Feel the {emotion} of {benefit} with {product_name}",
                f"Experience {benefit} like never before",
                f"Transform your {emotion} with {product_name}"
            ],
            CopyType.TAGLINE: [
                f"Where {emotion} meets innovation",
                f"Feel the difference, see the results",
                f"Emotionally intelligent solutions"
            ],
            CopyType.DESCRIPTION: [
                f"Imagine waking up to {benefit} every day. That's the promise of {product_name}. We've designed every aspect to evoke pure {emotion}.",
                f"Feel the surge of {emotion} as you discover what {product_name} can do for you. This isn't just a product – it's an emotional journey."
            ],
            CopyType.VALUE_PROPOSITION: [
                f"Don't just get results – feel them. {product_name} delivers {benefit} with an emotional connection that lasts.",
                f"Experience the {emotion} of success with {product_name}. Where logic meets emotion, and results follow."
            ],
            CopyType.CALL_TO_ACTION: [
                f"Start feeling {benefit} today",
                f"Experience the {emotion} now",
                f"Transform your emotions with {product_name}"
            ]
        }
        
        return templates.get(copy_type, [f"Feel {benefit} with {product_name}"])[0]
    
    def _generate_pattern_copy(self, product_info: Dict[str, Any], copy_type: CopyType, tone: Tone) -> str:
        """Generate copy using pattern recognition principles"""
        product_name = product_info.get("name", "product")
        benefit = product_info.get("key_benefit", "great results")
        pattern = product_info.get("familiar_concept", "success")
        
        templates = {
            CopyType.HEADLINE: [
                f"{product_name}: Because {pattern} works",
                f"The {pattern} solution you've been looking for",
                f"Obviously, {product_name} delivers {benefit}"
            ],
            CopyType.TAGLINE: [
                f"Proven {pattern}, proven results",
                f"Naturally effective solutions",
                f"The clear choice for {pattern}"
            ],
            CopyType.DESCRIPTION: [
                f"Just like successful businesses before you, you'll find that {product_name} naturally delivers {benefit}. It's the proven pattern for success.",
                f"Clearly, {product_name} follows the established pattern of {pattern}. That's why it consistently delivers {benefit}."
            ],
            CopyType.VALUE_PROPOSITION: [
                f"Because the pattern of {pattern} is proven, {product_name} delivers {benefit} every time.",
                f"Follow the proven path to {benefit} with {product_name}. The pattern is clear, the results are guaranteed."
            ],
            CopyType.CALL_TO_ACTION: [
                f"Join the proven pattern of success",
                f"Start following the path to {benefit}",
                f"Choose the clear solution"
            ]
        }
        
        return templates.get(copy_type, [f"Proven {pattern} with {product_name}"])[0]
    
    def _generate_simplicity_copy(self, product_info: Dict[str, Any], copy_type: CopyType, tone: Tone) -> str:
        """Generate copy using simplicity principles"""
        product_name = product_info.get("name", "product")
        benefit = product_info.get("key_benefit", "great results")
        
        templates = {
            CopyType.HEADLINE: [
                f"{product_name}. Simply {benefit}.",
                f"Easy {benefit}. Guaranteed.",
                f"Just {product_name}. Just {benefit}."
            ],
            CopyType.TAGLINE: [
                f"Simply effective",
                f"Easy results",
                f"Just works"
            ],
            CopyType.DESCRIPTION: [
                f"{product_name} is simple. It delivers {benefit}. That's it. No complexity, no confusion, just results.",
                f"Simply put, {product_name} gives you {benefit}. Easy to use, easy to understand, easy to love."
            ],
            CopyType.VALUE_PROPOSITION: [
                f"Get {benefit} simply. {product_name} makes it easy.",
                f"Simple solution, powerful results. That's {product_name}."
            ],
            CopyType.CALL_TO_ACTION: [
                f"Try it now. It's simple.",
                f"Get {benefit} easily",
                f"Start simply"
            ]
        }
        
        return templates.get(copy_type, [f"Simple {benefit} with {product_name}"])[0]
    
    def _generate_social_proof_copy(self, product_info: Dict[str, Any], copy_type: CopyType, tone: Tone) -> str:
        """Generate copy using social proof principles"""
        product_name = product_info.get("name", "product")
        benefit = product_info.get("key_benefit", "great results")
        users = product_info.get("user_count", "thousands")
        
        templates = {
            CopyType.HEADLINE: [
                f"Join {users} getting {benefit} with {product_name}",
                f"The {product_name} trusted by leaders",
                f"{users} can't be wrong"
            ],
            CopyType.TAGLINE: [
                f"Trusted by thousands",
                f"The popular choice",
                f"Join the success"
            ],
            CopyType.DESCRIPTION: [
                f"Over {users} users have discovered {benefit} with {product_name}. Join the community of successful leaders who trust our solution.",
                f"When {users} people choose {product_name} for {benefit}, you know it works. Join the movement today."
            ],
            CopyType.VALUE_PROPOSITION: [
                f"{users} users achieve {benefit} with {product_name}. Join them.",
                f"The trusted choice for {benefit}. Join {users} satisfied users."
            ],
            CopyType.CALL_TO_ACTION: [
                f"Join {users} successful users",
                f"Start your success story",
                f"Join the trusted community"
            ]
        }
        
        return templates.get(copy_type, [f"Join {users} using {product_name}"])[0]
    
    def _generate_scarcity_copy(self, product_info: Dict[str, Any], copy_type: CopyType, tone: Tone) -> str:
        """Generate copy using scarcity principles"""
        product_name = product_info.get("name", "product")
        benefit = product_info.get("key_benefit", "great results")
        
        templates = {
            CopyType.HEADLINE: [
                f"Limited access to {benefit}",
                f"Don't miss {product_name}",
                f"Exclusive {benefit} ends soon"
            ],
            CopyType.TAGLINE: [
                f"Limited time, unlimited results",
                f"Exclusive access",
                f"Don't miss out"
            ],
            CopyType.DESCRIPTION: [
                f"This is your limited opportunity to experience {benefit} with {product_name}. Exclusive access is ending soon – don't miss your chance.",
                f"Only a few spots remain for {benefit} with {product_name}. This exclusive offer won't last forever."
            ],
            CopyType.VALUE_PROPOSITION: [
                f"Limited time to get {benefit} with {product_name}. Act now.",
                f"Exclusive access to {benefit}. Limited spots available."
            ],
            CopyType.CALL_TO_ACTION: [
                f"Get {benefit} before it's too late",
                f"Claim your spot now",
                f"Don't miss this opportunity"
            ]
        }
        
        return templates.get(copy_type, [f"Limited {benefit} with {product_name}"])[0]
    
    def _generate_contrast_copy(self, product_info: Dict[str, Any], copy_type: CopyType, tone: Tone) -> str:
        """Generate copy using contrast principles"""
        product_name = product_info.get("name", "product")
        benefit = product_info.get("key_benefit", "great results")
        alternative = product_info.get("alternative", "traditional methods")
        
        templates = {
            CopyType.HEADLINE: [
                f"{product_name} vs {alternative}: No contest",
                f"Better than {alternative}",
                f"Unlike anything else"
            ],
            CopyType.TAGLINE: [
                f"Superior by design",
                f"The better choice",
                f"Unlike the rest"
            ],
            CopyType.DESCRIPTION: [
                f"Unlike {alternative} that leave you wanting more, {product_name} delivers {benefit} every time. The difference is clear.",
                f"While others struggle with {alternative}, {product_name} users enjoy {benefit}. Compare and see the superior results."
            ],
            CopyType.VALUE_PROPOSITION: [
                f"Better than {alternative}: {product_name} delivers {benefit}.",
                f"Choose superior results. Choose {product_name} over {alternative}."
            ],
            CopyType.CALL_TO_ACTION: [
                f"Choose the better solution",
                f"Upgrade from {alternative}",
                f"Experience the difference"
            ]
        }
        
        return templates.get(copy_type, [f"Better than {alternative} with {product_name}"])[0]
    
    def _generate_copy_variant(self, product_info: Dict[str, Any], principle: NeurosciencePrinciple, copy_type: CopyType, tone: Tone) -> CopyVariant:
        """Generate a single copy variant"""
        # Generate copy based on principle
        if principle == NeurosciencePrinciple.LIMBIC:
            text = self._generate_limbic_copy(product_info, copy_type, tone)
        elif principle == NeurosciencePrinciple.PATTERN:
            text = self._generate_pattern_copy(product_info, copy_type, tone)
        elif principle == NeurosciencePrinciple.SIMPLICITY:
            text = self._generate_simplicity_copy(product_info, copy_type, tone)
        elif principle == NeurosciencePrinciple.SOCIAL_PROOF:
            text = self._generate_social_proof_copy(product_info, copy_type, tone)
        elif principle == NeurosciencePrinciple.SCARCITY:
            text = self._generate_scarcity_copy(product_info, copy_type, tone)
        elif principle == NeurosciencePrinciple.CONTRAST:
            text = self._generate_contrast_copy(product_info, copy_type, tone)
        else:
            text = f"{product_info.get('name', 'Product')} delivers {product_info.get('key_benefit', 'results')}"
        
        # Calculate scores
        emotional_impact = self._calculate_emotional_impact(text)
        clarity_score = self._calculate_clarity_score(text)
        persuasion_score = self._calculate_persuasion_score(text, principle)
        effectiveness_score = (emotional_impact + clarity_score + persuasion_score) / 3
        
        # Generate explanation
        principle_info = self.principle_templates[principle]
        explanation = f"Uses {principle.value} principle: {principle_info['description']}. "
        explanation += f"Leverages {', '.join(principle_info['techniques'][:2])} for maximum impact."
        
        return CopyVariant(
            id=self._generate_copy_id(),
            text=text,
            principle=principle,
            copy_type=copy_type,
            tone=tone,
            effectiveness_score=effectiveness_score,
            emotional_impact=emotional_impact,
            clarity_score=clarity_score,
            persuasion_score=persuasion_score,
            explanation=explanation
        )
    
    async def generate_copy_variants(self, product_info: Dict[str, Any], copy_types: List[CopyType] = None, tones: List[Tone] = None) -> List[CopyVariant]:
        """
        Generate copy variants using neuroscience principles
        
        Args:
            product_info: Product information including name, benefits, target audience
            copy_types: Types of copy to generate (optional)
            tones: Tones to use (optional)
        
        Returns:
            List of CopyVariant objects
        """
        if copy_types is None:
            copy_types = [CopyType.HEADLINE, CopyType.TAGLINE, CopyType.DESCRIPTION, CopyType.VALUE_PROPOSITION, CopyType.CALL_TO_ACTION]
        
        if tones is None:
            tones = [Tone.PROFESSIONAL, Tone.CONFIDENT, Tone.EMPATHETIC]
        
        variants = []
        
        # Generate variants for each combination of principle, copy type, and tone
        for principle in NeurosciencePrinciple:
            for copy_type in copy_types:
                for tone in tones:
                    variant = self._generate_copy_variant(product_info, principle, copy_type, tone)
                    variants.append(variant)
        
        # Sort by effectiveness score
        variants.sort(key=lambda x: x.effectiveness_score, reverse=True)
        
        return variants
    
    def analyze_copy_variants(self, variants: List[CopyVariant]) -> CopyAnalysis:
        """Analyze copy variants and provide insights"""
        if not variants:
            return CopyAnalysis(
                total_variants=0,
                best_variant=None,
                principle_distribution={},
                tone_distribution={},
                average_scores={},
                recommendations=[]
            )
        
        # Find best variant
        best_variant = max(variants, key=lambda x: x.effectiveness_score)
        
        # Calculate distributions
        principle_distribution = {}
        for variant in variants:
            principle = variant.principle.value
            principle_distribution[principle] = principle_distribution.get(principle, 0) + 1
        
        tone_distribution = {}
        for variant in variants:
            tone = variant.tone.value
            tone_distribution[tone] = tone_distribution.get(tone, 0) + 1
        
        # Calculate average scores
        total_variants = len(variants)
        avg_effectiveness = sum(v.effectiveness_score for v in variants) / total_variants
        avg_emotional = sum(v.emotional_impact for v in variants) / total_variants
        avg_clarity = sum(v.clarity_score for v in variants) / total_variants
        avg_persuasion = sum(v.persuasion_score for v in variants) / total_variants
        
        average_scores = {
            "effectiveness": avg_effectiveness,
            "emotional_impact": avg_emotional,
            "clarity": avg_clarity,
            "persuasion": avg_persuasion
        }
        
        # Generate recommendations
        recommendations = []
        
        if avg_effectiveness < 0.7:
            recommendations.append("Consider refining product information for better copy generation")
        
        if avg_clarity < 0.6:
            recommendations.append("Focus on simplifying language for better clarity")
        
        if avg_emotional < 0.5:
            recommendations.append("Add more emotional language to increase impact")
        
        # Recommend best performing principle
        if principle_distribution:
            best_principle = max(principle_distribution.items(), key=lambda x: x[1])[0]
            recommendations.append(f"Principle '{best_principle}' shows strong performance - consider focusing on it")
        
        return CopyAnalysis(
            total_variants=total_variants,
            best_variant=best_variant,
            principle_distribution=principle_distribution,
            tone_distribution=tone_distribution,
            average_scores=average_scores,
            recommendations=recommendations
        )
    
    async def generate_copywriting_campaign(self, product_info: Dict[str, Any]) -> CopywritingResult:
        """
        Generate complete copywriting campaign with analysis
        
        Args:
            product_info: Product information
        
        Returns:
            CopywritingResult with variants and analysis
        """
        # Generate all variants
        variants = await self.generate_copy_variants(product_info)
        
        # Analyze variants
        analysis = self.analyze_copy_variants(variants)
        
        # Generate audience insights
        target_audience = product_info.get("target_audience", "professionals")
        audience_insights = [
            f"Target audience: {target_audience}",
            "Emotional appeals will resonate with decision-makers",
            "Social proof elements will build trust",
            "Clear value propositions needed for B2B audience"
        ]
        
        # Generate psychological triggers
        psychological_triggers = [
            "Loss aversion - fear of missing out on benefits",
            "Social validation - need to belong to successful group",
            "Authority bias - trust in proven solutions",
            "Reciprocity - value exchange mindset",
            "Commitment consistency - desire for logical decisions"
        ]
        
        # Generate A/B test recommendations
        top_variants = variants[:10]  # Top 10 variants
        ab_test_recommendations = []
        
        # Group by copy type for testing
        copy_type_groups = {}
        for variant in top_variants:
            copy_type = variant.copy_type.value
            if copy_type not in copy_type_groups:
                copy_type_groups[copy_type] = []
            copy_type_groups[copy_type].append(variant)
        
        for copy_type, type_variants in copy_type_groups.items():
            if len(type_variants) >= 2:
                ab_test_recommendations.append({
                    "test_name": f"{copy_type.title()} A/B Test",
                    "variant_a": type_variants[0].text,
                    "variant_b": type_variants[1].text,
                    "hypothesis": f"Testing {type_variants[0].principle.value} vs {type_variants[1].principle.value} principles",
                    "success_metric": "Conversion rate"
                })
        
        # Generate implementation guide
        implementation_guide = {
            "headline": "Use the highest-scoring headline variant",
            "tagline": "Select tagline with best emotional impact",
            "description": "Choose description with highest clarity score",
            "cta": "Use call-to-action with strongest persuasion score",
            "testing": "Implement A/B tests for continuous optimization"
        }
        
        return CopywritingResult(
            variants=variants,
            analysis=analysis,
            target_audience_insights=audience_insights,
            psychological_triggers=psychological_triggers,
            ab_test_recommendations=ab_test_recommendations,
            implementation_guide=implementation_guide
        )
