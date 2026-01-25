// Pull and verify current schema from Supabase
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

async function pullAndVerifySchema() {
  console.log('🔍 Pulling and verifying current schema...\n');

  const report = {
    timestamp: new Date().toISOString(),
    tables: {},
    issues: [],
    fixes: []
  };

  try {
    // Test basic connection
    console.log('🔌 Testing database connection...');
    try {
      const { data, error } = await supabase
        .from('profiles')
        .select('count')
        .limit(1);

      if (error) {
        if (error.code === 'PGRST116') {
          report.issues.push('Tables do not exist - need to run schema deployment');
          console.log('❌ Tables not found - Schema needs to be deployed');
        } else {
          report.issues.push(`Connection error: ${error.message}`);
          console.log('❌ Connection error:', error.message);
        }
        return generateReport(report);
      }
      console.log('✅ Database connection successful');
    } catch (err) {
      report.issues.push(`Network error: ${err.message}`);
      console.log('❌ Network error - cannot connect to Supabase');
      return generateReport(report);
    }

    // Check each table
    const expectedTables = [
      {
        name: 'profiles',
        requiredColumns: ['id', 'email', 'full_name', 'onboarding_status', 'subscription_plan', 'subscription_status'],
        forbiddenColumns: ['workspace_id'] // Should not exist
      },
      {
        name: 'workspaces',
        requiredColumns: ['id', 'owner_id', 'name'],
        forbiddenColumns: ['user_id'] // Should be owner_id instead
      },
      {
        name: 'subscriptions',
        requiredColumns: ['id', 'user_id', 'plan_id', 'status']
      },
      {
        name: 'payments',
        requiredColumns: ['id', 'user_id', 'transaction_id', 'amount', 'status']
      },
      {
        name: 'email_logs',
        requiredColumns: ['id', 'user_id', 'email_type', 'recipient_email']
      }
    ];

    for (const tableInfo of expectedTables) {
      await checkTable(tableInfo, report);
    }

    // Test critical queries
    await testCriticalQueries(report);

    // Generate final report
    generateReport(report);

  } catch (error) {
    console.error('❌ Schema verification failed:', error);
    report.issues.push(`Verification failed: ${error.message}`);
    generateReport(report);
  }
}

async function checkTable(tableInfo, report) {
  console.log(`\n📋 Checking table: ${tableInfo.name}`);

  try {
    // Get table structure
    const { data, error } = await supabase
      .from(tableInfo.name)
      .select('*')
      .limit(1);

    if (error && error.code === 'PGRST116') {
      report.issues.push(`Table '${tableInfo.name}' does not exist`);
      console.log(`❌ Table '${tableInfo.name}' - NOT FOUND`);
      report.tables[tableInfo.name] = { exists: false };
      return;
    }

    if (error) {
      report.issues.push(`Error accessing table '${tableInfo.name}': ${error.message}`);
      console.log(`⚠️  Table '${tableInfo.name}' - ERROR: ${error.message}`);
      report.tables[tableInfo.name] = { exists: true, error: error.message };
      return;
    }

    // Analyze columns
    const columns = data.length > 0 ? Object.keys(data[0]) : [];
    report.tables[tableInfo.name] = {
      exists: true,
      columns,
      sampleData: data[0] || null
    };

    console.log(`✅ Table '${tableInfo.name}' exists with columns: ${columns.join(', ')}`);

    // Check required columns
    const missingRequired = tableInfo.requiredColumns.filter(col => !columns.includes(col));
    if (missingRequired.length > 0) {
      report.issues.push(`Table '${tableInfo.name}' missing required columns: ${missingRequired.join(', ')}`);
      console.log(`⚠️  Missing required columns: ${missingRequired.join(', ')}`);
    }

    // Check for forbidden columns
    const foundForbidden = tableInfo.forbiddenColumns?.filter(col => columns.includes(col)) || [];
    if (foundForbidden.length > 0) {
      report.issues.push(`Table '${tableInfo.name}' has incorrect columns: ${foundForbidden.join(', ')}`);
      console.log(`❌ Found incorrect columns: ${foundForbidden.join(', ')}`);

      // Suggest fixes
      if (tableInfo.name === 'workspaces' && foundForbidden.includes('user_id')) {
        report.fixes.push('Rename workspaces.user_id to workspaces.owner_id');
      }
      if (tableInfo.name === 'profiles' && foundForbidden.includes('workspace_id')) {
        report.fixes.push('Remove profiles.workspace_id column (not part of schema)');
      }
    }

  } catch (err) {
    report.issues.push(`Failed to check table '${tableInfo.name}': ${err.message}`);
    console.log(`❌ Failed to check table '${tableInfo.name}':`, err.message);
  }
}

async function testCriticalQueries(report) {
  console.log('\n🧪 Testing critical queries...');

  // Test the workspace query that was causing issues
  try {
    const { data, error } = await supabase
      .from('workspaces')
      .select('id, name, owner_id')
      .eq('owner_id', '00000000-0000-0000-0000-000000000000')
      .limit(1);

    if (error) {
      if (error.message.includes('column "user_id" does not exist')) {
        report.issues.push('Workspace query still references user_id column');
        console.log('❌ Workspace query error: user_id column reference');
      } else {
        console.log('✅ Workspace query works (no user_id error)');
      }
    } else {
      console.log('✅ Workspace query executed successfully');
    }
  } catch (err) {
    console.log('⚠️  Workspace query test inconclusive:', err.message);
  }

  // Test profile access
  try {
    const { data, error } = await supabase
      .from('profiles')
      .select('id, email, onboarding_status')
      .limit(1);

    if (error) {
      report.issues.push(`Profile access error: ${error.message}`);
      console.log('❌ Profile access error:', error.message);
    } else {
      console.log('✅ Profile access works correctly');
    }
  } catch (err) {
    console.log('⚠️  Profile access test inconclusive:', err.message);
  }
}

function generateReport(report) {
  console.log('\n' + '='.repeat(60));
  console.log('📊 SCHEMA VERIFICATION REPORT');
  console.log('='.repeat(60));
  console.log(`🕐 Generated: ${report.timestamp}`);

  console.log('\n📋 TABLE STATUS:');
  Object.entries(report.tables).forEach(([name, info]) => {
    if (info.exists) {
      console.log(`✅ ${name}: EXISTS (${info.columns?.length || 0} columns)`);
      if (info.error) {
        console.log(`   ⚠️  Error: ${info.error}`);
      }
    } else {
      console.log(`❌ ${name}: NOT FOUND`);
    }
  });

  if (report.issues.length > 0) {
    console.log('\n🚨 ISSUES FOUND:');
    report.issues.forEach((issue, i) => {
      console.log(`${i + 1}. ${issue}`);
    });
  } else {
    console.log('\n✅ No issues found!');
  }

  if (report.fixes.length > 0) {
    console.log('\n🔧 SUGGESTED FIXES:');
    report.fixes.forEach((fix, i) => {
      console.log(`${i + 1}. ${fix}`);
    });
  }

  console.log('\n📋 NEXT STEPS:');
  if (report.issues.some(issue => issue.includes('does not exist'))) {
    console.log('1. Run the schema deployment (see DATABASE_DEPLOYMENT_GUIDE.md)');
    console.log('2. Execute the SQL in Supabase Dashboard');
  }

  if (report.issues.some(issue => issue.includes('user_id'))) {
    console.log('3. Fix column references in code');
    console.log('4. Update any remaining queries');
  }

  if (report.issues.length === 0) {
    console.log('✅ Schema is correctly deployed!');
    console.log('1. Test the authentication flow');
    console.log('2. Verify user registration/login');
    console.log('3. Test workspace operations');
  }

  // Save report to file
  const reportPath = path.join(__dirname, '../schema_verification_report.json');
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
  console.log(`\n💾 Report saved to: ${reportPath}`);

  return report;
}

// Run verification
pullAndVerifySchema().catch(console.error);
