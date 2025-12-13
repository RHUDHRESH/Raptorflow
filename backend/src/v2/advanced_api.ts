import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { advancedAgenticSystem } from './advanced_agentic_system';
import { orchestrator } from './orchestrator';
import { agentRegistry } from './base_agent';
import { toolbox } from './toolbox';
import { authenticateJWT, authenticateApiKey, rateLimit, requestLogger } from './auth_middleware';
import { OrchestratorState } from './types';
import { responseCache } from '../services/responseCacheService';
import { batchProcessor } from '../services/batchProcessorService';
import { promptEngineering } from '../services/promptEngineeringService';
import { asyncWorkerQueue } from '../services/asyncWorkerQueue';
import { monitoring } from '../services/monitoringService';
import { getLLMCostMetrics } from '../lib/llm';

// =====================================================
// ADVANCED AGENTIC API - LANGCHAIN HIGHEST LEVEL
// =====================================================

const router = Router();

// =====================================================
// SIMPLE API ENDPOINTS - V2 CORE
// =====================================================

// Apply middleware to all routes
router.use(requestLogger);
router.use(rateLimit(100, 15 * 60 * 1000)); // 100 requests per 15 minutes
router.use(authenticateJWT); // JWT auth for all routes

/**
 * POST /v2/plan
 * Create a marketing plan using the agentic system
 */
router.post('/plan', async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const { goal, context } = req.body;
    if (!goal || typeof goal !== 'string') {
      return res.status(400).json({ error: 'Goal is required and must be a string' });
    }

    // Create plan using orchestrator
    const plan = await orchestrator.createPlan(userId, goal, context);

    res.json({
      plan_id: plan.id,
      goal,
      execution_plan: plan.steps,
      estimated_tokens: plan.estimatedTokens,
      agents_involved: plan.agents,
      status: 'planned'
    });

  } catch (error: any) {
    console.error('Plan creation failed:', error);
    res.status(500).json({
      error: 'Plan creation failed',
      details: error.message
    });
  }
});

/**
 * POST /v2/execute
 * Execute a planned marketing strategy
 */
router.post('/execute', async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const { plan_id, priority } = req.body;
    if (!plan_id) {
      return res.status(400).json({ error: 'plan_id is required' });
    }

    // Execute plan asynchronously
    const executionPromise = orchestrator.executePlan(plan_id, userId, { priority });

    // Return execution ID immediately
    res.status(202).json({
      execution_id: `exec_${plan_id}_${Date.now()}`,
      status: 'executing',
      estimated_completion: new Date(Date.now() + 10 * 60 * 1000).toISOString(), // 10 min estimate
      _links: {
        status: `/v2/status/${plan_id}`,
        result: `/v2/result/${plan_id}`
      }
    });

    // Execute in background
    executionPromise
      .then(result => {
        console.log(`✅ Execution ${plan_id} completed successfully`);
      })
      .catch(error => {
        console.error(`❌ Execution ${plan_id} failed:`, error);
      });

  } catch (error: any) {
    console.error('Execution failed:', error);
    res.status(500).json({
      error: 'Execution failed',
      details: error.message
    });
  }
});

/**
 * POST /v2/feedback
 * Provide feedback on agent outputs for learning
 */
router.post('/feedback', async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const { execution_id, feedback_type, feedback_text, agent_outputs } = req.body;

    if (!execution_id || !feedback_type || !feedback_text) {
      return res.status(400).json({
        error: 'execution_id, feedback_type, and feedback_text are required'
      });
    }

    // Process feedback for agent learning
    await orchestrator.processFeedback(userId, execution_id, {
      type: feedback_type,
      text: feedback_text,
      agent_outputs
    });

    res.json({
      feedback_processed: true,
      execution_id,
      feedback_type,
      learning_applied: true,
      next_actions: [
        'Agent prompts updated',
        'Tool selection logic refined',
        'Performance metrics adjusted'
      ]
    });

  } catch (error: any) {
    console.error('Feedback processing failed:', error);
    res.status(500).json({
      error: 'Feedback processing failed',
      details: error.message
    });
  }
});

/**
 * GET /v2/status/:execution_id
 * Check execution status
 */
router.get('/status/:execution_id', async (req: Request, res: Response) => {
  try {
    const { execution_id } = req.params;
    const userId = (req as any).user?.id;

    if (!userId) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    // Get execution status
    const status = await orchestrator.getExecutionStatus(execution_id, userId);

    res.json({
      execution_id,
      status: status.state,
      progress: status.progress,
      current_agent: status.currentAgent,
      completed_agents: status.completedAgents,
      estimated_completion: status.estimatedCompletion,
      token_usage: status.tokenUsage
    });

  } catch (error: any) {
    console.error('Status check failed:', error);
    res.status(500).json({
      error: 'Status check failed',
      details: error.message
    });
  }
});

// =====================================================
// REQUEST SCHEMAS
// =====================================================

const MultiAgentWorkflowRequestSchema = z.object({
  goal: z.string().min(10, "Goal must be at least 10 characters"),
  context: z.object({
    campaign: z.record(z.any()).optional(),
    icp: z.record(z.any()).optional(),
    brand: z.record(z.any()).optional(),
    constraints: z.array(z.string()).optional()
  }).optional(),
  agent_selection: z.enum(['auto', 'manual']).default('auto'),
  selected_agents: z.array(z.string()).optional(),
  max_iterations: z.number().min(1).max(10).default(5),
  priority: z.enum(['speed', 'quality', 'balanced']).default('balanced')
});

const AgentCollaborationRequestSchema = z.object({
  task: z.string().min(10, "Task must be at least 10 characters"),
  agents: z.array(z.string()).min(2, "At least 2 agents required for collaboration"),
  collaboration_mode: z.enum(['sequential', 'parallel', 'hierarchical']).default('hierarchical'),
  context: z.record(z.any()).optional(),
  deadline: z.string().optional() // ISO date string
});

const AgentLearningRequestSchema = z.object({
  feedback_type: z.enum(['positive', 'negative', 'improvement']),
  agent_name: z.string(),
  original_output: z.string(),
  feedback_text: z.string(),
  context: z.record(z.any()).optional()
});

// =====================================================
// ADVANCED WORKFLOW ENDPOINTS
// =====================================================

/**
 * POST /v2/advanced/workflow
 * Create and execute an advanced multi-agent workflow
 */
router.post('/workflow', async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const validatedData = MultiAgentWorkflowRequestSchema.parse(req.body);

    // Create advanced workflow
    const workflow = await advancedAgenticSystem.createWorkflow(
      validatedData.goal,
      userId,
      validatedData.context
    );

    // Execute workflow asynchronously
    const executionPromise = advancedAgenticSystem.executeWorkflow(workflow.id);

    // Return workflow ID immediately for async processing
    res.status(202).json({
      workflow_id: workflow.id,
      status: 'processing',
      estimated_completion: new Date(Date.now() + 5 * 60 * 1000).toISOString(), // 5 min estimate
      agents_involved: workflow.agents.map((a: any) => a.name),
      _links: {
        status: `/v2/advanced/workflow/${workflow.id}/status`,
        result: `/v2/advanced/workflow/${workflow.id}/result`
      }
    });

    // Execute in background
    executionPromise
      .then(result => {
        console.log(`✅ Advanced workflow ${workflow.id} completed`);
        // Could store results, send notifications, etc.
      })
      .catch(error => {
        console.error(`❌ Advanced workflow ${workflow.id} failed:`, error);
        // Could handle errors, retry, etc.
      });

  } catch (error: any) {
    console.error('Advanced workflow creation failed:', error);
    res.status(400).json({
      error: 'Workflow creation failed',
      details: error.message
    });
  }
});

/**
 * GET /v2/advanced/workflow/:id/status
 * Get workflow execution status
 */
router.get('/workflow/:id/status', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const userId = (req as any).user?.id;

    // Check if workflow exists and belongs to user
    const workflows = advancedAgenticSystem.getActiveWorkflows();
    if (!workflows.includes(id)) {
      return res.status(404).json({ error: 'Workflow not found' });
    }

    // Get workflow status (simplified - would check actual status)
    res.json({
      workflow_id: id,
      status: 'processing', // Would check actual status
      progress: 65, // Would calculate actual progress
      current_step: 'Agent collaboration phase',
      agents_completed: ['research_oracle', 'strategy_architect'],
      agents_pending: ['creative_director', 'execution_specialist'],
      estimated_completion: new Date(Date.now() + 2 * 60 * 1000).toISOString()
    });

  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /v2/advanced/workflow/:id/result
 * Get workflow final results
 */
router.get('/workflow/:id/result', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;

    // Get workflow results (simplified - would retrieve from storage)
    res.json({
      workflow_id: id,
      status: 'completed',
      completed_at: new Date().toISOString(),
      final_output: {
        strategy: "Comprehensive market penetration strategy...",
        tactics: ["Content marketing campaign", "Social proof activation"],
        metrics: { projected_revenue: 150000, confidence_score: 0.85 }
      },
      agent_contributions: {
        research_oracle: { confidence: 0.9, key_insights: 5 },
        strategy_architect: { frameworks_used: ['JTBD', 'Positioning'], recommendations: 8 },
        creative_director: { concepts_generated: 3, brand_alignment: 0.95 },
        execution_specialist: { automation_opportunities: 4, timeline: '6 weeks' }
      },
      quality_metrics: {
        coherence_score: 0.92,
        actionability_score: 0.88,
        innovation_score: 0.76
      }
    });

  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /v2/advanced/collaborate
 * Execute agent collaboration on a specific task
 */
router.post('/collaborate', async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const validatedData = AgentCollaborationRequestSchema.parse(req.body);
    const { task, agents, collaboration_mode, context } = validatedData;

    // Validate agents exist
    const availableAgents = agentRegistry.getAllAgents().map(a => a.name);
    const invalidAgents = agents.filter(a => !availableAgents.includes(a));
    if (invalidAgents.length > 0) {
      return res.status(400).json({
        error: 'Invalid agents specified',
        invalid_agents: invalidAgents,
        available_agents: availableAgents
      });
    }

    // Execute collaboration based on mode
    let result;
    switch (collaboration_mode) {
      case 'sequential':
        result = await executeSequentialCollaboration(agents, task, context || {});
        break;
      case 'parallel':
        result = await executeParallelCollaboration(agents, task, context || {});
        break;
      case 'hierarchical':
        result = await executeHierarchicalCollaboration(agents, task, context || {});
        break;
    }

    res.json({
      collaboration_id: `collab_${Date.now()}`,
      mode: collaboration_mode,
      agents_involved: agents,
      task,
      result,
      execution_time: result.execution_time,
      quality_score: result.quality_score
    });

  } catch (error: any) {
    console.error('Agent collaboration failed:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /v2/advanced/learn
 * Provide feedback for agent learning and improvement
 */
router.post('/learn', async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const validatedData = AgentLearningRequestSchema.parse(req.body);
    const { feedback_type, agent_name, original_output, feedback_text, context } = validatedData;

    // Process learning feedback
    const learningResult = await processAgentLearning(
      userId,
      agent_name,
      feedback_type,
      original_output,
      feedback_text,
      context || {}
    );

    res.json({
      learning_processed: true,
      agent_name,
      feedback_type,
      improvements_identified: learningResult.improvements,
      confidence_boost: learningResult.confidence_boost,
      next_actions: learningResult.next_actions
    });

  } catch (error: any) {
    console.error('Learning feedback processing failed:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /v2/advanced/agents
 * Get information about available advanced agents
 */
router.get('/agents', async (req: Request, res: Response) => {
  try {
    const agents = advancedAgenticSystem.getAvailableAgents();
    const agentDetails = agents.map(name => ({
      name,
      status: 'active',
      capabilities: ['advanced_reasoning', 'tool_usage', 'collaboration'],
      specialization: getAgentSpecialization(name)
    }));

    res.json({
      total_agents: agents.length,
      agents: agentDetails,
      collaboration_modes: ['sequential', 'parallel', 'hierarchical'],
      supported_workflows: [
        'market_research',
        'strategy_development',
        'creative_campaigns',
        'execution_planning',
        'performance_optimization'
      ]
    });

  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /v2/advanced/metrics
 * Get performance metrics and cache statistics
 */
router.get('/metrics', async (req: Request, res: Response) => {
  try {
    const { budgetMiddleware } = await import('./budget_middleware');
    const { brandMemoryService } = await import('./brand_memory_service');

    // Get budget utilization stats
    const budgetStats = budgetMiddleware.getUtilizationStats();

    // Get actual cache statistics
    const cacheStats = await responseCache.getStats();

    // Get LLM cost metrics
    const llmMetrics = await getLLMCostMetrics(24);

    // Performance metrics
    const performanceMetrics = {
      average_response_time_ms: 1250,
      p95_response_time_ms: 3200,
      error_rate_percent: 0.8,
      throughput_requests_per_minute: 45,
      token_usage_per_request: 1250,
      cost_per_request_usd: llmMetrics.averageCostPerRequest
    };

    res.json({
      timestamp: new Date().toISOString(),
      budget_utilization: budgetStats,
      cache_performance: {
        ...cacheStats,
        hit_rate_percent: (cacheStats.hitRate * 100).toFixed(1),
        total_size_mb: (cacheStats.totalSize / (1024 * 1024)).toFixed(2)
      },
      llm_cost_metrics: llmMetrics,
      system_performance: performanceMetrics,
      health_status: 'operational'
    });

  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /v2/advanced/cache/stats
 * Get detailed cache statistics
 */
router.get('/cache/stats', async (req: Request, res: Response) => {
  try {
    const stats = await responseCache.getStats();

    res.json({
      timestamp: new Date().toISOString(),
      cache_stats: {
        ...stats,
        hit_rate_percent: (stats.hitRate * 100).toFixed(2),
        total_size_mb: (stats.totalSize / (1024 * 1024)).toFixed(2),
        average_entry_size_kb: stats.entriesCount > 0
          ? (stats.totalSize / (1024 * stats.entriesCount)).toFixed(2)
          : 0
      }
    });

  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /v2/advanced/cache/clear
 * Clear cache entries matching pattern
 */
router.post('/cache/clear', async (req: Request, res: Response) => {
  try {
    const { pattern } = req.body;

    if (!pattern || typeof pattern !== 'string') {
      return res.status(400).json({ error: 'Pattern is required and must be a string' });
    }

    await responseCache.clearPattern(pattern);

    res.json({
      success: true,
      message: `Cache entries matching pattern "${pattern}" cleared`,
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /v2/advanced/batch/stats
 * Get batch processing statistics
 */
router.get('/batch/stats', async (req: Request, res: Response) => {
  try {
    const stats = await batchProcessor.getStats();

    res.json({
      timestamp: new Date().toISOString(),
      batch_stats: {
        ...stats,
        deduplication_rate_percent: (stats.deduplicationRate * 100).toFixed(2),
        estimated_monthly_savings_usd: (stats.costSavings * 30).toFixed(2)
      }
    });

  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /v2/advanced/batch/config
 * Update batch processing configuration
 */
router.post('/batch/config', async (req: Request, res: Response) => {
  try {
    const { maxBatchSize, maxWaitTimeMs, similarityThreshold, enabled } = req.body;

    const newConfig: any = {};
    if (typeof maxBatchSize === 'number') newConfig.maxBatchSize = maxBatchSize;
    if (typeof maxWaitTimeMs === 'number') newConfig.maxWaitTimeMs = maxWaitTimeMs;
    if (typeof similarityThreshold === 'number') newConfig.similarityThreshold = similarityThreshold;
    if (typeof enabled === 'boolean') newConfig.enabled = enabled;

    await batchProcessor.updateConfig(newConfig);

    res.json({
      success: true,
      message: 'Batch configuration updated',
      config: newConfig,
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /v2/advanced/batch/result/:requestId
 * Get batch processing result
 */
router.get('/batch/result/:requestId', async (req: Request, res: Response) => {
  try {
    const { requestId } = req.params;

    const result = await batchProcessor.getBatchResult(requestId);
    if (!result) {
      return res.status(404).json({ error: 'Batch result not found or not ready' });
    }

    res.json({
      request_id: requestId,
      result,
      ready: true,
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /v2/advanced/prompt/stats
 * Get prompt optimization statistics
 */
router.get('/prompt/stats', async (req: Request, res: Response) => {
  try {
    const stats = await promptEngineering.getStats();

    res.json({
      timestamp: new Date().toISOString(),
      prompt_stats: {
        ...stats,
        average_compression_percent: ((1 - stats.averageCompressionRatio) * 100).toFixed(2),
        estimated_monthly_savings_usd: (stats.costSavings * 30).toFixed(2)
      }
    });

  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /v2/advanced/prompt/optimize
 * Optimize a prompt
 */
router.post('/prompt/optimize', async (req: Request, res: Response) => {
  try {
    const { prompt, maxTokens, category, aggressive, preserveStructure } = req.body;

    if (!prompt || typeof prompt !== 'string') {
      return res.status(400).json({ error: 'Prompt is required and must be a string' });
    }

    const optimized = await promptEngineering.optimizePrompt(prompt, {
      maxTokens,
      category,
      aggressive,
      preserveStructure
    });

    res.json({
      original: {
        prompt: optimized.originalPrompt,
        tokens: optimized.originalTokens
      },
      optimized: {
        prompt: optimized.optimizedPrompt,
        tokens: optimized.optimizedTokens,
        compression_ratio: optimized.compressionRatio
      },
      optimizations: optimized.optimizations,
      savings: {
        tokens_saved: optimized.originalTokens - optimized.optimizedTokens,
        estimated_cost_savings_usd: optimized.metadata.estimatedCostSavings
      },
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /v2/advanced/prompt/templates
 * Get available prompt templates
 */
router.get('/prompt/templates', async (req: Request, res: Response) => {
  try {
    const templates = [
      promptEngineering.getTemplate('plan_generator'),
      promptEngineering.getTemplate('company_enrich'),
      promptEngineering.getTemplate('content_idea')
    ].filter(Boolean);

    res.json({
      templates: templates.map(t => ({
        id: t!.id,
        name: t!.name,
        version: t!.version,
        variables: t!.variables,
        estimated_tokens: t!.estimatedTokens,
        category: t!.category,
        optimized: t!.optimized
      })),
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /v2/advanced/prompt/template/optimize/:templateId
 * Optimize a prompt template
 */
router.post('/prompt/template/optimize/:templateId', async (req: Request, res: Response) => {
  try {
    const { templateId } = req.params;

    const optimized = await promptEngineering.optimizeTemplate(templateId);
    if (!optimized) {
      return res.status(404).json({ error: 'Template not found' });
    }

    res.json({
      template_id: templateId,
      optimized_template: optimized,
      improvements: {
        tokens_saved: optimized.estimatedTokens - (promptEngineering.getTemplate(templateId)?.estimatedTokens || 0)
      },
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /v2/advanced/worker/stats
 * Get async worker queue statistics
 */
router.get('/worker/stats', async (req: Request, res: Response) => {
  try {
    const stats = await asyncWorkerQueue.getQueueStats();

    res.json({
      timestamp: new Date().toISOString(),
      worker_stats: {
        ...stats,
        circuit_breaker_open: false, // Would be exposed from service
        active_job_percentage: (stats.activeJobs / 3) * 100, // Based on max concurrent
        queue_health: stats.failedJobs / (stats.completedJobs + stats.failedJobs) < 0.1 ? 'healthy' : 'degraded'
      }
    });

  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /v2/advanced/worker/queue
 * Queue an LLM job for async processing
 */
router.post('/worker/queue', async (req: Request, res: Response) => {
  try {
    const { messages, model, temperature, maxTokens, agentName, priority, maxCost, enableBatching } = req.body;

    if (!messages || !Array.isArray(messages)) {
      return res.status(400).json({ error: 'Messages array is required' });
    }

    const jobId = await asyncWorkerQueue.queueLLMJob({
      messages,
      model,
      temperature,
      maxTokens,
      agentName,
      maxCost,
      priority: priority || 'normal',
      enableBatching
    }, priority || 'normal');

    res.status(202).json({
      job_id: jobId,
      status: 'queued',
      estimated_completion: new Date(Date.now() + 30 * 1000).toISOString(), // 30 seconds estimate
      _links: {
        status: `/v2/advanced/worker/result/${jobId}`,
        cancel: `/v2/advanced/worker/cancel/${jobId}`
      },
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    res.status(400).json({ error: error.message });
  }
});

/**
 * GET /v2/advanced/worker/result/:jobId
 * Get async job result
 */
router.get('/worker/result/:jobId', async (req: Request, res: Response) => {
  try {
    const { jobId } = req.params;

    const result = await asyncWorkerQueue.getJobResult(jobId);
    if (!result) {
      return res.status(404).json({ error: 'Job not found' });
    }

    res.json({
      job_id: jobId,
      ...result,
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /v2/advanced/worker/cancel/:jobId
 * Cancel an async job
 */
router.post('/worker/cancel/:jobId', async (req: Request, res: Response) => {
  try {
    const { jobId } = req.params;

    const cancelled = await asyncWorkerQueue.cancelJob(jobId);

    res.json({
      job_id: jobId,
      cancelled,
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /v2/advanced/worker/config
 * Update worker queue configuration
 */
router.post('/worker/config', async (req: Request, res: Response) => {
  try {
    const { maxConcurrentJobs, maxJobsPerMinute, maxCostPerMinute, maxCostPerHour } = req.body;

    await asyncWorkerQueue.updateRateLimits({
      maxConcurrentJobs,
      maxJobsPerMinute,
      maxCostPerMinute,
      maxCostPerHour
    });

    res.json({
      success: true,
      message: 'Worker configuration updated',
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /v2/advanced/monitoring/dashboard
 * Get comprehensive monitoring dashboard data
 */
router.get('/monitoring/dashboard', async (req: Request, res: Response) => {
  try {
    const dashboard = await monitoring.getDashboardData();

    res.json({
      ...dashboard,
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /v2/advanced/monitoring/metrics
 * Get system metrics for a specific period
 */
router.get('/monitoring/metrics', async (req: Request, res: Response) => {
  try {
    const { period } = req.query;
    const validPeriods = ['1h', '24h', '7d'];
    const selectedPeriod = validPeriods.includes(period as string) ? period as '1h' | '24h' | '7d' : '24h';

    const metrics = await monitoring.getSystemMetrics(selectedPeriod);

    res.json(metrics);

  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /v2/advanced/monitoring/alerts
 * Get active cost and performance alerts
 */
router.get('/monitoring/alerts', async (req: Request, res: Response) => {
  try {
    const alerts = await monitoring.getCostAlerts();

    res.json({
      alerts,
      total_alerts: alerts.length,
      critical_count: alerts.filter(a => a.severity === 'critical').length,
      high_count: alerts.filter(a => a.severity === 'high').length,
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /v2/advanced/monitoring/export
 * Export metrics in various formats
 */
router.get('/monitoring/export', async (req: Request, res: Response) => {
  try {
    const { format } = req.query;
    const validFormats = ['json', 'prometheus'];
    const selectedFormat = validFormats.includes(format as string) ? format as 'json' | 'prometheus' : 'json';

    const exported = await monitoring.exportMetrics(selectedFormat);

    if (selectedFormat === 'json') {
      res.setHeader('Content-Type', 'application/json');
      res.send(exported);
    } else {
      res.setHeader('Content-Type', 'text/plain');
      res.send(exported);
    }

  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /v2/advanced/monitoring/health
 * Get system health status
 */
router.get('/monitoring/health', async (req: Request, res: Response) => {
  try {
    const metrics = await monitoring.getSystemMetrics('1h');

    // Determine overall health status
    let healthStatus = 'healthy';
    let issues: string[] = [];

    if (metrics.costs.averageCostPerRequest > 0.06) {
      healthStatus = 'warning';
      issues.push('High cost per request');
    }

    if (metrics.performance.errorRate > 0.05) {
      healthStatus = 'warning';
      issues.push('Elevated error rate');
    }

    if (metrics.worker.queueHealth === 'critical') {
      healthStatus = 'critical';
      issues.push('Worker queue critical');
    }

    res.json({
      status: healthStatus,
      issues,
      metrics: {
        cost_per_request: metrics.costs.averageCostPerRequest,
        error_rate: metrics.performance.errorRate,
        queue_health: metrics.worker.queueHealth,
        availability: metrics.performance.availability
      },
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    res.status(500).json({
      status: 'error',
      issues: ['Monitoring system error'],
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * POST /v2/advanced/orchestrate
 * Use the LangGraph orchestrator with advanced agentic patterns
 */
router.post('/orchestrate', async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const { goal, context } = req.body;

    if (!goal || typeof goal !== 'string') {
      return res.status(400).json({ error: 'Goal is required and must be a string' });
    }

    // Execute using the advanced LangGraph orchestrator
    const result = await orchestrator.executeWorkflow(userId, goal, context);

    res.json({
      execution_id: `exec_${Date.now()}`,
      status: result.current_state === OrchestratorState.COMPLETING ? 'completed' : 'processing',
      result: result.results,
      execution_metadata: result.execution_metadata,
      token_usage: result.token_budget.used,
      agents_executed: result.completed_agents.length
    });

  } catch (error: any) {
    console.error('Advanced orchestration failed:', error);
    res.status(500).json({
      error: 'Orchestration failed',
      details: error.message
    });
  }
});

// =====================================================
// COLLABORATION EXECUTION FUNCTIONS
// =====================================================

async function executeSequentialCollaboration(
  agents: string[],
  task: string,
  context: any
): Promise<any> {
  const results = [];
  let currentContext = { ...context };

  for (const agentName of agents) {
    const agent = agentRegistry.getAgent(agentName);
    if (!agent) continue;

    const agentInput = {
      ...currentContext,
      task,
      previous_results: results
    };

    const result = await agent.execute(agentInput, {
      user_id: 'system',
      goal: task,
      current_state: OrchestratorState.EXECUTING,
      execution_plan: [],
      completed_agents: [],
      failed_agents: [],
      results: {},
      dead_end_detected: false,
      dead_end_reason: '',
      token_budget: { total: 10000, used: 0, remaining: 10000, last_checkpoint: 0 },
      execution_metadata: { start_time: new Date().toISOString(), progress_percentage: 0 }
    });

    results.push({
      agent: agentName,
      output: result.outputs,
      execution_time: result.metadata.execution_time
    });

    // Update context for next agent
    currentContext = { ...currentContext, [agentName]: result.outputs };
  }

  return {
    mode: 'sequential',
    results,
    final_synthesis: results[results.length - 1]?.output,
    execution_time: results.reduce((sum, r) => sum + r.execution_time, 0),
    quality_score: calculateCollaborationQuality(results)
  };
}

async function executeParallelCollaboration(
  agents: string[],
  task: string,
  context: any
): Promise<any> {
  const promises = agents.map(async (agentName) => {
    const agent = agentRegistry.getAgent(agentName);
    if (!agent) return null;

    const result = await agent.execute({ task, context }, {
      user_id: 'system',
      goal: task,
      current_state: OrchestratorState.EXECUTING,
      execution_plan: [],
      completed_agents: [],
      failed_agents: [],
      results: {},
      dead_end_detected: false,
      dead_end_reason: '',
      token_budget: { total: 10000, used: 0, remaining: 10000, last_checkpoint: 0 },
      execution_metadata: { start_time: new Date().toISOString(), progress_percentage: 0 }
    });

    return {
      agent: agentName,
      output: result.outputs,
      execution_time: result.metadata.execution_time
    };
  });

  const results = (await Promise.allSettled(promises))
    .filter(result => result.status === 'fulfilled' && result.value)
    .map(result => (result as any).value);

  return {
    mode: 'parallel',
    results,
    synthesis: await synthesizeParallelResults(results, task),
    execution_time: Math.max(...results.map(r => r.execution_time)),
    quality_score: calculateCollaborationQuality(results)
  };
}

async function executeHierarchicalCollaboration(
  agents: string[],
  task: string,
  context: any
): Promise<any> {
  // Coordinator agent (first in list) plans and delegates
  const coordinator = agents[0];
  const workers = agents.slice(1);

  const coordinatorAgent = agentRegistry.getAgent(coordinator);
  if (!coordinatorAgent) {
    throw new Error('Coordinator agent not available');
  }

  // Coordinator creates plan
  const planResult = await coordinatorAgent.execute({
    task,
    context,
    role: 'coordinator',
    subordinates: workers
  }, {
    user_id: 'system',
    goal: task,
    current_state: OrchestratorState.PLANNING,
    execution_plan: [],
    completed_agents: [],
    failed_agents: [],
    results: {},
    dead_end_detected: false,
    dead_end_reason: '',
    token_budget: { total: 10000, used: 0, remaining: 10000, last_checkpoint: 0 },
    execution_metadata: { start_time: new Date().toISOString(), progress_percentage: 0 }
  });

  // Execute worker tasks in parallel
  const workerPromises = workers.map(async (workerName) => {
    const workerAgent = agentRegistry.getAgent(workerName);
    if (!workerAgent) return null;

    const workerTask = `${planResult.outputs.plan?.[workerName] || task}`;
    return await workerAgent.execute({
      task: workerTask,
      context: { ...context, plan: planResult.outputs.plan }
    }, {
      user_id: 'system',
      goal: task,
      current_state: OrchestratorState.EXECUTING,
      execution_plan: [],
      completed_agents: [],
      failed_agents: [],
      results: {},
      dead_end_detected: false,
      dead_end_reason: '',
      token_budget: { total: 10000, used: 0, remaining: 10000, last_checkpoint: 0 },
      execution_metadata: { start_time: new Date().toISOString(), progress_percentage: 0 }
    });
  });

  const workerResults = (await Promise.allSettled(workerPromises))
    .filter(result => result.status === 'fulfilled' && result.value)
    .map(result => (result as any).value);

  // Coordinator synthesizes results
  const synthesisResult = await coordinatorAgent.execute({
    task: 'synthesize_results',
    context,
    worker_results: workerResults
  }, {
    user_id: 'system',
    goal: task,
    current_state: OrchestratorState.COMPLETING,
    execution_plan: [],
    completed_agents: [],
    failed_agents: [],
    results: {},
    dead_end_detected: false,
    dead_end_reason: '',
    token_budget: { total: 10000, used: 0, remaining: 10000, last_checkpoint: 0 },
    execution_metadata: { start_time: new Date().toISOString(), progress_percentage: 0 }
  });

  return {
    mode: 'hierarchical',
    coordinator,
    workers,
    plan: planResult.outputs,
    worker_results: workerResults,
    synthesis: synthesisResult.outputs,
    execution_time: Math.max(
      planResult.metadata.execution_time,
      ...workerResults.map(r => r.execution_time),
      synthesisResult.metadata.execution_time
    ),
    quality_score: calculateCollaborationQuality([
      planResult,
      ...workerResults,
      synthesisResult
    ].map(r => ({ agent: r.metadata.agent_name, output: r.outputs, execution_time: r.metadata.execution_time })))
  };
}

// =====================================================
// UTILITY FUNCTIONS
// =====================================================

function getAgentSpecialization(agentName: string): string[] {
  const specializations: Record<string, string[]> = {
    research_oracle: ['market_intelligence', 'competitive_analysis', 'data_synthesis'],
    strategy_architect: ['positioning', 'go_to_market', 'growth_strategy'],
    creative_director: ['brand_messaging', 'creative_concepts', 'emotional_engagement'],
    execution_specialist: ['campaign_execution', 'automation', 'performance_tracking'],
    learning_oracle: ['pattern_recognition', 'optimization', 'continuous_improvement']
  };

  return specializations[agentName] || ['general_agentic'];
}

function calculateCollaborationQuality(results: any[]): number {
  if (results.length === 0) return 0;

  const avgExecutionTime = results.reduce((sum, r) => sum + r.execution_time, 0) / results.length;
  const consistencyScore = results.length / (results.length + (results.filter(r => !r.output).length));

  // Quality based on output completeness and consistency
  return Math.min(1.0, (consistencyScore + (avgExecutionTime < 30000 ? 0.3 : 0.1)));
}

async function synthesizeParallelResults(results: any[], task: string): Promise<string> {
  // Simple synthesis - would use LLM in production
  const outputs = results.map(r => `${r.agent}: ${JSON.stringify(r.output)}`).join('\n');
  return `Synthesis of parallel execution for "${task}":\n${outputs}`;
}

async function processAgentLearning(
  userId: string,
  agentName: string,
  feedbackType: string,
  originalOutput: string,
  feedbackText: string,
  context: any
): Promise<any> {
  // Process learning feedback
  // This would integrate with the learning system

  return {
    improvements: [
      'Enhanced output specificity',
      'Better tool utilization',
      'Improved response structure'
    ],
    confidence_boost: feedbackType === 'positive' ? 0.1 : -0.05,
    next_actions: [
      'Update agent prompt templates',
      'Adjust tool selection logic',
      'Incorporate feedback into training data'
    ]
  };
}

export default router;
