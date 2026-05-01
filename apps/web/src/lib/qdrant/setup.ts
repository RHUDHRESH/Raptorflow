import { COLLECTION, getQdrantBaseUrl, getQdrantHeaders } from "./client";

export async function ensureCollection(): Promise<void> {
  const baseUrl = getQdrantBaseUrl();
  const headers = getQdrantHeaders();
  const listResponse = await fetch(`${baseUrl}/collections`, { headers });

  if (!listResponse.ok) {
    throw new Error(
      `Qdrant list collections failed: ${listResponse.status} ${listResponse.statusText}`,
    );
  }

  const listPayload = (await listResponse.json()) as {
    result?: { collections?: Array<{ name: string }> };
    collections?: Array<{ name: string }>;
  };
  const collections = listPayload.result?.collections ?? listPayload.collections ?? [];
  const exists = collections.some((c) => c.name === COLLECTION);

  if (!exists) {
    const createResponse = await fetch(`${baseUrl}/collections/${encodeURIComponent(COLLECTION)}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        ...headers,
      },
      body: JSON.stringify({
        vectors: {
          size: 1536,
          distance: "Cosine",
        },
      }),
    });

    if (!createResponse.ok) {
      throw new Error(
        `Qdrant create collection failed: ${createResponse.status} ${createResponse.statusText}`,
      );
    }
  }
}
