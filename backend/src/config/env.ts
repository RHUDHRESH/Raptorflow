import dotenv from 'dotenv';
import { z } from 'zod';

// Load environment variables from .env file
dotenv.config();

const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
  PORT: z.string().default('8000'),
  
  // Supabase
  SUPABASE_URL: z.string().url(),
  SUPABASE_SERVICE_ROLE_KEY: z.string().min(1),
  
  // Upstash Redis
  UPSTASH_REDIS_REST_URL: z.string().url(),
  UPSTASH_REDIS_REST_TOKEN: z.string().min(1),
  
  // PhonePe
  PHONEPE_MERCHANT_ID: z.string().min(1),
  PHONEPE_MERCHANT_KEY: z.string().min(1),
  PHONEPE_ENV: z.enum(['sandbox', 'production']).default('sandbox'),
  PHONEPE_WEBHOOK_SECRET: z.string().optional(),
  
  // URLs
  BACKEND_PUBLIC_URL: z.string().url(),
  FRONTEND_PUBLIC_URL: z.string().url(),
  
  // Google Cloud (for reference)
  GOOGLE_PROJECT_ID: z.string().optional(),
  GOOGLE_REGION: z.string().optional(),
});

const parsedEnv = envSchema.safeParse(process.env);

if (!parsedEnv.success) {
  console.error('❌ Invalid environment variables:', JSON.stringify(parsedEnv.error.format(), null, 2));
  // Fail fast in production, maybe warn in dev? No, fail fast always for critical infra.
  process.exit(1);
}

export const env = parsedEnv.data;
