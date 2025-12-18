import dotenv from 'dotenv';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Resolve the repo root .env (backend/src/config -> ../../../.env)
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const envCandidates = [
  path.resolve(process.cwd(), '.env'),
  path.resolve(__dirname, '../../../.env'),
  path.resolve(__dirname, '../../../../.env')
];

const envPath = envCandidates.find(fs.existsSync);
dotenv.config(envPath ? { path: envPath } : undefined);

export const env = {
  // Application Configuration
  NODE_ENV: process.env.NODE_ENV || 'development',
  PORT: process.env.PORT || '3001', // Default to 3001 for local dev; Cloud Run overrides via PORT
  FRONTEND_PUBLIC_URL: process.env.FRONTEND_PUBLIC_URL || process.env.VITE_FRONTEND_URL || 'http://localhost:5173',
  BACKEND_PUBLIC_URL: process.env.BACKEND_PUBLIC_URL || process.env.VITE_BACKEND_PUBLIC_URL || '',

  // SendGrid
  SENDGRID_API_KEY: process.env.SENDGRID_API_KEY || '',
  SENDGRID_FROM_EMAIL: process.env.SENDGRID_FROM_EMAIL || '',

  // Google Cloud Storage
  GCS_BUCKET: process.env.GCS_BUCKET || '',
  GCS_SIGNED_URL_EXPIRES_SECONDS: process.env.GCS_SIGNED_URL_EXPIRES_SECONDS || '900',

  // Supabase
  SUPABASE_URL: process.env.SUPABASE_URL || process.env.VITE_SUPABASE_URL || 'https://vpwwzsanuyhpkvgorcnc.supabase.co',
  SUPABASE_SERVICE_ROLE_KEY: process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_SERVICE_KEY || '',
  SUPABASE_ANON_KEY: process.env.SUPABASE_ANON_KEY || process.env.VITE_SUPABASE_ANON_KEY || '',

  // Google Cloud / Vertex AI
  GOOGLE_CLOUD_PROJECT_ID: process.env.GOOGLE_CLOUD_PROJECT_ID || process.env.VITE_GOOGLE_CLOUD_PROJECT_ID || 'raptorflow-477017',
  GOOGLE_CLOUD_LOCATION: process.env.GOOGLE_CLOUD_LOCATION || 'us-central1',
  VERTEX_AI_MODEL: process.env.VERTEX_AI_MODEL || 'gemini-1.5-pro-002',
  VERTEX_AI_FLASH_MODEL: process.env.VERTEX_AI_FLASH_MODEL || 'gemini-1.5-flash-002',

  // Upstash Redis
  UPSTASH_REDIS_URL: process.env.UPSTASH_REDIS_URL || '',
  UPSTASH_REDIS_TOKEN: process.env.UPSTASH_REDIS_TOKEN || '',

  // PhonePe Payment Gateway
  PHONEPE_MERCHANT_ID: process.env.PHONEPE_MERCHANT_ID || process.env.VITE_PHONEPE_MERCHANT_ID || '',
  PHONEPE_SALT_KEY: process.env.PHONEPE_SALT_KEY || process.env.VITE_PHONEPE_SALT_KEY || '',
  PHONEPE_SALT_INDEX: process.env.PHONEPE_SALT_INDEX || process.env.VITE_PHONEPE_SALT_INDEX || '1',
  PHONEPE_ENV: process.env.PHONEPE_ENV || process.env.VITE_PHONEPE_ENV || 'UAT', // UAT or PRODUCTION

  // PhonePe Standard Checkout (OAuth) - preferred integration mode
  PHONEPE_CLIENT_ID: process.env.PHONEPE_CLIENT_ID || '',
  PHONEPE_CLIENT_SECRET: process.env.PHONEPE_CLIENT_SECRET || '',
  PHONEPE_CLIENT_VERSION: process.env.PHONEPE_CLIENT_VERSION || '1',

  // Optional override for Standard Checkout API base URL (primarily for production)
  // Example: https://api.phonepe.com/apis
  PHONEPE_STANDARD_API_BASE: process.env.PHONEPE_STANDARD_API_BASE || '',

  // PhonePe Webhook verification (Standard Checkout + Autopay)
  // PhonePe sends: Authorization: SHA256(username:password)
  PHONEPE_WEBHOOK_USERNAME: process.env.PHONEPE_WEBHOOK_USERNAME || '',
  PHONEPE_WEBHOOK_PASSWORD: process.env.PHONEPE_WEBHOOK_PASSWORD || '',

  // AWS Configuration (for Bedrock models)
  AWS_REGION: process.env.AWS_REGION || process.env.VITE_AWS_REGION || 'us-east-1',
  AWS_ACCESS_KEY_ID: process.env.AWS_ACCESS_KEY_ID || '',
  AWS_SECRET_ACCESS_KEY: process.env.AWS_SECRET_ACCESS_KEY || '',
};

// Validate required environment variables in production
if (env.NODE_ENV === 'production') {
  const required = [
    'SUPABASE_SERVICE_ROLE_KEY',
    'GOOGLE_CLOUD_PROJECT_ID',
    'FRONTEND_PUBLIC_URL',
    'BACKEND_PUBLIC_URL'
  ];
  const missing = required.filter(key => !env[key as keyof typeof env]);

  if (missing.length > 0) {
    throw new Error(`Missing environment variables: ${missing.join(', ')}`);
  }
}

// Log configuration (development only)
if (env.NODE_ENV === 'development') {
  console.log('dY"İ Environment Configuration:');
  console.log(`   Port: ${env.PORT}`);
  console.log(`   Frontend URL: ${env.FRONTEND_PUBLIC_URL}`);
  console.log(`   Backend URL: ${env.BACKEND_PUBLIC_URL || '(not set)'}`);
  console.log(`   Supabase URL: ${env.SUPABASE_URL}`);
  console.log(`   Google Cloud Project: ${env.GOOGLE_CLOUD_PROJECT_ID || '(not set)'}`);
  console.log(`   PhonePe Merchant ID: ${env.PHONEPE_MERCHANT_ID ? 'ƒo" Set' : '(not set - mock mode)'}`);
  console.log(`   PhonePe Environment: ${env.PHONEPE_ENV}`);
}
