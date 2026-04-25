#!/usr/bin/env node
/**
 * Qdrant Reality Smoke Test
 *
 * Verifies Qdrant can:
 * 1. Respond to health check
 * 2. Create a collection with vector size 4, cosine distance
 * 3. Upsert a point
 * 4. Search/query the point
 * 5. Delete the collection
 *
 * Environment:
 * - QDRANT_SMOKE_URL         (default: http://localhost:6333)
 * - QDRANT_SMOKE_API_KEY     (optional)
 * - QDRANT_SMOKE_COLLECTION_PREFIX (default: raptorflow_smoke)
 *
 * Safety:
 * - Uses only random smoke collection names (never touches production collections)
 * - Cleans up after itself
 * - Does not run by default in CI
 */

const QDRANT_URL = process.env.QDRANT_SMOKE_URL || "http://localhost:6333";
const API_KEY = process.env.QDRANT_SMOKE_API_KEY || null;
const COLLECTION_PREFIX = process.env.QDRANT_SMOKE_COLLECTION_PREFIX || "raptorflow_smoke";

function headers() {
  const h = { "Content-Type": "application/json" };
  if (API_KEY) h["api-key"] = API_KEY;
  return h;
}

async function fetchWithTimeout(url, options, timeoutMs = 10000) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(url, { ...options, signal: controller.signal });
    clearTimeout(timeout);
    return res;
  } catch (err) {
    clearTimeout(timeout);
    throw err;
  }
}

async function checkLiveness() {
  process.stdout.write("[SMOKE QDRANT] Step 1: GET /healthz ... ");
  const maxAttempts = 5;
  let lastError = null;
  for (let i = 0; i < maxAttempts; i++) {
    try {
      const res = await fetchWithTimeout(`${QDRANT_URL}/healthz`, {
        headers: headers(),
      });
      if (!res.ok) {
        throw new Error(`Health check failed: ${res.status} ${res.statusText}`);
      }
      const text = await res.text();
      console.log("PASS (status:", res.status, ")");
      return true;
    } catch (err) {
      lastError = err;
      if (i < maxAttempts - 1) {
        process.stdout.write(`retry (${i + 1}/${maxAttempts})... `);
        await new Promise((r) => setTimeout(r, 2000));
      }
    }
  }
  console.log("FAIL:", lastError?.message || "Unknown error");
  return false;
}

async function createCollection(collectionName) {
  process.stdout.write(`[SMOKE QDRANT] Step 2: POST /collections/${collectionName} ... `);
  try {
    const res = await fetchWithTimeout(`${QDRANT_URL}/collections/${collectionName}`, {
      method: "PUT",
      headers: headers(),
      body: JSON.stringify({
        vectors: {
          size: 4,
          distance: "Cosine",
        },
      }),
    });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Create collection failed: ${res.status} ${text}`);
    }
    const data = await res.json();
    if (data.result !== true && data.status !== "acknowledged") {
      throw new Error(`Unexpected create response: ${JSON.stringify(data)}`);
    }
    console.log("PASS");
    return true;
  } catch (err) {
    console.log("FAIL:", err.message);
    return false;
  }
}

async function waitForCollection(collectionName) {
  process.stdout.write(
    `[SMOKE QDRANT] Step 2b: Wait for collection '${collectionName}' to be ready ... `,
  );
  const maxAttempts = 10;
  for (let i = 0; i < maxAttempts; i++) {
    try {
      const res = await fetchWithTimeout(`${QDRANT_URL}/collections/${collectionName}`, {
        headers: headers(),
      });
      if (res.ok) {
        const data = await res.json();
        if (data.result?.status === "green" || data.result?.status === "yellow") {
          console.log(`PASS (${i + 1} attempts)`);
          return true;
        }
      }
    } catch (_) {
      /* retry */
    }
    await new Promise((r) => setTimeout(r, 500));
  }
  console.log("FAIL: Collection not ready after 10 attempts");
  return false;
}

async function upsertPoint(collectionName) {
  process.stdout.write(`[SMOKE QDRANT] Step 3: PUT /collections/${collectionName}/points ... `);
  try {
    const res = await fetchWithTimeout(`${QDRANT_URL}/collections/${collectionName}/points`, {
      method: "PUT",
      headers: headers(),
      body: JSON.stringify({
        points: [
          {
            id: 1,
            vector: [0.1, 0.2, 0.3, 0.4],
            payload: { smoke: true, source: "runtime_reality" },
          },
        ],
      }),
    });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Upsert failed: ${res.status} ${text}`);
    }
    const data = await res.json();
    if (data.result?.upserted !== 1) {
      throw new Error(`Unexpected upsert response: ${JSON.stringify(data)}`);
    }
    console.log("PASS");
    return true;
  } catch (err) {
    console.log("FAIL:", err.message);
    return false;
  }
}

async function searchPoint(collectionName) {
  process.stdout.write(
    `[SMOKE QDRANT] Step 4: POST /collections/${collectionName}/points/search ... `,
  );
  try {
    const res = await fetchWithTimeout(
      `${QDRANT_URL}/collections/${collectionName}/points/search`,
      {
        method: "POST",
        headers: headers(),
        body: JSON.stringify({
          vector: [0.1, 0.2, 0.3, 0.4],
          limit: 1,
          with_payload: true,
        }),
      },
    );
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Search failed: ${res.status} ${text}`);
    }
    const data = await res.json();
    const results = data.result || [];
    if (results.length === 0) {
      throw new Error("No search results returned");
    }
    const point = results[0];
    if (point.payload?.smoke !== true) {
      throw new Error(`Unexpected payload: ${JSON.stringify(point.payload)}`);
    }
    console.log(`PASS (found ${results.length} result(s))`);
    return true;
  } catch (err) {
    console.log("FAIL:", err.message);
    return false;
  }
}

async function deleteCollection(collectionName) {
  process.stdout.write(`[SMOKE QDRANT] Step 5: DELETE /collections/${collectionName} ... `);
  try {
    const res = await fetchWithTimeout(`${QDRANT_URL}/collections/${collectionName}`, {
      method: "DELETE",
      headers: headers(),
    });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Delete failed: ${res.status} ${text}`);
    }
    console.log("PASS");
    return true;
  } catch (err) {
    console.log("WARN: Cleanup delete failed (non-fatal):", err.message);
    return false;
  }
}

async function main() {
  console.log("=== QDRANT RUNTIME REALITY SMOKE TEST ===");
  console.log(`[SMOKE QDRANT] Target: ${QDRANT_URL}`);
  if (API_KEY) {
    console.log("[SMOKE QDRANT] Using API key: YES");
  } else {
    console.log("[SMOKE QDRANT] Using API key: NO (anonymous)");
  }

  const timestamp = Date.now();
  const random = Math.random().toString(36).slice(2, 8);
  const collectionName = `${COLLECTION_PREFIX}_${timestamp}_${random}`;
  console.log(`[SMOKE QDRANT] Smoke collection: ${collectionName}`);
  console.log("");

  let passed = true;

  // Step 1: Health check
  if (!(await checkLiveness())) {
    passed = false;
    console.log("");
    console.log("[SMOKE QDRANT] FINAL: FAIL — Liveness check failed");
    process.exit(1);
  }

  // Step 2: Create collection
  if (!(await createCollection(collectionName))) {
    passed = false;
  }

  if (passed) {
    // Step 2b: Wait for collection to be ready
    if (!(await waitForCollection(collectionName))) {
      passed = false;
    }
  }

  // Step 3: Upsert point
  if (passed) {
    if (!(await upsertPoint(collectionName))) {
      passed = false;
    }
  }

  // Step 4: Search point
  if (passed) {
    if (!(await searchPoint(collectionName))) {
      passed = false;
    }
  }

  // Step 5: Delete collection (cleanup)
  const deleted = await deleteCollection(collectionName);
  if (!deleted) {
    console.log("[SMOKE QDRANT] WARN: Collection cleanup failed — may need manual removal");
  }

  console.log("");
  if (passed) {
    console.log("[SMOKE QDRANT] FINAL: PASS — All Qdrant smoke checks passed");
    process.exit(0);
  } else {
    console.log("[SMOKE QDRANT] FINAL: FAIL — One or more smoke checks failed");
    process.exit(1);
  }
}

main().catch((err) => {
  console.error("[SMOKE QDRANT] Unexpected error:", err);
  process.exit(1);
});
