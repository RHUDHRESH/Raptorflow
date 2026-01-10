# RaptorFlow Supabase Status Check Script

Write-Host "🔍 Checking RaptorFlow Supabase Configuration..." -ForegroundColor Cyan
Write-Host ""

# Check if supabase CLI is installed
$supabaseCommand = Get-Command supabase -ErrorAction SilentlyContinue
if (-not $supabaseCommand) {
    Write-Host "❌ Supabase CLI not installed" -ForegroundColor Red
    exit 1
} else {
    Write-Host "✅ Supabase CLI installed" -ForegroundColor Green
}

# Check config file
$configPath = ".\config.toml"
if (Test-Path $configPath) {
    Write-Host "✅ Config file exists" -ForegroundColor Green

    # Check site URL
    $configContent = Get-Content $configPath
    if ($configContent -match "site_url = `"https://raptorflow.in`"") {
        Write-Host "✅ Site URL configured for production" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Site URL not configured for production" -ForegroundColor Yellow
    }

    # Check redirect URLs
    if ($configContent -match "raptorflow.in") {
        Write-Host "✅ Redirect URLs include production domain" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Redirect URLs missing production domain" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Config file not found" -ForegroundColor Red
}

# Check migrations
$migrationsPath = ".\migrations"
if (Test-Path $migrationsPath) {
    $migrationFiles = Get-ChildItem -Path $migrationsPath -Filter "*.sql"
    Write-Host "✅ Found $($migrationFiles.Count) migration files:" -ForegroundColor Green
    foreach ($file in $migrationFiles) {
        Write-Host "   - $($file.Name)" -ForegroundColor Gray
    }
} else {
    Write-Host "❌ Migrations directory not found" -ForegroundColor Red
}

# Check project link
try {
    $status = supabase status 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Linked to Supabase project" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Not linked to Supabase project" -ForegroundColor Yellow
        Write-Host "   Run: supabase link --project-ref vpwwzsanuyhpkvgorcnc" -ForegroundColor Gray
    }
} catch {
    Write-Host "⚠️ Cannot check project status" -ForegroundColor Yellow
}

# Check environment files
$envLocalPath = "..\frontend\.env.local"
if (Test-Path $envLocalPath) {
    Write-Host "✅ Frontend .env.local exists" -ForegroundColor Green
    $envContent = Get-Content $envLocalPath
    if ($envContent -match "NEXT_PUBLIC_SUPABASE_URL") {
        Write-Host "✅ Supabase URL configured" -ForegroundColor Green
    }
    if ($envContent -match "SUPABASE_SERVICE_ROLE_KEY") {
        if ($envContent -match "your-service-role-key-here") {
            Write-Host "⚠️ Service role key needs to be updated" -ForegroundColor Yellow
        } else {
            Write-Host "✅ Service role key configured" -ForegroundColor Green
        }
    }
} else {
    Write-Host "❌ Frontend .env.local not found" -ForegroundColor Red
}

Write-Host ""
Write-Host "📋 Summary:" -ForegroundColor Cyan
Write-Host "1. Ensure Docker is running for local development" -ForegroundColor White
Write-Host "2. Run '.\setup.ps1' to link and push migrations" -ForegroundColor White
Write-Host "3. Configure Google OAuth in Supabase dashboard" -ForegroundColor White
Write-Host "4. Test authentication flow" -ForegroundColor White
