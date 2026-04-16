# Build script for Windows using Docker
# Uses pre-built Rust image to avoid Windows linker issues

param(
    [string]$Target = "raptorflow-api",
    [switch]$Release,
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

# Get the current directory (should be repo root)
$RepoRoot = Get-Location
$WorkspacePath = $RepoRoot.Path

# Docker image to use for building
$BuilderImage = "rust:1.94-bookworm"

# Build command
$BuildCommand = "cargo build -p $Target"
if ($Release) {
    $BuildCommand += " --release"
}

# Full Docker command
$DockerCommand = @"
bash -c "
  apt-get update && apt-get install -y pkg-config libssl-dev cmake
  $BuildCommand
"
"@

Write-Host "Building $Target using Docker..." -ForegroundColor Green
Write-Host "Repository: $WorkspacePath" -ForegroundColor Gray
Write-Host "Command: $BuildCommand" -ForegroundColor Gray
Write-Host ""

try {
    # Run the build
    $startTime = Get-Date

    docker run --rm `
        -v "${WorkspacePath}:/workspace" `
        -w "/workspace" `
        -e "CARGO_HOME=/workspace/.cargo" `
        -e "CARGO_TARGET_DIR=/workspace/target" `
        $BuilderImage `
        bash -c $DockerCommand

    $endTime = Get-Date
    $duration = $endTime - $startTime

    Write-Host ""
    Write-Host "Build completed successfully in $($duration.TotalSeconds.ToString("F1"))s" -ForegroundColor Green

    # Show the built binary location
    if ($Release) {
        $BinaryPath = Join-Path $WorkspacePath "target\release\$Target.exe"
    } else {
        $BinaryPath = Join-Path $WorkspacePath "target\debug\$Target.exe"
    }

    if (Test-Path $BinaryPath) {
        Write-Host "Binary location: $BinaryPath" -ForegroundColor Cyan
    } else {
        Write-Host "Binary not found at expected location" -ForegroundColor Yellow
    }

} catch {
    Write-Host ""
    Write-Host "Build failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Optional: Clean up if requested
if ($Clean) {
    Write-Host ""
    Write-Host "Cleaning build artifacts..." -ForegroundColor Yellow
    docker run --rm `
        -v "${WorkspacePath}:/workspace" `
        -w "/workspace" `
        $BuilderImage `
        bash -c "cargo clean"
    Write-Host "Clean completed" -ForegroundColor Green
}