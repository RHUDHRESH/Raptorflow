/**
 * Unified Orchestrator V3
 *
 * Single entry point for V1 and V2 agent orchestration.
 * Routes requests intelligently between legacy V1 and advanced V2 systems.
 */

import { z } from 'zod';
import { v4 as uuidv4 } from 'uuid';
import { AgentAdapter, adapterRegistry } from './adapters/base_adapter';
import { V1Adapter } from './adapters/v1_adapter';
import { V2Adapter } from './adapters/v2_adapter';
import { ContextBridge } from './context_bridge';
import { UnifiedRequest, UnifiedResponse, ExecutionStatus, AgentCapabilities } from './types';

// =====================================================
// UNIFIED ORCHESTRATOR V3
// =====================================================

export class UnifiedOrchestratorV3 {
  private v1Adapter: V1Adapter;
  private v2Adapter: V2Adapter;
  private contextBridge: ContextBridge;
  private activeExecutions: Map<string, ExecutionStatus> = new Map();

  constructor() {
    this.v1Adapter = new V1Adapter();
    this.v2Adapter = new V2Adapter();
    this.contextBridge = new ContextBridge();

    // Register adapters in the registry
    adapterRegistry.registerAdapter('v1', this.v1Adapter);
    adapterRegistry.registerAdapter('v2', this.v2Adapter);
  }

  /**
   * Execute a unified request, routing to appropriate system
   */
  async execute(request: UnifiedRequest): Promise<UnifiedResponse> {
    const executionId = uuidv4();
    const startTime = new Date();

    // Initialize execution status
    const status: ExecutionStatus = {
      executionId,
      status: 'queued',
      startTime,
      userId: request.userId,
      goal: request.goal,
      agentsInvolved: [],
      progress: 0
    };

    this.activeExecutions.set(executionId, status);

    try {
      // Classify request and route to appropriate system
      const routingDecision = await this.classifyAndRoute(request);

      status.status = 'processing';
      status.agentsInvolved = routingDecision.agents;
      status.systemUsed = routingDecision.system;

      // Execute based on routing decision
      let result: UnifiedResponse;

      if (routingDecision.system === 'v1') {
        result = await this.v1Adapter.execute(request, routingDecision);
      } else if (routingDecision.system === 'v2') {
        result = await this.v2Adapter.execute(request, routingDecision);
      } else if (routingDecision.system === 'hybrid') {
        result = await this.executeHybrid(request, routingDecision);
      } else {
        throw new Error(`Unknown routing system: ${routingDecision.system}`);
      }

      // Update final status
      status.status = 'completed';
      status.endTime = new Date();
      status.progress = 100;
      status.result = result;

      return {
        ...result,
        executionId,
        systemUsed: routingDecision.system,
        routingReason: routingDecision.reason
      };

    } catch (error: any) {
      status.status = 'failed';
      status.endTime = new Date();
      status.error = error.message;

      throw error;
    }
  }

  /**
   * Classify request and determine routing strategy
   */
  private async classifyAndRoute(request: UnifiedRequest): Promise<RoutingDecision> {
    const { goal, context, agentSelection, selectedAgents } = request;

    // Manual agent selection overrides auto-routing
    if (agentSelection === 'manual' && selectedAgents) {
      return this.routeManualSelection(selectedAgents);
    }

    // Auto-routing based on goal analysis
    return this.routeAutoSelection(goal, context);
  }

  /**
   * Route based on manual agent selection
   */
  private routeManualSelection(selectedAgents: string[]): RoutingDecision {
    const v1Agents = this.v1Adapter.getAvailableAgents();
    const v2Agents = this.v2Adapter.getAvailableAgents();

    const requestedV1Agents = selectedAgents.filter(agent => v1Agents.includes(agent));
    const requestedV2Agents = selectedAgents.filter(agent => v2Agents.includes(agent));

    if (requestedV1Agents.length > 0 && requestedV2Agents.length > 0) {
      return {
        system: 'hybrid',
        agents: selectedAgents,
        reason: 'Manual selection spans both V1 and V2 systems',
        v1Agents: requestedV1Agents,
        v2Agents: requestedV2Agents
      };
    } else if (requestedV1Agents.length > 0) {
      return {
        system: 'v1',
        agents: requestedV1Agents,
        reason: 'Manual selection of V1 agents'
      };
    } else if (requestedV2Agents.length > 0) {
      return {
        system: 'v2',
        agents: requestedV2Agents,
        reason: 'Manual selection of V2 agents'
      };
    } else {
      throw new Error(`No valid agents found in selection: ${selectedAgents.join(', ')}`);
    }
  }

  /**
   * Auto-route based on goal and context analysis
   */
  private async routeAutoSelection(goal: string, context: any): Promise<RoutingDecision> {
    // Analyze goal to determine complexity and requirements
    const goalAnalysis = this.analyzeGoal(goal);
    const contextAnalysis = this.analyzeContext(context);

    // Decision matrix
    if (goalAnalysis.complexity === 'high' || contextAnalysis.requiresOrchestration) {
      // Use V2 for complex, multi-step workflows
      return {
        system: 'v2',
        agents: await this.selectV2Agents(goalAnalysis, contextAnalysis),
        reason: 'Complex goal requiring multi-agent orchestration'
      };
    } else if (goalAnalysis.type === 'business_intelligence') {
      // Use V1 for business intelligence tasks
      return {
        system: 'v1',
        agents: await this.selectV1Agents(goalAnalysis, contextAnalysis),
        reason: 'Business intelligence task suited for V1 agents'
      };
    } else if (goalAnalysis.type === 'marketing_execution') {
      // Use V2 for marketing execution
      return {
        system: 'v2',
        agents: await this.selectV2Agents(goalAnalysis, contextAnalysis),
        reason: 'Marketing execution requiring V2 orchestration'
      };
    } else {
      // Default to V2 for advanced capabilities
      return {
        system: 'v2',
        agents: ['orchestrator'], // Let V2 orchestrator decide
        reason: 'Defaulting to V2 advanced orchestration'
      };
    }
  }

  /**
   * Execute hybrid workflow (V1 + V2 coordination)
   */
  private async executeHybrid(request: UnifiedRequest, routing: RoutingDecision): Promise<UnifiedResponse> {
    const { v1Agents = [], v2Agents = [] } = routing;

    // Execute V1 agents first to gather business intelligence
    if (v1Agents.length > 0) {
      const v1Request = { ...request, agentSelection: 'manual' as const, selectedAgents: v1Agents };
      const v1Result = await this.v1Adapter.execute(v1Request, routing);

      // Share V1 results with V2 context
      await this.contextBridge.shareContext('v1', {
        executionId: v1Result.executionId,
        results: v1Result.result,
        agents: v1Agents
      });
    }

    // Execute V2 agents with enhanced context
    if (v2Agents.length > 0) {
      const v2Request = { ...request, agentSelection: 'manual' as const, selectedAgents: v2Agents };
      const sharedContext = await this.contextBridge.getSharedContext('v2');

      // Enhance V2 request with V1 insights
      v2Request.context = {
        ...v2Request.context,
        v1Insights: sharedContext
      };

      return await this.v2Adapter.execute(v2Request, routing);
    }

    throw new Error('No agents specified for hybrid execution');
  }

  /**
   * Analyze goal to determine requirements
   */
  private analyzeGoal(goal: string): GoalAnalysis {
    const lowerGoal = goal.toLowerCase();

    // Determine goal type
    let type: 'business_intelligence' | 'marketing_execution' | 'mixed' = 'mixed';
    if (lowerGoal.includes('research') || lowerGoal.includes('analysis') || lowerGoal.includes('market')) {
      type = 'business_intelligence';
    } else if (lowerGoal.includes('campaign') || lowerGoal.includes('marketing') || lowerGoal.includes('advertising')) {
      type = 'marketing_execution';
    }

    // Determine complexity
    const complexityKeywords = ['comprehensive', 'complete', 'full', 'end-to-end', 'orchestrate'];
    const complexity = complexityKeywords.some(keyword => lowerGoal.includes(keyword)) ? 'high' : 'medium';

    return { type, complexity, keywords: this.extractKeywords(goal) };
  }

  /**
   * Analyze context to determine requirements
   */
  private analyzeContext(context: any): ContextAnalysis {
    const hasCampaign = !!context?.campaign;
    const hasICP = !!context?.icp;
    const hasBrand = !!context?.brand;
    const hasConstraints = !!(context?.constraints?.length > 0);

    return {
      hasCampaign,
      hasICP,
      hasBrand,
      hasConstraints,
      requiresOrchestration: hasCampaign || (hasICP && hasBrand) || hasConstraints
    };
  }

  /**
   * Select appropriate V1 agents
   */
  private async selectV1Agents(goal: GoalAnalysis, context: ContextAnalysis): Promise<string[]> {
    const agents: string[] = [];

    if (goal.keywords.includes('icp') || goal.keywords.includes('customer')) {
      agents.push('ICPBuildAgent');
    }

    if (goal.keywords.includes('market') || goal.keywords.includes('research')) {
      agents.push('TrendScraperAgent', 'CompetitorSurfaceAgent');
    }

    if (goal.keywords.includes('cohort') || goal.keywords.includes('segment')) {
      agents.push('CohortBuilderAgent');
    }

    return agents.length > 0 ? agents : ['StrategyProfileAgent']; // fallback
  }

  /**
   * Select appropriate V2 agents
   */
  private async selectV2Agents(goal: GoalAnalysis, context: ContextAnalysis): Promise<string[]> {
    const agents: string[] = [];

    if (goal.type === 'marketing_execution') {
      agents.push('campaign_architect_agent', 'creative_director_agent');
    }

    if (context.hasBrand) {
      agents.push('brand_memory_agent');
    }

    return agents.length > 0 ? agents : ['orchestrator']; // Let orchestrator decide
  }

  /**
   * Extract keywords from goal
   */
  private extractKeywords(text: string): string[] {
    const keywords = text.toLowerCase()
      .split(/\s+/)
      .filter(word => word.length > 3)
      .filter(word => !['that', 'with', 'from', 'this', 'will', 'have', 'been', 'were'].includes(word));

    return [...new Set(keywords)].slice(0, 10); // Limit to 10 unique keywords
  }

  /**
   * Get execution status
   */
  getExecutionStatus(executionId: string): ExecutionStatus | null {
    return this.activeExecutions.get(executionId) || null;
  }

  /**
   * List all available agents across systems
   */
  async getAllAvailableAgents(): Promise<AgentCapabilities[]> {
    const v1Agents = await this.v1Adapter.getCapabilities();
    const v2Agents = await this.v2Adapter.getCapabilities();

    return [...v1Agents, ...v2Agents];
  }

  /**
   * Get system health
   */
  async getHealth(): Promise<{
    v1: { status: 'healthy' | 'degraded' | 'unhealthy'; agents: number };
    v2: { status: 'healthy' | 'degraded' | 'unhealthy'; agents: number };
    overall: 'healthy' | 'degraded' | 'unhealthy';
  }> {
    const v1Health = await this.v1Adapter.getHealth();
    const v2Health = await this.v2Adapter.getHealth();

    const overall = (v1Health.status === 'healthy' && v2Health.status === 'healthy') ? 'healthy' :
                   (v1Health.status === 'unhealthy' || v2Health.status === 'unhealthy') ? 'unhealthy' : 'degraded';

    return {
      v1: v1Health,
      v2: v2Health,
      overall
    };
  }
}

// =====================================================
// TYPES AND INTERFACES
// =====================================================

export interface RoutingDecision {
  system: 'v1' | 'v2' | 'hybrid';
  agents: string[];
  reason: string;
  v1Agents?: string[];
  v2Agents?: string[];
}

export interface GoalAnalysis {
  type: 'business_intelligence' | 'marketing_execution' | 'mixed';
  complexity: 'low' | 'medium' | 'high';
  keywords: string[];
}

export interface ContextAnalysis {
  hasCampaign: boolean;
  hasICP: boolean;
  hasBrand: boolean;
  hasConstraints: boolean;
  requiresOrchestration: boolean;
}

export interface ExecutionStatus {
  executionId: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  startTime: Date;
  endTime?: Date;
  userId: string;
  goal: string;
  agentsInvolved: string[];
  systemUsed?: 'v1' | 'v2' | 'hybrid';
  progress: number;
  result?: any;
  error?: string;
}

// Singleton instance
export const unifiedOrchestrator = new UnifiedOrchestratorV3();
