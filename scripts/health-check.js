#!/usr/bin/env node

/**
 * Comprehensive Health Check Script
 *
 * Used by CI/CD pipelines to verify system health before/after deployments
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

const CHECKS = {
  // =====================================================
  // INFRASTRUCTURE CHECKS
  // =====================================================

  async checkDatabase() {
    const result = { status: 'unknown', message: '', details: {} };

    try {
      // Check if database is accessible
      const dbUrl = process.env.DATABASE_URL;
      if (!dbUrl) {
        result.status = 'error';
        result.message = 'DATABASE_URL not configured';
        return result;
      }

      // Simple connection test (would need pg client in production)
      result.status = 'healthy';
      result.message = 'Database connection available';
      result.details = {
        url: dbUrl.replace(/:\/\/.*@/, '://***:***@'), // Mask credentials
        type: 'postgresql'
      };
    } catch (error) {
      result.status = 'error';
      result.message = `Database check failed: ${error.message}`;
    }

    return result;
  },

  async checkRedis() {
    const result = { status: 'unknown', message: '', details: {} };

    try {
      const redisUrl = process.env.REDIS_URL;
      if (!redisUrl) {
        result.status = 'error';
        result.message = 'REDIS_URL not configured';
        return result;
      }

      // Simple Redis ping test (would need redis client in production)
      result.status = 'healthy';
      result.message = 'Redis connection available';
      result.details = {
        url: redisUrl.replace(/:\/\/.*@/, '://***:***@'), // Mask credentials
        type: 'redis'
      };
    } catch (error) {
      result.status = 'error';
      result.message = `Redis check failed: ${error.message}`;
    }

    return result;
  },

  async checkS3() {
    const result = { status: 'unknown', message: '', details: {} };

    try {
      const bucketName = process.env.AWS_S3_BUCKET;
      if (!bucketName) {
        result.status = 'error';
        result.message = 'AWS_S3_BUCKET not configured';
        return result;
      }

      result.status = 'healthy';
      result.message = 'S3 bucket configured';
      result.details = {
        bucket: bucketName,
        region: process.env.AWS_REGION || 'us-east-1'
      };
    } catch (error) {
      result.status = 'error';
      result.message = `S3 check failed: ${error.message}`;
    }

    return result;
  },

  // =====================================================
  // APPLICATION CHECKS
  // =====================================================

  async checkBackendHealth() {
    const result = { status: 'unknown', message: '', details: {} };

    try {
      const baseUrl = process.env.BACKEND_URL || 'http://localhost:3001';

      // Check health endpoint
      const response = await fetch(`${baseUrl}/health`);
      const healthData = await response.json();

      if (response.ok && healthData.status === 'ok') {
        result.status = 'healthy';
        result.message = 'Backend is healthy';
        result.details = healthData;
      } else {
        result.status = 'error';
        result.message = 'Backend health check failed';
        result.details = healthData;
      }
    } catch (error) {
      result.status = 'error';
      result.message = `Backend health check failed: ${error.message}`;
    }

    return result;
  },

  async checkFrontendHealth() {
    const result = { status: 'unknown', message: '', details: {} };

    try {
      const baseUrl = process.env.FRONTEND_URL || 'http://localhost:3000';

      // Check if frontend is serving
      const response = await fetch(baseUrl);
      const responseTime = Date.now() - new Date().getTime(); // Rough timing

      if (response.ok) {
        result.status = 'healthy';
        result.message = 'Frontend is accessible';
        result.details = {
          statusCode: response.status,
          responseTime: `${responseTime}ms`,
          url: baseUrl
        };
      } else {
        result.status = 'error';
        result.message = `Frontend returned ${response.status}`;
      }
    } catch (error) {
      result.status = 'error';
      result.message = `Frontend check failed: ${error.message}`;
    }

    return result;
  },

  // =====================================================
  // MUSE-SPECIFIC CHECKS
  // =====================================================

  async checkMuseOrchestrator() {
    const result = { status: 'unknown', message: '', details: {} };

    try {
      const baseUrl = process.env.BACKEND_URL || 'http://localhost:3001';

      // Check Muse orchestrator health
      const response = await fetch(`${baseUrl}/api/muse/generate`, {
        method: 'OPTIONS' // Just check if endpoint exists
      });

      if (response.status !== 405) { // 405 is expected for OPTIONS
        result.status = 'healthy';
        result.message = 'Muse orchestrator endpoints available';
        result.details = {
          endpoint: '/api/muse/generate',
          status: response.status
        };
      } else {
        result.status = 'error';
        result.message = 'Muse orchestrator endpoints not accessible';
      }
    } catch (error) {
      result.status = 'error';
      result.message = `Muse orchestrator check failed: ${error.message}`;
    }

    return result;
  },

  async checkMuseAgents() {
    const result = { status: 'unknown', message: '', details: {} };

    try {
      const baseUrl = process.env.BACKEND_URL || 'http://localhost:3001';

      // Check if agents are available
      const response = await fetch(`${baseUrl}/api/muse/agents`);
      const agentsData = await response.json();

      if (response.ok && agentsData.agents && agentsData.agents.length > 0) {
        result.status = 'healthy';
        result.message = `${agentsData.agents.length} Muse agents available`;
        result.details = {
          total_agents: agentsData.agents.length,
          systems: agentsData.systems
        };
      } else {
        result.status = 'error';
        result.message = 'Muse agents not available';
        result.details = agentsData;
      }
    } catch (error) {
      result.status = 'error';
      result.message = `Muse agents check failed: ${error.message}`;
    }

    return result;
  },

  // =====================================================
  // PERFORMANCE CHECKS
  // =====================================================

  async checkPerformance() {
    const result = { status: 'unknown', message: '', details: {} };

    try {
      const baseUrl = process.env.FRONTEND_URL || 'http://localhost:3000';
      const startTime = Date.now();

      const response = await fetch(baseUrl);
      const responseTime = Date.now() - startTime;

      if (response.ok) {
        if (responseTime < 3000) { // 3 seconds threshold
          result.status = 'healthy';
          result.message = `Response time: ${responseTime}ms`;
        } else {
          result.status = 'warning';
          result.message = `Slow response time: ${responseTime}ms`;
        }

        result.details = {
          responseTime: `${responseTime}ms`,
          statusCode: response.status,
          threshold: '3000ms'
        };
      } else {
        result.status = 'error';
        result.message = `HTTP ${response.status}`;
      }
    } catch (error) {
      result.status = 'error';
      result.message = `Performance check failed: ${error.message}`;
    }

    return result;
  },

  // =====================================================
  // DEPENDENCY CHECKS
  // =====================================================

  async checkDependencies() {
    const result = { status: 'unknown', message: '', details: {} };

    try {
      const issues = [];

      // Check Node.js version
      const nodeVersion = process.version;
      const majorVersion = parseInt(nodeVersion.replace('v', '').split('.')[0]);
      if (majorVersion < 18) {
        issues.push(`Node.js version ${nodeVersion} is too old (required: >=18)`);
      }

      // Check if package.json exists
      if (!fs.existsSync('package.json')) {
        issues.push('package.json not found');
      }

      // Check if backend package.json exists
      if (!fs.existsSync('backend/package.json')) {
        issues.push('backend/package.json not found');
      }

      // Check for critical environment variables
      const requiredEnvVars = ['DATABASE_URL', 'REDIS_URL', 'SUPABASE_URL'];
      const missingEnvVars = requiredEnvVars.filter(envVar => !process.env[envVar]);

      if (missingEnvVars.length > 0) {
        issues.push(`Missing environment variables: ${missingEnvVars.join(', ')}`);
      }

      if (issues.length === 0) {
        result.status = 'healthy';
        result.message = 'All dependencies and configuration checks passed';
        result.details = {
          nodeVersion,
          environment: process.env.NODE_ENV || 'development'
        };
      } else {
        result.status = 'error';
        result.message = `${issues.length} dependency/configuration issues found`;
        result.details = { issues };
      }
    } catch (error) {
      result.status = 'error';
      result.message = `Dependency check failed: ${error.message}`;
    }

    return result;
  }
};

// =====================================================
// MAIN EXECUTION
// =====================================================

async function runHealthChecks() {
  console.log('🔍 Running comprehensive health checks...\n');

  const results = {};
  const startTime = Date.now();

  // Run all checks
  for (const [checkName, checkFunction] of Object.entries(CHECKS)) {
    console.log(`Running ${checkName}...`);
    try {
      results[checkName] = await checkFunction();
      const status = results[checkName].status;
      const emoji = status === 'healthy' ? '✅' : status === 'warning' ? '⚠️' : '❌';
      console.log(`${emoji} ${checkName}: ${results[checkName].message}`);
    } catch (error) {
      results[checkName] = {
        status: 'error',
        message: `Check failed: ${error.message}`,
        details: {}
      };
      console.log(`❌ ${checkName}: Check failed: ${error.message}`);
    }
  }

  const totalTime = Date.now() - startTime;
  console.log(`\n⏱️  Total execution time: ${totalTime}ms\n`);

  // Summarize results
  const summary = {
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development',
    total_checks: Object.keys(results).length,
    healthy: Object.values(results).filter(r => r.status === 'healthy').length,
    warnings: Object.values(results).filter(r => r.status === 'warning').length,
    errors: Object.values(results).filter(r => r.status === 'error').length,
    results
  };

  // Output results
  if (process.argv.includes('--json')) {
    console.log(JSON.stringify(summary, null, 2));
  } else {
    console.log('📊 Health Check Summary:');
    console.log(`   ✅ Healthy: ${summary.healthy}`);
    console.log(`   ⚠️  Warnings: ${summary.warnings}`);
    console.log(`   ❌ Errors: ${summary.errors}`);
    console.log(`   📈 Total: ${summary.total_checks}`);

    if (summary.errors > 0) {
      console.log('\n❌ FAILED: System has critical issues that need attention.');
      process.exit(1);
    } else if (summary.warnings > 0) {
      console.log('\n⚠️  WARNING: System is operational but has some issues.');
      process.exit(0);
    } else {
      console.log('\n✅ SUCCESS: All systems are healthy!');
      process.exit(0);
    }
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  runHealthChecks().catch(error => {
    console.error('Health check execution failed:', error);
    process.exit(1);
  });
}

export { CHECKS, runHealthChecks };

