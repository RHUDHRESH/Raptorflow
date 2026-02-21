import { apiRequest } from "./http";
import type { RICP, CoreMessaging, Channel } from "@/types/foundation";

// ──────────────────────────────────────────────────────────────────────────────
// Types used by the Foundation PAGE (positioning / icps / messaging)
// ──────────────────────────────────────────────────────────────────────────────

type LockStatus = "draft" | "locked";

interface LockableSection {
  status: LockStatus;
  lockedAt?: Date;
  lockedBy?: string;
  version: number;
}

export interface ICP {
  id: string;
  name: string;
  description: string;
  firmographics: string;
  painPoints: string[];
  goals: string[];
}

export interface ProofPoint {
  claim: string;
  evidence: string;
  status: "validated" | "pending";
}

export interface FoundationData {
  status: LockStatus;
  progress: number;
  positioning: LockableSection & {
    companyName: string;
    tagline: string;
    valueProp: string;
    problem: string;
    solution: string;
  };
  ricps: RICP[];
  channels: Channel[];
  messaging: CoreMessaging | null;
}

// ──────────────────────────────────────────────────────────────────────────────
// Raw shape returned by the backend /foundation/ endpoint
// ──────────────────────────────────────────────────────────────────────────────

interface FoundationAPIResponse {
  id?: string;
  workspace_id?: string;
  company_info?: Record<string, unknown>;
  mission?: string;
  vision?: string;
  value_proposition?: string;
  brand_voice?: Record<string, unknown>;
  messaging?: Record<string, unknown>;
  status?: string;
  created_at?: string;
  updated_at?: string;
}

// ──────────────────────────────────────────────────────────────────────────────
// Helpers: adapt between backend JSON and the page's FoundationData
// ──────────────────────────────────────────────────────────────────────────────

function toFoundationData(raw: FoundationAPIResponse): FoundationData {
  const ci = (raw.company_info ?? {}) as Record<string, unknown>;
  const msg = (raw.messaging ?? {}) as Record<string, unknown>;
  const bv = (raw.brand_voice ?? {}) as Record<string, unknown>;

  return {
    status: (raw.status as LockStatus) ?? "draft",
    progress: 0, // computed client-side from fields
    positioning: {
      status: (ci.positioning_status as LockStatus) ?? "draft",
      version: (ci.positioning_version as number) ?? 1,
      companyName: (ci.company_name as string) ?? "",
      tagline: (ci.tagline as string) ?? "",
      valueProp: (raw.value_proposition as string) ?? "",
      problem: (ci.problem as string) ?? "",
      solution: (ci.solution as string) ?? "",
      lockedAt: ci.positioning_locked_at
        ? new Date(ci.positioning_locked_at as string)
        : undefined,
    },
    ricps: Array.isArray(ci.icps) ? (ci.icps as RICP[]) : [],
    channels: [],
    messaging: Object.keys(msg).length > 0 ? (msg as unknown as CoreMessaging) : null,
  };
}

function toBackendPayload(data: FoundationData): Record<string, unknown> {
  return {
    company_info: {
      company_name: data.positioning.companyName,
      tagline: data.positioning.tagline,
      problem: data.positioning.problem,
      solution: data.positioning.solution,
      positioning_status: data.positioning.status,
      positioning_version: data.positioning.version,
      positioning_locked_at: data.positioning.lockedAt?.toISOString(),
      icps: data.ricps,
    },
    value_proposition: data.positioning.valueProp,
    messaging: data.messaging || {},
    status: data.status,
  };
}

// ──────────────────────────────────────────────────────────────────────────────
// Empty / default foundation data
// ──────────────────────────────────────────────────────────────────────────────

export const EMPTY_FOUNDATION: FoundationData = {
  status: "draft",
  progress: 0,
  positioning: {
    status: "draft",
    version: 1,
    companyName: "",
    tagline: "",
    valueProp: "",
    problem: "",
    solution: "",
  },
  ricps: [],
  channels: [],
  messaging: null,
};

// ──────────────────────────────────────────────────────────────────────────────
// Service
// ──────────────────────────────────────────────────────────────────────────────

export const foundationService = {
  /** Fetch the foundation for a workspace, adapted to the page's FoundationData shape. */
  async get(workspaceId: string): Promise<FoundationData> {
    const raw = await apiRequest<FoundationAPIResponse>("/foundation/", {
      method: "GET",
      workspaceId,
    });
    return toFoundationData(raw);
  },

  /** Persist foundation data back to the backend. */
  async save(
    workspaceId: string,
    data: FoundationData
  ): Promise<FoundationData> {
    const payload = toBackendPayload(data);
    const raw = await apiRequest<FoundationAPIResponse>("/foundation/", {
      method: "PUT",
      workspaceId,
      body: JSON.stringify(payload),
    });
    return toFoundationData(raw);
  },
};
