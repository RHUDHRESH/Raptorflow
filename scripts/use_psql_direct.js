// Try to use psql directly with connection string
import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function usePsqlDirect() {
  console.log('🔧 Trying direct psql approach...\n');
  
  try {
    // Read the SQL file
    const sqlPath = path.join(__dirname, '../missing_tables.sql');
    const sqlContent = fs.readFileSync(sqlPath, 'utf8');
    
    console.log('📁 SQL file loaded');
    
    // Try different connection string formats
    const connectionStrings = [
      'postgresql://postgres.avnadmin@aws-0-us-east-1.pooler.supabase.com:5432/postgres',
      'postgresql://postgres@aws-0-us-east-1.pooler.supabase.com:5432/postgres',
      'postgresql://postgres:password@aws-0-us-east-1.pooler.supabase.com:5432/postgres'
    ];
    
    for (let i = 0; i < connectionStrings.length; i++) {
      const connStr = connectionStrings[i];
      console.log(`\n🔗 Trying connection string ${i + 1}/${connectionStrings.length}...`);
      
      try {
        // Try to execute psql
        const result = execSync(`psql "${connStr}" -c "${sqlContent}"`, {
          encoding: 'utf8',
          stdio: ['pipe', 'pipe', 'pipe'],
          timeout: 30000
        });
        
        console.log('✅ psql execution successful!');
        console.log('Output:', result);
        
        // Verify tables
        await verifyTables();
        return;
        
      } catch (err) {
        console.log(`❌ Connection ${i + 1} failed:`, err.message);
      }
    }
    
    console.log('\n❌ All psql connection attempts failed');
    
  } catch (error) {
    console.error('❌ Direct psql approach failed:', error);
  }
  
  console.log('\n📋 Manual execution still required:');
  console.log('1. Open Supabase Dashboard: https://app.supabase.com/project/vpwwzsanuyhpkvgorcnc');
  console.log('2. Go to SQL Editor');
  console.log('3. Execute the SQL from missing_tables.sql');
}

async function verifyTables() {
  console.log('\n🔍 Verifying tables after psql execution...');
  
  // Run the verification script
  try {
    const { execSync } = await import('child_process');
    const result = execSync('node scripts/quick_check.js', {
      encoding: 'utf8',
      cwd: path.join(__dirname, '..')
    });
    console.log(result);
  } catch (err) {
    console.log('Verification failed:', err.message);
  }
}

// Execute
usePsqlDirect().catch(console.error);
