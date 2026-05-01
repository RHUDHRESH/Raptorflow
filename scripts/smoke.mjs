import { constants } from "node:fs";
import { access, readFile } from "node:fs/promises";
import { join } from "node:path";

const root = process.cwd();

const requiredFiles = [
  "package.json",
  "pnpm-lock.yaml",
  "pnpm-workspace.yaml",
  "Cargo.toml",
  "docker-compose.yml",
  "vercel.json",
  "apps/web/src/app/(app)/layout.tsx",
  "apps/web/src/app/api/health/route.ts",
  "apps/web/src/brand/routes.ts",
  "apps/web/src/components/layout/shell-sidebar.tsx",
  "crates/auth/src/lib.rs",
  "crates/http/src/lib.rs",
  "crates/http/src/middleware/auth.rs",
  "crates/http/src/router.rs",
  "crates/jobs/src/lib.rs",
];

const authMarkers = ["ClerkWebhookEvent", "JwtValidator", "TenantContext"];
const httpAuthMarkers = ["AuthContext", "auth_middleware", "require_auth"];

function filePath(relativePath) {
  return join(root, ...relativePath.split("/"));
}

async function fileExists(relativePath) {
  try {
    await access(filePath(relativePath), constants.F_OK);
    return true;
  } catch {
    return false;
  }
}

async function assertFilesExist(files) {
  const missing = [];
  for (const relativePath of files) {
    if (!(await fileExists(relativePath))) {
      missing.push(relativePath);
    }
  }

  if (missing.length > 0) {
    throw new Error(`Missing required files:\n${missing.map((file) => `  - ${file}`).join("\n")}`);
  }
}

function extractRouteHrefs(source) {
  return [...new Set([...source.matchAll(/href:\s*"([^"]+)"/g)].map((match) => match[1]))];
}

function appPageForRoute(href) {
  const segments = href.split("/").filter(Boolean);
  return ["apps/web/src/app/(app)", ...segments, "page.tsx"].join("/");
}

function extractIconRoutes(sidebarSource) {
  const iconMap = sidebarSource.match(/const iconMap:[\s\S]*?=\s*\{(?<body>[\s\S]*?)\};/);
  if (!iconMap?.groups?.body) {
    throw new Error("Sidebar icon map missing.");
  }

  return [...iconMap.groups.body.matchAll(/"([^"]+)":/g)].map((match) => match[1]);
}

function cronRouteFile(cronPath) {
  const segments = cronPath.split("/").filter(Boolean);
  return ["apps/web/src/app", ...segments, "route.ts"].join("/");
}

async function main() {
  await assertFilesExist(requiredFiles);

  if (await fileExists("apps/web/vercel.json")) {
    throw new Error("Use the root vercel.json only; apps/web/vercel.json must not exist.");
  }

  const [routesSource, sidebarSource, authSource, httpAuthSource, routerSource, vercelSource] =
    await Promise.all([
      readFile(filePath("apps/web/src/brand/routes.ts"), "utf8"),
      readFile(filePath("apps/web/src/components/layout/shell-sidebar.tsx"), "utf8"),
      readFile(filePath("crates/auth/src/lib.rs"), "utf8"),
      readFile(filePath("crates/http/src/middleware/auth.rs"), "utf8"),
      readFile(filePath("crates/http/src/router.rs"), "utf8"),
      readFile(filePath("vercel.json"), "utf8"),
    ]);

  const routeHrefs = extractRouteHrefs(routesSource);
  if (routeHrefs.length === 0) {
    throw new Error("No route metadata found in apps/web/src/brand/routes.ts.");
  }

  await assertFilesExist(routeHrefs.map(appPageForRoute));

  if (!sidebarSource.includes("routeGroups.map")) {
    throw new Error("Sidebar must render from routeGroups so navigation has one metadata source.");
  }

  const iconRoutes = new Set(extractIconRoutes(sidebarSource));
  const missingIcons = routeHrefs.filter((href) => !iconRoutes.has(href));
  if (missingIcons.length > 0) {
    throw new Error(`Sidebar icon map is missing routes: ${missingIcons.join(", ")}`);
  }

  for (const marker of authMarkers) {
    if (!authSource.includes(marker)) {
      throw new Error(`Auth scaffold is missing marker: ${marker}`);
    }
  }

  for (const marker of httpAuthMarkers) {
    if (!httpAuthSource.includes(marker)) {
      throw new Error(`HTTP auth middleware is missing marker: ${marker}`);
    }
  }

  if (!routerSource.includes("protected_router(shared_state.clone())")) {
    throw new Error("HTTP router is missing protected route wrapping.");
  }

  if (!routerSource.includes('"/api/v1/office/ws"')) {
    throw new Error("HTTP router is missing office websocket routing.");
  }

  const vercelConfig = JSON.parse(vercelSource);
  const cronFiles = (vercelConfig.crons ?? []).map((cron) => cronRouteFile(cron.path));
  await assertFilesExist(cronFiles);

  console.log(
    `smoke check passed (${routeHrefs.length} nav routes, ${cronFiles.length} cron routes, root deploy config)`,
  );
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
});
