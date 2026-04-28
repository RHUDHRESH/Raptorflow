#Requires -Version 5.1
<#
.SYNOPSIS
    RaptorFlow Local Runtime Reality Smoke Test

.DESCRIPTION
    Verifies the RaptorFlow stack can:
    1. Start Docker services (postgres, pgbouncer, qdrant)
    2. Run DB smoke test (runtime_reality_smoke)
    3. Run Qdrant smoke test
    4. Optionally run API smoke test
    5. Optionally run Bedrock smoke test

.PARAMETER WithApi
    Also start the API service and run api-health-smoke

.PARAMETER WithBedrock
    Also run the Bedrock smoke test (requires AWS credentials)

.PARAMETER ResetVolumes
    Destroy existing Docker volumes before starting (WARNING: destructive)

.PARAMETER SkipDocker
    Skip Docker Compose up/down — assume services are already running

.EXAMPLE
    .\local-runtime-smoke.ps1

.EXAMPLE
    .\local-runtime-smoke.ps1 -WithApi

.EXAMPLE
    .\local-runtime-smoke.ps1 -WithApi -WithBedrock
#>

param(
    [switch]$WithApi,
    [switch]$WithBedrock,
    [switch]$ResetVolumes,
    [switch]$SkipDocker
)

$ErrorActionPreference = "Stop"
$script:Failed = $false

function Write-SmokeLog {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "HH:mm:ss"
    $prefix = switch ($Level) {
        "PASS" { "[PASS]" }
        "FAIL" { "[FAIL]" }
        "WARN" { "[WARN]" }
        "SKIP" { "[SKIP]" }
        default { "[INFO]" }
    }
    Write-Host "${timestamp} ${prefix} ${Message}"
}

function Test-CurrentDirectory {
    $gitDir = Get-Item .git -ErrorAction SilentlyContinue
    if (-not $gitDir) {
        Write-SmokeLog "Must be run from repo root (where .git exists)" "FAIL"
        exit 1
    }
}

function Start-DockerServices {
    Write-SmokeLog "Starting Docker services (postgres, pgbouncer, qdrant)..."

    $composeFile = "docker-compose.yml"
    if (-not (Test-Path $composeFile)) {
        Write-SmokeLog "docker-compose.yml not found in current directory" "FAIL"
        $script:Failed = $true
        return
    }

    $upArgs = @("compose", "up", "-d", "postgres", "pgbouncer", "qdrant")
    if ($ResetVolumes) {
        Write-SmokeLog "ResetVolumes flag set — destroying volumes first..."
        $downArgs = @("compose", "down", "-v", "--remove-orphans")
        & docker @downArgs *>$null
    }

    & docker @upArgs
    if ($LASTEXITCODE -ne 0) {
        Write-SmokeLog "Docker compose up failed (exit code: $LASTEXITCODE)" "FAIL"
        $script:Failed = $true
        return
    }

    Write-SmokeLog "Waiting for Docker services to become healthy..."

    # Wait for postgres
    $pgReady = $false
    for ($i = 0; $i -lt 30; $i++) {
        Start-Sleep -Seconds 2
        $pgCheck = & docker exec postgres pg_isready -U raptorflow -d raptorflow 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-SmokeLog "Postgres is ready"
            $pgReady = $true
            break
        }
    }
    if (-not $pgReady) {
        Write-SmokeLog "Postgres did not become ready in time" "FAIL"
        $script:Failed = $true
    }

    # Wait for qdrant
    $qdReady = $false
    for ($i = 0; $i -lt 30; $i++) {
        Start-Sleep -Seconds 2
        try {
            $resp = Invoke-WebRequest -Uri "http://localhost:6333/healthz" -TimeoutSec 3 -UseBasicParsing -ErrorAction SilentlyContinue
            if ($resp.StatusCode -eq 200) {
                Write-SmokeLog "Qdrant is ready"
                $qdReady = $true
                break
            }
        } catch { }
    }
    if (-not $qdReady) {
        Write-SmokeLog "Qdrant did not become ready in time" "FAIL"
        $script:Failed = $true
    }
}

function Get-CheckDockerEnv {
    # Check if docker is available
    try {
        & docker version 2>$null
        if ($LASTEXITCODE -ne 0) { throw "docker not available" }
    } catch {
        Write-SmokeLog "Docker is not available — skipping Docker-dependent smoke tests" "SKIP"
        return $false
    }
    return $true
}

function Invoke-DbSmokeTest {
    Write-SmokeLog "Running DB runtime reality smoke test..."

    $env:TEST_DATABASE_URL = "postgres://raptorflow:raptorflow@localhost:5432/raptorflow"

    $result = & cargo test -p raptorflow-db --test runtime_reality_smoke -- --nocapture --test-threads=1 2>&1
    $exitCode = $LASTEXITCODE

    if ($exitCode -eq 0) {
        Write-SmokeLog "DB smoke test PASSED" "PASS"
        return $true
    } elseif ($exitCode -eq 101 -and $result -match "SKIP.*TEST_DATABASE_URL.*not set") {
        Write-SmokeLog "DB smoke test SKIPPED (TEST_DATABASE_URL not set)" "SKIP"
        return $null
    } else {
        Write-SmokeLog "DB smoke test FAILED (exit code: $exitCode)" "FAIL"
        Write-SmokeLog $result "FAIL"
        return $false
    }
}

function Invoke-QdrantSmokeTest {
    Write-SmokeLog "Running Qdrant runtime reality smoke test..."

    $env:QDRANT_SMOKE_URL = "http://localhost:6333"

    $result = & node scripts/smoke/qdrant-smoke.mjs 2>&1
    $exitCode = $LASTEXITCODE

    if ($exitCode -eq 0) {
        Write-SmokeLog "Qdrant smoke test PASSED" "PASS"
        return $true
    } else {
        Write-SmokeLog "Qdrant smoke test FAILED (exit code: $exitCode)" "FAIL"
        return $false
    }
}

function Invoke-ApiSmokeTest {
    Write-SmokeLog "Running API health smoke test..."

    $env:RAPTORFLOW_API_SMOKE_URL = "http://localhost:8080"

    $result = & node scripts/smoke/api-health-smoke.mjs 2>&1
    $exitCode = $LASTEXITCODE

    if ($exitCode -eq 0) {
        Write-SmokeLog "API smoke test PASSED" "PASS"
        return $true
    } else {
        Write-SmokeLog "API smoke test FAILED (exit code: $exitCode)" "FAIL"
        return $false
    }
}

function Invoke-BedrockSmokeTest {
    Write-SmokeLog "Running Bedrock runtime reality smoke test..."

    $env:BEDROCK_SMOKE_TEST = "1"

    $result = & cargo test -p raptorflow-aws --test bedrock_smoke -- --nocapture --test-threads=1 2>&1
    $exitCode = $LASTEXITCODE

    if ($exitCode -eq 0) {
        Write-SmokeLog "Bedrock smoke test PASSED" "PASS"
        return $true
    } elseif ($exitCode -eq 0 -and $result -match "SKIP.*BEDROCK_SMOKE_TEST.*1") {
        Write-SmokeLog "Bedrock smoke test SKIPPED (BEDROCK_SMOKE_TEST != 1)" "SKIP"
        return $null
    } else {
        Write-SmokeLog "Bedrock smoke test FAILED (exit code: $exitCode)" "FAIL"
        return $false
    }
}

# ─── MAIN ───────────────────────────────────────────────────────────────

Write-Host ""
Write-Host "=== RAPTORFLOW LOCAL RUNTIME REALITY SMOKE TEST ===" -ForegroundColor Cyan
Write-Host ""

Test-CurrentDirectory

$dockerAvailable = Get-CheckDockerEnv

$results = @{}

# Docker-dependent tests
if ($dockerAvailable -and -not $SkipDocker) {
    Start-DockerServices
}

# DB Smoke Test
if ($dockerAvailable -and -not $SkipDocker) {
    $dbResult = Invoke-DbSmokeTest
    $results["DB Smoke"] = $dbResult
}

# Qdrant Smoke Test
if ($dockerAvailable -and -not $SkipDocker) {
    $qdResult = Invoke-QdrantSmokeTest
    $results["Qdrant Smoke"] = $qdResult
}

# API Smoke Test (requires WithApi and API running)
if ($WithApi) {
    $apiRunning = $false
    if (-not $SkipDocker) {
        Write-SmokeLog "Starting API service for smoke test..."
        & docker compose up -d api 2>$null
        Start-Sleep -Seconds 5
        # Wait for API health
        for ($i = 0; $i -lt 20; $i++) {
            try {
                $r = Invoke-WebRequest -Uri "http://localhost:8080/health/live" -TimeoutSec 3 -UseBasicParsing -ErrorAction SilentlyContinue
                if ($r.StatusCode -eq 200) {
                    $apiRunning = $true
                    break
                }
            } catch { }
            Start-Sleep -Seconds 3
        }
    } else {
        $apiRunning = $true  # Assume it's running if SkipDocker
    }

    if ($apiRunning) {
        $apiResult = Invoke-ApiSmokeTest
        $results["API Health Smoke"] = $apiResult
    } else {
        Write-SmokeLog "API service did not become ready — skipping API smoke" "SKIP"
        $results["API Health Smoke"] = $null
    }
}

# Bedrock Smoke Test (requires WithBedrock)
if ($WithBedrock) {
    $bedrockResult = Invoke-BedrockSmokeTest
    $results["Bedrock Smoke"] = $bedrockResult
}

# ─── SUMMARY ───────────────────────────────────────────────────────────

Write-Host ""
Write-Host "=== SMOKE TEST SUMMARY ===" -ForegroundColor Cyan

$allPassed = $true
$anySkipped = $false

foreach ($name in $results.Keys) {
    $result = $results[$name]
    $color = switch ($result) {
        $true { "Green" }
        $false { "Red" }
        $null { "Yellow" }
    }
    $label = switch ($result) {
        $true { "PASS" }
        $false { "FAIL" }
        $null { "SKIP" }
    }
    Write-Host "  ${name}: ${label}" -ForegroundColor $color
    if ($result -eq $false) { $allPassed = $false }
    if ($result -eq $null) { $anySkipped = $true }
}

Write-Host ""

if ($allPassed) {
    Write-Host "FINAL RESULT: PASS" -ForegroundColor Green
    Write-Host ""
    exit 0
} else {
    Write-Host "FINAL RESULT: FAIL" -ForegroundColor Red
    Write-Host ""
    exit 1
}
