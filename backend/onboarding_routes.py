import asyncio
import json
import logging
import os
import sys
import tempfile
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

# Core system imports
from core.session import get_session_manager
from core.supabase_mgr import get_supabase_admin
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from services.search.orchestrator import SOTASearchOrchestrator
from services.sota_ocr.service import DEFAULT_CONFIG as OCR_CONFIG
from services.sota_ocr.service import create_sota_ocr_service
from services.titan.orchestrator import TitanOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/onboarding", tags=["onboarding"])

# Initialize industrial services
session_manager = get_session_manager()
ocr_service = create_sota_ocr_service(OCR_CONFIG)
titan_engine = TitanOrchestrator()


# Pydantic models
class StepUpdateRequest(BaseModel):
    data: Dict[str, Any]
    version: int = 1


class URLProcessRequest(BaseModel):
    url: str
    item_id: str


# Helper functions
async def get_onboarding_session(session_id: str) -> Dict[str, Any]:
    """Get onboarding session data from Redis"""
    session = await session_manager.validate_session(session_id)
    if not session:
        # Create a temporary session if not found (for demo/onboarding flow)
        # In strict production, this would require auth
        return {
            "session_id": session_id,
            "created_at": datetime.utcnow().isoformat(),
            "steps": {},
            "vault": {},
        }
    return session.data or {"steps": {}, "vault": {}}


async def save_onboarding_session(session_id: str, data: Dict[str, Any]):
    """Save onboarding session data to Redis"""
    await session_manager.update_session_data(session_id, data)


# Web scraping function
async def scrape_website(url: str) -> Dict[str, Any]:
    """Scrape website content using the Titan SOTA Engine"""
    try:
        # Use Titan in RESEARCH mode for high quality scraping
        result = await titan_engine.execute(
            query=f"Extract business facts from {url}",
            mode="RESEARCH",
            focus_areas=["company profile", "pricing", "features"],
            use_stealth=True,
        )

        if result and "results" in result:
            top_result = result["results"][0] if result["results"] else {}
            return {
                "status": "success",
                "title": top_result.get("title", ""),
                "content": top_result.get(
                    "full_content", top_result.get("snippet", "")
                ),
                "url": url,
                "source": "titan_intelligence",
                "intelligence_map": result.get("intelligence_map"),
            }
        else:
            return {"status": "error", "error": "No content found for URL via Titan"}
    except Exception as e:
        logger.error(f"Titan scraping failed for {url}: {e}")
        return {"status": "error", "error": str(e)}


# API Endpoints
@router.post("/{session_id}/steps/{step_id}")
async def update_step_data(session_id: str, step_id: int, request: StepUpdateRequest):
    """Update step data with Redis persistence"""
    try:
        session_data = await get_onboarding_session(session_id)

        # Store step data
        if "steps" not in session_data:
            session_data["steps"] = {}

        session_data["steps"][str(step_id)] = {
            "data": request.data,
            "updated_at": datetime.utcnow().isoformat(),
            "version": request.version,
        }

        await save_onboarding_session(session_id, session_data)
        logger.info(f"Updated step {step_id} for session {session_id}")

        return {
            "success": True,
            "session_id": session_id,
            "step_id": step_id,
            "updated_at": session_data["steps"][str(step_id)]["updated_at"],
        }
    except Exception as e:
        logger.error(f"Error updating step data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/steps/{step_id}/run")
async def run_step_processing(session_id: str, step_id: int):
    """Trigger real AI processing for onboarding steps"""
    try:
        session_data = await get_onboarding_session(session_id)
        logger.info(
            f"Triggered AI processing for step {step_id} in session {session_id}"
        )

        if step_id == 2:
            # Step 2: Auto-Extraction using Titan Intelligence
            # Aggregate all evidence from vault
            vault = session_data.get("vault", {})
            evidence_text = ""
            for item in vault.values():
                if "ocr_result" in item:
                    evidence_text += f"\n\n--- Document: {item.get('filename')} ---\n"
                    evidence_text += item["ocr_result"].get("extracted_text", "")
                if "scrape_result" in item:
                    evidence_text += f"\n\n--- URL: {item.get('url')} ---\n"
                    evidence_text += item["scrape_result"].get("content", "")

            if not evidence_text:
                return {
                    "success": False,
                    "message": "No evidence found in vault to process",
                }

            # Execute Titan extraction
            titan_result = await titan_engine.execute(
                query=f"Identify company profile, core category, and primary ICP from this evidence: {evidence_text[:5000]}",
                mode="DEEP",
                focus_areas=["B2B SaaS", "Value Proposition", "ICP Demographics"],
            )

            # Map Titan results to expected facts format
            intel = titan_result.get("intelligence_map", {})
            facts = []

            # Extract Company Name
            if intel.get("summary"):
                facts.append(
                    {
                        "id": str(uuid.uuid4())[:8],
                        "category": "Company",
                        "label": "Intelligence Summary",
                        "value": intel["summary"],
                        "confidence": 95,
                        "status": "extracted",
                        "code": "F-INTEL",
                    }
                )

            for i, finding in enumerate(intel.get("key_findings", [])):
                facts.append(
                    {
                        "id": f"f{i}",
                        "category": "Evidence",
                        "label": f"Insight {i+1}",
                        "value": finding,
                        "confidence": 90,
                        "status": "extracted",
                        "code": f"F-00{i+1}",
                    }
                )

            if "steps" not in session_data:
                session_data["steps"] = {}

            session_data["steps"]["2"] = {
                "data": {
                    "facts": facts,
                    "warnings": [],
                    "extractionComplete": True,
                    "summary": intel.get(
                        "summary", "Extraction complete using Titan SOTA Engine."
                    ),
                    "raw_intelligence": intel,
                },
                "updated_at": datetime.utcnow().isoformat(),
                "version": 1,
            }

            await save_onboarding_session(session_id, session_data)

        return {
            "success": True,
            "message": f"AI processing completed for step {step_id}",
            "session_id": session_id,
            "step_id": step_id,
        }
    except Exception as e:
        logger.error(f"Error in AI step processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/vault/upload")
async def upload_file(
    session_id: str, file: UploadFile = File(...), item_id: str = Form(...)
):
    """Handle file upload with SOTA OCR processing"""
    try:
        session_data = await get_onboarding_session(session_id)
        file_content = await file.read()

        # Process with industrial SOTA OCR
        ocr_response = await ocr_service.process_document(
            file_data=file_content, filename=file.filename
        )

        file_info = {
            "item_id": item_id,
            "filename": file.filename,
            "size": len(file_content),
            "type": file.content_type,
            "uploaded_at": datetime.utcnow().isoformat(),
            "ocr_result": {
                "status": "success",
                "extracted_text": ocr_response.extracted_text,
                "confidence": ocr_response.confidence_score,
                "model_used": ocr_response.model_used,
                "page_count": ocr_response.page_count,
            },
        }

        if "vault" not in session_data:
            session_data["vault"] = {}
        session_data["vault"][item_id] = file_info

        await save_onboarding_session(session_id, session_data)
        logger.info(f"File processed via SOTA OCR: {file.filename}")

        return {
            "success": True,
            "item_id": item_id,
            "filename": file.filename,
            "ocr_processed": True,
            "confidence": ocr_response.confidence_score,
            "model": ocr_response.model_used,
        }
    except Exception as e:
        logger.error(f"SOTA OCR processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/vault/url")
async def process_url(session_id: str, request: URLProcessRequest):
    """Process URL using Titan Intelligence"""
    try:
        session_data = await get_onboarding_session(session_id)
        scrape_result = await scrape_website(request.url)

        if "vault" not in session_data:
            session_data["vault"] = {}

        url_info = {
            "item_id": request.item_id,
            "url": request.url,
            "processed_at": datetime.utcnow().isoformat(),
            "scrape_result": scrape_result,
        }

        session_data["vault"][request.item_id] = url_info
        await save_onboarding_session(session_id, session_data)

        return {
            "success": True,
            "item_id": request.item_id,
            "url": request.url,
            "scraped": scrape_result["status"] == "success",
            "title": scrape_result.get("title", ""),
            "intelligence_detected": "intelligence_map" in scrape_result,
        }
    except Exception as e:
        logger.error(f"Error processing URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/vault")
async def get_vault_contents(session_id: str):
    """Get all vault contents from Redis"""
    session_data = await get_onboarding_session(session_id)
    vault = session_data.get("vault", {})
    return {"session_id": session_id, "items": vault, "total_items": len(vault)}


@router.get("/{session_id}/steps/{step_id}")
async def get_step_data(session_id: str, step_id: int):
    """Get step data from Redis"""
    session_data = await get_onboarding_session(session_id)
    steps = session_data.get("steps", {})
    step_data = steps.get(str(step_id), {})

    return {
        "session_id": session_id,
        "step_id": step_id,
        "data": step_data.get("data", {}),
        "updated_at": step_data.get("updated_at"),
    }


@router.delete("/{session_id}/vault/{item_id}")
async def delete_vault_item(session_id: str, item_id: str):
    """Delete item from Redis-backed vault"""
    session_data = await get_onboarding_session(session_id)

    if "vault" in session_data and item_id in session_data["vault"]:
        del session_data["vault"][item_id]
        await save_onboarding_session(session_id, session_data)
        return {"success": True, "item_id": item_id}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@router.post("/{session_id}/finalize")
async def finalize_onboarding(session_id: str):
    """Finalize onboarding and update production status"""
    try:
        session_data = await get_onboarding_session(session_id)

        # 1. Aggregation
        steps = session_data.get("steps", {})
        vault = session_data.get("vault", {})

        business_context = {
            "version": "2.0",
            "generated_at": datetime.utcnow().isoformat(),
            "session_id": session_id,
            "company_profile": steps.get("1", {}).get("data", {}),
            "intelligence": {
                "evidence_count": len(vault),
                "facts": steps.get("2", {}).get("data", {}).get("facts", []),
            },
        }

        # 2. Persistence (Production GCS/DB)
        # Future: Save business_context to GCS Evidence Vault

        # 3. Update Supabase Status
        try:
            supabase = get_supabase_admin()
            user_id = session_data.get("user_id") or session_id

            supabase.table("profiles").update(
                {
                    "onboarding_status": "active",
                    "onboarding_completed_at": datetime.utcnow().isoformat(),
                }
            ).eq("id", user_id).execute()

            logger.info(f"User {user_id} marked as active in production")
        except Exception as se:
            logger.error(f"Supabase update failed: {se}")

        return {
            "success": True,
            "message": "Onboarding finalized with industrial intelligence.",
            "facts_extracted": len(business_context["intelligence"]["facts"]),
        }

    except Exception as e:
        logger.error(f"Error finalizing onboarding: {e}")
        raise HTTPException(status_code=500, detail=str(e))
