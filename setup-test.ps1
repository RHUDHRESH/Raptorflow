# RaptorFlow Test Setup Script for Windows
# This script helps set up the testing environment

Write-Host "=== RaptorFlow Test Setup ===" -ForegroundColor Cyan
Write-Host ""

# Check if .env.local exists
if (-not (Test-Path ".env.local")) {
    Write-Host "Creating .env.local template..." -ForegroundColor Yellow
    @"
# Frontend Environment Variables
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
"@ | Out-File -FilePath ".env.local" -Encoding utf8
    Write-Host "✓ Created .env.local - Please fill in your Supabase credentials" -ForegroundColor Green
} else {
    Write-Host "✓ .env.local already exists" -ForegroundColor Green
}

# Check if backend/.env exists
if (-not (Test-Path "backend\.env")) {
    Write-Host "Creating backend/.env template..." -ForegroundColor Yellow
    if (Test-Path "backend\.env.example") {
        Copy-Item "backend\.env.example" "backend\.env"
        Write-Host "✓ Created backend/.env from .env.example - Please fill in your credentials" -ForegroundColor Green
    } else {
        Write-Host "⚠ backend/.env.example not found. Please create backend/.env manually." -ForegroundColor Yellow
    }
} else {
    Write-Host "✓ backend/.env already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Next Steps ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Edit .env.local and fill in your Supabase credentials" -ForegroundColor White
Write-Host "2. Edit backend/.env and fill in your backend credentials" -ForegroundColor White
Write-Host ""
Write-Host "3. Install backend dependencies:" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Gray
Write-Host "   pip install -r requirements.txt" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Start backend (in one terminal):" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Gray
Write-Host "   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor Gray
Write-Host ""
Write-Host "5. Start frontend (in another terminal):" -ForegroundColor White
Write-Host "   npm run dev" -ForegroundColor Gray
Write-Host ""

