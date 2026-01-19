import { redisClient } from './redis-client';

export interface QueuedTask {
  id: string;
  type: string;
  payload: any;
  createdAt: number;
  priority: number;
}

const QUEUE_KEY = 'rf:task_queue';
const FAILED_QUEUE_KEY = 'rf:failed_tasks';

export const taskQueue = {
  /**
   * Push a new task to the queue
   */
  async push(type: string, payload: any, priority: number = 0): Promise<string> {
    const task: QueuedTask = {
      id: Math.random().toString(36).substring(2, 15),
      type,
      payload,
      createdAt: Date.now(),
      priority
    };

    await redisClient.lpush(QUEUE_KEY, JSON.stringify(task));
    console.log(`📡 Task queued: ${task.id} (${type})`);
    return task.id;
  },

  /**
   * Pop a task from the queue (Worker side)
   */
  async pop(): Promise<QueuedTask | null> {
    const data = await redisClient.rpop(QUEUE_KEY);
    if (!data) return null;
    return JSON.parse(data) as QueuedTask;
  },

  /**
   * Record a failed task for manual retry or audit
   */
  async recordFailure(task: QueuedTask, error: any) {
    const failureData = {
      task,
      error: error.message || error,
      failedAt: Date.now()
    };
    await redisClient.lpush(FAILED_QUEUE_KEY, JSON.stringify(failureData));
  },

  /**
   * Get queue depth
   */
  async getStatus() {
    const pending = await redisClient.llen(QUEUE_KEY);
    const failed = await redisClient.llen(FAILED_QUEUE_KEY);
    return { pending, failed };
  }
};
