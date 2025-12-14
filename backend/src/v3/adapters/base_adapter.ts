/**
 * Base Adapter Interface
 *
 * Defines the contract for V1 and V2 system adapters
 */

import { UnifiedRequest, UnifiedResponse, RoutingDecision, AgentCapabilities } from '../types';

// =====================================================
// BASE ADAPTER INTERFACE
// =====================================================

export interface AgentAdapter {
  /**
   * Execute a unified request
   */
  execute(request: UnifiedRequest, routing?: RoutingDecision): Promise<UnifiedResponse>;

  /**
   * Get list of available agents in this system
   */
  getAvailableAgents(): string[];

  /**
   * Get detailed capabilities of all agents
   */
  getCapabilities(): Promise<AgentCapabilities[]>;

  /**
   * Get health status of the adapter and its agents
   */
  getHealth(): Promise<{
    status: 'healthy' | 'degraded' | 'unhealthy';
    agents: number;
    message?: string;
  }>;

  /**
   * Check if adapter can handle specific agents
   */
  canHandleAgents(agentNames: string[]): boolean;

  /**
   * Get execution status for a specific execution
   */
  getExecutionStatus?(executionId: string): Promise<any>;
}

// =====================================================
// ADAPTER REGISTRY
// =====================================================

export class AdapterRegistry {
  private adapters: Map<string, AgentAdapter> = new Map();

  registerAdapter(system: string, adapter: AgentAdapter): void {
    this.adapters.set(system, adapter);
  }

  getAdapter(system: string): AgentAdapter | undefined {
    return this.adapters.get(system);
  }

  getAllAdapters(): AgentAdapter[] {
    return Array.from(this.adapters.values());
  }

  canHandleAgent(system: string, agentName: string): boolean {
    const adapter = this.adapters.get(system);
    return adapter ? adapter.canHandleAgents([agentName]) : false;
  }
}

// Singleton registry
export const adapterRegistry = new AdapterRegistry();


