"""
TEST SUITE FOR OCR COMPLEX
Comprehensive tests with real document verification
No graceful failures - tests must pass or explicitly fail
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List

import pytest

# Add parent directory to path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from base_processor import ProcessingStatus
from ocr_complex import OCRComplex, process_document


class TestOCRComplex:
    """Test suite for OCR Complex system"""

    @pytest.fixture
    def ocr_complex(self):
        """Create OCR Complex instance for testing"""
        config = {
            "confidence_threshold": 0.7,
            "auto_nlp": True,
            "max_file_size": 10 * 1024 * 1024,  # 10MB for tests
        }
        return OCRComplex(config)

    @pytest.fixture
    def sample_text_file(self):
        """Create a temporary text file for testing"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(
                """
            This is a sample document for testing the OCR Complex system.
            It contains multiple sentences to test various NLP functions.
            The sentiment of this document is neutral to positive.
            Contact us at test@example.com or call 123-456-7890.
            Visit our website at https://example.com for more information.
            """
            )
            yield f.name
        os.unlink(f.name)

    def test_text_processing_success(self, ocr_complex, sample_text_file):
        """Test successful text processing"""
        result = ocr_complex.process_document(sample_text_file)

        # Must succeed
        assert result["success"] is True, f"Processing failed: {result.get('error')}"
        assert result["error"] is None

        # Must have extraction step
        assert "extraction" in result["steps"]
        assert result["steps"]["extraction"]["success"] is True

        # Must have content
        assert result["final_output"] is not None
        content = result["final_output"]["extracted_content"]["text"]
        assert len(content) > 50, "Content too short"

        # Must have NLP results
        assert "nlp_analysis" in result["final_output"]
        nlp = result["final_output"]["nlp_analysis"]

        # Check sentiment analysis
        if "sentiment" in nlp:
            assert "overall_sentiment" in nlp["sentiment"]
            assert nlp["sentiment"]["confidence"] > 0.5

        # Check entity extraction
        if "entities" in nlp:
            assert "entities" in nlp["entities"]
            assert len(nlp["entities"]["entities"]) > 0

    def test_nonexistent_file(self, ocr_complex):
        """Test handling of nonexistent file"""
        result = ocr_complex.process_document("nonexistent.pdf")

        # Must fail explicitly
        assert result["success"] is False
        assert result["error"] is not None
        assert "does not exist" in result["error"]

        # Must have failed extraction step
        assert result["steps"]["extraction"]["success"] is False

    def test_empty_file(self, ocr_complex):
        """Test handling of empty file"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("")
            empty_file = f.name

        try:
            result = ocr_complex.process_document(empty_file)

            # Must fail
            assert result["success"] is False
            assert "too short" in result["error"] or "empty" in result["error"]
        finally:
            os.unlink(empty_file)

    def test_file_too_large(self, ocr_complex):
        """Test handling of file that exceeds size limit"""
        # Create a large temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            # Write more than the configured limit
            for _ in range(100000):
                f.write("This is a test line that makes the file large.\n")
            large_file = f.name

        try:
            result = ocr_complex.process_document(large_file)

            # Must fail
            assert result["success"] is False
            assert "too large" in result["error"]
        finally:
            os.unlink(large_file)

    def test_batch_processing(self, ocr_complex, sample_text_file):
        """Test batch processing of multiple files"""
        # Create another test file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Another test document for batch processing.")
            test_file2 = f.name

        try:
            results = ocr_complex.process_batch(
                [sample_text_file, test_file2, "nonexistent.pdf"]
            )

            # Should have 3 results + summary
            assert len(results) == 4

            # First two should succeed
            assert results[0]["success"] is True
            assert results[1]["success"] is True

            # Third should fail
            assert results[2]["success"] is False

            # Check summary
            assert results[3]["batch_summary"] is True
            assert results[3]["successful"] == 2
            assert results[3]["failed"] == 1

        finally:
            os.unlink(test_file2)

    def test_nlp_tasks(self, ocr_complex, sample_text_file):
        """Test specific NLP tasks"""
        options = {"nlp_tasks": ["sentiment", "entities", "summary"], "nlp": True}

        result = ocr_complex.process_document(sample_text_file, options)

        assert result["success"] is True

        # Check all requested NLP tasks are present
        nlp = result["final_output"]["nlp_analysis"]
        assert "sentiment" in nlp
        assert "entities" in nlp
        assert "summary" in nlp

        # Verify each has data
        assert nlp["sentiment"]["overall_sentiment"] is not None
        assert len(nlp["entities"]["entities"]) > 0
        assert len(nlp["summary"]["summary"]) > 20

    def test_confidence_threshold(self, ocr_complex, tmp_path):
        """Test confidence threshold enforcement"""
        # Create a file with potentially low confidence content
        low_conf_file = tmp_path / "low_conf_file.txt"
        with low_conf_file.open("w") as f:
            f.write("~!@#$%^&*()")  # Mostly symbols

        result = ocr_complex.process_document(str(low_conf_file))

        # Should fail due to low confidence
        assert result["success"] is False
        assert (
            "confidence" in result["error"].lower()
            or "verification" in result["error"].lower()
        )

    def test_supported_formats(self, ocr_complex):
        """Test supported formats list"""
        formats = ocr_complex.get_supported_formats()

        # Must include common formats
        assert ".pdf" in formats
        assert ".txt" in formats
        assert ".csv" in formats
        assert ".json" in formats
        assert ".png" in formats
        assert ".jpg" in formats

    def test_nlp_tasks_list(self, ocr_complex):
        """Test NLP tasks list"""
        tasks = ocr_complex.get_nlp_tasks()

        # Must include standard tasks
        assert "sentiment" in tasks
        assert "entities" in tasks
        assert "summary" in tasks
        assert "topics" in tasks


def run_integration_tests():
    """Run integration tests with real documents"""
    print("\n=== OCR Complex Integration Tests ===\n")

    # Test with a real document if available
    test_docs = ["test_document.pdf", "test_image.png", "test_data.csv"]

    config = {"confidence_threshold": 0.7, "auto_nlp": True}

    ocr = OCRComplex(config)

    for doc in test_docs:
        if os.path.exists(doc):
            print(f"Testing with {doc}...")
            result = ocr.process_document(doc)

            if result["success"]:
                print(
                    f"Γ£ô Success - Processing time: {result['processing_time']:.2f}s"
                )
                print(
                    f"  Content length: {len(result['final_output']['extracted_content']['text'])}"
                )
                print(
                    f"  Confidence: {result['final_output']['document_info']['confidence']:.2f}"
                )
            else:
                print(f"Γ£ù Failed - {result['error']}")
        else:
            print(f"Skipping {doc} (not found)")

    print("\n=== Test Complete ===\n")


if __name__ == "__main__":
    # Run integration tests
    run_integration_tests()

    # Run pytest if available
    try:
        pytest.main([__file__, "-v"])
    except:
        print("\nPytest not available. Run integration tests only DNA")
