import { NextRequest } from "next/server";

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
  params: { path: string[] }
) {
  const backendPath = resolveBackendPath(params.path);
  const backendUrl = new URL(backendPath, DEFAULT_BACKEND_URL);
  backendUrl.search = new URL(request.url).search;

  const headers = new Headers(request.headers);
  headers.delete("host");
  headers.delete("content-length");

  const isBodyAllowed = !["GET", "HEAD"].includes(request.method);

  const response = await fetch(backendUrl.toString(), {
    method: request.method,
    headers,
    body: isBodyAllowed ? request.body : undefined,
    redirect: "manual",
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
}

export async function GET(
  request: NextRequest,
  context: { params: { path: string[] } }
) {
  return proxyRequest(request, context.params);
}

export async function POST(
  request: NextRequest,
  context: { params: { path: string[] } }
) {
  return proxyRequest(request, context.params);
}

export async function PUT(
  request: NextRequest,
  context: { params: { path: string[] } }
) {
  return proxyRequest(request, context.params);
}

export async function PATCH(
  request: NextRequest,
  context: { params: { path: string[] } }
) {
  return proxyRequest(request, context.params);
}

export async function DELETE(
  request: NextRequest,
  context: { params: { path: string[] } }
) {
  return proxyRequest(request, context.params);
}

export async function OPTIONS(
  request: NextRequest,
  context: { params: { path: string[] } }
) {
  return proxyRequest(request, context.params);
}
