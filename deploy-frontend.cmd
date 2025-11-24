@echo off
REM Deploy RaptorFlow Frontend to Vercel (Windows)

echo.
echo 🚀 RaptorFlow Frontend Deployment to Vercel
echo ============================================

REM Check if Vercel CLI is installed
where vercel >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Vercel CLI not found. Install with: npm install -g vercel
    pause
    exit /b 1
)

REM Get project directory
cd /d "%~dp0"

REM Link project if not already linked
if not exist ".vercel" (
    echo 📝 Linking to Vercel project...
    call vercel link
)

REM Set environment variables
echo 🔐 Setting environment variables...
set /p SUPABASE_URL="Enter VITE_SUPABASE_URL: "
set /p SUPABASE_KEY="Enter VITE_SUPABASE_ANON_KEY: "
set /p BACKEND_URL="Enter VITE_BACKEND_API_URL: "
set /p POSTHOG_KEY="Enter VITE_POSTHOG_KEY (optional, press Enter to skip): "

call vercel env add VITE_SUPABASE_URL %SUPABASE_URL% --yes
call vercel env add VITE_SUPABASE_ANON_KEY %SUPABASE_KEY% --yes
call vercel env add VITE_BACKEND_API_URL %BACKEND_URL% --yes
if not "%POSTHOG_KEY%"=="" (
    call vercel env add VITE_POSTHOG_KEY %POSTHOG_KEY% --yes
)

REM Build and deploy
echo 🏗️  Building and deploying to Vercel...
call npm ci
call vercel deploy --prod

echo.
echo ✅ Frontend deployed successfully!
echo 📊 Check your deployment: https://vercel.com/dashboard
pause
