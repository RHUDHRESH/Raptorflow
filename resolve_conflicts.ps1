#!/usr/bin/env pwsh

# Script to resolve merge conflicts by choosing appropriate versions
# For this project, we'll primarily choose stage 2 (Next.js version) for most files

$conflictedFiles = git diff --name-only --diff-filter=U

Write-Host "Found $($conflictedFiles.Count) conflicted files"

foreach ($file in $conflictedFiles) {
    Write-Host "Resolving: $file"
    
    # Check if file exists in stage 2 (theirs)
    try {
        $null = git show :2:$file
        # If stage 2 exists, use it
        git show :2:$file | Out-File -FilePath $file -Encoding utf8
        git add $file
        Write-Host "  Resolved using stage 2 (Next.js version)"
    }
    catch {
        Write-Host "  Stage 2 not available for $file, trying stage 1"
        try {
            $null = git show :1:$file
            git show :1:$file | Out-File -FilePath $file -Encoding utf8
            git add $file
            Write-Host "  Resolved using stage 1"
        }
        catch {
            Write-Host "  Could not resolve $file - manual intervention needed"
        }
    }
}

Write-Host "Conflict resolution complete!"
