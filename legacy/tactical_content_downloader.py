#!/usr/bin/env python3
"""
Tactical Content Downloader - Downloads strategic business materials
Tests image understanding on diverse tactical content
"""

import os
import aiohttp
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any
import urllib.parse
from pathlib import Path

class TacticalContentDownloader:
    """Downloads tactical and strategic business content from internet"""
    
    def __init__(self):
        self.download_dir = "tactical_content_test"
        self.session = None
        self.setup_directory()
    
    def setup_directory(self):
        """Create download directory"""
        Path(self.download_dir).mkdir(exist_ok=True)
    
    async def download_file(self, session: aiohttp.ClientSession, url: str, filename: str) -> Dict[str, Any]:
        """Download a single file"""
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.read()
                    filepath = os.path.join(self.download_dir, filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(content)
                    
                    return {
                        "success": True,
                        "url": url,
                        "filename": filename,
                        "filepath": filepath,
                        "size": len(content),
                        "content_type": response.headers.get('content-type', 'unknown')
                    }
                else:
                    return {
                        "success": False,
                        "url": url,
                        "error": f"HTTP {response.status}"
                    }
        except Exception as e:
            return {
                "success": False,
                "url": url,
                "error": str(e)
            }
    
    async def download_tactical_content(self) -> List[Dict[str, Any]]:
        """Download various tactical and strategic content"""
        
        # Tactical content URLs - diverse business materials
        tactical_urls = [
            # Business Strategy Documents
            {
                "url": "https://www.mckinsey.com/featured-insights/mckinsey-on-ai/the-economic-potential-of-generative-ai",
                "category": "business_strategy",
                "description": "McKinsey AI Strategy Report"
            },
            {
                "url": "https://hbr.org/2023/11/the-state-of-ai-in-business",
                "category": "business_intelligence",
                "description": "Harvard Business Review AI Analysis"
            },
            
            # Military/Tactical Diagrams
            {
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Sun_Tzu_art_of_war.jpg/800px-Sun_Tzu_art_of_war.jpg",
                "category": "military_strategy",
                "description": "Sun Tzu Art of War"
            },
            {
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/NATO_Military_Symbol_For_Unit_Size.svg/500px-NATO_Military_Symbol_For_Unit_Size.svg.png",
                "category": "military_symbols",
                "description": "NATO Military Symbols"
            },
            
            # Financial Charts and Analytics
            {
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Stock_chart_pattern.svg/800px-Stock_chart_pattern.svg.png",
                "category": "financial_analysis",
                "description": "Stock Chart Pattern Analysis"
            },
            {
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Market_trend_chart.svg/800px-Market_trend_chart.svg.png",
                "category": "market_trends",
                "description": "Market Trend Analysis Chart"
            },
            
            # Business Process Diagrams
            {
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/SWOT_analysis.svg/800px-SWOT_analysis.svg.png",
                "category": "business_framework",
                "description": "SWOT Analysis Framework"
            },
            {
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/37/Porter_five_forces.svg/800px-Porter_five_forces.svg.png",
                "category": "competitive_analysis",
                "description": "Porter's Five Forces Analysis"
            },
            
            # Technology Architecture
            {
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Cloud_computing_architecture.svg/800px-Cloud_computing_architecture.svg.png",
                "category": "tech_architecture",
                "description": "Cloud Computing Architecture"
            },
            {
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Network_diagram.svg/800px-Network_diagram.svg.png",
                "category": "network_topology",
                "description": "Network Topology Diagram"
            },
            
            # Data Visualization
            {
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Pie_chart.svg/800px-Pie_chart.svg.png",
                "category": "data_visualization",
                "description": "Business Data Pie Chart"
            },
            {
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Bar_chart.svg/800px-Bar_chart.svg.png",
                "category": "data_visualization",
                "description": "Business Data Bar Chart"
            },
            
            # Maps and Geographic Analysis
            {
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/World_map_with_coordinates.svg/800px-World_map_with_coordinates.svg.png",
                "category": "geographic_analysis",
                "description": "World Strategic Map"
            },
            {
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Supply_chain_diagram.svg/800px-Supply_chain_diagram.svg.png",
                "category": "supply_chain",
                "description": "Supply Chain Strategy Diagram"
            },
            
            # Organizational Charts
            {
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Organizational_chart.svg/800px-Organizational_chart.svg.png",
                "category": "organizational_structure",
                "description": "Organizational Structure Chart"
            },
            {
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/Decision_tree.svg/800px-Decision_tree.svg.png",
                "category": "decision_analysis",
                "description": "Strategic Decision Tree"
            }
        ]
        
        async with aiohttp.ClientSession() as session:
            download_tasks = []
            
            for item in tactical_urls:
                # Generate filename from URL
                parsed_url = urllib.parse.urlparse(item["url"])
                original_filename = os.path.basename(parsed_url.path)
                if not original_filename or original_filename == "":
                    original_filename = f"tactical_image_{len(download_tasks)}.png"
                
                # Add timestamp to avoid conflicts
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{item['category']}_{timestamp}_{original_filename}"
                
                task = self.download_file(session, item["url"], filename)
                download_tasks.append(task)
            
            results = await asyncio.gather(*download_tasks, return_exceptions=True)
            
            # Add metadata to results
            final_results = []
            for i, result in enumerate(results):
                if isinstance(result, dict):
                    result.update({
                        "category": tactical_urls[i]["category"],
                        "description": tactical_urls[i]["description"]
                    })
                    final_results.append(result)
                else:
                    final_results.append({
                        "success": False,
                        "error": str(result),
                        "category": tactical_urls[i]["category"],
                        "description": tactical_urls[i]["description"]
                    })
            
            return final_results
    
    def generate_report(self, results: List[Dict[str, Any]]):
        """Generate download report"""
        successful = [r for r in results if r.get("success", False)]
        failed = [r for r in results if not r.get("success", False)]
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_attempts": len(results),
            "successful_downloads": len(successful),
            "failed_downloads": len(failed),
            "success_rate": len(successful) / len(results) * 100 if results else 0,
            "categories": {},
            "files": successful,
            "errors": failed
        }
        
        # Categorize successful downloads
        for file_info in successful:
            category = file_info["category"]
            if category not in report["categories"]:
                report["categories"][category] = []
            report["categories"][category].append(file_info)
        
        return report

async def main():
    """Main execution"""
    print("🎯 TACTICAL CONTENT DOWNLOADER")
    print("=" * 50)
    print("Downloading strategic business materials from internet...")
    
    downloader = TacticalContentDownloader()
    
    # Download tactical content
    results = await downloader.download_tactical_content()
    
    # Generate report
    report = downloader.generate_report(results)
    
    # Save report
    with open('tactical_download_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    # Display summary
    print(f"\n📊 DOWNLOAD SUMMARY")
    print(f"Total Attempts: {report['total_attempts']}")
    print(f"Successful: {report['successful_downloads']}")
    print(f"Failed: {report['failed_downloads']}")
    print(f"Success Rate: {report['success_rate']:.1f}%")
    
    print(f"\n📁 Categories Downloaded:")
    for category, files in report["categories"].items():
        print(f"  📂 {category}: {len(files)} files")
    
    print(f"\n📄 Files Downloaded:")
    for file_info in report["files"]:
        print(f"  ✅ {file_info['filename']} ({file_info['size']:,} bytes) - {file_info['description']}")
    
    if report["errors"]:
        print(f"\n❌ Download Errors:")
        for error in report["errors"]:
            print(f"  ❌ {error['description']}: {error['error']}")
    
    print(f"\n📂 Download Directory: {downloader.download_dir}")
    print(f"📄 Report saved to: tactical_download_report.json")
    
    # Test image understanding on downloaded content
    print(f"\n🧪 TESTING IMAGE UNDERSTANDING ON TACTICAL CONTENT")
    print("=" * 60)
    
    # Import and run image analyzer
    try:
        from advanced_image_understanding import AdvancedImageAnalyzer
        analyzer = AdvancedImageAnalyzer()
        
        analysis_results = {}
        for file_info in report["files"]:
            if file_info["filename"].lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
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
                else:
                    print(f"   ❌ Analysis Failed: {result['error']}")
        
        # Save analysis results
        with open('tactical_content_analysis.json', 'w') as f:
            json.dump(analysis_results, f, indent=2, default=str)
        
        print(f"\n📄 Tactical analysis saved to: tactical_content_analysis.json")
        
    except ImportError:
        print("⚠️  Advanced image analyzer not available")
    except Exception as e:
        print(f"❌ Analysis failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
