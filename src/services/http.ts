export class HttpError extends Error {
  status: number;
  url: string;
  body: unknown;

  constructor(message: string, opts: { status: number; url: string; body: unknown }) {
    super(message);
    this.name = "HttpError";
    this.status = opts.status;
    this.url = opts.url;
    this.body = opts.body;
  }
}

type ApiRequestOptions = Omit<RequestInit, "headers"> & {
  headers?: Record<string, string>;
  workspaceId?: string;
};

const API_BASE = "/api/proxy/v1";

async function readBody(response: Response): Promise<unknown> {
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    try {
      return await response.json();
    } catch {
      return null;
    }
  }
  try {
    return await response.text();
  } catch {
    return null;
  }
}

export async function apiRequest<T>(
  path: string,
  options: ApiRequestOptions = {}
): Promise<T> {
  const url = `${API_BASE}${path.startsWith("/") ? path : `/${path}`}`;

  const headers: Record<string, string> = {
    ...(options.headers ?? {}),
  };

  if (options.workspaceId) {
    headers["x-workspace-id"] = options.workspaceId;
  }

  // Default JSON content-type when sending a string body (callers can override).
  if (typeof options.body === "string" && !headers["content-type"]) {
    headers["content-type"] = "application/json";
  }

  const response = await fetch(url, {
    ...options,
    headers,
    cache: "no-store",
  });

  if (!response.ok) {
    const body = await readBody(response);
    const message =
      typeof body === "object" && body && "detail" in body
        ? String((body as any).detail)
        : `Request failed (${response.status})`;
    throw new HttpError(message, { status: response.status, url, body });
  }

  // 204 No Content
  if (response.status === 204) {
    return undefined as T;
  }

  const body = await readBody(response);
  return body as T;
}

