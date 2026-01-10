# Local Testing Guide for Raptorflow Cloud Scraper

## Quick Start - Local Testing

### Option 1: Windows (run-local.bat)
```bash
cd cloud-scraper
run-local.bat
```

### Option 2: Linux/Mac (run-local.sh)
```bash
cd cloud-scraper
chmod +x run-local.sh
./run-local.sh
```

### Option 3: Manual Setup
```bash
# Create virtual environment
python -m venv venv

# Windows
venv\Scripts\activate.bat

# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
npx playwright install chromium

# Set local mode
export LOCAL_MODE=true
export GOOGLE_CLOUD_PROJECT=raptorflow-local-test
export BUCKET_NAME=local-test-bucket
export TOPIC_NAME=local-test-topic
export PORT=8080

# Start service
python scraper_service.py
```

## Testing the Service

### Health Check
```bash
curl http://localhost:8080/health
```

### Test Scraping
```bash
curl -X POST "http://localhost:8080/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.pepsico.com/en/",
    "user_id": "test-user",
    "legal_basis": "testing"
  }'
```

### Get Stats
```bash
curl http://localhost:8080/stats
```

## Local Mode Features

### Mock Services
- **Storage**: Local file system (prints storage info to console)
- **Pub/Sub**: Local message queue (prints messages to console)
- **Logging**: Console output with structured logging
- **No Google Cloud dependencies**: Works without GCP credentials

### What Works Locally
✅ Full Playwright scraping (JavaScript execution)
✅ OCR text extraction from images
✅ Color extraction and styling analysis
✅ Screenshot capture (saved locally)
✅ Structured data extraction
✅ All API endpoints
✅ Error handling and logging

### What's Different Locally
- **Storage**: Files stored in memory, not persistent
- **Pub/Sub**: Messages logged to console, not actually queued
- **Screenshots**: Mock URLs, not actual cloud storage
- **No real costs**: Everything runs locally

## Testing Different URLs

### Simple Sites
```bash
curl -X POST "http://localhost:8080/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "user_id": "test"}'
```

### JavaScript-Heavy Sites
```bash
curl -X POST "http://localhost:8080/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.pepsico.com/en/", "user_id": "test"}'
```

### E-commerce Sites
```bash
curl -X POST "http://localhost:8080/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.amazon.com/dp/B08N5WRWNW", "user_id": "test"}'
```

## Expected Results

### Successful Response
```json
{
  "url": "https://www.pepsico.com/en/",
  "user_id": "test-user",
  "timestamp": "2026-01-02T01:00:00Z",
  "title": "Food and Drinks to Smile About",
  "content_length": 281178,
  "readable_text": "Discover more about our food, drinks...",
  "styles": {
    "background": "rgb(255, 255, 255)",
    "color": "rgb(0, 0, 0)",
    "accent": "rgb(0, 123, 255)",
    "theme_color": "#007bff"
  },
  "structured_data": [...],
  "meta_tags": {...},
  "images": [...],
  "ocr_text": "Text extracted from images...",
  "screenshot_url": "http://localhost:8080/mock-storage/screenshot.png",
  "processing_time": 15.2,
  "status": "success"
}
```

### Console Output
```
🔧 Running in local mode - using mock services
📝 Local logging: Setup complete
📁 Local storage: Saved local-test-bucket/results/test-user/12345.json (2845 bytes)
📨 Local Pub/Sub: Published message to projects/raptorflow-local-test/topics/local-test-topic
📁 Local storage: Saved local-test-bucket/screenshots/12345.png (156789 bytes)
```

## Troubleshooting

### Common Issues

1. **Playwright installation fails**
   ```bash
   # Install manually
   npx playwright install chromium
   ```

2. **OCR fails**
   ```bash
   # Install Tesseract manually
   # Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
   # Mac: brew install tesseract
   # Linux: sudo apt-get install tesseract-ocr
   ```

3. **Port already in use**
   ```bash
   # Change port
   export PORT=8081
   ```

4. **Virtual environment issues**
   ```bash
   # Recreate environment
   rm -rf venv
   python -m venv venv
   # Then activate and install again
   ```

### Performance Tips

1. **Increase timeout for slow sites**
   ```bash
   export SCRAPER_TIMEOUT=60
   ```

2. **Reduce memory usage**
   ```bash
   export MAX_CONTENT_LENGTH=1000000  # 1MB
   ```

3. **Disable OCR for faster processing**
   ```bash
   export ENABLE_OCR=false
   ```

## Integration Testing

### Test with Backend Integration
```bash
# Start scraper service
python scraper_service.py

# In another terminal, test backend integration
curl -X POST "http://localhost:8000/api/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.pepsico.com/en/",
    "user_id": "test-user"
  }'
```

### Load Testing
```bash
# Install Apache Bench
ab -n 10 -c 2 -p test.json -T application/json http://localhost:8080/scrape
```

Where `test.json` contains:
```json
{"url": "https://example.com", "user_id": "load-test"}
```

## Next Steps

1. **Run local tests** to verify functionality
2. **Test with various URLs** to ensure compatibility
3. **Check performance** with different site types
4. **Deploy to Cloud Run** when ready for production
5. **Monitor costs** and optimize as needed

## Deployment Comparison

| Feature | Local Mode | Cloud Run |
|---------|------------|-----------|
| Storage | In-memory | Google Cloud Storage |
| Pub/Sub | Console logging | Google Cloud Pub/Sub |
| Logging | Console | Google Cloud Logging |
| Cost | Free | Pay-per-use |
| Scaling | Single instance | Auto-scaling |
| Persistence | No | Yes |
| Monitoring | Console | Cloud Monitoring |

The local mode gives you full functionality for testing without any cloud costs or dependencies!
