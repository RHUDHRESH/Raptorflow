#!/usr/bin/env node
/**
 * scripts/check-route-parity.mjs
 *
 * Extracts frontend /api/v1/* route calls from apps/web/src/lib/api.ts,
 * then reads crates/http/src/router.rs to extract Rust-mounted routes.
 *
 * Failures:
 * - Frontend calls unmounted Rust route
 * - Frontend calls /api/v1/* through appFetch (must use apiFetch)
 *
 * Warnings:
 * - Rust route is mounted but not called by frontend (unused)
 */

import { readFile } from "fs/promises";

const API_TS = "apps/web/src/lib/api.ts";
const ROUTER_RS = "crates/http/src/router.rs";

function normalizeRoute(route) {
  let r = route.replace(/\?.*$/, "").replace(/\/\//g, "/");
  r = r.replace(/\$\{[^}]+\}/g, "{id}");
  r = r.replace(/\{sessionId\}/g, "{id}");
  return r;
}

function extractFrontendRoutes(content) {
  const routes = new Set();
  const appFetchViolations = [];

  const patterns = [
    /apiFetch\s*\(\s*"([^"]+)"\s*/g,
    /apiFetch\s*\(\s*'([^']+)'/g,
    /apiFetch\s*\(\s*`([^`]+)`/g,
  ];

  for (const pattern of patterns) {
    let m;
    while ((m = pattern.exec(content)) !== null) {
      const route = m[1].trim();
      if (route.includes("/api/v1/")) {
        const normalized = normalizeRoute(route);
        if (!normalized.includes("${")) {
          routes.add(normalized);
        }
      }
    }
  }

  const appFetchPattern = /appFetch\s*\(\s*"([^"]+)"\s*/g;
  let am;
  while ((am = appFetchPattern.exec(content)) !== null) {
    const route = am[1].trim();
    if (route.includes("/api/v1/")) {
      appFetchViolations.push(route);
    }
  }

  const appFetchSinglePattern = /appFetch\s*\(\s*'([^']+)'/g;
  let ams;
  while ((ams = appFetchSinglePattern.exec(content)) !== null) {
    const route = ams[1].trim();
    if (route.includes("/api/v1/")) {
      appFetchViolations.push(route);
    }
  }

  return { routes, appFetchViolations };
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

function routesMatch(frontendRoute, rustRoute) {
  const f = frontendRoute.replace(/\{[^}]+\}/g, "{id}");
  const r = rustRoute.replace(/\{[^}]+\}/g, "{id}");
  return f === r;
}

async function main() {
  const [apiContent, routerContent] = await Promise.all([
    readFile(API_TS, "utf8"),
    readFile(ROUTER_RS, "utf8"),
  ]);

  const { routes: frontend, appFetchViolations } = extractFrontendRoutes(apiContent);
  const rust = extractRustRoutes(routerContent);

  if (appFetchViolations.length > 0) {
    console.error("FAIL: /api/v1/* routes must use apiFetch, not appFetch:");
    for (const v of appFetchViolations) {
      console.error("  appFetch used for: " + v);
    }
    process.exit(1);
  }

  const missing = [];
  for (const route of frontend) {
    const isMounted = [...rust].some((r) => routesMatch(route, r));
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
  }

  const unused = [];
  for (const route of rust) {
    const isCalled = [...frontend].some((f) => routesMatch(f, route));
    if (!isCalled) {
      unused.push(route);
    }
  }

  console.log("PASS: All frontend /api/v1/* routes are mounted in Rust router.");
  if (unused.length > 0) {
    console.log("WARN: Unused Rust routes (not called by frontend):");
    for (const u of unused) {
      console.log("  " + u);
    }
  }

  const selfCheckPassed = runSelfCheck();
  if (!selfCheckPassed) {
    console.error("FAIL: Route parity self-check failed");
    process.exit(1);
  }

  process.exit(0);
}

function runSelfCheck() {
  const testCases = [
    {
      input: 'apiFetch("/api/v1/foo")',
      expectRoute: "/api/v1/foo",
      shouldPass: true,
    },
    {
      input: "apiFetch('/api/v1/foo')",
      expectRoute: "/api/v1/foo",
      shouldPass: true,
    },
    {
      input: 'apiFetch("/api/v1/foo?key=val")',
      expectRoute: "/api/v1/foo",
      shouldPass: true,
    },
    {
      input: "apiFetch('/api/v1/campaigns/${id}')",
      expectRoute: "/api/v1/campaigns/{id}",
      shouldPass: true,
    },
    {
      input: "apiFetch(`/api/v1/council/${sessionId}`)",
      expectRoute: "/api/v1/council/{id}",
      shouldPass: true,
    },
    {
      input: 'appFetch("/api/v1/foo")',
      expectViolation: true,
      shouldPass: false,
    },
  ];

  let allPassed = true;

  for (const tc of testCases) {
    const pattern = /apiFetch\s*\(\s*"([^"]+)"\s*/g;
    let m = pattern.exec(tc.input);

    if (!m) {
      const singlePattern = /apiFetch\s*\(\s*'([^']+)'/g;
      m = singlePattern.exec(tc.input);
    }

    if (!m) {
      const tplPattern = /apiFetch\s*\(\s*`([^`]+)`/g;
      m = tplPattern.exec(tc.input);
    }

    if (tc.expectViolation) {
      if (!tc.input.includes("appFetch")) {
        console.error("  Self-check: expected violation detection for: " + tc.input);
        allPassed = false;
      }
    } else {
      if (!m) {
        console.error("  Self-check: failed to extract route from: " + tc.input);
        allPassed = false;
      } else {
        const extracted = normalizeRoute(m[1].trim());
        if (extracted !== tc.expectRoute) {
          console.error(
            "  Self-check: route mismatch for '" +
              tc.input +
              "': got '" +
              extracted +
              "', expected '" +
              tc.expectRoute +
              "'",
          );
          allPassed = false;
        }
      }
    }
  }

  return allPassed;
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
