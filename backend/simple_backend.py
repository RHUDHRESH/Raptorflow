"""
Simple Backend Test Server for Onboarding
Tests OCR, web scraping, and basic functionality
"""

import asyncio
import json
import logging
import os
import tempfile
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="RaptorFlow Backend Test",
    description="Test backend for onboarding functionality",
    version="1.0.0",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo
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


# Web scraping function using basic requests
async def scrape_website(url: str) -> Dict[str, Any]:
    """Scrape website content using basic HTTP requests"""
    try:
        import httpx
        from bs4 import BeautifulSoup

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                title = soup.find("title")
                title_text = title.get_text().strip() if title else "No title found"

                # Get meta description
                meta_desc = soup.find("meta", attrs={"name": "description"})
                description = meta_desc.get("content", "") if meta_desc else ""

                # Get first paragraph as content
                first_p = soup.find("p")
                content = first_p.get_text().strip() if first_p else description

                return {
                    "status": "success",
                    "title": title_text,
                    "content": content[:500],  # Limit to 500 chars
                    "url": url,
                    "source": "direct_scrape",
                }
            else:
                return {"status": "error", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        logger.error(f"Scraping failed for {url}: {e}")
        return {"status": "error", "error": str(e)}


# OCR function using real Tesseract
async def process_ocr(file_path: str, file_content: bytes) -> Dict[str, Any]:
    """Process file with real OCR using Tesseract"""
    try:
        import io
        import os
        import tempfile

        import pytesseract
        from PIL import Image

        file_size = len(file_content)
        file_type = file_path.split(".")[-1] if "." in file_path else "unknown"

        # For images, perform real OCR
        if file_type.lower() in ["jpg", "jpeg", "png", "gif", "bmp", "tiff"]:
            try:
                # Open image from bytes
                image = Image.open(io.BytesIO(file_content))

                # Convert to RGB if necessary
                if image.mode != "RGB":
                    image = image.convert("RGB")

                # Perform OCR
                text = pytesseract.image_to_string(image)
                confidence_data = pytesseract.image_to_data(
                    image, output_type=pytesseract.Output.DICT
                )

                # Calculate average confidence
                confidences = [
                    int(conf) for conf in confidence_data["conf"] if int(conf) > 0
                ]
                avg_confidence = (
                    sum(confidences) / len(confidences) if confidences else 0
                )

                return {
                    "status": "success",
                    "extracted_text": text.strip(),
                    "page_count": 1,
                    "method": "tesseract_ocr",
                    "confidence": avg_confidence / 100.0,
                    "metadata": {
                        "width": image.width,
                        "height": image.height,
                        "format": image.format,
                        "mode": image.mode,
                    },
                }
            except Exception as e:
                logger.error(f"Image OCR failed: {e}")
                return {"status": "error", "error": f"Image OCR failed: {str(e)}"}

        # For PDFs, try to extract text with pdf2image + OCR
        elif file_type.lower() == "pdf":
            try:
                from pdf2image import convert_from_bytes

                # Convert PDF to images
                images = convert_from_bytes(file_content)

                all_text = []
                total_confidence = 0

                for i, image in enumerate(images):
                    # Perform OCR on each page
                    text = pytesseract.image_to_string(image)
                    confidence_data = pytesseract.image_to_data(
                        image, output_type=pytesseract.Output.DICT
                    )

                    confidences = [
                        int(conf) for conf in confidence_data["conf"] if int(conf) > 0
                    ]
                    page_confidence = (
                        sum(confidences) / len(confidences) if confidences else 0
                    )

                    all_text.append(text)
                    total_confidence += page_confidence

                combined_text = "\n\n".join(all_text)
                avg_confidence = total_confidence / len(images) if images else 0

                return {
                    "status": "success",
                    "extracted_text": combined_text.strip(),
                    "page_count": len(images),
                    "method": os.getenv("METHOD"),
                    "confidence": avg_confidence / 100.0,
                    "metadata": {"pages": len(images), "file_size": file_size},
                }
            except Exception as e:
                logger.error(f"PDF OCR failed: {e}")
                return {"status": "error", "error": f"PDF OCR failed: {str(e)}"}

        # For text files, just read the content
        elif file_type.lower() in ["txt", "md", "html", "htm", "json", "xml", "csv"]:
            try:
                text = file_content.decode("utf-8", errors="ignore")
                return {
                    "status": "success",
                    "extracted_text": text.strip(),
                    "page_count": 1,
                    "method": os.getenv("METHOD"),
                    "confidence": 1.0,
                    "metadata": {"encoding": "utf-8", "file_size": file_size},
                }
            except Exception as e:
                logger.error(f"Text extraction failed: {e}")
                return {"status": "error", "error": f"Text extraction failed: {str(e)}"}

        # For other file types, return basic info
        else:
            return {
                "status": "success",
                "extracted_text": f"[File Info] {file_path} ({file_size} bytes, type: {file_type}) - OCR not supported for this file type",
                "page_count": 1,
                "method": "file_info",
                "confidence": 0.1,
                "metadata": {"file_size": file_size, "file_type": file_type},
            }

    except Exception as e:
        logger.error(f"OCR processing failed: {e}")
        return {"status": "error", "error": str(e)}


# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Test OCR functionality
    ocr_working = False
    try:
        import pytesseract

        pytesseract.get_tesseract_version()
        ocr_working = True
    except:
        pass

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "web_scraping": True,
            "ocr_tesseract": ocr_working,
            "file_upload": True,
            "pdf_processing": True,
            "image_processing": True,
        },
    }


@app.post("/api/v1/onboarding/{session_id}/steps/{step_id}")
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


@app.post("/api/v1/onboarding/{session_id}/vault/upload")
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


@app.post("/api/v1/onboarding/{session_id}/vault/url")
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
            "snippet": scrape_result.get("content", "")[:200],
        }
    except Exception as e:
        logger.error(f"Error processing URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/onboarding/{session_id}/vault")
async def get_vault_contents(session_id: str):
    """Get all vault contents for a session"""
    try:
        session = get_session_data(session_id)
        vault = session.get("vault", {})

        return {"session_id": session_id, "items": vault, "total_items": len(vault)}
    except Exception as e:
        logger.error(f"Error getting vault contents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/onboarding/{session_id}/steps/{step_id}")
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


@app.get("/api/v1/onboarding/{session_id}")
async def get_session_data_endpoint(session_id: str):
    """Get complete session data"""
    try:
        session = get_session_data(session_id)
        return session
    except Exception as e:
        logger.error(f"Error getting session data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/onboarding/{session_id}/vault/{item_id}")
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


if __name__ == "__main__":
    raise SystemExit("Deprecated: use backend.main as the single entrypoint.")
