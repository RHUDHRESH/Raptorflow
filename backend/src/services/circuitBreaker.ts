/**
 * Circuit Breaker Service
 * Prevents cascading failures by failing fast when external services are down.
 */

export type CircuitState = 'CLOSED' | 'OPEN' | 'HALF_OPEN';

export interface CircuitBreakerOptions {
  failureThreshold: number;      // Number of failures before opening
  resetTimeout: number;          // Time in ms before attempting reset
  halfOpenMaxAttempts: number;   // Max attempts in half-open state
  monitorInterval?: number;      // Interval to check state
}

export interface CircuitBreakerStats {
  state: CircuitState;
  failures: number;
  successes: number;
  lastFailure: Date | null;
  lastSuccess: Date | null;
  totalRequests: number;
  failureRate: number;
}

class CircuitBreaker {
  private state: CircuitState = 'CLOSED';
  private failures = 0;
  private successes = 0;
  private lastFailure: Date | null = null;
  private lastSuccess: Date | null = null;
  private nextAttempt: Date | null = null;
  private halfOpenAttempts = 0;
  private totalRequests = 0;

  constructor(
    private readonly name: string,
    private readonly options: CircuitBreakerOptions
  ) {
    console.log(`🔌 Circuit breaker "${name}" initialized (threshold: ${options.failureThreshold})`);
  }

  /**
   * Execute a function with circuit breaker protection
   */
  async execute<T>(fn: () => Promise<T>, fallback?: () => Promise<T>): Promise<T> {
    this.totalRequests++;

    // Check if circuit is open
    if (this.state === 'OPEN') {
      if (this.nextAttempt && new Date() < this.nextAttempt) {
        console.warn(`⚡ Circuit "${this.name}" is OPEN - fast failing`);
        if (fallback) {
          return fallback();
        }
        throw new CircuitBreakerError(`Circuit "${this.name}" is open`, this.getStats());
      }
      // Time to try again - move to half-open
      this.state = 'HALF_OPEN';
      this.halfOpenAttempts = 0;
      console.log(`🔄 Circuit "${this.name}" moving to HALF_OPEN`);
    }

    // Check half-open limits
    if (this.state === 'HALF_OPEN' && this.halfOpenAttempts >= this.options.halfOpenMaxAttempts) {
      console.warn(`⚡ Circuit "${this.name}" HALF_OPEN limit reached - fast failing`);
      if (fallback) {
        return fallback();
      }
      throw new CircuitBreakerError(`Circuit "${this.name}" half-open limit reached`, this.getStats());
    }

    try {
      if (this.state === 'HALF_OPEN') {
        this.halfOpenAttempts++;
      }

      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure(error);
      if (fallback) {
        console.log(`🔄 Circuit "${this.name}" using fallback`);
        return fallback();
      }
      throw error;
    }
  }

  /**
   * Record a successful call
   */
  private onSuccess(): void {
    this.successes++;
    this.lastSuccess = new Date();

    if (this.state === 'HALF_OPEN') {
      // Success in half-open state - close the circuit
      this.state = 'CLOSED';
      this.failures = 0;
      console.log(`✅ Circuit "${this.name}" CLOSED after successful recovery`);
    }
  }

  /**
   * Record a failed call
   */
  private onFailure(error: unknown): void {
    this.failures++;
    this.lastFailure = new Date();

    console.error(`❌ Circuit "${this.name}" failure #${this.failures}:`, error);

    if (this.state === 'HALF_OPEN') {
      // Failure in half-open - open the circuit again
      this.openCircuit();
    } else if (this.failures >= this.options.failureThreshold) {
      // Too many failures - open the circuit
      this.openCircuit();
    }
  }

  /**
   * Open the circuit
   */
  private openCircuit(): void {
    this.state = 'OPEN';
    this.nextAttempt = new Date(Date.now() + this.options.resetTimeout);
    console.warn(`🚫 Circuit "${this.name}" OPENED - will retry at ${this.nextAttempt.toISOString()}`);
  }

  /**
   * Get current statistics
   */
  getStats(): CircuitBreakerStats {
    return {
      state: this.state,
      failures: this.failures,
      successes: this.successes,
      lastFailure: this.lastFailure,
      lastSuccess: this.lastSuccess,
      totalRequests: this.totalRequests,
      failureRate: this.totalRequests > 0 ? this.failures / this.totalRequests : 0,
    };
  }

  /**
   * Force reset the circuit breaker
   */
  reset(): void {
    this.state = 'CLOSED';
    this.failures = 0;
    this.successes = 0;
    this.halfOpenAttempts = 0;
    this.nextAttempt = null;
    console.log(`🔄 Circuit "${this.name}" manually reset`);
  }

  /**
   * Check if circuit allows requests
   */
  isAllowed(): boolean {
    if (this.state === 'CLOSED') return true;
    if (this.state === 'HALF_OPEN') return this.halfOpenAttempts < this.options.halfOpenMaxAttempts;
    if (this.state === 'OPEN' && this.nextAttempt && new Date() >= this.nextAttempt) return true;
    return false;
  }
}

/**
 * Custom error for circuit breaker failures
 */
export class CircuitBreakerError extends Error {
  constructor(
    message: string,
    public readonly stats: CircuitBreakerStats
  ) {
    super(message);
    this.name = 'CircuitBreakerError';
  }
}

// =====================================================
// PRE-CONFIGURED CIRCUIT BREAKERS
// =====================================================

/**
 * Circuit breaker for Vertex AI API calls
 */
export const vertexAICircuit = new CircuitBreaker('VertexAI', {
  failureThreshold: 5,        // Open after 5 failures
  resetTimeout: 30000,        // Wait 30 seconds before retry
  halfOpenMaxAttempts: 2,     // Allow 2 test requests in half-open
});

/**
 * Circuit breaker for Supabase API calls
 */
export const supabaseCircuit = new CircuitBreaker('Supabase', {
  failureThreshold: 3,        // Open after 3 failures
  resetTimeout: 15000,        // Wait 15 seconds before retry
  halfOpenMaxAttempts: 1,     // Allow 1 test request in half-open
});

/**
 * Circuit breaker for external API calls (scraping, enrichment)
 */
export const externalAPICircuit = new CircuitBreaker('ExternalAPI', {
  failureThreshold: 10,       // Open after 10 failures (more lenient)
  resetTimeout: 60000,        // Wait 60 seconds before retry
  halfOpenMaxAttempts: 3,     // Allow 3 test requests in half-open
});

/**
 * Circuit breaker for PhonePe payment API
 */
export const phonepeCircuit = new CircuitBreaker('PhonePe', {
  failureThreshold: 3,        // Open after 3 failures (critical)
  resetTimeout: 20000,        // Wait 20 seconds before retry
  halfOpenMaxAttempts: 1,     // Allow 1 test request in half-open
});

// Export factory for custom circuit breakers
export { CircuitBreaker };
