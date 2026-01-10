#!/bin/bash

# Enhanced Local Testing Script for Raptorflow Cloud Scraper with 20 FREE Upgrades
# This script sets up and runs the enhanced scraper locally for testing

set -e

echo "🚀 Setting up Enhanced Raptorflow Cloud Scraper with 20 FREE Upgrades..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install it first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install it first."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "🗑️ Removing existing virtual environment..."
    rm -rf venv
fi
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python dependencies with 20 FREE upgrades..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium

# Download NLTK data
echo "🧠 Downloading NLTK language data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"

# Check for optional components
echo "🔍 Checking for optional components..."

# Check Tesseract
if command -v tesseract &> /dev/null; then
    echo "✅ Tesseract found - OCR functionality enabled"
else
    echo "⚠️ Tesseract not found - OCR functionality will be disabled"
    echo "💡 To enable OCR: brew install tesseract (Mac) or sudo apt-get install tesseract-ocr (Linux)"
fi

# Check OpenCV
python -c "import cv2" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ OpenCV found - Computer vision enabled"
else
    echo "⚠️ OpenCV not found - Computer vision features disabled"
fi

# Check Redis (optional)
if command -v redis-server &> /dev/null; then
    echo "✅ Redis found - Advanced caching available"
else
    echo "⚠️ Redis not found - Using local SQLite caching only"
fi

# Set environment variables for local testing
export GOOGLE_CLOUD_PROJECT="raptorflow-enhanced-local"
export BUCKET_NAME="enhanced-local-test-bucket"
export TOPIC_NAME="enhanced-scraping-results"
export PORT=8080
export LOCAL_MODE=true

echo "✅ Enhanced setup complete!"
echo ""
echo "🎯 20 FREE Upgrades Enabled:"
echo "   ✅ JavaScript Execution (Playwright + Selenium)"
echo "   ✅ OCR & Visual Analysis (Tesseract + OpenCV + ColorThief)"
echo "   ✅ Content Enhancement (BeautifulSoup4 + lxml + html5lib + cssutils)"
echo "   ✅ Data Processing (pandas + numpy + scikit-learn + NLTK)"
echo "   ✅ Storage & Search (SQLite + Whoosh + Elasticsearch + Redis)"
echo "   ✅ Performance (asyncio + aiofiles + uvloop)"
echo "   ✅ Compliance (robots.txt parser + user-agent rotation + rate limiting)"
echo "   ✅ Quality Control (difflib + hashlib + langdetect)"
echo "   ✅ Monitoring (prometheus_client + structlog + psutil)"
echo ""
echo "🚀 Starting enhanced scraper service..."
echo "🌐 Service will be available at: http://localhost:8080"
echo "📊 Prometheus metrics: http://localhost:8001"
echo "🔍 Search endpoint: http://localhost:8080/search?q=your_query"
echo ""
echo "🧪 Enhanced test commands:"
echo "curl -X POST \"http://localhost:8080/scrape\" -H \"Content-Type: application/json\" -d '{\"url\":\"https://www.pepsico.com/en/\",\"user_id\":\"test-user\"}'"
echo ""
echo "📊 Enhanced stats: curl http://localhost:8080/stats"
echo "🔍 Search content: curl \"http://localhost:8080/search?q=pepsi\""
echo "🏥 Health check: curl http://localhost:8080/health"
echo "🛑 Stop with: Ctrl+C"
echo ""

# Start the service
python enhanced_scraper_service.py
