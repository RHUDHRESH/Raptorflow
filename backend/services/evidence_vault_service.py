"""
Evidence Vault Intelligence Service
Advanced evidence processing and intelligence for Raptorflow onboarding
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import asyncio
from pathlib import Path

# Import AI agents
from backend.agents.specialists.evidence_classifier import EvidenceClassifier
from backend.agents.specialists.extraction_orchestrator import ExtractionOrchestrator
from backend.agents.specialists.contradiction_detector import ContradictionDetector

# Import OCR and search services
from backend.services.ocr_service import OCRService
from backend.services.storage import get_enhanced_storage_service

logger = logging.getLogger(__name__)


class EvidenceType(str, Enum):
    """Types of evidence documents"""
    FINANCIAL = "financial"
    LEGAL = "legal"
    MARKETING = "marketing"
    PRODUCT = "product"
    STRATEGIC = "strategic"
    COMPETITIVE = "competitive"
    CUSTOMER = "customer"
    OPERATIONAL = "operational"
    TECHNICAL = "technical"
    OTHER = "other"


class ProcessingStatus(str, Enum):
    """Evidence processing status"""
    UPLOADED = "uploaded"
    CLASSIFIED = "classified"
    EXTRACTED = "extracted"
    VALIDATED = "validated"
    ERROR = "error"


@dataclass
class EvidenceItem:
    """Individual evidence item"""
    id: str
    name: str
    type: EvidenceType
    source_type: str  # file, url, text
    source_url: Optional[str] = None
    file_path: Optional[str] = None
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    classification: Dict[str, Any] = field(default_factory=dict)
    extracted_facts: List[Dict[str, Any]] = field(default_factory=list)
    processing_status: ProcessingStatus = ProcessingStatus.UPLOADED
    confidence_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "source_type": self.source_type,
            "source_url": self.source_url,
            "file_path": self.file_path,
            "content": self.content[:1000] + "..." if len(self.content) > 1000 else self.content,
            "metadata": self.metadata,
            "classification": self.classification,
            "extracted_facts_count": len(self.extracted_facts),
            "processing_status": self.processing_status.value,
            "confidence_score": self.confidence_score,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class VaultInsights:
    """Intelligence insights from evidence vault"""
    total_evidence: int
    evidence_types: Dict[str, int]
    processing_summary: Dict[str, int]
    key_themes: List[str]
    confidence_distribution: Dict[str, int]
    quality_score: float
    completeness_score: float
    recommendations: List[str]
    processing_time: float = 0.0


class EvidenceVaultService:
    """Intelligent evidence vault processing service"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize AI agents
        self.evidence_classifier = EvidenceClassifier()
        self.extraction_orchestrator = ExtractionOrchestrator()
        self.contradiction_detector = ContradictionDetector()
        
        # Initialize services
        self.ocr_service = OCRService()
        self.storage_service = get_enhanced_storage_service()
        
        # Evidence storage
        self.evidence_items: Dict[str, EvidenceItem] = {}
        
        # Processing queue
        self.processing_queue: List[str] = []
        self.is_processing = False
    
    async def add_evidence_file(self, file_path: str, file_content: bytes, metadata: Dict[str, Any] = None) -> EvidenceItem:
        """Add evidence file to vault"""
        try:
            # Generate evidence ID
            evidence_id = f"EVI-{len(self.evidence_items) + 1:04d}"
            
            # Extract content using OCR
            extracted_content = await self._extract_file_content(file_path, file_content)
            
            # Create evidence item
            evidence = EvidenceItem(
                id=evidence_id,
                name=Path(file_path).name,
                type=EvidenceType.OTHER,
                source_type="file",
                file_path=file_path,
                content=extracted_content,
                metadata=metadata or {}
            )
            
            # Store evidence
            self.evidence_items[evidence_id] = evidence
            
            # Add to processing queue
            self.processing_queue.append(evidence_id)
            
            # Start processing if not already running
            if not self.is_processing:
                asyncio.create_task(self._process_queue())
            
            self.logger.info(f"Added evidence file: {evidence_id} - {evidence.name}")
            return evidence
            
        except Exception as e:
            self.logger.error(f"Error adding evidence file: {e}")
            raise
    
    async def add_evidence_url(self, url: str, metadata: Dict[str, Any] = None) -> EvidenceItem:
        """Add evidence URL to vault"""
        try:
            # Generate evidence ID
            evidence_id = f"EVI-{len(self.evidence_items) + 1:04d}"
            
            # Extract content from URL
            extracted_content = await self._extract_url_content(url)
            
            # Create evidence item
            evidence = EvidenceItem(
                id=evidence_id,
                name=url,
                type=EvidenceType.OTHER,
                source_type="url",
                source_url=url,
                content=extracted_content,
                metadata=metadata or {}
            )
            
            # Store evidence
            self.evidence_items[evidence_id] = evidence
            
            # Add to processing queue
            self.processing_queue.append(evidence_id)
            
            # Start processing if not already running
            if not self.is_processing:
                asyncio.create_task(self._process_queue())
            
            self.logger.info(f"Added evidence URL: {evidence_id} - {url}")
            return evidence
            
        except Exception as e:
            self.logger.error(f"Error adding evidence URL: {e}")
            raise
    
    async def add_evidence_text(self, text: str, name: str, metadata: Dict[str, Any] = None) -> EvidenceItem:
        """Add evidence text to vault"""
        try:
            # Generate evidence ID
            evidence_id = f"EVI-{len(self.evidence_items) + 1:04d}"
            
            # Create evidence item
            evidence = EvidenceItem(
                id=evidence_id,
                name=name,
                type=EvidenceType.OTHER,
                source_type="text",
                content=text,
                metadata=metadata or {}
            )
            
            # Store evidence
            self.evidence_items[evidence_id] = evidence
            
            # Add to processing queue
            self.processing_queue.append(evidence_id)
            
            # Start processing if not already running
            if not self.is_processing:
                asyncio.create_task(self._process_queue())
            
            self.logger.info(f"Added evidence text: {evidence_id} - {name}")
            return evidence
            
        except Exception as e:
            self.logger.error(f"Error adding evidence text: {e}")
            raise
    
    async def _process_queue(self):
        """Process evidence queue"""
        if self.is_processing:
            return
        
        self.is_processing = True
        
        try:
            while self.processing_queue:
                evidence_id = self.processing_queue.pop(0)
                evidence = self.evidence_items.get(evidence_id)
                
                if evidence:
                    await self._process_evidence(evidence)
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.1)
                
        finally:
            self.is_processing = False
    
    async def _process_evidence(self, evidence: EvidenceItem):
        """Process individual evidence item"""
        try:
            start_time = datetime.now()
            
            # Step 1: Classify evidence
            classification = await self.evidence_classifier.classify_document({
                "content": evidence.content,
                "name": evidence.name,
                "metadata": evidence.metadata
            })
            
            evidence.type = EvidenceType(classification.get("document_type", "other"))
            evidence.classification = classification
            evidence.confidence_score = classification.get("confidence", 0.0)
            evidence.processing_status = ProcessingStatus.CLASSIFIED
            
            # Step 2: Extract facts
            extraction_result = await self.extraction_orchestrator.extract_facts_from_evidence([{
                "id": evidence.id,
                "content": evidence.content,
                "type": evidence.type.value,
                "name": evidence.name
            }])
            
            evidence.extracted_facts = extraction_result.facts
            evidence.processing_status = ProcessingStatus.EXTRACTED
            
            # Step 3: Validate quality
            quality_score = self._calculate_evidence_quality(evidence)
            evidence.metadata["quality_score"] = quality_score
            
            evidence.processing_status = ProcessingStatus.VALIDATED
            evidence.updated_at = datetime.now()
            
            processing_time = (datetime.now() - start_time).total_seconds()
            evidence.metadata["processing_time"] = processing_time
            
            self.logger.info(f"Processed evidence {evidence.id} in {processing_time:.2f}s")
            
        except Exception as e:
            evidence.processing_status = ProcessingStatus.ERROR
            evidence.metadata["error"] = str(e)
            self.logger.error(f"Error processing evidence {evidence.id}: {e}")
    
    async def _extract_file_content(self, file_path: str, file_content: bytes) -> str:
        """Extract content from file using OCR"""
        try:
            # Use OCR service
            result = await self.ocr_service.extract_text_from_bytes(file_content, file_path)
            return result.extracted_text
            
        except Exception as e:
            self.logger.error(f"Error extracting file content: {e}")
            return f"[Error extracting content from {file_path}]: {str(e)}"
    
    async def _extract_url_content(self, url: str) -> str:
        """Extract content from URL"""
        try:
            # Use web scraping service
            from services.web_scraping_service import WebScrapingService
            scraper = WebScrapingService()
            result = await scraper.scrape_url(url)
            return result.content
            
        except Exception as e:
            self.logger.error(f"Error extracting URL content: {e}")
            return f"[Error extracting content from {url}]: {str(e)}"
    
    def _calculate_evidence_quality(self, evidence: EvidenceItem) -> float:
        """Calculate evidence quality score"""
        score = 0.0
        
        # Content length (0-30 points)
        content_length = len(evidence.content)
        if content_length > 5000:
            score += 30
        elif content_length > 1000:
            score += 20
        elif content_length > 100:
            score += 10
        
        # Classification confidence (0-30 points)
        score += evidence.confidence_score * 30
        
        # Fact extraction (0-20 points)
        fact_count = len(evidence.extracted_facts)
        if fact_count > 10:
            score += 20
        elif fact_count > 5:
            score += 15
        elif fact_count > 0:
            score += 10
        
        # Content structure (0-20 points)
        if any(keyword in evidence.content.lower() for keyword in ["summary", "conclusion", "overview"]):
            score += 10
        if any(keyword in evidence.content.lower() for keyword in ["data", "analysis", "research"]):
            score += 10
        
        return min(100.0, score)
    
    async def get_evidence_by_id(self, evidence_id: str) -> Optional[EvidenceItem]:
        """Get evidence by ID"""
        return self.evidence_items.get(evidence_id)
    
    async def get_all_evidence(self) -> List[EvidenceItem]:
        """Get all evidence items"""
        return list(self.evidence_items.values())
    
    async def get_evidence_by_type(self, evidence_type: EvidenceType) -> List[EvidenceItem]:
        """Get evidence by type"""
        return [e for e in self.evidence_items.values() if e.type == evidence_type]
    
    async def get_processing_status(self) -> Dict[str, Any]:
        """Get processing status"""
        status_counts = {}
        for evidence in self.evidence_items.values():
            status = evidence.processing_status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_evidence": len(self.evidence_items),
            "processing_status": status_counts,
            "queue_length": len(self.processing_queue),
            "is_processing": self.is_processing
        }
    
    async def generate_vault_insights(self) -> VaultInsights:
        """Generate comprehensive vault insights"""
        start_time = datetime.now()
        
        # Calculate evidence types distribution
        type_counts = {}
        for evidence in self.evidence_items.values():
            type_name = evidence.type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        # Calculate processing summary
        status_counts = {}
        for evidence in self.evidence_items.values():
            status = evidence.processing_status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Extract key themes
        all_facts = []
        for evidence in self.evidence_items.values():
            all_facts.extend(evidence.extracted_facts)
        
        key_themes = self._extract_key_themes(all_facts)
        
        # Calculate confidence distribution
        confidence_dist = {"high": 0, "medium": 0, "low": 0}
        for evidence in self.evidence_items.values():
            if evidence.confidence_score > 0.7:
                confidence_dist["high"] += 1
            elif evidence.confidence_score > 0.4:
                confidence_dist["medium"] += 1
            else:
                confidence_dist["low"] += 1
        
        # Calculate quality and completeness scores
        quality_scores = [e.metadata.get("quality_score", 0) for e in self.evidence_items.values()]
        quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        completeness_score = self._calculate_completeness_score()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(type_counts, status_counts, quality_score)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return VaultInsights(
            total_evidence=len(self.evidence_items),
            evidence_types=type_counts,
            processing_summary=status_counts,
            key_themes=key_themes,
            confidence_distribution=confidence_dist,
            quality_score=quality_score,
            completeness_score=completeness_score,
            recommendations=recommendations,
            processing_time=processing_time
        )
    
    def _extract_key_themes(self, facts: List[Dict[str, Any]]) -> List[str]:
        """Extract key themes from facts"""
        themes = []
        
        # Count fact categories
        category_counts = {}
        for fact in facts:
            category = fact.get("category", "unknown")
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Get top categories as themes
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        themes = [category for category, count in sorted_categories[:5]]
        
        return themes
    
    def _calculate_completeness_score(self) -> float:
        """Calculate vault completeness score"""
        if not self.evidence_items:
            return 0.0
        
        # Check for different evidence types
        types_present = set(e.type.value for e in self.evidence_items.values())
        required_types = {"financial", "strategic", "competitive", "customer"}
        
        type_score = len(types_present & required_types) / len(required_types) * 40
        
        # Check processing completion
        processed_count = sum(1 for e in self.evidence_items.values() 
                            if e.processing_status == ProcessingStatus.VALIDATED)
        processing_score = (processed_count / len(self.evidence_items)) * 30
        
        # Check fact extraction
        total_facts = sum(len(e.extracted_facts) for e in self.evidence_items.values())
        facts_score = min(30, total_facts / 10)  # Cap at 30 points
        
        return type_score + processing_score + facts_score
    
    def _generate_recommendations(self, type_counts: Dict[str, int], status_counts: Dict[str, int], quality_score: float) -> List[str]:
        """Generate vault recommendations"""
        recommendations = []
        
        # Type-based recommendations
        if "financial" not in type_counts:
            recommendations.append("Add financial documents for comprehensive analysis")
        
        if "competitive" not in type_counts:
            recommendations.append("Include competitive intelligence documents")
        
        if "customer" not in type_counts:
            recommendations.append("Add customer feedback and testimonials")
        
        # Status-based recommendations
        error_count = status_counts.get("error", 0)
        if error_count > 0:
            recommendations.append(f"Resolve {error_count} processing errors")
        
        uploaded_count = status_counts.get("uploaded", 0)
        if uploaded_count > 0:
            recommendations.append(f"Process {uploaded_count} pending evidence items")
        
        # Quality-based recommendations
        if quality_score < 50:
            recommendations.append("Improve evidence quality with more detailed documents")
        
        if len(self.evidence_items) < 5:
            recommendations.append("Add more evidence documents for better insights")
        
        return recommendations
    
    async def search_evidence(self, query: str) -> List[EvidenceItem]:
        """Search evidence content"""
        results = []
        query_lower = query.lower()
        
        for evidence in self.evidence_items.values():
            # Search in content
            if query_lower in evidence.content.lower():
                results.append(evidence)
                continue
            
            # Search in name
            if query_lower in evidence.name.lower():
                results.append(evidence)
                continue
            
            # Search in extracted facts
            for fact in evidence.extracted_facts:
                if query_lower in fact.get("label", "").lower() or query_lower in fact.get("value", "").lower():
                    results.append(evidence)
                    break
        
        return results
    
    async def export_evidence_summary(self) -> Dict[str, Any]:
        """Export evidence summary for onboarding"""
        insights = await self.generate_vault_insights()
        
        return {
            "insights": {
                "total_evidence": insights.total_evidence,
                "quality_score": insights.quality_score,
                "completeness_score": insights.completeness_score,
                "key_themes": insights.key_themes
            },
            "evidence_items": [e.to_dict() for e in self.evidence_items.values()],
            "all_facts": [fact for e in self.evidence_items.values() for fact in e.extracted_facts],
            "recommendations": insights.recommendations,
            "export_timestamp": datetime.now().isoformat()
        }


# Export service
__all__ = ["EvidenceVaultService", "EvidenceItem", "VaultInsights"]
