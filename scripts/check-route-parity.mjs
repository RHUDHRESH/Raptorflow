#!/usr/bin/env node
/**
 * scripts/check-route-parity.mjs
 *
 * Reads apps/web/src/lib/api.ts to extract frontend /api/v1/* route calls,
 * then reads crates/http/src/router.rs to extract Rust-mounted /api/v1/* routes.
 * Fails if frontend calls a Rust route that is not mounted.
 */

import { readFile } from "fs/promises";

const API_TS = "apps/web/src/lib/api.ts";
const ROUTER_RS = "crates/http/src/router.rs";

function extractFrontendRoutes(content) {
  const routes = new Set();
  const re = /apiFetch\s*\(\s*`([^`]+)`/g;
  let m;
  while ((m = re.exec(content)) !== null) {
    const tpl = m[1];
    if (tpl.includes("/api/v1/")) {
      const normalized = tpl.replace(/\$\{[^}]+\}/g, "{id}").replace(/\/\//g, "/");
      if (!normalized.includes("${")) {
        routes.add(normalized);
      }
    }
  }
  return routes;
}

function extractRustRoutes(content) {
  const routes = new Set();
  const re = /route\(\s*"(\/api\/v1\/[^"]+)"\s*,/g;
  let m;
  while ((m = re.exec(content)) !== null) {
    const route = m[1].replace(/\{[^}]+\}/g, "{id}");
    routes.add(route);
  }
  return routes;
}

async function main() {
  const [apiContent, routerContent] = await Promise.all([
    readFile(API_TS, "utf8"),
    readFile(ROUTER_RS, "utf8"),
  ]);

  const frontend = extractFrontendRoutes(apiContent);
  const rust = extractRustRoutes(routerContent);

  const missing = [];
  for (const route of frontend) {
    const isMounted = [...rust].some(
      (r) => r.replace(/\{[^}]+\}/g, "{id}") === route.replace(/\{[^}]+\}/g, "{id}"),
    );
    if (!isMounted) {
      missing.push(route);
    }
  }

  if (missing.length > 0) {
    console.error("FAIL: Frontend calls unmounted Rust routes:");
    for (const m of missing) {
      console.error("  " + m);
    }
    process.exit(1);
  } else {
    console.log("PASS: All frontend /api/v1/* routes are mounted in Rust router.");
    process.exit(0);
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
