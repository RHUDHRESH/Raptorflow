// Manual Browser Simulation Test
// This simulates exactly what happens when a user fills out the login/signup forms

const http = require('http');

function makeRequest(options, data) {
  return new Promise((resolve, reject) => {
    const req = http.request(options, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        resolve({
          status: res.statusCode,
          headers: res.headers,
          body: body
        });
      });
    });

    req.on('error', reject);
    if (data) req.write(JSON.stringify(data));
    req.end();
  });
}

async function simulateUserFlow() {
  console.log('🌐 Simulating User Authentication Flow...\n');

  // Step 1: Visit the login page (like typing http://localhost:3000/login)
  console.log('📍 Step 1: Loading login page...');
  try {
    const loginPage = await makeRequest({
      hostname: 'localhost',
      port: 3000,
      path: '/login',
      method: 'GET',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    });

    if (loginPage.status === 200) {
      console.log('✅ Login page loaded successfully');
      console.log(`   Content-Type: ${loginPage.headers['content-type']}`);
      console.log(`   Page size: ${loginPage.body.length} bytes\n`);
    } else {
      console.log(`❌ Login page failed: ${loginPage.status}`);
      console.log(`   Body: ${loginPage.body}\n`);
      return;
    }
  } catch (error) {
    console.log(`❌ Failed to load login page: ${error.message}\n`);
    return;
  }

  // Step 2: Fill out signup form and submit (like user clicking "REQUEST ACCESS")
  console.log('📝 Step 2: Submitting signup form...');
  const formData = {
    email: 'testuser@gmail.com',
    password: 'password123',
    fullName: 'Test User'
  };

  try {
    // This simulates the form submission from the login page
    const signupResponse = await makeRequest({
      hostname: 'localhost',
      port: 3000,
      path: '/login',
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': '',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'http://localhost:3000/login'
      }
    }, `email=${encodeURIComponent(formData.email)}&password=${encodeURIComponent(formData.password)}&fullName=${encodeURIComponent(formData.fullName)}`);

    console.log(`📊 Signup response: ${signupResponse.status}`);
    if (signupResponse.status === 302 || signupResponse.status === 303) {
      console.log('✅ Form submitted - Redirecting to:', signupResponse.headers.location);
    } else {
      console.log('📄 Response body preview:', signupResponse.body.substring(0, 200) + '...');
    }
  } catch (error) {
    console.log(`❌ Form submission failed: ${error.message}`);
  }

  console.log('\n🔑 Step 3: Testing direct API call (what the frontend actually does)...');

  // Step 3: Test the actual authentication API that the frontend calls
  try {
    const authResponse = await makeRequest({
      hostname: 'localhost',
      port: 3000,
      path: '/api/auth-bypass',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    }, formData);

    console.log(`🔐 Auth API response: ${authResponse.status}`);
    if (authResponse.status === 200) {
      console.log('✅ Authentication successful!');
      const result = JSON.parse(authResponse.body);
      console.log(`   User ID: ${result.user.id}`);
      console.log(`   Email: ${result.user.email}`);
      console.log(`   Name: ${result.user.user_metadata.full_name}`);
      console.log(`   Session: ${result.session.access_token.substring(0, 20)}...`);
    } else {
      console.log('❌ Authentication failed');
      console.log('   Error:', authResponse.body);
    }
  } catch (error) {
    console.log(`❌ API call failed: ${error.message}`);
  }

  console.log('\n🏠 Step 4: Testing workspace access...');

  // Step 4: Try to access the workspace (protected page)
  try {
    const workspaceResponse = await makeRequest({
      hostname: 'localhost',
      port: 3000,
      path: '/workspace',
      method: 'GET',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    });

    console.log(`📊 Workspace response: ${workspaceResponse.status}`);
    if (workspaceResponse.status === 200) {
      console.log('✅ Workspace accessible');
    } else if (workspaceResponse.status === 302) {
      console.log('🔄 Redirected to:', workspaceResponse.headers.location);
    } else {
      console.log('❌ Workspace access denied');
    }
  } catch (error) {
    console.log(`❌ Workspace test failed: ${error.message}`);
  }

  console.log('\n🎉 Manual browser simulation completed!');
  console.log('\n📋 What this test simulated:');
  console.log('✅ User visiting login page');
  console.log('✅ User filling out signup form');
  console.log('✅ Form submission to backend');
  console.log('✅ Authentication API call');
  console.log('✅ Access to protected workspace');
  console.log('\n🔗 To test manually in browser:');
  console.log('1. Open http://localhost:3000/login');
  console.log('2. Click "REQUEST ACCESS" to switch to signup mode');
  console.log('3. Fill in: testuser@gmail.com / password123 / Test User');
  console.log('4. Click "Create Account"');
  console.log('5. Should redirect to workspace');
}

simulateUserFlow().catch(console.error);
