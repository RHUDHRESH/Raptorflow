/**
 * LLM Adapter for Orchestrator
 *
 * Vertex AI primary with OpenAI fallback, includes tracing and cost logging.
 * Handles automatic failover, request tracing, and usage metrics.
 */

import { ChatVertexAI } from '@langchain/google-vertexai';
import { ChatOpenAI } from '@langchain/openai';
import { env } from '../../config/env';
import { redisMemory } from '../../services/redisMemory';
import { telemetryService } from '../../services/telemetryService';

export interface LLMRequest {
  messages: Array<{ role: string; content: string }>;
  model?: string;
  temperature?: number;
  maxTokens?: number;
  agentName?: string;
  jobId?: string;
  userId?: string;
}

export interface LLMResponse {
  content: string;
  model: string;
  usage: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
  cost: number;
  latency: number;
  provider: 'vertex' | 'openai';
  fallbackUsed?: boolean;
}

export interface LLMError {
  message: string;
  code: string;
  provider: 'vertex' | 'openai';
  retryable: boolean;
}

class LLMAdapter {
  private vertexClient: ChatVertexAI;
  private openaiClient: ChatOpenAI | null = null;
  private readonly maxRetries = 3;
  private readonly retryDelay = 1000; // 1 second

  constructor() {
    // Initialize Vertex AI client
    this.vertexClient = new ChatVertexAI({
      model: 'gemini-2.5-flash-preview-05-20',
      location: env.GOOGLE_CLOUD_LOCATION,
      maxOutputTokens: 4096,
      temperature: 0.3,
    });

    // Initialize OpenAI client if API key is available
    if (env.OPENAI_API_KEY) {
      this.openaiClient = new ChatOpenAI({
        openAIApiKey: env.OPENAI_API_KEY,
        modelName: 'gpt-4o-mini',
        maxTokens: 4096,
        temperature: 0.3,
      });
    }
  }

  /**
   * Generate completion with Vertex AI primary, OpenAI fallback
   */
  async generateImage(options: {
    prompt: string;
    size?: string;
    quality?: 'standard' | 'hd';
    n?: number;
  }): Promise<{ imageBuffer: Buffer; metadata: any }> {
    const { prompt, size = '1024x1024', quality = 'standard', n = 1 } = options;

    // Use OpenAI DALL-E as primary image generation service
    try {
      const openai = await this.getOpenAIClient();

      const response = await openai.images.generate({
        model: 'dall-e-3',
        prompt,
        size: size as any,
        quality,
        n,
        response_format: 'url',
      });

      if (!response.data || response.data.length === 0) {
        throw new Error('No image data received from DALL-E');
      }

      // Download the image
      const imageUrl = response.data[0].url!;
      const imageResponse = await fetch(imageUrl);
      const imageBuffer = Buffer.from(await imageResponse.arrayBuffer());

      // Log usage
      await this.logUsage({
        provider: 'openai',
        model: 'dall-e-3',
        usage: {
          images: n,
          size,
          quality,
        },
        cost: this.calculateImageCost('dall-e-3', size, quality),
        latency: 0, // Would need to track this
        success: true,
      });

      return {
        imageBuffer,
        metadata: {
          provider: 'openai',
          model: 'dall-e-3',
          size,
          quality,
          prompt,
        },
      };

    } catch (error) {
      console.error('DALL-E image generation failed:', error);

      // Fallback to Vertex AI (if available) or throw error
      throw new Error(`Image generation failed: ${error.message}`);
    }
  }

  private calculateImageCost(model: string, size: string, quality: 'standard' | 'hd'): number {
    // DALL-E 3 pricing (as of 2024)
    const pricing = {
      'dall-e-3': {
        '1024x1024': { standard: 0.04, hd: 0.08 },
        '1792x1024': { standard: 0.08, hd: 0.12 },
        '1024x1792': { standard: 0.08, hd: 0.12 },
      },
    };

    return pricing[model]?.[size]?.[quality] || 0.04;
  }

  async generate(request: LLMRequest): Promise<LLMResponse> {
    const startTime = Date.now();
    const traceId = this.generateTraceId();

    // Log request start
    console.log(`🔄 [${traceId}] LLM Request: ${request.agentName || 'unknown'} - ${request.messages.length} messages`);

    let lastError: LLMError | null = null;

    // Try Vertex AI first
    try {
      const response = await this.tryVertexAI(request, traceId);
      const latency = Date.now() - startTime;

      await this.logUsage(response, request, latency, traceId);

      console.log(`✅ [${traceId}] Vertex AI success: ${response.usage.totalTokens} tokens, $${response.cost.toFixed(4)}`);

      return response;
    } catch (error) {
      lastError = this.parseVertexError(error);
      console.warn(`⚠️ [${traceId}] Vertex AI failed: ${lastError.message}`);

      // Try OpenAI fallback if available and error is retryable
      if (this.openaiClient && lastError.retryable) {
        try {
          console.log(`🔄 [${traceId}] Attempting OpenAI fallback`);
          const response = await this.tryOpenAI(request, traceId);
          const latency = Date.now() - startTime;

          await this.logUsage({ ...response, fallbackUsed: true }, request, latency, traceId);

          console.log(`✅ [${traceId}] OpenAI fallback success: ${response.usage.totalTokens} tokens, $${response.cost.toFixed(4)}`);

          return { ...response, fallbackUsed: true };
        } catch (openaiError) {
          const openaiErrorParsed = this.parseOpenAIError(openaiError);
          console.error(`❌ [${traceId}] OpenAI fallback also failed: ${openaiErrorParsed.message}`);

          lastError = openaiErrorParsed;
        }
      }
    }

    // All attempts failed
    const finalError = lastError || { message: 'Unknown error', code: 'UNKNOWN', provider: 'vertex' as const, retryable: false };
    throw new Error(`LLM request failed: ${finalError.message}`);
  }

  /**
   * Try Vertex AI request
   */
  private async tryVertexAI(request: LLMRequest, traceId: string): Promise<LLMResponse> {
    const model = this.getVertexModel(request);

    // Convert messages to LangChain format
    const messages = request.messages.map(msg => ({
      role: msg.role === 'user' ? 'human' : msg.role === 'assistant' ? 'ai' : 'system',
      content: msg.content,
    }));

    try {
      const response = await model.invoke(messages);

      // Estimate token usage (Vertex AI doesn't provide exact counts)
      const estimatedPromptTokens = this.estimateTokens(request.messages.map(m => m.content).join(' '));
      const estimatedCompletionTokens = this.estimateTokens(response.content);
      const totalTokens = estimatedPromptTokens + estimatedCompletionTokens;

      // Calculate cost (rough estimates for Gemini 2.5 Flash)
      const cost = this.calculateVertexCost(totalTokens);

      return {
        content: response.content,
        model: model.model,
        usage: {
          promptTokens: estimatedPromptTokens,
          completionTokens: estimatedCompletionTokens,
          totalTokens,
        },
        cost,
        latency: 0, // Will be set by caller
        provider: 'vertex',
      };
    } catch (error) {
      throw error;
    }
  }

  /**
   * Try OpenAI fallback request
   */
  private async tryOpenAI(request: LLMRequest, traceId: string): Promise<LLMResponse> {
    if (!this.openaiClient) {
      throw new Error('OpenAI client not configured');
    }

    const model = this.getOpenAIModel(request);

    // Convert messages to LangChain format
    const messages = request.messages.map(msg => ({
      role: msg.role,
      content: msg.content,
    }));

    const response = await model.invoke(messages);

    // Get actual usage from OpenAI response
    const usage = response.response_metadata?.usage;
    const promptTokens = usage?.prompt_tokens || 0;
    const completionTokens = usage?.completion_tokens || 0;
    const totalTokens = usage?.total_tokens || (promptTokens + completionTokens);

    // Calculate OpenAI cost
    const cost = this.calculateOpenAICost(totalTokens, model.modelName);

    return {
      content: response.content,
      model: model.modelName,
      usage: {
        promptTokens,
        completionTokens,
        totalTokens,
      },
      cost,
      latency: 0, // Will be set by caller
      provider: 'openai',
    };
  }

  /**
   * Get appropriate Vertex AI model
   */
  private getVertexModel(request: LLMRequest): ChatVertexAI {
    const modelName = request.model || 'gemini-2.5-flash-preview-05-20';

    return new ChatVertexAI({
      model: modelName,
      location: env.GOOGLE_CLOUD_LOCATION,
      maxOutputTokens: request.maxTokens || 4096,
      temperature: request.temperature || 0.3,
    });
  }

  /**
   * Get appropriate OpenAI model
   */
  private getOpenAIModel(request: LLMRequest): ChatOpenAI {
    if (!this.openaiClient) {
      throw new Error('OpenAI client not configured');
    }

    const modelName = request.model || 'gpt-4o-mini';

    return new ChatOpenAI({
      openAIApiKey: env.OPENAI_API_KEY,
      modelName,
      maxTokens: request.maxTokens || 4096,
      temperature: request.temperature || 0.3,
    });
  }

  /**
   * Log usage metrics and costs
   */
  private async logUsage(
    response: LLMResponse,
    request: LLMRequest,
    latency: number,
    traceId: string
  ): Promise<void> {
    try {
      const usageRecord = {
        id: `llm_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        traceId,
        timestamp: new Date().toISOString(),
        agentName: request.agentName,
        jobId: request.jobId,
        userId: request.userId,
        provider: response.provider,
        model: response.model,
        fallbackUsed: response.fallbackUsed || false,
        usage: response.usage,
        cost: response.cost,
        latency,
        metadata: {
          messageCount: request.messages.length,
          temperature: request.temperature,
          maxTokens: request.maxTokens,
        },
      };

      // Log to telemetry service
      await telemetryService.logLLMUsage(usageRecord);

      // Also store in Redis for backward compatibility
      await redisMemory.store(
        `llm_usage:${traceId}`,
        usageRecord,
        86400 * 30 // 30 days
      );

    } catch (error) {
      console.error('Failed to log LLM usage:', error);
    }
  }

  /**
   * Estimate token count (rough approximation)
   */
  private estimateTokens(text: string): number {
    // Rough approximation: 1 token ≈ 4 characters for English text
    return Math.ceil(text.length / 4);
  }

  /**
   * Calculate Vertex AI cost (rough estimates)
   */
  private calculateVertexCost(totalTokens: number): number {
    // Gemini 2.5 Flash pricing (approximate)
    // $0.15 per 1M input tokens, $0.60 per 1M output tokens
    // For simplicity, using average rate
    const costPerThousandTokens = 0.0003; // ~$0.30 per 1K tokens average
    return (totalTokens / 1000) * costPerThousandTokens;
  }

  /**
   * Calculate OpenAI cost
   */
  private calculateOpenAICost(totalTokens: number, model: string): number {
    // GPT-4o mini pricing
    const inputCostPerToken = 0.15 / 1000000; // $0.15 per 1M tokens
    const outputCostPerToken = 0.60 / 1000000; // $0.60 per 1M tokens

    // Rough split: assume 30% output tokens
    const estimatedOutputTokens = Math.ceil(totalTokens * 0.3);
    const estimatedInputTokens = totalTokens - estimatedOutputTokens;

    return (estimatedInputTokens * inputCostPerToken) + (estimatedOutputTokens * outputCostPerToken);
  }

  /**
   * Parse Vertex AI errors
   */
  private parseVertexError(error: any): LLMError {
    return {
      message: error.message || 'Vertex AI request failed',
      code: error.code || 'VERTEX_ERROR',
      provider: 'vertex',
      retryable: this.isRetryableError(error),
    };
  }

  /**
   * Parse OpenAI errors
   */
  private parseOpenAIError(error: any): LLMError {
    return {
      message: error.message || 'OpenAI request failed',
      code: error.code || 'OPENAI_ERROR',
      provider: 'openai',
      retryable: this.isRetryableError(error),
    };
  }

  /**
   * Determine if error is retryable
   */
  private isRetryableError(error: any): boolean {
    const retryableCodes = ['ECONNRESET', 'ETIMEDOUT', 'ENOTFOUND', '429', '500', '502', '503', '504'];
    const errorCode = error.code || error.status || '';

    return retryableCodes.some(code => errorCode.toString().includes(code));
  }

  /**
   * Generate unique trace ID
   */
  private generateTraceId(): string {
    return `llm_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Get usage statistics
   */
  async getUsageStats(hours: number = 24): Promise<{
    totalRequests: number;
    totalTokens: number;
    totalCost: number;
    averageLatency: number;
    fallbackRate: number;
  }> {
    // This would aggregate data from Redis/database
    // Implementation would depend on how we store the logs
    return {
      totalRequests: 0,
      totalTokens: 0,
      totalCost: 0,
      averageLatency: 0,
      fallbackRate: 0,
    };
  }

  /**
   * Health check for LLM providers
   */
  async healthCheck(): Promise<{
    vertex: boolean;
    openai: boolean;
  }> {
    const results = {
      vertex: false,
      openai: false,
    };

    // Test Vertex AI
    try {
      await this.tryVertexAI({
        messages: [{ role: 'user', content: 'Hello' }],
      }, 'health_check');
      results.vertex = true;
    } catch (error) {
      console.warn('Vertex AI health check failed:', error.message);
    }

    // Test OpenAI
    if (this.openaiClient) {
      try {
        await this.tryOpenAI({
          messages: [{ role: 'user', content: 'Hello' }],
        }, 'health_check');
        results.openai = true;
      } catch (error) {
        console.warn('OpenAI health check failed:', error.message);
      }
    }

    return results;
  }
}

// Export singleton instance
export const llmAdapter = new LLMAdapter();

// Export types
export type { LLMRequest, LLMResponse, LLMError };
