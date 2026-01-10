"""
IMAGE PREPROCESSING UTILITIES
Deskew, denoise, contrast/binarize to boost OCR accuracy.
No graceful failures: raise explicit errors on invalid input.
"""

from typing import Any, Dict, Tuple

import cv2
import numpy as np


def _to_gray(image: np.ndarray) -> np.ndarray:
    if image is None:
        raise ValueError("Input image is None")
    if len(image.shape) == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image


def deskew(image: np.ndarray, max_angle: float = 10.0) -> np.ndarray:
    """Deskew image using minAreaRect; skip if angle is negligible."""
    gray = _to_gray(image)
    coords = np.column_stack(np.where(gray > 0))
    if coords.size == 0:
        return image
    rect = cv2.minAreaRect(coords)
    angle = rect[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    if abs(angle) < 0.5 or abs(angle) > max_angle:
        return image  # No meaningful skew detected

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )
    return rotated


def denoise(image: np.ndarray, strength: int = 3) -> np.ndarray:
    """Median blur for salt-and-pepper noise."""
    return cv2.medianBlur(image, max(1, strength) | 1)


def enhance_contrast(image: np.ndarray) -> np.ndarray:
    """CLAHE for local contrast enhancement."""
    gray = _to_gray(image)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(gray)


def binarize(image: np.ndarray) -> np.ndarray:
    """Otsu thresholding."""
    gray = _to_gray(image)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary


def preprocess_for_ocr(image: np.ndarray, config: Dict[str, Any]) -> np.ndarray:
    """Pipeline combining deskew, denoise, contrast, binarization."""
    if image is None:
        raise ValueError("Image cannot be None")

    output = image
    if config.get("deskew", True):
        output = deskew(output)
    if config.get("denoise", True):
        output = denoise(output, strength=config.get("denoise_strength", 3))
    if config.get("contrast", True):
        output = enhance_contrast(output)
    if config.get("binarize", True):
        output = binarize(output)
    return output
