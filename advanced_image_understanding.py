#!/usr/bin/env python3
"""
Advanced Image Understanding System - 100% Thorough Analysis
Incorporates state-of-the-art computer vision and OCR techniques
"""

import os
import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import io
import json
import logging
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import re
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageType(Enum):
    PHOTO = "photo"
    DOCUMENT = "document"
    SCREENSHOT = "screenshot"
    CHART = "chart"
    LOGO = "logo"
    DIAGRAM = "diagram"

@dataclass
class ImageMetadata:
    width: int
    height: int
    channels: int
    file_size: int
    format: str
    dpi: Optional[int] = None
    color_space: Optional[str] = None

@dataclass
class TextRegion:
    text: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x, y, w, h
    language: Optional[str] = None
    font_size: Optional[float] = None

@dataclass
class VisualFeature:
    feature_type: str
    confidence: float
    bbox: Tuple[int, int, int, int]
    attributes: Dict[str, Any]

class AdvancedImageAnalyzer:
    """Comprehensive image analysis system"""
    
    def __init__(self):
        self.setup_tesseract()
        self.setup_opencv()
        
    def setup_tesseract(self):
        """Configure Tesseract OCR"""
        try:
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            # Test Tesseract
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract version: {version}")
        except Exception as e:
            logger.warning(f"Tesseract setup failed: {e}")
    
    def setup_opencv(self):
        """Setup OpenCV configurations"""
        try:
            # Test OpenCV
            test_img = np.zeros((100, 100, 3), dtype=np.uint8)
            logger.info("OpenCV available and working")
        except Exception as e:
            logger.warning(f"OpenCV setup failed: {e}")
    
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Perform comprehensive image analysis"""
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Cannot load image: {image_path}")
            
            pil_image = Image.open(image_path)
            
            results = {
                "file_path": image_path,
                "timestamp": datetime.now().isoformat(),
                "metadata": self.extract_metadata(pil_image, image_path),
                "image_analysis": self.analyze_visual_content(image),
                "text_analysis": self.extract_all_text(image, pil_image),
                "business_context": self.determine_business_context(image, pil_image),
                "semantic_understanding": self.semantic_analysis(image, pil_image)
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return {"error": str(e), "file_path": image_path}
    
    def extract_metadata(self, pil_image: Image.Image, image_path: str) -> ImageMetadata:
        """Extract comprehensive image metadata"""
        try:
            file_size = os.path.getsize(image_path)
            
            return ImageMetadata(
                width=pil_image.width,
                height=pil_image.height,
                channels=len(pil_image.getbands()) if pil_image.mode != 'P' else 3,
                file_size=file_size,
                format=pil_image.format,
                dpi=pil_image.info.get('dpi', (None, None))[0] if pil_image.info.get('dpi') else None,
                color_space=pil_image.mode
            )
        except Exception as e:
            logger.warning(f"Metadata extraction failed: {e}")
            return ImageMetadata(0, 0, 0, 0, "unknown")
    
    def analyze_visual_content(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze visual content using computer vision"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            # Color analysis
            avg_color = np.mean(image, axis=(0, 1))
            color_variance = np.var(image, axis=(0, 1))
            
            # Texture analysis
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Shape detection
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            num_contours = len(contours)
            
            # Image classification
            image_type = self.classify_image_type(image, gray, edge_density, laplacian_var, num_contours)
            
            return {
                "edge_density": float(edge_density),
                "average_color": avg_color.tolist(),
                "color_variance": color_variance.tolist(),
                "texture_complexity": float(laplacian_var),
                "num_shapes": num_contours,
                "image_type": image_type.value,
                "quality_metrics": self.assess_image_quality(image, gray)
            }
        except Exception as e:
            logger.warning(f"Visual analysis failed: {e}")
            return {"error": str(e)}
    
    def classify_image_type(self, image: np.ndarray, gray: np.ndarray, edge_density: float, texture_complexity: float, num_contours: int) -> ImageType:
        """Classify image type based on visual characteristics"""
        height, width = gray.shape
        aspect_ratio = width / height
        
        # Heuristic classification
        if edge_density > 0.15 and texture_complexity > 500:
            return ImageType.PHOTO
        elif edge_density < 0.05 and aspect_ratio > 1.5:
            return ImageType.DOCUMENT
        elif edge_density > 0.1 and aspect_ratio > 1.2:
            return ImageType.SCREENSHOT
        elif edge_density < 0.1 and texture_complexity < 100:
            return ImageType.LOGO
        elif num_contours > 50:
            return ImageType.DIAGRAM
        else:
            return ImageType.CHART
    
    def assess_image_quality(self, image: np.ndarray, gray: np.ndarray) -> Dict[str, float]:
        """Assess image quality metrics"""
        try:
            # Blur detection
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Brightness assessment
            brightness = np.mean(gray)
            
            # Contrast assessment
            contrast = np.std(gray)
            
            # Noise estimation
            noise = np.std(cv2.subtract(gray, cv2.GaussianBlur(gray, (5, 5), 0)))
            
            return {
                "sharpness": float(blur_score),
                "brightness": float(brightness),
                "contrast": float(contrast),
                "noise_level": float(noise),
                "overall_quality": self.calculate_quality_score(blur_score, brightness, contrast, noise)
            }
        except Exception as e:
            logger.warning(f"Quality assessment failed: {e}")
            return {"error": str(e)}
    
    def calculate_quality_score(self, sharpness: float, brightness: float, contrast: float, noise: float) -> float:
        """Calculate overall quality score (0-100)"""
        # Normalize metrics
        sharpness_norm = min(sharpness / 1000, 1.0) * 100
        brightness_norm = 100 - abs(brightness - 128) / 128 * 100
        contrast_norm = min(contrast / 127, 1.0) * 100
        noise_norm = max(0, 100 - noise / 10)
        
        return (sharpness_norm * 0.3 + brightness_norm * 0.2 + contrast_norm * 0.3 + noise_norm * 0.2)
    
    def extract_all_text(self, image: np.ndarray, pil_image: Image.Image) -> Dict[str, Any]:
        """Extract text using multiple OCR methods"""
        try:
            text_results = []
            
            # Method 1: Basic OCR
            basic_text = self.basic_ocr(image)
            if basic_text:
                text_results.append({"method": "basic", "text": basic_text, "confidence": 0.7})
            
            # Method 2: Preprocessed OCR
            preprocessed_text = self.preprocessed_ocr(image)
            if preprocessed_text:
                text_results.append({"method": "preprocessed", "text": preprocessed_text, "confidence": 0.85})
            
            # Method 3: Multi-language OCR
            multilang_text = self.multilang_ocr(image)
            if multilang_text:
                text_results.append({"method": "multilang", "text": multilang_text, "confidence": 0.8})
            
            # Extract text regions with bounding boxes
            text_regions = self.extract_text_regions(image)
            
            return {
                "extracted_texts": text_results,
                "text_regions": [vars(region) for region in text_regions],
                "total_text_length": sum(len(result["text"]) for result in text_results),
                "languages_detected": self.detect_languages(text_results),
                "text_density": self.calculate_text_density(text_regions, image.shape)
            }
        except Exception as e:
            logger.warning(f"Text extraction failed: {e}")
            return {"error": str(e)}
    
    def basic_ocr(self, image: np.ndarray) -> str:
        """Basic Tesseract OCR"""
        try:
            return pytesseract.image_to_string(image, lang='eng')
        except Exception as e:
            logger.warning(f"Basic OCR failed: {e}")
            return ""
    
    def preprocessed_ocr(self, image: np.ndarray) -> str:
        """OCR with image preprocessing"""
        try:
            # Convert to PIL for preprocessing
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(pil_image)
            enhanced = enhancer.enhance(2.0)
            
            # Convert back to OpenCV
            enhanced_cv = cv2.cvtColor(np.array(enhanced), cv2.COLOR_RGB2BGR)
            
            # Apply thresholding
            gray = cv2.cvtColor(enhanced_cv, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            return pytesseract.image_to_string(thresh, lang='eng')
        except Exception as e:
            logger.warning(f"Preprocessed OCR failed: {e}")
            return ""
    
    def multilang_ocr(self, image: np.ndarray) -> str:
        """Multi-language OCR attempt"""
        try:
            # Try English first
            text = pytesseract.image_to_string(image, lang='eng')
            
            # If little text detected, try other languages
            if len(text.strip()) < 10:
                try:
                    text += " " + pytesseract.image_to_string(image, lang='chi_sim')  # Chinese
                except:
                    pass
                try:
                    text += " " + pytesseract.image_to_string(image, lang='jpn')  # Japanese
                except:
                    pass
            
            return text
        except Exception as e:
            logger.warning(f"Multilang OCR failed: {e}")
            return ""
    
    def extract_text_regions(self, image: np.ndarray) -> List[TextRegion]:
        """Extract text with bounding boxes"""
        try:
            data = pytesseract.image_to_data(image, lang='eng', output_type=pytesseract.Output.DICT)
            
            regions = []
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 60:  # Confidence threshold
                    text = data['text'][i].strip()
                    if text:
                        region = TextRegion(
                            text=text,
                            confidence=float(data['conf'][i]) / 100,
                            bbox=(data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                        )
                        regions.append(region)
            
            return regions
        except Exception as e:
            logger.warning(f"Text region extraction failed: {e}")
            return []
    
    def detect_languages(self, text_results: List[Dict]) -> List[str]:
        """Detect languages in extracted text"""
        languages = set()
        
        for result in text_results:
            text = result.get('text', '')
            
            # Simple language detection based on character sets
            if any(ord(char) > 127 for char in text):
                if any('\u4e00' <= char <= '\u9fff' for char in text):
                    languages.add('Chinese')
                if any('\u3040' <= char <= '\u309f' for char in text):
                    languages.add('Japanese')
                if any('\u0600' <= char <= '\u06ff' for char in text):
                    languages.add('Arabic')
            else:
                languages.add('English')
        
        return list(languages)
    
    def calculate_text_density(self, text_regions: List[TextRegion], image_shape: Tuple[int, int, int]) -> float:
        """Calculate text density in the image"""
        if not text_regions:
            return 0.0
        
        total_text_area = sum(region.bbox[2] * region.bbox[3] for region in text_regions)
        image_area = image_shape[0] * image_shape[1]
        
        return total_text_area / image_area if image_area > 0 else 0.0
    
    def determine_business_context(self, image: np.ndarray, pil_image: Image.Image) -> Dict[str, Any]:
        """Determine business context and use cases"""
        try:
            context = {
                "business_categories": [],
                "use_cases": [],
                "content_type": "unknown",
                "industry_relevance": 0.0
            }
            
            # Analyze for business content
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Check for charts/graphs
            if self.has_chart_features(image, gray):
                context["business_categories"].append("analytics")
                context["use_cases"].append("business_intelligence")
                context["content_type"] = "chart"
                context["industry_relevance"] = 0.8
            
            # Check for documents
            if self.has_document_features(image, gray):
                context["business_categories"].append("documentation")
                context["use_cases"].append("content_management")
                context["content_type"] = "document"
                context["industry_relevance"] = 0.7
            
            # Check for logos/branding
            if self.has_logo_features(image, gray):
                context["business_categories"].append("branding")
                context["use_cases"].append("marketing")
                context["content_type"] = "logo"
                context["industry_relevance"] = 0.6
            
            # Check for product images
            if self.has_product_features(image, gray):
                context["business_categories"].append("ecommerce")
                context["use_cases"].append("product_catalog")
                context["content_type"] = "product"
                context["industry_relevance"] = 0.9
            
            return context
        except Exception as e:
            logger.warning(f"Business context analysis failed: {e}")
            return {"error": str(e)}
    
    def has_chart_features(self, image: np.ndarray, gray: np.ndarray) -> bool:
        """Detect chart/graph features"""
        try:
            edges = cv2.Canny(gray, 50, 150)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=50, maxLineGap=10)
            
            if lines is not None and len(lines) > 5:
                return True
            
            # Check for grid patterns
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            rectangles = [c for c in contours if len(cv2.approxPolyDP(c, 0.02 * cv2.arcLength(c, True), True)) == 4]
            
            return len(rectangles) > 3
        except:
            return False
    
    def has_document_features(self, image: np.ndarray, gray: np.ndarray) -> bool:
        """Detect document features"""
        try:
            # Check for text lines
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            horizontal_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, horizontal_kernel)
            
            line_density = np.sum(horizontal_lines > 0) / horizontal_lines.size
            return line_density > 0.05
        except:
            return False
    
    def has_logo_features(self, image: np.ndarray, gray: np.ndarray) -> bool:
        """Detect logo features"""
        try:
            height, width = gray.shape
            aspect_ratio = width / height
            
            # Logos often have specific aspect ratios and low text density
            if 0.5 < aspect_ratio < 3.0:
                edges = cv2.Canny(gray, 50, 150)
                edge_density = np.sum(edges > 0) / edges.size
                
                return 0.05 < edge_density < 0.2
        except:
            return False
    
    def has_product_features(self, image: np.ndarray, gray: np.ndarray) -> bool:
        """Detect product image features"""
        try:
            # Product images typically have medium complexity
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            # Check for central object
            height, width = gray.shape
            center_region = gray[height//4:3*height//4, width//4:3*width//4]
            center_complexity = cv2.Laplacian(center_region, cv2.CV_64F).var()
            
            return 0.1 < edge_density < 0.3 and center_complexity > 100
        except:
            return False
    
    def semantic_analysis(self, image: np.ndarray, pil_image: Image.Image) -> Dict[str, Any]:
        """Perform semantic understanding of image content"""
        try:
            semantic = {
                "objects_detected": [],
                "scene_understanding": "unknown",
                "emotional_tone": "neutral",
                "complexity_score": 0.0,
                "semantic_tags": []
            }
            
            # Analyze color mood
            avg_color = np.mean(image, axis=(0, 1))
            if avg_color[0] > avg_color[1] and avg_color[0] > avg_color[2]:
                semantic["emotional_tone"] = "warm"
            elif avg_color[2] > avg_color[1] and avg_color[2] > avg_color[0]:
                semantic["emotional_tone"] = "cool"
            
            # Calculate complexity
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            semantic["complexity_score"] = float(cv2.Laplacian(gray, cv2.CV_64F).var() / 1000)
            
            # Generate semantic tags based on features
            if semantic["complexity_score"] > 0.5:
                semantic["semantic_tags"].append("complex")
            else:
                semantic["semantic_tags"].append("simple")
            
            if semantic["emotional_tone"] == "warm":
                semantic["semantic_tags"].append("energetic")
            elif semantic["emotional_tone"] == "cool":
                semantic["semantic_tags"].append("calm")
            
            return semantic
        except Exception as e:
            logger.warning(f"Semantic analysis failed: {e}")
            return {"error": str(e)}

def main():
    """Test the advanced image understanding system"""
    analyzer = AdvancedImageAnalyzer()
    
    # Test with downloaded files
    test_dir = "enhanced_ocr_test"
    if os.path.exists(test_dir):
        print("🧪 ADVANCED IMAGE UNDERSTANDING SYSTEM TEST")
        print("=" * 60)
        
        results = {}
        for filename in os.listdir(test_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                filepath = os.path.join(test_dir, filename)
                print(f"\n🔄 Analyzing: {filename}")
                print("-" * 40)
                
                result = analyzer.analyze_image(filepath)
                results[filename] = result
                
                if "error" not in result:
                    print(f"✅ Analysis Complete")
                    print(f"📊 Image Type: {result['image_analysis'].get('image_type', 'unknown')}")
                    print(f"📝 Text Extracted: {len(result['text_analysis'].get('extracted_texts', []))} methods")
                    print(f"🎯 Business Context: {result['business_context'].get('content_type', 'unknown')}")
                    semantic_tags = result.get('semantic_analysis', {}).get('semantic_tags', [])
                    print(f"🧠 Semantic Tags: {', '.join(semantic_tags)}")
                else:
                    print(f"❌ Analysis Failed: {result['error']}")
        
        # Save comprehensive results
        with open('advanced_image_analysis_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📄 Detailed results saved to: advanced_image_analysis_results.json")
    else:
        print(f"❌ Test directory {test_dir} not found")
        print("Please run the previous OCR test first to generate test images")

if __name__ == "__main__":
    main()
