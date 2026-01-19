"""
Evidence Classifier Agent
Automatically detects document types and categorizes evidence with AI-powered analysis
"""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import re
import os
import mimetypes
from datetime import datetime

logger = logging.getLogger(__name__)


class EvidenceType(Enum):
    """Types of evidence documents"""
    PITCH_DECK = "pitch_deck"
    PRODUCT_SCREENSHOT = "product_screenshot"
    WEBSITE_CONTENT = "website_content"
    FINANCIAL_DOCUMENT = "financial_document"
    LEGAL_DOCUMENT = "legal_document"
    MARKETING_MATERIAL = "marketing_material"
    USER_TESTIMONIAL = "user_testimonial"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    MARKET_RESEARCH = "market_research"
    OTHER = "other"


@dataclass
class ClassificationResult:
    """Result of evidence classification"""
    evidence_type: EvidenceType
    confidence: float
    reasoning: str
    key_indicators: List[str]
    metadata: Dict[str, Any]


class EvidenceClassifier:
    """AI-powered evidence classification specialist with enhanced auto-recognition"""
    
    def __init__(self):
        self.classification_rules = self._load_classification_rules()
        self.logger = logging.getLogger(__name__)
        self.recommended_evidence = []
        self.classification_history = []
    
    def _load_classification_rules(self) -> Dict[EvidenceType, Dict[str, Any]]:
        """Load enhanced classification rules with AI-powered patterns"""
        return {
            EvidenceType.PITCH_DECK: {
                "keywords": ["pitch", "deck", "funding", "investment", "round", "seed", "series", "valuation", "traction", "executive", "founder", "mission", "vision", "problem", "solution", "market", "traction"],
                "file_patterns": [".pdf", ".pptx", ".ppt"],
                "content_patterns": [
                    r"(?:executive summary|team|founder|mission|vision|problem|solution|market|traction|traction|traction)",
                    r"(?:revenue|profit|growth|metrics|kpi|okr|traction)",
                    r"(?:seed|series|angel|vc|venture|capital|funding|startup|business)",
                    r"(?:traction|traction|traction|traction|traction|traction)",
                    r"(?:traction|traction|traction|traction|traction|traction)"
                ],
                "confidence_threshold": 0.7,
                "recommended": True,
                "description": "Investment pitch deck for funding"
            },
            EvidenceType.PRODUCT_SCREENSHOT: {
                "keywords": ["screenshot", "ui", "interface", "product", "app", "software", "tool", "platform", "dashboard", "login", "signup"],
                "file_patterns": [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".png"],
                "content_patterns": [
                    r"(?:dashboard|login|signup|settings|profile|navigation|menu|button|form)",
                    r"(?:feature|function|module|page|screen|view|interface|component)",
                    r"(?:user experience|ux|ui design|layout|visual|design|wireframe)",
                    r"(?:prototype|mockup|design|concept|screenshot|screen capture)"
                ],
                "confidence_threshold": 0.6,
                "recommended": True,
                "description": "Product interface screenshot"
            },
            EvidenceType.WEBSITE_CONTENT: {
                "keywords": ["website", "webpage", "blog", "article", "content", "copy", "text", "about", "services", "products"],
                "file_patterns": [".html", ".htm", ".txt", ".md", ".json"],
                "content_patterns": [
                    r"(?:http|www\.|\.com|\.org|\.io|\.co|\.net|\.ai)",
                    r"(?:about|contact|services|products|pricing|blog|news|team)",
                    r"(?:navigation|header|footer|sidebar|menu|content|main)",
                    r"(?:homepage|landing page|home|index|default)"
                ],
                "confidence_threshold": 0.5,
                "recommended": False,
                "description": "Website content or copy"
            },
            EvidenceType.FINANCIAL_DOCUMENT: {
                "keywords": ["financial", "statement", "balance", "income", "expense", "budget", "forecast", "p&l", "cash flow", "profit", "loss", "revenue"],
                "file_patterns": [".pdf", ".xlsx", ".xls", ".csv", ".doc", ".docx"],
                "content_patterns": [
                    r"(?:revenue|profit|loss|income|expense|budget|forecast|projection|financial)",
                    r"(?:balance|statement|sheet|cash|flow|equity|assets|liabilities|capital)",
                    r"(?:q[1-4]|quarterly|annual|monthly|fiscal year|fy|income statement)",
                    r"(?:tax|audit|compliance|regulatory|sec|gaap|ifrs)"
                ],
                "confidence_threshold": 0.8,
                "recommended": True,
                "description": "Financial statements and reports"
            },
            EvidenceType.LEGAL_DOCUMENT: {
                "keywords": ["legal", "contract", "agreement", "terms", "policy", "compliance", "regulation", "nda", "ip", "trademark"],
                "file_patterns": [".pdf", ".doc", ".docx", ".txt", ".rtf"],
                "content_patterns": [
                    r"(?:terms of service|privacy policy|user agreement|contract|agreement)",
                    r"(?:legal|attorney|counsel|compliance|regulatory|governance|lawyer)",
                    r"(?:liability|indemnification|warranty|guarantee|obligation|responsibility)",
                    r"(?:confidential|proprietary|intellectual property|copyright|patent|trademark)"
                ],
                "confidence_threshold": 0.8,
                "recommended": True,
                "description": "Legal documents and agreements"
            },
            EvidenceType.MARKETING_MATERIAL: {
                "keywords": ["marketing", "brochure", "flyer", "advertisement", "campaign", "promo", "brand", "collateral", "materials"],
                "file_patterns": [".pdf", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".psd", ".ai", ".eps"],
                "content_patterns": [
                    r"(?:campaign|promotion|advertisement|marketing|branding|advertising|social media)",
                    r"(?:brochure|flyer|catalog|specification|features|benefits|collateral)",
                    r"(?:call to action|cta|offer|discount|promotion|special deal|limited time)",
                    r"(|brand guidelines|style guide|logo|visual identity|brand identity)"
                ],
                "confidence_threshold": 0.6,
                "recommended": False,
                "description": "Marketing and promotional materials"
            },
            EvidenceType.USER_TESTIMONIAL: {
                "keywords": ["testimonial", "review", "feedback", "rating", "customer", "client", "user", "satisfied", "experience"],
                "file_patterns": [".txt", ".doc", ".docx", ".pdf", ".jpg", ".png", ".jpeg", ".video"],
                "content_patterns": [
                    r"(?:testimonial|review|feedback|rating|stars|score|opinion|experience|satisfied)",
                    r"(?:customer|client|user|happy|pleased|impressed|love|recommend)",
                    r"(?:endorsement|praise|compliment|appreciation|positive feedback)",
                    r"(?:case study|success story|result|outcome|achievement)"
                ],
                "confidence_threshold": 0.7,
                "recommended": False,
                "description": "Customer testimonials and reviews"
            },
            EvidenceType.COMPETITOR_ANALYSIS: {
                "keywords": ["competitor", "competition", "analysis", "comparison", "vs", "versus", "alternative", "market share", "positioning"],
                "file_patterns": [".pdf", ".doc", ".docx", ".txt", ".xlsx", ".xls", ".ppt", ".pptx"],
                "content_patterns": [
                    r"(?:competitor|competition|analysis|comparison|vs|versus|alternative|market share)",
                    r"(?:strengths|weaknesses|advantages|disadvantages|pros|cons|swot)",
                    r"(?:positioning|differentiation|value proposition|unique selling proposition)",
                    r"(|market|industry|landscape|players|leaders|followers|users)"
                ],
                "confidence_threshold": 0.7,
                "recommended": False,
                "description": "Competitor analysis and market research"
            },
            EvidenceType.MARKET_RESEARCH: {
                "keywords": ["research", "study", "report", "survey", "analysis", "insights", "findings", "data", "statistics", "trends"],
                "file_patterns": [".pdf", ".doc", ".docx", ".txt", ".xlsx", ".xls", ".ppt", ".pptx", ".csv"],
                "content_patterns": [
                    r"(?:research|study|report|survey|analysis|insights|findings|data|statistics|trends)",
                    r"(?:market|industry|trend|opportunity|challenge|growth|forecast)",
                    r"(|data|statistics|metrics|benchmark|projection|projection|survey|poll)",
                    r"(|demographics|psychographics|behaviors|preferences|insights)"
                ],
                "confidence_threshold": 0.6,
                "recommended": False,
                "description": "Market research and analysis reports"
            },
            EvidenceType.OTHER: {
                "keywords": [],
                "file_patterns": [],
                "content_patterns": [],
                "confidence_threshold": 0.3,
                "recommended": False,
                "description": "Other documents"
            }
        }
    
    async def classify_evidence(self, evidence: Dict[str, Any]) -> ClassificationResult:
        """
        Classify evidence based on content, filename, and metadata
        
        Args:
            evidence: Dictionary containing evidence data with keys:
                - filename: str
                - content_type: str
                - extracted_text: str (optional)
                - url: str (optional for web content)
                - size: int
                - metadata: dict (optional)
        
        Returns:
            ClassificationResult with type, confidence, and reasoning
        """
        try:
            filename = evidence.get("filename", "")
            content_type = evidence.get("content_type", "")
            extracted_text = evidence.get("extracted_text", "")
            url = evidence.get("url", "")
            size = evidence.get("size", 0)
            
            # Get file extension
            file_ext = ""
            if filename:
                file_ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
            
            # Calculate scores for each evidence type
            scores = {}
            for evidence_type, rules in self.classification_rules.items():
                score = 0.0
                indicators = []
                
                # Check filename keywords
                filename_lower = filename.lower()
                for keyword in rules["keywords"]:
                    if keyword in filename_lower:
                        score += 0.3
                        indicators.append(f"Filename contains '{keyword}'")
                
                # Check file extension
                if file_ext in rules["file_patterns"]:
                    score += 0.2
                    indicators.append(f"File extension '{file_ext}' matches")
                
                # Check content keywords
                if extracted_text:
                    text_lower = extracted_text.lower()
                    for keyword in rules["keywords"]:
                        if keyword in text_lower:
                            score += 0.3
                            indicators.append(f"Content contains '{keyword}'")
                    
                    # Check content patterns
                    for pattern in rules["content_patterns"]:
                        if pattern in text_lower:
                            score += 0.2
                            indicators.append(f"Content pattern '{pattern}' found")
                
                # Check URL patterns for web content
                if url and evidence_type == EvidenceType.WEBSITE_CONTENT:
                    if any(domain in url for domain in ["http://", "https://", "www."]):
                        score += 0.4
                        indicators.append("URL indicates website content")
                
                # Check content type
                if content_type:
                    if evidence_type == EvidenceType.PRODUCT_SCREENSHOT and "image" in content_type:
                        score += 0.3
                        indicators.append("Content type indicates image")
                    elif evidence_type == EvidenceType.WEBSITE_CONTENT and "html" in content_type:
                        score += 0.3
                        indicators.append("Content type indicates HTML")
                
                scores[evidence_type] = {
                    "score": score,
                    "indicators": indicators
                }
            
            # Find best match
            best_type = EvidenceType.OTHER
            best_score = 0.0
            best_indicators = []
            
            for evidence_type, result in scores.items():
                if result["score"] > best_score:
                    best_score = result["score"]
                    best_type = evidence_type
                    best_indicators = result["indicators"]
            
            # Apply minimum confidence thresholds
            min_confidence = self.classification_rules.get(best_type, {}).get("min_confidence", 0.5)
            if best_score < min_confidence:
                best_type = EvidenceType.OTHER
                best_indicators = ["Low confidence for all types"]
                best_score = 0.3
            
            # Generate reasoning
            reasoning = f"Classified as {best_type.value} with confidence {best_score:.2f}. "
            if best_indicators:
                reasoning += "Key indicators: " + ", ".join(best_indicators[:3])  # Limit to top 3
            
            return ClassificationResult(
                evidence_type=best_type,
                confidence=best_score,
                reasoning=reasoning,
                key_indicators=best_indicators,
                metadata={
                    "classification_scores": {k.value: v["score"] for k, v in scores.items()},
                    "file_extension": file_ext,
                    "content_type": content_type,
                    "evidence_size": size
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error classifying evidence: {str(e)}")
            return ClassificationResult(
                evidence_type=EvidenceType.OTHER,
                confidence=0.0,
                reasoning=f"Classification failed: {str(e)}",
                key_indicators=[],
                metadata={"error": str(e)}
            )
    
    async def batch_classify(self, evidence_list: List[Dict[str, Any]]) -> List[ClassificationResult]:
        """Classify multiple evidence items"""
        results = []
        for evidence in evidence_list:
            result = await self.classify_evidence(evidence)
            results.append(result)
        return results
    
    def get_supported_types(self) -> List[str]:
        """Get list of supported evidence types"""
        return [evidence_type.value for evidence_type in EvidenceType]
    
    def get_classification_rules(self) -> Dict[str, Dict[str, Any]]:
        """Get classification rules for UI display"""
        return {
            evidence_type.value: rules for evidence_type, rules in self.classification_rules.items()
        }
    
    def get_recommended_evidence(self) -> List[Dict[str, Any]]:
        """Get recommended evidence types for the onboarding process"""
        recommended = []
        for evidence_type, rules in self.classification_rules.items():
            if rules.get("recommended", False):
                recommended.append({
                    "type": evidence_type.value,
                    "description": rules.get("description", ""),
                    "priority": self._get_priority(evidence_type),
                    "examples": self._get_examples(evidence_type)
                })
        
        # Sort by priority
        recommended.sort(key=lambda x: x["priority"])
        return recommended
    
    def _get_priority(self, evidence_type: EvidenceType) -> int:
        """Get priority level for evidence type"""
        priority_map = {
            EvidenceType.PITCH_DECK: 1,
            EvidenceType.PRODUCT_SCREENSHOT: 2,
            EvidenceType.FINANCIAL_DOCUMENT: 3,
            EvidenceType.LEGAL_DOCUMENT: 4,
            EvidenceType.MARKET_RESEARCH: 5,
            EvidenceType.COMPETITOR_ANALYSIS: 6,
            EvidenceType.USER_TESTIMONIAL: 7,
            EvidenceType.MARKETING_MATERIAL: 8,
            EvidenceType.WEBSITE_CONTENT: 9,
            EvidenceType.OTHER: 10
        }
        return priority_map.get(evidence_type, 10)
    
    def _get_examples(self, evidence_type: EvidenceType) -> List[str]:
        """Get example filenames for evidence type"""
        examples = {
            EvidenceType.PITCH_DECK: [
                "seed_round_pitch_deck.pdf",
                "series_a_presentation.pptx",
                "investor_deck_final.pdf"
            ],
            EvidenceType.PRODUCT_SCREENSHOT: [
                "dashboard_view.png",
                "user_interface_screenshot.jpg",
                "product_demo_screen.png"
            ],
            EvidenceType.FINANCIAL_DOCUMENT: [
                "q3_financial_statements.pdf",
                "annual_report_2024.xlsx",
                "profit_loss_statement.pdf"
            ],
            EvidenceType.LEGAL_DOCUMENT: [
                "terms_of_service.pdf",
                "privacy_policy.docx",
                "user_agreement.pdf"
            ],
            EvidenceType.MARKET_RESEARCH: [
                "market_analysis_report.pdf",
                "industry_insights_2024.pdf",
                "customer_survey_results.xlsx"
            ],
            EvidenceType.COMPETITOR_ANALYSIS: [
                "competitor_landscape.pdf",
                "market_comparison_analysis.pdf",
                "competitive_positioning.docx"
            ],
            EvidenceType.USER_TESTIMONIAL: [
                "customer_testimonials.pdf",
                "client_success_stories.docx",
                "user_feedback_summary.pdf"
            ],
            EvidenceType.MARKETING_MATERIAL: [
                "product_brochure.pdf",
                "marketing_campaign_assets.zip",
                "brand_guidelines.pdf"
            ],
            EvidenceType.WEBSITE_CONTENT: [
                "homepage_content.html",
                "about_us_copy.txt",
                "product_pages_content.md"
            ],
            EvidenceType.OTHER: [
                "misc_document.pdf",
                "additional_info.txt",
                "supporting_material.docx"
            ]
        }
        return examples.get(evidence_type, [])
    
    def analyze_evidence_coverage(self, classified_evidence: List[ClassificationResult]) -> Dict[str, Any]:
        """Analyze coverage of evidence types and identify gaps"""
        type_counts = {}
        confidence_scores = {}
        
        for result in classified_evidence:
            type_name = result.evidence_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
            confidence_scores[type_name] = confidence_scores.get(type_name, []) + [result.confidence]
        
        # Calculate average confidence per type
        avg_confidence = {}
        for type_name, scores in confidence_scores.items():
            avg_confidence[type_name] = sum(scores) / len(scores)
        
        # Identify missing recommended evidence
        recommended_types = [e["type"] for e in self.get_recommended_evidence()]
        missing_recommended = [t for t in recommended_types if t not in type_counts]
        
        # Calculate coverage score
        total_recommended = len(recommended_types)
        covered_recommended = len([t for t in recommended_types if t in type_counts])
        coverage_score = covered_recommended / total_recommended if total_recommended > 0 else 0
        
        return {
            "type_counts": type_counts,
            "average_confidence": avg_confidence,
            "missing_recommended": missing_recommended,
            "coverage_score": coverage_score,
            "total_evidence": len(classified_evidence),
            "recommendations": self._generate_coverage_recommendations(missing_recommended, coverage_score)
        }
    
    def _generate_coverage_recommendations(self, missing_recommended: List[str], coverage_score: float) -> List[str]:
        """Generate recommendations for evidence coverage"""
        recommendations = []
        
        if coverage_score < 0.3:
            recommendations.append("Critical: You need to upload more evidence to complete your onboarding")
        elif coverage_score < 0.6:
            recommendations.append("Important: Add more evidence types to strengthen your business case")
        elif coverage_score < 0.9:
            recommendations.append("Good: Consider adding optional evidence types to complete your profile")
        
        if missing_recommended:
            missing_names = [self.classification_rules[EvidenceType(t)]["description"] for t in missing_recommended if t in [e.value for e in EvidenceType]]
            recommendations.append(f"Missing recommended evidence: {', '.join(missing_names)}")
        
        return recommendations
    
    def get_evidence_insights(self, classified_evidence: List[ClassificationResult]) -> Dict[str, Any]:
        """Get insights about the evidence collection"""
        if not classified_evidence:
            return {"message": "No evidence classified yet"}
        
        # Analyze confidence distribution
        confidences = [r.confidence for r in classified_evidence]
        avg_confidence = sum(confidences) / len(confidences)
        high_confidence = len([c for c in confidences if c >= 0.8])
        low_confidence = len([c for c in confidences if c < 0.5])
        
        # Analyze type distribution
        type_distribution = {}
        for result in classified_evidence:
            type_name = result.evidence_type.value
            type_distribution[type_name] = type_distribution.get(type_name, 0) + 1
        
        # Most common type
        most_common_type = max(type_distribution.items(), key=lambda x: x[1]) if type_distribution else ("other", 0)
        
        return {
            "total_evidence": len(classified_evidence),
            "average_confidence": round(avg_confidence, 2),
            "high_confidence_count": high_confidence,
            "low_confidence_count": low_confidence,
            "type_distribution": type_distribution,
            "most_common_type": most_common_type,
            "quality_score": round(avg_confidence * 0.7 + (len(classified_evidence) / 10) * 0.3, 2),
            "insights": self._generate_evidence_insights(avg_confidence, high_confidence, low_confidence, most_common_type)
        }
    
    def _generate_evidence_insights(self, avg_confidence: float, high_confidence: int, low_confidence: int, most_common_type: tuple) -> List[str]:
        """Generate insights about evidence quality"""
        insights = []
        
        if avg_confidence >= 0.8:
            insights.append("Excellent evidence quality with high confidence classifications")
        elif avg_confidence >= 0.6:
            insights.append("Good evidence quality with moderate confidence classifications")
        else:
            insights.append("Consider improving evidence quality for better classifications")
        
        if high_confidence > len(self.classification_history) * 0.5:
            insights.append("Strong evidence foundation with reliable classifications")
        
        if low_confidence > 0:
            insights.append(f"Some evidence may need manual review ({low_confidence} items)")
        
        if most_common_type[1] > 3:
            insights.append(f"Good coverage of {most_common_type[0]} evidence")
        
        return insights
