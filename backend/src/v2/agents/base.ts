/**
 * Base Orchestrator Agent
 *
 * Pure functions that accept typed inputs and return typed outputs.
 * Each agent exports a manifest and generate() function.
 */

import { z } from 'zod';
import { llmAdapter } from '../llm/adapter';
import { promptStore } from '../prompts/index';
import { redisMemory } from '../../services/redisMemory';

export interface AgentManifest {
  name: string;
  description: string;
  version: string;
  category: 'brand' | 'content' | 'marketing' | 'creative' | 'technical';
  inputs: {
    required: string[];
    optional: string[];
  };
  outputs: {
    type: string;
    format: 'text' | 'json' | 'markdown' | 'html';
    schema?: z.ZodSchema;
  };
  capabilities: string[];
  costEstimate: {
    minTokens: number;
    maxTokens: number;
    estimatedCost: number;
  };
  connectors?: string[]; // External services needed (S3, SES, etc.)
  metadata: {
    author: string;
    tags: string[];
    complexity: 'simple' | 'medium' | 'complex';
  };
}

export interface AgentInput {
  brandProfileId: string;
  inputOverrides?: Record<string, any>;
  contextSnapshot?: Record<string, any>;
  jobId?: string;
  userId?: string;
}

export interface AgentOutput {
  content: any;
  metadata: {
    model: string;
    promptVersion: string;
    tokens: number;
    cost: number;
    latency: number;
    provenance: Record<string, any>;
  };
}

export interface AgentContext {
  brandProfile: any;
  project?: any;
  conversationHistory?: any[];
  previousOutputs?: any[];
}

export abstract class BaseOrchestratorAgent {
  public readonly manifest: AgentManifest;

  constructor(manifest: AgentManifest) {
    this.manifest = manifest;
  }

  /**
   * Generate content using the agent
   */
  abstract generate(input: AgentInput): Promise<AgentOutput>;

  /**
   * Validate input against manifest requirements
   */
  protected validateInput(input: AgentInput): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    // Check required inputs
    for (const required of this.manifest.inputs.required) {
      if (!input[required as keyof AgentInput] && !input.inputOverrides?.[required]) {
        errors.push(`Missing required input: ${required}`);
      }
    }

    return { valid: errors.length === 0, errors };
  }

  /**
   * Get context for prompt rendering
   */
  protected async getContext(input: AgentInput): Promise<AgentContext> {
    const context: AgentContext = {
      brandProfile: null,
      project: null,
      conversationHistory: [],
      previousOutputs: [],
    };

    // Get brand profile from cache or database
    if (input.brandProfileId) {
      context.brandProfile = await redisMemory.getCachedBrandProfile(input.brandProfileId);
      // TODO: Fetch from database if not cached
    }

    // Get conversation history if available
    if (input.jobId) {
      const conversation = await redisMemory.getConversation(input.jobId);
      if (conversation) {
        context.conversationHistory = conversation.messages;
      }
    }

    return context;
  }

  /**
   * Render prompt with context
   */
  protected async renderPrompt(context: AgentContext, input: AgentInput): Promise<string> {
    const promptContext = {
      agentName: this.manifest.name,
      brandProfile: context.brandProfile,
      project: context.project,
      inputOverrides: input.inputOverrides,
      contextSnapshot: input.contextSnapshot,
    };

    const rendered = await promptStore.getRenderedPromptForAgent(
      this.manifest.name,
      promptContext
    );

    return rendered || this.getDefaultPrompt(context, input);
  }

  /**
   * Generate LLM request
   */
  protected async generateLLMRequest(
    prompt: string,
    input: AgentInput
  ): Promise<{ content: string; metadata: any }> {
    const messages = [
      { role: 'system', content: prompt },
    ];

    // Add conversation history if available
    if (input.contextSnapshot?.conversationHistory) {
      messages.push(...input.contextSnapshot.conversationHistory);
    }

    const response = await llmAdapter.generate({
      messages,
      agentName: this.manifest.name,
      jobId: input.jobId,
      userId: input.userId,
    });

    return {
      content: response.content,
      metadata: {
        model: response.model,
        promptVersion: '1.0.0', // TODO: Get from prompt store
        tokens: response.usage.totalTokens,
        cost: response.cost,
        latency: response.latency,
        provenance: {
          provider: response.provider,
          fallbackUsed: response.fallbackUsed,
          traceId: `llm_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        },
      },
    };
  }

  /**
   * Process and validate output
   */
  protected processOutput(rawContent: string, metadata: any): AgentOutput {
    let processedContent = rawContent;

    // Validate against output schema if provided
    if (this.manifest.outputs.schema) {
      try {
        const parsed = this.manifest.outputs.schema.parse(JSON.parse(rawContent));
        processedContent = parsed;
      } catch (error) {
        console.warn(`Output validation failed for ${this.manifest.name}:`, error);
        // Continue with raw content
      }
    }

    return {
      content: processedContent,
      metadata,
    };
  }

  /**
   * Default prompt fallback
   */
  protected getDefaultPrompt(context: AgentContext, input: AgentInput): string {
    return `You are a ${this.manifest.description}. Generate content based on the following context and requirements.

Brand Profile: ${JSON.stringify(context.brandProfile)}
Input Overrides: ${JSON.stringify(input.inputOverrides)}
Context: ${JSON.stringify(input.contextSnapshot)}

Generate the requested content following best practices for ${this.manifest.category} content.`;
  }

  /**
   * Store agent memory for future use
   */
  protected async storeAgentMemory(
    sessionId: string,
    data: any,
    ttlSeconds: number = 7200
  ): Promise<void> {
    await redisMemory.storeAgentMemory(this.manifest.name, sessionId, data, ttlSeconds);
  }

  /**
   * Retrieve agent memory
   */
  protected async getAgentMemory(sessionId: string): Promise<any> {
    return await redisMemory.getAgentMemory(this.manifest.name, sessionId);
  }
}

// Export types
export type { AgentManifest, AgentInput, AgentOutput, AgentContext };
