import { createClient } from '@supabase/supabase-js';
import { env } from '../config/env';

// Service role client for backend admin tasks
// This client has full access to your database, so use it carefully.
export const supabaseAdmin = createClient(
  env.SUPABASE_URL,
  env.SUPABASE_SERVICE_ROLE_KEY,
  {
    auth: {
      autoRefreshToken: false,
      persistSession: false,
    },
  }
);
