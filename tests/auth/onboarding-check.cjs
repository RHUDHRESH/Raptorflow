// Onboarding System Check
console.log('🔍 Checking onboarding system...');

const fs = require('fs');
const path = require('path');

const onboardingFiles = [
  'src/app/onboarding/page.tsx',
  'src/app/onboarding/layout.tsx',
  'src/app/onboarding/session/step/[stepId]/page.tsx',
  'src/components/onboarding/OnboardingShell.tsx',
  'src/stores/onboardingStore.ts'
];

let allGood = true;

onboardingFiles.forEach(file => {
  const fullPath = path.join(__dirname, '../../', file);
  if (fs.existsSync(fullPath)) {
    console.log(`✅ ${file}: EXISTS`);
  } else {
    console.log(`❌ ${file}: MISSING`);
    allGood = false;
  }
});

// Check onboarding routes
console.log('\n🔍 Checking onboarding routes...');
const routes = [
  '/onboarding',
  '/onboarding/session/step/1',
  '/onboarding/session/step/2',
  '/onboarding/session/step/3'
];

routes.forEach(route => {
  console.log(`📍 Route: ${route}`);
});

console.log(`\n✨ ${allGood ? 'ONBOARDING SETUP LOOKS GOOD!' : 'MISSING FILES FOUND!'}`);

// Check if redirect logic exists
console.log('\n🔍 Checking signup redirect logic...');
const signupPage = path.join(__dirname, '../../', 'src/app/signup/page.tsx');
if (fs.existsSync(signupPage)) {
  const signupContent = fs.readFileSync(signupPage, 'utf8');
  if (signupContent.includes('/onboarding')) {
    console.log('✅ Signup redirects to onboarding');
  } else {
    console.log('❌ Signup does NOT redirect to onboarding');
  }
} else {
  console.log('❌ Signup page not found');
}
