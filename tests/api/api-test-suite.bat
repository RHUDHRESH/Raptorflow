@echo off
REM RAPTORFLOW API TEST SUITE - Complete Testing Automation

echo 🔥 RAPTORFLOW API TEST SUITE
echo ==================================
echo.

REM Check if dev server is running
curl -s http://localhost:3000/api/health >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ DEV SERVER NOT RUNNING
    echo.
    echo Starting dev server...
    start /B npm run dev
    echo Waiting for server to start...
    timeout /t 15 /nobreak >nul
    echo.
)

echo 🧪 RUNNING API TESTS
echo.

echo 1️⃣ Quick Critical Endpoint Test
echo --------------------------------
node tests/api/quick-test-runner.cjs
echo.

echo 2️⃣ Comprehensive API Test
echo ----------------------------
echo Testing all endpoints (this will take a moment)...
node tests/api/comprehensive-api-test.cjs
echo.

echo 3️⃣ Health Check
echo ------------
curl -s http://localhost:3000/api/health
echo.
echo.

echo 4️⃣ Session Management Test
echo -------------------------
curl -s -X GET "http://localhost:3000/api/auth/session-management?userId=test-user"
echo.
echo.

echo 5️⃣ Payment Flow Test
echo -------------------
curl -s -X POST http://localhost:3000/api/complete-mock-payment ^
  -H "Content-Type: application/json" ^
  -d "{\"transactionId\": \"test-txn\", \"phonePeTransactionId\": \"test-pp\"}"
echo.
echo.

echo ✅ TEST SUITE COMPLETE
echo ===================
echo.
echo 📊 Results Summary:
echo • Quick Test: Critical endpoints status
echo • Comprehensive Test: All endpoints status  
echo • Health Check: System status
echo • Session Test: Session management status
echo • Payment Test: Mock payment flow status
echo.
echo 📋 Check results above for any issues
echo 📖 See tests/api/development-playbook.md for next steps
echo.

pause
