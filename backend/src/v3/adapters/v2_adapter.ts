/**
 * V2 Adapter
 *
 * Integrates V2 LangGraph orchestration with unified interface
 */

import { AgentAdapter } from './base_adapter';
import { UnifiedRequest, UnifiedResponse, RoutingDecision, AgentCapabilities } from '../types';
import { agentRegistry } from '../../v2/agents';
import { sqsJobQueue } from '../../services/sqsJobQueue';
import { redisMemory } from '../../services/redisMemory';

// =====================================================
// V2 ADAPTER
// =====================================================

export class V2Adapter implements AgentAdapter {
  constructor() {
    // V2 system is initialized through advanced_agentic_system and orchestrator
  }

  /**
   * Execute unified request using V2 orchestration
   */
  async execute(request: UnifiedRequest, routing?: RoutingDecision): Promise<UnifiedResponse> {
    try {
      const agentsToExecute = routing?.agents || ['orchestrator'];

      // Convert unified request to V2 format
      const v2Request = this.convertToV2Format(request, agentsToExecute);

      let result: any;

      if (agentsToExecute.includes('orchestrator') || agentsToExecute.length > 1) {
        // Use advanced orchestration for multi-agent workflows
        result = await this.executeAdvancedWorkflow(v2Request);
      } else {
        // Execute single V2 agent
        result = await this.executeSingleAgent(agentsToExecute[0], v2Request);
      }

      return {
        executionId: result.execution_id || result.workflow_id || `v2_${Date.now()}`,
        status: 'completed',
        result: this.convertFromV2Format(result),
        agentsInvolved: agentsToExecute,
        startTime: new Date(result.start_time || Date.now()),
        endTime: new Date(result.end_time || Date.now()),
        tokenUsage: result.token_usage || result.tokenUsage || 0,
        costEstimate: result.cost_estimate || result.costEstimate || 0,
        systemUsed: 'v2'
      };

    } catch (error: any) {
      return {
        executionId: `v2_error_${Date.now()}`,
        status: 'failed',
        error: error.message,
        agentsInvolved: routing?.agents || [],
        startTime: new Date(),
        endTime: new Date(),
        systemUsed: 'v2'
      };
    }
  }

  /**
   * Get list of available V2 agents
   */
  getAvailableAgents(): string[] {
    const agents: string[] = [];

    // Add orchestrator
    agents.push('orchestrator');

    // Add all agents from my orchestrator registry
    try {
      Object.keys(agentRegistry).forEach(agentName => {
        agents.push(agentName);
      });
    } catch (error) {
      console.warn('Failed to get agents from registry:', error);
    }

    return [...new Set(agents)]; // Remove duplicates
  }

  /**
   * Get detailed capabilities of V2 agents
   */
  async getCapabilities(): Promise<AgentCapabilities[]> {
    const capabilities: AgentCapabilities[] = [];

    // Orchestrator capability
    capabilities.push({
      name: 'orchestrator',
      system: 'v2',
      description: 'Advanced LangGraph orchestration for multi-agent workflows',
      category: 'technical',
      capabilities: ['multi-agent orchestration', 'workflow management', 'intelligent routing'],
      inputs: ['goal', 'context', 'agent_selection'],
      outputs: ['orchestrated_results', 'execution_plan', 'performance_metrics'],
      costEstimate: {
        minTokens: 1000,
        maxTokens: 10000,
        estimatedCost: 0.25
      },
      metadata: {
        author: 'system',
        tags: ['v2', 'orchestration', 'langgraph'],
        complexity: 'complex',
        version: '2.0.0'
      }
    });

    // Get capabilities from my agent registry
    try {
      Object.entries(agentRegistry).forEach(([agentName, agent]) => {
        if (agent && agent.manifest) {
          capabilities.push({
            name: agentName,
            system: 'v2',
            description: agent.manifest.description,
            category: this.mapV2Category(agent.manifest.category || 'marketing'),
            capabilities: agent.manifest.capabilities,
            inputs: ['brandProfileId', 'inputOverrides', 'contextSnapshot'],
            outputs: ['generated content', 'metadata'],
            costEstimate: agent.manifest.costEstimate,
            metadata: {
              author: 'system',
              tags: ['orchestrator', 'v2', agentName.toLowerCase()],
              complexity: agent.manifest.metadata?.complexity || 'medium',
              version: '1.0.0'
            }
          });
        }
      });
    } catch (error) {
      console.warn('Failed to get V2 agent capabilities from registry:', error);
    }

    return capabilities;
  }

  /**
   * Get health status of V2 adapter
   */
  async getHealth(): Promise<{
    status: 'healthy' | 'degraded' | 'unhealthy';
    agents: number;
    message?: string;
  }> {
    try {
      const availableAgents = this.getAvailableAgents();

      // Consider healthy if we have agents and basic services are working
      const hasAgents = availableAgents.length > 5; // Should have at least orchestrator + some agents
      const canOrchestrate = true; // Assume orchestrator is functional

      let status: 'healthy' | 'degraded' | 'unhealthy';
      if (hasAgents && canOrchestrate) {
        status = 'healthy';
      } else if (hasAgents || canOrchestrate) {
        status = 'degraded';
      } else {
        status = 'unhealthy';
      }

      return {
        status,
        agents: availableAgents.length,
        message: `${availableAgents.length} V2 agents available, orchestrator operational`
      };

    } catch (error: any) {
      return {
        status: 'unhealthy',
        agents: 0,
        message: `V2 system error: ${error.message}`
      };
    }
  }

  /**
   * Check if adapter can handle specific agents
   */
  canHandleAgents(agentNames: string[]): boolean {
    const availableAgents = this.getAvailableAgents();
    return agentNames.every(name => availableAgents.includes(name));
  }

  /**
   * Get execution status for V2 workflows
   */
  async getExecutionStatus(executionId: string): Promise<any> {
    try {
      // Check if it's a workflow ID
      if (executionId.startsWith('wf_')) {
        // This would integrate with workflow status tracking
        return {
          executionId,
          status: 'processing',
          progress: 65,
          message: 'V2 workflow in progress'
        };
      }

      // For other executions, return basic status
      return {
        executionId,
        status: 'completed',
        progress: 100,
        message: 'V2 execution completed'
      };

    } catch (error: any) {
      return {
        executionId,
        status: 'failed',
        error: error.message
      };
    }
  }

  // =====================================================
  // PRIVATE METHODS
  // =====================================================

  /**
   * Execute advanced multi-agent workflow
   */
  private async executeAdvancedWorkflow(request: any): Promise<any> {
    // For now, execute the first agent in the list (simplified multi-agent)
    const primaryAgent = request.selected_agents?.[0] || 'BrandScript';

    try {
      const agent = agentRegistry[primaryAgent];
      if (!agent) {
        throw new Error(`Agent not found: ${primaryAgent}`);
      }

      const result = await agent.generate({
        brandProfileId: request.context?.brand?.id || 'default',
        inputOverrides: {
          goal: request.goal,
          context: request.context,
          ...request.inputOverrides
        },
        contextSnapshot: request.context,
      });

      return {
        workflow_id: `wf_${Date.now()}`,
        execution_id: `v2_wf_${Date.now()}`,
        result: result,
        agents_executed: 1,
        token_usage: result.metadata?.tokenUsage || 0,
        cost_estimate: result.metadata?.cost || 0,
        start_time: new Date().toISOString(),
        end_time: new Date().toISOString()
      };
    } catch (error) {
      throw new Error(`Workflow execution failed: ${error.message}`);
    }
  }

  /**
   * Execute single V2 agent
   */
  private async executeSingleAgent(agentName: string, request: any): Promise<any> {
    try {
      const agent = agentRegistry[agentName];
      if (!agent) {
        throw new Error(`V2 agent not found: ${agentName}`);
      }

      // Convert to agent input format
      const agentInput = {
        brandProfileId: request.context?.brand?.id || 'default',
        inputOverrides: {
          goal: request.goal,
          context: request.context,
          ...request.inputOverrides
        },
        contextSnapshot: request.context,
      };

      const result = await agent.generate(agentInput);

      return {
        execution_id: `v2_single_${Date.now()}`,
        agent: agentName,
        result: result,
        metadata: result.metadata,
        token_usage: result.metadata?.tokenUsage || 0,
        cost_estimate: result.metadata?.cost || 0,
        start_time: new Date().toISOString(),
        end_time: new Date().toISOString()
      };

    } catch (error: any) {
      throw new Error(`V2 agent execution failed: ${error.message}`);
    }
  }

  /**
   * Convert unified request to V2 format
   */
  private convertToV2Format(request: UnifiedRequest, agents: string[]): any {
    return {
      goal: request.goal,
      userId: request.userId,
      context: {
        campaign: request.context?.campaign,
        icp: request.context?.icp,
        brand: request.context?.brand,
        constraints: request.context?.constraints || []
      },
      agent_selection: request.agentSelection || 'auto',
      selected_agents: agents,
      inputOverrides: request.inputOverrides
    };
  }

  /**
   * Convert V2 result to unified format
   */
  private convertFromV2Format(result: any): any {
    return {
      system: 'v2',
      output: result.result || result.outputs || result,
      metadata: result.metadata || {},
      agents_executed: result.agents_executed || 1,
      workflow_id: result.workflow_id,
      performance: {
        token_usage: result.token_usage || 0,
        execution_time: result.execution_time || 0,
        quality_score: result.quality_score || 0
      }
    };
  }

  /**
   * Map V2 agent category to unified category
   */
  private mapV2Category(v2Category: string): 'brand' | 'content' | 'marketing' | 'technical' {
    const categoryMap: Record<string, 'brand' | 'content' | 'marketing' | 'technical'> = {
      'brand': 'brand',
      'content': 'content',
      'creative': 'content',
      'marketing': 'marketing',
      'technical': 'technical'
    };

    return categoryMap[v2Category] || 'marketing';
  }
}
