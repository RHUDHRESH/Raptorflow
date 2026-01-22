"""
Multimodal Perception for Cognitive Engine

Handles perception from images and documents using vision models.
Implements PROMPT 12 from STREAM_3_COGNITIVE_ENGINE.
"""

import asyncio
import base64
import json
import os
import tempfile
from dataclasses import dataclass
from enum import Enum
from io import BytesIO
from typing import Any, Dict, List, Optional, Union

# Try to import vision libraries
try:
    from PIL import Image

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import PyPDF2

    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

from ..models import (
    DetectedIntent,
    Entity,
    EntityType,
    IntentType,
    Sentiment,
    SentimentResult,
)


class MediaType(Enum):
    """Types of media that can be processed."""

    IMAGE = "image"
    DOCUMENT = "document"
    TEXT = "text"


@dataclass
class ImageAnalysis:
    """Result of image analysis."""

    description: str
    objects_detected: List[str]
    text_detected: List[str]
    entities: List[Entity]
    sentiment: Optional[SentimentResult]
    confidence: float
    processing_time_ms: int
    metadata: Dict[str, Any]


@dataclass
class DocumentAnalysis:
    """Result of document analysis."""

    content: str
    page_count: int
    entities: List[Entity]
    key_topics: List[str]
    sentiment: Optional[SentimentResult]
    confidence: float
    processing_time_ms: int
    metadata: Dict[str, Any]


@dataclass
class MultimodalResult:
    """Result of multimodal perception."""

    media_type: MediaType
    analysis: Union[ImageAnalysis, DocumentAnalysis]
    extracted_text: str
    entities: List[Entity]
    confidence: float
    success: bool
    error_message: Optional[str] = None


class MultimodalPerception:
    """
    Handles perception from images and documents using vision models.

    Uses Gemini Vision API or similar for image analysis and OCR.
    """

    def __init__(self, vision_client=None, ocr_client=None):
        """
        Initialize multimodal perception.

        Args:
            vision_client: Vision model client (e.g., Gemini Vision)
            ocr_client: OCR client for text extraction
        """
        self.vision_client = vision_client
        self.ocr_client = ocr_client

        # Supported image formats
        self.supported_image_formats = {
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/bmp",
            "image/webp",
        }

        # Supported document formats
        self.supported_document_formats = {
            "application/pdf",
            "text/plain",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }

        # Object detection prompts
        self.object_detection_prompt = """
        Analyze this image and identify:
        1. Main objects and elements visible
        2. Text content (if any)
        3. People, brands, logos, or products
        4. Overall scene or context
        5. Any charts, graphs, or data visualizations

        Provide a detailed description focusing on business-relevant elements.
        """

        # Document analysis prompt
        self.document_analysis_prompt = """
        Analyze this document and extract:
        1. Main content and key points
        2. Companies, people, products mentioned
        3. Data, metrics, or figures
        4. Overall purpose and tone
        5. Action items or next steps

        Focus on business intelligence and actionable insights.
        """

    async def perceive_image(self, image_bytes: bytes) -> ImageAnalysis:
        """
        Analyze an image using vision models.

        Args:
            image_bytes: Raw image data

        Returns:
            ImageAnalysis with extracted information
        """
        import time

        start_time = time.time()

        try:
            # Validate image
            if not PIL_AVAILABLE:
                raise ImportError("PIL (Pillow) is required for image processing")

            # Open and validate image
            image = Image.open(BytesIO(image_bytes))

            # Extract text using OCR if available
            text_detected = []
            if self.ocr_client:
                try:
                    ocr_result = await self._extract_text_from_image(image_bytes)
                    text_detected = ocr_result
                except Exception as e:
                    print(f"OCR failed: {e}")

            # Use vision model for comprehensive analysis
            if self.vision_client:
                analysis_result = await self._analyze_with_vision_model(image_bytes)
            else:
                # Fallback to basic analysis
                analysis_result = await self._basic_image_analysis(image, text_detected)

            # Extract entities from detected text
            entities = await self._extract_entities_from_text(" ".join(text_detected))

            # Analyze sentiment if text detected
            sentiment = None
            if text_detected:
                sentiment = await self._analyze_sentiment(" ".join(text_detected))

            processing_time_ms = int((time.time() - start_time) * 1000)

            return ImageAnalysis(
                description=analysis_result.get("description", ""),
                objects_detected=analysis_result.get("objects", []),
                text_detected=text_detected,
                entities=entities,
                sentiment=sentiment,
                confidence=analysis_result.get("confidence", 0.5),
                processing_time_ms=processing_time_ms,
                metadata={
                    "image_format": image.format,
                    "image_size": image.size,
                    "ocr_used": bool(self.ocr_client),
                    "vision_model_used": bool(self.vision_client),
                },
            )

        except Exception as e:
            processing_time_ms = int((time.time() - start_time) * 1000)
            return ImageAnalysis(
                description="",
                objects_detected=[],
                text_detected=[],
                entities=[],
                sentiment=None,
                confidence=0.0,
                processing_time_ms=processing_time_ms,
                metadata={"error": str(e)},
            )

    async def perceive_document(
        self, doc_bytes: bytes, file_type: str = "application/pdf"
    ) -> DocumentAnalysis:
        """
        Analyze a document (PDF, Word, etc.).

        Args:
            doc_bytes: Raw document data
            file_type: MIME type of the document

        Returns:
            DocumentAnalysis with extracted information
        """
        import time

        start_time = time.time()

        try:
            # Extract text from document
            content = await self._extract_text_from_document(doc_bytes, file_type)

            if not content.strip():
                raise ValueError("No text could be extracted from document")

            # Extract entities from content
            entities = await self._extract_entities_from_text(content)

            # Identify key topics
            key_topics = await self._identify_key_topics(content)

            # Analyze sentiment
            sentiment = await self._analyze_sentiment(content)

            # Count pages (for PDFs)
            page_count = await self._count_pages(doc_bytes, file_type)

            # Use vision model for deeper analysis if available
            confidence = 0.7
            if self.vision_client:
                try:
                    # For multi-page documents, analyze first few pages
                    analysis_result = await self._analyze_document_with_vision(
                        content[:4000]
                    )
                    confidence = analysis_result.get("confidence", 0.8)
                except Exception as e:
                    print(f"Vision analysis failed: {e}")

            processing_time_ms = int((time.time() - start_time) * 1000)

            return DocumentAnalysis(
                content=content,
                page_count=page_count,
                entities=entities,
                key_topics=key_topics,
                sentiment=sentiment,
                confidence=confidence,
                processing_time_ms=processing_time_ms,
                metadata={
                    "file_type": file_type,
                    "content_length": len(content),
                    "vision_model_used": bool(self.vision_client),
                },
            )

        except Exception as e:
            processing_time_ms = int((time.time() - start_time) * 1000)
            return DocumentAnalysis(
                content="",
                page_count=0,
                entities=[],
                key_topics=[],
                sentiment=None,
                confidence=0.0,
                processing_time_ms=processing_time_ms,
                metadata={"error": str(e)},
            )

    async def perceive_multimodal(
        self, data: bytes, media_type: str
    ) -> MultimodalResult:
        """
        Generic multimodal perception method.

        Args:
            data: Raw media data
            media_type: MIME type of the media

        Returns:
            MultimodalResult with analysis
        """
        try:
            if media_type in self.supported_image_formats:
                analysis = await self.perceive_image(data)
                extracted_text = " ".join(analysis.text_detected)
                return MultimodalResult(
                    media_type=MediaType.IMAGE,
                    analysis=analysis,
                    extracted_text=extracted_text,
                    entities=analysis.entities,
                    confidence=analysis.confidence,
                    success=True,
                )

            elif media_type in self.supported_document_formats:
                analysis = await self.perceive_document(data, media_type)
                return MultimodalResult(
                    media_type=MediaType.DOCUMENT,
                    analysis=analysis,
                    extracted_text=analysis.content,
                    entities=analysis.entities,
                    confidence=analysis.confidence,
                    success=True,
                )

            else:
                return MultimodalResult(
                    media_type=MediaType.TEXT,
                    analysis=None,
                    extracted_text=data.decode("utf-8", errors="ignore"),
                    entities=[],
                    confidence=0.0,
                    success=False,
                    error_message=f"Unsupported media type: {media_type}",
                )

        except Exception as e:
            return MultimodalResult(
                media_type=MediaType.TEXT,
                analysis=None,
                extracted_text="",
                entities=[],
                confidence=0.0,
                success=False,
                error_message=str(e),
            )

    async def _extract_text_from_image(self, image_bytes: bytes) -> List[str]:
        """Extract text from image using OCR."""
        if not self.ocr_client:
            return []

        try:
            # Save image to temporary file
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                temp_file.write(image_bytes)
                temp_file_path = temp_file.name

            try:
                # Use OCR client (implementation depends on the client)
                result = await self.ocr_client.extract_text(temp_file_path)
                return result if isinstance(result, list) else [result]
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        except Exception as e:
            print(f"OCR extraction failed: {e}")
            return []

    async def _analyze_with_vision_model(self, image_bytes: bytes) -> Dict[str, Any]:
        """Analyze image using vision model."""
        if not self.vision_client:
            return {}

        try:
            # Convert image to base64 for API
            base64_image = base64.b64encode(image_bytes).decode("utf-8")

            # Call vision model
            response = await self.vision_client.analyze_image(
                image_data=base64_image, prompt=self.object_detection_prompt
            )

            return {
                "description": response.get("description", ""),
                "objects": response.get("objects", []),
                "confidence": response.get("confidence", 0.8),
            }

        except Exception as e:
            print(f"Vision model analysis failed: {e}")
            return {}

    async def _basic_image_analysis(
        self, image, text_detected: List[str]
    ) -> Dict[str, Any]:
        """Basic image analysis without vision model."""
        objects = []

        # Basic object detection based on image properties
        width, height = image.size
        aspect_ratio = width / height

        # Detect common layouts
        if aspect_ratio > 1.5:
            objects.append("wide_format")
        elif aspect_ratio < 0.7:
            objects.append("tall_format")
        else:
            objects.append("square_format")

        # Detect if it might be a chart/graph
        if (
            "chart" in " ".join(text_detected).lower()
            or "graph" in " ".join(text_detected).lower()
        ):
            objects.append("data_visualization")

        # Detect if it has text
        if text_detected:
            objects.append("contains_text")

        return {
            "description": f"Image with {len(objects)} detected features",
            "objects": objects,
            "confidence": 0.5,
        }

    async def _extract_text_from_document(
        self, doc_bytes: bytes, file_type: str
    ) -> str:
        """Extract text from document."""
        if file_type == "application/pdf" and PDF_AVAILABLE:
            return await self._extract_from_pdf(doc_bytes)
        elif file_type == "text/plain":
            return doc_bytes.decode("utf-8", errors="ignore")
        else:
            # For other formats, try to extract as text
            try:
                return doc_bytes.decode("utf-8", errors="ignore")
            except:
                return ""

    async def _extract_from_pdf(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF using PyPDF2."""
        if not PDF_AVAILABLE:
            return ""

        try:
            from io import BytesIO

            pdf_file = BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"

            return text.strip()

        except Exception as e:
            print(f"PDF extraction failed: {e}")
            return ""

    async def _extract_entities_from_text(self, text: str) -> List[Entity]:
        """Extract entities from text using basic patterns."""
        entities = []

        # Basic entity extraction patterns
        import re

        # Company names (simple pattern)
        company_pattern = (
            r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+Inc\.?|Corp\.?|LLC|Ltd\.?)\b"
        )
        for match in re.finditer(company_pattern, text):
            entities.append(
                Entity(
                    text=match.group(),
                    type=EntityType.COMPANY,
                    confidence=0.7,
                    start_pos=match.start(),
                    end_pos=match.end(),
                )
            )

        # Money amounts
        money_pattern = r"\$\d+(?:,\d{3})*(?:\.\d{2})?"
        for match in re.finditer(money_pattern, text):
            entities.append(
                Entity(
                    text=match.group(),
                    type=EntityType.MONEY,
                    confidence=0.9,
                    start_pos=match.start(),
                    end_pos=match.end(),
                )
            )

        # Dates
        date_pattern = r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"
        for match in re.finditer(date_pattern, text):
            entities.append(
                Entity(
                    text=match.group(),
                    type=EntityType.DATE,
                    confidence=0.8,
                    start_pos=match.start(),
                    end_pos=match.end(),
                )
            )

        return entities

    async def _identify_key_topics(self, text: str) -> List[str]:
        """Identify key topics from text."""
        # Simple keyword-based topic identification
        business_topics = {
            "marketing": ["marketing", "advertising", "promotion", "campaign", "brand"],
            "sales": ["sales", "revenue", "customers", "deals", "prospects"],
            "finance": ["financial", "budget", "cost", "investment", "profit"],
            "technology": ["software", "technology", "system", "platform", "digital"],
            "operations": [
                "operations",
                "process",
                "workflow",
                "efficiency",
                "productivity",
            ],
        }

        text_lower = text.lower()
        identified_topics = []

        for topic, keywords in business_topics.items():
            if any(keyword in text_lower for keyword in keywords):
                identified_topics.append(topic)

        return identified_topics

    async def _analyze_sentiment(self, text: str) -> SentimentResult:
        """Basic sentiment analysis."""
        # Simple sentiment analysis based on keywords
        positive_words = [
            "good",
            "great",
            "excellent",
            "positive",
            "success",
            "growth",
            "opportunity",
        ]
        negative_words = [
            "bad",
            "poor",
            "negative",
            "failure",
            "decline",
            "problem",
            "issue",
        ]

        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count > negative_count:
            sentiment = Sentiment.POSITIVE
            confidence = min(0.9, 0.5 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count:
            sentiment = Sentiment.NEGATIVE
            confidence = min(0.9, 0.5 + (negative_count - positive_count) * 0.1)
        else:
            sentiment = Sentiment.NEUTRAL
            confidence = 0.5

        return SentimentResult(
            sentiment=sentiment, confidence=confidence, emotional_signals=[]
        )

    async def _count_pages(self, doc_bytes: bytes, file_type: str) -> int:
        """Count pages in document."""
        if file_type == "application/pdf" and PDF_AVAILABLE:
            try:
                from io import BytesIO

                pdf_file = BytesIO(doc_bytes)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                return len(pdf_reader.pages)
            except:
                return 1
        else:
            return 1

    async def _analyze_document_with_vision(self, text_sample: str) -> Dict[str, Any]:
        """Analyze document text with vision model."""
        if not self.vision_client:
            return {}

        try:
            response = await self.vision_client.analyze_text(
                text=text_sample, prompt=self.document_analysis_prompt
            )

            return {
                "confidence": response.get("confidence", 0.8),
                "insights": response.get("insights", []),
            }

        except Exception as e:
            print(f"Document vision analysis failed: {e}")
            return {}

    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get supported media formats."""
        return {
            "images": list(self.supported_image_formats),
            "documents": list(self.supported_document_formats),
        }

    def is_format_supported(self, media_type: str) -> bool:
        """Check if media type is supported."""
        return (
            media_type in self.supported_image_formats
            or media_type in self.supported_document_formats
        )
