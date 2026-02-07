import { NextRequest, NextResponse } from "next/server";

const DEFAULT_BACKEND_URL =
  process.env.BACKEND_API_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000";

const INTERNAL_API_TOKEN = process.env.INTERNAL_API_TOKEN;

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

const FORWARDED_CONTEXT_HEADERS = [
  "x-user-id",
  "x-user-role",
  "x-user-email",
  "x-workspace-id",
  "x-workspace-slug",
];

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

  // Forward auth headers (Supabase JWT)
  const authorization = request.headers.get("authorization");
  if (authorization) {
    headers.set("authorization", authorization);
  }

  // Forward cookies (Supabase session cookies)
  const cookie = request.headers.get("cookie");
  if (cookie) {
    headers.set("cookie", cookie);
  }

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

  // Forward context headers set by middleware (user/workspace)
  for (const h of FORWARDED_CONTEXT_HEADERS) {
    const val = request.headers.get(h);
    if (val) {
      headers.set(h, val);
    }
  }

  // Add internal service token for privileged backend access
  if (INTERNAL_API_TOKEN) {
    headers.set("x-internal-token", INTERNAL_API_TOKEN);
  }

  const isBodyAllowed = !["GET", "HEAD"].includes(request.method);

  try {
    const response = await fetch(backendUrl.toString(), {
      method: request.method,
      headers,
      body: isBodyAllowed ? request.body : undefined,
      redirect: "manual",
      signal: AbortSignal.timeout(30_000),
    });

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
