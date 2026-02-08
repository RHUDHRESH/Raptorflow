import { apiRequest } from "./http";

export type ApiCampaign = {
  id: string;
  tenant_id: string;
  title: string;
  description?: string | null;
  objective: string;
  status: string;
  created_at?: string;
  updated_at?: string;
};

type CampaignListResponse = { campaigns: ApiCampaign[] };

export type CreateCampaignInput = {
  name: string;
  description?: string;
  objective?: string;
  status?: string;
};

export type UpdateCampaignInput = Partial<CreateCampaignInput>;

export const campaignsService = {
  async list(workspaceId: string): Promise<ApiCampaign[]> {
    const data = await apiRequest<CampaignListResponse>("/campaigns", {
      method: "GET",
      workspaceId,
    });
    return data.campaigns ?? [];
  },

  async create(workspaceId: string, input: CreateCampaignInput): Promise<ApiCampaign> {
    return apiRequest<ApiCampaign>("/campaigns", {
      method: "POST",
      workspaceId,
      body: JSON.stringify(input),
    });
  },

  async get(workspaceId: string, campaignId: string): Promise<ApiCampaign> {
    return apiRequest<ApiCampaign>(`/campaigns/${encodeURIComponent(campaignId)}`, {
      method: "GET",
      workspaceId,
    });
  },

  async update(
    workspaceId: string,
    campaignId: string,
    patch: UpdateCampaignInput
  ): Promise<ApiCampaign> {
    return apiRequest<ApiCampaign>(`/campaigns/${encodeURIComponent(campaignId)}`, {
      method: "PATCH",
      workspaceId,
      body: JSON.stringify(patch),
    });
  },

  async delete(workspaceId: string, campaignId: string): Promise<void> {
    await apiRequest<void>(`/campaigns/${encodeURIComponent(campaignId)}`, {
      method: "DELETE",
      workspaceId,
    });
  },
};
