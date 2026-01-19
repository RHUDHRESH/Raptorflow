// Test Authentication Flow
// Run with: node test-auth-flow.js

const fetch = require('node-fetch');

const BASE_URL = 'http://localhost:3000';

async function testAuthFlow() {
  console.log('🧪 Testing Authentication Flow...\n');

  // Test 1: Forgot Password API
  console.log('1. Testing forgot-password API...');
  try {
    const response = await fetch(`${BASE_URL}/api/auth/forgot-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: 'rhudhreshr@gmail.com'
      }),
    });

    const data = await response.json();
    if (response.ok) {
      console.log('✅ Forgot password API works');
      console.log('   Message:', data.message);
    } else {
      console.log('❌ Forgot password API failed:', data.error);
    }
  } catch (error) {
    console.log('❌ Forgot password API error:', error.message);
  }

  console.log('\n2. Testing login page accessibility...');
  try {
    const response = await fetch(`${BASE_URL}/login`);
    if (response.ok) {
      console.log('✅ Login page accessible');
    } else {
      console.log('❌ Login page not accessible');
    }
  } catch (error) {
    console.log('❌ Login page error:', error.message);
  }

  console.log('\n3. Testing forgot-password page accessibility...');
  try {
    const response = await fetch(`${BASE_URL}/forgot-password`);
    if (response.ok) {
      console.log('✅ Forgot password page accessible');
    } else {
      console.log('❌ Forgot password page not accessible');
    }
  } catch (error) {
    console.log('❌ Forgot password page error:', error.message);
  }

  console.log('\n4. Testing validate-reset-token API...');
  try {
    // This will fail with invalid token, which is expected
    const response = await fetch(`${BASE_URL}/api/auth/validate-reset-token-simple`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        token: 'invalid-token-test'
      }),
    });

    const data = await response.json();
    if (!response.ok && data.error === 'Invalid or expired reset token') {
      console.log('✅ Token validation API works (correctly rejects invalid token)');
    } else {
      console.log('❌ Token validation API unexpected response:', data);
    }
  } catch (error) {
    console.log('❌ Token validation API error:', error.message);
  }

  console.log('\n🎯 Authentication Flow Test Complete!');
  console.log('\nNext Steps:');
  console.log('1. Start dev server: npm run dev');
  console.log('2. Visit: http://localhost:3000/login');
  console.log('3. Test with email: rhudhreshr@gmail.com');
  console.log('4. Test password reset flow');
}

// Check if server is running
async function checkServer() {
  try {
    const response = await fetch(`${BASE_URL}/api/auth/forgot-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: 'test@test.com' })
    });
    
    if (response.status === 400) {
      // Server is running but API expects proper email
      return true;
    }
    return false;
  } catch (error) {
    return false;
  }
}

// Run tests
checkServer().then(isRunning => {
  if (isRunning) {
    testAuthFlow();
  } else {
    console.log('❌ Server not running at', BASE_URL);
    console.log('Please start the server with: npm run dev');
  }
});
