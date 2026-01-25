// Ultra Simple Auth Check - No Dependencies
console.log('🔥 Checking if auth pages exist...');

const fs = require('fs');
const path = require('path');

const pages = [
  'src/app/login/page.tsx',
  'src/app/signup/page.tsx', 
  'src/app/(shell)/dashboard/page.tsx'
];

let allGood = true;

pages.forEach(page => {
  const fullPath = path.join(__dirname, '../../', page);
  if (fs.existsSync(fullPath)) {
    console.log(`✅ ${page}: EXISTS`);
  } else {
    console.log(`❌ ${page}: MISSING`);
    allGood = false;
  }
});

// Check environment variables
console.log('\n🔍 Checking environment...');
const envFiles = ['.env.local', '.env.production'];
envFiles.forEach(env => {
  const envPath = path.join(__dirname, '../../', env);
  if (fs.existsSync(envPath)) {
    console.log(`✅ ${env}: EXISTS`);
  } else {
    console.log(`❌ ${env}: MISSING`);
    allGood = false;
  }
});

console.log(`\n✨ ${allGood ? 'AUTH SETUP LOOKS GOOD!' : 'MISSING FILES FOUND!'}`);
