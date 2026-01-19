# 🌐 Internet File Processor

A powerful Python tool for downloading and parsing files from URLs. Supports multiple file formats with comprehensive metadata extraction and error handling.

## ✨ Features

### 📁 **Supported File Formats**
- **JSON** - Structured data parsing with metadata
- **CSV** - Tabular data with headers and row counts
- **XML** - Hierarchical structure parsing
- **HTML** - Web content extraction (titles, links, images)
- **Markdown** - Structured document parsing
- **YAML** - Configuration file parsing
- **TXT/LOG** - Plain text with statistics

### 🚀 **Key Capabilities**
- **Async Downloads** - Fast concurrent file processing
- **Metadata Extraction** - File size, checksum, content analysis
- **Error Handling** - Graceful fallbacks and detailed error reporting
- **Content Preview** - Smart content summaries and previews
- **Batch Processing** - Process multiple URLs at once
- **Interactive Mode** - User-friendly command-line interface

## 🛠️ Installation

### Prerequisites
```bash
pip install aiohttp aiofiles
```

### Optional Dependencies (for enhanced parsing)
```bash
pip install beautifulsoup4 markdown pyyaml pandas lxml
```

### OCR Support (for PDF processing)
```bash
# Install backend OCR service dependencies
# See backend/services/ocr_service.py for requirements
```

## 📖 Usage

### 1. **Command Line Interface**

#### Single URL Processing
```bash
python simple_file_processor.py https://example.com/data.json
```

#### Multiple URLs
```bash
python simple_file_processor.py https://url1.com/file.json https://url2.com/data.csv
```

#### Save Results
```bash
python simple_file_processor.py https://example.com/data.json --output results.json
```

### 2. **Interactive Mode**

```bash
python interactive_file_processor.py
```

This provides a user-friendly menu-driven interface for:
- Processing individual URLs with preview options
- Batch processing multiple URLs
- Saving results to files

### 3. **Python API**

```python
import asyncio
from simple_file_processor import SimpleFileProcessor

async def process_files():
    async with SimpleFileProcessor() as processor:
        # Process single URL
        result = await processor.process_url("https://example.com/data.json")
        print(result)
        
        # Process multiple URLs
        urls = ["https://url1.com/file.json", "https://url2.com/data.csv"]
        for url in urls:
            result = await processor.process_url(url)
            print(f"Processed: {result['download_info']['filename']}")

asyncio.run(process_files())
```

## 📊 Output Format

### **Successful Processing Result**
```json
{
  "url": "https://example.com/data.json",
  "download_info": {
    "filename": "example_com_file.json",
    "size": 1024,
    "content_type": "application/json",
    "checksum": "sha256_hash_here",
    "downloaded_at": "timestamp"
  },
  "parse_result": {
    "status": "success",
    "file_info": {...},
    "parsed_content": {...},
    "metadata": {
      "file_type": ".json",
      "content_type": "application/json",
      "size_bytes": 1024,
      "checksum": "sha256_hash_here",
      "key_count": 10
    }
  }
}
```

### **Error Result**
```json
{
  "url": "https://example.com/file.xyz",
  "status": "error",
  "error": "Unsupported file format: .xyz"
}
```

## 🔧 Configuration

### **Custom Download Directory**
```python
processor = SimpleFileProcessor(download_dir="/path/to/downloads")
```

### **Timeout Settings**
The processor uses a 30-second timeout by default. This can be modified in the code.

### **User Agent**
The processor uses a custom user agent for web requests to avoid blocking.

## 📋 Format-Specific Features

### **JSON Files**
- Parse structured data
- Count keys and nested objects
- Validate JSON syntax

### **CSV Files**
- Extract headers and data rows
- Handle different delimiters
- Provide row counts

### **HTML Files**
- Extract page title
- Find all headings (h1-h6)
- List all links and images
- Extract clean text content

### **Markdown Files**
- Parse to HTML structure
- Extract headings hierarchy
- Find internal and external links
- Character and word counts

### **XML Files**
- Parse hierarchical structure
- Extract attributes and text content
- Handle namespaces

### **YAML Files**
- Parse configuration files
- Handle complex nested structures
- Validate YAML syntax

## 🛡️ Security Features

### **File Validation**
- URL format validation
- File size limits
- Content type verification
- Checksum calculation for integrity

### **Safe Processing**
- Temporary file cleanup
- Encoding handling (UTF-8 fallback)
- Error isolation (one file failure doesn't stop batch)

### **Privacy**
- No persistent storage unless explicitly requested
- Temporary files are automatically cleaned up
- User agent identification for web servers

## 🚨 Error Handling

### **Download Errors**
- HTTP error codes (404, 500, etc.)
- Network timeouts
- Invalid URLs
- SSL certificate issues

### **Parse Errors**
- Unsupported file formats
- Corrupted files
- Encoding issues
- Syntax errors (invalid JSON, XML, etc.)

### **Graceful Fallbacks**
- HTML parsing without BeautifulSoup
- Markdown parsing without markdown library
- YAML parsing without PyYAML

## 📈 Performance

### **Async Processing**
- Concurrent downloads
- Non-blocking I/O operations
- Efficient memory usage

### **Optimizations**
- Streaming downloads for large files
- Chunked file reading
- Minimal memory footprint

## 🔍 Examples

### **Example 1: Process API Response**
```python
import asyncio
from simple_file_processor import SimpleFileProcessor

async def process_api_data():
    async with SimpleFileProcessor() as processor:
        result = await processor.process_url("https://api.github.com/users/octocat")
        
        if result["parse_result"]["status"] == "success":
            user_data = result["parse_result"]["parsed_content"]
            print(f"User: {user_data.get('name')}")
            print(f"Repos: {user_data.get('public_repos')}")

asyncio.run(process_api_data())
```

### **Example 2: Extract Website Content**
```python
async def extract_website():
    async with SimpleFileProcessor() as processor:
        result = await processor.process_url("https://example.com")
        
        if result["parse_result"]["status"] == "success":
            content = result["parse_result"]["parsed_content"]
            print(f"Title: {content.get('title')}")
            print(f"Links: {len(content.get('links', []))}")
            print(f"Images: {len(content.get('images', []))}")

asyncio.run(extract_website())
```

### **Example 3: Batch CSV Processing**
```python
async def process_csv_files():
    urls = [
        "https://example.com/data1.csv",
        "https://example.com/data2.csv"
    ]
    
    async with SimpleFileProcessor() as processor:
        for url in urls:
            result = await processor.process_url(url)
            
            if result["parse_result"]["status"] == "success":
                csv_data = result["parse_result"]["parsed_content"]
                print(f"CSV {url}: {csv_data['row_count']} rows")

asyncio.run(process_csv_files())
```

## 🤝 Integration with Raptorflow

This file processor integrates seamlessly with the Raptorflow platform:

### **Onboarding Integration**
- Process uploaded files during user onboarding
- Extract content from document uploads
- Parse configuration files

### **Data Import**
- Import CSV data for campaign management
- Process JSON API responses
- Extract website content for analysis

### **Content Management**
- Parse markdown documentation
- Process HTML templates
- Handle configuration files

## 📝 Troubleshooting

### **Common Issues**

#### **SSL Certificate Errors**
```bash
# For testing only - disable SSL verification
# Modify the aiohttp.ClientSession in the code
ssl=False
```

#### **Large File Timeouts**
```python
# Increase timeout
aiohttp.ClientTimeout(total=60)  # 60 seconds
```

#### **Missing Dependencies**
```bash
# Install optional dependencies
pip install beautifulsoup4 markdown pyyaml pandas lxml
```

#### **Encoding Issues**
The processor automatically handles UTF-8 encoding and falls back to other encodings if needed.

### **Debug Mode**
Add print statements or logging to track processing steps:

```python
print(f"Downloading: {url}")
print(f"File saved: {file_path}")
print(f"Parsing: {file_ext}")
```

## 📄 License

This project is part of the Raptorflow platform and follows the same licensing terms.

## 🤝 Contributing

To contribute to this file processor:

1. Add support for new file formats
2. Improve error handling
3. Add new metadata extraction features
4. Optimize performance

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review the error messages in output
- Test with the interactive mode for debugging
