/**
 * V3 Unified API Routes
 *
 * REST API endpoints for the unified V1-V2 orchestration system
 */

import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { unifiedOrchestrator } from './unified_orchestrator';
import { UnifiedRequestSchema, UnifiedResponseSchema } from './types';
import { authenticateJWT } from '../v2/auth_middleware';

const router = Router();

// =====================================================
// UNIFIED API ROUTES
// =====================================================

// Apply authentication middleware
router.use(authenticateJWT);

// Health check endpoint
router.get('/health', async (req: Request, res: Response) => {
  try {
    const health = await unifiedOrchestrator.getHealth();

    res.json({
      status: 'ok',
      timestamp: new Date().toISOString(),
      system: 'unified-orchestrator-v3',
      version: '1.0.0',
      health
    });
  } catch (error: any) {
    res.status(500).json({
      status: 'error',
      message: error.message,
      system: 'unified-orchestrator-v3'
    });
  }
});

// =====================================================
// EXECUTION ENDPOINTS
// =====================================================

/**
 * POST /v3/execute
 * Execute a unified orchestration request
 */
router.post('/execute', async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    // Validate request
    const validatedData = UnifiedRequestSchema.parse({
      ...req.body,
      userId
    });

    // Execute orchestration
    const result = await unifiedOrchestrator.execute(validatedData);

    // Return appropriate HTTP status
    const statusCode = result.status === 'completed' ? 200 :
                      result.status === 'processing' ? 202 : 500;

    res.status(statusCode).json({
      ...result,
      _links: {
        status: `/v3/status/${result.executionId}`,
        result: `/v3/result/${result.executionId}`
      }
    });

  } catch (error: any) {
    console.error('Unified execution failed:', error);

    if (error instanceof z.ZodError) {
      return res.status(400).json({
        error: 'Validation failed',
        details: error.errors
      });
    }

    res.status(500).json({
      error: 'Execution failed',
      message: error.message
    });
  }
});

/**
 * GET /v3/status/:executionId
 * Get execution status
 */
router.get('/status/:executionId', async (req: Request, res: Response) => {
  try {
    const { executionId } = req.params;
    const userId = (req as any).user?.id;

    if (!userId) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const status = unifiedOrchestrator.getExecutionStatus(executionId);

    if (!status) {
      return res.status(404).json({ error: 'Execution not found' });
    }

    // Check if user owns this execution
    if (status.userId !== userId) {
      return res.status(403).json({ error: 'Access denied' });
    }

    res.json(status);

  } catch (error: any) {
    res.status(500).json({
      error: 'Status check failed',
      message: error.message
    });
  }
});

/**
 * GET /v3/result/:executionId
 * Get execution result
 */
router.get('/result/:executionId', async (req: Request, res: Response) => {
  try {
    const { executionId } = req.params;
    const userId = (req as any).user?.id;

    if (!userId) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const status = unifiedOrchestrator.getExecutionStatus(executionId);

    if (!status) {
      return res.status(404).json({ error: 'Execution not found' });
    }

    // Check if user owns this execution
    if (status.userId !== userId) {
      return res.status(403).json({ error: 'Access denied' });
    }

    if (status.status !== 'completed') {
      return res.status(202).json({
        status: status.status,
        message: 'Execution not yet completed',
        progress: status.progress
      });
    }

    res.json({
      executionId: status.executionId,
      status: status.status,
      result: status.result,
      agentsInvolved: status.agentsInvolved,
      tokenUsage: status.tokenUsage,
      costEstimate: status.costEstimate,
      systemUsed: status.systemUsed,
      completedAt: status.endTime
    });

  } catch (error: any) {
    res.status(500).json({
      error: 'Result retrieval failed',
      message: error.message
    });
  }
});

// =====================================================
// DISCOVERY ENDPOINTS
// =====================================================

/**
 * GET /v3/agents
 * List all available agents across systems
 */
router.get('/agents', async (req: Request, res: Response) => {
  try {
    const agents = await unifiedOrchestrator.getAllAvailableAgents();

    // Group by system
    const grouped = agents.reduce((acc, agent) => {
      const system = agent.system;
      if (!acc[system]) acc[system] = [];
      acc[system].push(agent);
      return acc;
    }, {} as Record<string, typeof agents>);

    res.json({
      total_agents: agents.length,
      systems: {
        v1: {
          count: grouped.v1?.length || 0,
          agents: grouped.v1 || []
        },
        v2: {
          count: grouped.v2?.length || 0,
          agents: grouped.v2 || []
        }
      },
      all_agents: agents
    });

  } catch (error: any) {
    res.status(500).json({
      error: 'Agent discovery failed',
      message: error.message
    });
  }
});

/**
 * GET /v3/capabilities
 * Get detailed capabilities of all agents
 */
router.get('/capabilities', async (req: Request, res: Response) => {
  try {
    const capabilities = await unifiedOrchestrator.getAllAvailableAgents();

    // Add usage examples and metadata
    const enhancedCapabilities = capabilities.map(agent => ({
      ...agent,
      api_usage: {
        endpoint: '/v3/execute',
        method: 'POST',
        example: {
          goal: `Example goal for ${agent.name}`,
          agentSelection: 'manual',
          selectedAgents: [agent.name]
        }
      },
      performance: {
        typical_response_time: agent.metadata.complexity === 'simple' ? '5-10s' :
                              agent.metadata.complexity === 'medium' ? '15-30s' : '30-120s',
        reliability: '99%'
      }
    }));

    res.json({
      timestamp: new Date().toISOString(),
      total_capabilities: enhancedCapabilities.length,
      capabilities: enhancedCapabilities
    });

  } catch (error: any) {
    res.status(500).json({
      error: 'Capabilities retrieval failed',
      message: error.message
    });
  }
});

// =====================================================
// ANALYTICS ENDPOINTS
// =====================================================

/**
 * GET /v3/metrics
 * Get orchestration metrics and performance data
 */
router.get('/metrics', async (req: Request, res: Response) => {
  try {
    const health = await unifiedOrchestrator.getHealth();

    // This would integrate with a metrics service
    const metrics = {
      timestamp: new Date().toISOString(),
      system_health: health,
      performance: {
        average_response_time_ms: 2500,
        success_rate_percent: 98.5,
        total_executions_today: 0,
        active_executions: 0
      },
      costs: {
        total_today_usd: 0,
        average_cost_per_execution_usd: 0.15,
        token_usage_today: 0
      },
      agents: {
        v1_active: health.v1.agents,
        v2_active: health.v2.agents,
        total_available: health.v1.agents + health.v2.agents
      }
    };

    res.json(metrics);

  } catch (error: any) {
    res.status(500).json({
      error: 'Metrics retrieval failed',
      message: error.message
    });
  }
});

/**
 * POST /v3/feedback
 * Provide feedback on orchestration results
 */
router.post('/feedback', async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const { executionId, rating, feedback, improvements } = req.body;

    if (!executionId || !rating) {
      return res.status(400).json({
        error: 'executionId and rating are required'
      });
    }

    // This would integrate with a feedback service
    console.log(`Feedback received for execution ${executionId}:`, {
      userId,
      rating,
      feedback,
      improvements
    });

    res.json({
      feedback_processed: true,
      executionId,
      rating,
      message: 'Thank you for your feedback. This helps improve our orchestration.'
    });

  } catch (error: any) {
    res.status(500).json({
      error: 'Feedback processing failed',
      message: error.message
    });
  }
});

// =====================================================
// BATCH OPERATIONS
// =====================================================

/**
 * POST /v3/batch
 * Execute multiple orchestration requests in batch
 */
router.post('/batch', async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user?.id;
    if (!userId) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const { requests, parallel = false } = req.body;

    if (!Array.isArray(requests) || requests.length === 0) {
      return res.status(400).json({ error: 'requests array is required' });
    }

    if (requests.length > 10) {
      return res.status(400).json({ error: 'Maximum 10 requests per batch' });
    }

    const batchId = `batch_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    if (parallel) {
      // Execute in parallel
      const promises = requests.map(requestData =>
        unifiedOrchestrator.execute({
          ...requestData,
          userId
        })
      );

      const results = await Promise.allSettled(promises);

      const response = {
        batchId,
        total_requests: requests.length,
        completed: results.filter(r => r.status === 'fulfilled').length,
        failed: results.filter(r => r.status === 'rejected').length,
        results: results.map((result, index) => ({
          request_index: index,
          status: result.status,
          ...(result.status === 'fulfilled'
            ? { data: result.value }
            : { error: (result as any).reason?.message }
          )
        }))
      };

      res.json(response);

    } else {
      // Execute sequentially
      const results = [];
      for (let i = 0; i < requests.length; i++) {
        try {
          const result = await unifiedOrchestrator.execute({
            ...requests[i],
            userId
          });
          results.push({ request_index: i, status: 'fulfilled', data: result });
        } catch (error: any) {
          results.push({
            request_index: i,
            status: 'rejected',
            error: error.message
          });
        }
      }

      res.json({
        batchId,
        total_requests: requests.length,
        completed: results.filter(r => r.status === 'fulfilled').length,
        failed: results.filter(r => r.status === 'rejected').length,
        results
      });
    }

  } catch (error: any) {
    res.status(500).json({
      error: 'Batch execution failed',
      message: error.message
    });
  }
});

export default router;


