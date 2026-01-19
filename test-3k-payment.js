// Test script to create a 3k payment
const fetch = require('node-fetch');

async function checkPlans() {
  try {
    const response = await fetch('http://localhost:3001/api/onboarding/plans');
    const plans = await response.json();
    console.log('Available Plans:', JSON.stringify(plans, null, 2));
    return plans;
  } catch (error) {
    console.error('Error fetching plans:', error);
  }
}

async function create3kPayment() {
  try {
    // First, let's create a custom payment request for 3000 rupees (30000 paise)
    const response = await fetch('http://localhost:3001/api/test-payment', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        amount: 30000, // 3000 rupees in paise
        description: 'Custom 3k Payment Test'
      })
    });
    
    const result = await response.json();
    console.log('3k Payment Response:', JSON.stringify(result, null, 2));
    return result;
  } catch (error) {
    console.error('Error creating 3k payment:', error);
  }
}

async function main() {
  console.log('🚀 Checking available plans...');
  await checkPlans();
  
  console.log('\n💰 Creating 3k payment test...');
  await create3kPayment();
}

main();
