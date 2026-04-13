import { readFile } from "node:fs/promises";
import { join } from "node:path";

const file = join(process.cwd(), "crates", "jobs", "src", "lib.rs");

const expectedJobs = [
  "swr-consolidation",
  "daily-wins",
  "intel-scan",
  "campaign-replanning",
  "embedding-worker",
  "prediction-resolution",
  "foundation-quick-scan",
  "foundation-deep-scan",
  "foundation-cache-invalidation",
  "content-feedback-loop",
  "monthly-cost-thresholds",
  "avatar-registry-sync",
  "research-request",
  "tool-gateway",
  "intern-dispatch",
  "stream-coordinator",
  "event-harvester"
];

const expectedSurfaces = [
  "research-request",
  "tool-gateway",
  "intern-dispatch",
  "stream-coordinator",
  "event-harvester"
];

const expectedRoutes = [
  "/",
  "/surfaces",
  "/research",
  "/tool-gateway",
  "/intern-dispatch",
  "/stream-coordinator",
  "/event-harvester"
];

function extractSection(source, startMarker, endMarker) {
  const start = source.indexOf(startMarker);
  if (start < 0) {
    throw new Error(`Missing section start: ${startMarker}`);
  }

  const from = start + startMarker.length;
  const end = source.indexOf(endMarker, from);
  if (end < 0) {
    throw new Error(`Missing section end: ${endMarker}`);
  }

  return source.slice(from, end);
}

function extractKeys(section) {
  return [...section.matchAll(/key:\s*"([^"]+)"/g)].map((match) => match[1]);
}

function extractRoutes(section) {
  return [...section.matchAll(/\.route\("([^"]+)"/g)].map((match) => match[1]);
}

function assertExactList(label, actual, expected) {
  const actualJson = JSON.stringify(actual);
  const expectedJson = JSON.stringify(expected);
  if (actualJson !== expectedJson) {
    throw new Error(`${label} mismatch.\nexpected: ${expectedJson}\nactual:   ${actualJson}`);
  }
}

async function main() {
  const source = await readFile(file, "utf8");

  const registrySection = extractSection(
    source,
    "pub fn registry() -> Vec<JobRegistration> {",
    "pub fn harness_surfaces() -> Vec<HarnessSurface> {"
  );
  const harnessSection = extractSection(
    source,
    "pub fn harness_surfaces() -> Vec<HarnessSurface> {",
    "pub fn router() -> Router {"
  );
  const routerSection = extractSection(
    source,
    "pub fn router() -> Router {",
    "async fn trigger_job() -> Json<Value> {"
  );

  const actualJobs = extractKeys(registrySection);
  const actualSurfaces = extractKeys(harnessSection);
  const actualRoutes = extractRoutes(routerSection);

  assertExactList("job registry", actualJobs, expectedJobs);
  assertExactList("harness surfaces", actualSurfaces, expectedSurfaces);
  assertExactList("job routes", actualRoutes, expectedRoutes);

  console.log(
    `job registry check passed (${actualJobs.length} jobs, ${actualSurfaces.length} surfaces, ${actualRoutes.length} routes)`
  );
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
});
