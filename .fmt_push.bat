@echo off
echo === ADDING FORMATTED FILES ===
git add -A

echo === COMMITTING ===
git commit -m "fix: cargo fmt formatting"

echo === PUSHING ===
git push origin HEAD

echo === DONE ===

