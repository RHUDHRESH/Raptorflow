import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

// Load environment variables from root .env
const __dirname = path.dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: path.resolve(__dirname, '../../../../.env') });

export const env = {
  // Application Configuration
  NODE_ENV: process.env.NODE_ENV || 'development',
  PORT: process.env.PORT || '3001',
  FRONTEND_PUBLIC_URL: process.env.FRONTEND_PUBLIC_URL || process.env.VITE_FRONTEND_URL || 'http://localhost:5173',
  
  // Supabase
  SUPABASE_URL: process.env.SUPABASE_URL || process.env.VITE_SUPABASE_URL || 'https://vpwwzsanuyhpkvgorcnc.supabase.co',
  SUPABASE_SERVICE_ROLE_KEY: process.env.SUPABASE_SERVICE_ROLE_KEY || '',
  
  // Google Cloud / Vertex AI
  GOOGLE_CLOUD_PROJECT_ID: process.env.GOOGLE_CLOUD_PROJECT_ID || process.env.VITE_GOOGLE_CLOUD_PROJECT_ID || '',
  GOOGLE_CLOUD_LOCATION: process.env.GOOGLE_CLOUD_LOCATION || 'us-central1',
  
  // PhonePe Payment Gateway
  PHONEPE_MERCHANT_ID: process.env.PHONEPE_MERCHANT_ID || process.env.VITE_PHONEPE_MERCHANT_ID || '',
  PHONEPE_SALT_KEY: process.env.PHONEPE_SALT_KEY || process.env.VITE_PHONEPE_SALT_KEY || '',
  PHONEPE_SALT_INDEX: process.env.PHONEPE_SALT_INDEX || process.env.VITE_PHONEPE_SALT_INDEX || '1',
  PHONEPE_ENV: process.env.PHONEPE_ENV || process.env.VITE_PHONEPE_ENV || 'UAT', // UAT or PRODUCTION
};

// Validate required environment variables in production
if (env.NODE_ENV === 'production') {
  const required = ['SUPABASE_SERVICE_ROLE_KEY', 'GOOGLE_CLOUD_PROJECT_ID'];
  const missing = required.filter(key => !env[key as keyof typeof env]);
  
  if (missing.length > 0) {
    console.warn(`⚠️ Missing environment variables: ${missing.join(', ')}`);
  }
}

// Log configuration (development only)
if (env.NODE_ENV === 'development') {
  console.log('📦 Environment Configuration:');
  console.log(`   Port: ${env.PORT}`);
  console.log(`   Frontend URL: ${env.FRONTEND_PUBLIC_URL}`);
  console.log(`   Supabase URL: ${env.SUPABASE_URL}`);
  console.log(`   Google Cloud Project: ${env.GOOGLE_CLOUD_PROJECT_ID || '(not set)'}`);
  console.log(`   PhonePe Merchant ID: ${env.PHONEPE_MERCHANT_ID ? '✓ Set' : '(not set - mock mode)'}`);
  console.log(`   PhonePe Environment: ${env.PHONEPE_ENV}`);
}
