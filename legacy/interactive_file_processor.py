#!/usr/bin/env python3
"""
Interactive File Processor Demo
User-friendly interface for downloading and parsing files from URLs
"""

import asyncio
import json
from simple_file_processor import SimpleFileProcessor

async def interactive_demo():
    """Interactive demo for user input"""
    print("🌐 Internet File Processor - Interactive Demo")
    print("=" * 60)
    print("Supported formats: JSON, CSV, XML, HTML, Markdown, YAML, TXT")
    print("Enter URLs to download and parse files")
    print("Type 'quit' or 'exit' to stop")
    print()
    
    async with SimpleFileProcessor() as processor:
        while True:
            url = input("📁 Enter URL: ").strip()
            
            if url.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not url:
                print("❌ Please enter a valid URL")
                continue
            
            if not url.startswith(('http://', 'https://')):
                print("❌ URL must start with http:// or https://")
                continue
            
            print(f"\n🔄 Processing: {url}")
            print("-" * 50)
            
            try:
                result = await processor.process_url(url)
                
                if result.get("status") == "error":
                    print(f"❌ Error: {result.get('error')}")
                    continue
                
                # Show summary
                download_info = result.get("download_info", {})
                parse_result = result.get("parse_result", {})
                
                print(f"✅ File: {download_info.get('filename')}")
                print(f"   Size: {download_info.get('size', 0):,} bytes")
                print(f"   Type: {download_info.get('content_type', 'unknown')}")
                print(f"   Checksum: {download_info.get('checksum', 'unknown')[:16]}...")
                
                status = parse_result.get("status", "unknown")
                if status == "success":
                    print(f"✅ Parsed: {status}")
                    
                    # Show metadata
                    metadata = parse_result.get("metadata", {})
                    if metadata:
                        print("   📊 Metadata:")
                        for key, value in metadata.items():
                            if isinstance(value, (int, float)):
                                print(f"     {key}: {value:,}")
                            else:
                                print(f"     {key}: {value}")
                    
                    # Ask if user wants to see full content
                    show_content = input("\n📄 Show full content? (y/n): ").strip().lower()
                    if show_content in ['y', 'yes']:
                        content = parse_result.get("parsed_content", {})
                        print("\n📄 Full Content:")
                        print("=" * 50)
                        print(json.dumps(content, indent=2, ensure_ascii=False))
                        print("=" * 50)
                    
                    # Ask if user wants to save to file
                    save_file = input("\n💾 Save to file? (y/n): ").strip().lower()
                    if save_file in ['y', 'yes']:
                        filename = input("   Enter filename (without extension): ").strip()
                        if filename:
                            output_file = f"{filename}.json"
                            content = parse_result.get("parsed_content", {})
                            with open(output_file, 'w', encoding='utf-8') as f:
                                json.dump(content, f, indent=2, ensure_ascii=False)
                            print(f"   ✅ Saved to: {output_file}")
                        
                elif status == "unsupported":
                    print(f"⚠️  Unsupported format: {parse_result.get('error')}")
                    print(f"   Supported: {', '.join(processor.supported_formats.keys())}")
                else:
                    print(f"❌ Parse error: {parse_result.get('error')}")
                
            except Exception as e:
                print(f"❌ Processing failed: {str(e)}")
            
            print("\n" + "-" * 50)

async def batch_demo():
    """Batch processing demo"""
    print("🌐 Internet File Processor - Batch Demo")
    print("=" * 60)
    
    # Get multiple URLs
    print("Enter multiple URLs (one per line). Enter empty line to start processing:")
    urls = []
    while True:
        url = input(f"URL {len(urls) + 1}: ").strip()
        if not url:
            break
        if url.startswith(('http://', 'https://')):
            urls.append(url)
        else:
            print("❌ Invalid URL format")
    
    if not urls:
        print("❌ No URLs provided")
        return
    
    print(f"\n🔄 Processing {len(urls)} URLs...")
    print("-" * 50)
    
    async with SimpleFileProcessor() as processor:
        results = []
        for url in urls:
            try:
                result = await processor.process_url(url)
                results.append(result)
                
                # Show quick status
                if result.get("status") == "error":
                    print(f"❌ {url}: {result.get('error')}")
                else:
                    download_info = result.get("download_info", {})
                    parse_result = result.get("parse_result", {})
                    status = parse_result.get("status", "unknown")
                    print(f"✅ {download_info.get('filename')} - {status}")
                    
            except Exception as e:
                print(f"❌ {url}: {str(e)}")
                results.append({"url": url, "status": "error", "error": str(e)})
        
        # Summary
        print("\n📊 Batch Summary:")
        print("-" * 50)
        successful = sum(1 for r in results if r.get("parse_result", {}).get("status") == "success")
        failed = len(results) - successful
        
        print(f"   Total URLs: {len(urls)}")
        print(f"   Successful: {successful}")
        print(f"   Failed: {failed}")
        
        # Ask to save results
        if results:
            save_results = input("\n💾 Save batch results? (y/n): ").strip().lower()
            if save_results in ['y', 'yes']:
                filename = input("   Enter filename (without extension): ").strip()
                if filename:
                    output_file = f"{filename}_batch_results.json"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(results, f, indent=2, ensure_ascii=False)
                    print(f"   ✅ Saved to: {output_file}")

async def main():
    """Main menu"""
    print("🌐 Internet File Processor")
    print("=" * 60)
    print("Choose an option:")
    print("1. Interactive mode (process one URL at a time)")
    print("2. Batch mode (process multiple URLs)")
    print("3. Exit")
    
    while True:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            await interactive_demo()
            break
        elif choice == '2':
            await batch_demo()
            break
        elif choice == '3':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    asyncio.run(main())
