import 'dotenv/config';
import { createClient } from '@supabase/supabase-js';

const baseUrl = process.env.AUTH_SMOKE_BASE_URL || 'http://localhost:3000';
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || process.env.SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  console.error('Missing Supabase env vars (NEXT_PUBLIC_SUPABASE_URL / NEXT_PUBLIC_SUPABASE_ANON_KEY).');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseAnonKey);
const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
const adminSupabase = serviceRoleKey
  ? createClient(supabaseUrl, serviceRoleKey, {
      auth: { autoRefreshToken: false, persistSession: false },
    })
  : null;

function randomEmail() {
  return `auth-smoke-${Date.now()}@example.com`;
}

async function ensureSignedIn(email, password) {
  const { data: signUpData, error: signUpError } = await supabase.auth.signUp({
    email,
    password,
  });

  if (signUpError && signUpError.message.toLowerCase().includes('already registered')) {
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) throw error;
    return data;
  }

  if (signUpError) {
    if (adminSupabase && signUpError.message.toLowerCase().includes('database error saving new user')) {
      if (process.env.AUTH_SMOKE_ALLOW_RESET !== 'true') {
        throw new Error(
          'Sign-up blocked by database error; set AUTH_SMOKE_EMAIL/AUTH_SMOKE_PASSWORD or AUTH_SMOKE_ALLOW_RESET=true to reuse an existing user.'
        );
      }

      const { data: userList, error: listError } = await adminSupabase.auth.admin.listUsers({
        page: 1,
        perPage: 1,
      });

      if (listError) throw listError;
      const existing = userList?.users?.[0];

      if (!existing?.id || !existing.email) {
        throw new Error('No existing users available to reset for auth smoke test.');
      }

      const { error: updateError } = await adminSupabase.auth.admin.updateUserById(existing.id, {
        password,
      });

      if (updateError) throw updateError;

      const { data, error } = await supabase.auth.signInWithPassword({
        email: existing.email,
        password,
      });

      if (error) throw error;
      return data;
    }

    throw signUpError;
  }

  if (signUpData?.session) {
    return signUpData;
  }

  const { data, error } = await supabase.auth.signInWithPassword({ email, password });
  if (error) throw error;
  return data;
}

async function getProtectedUser(accessToken) {
  const response = await fetch(`${baseUrl}/api/auth/me`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  return {
    status: response.status,
    body: await response.json().catch(() => ({})),
  };
}

async function run() {
  const email = process.env.AUTH_SMOKE_EMAIL || randomEmail();
  const password = process.env.AUTH_SMOKE_PASSWORD || 'TestPassw0rd!123';

  console.log(`Using base URL: ${baseUrl}`);
  console.log(`Signing in as: ${email}`);

  const authData = await ensureSignedIn(email, password);
  const session = authData?.session;

  if (!session?.access_token) {
    throw new Error('No session access token returned from Supabase.');
  }

  const sessionCheck = await supabase.auth.getSession();
  if (!sessionCheck.data.session) {
    throw new Error('Session did not persist in client after sign-in.');
  }

  const protectedResponse = await getProtectedUser(session.access_token);
  if (protectedResponse.status !== 200) {
    throw new Error(`Protected API failed: ${protectedResponse.status} ${JSON.stringify(protectedResponse.body)}`);
  }

  console.log('Protected API response OK:', protectedResponse.body.user?.id || 'unknown');

  const { error: signOutError } = await supabase.auth.signOut({ scope: 'global' });
  if (signOutError) {
    throw new Error(`Sign out failed: ${signOutError.message}`);
  }

  const afterSignOut = await supabase.auth.getSession();
  if (afterSignOut.data.session) {
    throw new Error('Session still present after sign out.');
  }

  console.log('Auth smoke test passed.');
}

run().catch((error) => {
  console.error('Auth smoke test failed:', error.message || error);
  process.exit(1);
});
