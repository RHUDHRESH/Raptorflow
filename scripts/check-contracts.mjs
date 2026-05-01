import { readFile } from "node:fs/promises";
import { join } from "node:path";

const files = [
  join(process.cwd(), "schemas", "openapi", "api-v1.yaml"),
  join(process.cwd(), "schemas", "ws", "office-event.json"),
  join(process.cwd(), "schemas", "ws", "session-events.json"),
  join(process.cwd(), "schemas", "ws", "council-events.json"),
  join(process.cwd(), "schemas", "domain", "tenant-contract.json"),
  join(process.cwd(), "schemas", "queues", "embedding-job.json"),
  join(process.cwd(), "schemas", "queues", "content-pregeneration-job.json"),
  join(process.cwd(), "packages", "contracts", "src", "index.ts"),
  join(process.cwd(), "packages", "contracts", "src", "domain.ts"),
  join(process.cwd(), "packages", "contracts", "src", "rest.ts"),
  join(process.cwd(), "packages", "contracts", "src", "ws.ts"),
];

const contents = new Map();
for (const file of files) {
  contents.set(file, await readFile(file, "utf8"));
}

const wsContract = contents.get(join(process.cwd(), "packages", "contracts", "src", "ws.ts"));
const restContract = contents.get(join(process.cwd(), "packages", "contracts", "src", "rest.ts"));
const indexContract = contents.get(join(process.cwd(), "packages", "contracts", "src", "index.ts"));
const openApiContract = contents.get(join(process.cwd(), "schemas", "openapi", "api-v1.yaml"));
const councilSchema = contents.get(join(process.cwd(), "schemas", "ws", "council-events.json"));
const tenantSchema = contents.get(join(process.cwd(), "schemas", "domain", "tenant-contract.json"));
const officeSchema = JSON.parse(
  contents.get(join(process.cwd(), "schemas", "ws", "office-event.json")),
);
const officeRust = await readFile(join(process.cwd(), "crates", "office", "src", "lib.rs"), "utf8");
const foundationRust = await readFile(
  join(process.cwd(), "crates", "foundation", "src", "lib.rs"),
  "utf8",
);
const domainContract = contents.get(
  join(process.cwd(), "packages", "contracts", "src", "domain.ts"),
);

for (const token of ["council.position", "council.synthesis"]) {
  if (!wsContract?.includes(token) || !councilSchema?.includes(token)) {
    console.error(`Missing council WS scaffold coverage: ${token}`);
    process.exit(1);
  }
}

const officeEventTypes = officeSchema?.properties?.eventType?.enum ?? [];
for (const token of officeEventTypes) {
  if (!wsContract?.includes(token) || !officeRust.includes(token)) {
    console.error(`Missing office event scaffold coverage: ${token}`);
    process.exit(1);
  }
}

const foundationRouteTokens = [
  "/scan/start",
  "/scan/quick",
  "/scan/deep",
  "/scan/status",
  "/scan/{scan_id}",
];

// ─── Route Diffing ──────────────────────────────────────────────────────
// Extract routes from the Rust router, OpenAPI spec, and frontend API client
// to ensure they stay in sync.

function extractRouterRoutes(content) {
  // Match patterns like "/api/v1/foo/bar" or "/api/v1/foo/{bar}" in router.rs
  const routes = new Set();
  const regex = /"(\/api\/v1\/[^"]+)"/g;
  let match;
  while ((match = regex.exec(content)) !== null) {
    routes.add(match[1]);
  }
  return routes;
}

function extractOpenApiRoutes(content) {
  // Match paths like /api/v1/foo/bar or /api/v1/foo/{bar} in OpenAPI yaml
  const routes = new Set();
  const regex = /^  \/api\/v1\/[^\s:]+/gm;
  let match;
  while ((match = regex.exec(content)) !== null) {
    routes.add(match[0].trim());
  }
  return routes;
}

function extractFrontendRoutes(content) {
  // Match fetch/base URL paths like /api/v1/foo/bar in api.ts
  const routes = new Set();
  const regex = /"(\/api\/v1\/[^"]+)"/g;
  let match;
  while ((match = regex.exec(content)) !== null) {
    routes.add(match[1]);
  }
  return routes;
}

const routerContent = await readFile(
  join(process.cwd(), "crates", "http", "src", "router.rs"),
  "utf8",
);
const frontendApiContent = await readFile(
  join(process.cwd(), "apps", "web", "src", "lib", "api.ts"),
  "utf8",
);

const routerRoutes = extractRouterRoutes(routerContent);
const openApiRoutes = extractOpenApiRoutes(openApiContract);
const frontendRoutes = extractFrontendRoutes(frontendApiContent);

// Known OpenAPI routes that are documented but not yet implemented in the router
const knownOpenApiGaps = new Set([
  "/api/v1/billing",
  "/api/v1/billing/orders",
  "/api/v1/billing/subscriptions/{id}",
  "/api/v1/billing/subscriptions/{id}/cancel",
  "/api/v1/uploads",
  "/api/v1/uploads/download",
  "/api/v1/uploads/{key}",
  "/api/v1/screenshots",
  "/api/v1/exports",
  "/api/v1/exports/download",
  "/api/v1/foundation/versions/{versionId}",
  "/api/v1/foundation/versions/{versionId}/sections/{section}",
]);

let routeDiffErrors = 0;
let knownGapsFound = 0;

// Check OpenAPI routes exist in router
for (const route of openApiRoutes) {
  if (knownOpenApiGaps.has(route)) {
    knownGapsFound++;
    continue;
  }
  // Normalize OpenAPI {param} to router {param} and /scan/{scan_id} to /scan/{scan_id}
  const normalized = route.replace(/\{(\w+)\}/g, "{$1}");
  const matchInRouter = Array.from(routerRoutes).some((r) => {
    const rNormalized = r.replace(/\{(\w+)\}/g, "{$1}");
    return rNormalized === normalized;
  });
  if (!matchInRouter) {
    console.error(`ROUTE DRIFT: OpenAPI path "${route}" not found in Rust router.`);
    routeDiffErrors++;
  }
}

// Check frontend API routes exist in router (or OpenAPI)
for (const route of frontendRoutes) {
  if (route.includes("${")) continue; // Skip template literals
  const matchInRouter = Array.from(routerRoutes).some((r) => {
    const rSegments = r.split("/");
    const fSegments = route.split("/");
    if (rSegments.length !== fSegments.length) return false;
    return rSegments.every((seg, i) => {
      return seg.startsWith("{") || seg === fSegments[i];
    });
  });
  if (!matchInRouter) {
    // Known template pattern — skip dynamic paths
    if (route.includes(":") || route.includes("?")) continue;
    console.error(
      `ROUTE DRIFT: Frontend calls "${route}" but no matching route exists in Rust router.`,
    );
    routeDiffErrors++;
  }
}

if (knownGapsFound > 0) {
  console.log(`Known unimplemented routes (documented, not yet in router): ${knownGapsFound}`);
}
if (routeDiffErrors > 0) {
  console.error(`\nRoute drift detected: ${routeDiffErrors} mismatches.`);
  process.exit(1);
}
console.log("Route diff check passed — router, OpenAPI, and frontend are in sync.");

for (const token of foundationRouteTokens) {
  if (!foundationRust.includes(token)) {
    console.error(`Missing foundation route scaffold coverage: ${token}`);
    process.exit(1);
  }
}

const foundationRestTokens = [
  "/api/v1/foundation/scan/start",
  "/api/v1/foundation/scan/quick",
  "/api/v1/foundation/scan/deep",
  "/api/v1/foundation/scan/status",
  "/api/v1/foundation/scan/{scan_id}",
];

for (const token of foundationRestTokens) {
  if (!restContract?.includes(token)) {
    console.error(`Missing foundation REST scaffold coverage: ${token}`);
    process.exit(1);
  }
}

const foundationOpenApiTokens = [
  "/api/v1/foundation/scan/start",
  "/api/v1/foundation/scan/quick",
  "/api/v1/foundation/scan/deep",
  "/api/v1/foundation/scan/{scan_id}",
  "/api/v1/foundation/scan/status",
];

for (const token of foundationOpenApiTokens) {
  if (!openApiContract?.includes(token)) {
    console.error(`Missing foundation OpenAPI scaffold coverage: ${token}`);
    process.exit(1);
  }
}

const foundationContractTokens = [
  "FoundationScanMode",
  "FoundationScanRequest",
  "FoundationScanStatusRecord",
  "FoundationVersion",
];

for (const token of foundationContractTokens) {
  if (!domainContract?.includes(token) || !foundationRust.includes(token)) {
    console.error(`Missing foundation data contract coverage: ${token}`);
    process.exit(1);
  }
}

for (const token of [
  "foundation.scan.started",
  "foundation.scan.progress",
  "foundation.scan.completed",
  "foundation.version.created",
  "foundation.version.updated",
  "foundation.section.injected",
  "foundation.snapshot.ready",
]) {
  if (!wsContract?.includes(token)) {
    console.error(`Missing foundation websocket scaffold coverage: ${token}`);
    process.exit(1);
  }
}

for (const token of [
  "/api/v1/foundation/scan/start",
  "/api/v1/foundation/scan/quick",
  "/api/v1/foundation/scan/deep",
  "/api/v1/foundation/scan/{scan_id}",
  "/api/v1/foundation/scan/status",
]) {
  if (!openApiContract?.includes(token)) {
    console.error(`Missing OpenAPI foundation scaffold coverage: ${token}`);
    process.exit(1);
  }
}

for (const namespace of [
  "/api/v1/foundation",
  "/api/v1/foundation/scan/quick",
  "/api/v1/foundation/scan/deep",
  "/api/v1/foundation/scan/{scan_id}",
  "/api/v1/campaigns",
  "/api/v1/council",
  "/api/v1/muse",
  "/api/v1/intel",
  "/api/v1/daily-wins",
  "/api/v1/nudges",
  "/api/v1/billing",
  "/api/v1/office",
  "/api/v1/uploads",
  "/api/v1/webhooks/clerk",
  "/api/v1/webhooks/razorpay",
  "/api/v1/internal/jobs",
]) {
  if (!restContract?.includes(namespace)) {
    console.error(`Missing REST namespace scaffold coverage: ${namespace}`);
    process.exit(1);
  }
}

for (const exportName of ["./domain", "./env", "./queues", "./rest", "./ws"]) {
  if (!indexContract?.includes(exportName)) {
    console.error(`Missing contract barrel export: ${exportName}`);
    process.exit(1);
  }
}

if (!tenantSchema?.includes('"required": ["org_id"]')) {
  console.error("Missing tenant contract org_id requirement.");
  process.exit(1);
}

console.log("contract files are present");
