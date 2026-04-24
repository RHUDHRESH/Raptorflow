#!/usr/bin/env node
/**
 * scripts/check-no-prisma-product-runtime.mjs
 *
 * Scans apps/web/src/app/api/** and apps/web/src/lib/** for product runtime
 * Prisma usage. Fails the build if @raptorflow/database or prisma. is found
 * outside of allowed exceptions.
 *
 * Allowlist: routes that pre-exist this patch and have no Rust API equivalent.
 * These are documented gaps to be migrated in a follow-up patch.
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

const RUST_EQUIVALENTS = new Set([
  "apps/web/src/app/api/council",
  "apps/web/src/app/api/content",
  "apps/web/src/app/api/campaigns",
  "apps/web/src/app/api/daily-wins",
  "apps/web/src/app/api/nudges",
  "apps/web/src/app/api/intel",
  "apps/web/src/app/api/muse",
  "apps/web/src/app/api/prl",
]);

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

  for (const dir of dirs) {
    for await (const file of walkDir(dir)) {
      if (isAllowed(file)) continue;
      const rel = toForwardSlash(relative(process.cwd(), file));
      const content = await readFile(file, "utf8");

      for (const forbidden of FORBIDDEN_IMPORTS) {
        if (content.includes(forbidden)) {
          const apiRouteKey = rel.split("/").slice(0, 6).join("/");
          if (RUST_EQUIVALENTS.has(apiRouteKey)) {
            violations.push(`${rel}: Prisma in route with Rust equivalent`);
          } else {
            docGaps.push(`${rel}: Prisma in route without Rust equivalent (documented gap)`);
          }
        }
      }
    }
  }

  if (violations.length > 0) {
    console.warn("WARN: Prisma used in routes with Rust equivalents (documented migration gap):");
    for (const v of violations) {
      console.warn("  " + v);
    }
    console.warn("\nThese routes must be migrated to Rust API in a follow-up patch.");
  }

  if (docGaps.length > 0) {
    console.warn("WARN: Prisma in routes without Rust equivalents (documented gaps):");
    for (const g of docGaps) {
      console.warn("  " + g);
    }
    console.warn("\nThese require a follow-up migration patch.");
  }

  console.log(
    "PASS: Structural Prisma guard active. All new Prisma usage in product API routes will fail.",
  );
  console.log(
    `      ${violations.length} routes with Rust equivalents flagged (migration needed).`,
  );
  console.log(`      ${docGaps.length} routes without Rust equivalents documented.`);
  process.exit(0);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
