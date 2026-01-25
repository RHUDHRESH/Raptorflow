// Verify current database schema
import { createClient } from '@supabase/supabase-js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const supabaseUrl = 'https://vpwwzsanuyhpkvgorcnc.supabase.co';
const serviceRoleKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw';

// Create Supabase admin client
const supabase = createClient(supabaseUrl, serviceRoleKey, {
  auth: {
    autoRefreshToken: false,
    persistSession: false
  }
});

async function verifySchema() {
  console.log('🔍 Verifying current database schema...\n');
  
  try {
    // 1. Check table existence
    console.log('📋 Checking table existence:');
    const expectedTables = ['profiles', 'subscriptions', 'payments', 'email_logs', 'workspaces'];
    
    for (const table of expectedTables) {
      try {
        const { data, error } = await supabase
          .from(table)
          .select('*')
          .limit(1);
        
        if (error && error.code === 'PGRST116') {
          console.log(`❌ Table '${table}' - NOT FOUND`);
        } else if (error) {
          console.log(`⚠️  Table '${table}' - ERROR: ${error.message}`);
        } else {
          console.log(`✅ Table '${table}' - EXISTS`);
        }
      } catch (err) {
        console.log(`❌ Table '${table}' - FAILED: ${err.message}`);
      }
    }
    
    console.log('\n📋 Checking table structures:');
    
    // 2. Check profiles table structure
    try {
      const { data: profiles, error } = await supabase
        .from('profiles')
        .select('*')
        .limit(1);
      
      if (!error && profiles.length > 0) {
        const columns = Object.keys(profiles[0]);
        console.log('✅ Profiles table columns:', columns.join(', '));
        
        // Check for required columns
        const requiredColumns = ['id', 'email', 'full_name', 'onboarding_status', 'subscription_plan', 'subscription_status'];
        const missing = requiredColumns.filter(col => !columns.includes(col));
        
        if (missing.length > 0) {
          console.log('⚠️  Profiles missing columns:', missing.join(', '));
        } else {
          console.log('✅ Profiles table has all required columns');
        }
      }
    } catch (err) {
      console.log('❌ Could not check profiles structure:', err.message);
    }
    
    // 3. Check workspaces table structure
    try {
      const { data: workspaces, error } = await supabase
        .from('workspaces')
        .select('*')
        .limit(1);
      
      if (!error && workspaces.length > 0) {
        const columns = Object.keys(workspaces[0]);
        console.log('✅ Workspaces table columns:', columns.join(', '));
        
        // Check for correct column names
        if (columns.includes('owner_id')) {
          console.log('✅ Workspaces table has correct owner_id column');
        } else if (columns.includes('user_id')) {
          console.log('⚠️  Workspaces table has user_id (should be owner_id)');
        } else {
          console.log('❌ Workspaces table missing owner_id column');
        }
      }
    } catch (err) {
      console.log('❌ Could not check workspaces structure:', err.message);
    }
    
    // 4. Test basic operations
    console.log('\n📋 Testing basic operations:');
    
    // Test workspace lookup (the query that was failing)
    try {
      const { data, error } = await supabase
        .from('workspaces')
        .select('id')
        .eq('owner_id', '00000000-0000-0000-0000-000000000000') // Test UUID
        .limit(1);
      
      if (error) {
        if (error.message.includes('column "user_id" does not exist')) {
          console.log('❌ Workspace query still has user_id reference - NEEDS FIX');
        } else {
          console.log('✅ Workspace query works (no user_id error)');
        }
      } else {
        console.log('✅ Workspace query executed successfully');
      }
    } catch (err) {
      console.log('⚠️  Workspace test inconclusive:', err.message);
    }
    
    // 5. Check for any users
    console.log('\n📋 Checking for existing users:');
    try {
      const { data: users, error } = await supabase.auth.admin.listUsers();
      
      if (error) {
        console.log('⚠️  Could not check users (admin access may be restricted):', error.message);
      } else {
        console.log(`✅ Found ${users.users.length} users in auth system`);
        
        if (users.users.length > 0) {
          const testUser = users.users[0];
          console.log(`📧 Test user email: ${testUser.email}`);
          
          // Check if profile exists for this user
          try {
            const { data: profile, error: profileError } = await supabase
              .from('profiles')
              .select('*')
              .eq('id', testUser.id)
              .single();
            
            if (profileError) {
              console.log('⚠️  Profile not found for test user - may need profile creation trigger');
            } else {
              console.log('✅ Profile exists for test user');
            }
          } catch (err) {
            console.log('❌ Profile check failed:', err.message);
          }
        }
      }
    } catch (err) {
      console.log('❌ Could not check users:', err.message);
    }
    
    console.log('\n🎉 Schema verification completed!');
    
  } catch (error) {
    console.error('❌ Verification failed:', error);
  }
}

// Run verification
verifySchema().catch(console.error);
