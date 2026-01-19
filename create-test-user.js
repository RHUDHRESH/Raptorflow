// Create Test User in Supabase
// Run with: node create-test-user.js

const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://vpwwzsanuyhpkvgorcnc.supabase.co';
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw';

const supabase = createClient(supabaseUrl, supabaseServiceKey);

async function createTestUser() {
  console.log('👤 Creating test user in Supabase...\n');

  const testEmail = 'rhudhreshr@gmail.com';
  const testPassword = 'TestPassword123';

  try {
    // Create user with admin API
    const { data, error } = await supabase.auth.admin.createUser({
      email: testEmail,
      password: testPassword,
      email_confirm: true,
      user_metadata: {
        full_name: 'Test User',
        role: 'user'
      }
    });

    if (error) {
      if (error.message.includes('already registered')) {
        console.log('✅ User already exists, updating password...');
        
        // Get existing user
        const { data: { users } } = await supabase.auth.admin.listUsers();
        const user = users.find(u => u.email === testEmail);
        
        if (user) {
          // Update password
          const { error: updateError } = await supabase.auth.admin.updateUser(
            user.id,
            { password: testPassword }
          );
          
          if (updateError) {
            console.log('❌ Failed to update password:', updateError.message);
            return;
          }
          
          console.log('✅ User password updated successfully');
        }
      } else {
        console.log('❌ Failed to create user:', error.message);
        return;
      }
    } else {
      console.log('✅ User created successfully');
      console.log('   Email:', testEmail);
      console.log('   Password:', testPassword);
      console.log('   User ID:', data.user.id);
    }

    // Check if profile exists
    const { data: profile, error: profileError } = await supabase
      .from('profiles')
      .select('*')
      .eq('email', testEmail)
      .single();

    if (profileError && profileError.code === 'PGRST116') {
      // Create profile
      const { error: createProfileError } = await supabase
        .from('profiles')
        .insert({
          id: data?.user?.id || user?.id,
          email: testEmail,
          full_name: 'Test User',
          role: 'user',
          subscription_plan: 'soar',
          subscription_status: 'active',
          onboarding_status: 'active'
        });

      if (createProfileError) {
        console.log('❌ Failed to create profile:', createProfileError.message);
      } else {
        console.log('✅ Profile created successfully');
      }
    } else if (profile) {
      console.log('✅ Profile already exists');
    }

    console.log('\n🎯 Test user ready!');
    console.log('   Login URL: http://localhost:3000/login');
    console.log('   Email:', testEmail);
    console.log('   Password:', testPassword);

  } catch (error) {
    console.log('❌ Error:', error.message);
  }
}

createTestUser();
