#!/usr/bin/env python3
"""
Business Image Downloader - Downloads real business images from internet
Tests image understanding on actual business content
"""

import os
import requests
from datetime import datetime
import json
from urllib.parse import urlparse
import time

class BusinessImageDownloader:
    """Downloads real business images from internet"""
    
    def __init__(self):
        self.download_dir = "business_images_test"
        os.makedirs(self.download_dir, exist_ok=True)
        
    def download_business_images(self):
        """Download real business images from various sources"""
        
        # Real business image URLs - reliable sources
        business_images = [
            {
                "url": "https://images.unsplash.com/photo-1556761175-5973dc0f32e7?w=800&h=600&fit=crop",
                "category": "business_meeting",
                "description": "Business Meeting in Office",
                "filename": "business_meeting.jpg"
            },
            {
                "url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=600&fit=crop",
                "category": "data_analysis",
                "description": "Data Analysis Dashboard",
                "filename": "data_dashboard.jpg"
            },
            {
                "url": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=800&h=600&fit=crop",
                "category": "office_workspace",
                "description": "Modern Office Workspace",
                "filename": "office_workspace.jpg"
            },
            {
                "url": "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=800&h=600&fit=crop",
                "category": "business_strategy",
                "description": "Business Strategy Session",
                "filename": "strategy_session.jpg"
            },
            {
                "url": "https://images.unsplash.com/photo-1557804506-669a67965ba0?w=800&h=600&fit=crop",
                "category": "finance_trading",
                "description": "Financial Trading Floor",
                "filename": "trading_floor.jpg"
            },
            {
                "url": "https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=800&h=600&fit=crop",
                "category": "technology_office",
                "description": "Technology Office Environment",
                "filename": "tech_office.jpg"
            },
            {
                "url": "https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=800&h=600&fit=crop",
                "category": "corporate_headquarters",
                "description": "Corporate Headquarters Building",
                "filename": "corporate_hq.jpg"
            },
            {
                "url": "https://images.unsplash.com/photo-1551434678-e076c223a692?w=800&h=600&fit=crop",
                "category": "business_presentation",
                "description": "Business Presentation",
                "filename": "presentation.jpg"
            },
            {
                "url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&h=600&fit=crop",
                "category": "retail_store",
                "description": "Modern Retail Store",
                "filename": "retail_store.jpg"
            },
            {
                "url": "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=800&h=600&fit=crop",
                "category": "manufacturing",
                "description": "Manufacturing Facility",
                "filename": "manufacturing.jpg"
            }
        ]
        
        print("🏢 BUSINESS IMAGE DOWNLOADER")
        print("=" * 50)
        print("Downloading real business images from internet...")
        
        downloaded_files = []
        
        for i, item in enumerate(business_images):
            try:
                print(f"\n📥 [{i+1}/{len(business_images)}] Downloading: {item['description']}")
                print(f"    Category: {item['category']}")
                
                # Add user agent to avoid blocking
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                response = requests.get(item["url"], headers=headers, timeout=30)
                
                if response.status_code == 200:
                    # Add timestamp to filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{item['category']}_{timestamp}_{item['filename']}"
                    filepath = os.path.join(self.download_dir, filename)
                    
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
                    print(f"    ✅ Downloaded: {filename} ({len(response.content):,} bytes)")
                else:
                    print(f"    ❌ Failed: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"    ❌ Error: {e}")
            
            # Add delay to avoid rate limiting
            time.sleep(1)
        
        # Save download report
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_downloads": len(downloaded_files),
            "files": downloaded_files
        }
        
        with open('business_images_download_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 DOWNLOAD COMPLETE")
        print(f"Files downloaded: {len(downloaded_files)}")
        print(f"Directory: {self.download_dir}")
        print(f"Report: business_images_download_report.json")
        
        return downloaded_files

def test_image_understanding(downloaded_files):
    """Test image understanding on real business images"""
    try:
        from advanced_image_understanding import AdvancedImageAnalyzer
        
        print(f"\n🧪 TESTING IMAGE UNDERSTANDING ON REAL BUSINESS IMAGES")
        print("=" * 60)
        
        analyzer = AdvancedImageAnalyzer()
        analysis_results = {}
        
        for file_info in downloaded_files:
            if file_info["filename"].lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                filepath = file_info["filepath"]
                print(f"\n🔍 Analyzing: {file_info['description']}")
                print(f"   Category: {file_info['category']}")
                print(f"   File: {file_info['filename']}")
                print(f"   Size: {file_info['size']:,} bytes")
                
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
                    
                    # Show color analysis
                    if result['image_analysis'].get('average_color'):
                        avg_color = result['image_analysis']['average_color']
                        print(f"   🎨 Dominant Color: RGB({int(avg_color[0])}, {int(avg_color[1])}, {int(avg_color[2])})")
                    
                else:
                    print(f"   ❌ Analysis Failed: {result['error']}")
        
        # Save analysis results
        with open('business_images_analysis.json', 'w') as f:
            json.dump(analysis_results, f, indent=2, default=str)
        
        print(f"\n📄 Business images analysis saved to: business_images_analysis.json")
        return analysis_results
        
    except ImportError:
        print("⚠️  Advanced image analyzer not available")
        return {}
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return {}

if __name__ == "__main__":
    # Download business images
    downloader = BusinessImageDownloader()
    files = downloader.download_business_images()
    
    # Test image understanding
    if files:
        test_image_understanding(files)
