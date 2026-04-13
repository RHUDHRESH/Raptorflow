import { access, readFile } from "node:fs/promises";
import { constants } from "node:fs";
import { join } from "node:path";

const appFiles = [
  "apps/web/src/app/(app)/app/page.tsx",
  "apps/web/src/app/(app)/layout.tsx",
  "apps/web/src/app/(app)/billing/page.tsx",
  "apps/web/src/app/(app)/campaigns/page.tsx",
  "apps/web/src/app/(app)/campaigns/[campaignId]/page.tsx",
  "apps/web/src/app/(app)/campaigns/[campaignId]/moves/page.tsx",
  "apps/web/src/app/(app)/campaigns/[campaignId]/moves/[moveId]/page.tsx",
  "apps/web/src/app/(app)/campaigns/[campaignId]/tasks/page.tsx",
  "apps/web/src/app/(app)/campaigns/[campaignId]/tasks/[taskId]/page.tsx",
  "apps/web/src/app/(app)/campaigns/[campaignId]/replanning/page.tsx",
  "apps/web/src/app/(app)/campaigns/[campaignId]/performance/page.tsx",
  "apps/web/src/app/(app)/foundation/page.tsx",
  "apps/web/src/app/(app)/foundation/[step]/page.tsx",
  "apps/web/src/app/(app)/intel/page.tsx",
  "apps/web/src/app/(app)/intel/[artifactId]/page.tsx",
  "apps/web/src/app/(app)/nudges/page.tsx",
  "apps/web/src/app/(app)/nudges/[nudgeId]/page.tsx",
  "apps/web/src/app/(app)/office/page.tsx",
  "apps/web/src/app/(app)/muse/page.tsx",
  "apps/web/src/app/(app)/council/page.tsx",
  "apps/web/src/app/(app)/daily-wins/page.tsx",
  "apps/web/src/app/(app)/internal/debug/page.tsx",
  "apps/web/src/app/(app)/uploads/page.tsx",
  "apps/web/src/app/(app)/uploads/assets/page.tsx",
  "apps/web/src/app/(app)/uploads/assets/[assetId]/page.tsx",
  "apps/web/src/app/(app)/settings/page.tsx",
  "apps/web/src/components/layout/app-shell.tsx",
  "apps/web/src/components/layout/route-shell.tsx",
  "apps/web/src/components/layout/shell-sidebar.tsx",
  "crates/auth/src/lib.rs",
  "crates/http/src/lib.rs",
  "crates/jobs/src/lib.rs"
];

const expectedNav = [
  "/app",
  "/foundation",
  "/campaigns",
  "/intel",
  "/nudges",
  "/uploads",
  "/office",
  "/muse",
  "/council",
  "/daily-wins",
  "/billing",
  "/settings"
];

const authMarkers = ["protected_router", "websocket_bootstrap", "AuthContext", "TenantContext"];

function filePath(relativePath) {
  return join(process.cwd(), ...relativePath.split("/"));
}

async function assertFilesExist(files) {
  for (const relativePath of files) {
    await access(filePath(relativePath), constants.F_OK);
  }
}

function extractNavigation(source) {
  const block = source.match(/const navigation = \[(?<items>[\s\S]*?)\]\s*(?:as const[\s\S]*?)?;/);
  if (!block?.groups?.items) {
    throw new Error("Sidebar navigation array missing.");
  }

  return [...block.groups.items.matchAll(/href:\s*"([^"]+)"/g)].map((match) => match[1]);
}

function assertExactList(label, actual, expected) {
  const actualJson = JSON.stringify(actual);
  const expectedJson = JSON.stringify(expected);
  if (actualJson !== expectedJson) {
    throw new Error(`${label} mismatch.\nexpected: ${expectedJson}\nactual:   ${actualJson}`);
  }
}

async function main() {
  await assertFilesExist(appFiles);

  const sidebar = await readFile(
    filePath("apps/web/src/components/layout/shell-sidebar.tsx"),
    "utf8"
  );
  const navigation = extractNavigation(sidebar);
  assertExactList("sidebar navigation", navigation, expectedNav);

  const auth = await readFile(filePath("crates/auth/src/lib.rs"), "utf8");
  const http = await readFile(filePath("crates/http/src/lib.rs"), "utf8");

  for (const marker of authMarkers) {
    if (!auth.includes(marker)) {
      throw new Error(`Auth scaffold is missing marker: ${marker}`);
    }
  }

  if (!http.includes("protected_router(settings.clone()")) {
    throw new Error("HTTP router is missing protected route wrapping.");
  }

  if (!http.includes("ws_router")) {
    throw new Error("HTTP router is missing websocket routing.");
  }

  console.log(
    `smoke check passed (${appFiles.length} files, ${navigation.length} nav entries, auth wired)`
  );
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
});
