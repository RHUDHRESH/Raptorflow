import { v4 as uuidv4 } from 'uuid';
import { getLangChainModelForAgent, getModelForAgent, logModelSelection } from '../../lib/llm';
import type { SwarmMessage, SwarmState, AgentRole, TaskPriority } from '../types/swarm';

/**
 * Base abstract class for all swarm agents
 * Provides standardized communication, memory management, and error handling
 */
export abstract class BaseSwarmAgent {
  protected readonly agentId: string;
  protected readonly role: AgentRole;
  protected model: any;
  protected memory: Map<string, any>;
  protected messageQueue: SwarmMessage[];

  constructor(role: AgentRole, agentName: string) {
    this.agentId = uuidv4();
    this.role = role;
    this.model = getLangChainModelForAgent(agentName);
    logModelSelection(agentName, 'medium', getModelForAgent(agentName));
    this.memory = new Map();
    this.messageQueue = [];
  }

  /**
   * Process incoming message and return response
   */
  abstract processMessage(message: SwarmMessage, state: SwarmState): Promise<SwarmMessage>;

  /**
   * Execute the agent's primary task
   */
  abstract executeTask(taskData: any, state: SwarmState): Promise<any>;

  /**
   * Standardized message creation
   */
  protected createMessage(
    content: any,
    recipientId: string,
    messageType: string,
    priority: TaskPriority = 'medium',
    requiresResponse: boolean = false
  ): SwarmMessage {
    return {
      id: uuidv4(),
      timestamp: new Date().toISOString(),
      senderId: this.agentId,
      senderRole: this.role,
      recipientId,
      messageType,
      content,
      priority,
      requiresResponse,
      status: 'pending'
    };
  }

  /**
   * Broadcast message to multiple recipients
   */
  protected broadcastMessage(
    content: any,
    recipientRoles: AgentRole[],
    messageType: string,
    priority: TaskPriority = 'medium'
  ): SwarmMessage[] {
    return recipientRoles.map(role => 
      this.createMessage(content, `role:${role}`, messageType, priority, false)
    );
  }

  /**
   * Store data in agent memory
   */
  protected storeMemory(key: string, data: any, ttl?: number): void {
    this.memory.set(key, {
      data,
      timestamp: Date.now(),
      ttl
    });
  }

  /**
   * Retrieve data from agent memory
   */
  protected retrieveMemory(key: string): any | null {
    const entry = this.memory.get(key);
    if (!entry) return null;
    
    // Check if entry has expired
    if (entry.ttl && Date.now() - entry.timestamp > entry.ttl) {
      this.memory.delete(key);
      return null;
    }
    
    return entry.data;
  }

  /**
   * Clear expired memory entries
   */
  protected cleanupMemory(): void {
    const now = Date.now();
    for (const [key, entry] of this.memory.entries()) {
      if (entry.ttl && now - entry.timestamp > entry.ttl) {
        this.memory.delete(key);
      }
    }
  }

  /**
   * Error handling with standardized error format
   */
  protected handleError(error: any, context: string): {
    success: false;
    error: string;
    details?: any;
    context: string;
  } {
    console.error(`[${this.role}] Error in ${context}:`, error);
    
    return {
      success: false,
      error: error.message || 'Unknown error occurred',
      details: error.stack || error,
      context
    };
  }

  /**
   * Success response format
   */
  protected createSuccessResponse(data: any, context: string): {
    success: true;
    data: any;
    context: string;
    timestamp: string;
  } {
    return {
      success: true,
      data,
      context,
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Validate incoming message format
   */
  protected validateMessage(message: SwarmMessage): boolean {
    return (
      message &&
      typeof message.id === 'string' &&
      typeof message.senderId === 'string' &&
      typeof message.recipientId === 'string' &&
      typeof message.content !== 'undefined'
    );
  }

  /**
   * Get agent capabilities and status
   */
  getAgentInfo(): {
    agentId: string;
    role: AgentRole;
    memorySize: number;
    queueLength: number;
    status: 'idle' | 'processing' | 'error';
  } {
    return {
      agentId: this.agentId,
      role: this.role,
      memorySize: this.memory.size,
      queueLength: this.messageQueue.length,
      status: this.messageQueue.length > 0 ? 'processing' : 'idle'
    };
  }

  /**
   * Queue management
   */
  protected addToQueue(message: SwarmMessage): void {
    this.messageQueue.push(message);
    // Sort by priority (high first, then medium, then low)
    this.messageQueue.sort((a, b) => {
      const priorityOrder = { high: 0, medium: 1, low: 2 };
      return priorityOrder[a.priority] - priorityOrder[b.priority];
    });
  }

  protected getNextMessage(): SwarmMessage | null {
    return this.messageQueue.shift() || null;
  }

  protected clearQueue(): void {
    this.messageQueue = [];
  }
}



