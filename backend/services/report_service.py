"""
RaptorFlow Report Generation Service
Phase 4.1.1: Multi-Format Report Generation

Generates comprehensive reports in multiple formats including PDF, Excel,
PowerPoint, and interactive web reports with data visualization.
"""

import asyncio
import io
import json
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum

import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio

from backend.services.llm_service import LLMService, ExtractionContext
from config import get_settings
from backend.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class ReportFormat(str, Enum):
    """Report output formats."""
    PDF = "pdf"
    EXCEL = "excel"
    POWERPOINT = "powerpoint"
    HTML = "html"
    JSON = "json"
    CSV = "csv"


class ReportType(str, Enum):
    """Types of reports."""
    EXECUTIVE_SUMMARY = "executive_summary"
    MARKET_ANALYSIS = "market_analysis"
    COMPETITIVE_INTELLIGENCE = "competitive_intelligence"
    ICP_ANALYSIS = "icp_analysis"
    FINANCIAL_PROJECTIONS = "financial_projections"
    DETAILED_ANALYSIS = "detailed_analysis"
    DASHBOARD = "dashboard"


class ChartType(str, Enum):
    """Chart types for visualizations."""
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    TREEMAP = "treemap"
    WATERFALL = "waterfall"
    FUNNEL = "funnel"


@dataclass
class ReportSection:
    """Individual report section."""
    title: str
    content: str
    charts: List[Dict]
    tables: List[Dict]
    metadata: Dict


@dataclass
class ChartConfig:
    """Chart configuration."""
    type: ChartType
    title: str
    data: Dict
    x_axis: Optional[str] = None
    y_axis: Optional[str] = None
    color_scheme: str = "viridis"
    size: Tuple[int, int] = (800, 600)


@dataclass
class GeneratedReport:
    """Generated report metadata."""
    id: str
    type: ReportType
    format: ReportFormat
    title: str
    sections: List[ReportSection]
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    generated_at: datetime
    metadata: Dict


class PDFGenerator:
    """PDF report generator."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        
    async def generate_pdf(self, report: GeneratedReport) -> bytes:
        """
        Generate PDF report.
        
        Args:
            report: Report to generate
            
        Returns:
            PDF file as bytes
        """
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            
            # Build story (content)
            story = []
            
            # Title page
            story.extend(await self._create_title_page(report))
            
            # Table of contents
            story.extend(await self._create_table_of_contents(report))
            
            # Executive summary
            story.extend(await self._create_executive_summary(report))
            
            # Sections
            for section in report.sections:
                story.extend(await self._create_section(section))
            
            # Build PDF
            doc.build(story)
            
            # Get bytes
            buffer.seek(0)
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            raise
    
    async def _create_title_page(self, report: GeneratedReport) -> List:
        """Create title page content."""
        content = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center
        )
        
        content.append(Paragraph(report.title, title_style))
        content.append(Spacer(1, 12))
        
        # Metadata
        meta_style = self.styles['Normal']
        content.append(Paragraph(f"Report Type: {report.type.value}", meta_style))
        content.append(Paragraph(f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M')}", meta_style))
        content.append(Paragraph(f"Sections: {len(report.sections)}", meta_style))
        
        content.append(Spacer(1, 24))
        
        return content
    
    async def _create_table_of_contents(self, report: GeneratedReport) -> List:
        """Create table of contents."""
        content = []
        
        # TOC title
        toc_style = ParagraphStyle(
            'TOCTitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=20
        )
        
        content.append(Paragraph("Table of Contents", toc_style))
        
        # TOC items
        toc_data = []
        for i, section in enumerate(report.sections, 1):
            toc_data.append([str(i), section.title])
        
        if toc_data:
            toc_table = Table(toc_data, colWidths=[0.5*inch, 4*inch])
            toc_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), 'CENTER'),
                ('FONTNAME', (0, 0), 'Helvetica'),
                ('FONTSIZE', (0, 0), 12),
                ('BOTTOMPADDING', (0, 0), 12),
            ]))
            
            content.append(toc_table)
        
        content.append(Spacer(1, 24))
        
        return content
    
    async def _create_executive_summary(self, report: GeneratedReport) -> List:
        """Create executive summary section."""
        content = []
        
        # Section title
        title_style = self.styles['Heading2']
        content.append(Paragraph("Executive Summary", title_style))
        content.append(Spacer(1, 12))
        
        # Summary content
        summary_style = self.styles['Normal']
        if report.sections:
            first_section = report.sections[0]
            content.append(Paragraph(first_section.content[:500] + "...", summary_style))
        
        # Key metrics
        if report.metadata.get('key_metrics'):
            metrics_data = [['Metric', 'Value']]
            for metric, value in report.metadata['key_metrics'].items():
                metrics_data.append([metric, str(value)])
            
            metrics_table = Table(metrics_data, colWidths=[2*inch, 2*inch])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), colors.black),
                ('ALIGN', (0, 0), 'LEFT'),
                ('FONTNAME', (0, 0), 'Helvetica'),
                ('FONTSIZE', (0, 0), 10),
                ('GRID', (0, 0), 1, 1, colors.black)
            ]))
            
            content.append(Spacer(1, 12))
            content.append(Paragraph("Key Metrics:", self.styles['Heading3']))
            content.append(metrics_table)
        
        content.append(Spacer(1, 24))
        
        return content
    
    async def _create_section(self, section: ReportSection) -> List:
        """Create report section."""
        content = []
        
        # Section title
        title_style = self.styles['Heading2']
        content.append(Paragraph(section.title, title_style))
        content.append(Spacer(1, 12))
        
        # Section content
        content_style = self.styles['Normal']
        content.append(Paragraph(section.content, content_style))
        content.append(Spacer(1, 12))
        
        # Charts (placeholder - would need chart generation)
        if section.charts:
            content.append(Paragraph("Charts:", self.styles['Heading3']))
            for chart in section.charts:
                content.append(Paragraph(f"• {chart.get('title', 'Chart')}", content_style))
        
        # Tables
        if section.tables:
            content.append(Paragraph("Data Tables:", self.styles['Heading3']))
            for table in section.tables:
                content.append(Paragraph(f"• {table.get('title', 'Table')}", content_style))
        
        content.append(Spacer(1, 24))
        
        return content


class ExcelGenerator:
    """Excel report generator."""
    
    async def generate_excel(self, report: GeneratedReport) -> bytes:
        """
        Generate Excel report.
        
        Args:
            report: Report to generate
            
        Returns:
            Excel file as bytes
        """
        try:
            buffer = io.BytesIO()
            
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                # Summary sheet
                await self._create_summary_sheet(report, writer)
                
                # Data sheets for each section
                for i, section in enumerate(report.sections):
                    await self._create_section_sheet(section, writer, f"Section_{i+1}")
                
                # Charts sheet
                if report.metadata.get('charts'):
                    await self._create_charts_sheet(report.metadata['charts'], writer)
            
            buffer.seek(0)
            excel_bytes = buffer.getvalue()
            buffer.close()
            
            return excel_bytes
            
        except Exception as e:
            logger.error(f"Excel generation failed: {e}")
            raise
    
    async def _create_summary_sheet(self, report: GeneratedReport, writer):
        """Create summary sheet in Excel."""
        summary_data = {
            'Report ID': [report.id],
            'Title': [report.title],
            'Type': [report.type.value],
            'Format': [report.format.value],
            'Generated': [report.generated_at.strftime('%Y-%m-%d %H:%M')],
            'Sections': [len(report.sections)]
        }
        
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name='Summary', index=False)
    
    async def _create_section_sheet(self, section: ReportSection, writer, sheet_name: str):
        """Create section sheet in Excel."""
        # Section metadata
        section_data = {
            'Section Title': [section.title],
            'Content Length': [len(section.content)],
            'Charts': [len(section.charts)],
            'Tables': [len(section.tables)]
        }
        
        df_section = pd.DataFrame(section_data)
        df_section.to_excel(writer, sheet_name=f"{sheet_name}_Info", index=False)
        
        # Section content
        if section.content:
            content_data = {'Content': [section.content]}
            df_content = pd.DataFrame(content_data)
            df_content.to_excel(writer, sheet_name=f"{sheet_name}_Content", index=False)
        
        # Section tables
        for i, table in enumerate(section.tables):
            if table.get('data'):
                df_table = pd.DataFrame(table['data'])
                df_table.to_excel(writer, sheet_name=f"{sheet_name}_Table_{i+1}", index=False)
    
    async def _create_charts_sheet(self, charts: List[Dict], writer):
        """Create charts data sheet in Excel."""
        if not charts:
            return
        
        # Combine all chart data
        all_chart_data = []
        for chart in charts:
            if chart.get('data'):
                chart_df = pd.DataFrame(chart['data'])
                chart_df['Chart_Title'] = chart.get('title', 'Chart')
                chart_df['Chart_Type'] = chart.get('type', 'Unknown')
                all_chart_data.append(chart_df)
        
        if all_chart_data:
            df_all_charts = pd.concat(all_chart_data, ignore_index=True)
            df_all_charts.to_excel(writer, sheet_name='Charts', index=False)


class PowerPointGenerator:
    """PowerPoint report generator."""
    
    async def generate_powerpoint(self, report: GeneratedReport) -> bytes:
        """
        Generate PowerPoint report.
        
        Args:
            report: Report to generate
            
        Returns:
            PowerPoint file as bytes
        """
        try:
            # This would use python-pptx library
            # For now, return placeholder implementation
            buffer = io.BytesIO()
            
            # Create basic PowerPoint structure
            # Title slide
            # Executive summary slide
            # Section slides
            # Chart slides
            # Conclusion slide
            
            buffer.seek(0)
            ppt_bytes = buffer.getvalue()
            buffer.close()
            
            return ppt_bytes
            
        except Exception as e:
            logger.error(f"PowerPoint generation failed: {e}")
            raise


class HTMLGenerator:
    """HTML report generator with interactive charts."""
    
    def __init__(self):
        self.chart_generator = ChartGenerator()
        
    async def generate_html(self, report: GeneratedReport) -> str:
        """
        Generate HTML report with interactive charts.
        
        Args:
            report: Report to generate
            
        Returns:
            HTML string
        """
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{report.title}</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                <style>
                    {self._get_css_styles()}
                </style>
            </head>
            <body>
                <div class="container">
                    <header class="header">
                        <h1>{report.title}</h1>
                        <div class="meta">
                            <span class="type">{report.type.value.replace('_', ' ').title()}</span>
                            <span class="date">{report.generated_at.strftime('%B %d, %Y')}</span>
                        </div>
                    </header>
                    
                    <nav class="toc">
                        <h2>Table of Contents</h2>
                        <ul>
                            {self._generate_toc_html(report.sections)}
                        </ul>
                    </nav>
                    
                    <main class="content">
                        {self._generate_executive_summary_html(report)}
                        {self._generate_sections_html(report.sections)}
                    </main>
                    
                    <footer class="footer">
                        <p>Generated by RaptorFlow Intelligence Platform</p>
                    </footer>
                </div>
                
                <script>
                    {self._generate_javascript(report)}
                </script>
            </body>
            </html>
            """
            
            return html_content
            
        except Exception as e:
            logger.error(f"HTML generation failed: {e}")
            raise
    
    def _get_css_styles(self) -> str:
        """Get CSS styles for HTML report."""
        return """
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background-color: #f8f9fa;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: white;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            
            .header {
                border-bottom: 2px solid #007bff;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }
            
            .header h1 {
                color: #007bff;
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            
            .meta {
                display: flex;
                gap: 20px;
                font-size: 0.9em;
                color: #666;
            }
            
            .toc {
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 30px;
            }
            
            .toc h2 {
                color: #007bff;
                margin-bottom: 15px;
            }
            
            .toc ul {
                list-style: none;
            }
            
            .toc li {
                padding: 8px 0;
                border-bottom: 1px solid #dee2e6;
            }
            
            .toc li a {
                color: #007bff;
                text-decoration: none;
                font-weight: 500;
            }
            
            .toc li a:hover {
                text-decoration: underline;
            }
            
            .content {
                margin-bottom: 40px;
            }
            
            .section {
                margin-bottom: 40px;
                padding: 20px;
                border: 1px solid #dee2e6;
                border-radius: 8px;
            }
            
            .section h2 {
                color: #007bff;
                margin-bottom: 20px;
                font-size: 1.8em;
            }
            
            .chart-container {
                margin: 20px 0;
                padding: 20px;
                background-color: #f8f9fa;
                border-radius: 8px;
            }
            
            .data-table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            
            .data-table th,
            .data-table td {
                border: 1px solid #dee2e6;
                padding: 12px;
                text-align: left;
            }
            
            .data-table th {
                background-color: #007bff;
                color: white;
                font-weight: bold;
            }
            
            .data-table tr:nth-child(even) {
                background-color: #f8f9fa;
            }
            
            .footer {
                text-align: center;
                padding-top: 40px;
                border-top: 1px solid #dee2e6;
                color: #666;
                font-size: 0.9em;
            }
        """
    
    def _generate_toc_html(self, sections: List[ReportSection]) -> str:
        """Generate table of contents HTML."""
        toc_items = []
        for i, section in enumerate(sections, 1):
            toc_items.append(f'<li><a href="#section-{i}">{section.title}</a></li>')
        
        return '\n'.join(toc_items)
    
    def _generate_executive_summary_html(self, report: GeneratedReport) -> str:
        """Generate executive summary HTML."""
        if not report.sections:
            return ""
        
        first_section = report.sections[0]
        summary_html = f"""
        <section class="section" id="executive-summary">
            <h2>Executive Summary</h2>
            <div class="summary-content">
                <p>{first_section.content[:1000]}</p>
                {self._generate_key_metrics_html(report.metadata.get('key_metrics', {}))}
            </div>
        </section>
        """
        
        return summary_html
    
    def _generate_key_metrics_html(self, key_metrics: Dict) -> str:
        """Generate key metrics HTML."""
        if not key_metrics:
            return ""
        
        metrics_html = '<div class="key-metrics"><h3>Key Metrics</h3><div class="metrics-grid">'
        
        for metric, value in key_metrics.items():
            metrics_html += f"""
            <div class="metric-card">
                <div class="metric-label">{metric}</div>
                <div class="metric-value">{value}</div>
            </div>
            """
        
        metrics_html += '</div></div>'
        
        return metrics_html
    
    def _generate_sections_html(self, sections: List[ReportSection]) -> str:
        """Generate sections HTML."""
        sections_html = ""
        
        for i, section in enumerate(sections, 1):
            sections_html += f"""
            <section class="section" id="section-{i}">
                <h2>{section.title}</h2>
                <div class="section-content">
                    <p>{section.content}</p>
                    {self._generate_charts_html(section.charts)}
                    {self._generate_tables_html(section.tables)}
                </div>
            </section>
            """
        
        return sections_html
    
    def _generate_charts_html(self, charts: List[Dict]) -> str:
        """Generate charts HTML."""
        if not charts:
            return ""
        
        charts_html = '<div class="charts-container"><h3>Charts</h3>'
        
        for chart in charts:
            chart_id = f"chart_{chart.get('id', 'unknown')}"
            charts_html += f'<div id="{chart_id}" class="chart-placeholder"></div>'
        
        charts_html += '</div>'
        
        return charts_html
    
    def _generate_tables_html(self, tables: List[Dict]) -> str:
        """Generate data tables HTML."""
        if not tables:
            return ""
        
        tables_html = '<div class="tables-container"><h3>Data Tables</h3>'
        
        for table in tables:
            if table.get('data'):
                table_html = self._create_html_table(table['data'], table.get('title', 'Table'))
                tables_html += table_html
        
        tables_html += '</div>'
        
        return tables_html
    
    def _create_html_table(self, data: List[Dict], title: str) -> str:
        """Create HTML table from data."""
        if not data:
            return ""
        
        # Get headers from first row
        headers = list(data[0].keys()) if data else []
        
        table_html = f'<h4>{title}</h4><table class="data-table"><thead><tr>'
        
        for header in headers:
            table_html += f'<th>{header}</th>'
        
        table_html += '</tr></thead><tbody>'
        
        for row in data:
            table_html += '<tr>'
            for header in headers:
                table_html += f'<td>{row.get(header, "")}</td>'
            table_html += '</tr>'
        
        table_html += '</tbody></table>'
        
        return table_html
    
    def _generate_javascript(self, report: GeneratedReport) -> str:
        """Generate JavaScript for interactive features."""
        js_code = """
        // Chart generation
        function generateCharts() {
            const charts = """ + json.dumps(report.metadata.get('charts', [])) + """;
            
            charts.forEach(chart => {
                const chartId = `chart_${chart.id}`;
                const element = document.getElementById(chartId);
                
                if (element && chart.data) {
                    const plotConfig = {
                        data: chart.data,
                        layout: {
                            title: chart.title,
                            autosize: true,
                            margin: { l: 50, r: 50, t: 50, b: 50 }
                        }
                    };
                    
                    switch(chart.type) {
                        case 'bar':
                            Plotly.newPlot(chartId, [{
                                x: chart.data.map(d => d.x),
                                y: chart.data.map(d => d.y),
                                type: 'bar'
                            }], plotConfig);
                            break;
                        case 'line':
                            Plotly.newPlot(chartId, [{
                                x: chart.data.map(d => d.x),
                                y: chart.data.map(d => d.y),
                                type: 'scatter',
                                mode: 'lines'
                            }], plotConfig);
                            break;
                        case 'pie':
                            Plotly.newPlot(chartId, [{
                                labels: chart.data.map(d => d.label),
                                values: chart.data.map(d => d.value),
                                type: 'pie'
                            }], plotConfig);
                            break;
                    }
                }
            });
        }
        
        // Smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
        
        // Initialize charts on page load
        document.addEventListener('DOMContentLoaded', generateCharts);
        """
        
        return js_code


class ChartGenerator:
    """Chart generation service."""
    
    async def generate_chart(self, config: ChartConfig) -> Dict:
        """
        Generate chart data and configuration.
        
        Args:
            config: Chart configuration
            
        Returns:
            Chart data dictionary
        """
        try:
            if config.type == ChartType.BAR:
                return await self._create_bar_chart(config)
            elif config.type == ChartType.LINE:
                return await self._create_line_chart(config)
            elif config.type == ChartType.PIE:
                return await self._create_pie_chart(config)
            elif config.type == ChartType.SCATTER:
                return await self._create_scatter_chart(config)
            elif config.type == ChartType.HEATMAP:
                return await self._create_heatmap(config)
            else:
                return await self._create_default_chart(config)
                
        except Exception as e:
            logger.error(f"Chart generation failed: {e}")
            return {}
    
    async def _create_bar_chart(self, config: ChartConfig) -> Dict:
        """Create bar chart."""
        data = config.data
        
        if isinstance(data, dict) and 'x' in data and 'y' in data:
            x_data = data['x']
            y_data = data['y']
        else:
            # Assume data is list of dicts
            x_data = [item.get('x', 0) for item in data]
            y_data = [item.get('y', 0) for item in data]
        
        chart_data = [{
            'x': x_data,
            'y': y_data,
            'type': 'bar',
            'name': config.title
        }]
        
        return {
            'id': f"chart_{datetime.utcnow().timestamp()}",
            'type': 'bar',
            'title': config.title,
            'data': chart_data,
            'config': {
                'layout': {
                    'title': config.title,
                    'xaxis': {'title': config.x_axis or 'X Axis'},
                    'yaxis': {'title': config.y_axis or 'Y Axis'}
                }
            }
        }
    
    async def _create_line_chart(self, config: ChartConfig) -> Dict:
        """Create line chart."""
        data = config.data
        
        if isinstance(data, dict) and 'x' in data and 'y' in data:
            x_data = data['x']
            y_data = data['y']
        else:
            x_data = [item.get('x', 0) for item in data]
            y_data = [item.get('y', 0) for item in data]
        
        chart_data = [{
            'x': x_data,
            'y': y_data,
            'type': 'scatter',
            'mode': 'lines',
            'name': config.title
        }]
        
        return {
            'id': f"chart_{datetime.utcnow().timestamp()}",
            'type': 'line',
            'title': config.title,
            'data': chart_data,
            'config': {
                'layout': {
                    'title': config.title,
                    'xaxis': {'title': config.x_axis or 'X Axis'},
                    'yaxis': {'title': config.y_axis or 'Y Axis'}
                }
            }
        }
    
    async def _create_pie_chart(self, config: ChartConfig) -> Dict:
        """Create pie chart."""
        data = config.data
        
        if isinstance(data, list) and len(data) > 0:
            labels = [item.get('label', 'Item') for item in data]
            values = [item.get('value', 0) for item in data]
        else:
            labels = list(data.keys()) if isinstance(data, dict) else []
            values = list(data.values()) if isinstance(data, dict) else []
        
        chart_data = [{
            'labels': labels,
            'values': values,
            'type': 'pie'
        }]
        
        return {
            'id': f"chart_{datetime.utcnow().timestamp()}",
            'type': 'pie',
            'title': config.title,
            'data': chart_data,
            'config': {
                'layout': {
                    'title': config.title
                }
            }
        }
    
    async def _create_scatter_chart(self, config: ChartConfig) -> Dict:
        """Create scatter chart."""
        return await self._create_line_chart(config)  # Similar structure
    
    async def _create_heatmap(self, config: ChartConfig) -> Dict:
        """Create heatmap."""
        data = config.data
        
        return {
            'id': f"chart_{datetime.utcnow().timestamp()}",
            'type': 'heatmap',
            'title': config.title,
            'data': data,
            'config': {
                'layout': {
                    'title': config.title,
                    'xaxis': {'title': config.x_axis or 'X Axis'},
                    'yaxis': {'title': config.y_axis or 'Y Axis'}
                }
            }
        }
    
    async def _create_default_chart(self, config: ChartConfig) -> Dict:
        """Create default chart."""
        return await self._create_bar_chart(config)


class ReportService:
    """Main report generation service."""
    
    def __init__(self):
        self.pdf_generator = PDFGenerator()
        self.excel_generator = ExcelGenerator()
        self.powerpoint_generator = PowerPointGenerator()
        self.html_generator = HTMLGenerator()
        self.chart_generator = ChartGenerator()
        self.llm_service = LLMService()
        
    async def generate_report(self, report_data: Dict, report_type: ReportType, format: ReportFormat) -> GeneratedReport:
        """
        Generate comprehensive report.
        
        Args:
            report_data: Data for report generation
            report_type: Type of report to generate
            format: Output format
            
        Returns:
            Generated report
        """
        try:
            # Generate report content using LLM
            report_content = await self._generate_report_content(report_data, report_type)
            
            # Generate charts
            charts = await self._generate_charts(report_data, report_type)
            
            # Create report sections
            sections = await self._create_sections(report_content, charts)
            
            # Create report object
            report = GeneratedReport(
                id=f"report_{datetime.utcnow().timestamp()}",
                type=report_type,
                format=format,
                title=report_content.get('title', f'{report_type.value.replace("_", " ").title()} Report'),
                sections=sections,
                metadata={
                    'charts': charts,
                    'key_metrics': report_content.get('key_metrics', {}),
                    'generation_time': datetime.utcnow().isoformat()
                }
            )
            
            # Generate file based on format
            if format == ReportFormat.PDF:
                file_bytes = await self.pdf_generator.generate_pdf(report)
                file_path = f"reports/{report.id}.pdf"
                await self._save_file(file_bytes, file_path)
                report.file_path = file_path
                report.file_size = len(file_bytes)
                
            elif format == ReportFormat.EXCEL:
                file_bytes = await self.excel_generator.generate_excel(report)
                file_path = f"reports/{report.id}.xlsx"
                await self._save_file(file_bytes, file_path)
                report.file_path = file_path
                report.file_size = len(file_bytes)
                
            elif format == ReportFormat.HTML:
                html_content = await self.html_generator.generate_html(report)
                file_path = f"reports/{report.id}.html"
                await self._save_file(html_content.encode(), file_path)
                report.file_path = file_path
                report.file_size = len(html_content.encode())
                
            elif format == ReportFormat.POWERPOINT:
                file_bytes = await self.powerpoint_generator.generate_powerpoint(report)
                file_path = f"reports/{report.id}.pptx"
                await self._save_file(file_bytes, file_path)
                report.file_path = file_path
                report.file_size = len(file_bytes)
                
            elif format == ReportFormat.JSON:
                json_content = json.dumps(report.__dict__, default=str, indent=2)
                file_path = f"reports/{report.id}.json"
                await self._save_file(json_content.encode(), file_path)
                report.file_path = file_path
                report.file_size = len(json_content.encode())
            
            return report
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            raise
    
    async def _generate_report_content(self, data: Dict, report_type: ReportType) -> Dict:
        """Generate report content using LLM."""
        try:
            context = ExtractionContext(
                business_context=data
            )
            
            prompt = f"""
            Generate comprehensive {report_type.value.replace("_", " ")} report content:
            
            Data Available:
            {json.dumps(data, indent=2)}
            
            Report Requirements:
            1. Executive summary (2-3 paragraphs)
            2. Key findings with data points
            3. Analysis and insights
            4. Recommendations with action items
            5. Risk factors and mitigation strategies
            6. Success metrics and KPIs
            
            Provide:
            - Report title
            - Section content
            - Key metrics dictionary
            - Chart suggestions (title, type, data description)
            
            Format as JSON with keys: title, sections, key_metrics, chart_suggestions
            """
            
            llm_result = await self.llm_service.generate_response(
                LLMRequest(
                    prompt=prompt,
                    model=ModelType.GPT4_TURBO,
                    temperature=0.2,
                    max_tokens=2000
                )
            )
            
            import json
            return json.loads(llm_result.content)
            
        except Exception as e:
            logger.error(f"Report content generation failed: {e}")
            return {'title': 'Report', 'sections': [], 'key_metrics': {}}
    
    async def _generate_charts(self, data: Dict, report_type: ReportType) -> List[Dict]:
        """Generate charts for report."""
        charts = []
        
        # Report type-specific charts
        if report_type == ReportType.MARKET_ANALYSIS:
            charts.extend([
                await self.chart_generator.generate_chart(ChartConfig(
                    type=ChartType.BAR,
                    title="Market Size Comparison",
                    data=data.get('market_sizes', [])
                )),
                await self.chart_generator.generate_chart(ChartConfig(
                    type=ChartType.PIE,
                    title="Market Share Distribution",
                    data=data.get('market_share', [])
                ))
            ])
        
        elif report_type == ReportType.COMPETITIVE_INTELLIGENCE:
            charts.extend([
                await self.chart_generator.generate_chart(ChartConfig(
                    type=ChartType.SCATTER,
                    title="Competitive Positioning",
                    data=data.get('positioning_data', [])
                )),
                await self.chart_generator.generate_chart(ChartConfig(
                    type=ChartType.BAR,
                    title="Feature Comparison",
                    data=data.get('feature_comparison', [])
                ))
            ])
        
        return charts
    
    async def _create_sections(self, content: Dict, charts: List[Dict]) -> List[ReportSection]:
        """Create report sections."""
        sections = []
        
        for i, section_content in enumerate(content.get('sections', [])):
            section = ReportSection(
                title=section_content.get('title', f'Section {i+1}'),
                content=section_content.get('content', ''),
                charts=[chart for chart in charts if chart.get('section') == i],
                tables=section_content.get('tables', []),
                metadata=section_content.get('metadata', {})
            )
            sections.append(section)
        
        return sections
    
    async def _save_file(self, content: bytes, file_path: str):
        """Save file to disk."""
        try:
            import os
            os.makedirs('reports', exist_ok=True)
            
            with open(file_path, 'wb') as f:
                f.write(content)
                
            logger.info(f"Report saved: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save file {file_path}: {e}")


# Pydantic models for API responses
class ReportGenerationRequest(BaseModel):
    """Request model for report generation."""
    data: Dict
    report_type: ReportType
    format: ReportFormat


class ReportResponse(BaseModel):
    """Response model for generated report."""
    id: str
    type: str
    format: str
    title: str
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    generated_at: datetime
    metadata: Dict


# Error classes
class ReportGenerationError(Exception):
    """Base report generation error."""
    pass


class PDFGenerationError(ReportGenerationError):
    """PDF generation error."""
    pass


class ExcelGenerationError(ReportGenerationError):
    """Excel generation error."""
    pass


class HTMLGenerationError(ReportGenerationError):
    """HTML generation error."""
    pass
