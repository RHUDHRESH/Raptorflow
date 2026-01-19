"""
AI Extraction Engine
Advanced fact extraction using multiple AI techniques
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import re
import asyncio
from pathlib import Path

# Import AI agents
from backend.agents.specialists.extraction_orchestrator import ExtractionOrchestrator

# Import Vertex AI for real AI processing
try:
    from services.vertex_ai_service import vertex_ai_service
except ImportError:
    vertex_ai_service = None

logger = logging.getLogger(__name__)


class FactCategory(str, Enum):
    """Categories of extracted facts"""
    COMPANY = "company"
    PRODUCT = "product"
    MARKET = "market"
    CUSTOMER = "customer"
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    STRATEGIC = "strategic"
    COMPETITIVE = "competitive"
    TECHNOLOGY = "technology"
    TEAM = "team"
    OTHER = "other"


class FactType(str, Enum):
    """Types of facts"""
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    TEMPORAL = "temporal"
    TEXTUAL = "textual"
    RELATIONSHIP = "relationship"
    METRIC = "metric"


class ConfidenceLevel(str, Enum):
    """Confidence levels for facts"""
    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"


@dataclass
class ExtractedFact:
    """Individual extracted fact"""
    id: str
    category: FactCategory
    type: FactType
    label: str
    value: str
    confidence: float
    confidence_level: ConfidenceLevel
    sources: List[Dict[str, Any]] = field(default_factory=list)
    context: str = ""
    extraction_method: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    validation_status: str = "pending"
    contradictions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "category": self.category.value,
            "type": self.type.value,
            "label": self.label,
            "value": self.value,
            "confidence": self.confidence,
            "confidence_level": self.confidence_level.value,
            "sources": self.sources,
            "context": self.context[:200] + "..." if len(self.context) > 200 else self.context,
            "extraction_method": self.extraction_method,
            "validation_status": self.validation_status,
            "contradictions": self.contradictions,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class ExtractionResult:
    """Result of fact extraction"""
    facts: List[ExtractedFact]
    total_facts: int
    processing_time: float
    sources_processed: int
    confidence_distribution: Dict[str, int]
    category_distribution: Dict[str, int]
    quality_score: float
    recommendations: List[str]
    extraction_metadata: Dict[str, Any] = field(default_factory=dict)


class AIExtractionEngine:
    """Advanced AI-powered fact extraction engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize extraction orchestrator
        self.extraction_orchestrator = ExtractionOrchestrator()
        
        # Fact patterns for regex extraction
        self.fact_patterns = self._initialize_fact_patterns()
        
        # Category keywords
        self.category_keywords = self._initialize_category_keywords()
        
        # Fact counter
        self.fact_counter = 0
    
    def _initialize_fact_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Initialize regex patterns for fact extraction"""
        return {
            "revenue": [
                re.compile(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:million|billion|thousand)?\s*(?:in\s*)?revenue', re.IGNORECASE),
                re.compile(r'revenue\s*(?:of|was|is)?\s*\$(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:million|billion|thousand)?', re.IGNORECASE),
                re.compile(r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:million|billion|thousand)?\s*(?:in\s*)?revenue', re.IGNORECASE)
            ],
            "employees": [
                re.compile(r'(\d+(?:,\d{3})*)\s*(?:employees|staff|team members?)', re.IGNORECASE),
                re.compile(r'(?:employees|staff|team members?)\s*(?:of|:)?\s*(\d+(?:,\d{3})*)', re.IGNORECASE)
            ],
            "founded": [
                re.compile(r'founded\s*(?:in\s*)?(\d{4})', re.IGNORECASE),
                re.compile(r'established\s*(?:in\s*)?(\d{4})', re.IGNORECASE),
                re.compile(r'(\d{4})\s*(?:founded|established)', re.IGNORECASE)
            ],
            "location": [
                re.compile(r'(?:located|based|headquartered)\s*(?:in|at)?\s*([A-Za-z\s,]+)', re.IGNORECASE),
                re.compile(r'([A-Za-z\s,]+)\s*(?:office|headquarters|location)', re.IGNORECASE)
            ],
            "funding": [
                re.compile(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:million|billion)?\s*(?:in\s*)?funding', re.IGNORECASE),
                re.compile(r'raised\s*\$(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:million|billion)?', re.IGNORECASE),
                re.compile(r'funding\s*(?:of|round)?\s*\$(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:million|billion)?', re.IGNORECASE)
            ],
            "customers": [
                re.compile(r'(\d+(?:,\d{3})*)\s*(?:customers|clients|users)', re.IGNORECASE),
                re.compile(r'(?:customers|clients|users)\s*(?:of|:)?\s*(\d+(?:,\d{3})*)', re.IGNORECASE)
            ],
            "growth": [
                re.compile(r'(\d+(?:\.\d+)?)%\s*(?:growth|increase|rise)', re.IGNORECASE),
                re.compile(r'growth\s*(?:of|rate)?\s*(\d+(?:\.\d+)?)%', re.IGNORECASE)
            ]
        }
    
    def _initialize_category_keywords(self) -> Dict[FactCategory, List[str]]:
        """Initialize keywords for category classification"""
        return {
            FactCategory.COMPANY: ["company", "business", "organization", "firm", "enterprise", "corporation"],
            FactCategory.PRODUCT: ["product", "service", "solution", "offering", "platform", "software"],
            FactCategory.MARKET: ["market", "industry", "sector", "vertical", "niche", "segment"],
            FactCategory.CUSTOMER: ["customer", "client", "user", "buyer", "prospect", "audience"],
            FactCategory.FINANCIAL: ["revenue", "profit", "income", "funding", "investment", "valuation", "price"],
            FactCategory.OPERATIONAL: ["operations", "process", "workflow", "procedure", "system", "infrastructure"],
            FactCategory.STRATEGIC: ["strategy", "mission", "vision", "goal", "objective", "plan", "roadmap"],
            FactCategory.COMPETITIVE: ["competitor", "competition", "rival", "alternative", "market share"],
            FactCategory.TECHNOLOGY: ["technology", "tech", "software", "hardware", "platform", "architecture"],
            FactCategory.TEAM: ["team", "employees", "staff", "personnel", "workforce", "leadership"]
        }
    
    async def extract_facts_from_evidence(self, evidence_list: List[Dict[str, Any]]) -> ExtractionResult:
        """Extract facts from multiple evidence items"""
        start_time = datetime.now()
        
        all_facts = []
        sources_processed = 0
        
        # Process each evidence item
        for evidence in evidence_list:
            try:
                facts = await self._extract_from_single_evidence(evidence)
                all_facts.extend(facts)
                sources_processed += 1
                
            except Exception as e:
                self.logger.error(f"Error extracting from evidence {evidence.get('id', 'unknown')}: {e}")
        
        # Deduplicate facts
        deduplicated_facts = self._deduplicate_facts(all_facts)
        
        # Calculate quality score
        quality_score = self._calculate_extraction_quality(deduplicated_facts)
        
        # Generate recommendations
        recommendations = self._generate_extraction_recommendations(deduplicated_facts, evidence_list)
        
        # Calculate distributions
        confidence_dist = self._calculate_confidence_distribution(deduplicated_facts)
        category_dist = self._calculate_category_distribution(deduplicated_facts)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return ExtractionResult(
            facts=deduplicated_facts,
            total_facts=len(deduplicated_facts),
            processing_time=processing_time,
            sources_processed=sources_processed,
            confidence_distribution=confidence_dist,
            category_distribution=category_dist,
            quality_score=quality_score,
            recommendations=recommendations,
            extraction_metadata={
                "extraction_methods": list(set(f.extraction_method for f in deduplicated_facts)),
                "average_confidence": sum(f.confidence for f in deduplicated_facts) / len(deduplicated_facts) if deduplicated_facts else 0.0,
                "high_confidence_facts": len([f for f in deduplicated_facts if f.confidence > 0.8])
            }
        )
    
    async def _extract_from_single_evidence(self, evidence: Dict[str, Any]) -> List[ExtractedFact]:
        """Extract facts from single evidence item"""
        facts = []
        content = evidence.get("content", "")
        evidence_id = evidence.get("id", "unknown")
        evidence_name = evidence.get("name", "Unknown")
        
        # Method 1: Pattern-based extraction
        pattern_facts = self._extract_with_patterns(content, evidence_id, evidence_name)
        facts.extend(pattern_facts)
        
        # Method 2: AI-powered extraction
        if vertex_ai_service:
            try:
                ai_facts = await self._extract_with_ai(content, evidence_id, evidence_name)
                facts.extend(ai_facts)
            except Exception as e:
                self.logger.warning(f"AI extraction failed for {evidence_id}: {e}")
        
        # Method 3: Keyword-based extraction
        keyword_facts = self._extract_with_keywords(content, evidence_id, evidence_name)
        facts.extend(keyword_facts)
        
        # Method 4: Use extraction orchestrator
        try:
            orchestrator_result = await self.extraction_orchestrator.extract_facts_from_evidence([evidence])
            orchestrator_facts = self._convert_orchestrator_facts(orchestrator_result.facts, evidence_id, evidence_name)
            facts.extend(orchestrator_facts)
        except Exception as e:
            self.logger.warning(f"Orchestrator extraction failed for {evidence_id}: {e}")
        
        return facts
    
    def _extract_with_patterns(self, content: str, evidence_id: str, evidence_name: str) -> List[ExtractedFact]:
        """Extract facts using regex patterns"""
        facts = []
        
        for pattern_type, patterns in self.fact_patterns.items():
            for pattern in patterns:
                matches = pattern.finditer(content)
                
                for match in matches:
                    fact = self._create_fact_from_match(
                        match, pattern_type, content, evidence_id, evidence_name
                    )
                    if fact:
                        facts.append(fact)
        
        return facts
    
    def _create_fact_from_match(self, match: re.Match, pattern_type: str, content: str, evidence_id: str, evidence_name: str) -> Optional[ExtractedFact]:
        """Create fact from regex match"""
        try:
            # Extract value
            value = match.group(1) if match.groups() else match.group(0)
            
            # Determine category and type
            category = self._determine_category_from_pattern(pattern_type)
            fact_type = self._determine_fact_type_from_value(value)
            
            # Create label
            label = self._create_label_from_pattern(pattern_type, value)
            
            # Calculate confidence
            confidence = self._calculate_pattern_confidence(match, pattern_type, content)
            
            # Get context
            start = max(0, match.start() - 100)
            end = min(len(content), match.end() + 100)
            context = content[start:end].strip()
            
            fact = ExtractedFact(
                id=self._generate_fact_id(),
                category=category,
                type=fact_type,
                label=label,
                value=value,
                confidence=confidence,
                confidence_level=self._get_confidence_level(confidence),
                sources=[{
                    "type": "evidence",
                    "id": evidence_id,
                    "name": evidence_name,
                    "match_text": match.group(0)
                }],
                context=context,
                extraction_method="pattern_matching",
                metadata={
                    "pattern_type": pattern_type,
                    "match_position": match.start(),
                    "pattern_confidence": confidence
                }
            )
            
            return fact
            
        except Exception as e:
            self.logger.error(f"Error creating fact from match: {e}")
            return None
    
    def _determine_category_from_pattern(self, pattern_type: str) -> FactCategory:
        """Determine fact category from pattern type"""
        category_mapping = {
            "revenue": FactCategory.FINANCIAL,
            "employees": FactCategory.TEAM,
            "founded": FactCategory.COMPANY,
            "location": FactCategory.COMPANY,
            "funding": FactCategory.FINANCIAL,
            "customers": FactCategory.CUSTOMER,
            "growth": FactCategory.MARKET
        }
        
        return category_mapping.get(pattern_type, FactCategory.OTHER)
    
    def _determine_fact_type_from_value(self, value: str) -> FactType:
        """Determine fact type from value"""
        # Numerical
        if re.match(r'^\d+(?:,\d{3})*(?:\.\d{2})?$', value):
            return FactType.NUMERICAL
        
        # Temporal (year)
        if re.match(r'^\d{4}$', value):
            return FactType.TEMPORAL
        
        # Percentage
        if re.match(r'^\d+(?:\.\d+)?%$', value):
            return FactType.METRIC
        
        # Textual
        return FactType.TEXTUAL
    
    def _create_label_from_pattern(self, pattern_type: str, value: str) -> str:
        """Create label from pattern type"""
        label_mapping = {
            "revenue": f"Revenue: {value}",
            "employees": f"Employee Count: {value}",
            "founded": f"Founded Year: {value}",
            "location": f"Location: {value}",
            "funding": f"Funding Amount: {value}",
            "customers": f"Customer Count: {value}",
            "growth": f"Growth Rate: {value}"
        }
        
        return label_mapping.get(pattern_type, f"Extracted Fact: {value}")
    
    def _calculate_pattern_confidence(self, match: re.Match, pattern_type: str, content: str) -> float:
        """Calculate confidence for pattern match"""
        base_confidence = 0.7
        
        # Boost for specific patterns
        if pattern_type in ["revenue", "funding"]:
            base_confidence = 0.8
        
        # Boost for context keywords
        context_start = max(0, match.start() - 50)
        context_end = min(len(content), match.end() + 50)
        context = content[context_start:context_end].lower()
        
        boost_keywords = ["official", "reported", "announced", "according", "stated", "confirmed"]
        if any(keyword in context for keyword in boost_keywords):
            base_confidence += 0.1
        
        # Reduce for ambiguous contexts
        ambiguous_keywords = ["estimate", "approximately", "around", "roughly", "about"]
        if any(keyword in context for keyword in ambiguous_keywords):
            base_confidence -= 0.1
        
        return min(1.0, max(0.0, base_confidence))
    
    async def _extract_with_ai(self, content: str, evidence_id: str, evidence_name: str) -> List[ExtractedFact]:
        """Extract facts using AI"""
        if not vertex_ai_service:
            return []
        
        try:
            # Prepare AI prompt
            prompt = f"""
Extract key facts from the following business document. Focus on:
- Company information (name, founded, location, employees)
- Financial data (revenue, funding, valuation)
- Product/service details
- Market information
- Customer data
- Competitive information

Document:
{content[:2000]}  # Limit content for AI processing

Provide facts in JSON format:
{{
    "facts": [
        {{
            "category": "company|product|market|customer|financial|operational|strategic|competitive|technology|team",
            "label": "Brief description of the fact",
            "value": "The extracted value",
            "confidence": 0.0-1.0,
            "context": "Relevant context from the document"
        }}
    ]
}}
"""
            
            # Call AI service
            response = await vertex_ai_service.generate_text(
                prompt=prompt,
                max_tokens=1500,
                temperature=0.3
            )
            
            if response["status"] == "success":
                return self._parse_ai_facts(response["text"], evidence_id, evidence_name)
            else:
                self.logger.warning(f"AI extraction failed: {response.get('error')}")
                return []
                
        except Exception as e:
            self.logger.error(f"AI extraction error: {e}")
            return []
    
    def _parse_ai_facts(self, ai_response: str, evidence_id: str, evidence_name: str) -> List[ExtractedFact]:
        """Parse AI response into facts"""
        facts = []
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if not json_match:
                return []
            
            data = json.loads(json_match.group(0))
            ai_facts = data.get("facts", [])
            
            for fact_data in ai_facts:
                try:
                    category = FactCategory(fact_data.get("category", "other"))
                    fact_type = self._determine_fact_type_from_value(fact_data.get("value", ""))
                    
                    fact = ExtractedFact(
                        id=self._generate_fact_id(),
                        category=category,
                        type=fact_type,
                        label=fact_data.get("label", "Extracted Fact"),
                        value=fact_data.get("value", ""),
                        confidence=float(fact_data.get("confidence", 0.5)),
                        confidence_level=self._get_confidence_level(float(fact_data.get("confidence", 0.5))),
                        sources=[{
                            "type": "evidence",
                            "id": evidence_id,
                            "name": evidence_name,
                            "extraction_method": "ai"
                        }],
                        context=fact_data.get("context", ""),
                        extraction_method="ai_extraction",
                        metadata={"ai_confidence": fact_data.get("confidence", 0.5)}
                    )
                    
                    facts.append(fact)
                    
                except Exception as e:
                    self.logger.error(f"Error parsing AI fact: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error parsing AI response: {e}")
        
        return facts
    
    def _extract_with_keywords(self, content: str, evidence_id: str, evidence_name: str) -> List[ExtractedFact]:
        """Extract facts using keyword matching"""
        facts = []
        
        # Split content into sentences
        sentences = re.split(r'[.!?]+', content)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:  # Skip very short sentences
                continue
            
            # Check for category keywords
            for category, keywords in self.category_keywords.items():
                for keyword in keywords:
                    if keyword.lower() in sentence.lower():
                        # Extract potential fact
                        fact = self._extract_fact_from_sentence(sentence, category, evidence_id, evidence_name)
                        if fact:
                            facts.append(fact)
                            break  # Only one fact per sentence per category
        
        return facts
    
    def _extract_fact_from_sentence(self, sentence: str, category: FactCategory, evidence_id: str, evidence_name: str) -> Optional[ExtractedFact]:
        """Extract fact from sentence"""
        # Simple extraction - look for key information patterns
        patterns = [
            r'is\s+(.+?)\s+(?:that|which|who)',
            r'provides\s+(.+?)\s+(?:to|for|with)',
            r'offers\s+(.+?)\s+(?:to|for|with)',
            r'specializes\s+in\s+(.+?)\s+(?:and|with)',
            r'focuses\s+on\s+(.+?)\s+(?:and|with)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                
                fact = ExtractedFact(
                    id=self._generate_fact_id(),
                    category=category,
                    type=FactType.TEXTUAL,
                    label=f"{category.value.title()} Information",
                    value=value,
                    confidence=0.6,  # Moderate confidence for keyword extraction
                    confidence_level=ConfidenceLevel.MEDIUM,
                    sources=[{
                        "type": "evidence",
                        "id": evidence_id,
                        "name": evidence_name,
                        "extraction_method": "keyword"
                    }],
                    context=sentence,
                    extraction_method="keyword_matching"
                )
                
                return fact
        
        return None
    
    def _convert_orchestrator_facts(self, orchestrator_facts: List[Any], evidence_id: str, evidence_name: str) -> List[ExtractedFact]:
        """Convert orchestrator facts to ExtractedFact format"""
        converted_facts = []
        
        for fact in orchestrator_facts:
            try:
                # Convert orchestrator fact format
                converted_fact = ExtractedFact(
                    id=self._generate_fact_id(),
                    category=FactCategory(fact.get("category", "other")),
                    type=FactType(fact.get("type", "textual")),
                    label=fact.get("label", "Extracted Fact"),
                    value=fact.get("value", ""),
                    confidence=float(fact.get("confidence", 0.5)),
                    confidence_level=self._get_confidence_level(float(fact.get("confidence", 0.5))),
                    sources=[{
                        "type": "evidence",
                        "id": evidence_id,
                        "name": evidence_name,
                        "extraction_method": "orchestrator"
                    }],
                    context=fact.get("context", ""),
                    extraction_method="orchestrator",
                    metadata=fact.get("metadata", {})
                )
                
                converted_facts.append(converted_fact)
                
            except Exception as e:
                self.logger.error(f"Error converting orchestrator fact: {e}")
                continue
        
        return converted_facts
    
    def _deduplicate_facts(self, facts: List[ExtractedFact]) -> List[ExtractedFact]:
        """Deduplicate facts based on similarity"""
        if not facts:
            return []
        
        deduplicated = []
        seen_facts = set()
        
        for fact in facts:
            # Create a key for deduplication
            key = f"{fact.category.value}:{fact.label.lower()}:{fact.value.lower()}"
            
            if key not in seen_facts:
                seen_facts.add(key)
                deduplicated.append(fact)
            else:
                # If duplicate, keep the one with higher confidence
                existing_fact = next(f for f in deduplicated if 
                                   f"{f.category.value}:{f.label.lower()}:{f.value.lower()}" == key)
                
                if fact.confidence > existing_fact.confidence:
                    deduplicated.remove(existing_fact)
                    deduplicated.append(fact)
        
        return deduplicated
    
    def _calculate_extraction_quality(self, facts: List[ExtractedFact]) -> float:
        """Calculate overall extraction quality score"""
        if not facts:
            return 0.0
        
        # Factors for quality score
        avg_confidence = sum(f.confidence for f in facts) / len(facts)
        
        # Category diversity (0-30 points)
        categories = set(f.category for f in facts)
        diversity_score = min(30, len(categories) * 3)
        
        # High confidence facts (0-40 points)
        high_conf_count = len([f for f in facts if f.confidence > 0.7])
        confidence_score = min(40, (high_conf_count / len(facts)) * 40)
        
        # Fact count (0-30 points)
        count_score = min(30, len(facts) * 2)
        
        total_score = diversity_score + confidence_score + count_score
        return min(100.0, total_score)
    
    def _generate_extraction_recommendations(self, facts: List[ExtractedFact], evidence_list: List[Dict[str, Any]]) -> List[str]:
        """Generate extraction recommendations"""
        recommendations = []
        
        if not facts:
            recommendations.append("No facts extracted - check evidence quality and content")
            return recommendations
        
        # Category coverage
        categories = set(f.category for f in facts)
        missing_categories = set(FactCategory) - categories
        
        if missing_categories:
            recommendations.append(f"Consider adding evidence for missing categories: {', '.join(c.value for c in missing_categories)}")
        
        # Confidence levels
        low_conf_facts = [f for f in facts if f.confidence < 0.5]
        if len(low_conf_facts) > len(facts) * 0.3:
            recommendations.append("Many low-confidence facts - consider reviewing and validating")
        
        # Evidence coverage
        if len(evidence_list) > 0 and len(facts) < len(evidence_list) * 2:
            recommendations.append("Low fact extraction rate - consider adding more detailed evidence")
        
        # Fact types
        fact_types = set(f.type for f in facts)
        if FactType.NUMERICAL not in fact_types:
            recommendations.append("No numerical facts extracted - consider adding financial or operational data")
        
        return recommendations
    
    def _calculate_confidence_distribution(self, facts: List[ExtractedFact]) -> Dict[str, int]:
        """Calculate confidence distribution"""
        distribution = {"very_high": 0, "high": 0, "medium": 0, "low": 0, "very_low": 0}
        
        for fact in facts:
            distribution[fact.confidence_level.value] += 1
        
        return distribution
    
    def _calculate_category_distribution(self, facts: List[ExtractedFact]) -> Dict[str, int]:
        """Calculate category distribution"""
        distribution = {}
        
        for fact in facts:
            category = fact.category.value
            distribution[category] = distribution.get(category, 0) + 1
        
        return distribution
    
    def _get_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Get confidence level from confidence score"""
        if confidence >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif confidence >= 0.7:
            return ConfidenceLevel.HIGH
        elif confidence >= 0.5:
            return ConfidenceLevel.MEDIUM
        elif confidence >= 0.3:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
    
    def _generate_fact_id(self) -> str:
        """Generate unique fact ID"""
        self.fact_counter += 1
        return f"FACT-{self.fact_counter:04d}"
    
    async def search_facts(self, facts: List[ExtractedFact], query: str) -> List[ExtractedFact]:
        """Search facts by query"""
        query_lower = query.lower()
        results = []
        
        for fact in facts:
            # Search in label, value, and context
            if (query_lower in fact.label.lower() or 
                query_lower in fact.value.lower() or 
                query_lower in fact.context.lower()):
                results.append(fact)
        
        return results
    
    async def validate_facts(self, facts: List[ExtractedFact]) -> List[ExtractedFact]:
        """Validate facts and update validation status"""
        validated_facts = []
        
        for fact in facts:
            # Basic validation rules
            is_valid = True
            validation_errors = []
            
            # Check for empty values
            if not fact.value.strip():
                is_valid = False
                validation_errors.append("Empty value")
            
            # Check for reasonable confidence
            if fact.confidence < 0.3:
                is_valid = False
                validation_errors.append("Low confidence")
            
            # Check for contradictory values (basic checks)
            if fact.category == FactCategory.FINANCIAL and fact.type == FactType.NUMERICAL:
                try:
                    value_num = float(fact.value.replace('$', '').replace(',', ''))
                    if value_num < 0:
                        is_valid = False
                        validation_errors.append("Negative financial value")
                except ValueError:
                    validation_errors.append("Invalid numerical format")
            
            # Update validation status
            fact.validation_status = "valid" if is_valid else "invalid"
            if validation_errors:
                fact.metadata["validation_errors"] = validation_errors
            
            validated_facts.append(fact)
        
        return validated_facts


# Export engine
__all__ = ["AIExtractionEngine", "ExtractedFact", "ExtractionResult"]
