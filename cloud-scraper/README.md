# Raptorflow Cloud Scraper

Production-ready web scraping service running on Google Cloud Run with enhanced capabilities.

## Features

- **Playwright-based scraping**: Full JavaScript execution and SPA support
- **OCR capabilities**: Extract text from images using Tesseract
- **Color extraction**: Get brand colors and styling information
- **Screenshot capture**: Full-page screenshots for visual analysis
- **Structured data extraction**: JSON-LD and meta tag parsing
- **Compliance tracking**: Legal basis and audit trails
- **Scalable architecture**: Auto-scales from 0 to 1000 instances
- **Cost effective**: Pay only when scraping (scales to zero)

## Architecture

```
Vercel Frontend → Cloud Run Service → Cloud Storage → Pub/Sub → Supabase
```

## Quick Start

### 1. Deploy to Google Cloud Run

```bash
cd cloud-scraper
chmod +x deploy.sh
./deploy.sh
```

### 2. Test the Service

```bash
# Health check
curl https://your-service-url.run.app/health

# Scrape a URL
curl -X POST "https://your-service-url.run.app/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.pepsico.com/en/",
    "user_id": "test-user",
    "legal_basis": "research"
  }'
```

## API Endpoints

### POST /scrape
Main scraping endpoint

**Request:**
```json
{
  "url": "https://example.com",
  "user_id": "user-123",
  "legal_basis": "user_request"
}
```

**Response:**
```json
{
  "url": "https://example.com",
  "user_id": "user-123",
  "timestamp": "2026-01-02T01:00:00Z",
  "title": "Example Page",
  "content_length": 50000,
  "readable_text": "Extracted text content...",
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
  "screenshot_url": "https://storage.googleapis.com/...",
  "processing_time": 15.2,
  "status": "success"
}
```

### GET /health
Health check endpoint

### GET /stats
Scraping statistics

## Cost Breakdown

- **Cloud Run**: $0.000024 per vCPU-second
- **Cloud Storage**: $0.020 per GB/month
- **Pub/Sub**: $0.40 per GB (first 10GB free)

**Estimated costs:**
- 1,000 scrapes/day: ~$22/month
- 10,000 scrapes/day: ~$220/month
- 100,000 scrapes/day: ~$2,200/month

## Configuration

Environment variables:
- `GOOGLE_CLOUD_PROJECT`: GCP project ID
- `BUCKET_NAME`: Cloud Storage bucket name
- `TOPIC_NAME`: Pub/Sub topic name
- `MAX_CONTENT_LENGTH`: Maximum content length (default: 10MB)

## Monitoring

View logs:
```bash
gcloud logs read "resource.type=cloud_run_revision" --limit 50
```

View service details:
```bash
gcloud run services describe raptorflow-scraper --region us-central1
```

## Security Features

- **Rate limiting**: Built-in request validation
- **Input sanitization**: URL validation and content length limits
- **Audit trails**: All requests logged with user context
- **Compliance**: Legal basis tracking for all scraping operations
- **Non-root user**: Container runs as non-privileged user

## Performance Optimizations

- **Connection pooling**: Reuses browser instances efficiently
- **Screenshot optimization**: PNG compression for storage
- **Content truncation**: Limits text storage to prevent bloat
- **Auto-scaling**: Scales to zero when not in use
- **Timeout handling**: 30-second timeout prevents hanging

## Integration with Raptorflow

The scraper integrates seamlessly with your existing Raptorflow architecture:

1. **Backend API**: Add scraping endpoints to your FastAPI backend
2. **Queue System**: Pub/Sub handles asynchronous processing
3. **Storage**: Cloud Storage for raw data, Supabase for metadata
4. **Frontend**: Vercel frontend calls Cloud Run service

## Enhanced Features

### OCR Capabilities
- Extract text from images and screenshots
- Support for English language (expandable)
- Grayscale conversion for better accuracy

### Color Extraction
- Background, text, and accent colors
- Theme color detection
- Font family extraction

### Structured Data
- JSON-LD parsing
- Meta tag extraction
- Schema.org detection

### Visual Analysis
- Full-page screenshots
- Image extraction with metadata
- Visual content indexing

## Deployment Notes

- **Region**: Deployed to us-central1 (configurable)
- **Scaling**: 0-10 instances (configurable)
- **Memory**: 1GiB per instance
- **Timeout**: 60 seconds
- **Concurrency**: 10 requests per instance

## Troubleshooting

### Common Issues

1. **Memory errors**: Increase memory allocation in deploy.sh
2. **Timeout errors**: Increase timeout in deploy.sh
3. **OCR failures**: Check Tesseract installation in Dockerfile
4. **Permission errors**: Ensure service account has storage/pubsub permissions

### Debug Mode

For debugging, you can run locally:
```bash
cd cloud-scraper
pip install -r requirements.txt
python scraper_service.py
```

## Next Steps

1. **Deploy the service** using the deployment script
2. **Test with various URLs** to verify functionality
3. **Monitor costs** and adjust scaling parameters
4. **Add custom integrations** with your Raptorflow backend
5. **Implement rate limiting** for user-specific quotas
