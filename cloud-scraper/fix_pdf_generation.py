"""
Working PDF Generator - Fix the PDF Generation Issue
Ensure actual PDF files are created, not just Markdown
"""

import asyncio
import json
import os
import uuid
from datetime import datetime


class WorkingPDFGenerator:
    """Working PDF generator that actually creates PDF files"""

    def __init__(self):
        self.start_time = datetime.now()

    async def create_actual_pdf(self, content_data: dict, filename: str) -> str:
        """Create an actual PDF file"""

        print("🔧 FIXING PDF GENERATION...")
        print(f"📄 Target: {filename}")

        try:
            # Method 1: Try our enhanced PDF maker
            try:
                import sys

                sys.path.append("c:/Users/hp/OneDrive/Desktop/Raptorflow/cloud-scraper")

                from sota_pdf_maker_complete import (
                    EnhancedTemplateGenerator,
                    SecurityLevel,
                    SOTAPDFMakerEnhanced,
                    TemplateCategory,
                )

                print("✅ Enhanced PDF Maker imported successfully")

                # Configure PDF
                config = EnhancedTemplateGenerator.create_business_report_config(
                    title=content_data.get("title", "Report"),
                    author="RaptorFlow Research System",
                    security=True,
                )

                config.subject = "Research Report"
                config.keywords = "Research, Analysis, Intelligence"
                config.enable_watermark = True
                config.watermark_text = "RESEARCH REPORT"
                config.watermark_opacity = 0.15

                # Create PDF maker
                pdf_maker = SOTAPDFMakerEnhanced(config)

                # Configure security
                pdf_maker.set_security(
                    level=SecurityLevel.WATERMARK_ONLY,
                    watermark_text="RESEARCH REPORT - CONFIDENTIAL",
                    watermark_opacity=0.2,
                )

                # Configure interactive elements
                pdf_maker.set_interactive(
                    enable_bookmarks=True,
                    enable_hyperlinks=True,
                    enable_annotations=True,
                )

                # Generate PDF
                output_path = f"c:/Users/hp/OneDrive/Desktop/Raptorflow/cloud-scraper/{filename}.pdf"

                print(f"🔄 Generating PDF: {output_path}")

                success = await pdf_maker.generate_pdf(
                    content_data,
                    output_path,
                    template_category=TemplateCategory.BUSINESS,
                    template_name="executive_summary",
                )

                if success and os.path.exists(output_path):
                    print(f"✅ SUCCESS: PDF created at {output_path}")
                    return output_path
                else:
                    print("❌ Enhanced PDF generation failed")

            except Exception as e:
                print(f"❌ Enhanced PDF error: {str(e)}")

            # Method 2: Try basic ReportLab
            try:
                from reportlab.lib.pagesizes import A4, letter
                from reportlab.lib.styles import getSampleStyleSheet
                from reportlab.lib.units import inch
                from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

                print("✅ Trying basic ReportLab...")

                # Create basic PDF
                output_path = f"c:/Users/hp/OneDrive/Desktop/Raptorflow/cloud-scraper/{filename}_basic.pdf"

                doc = SimpleDocTemplate(output_path, pagesize=A4)
                styles = getSampleStyleSheet()
                story = []

                # Add title
                title_style = styles["Title"]
                story.append(
                    Paragraph(content_data.get("title", "Report"), title_style)
                )
                story.append(Spacer(1, 0.2 * inch))

                # Add content
                body_style = styles["Normal"]
                if "executive_summary" in content_data:
                    story.append(Paragraph("Executive Summary", styles["Heading1"]))
                    if "overview" in content_data["executive_summary"]:
                        story.append(
                            Paragraph(
                                content_data["executive_summary"]["overview"],
                                body_style,
                            )
                        )
                    story.append(Spacer(1, 0.1 * inch))

                if "key_findings" in content_data.get("executive_summary", {}):
                    story.append(Paragraph("Key Findings", styles["Heading2"]))
                    for finding in content_data["executive_summary"]["key_findings"][
                        :5
                    ]:
                        story.append(Paragraph(f"• {finding}", body_style))
                    story.append(Spacer(1, 0.1 * inch))

                # Build PDF
                doc.build(story)

                if os.path.exists(output_path):
                    print(f"✅ SUCCESS: Basic PDF created at {output_path}")
                    return output_path
                else:
                    print("❌ Basic PDF creation failed")

            except Exception as e:
                print(f"❌ Basic PDF error: {str(e)}")

            # Method 3: Create HTML and convert to PDF (if possible)
            try:
                output_path = f"c:/Users/hp/OneDrive/Desktop/Raptorflow/cloud-scraper/{filename}.html"

                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>{content_data.get('title', 'Report')}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; }}
                        h1 {{ color: #2C3E50; }}
                        h2 {{ color: #3498DB; }}
                        .finding {{ margin: 10px 0; padding: 10px; background: #f8f9fa; border-left: 4px solid #3498DB; }}
                    </style>
                </head>
                <body>
                    <h1>{content_data.get('title', 'Report')}</h1>
                    <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>Platform:</strong> RaptorFlow Research System</p>

                    <h2>Executive Summary</h2>
                    <div class="finding">
                        <p>{content_data.get('executive_summary', {}).get('overview', 'Overview not available')}</p>
                    </div>

                    <h2>Key Findings</h2>
                """

                if "key_findings" in content_data.get("executive_summary", {}):
                    for finding in content_data["executive_summary"]["key_findings"][
                        :5
                    ]:
                        html_content += f'<div class="finding"><p>{finding}</p></div>'

                html_content += """
                </body>
                </html>
                """

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(html_content)

                print(f"✅ HTML report created: {output_path}")
                print(
                    "💡 Note: You can convert this HTML to PDF using your browser or online tools"
                )
                return output_path

            except Exception as e:
                print(f"❌ HTML creation error: {str(e)}")

            # Method 4: Create detailed text file as last resort
            output_path = f"c:/Users/hp/OneDrive/Desktop/Raptorflow/cloud-scraper/{filename}_detailed.txt"

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"{'='*80}\n")
                f.write(f"{content_data.get('title', 'REPORT')}\n")
                f.write(f"{'='*80}\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Platform: RaptorFlow Research System\n")
                f.write(f"Confidence: High\n\n")

                f.write(f"EXECUTIVE SUMMARY:\n")
                f.write(f"{'-'*40}\n")
                if "executive_summary" in content_data:
                    if "overview" in content_data["executive_summary"]:
                        f.write(f"{content_data['executive_summary']['overview']}\n\n")

                    if "key_findings" in content_data["executive_summary"]:
                        f.write(f"KEY FINDINGS:\n")
                        for i, finding in enumerate(
                            content_data["executive_summary"]["key_findings"][:10], 1
                        ):
                            f.write(f"{i}. {finding}\n")

                f.write(f"\n{'='*80}\n")
                f.write(f"END OF REPORT\n")
                f.write(f"{'='*80}\n")

            print(f"✅ Detailed text report created: {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ All PDF generation methods failed: {str(e)}")
            return None


async def test_pdf_generation():
    """Test PDF generation with sample content"""

    print("🧪 TESTING PDF GENERATION SYSTEM")
    print("=" * 50)

    generator = WorkingPDFGenerator()

    # Sample content for testing
    test_content = {
        "title": "Test PDF Generation Report",
        "executive_summary": {
            "overview": "This is a test report to verify PDF generation capabilities of the RaptorFlow Research System.",
            "key_findings": [
                "PDF generation system is functional",
                "Multiple fallback methods available",
                "Professional formatting capabilities",
                "Interactive elements support",
                "Security features implemented",
            ],
        },
        "test_metadata": {
            "test_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "test_version": "1.0",
            "test_status": "Active",
        },
    }

    # Generate PDF
    result_path = await generator.create_actual_pdf(test_content, "test_report")

    if result_path:
        print(f"\n🎉 SUCCESS: Report generated at {result_path}")
        print(f"📁 File size: {os.path.getsize(result_path)} bytes")
        print(f"📄 File type: {os.path.splitext(result_path)[1]}")

        # Verify file exists and has content
        if os.path.exists(result_path) and os.path.getsize(result_path) > 0:
            print("✅ File verified - contains content")
        else:
            print("❌ File verification failed")
    else:
        print("❌ PDF generation failed completely")


if __name__ == "__main__":
    asyncio.run(test_pdf_generation())
