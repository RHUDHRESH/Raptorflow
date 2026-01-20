#!/usr/bin/env python3
"""
Generate Tactical Content - Creates strategic business diagrams and charts
Tests image understanding on locally generated tactical materials
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import json
from datetime import datetime

class TacticalContentGenerator:
    """Generates various tactical and strategic business content"""
    
    def __init__(self):
        self.output_dir = "tactical_content_test"
        os.makedirs(self.output_dir, exist_ok=True)
        
    def create_swot_analysis(self):
        """Create SWOT Analysis diagram"""
        # Create blank canvas
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw SWOT quadrants
        # Strengths (top-left)
        draw.rectangle([50, 50, 380, 280], outline='green', width=3)
        draw.text([200, 60], "STRENGTHS", fill='green', anchor='mt')
        
        # Weaknesses (top-right)
        draw.rectangle([420, 50, 750, 280], outline='red', width=3)
        draw.text([585, 60], "WEAKNESSES", fill='red', anchor='mt')
        
        # Opportunities (bottom-left)
        draw.rectangle([50, 320, 380, 550], outline='blue', width=3)
        draw.text([200, 330], "OPPORTUNITIES", fill='blue', anchor='mt')
        
        # Threats (bottom-right)
        draw.rectangle([420, 320, 750, 550], outline='orange', width=3)
        draw.text([585, 330], "THREATS", fill='orange', anchor='mt')
        
        # Add sample text
        draw.text([200, 150], "• Market Leadership\n• Strong Brand\n• Innovation", fill='darkgreen', anchor='mt')
        draw.text([585, 150], "• Limited Budget\n• Small Team\n• Old Tech", fill='darkred', anchor='mt')
        draw.text([200, 420], "• New Markets\n• Digital Trends\n• Partnerships", fill='darkblue', anchor='mt')
        draw.text([585, 420], "• Competition\n• Regulations\n• Economic Risks", fill='darkorange', anchor='mt')
        
        return img
    
    def create_porter_five_forces(self):
        """Create Porter's Five Forces diagram"""
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        # Central box (Industry Competition)
        draw.rectangle([300, 250, 500, 350], outline='red', width=3, fill='lightcoral')
        draw.text([400, 300], "INDUSTRY\nCOMPETITION", fill='darkred', anchor='mt')
        
        # Threat of New Entrants (top)
        draw.rectangle([300, 50, 500, 150], outline='blue', width=3, fill='lightblue')
        draw.text([400, 100], "THREAT OF\nNEW ENTRANTS", fill='darkblue', anchor='mt')
        draw.line([400, 150, 400, 250], fill='black', width=2)
        
        # Bargaining Power of Suppliers (left)
        draw.rectangle([50, 250, 250, 350], outline='green', width=3, fill='lightgreen')
        draw.text([150, 300], "SUPPLIER\nPOWER", fill='darkgreen', anchor='mt')
        draw.line([250, 300, 300, 300], fill='black', width=2)
        
        # Bargaining Power of Buyers (right)
        draw.rectangle([550, 250, 750, 350], outline='orange', width=3, fill='lightyellow')
        draw.text([650, 300], "BUYER\nPOWER", fill='darkorange', anchor='mt')
        draw.line([500, 300, 550, 300], fill='black', width=2)
        
        # Threat of Substitutes (bottom)
        draw.rectangle([300, 450, 500, 550], outline='purple', width=3, fill='lavender')
        draw.text([400, 500], "THREAT OF\nSUBSTITUTES", fill='darkpurple', anchor='mt')
        draw.line([400, 350, 400, 450], fill='black', width=2)
        
        return img
    
    def create_financial_chart(self):
        """Create financial stock chart"""
        img = Image.new('RGB', (800, 400), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw axes
        draw.line([80, 50, 80, 350], fill='black', width=2)  # Y-axis
        draw.line([80, 350, 750, 350], fill='black', width=2)  # X-axis
        
        # Draw grid lines
        for i in range(5):
            y = 50 + i * 75
            draw.line([80, y, 750, y], fill='lightgray', width=1)
        
        # Draw stock price line (simulated data)
        prices = [100, 120, 115, 140, 135, 160, 155, 180, 175, 200, 195, 220]
        x_points = [80 + i * 55 for i in range(len(prices))]
        y_points = [350 - (price - 80) * 2 for price in prices]
        
        # Draw line
        for i in range(len(x_points) - 1):
            draw.line([x_points[i], y_points[i], x_points[i+1], y_points[i+1]], fill='blue', width=3)
        
        # Draw points
        for x, y in zip(x_points, y_points):
            draw.ellipse([x-3, y-3, x+3, y+3], fill='blue')
        
        # Add labels
        draw.text([400, 20], "STOCK PRICE ANALYSIS", fill='black', anchor='mt')
        draw.text([40, 200], "PRICE", fill='black', anchor='mt')
        draw.text([400, 380], "TIME", fill='black', anchor='mt')
        
        # Add price labels
        for i, price in enumerate([200, 160, 120, 80]):
            y = 350 - (price - 80) * 2
            draw.text([70, y], str(price), fill='black', anchor='rt')
        
        return img
    
    def create_org_chart(self):
        """Create organizational chart"""
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        # CEO box
        draw.rectangle([350, 50, 450, 100], outline='darkblue', width=2, fill='lightblue')
        draw.text([400, 75], "CEO", fill='darkblue', anchor='mt')
        
        # Department heads
        departments = [
            ("CTO", 200, 150),
            ("CFO", 400, 150),
            ("CMO", 600, 150)
        ]
        
        for dept, x, y in departments:
            draw.rectangle([x-50, y-25, x+50, y+25], outline='blue', width=2, fill='lightcyan')
            draw.text([x, y], dept, fill='darkblue', anchor='mt')
            # Connect to CEO
            draw.line([400, 100, x, y-25], fill='black', width=1)
        
        # Team members
        teams = [
            ("Dev Team", 150, 250, 200, 150),
            ("QA Team", 250, 250, 200, 150),
            ("Accounting", 350, 250, 400, 150),
            ("Finance", 450, 250, 400, 150),
            ("Sales", 550, 250, 600, 150),
            ("Marketing", 650, 250, 600, 150)
        ]
        
        for team, x, y, parent_x, parent_y in teams:
            draw.rectangle([x-40, y-20, x+40, y+20], outline='gray', width=1, fill='lightgray')
            draw.text([x, y], team, fill='black', anchor='mt')
            # Connect to department
            draw.line([parent_x, parent_y+25, x, y-20], fill='black', width=1)
        
        return img
    
    def create_decision_tree(self):
        """Create strategic decision tree"""
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        # Root decision
        draw.rectangle([350, 50, 450, 100], outline='darkgreen', width=2, fill='lightgreen')
        draw.text([400, 75], "Market\nEntry?", fill='darkgreen', anchor='mt')
        
        # First level branches
        # Yes branch
        draw.rectangle([200, 150, 300, 200], outline='green', width=2, fill='lightcyan')
        draw.text([250, 175], "YES", fill='darkgreen', anchor='mt')
        draw.line([400, 100, 250, 150], fill='black', width=2)
        
        # No branch
        draw.rectangle([500, 150, 600, 200], outline='red', width=2, fill='lightcoral')
        draw.text([550, 175], "NO", fill='darkred', anchor='mt')
        draw.line([400, 100, 550, 150], fill='black', width=2)
        
        # Second level (Yes branch)
        draw.rectangle([100, 250, 200, 300], outline='blue', width=2, fill='lightblue')
        draw.text([150, 275], "High\nInvestment", fill='darkblue', anchor='mt')
        draw.line([250, 200, 150, 250], fill='black', width=1)
        
        draw.rectangle([300, 250, 400, 300], outline='blue', width=2, fill='lightblue')
        draw.text([350, 275], "Low\nInvestment", fill='darkblue', anchor='mt')
        draw.line([250, 200, 350, 250], fill='black', width=1)
        
        # Second level (No branch)
        draw.rectangle([450, 250, 550, 300], outline='orange', width=2, fill='lightyellow')
        draw.text([500, 275], "Focus\nDomestic", fill='darkorange', anchor='mt')
        draw.line([550, 200, 500, 250], fill='black', width=1)
        
        draw.rectangle([600, 250, 700, 300], outline='orange', width=2, fill='lightyellow')
        draw.text([650, 275], "Explore\nOther", fill='darkorange', anchor='mt')
        draw.line([550, 200, 650, 250], fill='black', width=1)
        
        # Outcomes
        outcomes = [
            ("High Risk\nHigh Return", 150, 350),
            ("Low Risk\nModest Return", 350, 350),
            ("Stable\nGrowth", 500, 350),
            ("Strategic\nReview", 650, 350)
        ]
        
        for outcome, x, y in outcomes:
            draw.rectangle([x-50, y-25, x+50, y+25], outline='purple', width=2, fill='lavender')
            draw.text([x, y], outcome, fill='darkpurple', anchor='mt')
            # Connect lines
            if x == 150:
                draw.line([150, 300, 150, 325], fill='black', width=1)
            elif x == 350:
                draw.line([350, 300, 350, 325], fill='black', width=1)
            elif x == 500:
                draw.line([500, 300, 500, 325], fill='black', width=1)
            elif x == 650:
                draw.line([650, 300, 650, 325], fill='black', width=1)
        
        return img
    
    def create_supply_chain_diagram(self):
        """Create supply chain diagram"""
        img = Image.new('RGB', (800, 400), color='white')
        draw = ImageDraw.Draw(img)
        
        # Supply chain stages
        stages = [
            ("Suppliers", 100, 200),
            ("Manufacturing", 250, 200),
            ("Distribution", 400, 200),
            ("Retail", 550, 200),
            ("Customers", 700, 200)
        ]
        
        # Draw boxes and connections
        for i, (stage, x, y) in enumerate(stages):
            # Draw box
            draw.rectangle([x-40, y-30, x+40, y+30], outline='blue', width=2, fill='lightblue')
            draw.text([x, y], stage, fill='darkblue', anchor='mt')
            
            # Draw arrows
            if i < len(stages) - 1:
                next_x = stages[i+1][1]
                # Arrow line
                draw.line([x+40, y, next_x-40, y], fill='black', width=2)
                # Arrow head
                draw.polygon([next_x-40, y-5, next_x-40, y+5, next_x-30, y], fill='black')
        
        # Add information flow (dashed lines)
        info_flow = [
            ("Orders", 100, 100),
            ("Inventory", 250, 100),
            ("Shipments", 400, 100),
            ("Sales", 550, 100),
            ("Feedback", 700, 100)
        ]
        
        for i, (info, x, y) in enumerate(info_flow):
            draw.text([x, y], info, fill='gray', anchor='mt')
            if i < len(info_flow) - 1:
                next_x = info_flow[i+1][1]
                # Dashed line
                for j in range(x+40, next_x-40, 10):
                    draw.line([j, y, j+5, y], fill='gray', width=1)
        
        return img
    
    def generate_all_tactical_content(self):
        """Generate all tactical content"""
        print("🎯 GENERATING TACTICAL CONTENT")
        print("=" * 40)
        
        content_generators = [
            ("SWOT Analysis", self.create_swot_analysis, "business_framework"),
            ("Porter's Five Forces", self.create_porter_five_forces, "competitive_analysis"),
            ("Financial Stock Chart", self.create_financial_chart, "financial_analysis"),
            ("Organizational Chart", self.create_org_chart, "organizational_structure"),
            ("Strategic Decision Tree", self.create_decision_tree, "decision_analysis"),
            ("Supply Chain Diagram", self.create_supply_chain_diagram, "supply_chain")
        ]
        
        generated_files = []
        
        for name, generator, category in content_generators:
            try:
                print(f"📊 Creating: {name}")
                
                # Generate image
                img = generator()
                
                # Save with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{category}_{timestamp}_{name.lower().replace(' ', '_').replace('\'', '')}.png"
                filepath = os.path.join(self.output_dir, filename)
                
                img.save(filepath, 'PNG')
                
                file_info = {
                    "filename": filename,
                    "filepath": filepath,
                    "size": os.path.getsize(filepath),
                    "category": category,
                    "description": name,
                    "success": True
                }
                
                generated_files.append(file_info)
                print(f"   ✅ Saved: {filename}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Save generation report
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_generated": len(generated_files),
            "files": generated_files
        }
        
        with open('tactical_content_generation_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 GENERATION COMPLETE")
        print(f"Files generated: {len(generated_files)}")
        print(f"Directory: {self.output_dir}")
        print(f"Report: tactical_content_generation_report.json")
        
        return generated_files

def test_image_understanding(generated_files):
    """Test image understanding on generated tactical content"""
    try:
        from advanced_image_understanding import AdvancedImageAnalyzer
        
        print(f"\n🧪 TESTING IMAGE UNDERSTANDING ON TACTICAL CONTENT")
        print("=" * 60)
        
        analyzer = AdvancedImageAnalyzer()
        analysis_results = {}
        
        for file_info in generated_files:
            filepath = file_info["filepath"]
            print(f"\n🔍 Analyzing: {file_info['description']}")
            print(f"   Category: {file_info['category']}")
            print(f"   File: {file_info['filename']}")
            
            result = analyzer.analyze_image(filepath)
            analysis_results[file_info["filename"]] = result
            
            if "error" not in result:
                print(f"   ✅ Analysis Complete")
                print(f"   📊 Image Type: {result['image_analysis'].get('image_type', 'unknown')}")
                print(f"   🎯 Business Context: {result['business_context'].get('content_type', 'unknown')}")
                print(f"   📈 Industry Relevance: {result['business_context'].get('industry_relevance', 0):.1%}")
                semantic_tags = result.get('semantic_analysis', {}).get('semantic_tags', [])
                print(f"   🧠 Semantic Tags: {', '.join(semantic_tags)}")
                
                # Show additional insights
                if result['image_analysis'].get('quality_metrics'):
                    quality = result['image_analysis']['quality_metrics']
                    print(f"   📏 Quality Score: {quality.get('overall_quality', 0):.1f}/100")
                
                # Show business categories
                if result['business_context'].get('business_categories'):
                    categories = result['business_context']['business_categories']
                    print(f"   🏢 Business Categories: {', '.join(categories)}")
                
                # Show visual features
                if result['image_analysis'].get('edge_density'):
                    edge_density = result['image_analysis']['edge_density']
                    print(f"   🔲 Edge Density: {edge_density:.2%}")
                
            else:
                print(f"   ❌ Analysis Failed: {result['error']}")
        
        # Save analysis results
        with open('tactical_content_analysis.json', 'w') as f:
            json.dump(analysis_results, f, indent=2, default=str)
        
        print(f"\n📄 Tactical analysis saved to: tactical_content_analysis.json")
        return analysis_results
        
    except ImportError:
        print("⚠️  Advanced image analyzer not available")
        return {}
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return {}

if __name__ == "__main__":
    # Generate tactical content
    generator = TacticalContentGenerator()
    files = generator.generate_all_tactical_content()
    
    # Test image understanding
    if files:
        test_image_understanding(files)
