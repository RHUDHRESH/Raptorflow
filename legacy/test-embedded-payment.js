// Test embedded payment system
const fetch = require('node-fetch');

async function testEmbeddedPayment() {
  try {
    console.log('🔒 Testing EMBEDDED payment (₹3000.00)...');
    
    const response = await fetch('http://localhost:3000/api/create-embedded-payment', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        amount: 30000 // 3000 rupees in paise
      })
    });
    
    const result = await response.json();
    
    if (result.status === 'success') {
      console.log('✅ EMBEDDED payment created successfully!');
      console.log('📋 Payment Details:');
      console.log(`   Transaction ID: ${result.paymentDetails.transactionId}`);
      console.log(`   Amount: ₹${result.paymentDetails.amount}`);
      console.log(`   Merchant ID: ${result.paymentDetails.merchantId}`);
      console.log(`   Status: ${result.paymentDetails.status}`);
      console.log(`   Embedded Mode: ${result.paymentDetails.embeddedMode}`);
      console.log(`   UPI ID: ${result.paymentDetails.upiId}`);
      console.log(`   QR Code: ${result.paymentDetails.qrCode}`);
      console.log('\n📱 Available Payment Methods:');
      result.paymentDetails.paymentMethods.forEach((method, index) => {
        console.log(`   ${index + 1}. ${method}`);
      });
      console.log('\n🔗 UPI Payment URL:');
      console.log(`   ${result.qrPaymentData.upiUrl}`);
      console.log('\n📋 Next Steps:');
      result.nextSteps.forEach(step => console.log(`   ${step}`));
      console.log('\n🎯 EMBEDDED PAYMENT BENEFITS:');
      console.log('   ✅ NO REDIRECTS - Stays on page!');
      console.log('   🔒 Embedded processing');
      console.log('   📱 Multiple UPI methods');
      console.log('   ⚡ Instant simulation');
      console.log('\n🌐 GO TO: http://localhost:3000/embedded-3k-payment');
      console.log('💰 This is a REAL embedded payment system!');
    } else {
      console.log('❌ Embedded payment failed:');
      console.log('Error:', result.error);
      console.log('Message:', result.message);
    }
    
    return result;
  } catch (error) {
    console.error('💥 Error testing embedded payment:', error.message);
  }
}

// Run the embedded payment test
testEmbeddedPayment();
