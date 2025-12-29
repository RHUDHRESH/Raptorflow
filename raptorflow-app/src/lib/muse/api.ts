'use client';

import { apiFetch, getAuthHeaders } from '@/lib/backend';
import foundationMetadata from '@/lib/foundation_test.json';

export type MuseAssetRecord = {
  id: string;
  content: string;
  asset_type: string;
  metadata: Record<string, unknown>;
  status: string;
  quality_score?: number | null;
  generation_prompt?: string | null;
  generation_model?: string | null;
  generation_tokens?: number | null;
  tags?: string[] | null;
  created_at: string;
  updated_at: string;
};

export async function createMuseAsset(
  prompt: string,
  assetType = 'text',
  metadata: Record<string, unknown> | string = {}
): Promise<MuseAssetRecord> {
  const headers = await getAuthHeaders();
  const createResponse = await apiFetch<any>('/v1/muse/create', {
    method: 'POST',
    headers,
    body: JSON.stringify({ prompt }),
  });

  let metadataObject: Record<string, unknown>;
  if (typeof metadata === 'string') {
    try {
      metadataObject = JSON.parse(metadata) as Record<string, unknown>;
    } catch {
      metadataObject = { note: metadata };
    }
  } else {
    metadataObject = metadata;
  }
  const content = createResponse.asset_content || 'Generation failed.';
  const asset = await apiFetch<MuseAssetRecord>('/v1/muse/assets', {
    method: 'POST',
    headers,
    body: JSON.stringify({
      content,
      asset_type: assetType,
      metadata: {
        ...metadataObject,
        foundation_metadata: foundationMetadata,
      },
      status: 'ready',
      quality_score: createResponse.quality_score,
      generation_prompt: prompt,
      generation_model: 'muse-spine',
    }),
  });

  return asset;
}

export async function listMuseAssets(): Promise<MuseAssetRecord[]> {
  const headers = await getAuthHeaders();
  return apiFetch<MuseAssetRecord[]>('/v1/muse/assets', { headers });
}

export async function getMuseAsset(assetId: string): Promise<MuseAssetRecord> {
  const headers = await getAuthHeaders();
  return apiFetch<MuseAssetRecord>(`/v1/muse/assets/${assetId}`, { headers });
}

export async function updateMuseAsset(
  assetId: string,
  updates: Partial<MuseAssetRecord>
): Promise<MuseAssetRecord> {
  const headers = await getAuthHeaders();
  return apiFetch<MuseAssetRecord>(`/v1/muse/assets/${assetId}`, {
    method: 'PUT',
    headers,
    body: JSON.stringify({
      content: updates.content,
      asset_type: updates.asset_type,
      metadata: updates.metadata,
      status: updates.status,
      quality_score: updates.quality_score,
      tags: updates.tags,
    }),
  });
}
