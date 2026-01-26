# PowerShell script to update Supabase auth configuration
$SUPABASE_URL = "https://api.supabase.com/v1"
$PROJECT_ID = "vpwwzsanuyhpkvgorcnc"
$SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw"

$headers = @{
    "Authorization" = "Bearer $SERVICE_ROLE_KEY"
    "Content-Type" = "application/json"
}

Write-Host "🔧 Updating Supabase auth configuration..." -ForegroundColor Green

# Update redirect URLs
$body = @{
    site_url = "http://localhost:3000"
    additional_redirect_urls = @(
        "http://localhost:3000/auth/callback",
        "http://localhost:3001/auth/callback",
        "http://localhost:3002/auth/callback",
        "http://localhost:3003/auth/callback",
        "http://localhost:3004/auth/callback",
        "http://localhost:3005/auth/callback",
        "http://127.0.0.1:3000/auth/callback",
        "http://127.0.0.1:3001/auth/callback",
        "http://127.0.0.1:3002/auth/callback",
        "http://127.0.0.1:3003/auth/callback",
        "http://127.0.0.1:3004/auth/callback",
        "http://127.0.0.1:3005/auth/callback"
    )
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-RestMethod -Uri "$SUPABASE_URL/projects/$PROJECT_ID/config/auth" -Method PATCH -Headers $headers -Body $body
    Write-Host "✅ Auth configuration updated successfully!" -ForegroundColor Green
    Write-Host "Updated redirect URLs:" $response.additional_redirect_urls
} catch {
    Write-Host "❌ Failed to update auth config:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

Write-Host "🔧 Enabling Google OAuth provider..." -ForegroundColor Green

# Enable Google provider
$googleBody = @{
    enabled = $true
    client_id = "[REDACTED]"
    secret = "[REDACTED]"
    skip_nonce_check = $true
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$SUPABASE_URL/projects/$PROJECT_ID/config/auth/providers/google" -Method POST -Headers $headers -Body $googleBody
    Write-Host "✅ Google OAuth provider enabled successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to enable Google provider:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

Write-Host "🎉 Supabase auth configuration complete!" -ForegroundColor Cyan
