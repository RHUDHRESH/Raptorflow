#!/usr/bin/env node

const requiredEnvVars = [
  'NEXT_PUBLIC_SUPABASE_URL',
  'NEXT_PUBLIC_SUPABASE_ANON_KEY',
  'NEXT_PUBLIC_API_URL',
  'RESEND_API_KEY',
  'UPSTASH_REDIS_REST_URL',
  'UPSTASH_REDIS_REST_TOKEN',
  'VERTEX_AI_PROJECT_ID',
  'VERTEX_AI_LOCATION',
  'PHONEPE_MERCHANT_ID',
  'PHONEPE_SALT_KEY',
  'PHONEPE_SALT_INDEX'
];

console.log('🔍 Validating environment variables...');

let missingVars = [];
let invalidVars = [];

requiredEnvVars.forEach(varName => {
  const value = process.env[varName];
  if (!value) {
    missingVars.push(varName);
  } else if (value.includes('placeholder') || value.includes('your_')) {
    invalidVars.push(varName);
  }
});

if (missingVars.length > 0) {
  console.error('❌ Missing environment variables:');
  missingVars.forEach(varName => console.error(`  - ${varName}`));
  process.exit(1);
}

if (invalidVars.length > 0) {
  console.error('❌ Invalid environment variables (using placeholders):');
  invalidVars.forEach(varName => console.error(`  - ${varName}`));
  process.exit(1);
}

console.log('✅ All environment variables are properly configured');
