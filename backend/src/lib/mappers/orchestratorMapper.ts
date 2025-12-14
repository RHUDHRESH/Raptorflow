/**
 * Orchestrator context mappers
 * Transform and validate orchestrator state between runtime and schema
 */

import { z } from 'zod';
import { OrchestratorContext, OrchestratorState, Department } from '../../v2/types';

/**
 * Safely transform loose object to OrchestratorContext
 * Handles cases where runtime state doesn't match schema exactly
 */
export function toOrchestratorContext(
  input: Record<string, any>
): OrchestratorContext {
  // Provide defaults for missing required fields
  const safeInput = {
    user_id: input.user_id || '',
    goal: input.goal || '',
    campaign_context: input.campaign_context || {},
    icp_context: input.icp_context || {},
    current_state: input.current_state || OrchestratorState.INITIALIZING,
    execution_plan: input.execution_plan || [],
    completed_agents: input.completed_agents || [],
    failed_agents: input.failed_agents || [],
    results: input.results || {},
    dead_end_detected: input.dead_end_detected || false,
    dead_end_reason: input.dead_end_reason || undefined,
    token_budget: input.token_budget || {
      total: 100000,
      used: 0,
      remaining: 100000,
      last_checkpoint: 0
    },
    execution_metadata: input.execution_metadata || {
      start_time: new Date().toISOString(),
      progress_percentage: 0
    }
  };

  // Validate and return
  return OrchestratorContext.parse(safeInput);
}

/**
 * Transform OrchestratorContext to runtime-safe object
 * Useful for state persistence or external APIs
 */
export function fromOrchestratorContext(
  context: OrchestratorContext
): Record<string, any> {
  return {
    user_id: context.user_id,
    goal: context.goal,
    campaign_context: context.campaign_context,
    icp_context: context.icp_context,
    current_state: context.current_state,
    execution_plan: context.execution_plan.map(plan => ({
      department: plan.department,
      agents: plan.agents,
      dependencies: plan.dependencies,
      priority: plan.priority
    })),
    completed_agents: [...context.completed_agents],
    failed_agents: [...context.failed_agents],
    results: { ...context.results },
    dead_end_detected: context.dead_end_detected,
    dead_end_reason: context.dead_end_reason,
    token_budget: {
      total: context.token_budget.total,
      used: context.token_budget.used,
      remaining: context.token_budget.remaining,
      last_checkpoint: context.token_budget.last_checkpoint
    },
    execution_metadata: {
      start_time: context.execution_metadata.start_time,
      estimated_completion: context.execution_metadata.estimated_completion,
      current_step: context.execution_metadata.current_step,
      progress_percentage: context.execution_metadata.progress_percentage
    }
  };
}

/**
 * Create initial orchestrator context
 */
export function createInitialContext(
  userId: string,
  goal: string,
  tokenBudget: number = 100000
): OrchestratorContext {
  return toOrchestratorContext({
    user_id: userId,
    goal: goal,
    current_state: OrchestratorState.INITIALIZING,
    token_budget: {
      total: tokenBudget,
      used: 0,
      remaining: tokenBudget,
      last_checkpoint: 0
    },
    execution_metadata: {
      start_time: new Date().toISOString(),
      progress_percentage: 0
    }
  });
}

/**
 * Update context with execution progress
 */
export function updateExecutionProgress(
  context: OrchestratorContext,
  updates: {
    current_state?: OrchestratorState;
    completed_agents?: string[];
    failed_agents?: string[];
    results?: Record<string, any>;
    progress_percentage?: number;
    token_used?: number;
  }
): OrchestratorContext {
  const updated = fromOrchestratorContext(context);

  if (updates.current_state) updated.current_state = updates.current_state;
  if (updates.completed_agents) updated.completed_agents = [...new Set([...updated.completed_agents, ...updates.completed_agents])];
  if (updates.failed_agents) updated.failed_agents = [...new Set([...updated.failed_agents, ...updates.failed_agents])];
  if (updates.results) updated.results = { ...updated.results, ...updates.results };
  if (updates.progress_percentage !== undefined) updated.execution_metadata.progress_percentage = updates.progress_percentage;

  if (updates.token_used) {
    updated.token_budget.used += updates.token_used;
    updated.token_budget.remaining = Math.max(0, updated.token_budget.total - updated.token_budget.used);
  }

  return toOrchestratorContext(updated);
}


