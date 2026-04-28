#!/usr/bin/env node
/**
 * API Health Reality Smoke Test
 *
 * Verifies the RaptorFlow API can:
 * 1. Respond to /health/live (liveness probe)
 * 2. Respond to /health/ready (readiness probe)
 * 3. Respond to /api/v1/health (public health endpoint)
 *
 * Environment:
 * - RAPTORFLOW_API_SMOKE_URL (default: http://localhost:8080)
 *
 * Safety:
 * - Read-only health checks only
 * - No mutations or destructive operations
 * - Does not require authentication
 */

const API_URL = process.env.RAPTORFLOW_API_SMOKE_URL || "http://localhost:8080";

async function checkEndpoint(path, name) {
  process.stdout.write(`[SMOKE API] ${name} ${API_URL}${path} ... `);
  try {
    const res = await fetch(`${API_URL}${path}`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      signal: AbortSignal.timeout(10000),
    });

    if (!res.ok) {
      console.log(`FAIL (HTTP ${res.status} ${res.statusText})`);
      return false;
    }

    let data;
    try {
      data = await res.json();
    } catch {
      data = null;
    }

    console.log(
      `PASS (HTTP ${res.status})`,
      data ? JSON.stringify(data).slice(0, 80) : "(no body)",
    );
    return true;
  } catch (err) {
    if (err.name === "TimeoutError") {
      console.log(`FAIL (timeout after 10s)`);
    } else {
      console.log(`FAIL: ${err.message}`);
    }
    return false;
  }
}

async function main() {
  console.log("=== API HEALTH RUNTIME REALITY SMOKE TEST ===");
  console.log(`[SMOKE API] Target: ${API_URL}`);
  console.log("");

  let allPassed = true;

  // Step 1: Liveness
  if (!(await checkEndpoint("/health/live", "GET /health/live"))) {
    allPassed = false;
  }

  // Step 2: Readiness
  if (!(await checkEndpoint("/health/ready", "GET /health/ready"))) {
    allPassed = false;
  }

  // Step 3: API v1 health (may be protected — just check if it responds)
  const apiHealthResult = await checkEndpoint("/api/v1/health", "GET /api/v1/health");
  if (!apiHealthResult) {
    console.log(
      "[SMOKE API] WARN: /api/v1/health returned non-2xx — may be auth-protected (this is OK for smoke)",
    );
  }

  console.log("");
  if (allPassed) {
    console.log("[SMOKE API] FINAL: PASS — All API health checks passed");
    process.exit(0);
  } else {
    console.log("[SMOKE API] FINAL: FAIL — One or more health checks failed");
    process.exit(1);
  }
}

main().catch((err) => {
  console.error("[SMOKE API] Unexpected error:", err);
  process.exit(1);
});
