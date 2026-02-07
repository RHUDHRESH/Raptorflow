// Debug specific endpoint to see actual error
const http = require('http');

async function debugEndpoint(path) {
  return new Promise((resolve) => {
    const options = {
      hostname: 'localhost',
      port: 3000,
      path: path,
      method: 'GET',
      timeout: 5000,
      headers: {
        'Content-Type': 'application/json'
      }
    };

    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        console.log(`Status: ${res.statusCode} ${res.statusMessage}`);
        console.log(`Headers:`, res.headers);
        console.log(`Response:`, data);
        resolve({ status: res.statusCode, data });
      });
    });

    req.on('error', (error) => {
      console.log('Request error:', error);
      resolve({ status: 'ERROR', error: error.message });
    });

    req.on('timeout', () => {
      req.destroy();
      resolve({ status: 'TIMEOUT' });
    });

    req.end();
  });
}

// Test specific endpoints
async function main() {
  console.log('🔍 Debugging API endpoints...\n');

  await debugEndpoint('/api/health');
  console.log('\n' + '='.repeat(50) + '\n');

  await debugEndpoint('/api/auth/session-management');
  console.log('\n' + '='.repeat(50) + '\n');

  await debugEndpoint('/api/me/subscription');
}

main().catch(console.error);
