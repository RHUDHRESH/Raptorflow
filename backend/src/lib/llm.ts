import { VertexAI, GenerativeModel } from '@google-cloud/vertexai';
import { ChatVertexAI } from "@langchain/google-vertexai";
import { env } from '../config/env';

// =====================================================
// TIERED MODEL SYSTEM
// =====================================================

/**
 * Model tiers for different task complexities
 * 
 * REASONING_HEAVY: Complex multi-step reasoning, strategic analysis
 * REASONING: Standard reasoning tasks with structured output
 * GENERAL: Normal generation tasks
 * SIMPLE: Repetitive/simple parsing tasks
 */
export const ModelTier = {
  REASONING_HEAVY: 'gemini-2.0-flash-thinking-exp-01-21',  // Complex reasoning (thinking model)
  REASONING: 'gemini-2.5-pro-preview-06-05',               // Standard reasoning  
  GENERAL: 'gemini-2.5-flash-preview-05-20',               // Normal tasks
  SIMPLE: 'gemini-1.5-flash'                               // Repetitive/simple
} as const;

export type ModelTierType = typeof ModelTier[keyof typeof ModelTier];

/**
 * Task type to model tier mapping
 */
export type TaskType = 'heavy' | 'reasoning' | 'general' | 'simple';

const TASK_TO_TIER: Record<TaskType, ModelTierType> = {
  heavy: ModelTier.REASONING_HEAVY,
  reasoning: ModelTier.REASONING,
  general: ModelTier.GENERAL,
  simple: ModelTier.SIMPLE
};

/**
 * Get appropriate model for a task type
 */
export const getModelForTask = (taskType: TaskType): ModelTierType => {
  return TASK_TO_TIER[taskType] || ModelTier.GENERAL;
};

/**
 * Agent to task type mapping for automatic model selection
 */
export const AGENT_TASK_TYPES: Record<string, TaskType> = {
  // Heavy reasoning - complex analysis
  'ICPBuildAgent': 'heavy',
  'BarrierEngineAgent': 'heavy',
  'StrategyProfileAgent': 'heavy',
  
  // Reasoning - structured output generation
  'MoveAssemblyAgent': 'reasoning',
  'MuseAgent': 'reasoning',
  'PositioningParseAgent': 'reasoning',
  'MonetizationAgent': 'reasoning',
  
  // General - enrichment and analysis
  'CompanyEnrichAgent': 'general',
  'CompetitorSurfaceAgent': 'general',
  'TechStackSeedAgent': 'general',
  'JTBDMapperAgent': 'general',
  
  // Simple - parsing and extraction
  'SimpleParser': 'simple',
  'DataExtractor': 'simple'
};

/**
 * Get model for a specific agent
 */
export const getModelForAgent = (agentName: string): ModelTierType => {
  const taskType = AGENT_TASK_TYPES[agentName] || 'general';
  return getModelForTask(taskType);
};

// =====================================================
// VERTEX AI INITIALIZATION
// =====================================================

// Initialize Vertex AI (Native SDK)
export const vertexAI = new VertexAI({
  project: env.GOOGLE_CLOUD_PROJECT_ID,
  location: env.GOOGLE_CLOUD_LOCATION,
});

/**
 * Get native Vertex AI model
 */
export const getModel = (modelName: string): GenerativeModel => {
  return vertexAI.getGenerativeModel({ model: modelName });
};

/**
 * Get native model for task type
 */
export const getModelForTaskNative = (taskType: TaskType): GenerativeModel => {
  const modelName = getModelForTask(taskType);
  return getModel(modelName);
};

// =====================================================
// LANGCHAIN INITIALIZATION
// =====================================================

/**
 * Temperature settings per tier
 */
const TIER_TEMPERATURES: Record<TaskType, number> = {
  heavy: 0.1,      // Very deterministic for complex reasoning
  reasoning: 0.2,  // Slightly more creative for structured output
  general: 0.3,    // Balanced
  simple: 0.1      // Deterministic for parsing
};

/**
 * Max tokens per tier
 */
const TIER_MAX_TOKENS: Record<TaskType, number> = {
  heavy: 16384,    // Large output for complex analysis
  reasoning: 8192, // Standard structured output
  general: 4096,   // Normal generation
  simple: 2048     // Short outputs
};

/**
 * Get LangChain model with default settings
 * @deprecated Use getLangChainModelForTask instead for proper tier selection
 */
export const getLangChainModel = (modelName: string = ModelTier.GENERAL) => {
  return new ChatVertexAI({
    model: modelName,
    location: env.GOOGLE_CLOUD_LOCATION,
    maxOutputTokens: 8192,
    temperature: 0.2,
  });
};

/**
 * Get LangChain model for a specific task type with optimized settings
 */
export const getLangChainModelForTask = (taskType: TaskType) => {
  const modelName = getModelForTask(taskType);
  const temperature = TIER_TEMPERATURES[taskType];
  const maxOutputTokens = TIER_MAX_TOKENS[taskType];
  
  return new ChatVertexAI({
    model: modelName,
    location: env.GOOGLE_CLOUD_LOCATION,
    maxOutputTokens,
    temperature,
  });
};

/**
 * Get LangChain model for a specific agent
 */
export const getLangChainModelForAgent = (agentName: string) => {
  const taskType = AGENT_TASK_TYPES[agentName] || 'general';
  return getLangChainModelForTask(taskType);
};

// =====================================================
// UTILITY FUNCTIONS
// =====================================================

/**
 * Log model selection for debugging
 */
export const logModelSelection = (agentName: string, taskType: TaskType, model: string) => {
  if (env.NODE_ENV === 'development') {
    console.log(`🤖 [${agentName}] Using ${model} (task: ${taskType})`);
  }
};

/**
 * Get all available models
 */
export const getAvailableModels = () => ({
  tiers: ModelTier,
  taskTypes: Object.keys(TASK_TO_TIER),
  agentMappings: AGENT_TASK_TYPES
});
