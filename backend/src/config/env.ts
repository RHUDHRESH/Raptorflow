import dotenv from 'dotenv';
import path from 'path';

// Load environment variables from root .env
dotenv.config({ path: path.resolve(__dirname, '../../../../.env') });

export const env = {
  // Application Configuration
  NODE_ENV: process.env.NODE_ENV || 'development',
  PORT: process.env.PORT || '3000',
  FRONTEND_PUBLIC_URL: process.env.FRONTEND_PUBLIC_URL || 'http://localhost:5173',
  
  // Supabase (backend uses VITE_ prefix as fallback to avoid duplication)
  SUPABASE_URL: process.env.SUPABASE_URL || process.env.VITE_SUPABASE_URL || '',
  SUPABASE_SERVICE_ROLE_KEY: process.env.SUPABASE_SERVICE_ROLE_KEY || '',
  
  // Google Cloud / Vertex AI
  GOOGLE_CLOUD_PROJECT_ID: process.env.GOOGLE_CLOUD_PROJECT_ID || '',
  GOOGLE_CLOUD_LOCATION: process.env.GOOGLE_CLOUD_LOCATION || 'us-central1',
  
  // Redis / Upstash
  UPSTASH_REDIS_REST_URL: process.env.UPSTASH_REDIS_REST_URL || '',
  UPSTASH_REDIS_REST_TOKEN: process.env.UPSTASH_REDIS_REST_TOKEN || '',
  
  // PhonePe (backend uses VITE_ prefix as fallback to avoid duplication)
  PHONEPE_MERCHANT_ID: process.env.VITE_PHONEPE_MERCHANT_ID || '',
  PHONEPE_SALT_KEY: process.env.VITE_PHONEPE_SALT_KEY || '',
  PHONEPE_ENV: process.env.VITE_PHONEPE_ENV || 'UAT',
};
