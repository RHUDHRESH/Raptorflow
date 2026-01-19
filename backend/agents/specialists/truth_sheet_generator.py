"""
Truth Sheet Generator Agent
Auto-populates truth sheets from extracted evidence
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class TruthCategory(Enum):
    """Categories for truth sheet entries"""
    COMPANY = "company"
    PRODUCT = "product"
    MARKET = "market"
    CUSTOMER = "customer"
    COMPETITION = "competition"
    FINANCIALS = "financials"
    TEAM = "team"
    TECHNOLOGY = "technology"


class ConfidenceLevel(Enum):
    """Confidence level of extracted truth"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class TruthEntry:
    """A single truth sheet entry"""
    id: str
    category: TruthCategory
    field_name: str
    value: str
    source: str
    source_excerpt: Optional[str] = None
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    verified: bool = False
    user_edited: bool = False
    extracted_at: str = ""

    def to_dict(self):
        d = asdict(self)
        d["category"] = self.category.value
        d["confidence"] = self.confidence.value
        return d


@dataclass
class TruthSheet:
    """Complete truth sheet"""
    entries: List[TruthEntry]
    completeness_score: float
    categories_covered: List[str]
    missing_fields: List[str]
    recommendations: List[str]
    summary: str

    def to_dict(self):
        return {
            "entries": [e.to_dict() for e in self.entries],
            "completeness_score": self.completeness_score,
            "categories_covered": self.categories_covered,
            "missing_fields": self.missing_fields,
            "recommendations": self.recommendations,
            "summary": self.summary
        }


class TruthSheetGenerator:
    """AI-powered truth sheet generation from evidence"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.entry_counter = 0
    
    def _generate_entry_id(self) -> str:
        """Generate unique entry ID"""
        self.entry_counter += 1
        return f"TRU-{self.entry_counter:03d}"

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute truth sheet generation using current state."""
        evidence = state.get("evidence", [])
        sheet = await self.generate_truth_sheet(evidence)
        return {"output": sheet.to_dict()}

    async def generate_truth_sheet(self, evidence_list: List[Dict[str, Any]]) -> TruthSheet:
        """Generation logic"""
        # Basic implementation for now
        entries = []
        for ev in evidence_list:
            if ev.get("extracted_text"):
                # Mock a few entries for verification
                entries.append(TruthEntry(
                    id=self._generate_entry_id(),
                    category=TruthCategory.COMPANY,
                    field_name="company_name",
                    value="Extracted from " + ev.get("filename", "unknown"),
                    source=ev.get("filename", "unknown"),
                    confidence=ConfidenceLevel.HIGH,
                    extracted_at=datetime.now().isoformat()
                ))
        
        return TruthSheet(
            entries=entries,
            completeness_score=0.5,
            categories_covered=["company"],
            missing_fields=["mission", "market_size"],
            recommendations=["Verify extracted company name"],
            summary=f"Found {len(entries)} candidate truths."
        )