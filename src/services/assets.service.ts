import { apiRequest } from "./http";

export type AssetType = "image" | "document" | "video" | "audio";

export type AssetRecord = {
  id: string;
  workspace_id: string;
  filename: string;
  original_name: string;
  mime_type: string;
  size_bytes: number;
  storage_path: string;
  public_url?: string | null;
  asset_type: AssetType;
  metadata: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
};

type AssetUploadTarget = {
  signed_url: string;
  token: string;
  path: string;
  bucket: string;
};

type CreateAssetSessionResponse = {
  asset: AssetRecord;
  upload: AssetUploadTarget;
};

type AssetListResponse = {
  assets: AssetRecord[];
  total: number;
  offset: number;
  limit: number;
};

type ListAssetOptions = {
  limit?: number;
  offset?: number;
  assetType?: AssetType;
};

async function uploadToSignedUrl(target: AssetUploadTarget, file: File): Promise<void> {
  const response = await fetch(target.signed_url, {
    method: "PUT",
    headers: {
      "content-type": file.type || "application/octet-stream",
    },
    body: file,
  });

  if (!response.ok) {
    const text = await response.text().catch(() => "");
    throw new Error(text || `Storage upload failed (${response.status})`);
  }
}

export const assetsService = {
  async createSession(
    workspaceId: string,
    file: File,
    metadata: Record<string, unknown> = {}
  ): Promise<CreateAssetSessionResponse> {
    return apiRequest<CreateAssetSessionResponse>("/assets/sessions", {
      method: "POST",
      workspaceId,
      body: JSON.stringify({
        original_name: file.name,
        mime_type: file.type || "application/octet-stream",
        size_bytes: file.size,
        metadata,
      }),
    });
  },

  async confirm(
    workspaceId: string,
    assetId: string,
    metadata: Record<string, unknown> = {}
  ): Promise<AssetRecord> {
    return apiRequest<AssetRecord>(`/assets/${encodeURIComponent(assetId)}/confirm`, {
      method: "POST",
      workspaceId,
      body: JSON.stringify({ metadata }),
    });
  },

  async upload(
    workspaceId: string,
    file: File,
    metadata: Record<string, unknown> = {}
  ): Promise<AssetRecord> {
    const session = await this.createSession(workspaceId, file, metadata);
    await uploadToSignedUrl(session.upload, file);
    return this.confirm(workspaceId, session.asset.id, { ...metadata, status: "uploaded" });
  },

  async list(workspaceId: string, opts: ListAssetOptions = {}): Promise<AssetListResponse> {
    const query = new URLSearchParams();
    if (typeof opts.limit === "number") query.set("limit", String(opts.limit));
    if (typeof opts.offset === "number") query.set("offset", String(opts.offset));
    if (opts.assetType) query.set("asset_type", opts.assetType);

    const suffix = query.toString() ? `?${query.toString()}` : "";
    return apiRequest<AssetListResponse>(`/assets${suffix}`, {
      method: "GET",
      workspaceId,
    });
  },

  async remove(workspaceId: string, assetId: string): Promise<void> {
    await apiRequest<void>(`/assets/${encodeURIComponent(assetId)}`, {
      method: "DELETE",
      workspaceId,
    });
  },
};
