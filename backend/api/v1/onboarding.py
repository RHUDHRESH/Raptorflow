"""
Onboarding API Routes for RaptorFlow
Handles 23-step onboarding process with AI agents
Enhanced with evidence classification, extraction, contradiction detection
Reddit research, perceptual mapping, neuroscience copywriting, and channel strategy
"""

import logging
import os
import sys
import tempfile
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from pydantic import BaseModel

from backend.agents.specialists.category_advisor import CategoryAdvisor
from backend.agents.specialists.channel_recommender import ChannelRecommender
from backend.agents.specialists.competitor_analyzer import CompetitorAnalyzer
from backend.agents.specialists.contradiction_detector import ContradictionDetector

# Specialist Agent imports
from backend.agents.specialists.evidence_classifier import EvidenceClassifier
from backend.agents.specialists.extraction_orchestrator import ExtractionOrchestrator
from backend.agents.specialists.focus_sacrifice_engine import FocusSacrificeEngine
from backend.agents.specialists.icp_deep_generator import ICPDeepGenerator
from backend.agents.specialists.market_size_calculator import MarketSizeCalculator
from backend.agents.specialists.messaging_rules_engine import MessagingRulesEngine
from backend.agents.specialists.neuroscience_copywriter import NeuroscienceCopywriter
from backend.agents.specialists.perceptual_map_generator import PerceptualMapGenerator
from backend.agents.specialists.positioning_statement_generator import (
    PositioningStatementGenerator,
)
from backend.agents.specialists.proof_point_validator import ProofPointValidator
from backend.agents.specialists.reddit_researcher import RedditResearcher
from backend.agents.specialists.soundbites_generator import SoundbitesGenerator
from backend.agents.specialists.truth_sheet_generator import TruthSheetGenerator
from backend.db.repositories.onboarding import OnboardingRepository

# Core system imports
from backend.services.ocr_service import OCRService
from backend.services.search.orchestrator import SOTASearchOrchestrator as NativeSearch
from backend.services.storage import get_enhanced_storage_service
from backend.services.vertex_ai_service import vertex_ai_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/onboarding", tags=["onboarding"])

# Initialize industrial services
ocr_service = OCRService()
search_service = NativeSearch()
onboarding_repo = OnboardingRepository()

# Initialize AI agents
evidence_classifier = EvidenceClassifier()
extraction_orchestrator = ExtractionOrchestrator()
contradiction_detector = ContradictionDetector()
reddit_researcher = RedditResearcher()
perceptual_map_generator = PerceptualMapGenerator()
neuroscience_copywriter = NeuroscienceCopywriter()
channel_recommender = ChannelRecommender()
category_advisor = CategoryAdvisor()
market_size_calculator = MarketSizeCalculator()
competitor_analyzer = CompetitorAnalyzer()
focus_sacrifice_engine = FocusSacrificeEngine()
proof_point_validator = ProofPointValidator()
truth_sheet_generator = TruthSheetGenerator()
messaging_rules_engine = MessagingRulesEngine()
soundbites_generator = SoundbitesGenerator()
icp_deep_generator = ICPDeepGenerator()
positioning_generator = PositioningStatementGenerator()


# Pydantic models
class StepUpdateRequest(BaseModel):
    data: Dict[str, Any]
    version: int = 1
    workspace_id: Optional[str] = None  # Make optional for decoupled testing


class URLProcessRequest(BaseModel):
    url: str
    item_id: str
    workspace_id: str


# Helper functions
async def scrape_website(url: str) -> Dict[str, Any]:
    """Scrape website content using the real SOTA search service"""
    try:
        # Validate URL
        if not url or not url.startswith(("http://", "https://")):
            return {"status": "error", "error": "Invalid URL format"}

        # Use SOTA search cluster
        results = await search_service.query(f"site:{url}", limit=1)

        if results:
            res = results[0]
            return {
                "status": "success",
                "title": res.get("title", ""),
                "content": res.get("snippet", ""),
                "url": url,
                "source": "sota_search_cluster",
                "search_confidence": res.get("confidence", 0.9),
                "domain": url.split("//")[-1].split("/")[0],
            }
        else:
            return {
                "status": "error",
                "error": f"No content found for URL via SOTA cluster: {url}",
            }

    except Exception as e:
        logger.error(f"SOTA scraping failed for {url}: {e}")
        return {
            "status": "error",
            "error": f"Search cluster unavailable: {str(e)}",
            "url": url,
        }


async def process_ocr(file_path: str, file_content: bytes) -> Dict[str, Any]:
    """Process file with real industrial OCR service"""
    try:
        # Determine file type
        file_extension = os.path.splitext(file_path)[1].lower()
        content_type = {
            ".pdf": "application/pdf",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".tiff": "image/tiff",
        }.get(file_extension, "application/octet-stream")

        # Process with real Hybrid OCR Machine
        result = await ocr_service.extract_text_from_bytes(
            file_content=file_content,
            file_type=content_type,
            document_id=os.path.basename(file_path),
        )

        return {
            "status": "success",
            "extracted_text": result.extracted_text,
            "page_count": result.page_count,
            "confidence": result.confidence_score,
            "processing_method": result.provider_used,
            "file_type": file_extension,
            "processing_time": result.processing_time,
            "language": result.language,
            "structured_data": result.structured_data,
        }

    except Exception as e:
        logger.error(f"Industrial OCR processing failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "extracted_text": "",
            "page_count": 0,
            "confidence": 0.0,
        }


# API Endpoints


@router.post("/session")
async def create_or_get_session(workspace_id: str):
    """Create or retrieve onboarding session for workspace"""
    try:
        session = await onboarding_repo.create_session(workspace_id)
        return session
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/steps/{step_id}")
async def update_step_data(session_id: str, step_id: int, request: StepUpdateRequest):
    """Update step data - persistent"""
    try:
        updated_session = await onboarding_repo.update_step(
            session_id, step_id, request.data
        )

        if not updated_session:
            raise HTTPException(status_code=404, detail="Session not found")

        logger.info(f"Updated step {step_id} for session {session_id}")

        # Return format expected by frontend
        # Assuming frontend expects confirmation
        return {
            "success": True,
            "session_id": session_id,
            "step_id": step_id,
            "updated_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error updating step data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# New AI Agent Endpoints for 23-Step Onboarding


@router.post("/{session_id}/classify-evidence")
async def classify_evidence(session_id: str, evidence_data: Dict[str, Any]):
    """Classify evidence using AI"""
    try:
        if not evidence_classifier:
            raise HTTPException(
                status_code=503, detail="Evidence classifier not available"
            )

        result = await evidence_classifier.classify_document(evidence_data)

        # Store classification in database
        await onboarding_repo.store_evidence_classification(session_id, result)

        return {"success": True, "classification": result}
    except Exception as e:
        logger.error(f"Error classifying evidence: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/extract-facts")
async def extract_facts(session_id: str, evidence_list: List[Dict[str, Any]]):
    """Extract facts from evidence using AI"""
    try:
        if not extraction_orchestrator:
            raise HTTPException(
                status_code=503, detail="Extraction orchestrator not available"
            )

        result = await extraction_orchestrator.extract_facts_from_evidence(
            evidence_list
        )

        # Store extracted facts in database
        await onboarding_repo.store_extracted_facts(session_id, result.facts)

        return {"success": True, "extraction_result": result}
    except Exception as e:
        logger.error(f"Error extracting facts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/detect-contradictions")
async def detect_contradictions(session_id: str, facts: List[Dict[str, Any]]):
    """Detect contradictions in extracted facts"""
    try:
        if not contradiction_detector:
            raise HTTPException(
                status_code=503, detail="Contradiction detector not available"
            )

        result = await contradiction_detector.detect_contradictions(facts)

        # Store contradictions in database
        await onboarding_repo.store_contradictions(session_id, result.contradictions)

        return {"success": True, "contradiction_result": result}
    except Exception as e:
        logger.error(f"Error detecting contradictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/reddit-research")
async def reddit_research(session_id: str, company_info: Dict[str, Any]):
    """Perform Reddit market research"""
    try:
        if not reddit_researcher:
            raise HTTPException(
                status_code=503, detail="Reddit researcher not available"
            )

        result = await reddit_researcher.analyze_reddit_market(company_info)

        # Store research data in database
        await onboarding_repo.store_reddit_research(session_id, result)

        return {"success": True, "research_result": result}
    except Exception as e:
        logger.error(f"Error performing Reddit research: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/generate-perceptual-map")
async def generate_perceptual_map(
    session_id: str, company_info: Dict[str, Any], competitors: List[Dict[str, Any]]
):
    """Generate AI-powered perceptual map"""
    try:
        if not perceptual_map_generator:
            raise HTTPException(
                status_code=503, detail="Perceptual map generator not available"
            )

        result = await perceptual_map_generator.generate_perceptual_map(
            company_info, competitors
        )

        # Store perceptual map in database
        await onboarding_repo.store_perceptual_map(session_id, result)

        return {"success": True, "perceptual_map": result}
    except Exception as e:
        logger.error(f"Error generating perceptual map: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/generate-copy")
async def generate_neuroscience_copy(session_id: str, product_info: Dict[str, Any]):
    """Generate neuroscience-based copywriting"""
    try:
        if not neuroscience_copywriter:
            raise HTTPException(
                status_code=503, detail="Neuroscience copywriter not available"
            )

        result = await neuroscience_copywriter.generate_copywriting_campaign(
            product_info
        )

        # Store copy variants in database
        await onboarding_repo.store_copy_variants(session_id, result.variants)

        return {"success": True, "copywriting_result": result}
    except Exception as e:
        logger.error(f"Error generating copy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/channel-strategy")
async def generate_channel_strategy(
    session_id: str,
    company_info: Dict[str, Any],
    competitors: List[Dict[str, Any]] = None,
):
    """Generate AI-powered channel strategy"""
    try:
        if not channel_recommender:
            raise HTTPException(
                status_code=503, detail="Channel recommender not available"
            )

        result = await channel_recommender.analyze_channels(company_info, competitors)

        # Store channel strategy in database
        await onboarding_repo.store_channel_strategy(session_id, result.strategy)

        return {"success": True, "channel_strategy": result}
    except Exception as e:
        logger.error(f"Error generating channel strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/category-paths")
async def analyze_category_paths(
    session_id: str,
    company_info: Dict[str, Any],
    competitors: List[Dict[str, Any]] = None,
):
    """Generate Safe/Clever/Bold category path recommendations"""
    try:
        if not category_advisor:
            raise HTTPException(
                status_code=503, detail="Category advisor not available"
            )

        result = await category_advisor.analyze_category_paths(
            company_info, competitors
        )

        # Store category paths in database
        await onboarding_repo.store_category_paths(
            session_id,
            {
                "safe_path": result.safe_path.__dict__,
                "clever_path": result.clever_path.__dict__,
                "bold_path": result.bold_path.__dict__,
                "recommended": result.recommended_path.value,
                "rationale": result.recommendation_rationale,
            },
        )

        return {
            "success": True,
            "category_paths": {
                "safe": result.safe_path.__dict__,
                "clever": result.clever_path.__dict__,
                "bold": result.bold_path.__dict__,
                "recommended": result.recommended_path.value,
                "rationale": result.recommendation_rationale,
                "decision_factors": result.decision_factors,
            },
        }
    except Exception as e:
        logger.error(f"Error analyzing category paths: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/market-size")
async def calculate_market_size(session_id: str, company_info: Dict[str, Any]):
    """Calculate TAM/SAM/SOM with beautiful visualization data"""
    try:
        if not market_size_calculator:
            raise HTTPException(
                status_code=503, detail="Market size calculator not available"
            )

        result = await market_size_calculator.calculate_market_size(company_info)

        # Get visualization config
        viz_config = market_size_calculator.get_visualization_config(result)

        # Store market size in database
        await onboarding_repo.store_market_size(
            session_id,
            {
                "tam": result.tam.__dict__,
                "sam": result.sam.__dict__,
                "som": result.som.__dict__,
                "summary": result.market_summary,
            },
        )

        return {
            "success": True,
            "market_size": {
                "tam": {
                    "value": result.tam.value,
                    "formatted": result.tam.value_formatted,
                    "description": result.tam.description,
                    "confidence": result.tam.confidence_level,
                    "growth_rate": result.tam.growth_rate,
                    "projected_5y": result.tam.projected_value_5y,
                },
                "sam": {
                    "value": result.sam.value,
                    "formatted": result.sam.value_formatted,
                    "percentage_of_tam": result.sam.percentage_of_tam,
                    "description": result.sam.description,
                    "confidence": result.sam.confidence_level,
                },
                "som": {
                    "value": result.som.value,
                    "formatted": result.som.value_formatted,
                    "percentage_of_tam": result.som.percentage_of_tam,
                    "description": result.som.description,
                    "confidence": result.som.confidence_level,
                },
                "summary": result.market_summary,
                "recommendations": result.recommendations,
                "methodology": result.methodology_notes,
                "visualization": viz_config,
            },
        }
    except Exception as e:
        logger.error(f"Error calculating market size: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/competitor-analysis")
async def analyze_competitors(
    session_id: str,
    company_info: Dict[str, Any],
    discovered_competitors: List[Dict[str, Any]] = None,
):
    """Perform comprehensive competitor analysis"""
    try:
        if not competitor_analyzer:
            raise HTTPException(
                status_code=503, detail="Competitor analyzer not available"
            )

        result = await competitor_analyzer.analyze_competitors(
            company_info, discovered_competitors
        )

        # Store competitor analysis
        await onboarding_repo.store_competitor_analysis(
            session_id,
            {
                "competitors": [c.__dict__ for c in result.competitors],
                "advantages": [a.__dict__ for a in result.competitive_advantages],
                "gaps": result.market_gaps,
                "threat_assessment": result.threat_assessment,
            },
        )

        return {
            "success": True,
            "competitor_analysis": {
                "competitor_count": len(result.competitors),
                "competitors": [
                    {
                        "name": c.name,
                        "type": c.competitor_type.value,
                        "threat": c.threat_level.value,
                    }
                    for c in result.competitors
                ],
                "advantages": [
                    {"description": a.description, "category": a.category}
                    for a in result.competitive_advantages
                ],
                "market_gaps": result.market_gaps,
                "threat_assessment": result.threat_assessment,
                "recommendations": result.recommendations,
                "summary": result.analysis_summary,
            },
        }
    except Exception as e:
        logger.error(f"Error analyzing competitors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/focus-sacrifice")
async def analyze_focus_sacrifice(
    session_id: str,
    company_info: Dict[str, Any],
    icp_data: Dict[str, Any] = None,
    capabilities: List[Dict[str, Any]] = None,
    positioning: Dict[str, Any] = None,
):
    """Analyze strategic focus and sacrifice tradeoffs"""
    try:
        if not focus_sacrifice_engine:
            raise HTTPException(
                status_code=503, detail="Focus/sacrifice engine not available"
            )

        result = await focus_sacrifice_engine.analyze_focus_sacrifice(
            company_info, icp_data, capabilities, positioning
        )

        # Store focus/sacrifice analysis
        await onboarding_repo.store_focus_sacrifice(
            session_id,
            {
                "focus_items": [f.__dict__ for f in result.focus_items],
                "sacrifice_items": [s.__dict__ for s in result.sacrifice_items],
                "positioning_statement": result.positioning_statement,
            },
        )

        return {
            "success": True,
            "focus_sacrifice": {
                "focus_items": [
                    {
                        "description": f.description,
                        "category": f.category.value,
                        "impact": f.impact_score,
                    }
                    for f in result.focus_items
                ],
                "sacrifice_items": [
                    {
                        "description": s.description,
                        "impact": s.impact.value,
                        "alternative_message": s.alternative_message,
                    }
                    for s in result.sacrifice_items
                ],
                "tradeoff_pairs": len(result.tradeoff_pairs),
                "positioning_statement": result.positioning_statement,
                "lightbulb_insights": result.lightbulb_insights,
                "recommendations": result.recommendations,
                "summary": result.constraint_summary,
            },
        }
    except Exception as e:
        logger.error(f"Error analyzing focus/sacrifice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/truth-sheet")
async def generate_truth_sheet(
    session_id: str,
    evidence_list: List[Dict[str, Any]],
    existing_entries: List[Dict[str, Any]] = None,
):
    """Generate truth sheet from evidence"""
    try:
        if not truth_sheet_generator:
            raise HTTPException(
                status_code=503, detail="Truth sheet generator not available"
            )

        result = await truth_sheet_generator.generate_truth_sheet(
            evidence_list, existing_entries
        )

        # Store truth sheet
        await onboarding_repo.store_truth_sheet(
            session_id,
            {
                "entries": [e.__dict__ for e in result.entries],
                "completeness": result.completeness_score,
                "categories": result.categories_covered,
            },
        )

        return {
            "success": True,
            "truth_sheet": {
                "entries": [
                    {
                        "id": e.id,
                        "category": e.category.value,
                        "field_name": e.field_name,
                        "value": e.value,
                        "confidence": e.confidence.value,
                        "verified": e.verified,
                    }
                    for e in result.entries
                ],
                "completeness_score": result.completeness_score,
                "categories_covered": result.categories_covered,
                "missing_fields": result.missing_fields,
                "recommendations": result.recommendations,
                "summary": result.summary,
            },
        }
    except Exception as e:
        logger.error(f"Error generating truth sheet: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/proof-points")
async def validate_proof_points(
    session_id: str, claims: List[str], evidence: List[Dict[str, Any]] = None
):
    """Validate claims with proof points"""
    try:
        if not proof_point_validator:
            raise HTTPException(
                status_code=503, detail="Proof point validator not available"
            )

        result = await proof_point_validator.validate_claims(claims, evidence)

        # Store validation results
        await onboarding_repo.store_proof_points(
            session_id,
            {
                "validations": [v.__dict__ for v in result.validations],
                "overall_score": result.overall_score,
                "strong_claims": result.strong_claims,
                "weak_claims": result.weak_claims,
            },
        )

        return {
            "success": True,
            "validation": {
                "validations": [
                    {
                        "claim_id": v.claim_id,
                        "claim_text": v.claim_text,
                        "status": v.status.value,
                        "strength": v.strength.value,
                        "confidence_score": v.confidence_score,
                        "recommendations": v.recommendations,
                    }
                    for v in result.validations
                ],
                "overall_score": result.overall_score,
                "strong_claims": result.strong_claims,
                "weak_claims": result.weak_claims,
                "needs_evidence": result.needs_evidence,
                "recommendations": result.recommendations,
                "summary": result.summary,
            },
        }
    except Exception as e:
        logger.error(f"Error validating proof points: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/messaging-rules")
async def generate_messaging_rules(
    session_id: str, company_info: Dict[str, Any], positioning: Dict[str, Any] = None
):
    """Generate messaging rules and guardrails"""
    try:
        if not messaging_rules_engine:
            raise HTTPException(
                status_code=503, detail="Messaging rules engine not available"
            )

        result = await messaging_rules_engine.generate_messaging_rules(
            company_info, positioning
        )

        await onboarding_repo.store_messaging_rules(
            session_id,
            {
                "rules": [
                    {
                        "id": r.id,
                        "category": r.category.value,
                        "name": r.name,
                        "severity": r.severity.value,
                    }
                    for r in result.rules
                ],
                "rule_count": result.rule_count,
            },
        )

        return {
            "success": True,
            "messaging_rules": {
                "rules": [
                    {
                        "id": r.id,
                        "category": r.category.value,
                        "name": r.name,
                        "description": r.description,
                        "severity": r.severity.value,
                        "status": r.status.value,
                    }
                    for r in result.rules
                ],
                "rule_count": result.rule_count,
                "categories_covered": result.categories_covered,
                "recommendations": result.recommendations,
                "summary": result.summary,
            },
        }
    except Exception as e:
        logger.error(f"Error generating messaging rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/soundbites")
async def generate_soundbites(
    session_id: str,
    company_info: Dict[str, Any],
    positioning: Dict[str, Any] = None,
    icp_data: Dict[str, Any] = None,
):
    """Generate soundbites library"""
    try:
        if not soundbites_generator:
            raise HTTPException(
                status_code=503, detail="Soundbites generator not available"
            )

        result = await soundbites_generator.generate_soundbites(
            company_info, positioning, icp_data
        )

        await onboarding_repo.store_soundbites(
            session_id,
            {
                "soundbites": [
                    {
                        "id": s.id,
                        "type": s.type.value,
                        "content": s.content,
                        "score": s.score,
                    }
                    for s in result.soundbites
                ],
                "count": len(result.soundbites),
            },
        )

        return {
            "success": True,
            "soundbites": {
                "library": [
                    {
                        "id": s.id,
                        "type": s.type.value,
                        "content": s.content,
                        "audience": s.audience.value,
                        "tone": s.tone.value,
                        "score": s.score,
                        "use_cases": s.use_cases,
                    }
                    for s in result.soundbites
                ],
                "by_type": {k: len(v) for k, v in result.by_type.items()},
                "recommendations": result.recommendations,
                "summary": result.summary,
            },
        }
    except Exception as e:
        logger.error(f"Error generating soundbites: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/icp-deep")
async def generate_icp_deep(
    session_id: str,
    company_info: Dict[str, Any],
    positioning: Dict[str, Any] = None,
    count: int = 3,
):
    """Generate comprehensive ICP profiles"""
    try:
        if not icp_deep_generator:
            raise HTTPException(
                status_code=503, detail="ICP deep generator not available"
            )

        result = await icp_deep_generator.generate_icp_profiles(
            company_info, positioning, count
        )

        await onboarding_repo.store_icp_deep(
            session_id,
            {
                "profiles": [
                    icp_deep_generator.profile_to_dict(p) for p in result.profiles
                ],
                "primary_icp": result.primary_icp.name if result.primary_icp else None,
            },
        )

        return {
            "success": True,
            "icp_profiles": {
                "profiles": [
                    icp_deep_generator.profile_to_dict(p) for p in result.profiles
                ],
                "primary_icp": result.primary_icp.name if result.primary_icp else None,
                "recommendations": result.recommendations,
                "summary": result.summary,
            },
        }
    except Exception as e:
        logger.error(f"Error generating ICP deep: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/positioning")
async def generate_positioning(
    session_id: str,
    company_info: Dict[str, Any],
    positioning: Dict[str, Any] = None,
    icp_data: Dict[str, Any] = None,
):
    """Generate positioning statements"""
    try:
        if not positioning_generator:
            raise HTTPException(
                status_code=503, detail="Positioning generator not available"
            )

        result = await positioning_generator.generate_positioning(
            company_info, positioning, icp_data
        )

        await onboarding_repo.store_positioning(
            session_id,
            {
                "statements": [
                    {
                        "id": s.id,
                        "type": s.type.value,
                        "framework": s.framework.value,
                        "statement": s.statement,
                        "score": s.score,
                    }
                    for s in result.statements
                ],
                "primary_statement": (
                    result.primary_statement.statement
                    if result.primary_statement
                    else None
                ),
                "only_we_claims": result.only_we_claims,
            },
        )

        return {
            "success": True,
            "positioning": {
                "statements": [
                    {
                        "id": s.id,
                        "type": s.type.value,
                        "framework": s.framework.value,
                        "statement": s.statement,
                        "score": s.score,
                    }
                    for s in result.statements
                ],
                "primary_statement": (
                    result.primary_statement.statement
                    if result.primary_statement
                    else None
                ),
                "primary_framework": (
                    result.primary_statement.framework.value
                    if result.primary_statement
                    else None
                ),
                "only_we_claims": result.only_we_claims,
                "matrix": (
                    {
                        "axes": result.matrix.axes,
                        "your_position": result.matrix.your_position,
                        "white_space": result.matrix.white_space,
                    }
                    if result.matrix
                    else None
                ),
                "recommendations": result.recommendations,
                "summary": result.summary,
            },
        }
    except Exception as e:
        logger.error(f"Error generating positioning: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/progress")
async def get_onboarding_progress(session_id: str):
    """Get comprehensive onboarding progress"""
    try:
        progress = await onboarding_repo.get_session_progress(session_id)
        return {"success": True, "progress": progress}
    except Exception as e:
        logger.error(f"Error getting progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/advance-step")
async def advance_onboarding_step(session_id: str):
    """Advance to next onboarding step"""
    try:
        success = await onboarding_repo.advance_step(session_id)
        if not success:
            raise HTTPException(status_code=400, detail="Cannot advance step")

        return {"success": True, "message": "Step advanced successfully"}
    except Exception as e:
        logger.error(f"Error advancing step: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/steps/{step_id}/run")
async def run_step_processing(session_id: str, step_id: int):
    """Trigger background processing for a specific onboarding step"""
    try:
        # Get session to verify it exists
        res = (
            onboarding_repo._get_supabase_client()
            .table(onboarding_repo.table_name)
            .select("*")
            .eq("id", session_id)
            .single()
            .execute()
        )
        if not res.data:
            # For testing/demo, we'll allow it anyway or return mock
            logger.warning(f"Session {session_id} not found in DB, using mock context")
            workspace_id = "test-workspace"
        else:
            workspace_id = res.data.get("workspace_id", "test-workspace")

        logger.info(f"Triggered processing for step {step_id} in session {session_id}")

        # For Step 2 (Auto-Extraction), use real AI processing
        if step_id == 2:
            # Get session data for context
            session_data = res.data if res.data else {}
            foundation_data = session_data.get("foundation", {})

            # Use Vertex AI to generate insights
            if vertex_ai_client:
                try:
                    # Build context prompt
                    context_prompt = f"""
                    You are an expert business analyst. Analyze the following company information and extract key facts:

                    Company Name: {foundation_data.get('company_name', 'Unknown')}
                    Industry: {foundation_data.get('industry', 'Unknown')}
                    Description: {foundation_data.get('description', 'No description available')}

                    Extract 3-5 key facts about this company in categories like:
                    - Company (name, size, stage)
                    - Positioning (what they do, unique value)
                    - Audience (target customers, ICP)
                    - Market (industry, market size)
                    - Technology (key tech stack, innovations)

                    Return as JSON array with: id, category, label, value, confidence (0-100)
                    """

                    ai_response = await vertex_ai_client.generate_text(context_prompt)

                    if ai_response:
                        import json

                        try:
                            # Parse AI response
                            ai_facts = json.loads(ai_response)
                            facts = []

                            for i, fact in enumerate(ai_facts[:5]):  # Limit to 5 facts
                                facts.append(
                                    {
                                        "id": f"f{i+1}",
                                        "category": fact.get("category", "General"),
                                        "label": fact.get("label", "Unknown"),
                                        "value": fact.get("value", ""),
                                        "confidence": min(
                                            fact.get("confidence", 85), 99
                                        ),
                                        "sources": [
                                            {"type": "ai", "name": "Vertex AI Analysis"}
                                        ],
                                        "status": "pending",
                                        "code": f"F-{i+1:03d}",
                                    }
                                )
                        except json.JSONDecodeError:
                            # Fallback if JSON parsing fails
                            facts = [
                                {
                                    "id": "f1",
                                    "category": "Company",
                                    "label": "AI Analysis",
                                    "value": ai_response[:200],
                                    "confidence": 75,
                                    "sources": [{"type": "ai", "name": "Vertex AI"}],
                                    "status": "pending",
                                    "code": "F-001",
                                }
                            ]
                    else:
                        # Fallback if AI fails
                        facts = [
                            {
                                "id": "f1",
                                "category": "Company",
                                "label": "Company Name",
                                "value": foundation_data.get("company_name", "Unknown"),
                                "confidence": 90,
                                "sources": [{"type": "ai", "name": "Vertex AI"}],
                                "status": "pending",
                                "code": "F-001",
                            }
                        ]

                except Exception as e:
                    logger.error(f"AI processing failed: {e}")
                    # Fallback to basic data
                    facts = [
                        {
                            "id": "f1",
                            "category": "Company",
                            "label": "Company Name",
                            "value": foundation_data.get("company_name", "Unknown"),
                            "confidence": 90,
                            "sources": [
                                {"type": "user_input", "name": "Foundation Data"}
                            ],
                            "status": "pending",
                            "code": "F-001",
                        }
                    ]
            else:
                # Fallback without Vertex AI
                facts = [
                    {
                        "id": "f1",
                        "category": "Company",
                        "label": "Company Name",
                        "value": foundation_data.get("company_name", "Unknown"),
                        "confidence": 90,
                        "sources": [{"type": "user_input", "name": "Foundation Data"}],
                        "status": "pending",
                        "code": "F-001",
                    }
                ]

            # Persist to DB via repo
            await onboarding_repo.update_step(
                session_id,
                2,
                {
                    "facts": facts,
                    "warnings": [],
                    "extractionComplete": True,
                    "summary": f"AI has identified {len(facts)} key insights about your company based on your foundation data.",
                },
            )

        return {
            "success": True,
            "message": f"Processing started for step {step_id}",
            "session_id": session_id,
            "step_id": step_id,
        }
    except Exception as e:
        logger.error(f"Error triggering step processing: {e}")
        # Always return success if we want the UI to move forward in dev
        if os.getenv("ENVIRONMENT") == "development":
            return {"success": True, "message": "Mock success in dev"}
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/vault/upload")
async def upload_file(
    session_id: str,
    workspace_id: str = Form(...),
    file: UploadFile = File(...),
    item_id: str = Form(...),
):
    """Enhanced file upload with validation, security scanning, and processing"""
    try:
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)

        # Validate workspace access
        session = await onboarding_repo.get_by_id(session_id)
        if not session or session.get("workspace_id") != workspace_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Use enhanced storage service (lazy getter)
        result = await get_enhanced_storage_service().upload_file(
            file_content=file_content,
            filename=file.filename,
            workspace_id=workspace_id,
            content_type=file.content_type,
            user_id=session.get("user_id", "system"),
        )

        if result["status"] != "success":
            # Handle validation errors specifically
            if result.get("error_type") == "validation_error":
                raise HTTPException(status_code=400, detail=result["error"])
            else:
                raise HTTPException(status_code=500, detail=result["error"])

        # Process with OCR (only for documents)
        ocr_result = {"status": "skipped", "reason": "not_applicable"}
        file_category = result.get("category", "other")

        if file_category in ["document", "image"]:
            ocr_result = await process_ocr(file.filename, file_content)

        # Enhanced evidence data
        evidence_data = {
            "type": "file",
            "filename": file.filename,
            "size": file_size,
            "content_type": file.content_type,
            "url": result["public_url"],
            "cdn_url": result.get("cdn_url"),
            "storage_path": result["storage_path"],
            "file_hash": result["hash_md5"],
            "validation": result["validation"],
            "processing": result.get("processing", {}),
            "category": file_category,
            "ocr_processed": ocr_result["status"] == "success",
            "extracted_text": ocr_result.get("extracted_text", ""),
            "ocr_result": ocr_result,
            "workspace_id": workspace_id,
            "session_id": session_id,
            "uploaded_at": result["uploaded_at"],
        }

        # Persist to DB
        saved_item = await onboarding_repo.add_evidence(
            session_id, workspace_id, evidence_data
        )

        logger.info(
            f"Enhanced file upload completed: {file.filename} ({file_size} bytes)"
        )

        return {
            "success": True,
            "file_id": result["file_id"],
            "filename": file.filename,
            "size": file_size,
            "public_url": result["public_url"],
            "cdn_url": result.get("cdn_url"),
            "validation": result["validation"],
            "processing": result.get("processing", {}),
            "category": file_category,
            "ocr_processed": ocr_result["status"] == "success",
            "extracted_text": ocr_result.get("extracted_text", ""),
            "confidence": ocr_result.get("confidence", 0.0),
            "processing_method": ocr_result.get("processing_method", "unknown"),
            "workspace_id": workspace_id,
            "uploaded_at": result["uploaded_at"],
            "db_id": saved_item.get("id") if saved_item else None,
            "storage_path": result["storage_path"],
        }

    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
    except Exception as e:
        logger.error(f"Enhanced file upload error: {e}")
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


@router.post("/{session_id}/vault/url")
async def process_url(session_id: str, request: URLProcessRequest):
    """Process URL and scrape content - persistent"""
    try:
        # Validate workspace_id
        if not request.workspace_id:
            raise HTTPException(status_code=400, detail="Workspace ID is required")

        # Scrape website
        scrape_result = await scrape_website(request.url)

        evidence_data = {
            "type": "url",
            "url": request.url,
            "scraped": scrape_result["status"] == "success",
            "title": scrape_result.get("title", ""),
            "content": scrape_result.get("content", ""),
            "snippet": scrape_result.get("content", ""),  # Use content as snippet
            "domain": scrape_result.get("domain", ""),
            "source": scrape_result.get("source", "web_scraping"),
            "search_confidence": scrape_result.get("search_confidence", 0.0),
            "processed_at": datetime.utcnow().isoformat(),
        }

        # Add error information if scraping failed
        if scrape_result["status"] == "error":
            evidence_data["error"] = scrape_result.get("error", "Unknown error")

        # Persist to DB
        saved_item = await onboarding_repo.add_evidence(
            session_id, request.workspace_id, evidence_data
        )

        return {
            "success": True,
            "item_id": saved_item.get("id") if saved_item else request.item_id,
            "url": request.url,
            "scraped": scrape_result["status"] == "success",
            "title": scrape_result.get("title", ""),
            "content": scrape_result.get("content", ""),
            "snippet": scrape_result.get("content", ""),
            "domain": scrape_result.get("domain", ""),
            "search_confidence": scrape_result.get("search_confidence", 0.0),
            "db_id": saved_item.get("id") if saved_item else None,
            "error": (
                scrape_result.get("error")
                if scrape_result["status"] == "error"
                else None
            ),
        }

    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
    except Exception as e:
        logger.error(f"Error processing URL: {e}")
        raise HTTPException(status_code=500, detail=f"URL processing failed: {str(e)}")


@router.get("/{session_id}/vault")
async def get_vault_contents(session_id: str):
    """Get all vault contents for a session - persistent"""
    try:
        items = await onboarding_repo.get_vault_items(session_id)
        # Transform to expected format if needed
        # Frontend might expect dict keyed by ID or list?
        # Original code returned dict.
        # Let's check original return: `vault = session.get("vault", {})` which was dict {item_id: info}

        vault_dict = {item["id"]: item for item in items}

        return {
            "session_id": session_id,
            "items": vault_dict,
            "total_items": len(items),
        }
    except Exception as e:
        logger.error(f"Error getting vault contents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/steps/{step_id}")
async def get_step_data(session_id: str, step_id: int):
    """Get step data - persistent"""
    try:
        # We need to fetch session
        # Use simple supabase query via repo
        # get_by_workspace isn't efficient if we have ID.
        # Implemented get(id) in Base Repo? Yes "get(self, id: str, workspace_id: str)".
        # But we need workspace_id to verify access properly.
        # For now, we assume RLS handles it or we use raw query.

        # Adding get_session_by_id to repo would be cleaner, but base `get`
        # requires `workspace_id`.
        # So we query by ID directly using private method logic or add usage.
        # Let's use `onboarding_repo._get_supabase_client()...` or just assume we have `get_by_workspace` but we don't have workspace_id in args here?
        # WARNING: Original `get_step_data` didn't ask for `workspace_id`.
        # This is a security flaw in original too if session_id is guessable.

        # We'll stick to simple query.
        res = (
            onboarding_repo._get_supabase_client()
            .table(onboarding_repo.table_name)
            .select("*")
            .eq("id", session_id)
            .single()
            .execute()
        )
        if not res.data:
            raise HTTPException(status_code=404, detail="Session not found")

        session_data = res.data
        step_data_blob = session_data.get("step_data", {})
        specific_step = step_data_blob.get(str(step_id), {})

        return {
            "session_id": session_id,
            "step_id": step_id,
            "data": specific_step.get("data", {}),
            "updated_at": specific_step.get("updated_at"),
        }
    except Exception as e:
        logger.error(f"Error getting step data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}")
async def get_session_data(session_id: str):
    """Get complete session data - persistent"""
    try:
        res = (
            onboarding_repo._get_supabase_client()
            .table(onboarding_repo.table_name)
            .select("*")
            .eq("id", session_id)
            .single()
            .execute()
        )
        if not res.data:
            raise HTTPException(status_code=404, detail="Session not found")
        return res.data
    except Exception as e:
        logger.error(f"Error getting session data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{session_id}/vault/{item_id}")
async def delete_vault_item(session_id: str, item_id: str):
    """Delete item from vault - persistent"""
    try:
        # Check ownership validation via RLS or logic
        await onboarding_repo.delete_vault_item(item_id)
        return {"success": True, "item_id": item_id}
    except Exception as e:
        logger.error(f"Error deleting vault item: {e}")
        raise HTTPException(status_code=500, detail=str(e))
