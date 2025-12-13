/**
 * Connector Interface
 *
 * Standardized interface for external service integrations.
 */

export interface ConnectorConfig {
  apiKey?: string;
  apiSecret?: string;
  accessToken?: string;
  refreshToken?: string;
  baseUrl?: string;
  timeout?: number;
  rateLimit?: {
    requests: number;
    period: number; // in milliseconds
  };
}

export interface ConnectorResult<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  metadata?: {
    requestId?: string;
    rateLimitRemaining?: number;
    rateLimitReset?: number;
    cost?: number;
  };
}

export abstract class BaseConnector {
  protected config: ConnectorConfig;

  constructor(config: ConnectorConfig) {
    this.config = config;
  }

  /**
   * Test connection to the service
   */
  abstract testConnection(): Promise<ConnectorResult<boolean>>;

  /**
   * Get connector metadata
   */
  abstract getMetadata(): {
    name: string;
    description: string;
    capabilities: string[];
    rateLimits: {
      requests: number;
      period: number;
    };
    costPerRequest?: number;
  };

  /**
   * Update configuration
   */
  updateConfig(config: Partial<ConnectorConfig>): void {
    this.config = { ...this.config, ...config };
  }
}

// Export types
export type { ConnectorConfig, ConnectorResult };

