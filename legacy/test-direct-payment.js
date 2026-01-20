// Test direct PhonePe payment
const fetch = require('node-fetch');

async function testDirectPayment() {
  try {
    console.log('🔗 Testing DIRECT PhonePe payment (₹3000.00)...');
    
    const response = await fetch('http://localhost:3000/api/create-direct-payment', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        // IMPORTANT: amount is in paise. 3000 INR => 300000 paise
        amount: 300000,
        merchantId: 'PGTESTPAYUAT'
      })
    });
    
    const result = await response.json();
    
    if (result.status === 'success') {
      console.log('✅ DIRECT payment link created successfully!');
      console.log('📋 Payment Details:');
      console.log(`   Transaction ID: ${result.paymentDetails.transactionId}`);
      console.log(`   Amount: ₹${result.paymentDetails.amount}`);
      console.log(`   Merchant ID: ${result.paymentDetails.merchantId}`);
      console.log(`   Payment URL: ${result.paymentDetails.paymentUrl}`);
      console.log(`   Mode: ${result.paymentDetails.mode}`);
      console.log('\n🔗 REAL PhonePe Payment Link:', result.paymentDetails.paymentUrl);
      console.log('\n📋 Next Steps:');
      result.nextSteps.forEach(step => console.log(`   ${step}`));
      console.log('\n🎯 This is a REAL PhonePe UAT payment link!');
      console.log('💳 It will open the actual PhonePe payment interface');
      console.log('📱 You can pay with any UPI method (PhonePe, GPay, Paytm, etc.)');
    } else {
      console.log('❌ Direct payment failed:');
      console.log('Error:', result.error);
      console.log('Message:', result.message);
    }
    
    return result;
  } catch (error) {
    console.error('💥 Error testing direct payment:', error.message);
  }
}

// Run the direct payment test
testDirectPayment();
