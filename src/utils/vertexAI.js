/**
 * Vertex AI Model Configuration
 *
 * This utility manages model selection for different AI tasks.
 * Each task type is mapped to the most appropriate model.
 */

export const VERTEX_AI_MODELS = {
  // OCR and document processing
  OCR: 'pixtral-large-2411',

  // Fast, creative content generation
  CREATIVE_FAST: 'claude-3-5-haiku-20241022',

  // Deep creative reasoning and analysis
  CREATIVE_REASONING: 'claude-3-7-sonnet-20250219',

  // General purpose tasks (default)
  GENERAL_PURPOSE: 'gemini-2.0-flash-exp',

  // Primary reasoning and complex analysis
  REASONING: 'gemini-2.5-pro-preview-03-25',

  // Fallback reasoning model
  REASONING_FALLBACK: 'gemini-2.0-flash-thinking-exp-01-21'
};

/**
 * Task types for model selection
 */
export const TASK_TYPES = {
  OCR: 'ocr',
  CREATIVE_FAST: 'creative_fast',
  CREATIVE_REASONING: 'creative_reasoning',
  GENERAL_PURPOSE: 'general_purpose',
  REASONING: 'reasoning',
  REASONING_FALLBACK: 'reasoning_fallback'
};

/**
 * Get the appropriate model for a given task
 * @param {string} taskType - Type of task from TASK_TYPES
 * @returns {string} Model identifier
 */
export function getModelForTask(taskType) {
  const modelMap = {
    [TASK_TYPES.OCR]: VERTEX_AI_MODELS.OCR,
    [TASK_TYPES.CREATIVE_FAST]: VERTEX_AI_MODELS.CREATIVE_FAST,
    [TASK_TYPES.CREATIVE_REASONING]: VERTEX_AI_MODELS.CREATIVE_REASONING,
    [TASK_TYPES.GENERAL_PURPOSE]: VERTEX_AI_MODELS.GENERAL_PURPOSE,
    [TASK_TYPES.REASONING]: VERTEX_AI_MODELS.REASONING,
    [TASK_TYPES.REASONING_FALLBACK]: VERTEX_AI_MODELS.REASONING_FALLBACK
  };

  return modelMap[taskType] || VERTEX_AI_MODELS.GENERAL_PURPOSE;
}

/**
 * Get Vertex AI configuration
 * @returns {Object} Configuration object with apiKey and endpoint
 */
export function getVertexAIConfig() {
  return {
    apiKey: import.meta.env.VITE_VERTEX_AI_API_KEY || '',
    endpoint: import.meta.env.VITE_VERTEX_AI_ENDPOINT || 'us-central1-aiplatform.googleapis.com'
  };
}

/**
 * Construct Vertex AI API URL
 * @param {string} taskTypeOrModel - Task type from TASK_TYPES or direct model identifier
 * @param {string} action - API action (e.g., 'generateContent', 'streamGenerateContent')
 * @returns {string} Complete API URL
 */
export function getVertexAIUrl(taskTypeOrModel, action = 'generateContent') {
  const { apiKey, endpoint } = getVertexAIConfig();

  if (!apiKey) {
    throw new Error('Vertex AI API key not configured');
  }

  // Check if it's a task type or direct model identifier
  const model = Object.values(TASK_TYPES).includes(taskTypeOrModel)
    ? getModelForTask(taskTypeOrModel)
    : taskTypeOrModel;

  // Handle different model providers (Claude, Gemini, Mistral)
  let publisherPath;

  if (model.startsWith('claude-')) {
    publisherPath = `publishers/anthropic/models/${model}`;
  } else if (model.startsWith('gemini-')) {
    publisherPath = `publishers/google/models/${model}`;
  } else if (model.startsWith('pixtral-') || model.includes('mistral')) {
    publisherPath = `publishers/mistralai/models/${model}`;
  } else {
    // Default to Google publisher
    publisherPath = `publishers/google/models/${model}`;
  }

  return `https://${endpoint}/v1/${publisherPath}:${action}?key=${apiKey}`;
}

/**
 * Model capabilities and use cases
 */
export const MODEL_CAPABILITIES = {
  [VERTEX_AI_MODELS.OCR]: {
    name: 'Pixtral Large (Mistral OCR)',
    useCase: 'OCR, document processing, image understanding',
    strengths: ['Text extraction', 'Document analysis', 'Visual understanding'],
    contextWindow: '128K tokens'
  },
  [VERTEX_AI_MODELS.CREATIVE_FAST]: {
    name: 'Claude 3.5 Haiku',
    useCase: 'Fast creative generation, quick responses',
    strengths: ['Speed', 'Cost efficiency', 'Creative writing'],
    contextWindow: '200K tokens'
  },
  [VERTEX_AI_MODELS.CREATIVE_REASONING]: {
    name: 'Claude 3.7 Sonnet',
    useCase: 'Deep creative reasoning, complex analysis',
    strengths: ['Nuanced reasoning', 'Creative problem solving', 'Long context'],
    contextWindow: '200K tokens'
  },
  [VERTEX_AI_MODELS.GENERAL_PURPOSE]: {
    name: 'Gemini 2.0 Flash Experimental',
    useCase: 'General purpose tasks, balanced performance',
    strengths: ['Versatility', 'Speed', 'Multimodal'],
    contextWindow: '1M tokens'
  },
  [VERTEX_AI_MODELS.REASONING]: {
    name: 'Gemini 2.5 Pro Preview',
    useCase: 'Complex reasoning, deep analysis',
    strengths: ['Advanced reasoning', 'Code generation', 'Analysis'],
    contextWindow: '2M tokens'
  },
  [VERTEX_AI_MODELS.REASONING_FALLBACK]: {
    name: 'Gemini 2.0 Flash Thinking',
    useCase: 'Fallback reasoning with chain-of-thought',
    strengths: ['Transparent reasoning', 'Problem solving', 'Fast inference'],
    contextWindow: '32K tokens'
  }
};

/**
 * Get model information
 * @param {string} taskType - Task type from TASK_TYPES
 * @returns {Object} Model capabilities and information
 */
export function getModelInfo(taskType) {
  const model = getModelForTask(taskType);
  return {
    model,
    ...MODEL_CAPABILITIES[model]
  };
}
