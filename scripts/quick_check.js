// Minimal health check for the scorched-earth reconstruction stack.
// No auth. No payment. No Supabase browser client. No hardcoded secrets.

const backendBase =
  process.env.BACKEND_API_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000";

const nextBase = process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000";

function wantsJson() {
  return process.argv.includes("--json");
}

async function getJson(url) {
  const res = await fetch(url, { method: "GET" });
  const text = await res.text();
  let json = null;
  try {
    json = text ? JSON.parse(text) : null;
  } catch {
    json = null;
  }
  return { ok: res.ok, status: res.status, url, json, text: json ? null : text };
}

async function run() {
  const results = {
    backend: null,
    proxy: null,
  };

  // Backend direct check
  try {
    const url = `${backendBase.replace(/\/$/, "")}/health`;
    results.backend = await getJson(url);
  } catch (e) {
    results.backend = {
      ok: false,
      status: 0,
      url: `${backendBase.replace(/\/$/, "")}/health`,
      error: e instanceof Error ? e.message : String(e),
    };
  }

  // Next.js proxy check (requires Next dev server running)
  try {
    const url = `${nextBase.replace(/\/$/, "")}/api/proxy/v1/health`;
    results.proxy = await getJson(url);
  } catch (e) {
    results.proxy = {
      ok: false,
      status: 0,
      url: `${nextBase.replace(/\/$/, "")}/api/proxy/v1/health`,
      error: e instanceof Error ? e.message : String(e),
    };
  }

  if (wantsJson()) {
    process.stdout.write(`${JSON.stringify(results, null, 2)}\n`);
    return;
  }

  console.log("RaptorFlow reconstruction health check");
  console.log(
    `- Backend: ${results.backend.ok ? "OK" : "FAIL"} (${results.backend.status}) ${results.backend.url}`
  );
  if (!results.backend.ok) {
    console.log(
      `  detail: ${results.backend.error || results.backend.json?.detail || results.backend.text || "unknown"}`
    );
  }

  console.log(
    `- Next proxy: ${results.proxy.ok ? "OK" : "FAIL"} (${results.proxy.status}) ${results.proxy.url}`
  );
  if (!results.proxy.ok) {
    console.log(
      `  detail: ${results.proxy.error || results.proxy.json?.detail || results.proxy.text || "unknown"}`
    );
    console.log("  note: This check requires Next.js to be running (npm run dev).");
  }
}

run().catch((e) => {
  console.error("health-check failed:", e);
  process.exitCode = 1;
});
