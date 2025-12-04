# Update .env file script
$envContent = @"
# ============================================
# RAPTORFLOW ENVIRONMENT CONFIGURATION
# ============================================

# ============================================
# APPLICATION CONFIGURATION
# ============================================
NODE_ENV=development
PORT=3000
FRONTEND_PUBLIC_URL=http://localhost:5173

# ============================================
# SUPABASE CONFIGURATION
# ============================================
# Frontend variables (Vite requires VITE_ prefix)
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=

# Backend service role key (backend will use VITE_SUPABASE_URL as fallback)
SUPABASE_SERVICE_ROLE_KEY=

# ============================================
# GOOGLE CLOUD / VERTEX AI CONFIGURATION
# ============================================
GOOGLE_CLOUD_PROJECT_ID=
GOOGLE_CLOUD_LOCATION=us-central1

# ============================================
# REDIS / UPSTASH CONFIGURATION
# ============================================
UPSTASH_REDIS_REST_URL=
UPSTASH_REDIS_REST_TOKEN=

# ============================================
# PHONEPE PAYMENT GATEWAY CONFIGURATION
# ============================================
# Frontend variables (Vite requires VITE_ prefix)
VITE_PHONEPE_MERCHANT_ID=
VITE_PHONEPE_SALT_KEY=
VITE_PHONEPE_SALT_INDEX=1
VITE_PHONEPE_ENV=SANDBOX
"@

# Write to .env file
$envContent | Out-File -FilePath ".env" -Encoding utf8 -NoNewline

Write-Host "✓ .env file has been updated successfully!"
Write-Host ""
Write-Host "File location: $((Get-Item .env).FullName)"
Write-Host "File size: $((Get-Item .env).Length) bytes"
Write-Host ""
Write-Host "Variables in .env file:"
Get-Content .env | Where-Object { $_ -match '^[A-Z_]+\s*=' } | ForEach-Object {
    $varName = ($_ -split '=')[0].Trim()
    Write-Host "  - $varName"
}

