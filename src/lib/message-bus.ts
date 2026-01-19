import { redisClient } from './redis-client';

/**
 * Global Message Bus for Real-time State Sync
 * Uses Redis Pub/Sub (simulated via polling or EventSource for Upstash)
 */
export const messageBus = {
  /**
   * Publish a message to a channel
   */
  async publish(channel: string, data: any) {
    const payload = {
      channel,
      data,
      timestamp: Date.now()
    };
    
    // Standard Redis publish
    await redisClient.set(`bus:${channel}`, JSON.stringify(payload), { ex: 60 });
    console.log(`📢 Bus Publish [${channel}]`, data);
  },

  /**
   * Get latest message from a channel (for polling/SSE)
   */
  async getLatest(channel: string) {
    return await redisClient.getJSON(`bus:${channel}`);
  }
};
