@echo off
REM Local testing script for Raptorflow Cloud Scraper (Windows)
REM This script sets up and runs the scraper locally for testing

echo 🧪 Setting up local Raptorflow Cloud Scraper...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install it first.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install it first.
    pause
    exit /b 1
)

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Install Python dependencies
echo 📚 Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt

REM Install Playwright browsers
echo 🌐 Installing Playwright browsers...
npx playwright install chromium

REM Set environment variables for local testing
set GOOGLE_CLOUD_PROJECT=raptorflow-481505
set BUCKET_NAME=raptorflow-scraped-data
set TOPIC_NAME=scraping-results
set PORT=8080

echo ✅ Setup complete!
echo.
echo 🚀 Starting local scraper service...
echo 🌐 Service will be available at: http://localhost:8080
echo 🧪 Test with:
echo curl -X POST "http://localhost:8080/scrape" -H "Content-Type: application/json" -d "{\"url\":\"https://www.pepsico.com/en/\",\"user_id\":\"test-user\"}"
echo.
echo 📊 Health check: curl http://localhost:8080/health
echo 🛑 Stop with: Ctrl+C
echo.

REM Start the service
python scraper_service.py
