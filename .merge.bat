@echo off
set CI=true
set GIT_TERMINAL_PROMPT=0
set GIT_EDITOR=:
set EDITOR=:
set GIT_PAGER=cat
set PAGER=cat
set npm_config_yes=true

echo === MERGING PR 223 ===
gh pr merge 223 --merge --subject "feat: Steps 1-5 - memory, search, AI debate, schema validation, identity persistence"

echo === DONE ===
