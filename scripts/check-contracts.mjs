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
  "/scan/quick",
  "/scan/deep",
  "/scan/:scan_id",
  "/versions",
  "/versions/:version_id",
  "/versions/:version_id/sections/:section",
];

for (const token of foundationRouteTokens) {
  if (!foundationRust.includes(token)) {
    console.error(`Missing foundation route scaffold coverage: ${token}`);
    process.exit(1);
  }
}

const foundationRestTokens = [
  "/api/v1/foundation/scan/quick",
  "/api/v1/foundation/scan/deep",
  "/api/v1/foundation/scans/:scanId",
  "/api/v1/foundation/versions",
  "/api/v1/foundation/versions/:versionId",
  "/api/v1/foundation/versions/:versionId/sections/:section",
];

for (const token of foundationRestTokens) {
  if (!restContract?.includes(token)) {
    console.error(`Missing foundation REST scaffold coverage: ${token}`);
    process.exit(1);
  }
}

const foundationOpenApiTokens = [
  "/api/v1/foundation/scan/quick",
  "/api/v1/foundation/scan/deep",
  "/api/v1/foundation/scans/{scanId}",
  "/api/v1/foundation/versions",
  "/api/v1/foundation/versions/{versionId}",
  "/api/v1/foundation/versions/{versionId}/sections/{section}",
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
  "/api/v1/foundation/scan/quick",
  "/api/v1/foundation/scan/deep",
  "/api/v1/foundation/scans/{scanId}",
  "/api/v1/foundation/versions",
  "/api/v1/foundation/versions/{versionId}",
  "/api/v1/foundation/versions/{versionId}/sections/{section}",
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
  "/api/v1/foundation/scans/:scanId",
  "/api/v1/foundation/versions",
  "/api/v1/foundation/versions/:versionId",
  "/api/v1/foundation/versions/:versionId/sections/:section",
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
