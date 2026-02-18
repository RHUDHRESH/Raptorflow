import fs from "node:fs";
import path from "node:path";

const root = process.cwd();

const checks = [
  ["package.json", "Root package.json exists"],
  ["documentation/REPO_MAP.md", "Repo map exists (documentation contract)"],
  ["documentation/API_INVENTORY.md", "API inventory exists (documentation contract)"],
  ["documentation/AUTH_INVENTORY.md", "Auth inventory exists (documentation contract)"],
  ["documentation/AI_HUB_BEDROCK.md", "AI hub bedrock doc exists (documentation contract)"],
  ["src/app", "Canonical frontend app exists"],
  ["src/app/api/[...path]/route.ts", "Canonical Next API proxy exists"],
  ["backend/main.py", "Backend ASGI entrypoint exists"],
  ["backend/app_factory.py", "Backend app factory exists"],
  ["backend/api/registry.py", "Backend router registry exists"],
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

if (failed) {
  process.exit(1);
}
