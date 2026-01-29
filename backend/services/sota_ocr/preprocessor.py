"""
Advanced Document Preprocessing Pipeline
Implements state-of-the-art image enhancement and document analysis
"""

import asyncio
import io
import os
import tempfile
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

import cv2
import fitz  # PyMuPDF
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

from ..models import (
    DocumentCharacteristics,
    DocumentComplexity,
    DocumentType,
    LanguageCategory,
    ProcessingVolume,
)


@dataclass
class ImageQualityMetrics:
    """Metrics for image quality assessment."""

    sharpness_score: float
    noise_level: float
    contrast_ratio: float
    brightness_score: float
    skew_angle: float
    resolution_dpi: int
    text_density: float
    overall_quality: float


@dataclass
class PreprocessingResult:
    """Result of document preprocessing."""

    processed_images: List[np.ndarray]
    quality_metrics: ImageQualityMetrics
    document_characteristics: DocumentCharacteristics
    processing_steps: List[str]
    enhancement_applied: bool
    metadata: Dict[str, Any]


class ImageQualityAssessment:
    """Advanced image quality assessment using computer vision techniques."""

    def __init__(self):
        self.sharpness_threshold = 0.3
        self.noise_threshold = 0.5
        self.contrast_threshold = 0.2

    def assess_quality(self, image: np.ndarray) -> ImageQualityMetrics:
        """Comprehensive quality assessment of document image."""

        # Calculate sharpness using Laplacian variance
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness_score = min(laplacian_var / 1000.0, 1.0)

        # Estimate noise level
        noise_level = self._estimate_noise(gray)

        # Calculate contrast ratio
        contrast_ratio = self._calculate_contrast(gray)

        # Assess brightness
        brightness_score = np.mean(gray) / 255.0

        # Detect skew angle
        skew_angle = self._detect_skew_angle(gray)

        # Estimate resolution (heuristic based on image dimensions)
        height, width = gray.shape
        estimated_dpi = max(72, int(min(height, width) * 0.3))

        # Calculate text density
        text_density = self._calculate_text_density(gray)

        # Overall quality score
        overall_quality = (
            sharpness_score * 0.3
            + (1.0 - noise_level) * 0.2
            + contrast_ratio * 0.2
            + (1.0 - abs(brightness_score - 0.5)) * 0.1
            + (1.0 - abs(skew_angle) / 45.0) * 0.1
            + text_density * 0.1
        )

        return ImageQualityMetrics(
            sharpness_score=sharpness_score,
            noise_level=noise_level,
            contrast_ratio=contrast_ratio,
            brightness_score=brightness_score,
            skew_angle=skew_angle,
            resolution_dpi=estimated_dpi,
            text_density=text_density,
            overall_quality=overall_quality,
        )

    def _estimate_noise(self, gray_image: np.ndarray) -> float:
        """Estimate noise level using Laplacian operator."""
        # Apply median filter to get noise estimate
        blurred = cv2.medianBlur(gray_image, 5)
        noise = cv2.absdiff(gray_image, blurred)
        return np.mean(noise) / 255.0

    def _calculate_contrast(self, gray_image: np.ndarray) -> float:
        """Calculate contrast using RMS contrast."""
        hist = cv2.calcHist([gray_image], [0], None, [256], [0, 256])
        mean_intensity = np.mean(gray_image)
        rms_contrast = np.sqrt(
            np.sum(((np.arange(256) - mean_intensity) ** 2) * hist.flatten())
            / gray_image.size
        )
        return min(rms_contrast / 127.0, 1.0)

    def _detect_skew_angle(self, gray_image: np.ndarray) -> float:
        """Detect document skew angle using Hough transform."""
        # Edge detection
        edges = cv2.Canny(gray_image, 50, 150, apertureSize=3)

        # Hough line detection
        lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=100)

        if lines is None:
            return 0.0

        # Calculate angles
        angles = []
        for rho, theta in lines[:, 0]:
            angle = theta * 180 / np.pi
            if angle < 45:
                angles.append(angle)
            elif angle > 135:
                angles.append(angle - 180)

        if not angles:
            return 0.0

        # Return median angle
        return np.median(angles)

    def _calculate_text_density(self, gray_image: np.ndarray) -> float:
        """Calculate text density as ratio of text pixels to total pixels."""
        # Threshold to get binary image
        _, binary = cv2.threshold(
            gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        # Count text pixels (black pixels)
        text_pixels = np.sum(binary == 0)
        total_pixels = binary.size

        return text_pixels / total_pixels


class AdaptiveBinarization:
    """Adaptive binarization for different document types."""

    def __init__(self):
        self.block_size = 11
        self.c_constant = 2

    def binarize(self, image: np.ndarray, method: str = "adaptive") -> np.ndarray:
        """Apply binarization based on image characteristics."""
        gray = (
            cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        )

        if method == "adaptive":
            # Adaptive threshold for varying lighting
            binary = cv2.adaptiveThreshold(
                gray,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                self.block_size,
                self.c_constant,
            )
        elif method == "otsu":
            # Otsu's method for global thresholding
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        elif method == "sauvola":
            # Sauvola's local thresholding
            binary = self._sauvola_threshold(gray)
        else:
            # Default to adaptive
            binary = cv2.adaptiveThreshold(
                gray,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                self.block_size,
                self.c_constant,
            )

        return binary

    def _sauvola_threshold(self, gray_image: np.ndarray) -> np.ndarray:
        """Implement Sauvola's local thresholding algorithm."""
        # Calculate local mean and standard deviation
        kernel_size = 15
        kernel = np.ones((kernel_size, kernel_size), np.float32) / (kernel_size**2)

        # Local mean
        local_mean = cv2.filter2D(gray_image.astype(np.float32), -1, kernel)

        # Local standard deviation
        local_sq_mean = cv2.filter2D((gray_image.astype(np.float32)) ** 2, -1, kernel)
        local_std = np.sqrt(local_sq_mean - local_mean**2)

        # Sauvola threshold
        k = 0.34
        r = 128.0
        threshold = local_mean * (1 + k * (local_std / r - 1))

        # Apply threshold
        binary = (gray_image > threshold).astype(np.uint8) * 255
        return binary


class NoiseReduction:
    """Advanced noise reduction for document images."""

    def __init__(self):
        self.methods = {
            "median": self._median_filter,
            "gaussian": self._gaussian_filter,
            "bilateral": self._bilateral_filter,
            "morphological": self._morphological_filter,
        }

    def reduce_noise(self, image: np.ndarray, method: str = "auto") -> np.ndarray:
        """Reduce noise using optimal method."""
        if method == "auto":
            method = self._select_optimal_method(image)

        if method in self.methods:
            return self.methods[method](image)
        else:
            return self._median_filter(image)

    def _select_optimal_method(self, image: np.ndarray) -> str:
        """Select optimal noise reduction method based on image characteristics."""
        gray = (
            cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        )

        # Estimate noise level
        noise_level = np.std(cv2.medianBlur(gray, 5) - gray)

        if noise_level > 20:
            return "bilateral"  # High noise
        elif noise_level > 10:
            return "median"  # Medium noise
        else:
            return "gaussian"  # Low noise

    def _median_filter(self, image: np.ndarray) -> np.ndarray:
        """Apply median filter for salt-and-pepper noise."""
        return cv2.medianBlur(image, 3)

    def _gaussian_filter(self, image: np.ndarray) -> np.ndarray:
        """Apply Gaussian filter for general noise."""
        return cv2.GaussianBlur(image, (3, 3), 0)

    def _bilateral_filter(self, image: np.ndarray) -> np.ndarray:
        """Apply bilateral filter to preserve edges while reducing noise."""
        return cv2.bilateralFilter(image, 9, 75, 75)

    def _morphological_filter(self, image: np.ndarray) -> np.ndarray:
        """Apply morphological operations for noise removal."""
        kernel = np.ones((2, 2), np.uint8)
        opened = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
        return cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)


class SkewCorrection:
    """Advanced skew detection and correction."""

    def __init__(self):
        self.angle_tolerance = 0.5

    def correct_skew(self, image: np.ndarray) -> Tuple[np.ndarray, float]:
        """Detect and correct skew in document image."""
        gray = (
            cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        )

        # Detect skew angle
        angle = self._detect_skew_angle(gray)

        # Correct if angle is significant
        if abs(angle) > self.angle_tolerance:
            corrected = self._rotate_image(image, angle)
            return corrected, angle
        else:
            return image, 0.0

    def _detect_skew_angle(self, gray_image: np.ndarray) -> float:
        """Detect skew angle using Hough transform."""
        # Edge detection
        edges = cv2.Canny(gray_image, 50, 150, apertureSize=3)

        # Hough line detection
        lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=100)

        if lines is None:
            return 0.0

        # Calculate angles
        angles = []
        for rho, theta in lines[:, 0]:
            angle = theta * 180 / np.pi
            if angle < 45:
                angles.append(angle)
            elif angle > 135:
                angles.append(angle - 180)

        if not angles:
            return 0.0

        # Return median angle
        return np.median(angles)

    def _rotate_image(self, image: np.ndarray, angle: float) -> np.ndarray:
        """Rotate image by given angle."""
        height, width = image.shape[:2]
        center = (width // 2, height // 2)

        # Calculate rotation matrix
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

        # Apply rotation
        rotated = cv2.warpAffine(
            image,
            rotation_matrix,
            (width, height),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE,
        )

        return rotated


class ContrastEnhancement:
    """Advanced contrast enhancement techniques."""

    def __init__(self):
        self.methods = {
            "clahe": self._clahe_enhancement,
            "histogram_equalization": self._histogram_equalization,
            "adaptive_gamma": self._adaptive_gamma_correction,
            "retinex": self._retinex_enhancement,
        }

    def enhance_contrast(self, image: np.ndarray, method: str = "auto") -> np.ndarray:
        """Enhance contrast using optimal method."""
        if method == "auto":
            method = self._select_optimal_method(image)

        if method in self.methods:
            return self.methods[method](image)
        else:
            return self._clahe_enhancement(image)

    def _select_optimal_method(self, image: np.ndarray) -> str:
        """Select optimal contrast enhancement method."""
        gray = (
            cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        )

        # Calculate histogram characteristics
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist_flat = hist.flatten()

        # Check if histogram is concentrated (low contrast)
        non_zero_pixels = np.sum(hist_flat > 0)
        if non_zero_pixels < 50:
            return "clahe"  # Very low contrast
        elif np.std(hist_flat) < 1000:
            return "histogram_equalization"  # Low contrast
        else:
            return "clahe"  # General case

    def _clahe_enhancement(self, image: np.ndarray) -> np.ndarray:
        """Contrast Limited Adaptive Histogram Equalization."""
        gray = (
            cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        )

        # Apply CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # Convert back to color if needed
        if len(image.shape) == 3:
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)

        return enhanced

    def _histogram_equalization(self, image: np.ndarray) -> np.ndarray:
        """Standard histogram equalization."""
        gray = (
            cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        )
        equalized = cv2.equalizeHist(gray)

        if len(image.shape) == 3:
            equalized = cv2.cvtColor(equalized, cv2.COLOR_GRAY2BGR)

        return equalized

    def _adaptive_gamma_correction(self, image: np.ndarray) -> np.ndarray:
        """Adaptive gamma correction based on image brightness."""
        gray = (
            cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        )

        # Calculate optimal gamma
        mean_brightness = np.mean(gray)
        gamma = 1.0 / (1.0 + (mean_brightness / 255.0))

        # Apply gamma correction
        enhanced = np.power(gray / 255.0, gamma) * 255.0
        enhanced = np.clip(enhanced, 0, 255).astype(np.uint8)

        if len(image.shape) == 3:
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)

        return enhanced

    def _retinex_enhancement(self, image: np.ndarray) -> np.ndarray:
        """Retinex-based enhancement for illumination correction."""
        # Convert to float and normalize
        img_float = image.astype(np.float32) / 255.0

        # Apply single-scale retinex
        sigma = 15
        blurred = cv2.GaussianBlur(img_float, (0, 0), sigma)
        retinex = np.log10(img_float + 1e-6) - np.log10(blurred + 1e-6)

        # Normalize and convert back
        retinex = (retinex - np.min(retinex)) / (np.max(retinex) - np.min(retinex))
        enhanced = (retinex * 255).astype(np.uint8)

        return enhanced


class DocumentPreprocessor:
    """Advanced document preprocessing pipeline for optimal OCR performance."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.quality_assessor = ImageQualityAssessment()
        self.binarizer = AdaptiveBinarization()
        self.noise_reducer = NoiseReduction()
        self.skew_corrector = SkewCorrection()
        self.contrast_enhancer = ContrastEnhancement()

        # Configuration
        self.target_dpi = config.get("target_dpi", 200)
        self.enable_enhancement = config.get("enable_enhancement", True)
        self.preprocessing_pipeline = config.get("pipeline", "auto")

    async def analyze_document(
        self, document_path: str, file_data: bytes
    ) -> DocumentCharacteristics:
        """Analyze document to determine characteristics for model selection."""

        # Convert document to images
        images = await self._document_to_images(document_path, file_data)

        if not images:
            raise ValueError("Failed to convert document to images")

        # Analyze first page for characteristics
        first_image = images[0]

        # Quality assessment
        quality_metrics = self.quality_assessor.assess_quality(first_image)

        # Determine document type
        document_type = self._classify_document_type(first_image, images)

        # Determine complexity
        complexity = self._determine_complexity(first_image, quality_metrics)

        # Detect language (placeholder - would need language detection model)
        language = self._detect_language(first_image)
        language_category = self._categorize_language(language)

        # Determine processing volume (placeholder - would need business logic)
        volume = ProcessingVolume.MEDIUM

        # Check for special content
        has_tables = self._detect_tables(first_image)
        has_forms = self._detect_forms(first_image)
        has_mathematical_content = self._detect_mathematical_content(first_image)
        has_handwriting = self._detect_handwriting(first_image)

        return DocumentCharacteristics(
            document_type=document_type,
            complexity=complexity,
            language=language,
            language_category=language_category,
            volume=volume,
            has_tables=has_tables,
            has_forms=has_forms,
            has_mathematical_content=has_mathematical_content,
            has_handwriting=has_handwriting,
            image_quality=quality_metrics.overall_quality,
            resolution_dpi=quality_metrics.resolution_dpi,
            page_count=len(images),
            file_size_mb=len(file_data) / (1024 * 1024),
            skew_angle=quality_metrics.skew_angle,
            noise_level=quality_metrics.noise_level,
            contrast_ratio=quality_metrics.contrast_ratio,
        )

    async def process_document(
        self, file_data: bytes, model_name: str
    ) -> PreprocessingResult:
        """Process document with optimal preprocessing pipeline."""

        # Convert to images
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(file_data)
            temp_path = temp_file.name

        try:
            images = await self._document_to_images(temp_path, file_data)

            if not images:
                raise ValueError("Failed to convert document to images")

            # Process each image
            processed_images = []
            processing_steps = []
            enhancement_applied = False

            for i, image in enumerate(images):
                # Quality assessment
                quality_metrics = self.quality_assessor.assess_quality(image)
                processing_steps.append(f"Page {i+1}: Quality assessment")

                processed_image = image.copy()

                if self.enable_enhancement:
                    # Apply preprocessing steps based on quality

                    # Skew correction
                    if abs(quality_metrics.skew_angle) > 2.0:
                        processed_image, skew_angle = self.skew_corrector.correct_skew(
                            processed_image
                        )
                        processing_steps.append(
                            f"Page {i+1}: Skew correction ({skew_angle:.2f}°)"
                        )

                    # Noise reduction
                    if quality_metrics.noise_level > 0.3:
                        processed_image = self.noise_reducer.reduce_noise(
                            processed_image
                        )
                        processing_steps.append(f"Page {i+1}: Noise reduction")

                    # Contrast enhancement
                    if quality_metrics.contrast_ratio < 0.3:
                        processed_image = self.contrast_enhancer.enhance_contrast(
                            processed_image
                        )
                        processing_steps.append(f"Page {i+1}: Contrast enhancement")

                    # Binarization
                    processed_image = self.binarizer.binarize(processed_image)
                    processing_steps.append(f"Page {i+1}: Binarization")

                    enhancement_applied = True

                processed_images.append(processed_image)

            # Analyze document characteristics
            characteristics = await self.analyze_document(temp_path, file_data)

            return PreprocessingResult(
                processed_images=processed_images,
                quality_metrics=quality_metrics,
                document_characteristics=characteristics,
                processing_steps=processing_steps,
                enhancement_applied=enhancement_applied,
                metadata={
                    "model_name": model_name,
                    "target_dpi": self.target_dpi,
                    "preprocessing_pipeline": self.preprocessing_pipeline,
                },
            )

        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    async def _document_to_images(
        self, document_path: str, file_data: bytes
    ) -> List[np.ndarray]:
        """Convert document (PDF or image) to list of numpy arrays."""
        images = []

        try:
            # Determine file type from path
            if document_path.lower().endswith(".pdf"):
                # Process PDF
                pdf_document = fitz.open(stream=file_data, filetype="pdf")

                for page_num in range(len(pdf_document)):
                    page = pdf_document[page_num]

                    # Get page as image with high resolution
                    matrix = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
                    pix = page.get_pixmap(matrix=matrix)

                    # Convert to numpy array
                    img_data = pix.tobytes("png")
                    image = Image.open(io.BytesIO(img_data))

                    # Convert PIL to numpy array
                    np_image = np.array(image)
                    if len(np_image.shape) == 2:
                        np_image = cv2.cvtColor(np_image, cv2.COLOR_GRAY2BGR)

                    images.append(np_image)

                pdf_document.close()

            else:
                # Process image
                image = Image.open(io.BytesIO(file_data))
                np_image = np.array(image)

                if len(np_image.shape) == 2:
                    np_image = cv2.cvtColor(np_image, cv2.COLOR_GRAY2BGR)

                images.append(np_image)

        except Exception as e:
            raise ValueError(f"Failed to convert document to images: {str(e)}")

        return images

    def _classify_document_type(
        self, image: np.ndarray, all_images: List[np.ndarray]
    ) -> DocumentType:
        """Classify document type based on visual characteristics."""
        # Placeholder implementation
        # In production, would use computer vision models

        # Simple heuristics
        height, width = image.shape[:2]
        aspect_ratio = width / height

        if aspect_ratio > 3.0:
            return DocumentType.RECEIPT
        elif aspect_ratio < 0.8:
            return DocumentType.BUSINESS_CARD
        elif len(all_images) == 1 and height > 1000:
            return DocumentType.ID_DOCUMENT
        else:
            return DocumentType.PDF

    def _determine_complexity(
        self, image: np.ndarray, quality_metrics: ImageQualityMetrics
    ) -> DocumentComplexity:
        """Determine document complexity based on visual analysis."""
        complexity_score = 0.0

        # Quality factors
        if quality_metrics.overall_quality < 0.5:
            complexity_score += 0.3

        if quality_metrics.noise_level > 0.4:
            complexity_score += 0.2

        if abs(quality_metrics.skew_angle) > 5.0:
            complexity_score += 0.2

        if quality_metrics.contrast_ratio < 0.3:
            complexity_score += 0.2

        # Content complexity (placeholder)
        # In production, would use layout analysis
        text_density = quality_metrics.text_density
        if text_density > 0.4:
            complexity_score += 0.1

        # Determine complexity level
        if complexity_score < 0.3:
            return DocumentComplexity.SIMPLE
        elif complexity_score < 0.6:
            return DocumentComplexity.MODERATE
        elif complexity_score < 0.8:
            return DocumentComplexity.COMPLEX
        else:
            return DocumentComplexity.VERY_COMPLEX

    def _detect_language(self, image: np.ndarray) -> str:
        """Detect document language (placeholder)."""
        # In production, would use language detection models
        return "eng"  # Default to English

    def _categorize_language(self, language: str) -> LanguageCategory:
        """Categorize language by resource availability."""
        high_resource = ["eng", "chi_sim", "spa", "fra", "deu"]
        medium_resource = ["hin", "ara", "rus", "por", "jpn", "kor"]

        if language in high_resource:
            return LanguageCategory.HIGH_RESOURCE
        elif language in medium_resource:
            return LanguageCategory.MEDIUM_RESOURCE
        else:
            return LanguageCategory.LOW_RESOURCE

    def _detect_tables(self, image: np.ndarray) -> bool:
        """Detect if document contains tables (placeholder)."""
        # In production, would use table detection models
        return False

    def _detect_forms(self, image: np.ndarray) -> bool:
        """Detect if document contains forms (placeholder)."""
        # In production, would use form detection models
        return False

    def _detect_mathematical_content(self, image: np.ndarray) -> bool:
        """Detect if document contains mathematical content (placeholder)."""
        # In production, would use math detection models
        return False

    def _detect_handwriting(self, image: np.ndarray) -> bool:
        """Detect if document contains handwriting (placeholder)."""
        # In production, would use handwriting detection models
        return False
