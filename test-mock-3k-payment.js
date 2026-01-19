// Test the mock 3k payment
const fetch = require('node-fetch');

async function testMockPayment() {
  try {
    console.log('🎭 Testing MOCK 3k payment (₹3000.00)...');
    
    const response = await fetch('http://localhost:3000/api/test-payment-mock', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        amount: 30000, // 3000 rupees in paise
        planId: 'custom-3k-test'
      })
    });
    
    const result = await response.json();
    
    if (result.status === 'success') {
      console.log('✅ MOCK 3k Payment initiated successfully!');
      console.log('📋 Payment Details:');
      console.log(`   Transaction ID: ${result.testResults.transactionId}`);
      console.log(`   Amount: ₹${result.testResults.amount}`);
      console.log(`   PhonePe Transaction ID: ${result.testResults.phonePeTransactionId}`);
      console.log(`   Payment URL: ${result.testResults.paymentUrl}`);
      console.log(`   Mode: ${result.testResults.mockMode ? 'MOCK MODE' : 'LIVE'}`);
      console.log('\n🔗 Simulate payment:', result.testResults.paymentUrl);
      console.log('\n📋 Next Steps:');
      result.nextSteps.forEach(step => console.log(`   ${step}`));
      console.log('\n🎭 Mock Payment Details:');
      Object.entries(result.mockPaymentDetails).forEach(([key, value]) => {
        console.log(`   ${key}: ${value}`);
      });
    } else {
      console.log('❌ Mock payment failed:');
      console.log('Error:', result.error);
      console.log('\n🔧 Troubleshooting:');
      result.troubleshooting.forEach(tip => console.log(`   ${tip}`));
    }
    
    return result;
  } catch (error) {
    console.error('💥 Error testing mock payment:', error.message);
  }
}

// Run the mock payment test
testMockPayment();
