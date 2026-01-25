"""
Truth Sheet Generator Agent
Auto-populates truth sheets from extracted evidence via real AI inference
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from ..base import BaseAgent
from backend.agents.config import ModelTier
from ..state import AgentState

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
            "summary": self.summary,
        }


class TruthSheetGenerator(BaseAgent):
    """AI-powered truth sheet generation using real inference."""

    def __init__(self):
        super().__init__(
            name="TruthSheetGenerator",
            description="Consolidates multi-source evidence into a single source of truth via real AI inference",
            model_tier=ModelTier.FLASH,
            tools=["database"],
            skills=["data_synthesis", "fact_checking", "strategic_alignment"],
        )
        self.entry_counter = 0

    def get_system_prompt(self) -> str:
        return """You are the TruthSheetGenerator. Your job is to resolve inconsistencies and pick the 'Canonical Truth' from evidence.
        If a pitch deck says $1M ARR and a tax return says $800k, follow the most reliable source.
        Categorize truths into Company, Product, Market, etc."""

    def _generate_entry_id(self) -> str:
        """Generate unique entry ID"""
        self.entry_counter += 1
        return f"TRU-{self.entry_counter:03d}"

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute truth sheet generation using real AI inference."""
        extracted_facts = (
            state.get("step_data", {}).get("auto_extraction", {}).get("facts", [])
        )

        prompt = f"""Synthesize the following extracted facts into a definitive Truth Sheet.

EXTRACTED FACTS:
{json.dumps(extracted_facts, indent=2)}

Return a JSON report:
{{
  "entries": [
    {{
      "category": "company/product/market/etc",
      "field_name": "...",
      "value": "...",
      "source": "...",
      "confidence": "high/medium/low"
    }}
  ],
  "completeness_score": 0-100,
  "missing_fields": ["..."],
  "summary": "..."
}}"""

        res = await self._call_llm(prompt)
        try:
            clean_res = res.strip().replace("```json", "").replace("```", "")
            raw_data = json.loads(clean_res)

            entries = [
                TruthEntry(
                    id=self._generate_entry_id(),
                    category=TruthCategory(
                        e["category"].lower()
                        if e["category"].lower() in [t.value for t in TruthCategory]
                        else "company"
                    ),
                    field_name=e["field_name"],
                    value=e["value"],
                    source=e["source"],
                    confidence=ConfidenceLevel(
                        e["confidence"].lower()
                        if e["confidence"].lower()
                        in [cl.value for cl in ConfidenceLevel]
                        else "medium"
                    ),
                    extracted_at=datetime.now().isoformat(),
                )
                for e in raw_data.get("entries", [])
            ]

            sheet = TruthSheet(
                entries=entries,
                completeness_score=raw_data.get("completeness_score", 0),
                categories_covered=list(set(e.category.value for e in entries)),
                missing_fields=raw_data.get("missing_fields", []),
                recommendations=[],
                summary=raw_data.get("summary", ""),
            )
            return {"output": sheet.to_dict()}
        except:
            return {"output": {"error": "Failed to parse AI truth sheet"}}
