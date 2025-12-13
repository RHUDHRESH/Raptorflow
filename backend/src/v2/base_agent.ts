import { z } from 'zod';
import { AgentExecutor, createReactAgent } from "langchain/agents";
import { ChatPromptTemplate, MessagesPlaceholder } from "@langchain/core/prompts";
import { modelRouter, smartRoute } from './router';
import { toolbox } from './toolbox';
import { AgentIO, OrchestratorContext, BaseAgent as IBaseAgent } from './types';
import { budgetMiddleware, estimateTokensForTask } from './budget_middleware';
import { assembleSystemPrompt, AgentPromptContext, estimateTokenCount } from './prompts';
import { promptCache } from './cache';
import { tokenOptimizer, tokenBudgetManager } from './token_optimizer';

// =====================================================
// BASE AGENT CLASS - LANGCHAIN ADVANCED AGENTIC
// =====================================================

export abstract class BaseAgent implements IBaseAgent {
  public name: string;
  public department: any; // Will be imported from types
  public description: string;
  public input_schema: z.ZodSchema;
  public output_schema: z.ZodSchema;

  protected agentExecutor: AgentExecutor;
  protected prompt: ChatPromptTemplate;
  protected required_tools: string[] = [];
  protected model: any;

  constructor(
    name: string,
    department: any,
    description: string,
    inputSchema: z.ZodSchema,
    outputSchema: z.ZodSchema
  ) {
    this.name = name;
    this.department = department;
    this.description = description;
    this.input_schema = inputSchema;
    this.output_schema = outputSchema;

    // Initialize model
    this.model = modelRouter.getModelForAgent(this.name);

    // Build LangChain agent executor (highest level agentic abstraction)
    this.agentExecutor = this.buildAgentExecutor();
    this.prompt = this.buildPrompt();
  }

  /**
   * Build LangChain AgentExecutor with advanced agentic capabilities
   */
  private buildAgentExecutor(): AgentExecutor {
    const model = modelRouter.getModelForAgent(this.name);
    const tools = this.getTools();

    // Create ReAct agent (highest level of agentic reasoning)
    const agent = createReactAgent({
      llm: model,
      tools,
      prompt: this.buildPrompt(),
    });

    // AgentExecutor with advanced configuration
    return AgentExecutor.fromAgentAndTools({
      agent: agent as any,
      tools,
      callbacks: [
        {
          handleAgentAction: (action) => {
            console.log(`🔧 ${this.name} executing: ${action.tool}(${JSON.stringify(action.toolInput)})`);
          },
          handleAgentEnd: (result) => {
            console.log(`✅ ${this.name} completed: ${result.returnValues?.output?.substring(0, 100)}...`);
          },
          handleChainError: (error) => {
            console.error(`❌ ${this.name} chain error:`, error);
          }
        }
      ],
      maxIterations: 5,
      maxExecutionTime: 30000, // 30 seconds
      earlyStoppingMethod: "generate",
      returnIntermediateSteps: true,
      handleParsingErrors: true,
      verbose: process.env.NODE_ENV === 'development'
    });
  }

  /**
   * Build agent prompt template using SOTA prompt engineering
   */
  private buildPrompt(): ChatPromptTemplate {
    const context: AgentPromptContext = {
      agentName: this.name,
      department: this.department,
      tools: this.required_tools,
      context: {}
    };

    let systemPrompt = assembleSystemPrompt(this.name, context);

    // Apply SOTA token optimization
    const compressionResult = tokenOptimizer.compressPrompt(systemPrompt, 0.85); // Target 15% reduction
    systemPrompt = compressionResult.compressed;

    // Log token optimization for monitoring
    const originalTokens = compressionResult.originalTokens;
    const compressedTokens = compressionResult.compressedTokens;
    const savingsPercent = Math.round((1 - compressionResult.compressionRatio) * 100);

    console.log(`🤖 ${this.name} system prompt: ${compressedTokens}/${originalTokens} tokens (${savingsPercent}% saved)`);

    return ChatPromptTemplate.fromMessages([
      ["system", systemPrompt],
      ["human", "{input}"],
      new MessagesPlaceholder("agent_scratchpad"),
    ]);
  }


  /**
   * Execute the agent using LangChain AgentExecutor (highest level agentic execution)
   */
  async execute(input: any, context: OrchestratorContext): Promise<AgentIO> {
    const startTime = Date.now();
    const sessionId = `${context.user_id}_${this.name}_${Date.now()}`;

    try {
      // Validate input
      this.validate_input(input);

      // Estimate tokens with SOTA optimization
      const inputText = JSON.stringify(input);
      const estimatedTokens = estimateTokensForTask('general', inputText.length);

      // Check token budget (SOTA resource management)
      const tokenBudget = tokenBudgetManager.allocateBudget(sessionId, 50000); // 50K token budget per session
      const budgetCheck = tokenBudgetManager.checkBudget(sessionId, estimatedTokens);

      if (!budgetCheck.allowed) {
        throw new Error(`Token budget exceeded: ${budgetCheck.remainingTokens} tokens remaining`);
      }

      // Check legacy budget system
      const legacyBudgetCheck = budgetMiddleware.canExecuteAgent(
        context.user_id,
        this.name,
        estimatedTokens,
        estimatedTokens * 0.0001 // Rough cost estimate
      );

      if (!legacyBudgetCheck.allowed) {
        throw new Error(`Budget check failed: ${legacyBudgetCheck.reason}`);
      }

      // Prepare input for LangChain agent with token optimization
      const formattedInput = this.formatAgentInput(input, context);

      // Apply context optimization if input is too long
      const contextCheck = tokenOptimizer.willFitInContext(formattedInput, 8000); // Assume 8K context limit
      let optimizedInput = formattedInput;

      if (!contextCheck.fits) {
        console.log(`📏 Compressing context for ${this.name}: ${contextCheck.tokens} → ${contextCheck.compressedTokens} tokens`);
        const compression = tokenOptimizer.compressPrompt(formattedInput, 0.7);
        optimizedInput = compression.compressed;
      }

      const agentInput = {
        input: optimizedInput,
        ...this.getAdditionalContext(context)
      };

      // Check prompt cache for similar inputs (SOTA optimization)
      const promptHash = promptCache.generatePromptHash(
        formattedInput,
        modelRouter.getModelConfig(this.getModelTier()).name,
        this.getModelTemperature()
      );

      let cachedResponse = await promptCache.getCachedPrompt(promptHash);
      let result: any;

      if (cachedResponse) {
        console.log(`💾 Prompt cache hit for ${this.name}`);
        // Simulate LangChain result format
        result = {
          output: cachedResponse.response,
          intermediateSteps: [],
          metadata: cachedResponse.metadata
        };
      } else {
        // Execute using LangChain AgentExecutor (highest level agentic abstraction)
        result = await this.agentExecutor.call(agentInput);

        // Cache the response for future use
        try {
          await promptCache.cachePromptResponse(
            promptHash,
            result.output,
            {
              model: modelRouter.getModelConfig(this.getModelTier()).name,
              tokens_used: this.calculateTokenUsage(agentInput, result),
              temperature: this.getModelTemperature()
            }
          );
          console.log(`💾 Cached prompt response for ${this.name}`);
        } catch (cacheError) {
          console.warn(`Prompt cache write failed:`, cacheError);
        }
      }

      // Parse and validate output
      const parsedOutput = this.parseAgentOutput(result.output);

      // Calculate usage metrics with SOTA tracking
      const tokenUsage = this.calculateTokenUsage(agentInput, result);
      const costEstimate = this.calculateCost(tokenUsage);

      // Record usage in both systems
      tokenBudgetManager.recordUsage(sessionId, tokenUsage);
      budgetMiddleware.recordUsage(context.user_id, this.name, tokenUsage, costEstimate);

      const executionTime = Date.now() - startTime;

      return {
        inputs: input,
        outputs: parsedOutput,
        metadata: {
          agent_name: this.name,
          execution_time: executionTime,
          token_usage: tokenUsage,
          cost_estimate: costEstimate,
          model_used: modelRouter.getModelForAgent(this.name).model,
          success: true,
          timestamp: new Date().toISOString()
        }
      };

    } catch (error: any) {
      const executionTime = Date.now() - startTime;

      console.error(`LangChain Agent ${this.name} failed:`, error);

      return {
        inputs: input,
        outputs: {},
        metadata: {
          agent_name: this.name,
          execution_time: executionTime,
          token_usage: 0,
          cost_estimate: 0,
          model_used: modelRouter.getModelForAgent(this.name).model,
          success: false,
          errors: [error.message],
          timestamp: new Date().toISOString()
        }
      };
    }
  }

  /**
   * Format input for LangChain agent
   */
  protected formatAgentInput(input: any, context: OrchestratorContext): string {
    return `Task: ${JSON.stringify(input, null, 2)}

Context: ${JSON.stringify(context, null, 2)}

Execute your specialized role with maximum effectiveness.`;
  }

  /**
   * Get additional context for agent execution
   */
  protected getAdditionalContext(context: OrchestratorContext): Record<string, any> {
    return {};
  }

  /**
   * Parse and validate agent output using SOTA structured output techniques
   */
  protected parseAgentOutput(rawOutput: string): any {
    if (!rawOutput || typeof rawOutput !== 'string') {
      console.warn(`⚠️ ${this.name}: Invalid raw output type: ${typeof rawOutput}`);
      return { error: 'Invalid output format', raw: rawOutput };
    }

    // Strategy 1: Direct JSON parsing
    try {
      const parsed = JSON.parse(rawOutput.trim());
      return this.validateWithSchema(parsed);
    } catch (jsonError) {
      console.log(`📄 ${this.name}: JSON parsing failed, trying structured extraction`);
    }

    // Strategy 2: Extract JSON from markdown code blocks
    const jsonMatch = rawOutput.match(/```(?:json)?\s*(\{[\s\S]*?\})\s*```/);
    if (jsonMatch) {
      try {
        const extractedJson = JSON.parse(jsonMatch[1]);
        return this.validateWithSchema(extractedJson);
      } catch (extractError) {
        console.log(`📄 ${this.name}: JSON extraction failed`);
      }
    }

    // Strategy 3: Look for JSON-like patterns in text
    const jsonPattern = /\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}/g;
    const matches = rawOutput.match(jsonPattern);
    if (matches) {
      for (const match of matches) {
        try {
          const parsed = JSON.parse(match);
          const validated = this.validateWithSchema(parsed);
          if (validated) return validated;
        } catch {
          continue;
        }
      }
    }

    // Strategy 4: Fallback - return structured text analysis
    console.log(`📄 ${this.name}: Using fallback text parsing`);
    return {
      text_output: rawOutput,
      structured_analysis: this.extractStructuredElements(rawOutput),
      parsing_method: 'fallback_text'
    };
  }

  /**
   * Validate parsed output against the agent's zod schema
   */
  private validateWithSchema(parsedOutput: any): any {
    try {
      if (this.output_schema) {
        const validated = this.output_schema.parse(parsedOutput);
        console.log(`✅ ${this.name}: Output validation successful`);
        return validated;
      }
      return parsedOutput;
    } catch (validationError: any) {
      console.warn(`⚠️ ${this.name}: Schema validation failed:`, validationError.message);

      // Try to fix common validation issues
      const fixed = this.attemptValidationFix(parsedOutput, validationError);
      if (fixed) {
        console.log(`🔧 ${this.name}: Validation auto-fixed`);
        return fixed;
      }

      // Return with validation error info
      return {
        ...parsedOutput,
        _validation_error: validationError.message,
        _validation_issues: validationError.issues || []
      };
    }
  }

  /**
   * Attempt to fix common validation issues
   */
  private attemptValidationFix(data: any, error: any): any | null {
    if (!error.issues) return null;

    const fixed = { ...data };

    for (const issue of error.issues) {
      const path = issue.path?.join('.');
      if (!path) continue;

      // Fix missing required fields with defaults
      if (issue.code === 'invalid_type' && issue.received === 'undefined') {
        if (path.includes('score') || path.includes('confidence')) {
          fixed[path] = 0.5;
        } else if (path.includes('count') || path.includes('number')) {
          fixed[path] = 0;
        } else if (path.includes('list') || path.includes('array')) {
          fixed[path] = [];
        } else {
          fixed[path] = null;
        }
      }

      // Fix type mismatches
      if (issue.code === 'invalid_type') {
        if (issue.expected === 'number' && typeof data[path] === 'string') {
          const num = parseFloat(data[path]);
          if (!isNaN(num)) fixed[path] = num;
        } else if (issue.expected === 'string' && typeof data[path] === 'number') {
          fixed[path] = String(data[path]);
        } else if (issue.expected === 'boolean') {
          fixed[path] = Boolean(data[path]);
        }
      }
    }

    // Try validation again
    try {
      return this.output_schema.parse(fixed);
    } catch {
      return null;
    }
  }

  /**
   * Extract structured elements from unstructured text
   */
  private extractStructuredElements(text: string): any {
    const analysis = {
      word_count: text.split(/\s+/).length,
      sentences: text.split(/[.!?]+/).filter(s => s.trim()).length,
      contains_json: /\{.*\}/.test(text),
      contains_lists: /^[\s]*[-*•]\s/m.test(text),
      confidence_score: 0.5
    };

    // Try to extract key-value pairs
    const kvMatches = text.matchAll(/(\w+):\s*([^\n,]+)/g);
    const extracted = {};
    for (const match of kvMatches) {
      extracted[match[1].toLowerCase().replace(/\s+/g, '_')] = match[2].trim();
    }

    if (Object.keys(extracted).length > 0) {
      analysis.extracted_fields = extracted;
    }

    return analysis;
  }

  /**
   * Get the model tier currently being used by this agent
   */
  private getModelTier(): any {
    // This is a simplified implementation - in practice you'd track the actual model used
    return 'general';
  }

  /**
   * Get the temperature setting for the current model
   */
  private getModelTemperature(): number {
    // This is a simplified implementation - in practice you'd get this from the model config
    return 0.2;
  }

  /**
   * Calculate token usage from execution
   */
  protected calculateTokenUsage(input: any, result: any): number {
    const inputTokens = JSON.stringify(input).length / 4; // Rough token estimation
    const outputTokens = JSON.stringify(result).length / 4;
    const intermediateTokens = (result.intermediateSteps?.length || 0) * 50;

    return Math.ceil(inputTokens + outputTokens + intermediateTokens);
  }

  /**
   * Calculate execution cost
   */
  protected calculateCost(tokenUsage: number): number {
    // Get model cost from router
    const model = modelRouter.getModelForAgent(this.name);
    return tokenUsage * 0.0001; // Rough estimate, would use actual model pricing
  }

  /**
   * Validate input
   */
  validate_input(input: any): boolean {
    try {
      this.input_schema.parse(input);
      return true;
    } catch (error) {
      throw new Error(`Invalid input for ${this.name}: ${error}`);
    }
  }

  /**
   * Get required tools
   */
  get_required_tools(): string[] {
    return this.required_tools;
  }

  /**
   * Abstract method for agent-specific system prompt
   */
  protected abstract getSystemPrompt(): string;

  /**
   * Helper to get tools for execution
   */
  protected getTools(): any[] {
    return this.required_tools.map(toolName => toolbox.getLangChainTool(toolName)).filter(Boolean);
  }

  /**
   * Helper to execute tools
   */
  protected async executeTool(toolName: string, params: any): Promise<any> {
    return toolbox.executeTool(toolName, params);
  }

  /**
   * Helper to get user preferences
   */
  protected async getUserPreferences(userId: string): Promise<Record<string, any>> {
    // This would integrate with preference service
    return {};
  }

  /**
   * Helper to get brand context
   */
  protected async getBrandContext(userId: string): Promise<string> {
    // This would integrate with brand memory service
    return "Use professional, engaging tone.";
  }

  /**
   * Create structured output parser
   */
  protected createParser() {
    const { StructuredOutputParser } = require("@langchain/core/output_parsers");
    return StructuredOutputParser.fromZodSchema(this.output_schema);
  }

  /**
   * Create prompt template
   */
  protected createPrompt(template: string, variables: string[]) {
    const { PromptTemplate } = require("@langchain/core/prompts");
    return new PromptTemplate({
      template,
      inputVariables: variables
    });
  }
}

// =====================================================
// AGENT REGISTRY
// =====================================================

export class AgentRegistry {
  private static instance: AgentRegistry;
  private agents: Map<string, BaseAgent> = new Map();

  private constructor() {}

  static getInstance(): AgentRegistry {
    if (!AgentRegistry.instance) {
      AgentRegistry.instance = new AgentRegistry();
    }
    return AgentRegistry.instance;
  }

  /**
   * Register an agent
   */
  registerAgent(agent: BaseAgent): void {
    this.agents.set(agent.name, agent);
    console.log(`🤖 Registered agent: ${agent.name}`);
  }

  /**
   * Get an agent by name
   */
  getAgent(name: string): BaseAgent | undefined {
    return this.agents.get(name);
  }

  /**
   * Get all agents
   */
  getAllAgents(): BaseAgent[] {
    return Array.from(this.agents.values());
  }

  /**
   * Get agents by department
   */
  getAgentsByDepartment(department: any): BaseAgent[] {
    return this.getAllAgents().filter(agent => agent.department === department);
  }

  /**
   * Execute an agent by name
   */
  async executeAgent(
    name: string,
    input: any,
    context: OrchestratorContext
  ): Promise<AgentIO> {
    const agent = this.getAgent(name);
    if (!agent) {
      throw new Error(`Agent '${name}' not found`);
    }

    return agent.execute(input, context);
  }
}

// =====================================================
// GLOBAL AGENT REGISTRY INSTANCE
// =====================================================

export const agentRegistry = AgentRegistry.getInstance();
