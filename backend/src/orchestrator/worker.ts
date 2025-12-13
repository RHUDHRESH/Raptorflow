#!/usr/bin/env node

/**
 * Orchestrator Worker
 *
 * Processes jobs from the SQS queue asynchronously.
 * Run this separately from the main server.
 */

import { sqsJobQueue } from '../services/sqsJobQueue';
import { env } from '../config/env';

// Graceful shutdown handling
let isShuttingDown = false;

process.on('SIGTERM', () => {
  console.log('🛑 SIGTERM received, initiating graceful shutdown...');
  isShuttingDown = true;
  sqsJobQueue.stopWorkerLoop();
});

process.on('SIGINT', () => {
  console.log('🛑 SIGINT received, initiating graceful shutdown...');
  isShuttingDown = true;
  sqsJobQueue.stopWorkerLoop();
});

// Health check function
async function healthCheck(): Promise<void> {
  const sqsHealth = await sqsJobQueue.healthCheck();
  console.log(`🔍 Health Check - SQS: ${sqsHealth ? '✅' : '❌'}`);

  if (!sqsHealth) {
    console.error('❌ Health check failed, exiting...');
    process.exit(1);
  }
}

// Main worker function
export async function startWorker(): Promise<void> {
  console.log('🚀 Starting Orchestrator Worker');
  console.log(`📍 Environment: ${env.NODE_ENV}`);
  console.log(`🔗 SQS Queue: ${env.SQS_QUEUE_URL || 'Not configured'}`);

  // Initial health check
  await healthCheck();

  // Start the worker loop
  const pollInterval = parseInt(env.WORKER_POLL_INTERVAL || '5000');
  sqsJobQueue.startWorkerLoop(pollInterval);

  console.log(`⏰ Worker polling every ${pollInterval}ms`);
  console.log('✅ Orchestrator Worker is running');

  // Periodic health checks
  setInterval(async () => {
    if (!isShuttingDown) {
      await healthCheck();
    }
  }, 60000); // Every minute

  // Keep the process alive
  setInterval(() => {
    if (!isShuttingDown) {
      const stats = sqsJobQueue.getQueueStats();
      console.log(`📊 Queue Stats - Queued: ${stats.queued}, Active: ${stats.active}, Available: ${stats.availableCapacity}`);
    }
  }, 30000); // Every 30 seconds
}

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('💥 Uncaught Exception:', error);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('💥 Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

// When run directly (for testing), start the worker
if (require.main === module) {
  startWorker().catch((error) => {
    console.error('💥 Failed to start worker:', error);
    process.exit(1);
  });
}
