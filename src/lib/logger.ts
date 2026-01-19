import * as Sentry from '@sentry/nextjs'

// Production Logger for Raptorflow
// Centralized logging with structured data and monitoring

export enum LogLevel {
  ERROR = 'error',
  WARN = 'warn',
  INFO = 'info',
  DEBUG = 'debug'
}

export enum LogCategory {
  AUTH = 'auth',
  API = 'api',
  DATABASE = 'database',
  EMAIL = 'email',
  SECURITY = 'security',
  PERFORMANCE = 'performance',
  SYSTEM = 'system'
}

interface LogEntry {
  timestamp: string;
  level: LogLevel;
  category: LogCategory;
  message: string;
  metadata?: Record<string, any>;
  userId?: string;
  requestId?: string;
  ip?: string;
  userAgent?: string;
  stack?: string;
}

interface MonitoringMetrics {
  errorCount: number;
  warningCount: number;
  requestCount: number;
  authFailures: number;
  emailFailures: number;
  databaseErrors: number;
  lastError?: string;
  lastWarning?: string;
}

class Logger {
  private isProduction: boolean;
  private metrics: MonitoringMetrics;
  private logBuffer: LogEntry[] = [];
  private maxBufferSize = 1000;

  constructor() {
    this.isProduction = process.env.NODE_ENV === 'production';
    this.metrics = {
      errorCount: 0,
      warningCount: 0,
      requestCount: 0,
      authFailures: 0,
      emailFailures: 0,
      databaseErrors: 0
    };
  }

  /**
   * Log an error message
   */
  error(message: string, metadata?: Record<string, any>, category: LogCategory = LogCategory.SYSTEM): void {
    this.log(LogLevel.ERROR, message, metadata, category);
  }

  /**
   * Log a warning message
   */
  warn(message: string, metadata?: Record<string, any>, category: LogCategory = LogCategory.SYSTEM): void {
    this.log(LogLevel.WARN, message, metadata, category);
  }

  /**
   * Log an info message
   */
  info(message: string, metadata?: Record<string, any>, category: LogCategory = LogCategory.SYSTEM): void {
    this.log(LogLevel.INFO, message, metadata, category);
  }

  /**
   * Log a debug message (only in development)
   */
  debug(message: string, metadata?: Record<string, any>, category: LogCategory = LogCategory.SYSTEM): void {
    if (!this.isProduction) {
      this.log(LogLevel.DEBUG, message, metadata, category);
    }
  }

  /**
   * Log an authentication event
   */
  auth(message: string, metadata?: Record<string, any>): void {
    this.log(LogLevel.INFO, message, metadata, LogCategory.AUTH);
  }

  /**
   * Log an API event
   */
  api(message: string, metadata?: Record<string, any>): void {
    this.log(LogLevel.INFO, message, metadata, LogCategory.API);
  }

  /**
   * Log a database event
   */
  database(message: string, metadata?: Record<string, any>): void {
    this.log(LogLevel.INFO, message, metadata, LogCategory.DATABASE);
  }

  /**
   * Log an email event
   */
  email(message: string, metadata?: Record<string, any>): void {
    this.log(LogLevel.INFO, message, metadata, LogCategory.EMAIL);
  }

  /**
   * Log a security event
   */
  security(message: string, metadata?: Record<string, any>): void {
    this.log(LogLevel.WARN, message, metadata, LogCategory.SECURITY);
  }

  /**
   * Log a performance event
   */
  performance(message: string, metadata?: Record<string, any>): void {
    this.log(LogLevel.INFO, message, metadata, LogCategory.PERFORMANCE);
  }

  /**
   * Core logging method
   */
  private log(level: LogLevel, message: string, metadata?: Record<string, any>, category: LogCategory = LogCategory.SYSTEM): void {
    const logEntry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      category,
      message,
      metadata,
      stack: level === LogLevel.ERROR ? new Error().stack : undefined
    };

    // Update metrics
    this.updateMetrics(level, category);

    // Add to buffer
    this.addToBuffer(logEntry);

    // Output based on environment
    if (this.isProduction) {
      this.logProduction(logEntry);
    } else {
      this.logDevelopment(logEntry);
    }
  }

  /**
   * Update monitoring metrics
   */
  private updateMetrics(level: LogLevel, category: LogCategory): void {
    switch (level) {
      case LogLevel.ERROR:
        this.metrics.errorCount++;
        this.metrics.lastError = `${category}: ${this.metrics.errorCount}`;
        break;
      case LogLevel.WARN:
        this.metrics.warningCount++;
        this.metrics.lastWarning = `${category}: ${this.metrics.warningCount}`;
        break;
    }

    switch (category) {
      case LogCategory.AUTH:
        if (level === LogLevel.ERROR) this.metrics.authFailures++;
        break;
      case LogCategory.EMAIL:
        if (level === LogLevel.ERROR) this.metrics.emailFailures++;
        break;
      case LogCategory.DATABASE:
        if (level === LogLevel.ERROR) this.metrics.databaseErrors++;
        break;
      case LogCategory.API:
        this.metrics.requestCount++;
        break;
    }
  }

  /**
   * Add entry to buffer
   */
  private addToBuffer(entry: LogEntry): void {
    this.logBuffer.push(entry);
    
    // Maintain buffer size
    if (this.logBuffer.length > this.maxBufferSize) {
      this.logBuffer = this.logBuffer.slice(-this.maxBufferSize);
    }
  }

  /**
   * Production logging
   */
  private logProduction(entry: LogEntry): void {
    // In production, only log errors and warnings
    if (entry.level === LogLevel.ERROR || entry.level === LogLevel.WARN) {
      console.error(JSON.stringify({
        timestamp: entry.timestamp,
        level: entry.level,
        category: entry.category,
        message: entry.message,
        metadata: entry.metadata
      }));

      // Send to external monitoring service (Sentry, etc.)
      this.sendToMonitoring(entry);
    }
  }

  /**
   * Development logging
   */
  private logDevelopment(entry: LogEntry): void {
    const color = this.getColor(entry.level);
    const prefix = `[${entry.timestamp}] [${entry.level.toUpperCase()}] [${entry.category.toUpperCase()}]`;
    
    console.log(color, prefix, entry.message);
    
    if (entry.metadata) {
      console.log(color, 'Metadata:', JSON.stringify(entry.metadata, null, 2));
    }
    
    if (entry.stack) {
      console.log(color, 'Stack:', entry.stack);
    }
  }

  /**
   * Get color for console output
   */
  private getColor(level: LogLevel): string {
    switch (level) {
      case LogLevel.ERROR:
        return '\x1b[31m'; // Red
      case LogLevel.WARN:
        return '\x1b[33m'; // Yellow
      case LogLevel.INFO:
        return '\x1b[36m'; // Blue
      case LogLevel.DEBUG:
        return '\x1b[37m'; // White
      default:
        return '\x1b[0m'; // Reset
    }
  }

  /**
   * Send to external monitoring service
   */
  private sendToMonitoring(entry: LogEntry): void {
    // Send to Sentry if configured
    if (process.env.SENTRY_DSN && entry.level === LogLevel.ERROR) {
      try {
        // This integrates with Sentry
        Sentry.captureException(new Error(entry.message), {
          tags: { category: entry.category },
          extra: entry.metadata
        });
      } catch (error) {
        console.error('Failed to send to Sentry:', error);
      }
    }

    // Send to custom monitoring service
    if (process.env.MONITORING_WEBHOOK) {
      try {
        fetch(process.env.MONITORING_WEBHOOK, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(entry)
        }).catch(error => {
          console.error('Failed to send to monitoring webhook:', error);
        });
      } catch (error) {
        console.error('Failed to send to monitoring webhook:', error);
      }
    }
  }

  /**
   * Get current metrics
   */
  getMetrics(): MonitoringMetrics {
    return { ...this.metrics };
  }

  /**
   * Get recent logs
   */
  getRecentLogs(count: number = 100): LogEntry[] {
    return this.logBuffer.slice(-count);
  }

  /**
   * Clear metrics
   */
  clearMetrics(): void {
    this.metrics = {
      errorCount: 0,
      warningCount: 0,
      requestCount: 0,
      authFailures: 0,
      emailFailures: 0,
      databaseErrors: 0
    };
  }

  /**
   * Create request context logger
   */
  createContext(requestId: string, userId?: string, ip?: string, userAgent?: string) {
    return {
      error: (message: string, metadata?: Record<string, any>) => {
        this.error(message, {
          ...metadata,
          requestId,
          userId,
          ip,
          userAgent
        });
      },
      warn: (message: string, metadata?: Record<string, any>) => {
        this.warn(message, {
          ...metadata,
          requestId,
          userId,
          ip,
          userAgent
        });
      },
      info: (message: string, metadata?: Record<string, any>) => {
        this.info(message, {
          ...metadata,
          requestId,
          userId,
          ip,
          userAgent
        });
      },
      debug: (message: string, metadata?: Record<string, any>) => {
        this.debug(message, {
          ...metadata,
          requestId,
          userId,
          ip,
          userAgent
        });
      }
    };
  }
}

// Export singleton instance
export const logger = new Logger();

// Export convenience functions
export const logError = (message: string, metadata?: Record<string, any>, category?: LogCategory) => {
  logger.error(message, metadata, category);
};

export const logWarn = (message: string, metadata?: Record<string, any>, category?: LogCategory) => {
  logger.warn(message, metadata, category);
};

export const logInfo = (message: string, metadata?: Record<string, any>, category?: LogCategory) => {
  logger.info(message, metadata, category);
};

export const logDebug = (message: string, metadata?: Record<string, any>, category?: LogCategory) => {
  logger.debug(message, metadata, category);
};

export const logAuth = (message: string, metadata?: Record<string, any>) => {
  logger.auth(message, metadata);
};

export const logApi = (message: string, metadata?: Record<string, any>) => {
  logger.api(message, metadata);
};

export const logDatabase = (message: string, metadata?: Record<string, any>) => {
  logger.database(message, metadata);
};

export const logEmail = (message: string, metadata?: Record<string, any>) => {
  logger.email(message, metadata);
};

export const logSecurity = (message: string, metadata?: Record<string, any>) => {
  logger.security(message, metadata);
};

export const logPerformance = (message: string, metadata?: Record<string, any>) => {
  logger.performance(message, metadata);
};
