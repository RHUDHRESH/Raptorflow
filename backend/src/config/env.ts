import dotenv from 'dotenv';
import path from 'path';

// Load environment variables from root .env
dotenv.config({ path: path.resolve(__dirname, '../../../../.env') });

export const env = {
  NODE_ENV: process.env.NODE_ENV || 'development',
  PORT: process.env.PORT || '3000',
  FRONTEND_PUBLIC_URL: process.env.FRONTEND_PUBLIC_URL || 'http://localhost:5173',
  
  // Supabase
  SUPABASE_URL: process.env.SUPABASE_URL || '',
  SUPABASE_SERVICE_ROLE_KEY: process.env.SUPABASE_SERVICE_ROLE_KEY || '',
  
  // Google Cloud / Vertex AI
  GOOGLE_CLOUD_PROJECT_ID: process.env.GOOGLE_CLOUD_PROJECT_ID,
  GOOGLE_CLOUD_LOCATION: process.env.GOOGLE_CLOUD_LOCATION || 'us-central1',
  GOOGLE_PROJECT_ID: process.env.GOOGLE_CLOUD_PROJECT_ID, // Alias for compatibility
  GOOGLE_REGION: process.env.GOOGLE_CLOUD_LOCATION || 'us-central1', // Alias for compatibility
  
  // Redis
  UPSTASH_REDIS_REST_URL: process.env.UPSTASH_REDIS_REST_URL || '',
  UPSTASH_REDIS_REST_TOKEN: process.env.UPSTASH_REDIS_REST_TOKEN || '',
  
  // PhonePe
  PHONEPE_MERCHANT_ID: process.env.PHONEPE_MERCHANT_ID || '',
  PHONEPE_MERCHANT_KEY: process.env.PHONEPE_MERCHANT_KEY || '',
  PHONEPE_ENV: process.env.PHONEPE_ENV || 'UAT',
};
