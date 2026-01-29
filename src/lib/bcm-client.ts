import type { BusinessContext } from '@/lib/business-context';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export type ManifestSource = 'memory' | 'database' | 'api_rebuild' | string;

export interface ManifestResponse {
  success: boolean;
  manifest?: BusinessContext;
  version?: string;
  checksum?: string;
  generated_at?: string;
  source: ManifestSource;
  error?: string;
}

export interface ManifestSummary {
  id: string;
  workspace_id: string;
  version_major: number;
  version_minor: number;
  version_patch: number;
  checksum: string;
  created_at: string;
  source?: ManifestSource;
}

export interface CacheStats {
  cache_hits: number;
  cache_misses: number;
  hit_rate_percent: number;
  connection_errors: number;
  storage_errors: number;
  total_operations: number;
  redis_memory_used?: string;
  redis_connected_clients?: number;
  workspace_cached?: boolean;
}

export interface HealthCheck {
  redis: {
    redis_available: boolean;
    connection_status: string;
    response_time_ms?: number;
    error?: string;
  };
  database: string;
}

interface FetchOptions {
  signal?: AbortSignal;
  tier?: 'tier0' | 'tier1' | 'tier2';
  use_fallback?: boolean;
}

const defaultHeaders = {
  'Content-Type': 'application/json',
};

async function handleJsonResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorPayload = await response.json().catch(() => ({}));
    const message = errorPayload?.detail || response.statusText || 'Request failed';
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}

export async function getLatestManifest(
  workspaceId: string,
  options?: FetchOptions,
): Promise<ManifestResponse> {
  const url = new URL(`${API_BASE_URL}/api/v1/context/manifest`);
  url.searchParams.set('workspace_id', workspaceId);
  url.searchParams.set('tier', options?.tier || 'tier0');
  url.searchParams.set('use_fallback', String(options?.use_fallback ?? true));

  const response = await fetch(url.toString(), {
    method: 'GET',
    credentials: 'include',
    signal: options?.signal,
  });

  return handleJsonResponse<ManifestResponse>(response);
}

export async function triggerRebuild(
  workspaceId: string,
  force = false,
  signal?: AbortSignal,
): Promise<ManifestResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/context/rebuild`, {
    method: 'POST',
    credentials: 'include',
    headers: defaultHeaders,
    body: JSON.stringify({ workspace_id: workspaceId, force }),
    signal,
  });

  if (response.status === 304) {
    throw new Error('BCM unchanged');
  }

  return handleJsonResponse<ManifestResponse>(response);
}

export async function getManifestHistory(
  workspaceId: string,
  limit = 5,
  signal?: AbortSignal,
): Promise<{ success: boolean; versions: ManifestSummary[]; total_count: number }> {
  const url = new URL(`${API_BASE_URL}/api/v1/context/history`);
  url.searchParams.set('workspace_id', workspaceId);
  url.searchParams.set('limit', String(limit));

  const response = await fetch(url.toString(), {
    method: 'GET',
    credentials: 'include',
    signal,
  });

  return handleJsonResponse<{ success: boolean; versions: ManifestSummary[]; total_count: number }>(response);
}

export async function exportManifest(
  workspaceId: string,
  format: 'json' | 'markdown' = 'json',
  signal?: AbortSignal,
): Promise<Blob> {
  const url = new URL(`${API_BASE_URL}/api/v1/context/export`);
  url.searchParams.set('workspace_id', workspaceId);
  url.searchParams.set('format', format);

  const response = await fetch(url.toString(), {
    method: 'GET',
    credentials: 'include',
    signal,
  });

  if (!response.ok) {
    const errorPayload = await response.json().catch(() => ({}));
    const message = errorPayload?.detail || response.statusText || 'Export failed';
    throw new Error(message);
  }

  return response.blob();
}

export async function getCacheStats(
  workspaceId?: string,
  signal?: AbortSignal,
): Promise<{ success: boolean; stats: CacheStats; timestamp: string }> {
  const url = new URL(`${API_BASE_URL}/api/v1/context/stats`);
  if (workspaceId) {
    url.searchParams.set('workspace_id', workspaceId);
  }

  const response = await fetch(url.toString(), {
    method: 'GET',
    credentials: 'include',
    signal,
  });

  return handleJsonResponse<{ success: boolean; stats: CacheStats; timestamp: string }>(response);
}

export async function getHealthCheck(
  signal?: AbortSignal,
): Promise<{ success: boolean; health: HealthCheck; timestamp: string }> {
  const response = await fetch(`${API_BASE_URL}/api/v1/context/health`, {
    method: 'GET',
    credentials: 'include',
    signal,
  });

  return handleJsonResponse<{ success: boolean; health: HealthCheck; timestamp: string }>(response);
}

// Utility function to calculate freshness status
export function getFreshnessStatus(generatedAt?: string): {
  status: 'fresh' | 'stale' | 'expired';
  color: 'green' | 'yellow' | 'red';
  daysOld: number;
} {
  if (!generatedAt) {
    return { status: 'expired', color: 'red', daysOld: Infinity };
  }

  const now = new Date();
  const generated = new Date(generatedAt);
  const daysOld = Math.floor((now.getTime() - generated.getTime()) / (1000 * 60 * 60 * 24));

  if (daysOld < 7) {
    return { status: 'fresh', color: 'green', daysOld };
  } else if (daysOld < 14) {
    return { status: 'stale', color: 'yellow', daysOld };
  } else {
    return { status: 'expired', color: 'red', daysOld };
  }
}

// Utility function to format file size
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Utility function to download blob as file
export function downloadBlob(blob: Blob, filename: string): void {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}
