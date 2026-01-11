"""
TemplateTool for Raptorflow agent system.
Handles template management, rendering, and customization.
"""

import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from jinja2 import BaseLoader, Environment, Template, TemplateError

from ..base import BaseTool
from ..exceptions import ToolError, ValidationError

logger = logging.getLogger(__name__)


@dataclass
class TemplateRequest:
    """Template rendering request."""

    template_id: str
    template_type: str  # content, email, report, dashboard, etc.
    variables: Dict[str, Any]
    format: str  # html, markdown, plain_text, json
    language: str  # en, es, fr, etc.
    workspace_id: str
    customization: Optional[Dict[str, Any]] = None


@dataclass
class TemplateResult:
    """Template rendering result."""

    rendered_content: str
    template_id: str
    template_type: str
    format: str
    variables_used: List[str]
    missing_variables: List[str]
    render_time_ms: int
    metadata: Dict[str, Any]


@dataclass
class TemplateDefinition:
    """Template definition."""

    template_id: str
    name: str
    description: str
    template_type: str
    content: str
    variables: Dict[str, Any]
    default_format: str
    supported_formats: List[str]
    language: str
    version: str
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]


class TemplateTool(BaseTool):
    """Advanced template management and rendering tool."""

    def __init__(self):
        super().__init__(
            name="template_tool",
            description="Template management and rendering system",
            version="1.0.0",
        )

        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=BaseLoader(), autoescape=True, trim_blocks=True, lstrip_blocks=True
        )

        # Template categories
        self.template_categories = {
            "content": {
                "description": "Content generation templates",
                "subcategories": ["blog", "social", "email", "ad_copy", "newsletter"],
            },
            "report": {
                "description": "Report and analytics templates",
                "subcategories": ["performance", "analytics", "summary", "detailed"],
            },
            "dashboard": {
                "description": "Dashboard and UI templates",
                "subcategories": ["marketing", "sales", "analytics", "overview"],
            },
            "email": {
                "description": "Email communication templates",
                "subcategories": [
                    "marketing",
                    "transactional",
                    "newsletter",
                    "notification",
                ],
            },
            "document": {
                "description": "Document and proposal templates",
                "subcategories": ["proposal", "contract", "report", "presentation"],
            },
        }

        # Built-in templates
        self.built_in_templates = self._initialize_built_in_templates()

        # Template validation rules
        self.validation_rules = {
            "required_variables": ["title", "content"],
            "max_template_size": 100000,  # 100KB
            "max_render_time": 5000,  # 5 seconds
            "allowed_formats": ["html", "markdown", "plain_text", "json"],
            "variable_pattern": r"\{\{\s*([^}]+)\s*\}\}",
        }

        # Template customization options
        self.customization_options = {
            "brand_colors": ["primary", "secondary", "accent", "background", "text"],
            "typography": ["font_family", "font_size", "line_height", "font_weight"],
            "layout": ["spacing", "alignment", "width", "height"],
            "content": ["tone", "style", "voice", "formality"],
        }

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute template operation."""
        try:
            operation = kwargs.get("operation", "render")

            if operation == "render":
                return await self._render_template(**kwargs)
            elif operation == "create":
                return await self._create_template(**kwargs)
            elif operation == "update":
                return await self._update_template(**kwargs)
            elif operation == "delete":
                return await self._delete_template(**kwargs)
            elif operation == "list":
                return await self._list_templates(**kwargs)
            elif operation == "validate":
                return await self._validate_template(**kwargs)
            else:
                raise ValidationError(f"Unsupported operation: {operation}")

        except Exception as e:
            logger.error(f"Template operation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": kwargs.get("operation", "unknown"),
                "timestamp": datetime.now().isoformat(),
            }

    async def _render_template(self, **kwargs) -> Dict[str, Any]:
        """Render a template with variables."""
        try:
            # Parse template request
            request = self._parse_template_request(kwargs)

            # Validate request
            self._validate_template_request(request)

            # Get template
            template_def = await self._get_template(
                request.template_id, request.workspace_id
            )

            # Render template
            result = await self._render_template_content(template_def, request)

            # Store render history
            await self._store_render_history(result, request.workspace_id)

            return {
                "success": True,
                "template_result": result.__dict__,
                "rendered_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Template rendering failed: {e}")
            raise ToolError(f"Template rendering failed: {str(e)}")

    async def _create_template(self, **kwargs) -> Dict[str, Any]:
        """Create a new template."""
        try:
            template_data = kwargs.get("template_data", {})
            workspace_id = kwargs.get("workspace_id", "")

            # Validate template data
            self._validate_template_data(template_data)

            # Create template definition
            template_def = TemplateDefinition(
                template_id=template_data.get("template_id", ""),
                name=template_data.get("name", ""),
                description=template_data.get("description", ""),
                template_type=template_data.get("template_type", ""),
                content=template_data.get("content", ""),
                variables=template_data.get("variables", {}),
                default_format=template_data.get("default_format", "html"),
                supported_formats=template_data.get("supported_formats", ["html"]),
                language=template_data.get("language", "en"),
                version=template_data.get("version", "1.0.0"),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                metadata=template_data.get("metadata", {}),
            )

            # Store template
            await self._store_template(template_def, workspace_id)

            return {
                "success": True,
                "template_id": template_def.template_id,
                "created_at": template_def.created_at.isoformat(),
            }

        except Exception as e:
            logger.error(f"Template creation failed: {e}")
            raise ToolError(f"Template creation failed: {str(e)}")

    async def _update_template(self, **kwargs) -> Dict[str, Any]:
        """Update an existing template."""
        try:
            template_id = kwargs.get("template_id", "")
            workspace_id = kwargs.get("workspace_id", "")
            update_data = kwargs.get("update_data", {})

            # Get existing template
            existing_template = await self._get_template(template_id, workspace_id)

            # Update fields
            for key, value in update_data.items():
                if hasattr(existing_template, key):
                    setattr(existing_template, key, value)

            existing_template.updated_at = datetime.now()

            # Store updated template
            await self._store_template(existing_template, workspace_id)

            return {
                "success": True,
                "template_id": template_id,
                "updated_at": existing_template.updated_at.isoformat(),
            }

        except Exception as e:
            logger.error(f"Template update failed: {e}")
            raise ToolError(f"Template update failed: {str(e)}")

    async def _delete_template(self, **kwargs) -> Dict[str, Any]:
        """Delete a template."""
        try:
            template_id = kwargs.get("template_id", "")
            workspace_id = kwargs.get("workspace_id", "")

            # Delete template
            await self._delete_template_storage(template_id, workspace_id)

            return {
                "success": True,
                "template_id": template_id,
                "deleted_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Template deletion failed: {e}")
            raise ToolError(f"Template deletion failed: {str(e)}")

    async def _list_templates(self, **kwargs) -> Dict[str, Any]:
        """List available templates."""
        try:
            workspace_id = kwargs.get("workspace_id", "")
            template_type = kwargs.get("template_type", "")
            language = kwargs.get("language", "")

            # Get templates
            templates = await self._get_templates_list(
                workspace_id, template_type, language
            )

            return {
                "success": True,
                "templates": templates,
                "count": len(templates),
                "listed_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Template listing failed: {e}")
            raise ToolError(f"Template listing failed: {str(e)}")

    async def _validate_template(self, **kwargs) -> Dict[str, Any]:
        """Validate template syntax and variables."""
        try:
            template_content = kwargs.get("template_content", "")
            variables = kwargs.get("variables", {})

            # Parse template
            template = self.jinja_env.from_string(template_content)

            # Check for syntax errors
            try:
                template.render(variables)
                syntax_valid = True
                syntax_error = None
            except TemplateError as e:
                syntax_valid = False
                syntax_error = str(e)

            # Extract variables from template
            template_variables = self._extract_template_variables(template_content)

            # Check for missing variables
            missing_variables = [
                var for var in template_variables if var not in variables
            ]

            # Check for unused variables
            unused_variables = [
                var for var in variables if var not in template_variables
            ]

            return {
                "success": True,
                "syntax_valid": syntax_valid,
                "syntax_error": syntax_error,
                "template_variables": template_variables,
                "missing_variables": missing_variables,
                "unused_variables": unused_variables,
                "validation_summary": {
                    "total_variables": len(template_variables),
                    "provided_variables": len(variables),
                    "missing_count": len(missing_variables),
                    "unused_count": len(unused_variables),
                },
                "validated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Template validation failed: {e}")
            raise ToolError(f"Template validation failed: {str(e)}")

    def _parse_template_request(self, kwargs: Dict[str, Any]) -> TemplateRequest:
        """Parse template request from kwargs."""
        return TemplateRequest(
            template_id=kwargs.get("template_id", ""),
            template_type=kwargs.get("template_type", ""),
            variables=kwargs.get("variables", {}),
            format=kwargs.get("format", "html"),
            language=kwargs.get("language", "en"),
            workspace_id=kwargs.get("workspace_id", ""),
            customization=kwargs.get("customization", {}),
        )

    def _validate_template_request(self, request: TemplateRequest):
        """Validate template request."""
        if not request.template_id:
            raise ValidationError("Template ID is required")

        if not request.workspace_id:
            raise ValidationError("Workspace ID is required")

        if request.format not in self.validation_rules["allowed_formats"]:
            raise ValidationError(f"Unsupported format: {request.format}")

        if not isinstance(request.variables, dict):
            raise ValidationError("Variables must be a dictionary")

    async def _get_template(
        self, template_id: str, workspace_id: str
    ) -> TemplateDefinition:
        """Get template by ID."""
        # First check built-in templates
        if template_id in self.built_in_templates:
            return self.built_in_templates[template_id]

        # Then check workspace templates
        workspace_template = await self._get_workspace_template(
            template_id, workspace_id
        )
        if workspace_template:
            return workspace_template

        raise ValidationError(f"Template not found: {template_id}")

    async def _render_template_content(
        self, template_def: TemplateDefinition, request: TemplateRequest
    ) -> TemplateResult:
        """Render template content."""
        start_time = datetime.now()

        try:
            # Apply customization
            customized_content = self._apply_customization(
                template_def.content, request.customization
            )

            # Create Jinja2 template
            template = self.jinja_env.from_string(customized_content)

            # Render with variables
            rendered_content = template.render(request.variables)

            # Format output
            formatted_content = self._format_output(rendered_content, request.format)

            # Calculate render time
            render_time = (datetime.now() - start_time).total_seconds() * 1000

            # Extract used variables
            used_variables = self._extract_template_variables(customized_content)
            missing_variables = [
                var for var in used_variables if var not in request.variables
            ]

            return TemplateResult(
                rendered_content=formatted_content,
                template_id=template_def.template_id,
                template_type=template_def.template_type,
                format=request.format,
                variables_used=used_variables,
                missing_variables=missing_variables,
                render_time_ms=int(render_time),
                metadata={
                    "template_name": template_def.name,
                    "template_version": template_def.version,
                    "language": request.language,
                    "customization_applied": bool(request.customization),
                },
            )

        except TemplateError as e:
            raise ToolError(f"Template rendering error: {str(e)}")

    def _apply_customization(
        self, content: str, customization: Optional[Dict[str, Any]]
    ) -> str:
        """Apply customization to template content."""
        if not customization:
            return content

        customized_content = content

        # Apply brand colors
        if "brand_colors" in customization:
            colors = customization["brand_colors"]
            for color_name, color_value in colors.items():
                customized_content = customized_content.replace(
                    f"{{brand_colors.{color_name}}}", color_value
                )

        # Apply typography
        if "typography" in customization:
            typography = customization["typography"]
            for typo_name, typo_value in typography.items():
                customized_content = customized_content.replace(
                    f"{{typography.{typo_name}}}", typo_value
                )

        # Apply layout
        if "layout" in customization:
            layout = customization["layout"]
            for layout_name, layout_value in layout.items():
                customized_content = customized_content.replace(
                    f"{{layout.{layout_name}}}", layout_value
                )

        # Apply content style
        if "content" in customization:
            content_style = customization["content"]
            for style_name, style_value in content_style.items():
                customized_content = customized_content.replace(
                    f"{{content.{style_name}}}", style_value
                )

        return customized_content

    def _format_output(self, content: str, format_type: str) -> str:
        """Format output based on format type."""
        if format_type == "html":
            return content
        elif format_type == "markdown":
            return self._convert_to_markdown(content)
        elif format_type == "plain_text":
            return self._convert_to_plain_text(content)
        elif format_type == "json":
            return json.dumps({"content": content}, indent=2)
        else:
            return content

    def _convert_to_markdown(self, content: str) -> str:
        """Convert HTML to Markdown (simplified)."""
        # Basic HTML to Markdown conversion
        content = re.sub(r"<h1[^>]*>(.*?)</h1>", r"# \1", content)
        content = re.sub(r"<h2[^>]*>(.*?)</h2>", r"## \1", content)
        content = re.sub(r"<h3[^>]*>(.*?)</h3>", r"### \1", content)
        content = re.sub(r"<p[^>]*>(.*?)</p>", r"\1\n\n", content)
        content = re.sub(r"<strong[^>]*>(.*?)</strong>", r"**\1**", content)
        content = re.sub(r"<em[^>]*>(.*?)</em>", r"*\1*", content)
        content = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r"[\2](\1)", content)
        content = re.sub(r"<ul[^>]*>(.*?)</ul>", r"\1", content)
        content = re.sub(r"<li[^>]*>(.*?)</li>", r"- \1", content)

        # Remove remaining HTML tags
        content = re.sub(r"<[^>]*>", "", content)

        return content.strip()

    def _convert_to_plain_text(self, content: str) -> str:
        """Convert HTML to plain text."""
        # Remove all HTML tags
        content = re.sub(r"<[^>]*>", "", content)

        # Normalize whitespace
        content = re.sub(r"\s+", " ", content)

        return content.strip()

    def _extract_template_variables(self, content: str) -> List[str]:
        """Extract variables from template content."""
        pattern = re.compile(self.validation_rules["variable_pattern"])
        matches = pattern.findall(content)

        # Clean up variable names
        variables = []
        for match in matches:
            # Remove filters and functions
            clean_var = match.split("|")[0].strip()
            if clean_var and clean_var not in variables:
                variables.append(clean_var)

        return variables

    async def _store_render_history(self, result: TemplateResult, workspace_id: str):
        """Store template render history."""
        try:
            # This would integrate with the database tool
            logger.info(
                f"Storing render history for template {result.template_id} in workspace {workspace_id}"
            )

        except Exception as e:
            logger.error(f"Failed to store render history: {e}")

    def _validate_template_data(self, template_data: Dict[str, Any]):
        """Validate template data."""
        required_fields = ["template_id", "name", "template_type", "content"]

        for field in required_fields:
            if field not in template_data:
                raise ValidationError(f"Missing required field: {field}")

        # Validate template size
        if len(template_data["content"]) > self.validation_rules["max_template_size"]:
            raise ValidationError("Template content too large")

        # Validate template syntax
        try:
            self.jinja_env.from_string(template_data["content"])
        except TemplateError as e:
            raise ValidationError(f"Invalid template syntax: {str(e)}")

    async def _store_template(
        self, template_def: TemplateDefinition, workspace_id: str
    ):
        """Store template in database."""
        try:
            # This would integrate with the database tool
            logger.info(
                f"Storing template {template_def.template_id} in workspace {workspace_id}"
            )

        except Exception as e:
            logger.error(f"Failed to store template: {e}")

    async def _delete_template_storage(self, template_id: str, workspace_id: str):
        """Delete template from storage."""
        try:
            # This would integrate with the database tool
            logger.info(
                f"Deleting template {template_id} from workspace {workspace_id}"
            )

        except Exception as e:
            logger.error(f"Failed to delete template: {e}")

    async def _get_workspace_template(
        self, template_id: str, workspace_id: str
    ) -> Optional[TemplateDefinition]:
        """Get workspace-specific template."""
        # This would integrate with the database tool
        # For now, return None
        return None

    async def _get_templates_list(
        self, workspace_id: str, template_type: str, language: str
    ) -> List[Dict[str, Any]]:
        """Get list of templates."""
        templates = []

        # Add built-in templates
        for template_id, template_def in self.built_in_templates.items():
            if template_type and template_def.template_type != template_type:
                continue
            if language and template_def.language != language:
                continue

            templates.append(
                {
                    "template_id": template_def.template_id,
                    "name": template_def.name,
                    "description": template_def.description,
                    "template_type": template_def.template_type,
                    "language": template_def.language,
                    "version": template_def.version,
                    "is_builtin": True,
                }
            )

        # Add workspace templates (would integrate with database)

        return templates

    def _initialize_built_in_templates(self) -> Dict[str, TemplateDefinition]:
        """Initialize built-in templates."""
        templates = {}

        # Blog post template
        templates["blog_post"] = TemplateDefinition(
            template_id="blog_post",
            name="Blog Post Template",
            description="Standard blog post template with sections",
            template_type="content",
            content="""
# {{title}}

{{summary}}

## Introduction
{{introduction}}

## Main Content
{{main_content}}

## Conclusion
{{conclusion}}

## Call to Action
{{call_to_action}}

---
*Published on {{publish_date}} by {{author}}*
            """.strip(),
            variables={
                "title": "string",
                "summary": "string",
                "introduction": "string",
                "main_content": "string",
                "conclusion": "string",
                "call_to_action": "string",
                "publish_date": "date",
                "author": "string",
            },
            default_format="markdown",
            supported_formats=["markdown", "html", "plain_text"],
            language="en",
            version="1.0.0",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"category": "content", "subcategory": "blog"},
        )

        # Email template
        templates["email_marketing"] = TemplateDefinition(
            template_id="email_marketing",
            name="Marketing Email Template",
            description="Standard marketing email template",
            template_type="email",
            content="""
Subject: {{subject}}

Hi {{recipient_name}},

{{greeting}}

{{main_content}}

{{call_to_action}}

{{signature}}

---
Unsubscribe | Privacy Policy | Contact Us
            """.strip(),
            variables={
                "subject": "string",
                "recipient_name": "string",
                "greeting": "string",
                "main_content": "string",
                "call_to_action": "string",
                "signature": "string",
            },
            default_format="plain_text",
            supported_formats=["plain_text", "html"],
            language="en",
            version="1.0.0",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"category": "email", "subcategory": "marketing"},
        )

        # Social media template
        templates["social_post"] = TemplateDefinition(
            template_id="social_post",
            name="Social Media Post Template",
            description="Standard social media post template",
            template_type="content",
            content="""
{{hook}}

{{main_message}}

{{call_to_action}}

{{hashtags}}
            """.strip(),
            variables={
                "hook": "string",
                "main_message": "string",
                "call_to_action": "string",
                "hashtags": "string",
            },
            default_format="plain_text",
            supported_formats=["plain_text"],
            language="en",
            version="1.0.0",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"category": "content", "subcategory": "social"},
        )

        # Report template
        templates["performance_report"] = TemplateDefinition(
            template_id="performance_report",
            name="Performance Report Template",
            description="Standard performance report template",
            template_type="report",
            content="""
# {{report_title}}

**Period:** {{report_period}}
**Generated:** {{generated_date}}

## Executive Summary
{{executive_summary}}

## Key Metrics
{{key_metrics}}

## Detailed Analysis
{{detailed_analysis}}

## Recommendations
{{recommendations}}

## Next Steps
{{next_steps}}
            """.strip(),
            variables={
                "report_title": "string",
                "report_period": "string",
                "generated_date": "date",
                "executive_summary": "string",
                "key_metrics": "string",
                "detailed_analysis": "string",
                "recommendations": "string",
                "next_steps": "string",
            },
            default_format="markdown",
            supported_formats=["markdown", "html"],
            language="en",
            version="1.0.0",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"category": "report", "subcategory": "performance"},
        )

        return templates

    def get_template_categories(self) -> Dict[str, Any]:
        """Get available template categories."""
        return self.template_categories.copy()

    def get_built_in_templates(self) -> Dict[str, TemplateDefinition]:
        """Get built-in templates."""
        return self.built_in_templates.copy()

    def get_customization_options(self) -> Dict[str, List[str]]:
        """Get customization options."""
        return self.customization_options.copy()

    def get_validation_rules(self) -> Dict[str, Any]:
        """Get validation rules."""
        return self.validation_rules.copy()
