// Check OAuth configuration
import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';

dotenv.config();

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

const supabase = createClient(supabaseUrl, supabaseKey);

async function checkOAuthConfig() {
  try {
    console.log('🔍 Checking OAuth configuration...');

    // Try to get auth settings
    const { data, error } = await supabase.auth.getSession();
    console.log('Session check:', { data, error });

    // Test Google OAuth sign-in URL generation
    const { data: oauthData, error: oauthError } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: 'http://localhost:3000/auth/callback',
        skipBrowserRedirect: true
      }
    });

    console.log('OAuth URL generation:', { oauthData, oauthError });

  } catch (error) {
    console.error('Error checking OAuth:', error);
  }
}

checkOAuthConfig();
