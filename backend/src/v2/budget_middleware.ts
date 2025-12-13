import { OrchestratorContext, TokenBudget, createTokenBudget } from './types';
import { supabase } from '../lib/supabase';
import { trace, Span, SpanStatusCode } from '@opentelemetry/api';
import { performanceProfiler } from './observability';

// =====================================================
// TOKEN BUDGET MIDDLEWARE
// =====================================================

export interface BudgetLimits {
  maxTokensPerAgent: number;
  maxCostPerAgent: number;
  totalBudget: number;
  warningThreshold: number; // Percentage (e.g., 0.8 for 80%)
  criticalThreshold: number; // Percentage (e.g., 0.95 for 95%)
}

export const DEFAULT_BUDGET_LIMITS: BudgetLimits = {
  maxTokensPerAgent: 10000,
  maxCostPerAgent: 0.5, // $0.50
  totalBudget: 50000, // 50K tokens
  warningThreshold: 0.8,
  criticalThreshold: 0.95
};

export class BudgetMiddleware {
  private limits: BudgetLimits;
  private checkpoints: Map<string, TokenBudget> = new Map();
  private persistenceEnabled: boolean;

  constructor(limits: Partial<BudgetLimits> = {}, enablePersistence = true) {
    this.limits = { ...DEFAULT_BUDGET_LIMITS, ...limits };
    this.persistenceEnabled = enablePersistence;
  }

  /**
   * Initialize budget for a workflow with persistence
   */
  async initializeBudget(workflowId: string, totalBudget?: number): Promise<TokenBudget> {
    const tracer = trace.getTracer('raptorflow-budget');

    return tracer.startActiveSpan('initialize_budget', async (span: Span) => {
      span.setAttributes({
        'workflow.id': workflowId,
        'budget.total': totalBudget || this.limits.totalBudget
      });

      try {
        const budget = createTokenBudget(totalBudget || this.limits.totalBudget);

        // Store in memory cache
        this.checkpoints.set(workflowId, budget);

        // Persist to database if enabled
        if (this.persistenceEnabled) {
          await this.persistBudget(workflowId, budget);
          span.setAttribute('persisted', true);
        }

        span.setStatus({ code: SpanStatusCode.OK });
        span.end();
        return budget;
      } catch (error) {
        span.recordException(error as Error);
        span.setStatus({ code: SpanStatusCode.ERROR, message: (error as Error).message });
        span.end();
        throw error;
      }
    });
  }

  /**
   * Persist budget state to database
   */
  private async persistBudget(workflowId: string, budget: TokenBudget): Promise<void> {
    try {
      const budgetData = {
        workflow_id: workflowId,
        total_tokens: budget.total,
        used_tokens: budget.used,
        remaining_tokens: budget.remaining,
        checkpoints: budget.checkpoints,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      await supabase
        .from('workflow_budgets')
        .upsert(budgetData, {
          onConflict: 'workflow_id',
          returning: 'minimal'
        });

    } catch (error) {
      console.error('Failed to persist budget:', error);
      // Don't throw - persistence failure shouldn't break budget logic
    }
  }

  /**
   * Load budget from database
   */
  private async loadBudget(workflowId: string): Promise<TokenBudget | null> {
    try {
      const { data, error } = await supabase
        .from('workflow_budgets')
        .select('*')
        .eq('workflow_id', workflowId)
        .single();

      if (error || !data) return null;

      return {
        total: data.total_tokens,
        used: data.used_tokens,
        remaining: data.remaining_tokens,
        checkpoints: data.checkpoints || [],
        last_checkpoint: data.used_tokens
      };
    } catch (error) {
      console.error('Failed to load budget:', error);
      return null;
    }
  }

  /**
   * Check if an agent call is within budget
   */
  canExecuteAgent(
    workflowId: string,
    agentName: string,
    estimatedTokens: number,
    estimatedCost: number
  ): {
    allowed: boolean;
    reason?: string;
    remaining_budget: number;
    remaining_cost: number;
  } {
    const budget = this.checkpoints.get(workflowId);
    if (!budget) {
      return {
        allowed: false,
        reason: 'Budget not initialized',
        remaining_budget: 0,
        remaining_cost: 0
      };
    }

    // Check token limits
    if (estimatedTokens > this.limits.maxTokensPerAgent) {
      return {
        allowed: false,
        reason: `Estimated tokens (${estimatedTokens}) exceed per-agent limit (${this.limits.maxTokensPerAgent})`,
        remaining_budget: budget.remaining,
        remaining_cost: budget.total * 0.1 // Rough cost estimate
      };
    }

    // Check cost limits
    if (estimatedCost > this.limits.maxCostPerAgent) {
      return {
        allowed: false,
        reason: `Estimated cost ($${estimatedCost}) exceed per-agent limit ($${this.limits.maxCostPerAgent})`,
        remaining_budget: budget.remaining,
        remaining_cost: budget.total * 0.1
      };
    }

    // Check remaining budget
    if (estimatedTokens > budget.remaining) {
      return {
        allowed: false,
        reason: `Insufficient token budget. Required: ${estimatedTokens}, Remaining: ${budget.remaining}`,
        remaining_budget: budget.remaining,
        remaining_cost: budget.total * (budget.remaining / budget.total)
      };
    }

    return {
      allowed: true,
      remaining_budget: budget.remaining - estimatedTokens,
      remaining_cost: (budget.total - budget.used - estimatedTokens) * 0.0001 // Rough conversion
    };
  }

  /**
   * Record token usage after execution with persistence
   */
  async recordUsage(
    workflowId: string,
    agentName: string,
    actualTokens: number,
    actualCost: number
  ): Promise<void> {
    const tracer = trace.getTracer('raptorflow-budget');
    const endTiming = performanceProfiler.start('budget_record_usage');

    return tracer.startActiveSpan('record_usage', async (span: Span) => {
      span.setAttributes({
        'workflow.id': workflowId,
        'agent.name': agentName,
        'tokens.used': actualTokens,
        'cost.incurred': actualCost
      });

      try {
        let budget = this.checkpoints.get(workflowId);

        // Try to load from database if not in memory
        if (!budget && this.persistenceEnabled) {
          budget = await this.loadBudget(workflowId);
          if (budget) {
            this.checkpoints.set(workflowId, budget);
          }
        }

        if (!budget) {
          console.warn(`Budget not found for workflow ${workflowId}`);
          span.setStatus({ code: SpanStatusCode.ERROR, message: 'Budget not found' });
          span.end();
          endTiming();
          return;
        }

        budget.used += actualTokens;
        budget.remaining = Math.max(0, budget.remaining - actualTokens);
        budget.checkpoints.push(budget.used);

        // Persist updated budget if enabled
        if (this.persistenceEnabled) {
          await this.persistBudget(workflowId, budget);
          span.setAttribute('persisted', true);
        }

        // Log budget status
        const usagePercent = budget.used / budget.total;
        span.setAttributes({
          'budget.usage_percent': usagePercent,
          'budget.remaining': budget.remaining
        });

        console.log(`💰 Budget [${workflowId}]: ${budget.used}/${budget.total} tokens (${(usagePercent * 100).toFixed(1)}%) used by ${agentName}`);

        // Trigger alerts
        if (usagePercent >= this.limits.criticalThreshold) {
          console.error(`🚨 CRITICAL: Budget exceeded ${this.limits.criticalThreshold * 100}% for workflow ${workflowId}`);
          span.setAttribute('alert.level', 'critical');
        } else if (usagePercent >= this.limits.warningThreshold) {
          console.warn(`⚠️ WARNING: Budget exceeded ${this.limits.warningThreshold * 100}% for workflow ${workflowId}`);
          span.setAttribute('alert.level', 'warning');
        }

        span.setStatus({ code: SpanStatusCode.OK });
        span.end();
        endTiming();

      } catch (error) {
        span.recordException(error as Error);
        span.setStatus({ code: SpanStatusCode.ERROR, message: (error as Error).message });
        span.end();
        endTiming();
        throw error;
      }
    });
  }

  /**
   * Get budget status
   */
  getBudgetStatus(workflowId: string): TokenBudget | null {
    return this.checkpoints.get(workflowId) || null;
  }

  /**
   * Check if budget is exhausted
   */
  isBudgetExhausted(workflowId: string): boolean {
    const budget = this.checkpoints.get(workflowId);
    return !budget || budget.remaining <= 0;
  }

  /**
   * Get budget alerts
   */
  getBudgetAlerts(workflowId: string): Array<{
    level: 'warning' | 'critical';
    message: string;
  }> {
    const budget = this.checkpoints.get(workflowId);
    if (!budget) return [];

    const alerts: Array<{ level: 'warning' | 'critical'; message: string }> = [];
    const usagePercent = budget.used / budget.total;

    if (usagePercent >= this.limits.criticalThreshold) {
      alerts.push({
        level: 'critical',
        message: `Budget critically low: ${(usagePercent * 100).toFixed(1)}% used`
      });
    } else if (usagePercent >= this.limits.warningThreshold) {
      alerts.push({
        level: 'warning',
        message: `Budget warning: ${(usagePercent * 100).toFixed(1)}% used`
      });
    }

    // Check recent spending rate
    if (budget.checkpoints.length >= 3) {
      const recent = budget.checkpoints.slice(-3);
      const avgRecentSpend = (recent[recent.length - 1] - recent[0]) / recent.length;

      if (avgRecentSpend > budget.total * 0.1) { // Spending >10% per recent period
        alerts.push({
          level: 'warning',
          message: 'High spending rate detected - consider optimizing prompts'
        });
      }
    }

    return alerts;
  }

  /**
   * Force budget reset (admin only)
   */
  resetBudget(workflowId: string, newTotal?: number): TokenBudget {
    const total = newTotal || this.limits.totalBudget;
    const budget = createTokenBudget(total);
    this.checkpoints.set(workflowId, budget);
    console.log(`🔄 Budget reset for ${workflowId}: ${total} tokens`);
    return budget;
  }

  /**
   * Get budget utilization statistics
   */
  getUtilizationStats(): {
    active_workflows: number;
    total_allocated: number;
    total_used: number;
    average_utilization: number;
    workflows_over_limit: number;
  } {
    const workflows = Array.from(this.checkpoints.values());
    const activeWorkflows = workflows.length;
    const totalAllocated = workflows.reduce((sum, b) => sum + b.total, 0);
    const totalUsed = workflows.reduce((sum, b) => sum + b.used, 0);
    const averageUtilization = activeWorkflows > 0 ? totalUsed / totalAllocated : 0;
    const workflowsOverLimit = workflows.filter(b => b.used > b.total).length;

    return {
      active_workflows: activeWorkflows,
      total_allocated: totalAllocated,
      total_used: totalUsed,
      average_utilization: averageUtilization,
      workflows_over_limit: workflowsOverLimit
    };
  }
}

// =====================================================
// GLOBAL BUDGET MIDDLEWARE INSTANCE
// =====================================================

export const budgetMiddleware = new BudgetMiddleware();

// =====================================================
// CONTEXT-AWARE BUDGET FUNCTIONS
// =====================================================

/**
 * Update orchestrator context with budget information
 */
export const updateContextWithBudget = (
  context: OrchestratorContext,
  budget: TokenBudget
): OrchestratorContext => {
  return {
    ...context,
    token_budget: {
      total: budget.total,
      used: budget.used,
      remaining: budget.remaining,
      last_checkpoint: budget.used
    }
  };
};

/**
 * Check if workflow should continue based on budget
 */
export const shouldContinueWorkflow = (
  context: OrchestratorContext,
  nextAgentEstimatedTokens: number
): {
  should_continue: boolean;
  reason?: string;
  budget_alerts: Array<{ level: 'warning' | 'critical'; message: string }>;
} => {
  const budget = context.token_budget;

  if (budget.remaining < nextAgentEstimatedTokens) {
    return {
      should_continue: false,
      reason: `Insufficient budget: ${budget.remaining} tokens remaining, ${nextAgentEstimatedTokens} required`,
      budget_alerts: [{ level: 'critical', message: 'Budget exhausted' }]
    };
  }

  const usagePercent = budget.used / budget.total;
  const alerts = [];

  if (usagePercent >= 0.95) {
    alerts.push({ level: 'critical', message: 'Critical budget level reached' });
  } else if (usagePercent >= 0.8) {
    alerts.push({ level: 'warning', message: 'Budget warning threshold reached' });
  }

  return {
    should_continue: true,
    budget_alerts: alerts
  };
};

/**
 * Estimate tokens for different task types
 */
export const estimateTokensForTask = (
  taskType: 'simple' | 'general' | 'reasoning' | 'heavy',
  inputLength: number,
  expectedOutputLength?: number
): number => {
  const baseMultipliers = {
    simple: 1.2,
    general: 1.5,
    reasoning: 2.0,
    heavy: 3.0
  };

  const multiplier = baseMultipliers[taskType];
  const estimatedOutput = expectedOutputLength || Math.max(200, inputLength * 0.3);

  return Math.ceil((inputLength + estimatedOutput) * multiplier);
};

/**
 * Estimate cost for task
 */
export const estimateCostForTask = (
  taskType: 'simple' | 'general' | 'reasoning' | 'heavy',
  estimatedTokens: number
): number => {
  const costPerThousand = {
    simple: 0.075,
    general: 0.15,
    reasoning: 0.375,
    heavy: 0.5
  };

  return (estimatedTokens / 1000) * costPerThousand[taskType];
};
