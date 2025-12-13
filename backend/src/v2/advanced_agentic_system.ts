import { RaptorFlowOrchestrator } from './orchestrator';
import { agentRegistry } from './base_agent';
import { toolbox } from './toolbox';

// =====================================================
// ADVANCED AGENTIC SYSTEM - COORDINATION LAYER
// =====================================================

export class AdvancedAgenticSystem {
  private orchestrator: RaptorFlowOrchestrator;
  private activeWorkflows: Map<string, any> = new Map();

  constructor() {
    this.orchestrator = new RaptorFlowOrchestrator();
  }

  /**
   * Create an advanced workflow
   */
  async createWorkflow(goal: string, userId: string, context?: any): Promise<any> {
    const workflowId = `wf_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    const workflow = {
      id: workflowId,
      userId,
      goal,
      context,
      status: 'created',
      created_at: new Date().toISOString(),
      agents: await this.selectAgentsForWorkflow(goal, context),
      estimated_tokens: this.estimateWorkflowTokens(goal, context)
    };

    this.activeWorkflows.set(workflowId, workflow);
    return workflow;
  }

  /**
   * Execute an advanced workflow
   */
  async executeWorkflow(workflowId: string): Promise<any> {
    const workflow = this.activeWorkflows.get(workflowId);
    if (!workflow) {
      throw new Error('Workflow not found');
    }

    try {
      // Update status
      workflow.status = 'executing';
      workflow.started_at = new Date().toISOString();

      // Execute using orchestrator
      const result = await this.orchestrator.executeWorkflow({
        user_id: workflow.userId,
        goal: workflow.goal,
        campaign_context: workflow.context?.campaign || {},
        icp_context: workflow.context?.icp || {},
        current_state: 'EXECUTING',
        execution_plan: [],
        completed_agents: [],
        failed_agents: [],
        results: {},
        dead_end_detected: false,
        dead_end_reason: '',
        token_budget: { total: 50000, used: 0, remaining: 50000, last_checkpoint: 0 },
        execution_metadata: {
          start_time: new Date().toISOString(),
          progress_percentage: 0,
          estimated_completion: new Date(Date.now() + 15 * 60 * 1000).toISOString()
        }
      });

      // Update workflow
      workflow.status = 'completed';
      workflow.completed_at = new Date().toISOString();
      workflow.result = result;

      return result;

    } catch (error) {
      workflow.status = 'failed';
      workflow.error = error.message;
      throw error;
    }
  }

  /**
   * Get available agents
   */
  getAvailableAgents(): string[] {
    return agentRegistry.getAllAgents().map(agent => agent.name);
  }

  /**
   * Get active workflows
   */
  getActiveWorkflows(): string[] {
    return Array.from(this.activeWorkflows.keys());
  }

  /**
   * Get workflow status
   */
  getWorkflowStatus(workflowId: string): any {
    return this.activeWorkflows.get(workflowId) || null;
  }

  /**
   * Select agents for workflow based on goal and context
   */
  private async selectAgentsForWorkflow(goal: string, context?: any): Promise<string[]> {
    const goalLower = goal.toLowerCase();
    const selectedAgents: string[] = [];

    // Core agents always included
    selectedAgents.push('orchestrator', 'market_intel_agent');

    // Add specialized agents based on goal
    if (goalLower.includes('strategy') || goalLower.includes('positioning')) {
      selectedAgents.push('positioning_architect_agent', 'value_proposition_agent');
    }

    if (goalLower.includes('campaign') || goalLower.includes('launch')) {
      selectedAgents.push('campaign_architect_agent', 'move_designer_agent');
    }

    if (goalLower.includes('creative') || goalLower.includes('content')) {
      selectedAgents.push('creative_director_agent', 'copywriter_agent');
    }

    if (goalLower.includes('social') || goalLower.includes('community')) {
      selectedAgents.push('social_content_agent');
    }

    if (goalLower.includes('advertising') || goalLower.includes('ads')) {
      selectedAgents.push('ad_variants_agent', 'ads_targeting_agent');
    }

    if (goalLower.includes('automation') || goalLower.includes('email')) {
      selectedAgents.push('email_automation_agent', 'lead_nurture_agent');
    }

    if (goalLower.includes('analytics') || goalLower.includes('optimize')) {
      selectedAgents.push('metrics_interpreter_agent', 'forecasting_agent');
    }

    // Limit to prevent overload
    return selectedAgents.slice(0, 8);
  }

  /**
   * Estimate tokens for workflow
   */
  private estimateWorkflowTokens(goal: string, context?: any): number {
    const baseTokens = 10000; // Base overhead
    const goalTokens = goal.length * 2; // Rough token estimation
    const contextTokens = context ? JSON.stringify(context).length : 0;

    return baseTokens + goalTokens + contextTokens;
  }
}

// Export singleton instance
export const advancedAgenticSystem = new AdvancedAgenticSystem();