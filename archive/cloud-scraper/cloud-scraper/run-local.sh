#!/bin/bash

# Local testing script for Raptorflow Cloud Scraper
# This script sets up and runs the scraper locally for testing

set -e

echo "🧪 Setting up local Raptorflow Cloud Scraper..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install it first."
    exit 1
fi

# Check if Node.js is installed (for Playwright)
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install it first."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
npx playwright install chromium

# Set environment variables for local testing
export GOOGLE_CLOUD_PROJECT="raptorflow-481505"
export BUCKET_NAME="raptorflow-scraped-data"
export TOPIC_NAME="scraping-results"
export PORT=8080

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
