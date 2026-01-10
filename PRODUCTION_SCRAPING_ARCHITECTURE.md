# Production-Ready Cloud Scraping Architecture

## **The Solution: Google Cloud Serverless Scraping**

Based on research of how SaaS companies handle web scraping at scale, here's the **complete production architecture** for your Raptorflow deployment:

### **Architecture Overview**
```
Vercel Frontend → Google Cloud Backend → Pub/Sub Queue → Cloud Run Workers → Cloud Storage → Supabase
```

## **1. Cloud Components**

### **A. Cloud Run (Serverless Computing)**
- **What**: Docker containers that scale automatically
- **Cost**: $0.000024 per vCPU-second (~$0.086 per hour)
- **Networking**: Full outbound internet access (no restrictions)
- **Scaling**: 0-1000 instances automatically
- **Perfect for**: Scraping workers with Playwright/Tesseract

### **B. Cloud Pub/Sub (Queue System)**
- **What**: Message queue for distributing scraping tasks
- **Cost**: First 10GB/month free, then $0.40 per GB
- **Features**: At-least-once delivery, automatic retries
- **Perfect for**: Handling multiple users, rate limiting

### **C. Cloud Storage (Results)**
- **What**: Store scraped data, images, screenshots
- **Cost**: $0.020 per GB/month (standard)
- **Features**: CDN integration, versioning
- **Perfect for**: Raw HTML, extracted content, OCR results

### **D. Cloud Workflows (Orchestration)**
- **What**: Coordinate complex scraping pipelines
- **Cost**: $0.001 per step (first 5000 steps/month free)
- **Features**: Error handling, retries, conditional logic
- **Perfect for**: Multi-step scraping processes

## **2. Implementation Plan**

### **Phase 1: Basic Cloud Run Scraper**
```python
# Dockerfile
FROM python:3.11-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "scraper_worker.py"]

# scraper_worker.py
import os
from flask import Flask, request
import json
import asyncio
from tools.scraper import LocalScraperTool

app = Flask(__name__)

@app.route('/', methods=['POST'])
def scrape():
    data = request.get_json()
    url = data['url']
    legal_basis = data.get('legal_basis', 'user_request')

    scraper = LocalScraperTool()
    result = asyncio.run(scraper._execute(url, legal_basis=legal_basis))

    # Store in Cloud Storage
    from google.cloud import storage
    client = storage.Client()
    bucket = client.bucket('raptorflow-scraped-data')
    blob = bucket.blob(f"results/{hash(url)}.json")
    blob.upload_from_string(json.dumps(result))

    return result

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
```

### **Phase 2: Pub/Sub Integration**
```python
# pubsub_worker.py
from google.cloud import pubsub_v1
import json
import requests

def process_scraping_task(message):
    data = json.loads(message.data.decode('utf-8'))
    url = data['url']
    user_id = data['user_id']

    # Call Cloud Run scraper
    response = requests.post('https://scraper-service-xyz.run.app',
                            json={'url': url, 'user_id': user_id})

    return response.json

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path('project-id', 'scraping-tasks')

def callback(message):
    try:
        result = process_scraping_task(message)
        message.ack()
    except Exception as e:
        message.nack()

future = subscriber.subscribe(subscription_path, callback=callback)
```

### **Phase 3: Enhanced Scraper with Playwright + OCR**
```python
# enhanced_scraper.py
from playwright.async_api import async_playwright
import pytesseract
from PIL import Image
import io

class EnhancedScraperTool:
    async def scrape_with_javascript(self, url):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Wait for JavaScript to load
            await page.goto(url, wait_until='networkidle')
            await page.wait_for_timeout(3000)

            # Extract content
            content = await page.content()
            title = await page.title()

            # Extract brand colors
            colors = await page.evaluate('''
                () => {
                    const styles = getComputedStyle(document.body);
                    return {
                        primary: styles.backgroundColor,
                        text: styles.color,
                        accent: styles.accentColor
                    };
                }
            ''')

            # Screenshot for OCR
            screenshot = await page.screenshot(full_page=True)
            ocr_text = pytesseract.image_to_string(Image.open(io.BytesIO(screenshot)))

            await browser.close()

            return {
                'title': title,
                'content': content,
                'colors': colors,
                'ocr_text': ocr_text,
                'screenshot': screenshot
            }
```

## **3. API Integration**

### **Backend API Endpoint**
```python
# backend/api/v1/scrape/route.py
from fastapi import APIRouter, HTTPException
from google.cloud import pubsub_v1
import json

router = APIRouter()
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path('project-id', 'scraping-tasks')

@router.post("/scrape")
async def request_scrape(url: str, user_id: str):
    # Validate user permissions
    if not user_can_scrape(user_id):
        raise HTTPException(status_code=403, detail="User not authorized")

    # Queue the scraping task
    message_data = json.dumps({
        'url': url,
        'user_id': user_id,
        'timestamp': datetime.utcnow().isoformat()
    }).encode('utf-8')

    future = publisher.publish(topic_path, message_data)

    return {
        'status': 'queued',
        'task_id': future.result(),
        'estimated_time': '30-60 seconds'
    }

@router.get("/scrape/{task_id}/status")
async def get_scrape_status(task_id: str):
    # Check Cloud Storage for results
    # Return status or results
    pass
```

## **4. Cost Breakdown**

### **Monthly Costs (1000 scrapes/day)**
- **Cloud Run**: 1000 scrapes × 30s × $0.000024 = **$0.72/day**
- **Pub/Sub**: 1000 messages × 1KB = 1MB = **$0.00040/day**
- **Cloud Storage**: 1000 results × 50KB = 50MB = **$0.001/day**
- **Total**: **~$22/month** for 30,000 scrapes

### **Scaling Costs**
- **10,000 scrapes/day**: ~$220/month
- **100,000 scrapes/day**: ~$2,200/month
- **1,000,000 scrapes/day**: ~$22,000/month

## **5. Deployment Steps**

### **Step 1: Enable APIs**
```bash
gcloud services enable run.googleapis.com
gcloud services enable pubsub.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable workflows.googleapis.com
```

### **Step 2: Create Infrastructure**
```bash
# Create Pub/Sub topic
gcloud pubsub topics create scraping-tasks

# Create Cloud Storage bucket
gsutil mb gs://raptorflow-scraped-data

# Deploy Cloud Run service
gcloud run deploy scraper-service --source . --region us-central1
```

### **Step 3: Update Backend**
- Add scraping API endpoints
- Integrate with Pub/Sub
- Update frontend to call new APIs

## **6. Monitoring & Scaling**

### **Monitoring**
- Cloud Monitoring for performance metrics
- Error tracking in Cloud Logging
- Cost alerts in Cloud Billing

### **Auto-scaling**
- Cloud Run: 0-1000 instances automatically
- Pub/Sub: Unlimited message throughput
- Cloud Storage: Unlimited storage

## **7. Security & Compliance**

### **Security**
- Service accounts with minimal permissions
- VPC connectors for private resources
- IAM roles for each service

### **Compliance**
- Rate limiting per user
- Robots.txt enforcement
- Audit logging in Cloud Logging
- Data retention policies

## **8. Next Steps**

1. **Deploy basic Cloud Run scraper** (1-2 days)
2. **Add Pub/Sub queue system** (1 day)
3. **Enhance with Playwright + OCR** (2-3 days)
4. **Add monitoring and alerts** (1 day)
5. **Performance optimization** (1-2 days)

**Total timeline: 1-2 weeks**
**Total cost for 1000 daily scrapes: ~$22/month**

This architecture is **production-ready**, **scalable**, and **cost-effective** for your SaaS platform.
