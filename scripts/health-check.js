#!/usr/bin/env node

/**
 * Comprehensive Health Check Script
 *
 * Used by CI/CD pipelines to verify system health before/after deployments
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { pathToFileURL } from 'url';

const loadEnvFile = filePath => {
  if (!fs.existsSync(filePath)) return;
  const contents = fs.readFileSync(filePath, 'utf8');
  const lines = contents.split(/\r?\n/);
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const eqIndex = trimmed.indexOf('=');
    if (eqIndex <= 0) continue;
    const key = trimmed.slice(0, eqIndex).trim();
    let value = trimmed.slice(eqIndex + 1).trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    if (!process.env[key]) {
      process.env[key] = value;
    }
  }
};

const envPath = path.resolve(process.cwd(), '.env');
loadEnvFile(envPath);

const truthyValues = new Set(['1', 'true', 'yes', 'on']);
const isTruthy = value => truthyValues.has(String(value || '').toLowerCase());
const trimTrailingSlash = value => (value ? value.replace(/\/+$/, '') : value);
const normalizeUrl = value => {
  if (!value) return '';
  if (/^https?:\/\//i.test(value)) return value;
  return `https://${value}`;
};
const safeJson = async response => {
  try {
    return await response.json();
  } catch {
    return null;
  }
};
const maskValue = value => {
  if (!value) return '';
  if (value.length <= 8) return '***';
  return `${value.slice(0, 4)}...${value.slice(-4)}`;
};
const getBackendBaseUrl = () => {
  const explicit = process.env.BACKEND_URL || process.env.BACKEND_PUBLIC_URL;
  if (explicit) return trimTrailingSlash(explicit);
  const apiUrl = process.env.VITE_BACKEND_API_URL || process.env.VITE_API_URL;
  if (apiUrl) return trimTrailingSlash(apiUrl.replace(/\/api\/?$/, ''));
  return 'http://localhost:3001';
};
const getFrontendBaseUrl = () => {
  const explicit = process.env.FRONTEND_URL || process.env.FRONTEND_PUBLIC_URL || process.env.VITE_FRONTEND_URL;
  if (explicit) return trimTrailingSlash(explicit);
  const vercelUrl = process.env.VERCEL_URL;
  if (vercelUrl) return trimTrailingSlash(normalizeUrl(vercelUrl));
  return 'http://localhost:5173';
};

const CHECKS = {
  // =====================================================
  // INFRASTRUCTURE CHECKS
  // =====================================================

  async checkSupabase() {
    const result = { status: 'unknown', message: '', details: {} };

    try {
      const supabaseUrl = trimTrailingSlash(process.env.SUPABASE_URL || process.env.VITE_SUPABASE_URL || '');
      const anonKey = process.env.SUPABASE_ANON_KEY || process.env.VITE_SUPABASE_ANON_KEY || '';
      const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY || '';
      const apiKey = serviceKey || anonKey;

      if (!supabaseUrl) {
        result.status = 'error';
        result.message = 'SUPABASE_URL not configured';
        return result;
      }

      if (!apiKey) {
        result.status = 'error';
        result.message = 'SUPABASE_ANON_KEY or SUPABASE_SERVICE_ROLE_KEY not configured';
        return result;
      }

      const authRes = await fetch(`${supabaseUrl}/auth/v1/health`, {
        headers: {
          apikey: apiKey
        }
      });
      const authData = await safeJson(authRes);

      if (!authRes.ok) {
        result.status = 'error';
        result.message = `Supabase auth health failed (${authRes.status})`;
        result.details = { url: supabaseUrl, auth: authData };
        return result;
      }

      const plansRes = await fetch(`${supabaseUrl}/rest/v1/plans?select=code&limit=1`, {
        headers: {
          apikey: apiKey,
          Authorization: `Bearer ${apiKey}`
        }
      });
      const plansData = await safeJson(plansRes);

      if (!plansRes.ok) {
        result.status = 'error';
        result.message = 'Supabase connected but schema data missing (run migrations)';
        result.details = {
          url: supabaseUrl,
          auth: authData?.status || 'ok',
          schema: plansData || `HTTP ${plansRes.status}`
        };
        return result;
      }

      result.status = 'healthy';
      result.message = 'Supabase auth + schema OK';
      result.details = {
        url: supabaseUrl,
        auth: authData?.status || 'ok',
        sample_plan_code: Array.isArray(plansData) && plansData[0] ? plansData[0].code : null,
        api_key: maskValue(apiKey)
      };
    } catch (error) {
      result.status = 'error';
      result.message = `Supabase check failed: ${error.message}`;
    }

    return result;
  },

  async checkUpstash() {
    const result = { status: 'unknown', message: '', details: {} };

    try {
      const redisUrl = trimTrailingSlash(process.env.UPSTASH_REDIS_URL || process.env.UPSTASH_REDIS_REST_URL || '');
      const redisToken = process.env.UPSTASH_REDIS_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN || '';

      if (!redisUrl || !redisToken) {
        result.status = 'error';
        result.message = 'UPSTASH_REDIS_URL and UPSTASH_REDIS_TOKEN not configured';
        return result;
      }

      const testKey = `healthcheck:${Date.now()}`;
      const setRes = await fetch(`${redisUrl}/set/${encodeURIComponent(testKey)}/${encodeURIComponent('ok')}`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${redisToken}`
        }
      });
      const setData = await safeJson(setRes);

      if (!setRes.ok) {
        result.status = 'error';
        result.message = 'Upstash set failed';
        result.details = { url: redisUrl, response: setData || `HTTP ${setRes.status}` };
        return result;
      }

      const getRes = await fetch(`${redisUrl}/get/${encodeURIComponent(testKey)}`, {
        headers: {
          Authorization: `Bearer ${redisToken}`
        }
      });
      const getData = await safeJson(getRes);

      if (!getRes.ok || (getData && getData.result !== 'ok')) {
        result.status = 'error';
        result.message = 'Upstash get failed';
        result.details = { url: redisUrl, response: getData || `HTTP ${getRes.status}` };
        return result;
      }

      await fetch(`${redisUrl}/del/${encodeURIComponent(testKey)}`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${redisToken}`
        }
      });

      result.status = 'healthy';
      result.message = 'Upstash Redis OK';
      result.details = {
        url: redisUrl,
        token: maskValue(redisToken)
      };
    } catch (error) {
      result.status = 'error';
      result.message = `Upstash check failed: ${error.message}`;
    }

    return result;
  },

  async checkGCS() {
    const result = { status: 'unknown', message: '', details: {} };

    try {
      const bucketName = process.env.GCS_BUCKET;
      if (!bucketName) {
        result.status = 'error';
        result.message = 'GCS_BUCKET not configured';
        return result;
      }

      result.status = 'healthy';
      result.message = 'GCS bucket configured';
      result.details = {
        bucket: bucketName,
        project: process.env.GOOGLE_CLOUD_PROJECT_ID || process.env.GOOGLE_CLOUD_PROJECT || 'raptorflow-477017'
      };
    } catch (error) {
      result.status = 'error';
      result.message = `GCS check failed: ${error.message}`;
    }

    return result;
  },

  async checkVertexAI() {
    const result = { status: 'unknown', message: '', details: {} };

    try {
      const projectId = process.env.GOOGLE_CLOUD_PROJECT_ID || process.env.GOOGLE_CLOUD_PROJECT || '';
      const location = process.env.GOOGLE_CLOUD_LOCATION || process.env.VERTEX_AI_LOCATION || 'us-central1';
      const modelName = process.env.VERTEX_AI_FLASH_MODEL || process.env.VERTEX_AI_MODEL || 'gemini-1.5-flash';
      const credentialsPath = process.env.GOOGLE_APPLICATION_CREDENTIALS || '';

      if (!projectId) {
        result.status = 'error';
        result.message = 'GOOGLE_CLOUD_PROJECT_ID not configured';
        return result;
      }

      if (credentialsPath && !fs.existsSync(credentialsPath)) {
        result.status = 'error';
        result.message = 'GOOGLE_APPLICATION_CREDENTIALS path not found';
        result.details = { credentials: credentialsPath };
        return result;
      }

      const runLiveCheck = isTruthy(process.env.VERTEX_AI_HEALTHCHECK);
      if (!runLiveCheck) {
        result.status = credentialsPath ? 'healthy' : 'warning';
        result.message = 'Vertex AI config detected (set VERTEX_AI_HEALTHCHECK=1 for a live request)';
        result.details = {
          project: projectId,
          location,
          model: modelName,
          credentials: credentialsPath ? 'file set' : 'not set'
        };
        return result;
      }

      const { VertexAI } = await import('@google-cloud/vertexai');
      const vertexAI = new VertexAI({ project: projectId, location });
      const model = vertexAI.getGenerativeModel({ model: modelName });

      await model.generateContent({
        contents: [{ role: 'user', parts: [{ text: 'health check' }] }]
      });

      result.status = 'healthy';
      result.message = 'Vertex AI request succeeded';
      result.details = {
        project: projectId,
        location,
        model: modelName
      };
    } catch (error) {
      result.status = 'error';
      result.message = `Vertex AI check failed: ${error.message}`;
    }

    return result;
  },

  // =====================================================
  // APPLICATION CHECKS
  // =====================================================

  async checkBackendHealth() {
    const result = { status: 'unknown', message: '', details: {} };

    try {
      const baseUrl = getBackendBaseUrl();

      // Check health endpoint
      const response = await fetch(`${baseUrl}/health`);
      const healthData = await safeJson(response);

      if (response.ok && healthData?.status === 'ok') {
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
      const baseUrl = getFrontendBaseUrl();
      const startTime = Date.now();

      // Check if frontend is serving
      const response = await fetch(baseUrl);
      const responseTime = Date.now() - startTime;

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
      const baseUrl = getBackendBaseUrl();

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
      const baseUrl = getBackendBaseUrl();

      // Check if agents are available
      const response = await fetch(`${baseUrl}/api/muse/agents`);
      const agentsData = await safeJson(response);

      if (response.ok && agentsData?.agents && agentsData.agents.length > 0) {
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
      const baseUrl = getFrontendBaseUrl();
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
      const warnings = [];

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

      const supabaseUrl = process.env.SUPABASE_URL || process.env.VITE_SUPABASE_URL;
      const supabaseAnon = process.env.SUPABASE_ANON_KEY || process.env.VITE_SUPABASE_ANON_KEY;
      const supabaseService = process.env.SUPABASE_SERVICE_ROLE_KEY;
      if (!supabaseUrl) {
        issues.push('Missing SUPABASE_URL or VITE_SUPABASE_URL');
      }
      if (!supabaseAnon && !supabaseService) {
        issues.push('Missing SUPABASE_ANON_KEY or SUPABASE_SERVICE_ROLE_KEY');
      }

      const projectId = process.env.GOOGLE_CLOUD_PROJECT_ID || process.env.GOOGLE_CLOUD_PROJECT;
      if (!projectId) {
        warnings.push('GOOGLE_CLOUD_PROJECT_ID not configured (Vertex AI disabled)');
      }

      const upstashUrl = process.env.UPSTASH_REDIS_URL || process.env.UPSTASH_REDIS_REST_URL;
      const upstashToken = process.env.UPSTASH_REDIS_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN;
      if (!upstashUrl || !upstashToken) {
        warnings.push('Upstash Redis not configured (cache will fall back to memory)');
      }

      if (issues.length === 0 && warnings.length === 0) {
        result.status = 'healthy';
        result.message = 'All dependencies and configuration checks passed';
        result.details = {
          nodeVersion,
          environment: process.env.NODE_ENV || 'development'
        };
      } else if (issues.length === 0) {
        result.status = 'warning';
        result.message = `${warnings.length} optional configuration issues found`;
        result.details = { warnings, nodeVersion, environment: process.env.NODE_ENV || 'development' };
      } else {
        result.status = 'error';
        result.message = `${issues.length} dependency/configuration issues found`;
        result.details = { issues, warnings };
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
const invokedPath = process.argv[1]
  ? pathToFileURL(path.resolve(process.argv[1])).href
  : '';

if (import.meta.url === invokedPath) {
  runHealthChecks().catch(error => {
    console.error('Health check execution failed:', error);
    process.exit(1);
  });
}

export { CHECKS, runHealthChecks };

