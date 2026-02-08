#!/bin/bash

# Local testing script for Raptorflow Cloud Scraper (Linux/Mac) - FIXED VERSION
# This script sets up and runs the scraper locally for testing

set -e

echo "🧪 Setting up local Raptorflow Cloud Scraper..."

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
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium

# Check if Tesseract is available (optional)
echo "🔍 Checking for Tesseract (OCR)..."
if command -v tesseract &> /dev/null; then
    echo "✅ Tesseract found - OCR functionality enabled"
else
    echo "⚠️ Tesseract not found - OCR functionality will be disabled"
    echo "💡 To enable OCR:"
    echo "   Mac: brew install tesseract"
    echo "   Ubuntu/Debian: sudo apt-get install tesseract-ocr"
    echo "   CentOS/RHEL: sudo yum install tesseract"
fi

# Set environment variables for local testing
export GOOGLE_CLOUD_PROJECT="raptorflow-local-test"
export BUCKET_NAME="local-test-bucket"
export TOPIC_NAME="local-test-topic"
export PORT=8080
export LOCAL_MODE=true

echo "✅ Setup complete!"
echo ""
echo "🚀 Starting local scraper service..."
echo "🌐 Service will be available at: http://localhost:8080"
echo "🧪 Test with:"
echo "curl -X POST \"http://localhost:8080/scrape\" -H \"Content-Type: application/json\" -d '{\"url\":\"https://www.pepsico.com/en/\",\"user_id\":\"test-user\"}'"
echo ""
echo "📊 Health check: curl http://localhost:8080/health"
echo "🛑 Stop with: Ctrl+C"
echo ""

# Start the service
python scraper_service.py
