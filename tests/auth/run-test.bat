@echo off
REM Quick Auth Test Runner - Windows Version

echo 🔥 RAPTORFLOW AUTH TEST - QUICK RUN
echo ==================================

REM Check if dev server is running
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ DEV SERVER NOT RUNNING - Start with: npm run dev
    pause
    exit /b 1
)

REM Run the simple test
echo 🚀 Running auth tests...
node tests/auth/simple-auth-test.js

echo.
echo ✨ DONE! If you see ✅ above, auth is working!
echo 📝 If you see ❌, check the error message above
pause
