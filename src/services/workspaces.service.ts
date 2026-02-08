import { apiRequest } from "./http";

export type Workspace = {
  id: string;
  name: string;
  slug: string | null;
  settings: Record<string, unknown> | null;
  created_at?: string;
  updated_at?: string;
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
};
