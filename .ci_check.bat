@echo off
set CI=true

echo === CURRENT CI RUN (in progress) ===
gh run list --limit 1 --workflow CI --json databaseId,status,conclusion,headBranch,headSha

echo === LATEST CI RUN ID ===
for /f "tokens=2 delims=: " %%a in ('gh run list --limit 1 --workflow CI --json databaseId --jq ".[0].databaseId"') do set CI_RUN_ID=%%a
echo CI_RUN_ID=%CI_RUN_ID%

echo === CI JOBS ===
gh run view %CI_RUN_ID% --json jobs --jq ".jobs[] | {name, status, conclusion}"
