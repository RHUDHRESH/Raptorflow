import { NextResponse } from 'next/server';
import { createServerSupabaseClient } from '@/lib/supabase/server';
import { logger } from '@/lib/logger';

interface HealthCheck {
  status: 'healthy' | 'unhealthy' | 'degraded';
  timestamp: string;
  uptime: number;
  version: string;
  environment: string;
  services: {
    database: ServiceStatus;
    email: ServiceStatus;
    storage: ServiceStatus;
    auth: ServiceStatus;
  };
  metrics: {
    errorCount: number;
    warningCount: number;
    requestCount: number;
    authFailures: number;
    emailFailures: number;
    databaseErrors: number;
  };
}

interface ServiceStatus {
  status: 'healthy' | 'unhealthy' | 'degraded';
  responseTime?: number;
  lastCheck: string;
  error?: string;
}

const startTime = Date.now();

export async function GET() {
  const healthCheck: HealthCheck = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: Date.now() - startTime,
    version: process.env.npm_package_version || '1.0.0',
    environment: process.env.NODE_ENV || 'development',
    services: {
      database: await checkDatabaseHealth(),
      email: await checkEmailHealth(),
      storage: await checkStorageHealth(),
      auth: await checkAuthHealth()
    },
    metrics: {
    errorCount: 0,
    warningCount: 0,
    requestCount: 0,
    authFailures: 0,
    emailFailures: 0,
    databaseErrors: 0
  }
  };

  // Determine overall health
  const unhealthyServices = Object.values(healthCheck.services).filter(s => s.status === 'unhealthy');
  const degradedServices = Object.values(healthCheck.services).filter(s => s.status === 'degraded');

  if (unhealthyServices.length > 0) {
    healthCheck.status = 'unhealthy';
  } else if (degradedServices.length > 0) {
    healthCheck.status = 'degraded';
  }

  // Log health check
  logger.info('Health check performed', {
    status: healthCheck.status,
    services: healthCheck.services,
    metrics: healthCheck.metrics
  });

  return NextResponse.json(healthCheck, {
    status: healthCheck.status === 'healthy' ? 200 : 503,
    headers: {
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0'
    }
  });
}

async function checkDatabaseHealth(): Promise<ServiceStatus> {
  const startTime = Date.now();
  
  try {
    const supabase = await createServerSupabaseClient();
    
    // Test basic database connection
    const { data, error } = await supabase
      .from('profiles')
      .select('count', { count: 'exact', head: true });

    if (error) {
      return {
        status: 'unhealthy',
        lastCheck: new Date().toISOString(),
        error: error.message
      };
    }

    // Test password reset tokens table
    const { error: tokenError } = await supabase
      .from('password_reset_tokens')
      .select('count', { count: 'exact', head: true });

    if (tokenError) {
      return {
        status: 'degraded',
        lastCheck: new Date().toISOString(),
        error: 'Password reset tokens table not accessible'
      };
    }

    return {
      status: 'healthy',
      responseTime: Date.now() - startTime,
      lastCheck: new Date().toISOString()
    };
  } catch (error) {
    return {
      status: 'unhealthy',
      lastCheck: new Date().toISOString(),
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
}

async function checkEmailHealth(): Promise<ServiceStatus> {
  const startTime = Date.now();
  
  try {
    // Check if Resend API key is configured
    if (!process.env.RESEND_API_KEY) {
      return {
        status: 'unhealthy',
        lastCheck: new Date().toISOString(),
        error: 'Resend API key not configured'
      };
    }

    // Test Resend API (lightweight check)
    const response = await fetch('https://api.resend.com/domains', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${process.env.RESEND_API_KEY}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      return {
        status: 'unhealthy',
        lastCheck: new Date().toISOString(),
        error: `Resend API error: ${response.status}`
      };
    }

    return {
      status: 'healthy',
      responseTime: Date.now() - startTime,
      lastCheck: new Date().toISOString()
    };
  } catch (error) {
    return {
      status: 'unhealthy',
      lastCheck: new Date().toISOString(),
      error: error instanceof Error ? error.message : 'Email service unavailable'
    };
  }
}

async function checkStorageHealth(): Promise<ServiceStatus> {
  const startTime = Date.now();
  
  try {
    // Check if storage is configured
    if (!process.env.NEXT_PUBLIC_SUPABASE_URL) {
      return {
        status: 'unhealthy',
        lastCheck: new Date().toISOString(),
        error: 'Storage URL not configured'
      };
    }

    // Test storage access
    const response = await fetch(`${process.env.NEXT_PUBLIC_SUPABASE_URL}/storage/v1/bucket`, {
      method: 'GET',
      headers: {
        'apikey': process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      return {
        status: 'degraded',
        lastCheck: new Date().toISOString(),
        error: `Storage API error: ${response.status}`
      };
    }

    return {
      status: 'healthy',
      responseTime: Date.now() - startTime,
      lastCheck: new Date().toISOString()
    };
  } catch (error) {
    return {
      status: 'unhealthy',
      lastCheck: new Date().toISOString(),
      error: error instanceof Error ? error.message : 'Storage service unavailable'
    };
  }
}

async function checkAuthHealth(): Promise<ServiceStatus> {
  const startTime = Date.now();
  
  try {
    // Check if auth configuration is complete
    const requiredVars = [
      'NEXT_PUBLIC_SUPABASE_URL',
      'NEXT_PUBLIC_SUPABASE_ANON_KEY',
      'SUPABASE_SERVICE_ROLE_KEY'
    ];

    const missingVars = requiredVars.filter(v => !process.env[v]);
    
    if (missingVars.length > 0) {
      return {
        status: 'unhealthy',
        lastCheck: new Date().toISOString(),
        error: `Missing environment variables: ${missingVars.join(', ')}`
      };
    }

    // Test auth service
    const supabase = await createServerSupabaseClient();
    const { data, error } = await supabase.auth.getSession();

    if (error && error.message !== 'Invalid session') {
      return {
        status: 'degraded',
        lastCheck: new Date().toISOString(),
        error: 'Auth service partially functional'
      };
    }

    return {
      status: 'healthy',
      responseTime: Date.now() - startTime,
      lastCheck: new Date().toISOString()
    };
  } catch (error) {
    return {
      status: 'unhealthy',
      lastCheck: new Date().toISOString(),
      error: error instanceof Error ? error.message : 'Auth service unavailable'
    };
  }
}
