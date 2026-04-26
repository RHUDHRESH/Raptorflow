@echo off
set CI=true
set GIT_TERMINAL_PROMPT=0
set GIT_EDITOR=:
set EDITOR=:
set GIT_PAGER=cat
set PAGER=cat

echo === PR 223 STATUS ===
gh pr view 223 --json state,mergedAt,mergeCommit

echo === RECENT CI RUNS ===
gh run list --limit 5 --json name,conclusion,status

echo === DONE ===
