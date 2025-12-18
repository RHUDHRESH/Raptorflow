/**
 * Orchestrator Server
 *
 * Main REST API server for the Muse AI Agents orchestrator.
 * Handles agent requests, job queuing, and result delivery.
 */

import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import { z } from 'zod';
import { agentRegistry, type AgentName } from '../v2/agents';
import { redisMemory } from '../services/redisMemory';
import { llmAdapter } from '../v2/llm/adapter';
import { sqsJobQueue } from '../services/sqsJobQueue';
import { authService } from '../services/authService';

// Muse asset type to orchestrator agent mapping
const MUSE_ASSET_MAPPING: Record<string, AgentName> = {
  // Pillar content
  'pillar_webinar_script': 'BrandScript',
  'pillar_whitepaper': 'BrandScript',

  // Micro content
  'linkedin_post': 'SocialMediaIdeas',
  'twitter_thread': 'SocialMediaIdeas',

  // Sales enablement
  'battlecard': 'SalesEmail',
  'comparison_page': 'ProductDescription',
  'case_study': 'BrandStory',

  // Lifecycle
  'email_sequence': 'NurtureEmails',
  'onboarding_email': 'SalesEmail',

  // Tools
  'roi_calculator_spec': 'ProductDescription',

  // Images and Visuals
  'social_media_image': 'ImageGenerator',
  'hero_banner': 'ImageGenerator',
  'product_image': 'ImageGenerator',
  'brand_logo_concept': 'ImageGenerator',
  'infographic': 'ImageGenerator',
  'website_hero': 'ImageGenerator',

  // Fallbacks
  'pillar': 'BrandScript',
  'micro': 'SocialMediaIdeas',
  'sales': 'SalesEmail',
  'lifecycle': 'NurtureEmails',
  'abm': 'SalesEmail',
  'tools': 'ProductDescription',
  'images': 'ImageGenerator'
};

// Types
interface OrchestratorRequest {
  agentName: AgentName;
  brandProfileId: string;
  inputOverrides?: Record<string, unknown>;
  contextSnapshot?: Record<string, unknown>;
  priority?: number;
  metadata?: {
    source?: string;
    tags?: string[];
    priority?: 'low' | 'normal' | 'high' | 'urgent';
    timeout?: number;
    retryCount?: number;
    [key: string]: unknown;
  };
}

interface OrchestratorResponse {
  jobId: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  estimatedDuration: number;
  agentName: string;
  createdAt: string;
}

interface MuseRequest {
  asset_type: string;
  icp_id?: string;
  brandProfileId?: string;
  inputOverrides?: Record<string, unknown>;
  contextSnapshot?: Record<string, unknown>;
}

interface JobStatusResponse {
  jobId: string;
  status: 'queued' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  result?: Record<string, unknown>;
  error?: string;
  createdAt: string;
  updatedAt: string;
  duration?: number;
}

// Validation schemas
const orchestratorRequestSchema = z.object({
  agentName: z.enum(Object.keys(agentRegistry) as [AgentName, ...AgentName[]]),
  brandProfileId: z.string().uuid(),
  inputOverrides: z.record(z.any()).optional(),
  contextSnapshot: z.record(z.any()).optional(),
  priority: z.number().min(0).max(10).optional(),
  metadata: z.record(z.any()).optional(),
});

// Router setup (integrated into main backend)
const router = express.Router();

// Middleware (inherited from main app)
// Note: CORS and body parsing are handled by the main app

// Health check
router.get('/health', (req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: '1.0.0',
  });
});

// Get available agents
router.get('/agents', (req: Request, res: Response) => {
  const agents = Object.entries(agentRegistry).map(([name, agent]) => ({
    name,
    description: agent.manifest.description,
    category: agent.manifest.category,
    capabilities: agent.manifest.capabilities,
    costEstimate: agent.manifest.costEstimate,
    inputs: agent.manifest.inputs,
    outputs: agent.manifest.outputs,
  }));

  res.json({
    agents,
    total: agents.length,
    categories: [...new Set(agents.map(a => a.category))],
  });
});

// Get specific agent details
router.get('/agents/:agentName', (req: Request, res: Response) => {
  const { agentName } = req.params;

  if (!(agentName in agentRegistry)) {
    return res.status(404).json({
      error: 'Agent not found',
      message: `Agent '${agentName}' does not exist`,
    });
  }

  const agent = agentRegistry[agentName as AgentName];

  res.json({
    name: agentName,
    manifest: agent.manifest,
    status: 'available',
  });
});

// Submit job to agent (protected)
router.post('/jobs',
  authService.authenticateRequest.bind(authService),
  authService.checkQuotaMiddleware('request'),
  authService.authorize('orchestrator', 'create_job'),
  async (req: Request, res: Response) => {
  try {
    // Validate request
    const validatedData = orchestratorRequestSchema.parse(req.body);

    const { agentName, brandProfileId, inputOverrides, contextSnapshot, priority, metadata } = validatedData;

    // Generate job ID
    const jobId = `job_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    // Get agent
    const agent = agentRegistry[agentName];

    // Create job context
    const jobContext = {
      jobId,
      status: 'queued' as const,
      progress: 0,
      contextSnapshot: {
        ...contextSnapshot,
        agentName,
        brandProfileId,
        priority: priority || 0,
        submittedAt: new Date().toISOString(),
        metadata,
      },
      lastUpdate: Date.now(),
    };

    // Store job context in Redis
    await redisMemory.storeJobContext(jobId, jobContext);

    // Send job to SQS queue for asynchronous processing
    await sqsJobQueue.sendJob({
      jobId,
      agentName,
      input: {
        brandProfileId,
        inputOverrides,
        contextSnapshot,
        jobId,
        userId: metadata?.userId,
      },
      priority,
      contextSnapshot: jobContext.contextSnapshot,
      queuedAt: new Date().toISOString(),
      metadata,
    });

    const response: OrchestratorResponse = {
      jobId,
      status: 'queued',
      estimatedDuration: estimateJobDuration(agent.manifest.complexity),
      agentName,
      createdAt: new Date().toISOString(),
    };

    res.status(202).json(response);

  } catch (error) {
    console.error('Job submission error:', error);

    if (error instanceof z.ZodError) {
      return res.status(400).json({
        error: 'Validation error',
        message: 'Invalid request data',
        details: error.errors,
      });
    }

    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to submit job',
    });
  }
});

// Muse-specific endpoint for asset generation (simplified interface for Muse page)
router.post('/generate',
  authService.authenticateRequest.bind(authService),
  authService.checkQuotaMiddleware('request'),
  authService.authorize('orchestrator', 'create_job'),
  async (req: Request, res: Response) => {
  try {
    // Validate Muse request
    const museSchema = z.object({
      asset_type: z.string(),
      icp_id: z.string().optional(),
      brandProfileId: z.string().optional(),
      inputOverrides: z.record(z.unknown()).optional(),
      contextSnapshot: z.record(z.unknown()).optional(),
    });

    const validatedData = museSchema.parse(req.body);
    const { asset_type, icp_id, brandProfileId, inputOverrides, contextSnapshot } = validatedData;

    // Map asset type to orchestrator agent
    const agentName = MUSE_ASSET_MAPPING[asset_type] || MUSE_ASSET_MAPPING.pillar; // Default fallback

    if (!agentName || !(agentName in agentRegistry)) {
      return res.status(400).json({
        error: 'Unsupported asset type',
        message: `Asset type '${asset_type}' is not supported`,
        supported_types: Object.keys(MUSE_ASSET_MAPPING)
      });
    }

    // Get user context for brand profile
    const userContext = authService.extractUserContext(req);
    const finalBrandProfileId = brandProfileId || userContext.organizationId; // Use org as fallback

    if (!finalBrandProfileId) {
      return res.status(400).json({
        error: 'Brand profile required',
        message: 'Either provide brandProfileId or ensure user has organization context'
      });
    }

    // Create orchestrator request
    const orchestratorRequest: OrchestratorRequest = {
      agentName,
      brandProfileId: finalBrandProfileId,
      inputOverrides: {
        assetType: asset_type,
        icpId: icp_id,
        ...inputOverrides,
      },
      contextSnapshot: {
        source: 'muse_page',
        museAssetType: asset_type,
        icpId: icp_id,
        ...contextSnapshot,
      },
      priority: 1, // Normal priority for Muse requests
      metadata: {
        source: 'muse_page',
        assetType: asset_type,
        tags: ['muse', asset_type],
      }
    };

    // Generate job ID
    const jobId = `muse_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    // Get agent for estimated duration
    const agent = agentRegistry[agentName];

    // Create job context
    const jobContext = {
      jobId,
      status: 'queued' as const,
      progress: 0,
      contextSnapshot: {
        ...orchestratorRequest.contextSnapshot,
        agentName,
        brandProfileId: finalBrandProfileId,
        priority: orchestratorRequest.priority,
        submittedAt: new Date().toISOString(),
        metadata: orchestratorRequest.metadata,
      },
      lastUpdate: Date.now(),
    };

    // Store job context in Redis
    await redisMemory.storeJobContext(jobId, jobContext);

    // Send job to SQS queue
    await sqsJobQueue.sendJob({
      jobId,
      agentName,
      input: orchestratorRequest,
    });

    // Return Muse-compatible response
    res.status(202).json({
      job_id: jobId,
      asset_type: asset_type,
      status: 'generating',
      estimated_duration: agent.manifest.estimatedDuration || 30, // Default 30 seconds
      agent_name: agentName,
      created_at: new Date().toISOString(),
    });

  } catch (error: any) {
    console.error('Muse generation error:', error);

    if (error instanceof z.ZodError) {
      return res.status(400).json({
        error: 'Validation error',
        details: error.errors,
      });
    }

    res.status(500).json({
      error: 'Generation failed',
      message: 'Failed to start asset generation',
    });
  }
});

// Get Muse job status (simplified interface)
router.get('/generate/:jobId',
  authService.authenticateRequest.bind(authService),
  authService.authorize('orchestrator', 'read_job'),
  async (req: Request, res: Response) => {
  try {
    const { jobId } = req.params;

    const jobContext = await redisMemory.getJobContext(jobId);

    if (!jobContext) {
      return res.status(404).json({
        error: 'Job not found',
        message: `Generation job '${jobId}' does not exist`,
      });
    }

    // Return Muse-compatible response
    const response: any = {
      job_id: jobId,
      status: jobContext.status,
      progress: jobContext.progress,
      created_at: jobContext.contextSnapshot?.submittedAt,
    };

    // Add result if completed
    if (jobContext.status === 'completed' && jobContext.contextSnapshot?.result) {
      try {
        const result = JSON.parse(jobContext.contextSnapshot.result);
        const isImageAsset = getCategoryFromAssetType(jobContext.contextSnapshot.museAssetType) === 'images';

        response.asset = {
          id: `asset_${jobId}`,
          name: result.title || `Generated ${jobContext.contextSnapshot.museAssetType}`,
          asset_type: jobContext.contextSnapshot.museAssetType,
          category: getCategoryFromAssetType(jobContext.contextSnapshot.museAssetType),
          status: 'approved', // Muse expects approved status for completed assets
          content: isImageAsset ? (result.prompt || 'AI-generated image') : (result.content || result.description || JSON.stringify(result)),
          imageUrl: isImageAsset ? result.imageUrl : undefined,
          metadata: result,
          created_at: new Date().toISOString(),
        };
      } catch (parseError) {
        const isImageAsset = getCategoryFromAssetType(jobContext.contextSnapshot.museAssetType) === 'images';

        response.asset = {
          id: `asset_${jobId}`,
          name: `Generated ${jobContext.contextSnapshot.museAssetType}`,
          asset_type: jobContext.contextSnapshot.museAssetType,
          category: getCategoryFromAssetType(jobContext.contextSnapshot.museAssetType),
          status: 'approved',
          content: isImageAsset ? 'AI-generated image' : jobContext.contextSnapshot.result,
          imageUrl: isImageAsset ? jobContext.contextSnapshot.result : undefined,
          created_at: new Date().toISOString(),
        };
      }
    }

    // Add error if failed
    if (jobContext.status === 'failed') {
      response.error = jobContext.contextSnapshot?.error || 'Generation failed';
    }

    res.json(response);

  } catch (error: any) {
    console.error('Muse job status error:', error);
    res.status(500).json({
      error: 'Status check failed',
      message: 'Failed to get generation status',
    });
  }
});

// Generate PDF from asset content (for Muse page downloads)
router.post('/pdf/generate',
  authService.authenticateRequest.bind(authService),
  authService.authorize('orchestrator', 'create_job'),
  async (req: Request, res: Response) => {
  try {
    const { content, title, assetType, metadata } = req.body;

    if (!content || !title) {
      return res.status(400).json({
        error: 'Missing required fields',
        message: 'content and title are required'
      });
    }

    // Create simple HTML for PDF generation
    const html = `
      <!DOCTYPE html>
      <html>
        <head>
          <meta charset="UTF-8">
          <title>${title}</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
            h1 { color: #2563eb; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; }
            .metadata { background: #f8fafc; padding: 15px; border-radius: 8px; margin: 20px 0; }
            .content { white-space: pre-wrap; }
            .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb; font-size: 12px; color: #6b7280; }
          </style>
        </head>
        <body>
          <h1>${title}</h1>
          ${metadata ? `<div class="metadata">
            ${metadata.generatedAt ? `<p><strong>Generated:</strong> ${new Date(metadata.generatedAt).toLocaleDateString()}</p>` : ''}
            ${assetType ? `<p><strong>Type:</strong> ${assetType}</p>` : ''}
          </div>` : ''}
          <div class="content">${content}</div>
          <div class="footer">
            <p>Generated by Muse AI Agents</p>
          </div>
        </body>
      </html>
    `;

    // Generate PDF using html-pdf-node
    const { pdfGenerator } = await import('../services/pdfGenerator');
    const pdfResult = await pdfGenerator.generatePDF({
      template: 'custom',
      data: { html },
      filename: `${title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.pdf`,
      metadata: {
        type: 'muse_asset_download',
        source: 'muse_page',
        ...metadata
      }
    });

    res.json({
      url: pdfResult.url,
      filename: pdfResult.filename,
      size: pdfResult.size
    });

  } catch (error: any) {
    console.error('PDF generation error:', error);
    res.status(500).json({
      error: 'PDF generation failed',
      message: error.message
    });
  }
});

// Get job status (protected)
router.get('/jobs/:jobId',
  authService.authenticateRequest.bind(authService),
  authService.authorize('orchestrator', 'read_job'),
  async (req: Request, res: Response) => {
  try {
    const { jobId } = req.params;

    const jobContext = await redisMemory.getJobContext(jobId);

    if (!jobContext) {
      return res.status(404).json({
        error: 'Job not found',
        message: `Job '${jobId}' does not exist`,
      });
    }

    const response: JobStatusResponse = {
      jobId,
      status: jobContext.status,
      progress: jobContext.progress,
      result: jobContext.status === 'completed' ? jobContext.contextSnapshot?.result : undefined,
      error: jobContext.status === 'failed' ? jobContext.contextSnapshot?.error : undefined,
      createdAt: new Date(jobContext.contextSnapshot?.submittedAt).toISOString(),
      updatedAt: new Date(jobContext.lastUpdate).toISOString(),
      duration: jobContext.status === 'completed' ? jobContext.contextSnapshot?.duration : undefined,
    };

    res.json(response);

  } catch (error) {
    console.error('Job status error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to get job status',
    });
  }
});

// Get job results (alias for status, but more explicit)
router.get('/jobs/:jobId/result', async (req: Request, res: Response) => {
  const jobResponse = await getJobResponse(req.params.jobId);

  if (!jobResponse) {
    return res.status(404).json({
      error: 'Job not found',
      message: `Job '${req.params.jobId}' does not exist`,
    });
  }

  if (jobResponse.status !== 'completed') {
    return res.status(202).json({
      ...jobResponse,
      message: 'Job is still processing',
    });
  }

  res.json(jobResponse);
});

// List jobs (with pagination)
router.get('/jobs',
  authService.authenticateRequest.bind(authService),
  authService.authorize('orchestrator', 'list_jobs'),
  async (req: Request, res: Response) => {
  try {
    const { limit = 20, offset = 0, status, agentName } = req.query;

    // In a real implementation, this would query the database
    // For now, return empty array
    res.json({
      jobs: [],
      total: 0,
      limit: Number(limit),
      offset: Number(offset),
    });

  } catch (error) {
    console.error('Jobs list error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to list jobs',
    });
  }
});

// API Key management routes
router.post('/keys',
  authService.authenticateRequest.bind(authService),
  authService.authorize('orchestrator', 'manage_keys'),
  async (req: Request, res: Response) => {
  try {
    const { name, projectId, permissions, quotas, expiresIn } = req.body;
    const user = req.user;

    if (!user) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const apiKey = await authService.createAPIKey(
      name,
      projectId || user.projectId,
      user.organizationId,
      user.userId,
      permissions,
      quotas,
      expiresIn
    );

    // Don't return the actual key value for security
    res.json({
      id: apiKey.id,
      name: apiKey.name,
      projectId: apiKey.projectId,
      permissions: apiKey.permissions,
      quotas: apiKey.quotas,
      createdAt: apiKey.createdAt,
      expiresAt: apiKey.expiresAt,
    });

  } catch (error) {
    console.error('API key creation error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to create API key',
    });
  }
});

router.get('/keys',
  authService.authenticateRequest.bind(authService),
  authService.authorize('orchestrator', 'manage_keys'),
  async (req: Request, res: Response) => {
  try {
    const user = req.user;

    if (!user || !user.projectId) {
      return res.status(400).json({ error: 'Project ID required' });
    }

    const keys = await authService.getProjectAPIKeys(user.projectId);

    res.json({ keys });

  } catch (error) {
    console.error('API keys list error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to list API keys',
    });
  }
});

router.delete('/keys/:keyId',
  authService.authenticateRequest.bind(authService),
  authService.authorize('orchestrator', 'manage_keys'),
  async (req: Request, res: Response) => {
  try {
    const { keyId } = req.params;

    // In a real implementation, this would revoke the key
    // For now, just return success
    res.json({ message: 'API key revoked successfully' });

  } catch (error) {
    console.error('API key revocation error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to revoke API key',
    });
  }
});

// Quota status
router.get('/quotas',
  authService.authenticateRequest.bind(authService),
  async (req: Request, res: Response) => {
  try {
    const user = req.user;

    if (!user) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    // Get current usage (simplified)
    const { usage } = await authService.checkQuota(user, 'request', 0);

    res.json({
      usage,
      limits: {
        requestsPerHour: 1000,
        requestsPerDay: 10000,
        tokensPerHour: 100000,
        tokensPerDay: 1000000,
        costPerDay: 50.00,
      },
    });

  } catch (error) {
    console.error('Quota check error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to get quota status',
    });
  }
});

// Error handling middleware
router.use((error: Error, req: Request, res: Response, next: NextFunction) => {
  console.error('Unhandled error:', error);
  res.status(500).json({
    error: 'Internal server error',
    message: 'An unexpected error occurred',
  });
});

// 404 handler
router.use((req: Request, res: Response) => {
  res.status(404).json({
    error: 'Not found',
    message: `Route ${req.method} ${req.path} not found`,
  });
});

// Helper functions
async function getJobResponse(jobId: string): Promise<JobStatusResponse | null> {
  const jobContext = await redisMemory.getJobContext(jobId);

  if (!jobContext) return null;

  return {
    jobId,
    status: jobContext.status,
    progress: jobContext.progress,
    result: jobContext.status === 'completed' ? jobContext.contextSnapshot?.result : undefined,
    error: jobContext.status === 'failed' ? jobContext.contextSnapshot?.error : undefined,
    createdAt: new Date(jobContext.contextSnapshot?.submittedAt).toISOString(),
    updatedAt: new Date(jobContext.lastUpdate).toISOString(),
    duration: jobContext.status === 'completed' ? jobContext.contextSnapshot?.duration : undefined,
  };
}

function estimateJobDuration(complexity: string): number {
  const durationMap = {
    simple: 30000,    // 30 seconds
    medium: 60000,    // 1 minute
    complex: 120000,  // 2 minutes
  };

  return durationMap[complexity as keyof typeof durationMap] || 60000;
}


// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('SIGINT received, shutting down gracefully');
  process.exit(0);
});

// Helper function to map asset types to categories
function getCategoryFromAssetType(assetType: string): string {
  const categoryMap: Record<string, string> = {
    // Pillar content
    'pillar_webinar_script': 'pillar',
    'pillar_whitepaper': 'pillar',

    // Micro content
    'linkedin_post': 'micro',
    'twitter_thread': 'micro',

    // Sales enablement
    'battlecard': 'sales',
    'comparison_page': 'sales',
    'case_study': 'sales',

    // Lifecycle
    'email_sequence': 'lifecycle',
    'onboarding_email': 'lifecycle',

    // Tools
    'roi_calculator_spec': 'tools',

    // ABM
    'abm': 'abm'
  };

  return categoryMap[assetType] || 'pillar'; // Default to pillar
}

// Export router for use in main backend
export default router;
