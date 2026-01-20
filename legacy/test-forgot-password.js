// Test Forgot Password API
const fetch = require('node-fetch');

async function testForgotPassword() {
  console.log('🧪 Testing Forgot Password API...\n');

  try {
    const response = await fetch('http://localhost:3000/api/auth/forgot-password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: 'rhudhreshr@gmail.com'
      }),
    });

    const data = await response.json();
    
    console.log('Status:', response.status);
    console.log('Response:', JSON.stringify(data, null, 2));

    if (response.ok && data.success) {
      console.log('\n✅ API call successful!');
      console.log('📧 Email should be sent to: rhudhresh3697@gmail.com');
      console.log('🔗 Reset link:', data.resetLink);
      console.log('🎫 Token:', data.token);
      
      // Test token validation
      console.log('\n🧪 Testing token validation...');
      const validateResponse = await fetch('http://localhost:3000/api/auth/validate-reset-token-simple', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token: data.token
        }),
      });

      const validateData = await validateResponse.json();
      console.log('Validation Status:', validateResponse.status);
      console.log('Validation Response:', JSON.stringify(validateData, null, 2));

      if (validateData.valid) {
        console.log('\n✅ Token validation successful!');
        
        // Test password reset
        console.log('\n🧪 Testing password reset...');
        const resetResponse = await fetch('http://localhost:3000/api/auth/reset-password-simple', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            token: data.token,
            newPassword: 'NewPassword123'
          }),
        });

        const resetData = await resetResponse.json();
        console.log('Reset Status:', resetResponse.status);
        console.log('Reset Response:', JSON.stringify(resetData, null, 2));

        if (resetData.success) {
          console.log('\n✅ Password reset flow completed!');
        }
      }
    }

  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

testForgotPassword();
