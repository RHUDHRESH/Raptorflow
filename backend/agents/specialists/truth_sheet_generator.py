"""
Truth Sheet Generator Agent
Auto-populates truth sheets from extracted evidence
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
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
    HIGH = "high"  # Directly stated, verified
    MEDIUM = "medium"  # Inferred with good confidence
    LOW = "low"  # Weak inference, needs verification


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


@dataclass
class TruthSheet:
    """Complete truth sheet"""
    entries: List[TruthEntry]
    completeness_score: float  # 0-1
    categories_covered: List[str]
    missing_fields: List[str]
    recommendations: List[str]
    summary: str


class TruthSheetGenerator:
    """AI-powered truth sheet generation from evidence"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.entry_counter = 0
        self.field_patterns = self._load_field_patterns()
        self.required_fields = self._load_required_fields()
    
    def _load_field_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        """Load patterns for extracting truth sheet fields"""
        return {
            "company": {
                "company_name": [r"(?:company|we are|about)\s*:?\s*([A-Z][a-zA-Z0-9\s]+)", r"^([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)\s+is"],
                "founded_year": [r"founded\s*(?:in)?\s*(\d{4})", r"since\s+(\d{4})", r"established\s*(?:in)?\s*(\d{4})"],
                "headquarters": [r"headquartered?\s*(?:in)?\s*([A-Z][a-zA-Z\s,]+)", r"based\s*(?:in)?\s*([A-Z][a-zA-Z\s,]+)"],
                "team_size": [r"(\d+)\s*(?:employees|team members|people)", r"team\s*(?:of)?\s*(\d+)"],
                "mission": [r"mission\s*(?:is)?\s*:?\s*[\"']?([^\"'\n.]+)[\"']?", r"we\s+(?:aim|strive)\s+to\s+([^.]+)"],
            },
            "product": {
                "product_name": [r"product\s*(?:name)?\s*:?\s*([A-Z][a-zA-Z0-9\s]+)", r"introducing\s+([A-Z][a-zA-Z0-9\s]+)"],
                "product_category": [r"(?:is\s+a|as\s+a)\s+([a-zA-Z\s]+(?:platform|software|tool|solution|app))"],
                "core_feature": [r"(?:key|core|main)\s+feature\s*:?\s*([^.]+)", r"enables?\s+([^.]+)"],
                "pricing_model": [r"(subscription|per\s*seat|usage.based|freemium|one.time)", r"pricing\s*:?\s*([^.]+)"],
                "deployment": [r"(cloud|on.premise|hybrid|saas)", r"deployed?\s*(?:via|on)?\s*([^.]+)"],
            },
            "market": {
                "target_market": [r"target\s*(?:market|audience|customers?)?\s*:?\s*([^.]+)", r"designed\s+for\s+([^.]+)"],
                "market_size": [r"(\$[\d.]+[BMK]?)\s*(?:market|opportunity|TAM)", r"market\s*(?:size|opportunity)\s*:?\s*(\$[\d.]+[BMK]?)"],
                "industry": [r"(?:in\s+the|for\s+the)\s+([a-zA-Z\s]+)\s+(?:industry|sector|space)"],
                "geography": [r"(?:serving|in)\s+(North America|Europe|APAC|Global|US|UK|[A-Z][a-z]+)"],
            },
            "customer": {
                "customer_count": [r"(\d+[K+]?)\s*(?:customers|users|clients)", r"serving\s+(\d+[K+]?)\s+(?:customers|clients)"],
                "notable_customers": [r"(?:customers|clients)\s*(?:include|like)?\s*:?\s*([^.]+)", r"trusted\s+by\s+([^.]+)"],
                "customer_segment": [r"(SMB|enterprise|mid.market|startups?|small\s+business)", r"serving\s+(small|medium|large|enterprise)"],
            },
            "competition": {
                "competitors": [r"(?:competitors?|competing\s+with|vs\.?)\s*:?\s*([^.]+)"],
                "differentiator": [r"(?:unlike|different\s+from|compared\s+to)\s+([^,]+),?\s*we\s+([^.]+)"],
            },
            "financials": {
                "revenue": [r"(\$[\d.]+[BMK]?)\s*(?:in\s+)?(?:revenue|ARR|MRR)", r"revenue\s*:?\s*(\$[\d.]+[BMK]?)"],
                "funding": [r"raised\s+(\$[\d.]+[BMK]?)", r"(\$[\d.]+[BMK]?)\s*(?:in\s+)?funding", r"Series\s+([A-D])"],
                "growth_rate": [r"(\d+%)\s*(?:growth|YoY|MoM)", r"growing\s+(?:at)?\s*(\d+%)"],
            },
        }
    
    def _load_required_fields(self) -> Dict[str, List[str]]:
        """Load required fields for each category"""
        return {
            "company": ["company_name", "mission"],
            "product": ["product_name", "core_feature"],
            "market": ["target_market"],
            "customer": ["customer_segment"],
        }
    
    def _generate_entry_id(self) -> str:
        """Generate unique entry ID"""
        self.entry_counter += 1
        return f"TRU-{self.entry_counter:03d}"
    
    def _extract_field(self, content: str, patterns: List[str]) -> Tuple[Optional[str], Optional[str]]:
        """Extract a field value using patterns"""
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                # Get surrounding context
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 50)
                excerpt = "..." + content[start:end] + "..."
                return value, excerpt
        return None, None
    
    def _determine_confidence(self, value: str, source: str, pattern_matched: bool) -> ConfidenceLevel:
        """Determine confidence level of extraction"""
        # Higher confidence for pitch decks and official docs
        high_confidence_sources = ["pitch deck", "investor", "annual report", "press release"]
        if any(s in source.lower() for s in high_confidence_sources):
            return ConfidenceLevel.HIGH
        
        # Lower confidence for inferred values
        if not pattern_matched or len(value) > 200:
            return ConfidenceLevel.LOW
        
        return ConfidenceLevel.MEDIUM
    
    def _extract_from_content(self, content: str, source: str) -> List[TruthEntry]:
        """Extract truth entries from content"""
        entries = []
        
        for category_name, fields in self.field_patterns.items():
            category = TruthCategory(category_name)
            
            for field_name, patterns in fields.items():
                value, excerpt = self._extract_field(content, patterns)
                
                if value and len(value) > 2:
                    confidence = self._determine_confidence(value, source, True)
                    
                    entry = TruthEntry(
                        id=self._generate_entry_id(),
                        category=category,
                        field_name=field_name,
                        value=value[:500],  # Limit value length
                        source=source,
                        source_excerpt=excerpt,
                        confidence=confidence,
                        extracted_at=datetime.now().isoformat()
                    )
                    entries.append(entry)
        
        return entries
    
    def _deduplicate_entries(self, entries: List[TruthEntry]) -> List[TruthEntry]:
        """Remove duplicate entries, keeping highest confidence"""
        field_map: Dict[str, TruthEntry] = {}
        
        for entry in entries:
            key = f"{entry.category.value}:{entry.field_name}"
            
            if key not in field_map:
                field_map[key] = entry
            else:
                # Keep higher confidence entry
                existing = field_map[key]
                confidence_order = {ConfidenceLevel.HIGH: 3, ConfidenceLevel.MEDIUM: 2, ConfidenceLevel.LOW: 1}
                if confidence_order[entry.confidence] > confidence_order[existing.confidence]:
                    field_map[key] = entry
        
        return list(field_map.values())
    
    def _calculate_completeness(self, entries: List[TruthEntry]) -> Tuple[float, List[str]]:
        """Calculate completeness score and find missing fields"""
        extracted_fields = {(e.category.value, e.field_name) for e in entries}
        
        total_required = 0
        found_required = 0
        missing = []
        
        for category, fields in self.required_fields.items():
            for field in fields:
                total_required += 1
                if (category, field) in extracted_fields:
                    found_required += 1
                else:
                    missing.append(f"{category}.{field}")
        
        score = found_required / total_required if total_required > 0 else 0
        return score, missing
    
    async def generate_truth_sheet(self, evidence_list: List[Dict[str, Any]], existing_entries: List[Dict[str, Any]] = None) -> TruthSheet:
        """
        Generate a truth sheet from evidence
        
        Args:
            evidence_list: List of evidence documents with content
            existing_entries: Optional existing truth sheet entries to merge
        
        Returns:
            TruthSheet with extracted and merged entries
        """
        all_entries = []
        
        # Process each evidence item
        for evidence in evidence_list:
            content = evidence.get("content", "") or evidence.get("extracted_text", "")
            source = evidence.get("source", "") or evidence.get("filename", "Unknown")
            
            if content:
                entries = self._extract_from_content(content, source)
                all_entries.extend(entries)
        
        # Deduplicate
        deduplicated = self._deduplicate_entries(all_entries)
        
        # Merge with existing entries (user edits take priority)
        if existing_entries:
            for existing in existing_entries:
                if existing.get("user_edited"):
                    # Find and replace or add
                    key = f"{existing.get('category')}:{existing.get('field_name')}"
                    found = False
                    for i, entry in enumerate(deduplicated):
                        if f"{entry.category.value}:{entry.field_name}" == key:
                            deduplicated[i] = TruthEntry(
                                id=existing.get("id", self._generate_entry_id()),
                                category=TruthCategory(existing.get("category", "company")),
                                field_name=existing.get("field_name", ""),
                                value=existing.get("value", ""),
                                source="User Input",
                                confidence=ConfidenceLevel.HIGH,
                                verified=True,
                                user_edited=True,
                                extracted_at=existing.get("extracted_at", datetime.now().isoformat())
                            )
                            found = True
                            break
                    if not found:
                        deduplicated.append(TruthEntry(
                            id=existing.get("id", self._generate_entry_id()),
                            category=TruthCategory(existing.get("category", "company")),
                            field_name=existing.get("field_name", ""),
                            value=existing.get("value", ""),
                            source="User Input",
                            confidence=ConfidenceLevel.HIGH,
                            verified=True,
                            user_edited=True,
                            extracted_at=datetime.now().isoformat()
                        ))
        
        # Calculate completeness
        completeness, missing = self._calculate_completeness(deduplicated)
        
        # Get covered categories
        categories = list(set(e.category.value for e in deduplicated))
        
        # Generate recommendations
        recommendations = []
        if completeness < 0.5:
            recommendations.append("Truth sheet is less than 50% complete - upload more evidence")
        if missing:
            recommendations.append(f"Missing critical fields: {', '.join(missing[:5])}")
        if not any(e.confidence == ConfidenceLevel.HIGH for e in deduplicated):
            recommendations.append("No high-confidence entries - verify key information manually")
        
        # Generate summary
        high_conf = sum(1 for e in deduplicated if e.confidence == ConfidenceLevel.HIGH)
        summary = f"Generated {len(deduplicated)} truth entries from {len(evidence_list)} evidence items. "
        summary += f"Completeness: {completeness:.0%}. High-confidence entries: {high_conf}."
        
        return TruthSheet(
            entries=deduplicated,
            completeness_score=completeness,
            categories_covered=categories,
            missing_fields=missing,
            recommendations=recommendations,
            summary=summary
        )
    
    def get_truth_sheet_summary(self, sheet: TruthSheet) -> Dict[str, Any]:
        """Get summary for display"""
        return {
            "entry_count": len(sheet.entries),
            "completeness": sheet.completeness_score,
            "categories": sheet.categories_covered,
            "missing_count": len(sheet.missing_fields),
            "missing_fields": sheet.missing_fields[:5],
            "summary": sheet.summary,
            "recommendations": sheet.recommendations[:3]
        }
    
    def entries_to_dict(self, entries: List[TruthEntry]) -> Dict[str, Dict[str, Any]]:
        """Convert entries to a nested dictionary by category"""
        result: Dict[str, Dict[str, Any]] = {}
        
        for entry in entries:
            cat = entry.category.value
            if cat not in result:
                result[cat] = {}
            
            result[cat][entry.field_name] = {
                "id": entry.id,
                "value": entry.value,
                "source": entry.source,
                "confidence": entry.confidence.value,
                "verified": entry.verified,
                "user_edited": entry.user_edited
            }
        
        return result
