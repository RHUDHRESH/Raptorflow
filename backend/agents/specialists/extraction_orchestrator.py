"""
Extraction Orchestrator Agent
Coordinates AI extraction of facts and insights from evidence with enhanced real-time processing
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import json
import asyncio
from datetime import datetime
import hashlib
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


class FactCategory(Enum):
    """Categories of extracted facts"""
    COMPANY = "Company"
    POSITIONING = "Positioning"
    AUDIENCE = "Audience"
    MARKET = "Market"
    PRODUCT = "Product"
    REVENUE = "Revenue"
    TEAM = "Team"
    METRICS = "Metrics"
    COMPETITORS = "Competitors"
    OTHER = "Other"


class FactStatus(Enum):
    """Status of extracted facts"""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"


@dataclass
class ExtractedFact:
    """Represents a single extracted fact"""
    id: str
    category: FactCategory
    label: str
    value: str
    confidence: float
    sources: List[Dict[str, str]]
    status: FactStatus
    code: str
    extraction_method: str
    context: Optional[str] = None
    contradictions: List[str] = None
    
    def __post_init__(self):
        if self.contradictions is None:
            self.contradictions = []


@dataclass
class ExtractionResult:
    """Result of extraction process"""
    facts: List[ExtractedFact]
    summary: str
    warnings: List[str]
    extraction_complete: bool
    processing_time: float
    evidence_processed: int
    confidence_distribution: Dict[str, int]


class ExtractionOrchestrator:
    """Enhanced AI-powered extraction orchestrator with real-time processing"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.extraction_patterns = self._load_extraction_patterns()
        self.fact_counter = 0
        self.extraction_history = []
        self.confidence_thresholds = {
            "high": 0.8,
            "medium": 0.6,
            "low": 0.4
        }
        self.extraction_methods = {
            "pattern_matching": "Pattern-based extraction",
            "keyword_extraction": "Keyword-based extraction",
            "context_analysis": "Context-aware extraction",
            "semantic_analysis": "Semantic pattern extraction",
            "statistical_extraction": "Statistical pattern extraction"
        }
    
    def _load_extraction_patterns(self) -> Dict[FactCategory, Dict[str, Any]]:
        """Load extraction patterns for each fact category"""
        return {
            FactCategory.COMPANY: {
                "patterns": [
                    r"(?:company|startup|business) (?:name|called) ([A-Za-z0-9\s]+)",
                    r"([A-Za-z0-9\s]+) (?:is|was) (?:founded|established|created)",
                    r"we (?:are|build|provide|offer) ([A-Za-z0-9\s]+)"
                ],
                "keywords": ["company", "startup", "business", "organization", "firm"],
                "confidence_threshold": 0.7
            },
            FactCategory.POSITIONING: {
                "patterns": [
                    r"(?:we are|we provide|we offer) ([A-Za-z0-9\s]+)",
                    r"(?:our product|solution|platform) (?:is|provides|offers) ([A-Za-z0-9\s]+)",
                    r"(?:category|market|sector) ([A-Za-z0-9\s]+)"
                ],
                "keywords": ["platform", "solution", "service", "product", "system", "tool"],
                "confidence_threshold": 0.6
            },
            FactCategory.AUDIENCE: {
                "patterns": [
                    r"(?:target|for|serving) ([A-Za-z0-9\s]+) (?:customers|clients|users)",
                    r"(?:our audience|market) (?:is|includes) ([A-Za-z0-9\s]+)",
                    r"(?:designed|built|made) for ([A-Za-z0-9\s]+)"
                ],
                "keywords": ["customers", "users", "clients", "audience", "market", "segment"],
                "confidence_threshold": 0.6
            },
            FactCategory.MARKET: {
                "patterns": [
                    r"(?:market size|market value) (?:is|of) \$?([0-9,.]+)",
                    r"(?:total addressable market|TAM) (?:is|of) \$?([0-9,.]+)",
                    r"(?:industry|sector) (?:size|value) (?:is|of) \$?([0-9,.]+)"
                ],
                "keywords": ["market", "industry", "sector", "TAM", "SAM", "SOM"],
                "confidence_threshold": 0.7
            },
            FactCategory.PRODUCT: {
                "patterns": [
                    r"(?:product|feature|function) ([A-Za-z0-9\s]+)",
                    r"(?:our product|solution) (?:has|includes|offers) ([A-Za-z0-9\s]+)",
                    r"(?:key|main|primary) (?:feature|benefit) (?:is|are) ([A-Za-z0-9\s]+)"
                ],
                "keywords": ["feature", "function", "capability", "benefit", "advantage"],
                "confidence_threshold": 0.6
            },
            FactCategory.REVENUE: {
                "patterns": [
                    r"(?:revenue|income|earnings) (?:of|is) \$?([0-9,.]+)",
                    r"(?:annual|yearly|monthly) (?:revenue|sales) (?:of|is) \$?([0-9,.]+)",
                    r"(?:ARR|MRR) (?:is|of) \$?([0-9,.]+)"
                ],
                "keywords": ["revenue", "income", "sales", "ARR", "MRR", "earnings"],
                "confidence_threshold": 0.8
            },
            FactCategory.TEAM: {
                "patterns": [
                    r"(?:team|founders|employees) (?:size|count) (?:is|of) ([0-9]+)",
                    r"(?:founded by|created by|led by) ([A-Za-z0-9\s]+)",
                    r"(?:CEO|founder|co-founder) (?:is|are) ([A-Za-z0-9\s]+)"
                ],
                "keywords": ["team", "founder", "CEO", "employees", "staff", "leadership"],
                "confidence_threshold": 0.7
            },
            FactCategory.METRICS: {
                "patterns": [
                    r"([0-9,.]+)% (?:growth|increase|decrease)",
                    r"([0-9,.]+) (?:users|customers|clients)",
                    r"([0-9,.]+) (?:monthly|daily|weekly) (?:active|engaged)"
                ],
                "keywords": ["growth", "users", "customers", "active", "engaged", "retention"],
                "confidence_threshold": 0.6
            },
            FactCategory.COMPETITORS: {
                "patterns": [
                    r"(?:competitor|competition|rival) ([A-Za-z0-9\s]+)",
                    r"(?:competing with|against) ([A-Za-z0-9\s]+)",
                    r"(?:alternative to|vs) ([A-Za-z0-9\s]+)"
                ],
                "keywords": ["competitor", "competition", "rival", "alternative", "vs"],
                "confidence_threshold": 0.6
            }
        }
    
    def _generate_fact_id(self, category: FactCategory) -> str:
        """Generate unique fact ID"""
        self.fact_counter += 1
        category_code = category.value.upper()[0:3]
        return f"F-{category_code}-{self.fact_counter:03d}"
    
    def _extract_facts_from_text(self, text: str, source_info: Dict[str, str]) -> List[ExtractedFact]:
        """Extract facts from text using patterns and AI"""
        facts = []
        text_lower = text.lower()
        
        for category, patterns_info in self.extraction_patterns.items():
            category_facts = []
            
            # Try each pattern
            for pattern in patterns_info["patterns"]:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    if len(match.groups()) > 0:
                        value = match.group(1).strip()
                        
                        # Calculate confidence based on context and keywords
                        confidence = 0.5  # Base confidence
                        
                        # Boost confidence if keywords are present
                        for keyword in patterns_info["keywords"]:
                            if keyword in text_lower:
                                confidence += 0.1
                        
                        # Boost confidence based on pattern specificity
                        if len(pattern) > 50:  # More specific patterns
                            confidence += 0.1
                        
                        # Cap confidence
                        confidence = min(confidence, 0.9)
                        
                        # Only include if above threshold
                        if confidence >= patterns_info["confidence_threshold"]:
                            fact = ExtractedFact(
                                id=self._generate_fact_id(category),
                                category=category,
                                label=category.value,
                                value=value,
                                confidence=confidence,
                                sources=[source_info],
                                status=FactStatus.PENDING,
                                code=self._generate_fact_id(category),
                                extraction_method="pattern_matching",
                                context=text[max(0, match.start()-100):match.end()+100]
                            )
                            category_facts.append(fact)
            
            # Remove duplicates (same value in same category)
            seen_values = set()
            unique_facts = []
            for fact in category_facts:
                if fact.value.lower() not in seen_values:
                    seen_values.add(fact.value.lower())
                    unique_facts.append(fact)
            
            facts.extend(unique_facts)
        
        return facts
    
    def _extract_ai_insights(self, text: str, source_info: Dict[str, str]) -> List[ExtractedFact]:
        """Extract facts using AI-powered insights (mock implementation)"""
        # This would integrate with a real AI model in production
        # For now, we'll simulate with some basic heuristics
        
        facts = []
        
        # Look for company descriptions
        if any(word in text.lower() for word in ["we are", "we provide", "we offer", "our mission"]):
            # Extract a reasonable description
            sentences = text.split('.')
            for sentence in sentences:
                if any(word in sentence.lower() for word in ["we are", "we provide", "we offer"]):
                    if len(sentence.strip()) > 20:  # Minimum length
                        fact = ExtractedFact(
                            id=self._generate_fact_id(FactCategory.COMPANY),
                            category=FactCategory.COMPANY,
                            label="Company Description",
                            value=sentence.strip(),
                            confidence=0.7,
                            sources=[source_info],
                            status=FactStatus.PENDING,
                            code=self._generate_fact_id(FactCategory.COMPANY),
                            extraction_method="ai_insight"
                        )
                        facts.append(fact)
                        break
        
        return facts
    
    async def extract_from_evidence(self, evidence_list: List[Dict[str, Any]]) -> ExtractionResult:
        """
        Enhanced extraction from evidence with real-time processing and AI insights
        
        Args:
            evidence_list: List of evidence dictionaries
        
        Returns:
            ExtractionResult with extracted facts and metadata
        """
        start_time = datetime.now()
        
        all_facts = []
        warnings = []
        evidence_processed = 0
        extraction_stats = defaultdict(int)
        
        # Process each evidence item
        for evidence in evidence_list:
            try:
                # Prepare source information
                source_info = {
                    "type": evidence.get("type", "unknown"),
                    "name": evidence.get("filename", evidence.get("url", "unknown")),
                    "id": evidence.get("id", "unknown"),
                    "timestamp": datetime.now().isoformat()
                }
                
                # Get text content
                text_content = ""
                if evidence.get("extracted_text"):
                    text_content = evidence["extracted_text"]
                elif evidence.get("content"):
                    text_content = evidence["content"]
                elif evidence.get("title"):
                    text_content = evidence["title"]
                
                if not text_content:
                    warnings.append(f"No text content found in {source_info['name']}")
                    continue
                
                # Extract facts using multiple methods
                pattern_facts = self._extract_pattern_facts(text_content, source_info)
                keyword_facts = self._extract_keyword_facts(text_content, source_info)
                semantic_facts = await self._extract_semantic_facts(text_content, source_info)
                ai_insights = await self._extract_ai_insights(text_content, source_info)
                
                # Combine and deduplicate facts
                evidence_facts = pattern_facts + keyword_facts + semantic_facts + ai_insights
                evidence_facts = self._deduplicate_facts(evidence_facts)
                
                # Apply confidence filtering
                filtered_facts = [f for f in evidence_facts if f.confidence >= 0.5]
                
                all_facts.extend(filtered_facts)
                evidence_processed += 1
                
                # Update extraction statistics
                for fact in filtered_facts:
                    extraction_stats[fact.category.value] += 1
                    extraction_stats[fact.extraction_method] += 1
                
            except Exception as e:
                self.logger.error(f"Error processing evidence {evidence.get('id', 'unknown')}: {str(e)}")
                warnings.append(f"Failed to process {evidence.get('filename', 'unknown')}: {str(e)}")
                continue
        
        # Post-process facts
        processed_facts = await self._post_process_facts(all_facts)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Generate confidence distribution
        confidence_distribution = self._calculate_confidence_distribution(processed_facts)
        
        # Generate summary
        summary = self._generate_extraction_summary(processed_facts, evidence_processed, extraction_stats)
        
        # Store extraction history
        self.extraction_history.append({
            "timestamp": start_time.isoformat(),
            "evidence_count": len(evidence_list),
            "facts_extracted": len(processed_facts),
            "processing_time": processing_time,
            "extraction_stats": dict(extraction_stats)
        })
        
        return ExtractionResult(
            facts=processed_facts,
            summary=summary,
            warnings=warnings,
            extraction_complete=True,
            processing_time=processing_time,
            evidence_processed=evidence_processed,
            confidence_distribution=confidence_distribution
        )
    
    async def _extract_keyword_facts(self, text: str, source_info: Dict[str, str]) -> List[ExtractedFact]:
        """Extract facts using keyword-based analysis"""
        facts = []
        text_lower = text.lower()
        
        for category, patterns_info in self.extraction_patterns.items():
            keyword_matches = []
            
            # Find keyword matches
            for keyword in patterns_info["keywords"]:
                if keyword in text_lower:
                    # Extract context around keyword
                    keyword_pos = text_lower.find(keyword)
                    if keyword_pos != -1:
                        context_start = max(0, keyword_pos - 50)
                        context_end = min(len(text), keyword_pos + len(keyword) + 50)
                        context = text[context_start:context_end].strip()
                        
                        keyword_matches.append({
                            "keyword": keyword,
                            "context": context,
                            "position": keyword_pos
                        })
            
            # Create facts from keyword matches
            for match in keyword_matches:
                confidence = 0.6  # Base confidence for keyword matches
                
                # Boost confidence if multiple keywords found
                if len(keyword_matches) > 1:
                    confidence += 0.1
                
                fact = ExtractedFact(
                    id=self._generate_fact_id(category),
                    category=category,
                    label=f"Keyword: {match['keyword']}",
                    value=match["context"],
                    confidence=min(confidence, 0.8),
                    sources=[source_info],
                    status=FactStatus.PENDING,
                    code=self._generate_fact_id(category),
                    extraction_method="keyword_extraction",
                    context=match["context"]
                )
                facts.append(fact)
        
        return facts
    
    async def _extract_semantic_facts(self, text: str, source_info: Dict[str, str]) -> List[ExtractedFact]:
        """Extract facts using semantic analysis"""
        facts = []
        
        # Extract numerical data
        numbers = re.findall(r'\$?[\d,]+\.?\d*\s*(?:million|billion|thousand|k|m|b|t)?', text, re.IGNORECASE)
        for number in numbers:
            # Determine if this is revenue, market size, or other metric
            context_start = text.lower().find(number.lower())
            if context_start != -1:
                context = text[max(0, context_start-30):context_start+len(number)+30]
                
                category = FactCategory.METRICS
                if "revenue" in context.lower() or "income" in context.lower():
                    category = FactCategory.REVENUE
                elif "market" in context.lower() or "tam" in context.lower():
                    category = FactCategory.MARKET
                
                fact = ExtractedFact(
                    id=self._generate_fact_id(category),
                    category=category,
                    label="Numerical Data",
                    value=number,
                    confidence=0.7,
                    sources=[source_info],
                    status=FactStatus.PENDING,
                    code=self._generate_fact_id(category),
                    extraction_method="semantic_analysis",
                    context=context
                )
                facts.append(fact)
        
        # Extract company names (simplified)
        company_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Inc|LLC|Corp|Ltd|Company)',
            r'(?:We are|We provide|Our company is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'Founded by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                fact = ExtractedFact(
                    id=self._generate_fact_id(FactCategory.COMPANY),
                    category=FactCategory.COMPANY,
                    label="Company Name",
                    value=match,
                    confidence=0.8,
                    sources=[source_info],
                    status=FactStatus.PENDING,
                    code=self._generate_fact_id(FactCategory.COMPANY),
                    extraction_method="semantic_analysis",
                    context=text
                )
                facts.append(fact)
        
        return facts
    
    def _deduplicate_facts(self, facts: List[ExtractedFact]) -> List[ExtractedFact]:
        """Remove duplicate facts based on value and category"""
        seen = set()
        unique_facts = []
        
        for fact in facts:
            key = (fact.category.value, fact.value.lower().strip())
            if key not in seen:
                seen.add(key)
                unique_facts.append(fact)
        
        return unique_facts
    
    async def _post_process_facts(self, facts: List[ExtractedFact]) -> List[ExtractedFact]:
        """Post-process facts to improve quality and consistency"""
        processed_facts = []
        
        for fact in facts:
            # Clean up fact value
            cleaned_value = fact.value.strip()
            
            # Remove excessive whitespace
            cleaned_value = re.sub(r'\s+', ' ', cleaned_value)
            
            # Update fact with cleaned value
            fact.value = cleaned_value
            
            # Update status based on confidence
            if fact.confidence >= 0.8:
                fact.status = FactStatus.VERIFIED
            elif fact.confidence >= 0.6:
                fact.status = FactStatus.NEEDS_REVIEW
            else:
                fact.status = FactStatus.PENDING
            
            processed_facts.append(fact)
        
        return processed_facts
    
    def _calculate_confidence_distribution(self, facts: List[ExtractedFact]) -> Dict[str, int]:
        """Calculate distribution of confidence levels"""
        distribution = {"high": 0, "medium": 0, "low": 0}
        
        for fact in facts:
            if fact.confidence >= 0.8:
                distribution["high"] += 1
            elif fact.confidence >= 0.6:
                distribution["medium"] += 1
            else:
                distribution["low"] += 1
        
        return distribution
    
    def _generate_extraction_summary(self, facts: List[ExtractedFact], evidence_count: int, stats: Dict[str, int]) -> str:
        """Generate summary of extraction results"""
        if not facts:
            return "No facts were extracted from the evidence."
        
        # Count facts by category
        category_counts = defaultdict(int)
        for fact in facts:
            category_counts[fact.category.value] += 1
        
        # Find most common category
        most_common = max(category_counts.items(), key=lambda x: x[1]) if category_counts else ("None", 0)
        
        # Calculate average confidence
        avg_confidence = sum(f.confidence for f in facts) / len(facts)
        
        summary = f"Extracted {len(facts)} facts from {evidence_count} evidence items. "
        summary += f"Most common category: {most_common[0]} ({most_common[1]} facts). "
        summary += f"Average confidence: {avg_confidence:.2f}. "
        
        if stats.get("pattern_matching", 0) > 0:
            summary += f"Pattern matching found {stats['pattern_matching']} facts. "
        if stats.get("keyword_extraction", 0) > 0:
            summary += f"Keyword extraction found {stats['keyword_extraction']} facts. "
        if stats.get("semantic_analysis", 0) > 0:
            summary += f"Semantic analysis found {stats['semantic_analysis']} facts. "
        if stats.get("ai_insight", 0) > 0:
            summary += f"AI insights found {stats['ai_insight']} facts. "
        
        return summary
        
        # Calculate confidence distribution
        confidence_distribution = {"high": 0, "medium": 0, "low": 0}
        for fact in all_facts:
            if fact.confidence >= 0.8:
                confidence_distribution["high"] += 1
            elif fact.confidence >= 0.6:
                confidence_distribution["medium"] += 1
            else:
                confidence_distribution["low"] += 1
        
        # Generate summary
        total_facts = len(all_facts)
        high_confidence = confidence_distribution["high"]
        summary = f"AI has identified {total_facts} facts from your evidence. "
        summary += f"{high_confidence} facts have high confidence (80%+). "
        
        if total_facts > 0:
            # Count by category
            category_counts = {}
            for fact in all_facts:
                category_counts[fact.category.value] = category_counts.get(fact.category.value, 0) + 1
            
            top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            category_summary = ", ".join([f"{cat} ({count})" for cat, count in top_categories])
            summary += f"Top categories: {category_summary}."
        
        processing_time = time.time() - start_time
        
        return ExtractionResult(
            facts=all_facts,
            summary=summary,
            warnings=warnings,
            extraction_complete=True,
            processing_time=processing_time,
            evidence_processed=evidence_processed,
            confidence_distribution=confidence_distribution
        )
    
    async def update_fact_status(self, fact_id: str, status: FactStatus, notes: str = "") -> bool:
        """Update the status of a specific fact"""
        # This would typically update a database
        # For now, we'll just log the update
        self.logger.info(f"Updated fact {fact_id} to {status.value}: {notes}")
        return True
    
    def get_fact_statistics(self, facts: List[ExtractedFact]) -> Dict[str, Any]:
        """Get statistics about extracted facts"""
        if not facts:
            return {
                "total_facts": 0,
                "by_category": {},
                "by_status": {},
                "average_confidence": 0.0,
                "confidence_distribution": {"high": 0, "medium": 0, "low": 0}
            }
        
        # Count by category
        by_category = {}
        for fact in facts:
            by_category[fact.category.value] = by_category.get(fact.category.value, 0) + 1
        
        # Count by status
        by_status = {}
        for fact in facts:
            by_status[fact.status.value] = by_status.get(fact.status.value, 0) + 1
        
        # Average confidence
        avg_confidence = sum(fact.confidence for fact in facts) / len(facts)
        
        # Confidence distribution
        confidence_dist = {"high": 0, "medium": 0, "low": 0}
        for fact in facts:
            if fact.confidence >= 0.8:
                confidence_dist["high"] += 1
            elif fact.confidence >= 0.6:
                confidence_dist["medium"] += 1
            else:
                confidence_dist["low"] += 1
        
        return {
            "total_facts": len(facts),
            "by_category": by_category,
            "by_status": by_status,
            "average_confidence": round(avg_confidence, 2),
            "confidence_distribution": confidence_dist
        }
