@echo off
REM Wrapper script for gcloud MCP to ensure gcloud is in PATH
setlocal enabledelayedexpansion

REM Add gcloud SDK bin directory to PATH
set PATH=C:\Users\hp\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin;!PATH!

REM Verify gcloud executable exists
where gcloud >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: gcloud executable not found
    exit /b 1
)

REM Run the gcloud MCP server
npx -y @google-cloud/gcloud-mcp %*
