# Ausdauer Groups PDF Generator - Working Version
import os
from datetime import datetime

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

def main():
    """Main function to generate PDF"""
    try:
        # Create custom styles
        styles = getSampleStyleSheet()
        styles.add(
            ParagraphStyle(
                name="CustomTitle",
                parent=styles["Title"],
                fontSize=24,
                spaceAfter=30,
                textColor=HexColor("#2C3E50"),
                alignment=1,
            )
        )

        styles.add(
            ParagraphStyle(
                name="CustomHeading",
                parent=styles["Heading1"],
                fontSize=16,
                spaceAfter=12,
                textColor=HexColor("#3498DB"),
                spaceBefore=20,
            )
        )

        styles.add(
            ParagraphStyle(
                name="CustomSubheading",
                parent=styles["Heading2"],
                fontSize=14,
                spaceAfter=8,
                textColor=HexColor("#2980B9"),
                spaceBefore=15,
            )
        )

        # Create PDF document
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"c:/Users/hp/OneDrive/Desktop/Raptorflow/cloud-scraper/Ausdauer_Groups_Report_{timestamp}.pdf"
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )
        story = []

        # Title Page
        story.append(
            Paragraph(
                "AUSDAUER GROUPS - COMPREHENSIVE BUSINESS INTELLIGENCE REPORT",
                styles["CustomTitle"],
            )
        )
        story.append(Spacer(1, 0.3 * inch))

        story.append(
            Paragraph(
                "Multi-Domain Analysis Including Competitive Landscape",
                styles["Normal"],
            )
        )
        story.append(Spacer(1, 0.2 * inch))

        # Build PDF
        doc.build(story)

        # Verify file was created
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print(f"✅ SUCCESS: PDF created at {output_path}")
            print(f"📁 File size: {os.path.getsize(output_path)} bytes")
            return output_path
        else:
            print("❌ PDF file creation failed")
            return None

    except Exception as e:
        print(f"❌ PDF generation error: {str(e)}")
        return None

if __name__ == "__main__":
    result = main() if "main" in globals() else None
