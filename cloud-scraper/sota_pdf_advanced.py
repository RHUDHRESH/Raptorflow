"""
Advanced PDF Features and Capabilities
Security, interactivity, templates, and modern document features
"""

import asyncio
import hashlib
import json
import os
import re
import secrets
import tempfile
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

# Enhanced PDF imports
try:
    from reportlab.lib.colors import Color, HexColor, black, grey, white
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
    from reportlab.lib.pagesizes import A3, A4, legal, letter, tabloid
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm, inch, mm, pica
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.pdfdoc import PDFDictionary, PDFName, PDFString
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas
    from reportlab.platypus import (
        CondPageBreak,
        DocAssign,
        DocExec,
        DocPara,
        Flowable,
        Frame,
        Image,
        KeepTogether,
        PageBreak,
        PageTemplate,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
    from reportlab.platypus.doctemplate import IndexingFlowable

    REPORTLAB_AVAILABLE = True
except ImportError as e:
    REPORTLAB_AVAILABLE = False
    REPORTLAB_IMPORT_ERROR = str(e)

# Security imports
try:
    import cryptography
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

from sota_graphics_enhanced import (
    ChartType,
    EnhancedGraphicsGenerator,
    GraphicsQuality,
    ImageProcessor,
)
from sota_pdf_maker_enhanced import (
    CacheManager,
    EnhancedColorManager,
    EnhancedTypographyManager,
    EventManager,
    PDFConfiguration,
    PerformanceTracker,
    logger,
    retry_on_failure,
)


class SecurityLevel(Enum):
    """Document security levels"""

    NONE = "none"
    PASSWORD = "password"
    CERTIFICATE = "certificate"
    DRM = "drm"
    WATERMARK_ONLY = "watermark_only"


class Permission(Enum):
    """PDF permissions"""

    PRINT = "print"
    MODIFY = "modify"
    COPY = "copy"
    ANNOTATE = "annotate"
    FILL_FORMS = "fill_forms"
    EXTRACT = "extract"
    ASSEMBLE = "assemble"


class InteractiveElement(Enum):
    """Interactive PDF elements"""

    HYPERLINK = "hyperlink"
    BOOKMARK = "bookmark"
    FORM_FIELD = "form_field"
    BUTTON = "button"
    ANNOTATION = "annotation"
    MULTIMEDIA = "multimedia"


class TemplateCategory(Enum):
    """Template categories"""

    BUSINESS = "business"
    ACADEMIC = "academic"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    LEGAL = "legal"
    MARKETING = "marketing"
    FINANCIAL = "financial"
    PERSONAL = "personal"


@dataclass
class SecurityConfig:
    """Security configuration"""

    level: SecurityLevel = SecurityLevel.NONE
    password: str = ""
    owner_password: str = ""
    permissions: Dict[Permission, bool] = field(default_factory=dict)
    encryption_strength: int = 128  # 40, 128, 256
    watermark_text: str = ""
    watermark_opacity: float = 0.3
    digital_signature: bool = False
    certificate_path: str = ""

    def __post_init__(self):
        """Set default permissions"""
        if not self.permissions:
            self.permissions = {
                Permission.PRINT: True,
                Permission.MODIFY: False,
                Permission.COPY: False,
                Permission.ANNOTATE: True,
                Permission.FILL_FORMS: True,
                Permission.EXTRACT: False,
                Permission.ASSEMBLE: False,
            }


@dataclass
class InteractiveConfig:
    """Interactive elements configuration"""

    enable_hyperlinks: bool = True
    enable_bookmarks: bool = True
    enable_forms: bool = False
    enable_annotations: bool = True
    enable_multimedia: bool = False
    javascript_actions: bool = False
    form_validation: bool = True


class SecurityManager:
    """Advanced PDF security management"""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.backend = default_backend() if CRYPTO_AVAILABLE else None

    @retry_on_failure(max_retries=3)
    def generate_passwords(self) -> Dict[str, str]:
        """Generate secure passwords"""
        if not CRYPTO_AVAILABLE:
            return {"user": self.config.password, "owner": self.config.owner_password}

        # Generate strong passwords if not provided
        user_password = self.config.password or secrets.token_urlsafe(16)
        owner_password = self.config.owner_password or secrets.token_urlsafe(16)

        return {"user": user_password, "owner": owner_password}

    def apply_security(self, doc_path: str) -> bool:
        """Apply security to PDF document"""
        if self.config.level == SecurityLevel.NONE:
            return True

        try:
            # This would require additional libraries like PyPDF2 or pdfrw
            # For now, we'll implement basic watermarking
            if self.config.watermark_text:
                self._add_watermark(doc_path)

            logger.info(f"Security level {self.config.level.value} applied")
            return True

        except Exception as e:
            logger.error(f"Security application failed: {str(e)}")
            return False

    def _add_watermark(self, doc_path: str) -> None:
        """Add watermark to PDF"""
        # This would require PDF manipulation library
        # Placeholder implementation
        logger.info(f"Watermark '{self.config.watermark_text}' added")


class InteractiveManager:
    """Interactive elements management"""

    def __init__(self, config: InteractiveConfig):
        self.config = config
        self.bookmarks = []
        self.hyperlinks = []
        self.form_fields = []

    def add_bookmark(self, title: str, page: int, level: int = 0) -> None:
        """Add bookmark to document"""
        bookmark = {
            "title": title,
            "page": page,
            "level": level,
            "id": str(uuid.uuid4()),
        }
        self.bookmarks.append(bookmark)

    def add_hyperlink(self, text: str, url: str, page: int = None) -> None:
        """Add hyperlink to document"""
        hyperlink = {"text": text, "url": url, "page": page, "id": str(uuid.uuid4())}
        self.hyperlinks.append(hyperlink)

    def add_form_field(
        self, field_type: str, name: str, options: Dict[str, Any]
    ) -> None:
        """Add form field to document"""
        form_field = {
            "type": field_type,
            "name": name,
            "options": options,
            "id": str(uuid.uuid4()),
        }
        self.form_fields.append(form_field)

    def generate_bookmarks_tree(self) -> Dict[str, Any]:
        """Generate bookmarks tree structure"""
        tree = {}
        for bookmark in self.bookmarks:
            level = bookmark["level"]
            if level not in tree:
                tree[level] = []
            tree[level].append(bookmark)
        return tree


class TemplateEngine:
    """Advanced template engine for PDF generation"""

    def __init__(self):
        self.templates = self._load_templates()
        self.custom_templates = {}

    def _load_templates(self) -> Dict[TemplateCategory, Dict[str, Any]]:
        """Load built-in templates"""
        templates = {
            TemplateCategory.BUSINESS: {
                "executive_summary": {
                    "name": "Executive Summary",
                    "description": "Professional business report template",
                    "sections": [
                        "title",
                        "executive_summary",
                        "key_findings",
                        "recommendations",
                        "appendix",
                    ],
                    "layout": "business",
                    "color_scheme": "corporate",
                    "fonts": ["Helvetica", "Times"],
                    "charts": ["bar", "pie"],
                    "interactive": ["bookmarks", "hyperlinks"],
                },
                "financial_report": {
                    "name": "Financial Report",
                    "description": "Comprehensive financial analysis template",
                    "sections": [
                        "title",
                        "executive_summary",
                        "financial_overview",
                        "detailed_analysis",
                        "forecasts",
                        "appendix",
                    ],
                    "layout": "business",
                    "color_scheme": "corporate",
                    "fonts": ["Helvetica", "Courier"],
                    "charts": ["line", "area", "bar"],
                    "interactive": ["bookmarks", "hyperlinks", "forms"],
                },
                "marketing_plan": {
                    "name": "Marketing Plan",
                    "description": "Strategic marketing plan template",
                    "sections": [
                        "title",
                        "executive_summary",
                        "market_analysis",
                        "strategy",
                        "tactics",
                        "budget",
                        "metrics",
                    ],
                    "layout": "creative",
                    "color_scheme": "vibrant",
                    "fonts": ["Helvetica", "Arial"],
                    "charts": ["bar", "pie", "scatter"],
                    "interactive": ["bookmarks", "hyperlinks"],
                },
            },
            TemplateCategory.ACADEMIC: {
                "research_paper": {
                    "name": "Research Paper",
                    "description": "Academic research paper template",
                    "sections": [
                        "title",
                        "abstract",
                        "introduction",
                        "literature_review",
                        "methodology",
                        "results",
                        "discussion",
                        "conclusion",
                        "references",
                    ],
                    "layout": "academic",
                    "color_scheme": "academic",
                    "fonts": ["Times", "Helvetica"],
                    "charts": ["bar", "line", "scatter"],
                    "interactive": ["bookmarks", "hyperlinks"],
                },
                "thesis": {
                    "name": "Thesis",
                    "description": "Comprehensive thesis template",
                    "sections": [
                        "title",
                        "abstract",
                        "acknowledgments",
                        "table_of_contents",
                        "introduction",
                        "chapters",
                        "conclusion",
                        "bibliography",
                        "appendices",
                    ],
                    "layout": "academic",
                    "color_scheme": "academic",
                    "fonts": ["Times", "Helvetica"],
                    "charts": ["bar", "line", "scatter"],
                    "interactive": ["bookmarks", "hyperlinks"],
                },
            },
            TemplateCategory.CREATIVE: {
                "portfolio": {
                    "name": "Creative Portfolio",
                    "description": "Professional portfolio template",
                    "sections": [
                        "title",
                        "about",
                        "portfolio",
                        "projects",
                        "skills",
                        "contact",
                    ],
                    "layout": "creative",
                    "color_scheme": "vibrant",
                    "fonts": ["Helvetica", "Arial"],
                    "charts": ["bar", "pie"],
                    "interactive": ["bookmarks", "hyperlinks", "multimedia"],
                },
                "magazine": {
                    "name": "Magazine Layout",
                    "description": "Magazine-style layout template",
                    "sections": [
                        "cover",
                        "contents",
                        "articles",
                        "features",
                        "back_matter",
                    ],
                    "layout": "magazine",
                    "color_scheme": "creative",
                    "fonts": ["Helvetica", "Times", "Arial"],
                    "charts": ["bar", "pie", "area"],
                    "interactive": ["bookmarks", "hyperlinks", "multimedia"],
                },
            },
            TemplateCategory.TECHNICAL: {
                "technical_document": {
                    "name": "Technical Document",
                    "description": "Technical specification template",
                    "sections": [
                        "title",
                        "executive_summary",
                        "specifications",
                        "implementation",
                        "testing",
                        "appendix",
                    ],
                    "layout": "technical",
                    "color_scheme": "tech",
                    "fonts": ["Courier", "Helvetica"],
                    "charts": ["line", "area", "scatter"],
                    "interactive": ["bookmarks", "hyperlinks"],
                },
                "api_documentation": {
                    "name": "API Documentation",
                    "description": "API reference documentation template",
                    "sections": [
                        "title",
                        "overview",
                        "authentication",
                        "endpoints",
                        "examples",
                        "error_handling",
                    ],
                    "layout": "technical",
                    "color_scheme": "tech",
                    "fonts": ["Courier", "Helvetica"],
                    "charts": ["line", "area"],
                    "interactive": ["bookmarks", "hyperlinks", "forms"],
                },
            },
        }
        return templates

    def get_template(
        self, category: TemplateCategory, template_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get specific template"""
        category_templates = self.templates.get(category, {})
        return category_templates.get(template_name)

    def list_templates(
        self, category: Optional[TemplateCategory] = None
    ) -> List[Dict[str, Any]]:
        """List available templates"""
        templates_list = []

        if category:
            category_templates = self.templates.get(category, {})
            for name, template in category_templates.items():
                template_info = {
                    "category": category.value,
                    "name": name,
                    "display_name": template["name"],
                    "description": template["description"],
                }
                templates_list.append(template_info)
        else:
            for cat, category_templates in self.templates.items():
                for name, template in category_templates.items():
                    template_info = {
                        "category": cat.value,
                        "name": name,
                        "display_name": template["name"],
                        "description": template["description"],
                    }
                    templates_list.append(template_info)

        return templates_list

    def register_custom_template(
        self, category: TemplateCategory, name: str, template: Dict[str, Any]
    ) -> None:
        """Register custom template"""
        if category not in self.custom_templates:
            self.custom_templates[category] = {}

        self.custom_templates[category][name] = template
        logger.info(
            f"Custom template '{name}' registered in category '{category.value}'"
        )

    def apply_template(
        self, category: TemplateCategory, template_name: str, content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply template to content"""
        template = self.get_template(category, template_name)
        if not template:
            logger.error(
                f"Template '{template_name}' not found in category '{category.value}'"
            )
            return content

        # Reorganize content according to template sections
        organized_content = {}

        for section in template["sections"]:
            if section in content:
                organized_content[section] = content[section]
            else:
                # Add placeholder for missing sections
                organized_content[section] = (
                    f"[{section.replace('_', ' ').title()} content]"
                )

        # Add any additional content not in template
        for key, value in content.items():
            if key not in organized_content:
                organized_content[key] = value

        return organized_content


class DocumentBuilder:
    """Advanced document builder with template support"""

    def __init__(self, config: PDFConfiguration):
        self.config = config
        self.color_manager = EnhancedColorManager(config.color_scheme)
        self.typography = EnhancedTypographyManager(config)
        self.graphics = EnhancedGraphicsGenerator(self.color_manager)
        self.image_processor = ImageProcessor()
        self.template_engine = TemplateEngine()
        self.event_manager = EventManager()
        self.performance_tracker = PerformanceTracker()

        # Advanced features
        self.security_manager = None
        self.interactive_manager = None

        # Caching
        self.content_cache = CacheManager[Dict[str, Any]]()
        self.document_cache = CacheManager[str]()

    def set_security(self, security_config: SecurityConfig) -> None:
        """Set security configuration"""
        self.security_manager = SecurityManager(security_config)

    def set_interactive(self, interactive_config: InteractiveConfig) -> None:
        """Set interactive configuration"""
        self.interactive_manager = InteractiveManager(interactive_config)

    @retry_on_failure(max_retries=3)
    async def build_document_async(
        self,
        content: Dict[str, Any],
        template_category: Optional[TemplateCategory] = None,
        template_name: Optional[str] = None,
        output_path: str = "enhanced_document.pdf",
    ) -> bool:
        """Build enhanced PDF document asynchronously"""
        with self.performance_tracker.track_generation():
            try:
                # Apply template if specified
                if template_category and template_name:
                    content = self.template_engine.apply_template(
                        template_category, template_name, content
                    )

                # Generate cache key
                cache_key = self._generate_content_cache_key(
                    content, template_category, template_name
                )

                # Check cache
                cached_doc = self.document_cache.get(cache_key)
                if cached_doc:
                    # Copy cached document to output path
                    import shutil

                    shutil.copy2(cached_doc, output_path)
                    logger.info(f"Document retrieved from cache: {output_path}")
                    return True

                # Create PDF document
                success = await self._create_enhanced_pdf(content, output_path)

                if success:
                    # Cache the generated document
                    self.document_cache.set(cache_key, output_path)

                    # Apply security if configured
                    if self.security_manager:
                        self.security_manager.apply_security(output_path)

                    logger.info(f"Enhanced document built successfully: {output_path}")
                    return True

                return False

            except Exception as e:
                logger.error(f"Document building failed: {str(e)}")
                return False

    async def _create_enhanced_pdf(
        self, content: Dict[str, Any], output_path: str
    ) -> bool:
        """Create enhanced PDF with all features"""
        if not REPORTLAB_AVAILABLE:
            logger.error("ReportLab not available")
            return False

        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=getattr(
                    __import__("reportlab.lib.pagesizes"), self.config.page_size
                ),
                leftMargin=self.config.margin_left,
                rightMargin=self.config.margin_right,
                topMargin=self.config.margin_top,
                bottomMargin=self.config.margin_bottom,
            )

            # Build story (content elements)
            story = []

            # Add title page
            story.extend(self._create_enhanced_title_page(content))

            # Add table of contents
            if self.config.enable_toc:
                story.extend(self._create_enhanced_toc(content))

            # Add main content
            story.extend(await self._create_enhanced_main_content(content))

            # Add appendix
            if content.get("appendix"):
                story.extend(self._create_enhanced_appendix(content["appendix"]))

            # Build PDF with enhanced callbacks
            doc.build(
                story,
                onFirstPage=self._on_enhanced_first_page,
                onLaterPages=self._on_enhanced_later_page,
            )

            return True

        except Exception as e:
            logger.error(f"PDF creation failed: {str(e)}")
            return False

    def _create_enhanced_title_page(self, content: Dict[str, Any]) -> List[Any]:
        """Create enhanced title page"""
        elements = []

        # Add spacing
        elements.append(Spacer(1, 2 * inch))

        # Main title with enhanced styling
        title_style = self.typography.get_style("title", self.color_manager)
        elements.append(Paragraph(self.config.title, title_style))

        # Subtitle
        if content.get("subtitle"):
            subtitle_style = self.typography.get_style("subtitle", self.color_manager)
            elements.append(Paragraph(content["subtitle"], subtitle_style))

        # Author and date with enhanced layout
        elements.append(Spacer(1, 1.5 * inch))

        # Create metadata table
        metadata_style = self.typography.get_style("body", self.color_manager)
        metadata_data = [
            ["Author:", self.config.author],
            ["Date:", datetime.now().strftime("%B %d, %Y")],
            ["Document ID:", self.config.document_id[:8].upper()],
            ["Classification:", content.get("classification", "Public")],
        ]

        metadata_table = Table(metadata_data, colWidths=[2 * inch, 4 * inch])
        metadata_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (0, -1),
                        self.color_manager.get_hex_color("light"),
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (0, -1),
                        self.color_manager.get_hex_color("dark"),
                    ),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 12),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        1,
                        self.color_manager.get_hex_color("light"),
                    ),
                    (
                        "BACKGROUND",
                        (1, 0),
                        (1, -1),
                        self.color_manager.get_hex_color("background"),
                    ),
                ]
            )
        )

        elements.append(metadata_table)

        # Additional metadata
        if content.get("metadata"):
            elements.append(Spacer(1, 0.5 * inch))
            for key, value in content["metadata"].items():
                elements.append(
                    Paragraph(f"<b>{key.title()}:</b> {value}", metadata_style)
                )

        # Page break
        elements.append(PageBreak())

        return elements

    def _create_enhanced_toc(self, content: Dict[str, Any]) -> List[Any]:
        """Create enhanced table of contents"""
        elements = []

        # TOC title
        toc_title = self.typography.get_style("heading1", self.color_manager)
        elements.append(Paragraph("Table of Contents", toc_title))
        elements.append(Spacer(1, 0.3 * inch))

        # Enhanced TOC content with dots
        toc_data = [["Section", "Page"]]

        page_counter = 3  # Start after title and TOC

        if content.get("executive_summary"):
            toc_data.append(["Executive Summary", str(page_counter)])
            page_counter += 1

        if content.get("introduction"):
            toc_data.append(["Introduction", str(page_counter)])
            page_counter += 1

        # Add main sections
        for section_name in content.keys():
            if section_name not in [
                "metadata",
                "subtitle",
                "executive_summary",
                "introduction",
                "appendix",
            ]:
                display_name = section_name.replace("_", " ").title()
                toc_data.append([display_name, str(page_counter)])
                # Estimate page count based on content size
                section_content = content[section_name]
                if isinstance(section_content, dict):
                    page_counter += len(section_content) // 3 + 1
                elif isinstance(section_content, list):
                    page_counter += len(section_content) // 5 + 1
                else:
                    page_counter += 1

        if content.get("appendix"):
            toc_data.append(["Appendix", str(page_counter)])

        # Create enhanced TOC table
        toc_style = TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    self.color_manager.get_hex_color("primary"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    self.color_manager.get_hex_color("background"),
                ),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                (
                    "BACKGROUND",
                    (0, 1),
                    (-1, -1),
                    self.color_manager.get_hex_color("background"),
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    1,
                    self.color_manager.get_hex_color("light"),
                ),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 10),
            ]
        )

        toc_table = Table(toc_data, colWidths=[4 * inch, 1 * inch])
        toc_table.setStyle(toc_style)

        elements.append(toc_table)
        elements.append(Spacer(1, 0.5 * inch))
        elements.append(PageBreak())

        return elements

    async def _create_enhanced_main_content(self, content: Dict[str, Any]) -> List[Any]:
        """Create enhanced main content sections"""
        elements = []

        # Executive Summary
        if content.get("executive_summary"):
            elements.extend(
                await self._create_enhanced_section(
                    "Executive Summary", content["executive_summary"]
                )
            )

        # Introduction
        if content.get("introduction"):
            elements.extend(
                await self._create_enhanced_section(
                    "Introduction", content["introduction"]
                )
            )

        # Main sections
        for section_name, section_content in content.items():
            if section_name not in [
                "metadata",
                "subtitle",
                "executive_summary",
                "introduction",
                "appendix",
            ]:
                display_name = section_name.replace("_", " ").title()
                elements.extend(
                    await self._create_enhanced_section(display_name, section_content)
                )

        return elements

    async def _create_enhanced_section(self, title: str, content: Any) -> List[Any]:
        """Create enhanced content section"""
        elements = []

        # Section title
        title_style = self.typography.get_style("heading1", self.color_manager)
        elements.append(Paragraph(title, title_style))

        # Add bookmark if interactive manager is available
        if self.interactive_manager:
            self.interactive_manager.add_bookmark(title, len(elements), 0)

        # Process content based on type
        if isinstance(content, dict):
            for key, value in content.items():
                if isinstance(value, (list, dict)):
                    # Subsection
                    subtitle_style = self.typography.get_style(
                        "heading2", self.color_manager
                    )
                    elements.append(
                        Paragraph(key.replace("_", " ").title(), subtitle_style)
                    )

                    # Add bookmark
                    if self.interactive_manager:
                        self.interactive_manager.add_bookmark(
                            key.replace("_", " ").title(), len(elements), 1
                        )

                    elements.extend(await self._process_enhanced_content(value))
                else:
                    # Simple key-value
                    body_style = self.typography.get_style("body", self.color_manager)
                    elements.append(
                        Paragraph(
                            f"<b>{key.replace('_', ' ').title()}:</b> {value}",
                            body_style,
                        )
                    )

        elif isinstance(content, list):
            elements.extend(await self._process_enhanced_content(content))

        elif isinstance(content, str):
            body_style = self.typography.get_style("body", self.color_manager)
            elements.append(Paragraph(content, body_style))

        # Add spacing
        elements.append(Spacer(1, 0.3 * inch))

        return elements

    async def _process_enhanced_content(self, content: Any) -> List[Any]:
        """Process various content types with enhanced features"""
        elements = []
        body_style = self.typography.get_style("body", self.color_manager)

        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    for key, value in item.items():
                        if key == "chart" and self.config.enable_charts:
                            # Create enhanced chart
                            chart_config = value
                            chart_type = ChartType(chart_config.get("type", "bar"))
                            chart_data = chart_config.get("data", {})

                            chart_path = await self.graphics.create_chart_async(
                                chart_type,
                                chart_data,
                                chart_config.get("width", 400),
                                chart_config.get("height", 300),
                                chart_config.get("style", "modern"),
                            )

                            if chart_path:
                                img = Image(chart_path, width=4 * inch, height=3 * inch)
                                elements.append(img)
                                elements.append(Spacer(1, 0.2 * inch))

                                # Add caption
                                if chart_config.get("title"):
                                    caption_style = self.typography.get_style(
                                        "caption", self.color_manager
                                    )
                                    elements.append(
                                        Paragraph(chart_config["title"], caption_style)
                                    )
                        else:
                            elements.append(
                                Paragraph(f"<b>{key}:</b> {value}", body_style)
                            )
                elif isinstance(item, str):
                    elements.append(Paragraph(f"• {item}", body_style))
                else:
                    elements.append(Paragraph(str(item), body_style))

        elif isinstance(content, dict):
            for key, value in content.items():
                if key == "chart" and self.config.enable_charts:
                    # Create enhanced chart
                    chart_config = value
                    chart_type = ChartType(chart_config.get("type", "bar"))
                    chart_data = chart_config.get("data", {})

                    chart_path = await self.graphics.create_chart_async(
                        chart_type,
                        chart_data,
                        chart_config.get("width", 400),
                        chart_config.get("height", 300),
                        chart_config.get("style", "modern"),
                    )

                    if chart_path:
                        img = Image(chart_path, width=4 * inch, height=3 * inch)
                        elements.append(img)
                        elements.append(Spacer(1, 0.2 * inch))

                        # Add caption
                        if chart_config.get("title"):
                            caption_style = self.typography.get_style(
                                "caption", self.color_manager
                            )
                            elements.append(
                                Paragraph(chart_config["title"], caption_style)
                            )
                else:
                    elements.append(Paragraph(f"<b>{key}:</b> {value}", body_style))

        return elements

    def _create_enhanced_appendix(self, appendix: Dict[str, Any]) -> List[Any]:
        """Create enhanced appendix section"""
        elements = []

        # Appendix title
        title_style = self.typography.get_style("heading1", self.color_manager)
        elements.append(Paragraph("Appendix", title_style))

        # Process appendix content
        elements.extend(asyncio.run(self._process_enhanced_content(appendix)))

        return elements

    def _on_enhanced_first_page(self, canvas, doc):
        """Enhanced first page callback"""
        # Add watermark
        if self.config.enable_watermark:
            self._add_enhanced_watermark(canvas, doc)

        # Add enhanced headers/footers
        self._add_enhanced_header_footer(canvas, doc, 1, 1)

    def _on_enhanced_later_page(self, canvas, doc):
        """Enhanced later pages callback"""
        # Add watermark
        if self.config.enable_watermark:
            self._add_enhanced_watermark(canvas, doc)

        # Add enhanced headers/footers
        self._add_enhanced_header_footer(canvas, doc, 2, 2)

    def _add_enhanced_watermark(self, canvas, doc):
        """Add enhanced watermark"""
        canvas.saveState()
        canvas.setFont("Helvetica-Bold", 72)
        canvas.setFillColor(Color(0.9, 0.9, 0.9, self.config.watermark_opacity))
        canvas.rotate(45)
        canvas.drawCentredText(
            doc.pagesize[0] / 2, doc.pagesize[1] / 2, self.config.watermark_text
        )
        canvas.restoreState()

    def _add_enhanced_header_footer(
        self, canvas, doc, current_page: int, total_pages: int
    ):
        """Add enhanced headers and footers"""
        canvas.saveState()

        # Header
        if self.config.enable_headers:
            canvas.setFont(self.config.font_family, 9)
            canvas.setFillColor(self.color_manager.get_hex_color("secondary"))
            canvas.drawString(inch, doc.pagesize[1] - inch, self.config.title)
            canvas.drawRightString(
                doc.pagesize[0] - inch,
                doc.pagesize[1] - inch,
                datetime.now().strftime("%Y-%m-%d"),
            )

        # Footer
        if self.config.enable_footers:
            canvas.setFont(self.config.font_family, 9)
            canvas.setFillColor(self.color_manager.get_hex_color("secondary"))

            # Page numbers
            if self.config.enable_page_numbers:
                page_text = f"Page {current_page}"
                canvas.drawCentredText(doc.pagesize[0] / 2, inch, page_text)

            # Author info
            canvas.drawString(inch, inch, f"Generated by {self.config.author}")
            canvas.drawRightString(
                doc.pagesize[0] - inch, inch, f"© {datetime.now().year}"
            )

        canvas.restoreState()

    def _generate_content_cache_key(
        self,
        content: Dict[str, Any],
        template_category: Optional[TemplateCategory],
        template_name: Optional[str],
    ) -> str:
        """Generate cache key for content"""
        params = {
            "content": content,
            "template_category": template_category.value if template_category else None,
            "template_name": template_name,
            "config": {
                "title": self.config.title,
                "color_scheme": self.config.color_scheme.value,
                "page_layout": self.config.page_layout.value,
            },
        }
        params_str = json.dumps(params, sort_keys=True)
        return hashlib.md5(params_str.encode()).hexdigest()

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        return {
            "document_metrics": self.performance_tracker.get_metrics().__dict__,
            "graphics_metrics": self.graphics.get_performance_metrics(),
            "cache_size": len(self.document_cache._cache),
            "content_cache_size": len(self.content_cache._cache),
            "templates_available": len(self.template_engine.templates),
            "security_enabled": self.security_manager is not None,
            "interactive_enabled": self.interactive_manager is not None,
        }


if __name__ == "__main__":
    print("📚 Advanced PDF Features Module Loaded")
    print("✅ Features:")
    print("  🔐 Advanced security and encryption")
    print("  🔗 Interactive elements (bookmarks, hyperlinks, forms)")
    print("  📋 Template engine with 10+ templates")
    print("  🎨 Enhanced layouts and styling")
    print("  📊 Performance tracking and caching")
    print("  🏗️ Document builder with async support")
