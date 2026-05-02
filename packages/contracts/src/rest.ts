export const restNamespaces = [
  "/api/v1/foundation",
  "/api/v1/foundation/scan/start",
  "/api/v1/foundation/scan/quick",
  "/api/v1/foundation/scan/deep",
  "/api/v1/foundation/scan/status",
  "/api/v1/foundation/scan/{scan_id}",
  "/api/v1/foundation/versions",
  "/api/v1/foundation/versions/:versionId",
  "/api/v1/foundation/versions/:versionId/sections/:section",
  "/api/v1/campaigns",
  "/api/v1/council",
  "/api/v1/muse",
  "/api/v1/intel",
  "/api/v1/intel/signals",
  "/api/v1/intel/signals/{id}",
  "/api/v1/intel/competitors",
  "/api/v1/daily-wins",
  "/api/v1/nudges",
  "/api/v1/billing",
  "/api/v1/office",
  "/api/v1/uploads",
  "/api/v1/webhooks/clerk",
  "/api/v1/webhooks/razorpay",
  "/api/v1/internal/jobs",
  "/api/v1/internal/jobs/surfaces",
  "/api/v1/internal/jobs/research",
  "/api/v1/internal/jobs/tool-gateway",
  "/api/v1/internal/jobs/intern-dispatch",
  "/api/v1/internal/jobs/stream-coordinator",
  "/api/v1/internal/jobs/event-harvester",
  "/api/v1/health",
] as const;

export type RestNamespace = (typeof restNamespaces)[number];

export interface HealthResponse {
  status: "ok" | "degraded" | "error";
  version: string;
  db: "ok" | "unreachable";
}

export interface ApiError {
  error: string;
  detail?: string;
  code?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

export interface OrgContext {
  orgId: string;
  planTier?: string;
}

export interface UserContext {
  userId: string;
  email?: string;
}
