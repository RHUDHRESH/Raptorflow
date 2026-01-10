@echo off
echo Checking RaptorFlow Supabase Configuration...
echo.

REM Check if supabase CLI is installed
where supabase >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Supabase CLI not installed
    echo        Run: npm install -g supabase
    exit /b 1
) else (
    echo OK: Supabase CLI installed
)

REM Check config file
if exist config.toml (
    echo OK: Config file exists
    findstr "site_url = \"https://raptorflow.in\"" config.toml >nul
    if %errorlevel% equ 0 (
        echo OK: Site URL configured for production
    ) else (
        echo WARN: Site URL not configured for production
    )
    findstr "raptorflow.in" config.toml >nul
    if %errorlevel% equ 0 (
        echo OK: Redirect URLs include production domain
    ) else (
        echo WARN: Redirect URLs missing production domain
    )
) else (
    echo ERROR: Config file not found
)

REM Check migrations
if exist migrations (
    echo OK: Migrations directory exists
    dir /b migrations\*.sql 2>nul | find /c /v "" > temp_count.txt
    set /p count=<temp_count.txt
    echo OK: Found %count% migration files
    del temp_count.txt
) else (
    echo ERROR: Migrations directory not found
)

REM Check environment file
if exist ..\frontend\.env.local (
    echo OK: Frontend .env.local exists
    findstr "NEXT_PUBLIC_SUPABASE_URL" ..\frontend\.env.local >nul
    if %errorlevel% equ 0 (
        echo OK: Supabase URL configured
    )
    findstr "your-service-role-key-here" ..\frontend\.env.local >nul
    if %errorlevel% equ 0 (
        echo WARN: Service role key needs to be updated
    ) else (
        echo OK: Service role key configured
    )
) else (
    echo ERROR: Frontend .env.local not found
)

echo.
echo Summary:
echo 1. Ensure Docker is running for local development
echo 2. Run 'supabase link --project-ref vpwwzsanuyhpkvgorcnc'
echo 3. Run 'supabase db push' to apply migrations
echo 4. Configure Google OAuth in Supabase dashboard
echo 5. Test authentication flow
pause
