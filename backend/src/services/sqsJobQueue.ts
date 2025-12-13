/**
 * SQS Job Queue Service
 *
 * Handles asynchronous job queuing and processing using AWS SQS.
 */

import { SQSClient, SendMessageCommand, ReceiveMessageCommand, DeleteMessageCommand, Message } from '@aws-sdk/client-sqs';
import { env } from '../config/env';
import { agentRegistry, type AgentName } from '../v2/agents';
import { redisMemory } from './redisMemory';

export interface QueueJob {
  jobId: string;
  agentName: AgentName;
  input: any;
  priority: number;
  contextSnapshot: Record<string, any>;
  queuedAt: string;
  metadata?: Record<string, any>;
}

export interface QueueMessage {
  jobId: string;
  agentName: string;
  input: any;
  priority: number;
  contextSnapshot: Record<string, any>;
  queuedAt: string;
  retryCount: number;
  metadata?: Record<string, any>;
}

class SQSJobQueueService {
  private sqsClient: SQSClient;
  private queueUrl: string;
  private maxRetries = 3;
  private visibilityTimeout = 300; // 5 minutes
  private isProcessing = false;

  constructor() {
    this.sqsClient = new SQSClient({
      region: env.AWS_REGION,
    });
    this.queueUrl = env.SQS_QUEUE_URL || '';
  }

  /**
   * Send a job to the SQS queue
   */
  async sendJob(job: QueueJob): Promise<void> {
    const message: QueueMessage = {
      ...job,
      retryCount: 0,
    };

    const command = new SendMessageCommand({
      QueueUrl: this.queueUrl,
      MessageBody: JSON.stringify(message),
      MessageGroupId: job.agentName, // For FIFO queues (if used)
      MessageAttributes: {
        priority: {
          DataType: 'Number',
          StringValue: job.priority.toString(),
        },
        agentName: {
          DataType: 'String',
          StringValue: job.agentName,
        },
        jobId: {
          DataType: 'String',
          StringValue: job.jobId,
        },
      },
    });

    try {
      await this.sqsClient.send(command);
      console.log(`📤 Job ${job.jobId} sent to SQS queue`);
    } catch (error) {
      console.error('Failed to send job to SQS:', error);
      throw error;
    }
  }

  /**
   * Poll for messages and process them
   */
  async pollAndProcessJobs(): Promise<void> {
    if (this.isProcessing) {
      return; // Already processing
    }

    this.isProcessing = true;

    try {
      const command = new ReceiveMessageCommand({
        QueueUrl: this.queueUrl,
        MaxNumberOfMessages: 5, // Process up to 5 messages at once
        VisibilityTimeout: this.visibilityTimeout,
        WaitTimeSeconds: 20, // Long polling
        MessageAttributeNames: ['All'],
      });

      const response = await this.sqsClient.send(command);

      if (!response.Messages || response.Messages.length === 0) {
        return; // No messages to process
      }

      // Process messages concurrently
      const processingPromises = response.Messages.map(message =>
        this.processMessage(message)
      );

      await Promise.allSettled(processingPromises);

    } catch (error) {
      console.error('Error polling SQS queue:', error);
    } finally {
      this.isProcessing = false;
    }
  }

  /**
   * Process a single SQS message
   */
  private async processMessage(message: Message): Promise<void> {
    if (!message.Body || !message.ReceiptHandle) {
      console.warn('Invalid SQS message received');
      return;
    }

    try {
      const queueMessage: QueueMessage = JSON.parse(message.Body);

      console.log(`🔄 Processing job ${queueMessage.jobId} with agent ${queueMessage.agentName}`);

      // Update job status to running
      await redisMemory.updateJobProgress(queueMessage.jobId, 10, 'running');

      // Execute the job
      await this.executeJob(queueMessage);

      // Delete the message from the queue
      await this.deleteMessage(message.ReceiptHandle);

      console.log(`✅ Job ${queueMessage.jobId} completed successfully`);

    } catch (error) {
      console.error(`❌ Job processing failed:`, error);

      // Handle retry logic
      await this.handleJobFailure(message, error);
    }
  }

  /**
   * Execute a job using the appropriate agent
   */
  private async executeJob(queueMessage: QueueMessage): Promise<void> {
    const agent = agentRegistry[queueMessage.agentName as AgentName];

    if (!agent) {
      throw new Error(`Agent ${queueMessage.agentName} not found`);
    }

    const startTime = Date.now();

    try {
      // Execute the agent
      const result = await agent.generate(queueMessage.input);
      const duration = Date.now() - startTime;

      // Update job context with result
      const jobContext = await redisMemory.getJobContext(queueMessage.jobId);
      if (jobContext) {
        jobContext.status = 'completed';
        jobContext.progress = 100;
        jobContext.contextSnapshot = {
          ...jobContext.contextSnapshot,
          result: result.content,
          metadata: result.metadata,
          duration,
          completedAt: new Date().toISOString(),
        };
        jobContext.lastUpdate = Date.now();

        await redisMemory.storeJobContext(queueMessage.jobId, jobContext);
      }

    } catch (error) {
      // Update job with error
      const jobContext = await redisMemory.getJobContext(queueMessage.jobId);
      if (jobContext) {
        jobContext.status = 'failed';
        jobContext.progress = 0;
        jobContext.contextSnapshot = {
          ...jobContext.contextSnapshot,
          error: error instanceof Error ? error.message : 'Unknown error',
          failedAt: new Date().toISOString(),
        };
        jobContext.lastUpdate = Date.now();

        await redisMemory.storeJobContext(queueMessage.jobId, jobContext);
      }

      throw error;
    }
  }

  /**
   * Handle job failure and retry logic
   */
  private async handleJobFailure(message: Message, error: any): Promise<void> {
    if (!message.Body) return;

    const queueMessage: QueueMessage = JSON.parse(message.Body);

    if (queueMessage.retryCount < this.maxRetries) {
      // Increment retry count and re-queue
      queueMessage.retryCount += 1;

      console.log(`🔄 Retrying job ${queueMessage.jobId} (attempt ${queueMessage.retryCount}/${this.maxRetries})`);

      await this.sendJob({
        ...queueMessage,
        queuedAt: new Date().toISOString(),
      });
    } else {
      // Max retries exceeded, move to DLQ (handled by SQS redrive policy)
      console.error(`💀 Job ${queueMessage.jobId} failed permanently after ${this.maxRetries} attempts`);

      // Update job status to failed
      const jobContext = await redisMemory.getJobContext(queueMessage.jobId);
      if (jobContext) {
        jobContext.status = 'failed';
        jobContext.contextSnapshot = {
          ...jobContext.contextSnapshot,
          error: `Failed after ${this.maxRetries} attempts: ${error.message}`,
          finalFailureAt: new Date().toISOString(),
        };
        jobContext.lastUpdate = Date.now();

        await redisMemory.storeJobContext(queueMessage.jobId, jobContext);
      }
    }

    // Always delete the message from the main queue after processing
    if (message.ReceiptHandle) {
      await this.deleteMessage(message.ReceiptHandle);
    }
  }

  /**
   * Delete a message from the SQS queue
   */
  private async deleteMessage(receiptHandle: string): Promise<void> {
    const command = new DeleteMessageCommand({
      QueueUrl: this.queueUrl,
      ReceiptHandle: receiptHandle,
    });

    await this.sqsClient.send(command);
  }

  /**
   * Start the worker loop
   */
  startWorkerLoop(pollInterval: number = 5000): void {
    console.log('🚀 Starting SQS job queue worker loop');

    const poll = async () => {
      try {
        await this.pollAndProcessJobs();
      } catch (error) {
        console.error('Worker loop error:', error);
      }

      // Schedule next poll
      setTimeout(poll, pollInterval);
    };

    // Start polling
    poll();
  }

  /**
   * Stop the worker loop
   */
  stopWorkerLoop(): void {
    this.isProcessing = false;
    console.log('🛑 SQS job queue worker loop stopped');
  }

  /**
   * Get queue statistics
   */
  async getQueueStats(): Promise<{
    approximateNumberOfMessages: number;
    approximateNumberOfMessagesNotVisible: number;
  }> {
    // This would require additional SQS API calls to get queue attributes
    // For now, return placeholder
    return {
      approximateNumberOfMessages: 0,
      approximateNumberOfMessagesNotVisible: 0,
    };
  }

  /**
   * Health check for SQS connectivity
   */
  async healthCheck(): Promise<boolean> {
    try {
      // Try to get queue attributes
      const stats = await this.getQueueStats();
      return true;
    } catch (error) {
      console.error('SQS health check failed:', error);
      return false;
    }
  }
}

// Export singleton instance
export const sqsJobQueue = new SQSJobQueueService();

// Export types
export type { QueueJob, QueueMessage };

