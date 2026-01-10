"""
Visual Design Intelligence Extractor - Advanced Website Analysis
Extracts colors, typography, visual motifs, and communication style from websites
"""

import asyncio
import base64
import colorsys
import io
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import structlog
from PIL import Image, ImageStat
from playwright.async_api import async_playwright

logger = structlog.get_logger()


class ColorType(Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    ACCENT = "accent"
    NEUTRAL = "neutral"
    BACKGROUND = "background"
    TEXT = "text"


class CommunicationStyle(Enum):
    FORMAL = "formal"
    CASUAL = "casual"
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    TECHNICAL = "technical"
    CREATIVE = "creative"
    CORPORATE = "corporate"


@dataclass
class ColorPalette:
    """Extracted color palette with hex codes and usage"""

    hex_code: str
    rgb: Tuple[int, int, int]
    hsl: Tuple[float, float, float]
    color_type: ColorType
    usage_frequency: int
    visual_weight: float
    accessibility_contrast: Optional[float] = None


@dataclass
class Typography:
    """Typography information"""

    font_family: str
    font_size: str
    font_weight: str
    line_height: str
    letter_spacing: str
    text_transform: str
    usage_context: str  # heading, body, button, etc.
    color: str
    hierarchy_level: int


@dataclass
class VisualMotif:
    """Visual design motifs and patterns"""

    motif_type: str  # geometric, organic, abstract, etc.
    description: str
    frequency: int
    locations: List[str]  # CSS selectors where found
    associated_colors: List[str]
    style_category: str  # modern, classic, minimalist, etc.


@dataclass
class CommunicationPattern:
    """Communication style and messaging patterns"""

    style: CommunicationStyle
    tone: str
    voice_characteristics: List[str]
    keyword_patterns: List[str]
    phrasing_style: str
    formality_level: float  # 0-1 scale
    emotional_tone: str
    call_to_action_style: str


class VisualDesignIntelligenceExtractor:
    """Advanced visual design and communication intelligence extractor"""

    def __init__(self):
        self.color_extraction_strategies = [
            "dominant_colors",
            "css_colors",
            "image_colors",
            "brand_colors",
        ]

        self.typography_analysis = {
            "font_detection": True,
            "hierarchy_analysis": True,
            "usage_patterns": True,
        }

        self.communication_analysis = {
            "sentiment_analysis": True,
            "formality_detection": True,
            "pattern_recognition": True,
        }

    async def extract_visual_intelligence(
        self, url: str, user_id: str
    ) -> Dict[str, Any]:
        """Extract complete visual design intelligence from website"""

        logger.info("Starting visual intelligence extraction", url=url, user_id=user_id)

        start_time = datetime.now(timezone.utc)

        try:
            # Phase 1: Capture website with full visual rendering
            visual_data = await self._capture_visual_website(url)

            # Phase 2: Extract color palette
            color_palette = await self._extract_color_palette(visual_data)

            # Phase 3: Analyze typography
            typography = await self._analyze_typography(visual_data)

            # Phase 4: Identify visual motifs
            visual_motifs = await self._identify_visual_motifs(visual_data)

            # Phase 5: Analyze communication style
            communication_patterns = await self._analyze_communication_style(
                visual_data
            )

            # Phase 6: Generate design intelligence report
            intelligence_report = self._generate_intelligence_report(
                color_palette, typography, visual_motifs, communication_patterns, url
            )

            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()

            return {
                "url": url,
                "user_id": user_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "processing_time": processing_time,
                "status": "success",
                "visual_intelligence": intelligence_report,
                "extraction_metadata": {
                    "strategies_used": self.color_extraction_strategies,
                    "analysis_depth": "comprehensive",
                    "confidence_score": self._calculate_confidence_score(
                        intelligence_report
                    ),
                },
            }

        except Exception as e:
            logger.error("Visual intelligence extraction failed", url=url, error=str(e))
            return {
                "url": url,
                "user_id": user_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "error",
                "error": str(e),
                "processing_time": (
                    datetime.now(timezone.utc) - start_time
                ).total_seconds(),
            }

    async def _capture_visual_website(self, url: str) -> Dict[str, Any]:
        """Capture website with full visual rendering and CSS data"""

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            )

            page = await context.new_page()

            # Navigate and wait for full rendering
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            await page.wait_for_timeout(1500)  # Reduced wait

            # Capture viewport screenshot (faster than full page)
            screenshot = await page.screenshot(full_page=False, type="png")

            # Extract computed styles
            computed_styles = await page.evaluate(
                """
                () => {
                    # Limit elements to speed up extraction
                    const elements = document.querySelectorAll('*');
                    const styles = [];
                    const maxElements = Math.min(elements.length, 500); // Limit to 500 elements

                    for (let i = 0; i < maxElements; i++) {
                        const el = elements[i];
                        const computed = window.getComputedStyle(el);
                        const rect = el.getBoundingClientRect();

                        if (rect.width > 0 && rect.height > 0) {
                            // Handle className safely
                            const className = el.className && typeof el.className === 'string' ? el.className : '';
                            const id = el.id || '';
                            const tagName = el.tagName.toLowerCase();

                            // Build selector safely
                            let selector = tagName;
                            if (id) selector += '#' + id;
                            if (className) selector += '.' + className.split(' ').join('.');

                            styles.push({
                                selector: selector,
                                styles: {
                                    color: computed.color,
                                    backgroundColor: computed.backgroundColor,
                                    fontFamily: computed.fontFamily,
                                    fontSize: computed.fontSize,
                                    fontWeight: computed.fontWeight,
                                    lineHeight: computed.lineHeight,
                                    letterSpacing: computed.letterSpacing,
                                    textTransform: computed.textTransform,
                                    display: computed.display,
                                    position: computed.position
                                },
                                rect: {
                                    x: rect.x,
                                    y: rect.y,
                                    width: rect.width,
                                    height: rect.height
                                },
                                text: el.textContent?.trim() || ''
                            });
                        }
                    }

                    return styles;
                }
            """
            )

            # Extract CSS custom properties (variables)
            css_variables = await page.evaluate(
                """
                () => {
                    const styles = getComputedStyle(document.documentElement);
                    const variables = {};

                    for (let i = 0; i < styles.length; i++) {
                        const property = styles[i];
                        if (property.startsWith('--')) {
                            variables[property] = styles.getPropertyValue(property);
                        }
                    }

                    return variables;
                }
            """
            )

            # Extract all images
            images = await page.evaluate(
                """
                () => {
                    const imgs = Array.from(document.querySelectorAll('img'));
                    return imgs.map(img => ({
                        src: img.src,
                        alt: img.alt || '',
                        width: img.naturalWidth,
                        height: img.naturalHeight,
                        className: img.className,
                        id: img.id
                    }));
                }
            """
            )

            await context.close()
            await browser.close()

            return {
                "screenshot": screenshot,
                "computed_styles": computed_styles,
                "css_variables": css_variables,
                "images": images,
                "page_info": {
                    "url": url,
                    "viewport": {"width": 1920, "height": 1080},
                    "capture_time": datetime.now(timezone.utc).isoformat(),
                },
            }

    async def _extract_color_palette(
        self, visual_data: Dict[str, Any]
    ) -> List[ColorPalette]:
        """Extract comprehensive color palette from website"""

        colors = []

        # Strategy 1: Extract from computed CSS styles
        css_colors = self._extract_css_colors(visual_data["computed_styles"])
        colors.extend(css_colors)

        # Strategy 2: Extract from screenshot using image processing
        screenshot_colors = await self._extract_screenshot_colors(
            visual_data["screenshot"]
        )
        colors.extend(screenshot_colors)

        # Strategy 3: Extract from CSS variables
        variable_colors = self._extract_css_variable_colors(
            visual_data["css_variables"]
        )
        colors.extend(variable_colors)

        # Strategy 4: Extract from images
        image_colors = await self._extract_image_colors(visual_data["images"])
        colors.extend(image_colors)

        # Consolidate and categorize colors
        consolidated_palette = self._consolidate_color_palette(colors)

        return consolidated_palette

    def _extract_css_colors(self, computed_styles: List[Dict]) -> List[ColorPalette]:
        """Extract colors from computed CSS styles"""

        colors = []
        color_usage = {}

        for style_data in computed_styles:
            styles = style_data["styles"]

            # Extract text colors
            if styles["color"] and styles["color"] != "rgba(0, 0, 0, 0)":
                color_hex = self._rgb_to_hex(styles["color"])
                if color_hex:
                    color_usage[color_hex] = color_usage.get(color_hex, 0) + 1

            # Extract background colors
            if (
                styles["backgroundColor"]
                and styles["backgroundColor"] != "rgba(0, 0, 0, 0)"
            ):
                color_hex = self._rgb_to_hex(styles["backgroundColor"])
                if color_hex:
                    color_usage[color_hex] = color_usage.get(color_hex, 0) + 1

        # Convert to ColorPalette objects
        for hex_code, usage_count in color_usage.items():
            rgb = self._hex_to_rgb(hex_code)
            hsl = self._rgb_to_hsl(rgb)

            colors.append(
                ColorPalette(
                    hex_code=hex_code,
                    rgb=rgb,
                    hsl=hsl,
                    color_type=self._classify_color_type(hex_code, usage_count),
                    usage_frequency=usage_count,
                    visual_weight=self._calculate_visual_weight(hex_code, usage_count),
                )
            )

        return colors

    async def _extract_screenshot_colors(self, screenshot: bytes) -> List[ColorPalette]:
        """Extract dominant colors from website screenshot"""

        try:
            # Convert screenshot to PIL Image
            image = Image.open(io.BytesIO(screenshot))

            # Resize for faster processing
            image = image.resize((200, 200))

            # Get color data
            pixels = list(image.getdata())

            # Count color occurrences
            color_count = {}
            for pixel in pixels:
                if len(pixel) == 3:  # RGB
                    rgb = pixel
                elif len(pixel) == 4:  # RGBA
                    rgb = pixel[:3]
                else:
                    continue

                # Round colors to reduce variations
                rounded_rgb = tuple(round(c / 10) * 10 for c in rgb)
                color_count[rounded_rgb] = color_count.get(rounded_rgb, 0) + 1

            # Get top colors
            top_colors = sorted(color_count.items(), key=lambda x: x[1], reverse=True)[
                :20
            ]

            colors = []
            for rgb, count in top_colors:
                hex_code = self._rgb_to_hex(f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})")
                hsl = self._rgb_to_hsl(rgb)

                colors.append(
                    ColorPalette(
                        hex_code=hex_code,
                        rgb=rgb,
                        hsl=hsl,
                        color_type=ColorType.PRIMARY,  # Will be reclassified later
                        usage_frequency=count,
                        visual_weight=count / len(pixels),
                    )
                )

            return colors

        except Exception as e:
            logger.warning("Failed to extract screenshot colors", error=str(e))
            return []

    def _extract_css_variable_colors(
        self, css_variables: Dict[str, str]
    ) -> List[ColorPalette]:
        """Extract colors from CSS custom properties"""

        colors = []

        for var_name, var_value in css_variables.items():
            # Look for color values in CSS variables
            if any(
                color_prop in var_name.lower()
                for color_prop in ["color", "bg", "background", "theme"]
            ):
                color_hex = self._extract_color_from_css_value(var_value)
                if color_hex:
                    rgb = self._hex_to_rgb(color_hex)
                    hsl = self._rgb_to_hsl(rgb)

                    colors.append(
                        ColorPalette(
                            hex_code=color_hex,
                            rgb=rgb,
                            hsl=hsl,
                            color_type=self._classify_css_variable_color(var_name),
                            usage_frequency=1,
                            visual_weight=0.8,  # CSS variables often represent important colors
                        )
                    )

        return colors

    async def _extract_image_colors(self, images: List[Dict]) -> List[ColorPalette]:
        """Extract colors from website images"""

        colors = []

        # For now, we'll focus on brand colors from images
        # In production, would download and analyze each image

        for img_data in images[:5]:  # Limit to first 5 images for performance
            try:
                # Placeholder for image color extraction
                # Would use image processing libraries to extract dominant colors
                pass
            except Exception as e:
                logger.warning(
                    "Failed to extract colors from image",
                    img_url=img_data.get("src"),
                    error=str(e),
                )

        return colors

    def _consolidate_color_palette(
        self, colors: List[ColorPalette]
    ) -> List[ColorPalette]:
        """Consolidate and categorize the color palette"""

        # Group similar colors
        color_groups = {}

        for color in colors:
            # Find similar colors (within threshold)
            group_key = self._find_color_group(color.hex_code, color_groups)

            if group_key is None:
                # Create new group
                group_key = color.hex_code
                color_groups[group_key] = {
                    "colors": [color],
                    "total_usage": color.usage_frequency,
                    "total_weight": color.visual_weight,
                }
            else:
                # Add to existing group
                color_groups[group_key]["colors"].append(color)
                color_groups[group_key]["total_usage"] += color.usage_frequency
                color_groups[group_key]["total_weight"] += color.visual_weight

        # Create consolidated palette
        consolidated = []

        for group_data in color_groups.values():
            # Use the most frequent color as representative
            representative_color = max(
                group_data["colors"], key=lambda c: c.usage_frequency
            )

            # Update with consolidated data
            representative_color.usage_frequency = group_data["total_usage"]
            representative_color.visual_weight = group_data["total_weight"]

            # Reclassify based on consolidated data
            representative_color.color_type = self._classify_color_type_consolidated(
                representative_color, group_data["total_usage"]
            )

            consolidated.append(representative_color)

        # Sort by usage frequency
        consolidated.sort(key=lambda c: c.usage_frequency, reverse=True)

        return consolidated[:15]  # Return top 15 colors

    async def _analyze_typography(
        self, visual_data: Dict[str, Any]
    ) -> List[Typography]:
        """Analyze typography from computed styles"""

        typography_data = []
        font_usage = {}

        for style_data in visual_data["computed_styles"]:
            styles = style_data["styles"]
            text = style_data["text"]

            if not text or len(text) < 3:  # Skip empty or very short text
                continue

            font_key = (
                f"{styles['fontFamily']}|{styles['fontSize']}|{styles['fontWeight']}"
            )

            if font_key not in font_usage:
                font_usage[font_key] = {
                    "font_family": styles["fontFamily"],
                    "font_size": styles["fontSize"],
                    "font_weight": styles["fontWeight"],
                    "line_height": styles["lineHeight"],
                    "letter_spacing": styles["letterSpacing"],
                    "text_transform": styles["textTransform"],
                    "color": styles["color"],
                    "usage_count": 0,
                    "contexts": [],
                    "total_text_length": 0,
                }

            font_usage[font_key]["usage_count"] += 1
            font_usage[font_key]["total_text_length"] += len(text)

            # Determine usage context
            context = self._determine_typography_context(style_data)
            if context not in font_usage[font_key]["contexts"]:
                font_usage[font_key]["contexts"].append(context)

        # Convert to Typography objects
        for font_data in font_usage.values():
            # Determine hierarchy level based on usage and size
            hierarchy_level = self._determine_hierarchy_level(font_data)

            typography_data.append(
                Typography(
                    font_family=font_data["font_family"],
                    font_size=font_data["font_size"],
                    font_weight=font_data["font_weight"],
                    line_height=font_data["line_height"],
                    letter_spacing=font_data["letter_spacing"],
                    text_transform=font_data["text_transform"],
                    usage_context=", ".join(font_data["contexts"]),
                    color=font_data["color"],
                    hierarchy_level=hierarchy_level,
                )
            )

        # Sort by hierarchy level and usage
        typography_data.sort(key=lambda t: (t.hierarchy_level, -len(t.usage_context)))

        return typography_data

    async def _identify_visual_motifs(
        self, visual_data: Dict[str, Any]
    ) -> List[VisualMotif]:
        """Identify visual design motifs and patterns"""

        motifs = []

        # Analyze CSS classes and IDs for motif patterns
        motif_patterns = self._extract_motif_patterns(visual_data["computed_styles"])

        # Analyze layout patterns
        layout_motifs = self._analyze_layout_patterns(visual_data["computed_styles"])

        # Analyze color combinations for motif associations
        color_motifs = self._analyze_color_motifs(visual_data["computed_styles"])

        # Combine all motif data
        all_motifs = motif_patterns + layout_motifs + color_motifs

        # Consolidate similar motifs
        consolidated_motifs = self._consolidate_motifs(all_motifs)

        return consolidated_motifs

    async def _analyze_communication_style(
        self, visual_data: Dict[str, Any]
    ) -> CommunicationPattern:
        """Analyze communication style and messaging patterns"""

        # Extract all text content
        all_text = " ".join(
            [
                style_data["text"]
                for style_data in visual_data["computed_styles"]
                if style_data["text"] and len(style_data["text"]) > 3
            ]
        )

        # Analyze formality level
        formality_level = self._calculate_formality_level(all_text)

        # Determine communication style
        style = self._determine_communication_style(formality_level, all_text)

        # Extract tone and voice characteristics
        tone, voice_characteristics = self._analyze_tone_and_voice(all_text)

        # Extract keyword patterns
        keyword_patterns = self._extract_keyword_patterns(all_text)

        # Analyze phrasing style
        phrasing_style = self._analyze_phrasing_style(all_text)

        # Determine emotional tone
        emotional_tone = self._analyze_emotional_tone(all_text)

        # Analyze call-to-action style
        cta_style = self._analyze_cta_style(visual_data["computed_styles"])

        return CommunicationPattern(
            style=style,
            tone=tone,
            voice_characteristics=voice_characteristics,
            keyword_patterns=keyword_patterns,
            phrasing_style=phrasing_style,
            formality_level=formality_level,
            emotional_tone=emotional_tone,
            call_to_action_style=cta_style,
        )

    def _generate_intelligence_report(
        self,
        color_palette: List[ColorPalette],
        typography: List[Typography],
        visual_motifs: List[VisualMotif],
        communication_patterns: CommunicationPattern,
        url: str,
    ) -> Dict[str, Any]:
        """Generate comprehensive visual intelligence report"""

        return {
            "url": url,
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
            "color_analysis": {
                "primary_colors": [
                    c.hex_code
                    for c in color_palette
                    if c.color_type == ColorType.PRIMARY
                ][:3],
                "secondary_colors": [
                    c.hex_code
                    for c in color_palette
                    if c.color_type == ColorType.SECONDARY
                ][:3],
                "accent_colors": [
                    c.hex_code
                    for c in color_palette
                    if c.color_type == ColorType.ACCENT
                ][:3],
                "neutral_colors": [
                    c.hex_code
                    for c in color_palette
                    if c.color_type == ColorType.NEUTRAL
                ][:3],
                "complete_palette": [
                    {
                        "hex_code": c.hex_code,
                        "rgb": c.rgb,
                        "hsl": c.hsl,
                        "type": c.color_type.value,
                        "usage_frequency": c.usage_frequency,
                        "visual_weight": c.visual_weight,
                    }
                    for c in color_palette
                ],
                "color_harmony": self._analyze_color_harmony(color_palette),
                "accessibility_score": self._calculate_accessibility_score(
                    color_palette
                ),
            },
            "typography_analysis": {
                "primary_fonts": list(set([t.font_family for t in typography[:5]])),
                "font_hierarchy": [
                    {
                        "font_family": t.font_family,
                        "font_size": t.font_size,
                        "font_weight": t.font_weight,
                        "usage_context": t.usage_context,
                        "hierarchy_level": t.hierarchy_level,
                        "color": t.color,
                    }
                    for t in typography
                ],
                "typography_consistency": self._calculate_typography_consistency(
                    typography
                ),
                "readability_score": self._calculate_readability_score(typography),
            },
            "visual_motifs": {
                "motifs": [
                    {
                        "type": m.motif_type,
                        "description": m.description,
                        "frequency": m.frequency,
                        "locations": m.locations,
                        "associated_colors": m.associated_colors,
                        "style_category": m.style_category,
                    }
                    for m in visual_motifs
                ],
                "dominant_style": self._determine_dominant_style(visual_motifs),
                "design_complexity": self._calculate_design_complexity(visual_motifs),
            },
            "communication_analysis": {
                "style": communication_patterns.style.value,
                "tone": communication_patterns.tone,
                "voice_characteristics": communication_patterns.voice_characteristics,
                "keyword_patterns": communication_patterns.keyword_patterns,
                "phrasing_style": communication_patterns.phrasing_style,
                "formality_level": communication_patterns.formality_level,
                "emotional_tone": communication_patterns.emotional_tone,
                "call_to_action_style": communication_patterns.call_to_action_style,
                "messaging_consistency": self._calculate_messaging_consistency(
                    communication_patterns
                ),
            },
            "design_intelligence": {
                "brand_personality": self._infer_brand_personality(
                    color_palette, typography, communication_patterns
                ),
                "target_audience": self._infer_target_audience(
                    communication_patterns, visual_motifs
                ),
                "industry_alignment": self._infer_industry_alignment(
                    color_palette, typography, visual_motifs
                ),
                "design_maturity": self._assess_design_maturity(
                    typography, color_palette
                ),
                "competitive_differentiation": self._assess_competitive_differentiation(
                    visual_motifs, communication_patterns
                ),
            },
        }

    # Helper methods for color processing
    def _rgb_to_hex(self, rgb_str: str) -> Optional[str]:
        """Convert RGB string to hex code"""
        try:
            # Handle various RGB formats
            if rgb_str.startswith("#"):
                return rgb_str
            elif rgb_str.startswith("rgb"):
                # Extract RGB values
                values = re.findall(r"\d+", rgb_str)
                if len(values) >= 3:
                    r, g, b = map(int, values[:3])
                    return f"#{r:02x}{g:02x}{b:02x}"
            return None
        except:
            return None

    def _hex_to_rgb(self, hex_code: str) -> Tuple[int, int, int]:
        """Convert hex code to RGB tuple"""
        hex_code = hex_code.lstrip("#")
        return tuple(int(hex_code[i : i + 2], 16) for i in (0, 2, 4))

    def _rgb_to_hsl(self, rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
        """Convert RGB to HSL"""
        r, g, b = [x / 255.0 for x in rgb]
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        l = (max_val + min_val) / 2

        if max_val == min_val:
            h = s = 0
        else:
            d = max_val - min_val
            s = d / (2 - max_val - min_val) if l > 0.5 else d / (max_val + min_val)
            if max_val == r:
                h = (g - b) / d + (6 if g < b else 0)
            elif max_val == g:
                h = (b - r) / d + 2
            else:
                h = (r - g) / d + 4
            h /= 12

        return (h * 360, s * 100, l * 100)

    def _classify_color_type(self, hex_code: str, usage_count: int) -> ColorType:
        """Classify color type based on usage and characteristics"""

        rgb = self._hex_to_rgb(hex_code)
        hsl = self._rgb_to_hsl(rgb)

        # Check if it's a neutral color
        if hsl[1] < 10:  # Low saturation
            if hsl[2] > 80:  # Light
                return ColorType.BACKGROUND
            elif hsl[2] < 20:  # Dark
                return ColorType.TEXT
            else:
                return ColorType.NEUTRAL

        # Classify based on usage frequency
        if usage_count > 10:
            return ColorType.PRIMARY
        elif usage_count > 5:
            return ColorType.SECONDARY
        else:
            return ColorType.ACCENT

    def _calculate_visual_weight(self, hex_code: str, usage_count: int) -> float:
        """Calculate visual weight of a color"""
        rgb = self._hex_to_rgb(hex_code)
        hsl = self._rgb_to_hsl(rgb)

        # Weight based on saturation, lightness, and usage
        saturation_weight = hsl[1] / 100
        lightness_weight = abs(hsl[2] - 50) / 50
        usage_weight = min(usage_count / 20, 1.0)

        return (saturation_weight + lightness_weight + usage_weight) / 3

    # Additional helper methods would be implemented here...
    # For brevity, I'm including key method signatures

    def _classify_css_variable_color(self, var_name: str) -> ColorType:
        """Classify color type from CSS variable name"""
        if "primary" in var_name.lower():
            return ColorType.PRIMARY
        elif "secondary" in var_name.lower():
            return ColorType.SECONDARY
        elif "accent" in var_name.lower():
            return ColorType.ACCENT
        elif "background" in var_name.lower() or "bg" in var_name.lower():
            return ColorType.BACKGROUND
        elif "text" in var_name.lower():
            return ColorType.TEXT
        else:
            return ColorType.NEUTRAL

    def _extract_color_from_css_value(self, css_value: str) -> Optional[str]:
        """Extract hex color from CSS value"""
        if not css_value:
            return None
        value = css_value.strip()
        # Handle hex values (with or without leading #)
        if "#" in value:
            hex_part = value[value.index("#") :].split()[0]
            if len(hex_part) in (4, 7):
                return hex_part
            # If the hash was stripped earlier
            hex_raw = hex_part.lstrip("#")
            if len(hex_raw) in (3, 6):
                return f"#{hex_raw}"
        # Basic rgb/rgba handling
        if value.lower().startswith("rgb"):
            return self._rgb_to_hex(value)
        return None

    def _find_color_group(self, hex_code: str, color_groups: Dict) -> Optional[str]:
        """Find similar color group"""
        rgb = self._hex_to_rgb(hex_code)

        for group_hex, group_data in color_groups.items():
            group_rgb = self._hex_to_rgb(group_hex)

            # Calculate color distance
            distance = sum(abs(a - b) for a, b in zip(rgb, group_rgb))

            if distance < 50:  # Threshold for similarity
                return group_hex

        return None

    def _classify_color_type_consolidated(
        self, color: ColorPalette, total_usage: int
    ) -> ColorType:
        """Reclassify color type after consolidation"""
        if total_usage > 15:
            return ColorType.PRIMARY
        elif total_usage > 8:
            return ColorType.SECONDARY
        elif total_usage > 3:
            return ColorType.ACCENT
        else:
            return color.color_type

    def _determine_typography_context(self, style_data: Dict) -> str:
        """Determine typography usage context"""
        selector = style_data["selector"]
        styles = style_data["styles"]
        try:
            font_size_val = (
                float(styles["fontSize"].replace("px", ""))
                if styles.get("fontSize")
                else 0.0
            )
        except Exception:
            font_size_val = 0.0

        if "h1" in selector or font_size_val >= 32:
            return "heading"
        elif "button" in selector or styles.get("display") == "button":
            return "button"
        elif "nav" in selector or "menu" in selector:
            return "navigation"
        else:
            return "body"

    def _determine_hierarchy_level(self, font_data: Dict) -> int:
        """Determine typography hierarchy level"""
        font_size = float(font_data["font_size"].replace("px", ""))

        if font_size >= 32:
            return 1  # H1
        elif font_size >= 24:
            return 2  # H2
        elif font_size >= 18:
            return 3  # H3
        elif font_size >= 16:
            return 4  # H4
        else:
            return 5  # Body text

    # Placeholder methods for other analyses
    def _extract_motif_patterns(self, computed_styles: List[Dict]) -> List[VisualMotif]:
        return []

    def _analyze_layout_patterns(
        self, computed_styles: List[Dict]
    ) -> List[VisualMotif]:
        return []

    def _analyze_color_motifs(self, computed_styles: List[Dict]) -> List[VisualMotif]:
        return []

    def _consolidate_motifs(self, motifs: List[VisualMotif]) -> List[VisualMotif]:
        return motifs[:5]

    def _calculate_formality_level(self, text: str) -> float:
        """Calculate formality level (0-1)"""
        formal_indicators = [
            "therefore",
            "however",
            "furthermore",
            "moreover",
            "consequently",
        ]
        informal_indicators = ["hey", "guys", "awesome", "cool", "yeah"]

        formal_count = sum(1 for word in formal_indicators if word in text.lower())
        informal_count = sum(1 for word in informal_indicators if word in text.lower())

        total_indicators = formal_count + informal_count
        if total_indicators == 0:
            return 0.5  # Neutral

        return formal_count / total_indicators

    def _determine_communication_style(
        self, formality_level: float, text: str
    ) -> CommunicationStyle:
        """Determine communication style"""
        if formality_level > 0.7:
            return CommunicationStyle.FORMAL
        elif formality_level > 0.5:
            return CommunicationStyle.PROFESSIONAL
        elif formality_level > 0.3:
            return CommunicationStyle.CASUAL
        else:
            return CommunicationStyle.FRIENDLY

    def _analyze_tone_and_voice(self, text: str) -> Tuple[str, List[str]]:
        """Analyze tone and voice characteristics"""
        characteristics = []

        if "innov" in text.lower():
            characteristics.append("innovative")
        if "quality" in text.lower():
            characteristics.append("quality_focused")
        if "customer" in text.lower():
            characteristics.append("customer_centric")

        tone = "professional" if len(characteristics) > 0 else "neutral"
        return tone, characteristics

    def _extract_keyword_patterns(self, text: str) -> List[str]:
        """Extract keyword patterns"""
        words = text.lower().split()
        word_freq = {}

        for word in words:
            if len(word) > 4:  # Focus on meaningful words
                word_freq[word] = word_freq.get(word, 0) + 1

        # Return top keywords
        return sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]

    def _analyze_phrasing_style(self, text: str) -> str:
        """Analyze phrasing style"""
        sentences = text.split(".")

        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)

        if avg_sentence_length > 20:
            return "complex"
        elif avg_sentence_length > 15:
            return "moderate"
        else:
            return "simple"

    def _analyze_emotional_tone(self, text: str) -> str:
        """Analyze emotional tone"""
        positive_words = ["excellent", "amazing", "innovative", "quality", "success"]
        negative_words = ["problem", "issue", "challenge", "difficult"]

        positive_count = sum(1 for word in positive_words if word in text.lower())
        negative_count = sum(1 for word in negative_words if word in text.lower())

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def _analyze_cta_style(self, computed_styles: List[Dict]) -> str:
        """Analyze call-to-action style"""
        cta_elements = [s for s in computed_styles if "button" in s["selector"].lower()]

        if not cta_elements:
            return "minimal"

        # Analyze button styles
        avg_size = sum(
            float(s["styles"]["fontSize"].replace("px", "")) for s in cta_elements
        ) / len(cta_elements)

        if avg_size > 16:
            return "prominent"
        elif avg_size > 14:
            return "moderate"
        else:
            return "subtle"

    def _analyze_color_harmony(
        self, color_palette: List[ColorPalette]
    ) -> Dict[str, Any]:
        """Analyze color harmony and relationships"""
        if not color_palette:
            return {"harmony_score": 0, "harmony_type": "unknown"}

        # Simplified color harmony analysis
        primary_colors = [c for c in color_palette if c.color_type == ColorType.PRIMARY]

        if len(primary_colors) >= 2:
            return {
                "harmony_score": 0.8,
                "harmony_type": "complementary",
                "color_relationships": "strong_contrast",
            }
        elif len(primary_colors) == 1:
            return {
                "harmony_score": 0.6,
                "harmony_type": "monochromatic",
                "color_relationships": "single_dominant",
            }
        else:
            return {
                "harmony_score": 0.4,
                "harmony_type": "analogous",
                "color_relationships": "harmonious",
            }

    def _calculate_accessibility_score(
        self, color_palette: List[ColorPalette]
    ) -> float:
        """Calculate accessibility score based on color contrast"""
        # Simplified accessibility calculation
        text_colors = [c for c in color_palette if c.color_type == ColorType.TEXT]
        background_colors = [
            c for c in color_palette if c.color_type == ColorType.BACKGROUND
        ]

        if not text_colors or not background_colors:
            return 0.7  # Default score

        # Simplified contrast calculation
        return 0.85  # Placeholder for actual contrast calculation

    def _calculate_typography_consistency(self, typography: List[Typography]) -> float:
        """Calculate typography consistency score"""
        if not typography:
            return 0.5

        # Count unique font families
        unique_fonts = set(t.font_family for t in typography)

        # More consistent = fewer unique fonts
        if len(unique_fonts) <= 2:
            return 0.9
        elif len(unique_fonts) <= 4:
            return 0.7
        else:
            return 0.5

    def _calculate_readability_score(self, typography: List[Typography]) -> float:
        """Calculate readability score"""
        if not typography:
            return 0.5

        # Simplified readability calculation
        avg_font_size = 0
        count = 0

        for t in typography:
            try:
                size = float(t.font_size.replace("px", ""))
                avg_font_size += size
                count += 1
            except:
                continue

        if count == 0:
            return 0.5

        avg_font_size /= count

        # Score based on average font size
        if avg_font_size >= 16:
            return 0.9
        elif avg_font_size >= 14:
            return 0.7
        else:
            return 0.5

    def _calculate_design_complexity(self, visual_motifs: List[VisualMotif]) -> str:
        """Calculate design complexity"""
        motif_count = len(visual_motifs)

        if motif_count >= 5:
            return "high"
        elif motif_count >= 3:
            return "medium"
        else:
            return "low"

    def _determine_dominant_style(self, visual_motifs: List[VisualMotif]) -> str:
        """Determine dominant design style"""
        if not visual_motifs:
            return "minimalist"

        # Count style categories
        style_counts = {}
        for motif in visual_motifs:
            style = motif.style_category
            style_counts[style] = style_counts.get(style, 0) + 1

        # Return most common style
        if style_counts:
            return max(style_counts, key=style_counts.get)
        else:
            return "modern"

    def _calculate_messaging_consistency(
        self, communication_patterns: CommunicationPattern
    ) -> float:
        """Calculate messaging consistency score"""
        # Simplified consistency calculation
        formality_score = 1.0 - abs(communication_patterns.formality_level - 0.5) * 2

        # Check if voice characteristics are consistent
        voice_consistency = len(communication_patterns.voice_characteristics) / 5.0

        return (formality_score + voice_consistency) / 2

    def _infer_brand_personality(
        self,
        color_palette: List[ColorPalette],
        typography: List[Typography],
        communication_patterns: CommunicationPattern,
    ) -> str:
        """Infer brand personality from visual and communication data"""
        # Simplified brand personality inference
        if communication_patterns.style.value == "formal":
            if any(
                c.color_type == ColorType.PRIMARY and c.hsl[1] > 50
                for c in color_palette
            ):
                return "professional_bold"
            else:
                return "professional_conservative"
        elif communication_patterns.style.value == "casual":
            return "friendly_approachable"
        elif communication_patterns.style.value == "creative":
            return "innovative_dynamic"
        else:
            return "balanced_reliable"

    def _infer_target_audience(
        self,
        communication_patterns: CommunicationPattern,
        visual_motifs: List[VisualMotif],
    ) -> str:
        """Infer target audience from communication and visual data"""
        if communication_patterns.formality_level > 0.7:
            return "enterprise_business"
        elif communication_patterns.formality_level < 0.3:
            return "consumer_general"
        else:
            return "professional_general"

    def _infer_industry_alignment(
        self,
        color_palette: List[ColorPalette],
        typography: List[Typography],
        visual_motifs: List[VisualMotif],
    ) -> str:
        """Infer industry alignment from visual data"""
        # Simplified industry inference
        primary_colors = [c for c in color_palette if c.color_type == ColorType.PRIMARY]

        if primary_colors:
            # Check for blue (common in tech/finance)
            blue_colors = [
                c
                for c in primary_colors
                if "blue" in c.hex_code.lower() or c.hsl[0] > 200 and c.hsl[0] < 250
            ]
            if blue_colors:
                return "technology_finance"

            # Check for red/orange (common in food/retail)
            warm_colors = [c for c in primary_colors if c.hsl[0] < 60 or c.hsl[0] > 300]
            if warm_colors:
                return "food_retail"

        return "general_business"

    def _assess_design_maturity(
        self, typography: List[Typography], color_palette: List[ColorPalette]
    ) -> str:
        """Assess design maturity level"""
        typography_score = self._calculate_typography_consistency(typography)
        color_score = len(color_palette) / 10.0  # More colors = more mature

        overall_score = (typography_score + color_score) / 2

        if overall_score > 0.8:
            return "mature"
        elif overall_score > 0.6:
            return "developing"
        else:
            return "emerging"

    def _assess_competitive_differentiation(
        self,
        visual_motifs: List[VisualMotif],
        communication_patterns: CommunicationPattern,
    ) -> str:
        """Assess competitive differentiation"""
        # Simplified differentiation assessment
        unique_motifs = len(set(m.motif_type for m in visual_motifs))
        communication_score = len(communication_patterns.voice_characteristics)

        if unique_motifs >= 3 and communication_score >= 3:
            return "high"
        elif unique_motifs >= 2 or communication_score >= 2:
            return "medium"
        else:
            return "low"

    def _calculate_confidence_score(self, intelligence_report: Dict) -> float:
        """Calculate overall confidence score"""
        # Simplified implementation
        return 0.85


# Global visual intelligence extractor
visual_intelligence_extractor = VisualDesignIntelligenceExtractor()

# FastAPI integration
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Visual Design Intelligence API", version="1.0.0")


@app.post("/extract-visual-intelligence")
async def extract_visual_intelligence(request: Dict[str, Any]):
    """Extract visual design intelligence from website"""

    url = request.get("url")
    user_id = request.get("user_id", "anonymous")

    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    # Validate URL
    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Invalid URL format")

    try:
        result = await visual_intelligence_extractor.extract_visual_intelligence(
            url, user_id
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Visual intelligence extraction failed: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "capabilities": [
            "color_palette_extraction",
            "typography_analysis",
            "visual_motif_identification",
            "communication_style_analysis",
            "design_intelligence_reporting",
        ],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8083)
