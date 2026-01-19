// Create a 3k payment test
const fetch = require('node-fetch');

async function create3kPayment() {
  try {
    console.log('💰 Creating 3k payment test (₹3000.00)...');
    
    const response = await fetch('http://localhost:3000/api/test-payment', {
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
      console.log('✅ 3k Payment initiated successfully!');
      console.log('📋 Payment Details:');
      console.log(`   Transaction ID: ${result.testResults.transactionId}`);
      console.log(`   Amount: ₹${result.testResults.amount}`);
      console.log(`   PhonePe Transaction ID: ${result.testResults.phonePeTransactionId}`);
      console.log(`   Payment URL: ${result.testResults.paymentUrl}`);
      console.log('\n🔗 Click here to pay:', result.testResults.paymentUrl);
      console.log('\n📋 Next Steps:');
      result.nextSteps.forEach(step => console.log(`   ${step}`));
    } else {
      console.log('❌ Payment initiation failed:');
      console.log('Error:', result.error);
      console.log('\n🔧 Troubleshooting:');
      result.troubleshooting.forEach(tip => console.log(`   ${tip}`));
    }
    
    return result;
  } catch (error) {
    console.error('💥 Error creating 3k payment:', error.message);
  }
}

// Run the 3k payment test
create3kPayment();
