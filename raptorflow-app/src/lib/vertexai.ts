import { ChatVertexAI } from "@langchain/google-vertexai";
import { ChatGoogleGenerativeAI } from "@langchain/google-genai";
import { getInferenceConfig, type InferenceConfig } from "./inference-config";

// Lazy-initialized model instances
type GeminiChatModel = ChatVertexAI | ChatGoogleGenerativeAI;

let _gemini2Flash: GeminiChatModel | null = null;
let _gemini15Pro: GeminiChatModel | null = null;
let _gemini15Flash: GeminiChatModel | null = null;

const MODEL_FALLBACK_ORDER = [
  "gemini-2.5-flash-lite",
  "gemini-2.5-flash",
];

function isApiKeyCompatibleModel(modelName: string): boolean {
  return !modelName.trim().toLowerCase().startsWith("gemini-2.5");
}

function hasDefaultCredentials(): boolean {
  return Boolean(
    process.env.GOOGLE_APPLICATION_CREDENTIALS ||
      process.env.VERTEX_AI_USE_ADC === "true" ||
      process.env.NEXT_PUBLIC_VERTEX_AI_USE_ADC === "true"
  );
}

function buildModelChain(primary?: string, fallbacks?: string[]) {
  const chain = [primary, ...(fallbacks || []), ...MODEL_FALLBACK_ORDER].filter(
    Boolean
  ) as string[];
  return Array.from(new Set(chain));
}

function isModelAccessError(error: unknown): boolean {
  const message =
    error instanceof Error ? error.message : String(error ?? "");
  const status =
    (error as { response?: { status?: number } })?.response?.status ??
    (error as { status?: number })?.status;
  if (status === 401 || status === 403 || status === 404) {
    return true;
  }
  return /not found|not_found|does not have access|permission|401|403|404|unauthorized|api keys are not supported|credentials_missing/i.test(
    message
  );
}

/**
 * SOTA Model Factory.
 * Uses the singular INFERENCE_SIMPLE API key.
 */
function createModel(
  modelName: string,
  temperature: number,
  maxTokens: number,
  config?: InferenceConfig
): GeminiChatModel | null {
  try {
    const inference = config ?? getInferenceConfig();
    const hasCreds = hasDefaultCredentials();
    if (!inference.apiKey && !hasCreds) return null;

    if (hasCreds) {
      const modelConfig: ConstructorParameters<typeof ChatVertexAI>[0] = {
        model: modelName,
        temperature: temperature,
        maxOutputTokens: maxTokens,
        location: inference.region,
      };

      if (inference.apiKey) {
        modelConfig.apiKey = inference.apiKey;
      }

      return new ChatVertexAI(modelConfig);
    }

    if (!isApiKeyCompatibleModel(modelName)) {
      console.warn(
        `Skipping ${modelName} because it requires Vertex AI credentials.`
      );
      return null;
    }

    return new ChatGoogleGenerativeAI({
      model: modelName,
      temperature: temperature,
      maxOutputTokens: maxTokens,
      apiKey: inference.apiKey,
    });
  } catch (error) {
    console.error(`Failed to create model ${modelName}:`, error);
    return null;
  }
}

export async function invokeWithModelFallback<TInput>({
  input,
  modelName,
  temperature,
  maxTokens,
  tools,
  fallbackModels,
}: {
  input: TInput;
  modelName: string;
  temperature: number;
  maxTokens: number;
  tools?: unknown[];
  fallbackModels?: string[];
}): Promise<any> {
  const config = getInferenceConfig();
  const chain = buildModelChain(modelName, fallbackModels);
  let lastError: unknown;

  for (const name of chain) {
    const model = createModel(name, temperature, maxTokens, config);
    if (!model) {
      continue;
    }
    try {
      const target =
        tools && tools.length ? (model as any).bindTools(tools) : model;
      return await (target as any).invoke(input);
    } catch (error) {
      lastError = error;
      if (!isModelAccessError(error)) {
        throw error;
      }
    }
  }

  if (lastError) {
    throw lastError;
  }
  throw new Error("No available Gemini models for this request.");
}

// Getter functions for lazy initialization
export function getGemini2Flash(): GeminiChatModel | null {
  if (!_gemini2Flash) {
    const config = getInferenceConfig();
    const modelName = config.models.general || "gemini-2.5-flash-lite";
    _gemini2Flash = createModel(modelName, 0.7, 8192, config);
  }
  return _gemini2Flash;
}

export function getGemini15Pro(): GeminiChatModel | null {
  if (!_gemini15Pro) {
    const config = getInferenceConfig();
    const modelName =
      config.models.ultra || config.models.high || "gemini-2.5-flash";
    _gemini15Pro = createModel(modelName, 0.5, 8192, config);
  }
  return _gemini15Pro;
}

export function getGemini15Flash(): GeminiChatModel | null {
  if (!_gemini15Flash) {
    const config = getInferenceConfig();
    const modelName = config.models.general || "gemini-2.5-flash-lite";
    _gemini15Flash = createModel(modelName, 0.3, 2048, config);
  }
  return _gemini15Flash;
}

// Legacy exports for backward compatibility (will fail if credentials not set)
// These are kept for any existing code that imports them directly
export const gemini2Flash = null as unknown as GeminiChatModel;
export const gemini15Pro = null as unknown as GeminiChatModel;
export const gemini15Flash = null as unknown as GeminiChatModel;

export const geminiEmbeddingModel = "text-embedding-004"; // For reference in RAG
