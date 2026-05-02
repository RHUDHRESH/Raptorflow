import { publicEnv } from "./env";

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function getAuthToken(): Promise<string | null> {
  if (typeof window === "undefined") return null;

  try {
    for (let attempt = 0; attempt < 10; attempt += 1) {
      const clerk = (
        window as Window & {
          Clerk?: {
            loaded?: boolean;
            session?: {
              getToken?: (options?: { template?: string }) => Promise<string | null>;
            };
          };
        }
      ).Clerk;

      if (clerk?.loaded && clerk.session?.getToken) {
        const token = await Promise.race([
          clerk.session.getToken({ template: "backend" } as never).catch(() => null),
          clerk.session.getToken().catch(() => null),
          new Promise<null>((resolve) => setTimeout(() => resolve(null), 500)),
        ]);
        if (token) return token;
      }

      await new Promise((resolve) => setTimeout(resolve, 50));
    }
  } catch {
    // Clerk not loaded yet or session expired
  }

  return null;
}

export function getApiBaseUrl(): string {
  const base = publicEnv.apiBaseUrl;
  return base.replace(/\/$/, "");
}

export function getWsBaseUrl(): string {
  const apiBase = getApiBaseUrl();
  return apiBase.replace(/^http/, "ws");
}

export async function apiFetch<T>(
  path: string,
  options: {
    token?: string | null;
    method?: string;
    body?: unknown;
    headers?: HeadersInit;
    auth?: boolean;
  } = {},
): Promise<T> {
  const base = getApiBaseUrl();

  const token = options.auth ? (options.token ?? (await getAuthToken())) : null;

  const res = await fetch(`${base}${path}`, {
    method: options.method ?? "GET",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new ApiError(res.status, text || `API request failed with status ${res.status}`);
  }

  return res.json() as Promise<T>;
}

export async function appFetch<T>(
  path: string,
  options: {
    token?: string | null;
    method?: string;
    body?: unknown;
    headers?: HeadersInit;
    auth?: boolean;
  } = {},
): Promise<T> {
  const token = options.auth ? (options.token ?? null) : null;

  const res = await fetch(path, {
    method: options.method ?? "GET",
    credentials: "include",
    cache: "no-store",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new ApiError(res.status, text || `API request failed with status ${res.status}`);
  }

  return res.json() as Promise<T>;
}

export function unwrapList<T>(payload: unknown, keys: string[], fallback: T[] = []): T[] {
  if (Array.isArray(payload)) return payload as T[];
  if (payload && typeof payload === "object") {
    for (const key of keys) {
      const value = (payload as Record<string, unknown>)[key];
      if (Array.isArray(value)) return value as T[];
    }
  }
  return fallback;
}

export function unwrapItem<T>(payload: unknown, keys: string[]): T | null {
  if (payload && typeof payload === "object") {
    for (const key of keys) {
      const value = (payload as Record<string, unknown>)[key];
      if (value && typeof value === "object") {
        return value as T;
      }
    }
  }
  return (payload as T | null) ?? null;
}
