# RaptorFlow Supabase Setup Script (PowerShell)

Write-Host "🚀 Setting up RaptorFlow Supabase Project..." -ForegroundColor Cyan

# Check if supabase CLI is installed
$supabaseCommand = Get-Command supabase -ErrorAction SilentlyContinue
if (-not $supabaseCommand) {
    Write-Host "❌ Supabase CLI not found. Please install it first:" -ForegroundColor Red
    Write-Host "   npm install -g supabase" -ForegroundColor Yellow
    exit 1
}

# Login to Supabase
Write-Host "📝 Logging in to Supabase..." -ForegroundColor Green
Write-Host "Please get your access token from: https://supabase.com/dashboard/account/tokens" -ForegroundColor Yellow
supabase login

# Link to project
Write-Host "🔗 Linking to project..." -ForegroundColor Green
supabase link --project-ref vpwwzsanuyhpkvgorcnc

# Check status
Write-Host "📊 Checking project status..." -ForegroundColor Green
supabase status

# Push migrations
Write-Host "⬆️ Pushing database migrations..." -ForegroundColor Green
supabase db push

# Generate types
Write-Host "📝 Generating TypeScript types..." -ForegroundColor Green
supabase gen types typescript --local > ../frontend/src/types/supabase.ts

Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Go to https://supabase.com/dashboard/project/vpwwzsanuyhpkvgorcnc" -ForegroundColor White
Write-Host "2. Configure Authentication > Providers > Google" -ForegroundColor White
Write-Host "3. Set site URL to https://raptorflow.in" -ForegroundColor White
Write-Host "4. Add redirect URLs" -ForegroundColor White
