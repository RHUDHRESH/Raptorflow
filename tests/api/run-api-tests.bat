@echo off
REM API Endpoint Test Runner

echo 🔥 RAPTORFLOW API ENDPOINT TESTER
echo ==================================

REM Check if dev server is running
curl -s http://localhost:3000/api/health >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ DEV SERVER NOT RUNNING - Start with: npm run dev
    echo.
    echo Starting dev server...
    start /B npm run dev
    echo Waiting for server to start...
    timeout /t 10 /nobreak >nul
)

REM Run the API endpoint tests
echo 🚀 Testing all API endpoints...
node tests/api/api-endpoint-tester.js

echo.
echo ✨ API TESTING COMPLETE!
echo 📝 Check results above for any critical failures
pause
