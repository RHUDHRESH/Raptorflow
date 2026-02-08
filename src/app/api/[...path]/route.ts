import { NextRequest, NextResponse } from "next/server";

const DEFAULT_BACKEND_URL =
  process.env.BACKEND_API_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000";

const HOP_BY_HOP_HEADERS = new Set([
  "connection",
  "keep-alive",
  "proxy-authenticate",
  "proxy-authorization",
  "te",
  "trailer",
  "transfer-encoding",
  "upgrade",
]);

// In reconstruction mode we do not forward auth/session context.
// Tenant boundary is a single header: `x-workspace-id`.
const FORWARDED_HEADERS = ["x-workspace-id", "x-request-id", "x-idempotency-key"];

function resolveBackendPath(pathSegments: string[]): string {
  if (!pathSegments || pathSegments.length === 0) {
    return "/";
  }

  let segments = [...pathSegments];
  if (segments[0] === "proxy") {
    segments = segments.slice(1);
  }

  if (segments[0] === "v1" || segments[0] === "v2") {
    return `/api/${segments.join("/")}`;
  }

  return `/api/v1/${segments.join("/")}`;
}

async function proxyRequest(
  request: NextRequest,
  pathSegments: string[]
) {
  const backendPath = resolveBackendPath(pathSegments);
  const backendUrl = new URL(backendPath, DEFAULT_BACKEND_URL);
  backendUrl.search = new URL(request.url).search;

  const headers = new Headers();

  // Forward content-type
  const contentType = request.headers.get("content-type");
  if (contentType) {
    headers.set("content-type", contentType);
  }

  // Forward accept
  const accept = request.headers.get("accept");
  if (accept) {
    headers.set("accept", accept);
  }

  // Forward only the minimal, explicit headers we support.
  for (const h of FORWARDED_HEADERS) {
    const val = request.headers.get(h);
    if (val) {
      headers.set(h, val);
    }
  }

  const isBodyAllowed = !["GET", "HEAD"].includes(request.method);
  const body = isBodyAllowed ? await request.arrayBuffer() : undefined;

  try {
    const fetchOnce = (url: string) =>
      fetch(url, {
      method: request.method,
      headers,
      body: isBodyAllowed ? body : undefined,
      redirect: "manual",
      signal: AbortSignal.timeout(30_000),
    });

    // FastAPI commonly issues a 307 redirect for trailing-slash normalization.
    // Follow only same-origin redirects (prevents leaking headers to other hosts).
    let response = await fetchOnce(backendUrl.toString());
    for (let i = 0; i < 3 && (response.status === 307 || response.status === 308); i++) {
      const location = response.headers.get("location");
      if (!location) break;

      const nextUrl = new URL(location, backendUrl);
      if (nextUrl.origin !== backendUrl.origin) break;

      response = await fetchOnce(nextUrl.toString());
    }

    const responseHeaders = new Headers(response.headers);
    for (const header of HOP_BY_HOP_HEADERS) {
      responseHeaders.delete(header);
    }
    responseHeaders.delete("content-encoding");
    responseHeaders.delete("content-length");

    return new Response(response.body, {
      status: response.status,
      headers: responseHeaders,
    });
  } catch (error) {
    console.error("[proxy] Backend unreachable:", backendUrl.toString(), error);
    return NextResponse.json(
      { error: "Backend service unavailable", path: backendPath },
      { status: 502 }
    );
  }
}

type RouteContext = { params: Promise<{ path: string[] }> };

export async function GET(request: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  return proxyRequest(request, path);
}

export async function POST(request: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  return proxyRequest(request, path);
}

export async function PUT(request: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  return proxyRequest(request, path);
}

export async function PATCH(request: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  return proxyRequest(request, path);
}

export async function DELETE(request: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  return proxyRequest(request, path);
}

export async function OPTIONS(request: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  return proxyRequest(request, path);
}
