import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { Move, MoveStatus, MoveExecution, MoveConfig, MoveType } from '@/types/campaign';
import { useEnhancedCampaignStore } from './enhancedCampaignStore';

// Execution queue item
interface QueueItem {
  id: string;
  moveId: string;
  campaignId: string;
  scheduledAt: Date;
  priority: 'low' | 'normal' | 'high';
  retryCount: number;
  maxRetries: number;
}

// Execution log entry
interface ExecutionLog {
  id: string;
  moveId: string;
  timestamp: Date;
  level: 'info' | 'warn' | 'error';
  message: string;
  metadata?: Record<string, any>;
}

// Execution result
interface ExecutionResult {
  success: boolean;
  metrics?: Record<string, number>;
  artifacts?: string[];
  errors?: string[];
  nextRun?: Date;
}

// Execution engine state
interface ExecutionEngineState {
  // Queue management
  queue: QueueItem[];
  processing: boolean;
  currentExecution: string | null;

  // Execution history
  logs: ExecutionLog[];
  history: Record<string, ExecutionResult>;

  // Settings
  maxConcurrent: number;
  retryDelay: number;
  autoRetry: boolean;

  // Actions
  enqueueMove: (move: Move, campaignId: string, scheduledAt?: Date) => void;
  dequeueMove: (moveId: string) => void;
  processQueue: () => Promise<void>;
  executeMove: (move: Move) => Promise<ExecutionResult>;
  pauseQueue: () => void;
  resumeQueue: () => void;
  clearQueue: () => void;

  // Monitoring
  getQueueStatus: () => {
    pending: number;
    processing: number;
    completed: number;
    failed: number;
  };
  getMoveLogs: (moveId: string) => ExecutionLog[];
  getMoveHistory: (moveId: string) => ExecutionResult | null;
}

// Create execution engine store
export const useExecutionEngine = create<ExecutionEngineState>()(
  subscribeWithSelector(
    (set, get) => ({
      // Initial state
      queue: [],
      processing: false,
      currentExecution: null,
      logs: [],
      history: {},
      maxConcurrent: 5,
      retryDelay: 5000, // 5 seconds
      autoRetry: true,

      // Enqueue a move for execution
      enqueueMove: (move, campaignId, scheduledAt = new Date()) => {
        const queueItem: QueueItem = {
          id: `queue-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          moveId: move.id,
          campaignId,
          scheduledAt,
          priority: 'normal',
          retryCount: 0,
          maxRetries: 3
        };

        set(state => ({
          queue: [...state.queue, queueItem].sort((a, b) =>
            a.scheduledAt.getTime() - b.scheduledAt.getTime()
          )
        }));

        // Log enqueue
        set(state => ({
          logs: [...state.logs, {
            id: `log-${Date.now()}`,
            moveId: move.id,
            timestamp: new Date(),
            level: 'info',
            message: `Move enqueued for execution at ${scheduledAt.toISOString()}`
          }]
        }));
      },

      // Dequeue a move
      dequeueMove: (moveId) => {
        set(state => ({
          queue: state.queue.filter(item => item.moveId !== moveId)
        }));
      },

      // Process the execution queue
      processQueue: async () => {
        const state = get();
        if (state.processing || state.queue.length === 0) return;

        set({ processing: true });

        try {
          while (get().queue.length > 0 && get().processing) {
            const now = new Date();
            const readyItems = get().queue.filter(item =>
              item.scheduledAt <= now
            );

            if (readyItems.length === 0) {
              // Wait for next scheduled item
              const nextItem = get().queue[0];
              if (nextItem) {
                const delay = nextItem.scheduledAt.getTime() - now.getTime();
                await new Promise(resolve => setTimeout(resolve, Math.min(delay, 60000)));
              }
              continue;
            }

            // Process up to maxConcurrent items
            const batch = readyItems.slice(0, get().maxConcurrent);

            await Promise.all(
              batch.map(async (queueItem) => {
                // Get move from campaign store
                const campaigns = useEnhancedCampaignStore.getState().campaigns;
                const campaign = campaigns[queueItem.campaignId];
                const moves = useEnhancedCampaignStore.getState().moves;
                const move = moves[queueItem.moveId];

                if (!move || !campaign) {
                  // Remove invalid queue item
                  get().dequeueMove(queueItem.moveId);
                  return;
                }

                set({ currentExecution: queueItem.moveId });

                try {
                  // Execute the move
                  const result = await get().executeMove(move);

                  // Store result
                  set(state => ({
                    history: {
                      ...state.history,
                      [move.id]: result
                    }
                  }));

                  // Remove from queue
                  get().dequeueMove(queueItem.moveId);

                  // Update move status
                  await useEnhancedCampaignStore.getState().updateMove(move.id, {
                    status: result.success ? MoveStatus.COMPLETED : MoveStatus.FAILED,
                    execution: {
                      ...move.execution,
                      completedAt: new Date(),
                      lastResult: result
                    }
                  });

                  // Log completion
                  set(state => ({
                    logs: [...state.logs, {
                      id: `log-${Date.now()}`,
                      moveId: move.id,
                      timestamp: new Date(),
                      level: result.success ? 'info' : 'error',
                      message: result.success
                        ? 'Move executed successfully'
                        : `Move execution failed: ${result.errors?.join(', ')}`,
                      metadata: result.metrics
                    }]
                  }));

                } catch (error) {
                  // Handle execution error
                  const shouldRetry = get().autoRetry && queueItem.retryCount < queueItem.maxRetries;

                  if (shouldRetry) {
                    // Retry with delay
                    const retryItem = {
                      ...queueItem,
                      scheduledAt: new Date(Date.now() + get().retryDelay),
                      retryCount: queueItem.retryCount + 1
                    };

                    set(state => ({
                      queue: [...state.queue.filter(item => item.id !== queueItem.id), retryItem]
                    }));

                    // Log retry
                    set(state => ({
                      logs: [...state.logs, {
                        id: `log-${Date.now()}`,
                        moveId: move.id,
                        timestamp: new Date(),
                        level: 'warn',
                        message: `Move execution failed, retrying (${retryItem.retryCount}/${queueItem.maxRetries})`,
                        metadata: { error: error instanceof Error ? error.message : 'Unknown error' }
                      }]
                    }));
                  } else {
                    // Mark as failed
                    get().dequeueMove(queueItem.moveId);

                    await useEnhancedCampaignStore.getState().updateMove(move.id, {
                      status: MoveStatus.FAILED,
                      execution: {
                        ...move.execution,
                        completedAt: new Date(),
                        lastError: error instanceof Error ? error.message : 'Unknown error'
                      }
                    });

                    // Log failure
                    set(state => ({
                      logs: [...state.logs, {
                        id: `log-${Date.now()}`,
                        moveId: move.id,
                        timestamp: new Date(),
                        level: 'error',
                        message: `Move execution failed permanently`,
                        metadata: { error: error instanceof Error ? error.message : 'Unknown error' }
                      }]
                    }));
                  }
                } finally {
                  set({ currentExecution: null });
                }
              })
            );
          }
        } finally {
          set({ processing: false });
        }
      },

      // Execute a single move
      executeMove: async (move): Promise<ExecutionResult> => {
        // Update move status to running
        await useEnhancedCampaignStore.getState().updateMove(move.id, {
          status: MoveStatus.RUNNING,
          execution: {
            ...move.execution,
            startedAt: new Date(),
            attempts: move.execution.attempts + 1
          }
        });

        // Simulate execution based on move type
        await new Promise(resolve => setTimeout(resolve, 2000 + Math.random() * 3000));

        // Mock execution results based on move type
        const mockResults: Record<string, ExecutionResult> = {
          [MoveType.EMAIL]: {
            success: Math.random() > 0.1, // 90% success rate
            metrics: {
              sent: 1000,
              delivered: 950,
              opened: 400,
              clicked: 80,
              bounced: 50
            }
          },
          [MoveType.SOCIAL_MEDIA]: {
            success: Math.random() > 0.05, // 95% success rate
            metrics: {
              posts: 3,
              reach: 5000,
              engagement: 250,
              shares: 50
            }
          },
          [MoveType.CONTENT]: {
            success: Math.random() > 0.15, // 85% success rate
            metrics: {
              articles: 1,
              views: 2000,
              readTime: 300,
              shares: 100
            }
          },
          [MoveType.OUTREACH]: {
            success: Math.random() > 0.2, // 80% success rate
            metrics: {
              sent: 100,
              replies: 20,
              meetings: 5,
              conversion: 0.05
            }
          },
          [MoveType.ADS]: {
            success: Math.random() > 0.05, // 95% success rate
            metrics: {
              impressions: 10000,
              clicks: 100,
              conversions: 10,
              cost: 500
            }
          }
        };

        const result = mockResults[move.type] || {
          success: Math.random() > 0.1,
          metrics: {
            executions: 1
          }
        };

        // Add artifacts for some move types
        if (move.type === MoveType.CONTENT || move.type === MoveType.EMAIL) {
          result.artifacts = [
            `artifact-${move.id}-1`,
            `artifact-${move.id}-2`
          ];
        }

        // Schedule next run if applicable
        if (move.config.schedule?.frequency && result.success) {
          const frequencies: Record<string, number> = {
            'daily': 24 * 60 * 60 * 1000,
            'weekly': 7 * 24 * 60 * 60 * 1000,
            'monthly': 30 * 24 * 60 * 60 * 1000
          };

          const delay = frequencies[move.config.schedule.frequency];
          if (delay) {
            result.nextRun = new Date(Date.now() + delay);
          }
        }

        return result;
      },

      // Pause queue processing
      pauseQueue: () => {
        set({ processing: false });
      },

      // Resume queue processing
      resumeQueue: () => {
        const state = get();
        if (!state.processing && state.queue.length > 0) {
          state.processQueue();
        }
      },

      // Clear all items from queue
      clearQueue: () => {
        set({ queue: [] });
      },

      // Get queue status
      getQueueStatus: () => {
        const state = get();
        const campaigns = useEnhancedCampaignStore.getState().campaigns;
        const moves = useEnhancedCampaignStore.getState().moves;

        let pending = 0;
        let processing = 0;
        let completed = 0;
        let failed = 0;

        // Count queue items
        state.queue.forEach(item => {
          if (item.scheduledAt > new Date()) {
            pending++;
          } else {
            processing++;
          }
        });

        // Count move statuses
        Object.values(moves).forEach(move => {
          switch (move.status) {
            case MoveStatus.COMPLETED:
              completed++;
              break;
            case MoveStatus.FAILED:
              failed++;
              break;
          }
        });

        return { pending, processing, completed, failed };
      },

      // Get logs for a specific move
      getMoveLogs: (moveId) => {
        return get().logs.filter(log => log.moveId === moveId);
      },

      // Get execution history for a specific move
      getMoveHistory: (moveId) => {
        return get().history[moveId] || null;
      }
    }),
    {
      name: 'execution-engine'
    }
  )
);

// Start the execution engine when the module loads
let engineInterval: NodeJS.Timeout | null = null;

export const startExecutionEngine = () => {
  if (engineInterval) return;

  // Process queue every 30 seconds
  engineInterval = setInterval(() => {
    useExecutionEngine.getState().processQueue();
  }, 30000);

  // Initial process
  useExecutionEngine.getState().processQueue();
};

export const stopExecutionEngine = () => {
  if (engineInterval) {
    clearInterval(engineInterval);
    engineInterval = null;
  }
};

// Auto-start on module load
if (typeof window !== 'undefined') {
  startExecutionEngine();
}

// Export utilities
export const scheduleMove = (move: Move, campaignId: string, delay: number = 0) => {
  const scheduledAt = new Date(Date.now() + delay);
  useExecutionEngine.getState().enqueueMove(move, campaignId, scheduledAt);
};

export const scheduleRecurringMove = (
  move: Move,
  campaignId: string,
  frequency: 'daily' | 'weekly' | 'monthly',
  count?: number
) => {
  const frequencies = {
    daily: 24 * 60 * 60 * 1000,
    weekly: 7 * 24 * 60 * 60 * 1000,
    monthly: 30 * 24 * 60 * 60 * 1000
  };

  const delay = frequencies[frequency];
  const iterations = count || 10; // Default to 10 iterations

  for (let i = 0; i < iterations; i++) {
    const scheduledAt = new Date(Date.now() + (delay * i));
    useExecutionEngine.getState().enqueueMove(move, campaignId, scheduledAt);
  }
};
