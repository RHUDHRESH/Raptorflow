@echo off
gh run view 24961379722 --json jobs --jq ".jobs[] | {name, status, conclusion, url}" 
