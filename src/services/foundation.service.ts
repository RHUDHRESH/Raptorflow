import { apiRequest } from "./http";

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
  icps: ICP[];
  messaging: LockableSection & {
    oneLiner: string;
    elevatorPitch: string;
    keyMessages: string[];
    proofPoints: ProofPoint[];
  };
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
    icps: Array.isArray(ci.icps) ? (ci.icps as ICP[]) : [],
    messaging: {
      status: (msg.status as LockStatus) ?? "draft",
      version: (msg.version as number) ?? 1,
      oneLiner: (msg.one_liner as string) ?? "",
      elevatorPitch: (msg.elevator_pitch as string) ?? "",
      keyMessages: Array.isArray(msg.key_messages)
        ? (msg.key_messages as string[])
        : [],
      proofPoints: Array.isArray(msg.proof_points)
        ? (msg.proof_points as ProofPoint[])
        : [],
      lockedAt: msg.locked_at
        ? new Date(msg.locked_at as string)
        : undefined,
    },
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
      icps: data.icps,
    },
    value_proposition: data.positioning.valueProp,
    messaging: {
      status: data.messaging.status,
      version: data.messaging.version,
      one_liner: data.messaging.oneLiner,
      elevator_pitch: data.messaging.elevatorPitch,
      key_messages: data.messaging.keyMessages,
      proof_points: data.messaging.proofPoints,
      locked_at: data.messaging.lockedAt?.toISOString(),
    },
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
  icps: [],
  messaging: {
    status: "draft",
    version: 1,
    oneLiner: "",
    elevatorPitch: "",
    keyMessages: [],
    proofPoints: [],
  },
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
