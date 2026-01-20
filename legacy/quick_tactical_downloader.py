#!/usr/bin/env python3
"""
Quick Tactical Content Downloader - Fast download of strategic materials
"""

import os
import requests
from datetime import datetime
from urllib.parse import urlparse
import json

def download_tactical_content():
    """Download tactical content quickly"""
    
    # Tactical content URLs - reliable sources
    tactical_urls = [
        {
            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Sun_Tzu_art_of_war.jpg/800px-Sun_Tzu_art_of_war.jpg",
            "category": "military_strategy",
            "description": "Sun Tzu Art of War",
            "filename": "sun_tzu_art_of_war.jpg"
        },
        {
            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/SWOT_analysis.svg/800px-SWOT_analysis.svg.png",
            "category": "business_framework",
            "description": "SWOT Analysis Framework",
            "filename": "swot_analysis.png"
        },
        {
            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/37/Porter_five_forces.svg/800px-Porter_five_forces.svg.png",
            "category": "competitive_analysis",
            "description": "Porter's Five Forces Analysis",
            "filename": "porter_five_forces.png"
        },
        {
            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Cloud_computing_architecture.svg/800px-Cloud_computing_architecture.svg.png",
            "category": "tech_architecture",
            "description": "Cloud Computing Architecture",
            "filename": "cloud_architecture.png"
        },
        {
            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Pie_chart.svg/800px-Pie_chart.svg.png",
            "category": "data_visualization",
            "description": "Business Data Pie Chart",
            "filename": "pie_chart.png"
        },
        {
            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Bar_chart.svg/800px-Bar_chart.svg.png",
            "category": "data_visualization",
            "description": "Business Data Bar Chart",
            "filename": "bar_chart.png"
        },
        {
            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Stock_chart_pattern.svg/800px-Stock_chart_pattern.svg.png",
            "category": "financial_analysis",
            "description": "Stock Chart Pattern Analysis",
            "filename": "stock_chart.png"
        },
        {
            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Organizational_chart.svg/800px-Organizational_chart.svg.png",
            "category": "organizational_structure",
            "description": "Organizational Structure Chart",
            "filename": "org_chart.png"
        },
        {
            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/Decision_tree.svg/800px-Decision_tree.svg.png",
            "category": "decision_analysis",
            "description": "Strategic Decision Tree",
            "filename": "decision_tree.png"
        },
        {
            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Supply_chain_diagram.svg/800px-Supply_chain_diagram.svg.png",
            "category": "supply_chain",
            "description": "Supply Chain Strategy Diagram",
            "filename": "supply_chain.png"
        }
    ]
    
    # Create download directory
    download_dir = "tactical_content_test"
    os.makedirs(download_dir, exist_ok=True)
    
    print("🎯 QUICK TACTICAL CONTENT DOWNLOADER")
    print("=" * 50)
    
    downloaded_files = []
    
    for item in tactical_urls:
        try:
            print(f"📥 Downloading: {item['description']}")
            
            response = requests.get(item["url"], timeout=30)
            if response.status_code == 200:
                # Add timestamp to filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_{item['filename']}"
                filepath = os.path.join(download_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                file_info = {
                    "filename": filename,
                    "filepath": filepath,
                    "size": len(response.content),
                    "category": item["category"],
                    "description": item["description"],
                    "url": item["url"],
                    "success": True
                }
                
                downloaded_files.append(file_info)
                print(f"   ✅ Downloaded: {filename} ({len(response.content):,} bytes)")
            else:
                print(f"   ❌ Failed: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Save download report
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_downloads": len(downloaded_files),
        "files": downloaded_files
    }
    
    with open('quick_tactical_download_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📊 DOWNLOAD COMPLETE")
    print(f"Files downloaded: {len(downloaded_files)}")
    print(f"Directory: {download_dir}")
    print(f"Report: quick_tactical_download_report.json")
    
    return downloaded_files

def test_image_understanding(downloaded_files):
    """Test image understanding on tactical content"""
    try:
        from advanced_image_understanding import AdvancedImageAnalyzer
        
        print(f"\n🧪 TESTING IMAGE UNDERSTANDING ON TACTICAL CONTENT")
        print("=" * 60)
        
        analyzer = AdvancedImageAnalyzer()
        analysis_results = {}
        
        for file_info in downloaded_files:
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
                    
                    # Show additional insights
                    if result['image_analysis'].get('quality_metrics'):
                        quality = result['image_analysis']['quality_metrics']
                        print(f"   📏 Quality Score: {quality.get('overall_quality', 0):.1f}/100")
                    
                    # Show business categories
                    if result['business_context'].get('business_categories'):
                        categories = result['business_context']['business_categories']
                        print(f"   🏢 Business Categories: {', '.join(categories)}")
                        
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
    # Download tactical content
    files = download_tactical_content()
    
    # Test image understanding
    if files:
        test_image_understanding(files)
