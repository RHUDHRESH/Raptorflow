import { supabase } from './supabase';

export type ApiError = {
  detail?: string;
  error?: string;
};

export function getApiUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
}

export async function getSessionOrThrow() {
  const {
    data: { session },
  } = await supabase.auth.getSession();
  if (!session) {
    throw new Error('Authentication required.');
  }
  return session;
}

export async function getAuthHeaders() {
  const session = await getSessionOrThrow();
  return {
    Authorization: `Bearer ${session.access_token}`,
    'X-Tenant-ID': session.user.id,
    'Content-Type': 'application/json',
  };
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${getApiUrl()}${path}`;
  const headers = options.headers || {};
  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const payload = (await response.json().catch(() => ({}))) as ApiError;
    const message =
      payload.detail || payload.error || `Request failed (${response.status}).`;
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}
