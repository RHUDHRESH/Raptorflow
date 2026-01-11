"""
ExportTool for Raptorflow agent system.
Handles data export in multiple formats with customization options.
"""

import csv
import io
import json
import logging
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..base import BaseTool
from ..exceptions import ToolError, ValidationError

logger = logging.getLogger(__name__)


@dataclass
class ExportRequest:
    """Export request definition."""

    export_type: str  # data, report, analytics, content, workflow
    data_source: str  # database, file, api, memory
    format: str  # json, csv, xlsx, pdf, xml, yaml
    filters: Dict[str, Any]
    fields: List[str]
    sorting: List[Dict[str, str]]
    workspace_id: str
    user_id: Optional[str] = None
    export_options: Optional[Dict[str, Any]] = None


@dataclass
class ExportResult:
    """Export result."""

    export_id: str
    file_name: str
    file_format: str
    file_size: int
    record_count: int
    export_time_ms: int
    download_url: Optional[str]
    metadata: Dict[str, Any]


@dataclass
class ExportTemplate:
    """Export template definition."""

    template_id: str
    name: str
    description: str
    export_type: str
    format: str
    fields: List[str]
    filters: Dict[str, Any]
    sorting: List[Dict[str, str]]
    export_options: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class ExportTool(BaseTool):
    """Advanced data export tool with multiple format support."""

    def __init__(self):
        super().__init__(
            name="export_tool",
            description="Advanced data export with multiple format support",
            version="1.0.0",
        )

        # Supported export types
        self.export_types = {
            "data": {
                "description": "Raw data export",
                "supported_formats": ["json", "csv", "xlsx", "xml"],
                "default_fields": ["id", "created_at", "updated_at"],
                "max_records": 100000,
            },
            "report": {
                "description": "Formatted report export",
                "supported_formats": ["pdf", "html", "xlsx", "json"],
                "default_fields": ["title", "content", "metrics", "created_at"],
                "max_records": 10000,
            },
            "analytics": {
                "description": "Analytics data export",
                "supported_formats": ["json", "csv", "xlsx", "yaml"],
                "default_fields": ["metric_name", "value", "timestamp", "dimensions"],
                "max_records": 50000,
            },
            "content": {
                "description": "Content export",
                "supported_formats": ["json", "csv", "xml", "yaml"],
                "default_fields": [
                    "content_id",
                    "type",
                    "title",
                    "content",
                    "created_at",
                ],
                "max_records": 25000,
            },
            "workflow": {
                "description": "Workflow data export",
                "supported_formats": ["json", "yaml", "xml"],
                "default_fields": [
                    "workflow_id",
                    "status",
                    "steps",
                    "created_at",
                    "completed_at",
                ],
                "max_records": 5000,
            },
        }

        # Format configurations
        self.format_configs = {
            "json": {
                "extension": ".json",
                "mime_type": "application/json",
                "options": {"indent": 2, "ensure_ascii": False},
            },
            "csv": {
                "extension": ".csv",
                "mime_type": "text/csv",
                "options": {
                    "delimiter": ",",
                    "quotechar": '"',
                    "quoting": csv.QUOTE_MINIMAL,
                },
            },
            "xlsx": {
                "extension": ".xlsx",
                "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "options": {"engine": "openpyxl"},
            },
            "pdf": {
                "extension": ".pdf",
                "mime_type": "application/pdf",
                "options": {"format": "A4", "margin": "1cm"},
            },
            "xml": {
                "extension": ".xml",
                "mime_type ": "application/xml",
                "options": {"encoding": "utf-8", "pretty_print": True},
            },
            "yaml": {
                "extension": ".yaml",
                "mime_type": "application/x-yaml",
                "options": {"default_flow_style": False},
            },
        }

        # Export templates
        self.export_templates = self._initialize_export_templates()

        # Validation rules
        self.validation_rules = {
            "max_export_size": 100 * 1024 * 1024,  # 100MB
            "max_export_time": 300,  # 5 minutes
            "supported_formats": list(self.format_configs.keys()),
            "required_fields": ["workspace_id", "export_type", "format"],
        }

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute export operation."""
        try:
            operation = kwargs.get("operation", "export")

            if operation == "export":
                return await self._export_data(**kwargs)
            elif operation == "create_template":
                return await self._create_export_template(**kwargs)
            elif operation == "list_templates":
                return await self._list_export_templates(**kwargs)
            elif operation == "get_export_status":
                return await self._get_export_status(**kwargs)
            elif operation == "download":
                return await self._download_export(**kwargs)
            else:
                raise ValidationError(f"Unsupported operation: {operation}")

        except Exception as e:
            logger.error(f"Export operation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": kwargs.get("operation", "unknown"),
                "timestamp": datetime.now().isoformat(),
            }

    async def _export_data(self, **kwargs) -> Dict[str, Any]:
        """Export data in specified format."""
        try:
            # Parse export request
            request = self._parse_export_request(kwargs)

            # Validate request
            self._validate_export_request(request)

            # Get data
            data = await self._get_export_data(request)

            # Apply filters and sorting
            processed_data = self._process_data(data, request)

            # Export to format
            export_result = await self._export_to_format(processed_data, request)

            # Store export result
            await self._store_export_result(export_result, request.workspace_id)

            return {
                "success": True,
                "export_result": export_result.__dict__,
                "exported_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Data export failed: {e}")
            raise ToolError(f"Data export failed: {str(e)}")

    async def _create_export_template(self, **kwargs) -> Dict[str, Any]:
        """Create export template."""
        try:
            template_data = kwargs.get("template_data", {})
            workspace_id = kwargs.get("workspace_id", "")

            # Validate template data
            self._validate_template_data(template_data)

            # Create template
            template = ExportTemplate(
                template_id=template_data.get("template_id", ""),
                name=template_data.get("name", ""),
                description=template_data.get("description", ""),
                export_type=template_data.get("export_type", ""),
                format=template_data.get("format", ""),
                fields=template_data.get("fields", []),
                filters=template_data.get("filters", {}),
                sorting=template_data.get("sorting", []),
                export_options=template_data.get("export_options", {}),
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

            # Store template
            await self._store_export_template(template, workspace_id)

            return {
                "success": True,
                "template_id": template.template_id,
                "created_at": template.created_at.isoformat(),
            }

        except Exception as e:
            logger.error(f"Template creation failed: {e}")
            raise ToolError(f"Template creation failed: {str(e)}")

    async def _list_export_templates(self, **kwargs) -> Dict[str, Any]:
        """List available export templates."""
        try:
            workspace_id = kwargs.get("workspace_id", "")
            export_type = kwargs.get("export_type", "")

            # Get templates
            templates = await self._get_export_templates(workspace_id, export_type)

            return {
                "success": True,
                "templates": templates,
                "count": len(templates),
                "listed_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Template listing failed: {e}")
            raise ToolError(f"Template listing failed: {str(e)}")

    async def _get_export_status(self, **kwargs) -> Dict[str, Any]:
        """Get export status."""
        try:
            export_id = kwargs.get("export_id", "")
            workspace_id = kwargs.get("workspace_id", "")

            if not export_id:
                raise ValidationError("Export ID is required")

            # Get export status
            status = await self._retrieve_export_status(export_id, workspace_id)

            return {
                "success": True,
                "export_id": export_id,
                "status": status,
                "checked_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Status check failed: {e}")
            raise ToolError(f"Status check failed: {str(e)}")

    async def _download_export(self, **kwargs) -> Dict[str, Any]:
        """Download exported file."""
        try:
            export_id = kwargs.get("export_id", "")
            workspace_id = kwargs.get("workspace_id", "")

            if not export_id:
                raise ValidationError("Export ID is required")

            # Get export file
            file_data, file_info = await self._retrieve_export_file(
                export_id, workspace_id
            )

            return {
                "success": True,
                "file_data": file_data,
                "file_info": file_info,
                "downloaded_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Download failed: {e}")
            raise ToolError(f"Download failed: {str(e)}")

    def _parse_export_request(self, kwargs: Dict[str, Any]) -> ExportRequest:
        """Parse export request from kwargs."""
        return ExportRequest(
            export_type=kwargs.get("export_type", "data"),
            data_source=kwargs.get("data_source", "database"),
            format=kwargs.get("format", "json"),
            filters=kwargs.get("filters", {}),
            fields=kwargs.get("fields", []),
            sorting=kwargs.get("sorting", []),
            workspace_id=kwargs.get("workspace_id", ""),
            user_id=kwargs.get("user_id"),
            export_options=kwargs.get("export_options", {}),
        )

    def _validate_export_request(self, request: ExportRequest):
        """Validate export request."""
        # Check required fields
        for field in self.validation_rules["required_fields"]:
            if not getattr(request, field, None):
                raise ValidationError(f"Missing required field: {field}")

        # Validate export type
        if request.export_type not in self.export_types:
            raise ValidationError(f"Unsupported export type: {request.export_type}")

        # Validate format
        if request.format not in self.validation_rules["supported_formats"]:
            raise ValidationError(f"Unsupported format: {request.format}")

        # Check format compatibility with export type
        export_type_config = self.export_types[request.export_type]
        if request.format not in export_type_config["supported_formats"]:
            raise ValidationError(
                f"Format {request.format} not supported for export type {request.export_type}"
            )

        # Validate fields
        if not request.fields:
            request.fields = export_type_config["default_fields"]

    async def _get_export_data(self, request: ExportRequest) -> List[Dict[str, Any]]:
        """Get data for export."""
        try:
            # This would integrate with the database tool or other data sources
            # For now, return sample data
            sample_data = [
                {
                    "id": 1,
                    "title": "Sample Data 1",
                    "content": "Sample content",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                },
                {
                    "id": 2,
                    "title": "Sample Data 2",
                    "content": "Another sample content",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                },
            ]

            # Apply max records limit
            max_records = self.export_types[request.export_type]["max_records"]
            return sample_data[:max_records]

        except Exception as e:
            logger.error(f"Failed to get export data: {e}")
            raise ToolError(f"Failed to get export data: {str(e)}")

    def _process_data(
        self, data: List[Dict[str, Any]], request: ExportRequest
    ) -> List[Dict[str, Any]]:
        """Process data with filters and sorting."""
        processed_data = data.copy()

        # Apply filters
        if request.filters:
            processed_data = self._apply_filters(processed_data, request.filters)

        # Apply field selection
        if request.fields:
            processed_data = self._apply_field_selection(processed_data, request.fields)

        # Apply sorting
        if request.sorting:
            processed_data = self._apply_sorting(processed_data, request.sorting)

        return processed_data

    def _apply_filters(
        self, data: List[Dict[str, Any]], filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply filters to data."""
        filtered_data = []

        for item in data:
            include_item = True

            for field, filter_config in filters.items():
                if field not in item:
                    include_item = False
                    break

                field_value = item[field]

                # Handle different filter types
                if isinstance(filter_config, dict):
                    filter_type = filter_config.get("type", "equals")
                    filter_value = filter_config.get("value")

                    if filter_type == "equals":
                        if field_value != filter_value:
                            include_item = False
                            break
                    elif filter_type == "contains":
                        if filter_value not in str(field_value):
                            include_item = False
                            break
                    elif filter_type == "greater_than":
                        if field_value <= filter_value:
                            include_item = False
                            break
                    elif filter_type == "less_than":
                        if field_value >= filter_value:
                            include_item = False
                            break
                    elif filter_type == "in_list":
                        if field_value not in filter_value:
                            include_item = False
                            break
                else:
                    # Simple equality filter
                    if field_value != filter_config:
                        include_item = False
                        break

            if include_item:
                filtered_data.append(item)

        return filtered_data

    def _apply_field_selection(
        self, data: List[Dict[str, Any]], fields: List[str]
    ) -> List[Dict[str, Any]]:
        """Apply field selection to data."""
        selected_data = []

        for item in data:
            selected_item = {}
            for field in fields:
                if field in item:
                    selected_item[field] = item[field]
            selected_data.append(selected_item)

        return selected_data

    def _apply_sorting(
        self, data: List[Dict[str, Any]], sorting: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """Apply sorting to data."""
        if not sorting:
            return data

        # Sort by multiple fields
        for sort_config in reversed(sorting):
            field = sort_config.get("field")
            direction = sort_config.get("direction", "asc")

            if field:
                reverse = direction == "desc"
                data.sort(key=lambda x: x.get(field, ""), reverse=reverse)

        return data

    async def _export_to_format(
        self, data: List[Dict[str, Any]], request: ExportRequest
    ) -> ExportResult:
        """Export data to specified format."""
        start_time = datetime.now()

        try:
            # Generate file name
            file_name = self._generate_file_name(request)

            # Export based on format
            if request.format == "json":
                file_content = self._export_to_json(data, request.export_options)
            elif request.format == "csv":
                file_content = self._export_to_csv(data, request.export_options)
            elif request.format == "xlsx":
                file_content = self._export_to_xlsx(data, request.export_options)
            elif request.format == "pdf":
                file_content = self._export_to_pdf(data, request.export_options)
            elif request.format == "xml":
                file_content = self._export_to_xml(data, request.export_options)
            elif request.format == "yaml":
                file_content = self._export_to_yaml(data, request.export_options)
            else:
                raise ValidationError(f"Unsupported export format: {request.format}")

            # Calculate export time
            export_time = (datetime.now() - start_time).total_seconds() * 1000

            # Create export result
            result = ExportResult(
                export_id=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(file_name) % 10000}",
                file_name=file_name,
                file_format=request.format,
                file_size=len(file_content.encode("utf-8")),
                record_count=len(data),
                export_time_ms=int(export_time),
                download_url=None,  # Would be generated by storage system
                metadata={
                    "export_type": request.export_type,
                    "data_source": request.data_source,
                    "filters": request.filters,
                    "fields": request.fields,
                    "sorting": request.sorting,
                    "exported_at": datetime.now().isoformat(),
                    "workspace_id": request.workspace_id,
                    "user_id": request.user_id,
                },
            )

            # Store file content (would integrate with storage system)
            await self._store_export_file(
                result.export_id, file_content, request.workspace_id
            )

            return result

        except Exception as e:
            logger.error(f"Format export failed: {e}")
            raise ToolError(f"Format export failed: {str(e)}")

    def _generate_file_name(self, request: ExportRequest) -> str:
        """Generate file name for export."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        format_config = self.format_configs[request.format]

        return f"{request.export_type}_export_{timestamp}{format_config['extension']}"

    def _export_to_json(
        self, data: List[Dict[str, Any]], options: Dict[str, Any]
    ) -> str:
        """Export data to JSON format."""
        json_options = self.format_configs["json"]["options"].copy()
        json_options.update(options or {})

        return json.dumps(data, **json_options)

    def _export_to_csv(
        self, data: List[Dict[str, Any]], options: Dict[str, Any]
    ) -> str:
        """Export data to CSV format."""
        if not data:
            return ""

        output = io.StringIO()

        # Get CSV options
        csv_options = self.format_configs["csv"]["options"].copy()
        csv_options.update(options or {})

        writer = csv.DictWriter(output, fieldnames=data[0].keys(), **csv_options)
        writer.writeheader()
        writer.writerows(data)

        return output.getvalue()

    def _export_to_xlsx(
        self, data: List[Dict[str, Any]], options: Dict[str, Any]
    ) -> bytes:
        """Export data to Excel format."""
        try:
            import pandas as pd

            # Convert to DataFrame
            df = pd.DataFrame(data)

            # Create Excel file in memory
            output = io.BytesIO()

            # Get Excel options
            excel_options = self.format_configs["xlsx"]["options"].copy()
            excel_options.update(options or {})

            # Write to Excel
            with pd.ExcelWriter(
                output, engine=excel_options.get("engine", "openpyxl")
            ) as writer:
                df.to_excel(writer, index=False, sheet_name="Export Data")

            return output.getvalue()

        except ImportError:
            raise ToolError("pandas and openpyxl are required for Excel export")

    def _export_to_pdf(
        self, data: List[Dict[str, Any]], options: Dict[str, Any]
    ) -> bytes:
        """Export data to PDF format."""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4, letter
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import (
                Paragraph,
                SimpleDocTemplate,
                Table,
                TableStyle,
            )

            # Create PDF in memory
            output = io.BytesIO()

            # Get PDF options
            pdf_options = self.format_configs["pdf"]["options"].copy()
            pdf_options.update(options or {})

            # Create document
            doc = SimpleDocTemplate(
                output,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18,
            )

            # Create content
            story = []
            styles = getSampleStyleSheet()

            # Add title
            title = Paragraph("Data Export", styles["Title"])
            story.append(title)

            # Add table
            if data:
                headers = list(data[0].keys())
                table_data = [headers]

                for row in data:
                    table_data.append([str(row.get(header, "")) for header in headers])

                table = Table(table_data)
                table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, 0), 14),
                            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                            ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ]
                    )
                )
                story.append(table)

            # Build PDF
            doc.build(story)

            return output.getvalue()

        except ImportError:
            raise ToolError("reportlab is required for PDF export")

    def _export_to_xml(
        self, data: List[Dict[str, Any]], options: Dict[str, Any]
    ) -> str:
        """Export data to XML format."""
        import xml.etree.ElementTree as ET

        # Create root element
        root = ET.Element("export_data")
        root.set("export_type", "data")
        root.set("timestamp", datetime.now().isoformat())
        root.set("record_count", str(len(data)))

        # Add records
        for i, record in enumerate(data):
            record_elem = ET.SubElement(root, "record")
            record_elem.set("id", str(i))

            for key, value in record.items():
                field_elem = ET.SubElement(record_elem, "field")
                field_elem.set("name", key)
                field_elem.text = str(value)

        # Convert to string
        xml_options = self.format_configs["xml"]["options"].copy()
        xml_options.update(options or {})

        if xml_options.get("pretty_print", True):
            ET.indent(root)

        return ET.tostring(root, encoding=xml_options.get("encoding", "utf-8")).decode()

    def _export_to_yaml(
        self, data: List[Dict[str, Any]], options: Dict[str, Any]
    ) -> str:
        """Export data to YAML format."""
        try:
            import yaml

            yaml_options = self.format_configs["yaml"]["options"].copy()
            yaml_options.update(options or {})

            return yaml.dump(data, **yaml_options)

        except ImportError:
            raise ToolError("PyYAML is required for YAML export")

    async def _store_export_result(self, result: ExportResult, workspace_id: str):
        """Store export result in database."""
        try:
            # This would integrate with the database tool
            logger.info(
                f"Storing export result {result.export_id} in workspace {workspace_id}"
            )

        except Exception as e:
            logger.error(f"Failed to store export result: {e}")

    async def _store_export_file(
        self, export_id: str, file_content: Union[str, bytes], workspace_id: str
    ):
        """Store export file."""
        try:
            # This would integrate with the storage system
            logger.info(f"Storing export file {export_id} in workspace {workspace_id}")

        except Exception as e:
            logger.error(f"Failed to store export file: {e}")

    def _validate_template_data(self, template_data: Dict[str, Any]):
        """Validate export template data."""
        required_fields = ["template_id", "name", "export_type", "format"]

        for field in required_fields:
            if field not in template_data:
                raise ValidationError(f"Missing required field: {field}")

        # Validate export type and format compatibility
        if template_data["export_type"] not in self.export_types:
            raise ValidationError(
                f"Invalid export type: {template_data['export_type']}"
            )

        if template_data["format"] not in self.validation_rules["supported_formats"]:
            raise ValidationError(f"Invalid format: {template_data['format']}")

    async def _store_export_template(self, template: ExportTemplate, workspace_id: str):
        """Store export template."""
        try:
            # This would integrate with the database tool
            logger.info(
                f"Storing export template {template.template_id} in workspace {workspace_id}"
            )

        except Exception as e:
            logger.error(f"Failed to store export template: {e}")

    async def _get_export_templates(
        self, workspace_id: str, export_type: str
    ) -> List[Dict[str, Any]]:
        """Get export templates."""
        templates = []

        # Add built-in templates
        for template_id, template in self.export_templates.items():
            if export_type and template.export_type != export_type:
                continue

            templates.append(
                {
                    "template_id": template.template_id,
                    "name": template.name,
                    "description": template.description,
                    "export_type": template.export_type,
                    "format": template.format,
                    "fields": template.fields,
                    "is_builtin": True,
                }
            )

        # Add workspace templates (would integrate with database)

        return templates

    async def _retrieve_export_status(
        self, export_id: str, workspace_id: str
    ) -> Dict[str, Any]:
        """Retrieve export status."""
        # This would integrate with the database tool
        return {
            "status": "completed",
            "progress": 100,
            "file_size": 1024,
            "created_at": datetime.now().isoformat(),
        }

    async def _retrieve_export_file(self, export_id: str, workspace_id: str) -> tuple:
        """Retrieve export file."""
        # This would integrate with the storage system
        sample_content = '{"sample": "data"}'
        file_info = {
            "file_name": f"{export_id}.json",
            "file_format": "json",
            "file_size": len(sample_content),
        }

        return sample_content, file_info

    def _initialize_export_templates(self) -> Dict[str, ExportTemplate]:
        """Initialize built-in export templates."""
        templates = {}

        # Data export template
        templates["data_basic"] = ExportTemplate(
            template_id="data_basic",
            name="Basic Data Export",
            description="Basic data export with standard fields",
            export_type="data",
            format="json",
            fields=["id", "created_at", "updated_at"],
            filters={},
            sorting=[{"field": "created_at", "direction": "desc"}],
            export_options={},
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Report export template
        templates["report_summary"] = ExportTemplate(
            template_id="report_summary",
            name="Summary Report Export",
            description="Summary report in PDF format",
            export_type="report",
            format="pdf",
            fields=["title", "summary", "metrics", "created_at"],
            filters={},
            sorting=[{"field": "created_at", "direction": "desc"}],
            export_options={},
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Analytics export template
        templates["analytics_csv"] = ExportTemplate(
            template_id="analytics_csv",
            name="Analytics CSV Export",
            description="Analytics data in CSV format",
            export_type="analytics",
            format="csv",
            fields=["metric_name", "value", "timestamp", "dimensions"],
            filters={},
            sorting=[{"field": "timestamp", "direction": "desc"}],
            export_options={},
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        return templates

    def get_export_types(self) -> Dict[str, Any]:
        """Get available export types."""
        return self.export_types.copy()

    def get_supported_formats(self) -> List[str]:
        """Get supported export formats."""
        return self.validation_rules["supported_formats"].copy()

    def get_export_templates(self) -> Dict[str, ExportTemplate]:
        """Get built-in export templates."""
        return self.export_templates.copy()

    def get_format_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get format configurations."""
        return self.format_configs.copy()
