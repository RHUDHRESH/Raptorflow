import { ChatVertexAI } from "@langchain/google-vertexai";
// import { BedrockChat } from "@langchain/aws"; // TODO: Add when AWS Bedrock is configured
import { env } from '../config/env';

// =====================================================
// MODEL ROUTER - SOTA TIERED MODEL SELECTION
// =====================================================

/**
 * User-Requested Model Tiering Strategy:
 * - SIMPLE: Gemini 1.5 Flash (for dumb/simple tasks)
 * - GENERAL: Gemini 2.5 Flash (for next level/general tasks)
 * - REASONING: Gemini 2.0 Flash Thinking (for reasoning tasks)
 * - REASONING_HEAVY: Gemini 1.5 Pro (for heavy reasoning/complex tasks)
 *
 * Fallback Chain: 1.5 Pro → 2.0 Flash Thinking → 2.5 Flash → 1.5 Flash → Bedrock
 */

export enum ModelTier {
  // Vertex AI models (user-optimized tiering)
  REASONING_HEAVY = 'gemini-1.5-pro-002',            // Gemini 1.5 Pro for heavy reasoning
  REASONING = 'gemini-2.0-flash-thinking-exp-01-21', // Gemini 2.0 Flash for reasoning tasks
  GENERAL = 'gemini-2.5-flash-002',                  // Gemini 2.5 Flash for next level tasks
  SIMPLE = 'gemini-1.5-flash-002',                   // Gemini 1.5 for dumb/simple tasks

  // AWS Bedrock models (fallback/alternative)
  BEDROCK_CLAUDE_3_OPUS = 'anthropic.claude-3-opus-20240229-v1:0',
  BEDROCK_CLAUDE_3_SONNET = 'anthropic.claude-3-sonnet-20240229-v1:0',
  BEDROCK_CLAUDE_3_HAIKU = 'anthropic.claude-3-haiku-20240307-v1:0',
  BEDROCK_TITAN_TEXT_G1 = 'amazon.titan-text-express-v1'
}

export type TaskType = 'heavy' | 'reasoning' | 'general' | 'simple';

export interface ModelConfig {
  name: ModelTier;
  temperature: number;
  maxTokens: number;
  costPerToken: number; // Cost per 1000 tokens
  contextWindow: number;
  supportsThinking?: boolean;
  provider?: 'vertex' | 'bedrock'; // Default is vertex
  region?: string; // AWS region for Bedrock
  modelId?: string; // Bedrock model ID
}

// Model configurations with pricing (optimized 2024)
const MODEL_CONFIGS: Record<ModelTier, ModelConfig> = {
  [ModelTier.REASONING_HEAVY]: {
    name: ModelTier.REASONING_HEAVY,
    temperature: 0.1,
    maxTokens: 8192,
    costPerToken: 0.00125, // Gemini 1.5 Pro: $1.25 per 1000 tokens (input)
    contextWindow: 2097152, // 2M context
    supportsThinking: true
  },
  [ModelTier.REASONING]: {
    name: ModelTier.REASONING,
    temperature: 0.2,
    maxTokens: 8192,
    costPerToken: 0.00015, // Gemini 2.0 Flash Thinking: $0.15 per 1000 tokens (input)
    contextWindow: 32768, // 32K context with thinking
    supportsThinking: true
  },
  [ModelTier.GENERAL]: {
    name: ModelTier.GENERAL,
    temperature: 0.3,
    maxTokens: 4096,
    costPerToken: 0.000075, // Gemini 2.5 Flash: $0.075 per 1000 tokens (input)
    contextWindow: 1048576, // 1M context
  },
  [ModelTier.SIMPLE]: {
    name: ModelTier.SIMPLE,
    temperature: 0.1,
    maxTokens: 2048,
    costPerToken: 0.00001875, // Gemini 1.5 Flash: $0.01875 per 1000 tokens (input)
    contextWindow: 1048576, // 1M context
  },

  // AWS Bedrock models
  [ModelTier.BEDROCK_CLAUDE_3_OPUS]: {
    name: ModelTier.BEDROCK_CLAUDE_3_OPUS,
    temperature: 0.1,
    maxTokens: 4096,
    costPerToken: 0.000015, // $15 per 1M tokens (input)
    contextWindow: 200000, // 200K context
    provider: 'bedrock'
  },
  [ModelTier.BEDROCK_CLAUDE_3_SONNET]: {
    name: ModelTier.BEDROCK_CLAUDE_3_SONNET,
    temperature: 0.2,
    maxTokens: 4096,
    costPerToken: 0.000003, // $3 per 1M tokens (input)
    contextWindow: 200000,
    provider: 'bedrock'
  },
  [ModelTier.BEDROCK_CLAUDE_3_HAIKU]: {
    name: ModelTier.BEDROCK_CLAUDE_3_HAIKU,
    temperature: 0.3,
    maxTokens: 4096,
    costPerToken: 0.00000025, // $0.25 per 1M tokens (input)
    contextWindow: 200000,
    provider: 'bedrock'
  },
  [ModelTier.BEDROCK_TITAN_TEXT_G1]: {
    name: ModelTier.BEDROCK_TITAN_TEXT_G1,
    temperature: 0.1,
    maxTokens: 8000,
    costPerToken: 0.0000013, // $1.30 per 1M tokens (input)
    contextWindow: 8000,
    provider: 'bedrock'
  }
};

// Task type to model tier mapping
const TASK_TO_TIER: Record<TaskType, ModelTier> = {
  heavy: ModelTier.REASONING_HEAVY,
  reasoning: ModelTier.REASONING,
  general: ModelTier.GENERAL,
  simple: ModelTier.SIMPLE
};

// Agent-specific overrides (optimized for new tiering)
const AGENT_MODEL_OVERRIDES: Record<string, TaskType> = {
  // Heavy reasoning agents (Gemini 1.5 Pro)
  'icp_build_agent': 'heavy',
  'barrier_engine_agent': 'heavy',
  'strategy_profile_agent': 'heavy',
  'cohort_builder_agent': 'heavy',
  'competitor_intelligence_agent': 'heavy',
  'market_intel_agent': 'heavy',

  // Reasoning agents (Gemini 2.0 Flash)
  'move_assembly_agent': 'reasoning',
  'muse_agent': 'reasoning',
  'positioning_parse_agent': 'reasoning',
  'monetization_agent': 'reasoning',
  'radar_agent': 'reasoning',
  'content_idea_agent': 'reasoning',
  'cohort_tag_generator_agent': 'reasoning',
  'plan_generator_agent': 'reasoning',
  'campaign_architect_agent': 'reasoning',
  'offer_architect_agent': 'reasoning',
  'positioning_architect_agent': 'reasoning',
  'value_proposition_agent': 'reasoning',
  'revenue_model_agent': 'reasoning',

  // General agents (Gemini 2.5 Flash)
  'company_enrich_agent': 'general',
  'competitor_surface_agent': 'general',
  'tech_stack_seed_agent': 'general',
  'jtbd_mapper_agent': 'general',
  'trend_scraper_agent': 'general',
  'website_scraper_agent': 'general',
  'ad_variants_agent': 'general',
  'asset_repurposing_agent': 'general',
  'channel_mix_strategist_agent': 'general',
  'budget_allocation_agent': 'general',
  'sequencing_agent': 'general',
  'copywriter_agent': 'general',
  'visual_concept_agent': 'general',
  'social_content_agent': 'general',
  'longform_writer_agent': 'general',
  'posting_scheduler_agent': 'general',
  'email_automation_agent': 'general',
  'lead_nurture_agent': 'general',
  'retargeting_agent': 'general',
  'ads_targeting_agent': 'general',
  'distribution_strategist_agent': 'general',
  'move_designer_agent': 'general',
  'message_pillar_agent': 'general',
  'rtb_agent': 'general',
  'funnel_engineer_agent': 'general',
  'experiment_generator_agent': 'general',

  // Simple agents (Gemini 1.5 Flash)
  'simple_parser': 'simple',
  'data_extractor': 'simple',
  'input_validator': 'simple',
  'quality_rater_agent': 'simple',
  'rewrite_fixer_agent': 'simple',
  'metrics_interpreter_agent': 'simple',
  'kill_scale_agent': 'simple',
  'insight_engine_agent': 'simple',
  'lessons_learned_agent': 'simple',
  'forecasting_agent': 'simple',
  'rag_status_agent': 'simple',
  'attribution_lite_agent': 'simple',
  'user_preference_agent': 'simple',
  'template_weighting_agent': 'simple',
  'behavior_tracking_agent': 'simple',
  'knowledge_base_builder_agent': 'simple',
  'periodic_internet_learner_agent': 'simple',
  'persona_evolution_agent': 'simple',
  'brand_memory_agent': 'simple',
  'creative_director_agent': 'simple'
};

export class ModelRouter {
  private static instance: ModelRouter;
  private modelCache: Map<string, ChatVertexAI | any> = new Map(); // TODO: Fix when BedrockChat is available
  private modelHealth: Map<ModelTier, { lastUsed: Date; errorCount: number; avgLatency: number }> = new Map();

  private constructor() {}

  static getInstance(): ModelRouter {
    if (!ModelRouter.instance) {
      ModelRouter.instance = new ModelRouter();
    }
    return ModelRouter.instance;
  }

  /**
   * Get the appropriate model for a task type (with health-aware routing)
   */
  getModelForTask(taskType: TaskType): ChatVertexAI | any { // TODO: Fix when BedrockChat is available
    return this.getHealthiestModel(taskType);
  }

  /**
   * Get the appropriate model for an agent (with health-aware routing)
   */
  getModelForAgent(agentName: string): ChatVertexAI | any {
    const taskType = AGENT_MODEL_OVERRIDES[agentName.toLowerCase().replace(/\s+/g, '_')] || 'general';
    return this.getHealthiestModel(taskType);
  }

  /**
   * Get model by tier (supports both Vertex AI and AWS Bedrock)
   */
  getModel(modelTier: ModelTier): ChatVertexAI | any {
    const cacheKey = modelTier;

    if (this.modelCache.has(cacheKey)) {
      return this.modelCache.get(cacheKey)!;
    }

    const config = MODEL_CONFIGS[modelTier];

    let model: ChatVertexAI | any;

    if (config.provider === 'bedrock') {
      // AWS Bedrock model - TODO: Uncomment when Bedrock is configured
      // model = new BedrockChat({
      //   model: config.modelId || config.name,
      //   region: config.region || env.AWS_REGION || 'us-east-1',
      //   maxTokens: config.maxTokens,
      //   temperature: config.temperature,
      //   maxRetries: 3,
      //   timeout: 60000
      // });
      // Fallback to Vertex AI for now
      model = new ChatVertexAI({
        model: 'gemini-1.5-flash-002', // Fallback model
        temperature: config.temperature,
        maxOutputTokens: config.maxTokens,
        topP: 0.95,
        topK: 40
      });
    } else {
      // Vertex AI model (default)
      model = new ChatVertexAI({
        model: config.name,
        location: env.GOOGLE_CLOUD_LOCATION,
        maxOutputTokens: config.maxTokens,
        temperature: config.temperature,
        // Additional safety settings
        safetySettings: [
          {
            category: 'HARM_CATEGORY_HARASSMENT',
            threshold: 'BLOCK_MEDIUM_AND_ABOVE'
          },
          {
            category: 'HARM_CATEGORY_HATE_SPEECH',
            threshold: 'BLOCK_MEDIUM_AND_ABOVE'
          }
        ]
      });
    }

    this.modelCache.set(cacheKey, model);
    return model;
  }

  /**
   * Route based on complexity heuristics
   */
  routeByComplexity(
    inputLength: number,
    taskComplexity: 'low' | 'medium' | 'high',
    requiresThinking = false
  ): ChatVertexAI {
    // Force thinking model for complex reasoning tasks
    if (requiresThinking || taskComplexity === 'high') {
      return this.getModel(ModelTier.REASONING_HEAVY);
    }

    // Route based on input size and complexity
    if (taskComplexity === 'medium' || inputLength > 2000) {
      return this.getModel(ModelTier.REASONING);
    }

    if (inputLength > 500) {
      return this.getModel(ModelTier.GENERAL);
    }

    return this.getModel(ModelTier.SIMPLE);
  }

  /**
   * Get model configuration
   */
  getModelConfig(modelTier: ModelTier): ModelConfig {
    return MODEL_CONFIGS[modelTier];
  }

  /**
   * Estimate cost for a request
   */
  estimateCost(
    modelTier: ModelTier,
    inputTokens: number,
    outputTokens: number
  ): number {
    const config = MODEL_CONFIGS[modelTier];
    const totalTokens = inputTokens + outputTokens;
    return (totalTokens / 1000) * config.costPerToken;
  }

  /**
   * Get all available models
   */
  getAvailableModels(): Record<ModelTier, ModelConfig> {
    return { ...MODEL_CONFIGS };
  }

  /**
   * Force use of AWS Bedrock models (for testing AWS deployment)
   */
  getBedrockModel(tier: 'opus' | 'sonnet' | 'haiku' | 'titan' = 'haiku'): BedrockChat {
    const bedrockTiers = {
      opus: ModelTier.BEDROCK_CLAUDE_3_OPUS,
      sonnet: ModelTier.BEDROCK_CLAUDE_3_SONNET,
      haiku: ModelTier.BEDROCK_CLAUDE_3_HAIKU,
      titan: ModelTier.BEDROCK_TITAN_TEXT_G1
    };

    return this.getModel(bedrockTiers[tier]) as BedrockChat;
  }

  /**
   * Check if AWS Bedrock is configured and available
   */
  isBedrockAvailable(): boolean {
    return !!(env.AWS_ACCESS_KEY_ID && env.AWS_SECRET_ACCESS_KEY);
  }

  /**
   * Clear model cache (useful for testing)
   */
  clearCache(): void {
    this.modelCache.clear();
    this.modelHealth.clear();
  }

  /**
   * Get model with fallback logic (SOTA reliability)
   */
  getModelWithFallback(modelTier: ModelTier, fallbackTier?: ModelTier): ChatVertexAI | any {
    try {
      const model = this.getModel(modelTier);

      // Update health metrics
      this.updateModelHealth(modelTier, true);

      return model;
    } catch (error) {
      console.warn(`Model ${modelTier} failed, attempting fallback`);

      // Update health metrics for failed model
      this.updateModelHealth(modelTier, false);

      // Try fallback if provided
      if (fallbackTier) {
        try {
          console.log(`Using fallback model: ${fallbackTier}`);
          return this.getModel(fallbackTier);
        } catch (fallbackError) {
          console.error(`Fallback model ${fallbackTier} also failed`);
        }
      }

      // Auto-fallback based on tier hierarchy
      const fallback = this.getAutomaticFallback(modelTier);
      if (fallback && fallback !== modelTier) {
        try {
          console.log(`Using automatic fallback: ${fallback}`);
          return this.getModel(fallback);
        } catch (autoFallbackError) {
          console.error(`Automatic fallback ${fallback} failed`);
        }
      }

      throw new Error(`All model fallbacks failed for tier ${modelTier}`);
    }
  }

  /**
   * Get automatic fallback based on tier hierarchy (optimized for cost/performance)
   */
  private getAutomaticFallback(modelTier: ModelTier): ModelTier | null {
    // Primary Vertex AI fallbacks (cost-effective within same provider)
    const vertexFallbacks: Record<ModelTier, ModelTier> = {
      [ModelTier.REASONING_HEAVY]: ModelTier.REASONING,      // 1.5 Pro → 2.0 Flash
      [ModelTier.REASONING]: ModelTier.GENERAL,              // 2.0 Flash → 2.5 Flash
      [ModelTier.GENERAL]: ModelTier.SIMPLE,                 // 2.5 Flash → 1.5 Flash
      [ModelTier.SIMPLE]: ModelTier.BEDROCK_CLAUDE_3_HAIKU,  // 1.5 Flash → Bedrock cheapest
    };

    // AWS Bedrock fallbacks (within Bedrock ecosystem)
    const bedrockFallbacks: Record<ModelTier, ModelTier> = {
      [ModelTier.BEDROCK_CLAUDE_3_OPUS]: ModelTier.BEDROCK_CLAUDE_3_SONNET,
      [ModelTier.BEDROCK_CLAUDE_3_SONNET]: ModelTier.BEDROCK_CLAUDE_3_HAIKU,
      [ModelTier.BEDROCK_CLAUDE_3_HAIKU]: ModelTier.BEDROCK_TITAN_TEXT_G1,
      [ModelTier.BEDROCK_TITAN_TEXT_G1]: ModelTier.SIMPLE  // Back to Vertex cheapest
    };

    // Try Vertex AI fallback first, then Bedrock
    return vertexFallbacks[modelTier] || bedrockFallbacks[modelTier] || null;
  }

  /**
   * Update model health metrics
   */
  private updateModelHealth(modelTier: ModelTier, success: boolean, latency?: number): void {
    const health = this.modelHealth.get(modelTier) || {
      lastUsed: new Date(),
      errorCount: 0,
      avgLatency: 0
    };

    health.lastUsed = new Date();

    if (success) {
      health.errorCount = Math.max(0, health.errorCount - 1); // Decay errors
      if (latency !== undefined) {
        health.avgLatency = (health.avgLatency + latency) / 2; // Simple moving average
      }
    } else {
      health.errorCount += 1;
    }

    this.modelHealth.set(modelTier, health);
  }

  /**
   * Get the healthiest available model for a task type (SOTA selection)
   * Prioritizes reliability over pure performance/cost
   */
  getHealthiestModel(taskType: TaskType): ChatVertexAI | any {
    const primaryTier = TASK_TO_TIER[taskType];
    const candidates = [
      primaryTier,
      this.getAutomaticFallback(primaryTier),
      this.getAutomaticFallback(this.getAutomaticFallback(primaryTier)!) // Second fallback
    ].filter(Boolean) as ModelTier[];

    // Score models by health metrics (lower is better)
    let bestModel: ModelTier = primaryTier;
    let bestScore = Infinity;

    for (const tier of candidates) {
      const health = this.modelHealth.get(tier);

      if (!health) {
        // No health data means it's likely healthy (prefer newer models)
        bestModel = tier;
        break;
      }

      // Weighted scoring: errors (40%) + latency (60%)
      const errorScore = health.errorCount * 40;
      const latencyScore = (health.avgLatency / 1000) * 60; // Normalize to seconds
      const totalScore = errorScore + latencyScore;

      if (totalScore < bestScore) {
        bestScore = totalScore;
        bestModel = tier;
      }
    }

    console.log(`🎯 Selected ${bestModel} for ${taskType} task (health score: ${bestScore.toFixed(2)})`);
    return this.getModelWithFallback(bestModel);
  }

  /**
   * Get routing statistics with health metrics
   */
  getStats(): {
    cached_models: number;
    available_tiers: number;
    agent_overrides: number;
    model_health: Record<string, any>;
    primary_provider: string;
  } {
    const healthStats: Record<string, any> = {};
    for (const [tier, health] of this.modelHealth.entries()) {
      healthStats[tier] = {
        last_used: health.lastUsed.toISOString(),
        error_count: health.errorCount,
        avg_latency: Math.round(health.avgLatency),
        health_score: Math.max(0, 100 - health.errorCount * 10)
      };
    }

    return {
      cached_models: this.modelCache.size,
      available_tiers: Object.keys(MODEL_CONFIGS).length,
      agent_overrides: Object.keys(AGENT_MODEL_OVERRIDES).length,
      model_health: healthStats,
      primary_provider: 'vertex_ai_with_bedrock_fallback'
    };
  }
}

// =====================================================
// GLOBAL ROUTER INSTANCE
// =====================================================

export const modelRouter = ModelRouter.getInstance();

// =====================================================
// UTILITY FUNCTIONS
// =====================================================

/**
 * Quick model getter for agents (with health-aware routing)
 */
export const getModelForAgent = (agentName: string): ChatVertexAI | any => {
  return modelRouter.getModelForAgent(agentName);
};

/**
 * Quick model getter for tasks (with health-aware routing)
 */
export const getModelForTask = (taskType: TaskType): ChatVertexAI | any => {
  return modelRouter.getModelForTask(taskType);
};

/**
 * Estimate complexity from text
 */
export const estimateComplexity = (text: string): 'low' | 'medium' | 'high' => {
  const words = text.split(/\s+/).length;
  const hasComplexTerms = /\b(analyze|strategic|optimization|forecast|predict|model|algorithm)\b/i.test(text);
  const hasStructuredData = text.includes('{') || text.includes('[');

  if (words > 1000 || hasComplexTerms || hasStructuredData) {
    return 'high';
  }
  if (words > 300) {
    return 'medium';
  }
  return 'low';
};

/**
 * Smart routing based on input analysis (with health awareness)
 */
export const smartRoute = (
  agentName: string,
  input: string,
  options?: {
    forceTier?: ModelTier;
    requiresThinking?: boolean;
    preferBedrock?: boolean;
  }
): ChatVertexAI | any => {
  if (options?.forceTier) {
    return modelRouter.getModelWithFallback(options.forceTier);
  }

  // Force Bedrock if requested and available
  if (options?.preferBedrock && modelRouter.isBedrockAvailable()) {
    try {
      return modelRouter.getBedrockModel('haiku');
    } catch (error) {
      console.warn('Bedrock requested but failed, falling back to Vertex AI');
    }
  }

  const complexity = estimateComplexity(input);
  return modelRouter.routeByComplexity(
    input.length,
    complexity,
    options?.requiresThinking
  );
};
