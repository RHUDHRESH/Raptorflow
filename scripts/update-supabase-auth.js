// Script to update Supabase auth configuration
import fetch from 'node-fetch';

const SUPABASE_URL = 'https://api.supabase.com/v1';
const PROJECT_ID = 'vpwwzsanuyhpkvgorcnc';
const SERVICE_ROLE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw';

async function updateAuthConfig() {
  try {
    console.log('🔧 Updating Supabase auth configuration...');
    
    const response = await fetch(`${SUPABASE_URL}/projects/${PROJECT_ID}/config/auth`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${SERVICE_ROLE_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        site_url: 'http://localhost:3000',
        additional_redirect_urls: [
          'http://localhost:3000/auth/callback',
          'http://localhost:3001/auth/callback', 
          'http://localhost:3002/auth/callback',
          'http://localhost:3003/auth/callback',
          'http://localhost:3004/auth/callback',
          'http://localhost:3005/auth/callback',
          'http://127.0.0.1:3000/auth/callback',
          'http://127.0.0.1:3001/auth/callback',
          'http://127.0.0.1:3002/auth/callback',
          'http://127.0.0.1:3003/auth/callback',
          'http://127.0.0.1:3004/auth/callback',
          'http://127.0.0.1:3005/auth/callback'
        ]
      })
    });

    if (response.ok) {
      console.log('✅ Auth configuration updated successfully!');
      const data = await response.json();
      console.log('Updated redirect URLs:', data.additional_redirect_urls);
    } else {
      console.error('❌ Failed to update auth config:', await response.text());
    }
  } catch (error) {
    console.error('❌ Error updating auth config:', error);
  }
}

async function enableGoogleProvider() {
  try {
    console.log('🔧 Enabling Google OAuth provider...');
    
    const response = await fetch(`${SUPABASE_URL}/projects/${PROJECT_ID}/config/auth/providers/google`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${SERVICE_ROLE_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        enabled: true,
        client_id: '[REDACTED]',
        secret: '[REDACTED]',
        skip_nonce_check: true
      })
    });

    if (response.ok) {
      console.log('✅ Google OAuth provider enabled successfully!');
    } else {
      console.error('❌ Failed to enable Google provider:', await response.text());
    }
  } catch (error) {
    console.error('❌ Error enabling Google provider:', error);
  }
}

async function main() {
  await updateAuthConfig();
  await enableGoogleProvider();
  console.log('🎉 Supabase auth configuration complete!');
}

main();
