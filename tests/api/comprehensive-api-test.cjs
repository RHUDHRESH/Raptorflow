// Comprehensive API Test - All Endpoints Explicitly Tested
const http = require('http');

const API_ENDPOINTS = [
  // AUTH ENDPOINTS
  { path: '/api/auth/forgot-password', method: 'POST', critical: true, desc: 'Password reset request' },
  { path: '/api/auth/reset-password-simple', method: 'POST', critical: true, desc: 'Simple password reset' },
  { path: '/api/auth/verify-email', method: 'POST', critical: true, desc: 'Email verification' },
  { path: '/api/auth/session-management', method: 'GET', critical: true, desc: 'Session management (GET)' },
  { path: '/api/auth/session-management', method: 'POST', critical: true, desc: 'Session management (POST)' },
  { path: '/api/auth/two-factor', method: 'POST', critical: false, desc: '2FA setup' },
  
  // HEALTH & MONITORING
  { path: '/api/health', method: 'GET', critical: true, desc: 'System health check' },
  { path: '/api/monitoring/dashboard', method: 'GET', critical: false, desc: 'Monitoring dashboard' },
  { path: '/api/monitoring/enhanced-dashboard', method: 'GET', critical: false, desc: 'Enhanced dashboard' },
  
  // USER MANAGEMENT
  { path: '/api/me/subscription', method: 'GET', critical: true, desc: 'User subscription info' },
  { path: '/api/admin/impersonate', method: 'POST', critical: false, desc: 'Admin impersonation' },
  { path: '/api/admin/mfa/setup', method: 'POST', critical: false, desc: 'Admin MFA setup' },
  
  // ONBOARDING ENDPOINTS
  { path: '/api/onboarding/complete', method: 'POST', critical: true, desc: 'Complete onboarding' },
  { path: '/api/onboarding/create-workspace', method: 'POST', critical: true, desc: 'Create workspace' },
  { path: '/api/onboarding/classify', method: 'POST', critical: true, desc: 'Business classification' },
  { path: '/api/onboarding/category-paths', method: 'POST', critical: false, desc: 'Category paths' },
  { path: '/api/onboarding/channel-strategy', method: 'POST', critical: false, desc: 'Channel strategy' },
  { path: '/api/onboarding/competitor-analysis', method: 'POST', critical: false, desc: 'Competitor analysis' },
  { path: '/api/onboarding/contradictions', method: 'POST', critical: false, desc: 'Contradictions check' },
  { path: '/api/onboarding/current-selection', method: 'GET', critical: false, desc: 'Current selection' },
  { path: '/api/onboarding/extract', method: 'POST', critical: false, desc: 'Data extraction' },
  { path: '/api/onboarding/focus-sacrifice', method: 'POST', critical: false, desc: 'Focus sacrifice' },
  { path: '/api/onboarding/icp-deep', method: 'POST', critical: false, desc: 'Deep ICP analysis' },
  { path: '/api/onboarding/launch-readiness', method: 'POST', critical: false, desc: 'Launch readiness' },
  { path: '/api/onboarding/market-size', method: 'POST', critical: false, desc: 'Market size analysis' },
  { path: '/api/onboarding/messaging-rules', method: 'POST', critical: false, desc: 'Messaging rules' },
  { path: '/api/onboarding/neuroscience-copy', method: 'POST', critical: false, desc: 'Neuroscience copy' },
  { path: '/api/onboarding/perceptual-map', method: 'POST', critical: false, desc: 'Perceptual mapping' },
  { path: '/api/onboarding/positioning', method: 'POST', critical: false, desc: 'Positioning analysis' },
  
  // PAYMENT & BILLING
  { path: '/api/create-payment', method: 'POST', critical: true, desc: 'Create payment' },
  { path: '/api/create-embedded-payment', method: 'POST', critical: false, desc: 'Embedded payment' },
  { path: '/api/create-direct-payment', method: 'POST', critical: false, desc: 'Direct payment' },
  { path: '/api/complete-mock-payment', method: 'POST', critical: true, desc: 'Mock payment completion' },
  { path: '/api/billing/dunning', method: 'GET', critical: false, desc: 'Billing dunning' },
  
  // DATABASE & STORAGE
  { path: '/api/create-tables', method: 'POST', critical: false, desc: 'Create database tables' },
  { path: '/api/create-tables-direct', method: 'POST', critical: false, desc: 'Direct table creation' },
  { path: '/api/create-tables-final', method: 'POST', critical: false, desc: 'Final table creation' },
  { path: '/api/create-tables-immediate', method: 'POST', critical: false, desc: 'Immediate table creation' },
  { path: '/api/create-tables-now', method: 'POST', critical: false, desc: 'Create tables now' },
  { path: '/api/force-create-tables', method: 'POST', critical: false, desc: 'Force table creation' },
  { path: '/api/execute-sql', method: 'POST', critical: false, desc: 'Execute SQL' },
  { path: '/api/create-storage', method: 'POST', critical: false, desc: 'Create storage' },
  { path: '/api/init-storage', method: 'POST', critical: false, desc: 'Initialize storage' },
  { path: '/api/gcp-storage', method: 'GET', critical: false, desc: 'GCP storage' },
  
  // INTEGRATION & UTILITIES
  { path: '/api/integration-test', method: 'GET', critical: false, desc: 'Integration test' },
  { path: '/api/auto-setup', method: 'POST', critical: false, desc: 'Auto setup' },
  { path: '/api/auth-mock', method: 'GET', critical: false, desc: 'Auth mock' },
  { path: '/api/gdpr/data-export', method: 'GET', critical: false, desc: 'GDPR data export' }
];

async function testEndpoint(endpoint) {
  return new Promise((resolve) => {
    const { path, method, critical, desc } = endpoint;
    
    const options = {
      hostname: 'localhost',
      port: 3000,
      path: path,
      method: method,
      timeout: 8000,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'API-Tester/1.0'
      }
    };

    const startTime = Date.now();
    
    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        const responseTime = Date.now() - startTime;
        resolve({
          path,
          method,
          desc,
          status: res.statusCode,
          statusText: res.statusMessage,
          success: res.statusCode < 500,
          responseTime,
          response: data.substring(0, 150),
          critical
        });
      });
    });

    req.on('error', (error) => {
      const responseTime = Date.now() - startTime;
      resolve({
        path,
        method,
        desc,
        status: 'ERROR',
        statusText: error.message,
        success: false,
        responseTime,
        response: error.message,
        critical
      });
    });

    req.on('timeout', () => {
      req.destroy();
      const responseTime = Date.now() - startTime;
      resolve({
        path,
        method,
        desc,
        status: 'TIMEOUT',
        statusText: 'Request timeout',
        success: false,
        responseTime,
        response: 'Timeout after 8s',
        critical
      });
    });

    // For POST requests, send empty body
    if (method === 'POST') {
      req.write('{}');
    }
    
    req.end();
  });
}

async function testAllEndpoints() {
  console.log('🔥 COMPREHENSIVE API ENDPOINT TESTING');
  console.log('='.repeat(80));
  console.log(`Testing ${API_ENDPOINTS.length} endpoints...\n`);
  
  let successCount = 0;
  let failCount = 0;
  let criticalFailCount = 0;
  const results = [];

  for (const endpoint of API_ENDPOINTS) {
    const result = await testEndpoint(endpoint);
    results.push(result);
    
    const icon = result.success ? '✅' : '❌';
    const critical = result.critical ? ' [CRITICAL]' : '';
    const time = `${result.responseTime}ms`;
    
    console.log(`${icon} ${result.method} ${result.path}${critical} - ${result.status} (${time})`);
    console.log(`   ${result.desc}`);
    
    if (!result.success) {
      console.log(`   Error: ${result.statusText}`);
      failCount++;
      if (result.critical) criticalFailCount++;
    } else {
      successCount++;
    }
    
    console.log('');
    
    // Small delay between requests
    await new Promise(resolve => setTimeout(resolve, 300));
  }

  // Summary
  console.log('='.repeat(80));
  console.log('📊 API TESTING SUMMARY');
  console.log('='.repeat(80));
  console.log(`✅ Successful: ${successCount}/${API_ENDPOINTS.length}`);
  console.log(`❌ Failed: ${failCount}/${API_ENDPOINTS.length}`);
  console.log(`🚨 Critical Failures: ${criticalFailCount}`);
  
  if (criticalFailCount > 0) {
    console.log('\n🚨 CRITICAL FAILURES:');
    results
      .filter(r => !r.success && r.critical)
      .forEach(r => {
        console.log(`   ❌ ${r.method} ${r.path} - ${r.status} - ${r.desc}`);
      });
  }

  // Response time analysis
  const avgResponseTime = results.reduce((sum, r) => sum + r.responseTime, 0) / results.length;
  const slowEndpoints = results.filter(r => r.responseTime > 3000);
  
  console.log(`\n⏱️  Average Response Time: ${Math.round(avgResponseTime)}ms`);
  if (slowEndpoints.length > 0) {
    console.log('🐌 Slow Endpoints (>3s):');
    slowEndpoints.forEach(r => {
      console.log(`   🐌 ${r.path} - ${r.responseTime}ms`);
    });
  }

  console.log('\n' + '='.repeat(80));
  
  if (criticalFailCount === 0) {
    console.log('🎉 ALL CRITICAL API ENDPOINTS WORKING!');
  } else {
    console.log('⚠️  CRITICAL ISSUES FOUND - FIX REQUIRED');
  }
  
  console.log('='.repeat(80));
}

testAllEndpoints().catch(console.error);
