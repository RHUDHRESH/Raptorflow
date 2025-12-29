import { getMuseAuthHeaders } from './auth';

const backendUrl =
  process.env.NEXT_PUBLIC_BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || '';

export async function ingestFileContent(
  content: string,
  metadata: Record<string, unknown> = {}
) {
  if (!backendUrl) {
    throw new Error('Muse ingest backend not configured');
  }

  const auth = await getMuseAuthHeaders();
  if (!auth) {
    throw new Error('Authentication required for ingest');
  }

  const filename =
    typeof metadata.filename === 'string' && metadata.filename.length > 0
      ? metadata.filename
      : 'uploaded-file';

  const response = await fetch(`${backendUrl}/v1/muse/ingest`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...auth.headers,
    },
    body: JSON.stringify({
      content,
      filename,
      metadata: {
        ...metadata,
        ingested_at: new Date().toISOString(),
      },
    }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Muse ingest failed: ${errorText}`);
  }

  const result = await response.json();
  return result?.chunks_ingested || 0;
}
