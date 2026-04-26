@echo off
set CI=true
set GIT_TERMINAL_PROMPT=0
set GIT_EDITOR=:
set EDITOR=:
set GIT_PAGER=cat
set PAGER=cat
set npm_config_yes=true

echo === STATUS ===
git status --short

echo === STAGING ===
git add crates/harness/src/identity.rs database/migrations/0025_avatar_identity_persistence.sql crates/db/src/models.rs crates/db/src/queries.rs schemas/content/ crates/http/src/routes/validation.rs crates/http/Cargo.toml Cargo.toml

echo === COMMITTING ===
git commit -m "feat: Steps 4-5 - content validation + identity persistence"

echo === PUSHING ===
git push origin feat/council-visible-war-room-ui

echo === DONE ===
