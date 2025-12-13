/**
 * V1 Adapter
 *
 * Wraps V1 agents with unified interface for orchestration
 */

import { AgentAdapter } from './base_adapter';
import { UnifiedRequest, UnifiedResponse, RoutingDecision, AgentCapabilities } from '../types';
import { v4 as uuidv4 } from 'uuid';

// Import V1 agents
import { ICPBuildAgent } from '../../agents/ICPBuildAgent';
import { CohortBuilderAgent } from '../../agents/CohortBuilderAgent';
import { CompetitorSurfaceAgent } from '../../agents/CompetitorSurfaceAgent';
import { TrendScraperAgent } from '../../agents/TrendScraperAgent';
import { StrategyProfileAgent } from '../../agents/StrategyProfileAgent';
import { CompanyEnrichAgent } from '../../agents/CompanyEnrichAgent';
import { JTBDMapperAgent } from '../../agents/JTBDMapperAgent';
import { MonetizationAgent } from '../../agents/MonetizationAgent';
import { MoveAssemblyAgent } from '../../agents/MoveAssemblyAgent';
import { PlanGeneratorAgent } from '../../agents/PlanGeneratorAgent';
import { PositioningParseAgent } from '../../agents/PositioningParseAgent';
import { TechStackSeedAgent } from '../../agents/TechStackSeedAgent';
import { ContentIdeaAgent } from '../../agents/ContentIdeaAgent';
import { MuseAgent } from '../../agents/MuseAgent';
import { BarrierEngineAgent } from '../../agents/BarrierEngineAgent';
import { CohortTagGeneratorAgent } from '../../agents/CohortTagGeneratorAgent';

// =====================================================
// V1 ADAPTER
// =====================================================

export class V1Adapter implements AgentAdapter {
  private agents: Map<string, any> = new Map();
  private agentClasses: Map<string, any> = new Map();

  constructor() {
    this.initializeAgents();
  }

  /**
   * Initialize V1 agent instances
   */
  private initializeAgents(): void {
    // Map agent names to their classes
    this.agentClasses.set('ICPBuildAgent', ICPBuildAgent);
    this.agentClasses.set('CohortBuilderAgent', CohortBuilderAgent);
    this.agentClasses.set('CompetitorSurfaceAgent', CompetitorSurfaceAgent);
    this.agentClasses.set('TrendScraperAgent', TrendScraperAgent);
    this.agentClasses.set('StrategyProfileAgent', StrategyProfileAgent);
    this.agentClasses.set('CompanyEnrichAgent', CompanyEnrichAgent);
    this.agentClasses.set('JTBDMapperAgent', JTBDMapperAgent);
    this.agentClasses.set('MonetizationAgent', MonetizationAgent);
    this.agentClasses.set('MoveAssemblyAgent', MoveAssemblyAgent);
    this.agentClasses.set('PlanGeneratorAgent', PlanGeneratorAgent);
    this.agentClasses.set('PositioningParseAgent', PositioningParseAgent);
    this.agentClasses.set('TechStackSeedAgent', TechStackSeedAgent);
    this.agentClasses.set('ContentIdeaAgent', ContentIdeaAgent);
    this.agentClasses.set('MuseAgent', MuseAgent);
    this.agentClasses.set('BarrierEngineAgent', BarrierEngineAgent);
    this.agentClasses.set('CohortTagGeneratorAgent', CohortTagGeneratorAgent);
  }

  /**
   * Execute unified request using V1 agents
   */
  async execute(request: UnifiedRequest, routing?: RoutingDecision): Promise<UnifiedResponse> {
    const executionId = uuidv4();
    const startTime = new Date();

    try {
      const agentsToExecute = routing?.agents || await this.selectAgents(request);

      if (agentsToExecute.length === 0) {
        throw new Error('No suitable V1 agents found for request');
      }

      // For now, execute the first agent (V1 doesn't have multi-agent orchestration)
      const primaryAgent = agentsToExecute[0];
      const agentInstance = await this.getAgentInstance(primaryAgent);

      if (!agentInstance) {
        throw new Error(`V1 agent not available: ${primaryAgent}`);
      }

      // Convert unified request to V1 agent format
      const v1Input = this.convertToV1Format(request, primaryAgent);

      // Execute V1 agent
      const result = await agentInstance.execute(v1Input);

      const endTime = new Date();

      return {
        executionId,
        status: 'completed',
        result: this.convertFromV1Format(result, primaryAgent),
        agentsInvolved: [primaryAgent],
        startTime,
        endTime,
        tokenUsage: result.metadata?.tokens || 0,
        costEstimate: result.metadata?.cost || 0
      };

    } catch (error: any) {
      return {
        executionId,
        status: 'failed',
        error: error.message,
        agentsInvolved: routing?.agents || [],
        startTime,
        endTime: new Date()
      };
    }
  }

  /**
   * Get list of available V1 agents
   */
  getAvailableAgents(): string[] {
    return Array.from(this.agentClasses.keys());
  }

  /**
   * Get detailed capabilities of V1 agents
   */
  async getCapabilities(): Promise<AgentCapabilities[]> {
    const capabilities: AgentCapabilities[] = [];

    for (const [agentName, agentClass] of this.agentClasses.entries()) {
      try {
        // Create temporary instance to get manifest
        const tempInstance = new agentClass();

        capabilities.push({
          name: agentName,
          system: 'v1',
          description: tempInstance.description || `${agentName} for business intelligence`,
          category: this.mapV1Category(agentName),
          capabilities: this.getV1Capabilities(agentName),
          inputs: ['goal', 'context'],
          outputs: ['insights', 'recommendations'],
          costEstimate: {
            minTokens: 500,
            maxTokens: 2000,
            estimatedCost: 0.05
          },
          metadata: {
            author: 'legacy',
            tags: ['v1', 'business-intelligence'],
            complexity: 'medium',
            version: '1.0.0'
          }
        });
      } catch (error) {
        console.warn(`Failed to get capabilities for V1 agent ${agentName}:`, error);
      }
    }

    return capabilities;
  }

  /**
   * Get health status of V1 adapter
   */
  async getHealth(): Promise<{
    status: 'healthy' | 'degraded' | 'unhealthy';
    agents: number;
    message?: string;
  }> {
    const totalAgents = this.agentClasses.size;
    let functionalAgents = 0;

    for (const [agentName] of this.agentClasses.entries()) {
      try {
        const instance = await this.getAgentInstance(agentName);
        if (instance) functionalAgents++;
      } catch (error) {
        // Agent not functional
      }
    }

    const healthRatio = functionalAgents / totalAgents;

    let status: 'healthy' | 'degraded' | 'unhealthy';
    if (healthRatio >= 0.8) {
      status = 'healthy';
    } else if (healthRatio >= 0.5) {
      status = 'degraded';
    } else {
      status = 'unhealthy';
    }

    return {
      status,
      agents: functionalAgents,
      message: `${functionalAgents}/${totalAgents} V1 agents functional`
    };
  }

  /**
   * Check if adapter can handle specific agents
   */
  canHandleAgents(agentNames: string[]): boolean {
    const availableAgents = this.getAvailableAgents();
    return agentNames.every(name => availableAgents.includes(name));
  }

  // =====================================================
  // PRIVATE METHODS
  // =====================================================

  /**
   * Get or create agent instance
   */
  private async getAgentInstance(agentName: string): Promise<any> {
    if (this.agents.has(agentName)) {
      return this.agents.get(agentName);
    }

    const agentClass = this.agentClasses.get(agentName);
    if (!agentClass) {
      return null;
    }

    try {
      const instance = new agentClass();
      this.agents.set(agentName, instance);
      return instance;
    } catch (error) {
      console.error(`Failed to create V1 agent ${agentName}:`, error);
      return null;
    }
  }

  /**
   * Select appropriate V1 agents based on request
   */
  private async selectAgents(request: UnifiedRequest): Promise<string[]> {
    const { goal, context } = request;
    const goal_lower = goal.toLowerCase();

    // Simple keyword-based agent selection
    if (goal_lower.includes('icp') || goal_lower.includes('customer profile')) {
      return ['ICPBuildAgent'];
    }

    if (goal_lower.includes('cohort') || goal_lower.includes('segment')) {
      return ['CohortBuilderAgent'];
    }

    if (goal_lower.includes('competitor') || goal_lower.includes('competition')) {
      return ['CompetitorSurfaceAgent'];
    }

    if (goal_lower.includes('trend') || goal_lower.includes('market research')) {
      return ['TrendScraperAgent'];
    }

    if (goal_lower.includes('strategy') || goal_lower.includes('planning')) {
      return ['StrategyProfileAgent'];
    }

    if (goal_lower.includes('company') || goal_lower.includes('enrich')) {
      return ['CompanyEnrichAgent'];
    }

    // Default fallback
    return ['StrategyProfileAgent'];
  }

  /**
   * Convert unified request to V1 agent format
   */
  private convertToV1Format(request: UnifiedRequest, agentName: string): any {
    return {
      goal: request.goal,
      context: request.context,
      userId: request.userId,
      input: {
        goal: request.goal,
        context: request.context,
        brandProfile: request.context?.brand,
        project: request.context?.campaign,
        constraints: request.context?.constraints || []
      }
    };
  }

  /**
   * Convert V1 agent result to unified format
   */
  private convertFromV1Format(result: any, agentName: string): any {
    return {
      agent: agentName,
      system: 'v1',
      output: result.outputs || result,
      metadata: result.metadata || {},
      insights: this.extractInsights(result, agentName)
    };
  }

  /**
   * Extract insights from V1 agent results
   */
  private extractInsights(result: any, agentName: string): any {
    const output = result.outputs || result;

    switch (agentName) {
      case 'ICPBuildAgent':
        return {
          customer_segments: output.customer_segments || [],
          pain_points: output.pain_points || [],
          buying_triggers: output.buying_triggers || []
        };

      case 'CompetitorSurfaceAgent':
        return {
          competitors: output.competitors || [],
          market_position: output.market_position || {},
          threats: output.threats || []
        };

      case 'CohortBuilderAgent':
        return {
          cohorts: output.cohorts || [],
          segments: output.segments || [],
          characteristics: output.characteristics || {}
        };

      default:
        return output;
    }
  }

  /**
   * Map V1 agent to category
   */
  private mapV1Category(agentName: string): 'brand' | 'content' | 'marketing' | 'technical' {
    const categoryMap: Record<string, 'brand' | 'content' | 'marketing' | 'technical'> = {
      'ICPBuildAgent': 'marketing',
      'CohortBuilderAgent': 'marketing',
      'CompetitorSurfaceAgent': 'marketing',
      'TrendScraperAgent': 'marketing',
      'StrategyProfileAgent': 'marketing',
      'CompanyEnrichAgent': 'marketing',
      'JTBDMapperAgent': 'marketing',
      'MonetizationAgent': 'marketing',
      'MoveAssemblyAgent': 'marketing',
      'PlanGeneratorAgent': 'marketing',
      'PositioningParseAgent': 'brand',
      'TechStackSeedAgent': 'technical',
      'ContentIdeaAgent': 'content',
      'MuseAgent': 'creative',
      'BarrierEngineAgent': 'marketing',
      'CohortTagGeneratorAgent': 'marketing'
    };

    return categoryMap[agentName] || 'marketing';
  }

  /**
   * Get capabilities for V1 agent
   */
  private getV1Capabilities(agentName: string): string[] {
    const capabilityMap: Record<string, string[]> = {
      'ICPBuildAgent': ['customer analysis', 'market segmentation', 'buyer profiling'],
      'CohortBuilderAgent': ['cohort identification', 'segmentation', 'targeting'],
      'CompetitorSurfaceAgent': ['competitive analysis', 'market mapping', 'threat assessment'],
      'TrendScraperAgent': ['market research', 'trend analysis', 'industry insights'],
      'StrategyProfileAgent': ['strategic planning', 'market assessment', 'opportunity identification']
    };

    return capabilityMap[agentName] || ['business intelligence', 'market analysis'];
  }
}


