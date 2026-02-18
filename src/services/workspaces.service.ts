import { apiRequest } from "./http";

export type Workspace = {
  id: string;
  name: string;
  slug: string | null;
  settings: Record<string, unknown> | null;
  created_at?: string;
  updated_at?: string;
};

export type OnboardingStepKind = "short_text" | "long_text" | "list" | "url";

export type OnboardingStep = {
  id: string;
  title: string;
  description?: string;
  fields: {
    id: string;
    label: string;
    kind: OnboardingStepKind;
    required: boolean;
    placeholder?: string;
    help?: string | null;
  }[];
};

export type OnboardingStepsResponse = {
  schema_version: string;
  total_steps: number;
  required_steps: string[];
  steps: OnboardingStep[];
};

export type OnboardingStatus = {
  workspace_id: string;
  schema_version: string;
  completed: boolean;
  bcm_ready: boolean;
  completion_pct: number;
  answered_steps: number;
  total_steps: number;
  required_steps: string[];
  missing_required_steps: string[];
  next_step_id?: string | null;
  answers: Record<string, unknown>;
  updated_at?: string | null;
};

export type CompleteOnboardingInput = {
  schema_version: string;
  answers: Record<string, unknown>;
};

export type UpsertOnboardingAnswersInput = {
  schema_version: string;
  answers: Record<string, unknown>;
};

export type CompleteOnboardingResponse = {
  workspace: Workspace;
  onboarding: OnboardingStatus;
  bcm: Record<string, unknown>;
  business_context: Record<string, unknown>;
};

export type CreateWorkspaceInput = {
  name: string;
  slug?: string;
  settings?: Record<string, unknown>;
};

export type UpdateWorkspaceInput = {
  name?: string;
  slug?: string | null;
  settings?: Record<string, unknown> | null;
};

export type WorkspaceSelectionResponse = {
  workspace: Workspace;
};

export type WorkspaceSelectionInput = {
  workspace_id: string;
};

export const workspacesService = {
  async create(input: CreateWorkspaceInput): Promise<Workspace> {
    return apiRequest<Workspace>("/workspaces", {
      method: "POST",
      body: JSON.stringify(input),
    });
  },

  async get(id: string): Promise<Workspace> {
    return apiRequest<Workspace>(`/workspaces/${encodeURIComponent(id)}`, {
      method: "GET",
    });
  },

  async update(id: string, updates: UpdateWorkspaceInput): Promise<Workspace> {
    return apiRequest<Workspace>(`/workspaces/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: JSON.stringify(updates),
    });
  },

  async getDefaultForCurrentUser(): Promise<WorkspaceSelectionResponse> {
    return apiRequest<WorkspaceSelectionResponse>("/workspaces/me/default", {
      method: "GET",
    });
  },

  async selectForCurrentUser(
    payload: WorkspaceSelectionInput
  ): Promise<WorkspaceSelectionResponse> {
    return apiRequest<WorkspaceSelectionResponse>("/workspaces/me/select", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async getOnboardingSteps(): Promise<OnboardingStepsResponse> {
    return apiRequest<OnboardingStepsResponse>("/workspaces/onboarding/steps", {
      method: "GET",
    });
  },

  async getOnboardingStatus(id: string): Promise<OnboardingStatus> {
    return apiRequest<OnboardingStatus>(
      `/workspaces/${encodeURIComponent(id)}/onboarding/status`,
      { method: "GET" }
    );
  },

  async completeOnboarding(
    id: string,
    payload: CompleteOnboardingInput
  ): Promise<CompleteOnboardingResponse> {
    return apiRequest<CompleteOnboardingResponse>(
      `/workspaces/${encodeURIComponent(id)}/onboarding/complete`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      }
    );
  },

  async upsertOnboardingAnswers(
    id: string,
    payload: UpsertOnboardingAnswersInput
  ): Promise<OnboardingStatus> {
    return apiRequest<OnboardingStatus>(
      `/workspaces/${encodeURIComponent(id)}/onboarding/answers`,
      {
        method: "PUT",
        body: JSON.stringify(payload),
      }
    );
  },
};
