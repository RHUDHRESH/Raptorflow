// API Endpoint Tester - Explicit Individual Testing
import { chromium } from 'playwright';

const API_ENDPOINTS = [
  // Core Auth Endpoints
  { path: '/api/auth/forgot-password', method: 'POST', critical: true },
  { path: '/api/auth/reset-password-simple', method: 'POST', critical: true },
  { path: '/api/auth/verify-email', method: 'POST', critical: true },
  { path: '/api/auth/session-management', method: 'GET', critical: true },

  // Health
  { path: '/api/health', method: 'GET', critical: true },

  // User Management
  { path: '/api/me/subscription', method: 'GET', critical: true },
  { path: '/api/admin/impersonate', method: 'POST', critical: false },

  // Onboarding Core
  { path: '/api/onboarding/complete', method: 'POST', critical: true },
  { path: '/api/onboarding/create-workspace', method: 'POST', critical: true },
  { path: '/api/onboarding/classify', method: 'POST', critical: true },

  // Billing
  { path: '/api/billing/dunning', method: 'GET', critical: false }
];

class APIEndpointTester {
  constructor() {
    this.results = [];
    this.browser = null;
    this.page = null;
  }

  async init() {
    console.log('🚀 Initializing API Endpoint Tester...');
    this.browser = await chromium.launch({ headless: false });
    this.page = await browser.newPage();
  }

  async testEndpoint(endpoint) {
    const { path, method, critical } = endpoint;
    const url = `http://localhost:3000${path}`;

    console.log(`\n🔍 Testing: ${method} ${path}`);

    try {
      const response = await this.page.request.fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 10000
      });

      const status = response.status();
      const statusText = response.statusText();
      const contentType = response.headers()['content-type'] || 'unknown';

      let responseBody;
      try {
        responseBody = await response.text();
        // Truncate long responses
        if (responseBody.length > 200) {
          responseBody = responseBody.substring(0, 200) + '...';
        }
      } catch (e) {
        responseBody = 'Could not read response body';
      }

      const result = {
        endpoint: path,
        method,
        status,
        statusText,
        contentType,
        response: responseBody,
        success: status < 500,
        critical,
        timestamp: new Date().toISOString()
      };

      this.results.push(result);

      if (result.success) {
        console.log(`✅ ${method} ${path} - ${status} ${statusText}`);
      } else {
        console.log(`❌ ${method} ${path} - ${status} ${statusText}`);
        console.log(`   Response: ${responseBody}`);
      }

      return result;

    } catch (error) {
      const result = {
        endpoint: path,
        method,
        status: 'ERROR',
        statusText: error.message,
        contentType: 'error',
        response: error.message,
        success: false,
        critical,
        timestamp: new Date().toISOString()
      };

      this.results.push(result);
      console.log(`❌ ${method} ${path} - ERROR: ${error.message}`);

      return result;
    }
  }

  async testAllEndpoints() {
    console.log(`\n🎯 Testing ${API_ENDPOINTS.length} API endpoints...\n`);

    for (const endpoint of API_ENDPOINTS) {
      await this.testEndpoint(endpoint);
      // Small delay between requests
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    this.printSummary();
  }

  printSummary() {
    console.log('\n' + '='.repeat(80));
    console.log('📊 API ENDPOINT TEST SUMMARY');
    console.log('='.repeat(80));

    const successful = this.results.filter(r => r.success).length;
    const failed = this.results.filter(r => !r.success).length;
    const criticalFailed = this.results.filter(r => !r.success && r.critical).length;

    console.log(`✅ Successful: ${successful}/${this.results.length}`);
    console.log(`❌ Failed: ${failed}/${this.results.length}`);
    console.log(`🚨 Critical Failures: ${criticalFailed}`);

    if (criticalFailed > 0) {
      console.log('\n🚨 CRITICAL FAILURES:');
      this.results
        .filter(r => !r.success && r.critical)
        .forEach(r => {
          console.log(`   ❌ ${r.method} ${r.endpoint} - ${r.status} ${r.statusText}`);
        });
    }

    console.log('\n📋 Detailed Results:');
    this.results.forEach(r => {
      const icon = r.success ? '✅' : '❌';
      const critical = r.critical ? ' [CRITICAL]' : '';
      console.log(`   ${icon} ${r.method} ${r.endpoint}${critical} - ${r.status} ${r.statusText}`);
    });

    console.log('\n' + '='.repeat(80));

    if (criticalFailed === 0) {
      console.log('🎉 ALL CRITICAL ENDPOINTS WORKING!');
    } else {
      console.log('⚠️  CRITICAL ISSUES FOUND - FIX REQUIRED');
    }
  }

  async cleanup() {
    if (this.browser) {
      await this.browser.close();
    }
  }
}

// Main execution
async function main() {
  const tester = new APIEndpointTester();

  try {
    await tester.init();
    await tester.testAllEndpoints();
  } catch (error) {
    console.error('❌ Tester error:', error);
  } finally {
    await tester.cleanup();
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}

export { APIEndpointTester };
