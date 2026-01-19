#!/usr/bin/env python3
"""
Simple Internet File Downloader and Parser
Downloads files from URLs and parses various formats without backend dependencies
"""

import os
import sys
import asyncio
import aiohttp
import aiofiles
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse
import hashlib
import json
import csv
from dataclasses import dataclass

@dataclass
class FileInfo:
    """Information about downloaded file"""
    url: str
    filename: str
    file_path: str
    content_type: str
    size: int
    checksum: str
    downloaded_at: str

class SimpleFileProcessor:
    """Downloads and parses files from internet URLs"""
    
    def __init__(self, download_dir: Optional[str] = None):
        self.download_dir = download_dir or tempfile.mkdtemp(prefix="file_processor_")
        self.session = None
        self.supported_formats = {
            '.txt': self._parse_text,
            '.json': self._parse_json,
            '.csv': self._parse_csv,
            '.xml': self._parse_xml,
            '.html': self._parse_html,
            '.htm': self._parse_html,
            '.md': self._parse_markdown,
            '.yaml': self._parse_yaml,
            '.yml': self._parse_yaml,
            '.log': self._parse_text,
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'Mozilla/5.0 (compatible; Raptorflow FileProcessor)'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _get_filename_from_url(self, url: str, content_type: str = "") -> str:
        """Generate filename from URL and content type"""
        parsed = urlparse(url)
        original_name = os.path.basename(parsed.path)
        
        if original_name and '.' in original_name:
            return original_name
        
        # Generate filename based on content type
        content_type_map = {
            'text/plain': '.txt',
            'application/json': '.json',
            'text/csv': '.csv',
            'application/xml': '.xml',
            'text/html': '.html',
            'text/markdown': '.md',
        }
        
        ext = content_type_map.get(content_type, '.txt')
        domain = parsed.netloc.replace('.', '_')
        return f"{domain}_file{ext}"
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA256 checksum of file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    async def download_file(self, url: str) -> FileInfo:
        """Download file from URL"""
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}: {response.reason}")
                
                # Get content info
                content_type = response.headers.get('content-type', '').split(';')[0]
                
                # Generate filename
                filename = self._get_filename_from_url(url, content_type)
                file_path = os.path.join(self.download_dir, filename)
                
                # Download file
                async with aiofiles.open(file_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        await f.write(chunk)
                
                # Get file info
                file_size = os.path.getsize(file_path)
                checksum = self._calculate_checksum(file_path)
                
                return FileInfo(
                    url=url,
                    filename=filename,
                    file_path=file_path,
                    content_type=content_type,
                    size=file_size,
                    checksum=checksum,
                    downloaded_at=str(asyncio.get_event_loop().time())
                )
                
        except Exception as e:
            raise Exception(f"Failed to download {url}: {str(e)}")
    
    async def parse_file(self, file_info: FileInfo) -> Dict[str, Any]:
        """Parse downloaded file based on its type"""
        file_ext = Path(file_info.filename).suffix.lower()
        
        if file_ext not in self.supported_formats:
            return {
                "status": "unsupported",
                "error": f"Unsupported file format: {file_ext}",
                "supported_formats": list(self.supported_formats.keys())
            }
        
        try:
            parser_func = self.supported_formats[file_ext]
            parsed_content = await parser_func(file_info.file_path)
            
            return {
                "status": "success",
                "file_info": {
                    "filename": file_info.filename,
                    "content_type": file_info.content_type,
                    "size": file_info.size,
                    "checksum": file_info.checksum
                },
                "parsed_content": parsed_content,
                "metadata": self._extract_metadata(file_info, parsed_content)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to parse {file_info.filename}: {str(e)}",
                "file_info": {
                    "filename": file_info.filename,
                    "content_type": file_info.content_type
                }
            }
    
    def _extract_metadata(self, file_info: FileInfo, content: Any) -> Dict[str, Any]:
        """Extract metadata from parsed content"""
        metadata = {
            "file_type": Path(file_info.filename).suffix,
            "content_type": file_info.content_type,
            "size_bytes": file_info.size,
            "checksum": file_info.checksum
        }
        
        # Add content-specific metadata
        if isinstance(content, dict):
            if "data" in content and isinstance(content["data"], list):
                metadata["record_count"] = len(content["data"])
            elif isinstance(content, dict):
                metadata["key_count"] = len(content.keys())
        elif isinstance(content, list):
            metadata["record_count"] = len(content)
        elif isinstance(content, str):
            metadata["character_count"] = len(content)
            metadata["line_count"] = content.count('\n') + 1
            metadata["word_count"] = len(content.split())
        
        return metadata
    
    async def _parse_text(self, file_path: str) -> str:
        """Parse plain text file"""
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            return await f.read()
    
    async def _parse_json(self, file_path: str) -> Dict[str, Any]:
        """Parse JSON file"""
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
            return json.loads(content)
    
    async def _parse_csv(self, file_path: str) -> Dict[str, Any]:
        """Parse CSV file"""
        data = []
        headers = []
        
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
            
        lines = content.split('\n')
        if lines:
            reader = csv.DictReader(lines)
            headers = reader.fieldnames or []
            data = [dict(row) for row in reader if row]
        
        return {
            "headers": headers,
            "data": data,
            "row_count": len(data)
        }
    
    async def _parse_xml(self, file_path: str) -> Dict[str, Any]:
        """Parse XML file"""
        try:
            import xml.etree.ElementTree as ET
            
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            root = ET.fromstring(content)
            
            def element_to_dict(element):
                result = {}
                if element.text and element.text.strip():
                    result['text'] = element.text.strip()
                
                if element.attrib:
                    result['attributes'] = element.attrib
                
                children = {}
                for child in element:
                    child_data = element_to_dict(child)
                    if child.tag in children:
                        if not isinstance(children[child.tag], list):
                            children[child.tag] = [children[child.tag]]
                        children[child.tag].append(child_data)
                    else:
                        children[child.tag] = child_data
                
                if children:
                    result['children'] = children
                
                return result
            
            return {
                "root_tag": root.tag,
                "structure": element_to_dict(root)
            }
            
        except Exception as e:
            return {"error": f"XML parsing failed: {str(e)}"}
    
    async def _parse_html(self, file_path: str) -> Dict[str, Any]:
        """Parse HTML file"""
        try:
            from bs4 import BeautifulSoup
            
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract basic information
            title = soup.title.string if soup.title else ""
            headings = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
            links = [a.get('href') for a in soup.find_all('a', href=True)]
            images = [img.get('src') for img in soup.find_all('img', src=True)]
            
            # Extract text content
            text_content = soup.get_text(separator=' ', strip=True)
            
            return {
                "title": title,
                "headings": headings,
                "links": links,
                "images": images,
                "text_content": text_content,
                "metadata": {
                    "link_count": len(links),
                    "image_count": len(images),
                    "heading_count": len(headings)
                }
            }
            
        except ImportError:
            # Fallback to basic text extraction
            return await self._parse_text(file_path)
        except Exception as e:
            return {"error": f"HTML parsing failed: {str(e)}"}
    
    async def _parse_markdown(self, file_path: str) -> Dict[str, Any]:
        """Parse Markdown file"""
        try:
            import markdown
            from bs4 import BeautifulSoup
            
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            # Convert markdown to HTML
            html = markdown.markdown(content)
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract structured information
            headings = []
            for level in range(1, 7):
                for h in soup.find_all(f'h{level}'):
                    headings.append({
                        'level': level,
                        'text': h.get_text(strip=True)
                    })
            
            # Extract links
            links = []
            for a in soup.find_all('a', href=True):
                links.append({
                    'text': a.get_text(strip=True),
                    'href': a.get('href')
                })
            
            return {
                "original_markdown": content,
                "html_content": html,
                "headings": headings,
                "links": links,
                "metadata": {
                    "heading_count": len(headings),
                    "link_count": len(links),
                    "character_count": len(content)
                }
            }
            
        except ImportError:
            # Fallback to plain text
            content = await self._parse_text(file_path)
            return {"original_markdown": content, "fallback": True}
        except Exception as e:
            return {"error": f"Markdown parsing failed: {str(e)}"}
    
    async def _parse_yaml(self, file_path: str) -> Dict[str, Any]:
        """Parse YAML file"""
        try:
            import yaml
            
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            return yaml.safe_load(content)
            
        except ImportError:
            return {"error": "PyYAML not installed"}
        except Exception as e:
            return {"error": f"YAML parsing failed: {str(e)}"}
    
    async def process_url(self, url: str) -> Dict[str, Any]:
        """Complete workflow: download and parse file from URL"""
        try:
            # Download file
            file_info = await self.download_file(url)
            
            # Parse file
            parsed_result = await self.parse_file(file_info)
            
            return {
                "url": url,
                "download_info": {
                    "filename": file_info.filename,
                    "size": file_info.size,
                    "content_type": file_info.content_type,
                    "checksum": file_info.checksum,
                    "downloaded_at": file_info.downloaded_at
                },
                "parse_result": parsed_result
            }
            
        except Exception as e:
            return {
                "url": url,
                "status": "error",
                "error": str(e)
            }

# CLI Interface
async def main():
    """Command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Download and parse files from URLs')
    parser.add_argument('urls', nargs='+', help='URLs to process')
    parser.add_argument('--output', '-o', help='Output directory for results')
    parser.add_argument('--format', '-f', choices=['json', 'text'], default='json', help='Output format')
    
    args = parser.parse_args()
    
    async with SimpleFileProcessor() as processor:
        results = []
        for url in args.urls:
            result = await processor.process_url(url)
            results.append(result)
        
        if args.format == 'json':
            output = json.dumps(results, indent=2)
        else:
            output = '\n'.join([str(result) for result in results])
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Results saved to {args.output}")
        else:
            print(output)

if __name__ == "__main__":
    asyncio.run(main())
