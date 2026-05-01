#!/usr/bin/env node
/**
 * scripts/check-no-prisma-product-runtime.mjs
 *
 * Scans apps/web/src/app/api/** and apps/web/src/lib/** for product runtime
 * Prisma usage.
 *
 * Rules:
 * - FAIL: Prisma in routes WITH Rust equivalents -> exit 1
 * - WARN: Prisma in routes WITHOUT Rust equivalents -> exit 0 (unless ALLOW_PRISMA_GAPS=0)
 *
 * RUST_EQUIVALENTS maps API route prefixes to their specific sub-routes that have
 * Rust equivalents. Any sub-route NOT listed is a documented gap.
 */

import { readdir, readFile } from "fs/promises";
import { relative } from "path";

const APPS_API = "apps/web/src/app/api";
const APPS_LIB = "apps/web/src/lib";

const ALLOWED_PATHS = [
  /packages\/database\//,
  /scripts\//,
  /__tests__\//,
  /\.test\./,
  /\.spec\./,
  /test-fixture/,
  /mock/,
];

const RUST_EQUIVALENTS = {
  "apps/web/src/app/api/campaigns": new Set([
    "apps/web/src/app/api/campaigns/route.ts",
    "apps/web/src/app/api/campaigns/[id]/route.ts",
    "apps/web/src/app/api/campaigns/[id]/moves/route.ts",
    "apps/web/src/app/api/campaigns/[id]/moves/[moveId]/tasks/route.ts",
    "apps/web/src/app/api/campaigns/[id]/tasks/route.ts",
    "apps/web/src/app/api/campaigns/[id]/brief/route.ts",
  ]),
  "apps/web/src/app/api/daily-wins": new Set([
    "apps/web/src/app/api/daily-wins/route.ts",
    "apps/web/src/app/api/daily-wins/[id]/route.ts",
    "apps/web/src/app/api/daily-wins/today/route.ts",
  ]),
  "apps/web/src/app/api/nudges": new Set([
    "apps/web/src/app/api/nudges/route.ts",
    "apps/web/src/app/api/nudges/[id]/route.ts",
  ]),
  "apps/web/src/app/api/intel": new Set(["apps/web/src/app/api/intel/route.ts"]),
  "apps/web/src/app/api/muse": new Set([
    "apps/web/src/app/api/muse/conversations/route.ts",
    "apps/web/src/app/api/muse/conversations/[id]/route.ts",
    "apps/web/src/app/api/muse/conversations/[id]/chat/route.ts",
  ]),
  "apps/web/src/app/api/prl": new Set(["apps/web/src/app/api/prl/decay/route.ts"]),
};

const FORBIDDEN_IMPORTS = ["@raptorflow/database", "prisma."];

async function* walkDir(dir) {
  let entries;
  try {
    entries = await readdir(dir, { withFileTypes: true });
  } catch {
    return;
  }
  for (const entry of entries) {
    const full = dir + "/" + entry.name;
    if (entry.isDirectory()) {
      yield* walkDir(full);
    } else if (
      entry.isFile() &&
      (entry.name.endsWith(".ts") ||
        entry.name.endsWith(".tsx") ||
        entry.name.endsWith(".js") ||
        entry.name.endsWith(".mjs"))
    ) {
      yield full;
    }
  }
}

function isAllowed(filePath) {
  return ALLOWED_PATHS.some((p) => p.test(filePath));
}

function toForwardSlash(p) {
  return p.replace(/\\/g, "/");
}

async function main() {
  const violations = [];
  const docGaps = [];
  const dirs = [APPS_API, APPS_LIB];

  const allowGaps = process.env.ALLOW_PRISMA_GAPS !== "0";

  for (const dir of dirs) {
    for await (const file of walkDir(dir)) {
      if (isAllowed(file)) continue;
      const rel = toForwardSlash(relative(process.cwd(), file));
      const content = await readFile(file, "utf8");

      if (FORBIDDEN_IMPORTS.some((forbidden) => content.includes(forbidden))) {
        const apiRouteKey = rel.split("/").slice(0, 6).join("/");
        const rustEquivs = RUST_EQUIVALENTS[apiRouteKey];

        if (rustEquivs && rustEquivs.has(rel)) {
          violations.push(`${rel}: Prisma in route with Rust equivalent`);
        } else {
          docGaps.push(`${rel}: Prisma in route without Rust equivalent (documented gap)`);
        }
      }
    }
  }

  if (violations.length > 0) {
    console.error("FAIL: Prisma product runtime found where Rust equivalent exists:");
    for (const v of violations) {
      console.error("  " + v);
    }
    console.error("\nThese routes have been migrated to Rust. Remove Prisma usage.");
    process.exit(1);
  }

  if (docGaps.length > 0) {
    if (allowGaps) {
      console.warn("WARN: Prisma in routes without Rust equivalents (documented gaps):");
      for (const g of docGaps) {
        console.warn("  " + g);
      }
      console.warn("\nThese require a follow-up migration patch.");
    } else {
      console.error("FAIL: Prisma in routes without Rust equivalents (ALLOW_PRISMA_GAPS=0):");
      for (const g of docGaps) {
        console.error("  " + g);
      }
      process.exit(1);
    }
  }

  console.log("PASS: No Prisma product runtime violations.");
  if (docGaps.length > 0) {
    console.log(
      `      ${docGaps.length} routes without Rust equivalents documented (allowed in dev mode).`,
    );
  }
  process.exit(0);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
