"""
Onboarding API Routes for RaptorFlow
Handles file uploads, URL processing, and step data management
"""

import asyncio
import json
import logging
import os

# Import search and OCR capabilities
import sys
import tempfile
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

sys.path.append(os.path.join(os.path.dirname(__file__), "backend-clean"))
from core.search_native import NativeSearch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/onboarding", tags=["onboarding"])

# In-memory storage for demo (replace with proper storage in production)
onboarding_data = {}


# Pydantic models
class StepUpdateRequest(BaseModel):
    data: Dict[str, Any]
    version: int = 1


class URLProcessRequest(BaseModel):
    url: str
    item_id: str


# Helper functions
def get_session_data(session_id: str) -> Dict[str, Any]:
    """Get or create session data"""
    if session_id not in onboarding_data:
        onboarding_data[session_id] = {
            "session_id": session_id,
            "created_at": datetime.utcnow().isoformat(),
            "steps": {},
            "vault": {},
        }
    return onboarding_data[session_id]


# Web scraping function
async def scrape_website(url: str) -> Dict[str, Any]:
    """Scrape website content using the search engine"""
    try:
        search = NativeSearch()

        # First try to get info about the URL
        domain = url.split("//")[-1].split("/")[0]
        search_query = f"site:{domain}"

        results = await search.query(search_query, limit=1)

        await search.close()

        if results:
            return {
                "status": "success",
                "title": results[0].get("title", ""),
                "content": results[0].get("snippet", ""),
                "url": results[0].get("url", ""),
                "source": "web_scraping",
            }
        else:
            return {"status": "error", "error": "No content found for URL"}
    except Exception as e:
        logger.error(f"Scraping failed for {url}: {e}")
        return {"status": "error", "error": str(e)}


# OCR function (placeholder until Tesseract is installed)
async def process_ocr(file_path: str, file_content: bytes) -> Dict[str, Any]:
    """Process file with OCR (placeholder implementation)"""
    try:
        # For now, just extract basic file info
        file_size = len(file_content)
        file_type = file_path.split(".")[-1] if "." in file_path else "unknown"

        # TODO: Implement actual OCR when Tesseract is installed
        return {
            "status": "success",
            "extracted_text": f"[OCR Placeholder] File processed: {file_path} ({file_size} bytes, type: {file_type})",
            "page_count": 1,
            "method": "placeholder_ocr",
            "confidence": 0.5,
        }
    except Exception as e:
        logger.error(f"OCR processing failed: {e}")
        return {"status": "error", "error": str(e)}


# API Endpoints
@router.post("/{session_id}/steps/{step_id}")
async def update_step_data(session_id: str, step_id: int, request: StepUpdateRequest):
    """Update step data"""
    try:
        session = get_session_data(session_id)

        # Store step data
        if "steps" not in session:
            session["steps"] = {}

        session["steps"][str(step_id)] = {
            "data": request.data,
            "updated_at": datetime.utcnow().isoformat(),
            "version": request.version,
        }

        logger.info(f"Updated step {step_id} for session {session_id}")

        return {
            "success": True,
            "session_id": session_id,
            "step_id": step_id,
            "updated_at": session["steps"][str(step_id)]["updated_at"],
        }
    except Exception as e:
        logger.error(f"Error updating step data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/vault/upload")
async def upload_file(
    session_id: str, file: UploadFile = File(...), item_id: str = Form(...)
):
    """Handle file upload and processing"""
    try:
        session = get_session_data(session_id)

        # Read file content
        file_content = await file.read()
        file_size = len(file_content)

        # Store file info
        if "vault" not in session:
            session["vault"] = {}

        # Process with OCR
        ocr_result = await process_ocr(file.filename, file_content)

        file_info = {
            "item_id": item_id,
            "filename": file.filename,
            "size": file_size,
            "type": file.content_type,
            "uploaded_at": datetime.utcnow().isoformat(),
            "ocr_result": ocr_result,
        }

        session["vault"][item_id] = file_info

        logger.info(f"File uploaded: {file.filename} ({file_size} bytes)")

        return {
            "success": True,
            "item_id": item_id,
            "filename": file.filename,
            "size": file_size,
            "ocr_processed": ocr_result["status"] == "success",
            "extracted_text": ocr_result.get("extracted_text", ""),
        }
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/vault/url")
async def process_url(session_id: str, request: URLProcessRequest):
    """Process URL and scrape content"""
    try:
        session = get_session_data(session_id)

        # Scrape website
        scrape_result = await scrape_website(request.url)

        # Store result
        if "vault" not in session:
            session["vault"] = {}

        url_info = {
            "item_id": request.item_id,
            "url": request.url,
            "processed_at": datetime.utcnow().isoformat(),
            "scrape_result": scrape_result,
        }

        session["vault"][request.item_id] = url_info

        logger.info(f"URL processed: {request.url}")

        return {
            "success": True,
            "item_id": request.item_id,
            "url": request.url,
            "scraped": scrape_result["status"] == "success",
            "title": scrape_result.get("title", ""),
            "content": scrape_result.get("content", ""),
            "snippet": scrape_result.get("snippet", ""),
        }
    except Exception as e:
        logger.error(f"Error processing URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/vault")
async def get_vault_contents(session_id: str):
    """Get all vault contents for a session"""
    try:
        session = get_session_data(session_id)
        vault = session.get("vault", {})

        return {"session_id": session_id, "items": vault, "total_items": len(vault)}
    except Exception as e:
        logger.error(f"Error getting vault contents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/steps/{step_id}")
async def get_step_data(session_id: str, step_id: int):
    """Get step data"""
    try:
        session = get_session_data(session_id)
        steps = session.get("steps", {})
        step_data = steps.get(str(step_id), {})

        return {
            "session_id": session_id,
            "step_id": step_id,
            "data": step_data.get("data", {}),
            "updated_at": step_data.get("updated_at"),
        }
    except Exception as e:
        logger.error(f"Error getting step data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}")
async def get_session_data(session_id: str):
    """Get complete session data"""
    try:
        session = get_session_data(session_id)
        return session
    except Exception as e:
        logger.error(f"Error getting session data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{session_id}/vault/{item_id}")
async def delete_vault_item(session_id: str, item_id: str):
    """Delete item from vault"""
    try:
        session = get_session_data(session_id)

        if "vault" in session and item_id in session["vault"]:
            del session["vault"][item_id]
            logger.info(f"Deleted vault item: {item_id}")
            return {"success": True, "item_id": item_id}
        else:
            raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        logger.error(f"Error deleting vault item: {e}")
        raise HTTPException(status_code=500, detail=str(e))
