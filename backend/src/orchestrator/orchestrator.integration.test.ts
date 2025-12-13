/**
 * Integration Tests for Orchestrator
 *
 * End-to-end tests covering the full orchestrator flow:
 * Job submission → Queueing → Processing → Storage → Retrieval
 */

import { describe, it, expect, beforeAll, afterAll, beforeEach, vi } from 'vitest';
import request from 'supertest';

// Mock external dependencies
vi.mock('../services/redisMemory', () => ({
  redisMemory: {
    storeJobContext: vi.fn(),
    updateJobProgress: vi.fn(),
    getJobContext: vi.fn(),
    storeAgentMemory: vi.fn(),
    getAgentMemory: vi.fn(),
    delete: vi.fn(),
  },
}));

vi.mock('../services/sqsJobQueue', () => ({
  sqsJobQueue: {
    sendJob: vi.fn(),
  },
}));

vi.mock('../services/authService', () => ({
  authService: {
    authenticateRequest: vi.fn((req, res, next) => next()),
    checkQuotaMiddleware: vi.fn(() => (req, res, next) => next()),
    authorize: vi.fn(() => (req, res, next) => next()),
  },
}));

// Import after mocking
import app from './server';
import { redisMemory } from '../services/redisMemory';
import { sqsJobQueue } from '../services/sqsJobQueue';

const agent = request(app);

describe('Orchestrator Integration Tests', () => {
  const testBrandProfileId = '550e8400-e29b-41d4-a716-446655440000';
  const testJobId = 'job_test_123';

  beforeAll(async () => {
    // Setup test environment
    process.env.NODE_ENV = 'test';
  });

  afterAll(async () => {
    // Cleanup
  });

  beforeEach(() => {
    vi.clearAllMocks();

    // Setup default mock responses
    vi.mocked(redisMemory.storeJobContext).mockResolvedValue();
    vi.mocked(redisMemory.updateJobProgress).mockResolvedValue();
    vi.mocked(redisMemory.getJobContext).mockResolvedValue({
      jobId: testJobId,
      status: 'completed',
      progress: 100,
      contextSnapshot: {
        result: JSON.stringify({
          primaryTagline: 'Test Tagline',
          alternativeTaglines: ['Alt 1', 'Alt 2'],
        }),
        submittedAt: new Date().toISOString(),
        duration: 1500,
      },
      lastUpdate: Date.now(),
    });

    vi.mocked(sqsJobQueue.sendJob).mockResolvedValue();
  });

  describe('Health Check', () => {
    it('should return healthy status', async () => {
      const response = await agent.get('/health');

      expect(response.status).toBe(200);
      expect(response.body.status).toBe('healthy');
      expect(response.body.version).toBe('1.0.0');
      expect(response.body.timestamp).toBeDefined();
    });
  });

  describe('Agent Registry', () => {
    it('should list all available agents', async () => {
      const response = await agent.get('/agents');

      expect(response.status).toBe(200);
      expect(response.body.agents).toBeDefined();
      expect(Array.isArray(response.body.agents)).toBe(true);
      expect(response.body.agents.length).toBeGreaterThan(0);

      // Check agent structure
      const firstAgent = response.body.agents[0];
      expect(firstAgent).toHaveProperty('name');
      expect(firstAgent).toHaveProperty('description');
      expect(firstAgent).toHaveProperty('category');
      expect(firstAgent).toHaveProperty('capabilities');
      expect(firstAgent).toHaveProperty('costEstimate');
    });

    it('should return agent details', async () => {
      const response = await agent.get('/agents/Tagline');

      expect(response.status).toBe(200);
      expect(response.body.name).toBe('Tagline');
      expect(response.body.manifest).toBeDefined();
      expect(response.body.status).toBe('available');
    });

    it('should return 404 for unknown agent', async () => {
      const response = await agent.get('/agents/UnknownAgent');

      expect(response.status).toBe(404);
      expect(response.body.error).toBe('Agent not found');
    });
  });

  describe('Job Submission and Processing', () => {
    const validJobRequest = {
      agentName: 'Tagline',
      brandProfileId: testBrandProfileId,
      inputOverrides: {
        targetAudience: 'Millennials',
        industry: 'Technology',
      },
      contextSnapshot: {
        campaignGoal: 'Brand awareness',
      },
    };

    it('should accept valid job submission', async () => {
      const response = await agent
        .post('/jobs')
        .send(validJobRequest);

      expect(response.status).toBe(202);
      expect(response.body.jobId).toBeDefined();
      expect(response.body.status).toBe('queued');
      expect(response.body.estimatedDuration).toBeDefined();
      expect(response.body.agentName).toBe('Tagline');
    });

    it('should validate required fields', async () => {
      const invalidRequest = {
        agentName: 'Tagline',
        // Missing brandProfileId
        inputOverrides: {},
      };

      const response = await agent
        .post('/jobs')
        .send(invalidRequest);

      expect(response.status).toBe(400);
      expect(response.body.error).toBe('Validation error');
      expect(response.body.details).toBeDefined();
    });

    it('should reject unknown agents', async () => {
      const invalidRequest = {
        ...validJobRequest,
        agentName: 'UnknownAgent',
      };

      const response = await agent
        .post('/jobs')
        .send(invalidRequest);

      expect(response.status).toBe(400);
      expect(response.body.error).toBe('Validation error');
    });

    it('should queue job for processing', async () => {
      await agent
        .post('/jobs')
        .send(validJobRequest);

      expect(sqsJobQueue.sendJob).toHaveBeenCalledWith(
        expect.objectContaining({
          agentName: 'Tagline',
          input: expect.objectContaining({
            brandProfileId: testBrandProfileId,
            inputOverrides: validJobRequest.inputOverrides,
          }),
        })
      );

      expect(redisMemory.storeJobContext).toHaveBeenCalled();
    });
  });

  describe('Job Status and Results', () => {
    it('should return job status', async () => {
      const response = await agent
        .get(`/jobs/${testJobId}`);

      expect(response.status).toBe(200);
      expect(response.body.jobId).toBe(testJobId);
      expect(response.body.status).toBe('completed');
      expect(response.body.progress).toBe(100);
      expect(response.body.result).toBeDefined();
    });

    it('should return 404 for unknown job', async () => {
      vi.mocked(redisMemory.getJobContext).mockResolvedValue(null);

      const response = await agent
        .get('/jobs/unknown-job-id');

      expect(response.status).toBe(404);
      expect(response.body.error).toBe('Job not found');
    });

    it('should return job results when completed', async () => {
      const response = await agent
        .get(`/jobs/${testJobId}/result`);

      expect(response.status).toBe(200);
      expect(response.body.jobId).toBe(testJobId);
      expect(response.body.status).toBe('completed');
      expect(response.body.result).toBeDefined();
      expect(response.body.duration).toBeDefined();
    });

    it('should return 202 for processing jobs', async () => {
      vi.mocked(redisMemory.getJobContext).mockResolvedValue({
        jobId: testJobId,
        status: 'running',
        progress: 50,
        contextSnapshot: {},
        lastUpdate: Date.now(),
      });

      const response = await agent
        .get(`/jobs/${testJobId}/result`);

      expect(response.status).toBe(202);
      expect(response.body.status).toBe('running');
      expect(response.body.progress).toBe(50);
      expect(response.body.message).toBe('Job is still processing');
    });
  });

  describe('Error Handling', () => {
    it('should handle internal server errors gracefully', async () => {
      // Mock a service to throw an error
      vi.mocked(redisMemory.storeJobContext).mockRejectedValue(new Error('Database error'));

      const response = await agent
        .post('/jobs')
        .send({
          agentName: 'Tagline',
          brandProfileId: testBrandProfileId,
        });

      expect(response.status).toBe(500);
      expect(response.body.error).toBe('Internal server error');
    });

    it('should handle malformed JSON', async () => {
      const response = await agent
        .post('/jobs')
        .set('Content-Type', 'application/json')
        .send('{invalid json');

      expect(response.status).toBe(400);
    });
  });

  describe('End-to-End Flow', () => {
    it('should complete full job lifecycle', async () => {
      // 1. Submit job
      const submitResponse = await agent
        .post('/jobs')
        .send({
          agentName: 'Tagline',
          brandProfileId: testBrandProfileId,
          inputOverrides: { industry: 'Technology' },
        });

      expect(submitResponse.status).toBe(202);
      const jobId = submitResponse.body.jobId;

      // 2. Check job status (would be queued initially)
      let statusResponse = await agent
        .get(`/jobs/${jobId}`);

      expect(statusResponse.status).toBe(200);

      // 3. Get results (mocked as completed)
      const resultResponse = await agent
        .get(`/jobs/${jobId}/result`);

      expect(resultResponse.status).toBe(200);
      expect(resultResponse.body.result).toBeDefined();

      // 4. Verify the result structure
      const result = JSON.parse(resultResponse.body.result);
      expect(result.primaryTagline).toBeDefined();
      expect(result.alternativeTaglines).toBeDefined();
    });
  });
});