// Simple API Test - No Dependencies
const http = require('http');

const API_ENDPOINTS = [
  '/api/health',
  '/api/auth/session-management',
  '/api/me/subscription',
  '/api/onboarding/complete'
];

async function testEndpoint(path) {
  return new Promise((resolve) => {
    const options = {
      hostname: 'localhost',
      port: 3000,
      path: path,
      method: 'GET',
      timeout: 5000
    };

    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        resolve({
          path,
          status: res.statusCode,
          statusText: res.statusMessage,
          success: res.statusCode < 500,
          response: data.substring(0, 100)
        });
      });
    });

    req.on('error', (error) => {
      resolve({
        path,
        status: 'ERROR',
        statusText: error.message,
        success: false,
        response: error.message
      });
    });

    req.on('timeout', () => {
      req.destroy();
      resolve({
        path,
        status: 'TIMEOUT',
        statusText: 'Request timeout',
        success: false,
        response: 'Timeout'
      });
    });

    req.end();
  });
}

async function testAllEndpoints() {
  console.log('🔥 Testing API Endpoints...\n');

  let successCount = 0;
  let failCount = 0;

  for (const endpoint of API_ENDPOINTS) {
    const result = await testEndpoint(endpoint);

    if (result.success) {
      console.log(`✅ ${result.path} - ${result.status} ${result.statusText}`);
      successCount++;
    } else {
      console.log(`❌ ${result.path} - ${result.status} ${result.statusText}`);
      failCount++;
    }
  }

  console.log(`\n📊 Results: ${successCount} working, ${failCount} failed`);

  if (failCount === 0) {
    console.log('🎉 ALL API ENDPOINTS WORKING!');
  } else {
    console.log('⚠️  Some endpoints failed - check server status');
  }
}

testAllEndpoints().catch(console.error);
