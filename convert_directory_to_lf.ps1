# Bulk convert directory to LF line endings
# Usage: .\convert_directory_to_lf.ps1 "raptorflow-app\src"

param(
    [Parameter(Mandatory=$true)]
    [string]$Directory
)

Get-ChildItem -Path $Directory -Include *.ts,*.tsx,*.js,*.jsx,*.json,*.css,*.md,*.yml,*.yaml -Recurse -File | ForEach-Object {
    python convert_line_endings.py $_.FullName to_unix
}

Write-Host "Converted all source files in $Directory to LF format"
