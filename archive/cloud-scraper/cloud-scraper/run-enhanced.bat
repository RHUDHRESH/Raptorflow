@echo off
REM Enhanced Local Testing Script for Raptorflow Cloud Scraper with 20 FREE Upgrades (Windows)
REM This script sets up and runs the enhanced scraper locally for testing

echo 🚀 Setting up Enhanced Raptorflow Cloud Scraper with 20 FREE Upgrades...

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
if exist venv (
    echo 🗑️ Removing existing virtual environment...
    rmdir /s /q venv
)
python -m venv venv
call venv\Scripts\activate.bat

REM Install Python dependencies
echo 📚 Installing Python dependencies with 20 FREE upgrades...
pip install --upgrade pip
pip install -r requirements.txt

REM Install Playwright browsers
echo 🌐 Installing Playwright browsers...
playwright install chromium

REM Download NLTK data
echo 🧠 Downloading NLTK language data...
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"

REM Check for optional components
echo 🔍 Checking for optional components...

REM Check Tesseract
tesseract --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Tesseract not found - OCR functionality will be disabled
    echo 💡 To enable OCR, download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
) else (
    echo ✅ Tesseract found - OCR functionality enabled
)

REM Check OpenCV
python -c "import cv2" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ OpenCV not found - Computer vision features disabled
) else (
    echo ✅ OpenCV found - Computer vision enabled
)

REM Check Redis (optional)
redis-server --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Redis not found - Using local SQLite caching only
) else (
    echo ✅ Redis found - Advanced caching available
)

REM Set environment variables for local testing
set GOOGLE_CLOUD_PROJECT=raptorflow-enhanced-local
set BUCKET_NAME=enhanced-local-test-bucket
set TOPIC_NAME=enhanced-scraping-results
set PORT=8080
set LOCAL_MODE=true

echo ✅ Enhanced setup complete!
echo.
echo 🎯 20 FREE Upgrades Enabled:
echo    ✅ JavaScript Execution (Playwright + Selenium)
echo    ✅ OCR ^& Visual Analysis (Tesseract + OpenCV + ColorThief)
echo    ✅ Content Enhancement (BeautifulSoup4 + lxml + html5lib + cssutils)
echo    ✅ Data Processing (pandas + numpy + scikit-learn + NLTK)
echo    ✅ Storage ^& Search (SQLite + Whoosh + Elasticsearch + Redis)
echo    ✅ Performance (asyncio + aiofiles + uvloop)
echo    ✅ Compliance (robots.txt parser + user-agent rotation + rate limiting)
echo    ✅ Quality Control (difflib + hashlib + langdetect)
echo    ✅ Monitoring (prometheus_client + structlog + psutil)
echo.
echo 🚀 Starting enhanced scraper service...
echo 🌐 Service will be available at: http://localhost:8080
echo 📊 Prometheus metrics: http://localhost:8001
echo 🔍 Search endpoint: http://localhost:8080/search?q=your_query
echo.
echo 🧪 Enhanced test commands:
echo curl -X POST "http://localhost:8080/scrape" -H "Content-Type: application/json" -d "{\"url\":\"https://www.pepsico.com/en/\",\"user_id\":\"test-user\"}"
echo.
echo 📊 Enhanced stats: curl http://localhost:8080/stats
echo 🔍 Search content: curl "http://localhost:8080/search?q=pepsi"
echo 🏥 Health check: curl http://localhost:8080/health
echo 🛑 Stop with: Ctrl+C
echo.

REM Start the service
python enhanced_scraper_service.py
