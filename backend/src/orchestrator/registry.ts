/**
 * Orchestrator Routing Registry
 *
 * Manages agent registration, routing logic, job queuing, and context snapshotting.
 */

import { agentRegistry, type AgentName } from '../v2/agents';
import { redisMemory } from '../services/redisMemory';
import type { AgentManifest, AgentInput } from '../v2/agents/base';

export interface RoutingRule {
  condition: (input: AgentInput) => boolean;
  priority: number;
  agentName: AgentName;
  reason: string;
}

export interface JobQueueItem {
  jobId: string;
  agentName: AgentName;
  input: AgentInput;
  priority: number;
  queuedAt: number;
  contextSnapshot: Record<string, any>;
}

export interface RoutingResult {
  agentName: AgentName;
  confidence: number;
  reason: string;
  estimatedCost: number;
  estimatedDuration: number;
}

class OrchestratorRegistry {
  private routingRules: RoutingRule[] = [];
  private jobQueue: JobQueueItem[] = [];
  private maxConcurrentJobs = 10;
  private activeJobs = new Set<string>();

  constructor() {
    this.initializeRoutingRules();
  }

  /**
   * Register a new agent in the orchestrator
   */
  registerAgent(agentName: AgentName, manifest: AgentManifest): void {
    if (!(agentName in agentRegistry)) {
      throw new Error(`Agent ${agentName} not found in registry`);
    }

    console.log(`✅ Registered agent: ${agentName} (${manifest.category})`);
  }

  /**
   * Get agent manifest by name
   */
  getAgentManifest(agentName: AgentName): AgentManifest | null {
    const agent = agentRegistry[agentName];
    return agent ? agent.manifest : null;
  }

  /**
   * Route a request to the appropriate agent
   */
  async routeRequest(input: AgentInput): Promise<RoutingResult | null> {
    // Check explicit agent requests
    if (input.inputOverrides?.agentName) {
      const agentName = input.inputOverrides.agentName as AgentName;
      if (agentName in agentRegistry) {
        const manifest = this.getAgentManifest(agentName);
        return {
          agentName,
          confidence: 1.0,
          reason: 'Explicitly requested agent',
          estimatedCost: manifest?.costEstimate.estimatedCost || 0,
          estimatedDuration: this.estimateDuration(manifest?.metadata.complexity || 'medium'),
        };
      }
    }

    // Apply routing rules
    for (const rule of this.routingRules.sort((a, b) => b.priority - a.priority)) {
      if (rule.condition(input)) {
        const manifest = this.getAgentManifest(rule.agentName);
        return {
          agentName: rule.agentName,
          confidence: 0.9,
          reason: rule.reason,
          estimatedCost: manifest?.costEstimate.estimatedCost || 0,
          estimatedDuration: this.estimateDuration(manifest?.metadata.complexity || 'medium'),
        };
      }
    }

    // Fallback to intent-based routing
    return this.routeByIntent(input);
  }

  /**
   * Queue a job for processing
   */
  async queueJob(agentName: AgentName, input: AgentInput): Promise<string> {
    const jobId = `job_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const contextSnapshot = await this.createContextSnapshot(input);

    const queueItem: JobQueueItem = {
      jobId,
      agentName,
      input,
      priority: input.inputOverrides?.priority || 0,
      queuedAt: Date.now(),
      contextSnapshot,
    };

    // Add to in-memory queue
    this.jobQueue.push(queueItem);
    this.jobQueue.sort((a, b) => b.priority - a.priority); // Higher priority first

    // Store job context in Redis
    await redisMemory.storeJobContext(jobId, {
      jobId,
      status: 'queued',
      progress: 0,
      contextSnapshot,
      lastUpdate: Date.now(),
    });

    console.log(`📋 Job ${jobId} queued for agent ${agentName}`);
    return jobId;
  }

  /**
   * Get next job from queue
   */
  async getNextJob(): Promise<JobQueueItem | null> {
    // Check concurrency limits
    if (this.activeJobs.size >= this.maxConcurrentJobs) {
      return null;
    }

    // Find next available job
    const nextJob = this.jobQueue.find(job => !this.activeJobs.has(job.jobId));

    if (nextJob) {
      this.activeJobs.add(nextJob.jobId);
      this.jobQueue = this.jobQueue.filter(job => job.jobId !== nextJob.jobId);
    }

    return nextJob || null;
  }

  /**
   * Mark job as completed
   */
  completeJob(jobId: string): void {
    this.activeJobs.delete(jobId);
  }

  /**
   * Mark job as failed
   */
  failJob(jobId: string): void {
    this.activeJobs.delete(jobId);
  }

  /**
   * Get queue statistics
   */
  getQueueStats(): {
    queued: number;
    active: number;
    totalCapacity: number;
    availableCapacity: number;
  } {
    return {
      queued: this.jobQueue.length,
      active: this.activeJobs.size,
      totalCapacity: this.maxConcurrentJobs,
      availableCapacity: this.maxConcurrentJobs - this.activeJobs.size,
    };
  }

  /**
   * Create context snapshot for a job
   */
  private async createContextSnapshot(input: AgentInput): Promise<Record<string, any>> {
    const snapshot: Record<string, any> = {
      brandProfileId: input.brandProfileId,
      inputOverrides: input.inputOverrides,
      contextSnapshot: input.contextSnapshot,
      jobId: input.jobId,
      userId: input.userId,
      createdAt: new Date().toISOString(),
    };

    // Add brand profile data if available
    if (input.brandProfileId) {
      const brandProfile = await redisMemory.getCachedBrandProfile(input.brandProfileId);
      if (brandProfile) {
        snapshot.brandProfile = brandProfile;
      }
    }

    // Add conversation history if this is part of a conversation
    if (input.jobId) {
      const conversation = await redisMemory.getConversation(input.jobId);
      if (conversation) {
        snapshot.conversationHistory = conversation.messages;
      }
    }

    return snapshot;
  }

  /**
   * Route by analyzing input intent
   */
  private routeByIntent(input: AgentInput): RoutingResult | null {
    const context = input.contextSnapshot || {};
    const overrides = input.inputOverrides || {};

    // Analyze keywords and context to determine intent
    const text = [
      overrides.description,
      overrides.content,
      overrides.purpose,
      context.goal,
      context.type,
    ].filter(Boolean).join(' ').toLowerCase();

    // Brand-related intents
    if (text.includes('brand') && text.includes('story')) {
      return {
        agentName: 'BrandScript',
        confidence: 0.8,
        reason: 'Detected brand storytelling intent',
        estimatedCost: 0.015,
        estimatedDuration: 120000,
      };
    }

    if (text.includes('tagline') || text.includes('slogan')) {
      return {
        agentName: 'Tagline',
        confidence: 0.8,
        reason: 'Detected tagline creation intent',
        estimatedCost: 0.008,
        estimatedDuration: 60000,
      };
    }

    // Product-related intents
    if (text.includes('product') && text.includes('description')) {
      return {
        agentName: 'ProductDescription',
        confidence: 0.8,
        reason: 'Detected product description intent',
        estimatedCost: 0.010,
        estimatedDuration: 90000,
      };
    }

    // Content-related intents
    if (text.includes('one-liner') || text.includes('short message')) {
      return {
        agentName: 'OneLiner',
        confidence: 0.8,
        reason: 'Detected one-liner creation intent',
        estimatedCost: 0.005,
        estimatedDuration: 45000,
      };
    }

    if (text.includes('social media') || text.includes('social')) {
      return {
        agentName: 'SocialMediaIdeas',
        confidence: 0.8,
        reason: 'Detected social media content intent',
        estimatedCost: 0.012,
        estimatedDuration: 100000,
      };
    }

    // Marketing-related intents
    if (text.includes('email') && text.includes('sales')) {
      return {
        agentName: 'SalesEmail',
        confidence: 0.8,
        reason: 'Detected sales email intent',
        estimatedCost: 0.011,
        estimatedDuration: 95000,
      };
    }

    // Technical intents
    if (text.includes('website') && text.includes('wireframe')) {
      return {
        agentName: 'WebsiteWireframe',
        confidence: 0.8,
        reason: 'Detected website wireframe intent',
        estimatedCost: 0.014,
        estimatedDuration: 130000,
      };
    }

    return null;
  }

  /**
   * Initialize routing rules
   */
  private initializeRoutingRules(): void {
    this.routingRules = [
      // High priority explicit requests
      {
        condition: (input) => Boolean(input.inputOverrides?.priority && input.inputOverrides.priority >= 8),
        priority: 100,
        agentName: 'BrandScript', // Will be overridden by explicit agent
        reason: 'High priority job',
      },

      // Brand-related rules
      {
        condition: (input) => {
          const text = JSON.stringify(input.inputOverrides).toLowerCase();
          return text.includes('brand script') || text.includes('brand story');
        },
        priority: 90,
        agentName: 'BrandScript',
        reason: 'Explicit brand script request',
      },

      {
        condition: (input) => {
          const text = JSON.stringify(input.inputOverrides).toLowerCase();
          return text.includes('tagline') || text.includes('slogan');
        },
        priority: 85,
        agentName: 'Tagline',
        reason: 'Explicit tagline request',
      },

      // Content creation rules
      {
        condition: (input) => {
          const text = JSON.stringify(input.inputOverrides).toLowerCase();
          return text.includes('social media') || text.includes('social content');
        },
        priority: 80,
        agentName: 'SocialMediaIdeas',
        reason: 'Social media content request',
      },

      // Marketing rules
      {
        condition: (input) => {
          const text = JSON.stringify(input.inputOverrides).toLowerCase();
          return text.includes('sales email') || text.includes('email campaign');
        },
        priority: 75,
        agentName: 'SalesEmail',
        reason: 'Sales email request',
      },

      // Technical rules
      {
        condition: (input) => {
          const text = JSON.stringify(input.inputOverrides).toLowerCase();
          return text.includes('wireframe') || text.includes('website design');
        },
        priority: 70,
        agentName: 'WebsiteWireframe',
        reason: 'Website wireframe request',
      },
    ];
  }

  /**
   * Estimate job duration based on complexity
   */
  private estimateDuration(complexity: string): number {
    const durationMap = {
      simple: 30000,    // 30 seconds
      medium: 60000,    // 1 minute
      complex: 120000,  // 2 minutes
    };

    return durationMap[complexity as keyof typeof durationMap] || 60000;
  }

  /**
   * Get all registered agents
   */
  getRegisteredAgents(): Array<{ name: AgentName; manifest: AgentManifest }> {
    return Object.entries(agentRegistry).map(([name, agent]) => ({
      name: name as AgentName,
      manifest: agent.manifest,
    }));
  }

  /**
   * Get agent statistics
   */
  getAgentStats(): {
    totalAgents: number;
    agentsByCategory: Record<string, number>;
    queueStats: any;
  } {
    const agents = this.getRegisteredAgents();
    const agentsByCategory: Record<string, number> = {};

    agents.forEach(agent => {
      agentsByCategory[agent.manifest.category] =
        (agentsByCategory[agent.manifest.category] || 0) + 1;
    });

    return {
      totalAgents: agents.length,
      agentsByCategory,
      queueStats: this.getQueueStats(),
    };
  }
}

// Export singleton instance
export const orchestratorRegistry = new OrchestratorRegistry();

// Initialize all agents
Object.keys(agentRegistry).forEach(agentName => {
  orchestratorRegistry.registerAgent(agentName as AgentName, agentRegistry[agentName as AgentName].manifest);
});

// Export types
export type { RoutingRule, JobQueueItem, RoutingResult };

