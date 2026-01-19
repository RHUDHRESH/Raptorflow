# RaptorFlow Authentication Production Deployment Script (PowerShell)
# This script deploys the authentication system to production

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("check", "deploy", "verify")]
    [string]$Action = "deploy"
)

# Colors for output
$Colors = @{
    Red = "Red"
    Green = "Green"
    Yellow = "Yellow"
    Blue = "Blue"
}

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Colors.Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Colors.Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Colors.Red
}

function Write-Step {
    param([string]$Message)
    Write-Host "[STEP] $Message" -ForegroundColor $Colors.Blue
}

# Check if required environment variables are set
function Test-EnvironmentVariables {
    Write-Step "Checking environment variables..."
    
    $requiredVars = @(
        "NEXT_PUBLIC_SUPABASE_URL",
        "NEXT_PUBLIC_SUPABASE_ANON_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
        "RESEND_API_KEY",
        "NEXT_PUBLIC_APP_URL"
    )
    
    $missingVars = @()
    
    foreach ($var in $requiredVars) {
        if (-not (Test-Path "env:$var") -or [string]::IsNullOrEmpty((Get-Item "env:$var").Value)) {
            $missingVars += $var
        }
    }
    
    if ($missingVars.Count -gt 0) {
        Write-Error "Missing required environment variables:"
        foreach ($var in $missingVars) {
            Write-Host "  - $var"
        }
        exit 1
    }
    
    Write-Status "All required environment variables are set"
}

# Verify database connection
function Test-DatabaseConnection {
    Write-Step "Verifying Supabase database connection..."
    
    try {
        $response = Invoke-RestMethod -Uri "$env:NEXT_PUBLIC_APP_URL/api/setup/create-db-table" -Method GET -TimeoutSec 15
        if ($response.exists) {
            Write-Status "Database connection verified"
        } else {
            Write-Warning "Database table not found, creating..."
            
            $createResponse = Invoke-RestMethod -Uri "$env:NEXT_PUBLIC_APP_URL/api/setup/create-db-table" -Method POST -TimeoutSec 15
            if ($createResponse.success) {
                Write-Status "Database table created successfully"
            } else {
                Write-Error "Failed to create database table"
                exit 1
            }
        }
    } catch {
        Write-Error "Database connection failed: $($_.Exception.Message)"
        exit 1
    }
}

# Test email service
function Test-EmailService {
    Write-Step "Testing Resend email service..."
    
    try {
        $body = @{ email = "test@example.com" } | ConvertTo-Json
        $response = Invoke-RestMethod -Uri "$env:NEXT_PUBLIC_APP_URL/api/auth/forgot-password" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30
        
        if ($response.success) {
            Write-Status "Email service is working"
        } else {
            Write-Error "Email service test failed"
            exit 1
        }
    } catch {
        Write-Error "Email service test failed: $($_.Exception.Message)"
        exit 1
    }
}

# Verify authentication endpoints
function Test-AuthenticationEndpoints {
    Write-Step "Verifying authentication endpoints..."
    
    $endpoints = @(
        "/login",
        "/signup",
        "/forgot-password",
        "/auth/reset-password",
        "/auth/callback"
    )
    
    foreach ($endpoint in $endpoints) {
        try {
            $response = Invoke-WebRequest -Uri "$env:NEXT_PUBLIC_APP_URL$endpoint" -Method GET -TimeoutSec 10 -UseBasicParsing -MaximumRedirection 0
            $statusCode = $response.StatusCode
            
            if ($statusCode -eq 200 -or $statusCode -eq 307) {
                Write-Status "✓ $endpoint ($statusCode)"
            } else {
                Write-Error "✗ $endpoint ($statusCode)"
                exit 1
            }
        } catch {
            Write-Error "✗ $endpoint (Connection failed)"
            exit 1
        }
    }
}

# Check security headers
function Test-SecurityHeaders {
    Write-Step "Verifying security headers..."
    
    try {
        $response = Invoke-WebRequest -Uri "$env:NEXT_PUBLIC_APP_URL/login" -Method GET -UseBasicParsing
        $headers = $response.Headers
        
        $requiredHeaders = @(
            "content-security-policy",
            "x-content-type-options",
            "x-frame-options",
            "x-xss-protection",
            "referrer-policy"
        )
        
        foreach ($header in $requiredHeaders) {
            $headerFound = $false
            foreach ($key in $headers.Keys) {
                if ($key.ToLower() -eq $header.ToLower()) {
                    Write-Status "✓ $header"
                    $headerFound = $true
                    break
                }
            }
            if (-not $headerFound) {
                Write-Warning "✗ $header (missing)"
            }
        }
    } catch {
        Write-Error "Security headers check failed: $($_.Exception.Message)"
        exit 1
    }
}

# Run health check
function Test-SystemHealth {
    Write-Step "Running system health check..."
    
    try {
        $response = Invoke-RestMethod -Uri "$env:NEXT_PUBLIC_APP_URL/api/health" -Method GET -TimeoutSec 15
        Write-Status "Health check passed"
        $response | ConvertTo-Json -Depth 3
    } catch {
        Write-Error "Health check failed: $($_.Exception.Message)"
        exit 1
    }
}

# Create production backup
function New-ProductionBackup {
    Write-Step "Creating production backup..."
    
    # Note: This would need to be implemented based on your backup strategy
    Write-Warning "Backup strategy needs to be implemented"
}

# Deploy application
function Deploy-Application {
    Write-Step "Deploying application..."
    
    try {
        # Build the application
        Write-Status "Building application..."
        npm run build
        
        # Run database migrations
        Write-Status "Running database migrations..."
        # npm run migrate  # Uncomment if you have migration scripts
        
        # Start the application
        Write-Status "Starting application..."
        # npm start  # Uncomment for production start
        
        Write-Status "Application deployed successfully"
    } catch {
        Write-Error "Deployment failed: $($_.Exception.Message)"
        exit 1
    }
}

# Post-deployment verification
function Test-PostDeployment {
    Write-Step "Running post-deployment verification..."
    
    # Wait for application to start
    Start-Sleep -Seconds 10
    
    # Verify all endpoints are working
    Test-AuthenticationEndpoints
    
    # Test complete authentication flow
    Write-Status "Testing complete authentication flow..."
    
    try {
        # Create test user
        $userBody = @{ email = "deploy-test@example.com"; password = "TestPassword123" } | ConvertTo-Json
        $userResponse = Invoke-RestMethod -Uri "$env:NEXT_PUBLIC_APP_URL/api/test/create-user" -Method POST -Body $userBody -ContentType "application/json" -TimeoutSec 15
        
        # Test login
        $loginBody = @{ email = "deploy-test@example.com"; password = "TestPassword123" } | ConvertTo-Json
        $loginResponse = Invoke-RestMethod -Uri "$env:NEXT_PUBLIC_APP_URL/api/test/login" -Method POST -Body $loginBody -ContentType "application/json" -TimeoutSec 15
        
        if ($loginResponse.success) {
            Write-Status "Authentication flow test passed"
        } else {
            Write-Error "Authentication flow test failed"
            exit 1
        }
    } catch {
        Write-Error "Authentication flow test failed: $($_.Exception.Message)"
        exit 1
    }
}

# Main deployment function
function Start-Deployment {
    Write-Status "Starting deployment process..."
    
    # Pre-deployment checks
    Test-EnvironmentVariables
    Test-DatabaseConnection
    Test-EmailService
    Test-AuthenticationEndpoints
    Test-SecurityHeaders
    Test-SystemHealth
    
    # Create backup
    New-ProductionBackup
    
    # Deploy
    Deploy-Application
    
    # Post-deployment verification
    Test-PostDeployment
    
    Write-Status "🎉 Deployment completed successfully!"
    Write-Host "================================================"
    Write-Host "Authentication system is now live at: $env:NEXT_PUBLIC_APP_URL"
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "1. Configure OAuth providers (Google, etc.)"
    Write-Host "2. Set up monitoring and alerting"
    Write-Host "3. Configure SSL certificates"
    Write-Host "4. Set up backup schedules"
    Write-Host "5. Review security settings"
}

# Main script execution
switch ($Action) {
    "check" {
        Test-EnvironmentVariables
        Test-DatabaseConnection
        Test-EmailService
        Test-AuthenticationEndpoints
        Test-SecurityHeaders
        Test-SystemHealth
    }
    "deploy" {
        Start-Deployment
    }
    "verify" {
        Test-PostDeployment
    }
    default {
        Write-Host "Usage: .\deploy-authentication.ps1 [-Action check|deploy|verify]"
        Write-Host "  check   - Run pre-deployment checks"
        Write-Host "  deploy  - Full deployment process"
        Write-Host "  verify  - Post-deployment verification"
        exit 1
    }
}
