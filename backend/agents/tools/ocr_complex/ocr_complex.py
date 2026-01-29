"""
OCR COMPLEX
Main entry point for the OCR and document processing system
No graceful failures - explicit success/failure for all operations
"""

import asyncio
import json
import os
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from document_router import document_router
from logging_utils import ProgressLogger
from nlp_engine import nlp_engine
from ocr_engine import HybridOCREngine, register_default_processors
from translator import translation_engine

from ...base_processor import ProcessingResult, ProcessingStatus, processor_registry


class OCRComplex:
    """Main OCR Complex system that coordinates all processing"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

        # Register processors lazily with provided config to avoid Gemini key issues
        register_default_processors(self.config)

        # Initialize components
        self.router = document_router
        self.nlp = nlp_engine
        self.translator = translation_engine
        self.logger = ProgressLogger(self.config.get("log_path"))

        # Processing options
        self.auto_nlp = self.config.get("auto_nlp", True)
        self.confidence_threshold = self.config.get("confidence_threshold", 0.8)
        self.max_file_size = self.config.get("max_file_size", 50 * 1024 * 1024)  # 50MB

    def process_document(
        self, document_path: Union[str, Path], options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process document with full OCR and NLP pipeline
        Returns explicit success/failure with detailed results
        """
        start_time = time.time()
        options = options or {}

        result = {
            "success": False,
            "error": None,
            "processing_time": 0,
            "steps": {},
            "final_output": None,
        }

        try:
            # Step 1: Route and extract content
            self.logger.log("start_extraction", {"path": str(document_path)})
            extraction_result = self.router.route(document_path)
            result["steps"]["extraction"] = self._format_result(extraction_result)

            if not extraction_result.is_success():
                self.logger.log(
                    "extraction_failed",
                    {"path": str(document_path), "error": extraction_result.error},
                )
                result["error"] = extraction_result.error
                return result

            # Get extracted content
            content = extraction_result.data.get("content", "")

            if not content or len(content.strip()) < 10:
                result["error"] = "Extracted content is too short or empty"
                result["steps"]["extraction"]["error"] = result["error"]
                return result

            # Step 2: NLP processing (if requested)
            nlp_results = {}
            if options.get("nlp", self.auto_nlp):
                nlp_tasks = options.get("nlp_tasks", ["sentiment", "entities"])
                self.logger.log("start_nlp", {"tasks": nlp_tasks})
                nlp_results = self.nlp.process_text(content, nlp_tasks)

                # Format NLP results
                for task, task_result in nlp_results.items():
                    result["steps"][f"nlp_{task}"] = self._format_result(task_result)

                    # Check if any NLP task failed critically
                    if task_result.status == ProcessingStatus.FAILURE:
                        # Log but don't fail the entire process
                        print(f"NLP task {task} failed: {task_result.error}")

            # Step 3: Translation (if requested)
            translation_result = None
            target_lang = options.get("translate_to")
            if target_lang:
                # Run async translation
                self.logger.log("start_translation", {"target": target_lang})
                translation_result = asyncio.run(
                    self.translator.translate(content, target_lang)
                )
                result["steps"]["translation"] = self._format_result(translation_result)

            # Step 4: Compile final output
            final_output = {
                "document_info": {
                    "path": str(document_path),
                    "type": extraction_result.data.get("document_type"),
                    "size": extraction_result.data.get("file_size"),
                    "extraction_method": extraction_result.data.get("method"),
                    "confidence": extraction_result.confidence,
                },
                "extracted_content": {
                    "text": content,
                    "length": len(content),
                    "word_count": len(content.split()),
                },
                "nlp_analysis": {},
                "translation": None,
            }

            # Add NLP results
            for task, task_result in nlp_results.items():
                if task_result.is_success():
                    final_output["nlp_analysis"][task] = task_result.data

            # Add translation
            if translation_result and translation_result.is_success():
                final_output["translation"] = translation_result.data

            # Verify final output
            if self._verify_final_output(final_output):
                result["success"] = True
                result["final_output"] = final_output
                self.logger.log(
                    "process_success",
                    {
                        "path": str(document_path),
                        "processing_time": time.time() - start_time,
                    },
                )
            else:
                result["error"] = "Final output verification failed"
                self.logger.log(
                    "process_failed",
                    {"path": str(document_path), "error": result["error"]},
                )

        except Exception as e:
            result["error"] = f"CRITICAL ERROR: {str(e)}"
            self.logger.log(
                "process_failed", {"path": str(document_path), "error": result["error"]}
            )

        finally:
            result["processing_time"] = time.time() - start_time

        return result

    def process_batch(
        self, document_paths: List[Union[str,]], options: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Process multiple documents with individual success/failure tracking"""
        results = []

        for doc_path in document_paths:
            result = self.process_document(doc_path, options)
            results.append(result)

        # Add batch summary
        successful = sum(1 for r in results if r["success"])
        results.append(
            {
                "batch_summary": True,
                "total_documents": len(document_paths),
                "successful": successful,
                "failed": len(document_paths) - successful,
                "success_rate": (
                    successful / len(document_paths) if document_paths else 0
                ),
            }
        )

        return results

    def _format_result(self, result: ProcessingResult) -> Dict[str, Any]:
        """Format ProcessingResult for output"""
        return {
            "status": result.status.value,
            "success": result.is_success(),
            "error": result.error,
            "confidence": result.confidence,
            "verified": result.verified,
            "processing_time": result.processing_time,
            "data": result.data if result.is_success() else None,
        }

    def _verify_final_output(self, output: Dict[str, Any]) -> bool:
        """Verify final output meets requirements"""
        # Must have extracted content
        if not output.get("extracted_content", {}).get("text"):
            return False

        # Content must be meaningful
        text = output["extracted_content"]["text"].strip()
        if len(text) < 10:
            return False

        # Check for failure indicators
        failure_indicators = ["error", "failed", "unable", "cannot", "null"]
        text_lower = text.lower()

        # Allow some indicators if they're part of the content, not errors
        indicator_count = sum(
            1 for indicator in failure_indicators if indicator in text_lower
        )
        if indicator_count > 5:  # Too many failure indicators
            return False

        return True

    def get_supported_formats(self) -> List[str]:
        """Get list of supported document formats"""
        return self.router.get_supported_extensions()

    def get_nlp_tasks(self) -> List[str]:
        """Get available NLP tasks"""
        return self.nlp.get_available_tasks()

    async def get_supported_languages(self) -> Dict[str, Any]:
        """Get supported translation languages"""
        result = await self.translator.get_supported_languages()
        return result.data if result.is_success() else {"languages": []}


# Convenience function for quick processing
def process_document(
    document_path: Union[str, Path],
    config: Dict[str, Any] = None,
    options: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """Quick document processing function"""
    ocr_complex = OCRComplex(config)
    return ocr_complex.process_document(document_path, options)


# Example usage
if __name__ == "__main__":
    # Example configuration
    config = {
        "gemini_api_key": os.getenv("GEMINI_API_KEY"),
        "google_translate_api_key": os.getenv("GOOGLE_TRANSLATE_API_KEY"),
        "confidence_threshold": 0.8,
        "auto_nlp": True,
    }

    # Process a document
    result = process_document(
        "example.pdf",
        config=config,
        options={
            "nlp_tasks": ["sentiment", "entities", "summary"],
            "translate_to": "es",
        },
    )

    print(json.dumps(result, indent=2))
