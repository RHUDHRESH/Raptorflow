"""
Extraction Orchestrator Agent
Coordinates AI extraction of facts and insights from evidence with enhanced real-time processing
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
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

    def to_dict(self):
        d = asdict(self)
        d["category"] = self.category.value
        d["status"] = self.status.value
        return d


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

    def to_dict(self):
        return {
            "facts": [f.to_dict() for f in self.facts],
            "summary": self.summary,
            "warnings": self.warnings,
            "extraction_complete": self.extraction_complete,
            "processing_time": self.processing_time,
            "evidence_processed": self.evidence_processed,
            "confidence_distribution": self.confidence_distribution
        }


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
            }
        }

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute extraction using the current state."""
        evidence = state.get("evidence", [])
        result = await self.extract_from_evidence(evidence)
        return {"output": result.to_dict()}
    
    def _generate_fact_id(self, category: FactCategory) -> str:
        """Generate unique fact ID"""
        self.fact_counter += 1
        category_code = category.value.upper()[0:3]
        return f"F-{category_code}-{self.fact_counter:03d}"
    
    def _extract_pattern_facts(self, text: str, source_info: Dict[str, str]) -> List[ExtractedFact]:
        """Extract facts using patterns"""
        facts = []
        text_lower = text.lower()
        
        for category, patterns_info in self.extraction_patterns.items():
            for pattern in patterns_info["patterns"]:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    if len(match.groups()) > 0:
                        value = match.group(1).strip()
                        fact = ExtractedFact(
                            id=self._generate_fact_id(category),
                            category=category,
                            label=category.value,
                            value=value,
                            confidence=0.8,
                            sources=[source_info],
                            status=FactStatus.PENDING,
                            code=self._generate_fact_id(category),
                            extraction_method="pattern_matching",
                            context=text[max(0, match.start()-50):match.end()+50]
                        )
                        facts.append(fact)
        return facts

    async def _extract_keyword_facts(self, text: str, source_info: Dict[str, str]) -> List[ExtractedFact]:
        return [] # Placeholder

    async def _extract_semantic_facts(self, text: str, source_info: Dict[str, str]) -> List[ExtractedFact]:
        return [] # Placeholder

    async def _extract_ai_insights(self, text: str, source_info: Dict[str, str]) -> List[ExtractedFact]:
        return [] # Placeholder
    
    async def extract_from_evidence(self, evidence_list: List[Dict[str, Any]]) -> ExtractionResult:
        """Enhanced extraction from evidence"""
        start_time = datetime.now()
        all_facts = []
        evidence_processed = 0
        
        for evidence in evidence_list:
            source_info = {"name": evidence.get("filename", "unknown")}
            text = evidence.get("extracted_text", "")
            if text:
                facts = self._extract_pattern_facts(text, source_info)
                all_facts.extend(facts)
                evidence_processed += 1
        
        processing_time = (datetime.now() - start_time).total_seconds()
        return ExtractionResult(
            facts=all_facts,
            summary=f"Extracted {len(all_facts)} facts",
            warnings=[],
            extraction_complete=True,
            processing_time=processing_time,
            evidence_processed=evidence_processed,
            confidence_distribution={"high": len(all_facts), "medium": 0, "low": 0}
        )