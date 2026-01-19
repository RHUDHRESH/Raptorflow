// Update Test User Password in Supabase
// Run with: node update-test-user.js

const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://vpwwzsanuyhpkvgorcnc.supabase.co';
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw';

const supabase = createClient(supabaseUrl, supabaseServiceKey);

async function updateTestUser() {
  console.log('🔄 Updating test user in Supabase...\n');

  const testEmail = 'rhudhreshr@gmail.com';
  const testPassword = 'TestPassword123';

  try {
    // Get existing user
    const { data: { users }, error: listError } = await supabase.auth.admin.listUsers();
    
    if (listError) {
      console.log('❌ Failed to list users:', listError.message);
      return;
    }

    const user = users.find(u => u.email === testEmail);
    
    if (!user) {
      console.log('❌ User not found:', testEmail);
      return;
    }

    // Update password using GoTrueAdmin
    const { data, error: updateError } = await supabase.auth.admin.updateUserById(
      user.id,
      { 
        password: testPassword,
        email_confirm: true
      }
    );

    if (updateError) {
      console.log('❌ Failed to update password:', updateError.message);
      return;
    }

    console.log('✅ User password updated successfully');
    console.log('   Email:', testEmail);
    console.log('   Password:', testPassword);
    console.log('   User ID:', user.id);

    // Update profile
    const { error: profileError } = await supabase
      .from('profiles')
      .upsert({
        id: user.id,
        email: testEmail,
        full_name: 'Test User',
        role: 'user',
        subscription_plan: 'soar',
        subscription_status: 'active',
        onboarding_status: 'active',
        updated_at: new Date().toISOString()
      }, {
        onConflict: 'id'
      });

    if (profileError) {
      console.log('❌ Failed to update profile:', profileError.message);
    } else {
      console.log('✅ Profile updated successfully');
    }

    console.log('\n🎯 Test user ready!');
    console.log('   Login URL: http://localhost:3000/login');
    console.log('   Email:', testEmail);
    console.log('   Password:', testPassword);

  } catch (error) {
    console.log('❌ Error:', error.message);
  }
}

updateTestUser();
