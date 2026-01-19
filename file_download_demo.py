#!/usr/bin/env python3
"""
File Download Location Finder
Shows where downloaded files are stored and demonstrates the download process
"""

import os
import sys
import asyncio
import aiohttp
import aiofiles
import tempfile
from pathlib import Path
from typing import Tuple
from datetime import datetime

class FileDownloadDemo:
    """Demonstrates file download process and shows locations"""
    
    def __init__(self):
        self.session = None
        
        # Test files we downloaded earlier
        self.test_files = {
            "pdf": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            "png": "https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png"
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'Mozilla/5.0 (compatible; File Download Demo)'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def download_file_to_permanent_location(self, url: str, file_type: str) -> Tuple[str, int]:
        """Download file to permanent location"""
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}: {response.reason}")
                
                # Create permanent download directory
                download_dir = os.path.join(os.path.dirname(__file__), "downloaded_files")
                os.makedirs(download_dir, exist_ok=True)
                
                # Generate filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{file_type}_demo_{timestamp}.{file_type}"
                file_path = os.path.join(download_dir, filename)
                
                # Download file
                async with aiofiles.open(file_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        await f.write(chunk)
                
                file_size = os.path.getsize(file_path)
                return file_path, file_size
                
        except Exception as e:
            raise Exception(f"Failed to download {url}: {str(e)}")
    
    async def show_download_process(self):
        """Show the complete download process"""
        print("📁 FILE DOWNLOAD DEMONSTRATION")
        print("=" * 50)
        
        print(f"🗂️  Current working directory: {os.getcwd()}")
        print(f"📂 Raptorflow root: {os.path.dirname(__file__)}")
        
        # Show where temp files were created during testing
        print(f"\n📂 Previous test files were stored in temporary directories:")
        print(f"   📁 Temp directories are automatically cleaned up")
        print(f"   🗑️  Files are deleted when the program exits")
        
        # Download files to permanent location
        print(f"\n📥 Downloading files to permanent location...")
        
        for file_type, url in self.test_files.items():
            try:
                file_path, file_size = await self.download_file_to_permanent_location(url, file_type)
                filename = os.path.basename(file_path)
                
                print(f"✅ Downloaded: {filename}")
                print(f"   📍 Path: {file_path}")
                print(f"   📏 Size: {file_size:,} bytes")
                print(f"   🕒 Downloaded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print()
                
            except Exception as e:
                print(f"❌ Failed to download {file_type}: {str(e)}")
        
        # Show the permanent download directory
        download_dir = os.path.join(os.path.dirname(__file__), "downloaded_files")
        if os.path.exists(download_dir):
            print(f"📂 Permanent download directory: {download_dir}")
            
            # List files in the directory
            files = os.listdir(download_dir)
            if files:
                print(f"📄 Files in directory:")
                for file in files:
                    file_path = os.path.join(download_dir, file)
                    file_size = os.path.getsize(file_path)
                    print(f"   📄 {file} ({file_size:,} bytes)")
            else:
                print(f"📂 Directory is empty")
        
        return download_dir

async def main():
    """Main demonstration"""
    async with FileDownloadDemo() as demo:
        download_dir = await demo.show_download_process()
        
        print("\n" + "=" * 50)
        print("📋 SUMMARY")
        print("=" * 50)
        print(f"📂 Files downloaded to: {download_dir}")
        print(f"📁 These files will remain after the program exits")
        print(f"🔍 You can now test OCR on these downloaded files")
        print(f"📄 Use the file processing tools on these local files")

if __name__ == "__main__":
    asyncio.run(main())
