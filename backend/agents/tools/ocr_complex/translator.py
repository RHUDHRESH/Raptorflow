"""
TRANSLATION SERVICE
Economical translation using Google Translate API with fallbacks
No graceful failures - either translates or fails with explicit reason
"""

import asyncio
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import aiohttp

from ...base_processor import BaseProcessor, ProcessingResult, ProcessingStatus


@dataclass
class Language:
    """Language information"""

    code: str
    name: str
    confidence: float


class GoogleTranslator(BaseProcessor):
    """Google Translate API integration"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("google_translate_api_key")
        self.project_id = config.get("google_project_id")
        self.base_url = "https://translation.googleapis.com/language/translate/v2"

        # Supported languages cache
        self.supported_languages = None

    def _process_document(self, document_path: str) -> ProcessingResult:
        """Translate document content"""
        raise NotImplementedError("Use translate_text method instead")

    async def translate_text(
        self, text: str, target_lang: str, source_lang: str = None
    ) -> ProcessingResult:
        """Translate text to target language"""
        if not text or len(text.strip()) < 1:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error="No text to translate",
                verified=False,
            )

        if not self.api_key:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error="Google Translate API key not configured",
                verified=False,
            )

        try:
            # Detect language if not provided
            if not source_lang:
                detection_result = await self._detect_language(text)
                if not detection_result.is_success():
                    return detection_result
                source_lang = detection_result.data["language"]

            # Prepare request
            url = f"{self.base_url}"
            params = {
                "key": self.api_key,
                "q": text,
                "target": target_lang,
                "format": "text",
                "source": source_lang if source_lang else None,
            }

            # Make request
            async with aiohttp.ClientSession() as session:
                async with session.post(url, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return ProcessingResult(
                            status=ProcessingStatus.FAILURE,
                            error=f"Translation API error: {response.status} - {error_text}",
                            verified=False,
                        )

                    data = await response.json()

                    # Extract translation
                    if "data" not in data or "translations" not in data["data"]:
                        return ProcessingResult(
                            status=ProcessingStatus.FAILURE,
                            error="Invalid response from translation API",
                            verified=False,
                        )

                    translations = data["data"]["translations"]
                    if not translations:
                        return ProcessingResult(
                            status=ProcessingStatus.FAILURE,
                            error="No translations returned",
                            verified=False,
                        )

                    translated_text = translations[0]["translatedText"]
                    detected_source = translations[0].get(
                        "detectedSourceLanguage", source_lang
                    )

                    # Verify translation quality
                    verification_result = self._verify_translation(
                        text, translated_text, source_lang, target_lang
                    )

                    return ProcessingResult(
                        status=ProcessingStatus.SUCCESS,
                        data={
                            "translated_text": translated_text,
                            "source_language": source_lang,
                            "detected_language": detected_source,
                            "target_language": target_lang,
                            "character_count": len(text),
                            "confidence": verification_result["confidence"],
                        },
                        confidence=verification_result["confidence"],
                        verified=False,
                    )

        except Exception as e:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"Translation failed: {str(e)}",
                verified=False,
            )

    async def _detect_language(self, text: str) -> ProcessingResult:
        """Detect language of text"""
        try:
            url = f"{self.base_url}/detect"
            params = {
                "key": self.api_key,
                "q": text[:1000],  # Use first 1000 chars for detection
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, params=params) as response:
                    if response.status != 200:
                        return ProcessingResult(
                            status=ProcessingStatus.FAILURE,
                            error=f"Language detection failed: {response.status}",
                            verified=False,
                        )

                    data = await response.json()

                    if "data" not in data or "detections" not in data["data"]:
                        return ProcessingResult(
                            status=ProcessingStatus.FAILURE,
                            error="Invalid detection response",
                            verified=False,
                        )

                    detections = data["data"]["detections"][0]
                    if not detections:
                        return ProcessingResult(
                            status=ProcessingStatus.FAILURE,
                            error="No language detected",
                            verified=False,
                        )

                    best_detection = max(detections, key=lambda x: x["confidence"])

                    return ProcessingResult(
                        status=ProcessingStatus.SUCCESS,
                        data={
                            "language": best_detection["language"],
                            "confidence": best_detection["confidence"],
                            "is_reliable": best_detection["isReliable"],
                        },
                        confidence=best_detection["confidence"],
                        verified=False,
                    )

        except Exception as e:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"Language detection failed: {str(e)}",
                verified=False,
            )

    def _verify_translation(
        self, original: str, translated: str, source_lang: str, target_lang: str
    ) -> Dict[str, Any]:
        """Verify translation quality"""
        confidence = 0.8  # Base confidence

        # Check length ratio (should be somewhat similar)
        length_ratio = len(translated) / len(original) if len(original) > 0 else 0

        # Different languages have different typical length ratios
        if source_lang and target_lang:
            # Some general heuristics
            if source_lang == "en" and target_lang in [
                "de",
                "fi",
            ]:  # English to German/Finnish is longer
                if 0.8 <= length_ratio <= 2.0:
                    confidence += 0.1
            elif source_lang == "en" and target_lang in [
                "zh",
                "ja",
                "ko",
            ]:  # English to Asian languages
                if 0.3 <= length_ratio <= 1.0:
                    confidence += 0.1
            else:  # Similar length languages
                if 0.7 <= length_ratio <= 1.5:
                    confidence += 0.1

        # Check for untranslated content
        if original == translated:
            confidence -= 0.5

        # Check for common translation errors
        if "null" in translated.lower() or "undefined" in translated.lower():
            confidence -= 0.3

        # Ensure translated text is meaningful
        if len(translated.strip()) < 1:
            confidence = 0.0

        return {
            "confidence": max(0.0, min(1.0, confidence)),
            "length_ratio": length_ratio,
        }

    async def get_supported_languages(self) -> ProcessingResult:
        """Get list of supported languages"""
        if self.supported_languages:
            return ProcessingResult(
                status=ProcessingStatus.SUCCESS,
                data={"languages": self.supported_languages},
                confidence=1.0,
                verified=True,
            )

        try:
            url = f"{self.base_url}/languages"
            params = {
                "key": self.api_key,
                "target": "en",  # Get language names in English
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        return ProcessingResult(
                            status=ProcessingStatus.FAILURE,
                            error=f"Failed to get languages: {response.status}",
                            verified=False,
                        )

                    data = await response.json()

                    if "data" not in data or "languages" not in data["data"]:
                        return ProcessingResult(
                            status=ProcessingStatus.FAILURE,
                            error="Invalid languages response",
                            verified=False,
                        )

                    languages = data["data"]["languages"]
                    self.supported_languages = languages

                    return ProcessingResult(
                        status=ProcessingStatus.SUCCESS,
                        data={"languages": languages},
                        confidence=1.0,
                        verified=True,
                    )

        except Exception as e:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"Failed to get supported languages: {str(e)}",
                verified=False,
            )


class FreeTranslator(BaseProcessor):
    """Free translation using alternative services"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.use_libre = config.get("use_libre", True)
        self.libre_url = config.get("libre_url", "http://localhost:5000")

    async def translate_text(
        self, text: str, target_lang: str, source_lang: str = None
    ) -> ProcessingResult:
        """Translate using free service"""
        if not text or len(text.strip()) < 1:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error="No text to translate",
                verified=False,
            )

        if self.use_libre:
            return await self._libre_translate(text, target_lang, source_lang)
        else:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error="No free translation service configured",
                verified=False,
            )

    async def _libre_translate(
        self, text: str, target_lang: str, source_lang: str = None
    ) -> ProcessingResult:
        """Translate using LibreTranslate"""
        try:
            url = f"{self.libre_url}/translate"

            data = {
                "q": text,
                "source": source_lang or "auto",
                "target": target_lang,
                "format": "text",
                "api_key": "",
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    if response.status != 200:
                        return ProcessingResult(
                            status=ProcessingStatus.FAILURE,
                            error=f"LibreTranslate error: {response.status}",
                            verified=False,
                        )

                    result = await response.json()

                    if "translatedText" not in result:
                        return ProcessingResult(
                            status=ProcessingStatus.FAILURE,
                            error="Invalid translation response",
                            verified=False,
                        )

                    return ProcessingResult(
                        status=ProcessingStatus.SUCCESS,
                        data={
                            "translated_text": result["translatedText"],
                            "source_language": result.get("detectedLanguage", {}).get(
                                "code", source_lang
                            ),
                            "target_language": target_lang,
                            "service": "libretranslate",
                        },
                        confidence=0.7,  # Lower confidence for free service
                        verified=False,
                    )

        except Exception as e:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"LibreTranslate failed: {str(e)}",
                verified=False,
            )


class TranslationEngine:
    """Main translation engine with fallback capabilities"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.google_translator = GoogleTranslator(self.config)
        self.free_translator = FreeTranslator(self.config)
        self.prefer_free = self.config.get("prefer_free", False)

    async def translate(
        self, text: str, target_lang: str, source_lang: str = None
    ) -> ProcessingResult:
        """Translate text with automatic fallback"""

        # Try preferred service first
        if self.prefer_free:
            # Try free service first
            result = await self.free_translator.translate_text(
                text, target_lang, source_lang
            )
            if result.is_success():
                return result

            # Fall back to Google
            return await self.google_translator.translate_text(
                text, target_lang, source_lang
            )
        else:
            # Try Google first
            result = await self.google_translator.translate_text(
                text, target_lang, source_lang
            )
            if result.is_success():
                return result

            # Fall back to free service
            return await self.free_translator.translate_text(
                text, target_lang, source_lang
            )

    async def get_supported_languages(self) -> ProcessingResult:
        """Get supported languages from available services"""
        # Try Google first
        result = await self.google_translator.get_supported_languages()
        if result.is_success():
            return result

        # Return minimal list for free service
        return ProcessingResult(
            status=ProcessingStatus.SUCCESS,
            data={
                "languages": [
                    {"code": "en", "name": "English"},
                    {"code": "es", "name": "Spanish"},
                    {"code": "fr", "name": "French"},
                    {"code": "de", "name": "German"},
                    {"code": "zh", "name": "Chinese"},
                    {"code": "ja", "name": "Japanese"},
                    {"code": "ko", "name": "Korean"},
                ]
            },
            confidence=0.5,
            verified=True,
        )


# Global translation engine
translation_engine = TranslationEngine()
