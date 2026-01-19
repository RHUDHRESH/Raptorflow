"""
Proof Point Validator Agent
Validates and scores claims with supporting evidence
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class ProofType(Enum):
    """Types of proof evidence"""
    STATISTIC = "statistic"  # Numbers, percentages, metrics
    TESTIMONIAL = "testimonial"  # Customer quotes, reviews
    CASE_STUDY = "case_study"  # Detailed success stories
    AWARD = "award"  # Industry recognition
    CERTIFICATION = "certification"  # Third-party certifications
    RESEARCH = "research"  # Studies, whitepapers
    MEDIA = "media"  # Press mentions, articles
    DEMONSTRATION = "demonstration"  # Product demos, trials
    COMPARISON = "comparison"  # Competitive benchmarks


class VerificationStatus(Enum):
    """Claim verification status"""
    VERIFIED = "verified"
    PARTIALLY_VERIFIED = "partially_verified"
    UNVERIFIED = "unverified"
    DISPUTED = "disputed"
    NEEDS_EVIDENCE = "needs_evidence"


class ClaimStrength(Enum):
    """Strength of claim"""
    STRONG = "strong"  # Well-supported, specific, verifiable
    MODERATE = "moderate"  # Some support, could be stronger
    WEAK = "weak"  # Vague, unsupported, or generic


@dataclass
class ProofPoint:
    """A piece of supporting evidence"""
    id: str
    proof_type: ProofType
    content: str
    source: str
    source_url: Optional[str] = None
    date: Optional[str] = None
    credibility_score: float = 0.5  # 0-1
    relevance_score: float = 0.5  # 0-1
    specificity_score: float = 0.5  # 0-1


@dataclass
class ClaimValidation:
    """Validation result for a claim"""
    claim_id: str
    claim_text: str
    claim_category: str  # speed, quality, price, feature, outcome
    status: VerificationStatus
    strength: ClaimStrength
    confidence_score: float  # 0-1
    proof_points: List[ProofPoint]
    recommendations: List[str]
    improved_claim: Optional[str] = None
    risk_notes: Optional[str] = None


@dataclass
class ValidationResult:
    """Complete validation result"""
    validations: List[ClaimValidation]
    overall_score: float
    strong_claims: int
    weak_claims: int
    needs_evidence: int
    recommendations: List[str]
    summary: str


class ProofPointValidator:
    """AI-powered proof point validation agent"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.proof_counter = 0
        self.claim_counter = 0
        self.claim_patterns = self._load_claim_patterns()
        self.proof_indicators = self._load_proof_indicators()
    
    def _load_claim_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for categorizing claims"""
        return {
            "speed": ["faster", "quick", "instant", "minutes", "seconds", "real-time", "immediate"],
            "quality": ["best", "superior", "premium", "high-quality", "enterprise-grade", "reliable"],
            "price": ["affordable", "cost-effective", "save", "cheaper", "value", "ROI", "free"],
            "feature": ["only", "unique", "first", "exclusive", "patented", "proprietary"],
            "outcome": ["increase", "improve", "boost", "reduce", "eliminate", "achieve", "results"]
        }
    
    def _load_proof_indicators(self) -> Dict[str, float]:
        """Load indicators that suggest proof strength"""
        return {
            # Strong indicators
            "%": 0.8,
            "case study": 0.9,
            "according to": 0.7,
            "verified by": 0.9,
            "certified": 0.85,
            "awarded": 0.8,
            "published": 0.75,
            # Moderate indicators
            "customers say": 0.6,
            "users report": 0.6,
            "on average": 0.65,
            # Weak indicators
            "we believe": 0.2,
            "probably": 0.15,
            "might": 0.1,
        }
    
    def _generate_proof_id(self) -> str:
        """Generate unique proof ID"""
        self.proof_counter += 1
        return f"PRF-{self.proof_counter:03d}"
    
    def _generate_claim_id(self) -> str:
        """Generate unique claim ID"""
        self.claim_counter += 1
        return f"CLM-{self.claim_counter:03d}"
    
    def _categorize_claim(self, claim_text: str) -> str:
        """Categorize a claim based on patterns"""
        claim_lower = claim_text.lower()
        
        scores = {}
        for category, patterns in self.claim_patterns.items():
            score = sum(1 for p in patterns if p in claim_lower)
            scores[category] = score
        
        if max(scores.values()) == 0:
            return "general"
        
        return max(scores, key=scores.get)
    
    def _assess_claim_strength(self, claim_text: str, proof_points: List[ProofPoint]) -> Tuple[ClaimStrength, float]:
        """Assess the strength of a claim based on proof"""
        claim_lower = claim_text.lower()
        
        # Base score from proof points
        if not proof_points:
            return ClaimStrength.WEAK, 0.2
        
        avg_credibility = sum(p.credibility_score for p in proof_points) / len(proof_points)
        avg_relevance = sum(p.relevance_score for p in proof_points) / len(proof_points)
        avg_specificity = sum(p.specificity_score for p in proof_points) / len(proof_points)
        
        # Check for strong/weak language
        strength_modifier = 0
        for indicator, score in self.proof_indicators.items():
            if indicator in claim_lower:
                strength_modifier = max(strength_modifier, score - 0.5)
        
        # Calculate overall score
        base_score = (avg_credibility * 0.4 + avg_relevance * 0.3 + avg_specificity * 0.3)
        final_score = min(1.0, max(0.0, base_score + strength_modifier))
        
        # Determine strength level
        if final_score >= 0.7:
            return ClaimStrength.STRONG, final_score
        elif final_score >= 0.4:
            return ClaimStrength.MODERATE, final_score
        else:
            return ClaimStrength.WEAK, final_score
    
    def _determine_verification_status(self, claim_text: str, proof_points: List[ProofPoint]) -> VerificationStatus:
        """Determine verification status based on proof"""
        if not proof_points:
            return VerificationStatus.NEEDS_EVIDENCE
        
        avg_credibility = sum(p.credibility_score for p in proof_points) / len(proof_points)
        
        # Check for specific proof types
        has_hard_proof = any(p.proof_type in [ProofType.STATISTIC, ProofType.CASE_STUDY, ProofType.CERTIFICATION] for p in proof_points)
        
        if avg_credibility >= 0.8 and has_hard_proof:
            return VerificationStatus.VERIFIED
        elif avg_credibility >= 0.5:
            return VerificationStatus.PARTIALLY_VERIFIED
        else:
            return VerificationStatus.UNVERIFIED
    
    def _generate_improved_claim(self, claim_text: str, strength: ClaimStrength, proof_points: List[ProofPoint]) -> Optional[str]:
        """Generate an improved version of a weak claim"""
        if strength == ClaimStrength.STRONG:
            return None
        
        # Find strongest proof point
        if proof_points:
            best_proof = max(proof_points, key=lambda p: p.credibility_score)
            
            # Add specificity from proof
            if best_proof.proof_type == ProofType.STATISTIC:
                return f"{claim_text} — backed by data showing {best_proof.content}"
            elif best_proof.proof_type == ProofType.CASE_STUDY:
                return f"{claim_text}, as demonstrated by {best_proof.source}"
        
        # Generic improvement suggestions
        vague_words = ["best", "great", "amazing", "revolutionary"]
        improved = claim_text
        for word in vague_words:
            if word in improved.lower():
                improved = improved.replace(word, "[SPECIFIC METRIC]")
        
        return improved if improved != claim_text else None
    
    def _generate_recommendations(self, claim_text: str, status: VerificationStatus, strength: ClaimStrength) -> List[str]:
        """Generate recommendations for improving a claim"""
        recommendations = []
        
        if status == VerificationStatus.NEEDS_EVIDENCE:
            recommendations.append("Add supporting evidence: customer quote, statistic, or case study")
        
        if strength == ClaimStrength.WEAK:
            recommendations.append("Replace vague language with specific, measurable outcomes")
            recommendations.append("Consider adding a timeframe or quantifiable result")
        
        if "best" in claim_text.lower() or "only" in claim_text.lower():
            recommendations.append("Superlative claims require strong third-party validation")
        
        if not any(char.isdigit() for char in claim_text):
            recommendations.append("Add specific numbers or percentages to strengthen claim")
        
        return recommendations
    
    def _extract_proof_from_evidence(self, evidence: Dict[str, Any]) -> List[ProofPoint]:
        """Extract proof points from evidence data"""
        proof_points = []
        
        content = evidence.get("content", "") or evidence.get("extracted_text", "")
        source = evidence.get("source", "") or evidence.get("filename", "")
        
        # Look for statistics
        stat_pattern = r'\d+(?:\.\d+)?%|\$[\d,]+(?:\.\d+)?[KMB]?|\d+x|\d+ out of \d+'
        stats = re.findall(stat_pattern, content)
        for stat in stats[:3]:  # Limit to 3
            proof_points.append(ProofPoint(
                id=self._generate_proof_id(),
                proof_type=ProofType.STATISTIC,
                content=stat,
                source=source,
                credibility_score=0.75,
                relevance_score=0.7,
                specificity_score=0.85
            ))
        
        # Look for testimonials (quoted text)
        quote_pattern = r'"([^"]{20,200})"'
        quotes = re.findall(quote_pattern, content)
        for quote in quotes[:2]:
            proof_points.append(ProofPoint(
                id=self._generate_proof_id(),
                proof_type=ProofType.TESTIMONIAL,
                content=quote[:100] + "..." if len(quote) > 100 else quote,
                source=source,
                credibility_score=0.65,
                relevance_score=0.6,
                specificity_score=0.7
            ))
        
        return proof_points
    
    async def validate_claims(self, claims: List[str], evidence: List[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate a list of claims against available evidence
        
        Args:
            claims: List of claim strings to validate
            evidence: Optional list of evidence documents
        
        Returns:
            ValidationResult with detailed validation for each claim
        """
        evidence = evidence or []
        
        # Extract all proof points from evidence
        all_proof_points = []
        for ev in evidence:
            all_proof_points.extend(self._extract_proof_from_evidence(ev))
        
        validations = []
        for claim in claims:
            claim_id = self._generate_claim_id()
            category = self._categorize_claim(claim)
            
            # Find relevant proof points for this claim
            relevant_proofs = self._find_relevant_proofs(claim, all_proof_points)
            
            # Assess strength and status
            strength, confidence = self._assess_claim_strength(claim, relevant_proofs)
            status = self._determine_verification_status(claim, relevant_proofs)
            
            # Generate improvements and recommendations
            improved = self._generate_improved_claim(claim, strength, relevant_proofs)
            recommendations = self._generate_recommendations(claim, status, strength)
            
            validation = ClaimValidation(
                claim_id=claim_id,
                claim_text=claim,
                claim_category=category,
                status=status,
                strength=strength,
                confidence_score=confidence,
                proof_points=relevant_proofs,
                recommendations=recommendations,
                improved_claim=improved,
                risk_notes="Superlative claim requires strong validation" if "best" in claim.lower() else None
            )
            validations.append(validation)
        
        # Calculate overall metrics
        strong_count = sum(1 for v in validations if v.strength == ClaimStrength.STRONG)
        weak_count = sum(1 for v in validations if v.strength == ClaimStrength.WEAK)
        needs_evidence_count = sum(1 for v in validations if v.status == VerificationStatus.NEEDS_EVIDENCE)
        
        overall_score = sum(v.confidence_score for v in validations) / len(validations) if validations else 0
        
        # Generate overall recommendations
        overall_recommendations = []
        if weak_count > len(validations) / 2:
            overall_recommendations.append("More than half of claims are weak - focus on adding specific proof points")
        if needs_evidence_count > 0:
            overall_recommendations.append(f"{needs_evidence_count} claims need supporting evidence")
        if strong_count == 0:
            overall_recommendations.append("No strong claims - prioritize strengthening your best differentiators")
        
        summary = f"Validated {len(claims)} claims: {strong_count} strong, {len(validations) - strong_count - weak_count} moderate, {weak_count} weak. "
        summary += f"Overall proof score: {overall_score:.0%}."
        
        return ValidationResult(
            validations=validations,
            overall_score=overall_score,
            strong_claims=strong_count,
            weak_claims=weak_count,
            needs_evidence=needs_evidence_count,
            recommendations=overall_recommendations,
            summary=summary
        )
    
    def _find_relevant_proofs(self, claim: str, proof_points: List[ProofPoint]) -> List[ProofPoint]:
        """Find proof points relevant to a specific claim"""
        claim_words = set(claim.lower().split())
        
        relevant = []
        for proof in proof_points:
            proof_words = set(proof.content.lower().split())
            overlap = len(claim_words & proof_words)
            if overlap >= 2 or proof.relevance_score > 0.7:
                # Update relevance based on overlap
                proof.relevance_score = min(1.0, proof.relevance_score + overlap * 0.1)
                relevant.append(proof)
        
        return relevant[:5]  # Max 5 proof points per claim
    
    def get_validation_summary(self, result: ValidationResult) -> Dict[str, Any]:
        """Get summary for display"""
        return {
            "total_claims": len(result.validations),
            "strong_claims": result.strong_claims,
            "weak_claims": result.weak_claims,
            "needs_evidence": result.needs_evidence,
            "overall_score": result.overall_score,
            "summary": result.summary,
            "top_recommendations": result.recommendations[:3]
        }
