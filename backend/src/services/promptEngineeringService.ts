/**
 * Prompt Engineering Service - Optimizes prompts for cost and performance
 *
 * Features:
 * - Prompt compression and trimming
 * - Template optimization
 * - Token counting and limits
 * - Context pruning
 * - Prompt versioning and A/B testing
 */

export interface PromptTemplate {
  id: string;
  name: string;
  version: string;
  template: string;
  variables: string[];
  estimatedTokens: number;
  category: string;
  optimized?: boolean;
}

export interface OptimizedPrompt {
  originalPrompt: string;
  optimizedPrompt: string;
  originalTokens: number;
  optimizedTokens: number;
  compressionRatio: number;
  optimizations: string[]; // List of optimizations applied
  metadata: {
    templateId?: string;
    category: string;
    estimatedCostSavings: number;
  };
}

export interface PromptStats {
  totalPromptsProcessed: number;
  totalTokensSaved: number;
  averageCompressionRatio: number;
  optimizationTechniques: Record<string, number>; // technique -> usage count
  costSavings: number;
}

class PromptEngineeringService {
  private readonly templates = new Map<string, PromptTemplate>();
  private readonly STATS_KEY = 'prompt_stats';

  private stats: PromptStats = {
    totalPromptsProcessed: 0,
    totalTokensSaved: 0,
    averageCompressionRatio: 1.0,
    optimizationTechniques: {},
    costSavings: 0
  };

  constructor() {
    this.initializeTemplates();
    this.loadStats();
  }

  /**
   * Optimize a prompt for cost and performance
   */
  async optimizePrompt(
    prompt: string,
    options: {
      maxTokens?: number;
      category?: string;
      aggressive?: boolean; // More aggressive optimization
      preserveStructure?: boolean; // Keep original structure
    } = {}
  ): Promise<OptimizedPrompt> {
    const { maxTokens = 4000, category = 'general', aggressive = false, preserveStructure = false } = options;

    const originalTokens = this.estimateTokens(prompt);
    let optimizedPrompt = prompt;
    const optimizations: string[] = [];

    // Apply optimization techniques in order
    optimizedPrompt = this.removeRedundancy(optimizedPrompt, optimizations);
    optimizedPrompt = this.compressWhitespace(optimizedPrompt, optimizations);
    optimizedPrompt = this.simplifyLanguage(optimizedPrompt, optimizations);

    if (aggressive) {
      optimizedPrompt = this.removeOptionalContext(optimizedPrompt, optimizations);
      optimizedPrompt = this.shortenExamples(optimizedPrompt, optimizations);
    }

    if (!preserveStructure) {
      optimizedPrompt = this.restructureForEfficiency(optimizedPrompt, optimizations);
    }

    // Ensure we don't exceed token limits
    optimizedPrompt = this.enforceTokenLimit(optimizedPrompt, maxTokens, optimizations);

    const optimizedTokens = this.estimateTokens(optimizedPrompt);
    const compressionRatio = originalTokens > 0 ? optimizedTokens / originalTokens : 1;

    // Calculate estimated cost savings
    const tokenSavings = Math.max(0, originalTokens - optimizedTokens);
    const estimatedCostSavings = tokenSavings * 0.000015; // Rough estimate per token

    const result: OptimizedPrompt = {
      originalPrompt: prompt,
      optimizedPrompt,
      originalTokens,
      optimizedTokens,
      compressionRatio,
      optimizations,
      metadata: {
        category,
        estimatedCostSavings
      }
    };

    // Update stats
    await this.updateStats(result);

    return result;
  }

  /**
   * Optimize a template for repeated use
   */
  async optimizeTemplate(templateId: string): Promise<PromptTemplate | null> {
    const template = this.templates.get(templateId);
    if (!template) return null;

    const optimized = await this.optimizePrompt(template.template, {
      category: template.category,
      aggressive: true,
      preserveStructure: true
    });

    const optimizedTemplate: PromptTemplate = {
      ...template,
      template: optimized.optimizedPrompt,
      estimatedTokens: optimized.optimizedTokens,
      optimized: true,
      version: this.incrementVersion(template.version)
    };

    this.templates.set(templateId, optimizedTemplate);
    return optimizedTemplate;
  }

  /**
   * Register a prompt template
   */
  registerTemplate(template: PromptTemplate): void {
    this.templates.set(template.id, template);
  }

  /**
   * Get template by ID
   */
  getTemplate(templateId: string): PromptTemplate | null {
    return this.templates.get(templateId) || null;
  }

  /**
   * Fill template with variables
   */
  fillTemplate(templateId: string, variables: Record<string, any>): string | null {
    const template = this.templates.get(templateId);
    if (!template) return null;

    let filled = template.template;

    // Replace variables
    for (const [key, value] of Object.entries(variables)) {
      const placeholder = `{{${key}}}`;
      filled = filled.replace(new RegExp(placeholder, 'g'), String(value));
    }

    return filled;
  }

  /**
   * Optimize and fill template in one step
   */
  async optimizeAndFillTemplate(
    templateId: string,
    variables: Record<string, any>,
    options: Parameters<typeof this.optimizePrompt>[1] = {}
  ): Promise<OptimizedPrompt | null> {
    const filled = this.fillTemplate(templateId, variables);
    if (!filled) return null;

    const template = this.templates.get(templateId);
    return this.optimizePrompt(filled, {
      ...options,
      category: template?.category || options.category
    });
  }

  /**
   * Get prompt optimization statistics
   */
  async getStats(): Promise<PromptStats> {
    await this.loadStats();
    return { ...this.stats };
  }

  /**
   * Estimate tokens for a prompt (rough approximation)
   */
  estimateTokens(text: string): number {
    // Rough approximation: 1 token ≈ 4 characters for English text
    return Math.ceil(text.length / 4);
  }

  // ===== OPTIMIZATION TECHNIQUES =====

  private removeRedundancy(prompt: string, optimizations: string[]): string {
    let optimized = prompt;

    // Remove repeated phrases
    const repeatedPatterns = [
      /(\b\w+\b)(\s+\1)+/g, // Repeated words
      /(.{20,}?)\s*\1/g      // Repeated phrases
    ];

    for (const pattern of repeatedPatterns) {
      const matches = prompt.match(pattern);
      if (matches && matches.length > 1) {
        optimized = optimized.replace(pattern, '$1');
        optimizations.push('removed_redundancy');
      }
    }

    return optimized;
  }

  private compressWhitespace(prompt: string, optimizations: string[]): string {
    // Normalize whitespace
    let optimized = prompt
      .replace(/\n\s*\n/g, '\n')  // Multiple newlines to single
      .replace(/\s+/g, ' ')       // Multiple spaces to single
      .trim();

    if (optimized !== prompt) {
      optimizations.push('compressed_whitespace');
    }

    return optimized;
  }

  private simplifyLanguage(prompt: string, optimizations: string[]): string {
    // Simple language simplifications
    const simplifications: Record<string, string> = {
      'utilize': 'use',
      'implement': 'do',
      'facilitate': 'help',
      'leverage': 'use',
      'optimize': 'improve',
      'maximize': 'increase',
      'minimize': 'reduce',
      'comprehensive': 'complete',
      'significant': 'important',
      'substantial': 'large',
      'approximately': 'about',
      'specifically': 'clearly'
    };

    let optimized = prompt;
    let simplified = false;

    for (const [complex, simple] of Object.entries(simplifications)) {
      const regex = new RegExp(`\\b${complex}\\b`, 'gi');
      optimized = optimized.replace(regex, simple);
      if (optimized !== prompt) simplified = true;
    }

    if (simplified) {
      optimizations.push('simplified_language');
    }

    return optimized;
  }

  private removeOptionalContext(prompt: string, optimizations: string[]): string {
    // Remove less critical sections (marked with [optional] or similar)
    let optimized = prompt
      .replace(/\[optional[^\]]*\]/gi, '')
      .replace(/\(optional[^\)]*\)/gi, '');

    // Remove verbose introductions
    optimized = optimized.replace(/^.*?[.!?]\s*(?=You are|Your task|Generate|Create)/s, '');

    if (optimized !== prompt) {
      optimizations.push('removed_optional_context');
    }

    return optimized;
  }

  private shortenExamples(prompt: string, optimizations: string[]): string {
    // Shorten example sections while preserving structure
    const examplePattern = /(?:Example[s]?:?\s*)(.*?)(?=\n\n|\n(?:\d+\.|[-*+]))/gis;
    let optimized = prompt;
    let shortened = false;

    optimized = optimized.replace(examplePattern, (match, examples) => {
      // Keep only the first example or shorten all
      const exampleLines = examples.split('\n').filter(line => line.trim());
      if (exampleLines.length > 3) {
        const shortenedExamples = exampleLines.slice(0, 2).join('\n') + '\n...';
        shortened = true;
        return `Examples: ${shortenedExamples}`;
      }
      return match;
    });

    if (shortened) {
      optimizations.push('shortened_examples');
    }

    return optimized;
  }

  private restructureForEfficiency(prompt: string, optimizations: string[]): string {
    // Restructure for better LLM comprehension with fewer tokens
    let optimized = prompt;

    // Move key instructions to the beginning
    const instructionPattern = /(?:Your task|Generate|Create|You must|The plan must)(.*?)(?=\n\n|\n[A-Z]|$)/is;
    const instructionMatch = prompt.match(instructionPattern);

    if (instructionMatch) {
      const instruction = instructionMatch[0];
      optimized = optimized.replace(instructionPattern, '');
      optimized = `${instruction.trim()}\n\n${optimized.trim()}`;
      optimizations.push('restructured_instructions');
    }

    return optimized;
  }

  private enforceTokenLimit(prompt: string, maxTokens: number, optimizations: string[]): string {
    const currentTokens = this.estimateTokens(prompt);

    if (currentTokens <= maxTokens) {
      return prompt;
    }

    // Truncate from the end, keeping the beginning (most important)
    const charsToKeep = maxTokens * 4; // Rough approximation
    let truncated = prompt.slice(0, charsToKeep);

    // Try to end at a sentence boundary
    const lastSentenceEnd = Math.max(
      truncated.lastIndexOf('.'),
      truncated.lastIndexOf('!'),
      truncated.lastIndexOf('?'),
      truncated.lastIndexOf('\n\n')
    );

    if (lastSentenceEnd > charsToKeep * 0.8) {
      truncated = truncated.slice(0, lastSentenceEnd + 1);
    }

    optimizations.push('enforced_token_limit');
    return truncated;
  }

  private incrementVersion(version: string): string {
    const parts = version.split('.');
    const patch = parseInt(parts[parts.length - 1] || '0') + 1;
    parts[parts.length - 1] = patch.toString();
    return parts.join('.');
  }

  private async updateStats(result: OptimizedPrompt): Promise<void> {
    this.stats.totalPromptsProcessed++;
    this.stats.totalTokensSaved += Math.max(0, result.originalTokens - result.optimizedTokens);
    this.stats.averageCompressionRatio =
      (this.stats.averageCompressionRatio * (this.stats.totalPromptsProcessed - 1) + result.compressionRatio)
      / this.stats.totalPromptsProcessed;
    this.stats.costSavings += result.metadata.estimatedCostSavings;

    // Track optimization techniques
    for (const technique of result.optimizations) {
      this.stats.optimizationTechniques[technique] =
        (this.stats.optimizationTechniques[technique] || 0) + 1;
    }

    // Persist stats (simplified - would use Redis in production)
    // await redisMemory.store(this.STATS_KEY, JSON.stringify(this.stats), 86400);
  }

  private async loadStats(): Promise<void> {
    // Load from Redis if available
    // const saved = await redisMemory.get(this.STATS_KEY);
    // if (saved) this.stats = { ...this.stats, ...JSON.parse(saved) };
  }

  private initializeTemplates(): void {
    // Initialize with common templates
    const defaultTemplates: PromptTemplate[] = [
      {
        id: 'plan_generator',
        name: 'Plan Generator',
        version: '1.0.0',
        template: `Generate a detailed {{duration}}-week execution plan for {{company_name}}.

Goals: {{goals}}
Team: {{team_size}} people
Budget: {{budget}}

Create specific daily activities, deliverables, and success metrics.`,
        variables: ['duration', 'company_name', 'goals', 'team_size', 'budget'],
        estimatedTokens: 150,
        category: 'planning'
      },
      {
        id: 'company_enrich',
        name: 'Company Enrichment',
        version: '1.0.0',
        template: `Enrich company data for {{company_name}}.

Current data: {{current_data}}

Find: industry, size, revenue, website, social media, recent news.`,
        variables: ['company_name', 'current_data'],
        estimatedTokens: 80,
        category: 'enrichment'
      },
      {
        id: 'content_idea',
        name: 'Content Idea Generation',
        version: '1.0.0',
        template: `Generate {{count}} content ideas for {{topic}} on {{platform}}.

Target audience: {{audience}}
Goals: {{goals}}`,
        variables: ['count', 'topic', 'platform', 'audience', 'goals'],
        estimatedTokens: 60,
        category: 'content'
      }
    ];

    for (const template of defaultTemplates) {
      this.registerTemplate(template);
    }
  }
}

// Export singleton instance
export const promptEngineering = new PromptEngineeringService();

// Export types
export type { PromptTemplate, OptimizedPrompt, PromptStats };


