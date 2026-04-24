import { publicEnv } from "./env";

export interface AICompletionOptions {
  model?: string;
  temperature?: number;
  maxTokens?: number;
}

const DEFAULT_MODEL = "mixtral-8x7b-32768";
const GROQ_PROXY_URL = "/api/ai/chat";
const FETCH_TIMEOUT_MS = 30_000;

function fetchWithTimeout(
  url: string,
  init: RequestInit & { signal?: AbortSignal },
): Promise<Response> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);
  const promise = fetch(url, { ...init, signal: controller.signal });
  return promise.finally(() => clearTimeout(timeout));
}

export async function completion(
  prompt: string,
  system: string,
  options: AICompletionOptions = {},
): Promise<string> {
  if (!publicEnv.offlineMode) {
    throw new Error(
      "[ai] completion() called in non-offline mode. " +
        "Use GCP Gemini via crates/gcp on the backend instead.",
    );
  }

  if (!prompt.trim()) {
    throw new Error("[ai] prompt cannot be empty");
  }

  const model = options.model ?? DEFAULT_MODEL;

  let res: Response;
  try {
    res = await fetchWithTimeout(`${GROQ_PROXY_URL}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model,
        messages: [
          { role: "system", content: system || "You are a helpful assistant." },
          { role: "user", content: prompt },
        ],
        temperature: options.temperature ?? 0.7,
        max_tokens: options.maxTokens ?? 2048,
      }),
    });
  } catch (err) {
    if (err instanceof Error && err.name === "AbortError") {
      throw new Error(`[ai] GROQ request timed out after ${FETCH_TIMEOUT_MS}ms`);
    }
    throw err;
  }

  if (!res.ok) {
    const text = await res.text().catch(() => "(no body)");
    throw new Error(`[ai] GROQ API error ${res.status}: ${text}`);
  }

  const data = (await res.json()) as {
    choices?: { message?: { content?: string } }[];
    error?: { message?: string };
  };

  if (data.error) {
    throw new Error(`[ai] GROQ error: ${data.error.message}`);
  }

  const content = data.choices?.[0]?.message?.content;
  if (content === undefined) {
    throw new Error("[ai] GROQ returned no content in response");
  }

  return content;
}

export async function streamCompletion(
  prompt: string,
  system: string,
  onChunk: (text: string) => void,
  options: AICompletionOptions = {},
): Promise<void> {
  if (!publicEnv.offlineMode) {
    throw new Error("[ai] streamCompletion() called in non-offline mode");
  }

  if (!prompt.trim()) {
    throw new Error("[ai] prompt cannot be empty");
  }

  const model = options.model ?? DEFAULT_MODEL;

  let res: Response;
  try {
    res = await fetchWithTimeout(`${GROQ_PROXY_URL}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model,
        messages: [
          { role: "system", content: system || "You are a helpful assistant." },
          { role: "user", content: prompt },
        ],
        temperature: options.temperature ?? 0.7,
        max_tokens: options.maxTokens ?? 2048,
        stream: true,
      }),
    });
  } catch (err) {
    if (err instanceof Error && err.name === "AbortError") {
      throw new Error(`[ai] GROQ stream timed out after ${FETCH_TIMEOUT_MS}ms`);
    }
    throw err;
  }

  if (!res.ok || !res.body) {
    throw new Error(`[ai] GROQ stream error: ${res.status}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      const json = line.slice(6).trim();
      if (json === "[DONE]") return;
      try {
        const chunk: { choices?: { delta?: { content?: string } }[] } = JSON.parse(json);
        const content = chunk.choices?.[0]?.delta?.content;
        if (content) onChunk(content);
      } catch {
        // Skip malformed SSE lines
      }
    }
  }
}

export const aiConfig = {
  isConfigured: () => !publicEnv.offlineMode,
  isLocalMode: () => publicEnv.offlineMode,
  baseUrl: GROQ_PROXY_URL,
  defaultModel: DEFAULT_MODEL,
} as const;
