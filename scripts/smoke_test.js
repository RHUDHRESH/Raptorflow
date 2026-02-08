import fs from "node:fs";
import path from "node:path";

const root = process.cwd();

const checks = [
  ["package.json", "Root package.json exists"],
  ["REPO_MAP.md", "Repo map exists (AGENTS.md requirement)"],
  ["API_INVENTORY.md", "API inventory exists (AGENTS.md requirement)"],
  ["AUTH_INVENTORY.md", "Auth inventory exists (AGENTS.md requirement)"],
  ["src/app", "Canonical frontend app exists"],
  ["src/app/api/[...path]/route.ts", "Canonical Next API proxy exists"],
  ["backend/main.py", "Backend ASGI entrypoint exists"],
  ["backend/app_factory.py", "Backend app factory exists"],
  ["backend/api/registry.py", "Backend router registry exists"],
];

const archivedChecks = [
  ["frontend", "frontend/ARCHIVED.md"],
  ["backend/backend-clean", "backend/backend-clean/ARCHIVED.md"],
];

let failed = false;

for (const [relativePath, message] of checks) {
  const fullPath = path.join(root, relativePath);
  if (!fs.existsSync(fullPath)) {
    console.error(`FAIL: ${message} (${relativePath})`);
    failed = true;
  } else {
    console.log(`OK: ${message}`);
  }
}

for (const [dirPath, markerPath] of archivedChecks) {
  const fullDir = path.join(root, dirPath);
  const fullMarker = path.join(root, markerPath);
  if (fs.existsSync(fullDir) && !fs.existsSync(fullMarker)) {
    console.error(
      `FAIL: ${dirPath} exists but missing archive marker (${markerPath})`
    );
    failed = true;
  } else if (fs.existsSync(fullDir)) {
    console.log(`OK: ${dirPath} is marked archived`);
  }
}

if (failed) {
  process.exit(1);
}
